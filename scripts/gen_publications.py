#!/usr/bin/env python3
"""Generate Hugo publication pages from BibTeX file.

Non-destructive by default: only pages that don't exist yet are created, so
hand- or import-enriched fields (doi, url_pdf, abstract, tags, featured) on
existing pages are never clobbered. The generator writes url_pdf/abstract/etc.
as empty, so regenerating an existing page would wipe those enrichments.

Usage:
    python3 scripts/gen_publications.py            # create missing pages only
    python3 scripts/gen_publications.py --force    # regenerate ALL pages (lossy)
    python3 scripts/gen_publications.py KEY [KEY]  # regenerate only these keys
"""

import os
import re
import sys
import shutil
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

BIB_FILE = os.path.join(os.path.dirname(__file__), '../static/publications.bib')
PUB_DIR = os.path.join(os.path.dirname(__file__), '../content/publication')

# Bib entries kept as a record but NOT shown on the Publications page (which
# lists journal papers). Without this list the generator would recreate a page
# for each on every run. Edit here if one should start/stop appearing.
EXCLUDE_KEYS = {
    # Conference/meeting abstracts (PAG, ASA-CSSA-SSSA, MPMI) — not papers.
    'davis31twenty', 'king31identifying', 'klein31drought', 'monroe2024mutation',
    'king2024characterizing', 'yadav2024combining', 'sutherland2024genomic',
    'tiwari2022einkorn',
    # Spanish-language congreso/thesis item, no journal or DOI.
    'martinez2022ensamblaje',
    # Preprint duplicates of papers already published on the site.
    'klein2024climate',   # -> klein2025climate (New Phytologist)
    'monroe2022report',   # -> monroe2023reply (published reply)
    # Mangled-title duplicate of an existing entry.
    'lawrence2020js',     # -> lawrence2020open
    # Off-topic co-authorships (soil radiocarbon / phyllosphere) — excluded per
    # Grey: the site is plant genomics only.
    'hoyt2019old', 'hoyt2019timescales', 'trumbore2019israd', 'karasov2021host',
}

MONROE_PATTERN = re.compile(r'\bMonroe\b', re.IGNORECASE)

TYPE_MAP = {
    'article': 'article-journal',
    'inproceedings': 'paper-conference',
    'proceedings': 'paper-conference',
    'misc': 'article',
    'book': 'book',
    'phdthesis': 'thesis',
    'mastersthesis': 'thesis',
    'techreport': 'report',
    'unpublished': 'manuscript',
}

def parse_authors(author_str):
    parts = re.split(r'\s+and\s+', author_str.strip())
    result = []
    for part in parts:
        part = part.strip()
        if not part or part.lower() == 'others':
            continue
        if MONROE_PATTERN.search(part):
            result.append('grey-monroe')
        elif ',' in part:
            last, first = part.split(',', 1)
            result.append(f"{first.strip()} {last.strip()}")
        else:
            result.append(part)
    return result

def clean_text(s):
    """Remove basic LaTeX commands and braces."""
    s = re.sub(r'\\["\'\`\^~]\{?([a-zA-Z])\}?', r'\1', s)
    s = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\{([^}]*)\}', r'\1', s)
    s = s.replace('\\&', '&').replace('\\%', '%').strip()
    return s

def make_index_md(entry):
    title = clean_text(entry.get('title', ''))
    # Escape quotes in title
    title = title.replace('"', '\\"')
    authors = parse_authors(entry.get('author', ''))
    year = entry.get('year', '2000')
    doi = entry.get('doi', '')
    url = entry.get('url', '')
    journal = clean_text(entry.get('journal', ''))
    booktitle = clean_text(entry.get('booktitle', ''))
    volume = entry.get('volume', '')
    number = entry.get('number', '')
    pages = entry.get('pages', '').replace('--', '–')

    pub_name = journal or booktitle or ''
    if volume:
        pub_name += f", {volume}"
        if number:
            pub_name += f"({number})"
    if pages:
        pub_name += f":{pages}"

    pub_type = TYPE_MAP.get(entry.get('ENTRYTYPE', 'article').lower(), 'article-journal')
    if 'biorxiv' in pub_name.lower():
        pub_type = 'article'

    date = f"{year}-01-01T00:00:00Z"
    authors_yaml = '\n'.join(f'- {a}' for a in (authors if authors else ['grey-monroe']))
    doi_url = f"https://doi.org/{doi}" if doi else url or ''

    lines = [
        '---',
        f'title: "{title}"',
        'authors:',
        authors_yaml,
        f'date: "{date}"',
        f'doi: "{doi}"',
        '',
        f'publishDate: "{date}"',
        '',
        'publication_types:',
        f'- "{pub_type}"',
        '',
        f'publication: "*{pub_name}*"',
        'publication_short: ""',
        '',
        'abstract: ""',
        '',
        'tags: []',
        'featured: false',
        '',
        'url_pdf: ""',
        'url_code: ""',
        'url_dataset: ""',
        'url_poster: ""',
        'url_project: ""',
        'url_slides: ""',
        f'url_source: "{doi_url}"',
        'url_video: ""',
        '',
        'projects: []',
        'slides: ""',
        '---',
    ]
    return '\n'.join(lines) + '\n'

def get_raw_entry(bib_content, key):
    """Extract raw BibTeX entry for a given key."""
    pattern = re.compile(
        r'(@\w+\{\s*' + re.escape(key) + r'\s*,.*?)(?=\n@|\Z)',
        re.DOTALL
    )
    m = pattern.search(bib_content)
    return m.group(1).strip() if m else ''

def main():
    args = sys.argv[1:]
    force_all = '--force' in args
    force_keys = {a for a in args if not a.startswith('-')}

    with open(BIB_FILE, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    bib_db = bibtexparser.loads(raw_content, parser=parser)

    # Remove old template folders
    for old in ['journal-article', 'conference-paper', 'preprint']:
        old_path = os.path.join(PUB_DIR, old)
        if os.path.isdir(old_path):
            shutil.rmtree(old_path)
            print(f"Removed template folder: {old}")

    # Pass 1 — de-duplicate in memory (keep the entry with the most fields).
    # No filesystem writes here, so a duplicate key can never trigger a
    # delete-then-recreate of an already-enriched page.
    best = {}
    skipped = []
    excluded = []
    for entry in bib_db.entries:
        key = entry['ID']
        if key in EXCLUDE_KEYS:
            excluded.append(key)
            continue
        if key in best and len(entry) <= len(best[key]):
            skipped.append(key)
            continue
        best[key] = entry

    # Pass 2 — write pages. Non-destructive by default: an existing page is
    # left untouched unless explicitly forced, because the generator emits
    # url_pdf/abstract/tags empty and can't reproduce a DOI absent from the
    # .bib, so a blind rewrite would silently strip those enrichments.
    created = []
    regenerated = []
    preserved = []
    for key, entry in best.items():
        folder = os.path.join(PUB_DIR, key)
        index_path = os.path.join(folder, 'index.md')
        exists = os.path.isfile(index_path)
        forced = force_all or key in force_keys

        if exists and not forced:
            preserved.append(key)
            continue

        os.makedirs(folder, exist_ok=True)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(make_index_md(entry))

        raw = get_raw_entry(raw_content, key)
        with open(os.path.join(folder, 'cite.bib'), 'w', encoding='utf-8') as f:
            f.write(raw + '\n')

        (regenerated if exists else created).append(key)
        print(f"{'Regenerated' if exists else 'Created'}: {key}")

    if skipped:
        print(f"\nSkipped duplicate keys: {', '.join(sorted(set(skipped)))}")
    if excluded:
        print(f"Excluded {len(excluded)} non-paper/off-topic ent"
              f"{'ry' if len(excluded) == 1 else 'ries'} (see EXCLUDE_KEYS).")
    if preserved:
        print(f"Preserved {len(preserved)} existing page(s) (use --force to regenerate).")
    print(f"\nCreated: {len(created)}  Regenerated: {len(regenerated)}  Total entries: {len(best)}")

if __name__ == '__main__':
    main()
