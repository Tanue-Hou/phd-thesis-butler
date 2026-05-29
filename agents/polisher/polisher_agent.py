#!/usr/bin/env python3
"""
Polisher Agent — 三级润色（L1语言/L2结构/L3重写）
通过 mimo-v2.5 API 执行
"""

import json, os, sys, subprocess, re
from pathlib import Path

MIMO_API = "https://token-plan-cn.xiaomimimo.com/v1/chat/completions"
MIMO_MODEL = "mimo-v2.5"

def call_mimo(system_prompt, user_prompt, max_tokens=4096):
    """Call mimo-v2.5 API"""
    api_key = os.environ.get("XIAOMI_API_KEY", "")
    if not api_key:
        # Try to read from .env
        env_path = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("XIAOMI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip("'\"")
                        break

    if not api_key:
        return {"error": "XIAOMI_API_KEY not found"}

    payload = json.dumps({
        "model": MIMO_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    })

    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "60",
             "-X", "POST", MIMO_API,
             "-H", "Content-Type: application/json",
             "-H", f"Authorization: Bearer {api_key}",
             "-d", payload],
            capture_output=True, text=True, timeout=65
        )
        resp = json.loads(result.stdout)
        if "choices" in resp and len(resp["choices"]) > 0:
            return resp["choices"][0]["message"]["content"]
        return {"error": result.stdout[:500]}
    except Exception as e:
        return {"error": str(e)}


def polish(text, templates, utils, level="L1", discipline="ENGINEERING"):
    """Polish text using templates + mimo API"""

    level_descriptions = {
        "L1": "Только языковая правка: грамматика, лексика, связки, удаление повторов. НЕ менять структуру предложений, НЕ добавлять новые утверждения.",
        "L2": "Структурная правка: можно переставить предложения, добавить переходы, улучшить логику абзацев. НЕ менять выводы, НЕ добавлять новые факты.",
        "L3": "Академическое переписывание: полная переработка текста с сохранением всех фактов и выводов. НЕ добавлять новые ссылки или данные.",
    }

    system_prompt = f"""Ты — ассистент по академическому письму на русском языке (научные дисциплины).

Твоя задача: {level_descriptions.get(level, level_descriptions["L1"])}

ВАЖНО:
- НЕ добавляй новые факты, цифры, выводы или ссылки
- НЕ меняй научные результаты
- Сохрани все термины без изменений
- Используй академический стиль, соответствующий дисциплине: {discipline}

У тебя есть следующие шаблоны для ориентира (используй их стиль, НЕ копируй их дословно):"""

    if templates:
        system_prompt += "\n\n=== Шаблоны выражений ==="
        for t in templates[:5]:
            tmpl = t.get("template", "")
            usage = t.get("when_to_use", "")
            system_prompt += f"\n- [{t.get('layer','?')}] {tmpl}"
            if usage:
                system_prompt += f"\n  → {usage}"

    if utils:
        system_prompt += "\n\n=== Вспомогательные конструкции ==="
        for u in utils[:3]:
            system_prompt += f"\n- [{u.get('kind','?')}] {u.get('template','')}"

    system_prompt += f"""

Формат ответа (строго JSON):
{{"polished": "отредактированный текст",
 "changes": ["краткое описание каждого изменения"],
 "level": "{level}",
 "discipline": "{discipline}"}}"""

    result = call_mimo(system_prompt, f"Отредактируй следующий текст:\n\n{text}")

    # Try to parse JSON from response
    if isinstance(result, dict) and "error" in result:
        return result

    # Extract JSON from response
    try:
        # Try direct parse
        if result.strip().startswith("{"):
            return json.loads(result)
        # Try to find JSON in code block
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        return {"polished": result, "changes": ["basic polish applied"], "level": level}
    except:
        return {"polished": result, "changes": [], "level": level}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Input text")
    parser.add_argument("--file", help="Input file")
    parser.add_argument("--templates", help="Templates JSON file")
    parser.add_argument("--level", default="L1")
    parser.add_argument("--discipline", default="ENGINEERING")
    parser.add_argument("--output", "-o", default="/dev/stdout")
    args = parser.parse_args()

    text = args.text or ""
    if args.file:
        with open(args.file) as f:
            text = f.read()

    templates_data = []
    utils_data = []
    if args.templates:
        with open(args.templates) as f:
            td = json.load(f)
            templates_data = td.get("templates", [])
            utils_data = td.get("utils", [])

    result = polish(text, templates_data, utils_data, args.level, args.discipline)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    if "polished" in result:
        print(result["polished"][:200] + "..." if len(result["polished"]) > 200 else result["polished"])
