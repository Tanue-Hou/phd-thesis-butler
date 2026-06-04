# Semantic Scholar Data Source Profile

## Overview
Semantic Scholar is an AI-powered academic search engine developed by the Allen Institute for AI (AI2). It uses machine learning to extract meaning from scientific papers and build a rich citation graph. It covers over 200 million papers across all academic disciplines and is particularly strong in computer science, neuroscience, and biomedical research.

## Key Characteristics
- **Type**: AI-powered academic search engine / Citation database
- **Coverage**: 200M+ papers across all disciplines
- **Content**: Journal articles, conference papers, preprints, theses, books
- **Update frequency**: Near real-time (daily ingestion from Crossref, PubMed, arXiv, etc.)
- **Language**: Primarily English, but indexes papers in many languages
- **Access**: Free to search; API requires free API key

## API Access

### Semantic Scholar API (S2 API)
- **Base URL**: `https://api.semanticscholar.org/graph/v1`
- **Authentication**: Free API key (apply at https://www.semanticscholar.org/product/api#api-key)
- **Rate limit**: 1 request/second without key; 10 requests/second with key; 100/sec for Plus
- **Response format**: JSON

### Key Endpoints

**Paper search:**
```
GET https://api.semanticscholar.org/graph/v1/paper/search?query=robot+manipulation+planning&limit=50&fields=title,authors,year,citationCount,abstract,url,externalIds
```

**Paper by ID (arXiv, DOI, S2 paperId):**
```
GET https://api.semanticscholar.org/graph/v1/paper/ArXiv:2301.12345?fields=title,authors,abstract,citations,references
```

**Paper citations (papers that cite this paper):**
```
GET https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields=title,authors,year,citationCount&limit=100
```

**Paper references (papers cited by this paper):**
```
GET https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references?fields=title,authors,year&limit=100
```

**Author search:**
```
GET https://api.semanticscholar.org/graph/v1/author/search?query=Levine&fields=name,hIndex,paperCount,citationCount
```

**Bulk search with filters:**
```
GET https://api.semanticscholar.org/graph/v1/paper/search?query=task+planning&year=2020-2026&fieldsOfStudy=Computer+Science&fields=title,authors,year,citationCount&sort=citationCount:desc
```

## Metadata Fields
Rich field selection via `fields` parameter:
- `paperId` — Semantic Scholar unique ID
- `title`, `abstract`, `year`
- `authors` — list with `authorId`, `name`, `affiliations`, `externalIds` (ORCID, DBLP)
- `venue` — journal/conference name
- `publicationVenue` — structured venue object
- `externalIds` — DOI, ArXiv, PubMed, ACL, DBLP, CorpusId
- `citationCount`, `influentialCitationCount`
- `referenceCount`
- `fieldsOfStudy` — e.g., "Computer Science", "Mathematics"
- `s2FieldsOfStudy` — finer-grained classification
- `isOpenAccess`, `openAccessPdf`
- `tldr` — AI-generated one-sentence summary
- `citations`, `references` — linked paper objects

## Example: Python Usage
```python
import requests

API_KEY = "your-api-key"  # optional but recommended

headers = {"x-api-key": API_KEY} if API_KEY else {}
params = {
    "query": "robot manipulation planning",
    "year": "2020-2026",
    "fields": "title,authors,year,citationCount,abstract,tldr,url",
    "sort": "citationCount:desc",
    "limit": 50
}
r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search",
                  params=params, headers=headers)
data = r.json()
for paper in data.get("data", []):
    print(f"[{paper['year']}] {paper['title']} (citations: {paper['citationCount']})")
```

## Strengths
- **Citation graph**: Full citation and reference data for every indexed paper
- **influentialCitationCount**: Distinguishes perfunctory citations from meaningful ones
- **TLDR summaries**: AI-generated one-line abstracts for quick triage
- **Citation sorting**: Find high-impact papers instantly via `sort=citationCount:desc`
- **Cross-source**: Aggregates from Crossref, PubMed, arXiv, DBLP, and more
- **Author profiles**: h-index, paper count, citation count, affiliations
- **Fields of study**: Automatic topic classification
- **Open access detection**: `isOpenAccess` flag and direct PDF links

## Limitations
- API rate limits can be restrictive for large-scale crawling
- Free API key has lower rate limits than paid plans
- Coverage gaps exist for humanities and social sciences
- Some papers lack abstracts (especially older ones)
- Citation counts may lag behind Google Scholar
- No full-text search (searches metadata + abstract only)
- Author disambiguation is good but not perfect
- API fields parameter is required — defaults return minimal data

## Integration Notes
- Best paired with arXiv (for preprint access) and Crossref (for DOI metadata)
- The `externalIds` field links papers across databases (DOI, ArXiv ID, PubMed ID)
- Use `influentialCitationCount` instead of raw `citationCount` for quality filtering
- The `tldr` field is excellent for quick screening of search results
- Consider the Academic Graph API for author/institution-level analysis
- Python package: `semanticscholar` (`pip install semanticscholar`)

## Recommended Use in Literature Review
Semantic Scholar is ideal for:
1. Finding high-impact papers via citation count sorting
2. Building citation trees (forward and backward citation tracking)
3. Discovering influential works in a research area
4. Quick abstract screening via TLDR summaries
5. Author-level metrics (h-index, total citations)
6. Cross-referencing papers across arXiv, PubMed, and journals
