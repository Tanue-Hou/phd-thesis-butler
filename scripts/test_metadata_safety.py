#!/usr/bin/env python3
"""Offline regressions: never accesses Zotero or any network service."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import normalize_russian_metadata as n
import import_zotero_landscape_records as z

class MetadataSafety(unittest.TestCase):
    def test_different_dois_retained(self):
        records=[{'title_ru':'Vehicle control part I','doi':'10/a'}, {'title_ru':'Vehicle control part II','doi':'10/b'}]
        self.assertEqual(n.deduplicate(records), (records,0))
    def test_ambiguous_title_retained(self):
        records=[{'title_ru':'A','year':2024},{'title_ru':'A','year':2025}]
        self.assertEqual(len(n.deduplicate(records)[0]),2)
    def test_exact_duplicate_only(self):
        self.assertEqual(n.deduplicate([{'id':'x'},{'id':'x'}]),([{'id':'x'}],1))
    def test_existing_id(self):
        self.assertEqual(n._generate_id({'id':'original'},'literature'),'original')
    def test_hashseed_stability(self):
        code="import normalize_russian_metadata as n; import import_zotero_landscape_records as z; print(n._generate_id({'title':'A'},'literature')); print(z.zotero_item_to_landscape_record({'title':'A'})['id'])"
        out=[subprocess.check_output([sys.executable,'-c',code],cwd=Path(__file__).parent,env={**os.environ,'PYTHONHASHSEED':seed}) for seed in ['1','2']]
        self.assertEqual(*out)
    def test_same_title_different_data_ids(self):
        self.assertNotEqual(n._generate_id({'title':'A','year':2024},'literature'),n._generate_id({'title':'A','year':2025},'literature'))
    def test_invalid_input_keeps_prior_output(self):
        for data in [[{'title':'A','year':'BAD'}],[None],[{'title':'A','year':1800}]]:
            with self.subTest(data=data), tempfile.TemporaryDirectory() as d:
                inp=Path(d)/'in.json';out=Path(d)/'out.json'
                inp.write_text(json.dumps(data));out.write_text('PRIOR')
                p=subprocess.run([sys.executable,str(Path(n.__file__)), '-i',str(inp),'-o',str(out),'--validate'],capture_output=True)
                self.assertNotEqual(p.returncode,0)
                self.assertEqual(out.read_text(),'PRIOR')
    def test_normalizer_id_conflict_keeps_output(self):
        with tempfile.TemporaryDirectory() as d:
            inp=Path(d)/'in.json';out=Path(d)/'out.json'
            inp.write_text(json.dumps([{'id':'X','title':'A'},{'id':'X','title':'B'}]));out.write_text('PRIOR')
            result=subprocess.run([sys.executable,n.__file__,'-i',str(inp),'-o',str(out)],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(out.read_text(),'PRIOR')
    def test_normalizer_success(self):
        with tempfile.TemporaryDirectory() as d:
            inp=Path(d)/'in.json';out=Path(d)/'out.json'
            inp.write_text(json.dumps([{'id':'X','title':'A','year':2025,'authors':['Author']}]))
            result=subprocess.run([sys.executable,n.__file__,'-i',str(inp),'-o',str(out),'--validate'],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(out.read_text())[0]['id'],'X')
    def test_corporate_author(self):
        self.assertEqual(z.extract_authors({'creators':[{'name':'IEEE','creatorType':'author'}]}),['IEEE'])
    def test_zotero_failures_keep_output(self):
        for status,response in [('UNAVAILABLE',(True,[])),('AVAILABLE',(False,'error')),('AVAILABLE',(True,{})),('AVAILABLE',(True,[None]))]:
            with self.subTest(status=status,response=response),tempfile.TemporaryDirectory() as d:
                out=Path(d)/'out.json';out.write_text('PRIOR')
                args=SimpleNamespace(query='test',limit=1,output=str(out))
                with patch.object(z,'check_zotero_status',return_value=(status,'')),patch.object(z,'zotero_request',return_value=response):
                    self.assertEqual(z.cmd_search(args),1)
                self.assertEqual(out.read_text(),'PRIOR')
    def test_zotero_empty_success_clears_stale_output(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out.json';out.write_text('PRIOR')
            with patch.object(z,'check_zotero_status',return_value=('AVAILABLE','')),patch.object(z,'zotero_request',return_value=(True,[])):
                self.assertEqual(z.cmd_search(SimpleNamespace(query='test',limit=1,output=str(out))),0)
            self.assertEqual(json.loads(out.read_text()),[])
    def test_zotero_id_collision_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out.json';out.write_text('PRIOR')
            with patch.object(z,'check_zotero_status',return_value=('AVAILABLE','')),patch.object(z,'zotero_request',return_value=(True,[{'key':'X','title':'A'},{'key':'X','title':'B'}])):
                self.assertEqual(z.cmd_search(SimpleNamespace(query='test',limit=2,output=str(out))),1)
            self.assertEqual(out.read_text(),'PRIOR')
if __name__=='__main__':unittest.main()
