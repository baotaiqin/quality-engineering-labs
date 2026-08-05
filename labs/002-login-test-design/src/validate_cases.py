from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = {
    "case_id",
    "title",
    "category",
    "level",
    "technique",
    "precondition",
    "test_data",
    "steps",
    "expected",
    "risk",
    "priority",
    "requirement_id",
    "tags",
}

ALLOWED_CATEGORIES = {"功能", "接口", "安全", "性能", "兼容性", "可用性"}
ALLOWED_LEVELS = {"UI", "API", "服务", "端到端"}
ALLOWED_RISKS = {"高", "中", "低"}
ALLOWED_PRIORITIES = {"P0", "P1", "P2", "P3"}

REQUIRED_SCENARIO_TAGS = {
    "valid_login",
    "session_created",
    "empty_username",
    "empty_password",
    "username_min_minus",
    "username_min",
    "username_max",
    "username_max_plus",
    "password_min_minus",
    "password_min",
    "password_max",
    "password_max_plus",
    "nonexistent_user",
    "wrong_password",
    "disabled_account",
    "lock_threshold_minus",
    "lock_threshold",
    "locked_correct_password",
    "unlock",
    "duplicate_submit",
    "weak_network",
    "session_rotation",
    "accessible_error",
    "performance_target",
    "compatibility",
}

GENERIC_ERROR_TAGS = {"nonexistent_user", "wrong_password", "disabled_account"}
GENERIC_ERROR_TEXT = "账号或密码错误"
VAGUE_EXPECTED = {"正常", "符合预期", "登录失败", "提示错误"}


def load_cases(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"缺少字段: {', '.join(sorted(missing))}")
        return [
            {key: (value or "").strip() for key, value in row.items()}
            for row in reader
        ]


def parse_tags(case: dict[str, str]) -> set[str]:
    return {tag.strip() for tag in case["tags"].split(";") if tag.strip()}


def validate_cases(cases: Iterable[dict[str, str]]) -> list[str]:
    case_list = list(cases)
    errors: list[str] = []
    ids: set[str] = set()
    all_tags: set[str] = set()

    if not case_list:
        return ["用例文件为空"]

    for index, case in enumerate(case_list, start=2):
        case_id = case.get("case_id", "")
        if not case_id:
            errors.append(f"第{index}行缺少case_id")
        elif case_id in ids:
            errors.append(f"case_id重复: {case_id}")
        ids.add(case_id)

        for field in REQUIRED_COLUMNS:
            if not case.get(field, ""):
                errors.append(f"{case_id or f'第{index}行'}缺少{field}")

        if case.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"{case_id}的category不合法: {case.get('category', '')}")
        if case.get("level") not in ALLOWED_LEVELS:
            errors.append(f"{case_id}的level不合法: {case.get('level', '')}")
        if case.get("risk") not in ALLOWED_RISKS:
            errors.append(f"{case_id}的risk不合法: {case.get('risk', '')}")
        if case.get("priority") not in ALLOWED_PRIORITIES:
            errors.append(f"{case_id}的priority不合法: {case.get('priority', '')}")

        expected = case.get("expected", "")
        if expected in VAGUE_EXPECTED or len(expected) < 8:
            errors.append(f"{case_id}的预期结果缺少可判定标准")

        tags = parse_tags(case)
        all_tags.update(tags)
        if tags & GENERIC_ERROR_TAGS and GENERIC_ERROR_TEXT not in expected:
            errors.append(f"{case_id}没有使用统一登录失败提示")

    missing_tags = REQUIRED_SCENARIO_TAGS - all_tags
    if missing_tags:
        errors.append(f"缺少关键场景: {', '.join(sorted(missing_tags))}")

    return errors


def build_summary(cases: list[dict[str, str]]) -> dict[str, object]:
    requirements = sorted({case["requirement_id"] for case in cases})
    return {
        "case_count": len(cases),
        "category_counts": dict(sorted(Counter(case["category"] for case in cases).items())),
        "level_counts": dict(sorted(Counter(case["level"] for case in cases).items())),
        "technique_counts": dict(sorted(Counter(case["technique"] for case in cases).items())),
        "risk_counts": dict(sorted(Counter(case["risk"] for case in cases).items())),
        "priority_counts": dict(sorted(Counter(case["priority"] for case in cases).items())),
        "high_risk_count": sum(case["risk"] == "高" for case in cases),
        "requirements": requirements,
        "requirement_count": len(requirements),
    }


def write_coverage(cases: list[dict[str, str]], path: Path) -> None:
    counts = Counter(case["requirement_id"] for case in cases)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["requirement_id", "case_count"])
        writer.writerows(sorted(counts.items()))


def main() -> int:
    parser = argparse.ArgumentParser(description="校验登录测试用例并输出覆盖摘要")
    parser.add_argument("--input", type=Path, required=True, help="测试用例CSV路径")
    parser.add_argument("--output-dir", type=Path, required=True, help="输出目录")
    args = parser.parse_args()

    cases = load_cases(args.input)
    errors = validate_cases(cases)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "case_summary.json"
    summary_path.write_text(
        json.dumps(build_summary(cases), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_coverage(cases, args.output_dir / "requirement_coverage.csv")
    print(f"PASS: {len(cases)}条用例校验通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
