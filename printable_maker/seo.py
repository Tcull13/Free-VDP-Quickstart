"""SEO helpers for Etsy listings."""
from __future__ import annotations

from textwrap import dedent
from typing import Dict, List

from .data import PrintableIdea

MAX_TAGS = 13


def _sanitize_tag(tag: str) -> str:
    cleaned = tag.lower().strip()
    return cleaned.replace("  ", " ")


def generate_tags(idea: PrintableIdea) -> List[str]:
    """Create an optimized list of Etsy tags."""
    candidates = idea.trending_searches + idea.evergreen_keywords
    tags: List[str] = []
    for tag in candidates:
        sanitized = _sanitize_tag(tag)
        if sanitized not in tags and len(tags) < MAX_TAGS:
            tags.append(sanitized)
    if len(tags) < MAX_TAGS:
        for extra in [idea.category, idea.slug.replace("-", " ")]:
            sanitized = _sanitize_tag(extra)
            if sanitized not in tags and len(tags) < MAX_TAGS:
                tags.append(sanitized)
    return tags


def generate_title(idea: PrintableIdea) -> str:
    """Produce an Etsy-ready title with keyword targeting."""
    primary_keyword = idea.trending_searches[0]
    secondary_keyword = idea.evergreen_keywords[0]
    return (
        f"{idea.title} | {primary_keyword.title()} Printable, {secondary_keyword.title()} Template"
    )[:140]


def generate_description(idea: PrintableIdea) -> str:
    """Create a conversion-oriented, keyword-rich description."""
    bullet_lines = "\n".join(f"- {point}" for point in idea.differentiators)
    pain_lines = "\n".join(f"• {pain}" for pain in idea.pain_points)
    return dedent(
        f"""
        📌 WHAT'S INCLUDED\n
        {idea.title}\n
        {bullet_lines}\n
        🎯 PERFECT FOR\n        {idea.customer_profile}\n
        😓 SOLVES\n        {pain_lines}\n
        🔍 KEYWORDS\n        Trending: {', '.join(idea.trending_searches)}\n        Evergreen: {', '.join(idea.evergreen_keywords)}\n
        📥 INSTANT DOWNLOAD\n        You'll receive {', '.join(idea.deliverables)} immediately after purchase.
        """
    ).strip()


def seo_bundle(idea: PrintableIdea) -> Dict[str, object]:
    """Bundle SEO assets for downstream export."""
    return {
        "title": generate_title(idea),
        "description": generate_description(idea),
        "tags": generate_tags(idea),
        "price_point": idea.price_point,
    }
