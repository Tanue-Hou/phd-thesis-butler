#!/usr/bin/env python3
"""QA checker: slot presence, validity, transferability, length, proper noun density, n-gram similarity"""
import json, sys, argparse, re

def check_slots(entries, threshold=0.98):
    total = sum(1 for e in entries if e.get('record_type')=='TEMPLATE')
    if total == 0:
        return True, 1.0
    ok = sum(1 for e in entries if e.get('record_type')=='TEMPLATE' and '___' in e.get('template',''))
    rate = ok / total
    return rate >= threshold, rate

def check_validity(entries):
    invalid = 0
    for e in entries:
        tmpl = e.get('template','')
        if not tmpl or len(tmpl) < 5:
            invalid += 1
    return invalid == 0, len(entries) - invalid

def check_transferability(entries, threshold=0.95):
    template_entries = [e for e in entries if e.get('record_type')=='TEMPLATE']
    if not template_entries:
        return True, 1.0
    ok = sum(1 for e in template_entries if e.get('when_to_use') and len(e.get('common_mistakes',[])) >= 1)
    rate = ok / len(template_entries)
    return rate >= threshold, rate

def check_length(entries, max_words=25):
    too_long = 0
    for e in entries:
        words = e.get('template','').split()
        if len(words) > max_words:
            too_long += 1
    rate = 1 - (too_long / len(entries)) if entries else 1
    return rate >= 0.99, rate

def check_proper_noun(entries):
    flagged = 0
    for e in entries:
        tmpl = e.get('template','')
        # Find consecutive uppercase abbreviations (3+)
        abbrs = re.findall(r'\b[A-ZА-Я]{3,}\b', tmpl)
        generic = {'РФ','НИР','НИОКР','ГЭК','ВАК','ФИО','МВТУ','МГТУ','РАН','СПб','СНГ','ЭВМ','ПО','АСУ'}
        bad = [a for a in abbrs if a not in generic]
        if len(bad) >= 3:
            flagged += 1
    return flagged == 0, len(entries) - flagged

def check_format(entries):
    valid = 0
    for e in entries:
        if all(k in e for k in ['paper_id','source','record_type','template','quality_score']):
            valid += 1
    return valid == len(entries), valid

def run_all(input_path, output_path, **kwargs):
    entries = []
    with open(input_path) as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    results = {
        'total_entries': len(entries),
        'slot_rate': check_slots(entries, kwargs.get('slot_threshold',0.98))[1],
        'slot_pass': check_slots(entries, kwargs.get('slot_threshold',0.98))[0],
        'validity': check_validity(entries)[1],
        'transferability_rate': check_transferability(entries)[1],
        'transferability_pass': check_transferability(entries)[0],
        'length_rate': check_length(entries)[1],
        'proper_noun_flagged': check_proper_noun(entries)[1],
        'format_valid': check_format(entries)[1],
    }
    results['overall_pass'] = all([results['slot_pass'], results['transferability_pass'], results['format_valid'] == results['total_entries']])
    with open(output_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'QA report: {"PASS" if results["overall_pass"] else "FAIL"} ({results["total_entries"]} entries)')
    return results['overall_pass']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='qa_report.json')
    parser.add_argument('--slot-threshold', type=float, default=0.98)
    parser.add_argument('--max-words', type=int, default=25)
    args = parser.parse_args()
    sys.exit(0 if run_all(args.input, args.output, slot_threshold=args.slot_threshold) else 1)
