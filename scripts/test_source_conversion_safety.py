#!/usr/bin/env python3
"""Offline synthetic regressions. No source corpora modified."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import l1_annotate_templates as l1
import convert_v5_discipline_assets as converter


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def manifest(self, rows):
        file = self.root / 'map.json'
        file.write_text(json.dumps(rows))
        return file

    def row(self, **kwargs):
        return dict(source='S1', pdf_id='PDF1', paper_id='WORK1', cluster='SCI_TECH',
                    identity_evidence='review-reference:synthetic-1', reviewed=True, **kwargs)

    def test_no_ordered_or_fuzzy_mapping(self):
        with self.assertRaises(ValueError):
            l1.build_mapping()

    def test_exact_source_identity_only(self):
        mapping = l1.build_mapping(self.manifest([self.row()]))
        template = {'source':'S2', 'pdf_id':'PDF1', 'v5_cluster':'HUM_POL_ECON'}
        result = l1.annotate_record(template, mapping)
        self.assertEqual(result['v5_cluster'], 'HUM_POL_ECON')
        self.assertEqual(result['v5_cluster_status'], 'legacy_unverified')
        self.assertNotIn('mapped_paper_id', result)
        self.assertNotIn('v5_cluster_status', template)
        template['source'] = 'S1'
        self.assertEqual(l1.annotate_record(template, mapping)['mapped_paper_id'], 'WORK1')

    def test_unreviewed_and_conflict_rejected(self):
        row = self.row(); row['reviewed'] = False
        with self.assertRaises(ValueError):
            l1.build_mapping(self.manifest([row]))
        row = self.row(); other = dict(row, paper_id='WORK2')
        with self.assertRaises(ValueError):
            l1.build_mapping(self.manifest([row, other]))

    def test_annotation_cli_preserves_source(self):
        source = self.root / 'input'; source.mkdir()
        file = source / 'a.jsonl'; file.write_text('{"source":"S1","pdf_id":"PDF1"}\n')
        original = file.read_bytes()
        manifest = self.manifest([self.row()])
        output = self.root / 'out'
        cmd = [sys.executable, l1.__file__, '--verified-map', str(manifest), '--input-dir', str(source), '--output-dir', str(output)]
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.assertEqual(file.read_bytes(), original)
        self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.assertEqual(json.loads((output/'a.jsonl').read_text())['v5_cluster'], 'SCI_TECH')

    def fixture(self):
        return {'total_papers':2, 'extra_preserved_in_backup':{'x':1}, 'structure':{},
                'methodology':{'deep_analysis_available':2, 'classification_confidence':{'high':2},
                               'deep_methodology_routes':{'123456789012345ABC':1,'123456789012345XYZ':1}},
                'logic_chain':{'top_logic_skeletons':[{'skeleton':['a','b','c','d'],'frequency':1},
                                                       {'skeleton':['a','b','c','e'],'frequency':1}]},
                'writing_patterns':{}}

    def write_fixture(self, data):
        path = self.root / 'SCI_TECH.json'; path.write_text(json.dumps(data))
        return path

    def test_new_format_rerun_is_byte_identical(self):
        data = {field:[] for field in converter.ASSET_FIELDS}
        data.update(sampling_summary={'deep_analyzed':192}, evidence_summary={'classification_confidence':{'high':10}})
        path = self.write_fixture(data); original = path.read_bytes()
        with patch.object(converter, 'DISC_DIR', self.root):
            self.assertTrue(converter.convert('SCI_TECH'))
        self.assertEqual(path.read_bytes(), original)
        self.assertFalse(path.with_suffix('.json.pre-v5.1.bak').exists())

    def test_unknown_mixed_schema_fail_closed(self):
        for data in ({'unknown':1}, {'typical_structures':[]}):
            path = self.write_fixture(data); original = path.read_bytes()
            with patch.object(converter, 'DISC_DIR', self.root):
                self.assertFalse(converter.convert('SCI_TECH'))
            self.assertEqual(path.read_bytes(), original)

    def test_convert_backup_and_ids(self):
        path = self.write_fixture(self.fixture()); original = path.read_bytes()
        with patch.object(converter, 'DISC_DIR', self.root):
            self.assertTrue(converter.convert('SCI_TECH'))
            new_bytes = path.read_bytes()
            self.assertTrue(converter.convert('SCI_TECH'))
            self.assertEqual(path.read_bytes(), new_bytes)
        self.assertEqual(path.with_suffix('.json.pre-v5.1.bak').read_bytes(), original)
        data = json.loads(new_bytes)
        ids = [row['id'] for field in converter.ASSET_FIELDS for row in data[field]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(data['sampling_summary']['deep_analyzed'], 2)
        self.assertEqual(converter.stable_id('X','y',{'b':1,'a':2}), converter.stable_id('X','y',{'a':2,'b':1}))

    def test_duplicate_semantics_refused(self):
        data = self.fixture()
        data['logic_chain']['top_logic_skeletons'] *= 2
        path = self.write_fixture(data); original = path.read_bytes()
        with patch.object(converter, 'DISC_DIR', self.root):
            self.assertFalse(converter.convert('SCI_TECH'))
        self.assertEqual(path.read_bytes(), original)

    def test_dry_run_no_writes(self):
        path = self.write_fixture(self.fixture()); original = path.read_bytes()
        with patch.object(converter, 'DISC_DIR', self.root):
            self.assertTrue(converter.convert('SCI_TECH', dry_run=True))
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_backup_collision_fail_closed(self):
        path = self.write_fixture(self.fixture()); original = path.read_bytes()
        path.with_suffix('.json.pre-v5.1.bak').write_bytes(b'older backup')
        with patch.object(converter, 'DISC_DIR', self.root):
            self.assertFalse(converter.convert('SCI_TECH'))
        self.assertEqual(path.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
