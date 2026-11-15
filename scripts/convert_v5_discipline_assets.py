#!/usr/bin/env python3
"""
convert_v5_discipline_assets.py — v5.1
把当前统计聚合格式的 discipline JSON 转换为 v5.1 标准7类资产格式。

当前旧格式: structure / methodology / logic_chain / writing_patterns / common_failures
v5.1新格式: typical_structures / chapter_sequence / research_question_types /
            methodology_routes / logic_chains / validation_patterns / chapter_writing_rules

结构证据规则:
  - structure_composition 中 toc_clean 占比高 → 强证据
  - chapter_count_statistics median > 30 → 降权，写入 limitations
  - noisy_or_failed 占比高 → 说明数据质量问题
"""

import json, os, sys, hashlib, tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DISC_DIR = BASE / "assets" / "references" / "disciplines"
SCHEMA_PATH = BASE / "assets" / "references" / "schemas" / "discipline_asset.schema.json"

CLUSTERS = ["AUTOMATION_CONTROL", "SCI_TECH", "AGRI_MED", "ARTS_SPORTS", "HUM_POL_ECON"]


def load_schema():
    """加载 schema 用于验证"""
    if SCHEMA_PATH.exists():
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return None


ASSET_FIELDS = ["typical_structures", "chapter_sequence", "research_question_types",
                "methodology_routes", "logic_chains", "validation_patterns", "chapter_writing_rules"]


def stable_id(cluster, kind, value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"{cluster.lower()}_{kind}_{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def convert(cluster_name, dry_run=False):
    """转换单个学科 JSON"""
    path = DISC_DIR / f"{cluster_name}.json"
    if not path.exists():
        print(f"  ❌ {cluster_name}.json not found")
        return False
    
    original = path.read_bytes()
    old = json.loads(original)
    if not isinstance(old, dict):
        print("  ERROR: Expected a JSON object; source left unchanged")
        return False
    if any(field in old for field in ASSET_FIELDS):
        if not all(isinstance(old.get(field), list) for field in ASSET_FIELDS):
            print("  ERROR: Mixed or incomplete target format; refusing destructive conversion")
            return False
        print("  Already converted: source left byte-for-byte unchanged (not a data-quality certification)")
        return True
    if not all(isinstance(old.get(field), dict) for field in ("structure", "methodology", "logic_chain", "writing_patterns")):
        print("  ERROR: Unrecognized legacy schema; source left unchanged")
        return False
    print(f"\n  Processing: {cluster_name}.json...")
    
    # --- 提取旧数据 ---
    struct_old = old.get("structure", {})
    meth_old = old.get("methodology", {})
    logic_old = old.get("logic_chain", {})
    write_old = old.get("writing_patterns", {})
    fail_old = old.get("common_failures", {})
    
    # --- 1. typical_structures ---
    struct_comp = struct_old.get("structure_composition", {})
    cc_stats = struct_old.get("chapter_count_statistics", {})
    median_ch = cc_stats.get("median", 0)
    max_ch = cc_stats.get("max", 0)
    
    # 噪声判断
    noise_warning = None
    if median_ch > 30 or max_ch > 100:
        noise_warning = f"noisy structure detected: median={median_ch}, max={max_ch}"
    
    typical_structures = []
    if not noise_warning:
        # 只有无噪声时才用章节统计
        typical_structures.append({
            "id": f"{cluster_name.lower()}_typical_chapter_range",
            "description": f"Typical chapter count range for {cluster_name}",
            "typical_range": f"{cc_stats.get('min',0)}-{cc_stats.get('max',0)}",
            "evidence_count": cc_stats.get("count", 0),
            "source_quality": "heading_clean" if struct_comp.get("heading_clean", 0) > struct_comp.get("toc_clean", 0) else "toc_clean",
        })
    
    # --- 2. chapter_sequence (从top_logic_skeletons推断) ---
    top_skeletons = logic_old.get("top_logic_skeletons", [])
    chapter_sequence = []
    for sk in top_skeletons[:5]:
        skeleton = sk.get("skeleton", [])
        if skeleton:
            chapter_sequence.append({
                "id": stable_id(cluster_name, "seq", skeleton),
                "sequence": skeleton,
                "frequency": sk.get("frequency", 0),
                "evidence_count": sk.get("frequency", 0),
            })
    
    # --- 3. research_question_types ---
    top_meth = meth_old.get("top_methodology_hints", {})
    research_question_types = []
    for meth_type, freq in list(top_meth.items())[:8]:
        research_question_types.append({
            "id": stable_id(cluster_name, "rq", meth_type),
            "type": meth_type,
            "frequency": freq,
            "evidence_count": freq,
            "when_to_use": f"When research requires {meth_type} approach",
        })
    
    # --- 4. methodology_routes ---
    deep_methods = meth_old.get("deep_methodology_routes", {})
    methodology_routes = []
    for method, freq in list(deep_methods.items())[:8]:
        methodology_routes.append({
            "id": stable_id(cluster_name, "meth", method),
            "method": method,
            "frequency": freq,
            "evidence_count": freq,
            "layer4_count": freq,
        })
    if not methodology_routes:
        # Fallback to top_methodology_hints
        for hint, freq in list(top_meth.items())[:5]:
            methodology_routes.append({
                "id": stable_id(cluster_name, "meth", hint),
                "method": hint,
                "frequency": freq,
                "evidence_count": freq,
                "layer4_count": 0,
            })
    
    # --- 5. logic_chains ---
    elem_counts = logic_old.get("common_skeleton_elements", {})
    logic_chains = []
    if elem_counts:
        completeness = logic_old.get("deep_logic_completeness", {})
        logic_chains.append({
            "id": f"{cluster_name.lower()}_logic_main",
            "completeness_score": completeness.get("mean", 0),
            "element_counts": elem_counts,
            "evidence_count": completeness.get("count", 0),
            "layer4_count": completeness.get("count", 0),
            "mapping": {
                "problem": elem_counts.get("has_problem", 0),
                "goal": elem_counts.get("has_goal", 0),
                "method": elem_counts.get("has_method", 0),
                "experiment": elem_counts.get("has_experiment", 0),
                "result": elem_counts.get("has_result", 0),
                "conclusion": elem_counts.get("has_conclusion", 0),
            }
        })
    
    # --- 6. validation_patterns ---
    exp_types = meth_old.get("top_experiment_types", {})
    validation_patterns = []
    for etype, freq in list(exp_types.items())[:6]:
        validation_patterns.append({
            "id": stable_id(cluster_name, "val", etype),
            "validation_type": etype,
            "frequency": freq,
            "evidence_count": freq,
        })
    
    # --- 7. chapter_writing_rules ---
    top_terms = write_old.get("top_evidence_terms", [])
    deep_patterns = write_old.get("deep_writing_patterns", {})
    chapter_writing_rules = []
    
    # From writing patterns
    for pat, freq in list(deep_patterns.items())[:8]:
        chapter_writing_rules.append({
            "id": stable_id(cluster_name, "rule", pat),
            "pattern": pat,
            "frequency": freq,
            "evidence_count": freq,
            "when_to_use": f"When writing sections related to {pat}",
            "template_family_links": [{"recommended_categories": ["METHOD", "EXPERIMENT", "RESULT"]}],
        })
    
    # --- 构建新文档 ---
    new = {
        "cluster": cluster_name,
        "total_papers": old.get("total_papers", 0),
        "scope": {
            "clusters_covered": [cluster_name],
            "total_papers": old.get("total_papers", 0),
            "data_sources": list(struct_comp.keys()),
            "limitations": [],
        },
        "evidence_summary": {
            "structure_quality": struct_comp,
            "chapter_stats": cc_stats,
            "page_stats": struct_old.get("page_count_statistics", {}),
            "deep_analysis_available": meth_old.get("deep_analysis_available", 0),
            "classification_confidence": meth_old.get("classification_confidence", {}),
        },
        "limitations": [],
        "coverage_notes": {
            "disciplines_covered": write_old.get("disciplines_covered", {}),
            "deep_read_priorities": write_old.get("deep_read_priority_distribution", {}),
        },
        "sampling_summary": {
            "total_papers": old.get("total_papers", 0),
            "deep_analyzed": meth_old.get("deep_analysis_available", 0),
            "classification_confidence": meth_old.get("classification_confidence", {}),
        },
        # New v5.1 7-class assets
        "typical_structures": typical_structures,
        "chapter_sequence": chapter_sequence,
        "research_question_types": research_question_types,
        "methodology_routes": methodology_routes,
        "logic_chains": logic_chains,
        "validation_patterns": validation_patterns,
        "chapter_writing_rules": chapter_writing_rules,
        # Conversion metadata
        "_conversion": {
            "version": "5.1",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "noise_warning": noise_warning,
            "total_fields": sum(1 for f in [typical_structures, chapter_sequence, research_question_types, methodology_routes, logic_chains, validation_patterns, chapter_writing_rules] if f),
        }
    }
    
    # Add noise to limitations if needed
    if noise_warning:
        new["limitations"].append({
            "issue": noise_warning,
            "impact": "Chapter count statistics are unreliable for typical structure estimation",
            "recommendation": "Use toc_clean papers only for structural analysis",
        })
    
    # Validate before any write; duplicate semantics require review, not silent dropping.
    ids = [entry["id"] for field in ASSET_FIELDS for entry in new[field]]
    if len(ids) != len(set(ids)) or not validate_schema(new, load_schema()):
        print("  ERROR: Invalid or duplicate generated IDs; source left unchanged")
        return False

    # Write output
    if dry_run:
        print(f"  [DRY RUN] Would write {sum(len(v) for k,v in new.items() if k.startswith(('typical','chapter','research','methodology','logic','validation','_conversion')))} new asset entries")
        return True
    
    # Preserve all original fields in an immutable byte-for-byte sidecar.
    backup = path.with_suffix(path.suffix + ".pre-v5.1.bak")
    if backup.exists():
        if backup.read_bytes() != original:
            print("  ERROR: Existing backup differs; refusing overwrite")
            return False
    else:
        with backup.open("xb") as fh:
            fh.write(original)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as fh:
            temp_path = Path(fh.name)
            json.dump(new, fh, ensure_ascii=False, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
    
    # Stats
    total_new = sum(len(v) for k, v in new.items() 
                    if k in ["typical_structures","chapter_sequence","research_question_types",
                            "methodology_routes","logic_chains","validation_patterns","chapter_writing_rules"])
    print(f"  ✅ Wrote {total_new} new asset entries across 7 categories")
    if noise_warning:
        print(f"  ⚠️  {noise_warning}")
    return True


def validate_schema(new_data, schema):
    """简易schema验证"""
    if not schema:
        return True
    required_new = ["typical_structures", "chapter_sequence", "research_question_types",
                    "methodology_routes", "logic_chains", "validation_patterns", "chapter_writing_rules"]
    for field in required_new:
        if field not in new_data:
            print(f"  ❌ Missing required field: {field}")
            return False
        if not isinstance(new_data[field], list):
            print(f"  ❌ Field {field} should be list, got {type(new_data[field]).__name__}")
            return False
    return True


def main():
    dry_run = "--dry-run" in sys.argv
    targets = [a for a in sys.argv[1:] if not a.startswith("--")]
    
    if not targets or "--all" in sys.argv:
        targets = CLUSTERS
    
    schema = load_schema()
    if schema:
        print(f"Schema loaded: {SCHEMA_PATH.name}")
    
    print(f"{'='*60}\nConvert v5.0 → v5.1 Discipline Assets{' (DRY RUN)' if dry_run else ''}\n{'='*60}")
    
    all_ok = True
    for cl in targets:
        ok = convert(cl, dry_run)
        if not ok:
            all_ok = False
    
    print(f"\n{'='*60}")
    print(f"{'All conversions successful!' if all_ok else 'Some conversions failed.'}")
    print(f"{'='*60}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
