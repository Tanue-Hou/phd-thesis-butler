#!/usr/bin/env python3
"""
L2: 学科专用润色规则生成 — 从 Layer 4 深度分析数据中提取润色规则。

输入: .phd_build/layer4/*.json (679篇深度分析)
输出: assets/references/polishing_rules_v5.json — 每学科润色规则 + 错误检测

工作原理:
  对每个学科聚类，从所有深度分析论文中聚合:
  - writing_patterns → 学科写作风格规则
  - common_mistakes → 常见错误检测规则
  - methodology/experiment → 学科典型方法/实验模式
  - logic_chain → 逻辑完整性规则
"""

import json, os
from pathlib import Path
from collections import Counter, defaultdict

BASE = Path(__file__).resolve().parent.parent
L4_DIR = BASE / ".phd_build" / "layer4"
OUT_DIR = BASE / "assets" / "references"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CLUSTERS = ["AUTOMATION_CONTROL", "SCI_TECH", "AGRI_MED", "ARTS_SPORTS", "HUM_POL_ECON"]


def extract_polishing_rules():
    """从 Layer 4 数据提取润色规则"""
    
    # 按聚类聚合
    clusters = defaultdict(lambda: {
        "writing_patterns": Counter(),
        "common_mistakes": Counter(),
        "methodologies": Counter(),
        "validation_methods": Counter(),
        "experiment_types": Counter(),
        "logic_scores": [],
        "chain_gaps": Counter(),
        "chapter_roles": Counter(),
        "section_completeness": Counter(),
    })
    
    total = 0
    for f in sorted(L4_DIR.glob("*.json")):
        p = json.load(open(f))
        cl = p.get("a1_cluster", "UNKNOWN")
        if cl not in CLUSTERS:
            continue
        
        c = clusters[cl]
        total += 1
        
        # Writing patterns
        dw = p.get("deep_writing", {})
        for pat in dw.get("writing_patterns", []):
            c["writing_patterns"][pat] += 1
        
        # Common mistakes
        for err in dw.get("common_mistakes", []):
            c["common_mistakes"][err] += 1
        
        # Methodology
        dm = p.get("deep_methodology", {})
        if dm.get("primary_approach"):
            c["methodologies"][dm["primary_approach"]] += 1
        if dm.get("validation_method"):
            c["validation_methods"][dm["validation_method"]] += 1
        
        # Experiment
        de = p.get("deep_experiment", {})
        for et in de.get("types", []):
            c["experiment_types"][et] += 1
        
        # Logic chain
        dlc = p.get("deep_logic_chain", {})
        if dlc.get("completeness_score") is not None:
            c["logic_scores"].append(dlc["completeness_score"])
        for gap in dlc.get("chain_gaps", []):
            c["chain_gaps"][gap] += 1
        
        # Chapter roles
        for role, present in dw.get("chapter_roles", {}).items():
            if present:
                c["chapter_roles"][role] += 1
    
    print(f"Loaded {total} deep analysis papers")
    
    # Build per-cluster polishing rules
    polishing_rules = {}
    
    for cl, data in clusters.items():
        n = data["writing_patterns"].total() if data["writing_patterns"] else 1
        err_n = data["common_mistakes"].total() if data["common_mistakes"] else 1
        
        # Top writing patterns (≥1% frequency, or any pattern with count ≥ 2)
        top_patterns = []
        for pat, count in data["writing_patterns"].most_common(30):
            freq = count / max(n, 1)
            if count >= 2 or freq >= 0.01:
                top_patterns.append({
                    "pattern": pat,
                    "frequency": round(freq, 3),
                    "count": count
                })
        
        # Top common mistakes (any with count ≥ 1)
        top_mistakes = []
        for err, count in data["common_mistakes"].most_common(30):
            freq = count / max(err_n, 1)
            if count >= 1:
                top_mistakes.append({
                    "mistake": err,
                    "frequency": round(freq, 3),
                    "count": count
                })
        
        # Logic score stats
        ls = data["logic_scores"]
        avg_logic = round(sum(ls) / max(len(ls), 1), 2) if ls else 0
        
        # Chain gaps
        top_gaps = [{"gap": g, "count": c} for g, c in data["chain_gaps"].most_common(10)]
        
        # Build DO/DON'T rules from patterns and mistakes
        do_rules = []
        dont_rules = []
        
        # DO: patterns describing good practices
        for pat in top_patterns:
            p_text = pat["pattern"].lower()
            if any(kw in p_text for kw in ["наличие", "стандартная", "хорошая", "правильно", 
                                            "рекомендуется", "полная", "четкая", "логичная"]):
                do_rules.append(pat["pattern"])
            elif pat["count"] >= 3:
                do_rules.append(pat["pattern"])
        
        # DON'T: mistakes and problematic patterns
        for pat in top_patterns:
            p_text = pat["pattern"].lower()
            if any(kw in p_text for kw in ["отсутствие", "проблема", "недостаток", 
                                            "необычно", "фрагментарность", "нет "]): 
                dont_rules.append(pat["pattern"])
        
        # Also add top mistakes as DON'T
        for err in top_mistakes:
            dont_rules.append(f"⚠️ {err['mistake']}")
        
        polishing_rules[cl] = {
            "papers_analyzed": len(data["logic_scores"]),
            "avg_logic_completeness": avg_logic,
            "do_rules": do_rules[:15],
            "dont_rules": dont_rules[:15],
            "common_mistakes": top_mistakes[:15],
            "writing_patterns": top_patterns[:15],
            "top_methodologies": [{"method": m, "count": c} for m, c in data["methodologies"].most_common(10)],
            "top_validation_methods": dict(data["validation_methods"].most_common(5)),
            "logic_chain_gaps": top_gaps,
            "typical_chapter_roles": [r for r, c in data["chapter_roles"].most_common() if c > 1],
        }
    
    # Build cross-cluster universal rules
    universal_do = []
    universal_dont = []
    
    # Patterns common across all clusters
    all_writing_patterns = Counter()
    for cl, data in clusters.items():
        all_writing_patterns.update(data["writing_patterns"])
    
    for pat, count in all_writing_patterns.most_common(20):
        if count >= 10:
            if any(kw in pat.lower() for kw in ["хорошая", "правильно", "рекомендуется"]):
                universal_do.append(pat)
            else:
                universal_dont.append(pat)
    
    polishing_rules["UNIVERSAL"] = {
        "do_rules": universal_do[:10],
        "dont_rules": universal_dont[:10],
        "cross_cluster_note": "以下规则适用于所有学科聚类。学科专用规则见各聚类条目。"
    }
    
    # Add Russian polishing guidance for each cluster
    for cl in CLUSTERS:
        pr = polishing_rules[cl]
        ru_name = {
            "AUTOMATION_CONTROL": "автоматизация и управление",
            "SCI_TECH": "технические и естественные науки",
            "AGRI_MED": "сельскохозяйственные и медицинские науки",
            "ARTS_SPORTS": "искусство и спорт",
            "HUM_POL_ECON": "гуманитарные, политические и экономические науки",
        }.get(cl, cl)
        
        pr["cluster_name_ru"] = ru_name
        pr["polishing_guidelines"] = generate_guidelines(pr, ru_name)
    
    # Save
    out_path = OUT_DIR / "polishing_rules_v5.json"
    with open(out_path, "w") as fh:
        json.dump({
            "version": "5.0",
            "generated_from": f"Layer 4 deep analysis ({total} papers)",
            "clusters": polishing_rules
        }, fh, ensure_ascii=False, indent=2)
    
    print(f"\n✅ polishing_rules_v5.json saved ({os.path.getsize(out_path)//1024}KB)")
    for cl in CLUSTERS:
        pr = polishing_rules[cl]
        print(f"  {cl:25s}: {pr['papers_analyzed']:3d} papers, {len(pr['do_rules'])} DO / {len(pr['dont_rules'])} DON'T rules")
    
    return polishing_rules


def generate_guidelines(pr, ru_name):
    """为聚类生成自然语言的润色指南"""
    top_do = pr["do_rules"][:3] if pr["do_rules"] else ["следовать типовой структуре"]
    top_dont = pr["dont_rules"][:3] if pr["dont_rules"] else ["избегать типичных ошибок"]
    methods = [m["method"] for m in pr["top_methodologies"][:3]]
    
    return (
        f"При написании диссертации по {ru_name} рекомендуется:\n"
        f"• {chr(10)+'• '.join(top_do)}\n\n"
        f"Следует избегать:\n"
        f"• {chr(10)+'• '.join(top_dont)}\n\n"
        f"Типичные методологические подходы: {', '.join(methods) if methods else 'разнообразны'}.\n"
        f"Средняя полнота логической цепочки: {pr['avg_logic_completeness']}/1.0."
    )


def main():
    print("=" * 60)
    print("L2: 学科专用润色规则生成")
    print("=" * 60)
    extract_polishing_rules()
    print("L2 complete!")


if __name__ == "__main__":
    main()
