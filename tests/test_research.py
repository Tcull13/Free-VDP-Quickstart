"""Basic tests for printable research helpers."""
from printable_maker.data import get_top_ideas
from printable_maker.seo import generate_tags


def test_top_idea_slug():
    top = get_top_ideas(1)[0]
    assert top.slug == "minimalist-habit-tracker"


def test_tag_generation_limits():
    idea = get_top_ideas(1)[0]
    tags = generate_tags(idea)
    assert len(tags) <= 13
    assert len(tags) == len(set(tags))
