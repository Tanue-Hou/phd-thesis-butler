# RSL Source Profile (v5.2)

## Platform
Russian State Library (РГБ) — Dissertations and rare publications

## URL Pattern
- Catalog: `https://search.rsl.ru/record/{rsl_id}`

## Field Mapping (raw → normalized)

| Raw field       | Normalized field  | Notes                                |
|-----------------|-------------------|--------------------------------------|
| title           | title_ru          |                                      |
| author          | author            | Full name                            |
| year            | year              | Integer                              |
| degree          | degree_type       | Map: кандидат→candidate, доктор→doctoral |
| specialty_code  | specialty_code    | VAK code                             |
| specialty_name  | specialty_name    |                                      |
| institution     | institution       |                                      |
| platform        | source_platform   | Always "rsl"                         |
| rsl_id          | rsl_id            | RSL catalogue identifier             |
| keywords        | keywords_ru       | Array                                |
| abstract        | abstract_ru       |                                      |
| access          | full_text_status  | Map: open→open, restricted→needs_institution |
