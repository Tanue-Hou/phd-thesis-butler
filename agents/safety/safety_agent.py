#!/usr/bin/env python3
"""
Safety/QA Agent — 安全审查: 不引入新事实、不夸大、不抄袭、合规提示
"""

import json, sys, re

def safety_check(original, polished, discipline="ENGINEERING"):
    """Safety check on polished text"""
    issues = []

    # 1. Check for new factual claims (numbers, dates, references)
    orig_refs = re.findall(r'\[\d+\]|\(\w+,\s*\d{4}\)', original)
    polished_refs = re.findall(r'\[\d+\]|\(\w+,\s*\d{4}\)', polished)
    new_refs = [r for r in polished_refs if r not in orig_refs]
    if new_refs:
        issues.append({
            "type": "new_references",
            "detail": f"Появились новые ссылки: {new_refs[:3]}",
            "severity": "warning"
        })

    # 2. Check for overly confident language (academic integrity)
    overclaim_patterns = re.findall(
        r'(доказано|бесспорно|несомненно|гарантированно|абсолютно точно|полностью решает)',
        polished, re.IGNORECASE
    )
    new_overclaims = [p for p in overclaim_patterns if p.lower() not in original.lower()]
    if new_overclaims:
        issues.append({
            "type": "overconfident_language",
            "detail": f"Чрезмерно уверенные выражения: {new_overclaims}",
            "severity": "warning",
            "suggestion": "Заменить на: 'свидетельствует', 'позволяет предположить', 'можно сделать вывод'"
        })

    # 3. Check for potential plagiarism risk (exact template copy)
    template_markers = ["___", "[", "]"]
    has_slots = sum(1 for m in template_markers if m in polished)
    if has_slots > 3:
        issues.append({
            "type": "template_leftover",
            "detail": "В тексте остались слоты шаблонов (___, [...])",
            "severity": "error",
            "suggestion": "Заполнить все слоты перед использованием"
        })

    # 4. Check for discipline-specific compliance
    disc_checks = {
        "MEDICINE": {
            "required": ["пациент", "исследование"],
            "advice": "Убедитесь, что указаны критерии включения/исключения и одобрение этического комитета"
        },
        "ECONOMICS": {
            "required": [],
            "advice": "Проверьте указание спецификации, контроля эндогенности и робастности результатов"
        },
    }
    if discipline in disc_checks:
        info = disc_checks[discipline]
        for req in info["required"]:
            if req not in polished.lower():
                issues.append({
                    "type": "discipline_compliance",
                    "detail": f"Требуется упоминание: '{req}'",
                    "severity": "info",
                    "suggestion": info["advice"]
                })

    # 5. Summary
    has_errors = any(i["severity"] == "error" for i in issues)
    has_warnings = any(i["severity"] == "warning" for i in issues)

    return {
        "status": "error" if has_errors else ("warning" if has_warnings else "ok"),
        "issues": issues,
        "discipline": discipline,
        "risk_level": "high" if has_errors else ("medium" if has_warnings else "low"),
        "summary": f"Проверка безопасности: {len(issues)} замечаний."
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", help="Original text")
    parser.add_argument("--polished", help="Polished text")
    parser.add_argument("--discipline", default="ENGINEERING")
    parser.add_argument("--output", "-o", default="/dev/stdout")
    args = parser.parse_args()

    result = safety_check(args.original, args.polished, args.discipline)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Safety: {result['status']}, risk={result['risk_level']}, {len(result['issues'])} issues")
