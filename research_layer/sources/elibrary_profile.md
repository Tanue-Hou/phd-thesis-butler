# eLIBRARY Source Profile (v5.2)

## Platform
eLIBRARY.RU / РИНЦ (Russian Science Citation Index)

## URL Pattern
- Article: `https://elibrary.ru/item.asp?id={article_id}`
- Author: `https://elibrary.ru/author.asp?id={author_id}`

## Field Mapping (raw → normalized)

| Raw field                | Normalized field        | Notes                              |
|--------------------------|-------------------------|------------------------------------|
| elibrary_article_id      | elibrary_id             | String, e.g. "12345678"           |
| title                    | title_ru                |                                    |
| title_en                 | title_en                |                                    |
| author_list              | authors                 | Array of "Surname I.O."           |
| publication_year         | year                    | Integer                            |
| journal_name             | journal                 |                                    |
| doi                      | doi                     |                                    |
| citations_rinc           | rinc_citation_count     | Integer or null                    |
| keywords                 | keywords_ru             | Array of strings                   |
| abstract                 | abstract_ru             |                                    |
| fulltext                 | full_text_status        | Map: open→open, preview→preview_only |
| url                      | url                     |                                    |
| type                     | publication_type        | Map: journal_article, conference_paper, etc. |
| platform                 | source_platform         | Always "elibrary"                  |

## Specialty → Discipline Cluster Mapping

| VAK Code Prefix | Cluster               |
|-----------------|-----------------------|
| 05.13           | AUTOMATION_CONTROL    |
| 05.11, 05.12    | AUTOMATION_CONTROL    |
| 05.02           | SCI_TECH              |
| 05.13.11+       | SCI_TECH              |
| 06.01, 06.02    | AGRI_MED              |
| 03.00, 14.00    | AGRI_MED              |
| 13.00, 17.00    | ARTS_SPORTS           |
| 08.00, 22.00    | HUM_POL_ECON          |
| (other)         | UNCLASSIFIED          |
