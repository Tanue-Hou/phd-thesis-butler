# arXiv Data Source Profile

## Overview
arXiv is an open-access repository of electronic preprints (e-prints) maintained by Cornell University. It covers physics, mathematics, computer science, quantitative biology, quantitative finance, statistics, electrical engineering, economics, and related disciplines. arXiv is one of the most important sources for cutting-edge research that has not yet undergone formal peer review.

## Key Characteristics
- **Type**: Preprint repository / Open-access archive
- **Coverage**: Primarily STEM fields; strong in CS, math, physics, statistics
- **Content**: Preprints, working papers, accepted manuscripts
- **Update frequency**: Daily (submissions typically available within 24 hours)
- **Language**: English (predominantly), some submissions in other languages
- **Access**: Fully open access, no paywall

## Relevant Subject Classifications
For a thesis on Butler (robotics, control, or related topics), the most relevant arXiv categories include:
- `cs.RO` — Robotics
- `cs.AI` — Artificial Intelligence
- `cs.CV` — Computer Vision
- `cs.LG` — Machine Learning
- `cs.CL` — Computation and Language (NLP)
- `cs.MA` — Multiagent Systems
- `math.OC` — Optimization and Control
- `cs.SY` — Systems and Control
- `eess.SY` — Systems and Control (Electrical Engineering)

## API Access

### arXiv API (OAI-PMH and Search API)
- **Base URL**: `http://export.arxiv.org/api/query`
- **Protocol**: Atom/XML feed via HTTP GET
- **Authentication**: No API key required (open access)
- **Rate limit**: Be respectful — no more than 1 request per 3 seconds

### Search Query Syntax
The API supports boolean operators and field-specific searches:
- `all:` — search all fields
- `ti:` — title
- `au:` — author
- `abs:` — abstract
- `cat:` — subject category
- `AND`, `OR`, `ANDNOT` — boolean operators

### Example Queries

Search for robotics papers with "manipulation" in title:
```
http://export.arxiv.org/api/query?search_query=ti:manipulation+AND+cat:cs.RO&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending
```

Search for papers by a specific author in control theory:
```
http://export.arxiv.org/api/query?search_query=au:Russell+AND+cat:cs.AI&start=0&max_results=25
```

Search for recent papers on task planning:
```
http://export.arxiv.org/api/query?search_query=all:task+planning+AND+cat:cs.RO&sortBy=submittedDate&sortOrder=descending&max_results=50
```

## Metadata Fields
Each result in the Atom response includes:
- `title` — paper title
- `author` — list of authors with affiliation (if provided)
- `summary` — abstract
- `published` — original submission date
- `updated` — last update date
- `arxiv:primary_category` — primary subject classification
- `category` — all subject categories (tags)
- `id` — arXiv URL (permanent identifier)
- `link` — links to abstract page, PDF, DOI (if available)
- `arxiv:doi` — DOI if published in a journal
- `arxiv:journal_ref` — journal reference if published
- `arxiv:comment` — author comments (page count, conference info)

## Strengths
- Fastest source for brand-new research (often days/weeks before formal publication)
- No paywall — guaranteed full text access
- Well-structured API with category-based filtering
- Strong coverage of robotics, AI, control theory, optimization
- Links to subsequent journal publications when available
- PDF direct download available for every paper

## Limitations
- No peer review — quality varies significantly
- Not all preprints become published papers
- Metadata is less standardized than in Crossref or OpenAlex
- Author disambiguation is limited (no ORCID integration in search)
- Citation data is NOT available (no citation counts)
- Some older papers may lack full metadata
- No impact metrics

## Integration Notes
- For citation analysis, pair with Semantic Scholar or OpenAlex
- For DOI resolution and journal metadata, pair with Crossref
- The Atom XML response can be parsed with Python's `feedparser` library
- Consider using `arxiv` Python package (`pip install arxiv`) for convenient wrapper
- arXiv IDs follow the format `YYMM.NNNNN` (e.g., `2301.12345`)

## Recommended Use in Literature Review
arXiv is ideal for:
1. Finding the latest methods and architectures before they appear in journals
2. Surveying current research trends in robotics/AI
3. Accessing full-text PDFs for detailed reading
4. Identifying preprints that may later appear at top venues (NeurIPS, ICRA, IROS, etc.)
