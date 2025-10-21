"""Research analysis helpers for printable ideas."""
from __future__ import annotations

from dataclasses import asdict
from typing import Dict

from .data import PrintableIdea


def validate_market(idea: PrintableIdea) -> Dict[str, str]:
    """Validate that an idea meets the program's market criteria."""
    checks = {}

    checks["demand"] = (
        "Pass" if idea.demand_score >= 85 else "Fail"
    ) + f" (score: {idea.demand_score})"

    competition_threshold = 0.3
    checks["competition"] = (
        "Pass" if idea.competition_score <= competition_threshold else "Fail"
    ) + f" (score: {idea.competition_score:.2f}, threshold: {competition_threshold})"

    conversion_threshold = 0.06
    checks["conversion"] = (
        "Pass" if idea.conversion_rate >= conversion_threshold else "Fail"
    ) + f" (rate: {idea.conversion_rate:.2%})"

    checks["social_proof"] = (
        "Pass" if idea.average_monthly_sales >= 200 else "Fail"
    ) + f" (avg monthly sales: {idea.average_monthly_sales})"

    checks["pricing"] = "Pass" if 4 <= idea.price_point <= 12 else "Warn"

    return checks


def research_summary(idea: PrintableIdea) -> Dict[str, object]:
    """Create a structured summary of the idea research."""
    validation = validate_market(idea)
    result = {
        "idea": asdict(idea),
        "validation": validation,
        "opportunity_score": round(idea.opportunity_score(), 2),
        "positioning": {
            "seo_angle": idea.seo_angle,
            "unique_selling_points": idea.differentiators,
            "customer_profile": idea.customer_profile,
            "pain_points": idea.pain_points,
        },
    }
    return result


def format_markdown_report(summary: Dict[str, object]) -> str:
    """Generate a human-readable research report in Markdown."""
    idea = summary["idea"]
    report_lines = [
        f"# Printable Research Report — {idea['title']}",
        "",
        "## Opportunity Snapshot",
        f"* Opportunity score: **{summary['opportunity_score']}**",
        f"* Category: {idea['category'].title()} | Price point: ${idea['price_point']:.2f}",
        f"* Average monthly sales: {idea['average_monthly_sales']}",
        "",
        "## Validation Checklist",
    ]

    for name, result in summary["validation"].items():
        report_lines.append(f"* **{name.title()}** — {result}")

    report_lines.extend(
        [
            "",
            "## Why This Listing Wins",
        ]
    )

    for usp in summary["positioning"]["unique_selling_points"]:
        report_lines.append(f"* {usp}")

    report_lines.extend(
        [
            "",
            "## Customer Profile",
            summary["positioning"]["customer_profile"],
            "",
            "## Key Pain Points",
        ]
    )

    for pain in summary["positioning"]["pain_points"]:
        report_lines.append(f"* {pain}")

    report_lines.extend(
        [
            "",
            "## Keyword Targets",
            "**Trending:** " + ", ".join(idea["trending_searches"]),
            "**Evergreen:** " + ", ".join(idea["evergreen_keywords"]),
        ]
    )

    if idea.get("notes"):
        report_lines.extend(["", "## Research Notes"])
        for note in idea["notes"]:
            report_lines.append(f"* {note}")

    return "\n".join(report_lines)
