#!/usr/bin/env python3
"""
validate_evidence_layer.py — v5.3.0 门禁验证脚本
检查 evidence_layer 完整性和数据质量。

Exit code: 0 = 全部通过，1 = 至少1项失败。
"""

import json
import os
import re
import sys

# Resolve project root (one level up from scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

PASS = "\u2705"
FAIL = "\u274c"
results = []


def check(label, condition, detail=""):
    ok = bool(condition)
    symbol = PASS if ok else FAIL
    msg = f"  {symbol} {label}"
    if detail and not ok:
        msg += f"  ({detail})"
    print(msg)
    results.append(ok)
    return ok


def try_parse_json(filepath):
    """Try to parse a JSON file. Returns (data, error_msg)."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except json.JSONDecodeError as e:
        return None, str(e)
    except Exception as e:
        return None, f"{e.__class__.__name__}: {e}"


def has_fake_doi(text):
    """Detect placeholder/fake DOI patterns."""
    fake_doi_patterns = [
        r"10\.0000/",
        r"10\.XXXX/",
        r"10\.9999/",
        r"10\.example/",
        r"doi:\s*10\.0000",
        r"doi\.org/10\.0000",
    ]
    for pat in fake_doi_patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def has_fake_url(text):
    """Detect placeholder/fake URL patterns."""
    fake_url_patterns = [
        r"https?://example\.com",
        r"https?://example\.org",
        r"https?://fake\.",
        r"https?://placeholder\.",
        r"https?://test\.com",
        r"https?://dummy\.",
        r"https?://foo\.",
        r"https?://xxx\.",
        r"https?://localhost",
        r"https?://127\.0\.0\.1",
    ]
    for pat in fake_url_patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def check_json_content_quality(filepath, data):
    """Check a JSON file for quality issues: fake DOI/URL, missing source_id, bulk copy."""
    issues = []
    text = json.dumps(data, ensure_ascii=False)

    if has_fake_doi(text):
        issues.append("contains fake/placeholder DOI")
    if has_fake_url(text):
        issues.append("contains fake/placeholder URL")

    # Check for evidence bindings that reference literature without source_id.
    # Only flag objects nested inside evidence_bindings[] arrays (not top-level
    # literature records which use "id" instead of "source_id").
    def _find_bindings(obj, path="", in_bindings_array=False):
        if isinstance(obj, dict):
            if in_bindings_array:
                has_source_ref = "source_id" in obj or "matched_sources" in obj
                if not has_source_ref:
                    coverage = obj.get("coverage", obj.get("gap_status", ""))
                    if coverage not in ("missing", "gap"):
                        issues.append(
                            f"evidence binding without source_id at {path}")
            for k, v in obj.items():
                child_in_bindings = (k in ("evidence_bindings", "matched_sources"))
                _find_bindings(v, f"{path}.{k}", child_in_bindings)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                _find_bindings(item, f"{path}[{i}]", in_bindings_array)

    _find_bindings(data)

    # Check for suspiciously long text fields (> 500 chars may indicate bulk copy)
    def check_bulk_copy(obj, path=""):
        if isinstance(obj, str):
            if len(obj) > 500:
                issues.append(f"suspiciously long text ({len(obj)} chars) at {path} — possible bulk copy")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                check_bulk_copy(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_bulk_copy(item, f"{path}[{i}]")

    check_bulk_copy(data)

    return issues


def main():
    el = os.path.join(PROJECT_ROOT, "evidence_layer")
    schemas_dir = os.path.join(PROJECT_ROOT, "assets", "references", "schemas")

    print("=" * 60)
    print("evidence_layer 验证报告 (v5.3.0)")
    print(f"项目根目录: {PROJECT_ROOT}")
    print("=" * 60)

    # ── 1. evidence_layer/ 目录存在 ──
    check("1. evidence_layer/ 目录存在", os.path.isdir(el))

    # ── 2. WORKFLOW.md 存在 ──
    check("2. evidence_layer/WORKFLOW.md 存在",
          os.path.isfile(os.path.join(el, "WORKFLOW.md")))

    # ── 3. EVIDENCE_ROLE_TAXONOMY.md 存在 ──
    check("3. evidence_layer/EVIDENCE_ROLE_TAXONOMY.md 存在",
          os.path.isfile(os.path.join(el, "EVIDENCE_ROLE_TAXONOMY.md")))

    # ── 4. CHAPTER_EVIDENCE_BINDING.md 存在 ──
    check("4. evidence_layer/CHAPTER_EVIDENCE_BINDING.md 存在",
          os.path.isfile(os.path.join(el, "CHAPTER_EVIDENCE_BINDING.md")))

    # ── 5. CITATION_GAP_DETECTION.md 存在 ──
    check("5. evidence_layer/CITATION_GAP_DETECTION.md 存在",
          os.path.isfile(os.path.join(el, "CITATION_GAP_DETECTION.md")))

    # ── 6. templates/ 下3个模板存在 ──
    tpl_dir = os.path.join(el, "templates")
    expected_templates = [
        "chapter_evidence_map_template.md",
        "citation_gap_report_template.md",
        "evidence_aware_polishing_template.md",
    ]
    if os.path.isdir(tpl_dir):
        found_tpls = [t for t in expected_templates
                      if os.path.isfile(os.path.join(tpl_dir, t))]
    else:
        found_tpls = []
    check("6. templates/ 下3个模板全部存在",
          len(found_tpls) == 3,
          f"找到 {len(found_tpls)}/3: {', '.join(found_tpls)}")

    # ── 7. examples/ 下5个样例存在 ──
    ex_dir = os.path.join(el, "examples")
    expected_examples = [
        "normalized_literature_sample.json",
        "user_outline_sample.md",
        "user_chapter_sample.md",
        "chapter_evidence_map_sample.json",
        "citation_gap_report_sample.json",
    ]
    if os.path.isdir(ex_dir):
        actual_files = set(os.listdir(ex_dir))
        found_exs = [e for e in expected_examples if e in actual_files]
    else:
        found_exs = []
    check("7. examples/ 下5个样例全部存在",
          len(found_exs) == 5,
          f"找到 {len(found_exs)}/5: {', '.join(found_exs)}")

    # ── 8. 3个schema存在且JSON可解析 ──
    expected_schemas = [
        "evidence_binding_record.schema.json",
        "chapter_evidence_map.schema.json",
        "citation_gap_report.schema.json",
    ]
    schemas_ok = True
    for schema_name in expected_schemas:
        schema_path = os.path.join(schemas_dir, schema_name)
        label = f"8. schema {schema_name}"
        if check(f"{label} 存在", os.path.isfile(schema_path)):
            data, err = try_parse_json(schema_path)
            if err:
                check(f"   {schema_name} JSON 可解析", False, err)
                schemas_ok = False
            else:
                print(f"      {PASS} JSON 可解析")
                results.append(True)
        else:
            schemas_ok = False

    # ── 9. chapter_evidence_map_sample.json 必须包含指定字段 ──
    map_sample_path = os.path.join(ex_dir, "chapter_evidence_map_sample.json")
    if os.path.isfile(map_sample_path):
        map_data, map_err = try_parse_json(map_sample_path)
        if map_err:
            check("9. chapter_evidence_map_sample.json 可解析", False, map_err)
        else:
            # Flatten the JSON for field checking
            map_text = json.dumps(map_data, ensure_ascii=False)
            required_map_fields = [
                "chapter_id",
                "chapter_name",
                "bound_records",
                "gap_analysis",
            ]
            missing_map = [f for f in required_map_fields if f not in map_text]
            check("9. chapter_evidence_map_sample.json 包含必需字段",
                  len(missing_map) == 0,
                  f"缺少: {', '.join(missing_map)}" if missing_map else "")
    else:
        check("9. chapter_evidence_map_sample.json 存在", False, "文件不存在")

    # ── 10. citation_gap_report_sample.json 必须包含指定字段 ──
    gap_sample_path = os.path.join(ex_dir, "citation_gap_report_sample.json")
    if os.path.isfile(gap_sample_path):
        gap_data, gap_err = try_parse_json(gap_sample_path)
        if gap_err:
            check("10. citation_gap_report_sample.json 可解析", False, gap_err)
        else:
            gap_text = json.dumps(gap_data, ensure_ascii=False)
            required_gap_fields = [
                "claim_text",
                "claim_type",
                "citation_need",
                "gap_status",
                "recommended_evidence_role",
                "risk_level",
                "recommended_action",
            ]
            missing_gap = [f for f in required_gap_fields if f not in gap_text]
            check("10. citation_gap_report_sample.json 包含必需字段",
                  len(missing_gap) == 0,
                  f"缺少: {', '.join(missing_gap)}" if missing_gap else "")
    else:
        check("10. citation_gap_report_sample.json 存在", False, "文件不存在")

    # ── 11. 所有样例内容质量检查 ──
    print()
    print("  11. 样例内容质量检查（fake DOI/URL, missing source_id, bulk copy）")
    quality_ok = True
    if os.path.isdir(ex_dir):
        for fname in sorted(os.listdir(ex_dir)):
            fpath = os.path.join(ex_dir, fname)
            if not os.path.isfile(fpath):
                continue
            if not fname.endswith(".json"):
                continue
            data, err = try_parse_json(fpath)
            if err:
                print(f"      {FAIL} {fname}: JSON 解析失败: {err}")
                quality_ok = False
                continue
            issues = check_json_content_quality(fpath, data)
            if issues:
                for issue in issues:
                    print(f"      {FAIL} {fname}: {issue}")
                quality_ok = False
            else:
                print(f"      {PASS} {fname}: 内容质量合格")
    else:
        print(f"      {FAIL} examples/ 目录不存在")
        quality_ok = False
    check("11. 所有样例内容质量检查通过", quality_ok)

    # ── Summary ──
    print()
    print("=" * 60)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    if failed == 0:
        print("✅ ALL EVIDENCE LAYER CHECKS PASSED")
        print(f"全部通过: {passed}/{total} 项检查")
    else:
        print(f"结果: {passed} 通过, {failed} 失败 (共 {total} 项)")
        print("❌ EVIDENCE LAYER VALIDATION FAILED")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
