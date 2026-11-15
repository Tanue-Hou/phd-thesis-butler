#!/usr/bin/env python3
"""Synthetic regressions: retrieval candidates are not verified support."""
import json
import tempfile
import unittest
from pathlib import Path
import detect_citation_gaps as gaps
import bind_evidence_to_chapters as binder

class EvidenceSafety(unittest.TestCase):
    def source(self, id='s1', **extra):
        return dict(id=id, title_ru='Vehicle braking improves safety performance',
                    evidence_role=['method_basis'], **extra)

    def test_duplicate_source_not_coverage(self):
        s = self.source()
        self.assertEqual(gaps.match_literature('Vehicle braking improves safety', [s, s]), ('partial', ['s1']))

    def test_distinct_sources_still_not_coverage(self):
        self.assertEqual(gaps.match_literature('Vehicle braking improves safety', [self.source(), self.source('s2')])[0], 'partial')

    def test_doi_alias_dedup(self):
        rows = [self.source(doi='https://doi.org/10.1/ABC'), self.source('s2', doi='10.1/abc')]
        self.assertEqual(gaps.match_literature('Vehicle braking improves safety', rows)[1], ['s1'])
        self.assertEqual(len(binder.find_candidates('method_basis', rows, {'vehicle'})), 1)

    def test_contradiction_not_coverage(self):
        s = self.source()
        s['title_ru'] = 'Vehicle braking does not improve safety performance'
        self.assertEqual(gaps.match_literature('Vehicle braking improves safety', [s, s])[0], 'partial')

    def test_anonymous_not_bound(self):
        s = self.source('')
        self.assertEqual(gaps.match_literature('Vehicle braking improves safety', [s]), ('missing', []))
        self.assertEqual(binder.find_candidates('method_basis', [s], {'vehicle'}), [])

    def test_source_id_fallback(self):
        s = self.source('')
        s['source_id'] = 'fallback'
        self.assertEqual(gaps.match_literature('Vehicle braking improves safety', [s])[1], ['fallback'])

    def test_strength_never_verified(self):
        for n in (0, 2, 4, 100):
            self.assertNotIn(binder.classify_strength(n, True), ('strong', 'medium'))
            self.assertEqual(binder.classify_gap_status(True, 'strong'), 'partial')

    def test_binder_pipeline(self):
        chapter = next(k for k, roles in binder.CHAPTER_REQUIRED_ROLES.items() if 'method_basis' in roles)
        records, topic = binder.generate_binding_records(chapter, [self.source()], '## Vehicle braking improves safety performance')
        matched = [r for r in records if r['matched_source_ids']]
        self.assertTrue(matched)
        for r in matched:
            self.assertEqual(r['gap_status'], 'partial')
            self.assertEqual(r['verification_status'], 'candidate_unverified')
            self.assertEqual(r['evidence_strength'], 'weak')
        mapped = binder.build_chapter_evidence_map(chapter, records, topic)
        self.assertNotIn('strong', json.dumps(mapped))

    def test_detector_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'chapter.md'
            p.write_text('Vehicle braking improves safety performance [1].', encoding='utf-8')
            _, claims = gaps.detect_gaps(p, [self.source(), self.source()])
        self.assertTrue(claims)
        for claim in claims:
            self.assertNotEqual(claim['gap_status'], 'covered')
            self.assertNotIn(claim['evidence_strength'], ('strong', 'medium'))
            if claim['matched_source_id']:
                self.assertEqual(claim['verification_status'], 'candidate_unverified')

if __name__ == '__main__':
    unittest.main()
