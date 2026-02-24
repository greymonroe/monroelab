#!/usr/bin/env python3
"""
Monroe Lab Inbox Processor
Processes content update tickets from the inbox/ directory.
Usage: python scripts/process_inbox.py
"""

import os
import sys
import yaml
import shutil
import re
from datetime import date
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent
INBOX_DIR = REPO_ROOT / "inbox"
DONE_DIR = INBOX_DIR / "_done"
NEEDS_REVIEW_DIR = INBOX_DIR / "_needs_review"
AUTHORS_DIR = REPO_ROOT / "content" / "authors"
POSTS_DIR = REPO_ROOT / "content" / "post"
PUBS_BIB = REPO_ROOT / "data" / "publications.bib"

TODAY = date.today().isoformat()


def slugify(name: str) -> str:
    """Convert name to URL-safe slug."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug


def process_add_person(ticket: dict, ticket_path: Path) -> bool:
    """Create a new author profile."""
    required = ['name', 'role', 'user_groups']
    for field in required:
        if field not in ticket:
            print(f"  ERROR: Missing required field '{field}'")
            return False

    slug = ticket.get('slug', slugify(ticket['name']))
    author_dir = AUTHORS_DIR / slug

    if author_dir.exists():
        print(f"  WARNING: Author directory already exists: {slug}")
        return False

    author_dir.mkdir(parents=True)

    # Build frontmatter
    parts = ticket['name'].split()
    first = parts[0] if parts else ''
    last = parts[-1] if len(parts) > 1 else ''

    fm = {
        'title': ticket['name'],
        'first_name': first,
        'last_name': last,
        'role': ticket['role'],
        'highlight_name': False,
        'user_groups': ticket['user_groups'],
    }

    if 'email' in ticket:
        fm.setdefault('social', [])
        fm['social'].append({'icon': 'envelope', 'icon_pack': 'fas', 'link': f"mailto:{ticket['email']}"})

    if 'links' in ticket:
        fm.setdefault('social', [])
        if 'scholar' in ticket['links']:
            fm['social'].append({'icon': 'google-scholar', 'icon_pack': 'ai', 'link': ticket['links']['scholar']})
        if 'twitter' in ticket['links']:
            fm['social'].append({'icon': 'twitter', 'icon_pack': 'fab', 'link': ticket['links']['twitter']})
        if 'github' in ticket['links']:
            fm['social'].append({'icon': 'github', 'icon_pack': 'fab', 'link': ticket['links']['github']})

    if 'education' in ticket:
        fm['education'] = {'courses': [
            {'course': e.get('degree', ''), 'institution': e.get('institution', '')}
            for e in ticket['education']
        ]}

    if 'bio' in ticket:
        fm['bio'] = ticket['bio']

    bio_text = ticket.get('bio', '')
    content = f"---\n{yaml.dump(fm, default_flow_style=False)}---\n\n{bio_text}\n"

    output_file = author_dir / "_index.md"
    output_file.write_text(content)
    print(f"  Created author: {slug} -> {output_file}")
    return True


def process_move_to_alumni(ticket: dict, ticket_path: Path) -> bool:
    """Update an existing author to Alumni status."""
    if 'slug' not in ticket:
        print("  ERROR: Missing required field 'slug'")
        return False

    author_file = AUTHORS_DIR / ticket['slug'] / "_index.md"
    if not author_file.exists():
        print(f"  ERROR: Author not found: {ticket['slug']}")
        return False

    content = author_file.read_text()

    # Parse and update user_groups
    if 'user_groups:' in content:
        # Replace the user_groups section
        content = re.sub(
            r'user_groups:.*?(?=\n\w|\n---)',
            'user_groups:\n  - Alumni\n',
            content,
            flags=re.DOTALL
        )
    
    if 'new_role' in ticket:
        content = re.sub(
            r'role:.*\n',
            f"role: {ticket['new_role']}\n",
            content
        )

    author_file.write_text(content)
    print(f"  Updated to alumni: {ticket['slug']}")
    return True


def process_add_publication(ticket: dict, ticket_path: Path) -> bool:
    """Append a BibTeX entry to publications.bib."""
    if 'bibtex' not in ticket:
        print("  ERROR: Missing required field 'bibtex'")
        return False

    with open(PUBS_BIB, 'a') as f:
        f.write('\n\n')
        f.write(ticket['bibtex'].strip())
        f.write('\n')

    print(f"  Added publication to {PUBS_BIB}")
    return True


def process_add_news(ticket: dict, ticket_path: Path) -> bool:
    """Create a new news post."""
    required = ['title', 'summary']
    for field in required:
        if field not in ticket:
            print(f"  ERROR: Missing required field '{field}'")
            return False

    news_date = ticket.get('date', TODAY)
    title_slug = slugify(ticket['title'])[:50]
    filename = f"{news_date}-{title_slug}.md"

    fm = {
        'title': ticket['title'],
        'date': news_date,
        'summary': ticket['summary'],
    }

    if 'tags' in ticket:
        fm['tags'] = ticket['tags']

    if 'links' in ticket:
        fm['links'] = ticket['links']

    body = ticket.get('body', ticket['summary'])
    content = f"---\n{yaml.dump(fm, default_flow_style=False)}---\n\n{body}\n"

    output_file = POSTS_DIR / filename
    if output_file.exists():
        print(f"  WARNING: File already exists: {filename}")
        return False

    output_file.write_text(content)
    print(f"  Created news post: {filename}")
    return True


def process_add_spotlight(ticket: dict, ticket_path: Path) -> bool:
    """Create a spotlight page for a publication."""
    if 'publication_key' not in ticket:
        print("  ERROR: Missing required field 'publication_key'")
        return False

    pub_key = ticket['publication_key']
    spotlight_dir = REPO_ROOT / "content" / "pubs" / pub_key
    spotlight_dir.mkdir(parents=True, exist_ok=True)

    fm = {
        'title': ticket.get('title', pub_key),
        'summary': ticket.get('summary', ''),
        'date': TODAY,
    }

    content = f"---\n{yaml.dump(fm, default_flow_style=False)}---\n\n{ticket.get('summary', '')}\n"
    output_file = spotlight_dir / "index.md"
    output_file.write_text(content)
    print(f"  Created spotlight: {pub_key} -> {output_file}")
    return True


PROCESSORS = {
    'add-person': process_add_person,
    'move-to-alumni': process_move_to_alumni,
    'add-publication': process_add_publication,
    'add-news': process_add_news,
    'add-spotlight': process_add_spotlight,
}


def process_ticket(ticket_path: Path):
    """Process a single ticket file."""
    print(f"\nProcessing: {ticket_path.name}")

    try:
        content = ticket_path.read_text()
        ticket = yaml.safe_load(content)
    except Exception as e:
        print(f"  ERROR: Failed to parse YAML: {e}")
        move_to(ticket_path, NEEDS_REVIEW_DIR, f"# YAML parse error: {e}\n")
        return

    if not isinstance(ticket, dict) or 'type' not in ticket:
        print("  ERROR: Missing 'type' field")
        move_to(ticket_path, NEEDS_REVIEW_DIR, "# Missing 'type' field\n")
        return

    ticket_type = ticket['type']
    processor = PROCESSORS.get(ticket_type)

    if not processor:
        print(f"  ERROR: Unknown ticket type: {ticket_type}")
        move_to(ticket_path, NEEDS_REVIEW_DIR, f"# Unknown ticket type: {ticket_type}\n")
        return

    success = processor(ticket, ticket_path)

    if success:
        move_to(ticket_path, DONE_DIR / TODAY)
        print(f"  -> Moved to _done/{TODAY}/")
    else:
        move_to(ticket_path, NEEDS_REVIEW_DIR)
        print(f"  -> Moved to _needs_review/")


def move_to(source: Path, dest_dir: Path, prefix: str = ""):
    """Move a ticket file to the destination directory."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / source.name
    if prefix:
        original_content = source.read_text()
        dest.write_text(prefix + original_content)
        source.unlink()
    else:
        shutil.move(str(source), str(dest))


def main():
    print("Monroe Lab Inbox Processor")
    print("=" * 40)

    tickets = list(INBOX_DIR.glob("*.yaml")) + list(INBOX_DIR.glob("*.yml"))

    if not tickets:
        print("No tickets found in inbox/")
        print(f"Place .yaml ticket files in: {INBOX_DIR}")
        return

    print(f"Found {len(tickets)} ticket(s)")

    for ticket_path in sorted(tickets):
        process_ticket(ticket_path)

    print("\nDone.")


if __name__ == '__main__':
    main()
