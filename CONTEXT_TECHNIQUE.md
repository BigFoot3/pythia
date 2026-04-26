# Pythia — Contexte technique

Version cible : **0.4.1**
Checks implémentés : **16 / 16**
Dernière mise à jour : 2026-04-26

---

## Matrice des 16 checks

| # | ID | Catégorie | Fichier | Poids | Page-type aware | Statut |
|---|-----|-----------|---------|-------|-----------------|--------|
| 1 | `llms_txt_present` | structure | checks/structure.py | 1.0 | SKIP si pas de base_url | ✅ Implémenté |
| 2 | `llms_full_txt_present` | structure | checks/structure.py | 0.5 | SKIP si pas de base_url | ✅ Implémenté |
| 3 | `robots_ai_bots` | structure | checks/structure.py | 1.0 | — | ✅ Implémenté |
| 4 | `sitemap_accessible` | structure | checks/structure.py | 1.0 | SKIP si pas de base_url | ✅ Implémenté |
| 5 | `jsonld_present_valid` | structure | checks/schema.py | 1.0 | — | ✅ Implémenté |
| 6 | `single_h1` | html | checks/html.py | 1.0 | — | ✅ Implémenté |
| 7 | `heading_hierarchy` | html | checks/html.py | 1.0 | — | ✅ Implémenté |
| 8 | `title_length` | html | checks/html.py | 1.0 | — | ✅ Implémenté |
| 9 | `meta_description` | html | checks/html.py | 1.0 | — | ✅ Implémenté |
| 10 | `opengraph_minimal` | html | checks/html.py | 1.0 | — | ✅ Implémenté |
| 11 | `canonical_url` | html | checks/html.py | 0.75 | — | ✅ Implémenté (v0.2.0) |
| 12 | `generic_headings` | content | checks/content.py | 1.0 | — | ✅ Implémenté |
| 13 | `faq_pattern` | content | checks/content.py | 1.0 | SKIP homepage | ✅ Implémenté |
| 14 | `eeat_signals` | content | checks/content.py | 1.0 | SKIP homepage | ✅ Implémenté |
| 15 | `structured_content` | content | checks/content.py | 1.0 | — | ✅ Implémenté |
| 16 | `word_count` | content | checks/content.py | 1.0 | SKIP homepage | ✅ Implémenté (v0.2.0) |

---

## Détail des checks et seuils

### Catégorie : structure (poids 40%)

#### 1. `llms_txt_present`
GET `/llms.txt`
- **PASS** : HTTP 200 + body non vide
- **FAIL** : 404 / erreur réseau / body vide
- **SKIP** : pas de base_url (mode `audit_html` sans URL)

#### 2. `llms_full_txt_present`
GET `/llms-full.txt` *(check bonus — weight=0.5, score max = WARN)*
- **PASS** : HTTP 200 + body non vide
- **WARN** : absent ou 404
- **SKIP** : pas de base_url

#### 3. `robots_ai_bots`
Parse `/robots.txt`, vérifie l'absence de `Disallow: /` sur :
`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `CCBot`, `MistralAI-User`
- **PASS** : aucun bot IA bloqué
- **WARN** : `/robots.txt` absent
- **FAIL** : ≥ 1 bot IA bloqué explicitement

#### 4. `sitemap_accessible`
Cherche `Sitemap:` dans robots.txt, puis `/sitemap.xml`
- **PASS** : sitemap trouvé + HTTP 200
- **FAIL** : aucun sitemap trouvable
- **SKIP** : pas de base_url

#### 5. `jsonld_present_valid`
`<script type="application/ld+json">` via BS4 + `json.loads()`
- **PASS** : ≥ 1 bloc JSON-LD parseable
- **WARN** : bloc présent mais JSON malformé
- **FAIL** : aucun bloc JSON-LD

---

### Catégorie : html (poids 30%)

#### 6. `single_h1`
Compte `<h1>` dans le body
- **PASS** : exactement 1
- **WARN** : > 1
- **FAIL** : 0

#### 7. `heading_hierarchy`
Vérifie qu'aucun saut de niveau ne se produit
- **PASS** : hiérarchie continue
- **FAIL** : ≥ 1 saut de niveau

#### 8. `title_length`
`<title>` longueur (strip)
- **PASS** : 30–65 chars
- **WARN** : présent mais hors plage
- **FAIL** : absent

#### 9. `meta_description`
`<meta name="description" content="...">` longueur
- **PASS** : 70–160 chars
- **WARN** : présent mais hors plage
- **FAIL** : absent

#### 10. `opengraph_minimal`
`og:title` + `og:description` + `og:type`
- **PASS** : 3/3 tags présents
- **WARN** : 1 ou 2 tags manquants
- **FAIL** : 0 tags OG

#### 11. `canonical_url` *(v0.2.0)*
`<link rel="canonical" href="...">` dans `<head>`
- **PASS** : présent avec href non vide
- **WARN** : absent

---

### Catégorie : content (poids 30%)

#### 12. `generic_headings`
H1–H6 contenant : `home`, `welcome`, `page`, `untitled`
- **PASS** : 0 heading générique
- **WARN** : 1–2 génériques en H2–H6 uniquement
- **FAIL** : H1 générique **ou** ≥ 3 headings génériques

#### 13. `faq_pattern`
Détecte : `<dl>`, `<details><summary>`, `itemtype="FAQPage"`, JSON-LD FAQPage
- **PASS** : pattern détecté
- **WARN** : absent
- **SKIP** : page de type homepage

#### 14. `eeat_signals`
Auteur : `rel="author"`, `[itemprop="author"]`, `.author`, `.byline`
Date : `<time>`, `[itemprop="datePublished"]`, `meta[property="article:published_time"]`
- **PASS** : auteur + date détectés
- **WARN** : un seul signal sur deux
- **FAIL** : aucun signal
- **SKIP** : page de type homepage

#### 15. `structured_content`
`<ul>`, `<ol>`, ou `<table>` dans `<body>`
- **PASS** : ≥ 1 élément structuré
- **FAIL** : aucun

#### 16. `word_count` *(v0.2.0)*
Compte les mots du body (excluant `<nav>`, `<header>`, `<footer>`, `<aside>`, `<script>`, `<style>`)
- **PASS** : ≥ 300 mots
- **WARN** : 100–299 mots
- **FAIL** : < 100 mots
- **SKIP** : page de type homepage

---

## Scoring global

```
score_check : PASS=100, WARN=50, FAIL=0, SKIP=exclu
score_catégorie = Σ(score × weight) / Σ(weight) sur checks non-SKIP
score_global = score_structure×0.40 + score_html×0.30 + score_content×0.30
```

Threshold CLI par défaut : **70/100**. Exit code 1 si score < threshold.

---

## Page-type awareness (v0.2.0)

| Type | Détection auto (mode `auto`) | Checks skippés |
|------|------------------------------|----------------|
| `homepage` | URL path = `""`, `"/"`, `/index.html`, `/index.php`, `/index.htm` | `faq_pattern`, `eeat_signals`, `word_count` |
| `article` | Tout autre path | aucun |
| `doc` | Explicite uniquement (`--page-type doc`) | aucun |

---

## API publique (v0.4.0)

```python
from pythia import audit_url, audit_html, fix_url, compare_urls
from pythia import Report, CheckResult, Fix, FixReport, CompareReport, AuditContext

# Audit live
report: Report = await audit_url("https://example.com/page")

# Audit offline
report: Report = await audit_html(html_string, base_url="https://example.com/page")

# Fixes HTML prêts à coller
fix_report: FixReport = await fix_url("https://example.com/page")
for fix in fix_report.fixes:
    print(fix.check_name, fix.location, fix.snippet)

# Comparaison concurrentielle
cmp: CompareReport = await compare_urls("https://site-a.com", "https://site-b.com")
print(cmp.leader, cmp.score_delta)
```

Exports `__init__.py` : `audit_url`, `audit_html`, `fix_url`, `compare_urls`, `generate_fixes`,
`generate_llms_txt`, `Report`, `CheckResult`, `Fix`, `FixReport`, `CompareReport`, `AuditContext`, `__version__`

---

## Sessions de travail

| Session | Date | Travail effectué |
|---------|------|-----------------|
| Scaffold v0.1 | 2026-04-24 | Arbo complète, pyproject.toml, models, scoring, i18n, fetcher, CLI, reporters, 14 stubs, CI, README, CLAUDE.md |
| v0.1.0 — checks complets | 2026-04-24 | 14 checks implémentés (structure, schema, html, content), 88 tests, ruff clean, publié PyPI |
| v0.2.0 — page-type + 2 nouveaux checks | 2026-04-25 | `--page-type`, auto-détection homepage, `eeat`/`faq` SKIP homepage, `canonical_url`, `word_count`, 112 tests |
| v0.2.1 — API publique | 2026-04-25 | `api.py` (`audit_url`, `audit_html`), `__init__.py` exports, SKIP gracieux structure sans base_url, 125 tests |
| v0.4.0 — fix + compare | 2026-04-26 | `pythia fix` (fixers.py, reporters/fixes.py, Fix/FixReport models), `pythia compare` (reporters/compare.py, CompareReport model), `fix_url()`/`compare_urls()` API, fix JSON CLI print(), 212 tests |
| v0.4.1 — GitHub Action | 2026-04-26 | `action.yml` composite action (`BigFoot3/pythia@v1`), dual-pass audit (JSON outputs + Markdown step summary), `publish.yml` pattern fix `v*` → `v*.*.*`, floating `v1` tag |
