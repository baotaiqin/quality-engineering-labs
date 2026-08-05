from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from validate_cases import build_summary, load_cases, validate_cases, write_coverage
from generate_charts import generate_all


DATA_PATH = ROOT / "data" / "login_test_cases.csv"


class ValidateCasesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_cases(DATA_PATH)

    def test_complete_case_set_passes(self) -> None:
        self.assertEqual([], validate_cases(self.cases))

    def test_duplicate_case_id_is_rejected(self) -> None:
        cases = copy.deepcopy(self.cases)
        cases[1]["case_id"] = cases[0]["case_id"]
        self.assertTrue(any("case_id重复" in error for error in validate_cases(cases)))

    def test_missing_boundary_scenario_is_rejected(self) -> None:
        cases = [case for case in copy.deepcopy(self.cases) if "username_max_plus" not in case["tags"]]
        self.assertTrue(any("username_max_plus" in error for error in validate_cases(cases)))

    def test_vague_expected_result_is_rejected(self) -> None:
        cases = copy.deepcopy(self.cases)
        cases[0]["expected"] = "符合预期"
        self.assertTrue(any("缺少可判定标准" in error for error in validate_cases(cases)))

    def test_account_enumeration_message_is_rejected(self) -> None:
        cases = copy.deepcopy(self.cases)
        target = next(case for case in cases if "nonexistent_user" in case["tags"])
        target["expected"] = "拒绝登录；提示用户名不存在"
        self.assertTrue(any("统一登录失败提示" in error for error in validate_cases(cases)))

    def test_summary_and_coverage_are_generated(self) -> None:
        summary = build_summary(self.cases)
        self.assertEqual(27, summary["case_count"])
        self.assertEqual(10, summary["requirement_count"])
        self.assertEqual({"P0": 5, "P1": 12, "P2": 10}, summary["priority_counts"])
        self.assertEqual({"中": 8, "低": 12, "高": 7}, summary["risk_counts"])
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "coverage.csv"
            write_coverage(self.cases, output)
            self.assertIn("AUTH-001", output.read_text(encoding="utf-8-sig"))

    def test_six_article_charts_are_generated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            paths = generate_all(DATA_PATH, Path(temp_dir))
            self.assertEqual(6, len(paths))
            self.assertTrue(all(path.exists() for path in paths))


if __name__ == "__main__":
    unittest.main()
