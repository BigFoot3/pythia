# Changelog

All notable changes to pythia-geo are documented here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
