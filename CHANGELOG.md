# Changelog

## v5.2.0 — Russian Research Layer (2026-06-04)

### Added
- `research_layer/` — research workflow infrastructure with 8 source profiles
- 2 JSON schemas for standardized Russian literature/dissertation records
- `scripts/normalize_russian_metadata.py` — metadata standardization
- `scripts/build_literature_review_brief.py` — literature review generator
- `scripts/validate_research_layer.py` — 17-item validation gate

### Changed
- SKILL.md: added Research Layer reference

### Validation
- validate_skill_assets.py: 0 errors
- validate_planning_assets.py: PASS
- validate_research_layer.py: 17/17 PASS (local)
- smoke_test: 7/7 PASS

## v5.2.1 — Research Layer fixes (2026-06-04)

### Fixed
- Version unification: BUILD_INFO/SKILL/README all at 5.2.1
- `normalize_russian_metadata.py`: added `source` field alias support
- CJK cleanup in QUERY_STRATEGY.md and WORKFLOW.md
- SKILL.md: version corrected from 5.1.3 to 5.2.1
- README.md: version corrected from 5.2.3 to 5.2.1

### Added
- `build_literature_review_brief.py` now tracked in git

### Validation
- validate_skill_assets.py --deep: 0 errors
- validate_planning_assets.py: PASS
- validate_research_layer.py: 20/20 PASS
- smoke_test: 7/7 PASS

## v5.1.3 — Runtime reliability (Codex)

See git log for details.
