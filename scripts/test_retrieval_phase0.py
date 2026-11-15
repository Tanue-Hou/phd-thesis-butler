"""Synthetic regressions; not a corpus relevance/rights certification."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('retrieval', os.environ.get('RETRIEVAL_SCRIPT', str(ROOT/'scripts/retrieve_templates.py')))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.base = Path(self.tmp.name)
        self.old = m.BASE; m.BASE = self.base
        p = self.base/'assets/references'; p.mkdir(parents=True)
        (p/'cluster_mapping.json').write_bytes((ROOT/'assets/references/cluster_mapping.json').read_bytes())
    def tearDown(self):
        m.BASE = self.old; self.tmp.cleanup()
    def row(self, text='Модель системы [параметр]', tag='SCI_TECH', category='MODEL', **kw):
        return dict(template=text, v5_cluster=tag, category=category, quality_score=2, **kw)
    def write(self, rel, rows):
        p=self.base/rel; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('\n'.join(json.dumps(x,ensure_ascii=False) for x in rows),encoding='utf8')
    def seed(self, rows):
        self.write('assets/cluster/TECH_LIFE/quality/QUALITY2_MODEL.jsonl', rows)
    def get(self, **kw):
        return m.retrieve(dict(category='MODEL', cluster='SCI_TECH', query='модель', **kw))
    def test_misfiled_record_found(self):
        self.write('assets/cluster/HUM_SOC/quality/QUALITY2_MODEL.jsonl',[self.row()])
        self.assertEqual(len(self.get()),1)
    def test_wrong_label_rejected(self):
        self.seed([self.row(tag='HUM_POL_ECON')]); self.assertEqual(self.get(),[])
    def test_unknown_and_missing_labels_rejected(self):
        self.seed([self.row(tag='UNKNOWN'),self.row(tag=None)]); self.assertEqual(self.get(),[])
    def test_no_match_empty(self):
        self.seed([self.row()]); self.assertEqual(m.retrieve(dict(cluster='TECH_LIFE',query='zzzxxyy')),[])
    def test_short_only_query_not_browse(self):
        self.seed([self.row()]); self.assertEqual(m.retrieve(dict(cluster='TECH_LIFE',query='a')),[])
    def test_browse_preserves_slots(self):
        self.seed([self.row()]); r=m.retrieve(dict(cluster='SCI_TECH',query='')); self.assertEqual(r[0]['template'],'Модель системы [параметр]')
    def test_empty_category_scans_files(self):
        self.seed([self.row()]); self.assertEqual(len(m.retrieve(dict(cluster='SCI_TECH',query='модель'))),1)
    def test_category_filters_all_file(self):
        self.write('assets/cluster/GLOBAL/quality/QUALITY2_ALL.jsonl',[self.row(category='TRANSITION')]); self.assertEqual(self.get(),[])
    def test_global_existing_category_file(self):
        self.write('assets/global/quality/QUALITY2_MODEL.jsonl',[self.row()]); self.assertEqual(self.get()[0]['hit_layer'],'GLOBAL')
    def test_global_still_respects_scope(self):
        self.write('assets/global/quality/QUALITY2_MODEL.jsonl',[self.row(tag='HUM_POL_ECON')]); self.assertEqual(self.get(),[])
    def test_explicit_global_browse(self):
        self.seed([self.row(tag='HUM_POL_ECON')]); self.assertEqual(len(m.retrieve(dict(cluster='GLOBAL'))),1)
    def test_deduplicates(self):
        self.seed([self.row()]); self.write('assets/cluster/HUM_SOC/quality/QUALITY2_ALL.jsonl',[self.row()]); self.assertEqual(len(self.get()),1)
    def test_metadata_no_semantic_certification(self):
        self.seed([self.row()]); r=m.retrieve(dict(cluster='TECH_LIFE'))[0]
        self.assertEqual(r['v5_cluster'],'SCI_TECH'); self.assertEqual(r['classification_status'],'unverified_source_label');self.assertEqual(r['alias_resolution'],'legacy_lossy_mapping')
    def test_invalid_cluster_fails_closed(self):
        with self.assertRaises(ValueError): m.retrieve(dict(cluster='../../bad'))
    def test_nonpositive_limit(self):
        self.seed([self.row()]); self.assertEqual(m.retrieve(dict(cluster='TECH_LIFE',limit=-1)),[])
    def test_no_false_discipline_hit(self):
        self.write('assets/discipline/технические_науки.jsonl',[self.row()]); self.assertEqual(self.get(),[])

if __name__ == '__main__': unittest.main()
