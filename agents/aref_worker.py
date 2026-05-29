#!/usr/bin/env python3
"""
AREF Worker — автореферат 抽取 + G1 门控
从 queue/aref_todo/ 领取任务 → 抽取 → 写 raw JSONL → 运行 G1
与 DIS worker 独立运行，互不干扰
"""

import json, os, sys, re, time, subprocess, shutil
from pathlib import Path

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")
CACHE_DIR = Path(f"/tmp/.cache/phd-thesis-butler/aref_worker_{os.getpid()}")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

MIMO_API = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
MIMO_MODEL = "mimo-v2.5"

def get_api_key():
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
    return text[:15000]  # Truncate

def call_mimo_aref(pdf_text, subject):
    """Call mimo-v2.5 to extract AREF templates — with retry+backoff for 429"""
    api_key = get_api_key()
    if not api_key:
        return {"error": "XIAOMI_API_KEY not found"}

    system_prompt = f"""Ты — ассистент по извлечению шаблонов академического письма из АВТОРЕФЕРАТОВ диссертаций.

Автореферат — это краткое изложение диссертации (16-24 стр.), содержащее:
- АКТУАЛЬНОСТЬ темы (актуальность темы исследования)
- НОВИЗНА (научная новизна)  
- ЦЕЛЬ И ЗАДАЧИ (цель и задачи исследования)
- ОБЪЕКТ И ПРЕДМЕТ (объект и предмет исследования)
- МЕТОДЫ (методология и методы)
- ПОЛОЖЕНИЯ (положения, выносимые на защиту)
- ТЕОРЕТИЧЕСКАЯ ЗНАЧИМОСТЬ
- ПРАКТИЧЕСКАЯ ЗНАЧИМОСТЬ
- АПРОБАЦИЯ (апробация результатов)
- ВЫВОДЫ (основные выводы)
- ПЕРСПЕКТИВЫ (перспективы дальнейшей разработки)

Извлеки 4-10 шаблонных выражений из предоставленного текста. Для каждого шаблона укажи:

1. template: выражение с [...] вместо специфических терминов (сохрани структуру)
2. category: АКТУАЛЬНОСТЬ|НОВИЗНА|ЦЕЛЬ_ЗАДАЧИ|ОБЪЕКТ_ПРЕДМЕТ|МЕТОДЫ|ПОЛОЖЕНИЯ|ТЕОРЕТИЧЕСКАЯ_ЗНАЧИМОСТЬ|ПРАКТИЧЕСКАЯ_ЗНАЧИМОСТЬ|АПРОБАЦИЯ|ВЫВОДЫ|ПЕРСПЕКТИВЫ
3. subtype: уточняющий подтип
4. when_to_use: когда использовать этот шаблон (на русском, 1 фраза)
5. common_mistakes: типичные ошибки (массив, 1-2 пункта)
6. quality_score: 2 (отличный, междисциплинарный) | 1 (хороший, требует адаптации) | 0 (слишком специфичный)

Дисциплина: {subject}

ВАЖНО:
- Используй только [...] для замены переменных частей
- НЕ копируй целые предложения — только структурные шаблоны
- Авторефераты имеют формальную структуру — ищи типовые клише для каждого раздела
- quality_score=2 только если шаблон действительно междисциплинарный

Формат ответа (строго JSON-массив):
[{{"template": "...", "category": "...", "subtype": "...", "when_to_use": "...", "common_mistakes": ["..."], "quality_score": 2}}]"""

    payload = json.dumps({
        "model": MIMO_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Извлеки шаблоны из этого автореферата (дисциплина: {subject}):\n\n{pdf_text[:12000]}"}
        ],
        "max_tokens": 4096,
        "temperature": 0.3,
    })

    max_retries = 5
    for attempt in range(max_retries):
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
            # Check for API-level errors (429, etc)
            if "error" in resp:
                code = resp["error"].get("code", "")
                if code == "429":
                    wait = min(2 ** attempt * 5, 60)  # 5s, 10s, 20s, 40s, 60s
                    time.sleep(wait)
                    continue
                return {"error": f"API error {code}: {resp['error'].get('message', '')}"}
            if "choices" in resp and len(resp["choices"]) > 0:
                content = resp["choices"][0]["message"]["content"]
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                return json.loads(content)
            return {"error": "no choices in response", "raw": result.stdout[:300]}
        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt * 3)
                continue
            return {"error": f"JSON decode: {e}"}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt * 3)
                continue
            return {"error": str(e)}

    return {"error": "max retries exhausted"}

def g1_check(entries, pdf_path):
    """Gate 1: JSON parsable 100%, field completeness >=98%, [...] only"""
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
        if "___" in e.get("template", ""):
            return False, "___ placeholder found in template"

    rate = valid / total
    if rate < 0.98:
        return False, f"field completeness {rate:.0%} < 98%"

    return True, f"G1 passed ({total} templates, {rate:.0%} complete)"

def process_aref_job(job_file):
    """Process a single AREF job"""
    with open(job_file) as f:
        job = json.load(f)

    pdf_path = job["pdf_path"]
    subject = job.get("subject", "engineering")

    # Resolve PDF path
    full_pdf = BASE / pdf_path
    if not full_pdf.exists():
        return False, f"PDF not found: {full_pdf}"

    # Extract text from PDF
    text = extract_pdf_text(str(full_pdf))
    if len(text) < 50:
        return False, f"PDF text too short ({len(text)} chars)"

    # Call mimo API with AREF-optimized prompt
    entries = call_mimo_aref(text, subject)
    if isinstance(entries, dict) and "error" in entries:
        return False, f"API error: {entries['error']}"

    # G1 Gate
    ok, msg = g1_check(entries, str(full_pdf))
    if not ok:
        return False, f"G1 failed: {msg}"

    # Add metadata
    for e in entries:
        e["source"] = "MSU"
        e["doc_type"] = "автореферат"
        e["subject"] = subject
        e["pdf_id"] = job.get("id", "")
        if "slots" not in e:
            e["slots"] = []

    return True, entries

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", help="Job file path")
    parser.add_argument("--output", "-o", help="Output directory", default="data/raw/AREF")
    args = parser.parse_args()

    with open(args.job) as f:
        job = json.load(f)

    ok, result = process_aref_job(args.job)

    if ok:
        source = "MSU"
        out_dir = BASE / args.output / source
        out_dir.mkdir(parents=True, exist_ok=True)
        tmp_file = out_dir / f"{job['id']}.tmp"
        final_file = out_dir / f"{job['id']}.jsonl"

        with open(tmp_file, 'w') as f:
            for entry in result:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        os.rename(tmp_file, final_file)

        print(f"OK {job['id']}: {len(result)} AREF templates -> {final_file}")
    else:
        print(f"FAIL {job['id']}: {result}")
        sys.exit(1)
