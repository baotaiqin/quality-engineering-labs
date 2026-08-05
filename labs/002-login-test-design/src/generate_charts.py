from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1600, 900
BACKGROUND = "#FFFFFF"
TEXT = "#202124"
MUTED = "#667085"
BLUE = "#3977C3"
BLUE_LIGHT = "#E8F1FA"
GRID = "#E4E7EC"
GREEN = "#3B8C6E"
AMBER = "#D18B2C"
RED = "#C75252"


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


def text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    size: int,
    color: str = TEXT,
    bold: bool = False,
    anchor: str | None = None,
) -> None:
    draw.text(xy, value, font=find_font(size, bold), fill=color, anchor=anchor)


def canvas(title: str, subtitle: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    text(draw, (90, 60), title, 46, bold=True)
    text(draw, (90, 125), subtitle, 24, color=MUTED)
    return image, draw


def save(image: Image.Image, output_dir: Path, filename: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    image.save(path, format="PNG", optimize=True)
    return path


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    note: str,
    fill: str = BLUE_LIGHT,
) -> None:
    draw.rounded_rectangle(box, radius=20, fill=fill, outline=GRID, width=2)
    x1, y1, x2, y2 = box
    text(draw, ((x1 + x2) // 2, y1 + 54), label, 31, bold=True, anchor="mm")
    text(draw, ((x1 + x2) // 2, y1 + 108), note, 22, color=MUTED, anchor="mm")


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int]) -> None:
    draw.line((*start, *end), fill=BLUE, width=5)
    x, y = end
    draw.polygon([(x, y), (x - 16, y - 10), (x - 16, y + 10)], fill=BLUE)


def draw_cover(output_dir: Path) -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((100, 125, 112, 660), fill=BLUE)
    text(draw, (165, 150), "登录功能怎么测？", 70, bold=True)
    text(draw, (165, 260), "从需求范围到27条核心用例", 54, bold=True)
    text(draw, (165, 390), "先确定范围，再讨论覆盖和优先级", 30, color=MUTED)
    draw.line((165, 500, 1410, 500), fill=GRID, width=3)
    text(draw, (165, 575), "登录案例", 34, color=BLUE, bold=True)
    text(draw, (430, 575), "结构化用例", 34, color=BLUE, bold=True)
    text(draw, (760, 575), "自动校验", 34, color=BLUE, bold=True)
    return save(image, output_dir, "00-cover.png")


def draw_test_scope(output_dir: Path) -> Path:
    image, draw = canvas("登录功能的测试对象", "从页面操作一直看到会话与依赖")
    boxes = [
        ((100, 300, 400, 480), "页面交互", "输入、提示、键盘操作"),
        ((475, 300, 775, 480), "登录接口", "参数、错误码、重复请求"),
        ((850, 300, 1150, 480), "认证服务", "校验、计数、账号状态"),
        ((1225, 300, 1525, 480), "会话与数据", "令牌、跳转、审计记录"),
    ]
    for box, label, note in boxes:
        rounded_box(draw, box, label, note)
    for left, right in zip(boxes, boxes[1:]):
        x1 = left[0][2]
        y = (left[0][1] + left[0][3]) // 2
        x2 = right[0][0]
        arrow(draw, (x1 + 10, y), (x2 - 10, y))
    text(draw, (800, 650), "测试对象不是一个按钮，而是一条完整的认证链路", 30, color=MUTED, anchor="mm")
    return save(image, output_dir, "01-login-test-scope.png")


def draw_design_path(output_dir: Path) -> Path:
    image, draw = canvas("从需求到测试证据", "每条用例都应该能回答五个问题")
    labels = [
        ("需求", "系统应该做什么"),
        ("风险", "哪里失败代价最大"),
        ("测试条件", "要验证什么组合"),
        ("测试用例", "数据、步骤、前置状态"),
        ("判定与证据", "怎样算通过或失败"),
    ]
    left = 70
    width = 260
    gap = 45
    for index, (label, note) in enumerate(labels):
        x1 = left + index * (width + gap)
        box = (x1, 300, x1 + width, 500)
        rounded_box(draw, box, label, note, fill="#F7F9FC" if index % 2 else BLUE_LIGHT)
        if index < len(labels) - 1:
            arrow(draw, (x1 + width + 8, 400), (x1 + width + gap - 8, 400))
    text(draw, (800, 650), "缺少判定标准的用例，执行后仍然无法形成质量结论", 30, color=MUTED, anchor="mm")
    return save(image, output_dir, "02-design-path.png")


def load_cases(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def draw_category_distribution(cases: list[dict[str, str]], output_dir: Path) -> Path:
    image, draw = canvas("登录用例按类别分布", f"共{len(cases)}条结构化用例")
    order = ["功能", "安全", "接口", "可用性", "性能", "兼容性"]
    counts = Counter(case["category"] for case in cases)
    max_count = max(counts.values())
    chart_left, chart_right = 360, 1390
    y_start, row_gap = 230, 92
    for index, label in enumerate(order):
        y = y_start + index * row_gap
        count = counts.get(label, 0)
        text(draw, (320, y), label, 27, anchor="rm")
        draw.rounded_rectangle((chart_left, y - 24, chart_right, y + 24), radius=12, fill="#F2F4F7")
        value_right = chart_left + int((chart_right - chart_left) * count / max_count)
        draw.rounded_rectangle((chart_left, y - 24, value_right, y + 24), radius=12, fill=BLUE)
        text(draw, (value_right + 18, y), str(count), 25, bold=True, anchor="lm")
    return save(image, output_dir, "03-case-category-distribution.png")


def draw_boundaries(output_dir: Path) -> Path:
    image, draw = canvas("输入边界怎么取值", "边界值关注下界外、下界、上界、上界外")

    def number_line(y: int, label: str, values: list[tuple[int, str, str]]) -> None:
        text(draw, (170, y), label, 30, bold=True, anchor="rm")
        draw.line((260, y, 1430, y), fill=GRID, width=5)
        positions = [390, 650, 1030, 1290]
        for x, (value, note, color) in zip(positions, values):
            draw.ellipse((x - 15, y - 15, x + 15, y + 15), fill=color)
            text(draw, (x, y - 55), str(value), 28, bold=True, anchor="mm")
            text(draw, (x, y + 58), note, 22, color=MUTED, anchor="mm")

    number_line(330, "用户名长度", [(3, "下界外", RED), (4, "下界", GREEN), (20, "上界", GREEN), (21, "上界外", RED)])
    number_line(610, "密码长度", [(7, "下界外", RED), (8, "下界", GREEN), (64, "上界", GREEN), (65, "上界外", RED)])
    return save(image, output_dir, "04-boundary-values.png")


def draw_state_transition(output_dir: Path) -> Path:
    image, draw = canvas("账号状态迁移", "连续失败次数会改变下一次登录的预期结果")
    rounded_box(draw, (120, 310, 430, 500), "正常", "失败次数 0～3", fill="#EAF5F0")
    rounded_box(draw, (645, 310, 955, 500), "临界", "第4次失败", fill="#FFF4E3")
    rounded_box(draw, (1170, 310, 1480, 500), "临时锁定", "第5次失败后", fill="#FBECEC")
    arrow(draw, (440, 405), (635, 405))
    arrow(draw, (965, 405), (1160, 405))
    text(draw, (537, 360), "继续失败", 22, color=MUTED, anchor="mm")
    text(draw, (1062, 360), "达到阈值", 22, color=MUTED, anchor="mm")
    draw.line((1325, 535, 1325, 680, 275, 680, 275, 515), fill=BLUE, width=5)
    draw.polygon([(275, 515), (265, 533), (285, 533)], fill=BLUE)
    text(draw, (800, 725), "锁定到期且凭据正确：恢复登录，失败计数清零", 27, color=MUTED, anchor="mm")
    return save(image, output_dir, "05-state-transition.png")


def draw_priority(cases: list[dict[str, str]], output_dir: Path) -> Path:
    image, draw = canvas("风险与执行优先级", "风险看失败影响，优先级还要考虑核心链路和执行成本")
    counts = Counter((case["risk"], case["priority"]) for case in cases)
    risks = ["高", "中", "低"]
    priorities = ["P0", "P1", "P2", "P3"]
    x0, y0, cell_w, cell_h = 430, 250, 230, 140
    colors = {"高": "#FBECEC", "中": "#FFF4E3", "低": "#EAF5F0"}
    for col, priority in enumerate(priorities):
        text(draw, (x0 + col * cell_w + cell_w // 2, 210), priority, 28, bold=True, anchor="mm")
    for row, risk in enumerate(risks):
        text(draw, (360, y0 + row * cell_h + cell_h // 2), f"{risk}风险", 28, bold=True, anchor="rm")
        for col, priority in enumerate(priorities):
            box = (x0 + col * cell_w, y0 + row * cell_h, x0 + (col + 1) * cell_w - 12, y0 + (row + 1) * cell_h - 12)
            draw.rounded_rectangle(box, radius=14, fill=colors[risk], outline=GRID, width=2)
            value = counts.get((risk, priority), 0)
            text(draw, ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2), str(value), 38, bold=True, anchor="mm")
    text(draw, (800, 730), "同一风险等级的用例，也可能安排在不同执行批次", 24, color=MUTED, anchor="mm")
    return save(image, output_dir, "06-risk-priority.png")


def generate_all(cases_path: Path, output_dir: Path, include_cover: bool = False) -> list[Path]:
    cases = load_cases(cases_path)
    paths: list[Path] = []
    if include_cover:
        paths.append(draw_cover(output_dir))
    paths.extend(
        [
            draw_test_scope(output_dir),
            draw_design_path(output_dir),
            draw_category_distribution(cases, output_dir),
            draw_boundaries(output_dir),
            draw_state_transition(output_dir),
            draw_priority(cases, output_dir),
        ]
    )
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="生成登录测试设计图表")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--include-cover", action="store_true")
    args = parser.parse_args()
    paths = generate_all(args.cases, args.output_dir, args.include_cover)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
