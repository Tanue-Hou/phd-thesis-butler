#!/usr/bin/env python3
"""Coverage check: 3-tier gap detection"""
import json, sys, argparse
from collections import defaultdict

COVERAGE_SPEC = {
    'N_core': 200,
    'N_mid': 80,
    'N_rare': 30,
    'core_subtypes': ['INTRO.objective','INTRO.tasks','SURVEY.gap','MODEL.assumptions',
                      'MODEL.boundary_conditions','MODEL.notation','MODEL.units',
                      'EXPERIMENT.metrics','EXPERIMENT.baselines','RESULT.numeric_reporting',
                      'RESULT.improvement_reporting','CONCLUSION.limitations','CONCLUSION.future_work',
                      'TRANSITION.paragraph_linkers','CONSERVATIVE.hedging','NUMERIC.error_report'],
    'mid_subtypes': ['SURVEY.taxonomy','SURVEY.comparison','SURVEY.positioning',
                     'METHOD.algorithm_steps','METHOD.implementation_details',
                     'DISCUSSION.interpretation_hedged','FORMAL_DEFS.definition',
                     'FORMAL_DEFS.symbol_introductions','CONNECTIVE.contrast',
                     'CONNECTIVE.addition','CONNECTIVE.cause_effect'],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='gap_report.json')
    parser.add_argument('--source', choices=['DIS','AREF'], default='DIS')
    args = parser.parse_args()
    
    counts = defaultdict(int)
    with open(args.input) as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                key = f"{obj.get('category','')}.{obj.get('subtype','')}"
                counts[key] += 1
    
    gaps = {'P0_core': [], 'P1_mid': [], 'P2_rare_filled': []}
    for st in COVERAGE_SPEC.get('core_subtypes', []):
        c = counts.get(st, 0)
        if c < COVERAGE_SPEC['N_core']:
            gaps['P0_core'].append({'subtype': st, 'current': c, 'target': COVERAGE_SPEC['N_core']})
    for st in COVERAGE_SPEC.get('mid_subtypes', []):
        c = counts.get(st, 0)
        if c < COVERAGE_SPEC['N_mid']:
            gaps['P1_mid'].append({'subtype': st, 'current': c, 'target': COVERAGE_SPEC['N_mid']})
    
    report = {
        'source': args.source,
        'total_entries': sum(counts.values()),
        'unique_subtypes': len(counts),
        'gaps': gaps,
        'all_covered': len(gaps['P0_core']) == 0 and len(gaps['P1_mid']) == 0,
    }
    with open(args.output, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f'Coverage: {report["total_entries"]} entries, {report["unique_subtypes"]} subtypes, {"ALL COVERED" if report["all_covered"] else f"{len(gaps["P0_core"])} P0 + {len(gaps["P1_mid"])} P1 gaps"}')
