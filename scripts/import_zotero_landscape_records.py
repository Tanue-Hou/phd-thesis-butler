#!/usr/bin/env python3
"""
import_zotero_landscape_records.py — v5.4.0 Zotero Landscape Record Importer

Provides two subcommands:
  status  — Check if Zotero Local API is accessible
  search  — Search Zotero items and output landscape-ready records

Usage:
    python3 scripts/import_zotero_landscape_records.py status

    python3 scripts/import_zotero_landscape_records.py search \
      --query "vehicle state estimation" \
      --limit 20 \
      --output .phd_build/zotero/landscape_records.json

Pure standard library — no external dependencies.
Zotero Local API: http://127.0.0.1:23119
"""

import argparse
import json
import sys
import os
import urllib.request
import urllib.error
import urllib.parse
import re
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ZOTERO_API_BASE = "http://127.0.0.1:23119"
ZOTERO_API_TIMEOUT = 5  # seconds
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Item types to skip
SKIP_TYPES = {"attachment", "note", "annotation"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def log(msg):
    """Print to stderr."""
    print(msg, file=sys.stderr)


def zotero_request(path, params=None, timeout=ZOTERO_API_TIMEOUT):
    """Make a request to the Zotero Local API. Returns (success, data_or_error)."""
    url = f"{ZOTERO_API_BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, headers={"Zotero-API-Version": "3"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, data
    except urllib.error.URLError as e:
        return False, f"Connection error: {e}"
    except TimeoutError:
        return False, "Connection timed out"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON response: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e.__class__.__name__}: {e}"


def check_zotero_status():
    """Check if Zotero Local API is accessible."""
    success, data = zotero_request("/connector/ping")
    return success


def extract_authors(item_data):
    """Extract author names from Zotero creators field."""
    creators = item_data.get("creators", [])
    authors = []
    for c in creators:
        if c.get("creatorType") == "author":
            first = c.get("firstName", "")
            last = c.get("lastName", "")
            if first and last:
                authors.append(f"{last} {first}")
            elif last:
                authors.append(last)
            elif first:
                authors.append(first)
    return authors


def extract_year(item_data):
    """Extract year from Zotero date field."""
    date_str = item_data.get("date", "")
    if not date_str:
        return None
    # Try to extract 4-digit year
    match = re.search(r"(\d{4})", date_str)
    if match:
        year = int(match.group(1))
        if 1900 <= year <= 2030:
            return year
    return None


def extract_keywords(item_data):
    """Extract keywords/tags from Zotero item."""
    tags = item_data.get("tags", [])
    return [t.get("tag", "") for t in tags if t.get("tag")]


def detect_discipline_cluster(item_data):
    """Heuristic discipline cluster detection from title/abstract."""
    text = " ".join([
        item_data.get("title", ""),
        item_data.get("abstractNote", ""),
    ]).lower()

    # Technical / automation keywords
    tech_kw = ["control", "automation", "signal", "diagnostic", "vibrat",
               "sensor", "estimation", "filter", "kalman", "observer",
               "vehicle", "transmission", "gearbox", "engine", "motor"]
    sci_kw = ["physics", "chemistry", "mathematics", "biology",
              "material", "mechanics", "thermodynamic"]
    med_kw = ["medical", "clinical", "patient", "disease", "health",
              "pharmaceutical"]

    tech_score = sum(1 for kw in tech_kw if kw in text)
    sci_score = sum(1 for kw in sci_kw if kw in text)
    med_score = sum(1 for kw in med_kw if kw in text)

    if tech_score >= sci_score and tech_score >= med_score and tech_score > 0:
        return "AUTOMATION_CONTROL"
    if sci_score > 0:
        return "SCI_TECH"
    if med_score > 0:
        return "AGRI_MED"
    return "UNCLASSIFIED"


def zotero_item_to_landscape_record(item):
    """Convert a Zotero API item to a landscape-ready record."""
    data = item.get("data", item)
    item_type = data.get("itemType", "")

    if item_type in SKIP_TYPES:
        return None

    key = data.get("key", "")
    title = data.get("title", "")
    if not title:
        return None

    authors = extract_authors(data)
    year = extract_year(data)
    keywords = extract_keywords(data)
    abstract = data.get("abstractNote", "")
    doi = data.get("DOI", "")
    url = data.get("url", "")
    publication_type = data.get("itemType", "other")
    journal = data.get("publicationTitle", "") or data.get("journalAbbreviation", "")
    volume = data.get("volume", "")
    pages = data.get("pages", "")

    # Map Zotero item types to our types
    type_map = {
        "journalArticle": "journal_article",
        "conferencePaper": "conference_paper",
        "book": "monograph",
        "bookSection": "book_section",
        "thesis": "thesis",
        "preprint": "preprint",
        "report": "report",
    }
    pub_type = type_map.get(publication_type, "other")

    record = {
        "id": f"zotero_{key}" if key else f"zotero_{hash(title) % 100000:05d}",
        "title_ru": title,
        "title_en": title,
        "authors": authors if authors else ["Unknown"],
        "year": year,
        "publication_type": pub_type,
        "journal": journal,
        "doi": doi if doi else None,
        "url": url if url else None,
        "keywords_ru": keywords,
        "abstract_ru": abstract if abstract else None,
        "source_platform": "zotero",
        "source": "zotero_local_api",
        "discipline_cluster": detect_discipline_cluster(data),
        "evidence_role": ["literature_pool"],
        "read_depth": "imported",
        "source_access": "zotero_local",
        "structure_confidence": 0.5,
    }

    # Add volume/pages if available
    if volume:
        record["volume"] = volume
    if pages:
        record["pages"] = pages

    return record


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_status(args):
    """Check Zotero Local API availability."""
    if check_zotero_status():
        print("Zotero API: AVAILABLE")
        return 0
    else:
        print("Zotero API: UNAVAILABLE")
        print(f"  (Could not connect to {ZOTERO_API_BASE})")
        print("  Make sure Zotero is running with the Local API enabled.")
        return 0  # Exit 0 even on failure (no crash)


def cmd_search(args):
    """Search Zotero items and output landscape-ready records."""
    query = args.query
    limit = args.limit
    output_path = args.output

    # Check API first
    if not check_zotero_status():
        print("ERROR: Zotero API is not available.", file=sys.stderr)
        print(f"  Cannot connect to {ZOTERO_API_BASE}", file=sys.stderr)
        print("  Make sure Zotero is running with the Local API enabled.", file=sys.stderr)
        sys.exit(0)  # Exit 0, not crash

    # Search items
    log(f"Searching Zotero for: '{query}' (limit={limit})")

    params = {
        "q": query,
        "qmode": "titleCreatorYear",
        "itemType": "-attachment || -note",
        "limit": str(limit),
        "format": "json",
    }

    success, data = zotero_request("/api/users/0/items", params, timeout=10)
    if not success:
        print(f"ERROR: Zotero search failed: {data}", file=sys.stderr)
        sys.exit(0)  # Exit 0, not crash

    if not isinstance(data, list):
        print(f"ERROR: Unexpected response format from Zotero API", file=sys.stderr)
        sys.exit(0)

    log(f"Received {len(data)} items from Zotero")

    # Convert to landscape records
    records = []
    skipped = 0
    for item in data:
        record = zotero_item_to_landscape_record(item)
        if record:
            records.append(record)
        else:
            skipped += 1

    log(f"Converted {len(records)} records ({skipped} skipped as notes/attachments/empty)")

    if not records:
        print("No valid records found. Try a different search query.")
        # Write empty array
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"Empty result written to: {output_path}")
        return 0

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Written {len(records)} landscape records to: {output_path}")

    # Print summary
    pub_types = {}
    for r in records:
        pt = r.get("publication_type", "other")
        pub_types[pt] = pub_types.get(pt, 0) + 1
    print(f"\nSummary:")
    print(f"  Records: {len(records)}")
    for pt, cnt in sorted(pub_types.items(), key=lambda x: -x[1]):
        print(f"  {pt}: {cnt}")

    years = [r["year"] for r in records if r.get("year")]
    if years:
        print(f"  Year range: {min(years)}-{max(years)}")

    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Import landscape records from Zotero Local API."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-command")

    # status subcommand
    sub_status = subparsers.add_parser("status",
                                        help="Check Zotero Local API availability")

    # search subcommand
    sub_search = subparsers.add_parser("search",
                                        help="Search Zotero items and export landscape records")
    sub_search.add_argument("--query", required=True,
                            help="Search query (title/author/tag)")
    sub_search.add_argument("--limit", type=int, default=20,
                            help="Maximum number of results (default: 20)")
    sub_search.add_argument("--output", required=True,
                            help="Output JSON file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "status":
        return cmd_status(args)
    elif args.command == "search":
        return cmd_search(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
