#!/usr/bin/env python3
"""
Worker — PDF 抽取 + G1 门控
从 queue/todo 领取任务 → 抽取 → 写 raw JSONL → 运行 G1
"""

import json, os, sys, re, time, subprocess, shutil
from pathlib import Path

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")
QUEUE = BASE / "queue"
CACHE_DIR = Path(f"/tmp/.cache/phd-thesis-butler/worker_{os.getpid()}")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MIMO_API = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
MIMO_MODEL = "mimo-v2.5"

def get_api_key():
    """Get XIAOMI_API_KEY from env or .env"""
    key = os.environ.get("XIAOMI_API_KEY", "")
    if key: return key
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("XIAOMI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip("'\"").strip()
    return ""

def extract_pdf_text(pdf_path):
    """Extract text from PDF using PyMuPDF"""
    import fitz
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text[:15000]  # Truncate to avoid token limits

def call_mimo(pdf_text, subject, category_hint=""):
    """Call mimo-v2.5 to extract templates from text"""
    api_key = get_api_key()
    if not api_key:
        return {"error": "XIAOMI_API_KEY not found"}

    system_prompt = f"""Ты — ассистент по извлечению шаблонов академического письма из диссертаций.

Извлеки 3-7 шаблонных выражений из предоставленного текста. Для каждого шаблона укажи:

1. template: выражение с [...] вместо специфических терминов (сохрани структуру)
2. category: INTRO|SURVEY|MODEL|METHOD|EXPERIMENT|RESULT|DISCUSSION|CONCLUSION|TRANSITION|FORMAL_DEFS
3. subtype: уточняющий подтип
4. when_to_use: когда использовать этот шаблон (на русском, 1 фраза)
5. common_mistakes: типичные ошибки (массив, 1-2 пункта)
6. quality_score: 2 (отличный, междисциплинарный) | 1 (хороший, требует адаптации)

Дисциплина: {subject}

ВАЖНО:
- Используй только [...] для замены переменных частей
- НЕ копируй целые предложения — только структурные шаблоны
- quality_score=2 только если шаблон действительно междисциплинарный

Формат ответа (строго JSON-массив):
[{{"template": "...", "category": "...", "subtype": "...", "when_to_use": "...", "common_mistakes": ["..."], "quality_score": 2}}]"""

    payload = json.dumps({
        "model": MIMO_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Извлеки шаблоны из этого текста (категория: {category_hint}):\n\n{pdf_text[:12000]}"}
        ],
        "max_tokens": 4096,
        "temperature": 0.3,
    })

    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "120",
             "-X", "POST", MIMO_API,
             "-H", "Content-Type: application/json",
             "-H", f"Authorization: Bearer {api_key}",
             "-d", payload],
            capture_output=True, text=True, timeout=130
        )
        resp = json.loads(result.stdout)
        if "choices" in resp and len(resp["choices"]) > 0:
            content = resp["choices"][0]["message"]["content"]
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        return {"error": "no choices in response", "raw": result.stdout[:500]}
    except Exception as e:
        return {"error": str(e)}

def g1_check(entries, pdf_path):
    """Gate 1: JSON parsable 100%, field completeness ≥98%, [...] only"""
    if isinstance(entries, dict) and "error" in entries:
        return False, entries["error"]

    total = len(entries)
    if total == 0:
        return False, "no templates extracted"

    valid = 0
    for e in entries:
        has_template = bool(e.get("template"))
        has_category = bool(e.get("category"))
        has_subtype = bool(e.get("subtype"))
        has_quality = e.get("quality_score") is not None
        if has_template and has_category and has_subtype and has_quality:
            valid += 1
        # Check for ___
        if "___" in e.get("template", ""):
            return False, "___ placeholder found in template"

    rate = valid / total
    if rate < 0.98:
        return False, f"field completeness {rate:.0%} < 98%"

    return True, f"G1 passed ({total} templates, {rate:.0%} complete)"

def process_job(job_file):
    """Process a single job"""
    with open(job_file) as f:
        job = json.load(f)

    pdf_path = job["pdf_path"]
    subject = job.get("subject", "engineering")
    category_hint = job.get("category_hint", "")

    # Extract text from PDF
    text = extract_pdf_text(pdf_path)
    if len(text) < 50:
        return False, f"PDF text too short ({len(text)} chars)"

    # Call mimo API
    entries = call_mimo(text, subject, category_hint)
    if isinstance(entries, dict) and "error" in entries:
        return False, f"API error: {entries['error']}"

    # G1 Gate
    ok, msg = g1_check(entries, pdf_path)
    if not ok:
        return False, f"G1 failed: {msg}"

    # Add metadata
    for e in entries:
        e["source"] = job.get("source", "UNKNOWN")
        e["subject"] = subject
        e["pdf_id"] = job.get("id", "")
        if "slots" not in e:
            e["slots"] = []

    return True, entries

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", help="Job file path")
    parser.add_argument("--output", "-o", help="Output directory", default="data/raw")
    args = parser.parse_args()

    with open(args.job) as f:
        job = json.load(f)

    ok, result = process_job(args.job)

    if ok:
        # Atomic write: tmp → rename
        source = job.get("source", "unknown")
        out_dir = BASE / args.output / source
        out_dir.mkdir(parents=True, exist_ok=True)
        tmp_file = out_dir / f"{job['id']}.tmp"
        final_file = out_dir / f"{job['id']}.jsonl"

        with open(tmp_file, 'w') as f:
            for entry in result:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        os.rename(tmp_file, final_file)

        print(f"OK {job['id']}: {len(result)} templates → {final_file}")
    else:
        print(f"FAIL {job['id']}: {result}")
        sys.exit(1)
