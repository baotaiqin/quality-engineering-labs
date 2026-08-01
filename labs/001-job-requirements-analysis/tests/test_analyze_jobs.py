from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analyze_jobs import (  # noqa: E402
    capability_prevalence,
    deduplicate_jobs,
    load_jobs,
    parse_tokens,
    run_analysis,
    skill_frequency,
)
from generate_charts import generate_all  # noqa: E402


class ParseTokensTests(unittest.TestCase):
    def test_empty_and_whitespace_are_ignored(self) -> None:
        self.assertEqual(parse_tokens(None), set())
        self.assertEqual(parse_tokens("  | Python | | Java "), {"Python", "Java"})


class AggregationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = [
            {
                "job_id": "1",
                "company": "A",
                "title": "测试开发一",
                "source_url": "https://example.com/a?x=1",
                "access_date": "2026-08-02",
                "languages": "Python|Java",
                "test_foundations": "test_theory",
                "automation_tools": "pytest",
                "engineering_systems": "Linux",
                "ai_quality": "LLM",
                "quality_activities": "automation_test",
            },
            {
                "job_id": "2",
                "company": "A",
                "title": "测试开发二",
                "source_url": "https://example.com/b",
                "access_date": "2026-08-02",
                "languages": "Python",
                "test_foundations": "",
                "automation_tools": "",
                "engineering_systems": "",
                "ai_quality": "Agent",
                "quality_activities": "root_cause_analysis",
            },
            {
                "job_id": "3",
                "company": "B",
                "title": "软件测试",
                "source_url": "https://example.com/c",
                "access_date": "2026-08-02",
                "languages": "Java",
                "test_foundations": "test_process",
                "automation_tools": "Selenium",
                "engineering_systems": "SQL",
                "ai_quality": "",
                "quality_activities": "test_design",
            },
        ]

    def test_company_weighting_does_not_double_count_same_company(self) -> None:
        language_rows = [row for row in skill_frequency(self.rows) if row["category"] == "languages"]
        python = next(row for row in language_rows if row["skill"] == "Python")
        self.assertEqual(python["job_count"], 2)
        self.assertEqual(python["company_count"], 1)

    def test_ai_capability_is_detected(self) -> None:
        result = {row["capability"]: row for row in capability_prevalence(self.rows)}
        self.assertEqual(result["AI与模型评测"]["job_count"], 2)
        self.assertEqual(result["AI与模型评测"]["company_count"], 1)

    def test_exact_duplicate_is_removed(self) -> None:
        duplicate = dict(self.rows[0], job_id="4", source_url="https://example.com/a")
        self.assertEqual(len(deduplicate_jobs([*self.rows, duplicate])), 3)


class DatasetIntegrationTests(unittest.TestCase):
    def test_curated_dataset_and_outputs(self) -> None:
        data_path = PROJECT_ROOT / "data" / "job_samples.csv"
        rows = load_jobs(data_path)
        self.assertEqual(len(rows), 18)
        self.assertGreaterEqual(len({row["company"] for row in rows}), 10)

        with tempfile.TemporaryDirectory() as temp_dir:
            metadata = run_analysis(data_path, Path(temp_dir))
            self.assertEqual(metadata["job_count"], 18)
            self.assertTrue((Path(temp_dir) / "capability_prevalence.csv").exists())
            with (Path(temp_dir) / "skill_frequency.csv").open(
                "r", encoding="utf-8-sig", newline=""
            ) as handle:
                self.assertGreater(len(list(csv.DictReader(handle))), 10)

    def test_chart_generation_smoke(self) -> None:
        data_path = PROJECT_ROOT / "data" / "job_samples.csv"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            analysis_dir = temp_path / "analysis"
            chart_dir = temp_path / "charts"
            asset_dir = temp_path / "assets"
            run_analysis(data_path, analysis_dir)
            paths = generate_all(analysis_dir, chart_dir, asset_dir)
            self.assertEqual(len(paths), 6)
            self.assertTrue(all(path.exists() for path in paths))
            self.assertTrue((asset_dir / "00-cover.png").exists())


if __name__ == "__main__":
    unittest.main()
