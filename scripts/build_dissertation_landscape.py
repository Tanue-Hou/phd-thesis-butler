#!/usr/bin/env python3
"""
build_dissertation_landscape.py — v5.4.0 Dissertation Landscape Builder

Reads dissertation records from an input JSON file, clusters them by theme,
analyzes chapter structures, methodology types, and validation patterns,
then generates a recommended outline for the user's thesis.

Outputs both JSON and Markdown reports.

Usage:
    python3 scripts/build_dissertation_landscape.py \
      --input research_layer/landscape/examples/dissercat_landscape_input_sample.json \
      --output-json /tmp/dissertation_landscape_result.json \
      --output-md /tmp/dissertation_landscape_report.md \
      --topic "vehicle state estimation"

Pure standard library — no external dependencies.
"""

import argparse
import json
import sys
import os
from collections import Counter, OrderedDict
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CHAPTER_ROLE_MAP = {
    "введение": "INTRODUCTION",
    "introduction": "INTRODUCTION",
    "обзор": "LITERATURE_REVIEW",
    "литератур": "LITERATURE_REVIEW",
    "literature review": "LITERATURE_REVIEW",
    "related work": "LITERATURE_REVIEW",
    "анализ": "ANALYSIS",
    "analysis": "ANALYSIS",
    "модел": "MODELING",
    "моделирован": "MODELING",
    "model": "MODELING",
    "теор": "THEORY",
    "theory": "THEORY",
    "theoretical": "THEORY",
    "метод": "METHODOLOGY",
    "method": "METHODOLOGY",
    "алгоритм": "ALGORITHM",
    "algorithm": "ALGORITHM",
    "эксперимент": "EXPERIMENT",
    "experiment": "EXPERIMENT",
    "experimental": "EXPERIMENT",
    "результат": "RESULTS",
    "result": "RESULTS",
    "обсуждение": "DISCUSSION",
    "discussion": "DISCUSSION",
    "внедрен": "IMPLEMENTATION",
    "implementation": "IMPLEMENTATION",
    "заключен": "CONCLUSION",
    "conclusion": "CONCLUSION",
    "вывод": "CONCLUSION",
    "рекомендац": "RECOMMENDATIONS",
    "recommendation": "RECOMMENDATIONS",
    "оптимиз": "OPTIMIZATION",
    "optimization": "OPTIMIZATION",
    "проверк": "VALIDATION",
    "validation": "VALIDATION",
    "verification": "VALIDATION",
    "числен": "NUMERICAL",
    "numerical": "NUMERICAL",
    "промышл": "INDUSTRIAL",
    "industrial": "INDUSTRIAL",
}

METHODOLOGY_LABELS = {
    "kalman_filtering": "Kalman Filtering / State Estimation",
    "adaptive_filtering": "Adaptive Filtering / Online Estimation",
    "sensor_fusion": "Multi-Sensor Fusion / Integration",
    "signal_processing": "Signal Processing & Analysis",
    "experimental_materials": "Experimental Materials Science",
    "machine_learning": "Machine Learning / Neural Networks",
    "analytical_modeling": "Analytical / Mathematical Modeling",
    "numerical_simulation": "Numerical Simulation (FEM/CFD)",
    "field_testing": "Field Testing / In-situ Measurement",
    "survey_questionnaire": "Survey / Questionnaire",
    "case_study": "Case Study",
    "nonlinear_modeling": "Nonlinear System Identification",
    "recursive_estimation": "Recursive Estimation / RLS",
}

VALIDATION_LABELS = {
    "experimental_bench": "Experimental Bench Testing",
    "numerical_simulation": "Numerical Simulation Validation",
    "industrial_pilot": "Industrial Pilot / Field Deployment",
    "comparison_benchmark": "Comparison with Benchmark Methods",
    "statistical_analysis": "Statistical Hypothesis Testing",
    "cross_validation": "Cross-validation (ML)",
    "analytical_proof": "Analytical / Formal Proof",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_field(rec, *names, default=""):
    """Get first non-empty field value."""
    for name in names:
        val = rec.get(name)
        if val is not None and val != "":
            return val
    return default


def get_field_list(rec, *names, default=None):
    """Get first non-empty list field from alternatives."""
    for name in names:
        val = rec.get(name)
        if val is not None:
            return safe_list(val)
    return default or []


def normalize_confidence(val, default=0.5):
    """Normalize structure_confidence to float. Accepts string, float, int, None."""
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val_lower = val.lower().strip()
        mapping = {"high": 0.9, "medium": 0.6, "low": 0.3}
        if val_lower in mapping:
            return mapping[val_lower]
        try:
            return float(val_lower)
        except (ValueError, TypeError):
            return default
    return default


def safe_str(val, default="unknown"):
    """Safely convert value to string, handling None."""
    if val is None:
        return default
    if isinstance(val, str):
        return val if val.strip() else default
    return str(val)


def log(msg):
    """Print to stderr."""
    print(msg, file=sys.stderr)


def safe_list(val, default=None):
    """Ensure value is a list."""
    if isinstance(val, list):
        return val
    if val is None:
        return default or []
    return [val]


def extract_chapter_roles(chapter_titles):
    """Map chapter titles to standardized roles."""
    roles = []
    for title in chapter_titles:
        title_lower = title.lower()
        matched = False
        for keyword, role in CHAPTER_ROLE_MAP.items():
            if keyword in title_lower:
                roles.append(role)
                matched = True
                break
        if not matched:
            roles.append("OTHER")
    return roles


def cluster_themes(records, topic=""):
    """Cluster records by thematic similarity using keywords and discipline."""
    clusters = []

    # Simple keyword-based clustering
    keyword_groups = {}
    for rec in records:
        keywords = [k.lower() for k in get_field_list(rec, "keywords", "keywords_ru")]
        title = get_field(rec, "title", "title_ru", "name").lower()

        # Find dominant theme — support both Russian and English keywords
        theme = "general"
        theme_keywords = [
            ("диагност", "диагностик", "diagnostics"),
            ("вибро", "вибрация", "vibration"),
            ("нейронн", "нейросет", "neural"),
            ("машинн", "machine_learning", "машинное обучение"),
            ("износ", "wear", "изнашивание"),
            ("модел", "моделирован", "модель", "model"),
            ("оптимиз", "оптимизация", "optimization"),
            ("алгоритм", "алгоритми", "algorithm"),
            ("эксперимент", "эксперименталь", "experiment"),
            ("управл", "управление", "control"),
            ("передач", "передачи", "transmission"),
            ("редуктор", "gearbox"),
            ("робот", "robot"),
            ("фильтр калман", "kalman", "калмановск"),
            ("оценк", "оцениван", "state estimation", "estimation"),
            ("транспортн", "vehicle", "automotive"),
            ("покрыти", "сцеплен", "tire", "tire_road", "adhesion"),
            ("шн", "шин", "tire force"),
        ]
        all_text = " ".join(keywords) + " " + title
        for kw_tuple in theme_keywords:
            for kw in kw_tuple:
                if kw in all_text:
                    theme = kw_tuple[-1]  # Use the last entry as the canonical cluster name
                    break
            if theme != "general":
                break

        keyword_groups.setdefault(theme, []).append(rec)

    for theme, recs in keyword_groups.items():
        all_keywords = []
        for r in recs:
            all_keywords.extend([k.lower() for k in get_field_list(r, "keywords", "keywords_ru")])
        top_kw = [kw for kw, _ in Counter(all_keywords).most_common(5)]

        clusters.append({
            "theme_id": theme,
            "theme_label": theme.replace("_", " ").title(),
            "count": len(recs),
            "record_ids": [r["id"] for r in recs],
            "top_keywords": top_kw,
            "representative_title": get_field(recs[0], "title", "title_ru", "name"),
        })

    clusters.sort(key=lambda c: c["count"], reverse=True)
    return clusters


def analyze_structure_patterns(records):
    """Identify common chapter structure patterns."""
    pattern_counter = Counter()
    pattern_examples = {}

    for rec in records:
        chapters = get_field_list(rec, "chapter_titles", "toc", "chapter_structure")
        if not chapters:
            # Try extracting titles from chapter_structure objects
            cs = rec.get("chapter_structure")
            if isinstance(cs, list) and all(isinstance(c, dict) for c in cs):
                chapters = [c.get("title", c.get("heading", "")) for c in cs if c.get("title") or c.get("heading")]
        if not chapters:
            continue
        roles = extract_chapter_roles(chapters)
        pattern_key = " → ".join(roles)
        pattern_counter[pattern_key] += 1
        if pattern_key not in pattern_examples:
            pattern_examples[pattern_key] = {
                "roles": roles,
                "example_id": rec["id"],
                "example_title": get_field(rec, "title", "title_ru", "name"),
                "chapter_count": len(chapters),
            }

    patterns = []
    for i, (key, count) in enumerate(pattern_counter.most_common(3), 1):
        info = pattern_examples[key]
        patterns.append({
            "pattern_id": f"SP{i:02d}",
            "sequence": info["roles"],
            "chapter_count": info["chapter_count"],
            "frequency": count,
            "example_record_id": info["example_id"],
            "example_title": info["example_title"],
        })

    return patterns


def analyze_methodology_patterns(records):
    """Identify methodology categories."""
    meth_counter = Counter()
    meth_examples = {}

    for rec in records:
        mt = rec.get("methodology_type", "")
        if not mt:
            # Try extracting from methods array
            methods_list = get_field_list(rec, "methods")
            if methods_list:
                # Categorize methods
                method_text = " ".join(m.lower() for m in methods_list)
                if any(kw in method_text for kw in ["адаптивн", "adaptive", "online"]):
                    mt = "adaptive_filtering"
                elif any(kw in method_text for kw in ["сенсорн", "слияни", "sensor fusion", "fusion", "multi-sensor"]):
                    mt = "sensor_fusion"
                elif any(kw in method_text for kw in ["рекурсивн", "rls", "recursive"]):
                    mt = "recursive_estimation"
                elif any(kw in method_text for kw in ["kalman", "фильтр", "ekf", "ukf", "фильтрация"]):
                    mt = "kalman_filtering"
                elif any(kw in method_text for kw in ["neural", "нейрон", "deep learning", "сверточн"]):
                    mt = "machine_learning"
                elif any(kw in method_text for kw in ["нелинейн", "nonlinear", "идентификац"]):
                    mt = "nonlinear_modeling"
                elif any(kw in method_text for kw in ["model", "модел", "simul", "имитацион"]):
                    mt = "analytical_modeling"
                elif any(kw in method_text for kw in ["experiment", "эксперимент", "test", "испыта"]):
                    mt = "experimental_materials"
                elif any(kw in method_text for kw in ["signal", "сигнал", "частот", "frequency"]):
                    mt = "signal_processing"
                else:
                    mt = "unknown"
        if not mt:
            mt = "unknown"
        meth_counter[mt] += 1
        if mt not in meth_examples:
            meth_examples[mt] = rec["id"]

    patterns = []
    for i, (mt, count) in enumerate(meth_counter.most_common(3), 1):
        patterns.append({
            "method_id": f"MP{i:02d}",
            "methodology_type": mt,
            "label": METHODOLOGY_LABELS.get(mt, safe_str(mt).replace("_", " ").title()),
            "frequency": count,
            "example_record_ids": [r["id"] for r in records if r.get("methodology_type") == mt][:3],
        })

    return patterns


def analyze_validation_patterns(records):
    """Identify validation pattern categories."""
    val_counter = Counter()
    val_examples = {}

    for rec in records:
        vt = rec.get("validation_type", "unknown")
        if vt is None or (isinstance(vt, str) and not vt.strip()):
            vt = "unknown"
        val_counter[vt] += 1
        if vt not in val_examples:
            val_examples[vt] = rec["id"]

    patterns = []
    for i, (vt, count) in enumerate(val_counter.most_common(3), 1):
        patterns.append({
            "validation_id": f"VP{i:02d}",
            "validation_type": vt,
            "label": VALIDATION_LABELS.get(vt, safe_str(vt).replace("_", " ").title()),
            "frequency": count,
            "example_record_ids": [r["id"] for r in records if r.get("validation_type") == vt][:3],
        })

    return patterns


def find_positioning_gaps(records, topic):
    """Identify gaps in the dissertation landscape."""
    gaps = []
    all_meth = set(r.get("methodology_type", "") for r in records)
    all_val = set(r.get("validation_type", "") for r in records)
    all_years = [r.get("year", 0) for r in records if r.get("year")]
    recent = [y for y in all_years if y >= 2020]

    # Check methodology gaps
    known_meth = {"signal_processing", "experimental_materials", "machine_learning",
                  "analytical_modeling", "numerical_simulation", "field_testing"}
    missing_meth = known_meth - all_meth
    if missing_meth:
        gaps.append({
            "gap_type": "methodology",
            "description": f"No dissertations found using: {', '.join(m.replace('_', ' ') for m in sorted(missing_meth)[:3])}",
            "opportunity": "Potential novel contribution using underrepresented methodology",
        })

    # Check temporal gaps
    if len(recent) < len(all_years) * 0.5:
        gaps.append({
            "gap_type": "temporal",
            "description": f"Only {len(recent)}/{len(all_years)} dissertations from 2020+",
            "opportunity": "Field may benefit from updated recent perspective",
        })

    # Check validation gaps
    if "industrial_pilot" not in all_val and "experimental_bench" in all_val:
        gaps.append({
            "gap_type": "validation_scale",
            "description": "Most validations are bench-level; no industrial pilot deployments found",
            "opportunity": "Industrial-scale validation could be a differentiator",
        })

    return gaps


def generate_borrowable_moves(records):
    """Identify reusable rhetorical/conceptual moves from the corpus."""
    moves = []

    # Analyze common structural moves
    has_intro_survey = 0
    has_exp_impl = 0
    for rec in records:
        chapters = get_field_list(rec, "chapter_titles", "toc", "chapter_structure")
        # Also try extracting from chapter_structure objects
        if not chapters:
            cs = rec.get("chapter_structure")
            if isinstance(cs, list) and all(isinstance(c, dict) for c in cs):
                chapters = [c.get("title", c.get("heading", "")) for c in cs if c.get("title") or c.get("heading")]
        roles = extract_chapter_roles(chapters)
        if "INTRODUCTION" in roles and "LITERATURE_REVIEW" in roles:
            has_intro_survey += 1
        if "EXPERIMENT" in roles and "IMPLEMENTATION" in roles:
            has_exp_impl += 1

    if has_intro_survey >= 1:
        moves.append({
            "move_id": "BM01",
            "move_type": "structural",
            "description": "Standard Intro → Literature Review opening pattern",
            "prevalence": f"{has_intro_survey}/{len(records)} dissertations",
            "recommendation": "Adopt for Chapter 1 — establishes context and identifies gaps",
        })

    if has_exp_impl >= 1:
        moves.append({
            "move_id": "BM02",
            "move_type": "structural",
            "description": "Experiment → Implementation closure pattern",
            "prevalence": f"{has_exp_impl}/{len(records)} dissertations",
            "recommendation": "Consider for final chapters — demonstrates practical impact",
        })

    # Check for Kalman/state estimation based approaches
    kalman_count = sum(1 for r in records if r.get("methodology_type") == "kalman_filtering"
                       or any("kalman" in m.lower() or "фильтр" in m.lower() for m in get_field_list(r, "methods")))
    if kalman_count >= 1:
        moves.append({
            "move_id": "BM03",
            "move_type": "methodological",
            "description": "Kalman filtering / state estimation as core methodology",
            "prevalence": f"{kalman_count}/{len(records)} dissertations",
            "recommendation": "Dominant methodology — benchmark against existing EKF/UKF variants or propose adaptive/sensor-fusion improvements",
        })

    # Check for sensor fusion
    fusion_count = sum(1 for r in records
                       if any(kw in " ".join(m.lower() for m in get_field_list(r, "methods"))
                              for kw in ["sensor fusion", "сенсорн", "слияни", "multi-sensor"]))
    if fusion_count >= 1:
        moves.append({
            "move_id": "BM04",
            "move_type": "methodological",
            "description": "Multi-sensor fusion as research trend",
            "prevalence": f"{fusion_count}/{len(records)} dissertations",
            "recommendation": "Consider fusing complementary sensors (IMU+GPS+tire) for enhanced robustness",
        })

    # Check for adaptive/online methods
    adaptive_count = sum(1 for r in records
                         if any(kw in " ".join(m.lower() for m in get_field_list(r, "methods"))
                                for kw in ["адаптивн", "adaptive", "online", "recursive"]))
    if adaptive_count >= 1:
        moves.append({
            "move_id": "BM05",
            "move_type": "methodological",
            "description": "Adaptive/online estimation methods for real-time applications",
            "prevalence": f"{adaptive_count}/{len(records)} dissertations",
            "recommendation": "Online adaptation is a key trend — consider combining adaptive filtering with physics-informed constraints",
        })

    return moves


def generate_risk_warnings(records, topic):
    """Generate warnings about potential risks."""
    warnings = []
    total = len(records)

    # Check saturation
    diag_count = sum(1 for r in records
                     if any(kw in r.get("title_ru", "").lower()
                            for kw in ["диагност", "диагноз"]))
    if diag_count > total * 0.6:
        warnings.append({
            "risk_type": "saturation",
            "severity": "medium",
            "description": f"High concentration on diagnostics topic ({diag_count}/{total})",
            "mitigation": "Differentiate via novel methodology or application domain",
        })

    # Check for stale references
    old_years = sum(1 for r in records if (r.get("year") or 2025) < 2018)
    if old_years > total * 0.3:
        warnings.append({
            "risk_type": "currency",
            "severity": "low",
            "description": f"{old_years}/{total} references predate 2018",
            "mitigation": "Supplement with recent publications from 2022+",
        })

    # Check access limitations
    preview_only = sum(1 for r in records if r.get("full_text_status") == "preview_only")
    if preview_only > total * 0.5:
        warnings.append({
            "risk_type": "access",
            "severity": "medium",
            "description": f"{preview_only}/{total} dissertations are preview-only",
            "mitigation": "Consider accessing via RSL interlibrary loan or institution library",
        })

    # Check confidence
    low_conf = sum(1 for r in records if normalize_confidence(r.get("structure_confidence", 1.0)) < 0.7)
    if low_conf > 0:
        warnings.append({
            "risk_type": "data_quality",
            "severity": "low",
            "description": f"{low_conf}/{total} records have low structure confidence",
            "mitigation": "Verify chapter structures manually for these records",
        })

    return warnings


def generate_recommended_outline(records, topic, structure_patterns):
    """Generate a recommended thesis outline based on landscape analysis."""
    # Find the most common structure pattern
    if structure_patterns:
        top_pattern = structure_patterns[0]
        common_roles = top_pattern["sequence"]
    else:
        common_roles = ["INTRODUCTION", "LITERATURE_REVIEW", "METHODOLOGY",
                        "EXPERIMENT", "RESULTS", "CONCLUSION"]

    outline = []
    role_details = {
        "INTRODUCTION": {
            "title": "Введение",
            "role": "Introduction and problem statement",
            "purpose": "Define research problem, objectives, and novelty; state hypothesis",
        },
        "LITERATURE_REVIEW": {
            "title": "Обзор литературы и постановка задачи",
            "role": "Literature review and gap analysis",
            "purpose": "Survey existing approaches, identify gaps, justify research direction",
        },
        "THEORY": {
            "title": "Теоретические основы",
            "role": "Theoretical foundations",
            "purpose": "Present mathematical/theoretical framework underlying the research",
        },
        "MODELING": {
            "title": "Математическое моделирование",
            "role": "Mathematical modeling",
            "purpose": "Develop formal models of the system/process under study",
        },
        "METHODOLOGY": {
            "title": "Методология исследования",
            "role": "Research methodology",
            "purpose": "Describe methods, algorithms, and experimental design",
        },
        "ALGORITHM": {
            "title": "Разработка алгоритмов",
            "role": "Algorithm development",
            "purpose": "Present novel algorithms or computational approaches",
        },
        "EXPERIMENT": {
            "title": "Экспериментальные исследования",
            "role": "Experimental validation",
            "purpose": "Describe experimental setup, procedures, and data collection",
        },
        "RESULTS": {
            "title": "Результаты и анализ",
            "role": "Results and analysis",
            "purpose": "Present experimental results, compare with theory/benchmarks",
        },
        "DISCUSSION": {
            "title": "Обсуждение результатов",
            "role": "Discussion",
            "purpose": "Interpret results, compare with related work, discuss limitations",
        },
        "IMPLEMENTATION": {
            "title": "Внедрение и практические рекомендации",
            "role": "Implementation and recommendations",
            "purpose": "Describe practical deployment and provide actionable recommendations",
        },
        "VALIDATION": {
            "title": "Верификация и валидация",
            "role": "Verification and validation",
            "purpose": "Verify correctness and validate effectiveness of proposed approach",
        },
        "CONCLUSION": {
            "title": "Заключение",
            "role": "Conclusion",
            "purpose": "Summarize contributions, list publications, outline future work",
        },
    }

    # Build outline from common roles, enriched with topic-specific titles
    chapter_id = 0
    seen_roles = set()
    for role in common_roles:
        if role in seen_roles:
            continue
        seen_roles.add(role)
        chapter_id += 1
        details = role_details.get(role, {
            "title": role.replace("_", " ").title(),
            "role": role.replace("_", " "),
            "purpose": "Address " + role.replace("_", " ").lower(),
        })

        # Customize title with topic if available
        title = details["title"]
        if topic and role == "LITERATURE_REVIEW":
            title = f"Обзор литературы по направлению «{topic}»"
        elif topic and role == "METHODOLOGY":
            title = f"Методология исследования {topic}"

        outline.append({
            "chapter_id": f"CH{chapter_id:02d}",
            "title": title,
            "role": details["role"],
            "purpose": details["purpose"],
        })

    return outline


def generate_source_summary(records):
    """Generate summary of data sources."""
    platforms = Counter()
    years = []
    for rec in records:
        # Priority: source_name > source_platform > source > unknown
        source = rec.get("source_name") or rec.get("source_platform") or rec.get("source") or "unknown"
        source = safe_str(source).lower().replace("_local_api", "").replace("_local", "")
        platforms[source] += 1
        if rec.get("year"):
            years.append(rec["year"])

    summary = {
        "total_records": len(records),
        "platforms": dict(platforms),
        "year_range": f"{min(years)}-{max(years)}" if years else "unknown",
    }
    return summary


def generate_read_depth_summary(records):
    """Generate summary of read depths."""
    depths = Counter()
    for rec in records:
        depths[rec.get("read_depth", "unknown")] += 1
    return dict(depths)


def build_landscape_json(records, topic, user_direction=""):
    """Build the complete landscape JSON output."""
    theme_clusters = cluster_themes(records, topic)
    structure_patterns = analyze_structure_patterns(records)
    methodology_patterns = analyze_methodology_patterns(records)
    validation_patterns = analyze_validation_patterns(records)
    positioning_gaps = find_positioning_gaps(records, topic)
    borrowable_moves = generate_borrowable_moves(records)
    risk_warnings = generate_risk_warnings(records, topic)
    recommended_outline = generate_recommended_outline(records, topic, structure_patterns)

    result = {
        "topic": topic,
        "user_direction": user_direction or topic,
        "records_count": len(records),
        "source_summary": generate_source_summary(records),
        "read_depth_summary": generate_read_depth_summary(records),
        "theme_clusters": theme_clusters,
        "structure_patterns": structure_patterns,
        "methodology_patterns": methodology_patterns,
        "validation_patterns": validation_patterns,
        "positioning_gaps": positioning_gaps,
        "borrowable_moves": borrowable_moves,
        "risk_warnings": risk_warnings,
        "recommended_outline": recommended_outline,
        "planning_layer_routes": [
            "planning_layer/chapter_plans/",
            "planning_layer/experiment_plans/",
        ],
        "evidence_layer_routes": [
            "evidence_layer/bindings/",
            "evidence_layer/citation_gaps/",
        ],
    }

    return result


def build_markdown_report(landscape_data):
    """Build the 12-section Markdown report."""
    topic = landscape_data.get("topic", "")
    records = landscape_data.get("records_count", 0)
    source_summary = landscape_data.get("source_summary", {})
    read_depth = landscape_data.get("read_depth_summary", {})
    clusters = landscape_data.get("theme_clusters", [])
    structures = landscape_data.get("structure_patterns", [])
    methods = landscape_data.get("methodology_patterns", [])
    validations = landscape_data.get("validation_patterns", [])
    gaps = landscape_data.get("positioning_gaps", [])
    moves = landscape_data.get("borrowable_moves", [])
    warnings = landscape_data.get("risk_warnings", [])
    outline = landscape_data.get("recommended_outline", [])

    lines = []
    lines.append("# Dissertation Landscape Report")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append(f"*phd-thesis-butler v5.4.0*")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Section 1: Research Direction
    lines.append("## 1. Research Direction")
    lines.append("")
    lines.append(f"**Topic:** {topic}")
    if landscape_data.get("user_direction"):
        lines.append(f"**User Direction:** {landscape_data['user_direction']}")
    lines.append("")

    # Section 2: Source Coverage
    lines.append("## 2. Source Coverage")
    lines.append("")
    lines.append(f"- **Total records analyzed:** {records}")
    if source_summary.get("platforms"):
        for plat, cnt in source_summary["platforms"].items():
            lines.append(f"- **{plat}:** {cnt} records")
    if source_summary.get("year_range"):
        lines.append(f"- **Year range:** {source_summary['year_range']}")
    if read_depth:
        lines.append("")
        lines.append("**Read depth distribution:**")
        for depth, cnt in read_depth.items():
            lines.append(f"- {depth}: {cnt}")
    lines.append("")

    # Section 3: Comparable Dissertations
    lines.append("## 3. Comparable Dissertations")
    lines.append("")
    lines.append("Records analyzed in this landscape (grouped by theme cluster):")
    lines.append("")
    for cluster in clusters:
        lines.append(f"### {cluster['theme_label']} ({cluster['count']} records)")
        for rid in cluster.get("record_ids", []):
            lines.append(f"- `{rid}`")
        if cluster.get("top_keywords"):
            lines.append(f"- Top keywords: {', '.join(cluster['top_keywords'])}")
        lines.append("")

    # Section 4: Theme Clusters
    lines.append("## 4. Theme Clusters")
    lines.append("")
    lines.append("| # | Theme | Count | Top Keywords |")
    lines.append("|---|-------|-------|--------------|")
    for i, cl in enumerate(clusters, 1):
        kw_str = ", ".join(cl.get("top_keywords", [])[:3])
        lines.append(f"| {i} | {cl['theme_label']} | {cl['count']} | {kw_str} |")
    lines.append("")

    # Section 5: Chapter Structure Comparison
    lines.append("## 5. Chapter Structure Comparison")
    lines.append("")
    for sp in structures:
        lines.append(f"### Pattern {sp['pattern_id']} (frequency: {sp['frequency']})")
        lines.append(f"- **Chapter count:** {sp['chapter_count']}")
        lines.append(f"- **Sequence:** {' → '.join(sp['sequence'])}")
        lines.append(f"- **Example:** {sp.get('example_title', sp.get('example_record_id', ''))}")
        lines.append("")

    # Section 6: Methodology Landscape
    lines.append("## 6. Methodology Landscape")
    lines.append("")
    lines.append("| # | Methodology | Frequency | Examples |")
    lines.append("|---|-------------|-----------|----------|")
    for mp in methods:
        ex_ids = ", ".join(mp.get("example_record_ids", [])[:2])
        lines.append(f"| {mp['method_id']} | {mp['label']} | {mp['frequency']} | {ex_ids} |")
    lines.append("")

    # Section 7: Validation/Argumentation Patterns
    lines.append("## 7. Validation/Argumentation Patterns")
    lines.append("")
    lines.append("| # | Validation Type | Frequency | Examples |")
    lines.append("|---|-----------------|-----------|----------|")
    for vp in validations:
        ex_ids = ", ".join(vp.get("example_record_ids", [])[:2])
        lines.append(f"| {vp['validation_id']} | {vp['label']} | {vp['frequency']} | {ex_ids} |")
    lines.append("")

    # Section 8: User Positioning
    lines.append("## 8. User Positioning")
    lines.append("")
    if gaps:
        for gap in gaps:
            lines.append(f"- **{gap['gap_type'].replace('_', ' ').title()}:** {gap['description']}")
            lines.append(f"  - *Opportunity:* {gap['opportunity']}")
        lines.append("")
    else:
        lines.append("No significant positioning gaps identified.")
        lines.append("")

    # Section 9: Borrowable Writing Moves
    lines.append("## 9. Borrowable Writing Moves")
    lines.append("")
    if moves:
        for move in moves:
            lines.append(f"### {move['move_id']}: {move['move_type'].title()} Move")
            lines.append(f"- **Description:** {move['description']}")
            lines.append(f"- **Prevalence:** {move['prevalence']}")
            lines.append(f"- **Recommendation:** {move['recommendation']}")
            lines.append("")
    else:
        lines.append("No specific borrowable moves identified.")
        lines.append("")

    # Section 10: Risk Warnings
    lines.append("## 10. Risk Warnings")
    lines.append("")
    if warnings:
        for warn in warnings:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(warn["severity"], "⚪")
            lines.append(f"- {severity_icon} **{warn['risk_type'].title()}** [{warn['severity']}]: {warn['description']}")
            lines.append(f"  - *Mitigation:* {warn['mitigation']}")
        lines.append("")
    else:
        lines.append("No risk warnings identified.")
        lines.append("")

    # Section 11: Recommended Thesis Outline
    lines.append("## 11. Recommended Thesis Outline")
    lines.append("")
    lines.append(f"Based on analysis of {records} comparable dissertations, the following outline is recommended:")
    lines.append("")
    for ch in outline:
        lines.append(f"### {ch['chapter_id']}: {ch['title']}")
        lines.append(f"- **Role:** {ch['role']}")
        lines.append(f"- **Purpose:** {ch['purpose']}")
        lines.append("")

    # Section 12: Next Actions
    lines.append("## 12. Next Actions")
    lines.append("")
    lines.append("Suggested next steps based on this landscape analysis:")
    lines.append("")
    lines.append("1. **Refine research question** — Use positioning gaps to sharpen your novelty claim")
    lines.append("2. **Access key dissertations** — Request full text for top comparable works via RSL or institution library")
    lines.append("3. **Build chapter plan** — Run `build_chapter_plan.py` with the recommended outline")
    lines.append("4. **Identify evidence gaps** — Run `detect_citation_gaps.py` to find what evidence you still need")
    lines.append("5. **Collect methodology details** — Deep-read methodology chapters from top 3 comparable dissertations")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*This report was generated by phd-thesis-butler v5.4.0 Dissertation Landscape feature.*")
    lines.append(f"*Data sources: {', '.join(source_summary.get('platforms', {}).keys())}*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Build dissertation landscape analysis from records JSON."
    )
    parser.add_argument("--input", required=True,
                        help="Path to input JSON array of dissertation records")
    parser.add_argument("--output-json", required=True,
                        help="Path to output JSON file")
    parser.add_argument("--output-md", required=True,
                        help="Path to output Markdown report")
    parser.add_argument("--topic", default="",
                        help="Research topic / direction")
    parser.add_argument("--direction", default="",
                        help="User research direction (defaults to topic)")
    args = parser.parse_args()

    # Read input
    if not os.path.isfile(args.input):
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not isinstance(records, list) or len(records) == 0:
        print("ERROR: Input must be a non-empty JSON array", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(records)} records from {args.input}")

    # Build landscape
    topic = args.topic
    user_direction = args.direction or topic
    landscape = build_landscape_json(records, topic, user_direction)

    # Write JSON
    os.makedirs(os.path.dirname(os.path.abspath(args.output_json)), exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(landscape, f, ensure_ascii=False, indent=2)
    print(f"JSON output written to: {args.output_json}")

    # Write Markdown
    os.makedirs(os.path.dirname(os.path.abspath(args.output_md)), exist_ok=True)
    md_report = build_markdown_report(landscape)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"Markdown report written to: {args.output_md}")

    # Summary
    print(f"\nLandscape summary:")
    print(f"  Records: {landscape['records_count']}")
    print(f"  Theme clusters: {len(landscape['theme_clusters'])}")
    print(f"  Structure patterns: {len(landscape['structure_patterns'])}")
    print(f"  Methodology patterns: {len(landscape['methodology_patterns'])}")
    print(f"  Validation patterns: {len(landscape['validation_patterns'])}")
    print(f"  Positioning gaps: {len(landscape['positioning_gaps'])}")
    print(f"  Borrowable moves: {len(landscape['borrowable_moves'])}")
    print(f"  Risk warnings: {len(landscape['risk_warnings'])}")
    print(f"  Recommended outline chapters: {len(landscape['recommended_outline'])}")


if __name__ == "__main__":
    main()
