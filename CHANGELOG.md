# Changelog

## v5.2.0 — Russian Research Layer (2026-06-04)

### Added
- `research_layer/` — complete research workflow infrastructure
  - `WORKFLOW.md` — 3 research modes (Planning, Intake, Review)
  - `QUERY_STRATEGY.md` — keyword decomposition, synonym expansion, VAK code matching
  - `sources/` — 8 data source profiles (4 Russian + 4 international)
  - `templates/` — 5 discipline-specific search strategy templates
  - `examples/` — 3 sample files for end-to-end validation
- `assets/references/schemas/russian_literature_record.schema.json`
- `assets/references/schemas/russian_dissertation_record.schema.json`
- `scripts/normalize_russian_metadata.py` — metadata standardization
- `scripts/build_literature_review_brief.py` — GOST/Harvard literature review generator
- `scripts/validate_research_layer.py` — 17-item validation gate

### Changed
- SKILL.md: added Research Layer section with 3 modes
- README.md: version bump to 5.2
- BUILD_INFO.json: version/schema to 5.2

### Validation
- validate_skill_assets.py: ✅ 0 errors
- validate_planning_assets.py: ✅ PASS
- validate_research_layer.py: ✅ 17/17 PASS
- smoke_test: ✅ 7/7 PASS
