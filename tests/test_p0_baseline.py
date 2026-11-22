import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RetrievalBaseline(unittest.TestCase):
    def test_shipped_assets(self):
        for cluster, layer, label in (
            ("SCI_TECH", "CLUSTER", "SCI_TECH"),
            ("HUM_POL_ECON", "CLUSTER", "HUM_POL_ECON"),
            ("UNKNOWN", "GLOBAL", "GLOBAL"),
        ):
            with self.subTest(cluster=cluster):
                result = subprocess.check_output(
                    [sys.executable, str(ROOT / "scripts/retrieve_templates.py"),
                     "-c", "MODEL", "-k", cluster, "-q", "математическая модель", "-l", "5"],
                    encoding="utf-8",
                )
                rows = json.loads(result)
                self.assertEqual(len(rows), 5)
                self.assertEqual(rows[0]["hit_layer"], layer)
                self.assertTrue(all(
                    (row["hit_layer"], row["v5_cluster"]) in {(layer, label), ("GLOBAL", "GLOBAL")}
                    for row in rows
                ))

    def test_mixed_storage_and_optional_discipline(self):
        module = load_script("retrieve_templates")
        with tempfile.TemporaryDirectory() as directory, patch.object(module, "BASE", Path(directory)):
            mapping = Path("assets/references/cluster_mapping.json")
            (module.BASE / mapping).parent.mkdir(parents=True)
            (module.BASE / mapping).write_bytes((ROOT / mapping).read_bytes())

            def write(path, *entries):
                path = module.BASE / "assets" / path
                path.parent.mkdir(parents=True, exist_ok=True)
                rows = [
                    dict(template=text, v5_cluster=label, category="MODEL", quality_score=2)
                    for text, label in entries
                ]
                path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows),
                                encoding="utf-8-sig")

            write("cluster/TECH_LIFE/quality/QUALITY2_ALL.jsonl",
                  ("Модель чайника для экономического прогноза", "HUM_POL_ECON"),
                  ("Модель чайника с датчиком", " sci_tech "),
                  ("Модель чайника для неизвестной области", ["SCI_TECH"]),
                  ("Модель чайника с пустой меткой", None))
            write("cluster/HUM_SOC/quality/QUALITY2_MODEL.jsonl",
                  ("Модель чайника с датчиком", "SCI_TECH"),
                  ("Модель чайника с термостатом", "SCI_TECH"))
            write("global/quality/QUALITY2_MODEL.jsonl",
                  ("Модель чайника в общем виде", "GLOBAL"),
                  ("Модель чайника с повреждённой меткой", ["GLOBAL"]))
            params = dict(category="MODEL", cluster="SCI_TECH",
                          discipline="испытательная дисциплина", query="модель чайника")
            rows = module.retrieve(params)
            self.assertEqual([r["hit_layer"] for r in rows], ["CLUSTER", "CLUSTER", "GLOBAL"])
            self.assertEqual([r["hit_reason"] for r in rows],
                             ["cluster_label", "cluster_label", "global_fallback"])
            self.assertEqual(module.retrieve(dict(params, query="несуществующийтермин")), [])
            self.assertEqual(module.retrieve(dict(params, query="", limit=0)), [])
            browse = module.retrieve(dict(params, category="", cluster="UNKNOWN", query=""))
            self.assertEqual(browse[0]["hit_layer"], "GLOBAL")

            write("discipline/испытательная_дисциплина.jsonl",
                  ("Модель чайника с датчиком", "HUM_POL_ECON"))
            rows = module.retrieve(params)
            self.assertEqual([r["hit_layer"] for r in rows], ["DISCIPLINE", "CLUSTER", "GLOBAL"])
            self.assertEqual(rows[0]["hit_reason"], "discipline_file")
            legacy = module.retrieve(dict(params, discipline="", cluster="TECH_LIFE"))
            self.assertEqual([r["hit_reason"] for r in legacy],
                             ["legacy_cluster_label", "legacy_cluster_label", "global_fallback"])


class StructureBaseline(unittest.TestCase):
    def test_only_usable_headings_feed_patterns(self):
        module = load_script("build_dissertation_landscape")
        records = [
            dict(id="demo-1", structure_confidence="medium",
                 toc=["Глава 1. Обзор", "1.1. Словарь", "Глава 2. Эксперимент", "Заключение"]),
            dict(id="demo-2", structure_confidence="low", chapter_titles=["Обзор"]),
            dict(id="demo-3", structure_confidence="high", toc=["произвольная строка"] * 98),
            dict(id="demo-4", structure_confidence="high", toc=["Глава 1. Обзор", "Глава 1. Дубль"]),
        ]
        patterns = module.analyze_structure_patterns(records)
        self.assertEqual([(r["chapter_count"], r["frequency"]) for r in patterns], [(2, 1)])


    def test_explicit_chapter_levels(self):
        module = load_script("build_dissertation_landscape")
        record = dict(id="demo", structure_confidence="high", chapter_structure=[
            {"level": 1, "title": "Обзор литературы"},
            {"level": 2, "title": "Подраздел"},
            {"level": "1", "title": "Эксперимент"},
        ])
        result = module.build_landscape_json([record], "demo")
        self.assertEqual(result["structure_coverage"]["records_with_usable_headings"], 1)
        pattern, = result["structure_patterns"]
        self.assertEqual(pattern["chapter_count"], 2)
        self.assertEqual(pattern["sequence"], ["LITERATURE_REVIEW", "EXPERIMENT"])
        self.assertIn("1/1 records with usable chapter headings",
                      module.build_markdown_report(result))

    def test_chapter_titles_exclude_numbered_subsections(self):
        module = load_script("build_dissertation_landscape")
        record = dict(id="demo", structure_confidence="high")
        subsections = ["1.1. Обзор", "1.2. Эксперимент"]
        result = module.build_landscape_json([dict(record, chapter_titles=subsections)], "demo")
        self.assertEqual(result["structure_coverage"]["records_with_usable_headings"], 0)
        self.assertEqual(result["structure_patterns"], [])

        headings = ["Обзор литературы", "Эксперимент"]
        result = module.build_landscape_json(
            [dict(record, chapter_titles=[headings[0], *subsections, headings[1]])], "demo"
        )
        pattern, = result["structure_patterns"]
        self.assertEqual(pattern["chapter_count"], 2)

    def test_outline_source_and_eligible_denominator(self):
        module = load_script("build_dissertation_landscape")
        result = module.build_landscape_json([dict(id="missing", structure_confidence="high")], "demo")
        report = module.build_markdown_report(result)
        self.assertIn("This outline uses the default template", report)
        self.assertNotIn("most common observed chapter pattern", report)
        self.assertNotIn("Based on analysis of 1 comparable dissertations", report)

        records = [
            dict(id="demo-1", structure_confidence="high", chapter_titles=["Обзор", "Эксперимент"]),
            dict(id="demo-2", structure_confidence="high", chapter_titles=["Обзор", "Эксперимент"]),
            dict(id="demo-3", structure_confidence="high", chapter_titles=["Эксперимент"]),
            dict(id="demo-4", structure_confidence="high"),
        ]
        result = module.build_landscape_json(records, "demo")
        report = module.build_markdown_report(result)
        self.assertIn("2/3 records with usable chapter headings", report)
        self.assertIn("Structure coverage was 3/4 records", report)
        self.assertNotIn("uses the default template", report)


if __name__ == "__main__":
    unittest.main()
