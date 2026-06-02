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

CJK_RE = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')
CJK_PUNCT_RE = re.compile(r'[，。；：！？、（）【】《》]')
CYRILLIC_RE = re.compile(r'[А-Яа-яЁё]')

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
}


def e(msg):
    errors.append(msg)
    print(f"  ❌ {msg}")


def ok(msg):
    print(f"  ✅ {msg}")


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
    required_dirs = [
        "assets/discipline",
        "assets/cluster/TECH_LIFE",
        "assets/cluster/HUM_SOC",
        "assets/references",
        "scripts",
        "evals",
    ]
    for d in required_dirs:
        if not (BASE / d).is_dir():
            e(f"Missing required directory: {d}/")

    disc_dir = BASE / "assets/discipline"
    if disc_dir.is_dir():
        disc_count = len(list(disc_dir.glob("*.jsonl")))
        ok(f"{disc_count} discipline JSONL files")

    ref_dir = BASE / "assets/references"
    if ref_dir.is_dir():
        ref_files = list(ref_dir.glob("*.json")) + list(ref_dir.glob("*.md"))
        ok(f"{len(ref_files)} reference files")


def check_build_info():
    print("\n🔢 BUILD_INFO consistency check")
    bi_path = BASE / "BUILD_INFO.json"
    if not bi_path.exists():
        e("BUILD_INFO.json not found")
        return
    with open(bi_path) as f:
        bi = json.load(f)

    version = bi.get("version", "")
    ok(f"Version: {version}")

    skill_path = BASE / "SKILL.md"
    if skill_path.exists():
        with open(skill_path) as f:
            for line in f:
                if line.startswith("version:"):
                    skill_ver = line.split('"')[1] if '"' in line else ""
                    if skill_ver == version:
                        ok(f"SKILL.md version matches BUILD_INFO")
                    else:
                        e(f"SKILL.md version ({skill_ver}) != BUILD_INFO ({version})")
                    break


def check_jsonl_content(deep=False):
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
                except:
                    e(f"{f.relative_to(BASE)}:{i}: JSON parse error")
                    continue

                t = d.get("template") or d.get("text", "")
                qs = d.get("quality_score")
                cat = d.get("category", "")

                if qs is not None and qs not in (0, 1, 2):
                    e(f"{f.relative_to(BASE)}:{i}: invalid quality_score={qs}")
                if cat and cat not in VALID_CATEGORIES:
                    # Skip unknown category check for quality/ directories (Russian taxonomy names)
                    if "/quality/" not in str(f) and "\\quality\\" not in str(f):
                        e(f"{f.relative_to(BASE)}:{i}: unknown category '{cat}'")

                for key, val in d.items():
                    if isinstance(val, str):
                        if CJK_RE.search(val):
                            e(f"{f.relative_to(BASE)}:{i}: CJK in '{key}': {val[:60]}")
                    elif isinstance(val, list):
                        for j, item in enumerate(val):
                            if isinstance(item, str) and CJK_RE.search(item):
                                e(f"{f.relative_to(BASE)}:{i}: CJK in '{key}[{j}]': {item[:60]}")

                if t and not CYRILLIC_RE.search(t):
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
    print("=" * 60)

    check_structure()
    check_build_info()
    check_jsonl_content(deep=args.deep)

    print(f"\n{'=' * 60}")
    if errors:
        print(f"\n❌ FAILED — {len(errors)} issue(s)")
        sys.exit(1)
    else:
        print("\n✅ ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
