# Changelog

All notable changes to pythia-geo are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.4.0] — 2026-04-26

### Added
- **`pythia fix <url>`** — new CLI command that generates ready-to-paste HTML/server
  snippets for every FAIL/WARN check:
  - Fixes grouped by location: `<head>`, `<body>`, server-side actions, content guidance
  - Each fix carries the exact snippet to copy-paste, plus an optional explanatory note
  - Supports `--format json` for programmatic consumption
- **`fix_url(url) -> FixReport`** — new public async API; `FixReport` contains the full
  `audit: Report` and `fixes: list[Fix]`
- **`generate_fixes(report) -> list[Fix]`** — pure function exported from `pythia`
- **`Fix`** and **`FixReport`** Pydantic models exported from `pythia`
- **`pythia compare <url1> <url2>`** — new CLI command that audits both URLs concurrently
  and presents a side-by-side check-by-check comparison table with per-category scores
  and a leader verdict
- **`compare_urls(url1, url2) -> CompareReport`** — new public async API; both audits run
  concurrently via `asyncio.gather()`
- **`CompareReport`** Pydantic model exported from `pythia`
- 59 new tests (212 total, up from 153); all renderers covered (md + json)

### Fixed
- JSON CLI output now uses `print()` instead of `console.print()` — prevents Rich from
  wrapping long lines and inserting ANSI codes that break `json.loads()` in scripts

## [0.3.0] — 2026-04-25

### Added
- **`pythia generate-llms <url>`** — new CLI command that generates a ready-to-deploy
  `llms.txt` by crawling the site's sitemap:
  - Reads `robots.txt` to find a declared `Sitemap:` URL, falls back to `/sitemap.xml`
  - Handles sitemap index files (follows one level of indirection)
  - Fetches up to `--max-pages` pages concurrently (default 50, concurrency 5)
  - Groups pages by their first URL path segment into `## Section` headings
  - `Main` section always appears first; remaining sections sorted alphabetically
- **`generate_llms_txt(url, max_pages, concurrency)`** exported from `pythia` as public API
- **`pythia.generators`** subpackage with `llms_txt.py` core logic
- 28 new tests (153 total), covering pure helpers + integration via `respx`

## [0.2.1] — 2026-04-25

### Added
- **Public Python API** — `pythia` is now usable as a library, not just a CLI:
  - `audit_url(url, lang, page_type, threshold) -> Report` — fetch + audit over HTTP
  - `audit_html(html, base_url, lang, page_type, threshold) -> Report` — offline/CI audit
  - Both exported from `pythia.__init__` alongside `Report`, `CheckResult`, `AuditContext`
- Structure checks (`llms_txt`, `llms_full_txt`, `sitemap`) now return `SKIP` gracefully
  when called via `audit_html("")` without a base URL.
- 13 new tests (`test_api.py`), 125 total.

## [0.2.0] — 2026-04-25

### Added
- **Page-type awareness** (`--page-type auto|article|homepage|doc`): auto-detects homepage
  when URL path is `/` or empty; article/doc pages retain full check coverage.
- **`eeat_signals`** and **`faq_pattern`** checks now return `SKIP` for homepage pages —
  navigation pages don't have author bylines or FAQ sections, so they no longer penalize
  the score for sites like MDN or YouTube whose homepage is purely navigational.
- **New check `word_count`** (content, weight 1.0): PASS ≥ 300 words, WARN 100–299, FAIL < 100.
  Excludes `<nav>`, `<header>`, `<footer>`, `<aside>`, `<script>`, `<style>` from the count.
  Automatically skipped for homepage pages.
- **New check `canonical_url`** (html, weight 0.75): PASS if `<link rel="canonical">` is
  present with a non-empty `href`; WARN otherwise. Helps AI systems avoid indexing duplicates.
- **Page type shown in report** header (`page type: article / homepage / doc`).
- `Report` model now carries a `page_type` field.
- 24 new tests (112 total, up from 88).

## [0.1.0] — 2026-04-24

_First release — 14 GEO/AEO checks implemented._
