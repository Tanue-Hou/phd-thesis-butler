#!/usr/bin/env python3
"""
build_literature_review_brief.py — Generate a structured literature review brief in Markdown.

Reads a JSON array of normalized records (russian_literature_record and/or
russian_dissertation_record format) and produces a structured Markdown document
organised by discipline_cluster → evidence_role, with a ГОСТ- or Harvard-formatted
reference list at the end.

Usage:
    python3 scripts/build_literature_review_brief.py \
        --input normalized_records.json \
        --output literature_review_brief.md

    python3 scripts/build_literature_review_brief.py \
        --input normalized_records.json \
        --output brief.md \
        --topic "Диагностика автоматических коробок передач" \
        --style gost

    python3 scripts/build_literature_review_brief.py \
        --input normalized_records.json \
        --dry-run

Pure standard library — no external dependencies.
"""

import argparse
import json
import sys
from collections import Counter, OrderedDict
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLUSTER_DISPLAY = {
    "AUTOMATION_CONTROL": "Автоматика и управление",
    "SCI_TECH":           "Естественные и технические науки",
    "AGRI_MED":           "Сельское хозяйство и медицина",
    "ARTS_SPORTS":        "Искусство и спорт",
    "HUM_POL_ECON":       "Гуманитарные, политические и экономические науки",
    "UNCLASSIFIED":       "Неклассифицированные источники",
}

# Preferred cluster display order
CLUSTER_ORDER = [
    "AUTOMATION_CONTROL",
    "SCI_TECH",
    "AGRI_MED",
    "HUM_POL_ECON",
    "ARTS_SPORTS",
    "UNCLASSIFIED",
]

EVIDENCE_ROLE_DISPLAY = {
    # Literature roles
    "background":           "Фоновые и обзорные работы",
    "gap":                  "Выявление пробелов в знаниях",
    "method":               "Методологические подходы",
    "validation":           "Валидация и экспериментальные данные",
    "comparison":           "Сравнительные исследования",
    "definition":           "Определения и терминология",
    "result":               "Результаты и выводы",
    # Dissertation roles
    "structure_reference":  "Структурные референсы (диссертации)",
    "method_reference":     "Методические референсы (диссертации)",
    "literature_pool":      "Литературный пул (диссертации)",
    "comparison_case":      "Сравнительные случаи (диссертации)",
    "citation_example":     "Примеры цитирования (диссертации)",
}

EVIDENCE_ROLE_ORDER = [
    "background",
    "definition",
    "gap",
    "method",
    "method_reference",
    "validation",
    "comparison",
    "comparison_case",
    "result",
    "structure_reference",
    "literature_pool",
    "citation_example",
]

SECTIONS_SUGGESTION = {
    "background":     "Глава 1 (Обзор литературы)",
    "gap":            "Глава 1 (Постановка задачи)",
    "method":         "Глава 2 (Методология)",
    "validation":     "Глава 3 (Экспериментальная часть)",
    "comparison":     "Глава 3 (Сравнительный анализ)",
    "definition":     "Глава 1 (Терминологический аппарат)",
    "result":         "Глава 4 (Обсуждение результатов)",
    "structure_reference": "Глава 1 (Структура работы)",
    "method_reference":    "Глава 2 (Методология)",
    "literature_pool":     "Глава 1 (Обзор литературы)",
    "comparison_case":     "Глава 3 (Сравнительный анализ)",
    "citation_example":    "Глава 1 (Обзор литературы)",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg):
    """Print to stderr."""
    print(msg, file=sys.stderr)


def is_dissertation(record):
    """Detect whether a record is a dissertation type."""
    return "author" in record and "degree_type" in record


def get_authors(record):
    """Extract authors list from either record type."""
    if is_dissertation(record):
        return [record.get("author", "")]
    return record.get("authors", [])


def get_title(record):
    """Extract Russian title."""
    return record.get("title_ru", "")


def get_year(record):
    """Extract year."""
    return record.get("year", "?")


def get_source_info(record):
    """Extract journal/institution info."""
    if is_dissertation(record):
        parts = []
        if record.get("institution"):
            parts.append(record["institution"])
        if record.get("specialty_name"):
            parts.append(f"Специальность: {record['specialty_name']}")
        return ". ".join(parts) if parts else ""
    return record.get("journal", "") or ""


def get_evidence_roles(record):
    """Extract evidence roles list."""
    roles = record.get("evidence_role", [])
    if isinstance(roles, str):
        return [roles]
    return roles


def get_pub_type_label(record):
    """Human-readable publication type."""
    if is_dissertation(record):
        degree = record.get("degree_type", "unknown")
        labels = {
            "candidate": "Кандидатская диссертация",
            "doctoral":  "Докторская диссертация",
            "abstract":  "Автореферат",
            "unknown":   "Диссертация",
        }
        return labels.get(degree, "Диссертация")
    pub_type = record.get("publication_type", "other")
    labels = {
        "journal_article":  "Статья",
        "conference_paper": "Доклад на конференции",
        "monograph":        "Монография",
        "preprint":         "Препринт",
        "other":            "Публикация",
    }
    return labels.get(pub_type, "Публикация")


# ---------------------------------------------------------------------------
# ГОСТ citation formatting
# ---------------------------------------------------------------------------

def format_gost_author(author_str):
    """
    Convert 'Иванов Иван Иванович' or 'Иванов И.И.' to ГОСТ inline format.
    ГОСТ: Иванов, И. И.
    """
    parts = author_str.strip().split()
    if not parts:
        return author_str
    surname = parts[0]
    initials = ""
    for p in parts[1:]:
        # Already abbreviated: 'И.И.' or 'И. И.'
        if "." in p:
            initials += p.replace(" ", "")
        else:
            # Full first name: take first letter
            initials += p[0] + "."
    if initials:
        return f"{surname}, {initials}"
    return surname


def format_gost_authors_short(authors):
    """Format authors list for inline citation: Иванов И. И., Петров П. П."""
    if not authors:
        return ""
    formatted = []
    for a in authors[:3]:
        formatted.append(format_gost_author(a))
    result = ", ".join(formatted)
    if len(authors) > 3:
        result += " и др."
    return result


def format_gost_entry(idx, record):
    """
    Format a single reference in ГОСТ style (ГОСТ Р 7.0.5-2008).
    """
    authors = get_authors(record)
    title = get_title(record)
    year = get_year(record)
    source = get_source_info(record)

    authors_str = format_gost_authors_short(authors)

    if is_dissertation(record):
        degree = record.get("degree_type", "unknown")
        degree_label = {
            "candidate": "канд. техн. наук",
            "doctoral":  "д-р техн. наук",
            "abstract":  "",
            "unknown":   "",
        }.get(degree, "")
        spec = record.get("specialty_code", "")
        spec_str = f" — Специальность: {spec}" if spec else ""
        inst = record.get("institution", "")
        pages = record.get("page_count")
        pages_str = f" — {pages} с." if pages else ""

        parts = [f"{authors_str} {title}"]
        if degree_label:
            parts[0] += f" : {degree_label}"
        if inst:
            parts.append(f"{inst}")
        parts[-1] += f", {year}."
        if pages_str:
            parts[-1] += pages_str
        if spec_str:
            parts[-1] += spec_str
        return " ".join(parts)

    # Literature type
    pub_type = record.get("publication_type", "other")
    journal = record.get("journal", "")
    doi = record.get("doi", "")
    url = record.get("url", "")

    if pub_type == "journal_article" and journal:
        ref = f"{authors_str} {title} // {journal}. — {year}."
    elif pub_type == "conference_paper":
        ref = f"{authors_str} {title} // Материалы конференции. — {year}."
    elif pub_type == "monograph":
        ref = f"{authors_str} {title}. — {year}."
    else:
        ref = f"{authors_str} {title} // {journal}. — {year}." if journal else f"{authors_str} {title}. — {year}."

    if doi:
        ref += f" — DOI: {doi}."
    elif url:
        ref += f" — URL: {url}."

    return ref


def format_harvard_entry(idx, record):
    """Format a single reference in Harvard style."""
    authors = get_authors(record)
    title = get_title(record)
    year = get_year(record)
    source = get_source_info(record)

    # Harvard: Surname, I.I. (Year) Title. Source.
    if not authors:
        authors_str = "Unknown"
    else:
        formatted = []
        for a in authors[:3]:
            formatted.append(format_gost_author(a))
        authors_str = ", ".join(formatted)
        if len(authors) > 3:
            authors_str += " et al."

    if is_dissertation(record):
        inst = record.get("institution", "")
        degree = record.get("degree_type", "unknown")
        degree_label = {
            "candidate": "PhD thesis",
            "doctoral":  "Doctoral thesis",
            "abstract":  "Abstract",
            "unknown":   "Thesis",
        }.get(degree, "Thesis")
        if inst:
            return f"{authors_str} ({year}) {title}. {degree_label}, {inst}."
        return f"{authors_str} ({year}) {title}. {degree_label}."

    journal = record.get("journal", "")
    doi = record.get("doi", "")

    if journal:
        ref = f"{authors_str} ({year}) '{title}', {journal}."
    else:
        ref = f"{authors_str} ({year}) {title}."

    if doi:
        ref += f" doi:{doi}"
    return ref


# ---------------------------------------------------------------------------
# Grouping and sorting
# ---------------------------------------------------------------------------

def group_records(records):
    """
    Group records by discipline_cluster, then by evidence_role.
    Returns OrderedDict[cluster] -> OrderedDict[role] -> [records].
    """
    clusters = OrderedDict()

    for rec in records:
        cluster = rec.get("discipline_cluster", "UNCLASSIFIED")
        roles = get_evidence_roles(rec)
        if not roles:
            roles = ["background"]  # default

        for role in roles:
            clusters.setdefault(cluster, OrderedDict())
            clusters[cluster].setdefault(role, [])
            clusters[cluster][role].append(rec)

    # Sort clusters by CLUSTER_ORDER
    sorted_clusters = OrderedDict()
    for c in CLUSTER_ORDER:
        if c in clusters:
            sorted_clusters[c] = clusters[c]
    # Append any remaining
    for c in clusters:
        if c not in sorted_clusters:
            sorted_clusters[c] = clusters[c]

    # Sort roles within each cluster by EVIDENCE_ROLE_ORDER
    final = OrderedDict()
    for cluster, roles in sorted_clusters.items():
        sorted_roles = OrderedDict()
        for r in EVIDENCE_ROLE_ORDER:
            if r in roles:
                sorted_roles[r] = roles[r]
        for r in roles:
            if r not in sorted_roles:
                sorted_roles[r] = roles[r]
        final[cluster] = sorted_roles

    return final


# ---------------------------------------------------------------------------
# Topic summary generation (heuristic, no LLM)
# ---------------------------------------------------------------------------

def generate_topic_summary(records, topic):
    """Generate a brief research status summary based on records and topic."""
    total = len(records)
    clusters = Counter()
    years = []
    pub_types = Counter()

    for rec in records:
        clusters[rec.get("discipline_cluster", "UNCLASSIFIED")] += 1
        y = rec.get("year")
        if y and isinstance(y, int):
            years.append(y)
        if is_dissertation(rec):
            pub_types["dissertation"] += 1
        else:
            pub_types[rec.get("publication_type", "other")] += 1

    year_range = ""
    if years:
        year_range = f"{min(years)}–{max(years)}"

    top_clusters = clusters.most_common(3)
    cluster_names = [CLUSTER_DISPLAY.get(c, c) or c for c, _ in top_clusters]

    lines = []
    lines.append("## Обзор текущего состояния исследований\n")
    if topic:
        lines.append(f"**Направление:** {topic}\n")
    lines.append(
        f"Всего проанализировано **{total}** источников"
        f"{f' за период {year_range}' if year_range else ''}."
    )
    if cluster_names:
        lines.append(
            f"Основные предметные области: {', '.join(cluster_names)}."
        )

    # Publication type breakdown
    type_parts = []
    if pub_types.get("journal_article"):
        type_parts.append(f"журнальных статей — {pub_types['journal_article']}")
    if pub_types.get("conference_paper"):
        type_parts.append(f"докладов на конференциях — {pub_types['conference_paper']}")
    if pub_types.get("dissertation"):
        type_parts.append(f"диссертаций — {pub_types['dissertation']}")
    if pub_types.get("monograph"):
        type_parts.append(f"монографий — {pub_types['monograph']}")
    if type_parts:
        lines.append("Среди них: " + ", ".join(type_parts) + ".")

    # Year distribution
    if years:
        recent = sum(1 for y in years if y >= 2018)
        lines.append(
            f"Наиболее актуальные источники ({recent} из {total}) опубликованы в 2018 году и позднее."
        )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def build_markdown(records, topic=None, style="gost"):
    """Build the full Markdown document."""
    grouped = group_records(records)
    format_entry = format_gost_entry if style == "gost" else format_harvard_entry

    lines = []
    lines.append("# Обзор литературы — структурированный бриф\n")
    lines.append(f"*Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    lines.append(f"*Формат библиографии: {'ГОСТ Р 7.0.5-2008' if style == 'gost' else 'Harvard'}*\n")
    lines.append("---\n")

    # Topic summary
    if topic:
        lines.append(generate_topic_summary(records, topic))
        lines.append("---\n")

    # Statistics overview
    lines.append("## Статистика по кластерам\n")
    lines.append("| Кластер | Кол-во источников |")
    lines.append("|---------|-------------------|")
    total_items = 0
    seen_counts = set()
    for cluster, roles in grouped.items():
        cluster_ids = set()
        for recs in roles.values():
            for rec in recs:
                rid = rec.get("id", "")
                if rid:
                    cluster_ids.add(rid)
                    seen_counts.add(rid)
        count = len(cluster_ids)
        total_items += count
        lines.append(f"| {CLUSTER_DISPLAY.get(cluster, cluster)} | {count} |")
    lines.append(f"| **Итого** | **{len(seen_counts)}** |")
    lines.append("")
    lines.append("---\n")

    # Main body: cluster → role → entries
    global_idx = 0
    reference_list = []  # for bibliography at end

    for cluster, roles in grouped.items():
        cluster_name = CLUSTER_DISPLAY.get(cluster, cluster)
        lines.append(f"## {cluster_name}\n")

        for role, recs in roles.items():
            role_name = EVIDENCE_ROLE_DISPLAY.get(role, role)
            lines.append(f"### {role_name}\n")

            for rec in recs:
                global_idx += 1
                title = get_title(rec)
                authors = get_authors(rec)
                year = get_year(rec)
                source = get_source_info(rec)
                pub_label = get_pub_type_label(rec)
                notes = rec.get("notes_for_writer", "")
                section = SECTIONS_SUGGESTION.get(role, "Глава 1")
                elibrary_id = rec.get("elibrary_id", "")
                doi = rec.get("doi", "")
                url = rec.get("url", "")

                authors_short = format_gost_authors_short(authors)

                lines.append(f"**{global_idx}. {authors_short}**")
                lines.append(f"*{title}* ({year})")
                lines.append(f"- Тип: {pub_label}")
                if source:
                    lines.append(f"- Источник: {source}")
                if elibrary_id:
                    lines.append(f"- eLIBRARY ID: {elibrary_id}")
                if doi:
                    lines.append(f"- DOI: {doi}")
                if url:
                    lines.append(f"- URL: {url}")
                lines.append(f"- Роль в обзоре: {role_name}")
                lines.append(f"- Рекомендуемая секция: **{section}**")
                if notes:
                    lines.append(f"- Заметки: {notes}")
                lines.append("")

                # Collect for bibliography (dedup by id)
                rid = rec.get("id", "")
                if rid and rid not in [r.get("id", "") for r in reference_list]:
                    reference_list.append(rec)

        lines.append("---\n")

    # Bibliography
    lines.append("## Список литературы\n")
    for i, rec in enumerate(reference_list, 1):
        lines.append(f"{i}. {format_entry(i, rec)}")
    lines.append("")
    lines.append("---\n")
    lines.append(f"*Всего в брифе: {len(reference_list)} источников*\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Dry-run statistics
# ---------------------------------------------------------------------------

def print_dry_run_stats(records):
    """Print statistics without generating output."""
    log("=" * 60)
    log("DRY-RUN: Статистика входных данных")
    log("=" * 60)

    total = len(records)
    log(f"Всего записей: {total}")

    # Record types
    lit_count = sum(1 for r in records if not is_dissertation(r))
    diss_count = total - lit_count
    log(f"  Литературные записи:  {lit_count}")
    log(f"  Диссертационные записи: {diss_count}")

    # Cluster distribution
    clusters = Counter(r.get("discipline_cluster", "UNCLASSIFIED") for r in records)
    log("\nРаспределение по кластерам:")
    for c in CLUSTER_ORDER:
        if c in clusters:
            log(f"  {CLUSTER_DISPLAY.get(c, c):45s} {clusters[c]}")
    for c in clusters:
        if c not in CLUSTER_ORDER:
            log(f"  {CLUSTER_DISPLAY.get(c, c):45s} {clusters[c]}")

    # Evidence role distribution
    all_roles = Counter()
    for r in records:
        for role in get_evidence_roles(r):
            all_roles[role] += 1
    log("\nРаспределение по ролям (evidence_role):")
    for role in EVIDENCE_ROLE_ORDER:
        if role in all_roles:
            log(f"  {EVIDENCE_ROLE_DISPLAY.get(role, role):45s} {all_roles[role]}")
    for role in all_roles:
        if role not in EVIDENCE_ROLE_ORDER:
            log(f"  {EVIDENCE_ROLE_DISPLAY.get(role, role):45s} {all_roles[role]}")

    # Year range
    years = [r.get("year") for r in records if isinstance(r.get("year"), int)]
    if years:
        log(f"\nДиапазон лет: {min(years)}–{max(years)}")
        recent = sum(1 for y in years if y >= 2018)
        log(f"Актуальные (2018+): {recent} ({100*recent//len(years)}%)")

    # Publication types
    pub_types = Counter()
    for r in records:
        if is_dissertation(r):
            pub_types["dissertation"] += 1
        else:
            pub_types[r.get("publication_type", "other")] += 1
    log("\nТипы публикаций:")
    for pt, cnt in pub_types.most_common():
        log(f"  {pt:30s} {cnt}")

    # Missing fields
    missing_roles = sum(1 for r in records if not get_evidence_roles(r))
    missing_cluster = sum(1 for r in records if not r.get("discipline_cluster"))
    log(f"\nЗаписей без evidence_role:     {missing_roles}")
    log(f"Записей без discipline_cluster: {missing_cluster}")

    # Grouped preview
    grouped = group_records(records)
    log("\nСтруктура сгруппированного вывода:")
    for cluster, roles in grouped.items():
        total_c = sum(len(recs) for recs in roles.values())
        log(f"  {CLUSTER_DISPLAY.get(cluster, cluster)} ({total_c} ист.)")
        for role, recs in roles.items():
            log(f"    └─ {EVIDENCE_ROLE_DISPLAY.get(role, role)}: {len(recs)}")

    log("=" * 60)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a structured literature review brief in Markdown."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Input JSON file (array of normalized literature/dissertation records)"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output Markdown file path (required unless --dry-run)"
    )
    parser.add_argument(
        "--topic", "-t", default=None,
        help="Optional research topic description for the summary section"
    )
    parser.add_argument(
        "--style", "-s", choices=["gost", "harvard"], default="gost",
        help="Bibliography citation style (default: gost)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print statistics only, do not generate output file"
    )
    args = parser.parse_args()

    # Validate arguments
    if not args.dry_run and not args.output:
        parser.error("--output is required unless --dry-run is used")

    # Read input
    log(f"Чтение входного файла: {args.input}")
    try:
        with open(args.input, encoding="utf-8") as f:
            records = json.load(f)
    except FileNotFoundError:
        log(f"ОШИБКА: Файл не найден: {args.input}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        log(f"ОШИБКА: Некорректный JSON: {e}")
        sys.exit(1)

    if not isinstance(records, list):
        log("ОШИБКА: Входные данные должны быть JSON-массивом")
        sys.exit(1)

    if not records:
        log("ПРЕДУПРЕЖДЕНИЕ: Входной массив пуст")
        if args.dry_run:
            return
        sys.exit(0)

    log(f"Загружено записей: {len(records)}")

    # Dry-run mode
    if args.dry_run:
        print_dry_run_stats(records)
        return

    # Generate markdown
    log(f"Генерация Markdown (стиль: {args.style})...")
    md_content = build_markdown(records, topic=args.topic, style=args.style)

    # Write output
    log(f"Запись в файл: {args.output}")
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(md_content)

    log(f"Готово! Файл записан: {args.output}")
    log(f"Источников в брифе: {len(records)}")


if __name__ == "__main__":
    main()
