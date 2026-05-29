# Batch Download Techniques (PhD Thesis Butler)

Techniques discovered during the MSU + SPbSU bulk download (2026-05).

## Timeout & Resilience

Batch download scripts MUST use aggressive timeouts. A single hung connection stalls the entire batch.

```python
# Good pattern — separate timeouts for page fetch vs file download
TIMEOUT_PAGE = 8   # seconds for HTML page
TIMEOUT_FILE = 15  # seconds for PDF file

def safe_curl(url, timeout=TIMEOUT_PAGE):
    """Curl with strict timeouts, returns (success, output)"""
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout), url, 
             "--connect-timeout", "5", "--retry", "1", "--retry-delay", "1"],
            capture_output=True, text=True, timeout=timeout+5
        )
        return True, r.stdout
    except subprocess.TimeoutExpired:
        return False, ""
```

**Key: `--connect-timeout` + `--max-time` + `subprocess timeout` = triple protection.**

## Subject Extraction (SPbSU)

SPbSU author pages contain the subject in this format:
```
Диссертация на соискание ученой степени кандидата химических наук
```

Regex: `r'(?:кандидата|доктора)\s+([а-яё]+\s+наук)'`

**Pitfall:** The page also has "Научная специальность 5.8.2. Теория и методика обучения и воспитания..." which contains `наук` and can be incorrectly matched. Always anchor to the degree line (кандидата/доктора).

## Folder Name Length Protection

VAK specialty names can be extremely long (>200 chars). Sanity-check before creating folders:

```python
if len(author_folder) > 80 or len(author_folder) < 5:
    # Skip — something went wrong with parsing
    continue
```

## MSU File UUID Resolution

MSU stores files as UUIDs, not filenames. Steps to get them:

1. Fetch API: `https://dissovet.msu.ru/api/dissertations` → gets all metadata
2. For each dissertation: fetch `/dissertation/{code}` → extract UUIDs from `href="/file/dissovet-docs/{uuid}"`
3. Check file sizes with HEAD request: sort largest = dissertation, smallest = avtoreferat
4. Download: `GET /file/dissovet-docs/{uuid}` → returns PDF

## SPbSU Page Structure

| Content | Location on page |
|---------|-----------------|
| Full name | `<title>` tag, first part before `/` |
| Subject | Line with "кандидата XXX наук" or "доктора XXX наук" |
| Title | Line starting with "Тема:" |
| Defense date | First `DD.MM.YYYY` pattern in page (multiple dates exist) |
| PDF links | `href="*.pdf"` — filter out otzyv/prikaz/diplom/zayavlenie |

SPbSU listing: `/dissertatsionnye-sovety-spbgu/proshedshie-zashchity-dissertatsij.html?start=N`
N = 0, 20, 40, ..., 1400 (20 per page, ~1412 total).

## File Size Expectations

| Source | Dissertation PDF | Avtoreferat PDF |
|--------|-----------------|-----------------|
| MSU | 2-15 MB | ~50-100 KB |
| SPbSU | 0.5-6 MB | Rarely available separately |

## Author Name Sanity

The author name on SPbSU pages can contain the VAK code line if regex is greedy. Filter lines with `/` transliteration and exclude lines containing 'Научная', 'специальность', 'Диссертация'.

## Quality Check After Download

```bash
# Check PDF header (must start with %PDF)
head -c 10 file.pdf | xxd

# Count valid PDFs
find data -name "диссертация.pdf" -exec sh -c 'head -c 4 "$1" | grep -q "%PDF"' _ {} \; -print | wc -l

# Find missing or empty files
find data -name "диссертация.pdf" -size -1000c
```
