#!/usr/bin/env python3
"""Read-only audit by default; explicit migration writes a new isolated assets copy.
No inferred source identities, rights, classifications or statistical cleaning.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sys
import tempfile

KEY_MAP = {key.replace('_', '[...]'): key for key in (
    'paper_id', 'record_type', 'when_to_use', 'quality_score', 'schema_version', 'common_mistakes')}
FIELDS = ('typical_structures', 'chapter_sequence', 'research_question_types',
          'methodology_routes', 'logic_chains', 'validation_patterns', 'chapter_writing_rules')


def strict_json_loads(text):
    """Reject duplicate object keys and nonstandard numbers before migration."""
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ValueError(f'Nonstandard JSON number: {value}')
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError(f'JSON number exceeds finite float range: {value}')
        return number
    return json.loads(text, object_pairs_hook=object_pairs, parse_constant=invalid_constant,
                      parse_float=finite_float)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def normalize_keys(row):
    """Only rename six known damaged top-level keys; never modify values/slots."""
    result = dict(row)
    changes = []
    for old, new in KEY_MAP.items():
        if old not in row:
            continue
        if new in row:
            raise ValueError(f'Key collision {old} -> {new}; explicit review required')
        result[new] = result.pop(old)
        changes.append({'old_key':old, 'new_key':new})
    return result, changes


def iter_strings(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_strings(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_strings(child, path + (index,))
    elif isinstance(value, str):
        yield path, value


def plan(source, repair_ids=False):
    if Path(source).is_symlink():
        raise ValueError('Symlink source refused')
    source = Path(source).resolve()
    if not source.is_dir():
        raise ValueError('Missing assets directory')
    paths = sorted(source.rglob('*'))
    if any(p.is_symlink() for p in paths):
        raise ValueError('Symlink source refused; inspect explicitly')
    originals = {str(p.relative_to(source)):p.read_bytes() for p in paths if p.is_file()}
    outputs = dict(originals)
    key_changes, id_changes, warnings = [], [], []
    raw_rows, repaired_rows = [], []
    parsed_docs = {}
    for relative, data in originals.items():
        if relative.endswith('.jsonl'):
            rows = []
            for line_num, line in enumerate(data.decode('utf-8').splitlines(), 1):
                if not line.strip():
                    continue
                row = strict_json_loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f'{relative}:{line_num}: expected object')
                fixed, changes = normalize_keys(row)
                for key in fixed:
                    if '[...]' in key:
                        warnings.append({'file':relative, 'line':line_num, 'unresolved_key':key})
                if changes:
                    key_changes.append({'file':relative, 'line':line_num, 'changes':changes})
                rows.append(fixed); raw_rows.append(row); repaired_rows.append(fixed)
            parsed_docs[relative] = rows
            if any(c['file'] == relative for c in key_changes):
                outputs[relative] = ('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows)+'\n').encode('utf-8')
        elif relative.endswith('.json'):
            parsed_docs[relative] = strict_json_loads(data)

    duplicate_groups = []
    for relative, document in parsed_docs.items():
        if not relative.startswith('references/disciplines/') or not relative.endswith('.json'):
            continue
        groups = defaultdict(list)
        for field in FIELDS:
            for index, row in enumerate(document.get(field, [])):
                if isinstance(row, dict) and row.get('id'):
                    groups[row['id']].append((field, index, row))
        for old_id, entries in groups.items():
            if len(entries) < 2:
                continue
            duplicate_groups.append({'file':relative, 'old_id':old_id, 'count':len(entries)})
            if not repair_ids:
                continue
            # A reference to the old ambiguous ID cannot be reassigned automatically.
            own_paths = {(field, index, 'id') for field, index, _ in entries}
            for other_name, other_doc in parsed_docs.items():
                for pointer, value in iter_strings(other_doc):
                    if old_id in value and not (other_name == relative and pointer in own_paths):
                        raise ValueError(f'Ambiguous ID reference {old_id} in {other_name}:{pointer}')
            used = set(groups)
            for field, index, row in entries:
                payload = {k:v for k,v in row.items() if k != 'id'}
                new_id = f"{document.get('cluster','unknown').lower()}_{field}_" + digest(canonical(payload).encode())
                if new_id in used:
                    raise ValueError(f'Duplicate semantic content or ID collision: {relative}:{old_id}')
                used.add(new_id)
                row['id'] = new_id
                id_changes.append({'file':relative, 'field':field, 'index':index, 'old_id':old_id, 'new_id':new_id})
        if repair_ids:
            all_ids = [r.get('id') for f in FIELDS for r in document.get(f, []) if isinstance(r, dict) and r.get('id')]
            if len(all_ids) != len(set(all_ids)):
                raise ValueError(f'Generated ID collision in {relative}')
        if repair_ids and any(c['file'] == relative for c in id_changes):
            outputs[relative] = (json.dumps(document, ensure_ascii=False, indent=2)+'\n').encode()

    def counts(rows):
        return {'physical_rows':len(rows),
                'unique_complete_json_records':len({canonical(r) for r in rows}),
                'unique_template_texts':len({r['template'] for r in rows if isinstance(r.get('template'),str)}),
                'missing_quality_score_rows':sum('quality_score' not in r for r in rows),
                'nonempty_paper_id_rows':sum(bool(r.get('paper_id')) for r in rows)}
    report = {'schema_version':1, 'mode':'preview', 'counts_before':counts(raw_rows),
              'counts_after_proposed_keys':counts(repaired_rows),
              'jsonl_files':sum(p.endswith('.jsonl') for p in originals),
              'key_changed_rows':len(key_changes), 'id_duplicate_groups':duplicate_groups,
              'id_changes':id_changes, 'key_changes':key_changes, 'warnings':warnings,
              'limitations':['Physical rows and template counts are not counts of verified papers.',
                             'Restored quality_score is historical metadata, not newly certified quality.',
                             'Identity, classifications, source rights and noisy chapter statistics unchanged.',
                             'ID rewrite cannot update references outside this assets snapshot; review manifest before adoption.'],
              'files':[{'path':p,'before_sha256':digest(b),'after_sha256':digest(outputs[p]),
                        'changed':b != outputs[p]} for p,b in originals.items()]}
    return outputs, report


def apply_plan(source, destination, outputs, report):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.exists() or source == destination or source in destination.parents or destination in source.parents:
        raise ValueError('Output must be a new directory outside source tree')
    current_files = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}
    if current_files != set(outputs):
        raise ValueError('Source file list changed after preview')
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('Source symlink appeared after preview')
    # Guard against stale preview/source changes before copying bytes.
    for entry in report['files']:
        if digest((source/entry['path']).read_bytes()) != entry['before_sha256']:
            raise ValueError('Source changed after preview; rerun audit')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.asset-repair-', dir=destination.parent))
    try:
        for relative,data in outputs.items():
            path = temporary/'assets'/relative; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        manifest = dict(report, mode='isolated_copy')
        (temporary/'REPAIR_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        (temporary/'AUDIT_COUNTS.json').write_text(json.dumps({k:manifest[k] for k in ('counts_before','counts_after_proposed_keys','jsonl_files','limitations')},ensure_ascii=False,indent=2),encoding='utf-8')
        os.rename(temporary,destination)
    finally:
        if temporary.exists():shutil.rmtree(temporary)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets',type=Path,default=Path(__file__).resolve().parent.parent/'assets')
    parser.add_argument('--repair-ids',action='store_true')
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    try:
        outputs,report=plan(args.assets,args.repair_ids)
        if args.apply:
            if not args.output_dir:raise ValueError('--apply requires --output-dir')
            apply_plan(args.assets,args.output_dir,outputs,report)
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return 0
    except (ValueError,OSError,TypeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr); return 1

if __name__=='__main__':sys.exit(main())
