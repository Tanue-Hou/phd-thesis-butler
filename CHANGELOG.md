# Changelog

## v5.4.0 — Dissertation Landscape (2026-06-05)

### Added
- `research_layer/landscape/` — Dissertation Landscape Mode with 4 guide documents
  - `DISSERTATION_LANDSCAPE.md` — end-to-end workflow for landscape comparison
  - `AGENTIC_SEARCH.md` — agentic search strategy for DisserCat/eLIBRARY/CyberLeninka/OpenAlex
  - `ZOTERO_PRIVATE_CORPUS.md` — Zotero private corpus integration with capability gate
  - `COMPARISON_RUBRIC.md` — rubric for chapter/methodology/validation comparison
  - 4 example files (dissercat input, zotero input, landscape result JSON, landscape report MD)
- `scripts/build_dissertation_landscape.py` — landscape analysis builder (JSON + Markdown output)
- `scripts/import_zotero_landscape_records.py` — Zotero Local API connector (status/search modes)
- `scripts/validate_dissertation_landscape.py` — 34-item validation gate
- SKILL.md: Dissertation Landscape Mode with trigger conditions, Zotero capability gate, and routing rules

### Changed
- README.md: version header v5.4.0, version history updated (ZH/EN), capability description
- BUILD_INFO.json: version 5.4.0, schema_version 5.4

### Capabilities
- Agentic dissertation search across public Russian dissertation sources
- Zotero private corpus integration with graceful degradation
- 12-section landscape report: source coverage, theme clustering, structure/methodology/validation comparison, user positioning, recommended outline
- read_depth/source_access/structure_confidence annotation on every record
- recommended_outline mappable to planning_layer chapter types
- evidence_layer_routes linking chapters to evidence binding needs

### Validation
- validate_dissertation_landscape.py: passes
- All record examples have read_depth, source_access, structure_confidence
- No large verbatim text in landscape artifacts
- No Zotero local attachment paths in public examples

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
- validate_research_layer.py: ✅ 17/17 PASS
- smoke_test: 7/7 PASS

## v5.2.1 — Research Layer fixes (2026-06-04)

### Fixed
- Version unification: BUILD_INFO/SKILL/README all at 5.2.1
- `normalize_russian_metadata.py`: added `source` field alias support to all call sites
- CJK cleanup in QUERY_STRATEGY.md, WORKFLOW.md, and subtype fields in discipline JSONL
- SKILL.md: version corrected from 5.1.3 to 5.2.1, duplicate Research Layer section removed
- README.md: version corrected from 5.2.3 to 5.2.1
- DisserCat samples: fields renamed to match schema, degree_type normalized
- Research Layer validation: all 17/17 checks pass end-to-end

### Added
- `scripts/build_literature_review_brief.py` added to repository (force-add, exempt from gitignore)

### Validation
- validate_skill_assets.py --deep: 0 errors
- validate_planning_assets.py: PASS
- validate_research_layer.py: ✅ 17/17 PASS
- smoke_test: 7/7 PASS

## v5.1.3 — Runtime reliability (Codex)

See git log for details.
