#!/usr/bin/env python3
"""Offline regression tests. No private source or Zotero access."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import build_dissertation_landscape as builder
import validate_dissertation_landscape as validator
import l2_polish_rules as polish


class LandscapeSafetyTests(unittest.TestCase):
    def test_empty_priority_uses_fallback(self):
        self.assertEqual(builder.get_field_list({'chapter_titles': [], 'toc': ['Introduction']}, 'chapter_titles', 'toc'), ['Introduction'])

    def test_object_chapters_and_bad_entries(self):
        self.assertEqual(builder.extract_chapter_roles([{'title':'Introduction'}, {'heading':'Conclusion'}, None, 2, {}]), builder.extract_chapter_roles(['Introduction','Conclusion']))
        patterns = builder.analyze_structure_patterns([{'id':'r1', 'chapter_structure':[{'title':'Introduction'}]}])
        self.assertEqual(patterns[0]['chapter_count'] if 'chapter_count' in patterns[0] else patterns[0]['frequency'], 1)

    def test_count_uses_only_valid_chapter_titles(self):
        patterns = builder.analyze_structure_patterns([{'id':'r1', 'chapter_structure':[{'title':'Introduction'}, None, 2, {}]}])
        self.assertEqual(patterns[0]['chapter_count'], 1)
        self.assertEqual(len(patterns[0]['sequence']), 1)

    def test_all_invalid_chapters_do_not_create_empty_pattern(self):
        self.assertEqual(builder.analyze_structure_patterns([{'id':'r1', 'chapter_structure':[None, 2, {}, '  ']}]), [])

    def test_gaps_are_sample_observations_not_novelty(self):
        gaps = builder.find_positioning_gaps([{'year':2020,'validation_type':'experimental_bench'}], '', reference_year=2030)
        self.assertIn('2025+', next(g['description'] for g in gaps if g['gap_type']=='temporal'))
        self.assertIn('sample absence is not novelty evidence', gaps[0]['opportunity'])
        self.assertIn('sample', next(g['description'] for g in gaps if g['gap_type']=='validation_scale'))

    def test_bad_and_future_years_not_recent(self):
        gaps = builder.find_positioning_gaps([{'year':'bad'}, {'year':True}, {'year':2099}], '', reference_year=2030)
        self.assertFalse(any(g['gap_type']=='temporal' for g in gaps))

    def test_deep_failure_propagates_once(self):
        names = ['validate_sample_input', 'validate_landscape_output', 'validate_markdown_report', 'validate_no_zotero_paths_in_examples', 'deep_validate']
        with contextlib.ExitStack() as stack:
            for name in names:
                stack.enter_context(patch.object(validator, name, return_value=None))
            e2e = stack.enter_context(patch.object(validator, 'validate_e2e_build', return_value=False))
            stack.enter_context(patch('sys.argv', ['validator', '--deep']))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            self.assertEqual(validator.main(), 1)
            e2e.assert_called_once()

    def test_empty_l4_does_not_write(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)/'out'; out.mkdir()
            output = out/'polishing_rules_v5.json'; output.write_text('preserve')
            with patch.object(polish,'L4_DIR',Path(td)/'missing'), patch.object(polish,'OUT_DIR',out), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(polish.main(),1)
            self.assertEqual(output.read_text(),'preserve')

    def test_partial_l4_does_not_replace_existing(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td); l4=path/'l4'; l4.mkdir(); out=path/'out'; out.mkdir()
            (l4/'one.json').write_text(json.dumps({'a1_cluster':'SCI_TECH'}))
            output=out/'polishing_rules_v5.json'; output.write_text('preserve')
            with patch.object(polish,'L4_DIR',l4), patch.object(polish,'OUT_DIR',out), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(polish.main(),1)
            self.assertEqual(output.read_text(),'preserve')


if __name__ == '__main__':
    unittest.main()
