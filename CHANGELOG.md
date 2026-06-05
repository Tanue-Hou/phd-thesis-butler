# Changelog

## v5.4.1 — Unified Workflow Router (2026-06-05)

### Changed
- SKILL.md: Added Workflow Router section with 4-workflow routing priority, multi-intent handling, and internal layer role assignment. Existing mode docs kept as downstream references.
- README.md: Restructured from flat capability table to 4-workflow model (①俄语润色 ②论文规划 ③文献调研与论文对比 ④证据检查). ZH and EN capability descriptions, hierarchy tree, and architecture sections updated.
- Added `routing/WORKFLOW_ROUTER.md` — centralized routing rules document.

### Key design decisions
- `assets/references/disciplines/` → internal knowledge asset, not a user entry point
- `research_layer/landscape/` → advanced sub-workflow of Research/Literature (Workflow 3), not standalone
- landscape → borrowing from comparative analysis (用户说"同方向论文/Zotero"才激活), no longer independent entry
- Multi-intent: if user asks for both "polish + check citations", Evidence first → Polish
- Layer names in SKILL.md renamed: Research Layer → Research/Literature — Workflow 3, Evidence-Aware Writing → Evidence — Workflow 4, etc.

### Validation
- validate_skill_assets.py: ✅ ALL PASS
- validate_dissertation_landscape.py: ✅ 163/163
- validate_research_layer.py: ✅ 17/17
- validate_evidence_layer.py: ✅ ALL PASS
- validate_planning_assets.py: ✅ 22/22
- smoke_test.sh: ✅ 7/7

## v5.4.0 (hotfix 2026-06-05) — Landscape pipeline stabilization

### Fixed
- **P0**: `structure_confidence` type mismatch — now accepts string ("high"/"medium"/"low"), numeric 0.0-1.0, or None, via `normalize_confidence()` helper
- **P0**: Zotero status check — uses `/api/users/0/items/top?limit=1` instead of `/connector/ping` (which returns HTML); 3-way status: AVAILABLE / APP_RUNNING / UNAVAILABLE
- **P1**: `validation_type: null` crash — null/empty/None now safely handled as "unknown" via `safe_str()`
- **P1**: `read_depth`/`source_access` enums unified — all samples, import script output, and validator now use canonical values
- **P1**: `source_summary` reads `source_name` with fallback chain (`source_name > source_platform > source`)
- **P1**: `year: null` crash — safe comparison with `(r.get("year") or 2025)`
- **P1**: Methodology/validation label generation — `None.replace()` crash fixed via `safe_str()`
- **P1**: Aggressive record merge — reduced from merging 20+ records per theme to zero; now accurately reports 10/8 records

### Enhanced
- Validator: read_depth/source_access enum validation, structure_confidence string/numeric/null, E2E build test on raw samples (--deep mode: 228/228 checks)

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
