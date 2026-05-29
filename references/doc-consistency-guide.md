# Document Consistency Guide — Single Source of Truth

## Problem
When a project has multiple documentation files (README.md, SKILL.md, CHANGELOG.md, PROJECT.md) and data files (MASTER_*.jsonl), the numbers can diverge. Users who spot a contradiction lose trust in the project.

## Root Cause
The same piece of information (total template count, version number, layer sizes) gets manually updated in N places. A missed update in any one creates a silent inconsistency.

## Solution: Single Source of Truth + Audit

### 1. Designate ONE authoritative number
The **SKILL.md frontmatter** is the canonical source for:
- `description`: total count + source breakdown (e.g. "16,735 pure Russian templates from 1,042 dissertations + 361 abstracts")
- `version`: current release version (e.g. "3.2")

### 2. Derive all other docs from this source
Every other file follows the SKILL.md frontmatter:

| File | What to sync | Sync method |
|------|-------------|-------------|
| `README.md` top summary | template count, source universities | Manual edit, verify against SKILL.md |
| `README.md` Current Build table | DIS/AREF/UTILS breakdown, layer sizes | Read actual file line counts, update table |
| `README.md` Phase 4 architecture | GLOBAL/TECH_LIFE/HUM_SOC counts | Read actual JSONL files in assets/ |
| `CHANGELOG.md` entries | version number, change description | Write at commit time, reference SKILL.md version |
| `PROJECT.md` | current version, status | Sync after each release |
| Data files (MASTER_*.jsonl) | actual template counts | Count via `wc -l` or Python |

### 3. Pre-commit verification checklist
Before any `git commit` that touches documentation:
```
1. Count actual data: wc -l data/curated/master/*.jsonl
2. Verify SKILL.md frontmatter matches actual counts
3. Verify README Current Build table matches actual counts
4. Verify README top summary matches SKILL.md description
5. Verify CHANGELOG version matches SKILL.md version
```

### 4. Trilingual README pattern
When maintaining a multilingual README (EN/RU/ZH):
- All three language sections must use the **same** numbers
- Keep numbers as hard values (not "~300") to prevent silent drift
- When updating a number, update ALL three language sections
- Use `<details>` with flag emoji for clean language toggles

### 5. Release workflow
```
1. Update data files → get actual counts
2. Update SKILL.md frontmatter (version + description)
3. Update SKILL.md body (data file references table)
4. Update README (all 3 language sections)
5. Update CHANGELOG
6. git diff — verify no stale numbers remain
7. commit & tag
```

## Audit Script
```python
# Quick consistency check before release:
import json, re
from pathlib import Path

skill_md = Path("SKILL.md").read_text()
version = re.search(r'version: "([^"]+)"', skill_md).group(1)
desc = re.search(r'description: "([^"]+)"', skill_md).group(1)
dis_count = sum(1 for _ in open("data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl"))
aref_count = sum(1 for _ in open("data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl"))
utils_count = sum(1 for _ in open("data/curated/master/MASTER_UTILS.jsonl"))
total = dis_count + aref_count + utils_count
print(f"Files: DIS={dis_count} AREF={aref_count} UTILS={utils_count} Total={total}")
print(f"SKILL.md: version={version}, desc={desc[:60]}...")
print(f"Match: {str(total) in desc}")
```
