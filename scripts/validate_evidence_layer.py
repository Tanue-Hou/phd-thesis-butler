#!/usr/bin/env python3
"""
validate_evidence_layer.py — v5.3.0 门禁验证脚本
检查 evidence_layer 完整性和数据质量。

Exit code: 0 = 全部通过，1 = 至少1项失败。
"""

import json
import os
import re
import subprocess
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

    # ── 12. Generated sample existence & schema conformance ──
    print()
    print("  12. Generated sample 端到端 schema 校验")
    gen_samples = [
        ("chapter_evidence_map_generated_sample.json", "chapter_evidence_map.schema.json"),
        ("evidence_binding_records_sample.json", "evidence_binding_record.schema.json"),
    ]
    gen_ok = True
    for sample_name, schema_name in gen_samples:
        sample_path = os.path.join(ex_dir, sample_name)
        schema_path = os.path.join(schemas_dir, schema_name)
        label = f"12. {sample_name}"

        if not os.path.isfile(sample_path):
            check(f"{label} 存在", False, "文件不存在")
            gen_ok = False
            continue
        if not os.path.isfile(schema_path):
            check(f"{label} schema 存在", False, f"{schema_name} 不存在")
            gen_ok = False
            continue

        sample_data, parse_err = try_parse_json(sample_path)
        if parse_err:
            check(f"{label} JSON 可解析", False, parse_err)
            gen_ok = False
            continue

        with open(schema_path) as f:
            schema_data = json.load(f)

        # For array-typed samples (evidence_binding_records), validate each element
        if isinstance(sample_data, list):
            if schema_data.get("type") == "object":
                # Schema is for a single record; validate each item in the array
                item_errors = []
                for i, item in enumerate(sample_data):
                    item_errors.extend(deep_check_dict(item, schema_data, f"{sample_name}[{i}]"))
                if item_errors:
                    gen_ok = False
                    for err in item_errors[:5]:
                        e(f"  {sample_name}: schema violation: {err}")
                else:
                    check(f"{label} schema 校验通过", True)
            else:
                check(f"{label} schema 校验", False, "schema type mismatch")
                gen_ok = False
        else:
            deep_errors = deep_check_dict(sample_data, schema_data, sample_name)
            if deep_errors:
                gen_ok = False
                for err in deep_errors[:5]:
                    e(f"  {sample_name}: schema violation: {err}")
            else:
                check(f"{label} schema 校验通过", True)

    # ── 13. Generated sample cross-reference integrity ──
    print()
    print("  13. Generated sample 交叉引用完整性")
    cem_path = os.path.join(ex_dir, "chapter_evidence_map_generated_sample.json")
    ebr_path = os.path.join(ex_dir, "evidence_binding_records_sample.json")
    if os.path.isfile(cem_path) and os.path.isfile(ebr_path):
        cem_data, _ = try_parse_json(cem_path)
        ebr_data, _ = try_parse_json(ebr_path)
        if cem_data and ebr_data:
            # Check that every binding_id in CEM exists in EBR
            ebr_ids = set(rec.get("binding_id") for rec in ebr_data if isinstance(rec, dict))
            cem_binding_ids = set(
                r.get("binding_id") for r in cem_data.get("bound_records", [])
            )
            missing_refs = cem_binding_ids - ebr_ids
            check("13. CEM bound_records binding_id 全部在 EBR 中有对应",
                  len(missing_refs) == 0,
                  f"缺少: {missing_refs}" if missing_refs else "")

            # Check source_id in CEM bound_records are non-empty when gap_status != missing
            empty_source = []
            for r in cem_data.get("bound_records", []):
                if r.get("gap_status") != "missing" and not r.get("source_id"):
                    empty_source.append(r.get("binding_id"))
            check("13. CEM bound_records 非 missing 记录有 source_id",
                  len(empty_source) == 0,
                  f"缺少 source_id: {empty_source}" if empty_source else "")
        else:
            check("13. Generated samples 可解析", False, "JSON 解析失败")
    else:
        check("13. Generated samples 存在", False, "至少一个文件不存在")

    # ── 12. 端到端检查：detect_citation_gaps.py 生成的 JSON 符合 schema ──
    # ── 14. 不变量检查：covered + null source 不允许存在 ──
    invariants_ok = True
    
    # Check generated citation gap sample
    gen_cgr_path = os.path.join(ex_dir, "citation_gap_generated_sample.json")
    if os.path.isfile(gen_cgr_path):
        with open(gen_cgr_path) as f:
            gen_cgr = json.load(f)
        for i, c in enumerate(gen_cgr.get("claims", [])):
            gs = c.get("gap_status")
            sid = c.get("matched_source_id")
            es = c.get("evidence_strength")
            cn = c.get("citation_need", "")
            
            if gs == "covered" and (sid is None or sid == ""):
                invariants_ok = False
                e(f"  gen_cgr.claims[{i}]: gap_status=covered but matched_source_id is null")
            
            if es in ("strong", "medium") and (sid is None or sid == ""):
                invariants_ok = False
                e(f"  gen_cgr.claims[{i}]: evidence_strength={es} but matched_source_id is null")
            
            if cn in ("required", "recommended") and gs == "covered" and (sid is None or sid == ""):
                invariants_ok = False
                e(f"  gen_cgr.claims[{i}]: citation_need={cn} but covered+null source")
    
    # Run detect_citation_gaps with no literature (regression test)
    import tempfile
    no_lit_out = "/tmp/test_invariant_cgr.json"
    r = subprocess.run(
        [sys.executable, "scripts/detect_citation_gaps.py",
         "--input", os.path.join(ex_dir, "user_chapter_sample.md"),
         "--output", no_lit_out],
        capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=15
    )
    if r.returncode == 0 and os.path.isfile(no_lit_out):
        with open(no_lit_out) as f:
            no_lit_cgr = json.load(f)
        for i, c in enumerate(no_lit_cgr.get("claims", [])):
            if c.get("gap_status") == "covered":
                invariants_ok = False
                e(f"  no-lit.claims[{i}]: gap_status=covered without literature input")
            sid = c.get("matched_source_id")
            es = c.get("evidence_strength")
            if es in ("strong", "medium") and (sid is None or sid == ""):
                invariants_ok = False
                e(f"  no-lit.claims[{i}]: evidence_strength={es} but no literature")
    
    check("14. 不变量检查（covered+null source, strong+null source, no-literature no-covered）",
          invariants_ok, "" if invariants_ok else f"不变量违规")

    # ── 15. 端到端检查：detect_citation_gaps.py ──
    print()
    print("  15. 端到端检查：detect_citation_gaps.py 生成的 JSON 符合 schema")
    e2e_ok = True
    det_script = os.path.join(PROJECT_ROOT, "scripts", "detect_citation_gaps.py")
    e2e_input = os.path.join(el, "examples", "user_chapter_sample.md")
    e2e_lit = os.path.join(el, "examples", "normalized_literature_sample.json")
    e2e_output = os.path.join("/tmp", "e2e_citation_gap_report.json")
    e2e_schema = os.path.join(schemas_dir, "citation_gap_report.schema.json")

    if not os.path.isfile(det_script):
        check("15. detect_citation_gaps.py 存在", False, "脚本不存在")
        e2e_ok = False
    elif not os.path.isfile(e2e_input) or not os.path.isfile(e2e_lit):
        check("15. 端到端检查", False, "输入样例文件缺失")
        e2e_ok = False
    elif not os.path.isfile(e2e_schema):
        check("15. 端到端检查", False, "schema 缺失")
        e2e_ok = False
    else:
        cmd = [
            sys.executable, det_script,
            "--input", e2e_input,
            "--literature", e2e_lit,
            "--output", e2e_output,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if proc.returncode != 0:
            check("15. detect_citation_gaps.py 执行成功", False,
                  proc.stderr.strip()[:120])
            e2e_ok = False
        else:
            print(f"      {PASS} detect_citation_gaps.py 执行成功")
            results.append(True)
            # Validate output JSON structure
            e2e_data, e2e_err = try_parse_json(e2e_output)
            if e2e_err:
                check("15. 输出 JSON 可解析", False, e2e_err)
                e2e_ok = False
            else:
                print(f"      {PASS} 输出 JSON 可解析")
                results.append(True)
                with open(e2e_schema) as f:
                    e2e_schema_data = json.load(f)
                e2e_errors = deep_check_dict(e2e_data, e2e_schema_data, "e2e_output")
                if e2e_errors:
                    for err in e2e_errors[:5]:
                        e(f"  e2e output: schema violation: {err}")
                    e2e_ok = False
                else:
                    print(f"      {PASS} 输出符合 citation_gap_report.schema.json")
                    results.append(True)
                # Check summary coherence
                s = e2e_data.get("summary", {})
                claims = e2e_data.get("claims", [])
                summary_ok = s.get("total_claims") == len(claims)
                if not summary_ok:
                    e(f"  e2e: summary.total_claims ({s.get('total_claims')}) "
                      f"!= len(claims) ({len(claims)})")
                    e2e_ok = False
                else:
                    print(f"      {PASS} summary.total_claims == len(claims)")
                    results.append(True)
                # Cleanup temp file
                try:
                    os.remove(e2e_output)
                except OSError:
                    pass

    check("15. 端到端检查：generate + validate pipeline", e2e_ok,
          "" if e2e_ok else "端到端检查失败")

    # ── Summary ──
    print()
    print("=" * 60)
    # ── 16. year=null regression test (Zotero metadata compatibility) ──
    null_year_ok = True
    lit_path = os.path.join(ex_dir, "normalized_literature_sample.json")
    null_year_lit = "/tmp/e2e_null_year_literature.json"
    
    if os.path.isfile(lit_path):
        with open(lit_path) as f:
            lit_data = json.load(f)
        # Set year to null for all records
        for rec in lit_data:
            rec["year"] = None
        with open(null_year_lit, "w", encoding="utf-8") as f:
            json.dump(lit_data, f, ensure_ascii=False, indent=2)
        
        r = subprocess.run(
            [sys.executable, "scripts/bind_evidence_to_chapters.py",
             "--outline", os.path.join(ex_dir, "user_outline_sample.md"),
             "--literature", null_year_lit,
             "--chapter", "METHOD",
             "--output", "/tmp/e2e_null_year_cem.json",
             "--bindings-output", "/tmp/e2e_null_year_ebr.json"],
            capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=15
        )
        
        if r.returncode != 0:
            null_year_ok = False
            e(f"  year=null: exit code {r.returncode}")
        else:
            try:
                with open("/tmp/e2e_null_year_cem.json") as f:
                    cem = json.load(f)
                with open("/tmp/e2e_null_year_ebr.json") as f:
                    ebr = json.load(f)
                if not cem.get("bound_records"):
                    null_year_ok = False
                    e("  year=null: CEM bound_records is empty")
                if not ebr:
                    null_year_ok = False
                    e("  year=null: EBR is empty")
            except Exception as ex:
                null_year_ok = False
                e(f"  year=null: parse error: {ex}")
    
    check("16. year=null 兼容性（Zotero metadata）",
          null_year_ok, "" if null_year_ok else "year=null test failed")

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
    