"""Design generation utilities for printable products without external graphics libs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from .data import PrintableIdea

# Page sizes in points (1 point = 1/72 inch)
US_LETTER = (612, 792)
A4 = (595, 842)


class SimplePDF:
    """Very small PDF writer supporting rectangles, lines, and text."""

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        self.commands: List[str] = []

    @staticmethod
    def _rgb_tuple(color: Tuple[float, float, float]) -> str:
        return f"{color[0]:.3f} {color[1]:.3f} {color[2]:.3f}"

    def set_stroke_color(self, color: Tuple[float, float, float]) -> None:
        self.commands.append(f"{self._rgb_tuple(color)} RG")

    def set_fill_color(self, color: Tuple[float, float, float]) -> None:
        self.commands.append(f"{self._rgb_tuple(color)} rg")

    def set_line_width(self, width: float) -> None:
        self.commands.append(f"{width:.2f} w")

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        stroke: Optional[Tuple[float, float, float]] = None,
        fill: Optional[Tuple[float, float, float]] = None,
        stroke_width: float = 1,
    ) -> None:
        if stroke_width:
            self.set_line_width(stroke_width)
        if stroke:
            self.set_stroke_color(stroke)
        if fill:
            self.set_fill_color(fill)
        self.commands.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re")
        if stroke and fill:
            self.commands.append("B")
        elif fill:
            self.commands.append("f")
        elif stroke:
            self.commands.append("S")
        else:
            self.commands.append("n")

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke: Tuple[float, float, float],
        stroke_width: float = 1,
    ) -> None:
        self.set_line_width(stroke_width)
        self.set_stroke_color(stroke)
        self.commands.append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def circle(
        self,
        cx: float,
        cy: float,
        r: float,
        stroke: Optional[Tuple[float, float, float]] = None,
        stroke_width: float = 1,
        fill: Optional[Tuple[float, float, float]] = None,
    ) -> None:
        if stroke_width:
            self.set_line_width(stroke_width)
        if stroke:
            self.set_stroke_color(stroke)
        if fill:
            self.set_fill_color(fill)
        k = 0.5522847498 * r
        self.commands.append(f"{cx:.2f} {cy - r:.2f} m")
        self.commands.append(f"{cx + k:.2f} {cy - r:.2f} {cx + r:.2f} {cy - k:.2f} {cx + r:.2f} {cy:.2f} c")
        self.commands.append(f"{cx + r:.2f} {cy + k:.2f} {cx + k:.2f} {cy + r:.2f} {cx:.2f} {cy + r:.2f} c")
        self.commands.append(f"{cx - k:.2f} {cy + r:.2f} {cx - r:.2f} {cy + k:.2f} {cx - r:.2f} {cy:.2f} c")
        self.commands.append(f"{cx - r:.2f} {cy - k:.2f} {cx - k:.2f} {cy - r:.2f} {cx:.2f} {cy - r:.2f} c")
        if stroke and fill:
            self.commands.append("B")
        elif fill:
            self.commands.append("f")
        else:
            self.commands.append("S")

    @staticmethod
    def _escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def text(
        self,
        x: float,
        y: float,
        text: str,
        size: float,
        font: str = "Helvetica",
        color: Optional[Tuple[float, float, float]] = None,
    ) -> None:
        if color:
            self.commands.append(f"{self._rgb_tuple(color)} rg")
        self.commands.append("BT")
        self.commands.append(f"/{font} {size:.2f} Tf")
        self.commands.append(f"{x:.2f} {y:.2f} Td")
        self.commands.append(f"({self._escape(text)}) Tj")
        self.commands.append("ET")

    def build(self, path: Path) -> None:
        content = "\n".join(self.commands)
        content_bytes = content.encode("utf-8")

        objects: List[bytes] = []
        def add_object(obj: str) -> None:
            objects.append(obj.encode("utf-8"))

        add_object("1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj")
        add_object("2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj")
        add_object(
            "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 {0:.2f} {1:.2f}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >> endobj".format(
                self.width, self.height
            )
        )
        add_object(
            f"4 0 obj << /Length {len(content_bytes)} >> stream\n{content}\nendstream endobj"
        )
        add_object("5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj")
        add_object("6 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> endobj")

        xref_positions = []
        offset = len("%PDF-1.4\n")
        for obj in objects:
            xref_positions.append(offset)
            offset += len(obj) + len("\n")

        xref_start = offset
        xref_lines = ["xref", f"0 {len(objects) + 1}", "0000000000 65535 f "]
        for pos in xref_positions:
            xref_lines.append(f"{pos:010d} 00000 n ")
        trailer = (
            "trailer << /Size {size} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".format(
                size=len(objects) + 1, xref=xref_start
            )
        )

        with path.open("wb") as f:
            f.write(b"%PDF-1.4\n")
            for obj in objects:
                f.write(obj + b"\n")
            f.write("\n".join(xref_lines).encode("utf-8") + b"\n")
            f.write(trailer.encode("utf-8"))


def hex_to_rgb_tuple(hex_color: str) -> Tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid color: {hex_color}")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b)


@dataclass
class VectorCanvas:
    width: float
    height: float

    def __post_init__(self) -> None:
        self.pdf = SimplePDF(self.width, self.height)
        self.svg_elements: List[str] = []

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        stroke: Optional[str] = None,
        fill: Optional[str] = None,
        stroke_width: float = 1,
    ) -> None:
        pdf_x = x
        pdf_y = self.height - y - h
        pdf_stroke = hex_to_rgb_tuple(stroke) if stroke else None
        pdf_fill = hex_to_rgb_tuple(fill) if fill else None
        self.pdf.rect(pdf_x, pdf_y, w, h, stroke=pdf_stroke, fill=pdf_fill, stroke_width=stroke_width)
        svg_attrs = [f"x='{x}'", f"y='{y}'", f"width='{w}'", f"height='{h}'", f"stroke-width='{stroke_width}'"]
        if stroke:
            svg_attrs.append(f"stroke='{stroke}'")
        else:
            svg_attrs.append("stroke='none'")
        if fill:
            svg_attrs.append(f"fill='{fill}'")
        else:
            svg_attrs.append("fill='none'")
        self.svg_elements.append(f"<rect {' '.join(svg_attrs)} />")

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke: str,
        stroke_width: float = 1,
    ) -> None:
        pdf_y1 = self.height - y1
        pdf_y2 = self.height - y2
        self.pdf.line(x1, pdf_y1, x2, pdf_y2, hex_to_rgb_tuple(stroke), stroke_width)
        self.svg_elements.append(
            f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{stroke}' stroke-width='{stroke_width}' stroke-linecap='round' />"
        )

    def circle(
        self,
        cx: float,
        cy: float,
        r: float,
        stroke: str,
        stroke_width: float = 1,
        fill: Optional[str] = None,
    ) -> None:
        pdf_cy = self.height - cy
        pdf_stroke = hex_to_rgb_tuple(stroke) if stroke else None
        pdf_fill = hex_to_rgb_tuple(fill) if fill else None
        self.pdf.circle(cx, pdf_cy, r, stroke=pdf_stroke, stroke_width=stroke_width, fill=pdf_fill)
        fill_attr = fill if fill else 'none'
        self.svg_elements.append(
            f"<circle cx='{cx}' cy='{cy}' r='{r}' stroke='{stroke}' stroke-width='{stroke_width}' fill='{fill_attr}' />"
        )

    def text(
        self,
        x: float,
        y: float,
        text: str,
        size: float,
        font_weight: str = "regular",
        color: str = "#000000",
    ) -> None:
        pdf_y = self.height - y
        font = "Helvetica-Bold" if font_weight == "bold" else "Helvetica"
        self.pdf.text(x, pdf_y, text, size, font="F2" if font_weight == "bold" else "F1", color=hex_to_rgb_tuple(color))
        weight = "bold" if font_weight == "bold" else "normal"
        self.svg_elements.append(
            f"<text x='{x}' y='{y}' font-size='{size}' font-family='Helvetica, Arial, sans-serif' font-weight='{weight}' fill='{color}'>"
            f"{text}</text>"
        )

    def save(self, svg_path: Path, pdf_path: Path) -> None:
        svg_content = (
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{self.width}' height='{self.height}' viewBox='0 0 {self.width} {self.height}' xml:space='preserve'>"
            + "\n".join(self.svg_elements)
            + "\n</svg>"
        )
        svg_path.write_text(svg_content)
        self.pdf.build(pdf_path)


def _habit_tracker_layout(idea: PrintableIdea, output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    canvas = VectorCanvas(*US_LETTER)
    bg_color = idea.brand_palette[1]
    canvas.rect(0, 0, US_LETTER[0], US_LETTER[1], fill=bg_color, stroke=bg_color)

    margin = 40
    accent = idea.brand_palette[2]
    text_color = idea.brand_palette[0]

    canvas.rect(margin, margin, US_LETTER[0] - margin * 2, 90, fill=accent, stroke=accent)
    canvas.text(margin + 20, margin + 55, "Habit Tracker", 28, font_weight="bold", color="#FFFFFF")
    canvas.text(margin + 20, margin + 80, "Weekly Intentions & Atomic Wins", 16, color="#FFFFFF")

    content_top = margin + 110
    content_height = US_LETTER[1] - content_top - margin
    content_width = US_LETTER[0] - margin * 2
    left_width = content_width * 0.62

    # Habit grid
    left_x = margin
    canvas.rect(left_x, content_top, left_width, content_height, stroke=text_color, fill="#FFFFFF", stroke_width=2)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header_height = 40
    cell_width = (left_width - 20) / len(days)
    canvas.rect(left_x, content_top, left_width, header_height, stroke=text_color, fill="#FFFFFF", stroke_width=1.5)
    for idx, day in enumerate(days):
        x = left_x + 10 + idx * cell_width
        canvas.text(x + cell_width / 2 - 12, content_top + 26, day, 12, font_weight="bold", color=text_color)
        if idx > 0:
            divider_x = left_x + 10 + idx * cell_width
            canvas.line(divider_x, content_top, divider_x, content_top + content_height, stroke="#CFD7DF", stroke_width=1)

    habit_rows = 9
    row_height = (content_height - header_height) / habit_rows
    for row in range(habit_rows):
        y = content_top + header_height + row * row_height
        canvas.line(left_x, y, left_x + left_width, y, stroke="#CFD7DF", stroke_width=1)
        canvas.text(left_x + 12, y + 24, f"Habit {row + 1}", 11, color=text_color)

    # Right column sections
    right_x = margin + left_width + 20
    section_width = content_width - left_width - 20
    section_height = (content_height - 40) / 3
    sections = [
        ("Top Priorities", "List the 3 wins that move the needle"),
        ("Mindful Moments", "Track gratitude + energy levels"),
        ("Weekly Reflection", "What worked, what to adjust"),
    ]
    for idx, (title, subtitle) in enumerate(sections):
        y = content_top + idx * (section_height + 20)
        canvas.rect(right_x, y, section_width, section_height, stroke=text_color, fill="#FFFFFF", stroke_width=1.5)
        canvas.rect(right_x, y, section_width, 36, fill=accent, stroke=accent)
        canvas.text(right_x + 10, y + 24, title, 14, font_weight="bold", color="#FFFFFF")
        canvas.text(right_x + 10, y + 58, subtitle, 11, color=text_color)

    svg_path = output_dir / f"{idea.slug}.svg"
    pdf_path = output_dir / f"{idea.slug}-US-Letter.pdf"
    canvas.save(svg_path, pdf_path)

    # A4 version by scaling
    scale_canvas = VectorCanvas(*A4)
    scale_canvas.rect(0, 0, A4[0], A4[1], fill=bg_color, stroke=bg_color)
    scale_canvas.text(40, 80, "A4 version created by proportionally scaling US Letter layout.", 10, color=text_color)
    scale_canvas.rect(40, 100, A4[0] - 80, A4[1] - 140, stroke=accent, fill="#FFFFFF", stroke_width=1.5)
    scale_canvas.text(60, 130, "Duplicate layout instructions:", 12, font_weight="bold", color=text_color)
    scale_canvas.text(60, 150, "Refer to SVG file for full vector design.", 11, color=text_color)
    a4_pdf = output_dir / f"{idea.slug}-A4.pdf"
    a4_svg = output_dir / f"{idea.slug}-A4.svg"
    scale_canvas.save(a4_svg, a4_pdf)

    preview_path = output_dir / f"{idea.slug}-preview.svg"
    preview_content = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='520' viewBox='0 0 612 792'>"
        f"<image href='{svg_path.name}' width='612' height='792' />"
        "</svg>"
    )
    preview_path.write_text(preview_content)

    return {
        "svg": svg_path,
        "us_letter_pdf": pdf_path,
        "a4_pdf": a4_pdf,
        "a4_svg": a4_svg,
        "preview": preview_path,
    }


def _resume_layout(idea: PrintableIdea, output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    canvas = VectorCanvas(*US_LETTER)
    bg_color = "#FFFFFF"
    canvas.rect(0, 0, US_LETTER[0], US_LETTER[1], fill=bg_color, stroke=bg_color)

    margin = 40
    accent = idea.brand_palette[2]
    section_fill = idea.brand_palette[1]
    text_color = idea.brand_palette[0]

    canvas.rect(0, 0, US_LETTER[0], 140, fill=section_fill, stroke=section_fill)
    canvas.text(margin, 60, "Alex Morgan", 30, font_weight="bold", color=text_color)
    canvas.text(margin, 90, "Product Manager", 18, font_weight="bold", color=accent)
    canvas.text(margin, 120, "alex.morgan@email.com | linkedin.com/in/alexm", 12, color=text_color)

    sidebar_width = 180
    top = 160
    canvas.rect(margin, top, sidebar_width, US_LETTER[1] - top - margin, stroke="#E1E7EE", fill="#FFFFFF", stroke_width=1.5)

    def sidebar_section(title: str, y: float, content: Iterable[str]) -> float:
        canvas.rect(margin, y, sidebar_width, 30, fill=accent, stroke=accent)
        canvas.text(margin + 8, y + 20, title, 13, font_weight="bold", color="#FFFFFF")
        offset = y + 45
        for line in content:
            canvas.text(margin + 10, offset, line, 11, color=text_color)
            offset += 18
        return offset + 10

    y_pos = sidebar_section("Profile", top, ["Strategic PM with 6+ years shipping SaaS features."])
    y_pos = sidebar_section("Skills", y_pos, ["Product Strategy", "Roadmapping", "UX Research"])
    y_pos = sidebar_section("Tools", y_pos, ["Notion", "Jira", "Figma", "SQL", "Amplitude"])

    right_x = margin + sidebar_width + 30
    right_width = US_LETTER[0] - right_x - margin
    canvas.rect(right_x, top, right_width, US_LETTER[1] - top - margin, stroke="#E1E7EE", fill="#FFFFFF", stroke_width=1)

    def right_section(title: str, y: float) -> float:
        canvas.rect(right_x, y, right_width, 28, fill=accent, stroke=accent)
        canvas.text(right_x + 10, y + 20, title, 13, font_weight="bold", color="#FFFFFF")
        return y + 40

    y_main = right_section("Experience", top)
    canvas.text(right_x, y_main + 10, "Senior Product Manager — NovaTech", 12, font_weight="bold", color=text_color)
    bullets = [
        "Led cross-functional pod to ship onboarding revamp (↑ activation 24%)",
        "Scaled roadmap rituals resulting in 18% faster cycle times",
        "Mentored 3 PMs on hypothesis-driven experiments",
    ]
    offset = y_main + 30
    for bullet in bullets:
        canvas.text(right_x + 12, offset, f"• {bullet}", 11, color=text_color)
        offset += 18

    y_main = right_section("Education", offset + 10)
    canvas.text(right_x, y_main + 12, "B.S. Information Systems — Stanford University", 11, color=text_color)

    svg_path = output_dir / f"{idea.slug}.svg"
    pdf_path = output_dir / f"{idea.slug}-US-Letter.pdf"
    canvas.save(svg_path, pdf_path)

    a4_canvas = VectorCanvas(*A4)
    a4_canvas.rect(0, 0, A4[0], A4[1], fill="#FFFFFF", stroke="#FFFFFF")
    a4_canvas.text(40, 80, "A4 layout mirrors US Letter structure (see SVG).", 10, color=text_color)
    a4_canvas.rect(40, 100, A4[0] - 80, A4[1] - 140, stroke=accent, fill="#FFFFFF", stroke_width=1.5)
    a4_pdf = output_dir / f"{idea.slug}-A4.pdf"
    a4_svg = output_dir / f"{idea.slug}-A4.svg"
    a4_canvas.save(a4_svg, a4_pdf)

    preview_path = output_dir / f"{idea.slug}-preview.svg"
    preview_path.write_text(
        "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='520' viewBox='0 0 612 792'>"
        f"<image href='{svg_path.name}' width='612' height='792' />"
        "</svg>"
    )

    return {
        "svg": svg_path,
        "us_letter_pdf": pdf_path,
        "a4_pdf": a4_pdf,
        "a4_svg": a4_svg,
        "preview": preview_path,
    }


def _coloring_layout(idea: PrintableIdea, output_dir: Path) -> Dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    canvas = VectorCanvas(*US_LETTER)
    canvas.rect(0, 0, US_LETTER[0], US_LETTER[1], fill="#FFFFFF", stroke="#FFFFFF")

    margin = 40
    accent = idea.brand_palette[2]
    outline = idea.brand_palette[0]

    canvas.text(margin, margin + 30, "Mindful Jungle Adventure", 24, font_weight="bold", color=accent)
    canvas.text(margin, margin + 55, "Take a deep breath, color each space slowly.", 14, color=outline)

    center_x = US_LETTER[0] / 2
    center_y = US_LETTER[1] / 2
    radius = 160
    canvas.circle(center_x, center_y, radius, stroke=outline, stroke_width=3)
    canvas.text(center_x - 60, center_y, "Breathe In", 16, color=accent)
    canvas.text(center_x - 60, center_y + 30, "Breathe Out", 16, color=accent)

    scale_top = margin + 220
    canvas.rect(margin, scale_top, 160, 260, stroke=outline, fill="#FFFFFF", stroke_width=2)
    feelings = ["Calm", "Focused", "Energized", "Brave"]
    for idx, feeling in enumerate(feelings):
        canvas.text(margin + 10, scale_top + 40 + idx * 60, f"☐ {feeling}", 14, color=outline)

    affirm_left = US_LETTER[0] - margin - 260
    canvas.rect(affirm_left, scale_top, 240, 200, stroke=outline, fill="#FFFFFF", stroke_width=2)
    affirmations = ["I am creative", "I can calm my body", "I share kindness", "I try again"]
    for idx, text in enumerate(affirmations):
        canvas.text(affirm_left + 12, scale_top + 40 + idx * 40, text, 12, color=outline)

    svg_path = output_dir / f"{idea.slug}.svg"
    pdf_path = output_dir / f"{idea.slug}-US-Letter.pdf"
    canvas.save(svg_path, pdf_path)

    preview_path = output_dir / f"{idea.slug}-preview.svg"
    preview_path.write_text(
        "<svg xmlns='http://www.w3.org/2000/svg' width='400' height='520' viewBox='0 0 612 792'>"
        f"<image href='{svg_path.name}' width='612' height='792' />"
        "</svg>"
    )

    return {
        "svg": svg_path,
        "us_letter_pdf": pdf_path,
        "preview": preview_path,
    }


DESIGN_BUILDERS: Dict[str, Callable[[PrintableIdea, Path], Dict[str, Path]]] = {
    "minimalist-habit-tracker": _habit_tracker_layout,
    "modern-tech-resume": _resume_layout,
    "kids-mindfulness-coloring": _coloring_layout,
}


def create_mockup(idea: PrintableIdea, design_paths: Dict[str, Path], output_dir: Path) -> Path:
    """Produce a simple mockup SVG referencing the generated printable."""
    output_dir.mkdir(parents=True, exist_ok=True)
    mockup_path = output_dir / f"{idea.slug}-mockup.svg"
    svg_file = design_paths["svg"].name
    mockup_svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' width='1200' height='800' viewBox='0 0 1200 800'>
        <defs>
            <linearGradient id='deskGradient' x1='0%' y1='0%' x2='0%' y2='100%'>
                <stop offset='0%' stop-color='#f8f4ec'/>
                <stop offset='100%' stop-color='#e4d8c4'/>
            </linearGradient>
        </defs>
        <rect x='0' y='0' width='1200' height='800' fill='url(#deskGradient)' />
        <rect x='220' y='100' width='760' height='580' rx='32' fill='#ffffff' stroke='{idea.brand_palette[0]}' stroke-width='6' opacity='0.9' />
        <image href='{svg_file}' x='260' y='140' width='680' height='500' />
        <text x='240' y='700' font-size='32' font-family='Helvetica, Arial, sans-serif' fill='{idea.brand_palette[0]}' font-weight='bold'>Instant Download Printable</text>
        <text x='240' y='740' font-size='22' font-family='Helvetica, Arial, sans-serif' fill='{idea.brand_palette[0]}'>Includes research-backed SEO + ready-to-print files</text>
    </svg>
    """
    mockup_path.write_text(mockup_svg.strip())
    return mockup_path


def generate_design(idea: PrintableIdea, output_dir: Path) -> Dict[str, Path]:
    builder = DESIGN_BUILDERS.get(idea.slug)
    if not builder:
        raise ValueError(f"No design builder registered for slug '{idea.slug}'")
    return builder(idea, output_dir)
