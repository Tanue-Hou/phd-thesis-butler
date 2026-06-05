#!/usr/bin/env python3
"""
render_citation_gap_report.py

Converts citation_gap_report.json into a human-readable Markdown report.

Usage:
    python3 scripts/render_citation_gap_report.py --input gap.json --output gap_report.md

Pure Python standard library — no external dependencies.
"""

import argparse
import json
import sys
from datetime import datetime

# ── Russian labels ──────────────────────────────────────────────────────────

RISK_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}

CLAIM_TYPE_LABELS = {
    "factual_claim": "Фактологический",
    "methodological_claim": "Методологический",
    "evaluative_claim": "Оценочный",
    "gap_claim": "Заявление о пробеле",
    "contribution_claim": "Заявление о вкладе",
    "theoretical_claim": "Теоретический",
    "descriptive_claim": "Описательный",
    "common_knowledge": "Общеизвестный факт",
    "research_gap_claim": "Пробел в исследованиях",
    "result_claim": "Результат",
    "background_claim": "Фоновый контекст",
}

EVIDENCE_ROLE_LABELS = {
    "background_context": "фоновый контекст",
    "research_gap": "пробел в исследованиях",
    "definition": "определение",
    "method_basis": "обоснование метода",
    "method_comparison": "сравнение методов",
    "benchmark": "эталон",
    "validation_standard": "стандарт валидации",
    "empirical_support": "эмпирическая поддержка",
    "contradiction": "противоречие",
    "contribution_positioning": "позиционирование вклада",
    "structure_reference": "структурная ссылка",
    "supplementary_detail": "дополнительная деталь",
}

RISK_LABELS = {
    "critical": "критический",
    "high": "высокий",
    "medium": "средний",
    "low": "низкий",
}


def risk_sort_key(claim: dict) -> tuple:
    return (RISK_ORDER.get(claim.get("risk_level", "low"), 9), claim.get("claim_id", ""))


def pct(n: int, d: int) -> str:
    if d == 0:
        return "0.0"
    return f"{n / d * 100:.1f}"


def render(data: dict) -> str:
    lines: list[str] = []
    w = lines.append  # shorthand

    chapter = data.get("chapter", "—")
    report_id = data.get("report_id", "—")
    generated_at = data.get("generated_at", "")

    # ── Title ──
    w(f"# Отчёт об анализе цитирований — {chapter}")
    w("")
    w(f"Идентификатор отчёта: `{report_id}`")
    if generated_at:
        w(f"Дата формирования: {generated_at}")
    w("")

    claims = data.get("claims", [])

    # ── Summary ──
    summary = data.get("summary", {})
    total = summary.get("total_claims", len(claims))
    needs_cite = summary.get("needs_citation", 0)
    n_covered = summary.get("covered", 0)
    n_partial = summary.get("partial", 0)
    n_missing = summary.get("missing", 0)
    n_not_needed = summary.get("not_needed", 0)
    evidence_cov = summary.get("evidence_coverage_ratio")
    overall_res = summary.get("overall_resolution_ratio")

    # Compute high-risk count
    high_risk = sum(1 for c in claims if c.get("risk_level") in ("critical", "high"))

    w("## 一、总体风险")
    w("")
    w(f"- **总论断数**: {total}")
    w(f"- **需引用**: {needs_cite}")
    if evidence_cov is not None:
        w(f"- **证据覆盖率**: {evidence_cov * 100:.1f}%")
    else:
        denom = n_covered + n_partial + n_missing
        w(f"- **证据覆盖率**: {pct(n_covered, denom)}%")
    # ── 需引用论断比例 from summary.citation_gap_ratio or compute from claims ──
    cgr = summary.get("citation_gap_ratio") if summary else None
    if cgr is not None:
        w(f"- **需引用论断比例**: {cgr * 100:.1f}%")
    else:
        denom = n_covered + n_partial + n_missing + n_not_needed
        w(f"- **需引用论断比例**: {pct(n_required + n_recommended, denom)}%")
    w(f"- **高风险论断**: {high_risk}")
    w("")

    # ── Partition claims ──
    missing = sorted(
        [c for c in claims if c.get("gap_status") == "missing"],
        key=risk_sort_key,
        reverse=True,
    )
    partial = [c for c in claims if c.get("gap_status") == "partial"]
    covered = [c for c in claims if c.get("gap_status") == "covered"]
    not_needed = [c for c in claims if c.get("gap_status") == "not_needed"]

    # ── Missing ──
    w("## 二、必须补引用的句子（missing）")
    w("")
    if not missing:
        w("_Нет пропущенных ссылок._")
        w("")
    else:
        for c in missing:
            claim_type = c.get("claim_type", "")
            risk = c.get("risk_level", "low")
            role = c.get("recommended_evidence_role", "")
            action = c.get("recommended_action", "")

            type_label = CLAIM_TYPE_LABELS.get(claim_type, claim_type)
            role_label = EVIDENCE_ROLE_LABELS.get(role, role)
            risk_label = RISK_LABELS.get(risk, risk)

            why = f"Тип утверждения: {type_label}."
            if claim_type in ("factual_claim", "result_claim", "evaluative_claim"):
                why += " Необходимо подкрепить фактическими данными из литературы."
            elif claim_type == "methodological_claim":
                why += " Методологическое обоснование требует ссылки на источник."
            elif claim_type in ("gap_claim", "research_gap_claim"):
                why += " Заявление о пробеле в исследованиях должно быть подтверждено обзором литературы."
            elif claim_type == "theoretical_claim":
                why += " Теоретическое положение нуждается в обосновании."
            elif claim_type == "contribution_claim":
                why += " Позиционирование вклада требует ссылок на предшествующие работы."

            w(f"- **{c.get('claim_text', '—')}**")
            w(f"  - **Почему нужно цитирование**: {why}")
            if action:
                w(f"  - **Рекомендация**: {action}")
            if role_label:
                w(f"  - **Тип источника**: {role_label}")
            w(f"  - **Уровень риска**: {risk_label}")
            w("")

    # ── Partial ──
    w("## 三、建议补 российских источников（partial）")
    w("")
    if not partial:
        w("_Нет частично покрытых утверждений._")
        w("")
    else:
        for c in partial:
            claim_type = c.get("claim_type", "")
            action = c.get("recommended_action", "")
            query = c.get("recommended_query", "")
            role = c.get("recommended_evidence_role", "")

            type_label = CLAIM_TYPE_LABELS.get(claim_type, claim_type)
            role_label = EVIDENCE_ROLE_LABELS.get(role, role)

            why = f"Тип: {type_label}."
            if role_label:
                why += f" Требуется: {role_label}."

            w(f"- **{c.get('claim_text', '—')}**")
            w(f"  - **Почему**: {why}")
            if action:
                w(f"  - **Рекомендация**: {action}")
            if query:
                w(f"  - **Запрос для поиска**: `{query}`")
            w("")

    # ── Covered ──
    w("## 四、已有文献支撑的句子（covered）")
    w("")
    if not covered:
        w("_Нет._")
        w("")
    else:
        for c in covered:
            w(f"- `covered` — {c.get('claim_text', '—')}")
        w("")

    # ── not_needed section ──
    w("")
    w("## 五、不需要引用的句子（not_needed）")
    w("")
    w("下列句子属于常识性或描述性陈述，不需要引用：")
    w("")
    if not not_needed:
        w("_Нет._")
        w("")
    else:
        for c in not_needed:
            w(f"- {c.get('claim_text', '—')}")
        w("")

    # ── Search suggestions ──
    w("")
    w("## 六、下一步检索建议")
    w("")
    suggestions = []
    for c in missing:
        query = c.get("recommended_query", "")
        action = c.get("recommended_action", "")
        role = c.get("recommended_evidence_role", "")
        role_label = EVIDENCE_ROLE_LABELS.get(role, role)
        if query:
            suggestions.append((c.get("risk_level", "low"), f"Искать: `{query}` — {role_label}"))
        elif action:
            suggestions.append((c.get("risk_level", "low"), f"{action} — ({role_label})"))

    # Also collect from partial
    for c in partial:
        query = c.get("recommended_query", "")
        action = c.get("recommended_action", "")
        role = c.get("recommended_evidence_role", "")
        role_label = EVIDENCE_ROLE_LABELS.get(role, role)
        if query:
            suggestions.append((c.get("risk_level", "low"), f"Искать: `{query}` — {role_label}"))
        elif action:
            suggestions.append((c.get("risk_level", "low"), f"{action} — ({role_label})"))

    if not suggestions:
        w("_Нет рекомендаций._")
    else:
        # Sort by risk
        risk_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        suggestions.sort(key=lambda x: risk_rank.get(x[0], 9))
        for i, (risk, text) in enumerate(suggestions, 1):
            risk_label = RISK_LABELS.get(risk, risk)
            w(f"{i}. [{risk_label}] {text}")

    w("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Преобразует citation_gap_report.json в читаемый Markdown-отчёт"
    )
    parser.add_argument("--input", "-i", required=True, help="Путь к citation_gap_report.json")
    parser.add_argument("--output", "-o", required=True, help="Путь для сохранения .md")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    md = render(data)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"[OK] Отчёт сохранён: {args.output}")


if __name__ == "__main__":
    main()
