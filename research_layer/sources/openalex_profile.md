# OpenAlex Data Source Profile

## Overview
OpenAlex is a fully open catalog of the global research system, built by OurResearch as a replacement for the discontinued Microsoft Academic Graph. It indexes over 250 million scholarly works (papers), 100 million author profiles, 100,000+ institutions, and millions of concepts/topics. OpenAlex is completely free with no API key required, making it one of the most accessible large-scale academic databases.

## Key Characteristics
- **Type**: Open scholarly graph / Bibliometric database
- **Coverage**: 250M+ works, 100M+ authors, 100K+ institutions, 65K+ sources
- **Content**: Journal articles, conference papers, books, datasets, preprints
- **Update frequency**: Daily
- **Language**: All languages (metadata in English)
- **Access**: Completely free, no API key required (polite pool needs email)

## API Access

### OpenAlex API
- **Base URL**: `https://api.openalex.org`
- **Authentication**: None required. Add `mailto=your@email.com` for polite pool (faster, more reliable)
- **Rate limit**: 10 requests/second (polite pool), 1 request/second (anonymous)
- **Response format**: JSON

### Key Entities (Endpoints)

| Entity | URL | Description |
|--------|-----|-------------|
| Works | `/works` | Scholarly papers, articles, etc. |
| Authors | `/authors` | Author profiles with metrics |
| Sources | `/sources` | Journals, repositories, etc. |
| Institutions | `/institutions` | Universities, labs, etc. |
| Concepts | `/concepts` | Topics/subjects (deprecated in favor of Topics) |
| Topics | `/topics` | New topic classification system |
| Funders | `/funders` | Research funding organizations |
| Publishers | `/publishers` | Journal/book publishers |

### Example Queries

Search for works about "robot manipulation planning":
```
https://api.openalex.org/works?search=robot%20manipulation%20planning&filter=publication_year:2020-2026&sort=cited_by_count:desc&per_page=50&mailto=your@email.com
```

Search with concept/topic filter:
```
https://api.openalex.org/works?search=task+planning&filter=concepts.id:C154945302,publication_year:2020-2026&sort=cited_by_count:desc&per_page=50
```

Find works by author (OpenAlex author ID):
```
https://api.openalex.org/works?filter=author.id:A1234567890&sort=publication_year:desc
```

Get author profile:
```
https://api.openalex.org/authors/A1234567890?mailto=your@email.com
```

Find works with a specific DOI:
```
https://api.openalex.org/works/doi:10.1234/example.doi
```

Find works from a specific institution:
```
https://api.openalex.org/works?filter=institutions.id:I133049507&filter=publication_year:2020-2026&sort=cited_by_count:desc
```

Get funding information:
```
https://api.openalex.org/works?filter=grants.funder:I133049507&per_page=50
```

## Metadata Fields (Works)
Each work object includes:
- `id` — OpenAlex ID (e.g., `W2741809807`)
- `doi` — DOI URL
- `title`, `display_name`
- `publication_year`, `publication_date`
- `authorships` — list of authors with `author` (id, name, ORCID), `institutions`, `is_corresponding`
- `primary_location` — source (journal), PDF URL
- `locations` — all locations (journal + repositories)
- `open_access` — OA status, OA URL, license
- `cited_by_count` — total citation count
- `referenced_works` — list of OpenAlex IDs of cited works
- `related_works` — algorithmically related works
- `concepts` / `topics` — automatic topic classification with scores
- `sustainable_development_goals` — SDG classification
- `grants` — funding information
- `type` — article, book-chapter, dataset, etc.
- `language` — ISO language code
- `biblio` — volume, issue, first/last page
- `abstract_inverted_index` — reconstructable abstract

## Strengths
- **Completely free**: No API key, no paywall, no rate-limit surprises
- **Largest open index**: 250M+ works, broader than Scopus or Web of Science
- **Rich entity graph**: Works ↔ Authors ↔ Institutions ↔ Funders ↔ Topics
- **Bibliometric-ready**: Built for large-scale analysis, has snapshot dumps
- **Open access tracking**: Identifies OA status and provides PDF links
- **Institutional analysis**: Filter by institution, compare output
- **Funding analysis**: Track grant-funded research
- **Topic classification**: Automatic tagging with scores
- **Snapshot dumps**: Full database available for download (S3)

## Limitations
- Metadata quality depends on upstream sources (Crossref, PubMed, etc.)
- Abstract reconstruction from inverted index is imperfect
- Author disambiguation is good but still has merge/split errors
- No full-text search (searches titles and abstracts only)
- Concept/topic classification is being deprecated in favor of new Topics system
- Some older papers have sparse metadata
- No peer-review status information
- Citation counts may differ from Google Scholar or Scopus

## Integration Notes
- OpenAlex IDs can be mapped to DOIs, PubMed IDs, and MAG IDs
- Use `referenced_works` field for building citation networks
- For large-scale analysis, download the full snapshot (available monthly on S3)
- The `abstract_inverted_index` requires reconstruction (Python example below)
- Python package: `pyalex` (`pip install pyalex`)

### Reconstruct Abstract from Inverted Index
```python
def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(w for _, w in word_positions)
```

## Recommended Use in Literature Review
OpenAlex is ideal for:
1. Large-scale bibliometric analysis (publication trends, citation patterns)
2. Mapping the research landscape by topic/institution/country
3. Identifying top authors and institutions in a field
4. Tracking funding sources and grant-funded research
5. Finding open-access versions of papers
6. Building comprehensive citation networks
7. Cross-referencing with other databases via shared IDs (DOI, PMID)
