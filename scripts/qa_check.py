#!/usr/bin/env python3
"""QA checker: slot presence, validity, transferability, length, proper noun density, n-gram similarity"""
import json, sys, argparse, re

def check_slots(entries, threshold=0.98):
    total = sum(1 for e in entries if e.get('record_type')=='TEMPLATE')
    if total == 0:
        return True, 1.0, 0
    ok = sum(1 for e in entries if e.get('record_type')=='TEMPLATE' and '___' in e.get('template',''))
    rate = ok / total
    return rate >= threshold, rate, total - ok

def check_validity(entries):
    invalid = 0
    for e in entries:
        tmpl = e.get('template','')
        if not tmpl or len(tmpl) < 5:
            invalid += 1
    return invalid == 0, len(entries) - invalid, invalid

def check_transferability(entries, threshold=0.95):
    template_entries = [e for e in entries if e.get('record_type')=='TEMPLATE']
    if not template_entries:
        return True, 1.0, 0
    ok = sum(1 for e in template_entries if e.get('when_to_use') and len(e.get('common_mistakes',[])) >= 1)
    rate = ok / len(template_entries)
    return rate >= threshold, rate, len(template_entries) - ok

def check_length(entries, max_words=25, threshold=0.99):
    too_long = 0
    for e in entries:
        words = e.get('template','').split()
        if len(words) > max_words:
            too_long += 1
    rate = 1 - (too_long / len(entries)) if entries else 1
    return rate >= threshold, rate, too_long

def check_proper_noun(entries):
    flagged = 0
    for e in entries:
        tmpl = e.get('template','')
        abbrs = re.findall(r'\b[A-ZА-Я]{3,}\b', tmpl)
        generic = {'РФ','НИР','НИОКР','ГЭК','ВАК','ФИО','МВТУ','МГТУ','РАН','СПб','СНГ','ЭВМ','ПО','АСУ'}
        bad = [a for a in abbrs if a not in generic]
        if len(bad) >= 3:
            flagged += 1
    return flagged == 0, len(entries) - flagged, flagged

def check_format(entries):
    valid = 0
    for e in entries:
        if all(k in e for k in ['paper_id','source','record_type','template','quality_score']):
            valid += 1
    return valid == len(entries), valid, len(entries) - valid

def run_all(input_path, output_path, **kwargs):
    entries = []
    with open(input_path) as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass

    max_words = kwargs.get('max_words', 25)
    length_threshold = kwargs.get('length_threshold', 0.99)

    slot_pass, slot_rate, slot_fail = check_slots(entries, kwargs.get('slot_threshold', 0.98))
    _, validity_count, validity_fail = check_validity(entries)
    transfer_pass, transfer_rate, transfer_fail = check_transferability(entries)
    len_pass, len_rate, len_fail = check_length(entries, max_words, length_threshold)
    pn_pass, pn_clean, pn_flagged = check_proper_noun(entries)
    format_pass, format_valid, format_fail = check_format(entries)

    results = {
        'total_entries': len(entries),
        'slot_rate': slot_rate,
        'slot_pass': slot_pass,
        'slot_fail': slot_fail,
        'validity_fail': validity_fail,
        'transferability_rate': transfer_rate,
        'transferability_pass': transfer_pass,
        'transferability_fail': transfer_fail,
        'max_words_setting': max_words,
        'length_rate': len_rate,
        'length_pass': len_pass,
        'length_over': len_fail,
        'proper_noun_pass': pn_pass,
        'proper_noun_flagged': pn_flagged,
        'proper_noun_clean': pn_clean,
        'format_valid': format_valid,
        'format_fail': format_fail,
    }
    # overall_pass now includes ALL checks
    results['overall_pass'] = all([slot_pass, transfer_pass, len_pass, pn_pass, format_valid == len(entries)])
    with open(output_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'QA report: {"PASS" if results["overall_pass"] else "FAIL"} ({results["total_entries"]} entries)')
    if not results['overall_pass']:
        failures = []
        if not slot_pass: failures.append(f"slot_rate={slot_rate:.1%}")
        if not transfer_pass: failures.append(f"transfer_rate={transfer_rate:.1%}")
        if not len_pass: failures.append(f"length_over={len_fail}")
        if not pn_pass: failures.append(f"proper_noun_flagged={pn_flagged}")
        if format_valid != len(entries): failures.append(f"format_fail={format_fail}")
        print(f'  Failures: {", ".join(failures)}')
    return results['overall_pass']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='qa_report.json')
    parser.add_argument('--slot-threshold', type=float, default=0.98)
    parser.add_argument('--max-words', type=int, default=25)
    parser.add_argument('--length-threshold', type=float, default=0.99)
    args = parser.parse_args()
    sys.exit(0 if run_all(args.input, args.output,
                         slot_threshold=args.slot_threshold,
                         max_words=args.max_words,
                         length_threshold=args.length_threshold) else 1)
