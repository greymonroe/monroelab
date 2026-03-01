# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **TGCA Lab** (formerly Monroe Lab) academic website — a Hugo-based static site using the HugoBlox/Wowchemy Research Group template, hosted on GitHub Pages with a Netlify mirror at monroelab.org.

## Development Commands

```bash
hugo server                        # Local dev server at http://localhost:1313
hugo --gc --minify                 # Production build to public/
python3 scripts/process_inbox.py   # Process content-update tickets from inbox/
python3 scripts/gen_publications.py # Convert publications.bib → publication pages
```

No lint or test commands — this is a static site generator only.

**Deployment:** Pushing to `main` triggers GitHub Actions (`.github/workflows/publish.yaml`) which builds and deploys to GitHub Pages automatically.

## Architecture

**Stack:** Hugo + HugoBlox (`blox-bootstrap/v5`, `blox-plugin-decap-cms`, `blox-plugin-netlify`) + Bootstrap 5 + custom SCSS.

**Content lives in `content/`:**
- `authors/[slug]/_index.md` — lab member profiles
- `publication/[key]/index.md` — publication pages (auto-generated from BibTeX)
- `post/` — news/blog posts
- `_index.md` — homepage with hero + collapsible news sections

**Configuration in `config/_default/`:**
- `hugo.yaml` — site title, baseURL, core settings
- `params.yaml` — appearance, SEO, analytics, footer
- `menus.yaml` — 7-item navigation menu
- `module.yaml` — Hugo module imports

**Custom layouts in `layouts/`:**
- `shortcodes/researchtopic.html` — collapsible research topic blocks
- `shortcodes/newsyear.html` — collapsible year-grouped news sections
- `partials/blocks/people.html` — team member card display
- `partials/views/citation.html` — publication citation formatting

**Custom styling:** `assets/scss/custom.scss` — hero height (45.5vw matching 2080×946 banner), people card sizing (200×200px avatars), collapsible section styling, CTA button overrides.

## Content Update Workflow (Ticketing System)

Content changes are submitted as YAML "tickets" in `inbox/`. Running `process_inbox.py` handles them. Processed tickets move to `_done/YYYY-MM-DD/` or `_needs_review/` with an explanatory comment.

**Ticket schemas:**

```yaml
# Add a lab member
type: add-person
name: "First Last"
slug: "first-last"
role: "PhD Student"
user_groups: ["Graduate Students"]
email: "flast@ucdavis.edu"
bio: "Short bio."
education:
  - degree: "BS Biology"
    institution: "Some University"
links:
  scholar: "https://scholar.google.com/..."

# Move someone to alumni
type: move-to-alumni
slug: "first-last"
new_role: "PhD → Postdoc at [Institution]"

# Add a publication (raw BibTeX)
type: add-publication
bibtex: |
  @article{Key2024, author = {...}, ...}

# Add a news post
type: add-news
title: "News Title"
date: "2024-01-15"
summary: "Brief summary."
body: |
  Full text of the news post.
links:
  - name: "Read Paper"
    url: "https://doi.org/..."

# Add a publication spotlight page
type: add-spotlight
publication_key: "Monroe2022Nature"
title: "Spotlight Title"
summary: "Extended description."
```

## Publications

Publications are managed via BibTeX:
1. Edit `publications.bib`
2. Run `gen_publications.py` to regenerate `content/publication/` entries
3. OR push to main — `.github/workflows/import-publications.yml` runs the `academic` Python package to auto-import

## Key Media Assets

- `assets/media/banner-people.png` — homepage hero image
- `assets/media/hero-tgca.png` — TGCA Lab logo
- `assets/media/kolibri-logo.png`, `recycling-logo.png` — project logos
- Static files served from `static/` (e.g., `static/media/` for news item logos)
