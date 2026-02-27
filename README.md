# Monroe Lab Website

This is the source repository for the [Monroe Lab](https://monroelab.org) website at UC Davis.

The Monroe Lab is based in the [Department of Plant Sciences](https://www.plantsciences.ucdavis.edu/) and [Genome Center](https://genomecenter.ucdavis.edu/) at UC Davis. We study the biology of mutation — DNA damage, DNA repair, and how new genetic variation arises, drives adaptation, and shapes the evolution of crops and wild plants.

## Tech Stack

- Built with [Hugo](https://gohugo.io/) using the [HugoBlox](https://hugoblox.com/) framework
- Deployed to [GitHub Pages](https://pages.github.com/) and mirrored at [monroelab.org](https://monroelab.org)
- Content lives in `content/`; lab member profiles in `content/authors/`; publications in `content/publication/`

## Structure

| Directory | Contents |
|-----------|----------|
| `content/` | Pages (research, people, teaching, outreach, resources, opportunities) |
| `content/authors/` | Lab member profiles and photos |
| `content/publication/` | Publication entries with PDFs and metadata |
| `assets/media/` | Images and banner photos |
| `assets/scss/custom.scss` | Custom CSS overrides |
| `layouts/` | Hugo template overrides |
| `config/_default/` | Site configuration |

## Local Development

```bash
hugo server
```

Requires [Hugo](https://gohugo.io/installation/) (extended version recommended).
