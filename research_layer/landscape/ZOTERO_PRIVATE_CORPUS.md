# Zotero Private Corpus Workflow

> phd-thesis-butler v5.4.0 | research_layer/landscape

## Overview

The Zotero private corpus integration allows the agent to incorporate the user's personal research library into the dissertation landscape analysis. This provides a view of what the user has already collected — dissertations, theses, and related papers they've saved.

**Key principle:** Zotero data is private. The agent must never expose attachment paths, local file paths, or library internals in any output.

---

## Zotero Capability Gate

Before any Zotero operations, the agent MUST verify the following capability gate:

```
ZOTERO CAPABILITY GATE
═══════════════════════
1. Local API Reachability
   → GET http://localhost:23119/api/users/0/items?limit=1
   → Expected: 200 OK with JSON response
   → If fail: "Zotero Local API is not reachable.
               Ensure Zotero desktop is running with Local API enabled."

2. Library Content Check
   → Verify response contains at least 1 item
   → If empty: "Zotero library appears empty. Add references first."

3. Collection Discovery (optional)
   → GET http://localhost:23119/api/users/0/collections
   → List available collections for user selection

4. Full-text Index Status
   → GET http://localhost:23119/api/users/0/items/{key}/fulltext
   → Check if indexed fulltext is available for sample items
   → Note: Not all items will have indexed fulltext

ALL GATES PASSED → proceed with Zotero integration
ANY GATE FAILED  → skip Zotero, proceed with external sources only
                    log warning, do NOT block landscape generation
```

---

## Search Strategy

### Step 1: Query Construction

Build Zotero search queries from the user's topic:

1. **Keyword search** — Search across title, abstract, and notes
2. **Tag-based filtering** — Use user-defined tags if relevant
3. **Collection scoping** — Limit to relevant collections if user specifies

**Zotero Local API search endpoint:**
```
GET http://localhost:23119/api/users/0/items?q={search_terms}&itemType=-attachment%20||%20-note&limit=100&format=json
```

### Step 2: Filtering

The agent MUST apply these filters:

| Filter | Rule |
|---|---|
| Skip attachments | `itemType != "attachment"` |
| Skip notes | `itemType != "note"` |
| Skip standalone notes | `itemType != "note"` (API-level filter) |
| Include only relevant types | Prefer: thesis, journalArticle, conferencePaper, book, report |
| Relevance check | Title/abstract must contain topic-related terms |

### Step 3: Field Extraction

For each Zotero record, extract:

| Field | Zotero API Path | Notes |
|---|---|---|
| `zotero_item_key` | `data.key` | Zotero item key (e.g., `ABCD1234`) |
| `title` | `data.title` | May be null — handle gracefully |
| `author` | `data.creators[0]` | Concatenate first/last; may be empty array |
| `year` | `data.date` | Parse year from date string; may be null |
| `abstract` | `data.abstractNote` | May be empty |
| `keywords` | `data.tags[].tag` | Array of tag strings |
| `bibtex_key` | Generate from author+year+title | Auto-generated citation key |
| `zotero_collection` | From collection membership | Which collection(s) this item belongs to |
| `zotero_tags` | `data.tags` | Full tag array with metadata |
| `indexed_fulltext_available` | Check `/fulltext` endpoint | Boolean |

---

## Field Handling — Edge Cases

### Null Year (`year: null`)

When `data.date` is empty or unparseable:
- Set `year: null` in the output record
- Do NOT guess or fabricate a year
- Flag the record: `warnings: ["year_unknown"]`
- In rubric analysis, exclude from year-based trends

### Null Title (`title: null`)

When `data.title` is empty:
- Set `title: null` in the output record
- This should be rare — flag for user review
- Set `structure_confidence: 0.0`
- Flag: `warnings: ["title_missing"]`

### Empty Authors (`authors: []`)

When `data.creators` is empty:
- Set `author: ""` (empty string)
- Do NOT fabricate author names
- Set `structure_confidence: 0.0`
- Flag: `warnings: ["author_missing"]`

### Missing Abstract

When `data.abstractNote` is empty:
- Set `abstract: null`
- Try to retrieve indexed fulltext as fallback
- If fulltext available, generate a synthetic abstract note

---

## Privacy Boundaries

### NEVER Expose

The following must NEVER appear in any output (report, JSON, logs, or messages):

| Protected Data | Why |
|---|---|
| Attachment file paths | Reveals local filesystem structure |
| Zotero data directory path | Reveals local install location |
| Zotero user ID / API key | Authentication credentials |
| Full tag lists (if sensitive) | May contain personal organizational notes |
| Note content (if private) | User's personal annotations |

### Safe to Include

| Data | In Output? |
|---|---|
| Zotero item key | Yes (for user cross-reference) |
| Collection name | Yes |
| Public metadata (title, author, etc.) | Yes |
| Whether fulltext is indexed | Yes (boolean only, no paths) |
| Tag names (non-sensitive) | Yes |

### Privacy Filter

Before any record enters the output pipeline, apply this filter:

```
REDACT_ATTACHMENT_PATHS:
  - Strip any field matching pattern: /path/to/, C:\, /mnt/, /home/
  - Replace with: "[attachment_available]"
  - Specifically check: data.links, data.content, attachment metadata
```

---

## Zotero Record Schema

Zotero records in the landscape input carry additional fields:

```json
{
  "id": "zotero-ABCD1234",
  "source_name": "zotero",
  "source_url": null,
  "source_access": "zotero_metadata",
  "read_depth": "abstract_toc",
  "structure_confidence": 0.5,
  "title": "Vehicle Parameter Estimation Methods",
  "author": "Petrov A.V.",
  "year": 2019,
  "degree_type": "candidate",
  "specialty_code": "05.22.10",
  "specialty_name": "Operation of transport vehicles",
  "institution": null,
  "abstract": "The dissertation examines...",
  "keywords": ["vehicle dynamics", "parameter estimation", "Kalman filter"],
  "toc": [],
  "methods": ["Kalman filtering", "least squares"],
  "validation_type": "simulation",
  "zotero_item_key": "ABCD1234",
  "bibtex_key": "petrov2019vehicle",
  "zotero_collection": "PhD References",
  "zotero_tags": ["phd", "vehicle-dynamics", "estimation"],
  "indexed_fulltext_available": true
}
```

---

## Integration with Landscape Analysis

Zotero records are merged with external source records in the deduplication step:

1. **Deduplication** — Match by (author, year, title similarity)
2. **Provenance tagging** — Records retain `source_name: "zotero"` tag
3. **Read depth elevation** — If Zotero has indexed fulltext, read_depth may be elevated
4. **Confidence adjustment** — Zotero records with fulltext get higher structure_confidence

---

## Error Handling

| Scenario | Handling |
|---|---|
| Zotero not running | Skip silently, proceed with external sources |
| API returns 403 | Log warning, skip Zotero |
| Item has no metadata | Include with low confidence, flag for review |
| Collection not found | Use "Unfiled Items" as fallback |
| Fulltext index empty | Set `indexed_fulltext_available: false`, continue |
