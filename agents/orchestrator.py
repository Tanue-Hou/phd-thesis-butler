#!/usr/bin/env python3
"""
Orchestrator — 端到端润色管线
1. Router → 2. Retriever → 3. Polisher → 4. Consistency → 5. Safety
"""

import json, os, sys, subprocess, re
from pathlib import Path

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")

def run_pipeline(text, filepath="", config_path="", level="L1"):
    """Run full polish pipeline"""
    step_results = {}
    
    # Step 1: Router
    plan_file = BASE / "logs" / "_plan.json"
    subprocess.run(["python3", str(BASE / "agents/router/router_agent.py"),
        "--text", text, "--output", str(plan_file),
        *(["--config", config_path] if config_path else []),
        *(["--file", filepath] if filepath else [])],
        capture_output=True, timeout=10)
    
    with open(plan_file) as f:
        plan = json.load(f)
    step_results["router"] = plan
    
    cluster = plan["discipline_inference"]["cluster"]
    discipline = plan["discipline_inference"]["discipline"]
    category = plan["scene_inference"]["category"]
    
    # Step 2: Retriever
    tmpl_file = BASE / "logs" / "_templates.json"
    subprocess.run(["python3", str(BASE / "agents/retriever/retriever_agent.py"),
        "--plan", str(plan_file), "--output", str(tmpl_file)],
        capture_output=True, timeout=10)
    
    with open(tmpl_file) as f:
        templates = json.load(f)
    step_results["retriever"] = templates
    
    # Step 3: Polisher
    polished_file = BASE / "logs" / "_polished.json"
    
    # Try online (API) mode first
    api_key = os.environ.get("XIAOMI_API_KEY", "")
    if not api_key:
        env_path = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("XIAOMI_API_KEY="):
                        api_key = line.split("=", 1)[1].strip().strip("'\"")
                        break
    
    if api_key:
        # Online mode via Polisher agent
        subprocess.run(["python3", str(BASE / "agents/polisher/polisher_agent.py"),
            "--text", text, "--templates", str(tmpl_file),
            "--level", level, "--discipline", discipline,
            "--output", str(polished_file)],
            capture_output=True, timeout=70)
    else:
        # Offline mode: rules-based polishing
        polished = offline_polish(text, templates, level, discipline)
        with open(polished_file, 'w', encoding='utf-8') as f:
            json.dump(polished, f, ensure_ascii=False, indent=2)
    
    with open(polished_file) as f:
        polished_result = json.load(f)
    step_results["polisher"] = polished_result
    
    polished_text = polished_result.get("polished", text)
    
    # Step 4: Consistency
    cons_file = BASE / "logs" / "_consistency.json"
    subprocess.run(["python3", str(BASE / "agents/consistency/consistency_agent.py"),
        "--original", text, "--polished", polished_text,
        "--discipline", discipline, "--output", str(cons_file)],
        capture_output=True, timeout=10)
    
    with open(cons_file) as f:
        cons_result = json.load(f)
    step_results["consistency"] = cons_result
    
    # Step 5: Safety
    safe_file = BASE / "logs" / "_safety.json"
    subprocess.run(["python3", str(BASE / "agents/safety/safety_agent.py"),
        "--original", text, "--polished", polished_text,
        "--discipline", discipline, "--output", str(safe_file)],
        capture_output=True, timeout=10)
    
    with open(safe_file) as f:
        safe_result = json.load(f)
    step_results["safety"] = safe_result
    
    # Build output
    changes = polished_result.get("changes", [])
    if cons_result.get("issues"):
        changes.append(f"一致性: {len(cons_result['issues'])} замечаний")
    if safe_result.get("risk_level") != "low":
        changes.append(f"⚠️ {safe_result.get('summary', '')}")
    
    output = {
        "polished": polished_text,
        "changes": changes[:3],
        "discipline": f"{discipline}[{cluster}]",
        "scene": f"{category}",
        "level": level,
        "risk": safe_result.get("risk_level", "low"),
        "templates_found": templates.get("count", 0),
    }
    return output


def offline_polish(text, templates, level, discipline):
    """Offline rules-based polishing (no API key needed)"""
    polished = text
    
    # Basic rule-based fixes
    # 1. Remove "Во-первых" paragraph openers (not academic)
    polished = re.sub(r'^Во-первых,\s*', '', polished)
    polished = re.sub(r'^Во-вторых,\s*', '', polished)
    
    # 2. Strengthen weak connectors
    polished = polished.replace(' и т.д.', ' и др.')
    polished = polished.replace('и так далее', 'и тому подобное')
    
    # 3. Add academic hedging where appropriate
    if 'лучше' in polished:
        polished = polished.replace('лучше', 'обеспечивает более высокую эффективность')
    if 'хуже' in polished:
        polished = polished.replace('хуже', 'уступает по показателю')
    if 'хороший' in polished or 'хорошие' in polished:
        polished = re.sub(r'хорош[ие]', 'высокие', polished)
    
    changes = ["Применены базовые правила академического стиля"]
    
    if templates.get("templates"):
        tmpl = templates["templates"][0].get("template", "")
        changes.append(f"Шаблон-ориентир: {tmpl[:50]}...")
    
    if templates.get("utils"):
        changes.append(f"Добавлены консервативные конструкции")
    
    return {"polished": polished, "changes": changes, "level": level, "discipline": discipline, "mode": "offline"}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", help="Input text")
    parser.add_argument("--file", help="Input file path")
    parser.add_argument("--level", default="L1", choices=["L1", "L2"])
    parser.add_argument("--output", "-o", default="/dev/stdout")
    args = parser.parse_args()
    
    text = args.text or ""
    if args.file:
        with open(args.file) as f:
            text = f.read()
    
    if not text:
        print("ERROR: no text provided")
        sys.exit(1)
    
    result = run_pipeline(text, args.file or "", level=args.level)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("📝 润色后文本")
    print(f"{'='*60}")
    print(result["polished"])
    print(f"\n{'='*60}")
    print("✏️ 改动摘要")
    print(f"{'='*60}")
    for c in result["changes"]:
        print(f"  • {c}")
    print(f"\n学科: {result['discipline']} | 场景: {result['scene']} | 级别: {result['level']}")
    print(f"模板命中: {result['templates_found']} | 风险: {result['risk']}")
