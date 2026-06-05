# Agentic Search Workflow

> phd-thesis-butler v5.4.0 | research_layer/landscape

## Overview

Agentic search is the automated discovery and parsing of dissertation records from public academic sources. The agent generates search queries, executes them against source APIs or public pages, and extracts structured metadata.

---

## Supported Sources

| Source | URL | Language | Access Method |
|---|---|---|---|
| DisserCat | dissercat.com | ru | Public page parse |
| eLIBRARY | elibrary.ru | ru | Public page parse |
| CyberLeninka | cyberleninka.ru | ru/en | Public page parse |
| OpenAlex | openalex.org | en | REST API |
| Semantic Scholar | semanticscholar.org | en | REST API |

---

## Query Generation

### Russian-Language Sources (DisserCat, eLIBRARY, CyberLeninka)

The agent generates Russian search queries from the user's topic using the following strategy:

1. **Core term translation** — Translate key concepts to Russian academic terminology
2. **Synonym expansion** — Add discipline-specific Russian synonyms
3. **Specialty code targeting** — If the user's specialty code is known, include it as a filter
4. **Query variants** — Generate 3–5 query variants to maximize recall

**Example:**
- User topic: "Vehicle state estimation using Kalman filtering"
- Generated queries:
  - `"оценка состояния транспортного средства" фильтр Калмана`
  - `"идентификация параметров автомобиля" методы оценки`
  - `"моделирование динамики транспортного средства" идентификация состояния`

### English-Language Sources (OpenAlex, Semantic Scholar)

1. **Direct keyword search** — Use user's topic terms directly
2. **Concept extraction** — Identify key concepts for concept-based search
3. **Boolean construction** — Build AND/OR queries for precision/recall balance

**Example:**
- `vehicle state estimation AND Kalman filter`
- `("vehicle dynamics" OR "vehicle state") AND ("estimation" OR "identification")`

---

## Search Execution

### API-Based Sources (OpenAlex, Semantic Scholar)

- Use REST API with pagination
- Respect rate limits (Semantic Scholar: 100 req/5min without key)
- Filter by document type (dissertation/thesis only if available)
- Capture: id, title, authors, year, abstract, concepts, cited_by_count

### Public Page Sources (DisserCat, eLIBRARY, CyberLeninka)

- Load search results page
- Parse result list for dissertation links
- Visit each dissertation's public page
- Extract all available metadata from public HTML
- Respect robots.txt and implement polite delays

---

## Field Extraction

For each record, extract the following fields (when available):

### Required Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Source-specific identifier |
| `source_name` | string | Which source this came from |
| `source_url` | string | Public URL to the dissertation page |
| `source_access` | enum | Access level (see taxonomy below) |
| `read_depth` | enum | How much content was read (see taxonomy below) |
| `structure_confidence` | float | 0.0–1.0 confidence in structure extraction |
| `title` | string | Dissertation title |
| `author` | string | Author name |
| `year` | integer | Year of defense |

### Extended Fields

| Field | Type | Description |
|---|---|---|
| `degree_type` | enum | `candidate` / `doctoral` |
| `specialty_code` | string | VAK specialty code (Russian system) |
| `specialty_name` | string | Specialty name |
| `institution` | string | Defending institution |
| `abstract` | string | Abstract text (if publicly available) |
| `keywords` | string[] | Author-assigned keywords |
| `toc` | string[] | Table of contents — chapter titles |
| `methods` | string[] | Extracted method references |
| `validation_type` | string | Type of validation described |

---

## Source Access Taxonomy

The `source_access` field indicates how the content was accessed:

| Value | Meaning |
|---|---|
| `public_page` | Publicly available web page (no auth required) |
| `public_api` | Public API endpoint (OpenAlex, Semantic Scholar) |
| `zotero_metadata` | From Zotero local library (metadata only) |
| `zotero_indexed_fulltext` | From Zotero with indexed fulltext attachment |
| `limited_preview` | Partial access (e.g., first N pages only) |
| `abstract_only` | Only abstract was available |

---

## Read Depth Taxonomy

The `read_depth` field indicates how much content was actually processed:

| Value | Meaning | Typical Fields Available |
|---|---|---|
| `title_only` | Only title was retrieved | title, author, year |
| `abstract_toc` | Abstract and table of contents parsed | + abstract, toc, keywords |
| `full_metadata` | All public metadata fields extracted | + specialty, institution, methods |
| `partial_fulltext` | Some fulltext content read (e.g., preview) | + partial chapter content |
| `fulltext` | Complete dissertation text available | + all content, citations |

**Confidence mapping:**
- `title_only` → structure_confidence: 0.1–0.2
- `abstract_toc` → structure_confidence: 0.4–0.7
- `full_metadata` → structure_confidence: 0.6–0.8
- `partial_fulltext` → structure_confidence: 0.7–0.9
- `fulltext` → structure_confidence: 0.9–1.0

---

## Parsing Strategy by Source

### DisserCat

DisserCat public pages typically contain:
- Title, author, year, institution
- Specialty code and name
- Abstract (автореферат)
- Keywords
- Table of contents (оглавление) — sometimes available
- Scientific advisor name

**Parsing approach:** Extract structured data from the dissertation's public detail page. The abstract page (`/diss/.../avtoreferat`) often has richer metadata than the summary page.

### eLIBRARY

eLIBRARY pages may contain:
- Title, author, year
- Specialty code
- Abstract
- Keywords
- Institution

**Parsing approach:** Search results list + detail page. Note: eLIBRARY may require login for some fields — only extract publicly visible data.

### CyberLeninka

CyberLeninka hosts open-access fulltexts:
- Full metadata is typically available
- Abstract and keywords are on the main page
- Fulltext PDF may be accessible

**Parsing approach:** Detail page metadata extraction. If fulltext is publicly available, read_depth can be elevated to `partial_fulltext` or `fulltext`.

### OpenAlex

OpenAlex REST API (`api.openalex.org`):
- Rich metadata via `works` endpoint
- Concept tags, cited_by_count
- Abstract reconstruction from inverted index
- Author affiliations

**Parsing approach:** API query → JSON parsing. Filter by `type: "dissertation"` if available.

### Semantic Scholar

Semantic Scholar API (`api.semanticscholar.org`):
- Paper search endpoint
- Fields: title, abstract, year, authors, citationCount
- S2 paper IDs for cross-referencing

**Parsing approach:** API query → JSON parsing. Filter by `publicationTypes: ["Review"]` or use venue filtering for dissertations.

---

## Error Handling

| Scenario | Handling |
|---|---|
| Source unreachable | Log warning, skip source, continue with others |
| Rate limited | Back off exponentially, retry with delay |
| Parse failure | Record with `structure_confidence: 0.0`, flag for review |
| Empty results | Log, try alternate query variants |
| Auth required | Skip authenticated-only content, use public data only |

---

## Output Format

Each search run produces an array of record objects matching the schema in `examples/dissercat_landscape_input_sample.json`.

The agent MUST populate `source_access` and `read_depth` on every record — these fields are never optional.
