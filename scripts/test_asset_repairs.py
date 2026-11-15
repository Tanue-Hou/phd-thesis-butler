#!/usr/bin/env python3
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest
import preview_asset_repairs as repair

class AssetRepairTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.source=self.root/'assets';self.source.mkdir()
    def fixture(self,rows=None):
        rows=rows if rows is not None else [{'paper[...]id':'p','template':'[...] 学习','common[...]mestakes':['x'],'quality[...]score':2}]
        (self.source/'one.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
    def discipline(self, entries):
        p=self.source/'references/disciplines/SCI_TECH.json';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({'cluster':'SCI_TECH','chapter_sequence':entries}));return p
    def test_preview_is_read_only_and_slots_preserved(self):
        self.fixture();before=(self.source/'one.jsonl').read_bytes()
        output,report=repair.plan(self.source)
        fixed=json.loads(output['one.jsonl'])
        self.assertEqual(fixed['template'],'[...] 学习');self.assertEqual(fixed['quality_score'],2)
        self.assertIn('common[...]mestakes',fixed);self.assertEqual(len(report['warnings']),1)
        self.assertEqual((self.source/'one.jsonl').read_bytes(),before)
        self.assertEqual(report['counts_before']['physical_rows'],report['counts_after_proposed_keys']['physical_rows'])
    def test_key_collision_even_equal_values_refused(self):
        self.fixture([{'paper[...]id':'p','paper_id':'p'}])
        with self.assertRaises(ValueError):repair.plan(self.source)
    def test_duplicate_ids_get_distinct_stable_ids_and_manifest(self):
        self.fixture();self.discipline([{'id':'same','sequence':['a']},{'id':'same','sequence':['b']}])
        output,report=repair.plan(self.source,True);again,_=repair.plan(self.source,True)
        self.assertEqual(output,again);self.assertEqual(len(report['id_changes']),2)
        rows=json.loads(output['references/disciplines/SCI_TECH.json'])['chapter_sequence']
        self.assertEqual(len({r['id'] for r in rows}),2)
    def test_identical_duplicate_content_refused(self):
        self.discipline([{'id':'same','sequence':['a']}]*2)
        with self.assertRaises(ValueError):repair.plan(self.source,True)
    def test_ambiguous_reference_refused(self):
        self.discipline([{'id':'same','sequence':['a']},{'id':'same','sequence':['b']}])
        (self.source/'refs.json').write_text('{"reference":"same"}')
        with self.assertRaises(ValueError):repair.plan(self.source,True)
    def test_copy_output_and_source_unchanged(self):
        self.fixture();before=(self.source/'one.jsonl').read_bytes();output,report=repair.plan(self.source)
        dest=self.root/'candidate';repair.apply_plan(self.source,dest,output,report)
        self.assertEqual((self.source/'one.jsonl').read_bytes(),before)
        self.assertTrue((dest/'AUDIT_COUNTS.json').exists())
        with self.assertRaises(ValueError):repair.apply_plan(self.source,dest,output,report)
    def test_nested_output_refused(self):
        self.fixture();output,report=repair.plan(self.source)
        with self.assertRaises(ValueError):repair.apply_plan(self.source,self.source/'out',output,report)
    def test_stale_source_refused(self):
        self.fixture();output,report=repair.plan(self.source)
        (self.source/'one.jsonl').write_text('{}')
        with self.assertRaises(ValueError):repair.apply_plan(self.source,self.root/'out',output,report)
    def test_new_source_file_refused(self):
        self.fixture();output,report=repair.plan(self.source);(self.source/'new.json').write_text('{}')
        with self.assertRaises(ValueError):repair.apply_plan(self.source,self.root/'out',output,report)
    def test_symlink_refused(self):
        self.fixture();(self.source/'link').symlink_to(self.source/'one.jsonl')
        with self.assertRaises(ValueError):repair.plan(self.source)
    def test_duplicate_keys_rejected_at_any_depth(self):
        for name, data in [('bad.jsonl', '{"paper_id":"one","paper_id":"two"}'),
                           ('bad.json', '{"nested":{"x":1,"x":2}}')]:
            path = self.source/name
            path.write_text(data)
            with self.assertRaises(ValueError):repair.plan(self.source)
            self.assertEqual(path.read_text(), data)
            path.unlink()

    def test_nonstandard_numbers_rejected(self):
        for value in ('NaN', 'Infinity', '-Infinity', '1e999', '-1e999'):
            for suffix in ('json', 'jsonl'):
                path=self.source/('bad.'+suffix)
                path.write_text('{"nested":['+value+']}')
                with self.assertRaises(ValueError):repair.plan(self.source)
                path.unlink()

    def test_invalid_json_cli_never_publishes(self):
        for index, data in enumerate(('{"x":1,"x":2}', '{"x":NaN}', '{"nested":{"x":Infinity}}')):
            source_file=self.source/'bad.jsonl';source_file.write_text(data)
            dest=self.root/('out'+str(index))
            result=subprocess.run([sys.executable,repair.__file__,'--assets',str(self.source),'--apply','--output-dir',str(dest)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse(dest.exists())
            self.assertEqual(source_file.read_text(),data)

    def test_malformed_json_refused(self):
        (self.source/'bad.jsonl').write_text('{bad')
        with self.assertRaises(ValueError):repair.plan(self.source)

if __name__=='__main__':unittest.main()
