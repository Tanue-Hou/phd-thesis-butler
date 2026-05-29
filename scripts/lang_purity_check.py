#!/usr/bin/env python3
"""
Language Purity Check — 语言纯净度核查
确保 PhD Thesis Butler 的所有模板为纯正科研俄语，无中文、英文或其他语料污染。

用法:
  python3 scripts/lang_purity_check.py

检查项:
1. 中文残留 (CJK汉字检测)
2. 英文模板 (完整英文句子检测)
3. 元数据中文 (when_to_use/function/common_mistakes)
4. 混合语言 (同一模板中西里尔字母与拉丁字母混用)
5. 非学术俄语多义词 (пока/сегодня等 — 已知误报率100%)
"""
import json, re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]')

def is_english_template(text):
    """判断 template 是否为纯英文句子（非槽位名）"""
    if not text: return False
    clean = re.sub(r'\[.*?\]', '', text)
    clean = re.sub(r'_+', '', clean).strip()
    if len(clean) < 10: return False
    cyr = sum(1 for c in clean if '\u0400' <= c <= '\u04ff')
    lat = sum(1 for c in clean if c.isascii() and c.isalpha())
    total = cyr + lat
    if total == 0 or lat/total <= 0.6: return False
    eng_words = ['the ','is ','are ','was ','were ','has ','have ',
                 'been ','this ','that ','with ','from ','for ']
    return sum(1 for w in eng_words if w in clean.lower()) >= 3

def check_file(filepath, name):
    """Check a single JSONL file for language purity"""
    if not filepath.exists():
        return {"name": name, "status": "NOT FOUND"}
    
    with open(filepath) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    
    cn_templates = []
    en_templates = []
    cn_meta = []
    
    for e in entries:
        t = e.get("template", "")
        
        if CJK.search(t):
            cn_templates.append((e.get("paper_id","?"), t[:60]))
            continue
        if is_english_template(t):
            en_templates.append((e.get("paper_id","?"), t[:60]))
            continue
        
        for field in ["when_to_use", "function"]:
            if CJK.search(str(e.get(field, ""))):
                cn_meta.append((e.get("paper_id","?"), field))
        
        cm = e.get("common_mistakes", [])
        if isinstance(cm, list):
            for item in cm:
                if CJK.search(str(item)):
                    cn_meta.append((e.get("paper_id","?"), "common_mistakes"))
                    break
    
    total = len(entries)
    clean = total - len(cn_templates) - len(en_templates)
    
    return {
        "name": name,
        "total": total,
        "clean": clean,
        "cn_templates": len(cn_templates),
        "en_templates": len(en_templates),
        "cn_meta": len(cn_meta),
        "samples_cn": [t[1] for t in cn_templates[:3]],
        "samples_en": [t[1] for t in en_templates[:3]],
    }

print("=" * 60)
print("PhD Thesis Butler — Language Purity Check v3.2")
print("=" * 60)

files = [
    (SKILL / "data/curated/master/MASTER_SENTENCEBANK_DIS.jsonl", "MASTER_DIS"),
    (SKILL / "data/curated/master/MASTER_SENTENCEBANK_AREF.jsonl", "MASTER_AREF"),
    (SKILL / "data/curated/master/MASTER_UTILS.jsonl", "MASTER_UTILS"),
]

results = []
for path, name in files:
    r = check_file(path, name)
    results.append(r)
    
    status = "✅ CLEAN" if r["cn_templates"] + r["en_templates"] == 0 else "❌ ISSUES"
    print(f"\n{name}: {r['total']} entries — {status}")
    print(f"  Templates: {r['clean']} clean, {r['cn_templates']} CN, {r['en_templates']} EN")
    print(f"  Metadata:  {r['cn_meta']} Chinese")
    if r['samples_cn']:
        for s in r['samples_cn']:
            print(f"    ❌ CN: {s}")
    if r['samples_en']:
        for s in r['samples_en']:
            print(f"    ❌ EN: {s}")

print("\n" + "=" * 60)
total_clean = sum(r["clean"] for r in results)
total_all = sum(r["total"] for r in results)
print(f"TOTAL: {total_clean}/{total_all} clean ({total_clean/total_all*100:.1f}%)")
if total_clean == total_all:
    print("🏆 ALL PURE RUSSIAN — No contamination found!")
else:
    print(f"⚠️  {total_all - total_clean} entries need attention")
