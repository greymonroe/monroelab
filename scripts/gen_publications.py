#!/usr/bin/env python3
"""Generate Hugo publication pages from BibTeX file."""

import os
import re
import shutil
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

BIB_FILE = os.path.join(os.path.dirname(__file__), '../static/publications.bib')
PUB_DIR = os.path.join(os.path.dirname(__file__), '../content/publication')

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

    seen_keys = {}
    skipped = []

    for entry in bib_db.entries:
        key = entry['ID']

        # De-duplicate: keep the entry with more fields (more complete)
        if key in seen_keys:
            existing = seen_keys[key]
            if len(entry) <= len(existing):
                skipped.append(key)
                continue
            else:
                old_folder = os.path.join(PUB_DIR, key)
                if os.path.isdir(old_folder):
                    shutil.rmtree(old_folder)

        seen_keys[key] = entry

        folder = os.path.join(PUB_DIR, key)
        os.makedirs(folder, exist_ok=True)

        with open(os.path.join(folder, 'index.md'), 'w', encoding='utf-8') as f:
            f.write(make_index_md(entry))

        raw = get_raw_entry(raw_content, key)
        with open(os.path.join(folder, 'cite.bib'), 'w', encoding='utf-8') as f:
            f.write(raw + '\n')

        print(f"Created: {key}")

    if skipped:
        print(f"\nSkipped duplicates: {', '.join(skipped)}")
    print(f"\nTotal created: {len(seen_keys)}")

if __name__ == '__main__':
    main()
