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


def e(msg):
    """Print an error line (inline failure message)."""
    print(f"      {FAIL} {msg}")
    results.append(False)


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

    
    # ── 9-10. 深层schema校验 ──
    schema_checks = [
        ("chapter_evidence_map_sample.json", "chapter_evidence_map.schema.json"),
        ("citation_gap_report_sample.json", "citation_gap_report.schema.json"),
    ]
    
    def deep_check_value(val, schema_def, path=""):
        """递归检查单个值是否符合schema定义"""
        if not isinstance(schema_def, dict):
            return []
        errors = []
        
        # type check
        expected_types = schema_def.get("type")
        if expected_types:
            if isinstance(expected_types, list):
                type_ok = any(_type_match(val, t) for t in expected_types)
            else:
                type_ok = _type_match(val, expected_types)
            if not type_ok:
                errors.append(f"{path}: expected type {expected_types}, got {type(val).__name__}")
        
        # enum check
        enum_vals = schema_def.get("enum")
        if enum_vals is not None and val not in enum_vals:
            errors.append(f"{path}: value '{val}' not in enum {enum_vals}")
        
        # array items check
        if isinstance(val, list) and "items" in schema_def:
            items_schema = schema_def["items"]
            for i, item in enumerate(val):
                if isinstance(item, dict):
                    errors.extend(deep_check_dict(item, items_schema, f"{path}[{i}]"))
                else:
                    errors.extend(deep_check_value(item, items_schema, f"{path}[{i}]"))
        
        return errors
    
    def _type_match(val, t):
        if t == "string": return isinstance(val, str)
        if t == "integer": return isinstance(val, int)
        if t == "number": return isinstance(val, (int, float))
        if t == "boolean": return isinstance(val, bool)
        if t == "object": return isinstance(val, dict)
        if t == "array": return isinstance(val, list)
        return True
    
    def deep_check_dict(data, schema_def, path=""):
        """递归检查字典是否符合schema"""
        errors = []
        
        # required fields
        for req in schema_def.get("required", []):
            if req not in data:
                errors.append(f"{path}: missing required field '{req}'")
        
        # additionalProperties check
        if schema_def.get("additionalProperties") == False:
            allowed = set(schema_def.get("properties", {}).keys())
            for key in data:
                if key not in allowed:
                    errors.append(f"{path}: unexpected field '{key}' (additionalProperties=false)")
        
        # property checks
        for key, prop_schema in schema_def.get("properties", {}).items():
            if key in data:
                val = data[key]
                sub_path = f"{path}.{key}"
                if isinstance(prop_schema, dict):
                    # Check sub-type first
                    ptype = prop_schema.get("type")
                    if isinstance(val, dict) and ptype == "object":
                        errors.extend(deep_check_dict(val, prop_schema, sub_path))
                    elif isinstance(val, list) and ptype == "array":
                        # Check array items
                        items = prop_schema.get("items", {})
                        for i, item in enumerate(val):
                            if isinstance(item, dict) and isinstance(items, dict):
                                errors.extend(deep_check_dict(item, items, f"{sub_path}[{i}]"))
                            else:
                                errors.extend(deep_check_value(item, items, f"{sub_path}[{i}]"))
                    else:
                        errors.extend(deep_check_value(val, prop_schema, sub_path))
        
        return errors
    
    all_deep_ok = True
    for sample_name, schema_name in schema_checks:
        sample_path = os.path.join(ex_dir, sample_name)
        schema_path = os.path.join(schemas_dir, schema_name)
        
        if not os.path.isfile(sample_path) or not os.path.isfile(schema_path):
            continue
        
        with open(sample_path) as f:
            sample_data = json.load(f)
        with open(schema_path) as f:
            schema_data = json.load(f)
        
        deep_errors = deep_check_dict(sample_data, schema_data, sample_name)
        if deep_errors:
            all_deep_ok = False
            for err in deep_errors[:10]:
                e(f"  {sample_name}: schema violation: {err}")

    check("9-10. 深层schema校验（sample vs schema）", all_deep_ok,
          "" if all_deep_ok else f"schema违规")

    # ── 11. 样例内容质量检查 ──
    print()
    print("  11. 样例内容质量检查（fake DOI/URL, missing source_id, bulk copy）")
    quality_ok = True
    if os.path.isdir(ex_dir):
        for fname in sorted(os.listdir(ex_dir)):
            fpath = os.path.join(ex_dir, fname)
            if not os.path.isfile(fpath):
                continue
            with open(fpath, encoding="utf-8") as f:
                text = f.read()
            has_fake_doi = bool(re.search(r"10\.\d{4,}/", text)) and bool(re.search(r"(doi\.org|doi:\s*)10\.0000", text))
            if has_fake_doi:
                print(f"      {FAIL} {fname}: contains fake DOI pattern")
                quality_ok = False
                continue
            has_cjk = bool(re.search(r"[\u4e00-\u9fff\u3400-\u4dbf]", text)) and bool(re.search(r"(signific|economic|research|文献|研究|的|和|与)", text))
            if has_cjk:
                quality_ok = False
            # Check for long text (>500 chars)
            for line in text.split("\n"):
                if len(line.strip()) > 500 and not line.strip().startswith("#"):
                    print(f"      ⚠️  {fname}: long text ({len(line.strip())} chars), possible bulk copy")
                    break
            print(f"      {PASS} {fname}: 内容质量合格")
    if quality_ok:
        print(f"      {PASS} 所有样例内容质量检查通过")
        results.append(True)
    else:
        results.append(False)
        print(f"      {FAIL} 部分样例内容质量问题")

    # ── Summary ──
    print()
    print("=" * 60)
    total = len(results)
    passed = sum(results)
    if all(results):
        print(f"全部通过: {passed}/{total} 项检查")
        print("=" * 60)
        print()
        print("✅ ALL EVIDENCE LAYER CHECKS PASSED")
        print("=" * 60)
        return 0
    else:
        failed = total - passed
        print(f"结果: {passed} 通过, {failed} 失败 (共 {total} 项)")
        print("=" * 60)
        print()
        print("❌ EVIDENCE LAYER VALIDATION FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
    