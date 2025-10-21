# Printable Seller Automation

This project provides a turnkey command-line workflow for researching high-opportunity printables and generating the deliverables needed for an Etsy listing. It produces:

- A research dossier with market validation and keyword strategy
- Production-ready printable files (SVG masters with ready-to-upload PDF exports)
- A desk-style mockup SVG for merchandising
- SEO-ready title, description, and tags tailored for Etsy

## Getting Started

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # optional, no external deps required
```

2. Run the generator. By default it selects the highest opportunity printable idea:

```bash
python -m printable_maker
```

Outputs are written to `output/<idea-slug>-<timestamp>/` and include research, design, mockup, and SEO subfolders. Use `--idea` to force a specific printable concept:

```bash
python -m printable_maker --idea modern-tech-resume
```

Use `--output-dir` to control the destination path.

## Tests

The lightweight test suite checks the scoring model and SEO tag generation. Run it with:

```bash
pytest
```

## Dataset

The research engine ships with a curated dataset of high-converting printable niches. Each record captures demand, competition, keyword targets, and design notes that feed the automatic layout builders and SEO writers.
