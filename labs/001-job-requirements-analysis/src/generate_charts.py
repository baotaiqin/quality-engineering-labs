"""Generate simple, reproducible PNG charts for the job analysis."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1600, 900
BACKGROUND = "#FFFFFF"
TEXT = "#222222"
MUTED = "#666666"
GRID = "#E5E7EB"
BAR = "#3977C3"
BAR_LIGHT = "#DCE8F5"

SKILL_LABELS = {
    "Python": "Python",
    "Java": "Java",
    "Go": "Go",
    "C/C++": "C/C++",
    "Shell": "Shell",
    "Ruby": "Ruby",
    "JavaScript": "JavaScript",
    "PHP": "PHP",
    "automation_test": "自动化测试",
    "root_cause_analysis": "问题定位/根因分析",
    "data_analysis": "数据分析",
    "performance_test": "性能测试",
    "tool_development": "测试工具开发",
    "functional_test": "功能测试",
    "platform_development": "测试平台建设",
    "stability_test": "稳定性测试",
    "defect_management": "缺陷跟踪",
    "api_test": "接口测试",
    "compatibility_test": "兼容性测试",
    "AI_testing": "AI辅助/智能测试",
    "AI_tools": "AI工具应用",
    "Agent": "Agent",
    "LLM": "LLM",
    "ML_DL": "机器学习/深度学习",
    "model_evaluation": "模型评测",
    "benchmark": "Benchmark",
    "dataset_construction": "评测集构建",
    "PromptEngineering": "Prompt工程",
    "RAG": "RAG",
}

TRACK_LABELS = {
    "standard_test_dev": "通用测试开发",
    "software_test": "软件测试",
    "ai_software_quality": "AI软件质量",
    "model_evaluation": "大模型评测",
    "algorithm_test": "算法测试",
}


def find_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def write_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    size: int,
    color: str = TEXT,
    bold: bool = False,
    anchor: str | None = None,
) -> None:
    draw.text(xy, value, font=find_font(size, bold), fill=color, anchor=anchor)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def save(image: Image.Image, output_dir: Path, filename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    image.save(path, format="PNG", optimize=True)
    return path


def draw_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    write_text(draw, (90, 62), title, 46, bold=True)
    write_text(draw, (90, 126), subtitle, 24, MUTED)


def draw_percent_chart(
    rows: Sequence[dict[str, str]],
    output_dir: Path,
    filename: str,
    title: str,
    subtitle: str,
    label_key: str,
    value_key: str,
    count_key: str,
    unit: str,
    limit: int = 8,
) -> Path:
    selected = list(rows[:limit])
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw_title(draw, title, subtitle)

    label_right = 400
    chart_left = 440
    chart_right = 1390
    chart_top = 220
    chart_bottom = 765

    for tick in (0, 25, 50, 75, 100):
        x = chart_left + int((chart_right - chart_left) * tick / 100)
        draw.line((x, chart_top - 18, x, chart_bottom), fill=GRID, width=2)
        write_text(draw, (x, chart_bottom + 22), f"{tick}%", 19, MUTED, anchor="ma")

    row_height = (chart_bottom - chart_top) / max(len(selected), 1)
    bar_height = min(42, int(row_height * 0.56))
    for index, row in enumerate(selected):
        y_center = int(chart_top + (index + 0.5) * row_height)
        raw_label = row[label_key]
        label = TRACK_LABELS.get(raw_label, SKILL_LABELS.get(raw_label, raw_label))
        value = float(row[value_key])
        count = row[count_key]
        write_text(draw, (label_right, y_center), label, 25, anchor="rm")
        bar_top = y_center - bar_height // 2
        bar_bottom = y_center + bar_height // 2
        draw.rectangle((chart_left, bar_top, chart_right, bar_bottom), fill=BAR_LIGHT)
        value_right = chart_left + int((chart_right - chart_left) * value / 100)
        draw.rectangle((chart_left, bar_top, max(chart_left + 3, value_right), bar_bottom), fill=BAR)
        value_x = min(value_right + 14, 1510)
        write_text(draw, (value_x, y_center), f"{value:.1f}%  ({count}{unit})", 22, TEXT, anchor="lm")

    return save(image, output_dir, filename)


def draw_cover(metadata: dict[str, object], output_dir: Path) -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((100, 120, 112, 650), fill=BAR)
    write_text(draw, (165, 145), "拆解18个27届测试岗位", 64, bold=True)
    write_text(draw, (165, 245), "测试开发需要哪些能力？", 64, bold=True)
    write_text(draw, (165, 380), "公开岗位样本的Python统计与观察", 31, MUTED)
    draw.line((165, 485, 1410, 485), fill=GRID, width=3)
    write_text(draw, (165, 555), f"{metadata['job_count']} 个岗位", 34, BAR, bold=True)
    write_text(draw, (485, 555), f"{metadata['company_count']} 家企业/机构", 34, BAR, bold=True)
    write_text(draw, (890, 555), "岗位与公司双口径", 34, BAR, bold=True)
    return save(image, output_dir, "00-cover.png")


def generate_all(
    analysis_dir: Path,
    output_dir: Path,
    article_assets_dir: Path | None = None,
) -> list[Path]:
    metadata = json.loads((analysis_dir / "summary.json").read_text(encoding="utf-8"))
    capabilities = load_csv(analysis_dir / "capability_prevalence.csv")
    skills = load_csv(analysis_dir / "skill_frequency.csv")
    tracks = load_csv(analysis_dir / "track_distribution.csv")

    paths = [
        draw_percent_chart(
            tracks,
            output_dir,
            "01-track-distribution.png",
            "岗位方向分布",
            "18个公开岗位，按岗位方向统计",
            "value",
            "pct",
            "count",
            "个岗位",
        ),
        draw_percent_chart(
            capabilities,
            output_dir,
            "02-capability-job-level.png",
            "七类能力在岗位中的出现率",
            "岗位口径：18个岗位，每个岗位只计一次",
            "capability",
            "job_pct",
            "job_count",
            "个岗位",
        ),
    ]

    company_rows = sorted(capabilities, key=lambda row: -float(row["company_pct"]))
    paths.append(
        draw_percent_chart(
            company_rows,
            output_dir,
            "03-capability-company-level.png",
            "七类能力在公司中的出现率",
            "公司口径：13家企业/机构，同一公司多个岗位合并",
            "capability",
            "company_pct",
            "company_count",
            "家",
        )
    )

    language_rows = [row for row in skills if row["category"] == "languages"]
    paths.append(
        draw_percent_chart(
            language_rows,
            output_dir,
            "04-language-frequency.png",
            "编程语言出现频次",
            "统计岗位描述中明确出现的语言",
            "skill",
            "job_pct",
            "job_count",
            "个岗位",
        )
    )

    activity_rows = [row for row in skills if row["category"] == "quality_activities"]
    paths.append(
        draw_percent_chart(
            activity_rows,
            output_dir,
            "05-quality-activities.png",
            "质量活动出现频次",
            "展示样本中出现频率最高的8项活动",
            "skill",
            "job_pct",
            "job_count",
            "个岗位",
        )
    )

    ai_rows = [row for row in skills if row["category"] == "ai_quality"]
    paths.append(
        draw_percent_chart(
            ai_rows,
            output_dir,
            "06-ai-skills.png",
            "AI相关能力出现频次",
            "展示样本中明确出现的AI相关标签",
            "skill",
            "job_pct",
            "job_count",
            "个岗位",
            limit=10,
        )
    )

    if article_assets_dir is not None:
        article_assets_dir.mkdir(parents=True, exist_ok=True)
        draw_cover(metadata, article_assets_dir)
        for path in paths:
            shutil.copy2(path, article_assets_dir / path.name)
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--article-assets-dir", type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    paths = generate_all(args.analysis_dir, args.output_dir, args.article_assets_dir)
    print("\n".join(str(path) for path in paths))


if __name__ == "__main__":
    main()
