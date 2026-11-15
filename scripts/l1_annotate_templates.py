#!/usr/bin/env python3
"""Annotate copies using an explicitly reviewed source-identity manifest.

Discipline/source similarity is NOT work identity. Legacy ordered/fuzzy joins
are intentionally disabled. Existing assets are never modified by this CLI.
A manifest records human review, not an independent rights certification.
"""
import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ASSETS = BASE / 'assets'
CLUSTERS = {'AUTOMATION_CONTROL', 'SCI_TECH', 'AGRI_MED', 'ARTS_SPORTS', 'HUM_POL_ECON'}


def build_mapping(manifest=None):
    """Load reviewed exact (source, pdf_id) joins, reject conflicts/weak joins.

    Manifest: a JSON list with source, pdf_id, paper_id, cluster,
    identity_evidence (nonempty locator/hash/review reference), reviewed=true.
    No fallback on discipline, filenames, sequence or directory labels.
    """
    if manifest is None:
        raise ValueError('A reviewed identity manifest is required; ordered/fuzzy joins are disabled')
    records = json.loads(Path(manifest).read_text(encoding='utf-8'))
    if not isinstance(records, list):
        raise ValueError('Identity manifest must be a list')
    mapping = {}
    for row in records:
        if not isinstance(row, dict) or row.get('reviewed') is not True:
            raise ValueError('Every mapping must explicitly record reviewed=true')
        for field in ('source', 'pdf_id', 'paper_id', 'identity_evidence'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f'Missing identity field: {field}')
        if row.get('cluster') not in CLUSTERS:
            raise ValueError('Unsupported cluster in reviewed mapping')
        key = (row['source'], row['pdf_id'])
        if key in mapping and mapping[key] != row:
            raise ValueError(f'Conflicting source identity: {key}')
        mapping[key] = row
    if not mapping:
        raise ValueError('Empty manifest: no reviewed identities')
    return mapping


def annotate_record(record, mapping):
    result = dict(record)
    match = mapping.get((record.get('source'), record.get('pdf_id')))
    if match:
        if 'v5_cluster' in record:
            result.setdefault('legacy_v5_cluster', record['v5_cluster'])
        result.update(v5_cluster=match['cluster'],
                      v5_cluster_status='reviewed_identity_mapping',
                      mapped_paper_id=match['paper_id'],
                      identity_evidence=match['identity_evidence'])
    else:
        # Keep existing labels/data as history, do not fabricate a new label.
        result['v5_cluster_status'] = 'legacy_unverified' if record.get('v5_cluster') else 'unmapped'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verified-map', required=True, type=Path)
    parser.add_argument('--input-dir', default=ASSETS, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path,
                        help='New, nonexistent output directory; never the source assets')
    args = parser.parse_args()
    try:
        mapping = build_mapping(args.verified_map)
        source, destination = args.input_dir.resolve(), args.output_dir.resolve()
        if destination.exists() or source == destination or source in destination.parents or destination in source.parents:
            raise ValueError('Output must be a new directory outside the input tree')
        files = sorted(source.rglob('*.jsonl'))
        if not files:
            raise ValueError('No input JSONL files')
        # Validate all inputs before creating any output; no stale partial success.
        parsed = [(p.relative_to(source), [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]) for p in files]
        if any(not isinstance(row, dict) for _, rows in parsed for row in rows):
            raise ValueError('JSONL records must be objects')
        destination.mkdir(parents=True)
        for relative, rows in parsed:
            output = destination / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open('x', encoding='utf-8') as stream:
                for row in rows:
                    stream.write(json.dumps(annotate_record(row, mapping), ensure_ascii=False) + '\n')
        print(f'Wrote {len(files)} annotated copies. Source assets unchanged; unmatched labels remain unverified.')
        return 0
    except (ValueError, OSError, TypeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
