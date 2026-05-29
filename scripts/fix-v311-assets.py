#!/usr/bin/env python3
"""
v3.1.1 Asset Layer Fix — Re-run after G4 classify to ensure:
1. GLOBAL/TECH_LIME/HUM_SOC layer assignment per LAYER_ASSIGNMENT_RULES
2. Zero overlap across layers
3. quality/ files per category per layer  
4. ___ → [...] placeholder migration
5. PII scan

Usage: python3 scripts/fix-v311-assets.py
Requires: CLASSIFIED_MASTER.jsonl in data/classified/
"""
import json, re, sys
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")
ASSETS = BASE / "assets"

def safe_write(path, entries):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')

def load_jsonl(path):
    if not path.exists(): return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

# Tech/science disciplines
TECH_DISCIPLINES = {
    "физико-математические науки", "физико-математических наук",
    "биологические науки", "биологических наук",
    "химические науки", "химических наук",
    "технические науки", "технических наук",
    "географические науки", "географических наук",
    "геолого-минералогические науки", "геолого-минералогических наук",
    "медицинские науки", "медицинских наук",
    "фармацевтических наук", "engineering",
}

HUM_SOC_DISCIPLINES = {
    "исторические науки", "исторических наук",
    "филологические науки", "филологических наук",
    "философские науки", "философских наук",
    "культурология", "культурологии",
    "искусствоведение", "искусствоведения",
    "педагогические науки", "педагогических наук",
    "психологические науки", "психологических наук",
    "социологические науки", "социологических наук",
    "политические науки", "политических наук",
    "экономические науки", "экономических наук",
    "юридические науки", "юридических наук",
}

def get_cluster(subject):
    s = subject.lower().replace("_", " ").strip()
    if s in TECH_DISCIPLINES: return "TECH_LIFE"
    if s in HUM_SOC_DISCIPLINES: return "HUM_SOC"
    if "други" in s: return "TECH_LIFE"
    return None

# Main
cls_master = load_jsonl(BASE / "data/classified/CLASSIFIED_MASTER.jsonl")
print(f"Loaded {len(cls_master)} classified entries")

# Track per-template cluster distribution
template_clusters = defaultdict(set)
template_disciplines = defaultdict(set)
for e in cls_master:
    tmpl = e.get("template", "").strip()
    subj = e.get("subject", "").strip().lower().replace("_", " ")
    cluster = get_cluster(subj)
    if cluster:
        template_clusters[tmpl].add(cluster)
        template_disciplines[tmpl].add(subj)

# Assign layers
layer_entries = defaultdict(list)
for e in cls_master:
    tmpl = e.get("template", "").strip()
    subj = e.get("subject", "").strip().lower().replace("_", " ")
    cluster = get_cluster(subj)
    qs = e.get("quality_score", 1)
    n_clusters = len(template_clusters.get(tmpl, set()))
    is_global_cat = e.get("category", "") in ("TRANSITION",)
    
    if n_clusters >= 2 or is_global_cat:
        if qs >= 2:
            layer_entries["GLOBAL"].append(e)
        elif cluster:
            layer_entries[cluster].append(e)
    elif cluster:
        layer_entries[cluster].append(e)

# Write master files
for layer in ["GLOBAL", "TECH_LIFE", "HUM_SOC", "ART_SPORT"]:
    entries = layer_entries.get(layer, [])
    if entries:
        safe_write(ASSETS / f"cluster/{layer}/master/MASTER.jsonl", entries)
        print(f"  {layer}/master/MASTER.jsonl: {len(entries)} entries")

# Generate quality files (no cross-layer overlap)
for layer in ["GLOBAL", "TECH_LIFE", "HUM_SOC", "ART_SPORT"]:
    entries = layer_entries.get(layer, [])
    if not entries: continue
    q2 = [e for e in entries if e.get("quality_score") == 2]
    by_cat = defaultdict(list)
    for e in q2:
        by_cat[e.get("category", "OTHER")].append(e)
    for cat, cat_entries in by_cat.items():
        safe_write(ASSETS / f"cluster/{layer}/quality/QUALITY2_{cat}.jsonl", cat_entries)
    safe_write(ASSETS / f"cluster/{layer}/quality/QUALITY2_ALL.jsonl", q2)

# Verify zero overlap
all_templates = {}
for layer in ["GLOBAL", "TECH_LIFE", "HUM_SOC", "ART_SPORT"]:
    all_templates[layer] = {e.get("template", "") for e in layer_entries.get(layer, [])}
overlaps = [(a, b, len(all_templates[a] & all_templates[b]))
            for i, a in enumerate(all_templates) for j, b in enumerate(all_templates) if i < j
            if all_templates[a] & all_templates[b]]
print(f"Zero overlap: {'PASS' if not overlaps else 'FAIL: '+str(overlaps)}")

# Migrate ___ → [...]
placeholder_count = 0
for entries in layer_entries.values():
    for e in entries:
        old_t = e.get("template", "")
        new_t = re.sub(r'_+', '[...]', old_t)
        if old_t != new_t:
            placeholder_count += old_t.count("___")
            e["template"] = new_t

# Fix standalone UTILS files
for path in [
    ASSETS / "global/master/UTILS.jsonl",
    ASSETS / "cluster/TECH_LIFE/master/UTILS.jsonl",
]:
    if path.exists():
        with open(path) as f: content = f.read()
        new_content = re.sub(r'_+', '[...]', content)
        if content != new_content:
            with open(path, 'w') as f: f.write(new_content)

# PII scan
name_patterns = [
    r'\b[А-Я][а-я]+ [А-Я][а-я]+(?: [А-Я][а-я]+)?\b',
    r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b',
    r'\b(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}\b',
]
pii_hits = []
for e in cls_master:
    for k in ["template", "when_to_use", "common_mistakes"]:
        text = str(e.get(k, ""))
        for pat in name_patterns:
            for m in re.findall(pat, text):
                if len(m) >= 6:
                    pii_hits.append(m)

# Write report
report = {
    "version": "3.1.1",
    "layers": {l: len(layer_entries.get(l, [])) for l in ["GLOBAL", "TECH_LIFE", "HUM_SOC", "ART_SPORT"]},
    "placeholders_fixed": placeholder_count,
    "pii_hits": len(set(pii_hits)),
    "zero_overlap": len(overlaps) == 0,
}
safe_write(ASSETS / "v3.1.1_FIX_REPORT.json", [report])
print(f"\nDone. Report: {ASSETS / 'v3.1.1_FIX_REPORT.json'}")
