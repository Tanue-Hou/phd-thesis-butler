# CyberLeninka Source Profile (v5.2)

## Platform
CyberLeninka — Open-access Russian scientific library

## URL Pattern
- Article: `https://cyberleninka.ru/article/n/{slug}`

## Field Mapping (raw → normalized)

| Raw field       | Normalized field     | Notes                                |
|-----------------|----------------------|--------------------------------------|
| title           | title_ru             |                                      |
| title_en        | title_en             | Often available                      |
| authors         | authors              | Array of "Surname I.O."             |
| year            | year                 | Integer                              |
| journal         | journal              |                                      |
| doi             | doi                  |                                      |
| keywords        | keywords_ru          | Array                                |
| abstract        | abstract_ru          |                                      |
| url             | url                  | CyberLeninka article URL             |
| type            | publication_type     | Map to schema enum                   |
| platform        | source_platform      | Always "cyberleninka"                |
| access          | full_text_status     | Usually "open"                       |
