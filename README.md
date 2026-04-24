# Pythia

> *The oracle that tells you how AIs see your site.*

[![PyPI](https://img.shields.io/pypi/v/pythia-geo)](https://pypi.org/project/pythia-geo/)
[![Python](https://img.shields.io/pypi/pyversions/pythia-geo)](https://pypi.org/project/pythia-geo/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/BigFoot3/pythia/actions/workflows/ci.yml/badge.svg)](https://github.com/BigFoot3/pythia/actions)
[![Coverage](https://codecov.io/gh/BigFoot3/pythia/branch/main/graph/badge.svg)](https://codecov.io/gh/BigFoot3/pythia)
[![PyPI downloads](https://img.shields.io/pypi/dm/pythia-geo)](https://pypi.org/project/pythia-geo/)

**Pythia** is a local-first CLI that audits any webpage for **GEO** (Generative Engine Optimization) and **AEO** (Answer Engine Optimization) — making sure AI systems like ChatGPT, Claude, Perplexity, and Mistral can read, cite, and recommend your content.

No API key. No SaaS. No cloud account. Works on any public URL.
Pipe it into CI/CD and fail the build if your GEO score drops below threshold.

```bash
pip install pythia-geo
pythia audit https://example.com
```

---

## Why GEO matters

Traditional SEO optimizes for crawlers. GEO optimizes for **large language models** that summarize, answer, and cite web content directly in their responses. If your site isn't structured for AI comprehension, you're invisible to a growing share of user queries.

Pythia checks 14 signals across three categories:

| Category | Weight | What it covers |
|----------|--------|----------------|
| **Structure** | 40% | `llms.txt`, `robots.txt` bot policies, sitemap, JSON-LD |
| **HTML** | 30% | H1 uniqueness, heading hierarchy, title, meta description, OpenGraph |
| **Content** | 30% | Generic headings, FAQ patterns, E-E-A-T signals, structured lists |

---

## Quick start

```bash
# Audit a URL, print Markdown report
pythia audit https://example.com

# JSON output for CI integration
pythia audit https://example.com --format json

# French output
pythia audit https://example.com --lang fr

# Fail if score < 80 (default threshold: 70)
pythia audit https://example.com --threshold 80

# Save report to file
pythia audit https://example.com --output report.md

# List all available checks
pythia list-checks
```

Exit code: **0** if score ≥ threshold, **1** otherwise.

---

## CI/CD integration

```yaml
# .github/workflows/geo-audit.yml
- name: GEO audit
  run: |
    pip install pythia-geo
    pythia audit https://yoursite.com --threshold 70 --format json --output geo-report.json
```

---

## Sample output

```
# Pythia GEO Audit — https://example.com

Score: 74/100  ●●●●●●●○○○  ❌ FAIL (threshold: 70)

## STRUCTURE (40%)  —  32/100

- ✅ PASS `llms_txt_present` — llms.txt found and accessible
- ⚠️  WARN `llms_full_txt_present` — llms-full.txt not found (optional but recommended)
- ✅ PASS `robots_ai_bots` — No AI bots blocked in robots.txt
- ✅ PASS `sitemap_accessible` — Sitemap found and accessible
- ❌ FAIL `jsonld_present_valid` — No JSON-LD structured data found

## HTML (30%)  —  25/100

- ✅ PASS `single_h1` — Exactly one H1 found
- ✅ PASS `heading_hierarchy` — Heading hierarchy is sequential
- ✅ PASS `title_length` — Title length is within 30–65 characters
- ⚠️  WARN `meta_description` — Meta description present but length is outside 70–160 characters
- ❌ FAIL `opengraph_minimal` — No OpenGraph tags found

## CONTENT (30%)  —  17/100

- ✅ PASS `generic_headings` — No generic headings detected
- ⚠️  WARN `faq_pattern` — No FAQ structure found
- ✅ PASS `eeat_signals` — Author and publication date detected
- ❌ FAIL `structured_content` — No structured content found (no lists or tables)

## Recommendations

- **`jsonld_present_valid`** — Add <script type="application/ld+json"> with Organization or Article schema
- **`opengraph_minimal`** — Add og:title, og:description, og:type meta tags
- **`structured_content`** — Use <ul>, <ol>, or <table> to structure your content
```

---

## Checks reference

| # | ID | Category | PASS | WARN | FAIL |
|---|-----|----------|------|------|------|
| 1 | `llms_txt_present` | structure | /llms.txt accessible | — | missing or empty |
| 2 | `llms_full_txt_present` | structure | /llms-full.txt accessible | missing | — |
| 3 | `robots_ai_bots` | structure | no AI bots blocked | robots.txt missing | ≥1 bot blocked |
| 4 | `sitemap_accessible` | structure | sitemap found | — | not found |
| 5 | `jsonld_present_valid` | structure | valid JSON-LD found | malformed JSON | none |
| 6 | `single_h1` | html | exactly 1 H1 | >1 H1 | no H1 |
| 7 | `heading_hierarchy` | html | no level gaps | — | ≥1 gap |
| 8 | `title_length` | html | 30–65 chars | out of range | missing |
| 9 | `meta_description` | html | 70–160 chars | out of range | missing |
| 10 | `opengraph_minimal` | html | og:title + og:description + og:type | 1–2 missing | none |
| 11 | `generic_headings` | content | 0 generic | 1–2 in H2+ | H1 generic or ≥3 |
| 12 | `faq_pattern` | content | FAQ detected | none found | — |
| 13 | `eeat_signals` | content | author + date | one of two | neither |
| 14 | `structured_content` | content | ≥1 list or table | — | none |

AI bots checked by `robots_ai_bots`: `GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `CCBot`, `MistralAI-User`.

---

## About the name

In ancient Greece, **Pythia** was the Oracle of Delphi — the high priestess of Apollo who delivered prophecies to kings, generals, and philosophers. Seekers traveled from across the Mediterranean to ask her questions and receive pivotal answers that shaped history.

Today, LLMs are the new oracles. Ask ChatGPT about a product, a concept, a brand — and it will answer with the confidence of a Delphic prophecy. Whether your site appears in that answer, and how accurately it's represented, depends entirely on how well your content speaks to these modern oracles.

**Pythia** ensures the oracle speaks your truth.

The name also fits the [Kryptide](https://kryptide.fr) ecosystem: *kryptos* (κρυπτός) means "hidden" in Greek — Pythia is the one who *reveals*.

---

## Contributing

Issues and PRs welcome. See the project conventions in `CLAUDE.md`.

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `test:`, `chore:`.

---

## License

MIT — see [LICENSE](LICENSE).

---

<details>
<summary>🇫🇷 En français</summary>

**Pythia** est un CLI Python qui audite n'importe quelle page web pour le **GEO** (Generative Engine Optimization) — l'optimisation pour les moteurs de réponse IA comme ChatGPT, Claude, Perplexity et Mistral.

Sans clé API. Sans SaaS. Fonctionne en local ou en CI/CD.

```bash
pip install pythia-geo
pythia audit https://monsite.fr --lang fr
```

14 vérifications réparties en trois catégories : structure (40%), HTML (30%), contenu (30%).
Score sur 100. Seuil configurable (défaut : 70). Code de sortie 1 si sous le seuil.

</details>
