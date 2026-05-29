#!/usr/bin/env python3
"""
Consistency Agent — 术语/符号/引用口径一致性检查
"""

import json, sys, re

def check_consistency(original, polished, discipline="ENGINEERING"):
    """Check consistency between original and polished text"""
    issues = []

    # 1. Check that no new numbers/facts were introduced
    orig_nums = set(re.findall(r'\b\d+(?:[.,]\d+)?', original))
    polished_nums = set(re.findall(r'\b\d+(?:[.,]\d+)?', polished))
    new_nums = polished_nums - orig_nums
    if new_nums:
        issues.append({
            "type": "new_numbers",
            "detail": f"Появились новые числа: {list(new_nums)[:5]}",
            "severity": "warning"
        })

    # 2. Check term consistency (simple: same words should appear)
    orig_terms = set(w for w in original.split() if w[0].isupper() and len(w) > 2)
    polished_terms = set(w for w in polished.split() if w[0].isupper() and len(w) > 2)
    missing_terms = orig_terms - polished_terms
    if missing_terms:
        issues.append({
            "type": "missing_terms",
            "detail": f"Пропущены термины: {list(missing_terms)[:5]}",
            "severity": "info"
        })

    # 3. Check discipline-specific patterns
    disc_checks = {
        "MEDICINE": ["пациент", "критерий", "n=", "исследование"],
        "ECONOMICS": ["регресси", "эндогенност", "робастност", "значимост"],
        "MATHEMATICS": ["лемма", "теорема", "доказательств"],
        "ENGINEERING": ["систем", "алгоритм", "параметр", "управлени"],
    }

    if discipline in disc_checks:
        for kw in disc_checks[discipline]:
            if kw in original.lower() and kw not in polished.lower():
                issues.append({
                    "type": "discipline_term_missing",
                    "detail": f"Дисциплинарный термин '{kw}' отсутствует в отредактированном тексте",
                    "severity": "warning"
                })

    # 4. Check for overly strong claims vs original
    strong_patterns = [
        (r'всегда|никогда|абсолютно|полностью|гарантированно', 'категоричные выражения'),
        (r'доказано|бесспорно|несомненно|очевидно, что', 'сильные утверждения без обоснования'),
    ]
    for pattern, desc in strong_patterns:
        new_strong = set(re.findall(pattern, polished.lower())) - set(re.findall(pattern, original.lower()))
        if new_strong:
            issues.append({
                "type": "overclaim",
                "detail": f"Появились {desc}: {new_strong}",
                "severity": "warning"
            })

    status = "ok" if not any(i["severity"] == "warning" for i in issues) else "changed"
    return {"status": status, "issues": issues, "discipline": discipline}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", help="Original text")
    parser.add_argument("--polished", help="Polished text")
    parser.add_argument("--discipline", default="ENGINEERING")
    parser.add_argument("--output", "-o", default="/dev/stdout")
    args = parser.parse_args()

    result = check_consistency(args.original, args.polished, args.discipline)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Consistency: {result['status']}, {len(result['issues'])} issues")
