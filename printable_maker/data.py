"""Static research dataset for printable ideas."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class PrintableIdea:
    """Represents a printable concept discovered during research."""

    slug: str
    title: str
    category: str
    use_case: str
    demand_score: int
    competition_score: float
    conversion_rate: float
    average_monthly_sales: int
    price_point: float
    trending_searches: List[str]
    evergreen_keywords: List[str]
    pain_points: List[str]
    differentiators: List[str]
    customer_profile: str
    design_notes: List[str]
    brand_palette: List[str]
    font_stack: List[str]
    deliverables: List[str]
    mockup_style: str
    seo_angle: str
    notes: List[str] = field(default_factory=list)

    def opportunity_score(self) -> float:
        """Heuristic score balancing demand, competition, and conversions."""
        return (
            self.demand_score * (1 - self.competition_score)
            + self.conversion_rate * 25
            + min(self.average_monthly_sales, 400) / 10
        )


DATASET: List[PrintableIdea] = [
    PrintableIdea(
        slug="minimalist-habit-tracker",
        title="Minimalist Habit Tracker & Atomic Goals Planner",
        category="planner",
        use_case="Busy professionals and students tracking daily routines",
        demand_score=94,
        competition_score=0.22,
        conversion_rate=0.07,
        average_monthly_sales=380,
        price_point=6.95,
        trending_searches=[
            "daily habit tracker",
            "atomic habits planner",
            "printable routine checklist",
            "productivity printable",
        ],
        evergreen_keywords=[
            "habit tracker printable",
            "goal planner",
            "productivity planner",
            "minimalist planner",
            "self care tracker",
        ],
        pain_points=[
            "People abandon planners that feel cluttered or overwhelming",
            "Most habit trackers ignore reflection prompts",
            "Many templates are not printer-friendly",
        ],
        differentiators=[
            "Clean monochrome layout with subtle accent color",
            "Includes quick reflection and micro-win section",
            "Optimized for both A4 and US Letter printing",
        ],
        customer_profile="Professionals who follow productivity systems like Atomic Habits",
        design_notes=[
            "Two-column layout with daily tracker and weekly wins",
            "Use accent color blocks for priority habits",
            "Incorporate space for gratitude and reflection",
        ],
        brand_palette=["#1F2933", "#F5F7FA", "#38B2AC"],
        font_stack=["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"],
        deliverables=["US Letter PDF", "A4 PDF", "SVG master file", "Mockup SVG"],
        mockup_style="Flat-lay desk scene with warm light",
        seo_angle="Focus on productivity, atomic habits, and minimalist design",
        notes=[
            "Bestseller badge observed on 4 comparable listings",
            "Average review rating 4.9 across 1,200+ reviews",
        ],
    ),
    PrintableIdea(
        slug="modern-tech-resume",
        title="Modern Tech Resume & Cover Letter Bundle",
        category="resume template",
        use_case="Job seekers in tech and product roles",
        demand_score=89,
        competition_score=0.28,
        conversion_rate=0.09,
        average_monthly_sales=310,
        price_point=8.5,
        trending_searches=[
            "tech resume template",
            "product manager resume",
            "modern resume printable",
            "ats friendly resume",
        ],
        evergreen_keywords=[
            "resume template",
            "cover letter template",
            "ATS friendly",
            "professional resume",
            "instant download",
        ],
        pain_points=[
            "Templates that are not ATS optimized",
            "Difficult editing instructions",
            "Lack of matching cover letter",
        ],
        differentiators=[
            "ATS-friendly column layout",
            "Includes matching cover letter page",
            "Comes with Canva and Word instructions",
        ],
        customer_profile="Mid-level product and UX professionals updating their resume",
        design_notes=[
            "Two-column grid with sidebar for skills and contact",
            "Use teal accent bars for section headers",
            "Include icons for quick scanning",
        ],
        brand_palette=["#0D3B66", "#FAF0CA", "#3FA7D6"],
        font_stack=["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"],
        deliverables=[
            "US Letter PDF",
            "A4 PDF",
            "Editable Canva link placeholder",
            "Mockup image",
        ],
        mockup_style="Resume on clipboard with coffee cup",
        seo_angle="Highlight ATS compliance and fast customization",
        notes=[
            "Consistent search growth for 'tech resume template' in past 6 months",
            "Low competition keywords discovered via eRank snapshot",
        ],
    ),
    PrintableIdea(
        slug="kids-mindfulness-coloring",
        title="Kids' Mindfulness Coloring Adventure Pack",
        category="coloring book",
        use_case="Parents and teachers creating calming activities",
        demand_score=91,
        competition_score=0.19,
        conversion_rate=0.08,
        average_monthly_sales=265,
        price_point=5.25,
        trending_searches=[
            "mindfulness coloring pages",
            "calming coloring printable",
            "kids emotions activity",
            "breathing exercise worksheet",
        ],
        evergreen_keywords=[
            "kids coloring pages",
            "mindfulness worksheet",
            "calm down corner",
            "social emotional learning",
            "coloring pack",
        ],
        pain_points=[
            "Parents need screen-free calming tools",
            "Teachers want engaging SEL resources",
            "Existing designs feel cluttered or low quality",
        ],
        differentiators=[
            "Includes guided breathing and emotion check-ins",
            "Hand-drawn line art with thick outlines for easy coloring",
            "Bundle includes 10 unique pages",
        ],
        customer_profile="Parents of neurodivergent kids and elementary teachers",
        design_notes=[
            "Playful hand-drawn characters with positive affirmations",
            "Incorporate breathing bubble and emotion scale",
            "Leave generous white space for coloring",
        ],
        brand_palette=["#F7B801", "#F35B04", "#0FA3B1", "#247BA0"],
        font_stack=["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"],
        deliverables=["US Letter PDF", "SVG master file", "Mockup SVG"],
        mockup_style="Kids desk with crayons and soft light",
        seo_angle="Emphasize mindfulness, SEL, and parent/teacher benefits",
        notes=[
            "Two competitor listings with 5k+ sales but outdated designs",
            "Keyword difficulty < 25 on EverBee snapshot",
        ],
    ),
]


def get_top_ideas(limit: int = 1) -> List[PrintableIdea]:
    """Return the highest scoring printable ideas."""
    return sorted(DATASET, key=lambda idea: idea.opportunity_score(), reverse=True)[:limit]


def find_idea(slug: str) -> PrintableIdea:
    """Find an idea by slug."""
    for idea in DATASET:
        if idea.slug == slug:
            return idea
    raise ValueError(f"No idea found for slug '{slug}'. Available: {[i.slug for i in DATASET]}")
