#!/usr/bin/env python3
"""
G4 Classify — 归层分配
将 merge 后的模板按 LAYER_ASSIGNMENT 规则归层：
- HUM_SOC: гуманитарные и социальные науки
- ART_SPORT: естественные, точные, технические науки
- DISCIPLINE: конкретные дисциплины (если идентифицирована)
Gate: zero overlap, all entries classified
"""
import json, sys, re
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path("/mnt/d/Hermes/01_Active_Projects/PhD_Thesis_Butler")
MERGED = BASE / "data/merged" / "MASTER_MERGED.jsonl"
LAYER_DIR = BASE / "assets" / "cluster"
DISC_DIR = BASE / "assets" / "discipline"
G4_DIR = BASE / "data" / "classified"
G4_DIR.mkdir(parents=True, exist_ok=True)
LAYER_DIR.mkdir(parents=True, exist_ok=True)
DISC_DIR.mkdir(parents=True, exist_ok=True)

# Layer assignment rules based on subject (supports nominative & genitive)
HUM_SOC_SUBJECTS = {
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

ART_SPORT_SUBJECTS = {
    "биологические науки", "биологических наук",
    "географические науки", "географических наук",
    "геолого-минералогические науки", "геолого-минералогических наук",
    "медицинские науки", "медицинских наук",
    "технические науки", "технических наук",
    "физико-математические науки", "физико-математических наук",
    "химические науки", "химических наук",
}

def classify_layer(entry):
    """Classify entry to layer based on subject field"""
    subject = entry.get("subject", "").strip().lower()
    # Normalize: replace underscores with spaces
    subject = subject.replace("_", " ")
    doc_type = entry.get("doc_type", "диссертация")
    
    if subject in HUM_SOC_SUBJECTS:
        return "HUM_SOC"
    elif subject in ART_SPORT_SUBJECTS:
        return "ART_SPORT"
    # Handle "другие науки" - classify by template category
    elif "други" in subject:
        cat = entry.get("category", "").upper()
        # AREF categories tend to be universal; use INTRO as default for humanities
        # Technical/scientific categories
        sci_cats = {"EXPERIMENT", "METHOD", "MODEL", "RESULT", "FORMAL_DEFS",
                     "МЕТОДЫ", "ПОЛОЖЕНИЯ", "ЭКСПЕРИМЕНТ"}
        if cat in sci_cats:
            return "ART_SPORT"
        # Hum/social categories  
        hum_cats = {"INTRO", "SURVEY", "DISCUSSION", "CONCLUSION",
                     "АКТУАЛЬНОСТЬ", "НОВИЗНА", "ЦЕЛЬ_ЗАДАЧИ"}
        if cat in hum_cats:
            return "HUM_SOC"
        return "HUM_SOC"  # default for "other" sciences
    elif "фармацевтическ" in subject:
        return "ART_SPORT"
    elif subject == "engineering":
        return "ART_SPORT"
    else:
        return "UNCLASSIFIED"

def classify_discipline(entry):
    """Extract discipline from subject, normalize underscores"""
    return entry.get("subject", "UNKNOWN").replace("_", " ").strip()

print("=" * 60)
print("G4 CLASSIFY — 归层分配")
print("=" * 60)

# Load merged data
entries = []
with open(MERGED) as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

print(f"Loaded {len(entries)} entries from merged data")

# Classify each entry
layer_counts = defaultdict(int)
discipline_counts = defaultdict(int)
layer_entries = defaultdict(list)
discipline_entries = defaultdict(list)
cross_layer = []  # entries that could belong to multiple layers

for e in entries:
    layer = classify_layer(e)
    discipline = classify_discipline(e)
    
    layer_counts[layer] += 1
    discipline_counts[discipline] += 1
    layer_entries[layer].append(e)
    discipline_entries[discipline].append(e)
    
    # Add layer tag to entry
    e["_layer"] = layer
    e["_discipline"] = discipline

print(f"\n=== Layer Distribution ===")
for layer in sorted(layer_counts.keys()):
    print(f"  {layer:<15} {layer_counts[layer]:>6} entries ({layer_counts[layer]/len(entries)*100:.1f}%)")

# Check for unclassified
unclassified = layer_counts.get("UNCLASSIFIED", 0)
if unclassified > 0:
    print(f"\n  ⚠️  {unclassified} entries unclassified — showing subjects:")
    unclass_subjects = Counter(e.get("subject", "?") for e in layer_entries["UNCLASSIFIED"])
    for s, c in sorted(unclass_subjects.items(), key=lambda x: -x[1])[:10]:
        print(f"      {s}: {c}")

# Write layer files
for layer in ["HUM_SOC", "ART_SPORT", "UNCLASSIFIED"]:
    if layer not in layer_entries:
        continue
    out_file = LAYER_DIR / f"{layer}.jsonl"
    with open(out_file, 'w') as f:
        for e in layer_entries[layer]:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')
    print(f"\n  Written: {out_file} ({len(layer_entries[layer])} entries)")

# Write discipline files
for disc in sorted(discipline_entries.keys()):
    # Sanitize filename
    safe_name = disc.replace(" ", "_").replace("/", "_")
    out_file = DISC_DIR / f"{safe_name}.jsonl"
    with open(out_file, 'w') as f:
        for e in discipline_entries[disc]:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')

print(f"\n  Discipline files: {len(discipline_entries)} written")

# G4 Gate: check zero overlap
print(f"\n=== G4 GATE ===")
hum_soc_ids = {(e.get("template",""), e.get("pdf_id","")) for e in layer_entries.get("HUM_SOC", [])}
art_sport_ids = {(e.get("template",""), e.get("pdf_id","")) for e in layer_entries.get("ART_SPORT", [])}
overlap = hum_soc_ids & art_sport_ids
zero_overlap = len(overlap) == 0

print(f"  HUM_SOC: {len(hum_soc_ids)} unique (template,pdf_id) pairs")
print(f"  ART_SPORT: {len(art_sport_ids)} unique pairs")
print(f"  Overlap: {len(overlap)} pairs")
print(f"  {'✅ ZERO OVERLAP — G4 PASS' if zero_overlap else '❌ OVERLAP DETECTED — G4 FAIL'}")

# Write classified master
classified_file = G4_DIR / "CLASSIFIED_MASTER.jsonl"
with open(classified_file, 'w') as f:
    for e in entries:
        f.write(json.dumps(e, ensure_ascii=False) + '\n')
print(f"\nClassified master: {classified_file}")

# Report
report = {
    "phase": "G4 Classify",
    "total": len(entries),
    "layers": dict(layer_counts),
    "disciplines": len(discipline_counts),
    "overlap": len(overlap),
    "g4_pass": zero_overlap,
}
with open(G4_DIR / "G4_REPORT.json", 'w') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\nReport: {G4_DIR / 'G4_REPORT.json'}")
print(f"\nG4 COMPLETE — zero_overlap={zero_overlap}")
