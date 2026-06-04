# DisserCat Source Profile (v5.2)

## Platform
DisserCat — Russian Dissertation Catalog

## URL Pattern
- Dissertation: `https://www.dissercat.com/content/{slug}`

## Field Mapping (raw → normalized)

| Raw field           | Normalized field     | Notes                                |
|---------------------|----------------------|--------------------------------------|
| title               | title_ru             |                                      |
| author              | author               | Single string, full name             |
| year                | year                 | Integer                              |
| degree              | degree_type          | Map: кандидат→candidate, доктор→doctoral |
| specialty_code      | specialty_code       | VAK code, e.g. "05.13.01"           |
| specialty_name      | specialty_name       |                                      |
| institution         | institution          |                                      |
| platform            | source_platform      | Always "dissercat"                   |
| url                 | dissercat_url        |                                      |
| keywords_ru         | keywords_ru          | Array                                |
| abstract_ru         | abstract_ru          |                                      |
| table_of_contents   | toc_available        | Boolean                              |
| intro_text          | intro_available      | Boolean                              |
| bibliography        | bibliography_available | Boolean                            |
| chapter_count       | chapter_count        | Integer or null                      |
| page_count          | page_count           | Integer or null                      |
| access              | full_text_status     | Map: open→open, preview→preview_only |

## Specialty → Discipline Cluster Mapping
Same as eLIBRARY profile (VAK code prefix mapping).
