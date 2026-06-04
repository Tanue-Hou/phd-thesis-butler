# Crossref Data Source Profile

## Overview
Crossref is the official DOI registration agency for scholarly publishing. It maintains metadata for over 150 million DOIs registered by thousands of publishers worldwide. Crossref is not a search engine but a metadata infrastructure — it provides authoritative bibliographic metadata, citation linking, and DOI resolution for virtually all published scholarly content.

## Key Characteristics
- **Type**: DOI registration agency / Metadata infrastructure
- **Coverage**: 150M+ DOIs from 19,000+ member organizations
- **Content**: Journal articles, conference papers, books, datasets, preprints, reports
- **Update frequency**: Real-time (publishers deposit metadata continuously)
- **Language**: Metadata in English; content in all languages
- **Access**: Free metadata API (no key required for basic use; polite pool recommended)

## API Access

### Crossref REST API
- **Base URL**: `https://api.crossref.org`
- **Authentication**: No key required for basic use. Add `mailto=your@email.com` for polite pool.
- **Rate limit**: 50 requests/second (polite pool), significantly lower without email
- **Response format**: JSON (default), also supports `text/x-bibliography` for formatted citations

### Key Endpoints

**Search works (full-text query):**
```
https://api.crossref.org/works?query=robot+manipulation+planning&rows=50&sort=is-referenced-by-count&order=desc&mailto=your@email.com
```

**Get work by DOI:**
```
https://api.crossref.org/works/10.1109/TRO.2023.1234567
```

**Get formatted citation (APA, MLA, etc.):**
```
https://api.crossref.org/works/10.1109/TRO.2023.1234567
Accept: text/x-bibliography; style=apa
```

**Search by author:**
```
https://api.crossref.org/works?query.author=Levine&query=manipulation&rows=25&mailto=your@email.com
```

**Search by journal (ISSN filter):**
```
https://api.crossref.org/works?query=deep+reinforcement+learning&filter=issn:2331-8422&rows=25
```

**Search by date range:**
```
https://api.crossref.org/works?query=task+planning&filter=from-pub-date:2020-01-01,until-pub-date:2026-12-31&rows=50
```

**Get citations for a DOI (via Crossref Cited-by API):**
```
https://api.crossref.org/works/10.1109/TRO.2023.1234567/cited-by
```

**Get references listed by a DOI:**
```
https://api.crossref.org/works/10.1109/TRO.2023.1234567
(see the "reference" field in the response)
```

**Funders registry:**
```
https://api.crossref.org/funders?query=national+science+foundation
```

**Journals:**
```
https://api.crossref.org/journals?query=robotics&issn=2331-8422
```

## Metadata Fields
Each work object includes:
- `DOI` — the Digital Object Identifier
- `title` — paper title (array, usually one element)
- `author` — list with `given`, `family`, `ORCID`, `affiliation`
- `abstract` — JATS XML abstract (when deposited by publisher)
- `published-print`, `published-online`, `created`, `deposited` — dates
- `container-title` — journal/conference name
- `volume`, `issue`, `page` — bibliographic details
- `type` — journal-article, proceedings-article, book-chapter, etc.
- `publisher` — publisher name
- `ISSN`, `ISBN` — source identifiers
- `is-referenced-by-count` — citation count (from Crossref data only)
- `reference` — references list (if deposited by publisher)
- `reference-count` — number of references
- `subject` — subject tags
- `funder` — funding information (grant numbers, funder DOI)
- `license` — content license
- `link`, `resource.primary` — full-text links
- `clinical-trial-number` — for medical papers
- `group-title` — preprint server grouping

## Strengths
- **Authoritative metadata**: Official DOI source, publisher-deposited
- **Citation formatting**: Direct bibliography output in any CSL style
- **Funder metadata**: Links papers to grants and funding bodies
- **Broadest DOI coverage**: Nearly all published scholarly content
- **Reliable bibliographic data**: Volume, issue, pages, ISSN — publication details
- **ORCID integration**: Author ORCIDs when provided by publishers
- **Cited-by counts**: Citation data for DOIs registered with Crossref
- **Event API**: Real-time notifications of new DOI registrations
- **No cost**: Free for metadata queries

## Limitations
- **Not a full-text search engine**: `query` searches metadata, not paper content
- **Citation data is incomplete**: Only counts citations between Crossref-registered DOIs; does not cover all citation relationships (unlike Semantic Scholar)
- **Abstracts are optional**: Not all publishers deposit abstracts
- **Reference data is optional**: Not all publishers deposit reference lists
- **No relevance ranking**: Search results are by match, not semantic relevance
- **No topic classification**: No automatic concept/topic tagging
- **No author profiles**: No aggregate author metrics (use OpenAlex for this)
- **Publisher-dependent quality**: Metadata quality varies by publisher

## Integration Notes
- Crossref is the canonical source for DOI metadata — use it to validate and enrich DOIs found elsewhere
- For formatted citations (APA, IEEE, etc.), use the `Accept: text/x-bibliography` header
- Combine with Semantic Scholar for richer citation analysis
- Combine with OpenAlex for bibliometric analysis and author profiles
- The `CrossrefEvent` API provides real-time alerts for new papers matching filters
- Python package: `crossrefapi` or `habanero` (`pip install habanero`)

### Generate APA Citation via API
```python
import requests

doi = "10.1109/TRO.2023.1234567"
headers = {"Accept": "text/x-bibliography; style=apa; locale=en-US"}
r = requests.get(f"https://api.crossref.org/works/{doi}", headers=headers)
print(r.text)
# Output: Levine, S., et al. (2023). Paper Title. IEEE Transactions on Robotics, 39(4), ...
```

### Validate and Enrich a DOI
```python
import requests

doi = "10.1109/TRO.2023.1234567"
r = requests.get(f"https://api.crossref.org/works/{doi}?mailto=your@email.com")
data = r.json()["message"]
print(f"Title: {data['title'][0]}")
print(f"Journal: {data.get('container-title', ['N/A'])[0]}")
print(f"Citations: {data['is-referenced-by-count']}")
print(f"References: {data['reference-count']}")
```

## Recommended Use in Literature Review
Crossref is ideal for:
1. Validating and enriching DOI metadata (title, authors, journal, dates)
2. Generating properly formatted citations (APA, IEEE, Chicago, etc.)
3. Finding publisher-deposited abstracts for papers identified via other sources
4. Tracking funder/grant information for papers
5. Building reference lists from DOI inputs
6. Checking citation counts for specific DOIs
7. Resolving DOIs to full-text publisher pages
