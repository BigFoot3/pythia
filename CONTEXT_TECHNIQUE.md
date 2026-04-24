# Pythia — Contexte technique

Version cible : **0.1.0**
Checks implémentés : **0 / 14**
Dernière mise à jour : 2026-04-24

---

## Matrice des 14 checks

| # | ID | Catégorie | Fichier | Statut |
|---|-----|-----------|---------|--------|
| 1 | `llms_txt_present` | structure | checks/structure.py | 🔲 TODO |
| 2 | `llms_full_txt_present` | structure | checks/structure.py | 🔲 TODO |
| 3 | `robots_ai_bots` | structure | checks/structure.py | 🔲 TODO |
| 4 | `sitemap_accessible` | structure | checks/structure.py | 🔲 TODO |
| 5 | `jsonld_present_valid` | structure | checks/schema.py | 🔲 TODO |
| 6 | `single_h1` | html | checks/html.py | 🔲 TODO |
| 7 | `heading_hierarchy` | html | checks/html.py | 🔲 TODO |
| 8 | `title_length` | html | checks/html.py | 🔲 TODO |
| 9 | `meta_description` | html | checks/html.py | 🔲 TODO |
| 10 | `opengraph_minimal` | html | checks/html.py | 🔲 TODO |
| 11 | `generic_headings` | content | checks/content.py | 🔲 TODO |
| 12 | `faq_pattern` | content | checks/content.py | 🔲 TODO |
| 13 | `eeat_signals` | content | checks/content.py | 🔲 TODO |
| 14 | `structured_content` | content | checks/content.py | 🔲 TODO |

---

## Détail des checks et seuils

### Catégorie : structure (poids 40%)

#### 1. `llms_txt_present`
GET `/llms.txt`
- **PASS** : HTTP 200 + body non vide
- **FAIL** : 404 / erreur réseau / body vide

#### 2. `llms_full_txt_present`
GET `/llms-full.txt` *(check bonus — weight=0.5, score max = WARN)*
- **PASS** : HTTP 200 + body non vide
- **WARN** : absent ou 404

#### 3. `robots_ai_bots`
Parse `/robots.txt`, vérifie l'absence de `Disallow` sur :
`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `CCBot`, `MistralAI-User`
- **PASS** : aucun bot IA bloqué
- **WARN** : `/robots.txt` absent
- **FAIL** : ≥ 1 bot IA bloqué explicitement

#### 4. `sitemap_accessible`
Cherche `/sitemap.xml` direct, ou `Sitemap:` dans robots.txt
- **PASS** : sitemap trouvé + HTTP 200
- **FAIL** : aucun sitemap trouvable ou inaccessible

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

---

### Catégorie : content (poids 30%)

#### 11. `generic_headings`
H1–H6 contenant (case-insensitive) : `home`, `welcome`, `page`, `untitled`
- **PASS** : 0 heading générique
- **WARN** : 1–2 génériques en H2–H6 uniquement
- **FAIL** : H1 générique **ou** ≥ 3 headings génériques

#### 12. `faq_pattern`
Détecte : `<dl>`, `<details><summary>`, `itemtype="FAQPage"`, ou ≥ 3 paires Q/R
- **PASS** : pattern détecté
- **WARN** : absent *(WARN et non FAIL — la FAQ est un bonus GEO)*

#### 13. `eeat_signals`
Auteur : `rel="author"`, `[itemprop="author"]`, `.author`, `.byline`
Date : `<time>`, `[itemprop="datePublished"]`, `meta[property="article:published_time"]`
- **PASS** : auteur + date détectés
- **WARN** : un seul signal sur deux
- **FAIL** : aucun signal

#### 14. `structured_content`
`<ul>`, `<ol>`, ou `<table>` dans `<body>`
- **PASS** : ≥ 1 élément structuré
- **FAIL** : aucun

---

## Scoring global

```
score_check : PASS=100, WARN=50, FAIL=0, SKIP=exclu
score_catégorie = Σ(score × weight) / Σ(weight) sur checks non-SKIP
score_global = score_structure×0.40 + score_html×0.30 + score_content×0.30
```

Threshold CLI par défaut : **70/100**. Exit code 1 si score < threshold.

---

## Sessions de travail

| Session | Date | Travail effectué |
|---------|------|-----------------|
| Scaffold v0.1 | 2026-04-24 | Arbo complète, pyproject.toml, models, scoring, i18n, fetcher, CLI, reporters, 14 stubs, CI, README, CLAUDE.md |
