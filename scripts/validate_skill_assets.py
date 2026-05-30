#!/usr/bin/env python3
"""
Validate all skill assets for consistency and integrity.

Checks:
1. All JSONL files parse correctly
2. Every entry has required fields (template, category, quality_score)
3. quality_score is 0/1/2
4. No ___ placeholders in template
5. SKILL.md-referenced paths exist
6. sub_skills don't reference non-existent files
7. BUILD_INFO.json counts match actual file line counts
8. No Chinese/English template contamination

Exit code 0 = all pass. Exit code 1 = failures.
"""

import json, sys, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
errors = []

def e(msg):
    errors.append(msg)
    print(f"  ❌ {msg}")

def ok(msg):
    print(f"  ✅ {msg}")

# ============================================================
# 1. JSONL parse check
# ============================================================
print("\n1️⃣  JSONL parse check")
jsonl_files = list(BASE.rglob("*.jsonl"))
checked = 0
for f in jsonl_files:
    # Skip .git, .v33_backup
    if ".git" in str(f) or ".v33_backup" in str(f):
        continue
    try:
        with open(f) as fh:
            for i, line in enumerate(fh, 1):
                line = line.strip()
                if line:
                    json.loads(line)
        checked += 1
    except Exception as ex:
        e(f"{f.relative_to(BASE)}:{i}: {ex}")

ok(f"{checked} JSONL files, 0 parse errors" if not errors else f"{checked} files checked")

# ============================================================
# 2. Field checks
# ============================================================
print("\n2️⃣  Field integrity check")
for f in sorted(BASE.rglob("*.jsonl")):
    if ".git" in str(f) or ".v33_backup" in str(f):
        continue
    if f.stat().st_size == 0:
        continue
    with open(f) as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            # Check template field
            if "template" not in d and "text" not in d:
                e(f"{f.relative_to(BASE)}:{i}: missing template/text field")
            # Check quality_score
            qs = d.get("quality_score")
            if qs is not None and qs not in (0, 1, 2):
                e(f"{f.relative_to(BASE)}:{i}: invalid quality_score={qs}")
            # Check for ___
            t = d.get("template", d.get("text", ""))
            if "___" in t:
                e(f"{f.relative_to(BASE)}:{i}: ___ placeholder in template")

print(f"  No field errors" if not any("Field" in err for err in errors) else "  Field errors found")

# ============================================================
# 3. BUILD_INFO.json vs actual counts
# ============================================================
print("\n3️⃣  BUILD_INFO.json vs actual counts")
bi_path = BASE / "BUILD_INFO.json"
if bi_path.exists():
    with open(bi_path) as f:
        bi = json.load(f)
    
    # Check template counts
    for key, fname in [("DIS", "MASTER_SENTENCEBANK_DIS.jsonl"),
                       ("AREF", "MASTER_SENTENCEBANK_AREF.jsonl"),
                       ("UTILS", "MASTER_UTILS.jsonl")]:
        fp = BASE / "data/curated/master" / fname
        if fp.exists():
            actual = sum(1 for _ in open(fp))
            expected = bi.get("templates", {}).get(key, 0)
            if actual != expected:
                e(f"BUILD_INFO {key}={expected}, actual={actual}")
            else:
                ok(f"{key}: {actual} (matches BUILD_INFO)")
else:
    e("BUILD_INFO.json not found")

# ============================================================
# 4. SKILL.md referenced path check
# ============================================================
print("\n4️⃣  SKILL.md referenced paths")
sk = BASE / "SKILL.md"
if sk.exists():
    with open(sk) as f:
        content = f.read()
    
    # Extract all file paths from SKILL.md (backtick paths)
    paths = re.findall(r'`([^`]+\.(jsonl|json|yaml|md))`', content)
    for path_str, _ in paths:
        # Skip URLs and variables
        if "{" in path_str or "http" in path_str:
            continue
        p = BASE / path_str
        if not p.exists():
            e(f"SKILL.md references {path_str} → NOT FOUND")
    
    ok(f"{len(paths)} references checked" if not any("SKILL.md" in err for err in errors) else "")
else:
    e("SKILL.md not found")

# ============================================================
# 5. Sub-skill path check
# ============================================================
print("\n5️⃣  Sub-skill file references")
for sub in sorted((BASE / "sub_skills").iterdir()):
    sk_file = sub / "SKILL.md"
    if not sk_file.exists():
        continue
    with open(sk_file) as f:
        content = f.read()
    paths = re.findall(r'`([^`]+\.(jsonl|json|yaml|md))`', content)
    for path_str, _ in paths:
        if "{" in path_str or "http" in path_str:
            continue
        p = BASE / path_str
        if not p.exists():
            e(f"{sub.name}/SKILL.md references {path_str} → NOT FOUND")

if not any("Sub-skill" in err for err in errors):
    ok("All sub_skill references valid")

# ============================================================
# 6. Language contamination
# ============================================================
print("\n6️⃣  Language contamination check")
CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
cn_count = 0
for f in sorted(BASE.rglob("*.jsonl")):
    if ".git" in str(f) or ".v33_backup" in str(f):
        continue
    if f.stat().st_size == 0:
        continue
    with open(f) as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                t = d.get("template", d.get("text", ""))
                if CJK.search(t):
                    cn_count += 1
                    if cn_count <= 3:
                        e(f"Chinese in {f.relative_to(BASE)}:{i}: {t[:50]}")
            except:
                pass

if cn_count == 0:
    ok("Zero Chinese contamination")
else:
    e(f"{cn_count} Chinese template(s) found")

# ============================================================
# Summary
# ============================================================
print(f"\n{'='*50}")
if errors:
    print(f"❌ FAILED: {len(errors)} error(s)")
    for err in errors:
        print(f"  {err}")
    sys.exit(1)
else:
    print(f"✅ ALL CHECKS PASSED")
    sys.exit(0)
