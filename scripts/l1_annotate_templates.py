#!/usr/bin/env python3
"""
L1: 元数据标注 — 给16,722个模板添加v5.0学科聚类标签。

方法: 通过 (source, discipline) 建立模板 pdf_id → Layer 3 paper_id → cluster 映射。
最大并行: 按JSONL文件分片，每文件独立进程处理。
"""

import json, os, sys, re, time, subprocess
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent.parent
ASSETS = BASE / "assets"
L3_DIR = BASE / ".phd_build" / "layer3"
MAPPING_OUT = BASE / ".phd_build" / "pdf_cluster_mapping.json"


def norm_disc(d):
    """标准化学科名用于匹配"""
    d = d.lower().strip().replace('_', ' ').replace('-', ' ')
    return re.sub(r'\s+', ' ', d)


def build_mapping():
    """构建 pdf_id → (paper_id, v5_cluster) 映射"""
    print("Building pdf_id → cluster mapping...")
    
    # Step 1: Collect all template pdf_ids with their source+discipline
    tpl_entries = []  # (source, norm_disc, pdf_id)
    for root, dirs, files in os.walk(ASSETS):
        for f in files:
            if not f.endswith('.jsonl'): continue
            with open(os.path.join(root, f)) as fh:
                for line in fh:
                    if not line.strip(): continue
                    t = json.loads(line)
                    pid = t.get('pdf_id', '')
                    if pid:
                        tpl_entries.append((
                            t.get('source', ''),
                            norm_disc(t.get('_discipline', '')),
                            pid
                        ))
    
    unique_entries = list(set(tpl_entries))
    unique_entries.sort(key=lambda x: (x[0], x[1], x[2]))
    print(f"  Unique template pdf_ids: {len(unique_entries)}")
    
    # Step 2: Collect Layer 3 papers sorted by (source, discipline, paper_id)
    l3_papers = []
    for f in sorted(L3_DIR.glob("*.json")):
        p = json.load(open(f))
        pid = p.get('paper_id', f.stem)
        src = p.get('source', '')
        rd = norm_disc(p.get('raw_discipline', ''))
        cl = p.get('a1_cluster', 'UNKNOWN')
        l3_papers.append((src, rd, pid, cl))
    
    print(f"  Layer 3 papers: {len(l3_papers)}")
    
    # Step 3: Match by (source, discipline)
    # Group L3 papers by (source, norm_disc)
    l3_groups = defaultdict(list)
    for src, rd, pid, cl in l3_papers:
        l3_groups[(src, rd)].append((pid, cl))
    
    # For each template pdf_id, find matching L3 paper
    mapping = {}
    used_papers = set()
    unmatched_tpl = 0
    
    for src, disc, pdf_id in unique_entries:
        # Find matching group
        group_key = (src, disc)
        avail = [p for p in l3_groups.get(group_key, []) if p[0] not in used_papers]
        
        if avail:
            # Take first available
            paper_id, cluster = avail[0]
            used_papers.add(paper_id)
            mapping[pdf_id] = {"paper_id": paper_id, "cluster": cluster}
        else:
            # Try fuzzy match: find L3 group that contains this discipline
            fuzzy_match = None
            for (l3_src, l3_disc), papers in l3_groups.items():
                if l3_src == src and (disc in l3_disc or l3_disc in disc):
                    avail = [p for p in papers if p[0] not in used_papers]
                    if avail:
                        fuzzy_match = (l3_disc, avail[0])
                        break
            
            if fuzzy_match:
                paper_id, cluster = fuzzy_match[1]
                used_papers.add(paper_id)
                mapping[pdf_id] = {"paper_id": paper_id, "cluster": cluster, "match_type": "fuzzy"}
            else:
                unmatched_tpl += 1
                # Fallback: use _layer from template
                mapping[pdf_id] = {"cluster": "UNKNOWN", "match_type": "fallback"}
    
    # Save mapping
    with open(MAPPING_OUT, "w") as fh:
        json.dump(mapping, fh, ensure_ascii=False, indent=2)
    
    # Stats
    clusters = defaultdict(int)
    for v in mapping.values():
        clusters[v.get("cluster", "UNKNOWN")] += 1
    
    print(f"\n  Mapped: {len(mapping)}")
    print(f"  Unmatched (fallback): {unmatched_tpl}")
    print(f"  Cluster distribution:")
    for c, n in sorted(clusters.items(), key=lambda x:-x[1]):
        print(f"    {c}: {n}")
    
    return mapping


def main():
    chunk_total = int(sys.argv[sys.argv.index("--chunks") + 1]) if "--chunks" in sys.argv else 1
    chunk_idx = int(sys.argv[sys.argv.index("--chunk") + 1]) if "--chunk" in sys.argv else 0
    
    if chunk_idx == 0:
        # Build mapping once (only chunk 0 does this)
        mapping = build_mapping()
    else:
        # Wait for mapping to exist
        while not MAPPING_OUT.exists():
            time.sleep(1)
        mapping = json.load(open(MAPPING_OUT))
    
    print(f"Chunk {chunk_idx}/{chunk_total}: annotating templates...")
    
    # Collect all JSONL files
    all_files = []
    for root, dirs, files in os.walk(ASSETS):
        for f in files:
            if f.endswith('.jsonl'):
                all_files.append(os.path.join(root, f))
    
    all_files.sort()
    total = len(all_files)
    
    # Assign files to this chunk
    chunk_files = [f for i, f in enumerate(all_files) if i % chunk_total == chunk_idx]
    
    print(f"  {len(chunk_files)}/{total} JSONL files assigned")
    
    stats = {"processed": 0, "annotated": 0, "skipped": 0}
    
    for filepath in chunk_files:
        rel = filepath.replace(str(BASE), '')
        lines = []
        annotated = 0
        with open(filepath) as fh:
            for line in fh:
                if not line.strip(): continue
                t = json.loads(line)
                stats["processed"] += 1
                
                pdf_id = t.get('pdf_id', '')
                if pdf_id and pdf_id in mapping:
                    t['v5_cluster'] = mapping[pdf_id].get('cluster', 'UNKNOWN')
                    annotated += 1
                elif '_layer' in t:
                    # Fallback: old layer → new cluster
                    layer_map = {
                        'HUM_SOC': 'HUM_POL_ECON',
                        'TECH_LIFE': 'SCI_TECH',
                        'GLOBAL': 'GLOBAL',
                        'MATH_PHYS': 'SCI_TECH',
                    }
                    t['v5_cluster'] = layer_map.get(t.get('_layer', ''), 'GLOBAL')
                else:
                    t['v5_cluster'] = 'GLOBAL'
                
                lines.append(json.dumps(t, ensure_ascii=False))
        
        # Write back
        with open(filepath, "w") as fh:
            fh.write('\n'.join(lines) + '\n')
        
        stats["annotated"] += annotated
        print(f"  ✅ {rel}: {annotated} annotated")
    
    print(f"Chunk {chunk_idx}: {stats['processed']} templates, {stats['annotated']} annotated")


if __name__ == "__main__":
    main()
