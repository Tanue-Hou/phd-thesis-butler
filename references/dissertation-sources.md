# Russian Dissertation Public Sources

Sources discovered during the PhD Thesis Butler expansion project. Each source has an API or paginated HTML listing that can be programmatically accessed.

## 1. МГУ — dissovet.msu.ru

**URL:** https://dissovet.msu.ru/
**API:** https://dissovet.msu.ru/api/dissertations → returns full JSON metadata (3,826 entries as of 2026-05)
**Per-dissertation page:** `/dissertation/{code}` (code from API's `dissertationCode` field)
**File download:** `/file/dissovet-docs/{uuid}` → returns PDF
**Metadata fields:** guid, fullname, title, dissertationCode, announcedDate, dissovetName, industryName, statusDesc, academicDegreeName

## 2. СПбГУ — disser.spbu.ru

**URL:** https://disser.spbu.ru/
**Past defenses:** `/dissertatsionnye-sovety-spbgu/proshedshie-zashchity-dissertatsij.html`
**Pagination:** `?start=N` where N = 0, 20, 40, ... (20 items per page)
**Total count:** ~1,410 entries (last page at start=1400, partial)
**Also has:** RSS feed at `.feed?type=rss` and `.feed?type=atom`

## 3. disserCat — cross-university aggregator

**URL:** https://www.dissercat.com/
**Volume:** 440,000+ dissertations + 300,000+ free avtoreferaty
**Search:** `/?q={keyword}` (HTML response)
**Free content:** Avtoreferaty (abstracts) are free to download
**Organization:** By VAK specialty codes

## 4. РГБ — search.rsl.ru (Russian State Library)

**URL:** https://search.rsl.ru/
**Note:** Official repository of all defended Russian dissertations. Full text requires registration/library card. Use as metadata fallback.

## Scraping Notes

- MSU uses a SvelteKit SPA; the API endpoint was found by inspecting the app's JS bundle (`/build/app.*.js`)
- SPbSU uses Joomla with standard pagination
- disserCat uses server-rendered HTML, easier to parse than SPAs
- SPbSU's `?start=N` pagination goes to at least N=1400
- All discovered URLs return PDFs with proper Content-Type headers
