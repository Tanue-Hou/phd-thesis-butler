#!/usr/bin/env python3
"""Generate TOP50.md from QUALITY2_SELECTION"""
import json, sys, argparse, os
from collections import defaultdict

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--category', default=None)
    args = parser.parse_args()
    
    entries = []
    with open(args.input) as f:
        for line in f:
            if line.strip():
                e = json.loads(line)
                if e.get('quality_score') == 2:
                    entries.append(e)
    
    groups = defaultdict(list)
    for e in entries:
        groups[e.get('category','unknown')].append(e)
    
    os.makedirs(args.output_dir, exist_ok=True)
    for cat, items in groups.items():
        if args.category and cat != args.category:
            continue
        top = sorted(items, key=lambda x: len(x.get('template','')), reverse=True)[:50]
        fname = f"{args.output_dir}/TOP50_{cat}.md"
        with open(fname, 'w') as f:
            f.write(f"# Top 50 Templates — {cat}\n\n")
            for i, e in enumerate(top, 1):
                f.write(f"### {i}. {e.get('template','')}\n")
                f.write(f"- subtype: {e.get('subtype','')}\n")
                f.write(f"- when_to_use: {e.get('when_to_use','')}\n")
                f.write(f"- quality: {e.get('quality_score',0)}\n\n")
        print(f'Generated: {fname} ({len(top)} entries)')
