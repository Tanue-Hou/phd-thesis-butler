#!/usr/bin/env python3
"""Aggregator: dedup → merge → filter → split → coverage → stats"""
import json, sys, argparse, os, re
from collections import defaultdict

def dedup(input_path, output_path, fields):
    seen = set()
    with open(input_path) as f, open(output_path, 'w') as out:
        for line in f:
            obj = json.loads(line)
            key = tuple(obj.get(f, '') for f in fields)
            if key not in seen:
                seen.add(key)
                out.write(line)

def merge(input_path, output_path, threshold=0.85):
    items = []
    with open(input_path) as f:
        for line in f:
            items.append(json.loads(line))
    # Group by (record_type, category, subtype)
    groups = defaultdict(list)
    for it in items:
        groups[(it.get('record_type',''), it.get('category',''), it.get('subtype',''))].append(it)
    with open(output_path, 'w') as out:
        for key, group in groups.items():
            group.sort(key=lambda x: x.get('quality_score',0), reverse=True)
            kept = set()
            for it in group:
                tmpl = it.get('template','')
                if tmpl in kept:
                    continue
                kept.add(tmpl)
                out.write(json.dumps(it, ensure_ascii=False) + '\n')

def filter_q(input_path, output_path, drop_q0=True):
    with open(input_path) as f, open(output_path, 'w') as out:
        for line in f:
            obj = json.loads(line)
            if drop_q0 and obj.get('quality_score',0) == 0:
                continue
            out.write(line)

def split(input_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    by_type = {'TEMPLATE': [], 'UTIL': []}
    with open(input_path) as f:
        for line in f:
            obj = json.loads(line)
            rt = obj.get('record_type','')
            if rt in by_type:
                by_type[rt].append(obj)
    for rt, items in by_type.items():
        if rt == 'TEMPLATE':
            name = 'MASTER_SENTENCEBANK_DIS.jsonl'
        else:
            name = 'MASTER_UTILS.jsonl'
        with open(f'{out_dir}/{name}', 'w') as out:
            for it in items:
                out.write(json.dumps(it, ensure_ascii=False) + '\n')
    print(f'Split: {len(by_type["TEMPLATE"])} TEMPLATE, {len(by_type["UTIL"])} UTIL')

def coverage(input_path, spec_path, gap_output):
    with open(spec_path) as f:
        import yaml
        spec = yaml.safe_load(f)
    tiers = spec.get('coverage_tiers', {})
    counts = defaultdict(int)
    with open(input_path) as f:
        for line in f:
            obj = json.loads(line)
            cat = obj.get('category','')
            sub = obj.get('subtype','')
            counts[f'{cat}.{sub}'] += 1
    gaps = {'P0': [], 'P1': [], 'P2': []}
    # This is simplified; real impl checks each subtype against N_core/N_mid/N_rare
    with open(gap_output, 'w') as f:
        json.dump({'total_entries': sum(counts.values()), 'subtypes_covered': len(counts), 'gaps': {}}, f)
    print(f'Coverage: {sum(counts.values())} entries, {len(counts)} subtypes')

def stats(input_paths, output_path):
    stats_data = {}
    for label, path in input_paths.items():
        if not os.path.exists(path):
            continue
        entries = []
        with open(path) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        qs = defaultdict(int)
        for e in entries:
            qs[e.get('quality_score',0)] += 1
        cats = set(e.get('category','') for e in entries)
        stats_data[label] = {
            'count': len(entries),
            'quality_distribution': dict(qs),
            'categories_covered': len(cats),
        }
    with open(output_path, 'w') as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=2)
    print(f'Stats written to {output_path}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['dedup','merge','filter','split','coverage','stats'])
    parser.add_argument('--input', '--input-path')
    parser.add_argument('--output', '--output-path')
    parser.add_argument('--out-dir')
    parser.add_argument('--fields', nargs='+', default=['record_type','category','subtype','template'])
    parser.add_argument('--threshold', type=float, default=0.85)
    parser.add_argument('--drop-quality0', action='store_true', default=True)
    parser.add_argument('--spec', default=None)
    parser.add_argument('--gap-output', default=None)
    args = parser.parse_args()
    
    if args.action == 'dedup':
        dedup(args.input, args.output, args.fields)
    elif args.action == 'merge':
        merge(args.input, args.output, args.threshold)
    elif args.action == 'filter':
        filter_q(args.input, args.output, args.drop_quality0)
    elif args.action == 'split':
        split(args.input, args.out_dir)
    elif args.action == 'coverage':
        coverage(args.input, args.spec, args.gap_output)
    elif args.action == 'stats':
        stats(dict(zip(['dis','aref','utils'],[args.input])), args.output)
