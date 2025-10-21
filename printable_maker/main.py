"""CLI entry point for generating printable products end-to-end."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .data import PrintableIdea, find_idea, get_top_ideas
from .design import create_mockup, generate_design
from .research import format_markdown_report, research_summary
from .seo import seo_bundle


def _resolve_output_dir(base: Optional[str], idea: PrintableIdea) -> Path:
    if base:
        return Path(base)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return Path("output") / f"{idea.slug}-{timestamp}"


def run(argv: Optional[list[str]] = None) -> Path:
    parser = argparse.ArgumentParser(description="Generate research, design, and SEO assets for printable products.")
    parser.add_argument("--idea", help="Slug of the idea to generate", default=None)
    parser.add_argument("--output-dir", help="Optional output directory")
    args = parser.parse_args(argv)

    if args.idea:
        idea = find_idea(args.idea)
    else:
        idea = get_top_ideas(1)[0]

    output_dir = _resolve_output_dir(args.output_dir, idea)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Research assets
    summary = research_summary(idea)
    research_dir = output_dir / "research"
    research_dir.mkdir(exist_ok=True)

    (research_dir / "research-summary.json").write_text(json.dumps(summary, indent=2))
    (research_dir / "research-report.md").write_text(format_markdown_report(summary))

    # Design assets
    design_dir = output_dir / "design"
    design_paths = generate_design(idea, design_dir)

    mockup_dir = output_dir / "mockups"
    mockup_path = create_mockup(idea, design_paths, mockup_dir)

    # SEO assets
    seo_dir = output_dir / "seo"
    seo_dir.mkdir(exist_ok=True)
    seo = seo_bundle(idea)
    (seo_dir / "seo.json").write_text(json.dumps(seo, indent=2))
    description_txt = f"Title: {seo['title']}\n\nTags: {', '.join(seo['tags'])}\n\nDescription:\n{seo['description']}\n"
    (seo_dir / "seo.txt").write_text(description_txt)

    deliverables = {
        "idea": idea.slug,
        "output_dir": str(output_dir.resolve()),
        "design": {k: str(v) for k, v in design_paths.items()},
        "mockup": str(mockup_path),
        "seo": seo,
        "research": summary,
    }
    (output_dir / "deliverables.json").write_text(json.dumps(deliverables, indent=2))

    print("Generated assets for idea:", idea.title)
    print("Output directory:", output_dir)
    print("Design files:")
    for key, path in design_paths.items():
        print(f"  - {key}: {path}")
    print("Mockup:", mockup_path)
    print("SEO title:", seo["title"])
    print("SEO tags:", ", ".join(seo["tags"]))

    return output_dir


if __name__ == "__main__":
    run()
