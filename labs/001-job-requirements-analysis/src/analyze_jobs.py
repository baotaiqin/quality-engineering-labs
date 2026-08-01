"""Analyze a manually curated sample of 2027 graduate QA-related job posts.

The script deliberately reports both job-level and company-level prevalence.
Company-level aggregation reduces the influence of companies that publish
several specialized positions in the sample.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence


TOKEN_FIELDS = (
    "languages",
    "test_foundations",
    "automation_tools",
    "engineering_systems",
    "ai_quality",
    "quality_activities",
)

REQUIRED_FIELDS = (
    "job_id",
    "company",
    "title",
    "track",
    "source_url",
    "access_date",
    *TOKEN_FIELDS,
)

CAPABILITY_RULES: Mapping[str, Mapping[str, set[str] | None]] = {
    "编程语言": {"languages": None},
    "测试基础与用例设计": {
        "test_foundations": None,
        "quality_activities": {"test_design", "defect_management"},
    },
    "自动化与工具开发": {
        "automation_tools": None,
        "quality_activities": {
            "automation_test",
            "tool_development",
            "platform_development",
        },
    },
    "计算机与系统基础": {
        "engineering_systems": {
            "Linux",
            "SQL",
            "Git",
            "networks",
            "data_structures_algorithms",
            "operating_system",
        }
    },
    "性能稳定性与定位": {
        "quality_activities": {
            "performance_test",
            "stability_test",
            "root_cause_analysis",
            "monitoring",
            "fault_injection",
            "data_analysis",
        }
    },
    "工程化与基础设施": {
        "engineering_systems": {
            "CI_CD",
            "Docker",
            "Kubernetes",
            "OpenStack",
            "GPU",
            "distributed_systems",
        }
    },
    "AI与模型评测": {"ai_quality": None},
}


def parse_tokens(value: str | None) -> set[str]:
    """Split a pipe-delimited cell and discard whitespace-only tokens."""

    if not value:
        return set()
    return {token.strip() for token in value.split("|") if token.strip()}


def load_jobs(path: Path) -> list[dict[str, str]]:
    """Load and validate the CSV dataset."""

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = set(reader.fieldnames or ())
        missing = set(REQUIRED_FIELDS) - fieldnames
        if missing:
            raise ValueError(f"missing required columns: {sorted(missing)}")
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]

    if not rows:
        raise ValueError("dataset is empty")

    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        for field in ("job_id", "company", "title", "source_url"):
            if not row[field]:
                raise ValueError(f"row {index}: {field} must not be empty")
        if row["job_id"] in seen_ids:
            raise ValueError(f"row {index}: duplicate job_id {row['job_id']}")
        seen_ids.add(row["job_id"])
    return rows


def deduplicate_jobs(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    """Remove exact company/title/URL duplicates while preserving order."""

    unique: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (
            row["company"].casefold(),
            row["title"].casefold(),
            row["source_url"].split("?", 1)[0].rstrip("/").casefold(),
        )
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def _row_has_capability(row: Mapping[str, str], rules: Mapping[str, set[str] | None]) -> bool:
    for field, accepted in rules.items():
        tokens = parse_tokens(row.get(field))
        if tokens and (accepted is None or tokens.intersection(accepted)):
            return True
    return False


def capability_prevalence(rows: Sequence[dict[str, str]]) -> list[dict[str, int | float | str]]:
    """Calculate capability prevalence by job and by distinct company."""

    companies = sorted({row["company"] for row in rows})
    output: list[dict[str, int | float | str]] = []
    for capability, rules in CAPABILITY_RULES.items():
        job_count = sum(_row_has_capability(row, rules) for row in rows)
        company_count = sum(
            any(_row_has_capability(row, rules) for row in rows if row["company"] == company)
            for company in companies
        )
        output.append(
            {
                "capability": capability,
                "job_count": job_count,
                "job_pct": round(job_count / len(rows) * 100, 1),
                "company_count": company_count,
                "company_pct": round(company_count / len(companies) * 100, 1),
            }
        )
    return sorted(output, key=lambda item: (-int(item["job_count"]), str(item["capability"])))


def skill_frequency(rows: Sequence[dict[str, str]]) -> list[dict[str, int | float | str]]:
    """Count every canonical skill token by job and distinct company."""

    companies = sorted({row["company"] for row in rows})
    result: list[dict[str, int | float | str]] = []
    for field in TOKEN_FIELDS:
        job_counter: Counter[str] = Counter()
        company_counter: Counter[str] = Counter()
        for row in rows:
            job_counter.update(parse_tokens(row[field]))
        for company in companies:
            company_tokens: set[str] = set()
            for row in rows:
                if row["company"] == company:
                    company_tokens.update(parse_tokens(row[field]))
            company_counter.update(company_tokens)
        for skill, job_count in job_counter.items():
            result.append(
                {
                    "category": field,
                    "skill": skill,
                    "job_count": job_count,
                    "job_pct": round(job_count / len(rows) * 100, 1),
                    "company_count": company_counter[skill],
                    "company_pct": round(company_counter[skill] / len(companies) * 100, 1),
                }
            )
    return sorted(
        result,
        key=lambda item: (str(item["category"]), -int(item["job_count"]), str(item["skill"])),
    )


def distribution(rows: Sequence[dict[str, str]], field: str) -> list[dict[str, int | float | str]]:
    counts = Counter(row[field] or "未标注" for row in rows)
    return [
        {"value": value, "count": count, "pct": round(count / len(rows) * 100, 1)}
        for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def write_csv(path: Path, rows: Sequence[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty result: {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_analysis(input_path: Path, output_dir: Path) -> dict[str, object]:
    rows = deduplicate_jobs(load_jobs(input_path))
    companies = sorted({row["company"] for row in rows})
    capability_rows = capability_prevalence(rows)
    skill_rows = skill_frequency(rows)

    write_csv(output_dir / "capability_prevalence.csv", capability_rows)
    write_csv(output_dir / "skill_frequency.csv", skill_rows)
    write_csv(output_dir / "track_distribution.csv", distribution(rows, "track"))
    write_csv(output_dir / "source_distribution.csv", distribution(rows, "source_platform"))

    metadata: dict[str, object] = {
        "job_count": len(rows),
        "company_count": len(companies),
        "companies": companies,
        "access_date": max(row["access_date"] for row in rows),
        "method": "manual coding; job-level and company-level aggregation",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Path to job_samples.csv")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for analysis outputs")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    metadata = run_analysis(args.input, args.output_dir)
    print(json.dumps(metadata, ensure_ascii=False))


if __name__ == "__main__":
    main()
