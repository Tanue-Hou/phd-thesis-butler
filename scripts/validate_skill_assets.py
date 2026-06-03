#!/usr/bin/env python3
"""
validate_skill_assets.py — Validate all skill assets for consistency and integrity.

Fast mode (default): existence checks + BUILD_INFO cross-verify + spot-check first 50 lines.
Deep mode (--deep): full line-by-line content scan of ALL JSONL files.

Exit code 0 = all pass. Exit code 1 = failures.
"""

import json, sys, re, argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
errors = []
warnings = []

CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
CJK_PUNCT_RE = re.compile(r'[，。；：！？、（）【】《》]')
CYRILLIC_RE = re.compile(r'[А-Яа-яЁё]')
VERSION_RE = re.compile(r'(\d+\.\d+(?:\.\d+)?)')

EN_WHITELIST = {
    'DIS', 'AREF', 'UTILS', 'MODEL', 'INTRO', 'SURVEY', 'METHOD', 'EXPERIMENT',
    'RESULT', 'DISCUSSION', 'CONCLUSION', 'TRANSITION', 'FORMAL_DEFS', 'ENGINEERING',
    'CONNECTIVE', 'CONSERVATIVE', 'NUMERIC', 'TECH_LIFE', 'HUM_SOC', 'ART_SPORT',
    'MATH_PHYS', 'GLOBAL', 'CLUSTER', 'DISCIPLINE', 'PINN', 'LoRA', 'UKF', 'ESO',
    'MPC', 'IMU', 'GPS', 'WLS', 'CarSim', 'Matlab', 'Python', 'CC', 'PhD',
    'vitro', 'vivo', 'situ', 'silico', 'et', 'al', 'etc', 'vs', 'via',
    'in', 'on', 'at', 'by', 'to', 'of', 'for', 'with', 'from', 'as',
}

SAMPLE_LIMIT = 20
VALID_CATEGORIES = {
    'INTRO', 'SURVEY', 'MODEL', 'METHOD', 'EXPERIMENT', 'RESULT',
    'DISCUSSION', 'CONCLUSION', 'TRANSITION', 'FORMAL_DEFS', 'ENGINEERING',
    'AREF', 'UTILS',
    # AREF categories (Russian dissertation review standard)
    'АКТУАЛЬНОСТЬ', 'НОВИЗНА', 'ЦЕЛЬ_ЗАДАЧИ', 'МЕТОДЫ',
    'ОБЪЕКТ_ПРЕДМЕТ', 'ПОЛОЖЕНИЯ', 'ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ',
    'ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ', 'АПРОБАЦИЯ', 'ВЫВОДЫ',
    'ПЕРСПЕКТИВЫ', 'СТЕПЕНЬ_РАЗРАБОТАННОСТИ', 'ДОСТОВЕРНОСТЬ',
    'СТРУКТУРА',
}

EXPECTED_DISCIPLINES = [
    'AUTOMATION_CONTROL', 'SCI_TECH', 'AGRI_MED', 'ARTS_SPORTS', 'HUM_POL_ECON',
]

MAX_LEAKED_TEXT_LEN = 500  # strings longer than this may be original text leakage (increased for v5.1 enhanced Russian descriptions)


def e(msg):
    errors.append(msg)
    print(f"  ❌ {msg}")


def w(msg):
    warnings.append(msg)
    print(f"  ⚠️  {msg}")


def ok(msg):
    print(f"  ✅ {msg}")


def normalize_version(v):
    """Normalize version string: strip quotes, whitespace, leading 'v'."""
    v = v.strip().strip('"').strip("'").lstrip('v').rstrip('.')
    # Pad to 3 components: 5.0 -> 5.0.0
    parts = v.split('.')
    while len(parts) < 3:
        parts.append('0')
    return '.'.join(parts)


def get_jsonl_files():
    files = []
    for f in sorted(BASE.rglob("*.jsonl")):
        if ".git" in str(f) or ".v33_backup" in str(f) or ".phd_build" in str(f):
            continue
        if "/data/" in str(f) or "\\data\\" in str(f):
            continue
        files.append(f)
    return files


def check_structure():
    print("\n0️⃣  Structure existence check")
    # Only check dirs that actually exist — skip silently if not present
    optional_dirs = [
        "assets/references/disciplines",
        "assets/references",
        "assets/cluster/TECH_LIFE",
        "assets/cluster/HUM_SOC",
        "assets/global",
        "scripts",
        "evals",
    ]
    for d in optional_dirs:
        if (BASE / d).is_dir():
            ok(f"Directory exists: {d}/")
        else:
            w(f"Optional directory missing: {d}/")

    # Discipline JSON files (v5.1 core asset)
    disc_dir = BASE / "assets/references/disciplines"
    if disc_dir.is_dir():
        json_files = list(disc_dir.glob("*.json"))
        ok(f"{len(json_files)} discipline JSON files found")
        found_names = {f.stem for f in json_files}
        for name in EXPECTED_DISCIPLINES:
            if name in found_names:
                ok(f"  Discipline: {name}.json")
            else:
                e(f"Missing discipline JSON: {name}.json")
    else:
        e("Discipline directory not found: assets/references/disciplines/")

    ref_dir = BASE / "assets/references"
    if ref_dir.is_dir():
        ref_files = list(ref_dir.glob("*.json")) + list(ref_dir.glob("*.md"))
        ok(f"{len(ref_files)} reference files")


def extract_version_from_file(path):
    """Extract version string from a file (YAML front-matter or plain text)."""
    try:
        with open(path, encoding='utf-8') as f:
            content = f.read(4096)
    except Exception:
        return None

    # Try YAML front-matter: version: "5.0"
    m = re.search(r'^version:\s*["\']?(\d[\d.]*)["\']?', content, re.MULTILINE)
    if m:
        return m.group(1)
    # Try markdown heading: # ... v5.0
    m = re.search(r'v(\d+\.\d+(?:\.\d+)?)', content)
    if m:
        return m.group(1)
    # Try JSON: "version": "5.0.0"
    m = re.search(r'"version"\s*:\s*"(\d[\d.]*)"', content)
    if m:
        return m.group(1)
    return None


def check_build_info():
    print("\n🔢 BUILD_INFO / SKILL / README version consistency check")
    bi_path = BASE / "BUILD_INFO.json"
    if not bi_path.exists():
        e("BUILD_INFO.json not found")
        return

    with open(bi_path) as f:
        bi = json.load(f)

    bi_version = bi.get("version", "")
    ok(f"BUILD_INFO version: {bi_version}")

    versions = {"BUILD_INFO.json": bi_version}

    skill_path = BASE / "SKILL.md"
    if skill_path.exists():
        sv = extract_version_from_file(skill_path)
        if sv:
            versions["SKILL.md"] = sv
            ok(f"SKILL.md version: {sv}")
        else:
            w("Could not extract version from SKILL.md")
    else:
        w("SKILL.md not found")

    readme_path = BASE / "README.md"
    if readme_path.exists():
        rv = extract_version_from_file(readme_path)
        if rv:
            versions["README.md"] = rv
            ok(f"README.md version: {rv}")
        else:
            w("Could not extract version from README.md")
    else:
        w("README.md not found")

    # Normalize and compare
    norm = {}
    for fname, ver in versions.items():
        nv = normalize_version(ver)
        norm[fname] = nv

    unique_versions = set(norm.values())
    if len(unique_versions) == 1:
        ok(f"All versions consistent: {unique_versions.pop()}")
    else:
        for fname, nv in norm.items():
            e(f"Version mismatch: {fname} = {nv}")


def check_discipline_jsons():
    """Validate discipline JSON files for v5.1 requirements."""
    print("\n📚 v5.1 Discipline JSON validation")
    disc_dir = BASE / "assets/references/disciplines"
    if not disc_dir.is_dir():
        e("Cannot validate disciplines — directory missing")
        return

    for name in EXPECTED_DISCIPLINES:
        fpath = disc_dir / f"{name}.json"
        if not fpath.exists():
            continue  # already reported in check_structure
        try:
            with open(fpath, encoding='utf-8') as f:
                data = json.load(f)
            ok(f"{name}.json: valid JSON")
        except json.JSONDecodeError as ex:
            e(f"{name}.json: JSON parse error: {ex}")
            continue

        # Check top-level keys
        if "cluster" not in data:
            e(f"{name}.json: missing 'cluster' key")

        # Check structure.typical_structure for chapter_count > 30 warning
        struct = data.get("structure", {})
        typical = struct.get("typical_structure", {})
        median_ch = typical.get("median_chapters", 0)
        if isinstance(median_ch, (int, float)) and median_ch > 30:
            w(f"{name}.json: median_chapters={median_ch} > 30 — "
              f"do not treat as strong evidence for typical structure")

        # Check for long text leakage in deep_writing_patterns and logic_chain
        _check_text_leakage(name, data)

    # Also check UNKNOWN.json if present
    unknown_path = disc_dir / "UNKNOWN.json"
    if unknown_path.exists():
        try:
            with open(unknown_path, encoding='utf-8') as f:
                json.load(f)
            ok("UNKNOWN.json: valid JSON")
        except json.JSONDecodeError as ex:
            e(f"UNKNOWN.json: JSON parse error: {ex}")


def _check_text_leakage(name, data):
    """Check for long original-text leakage in discipline JSONs."""
    def scan_strings(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                scan_strings(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                scan_strings(item, f"{path}[{i}]")
        elif isinstance(obj, str):
            # Long strings may be original text leakage
            if len(obj) > MAX_LEAKED_TEXT_LEN:
                # Check if it looks like structured metadata vs. original text
                if CYRILLIC_RE.search(obj) and any(c in obj for c in '.!?,;:'):
                    w(f"{name}.json{path}: possible text leakage ({len(obj)} chars): "
                      f"{obj[:80]}...")
            # Check for CJK in discipline JSONs (should be Russian/metadata)
            if CJK_RE.search(obj):
                e(f"{name}.json{path}: CJK text found: {obj[:80]}")

    scan_strings(data)


def check_jsonl_content(deep=False):
    """Check JSONL files for content validity."""
    mode = "deep" if deep else f"fast (up to {SAMPLE_LIMIT}/file)"
    print(f"\n🔎 JSONL content check ({mode})")

    jsonl_files = get_jsonl_files()
    checked_lines = 0
    empty_files = 0

    for f in jsonl_files:
        if f.stat().st_size == 0:
            empty_files += 1
            continue

        with open(f, encoding='utf-8') as fh:
            for i, line in enumerate(fh, 1):
                if not deep and i > SAMPLE_LIMIT:
                    break
                line = line.strip()
                if not line:
                    continue
                checked_lines += 1
                try:
                    d = json.loads(line)
                except Exception:
                    e(f"{f.relative_to(BASE)}:{i}: JSON parse error")
                    continue

                t = d.get("template") or d.get("text", "")
                qs = d.get("quality_score")
                cat = d.get("category", "")

                if qs is not None and qs not in (0, 1, 2):
                    e(f"{f.relative_to(BASE)}:{i}: invalid quality_score={qs}")
                if cat and cat not in VALID_CATEGORIES:
                    e(f"{f.relative_to(BASE)}:{i}: unknown category '{cat}'")

                # CJK check — skip if entry is tagged as mixed
                v5_lang = d.get('v5_lang', 'ru')
                if v5_lang != 'mixed':
                    for key in ('template', 'text'):
                        val = d.get(key, "")
                        if isinstance(val, str) and CJK_RE.search(val):
                            e(f"{f.relative_to(BASE)}:{i}: CJK in '{key}': {val[:60]}")
                        elif isinstance(val, list):
                            for j, item in enumerate(val):
                                if isinstance(item, str) and CJK_RE.search(item):
                                    e(f"{f.relative_to(BASE)}:{i}: CJK in '{key}[{j}]': {item[:60]}")
                
                # Check for non-Russian template — skip if tagged as mixed
                if t and not CYRILLIC_RE.search(t) and v5_lang != 'mixed':
                    e(f"{f.relative_to(BASE)}:{i}: non-Russian template: {t[:60]}")

    ok(f"{len(jsonl_files)} files, {checked_lines} lines checked")
    if empty_files:
        ok(f"{empty_files} empty files (skipped)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--deep", action="store_true")
    args = parser.parse_args()

    print("=" * 60)
    print(f"Skill Asset Validation  |  {BASE.name}")
    print(f"Mode: {'deep' if args.deep else 'fast'}")
    print("=" * 60)

    check_structure()
    check_build_info()
    check_discipline_jsons()
    check_jsonl_content(deep=args.deep)

    print(f"\n{'=' * 60}")
    if warnings:
        print(f"\n⚠️  {len(warnings)} warning(s)")
    if errors:
        print(f"\n❌ FAILED — {len(errors)} error(s)")
        sys.exit(1)
    else:
        print(f"\n✅ ALL CHECKS PASSED ({len(warnings)} warning(s))")
        sys.exit(0)


if __name__ == "__main__":
    main()
