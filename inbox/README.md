# Monroe Lab Content Inbox

This folder is a staging area for content updates to the website.
Drop ticket files here, then run `python scripts/process_inbox.py` to apply them.

## Ticket Format

Each ticket is a YAML file with a `type` field:

---

### type: add-person
```yaml
type: add-person
name: "First Last"
slug: "first-last"
role: "PhD Student"
user_groups:
  - "Graduate Students"
email: "flast@ucdavis.edu"
bio: "Short bio text."
education:
  - degree: "BS Biology"
    institution: "Some University"
links:
  scholar: "https://scholar.google.com/..."
  twitter: "https://twitter.com/..."
```

### type: move-to-alumni
```yaml
type: move-to-alumni
slug: "first-last"
new_role: "PhD → Postdoc at [Institution]"
```

### type: add-publication
```yaml
type: add-publication
bibtex: |
  @article{Key2024,
    author = {Author, First},
    title = {Paper Title},
    journal = {Journal},
    year = {2024},
    doi = {10.xxxx/xxx}
  }
```

### type: add-news
```yaml
type: add-news
title: "News Item Title"
date: "2024-01-15"
summary: "Brief summary of the news."
body: |
  Full text of the news post.
  Can be multiple paragraphs.
links:
  - name: "Read Paper"
    url: "https://doi.org/..."
```

### type: add-spotlight
```yaml
type: add-spotlight
publication_key: "Monroe2022Nature"
title: "Spotlight Title"
summary: "Extended description for spotlight page."
```

---

Processed tickets are moved to `_done/YYYY-MM-DD/`.
Ambiguous tickets are moved to `_needs_review/` with a comment explaining the issue.
