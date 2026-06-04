#!/usr/bin/env python3
"""
validate_research_layer.py — v5.2 门禁验证脚本
检查 research_layer 完整性和端到端可用性。

Exit code: 0 = 全部通过，1 = 至少1项失败。
"""

import json
import os
import sys
import importlib.util

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


def main():
    rl = os.path.join(PROJECT_ROOT, "research_layer")
    assets = os.path.join(PROJECT_ROOT, "assets")

    print("=" * 60)
    print("research_layer 验证报告 (v5.2)")
    print(f"项目根目录: {PROJECT_ROOT}")
    print("=" * 60)

    # 1. research_layer/ 目录存在
    check("1. research_layer/ 目录存在", os.path.isdir(rl))

    # 2. WORKFLOW.md
    check("2. research_layer/WORKFLOW.md 存在",
          os.path.isfile(os.path.join(rl, "WORKFLOW.md")))

    # 3. QUERY_STRATEGY.md
    check("3. research_layer/QUERY_STRATEGY.md 存在",
          os.path.isfile(os.path.join(rl, "QUERY_STRATEGY.md")))

    # 4. sources/ 下至少有4个 profile 文件
    sources_dir = os.path.join(rl, "sources")
    if os.path.isdir(sources_dir):
        profiles = [f for f in os.listdir(sources_dir) if f.endswith("_profile.md")]
    else:
        profiles = []
    check("4. sources/ 下至少有4个 profile 文件 (至少4个)",
          len(profiles) >= 4, f"找到 {len(profiles)} 个")

    # 5. 8 个已知 profile 中至少 6 个存在
    expected_profiles = [
        "elibrary_profile.md",
        "dissercat_profile.md",
        "rsl_profile.md",
        "cyberleninka_profile.md",
        "arxiv_profile.md",
        "semantic_scholar_profile.md",
        "openalex_profile.md",
        "crossref_profile.md",
    ]
    found = [p for p in expected_profiles if os.path.isfile(os.path.join(sources_dir, p))]
    check("5. 8个已知 profile 中至少6个存在",
          len(found) >= 6, f"找到 {len(found)}/8: {', '.join(found)}")

    # 6. templates/ 下至少有3个学科模板
    tpl_dir = os.path.join(rl, "templates")
    if os.path.isdir(tpl_dir):
        templates = [f for f in os.listdir(tpl_dir) if os.path.isfile(os.path.join(tpl_dir, f))]
    else:
        templates = []
    check("6. templates/ 下至少有3个学科模板",
          len(templates) >= 3, f"找到 {len(templates)} 个")

    # 7. russian_literature_record.schema.json 存在且可解析
    lit_schema = os.path.join(assets, "references", "schemas",
                              "russian_literature_record.schema.json")
    if check("7. russian_literature_record.schema.json 存在",
             os.path.isfile(lit_schema)):
        try:
            with open(lit_schema, "r", encoding="utf-8") as f:
                json.load(f)
            print(f"      {PASS} JSON 可解析")
            results.append(True)
        except json.JSONDecodeError as e:
            print(f"      {FAIL} JSON 解析失败: {e}")
            results.append(False)

    # 8. russian_dissertation_record.schema.json 存在且可解析
    diss_schema = os.path.join(assets, "references", "schemas",
                               "russian_dissertation_record.schema.json")
    if check("8. russian_dissertation_record.schema.json 存在",
             os.path.isfile(diss_schema)):
        try:
            with open(diss_schema, "r", encoding="utf-8") as f:
                json.load(f)
            print(f"      {PASS} JSON 可解析")
            results.append(True)
        except json.JSONDecodeError as e:
            print(f"      {FAIL} JSON 解析失败: {e}")
            results.append(False)

    # Helper: import a module from file path
    def try_import(module_path, name):
        try:
            spec = importlib.util.spec_from_file_location(name, module_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return True, None
        except Exception as e:
            return False, str(e)

    # 9. normalize_russian_metadata.py 可执行（importable）
    norm_script = os.path.join(SCRIPT_DIR, "normalize_russian_metadata.py")
    if check("9. normalize_russian_metadata.py 可导入",
             os.path.isfile(norm_script)):
        ok, err = try_import(norm_script, "normalize_russian_metadata")
        check("   import 成功", ok, err)

    # 10. build_literature_review_brief.py 可执行（importable）
    brief_script = os.path.join(SCRIPT_DIR, "build_literature_review_brief.py")
    if check("10. build_literature_review_brief.py 可导入",
             os.path.isfile(brief_script)):
        ok, err = try_import(brief_script, "build_literature_review_brief")
        check("   import 成功", ok, err)

    # 11. examples/elibrary_sample.json 存在
    elib_sample = os.path.join(rl, "examples", "elibrary_sample.json")
    check("11. examples/elibrary_sample.json 存在",
          os.path.isfile(elib_sample))

    # 12. examples/dissercat_sample.json 存在
    diss_sample = os.path.join(rl, "examples", "dissercat_sample.json")
    check("12. examples/dissercat_sample.json 存在",
          os.path.isfile(diss_sample))

    # 13. 端到端测试：elibrary_sample -> normalize -> brief -> 非空Markdown
    print()
    print("  13. 端到端测试（elibrary_sample → normalize → brief → Markdown）")
    e2e_ok = True
    try:
        # 读取 sample
        with open(elib_sample, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        print(f"      {PASS} 读取 elibrary_sample.json 成功")

        # normalize via subprocess
        import tempfile, subprocess, sys as py_sys
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump(raw_data, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name
        norm_out = tmp_path.replace(".json", "_norm.json")
        r = subprocess.run(
            [py_sys.executable, norm_script, "--input", tmp_path, "--output", norm_out],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            raise RuntimeError(f"normalize failed: {r.stderr[:200]}")
        with open(norm_out, "r", encoding="utf-8") as f:
            normalized = json.load(f)
        print(f"      {PASS} normalize 成功 ({len(normalized)} records)")
        os.unlink(tmp_path)

        # brief via subprocess
        brief_out = tmp_path.replace(".json", "_brief.md")
        r2 = subprocess.run(
            [py_sys.executable, brief_script, "--input", norm_out, "--output", brief_out],
            capture_output=True, text=True, timeout=30
        )
        if r2.returncode != 0:
            raise RuntimeError(f"build_review failed: {r2.stderr[:200]}")
        with open(brief_out, "r", encoding="utf-8") as f:
            md_output = f.read()
        print(f"      {PASS} build_literature_review_brief 成功 ({len(md_output)} chars)")
        os.unlink(norm_out)
        os.unlink(brief_out)

        if isinstance(md_output, str) and len(md_output.strip()) > 0:
            print(f"      {PASS} 输出非空 Markdown ({len(md_output)} 字符)")
        else:
            print(f"      {FAIL} 输出为空或非字符串")
            e2e_ok = False
    except FileNotFoundError as e:
        print(f"      {FAIL} 文件未找到: {e}")
        e2e_ok = False
    except Exception as e:
        print(f"      {FAIL} 端到端测试失败: {e.__class__.__name__}: {e}")
        e2e_ok = False

    results.append(e2e_ok)

    # Summary
    print()
    print("=" * 60)
    total = len(results)
    passed = sum(results)
    failed = total - passed
    if failed == 0:
        print(f"全部通过: {passed}/{total} 项检查")
    else:
        print(f"结果: {passed} 通过, {failed} 失败 (共 {total} 项)")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
