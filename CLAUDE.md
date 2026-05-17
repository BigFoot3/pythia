# Pythia — CLAUDE.md

CLI Python et bibliothèque PyPI d'audit GEO/AEO (Generative Engine Optimization) — 16 checks, local-first, sans clé API requise. Distribué sur PyPI sous `pythia-geo`.

> Fichier de référence pour Claude Code. Mettre à jour après chaque milestone.
> Dernière mise à jour : 2026-05-17

---

## Distribution

| Attribut | Valeur |
|----------|--------|
| Nom PyPI | `pythia-geo` |
| Version | `0.4.1` |
| Import Python | `pythia` |
| Commande CLI | `pythia` |
| Repo | `git@github.com:BigFoot3/pythia.git` |
| Path VPS | `/root/pythia/` |
| VPS | Hetzner CX23, Nuremberg — 178.104.41.200 |
| OS | Ubuntu 24.04, Python 3.12 |
| Service | — (pas de service systemd — CLI + lib PyPI) |
| URL | — (pas d'exposition web) |

---

## Stack

| Package | Version | Rôle |
|---------|---------|------|
| typer | 0.24.2 | CLI entrypoint |
| rich | 15.0.0 | Affichage terminal |
| httpx | 0.28.1 | HTTP async |
| beautifulsoup4 | 4.14.3 | Parsing HTML |
| lxml | 6.1.0 | Parser HTML (backend BS4) |
| pydantic | 2.13.3 | Modèles de données |

Dev uniquement : `pytest 9.0.3`, `pytest-asyncio 1.3.0`, `pytest-cov 7.1.0`, `respx 0.23.1`, `ruff 0.15.12`.
Build : `hatchling`.

---

## Structure du projet

```
src/pythia/
  __init__.py         # __version__ + exports publics (audit_url, audit_html, fix_url, compare_urls, generate_fixes, generate_llms_txt, modèles)
  cli.py              # Typer app — commandes : audit / fix / compare / generate-llms / list-checks / version
  api.py              # audit_url(), audit_html() — point d'entrée bibliothèque
  fetcher.py          # httpx async — fetch_page(), fetch_robots(), fetch_url()
                      # cache in-memory dans AuditContext._cache
  models.py           # CheckResult, Report, AuditContext, Fix, FixReport, CompareReport (pydantic)
  scoring.py          # score_results(), build_report() — pondération 40/30/30
  fixers.py           # generate_fixes(report) — génère les snippets HTML prêts à coller par check FAIL/WARN
  i18n.py             # get_message(check_name, status, lang) — FR et EN
  checks/
    __init__.py       # ALL_CHECKS : list[type[BaseCheck]] — registre statique (16 checks)
    base.py           # BaseCheck ABC — _result(status, ctx), _skip(reason)
    structure.py      # checks 1–5 : llms_txt, llms_full_txt, robots_ai_bots, sitemap, jsonld_present_valid
    schema.py         # (héritage v0.1 — jsonld_present_valid migré dans structure.py)
    html.py           # checks 6–11 : single_h1, heading_hierarchy, title_length,
                      #               meta_description, opengraph_minimal, canonical_url
    content.py        # checks 12–16 : generic_headings, faq_pattern, eeat_signals,
                      #                structured_content, word_count
  reporters/
    markdown.py       # render_markdown(report) -> str
    json_reporter.py  # render_json(report) -> str  (pas json.py — conflit stdlib)
    fixes.py          # render_fixes_markdown(), render_fixes_json()
    compare.py        # render_compare_markdown(), render_compare_json()
  generators/
    __init__.py       # exports generate_llms_txt
    llms_txt.py       # generate_llms_txt(url, max_pages, concurrency) — crawl sitemap → llms.txt
tests/
  conftest.py
  fixtures/
  test_api.py
  test_cli.py
  test_compare.py
  test_fixers.py
  test_models.py
  test_scoring.py
  test_checks/
    test_structure.py
    test_schema.py
    test_html.py
    test_content.py
  test_generators/
    test_llms_txt.py
action.yml              # GitHub Action composite (BigFoot3/pythia@v1) — audit en CI
pyproject.toml          # hatchling build, dépendances, ruff, pytest, coverage
CHANGELOG.md
CONTEXT_TECHNIQUE.md    # Matrice complète des 16 checks + seuils + sessions de travail
dist/                   # Wheel + sdist publiés sur PyPI
```

---

## Commandes CLI

```bash
# Audit — rapport Markdown (défaut) ou JSON
pythia audit https://example.com
pythia audit https://example.com --format json --lang fr --threshold 80 --output report.md --page-type article

# Fix — snippets HTML prêts à coller pour chaque FAIL/WARN
pythia fix https://example.com
pythia fix https://example.com --format json

# Compare — comparaison concurrentielle deux URLs côte à côte
pythia compare https://site-a.com https://site-b.com

# Générer un llms.txt depuis le sitemap du site
pythia generate-llms https://example.com --max-pages 50

# Utilitaires
pythia list-checks   # liste les 16 checks disponibles
pythia version
```

Exit code : **0** si score ≥ threshold (défaut 70), **1** sinon.

---

## API publique Python

```python
from pythia import audit_url, audit_html, fix_url, compare_urls, generate_fixes, generate_llms_txt
from pythia import Report, CheckResult, Fix, FixReport, CompareReport, AuditContext

# Audit live
report: Report = await audit_url("https://example.com/page")

# Audit offline (CI, HTML brut)
report: Report = await audit_html(html_string, base_url="https://example.com/page")

# Fixes HTML prêts à coller
fix_report: FixReport = await fix_url("https://example.com/page")
for fix in fix_report.fixes:
    print(fix.check_name, fix.location, fix.snippet)

# Comparaison concurrentielle
cmp: CompareReport = await compare_urls("https://site-a.com", "https://site-b.com")
print(cmp.leader, cmp.score_delta)

# Générer llms.txt
llms_content: str = await generate_llms_txt("https://example.com", max_pages=50, concurrency=5)
```

---

## Architecture des checks

### 16 checks — 3 catégories

| Cat. | Poids | # | ID | PASS | WARN | FAIL | SKIP |
|------|-------|---|----|------|------|------|------|
| structure | 40% | 1 | `llms_txt_present` | /llms.txt 200 non-vide | — | absent/vide | sans base_url |
| structure | 40% | 2 | `llms_full_txt_present` | /llms-full.txt 200 | absent | — | sans base_url |
| structure | 40% | 3 | `robots_ai_bots` | aucun bot IA bloqué | robots.txt absent | ≥1 bot bloqué | — |
| structure | 40% | 4 | `sitemap_accessible` | sitemap trouvé 200 | — | introuvable | sans base_url |
| structure | 40% | 5 | `jsonld_present_valid` | JSON-LD valide | JSON malformé | aucun | — |
| html | 30% | 6 | `single_h1` | exactement 1 | >1 | aucun | — |
| html | 30% | 7 | `heading_hierarchy` | continu | — | ≥1 saut | — |
| html | 30% | 8 | `title_length` | 30–65 chars | hors plage | absent | — |
| html | 30% | 9 | `meta_description` | 70–160 chars | hors plage | absent | — |
| html | 30% | 10 | `opengraph_minimal` | 3/3 tags OG | 1–2 manquants | aucun tag | — |
| html | 30% | 11 | `canonical_url` | `<link rel=canonical>` présent | absent | — | — |
| content | 30% | 12 | `generic_headings` | 0 générique | 1–2 en H2+ | H1 générique ou ≥3 | — |
| content | 30% | 13 | `faq_pattern` | FAQ détectée | absente | — | homepage |
| content | 30% | 14 | `eeat_signals` | auteur + date | un seul | aucun | homepage |
| content | 30% | 15 | `structured_content` | ≥1 liste ou table | — | aucun | — |
| content | 30% | 16 | `word_count` | ≥300 mots | 100–299 | <100 | homepage |

**Poids intra-catégorie :** llms_full_txt=0.5, canonical_url=0.75, tous les autres=1.0.

### Scoring

```
score_check : PASS=100, WARN=50, FAIL=0, SKIP=exclu du calcul
score_catégorie = Σ(score × weight) / Σ(weight)  [checks non-SKIP]
score_global = score_structure×0.40 + score_html×0.30 + score_content×0.30
```

### Page-type awareness

| Type | Détection (mode `auto`) | Checks skippés |
|------|------------------------|----------------|
| `homepage` | URL path = `""`, `/`, `/index.html`, `/index.php` | `faq_pattern`, `eeat_signals`, `word_count` |
| `article` | tout autre path | aucun |
| `doc` | explicite (`--page-type doc`) | aucun |

---

## Contrat d'interface (BaseCheck)

```python
class BaseCheck(ABC):
    name: str          # identifiant snake_case
    category: Literal["structure", "html", "content"]
    weight: float = 1.0

    @abstractmethod
    async def run(self, ctx: AuditContext) -> CheckResult: ...

    def _result(self, status, ctx, details=None, recommendation=None) -> CheckResult: ...
    def _skip(self, reason="") -> CheckResult: ...
```

- `run()` ne lève **jamais** d'exception — retourner `_skip()` en cas d'erreur.
- `CheckResult.score` est toujours cohérent avec `status` via `_result()`.

---

## GitHub Action (`action.yml`)

Composite action `BigFoot3/pythia@v1` — audite une URL dans n'importe quel workflow CI :

```yaml
- uses: BigFoot3/pythia@v1
  with:
    url: https://example.com
    threshold: 70        # défaut
    fail-on-fail: true   # défaut
    page-type: auto      # défaut
    lang: en             # défaut
```

Outputs : `score` (float), `passed` (true/false).
Dual-pass : JSON pour les outputs typés + Markdown pour `$GITHUB_STEP_SUMMARY`.

---

## CI/CD

- **CI** : `.github/workflows/ci.yml` — Linux + macOS, Python 3.11 + 3.12, lint (ruff) + tests
- **Publish** : `.github/workflows/publish.yml` — tag `v*.*.*` → PyPI via trusted publishing (OIDC)
  - Owner: BigFoot3 | Repo: pythia | Workflow: publish.yml

---

## Tests

```bash
cd /root/pythia && source .venv/bin/activate

# Suite complète (216 tests)
pytest tests/ -v --cov=src/pythia

# Module spécifique
pytest tests/test_checks/test_html.py -v

# Lint
ruff check src/ tests/

# Build
hatch build
```

Couverture minimale : **80%** (`fail_under = 80` dans pyproject.toml).

---

## Invariants

- `BaseCheck.run()` ne lève jamais d'exception — retourner `SKIP` avec message explicatif.
- `CheckResult.score` toujours cohérent avec `status` (via `_result()`).
- `reporters/json_reporter.py` (pas `json.py`) — évite conflit avec `import json` stdlib.
- Tests écrits **en même temps** que le code — jamais après.
- Commit messages conventionnels : `feat:`, `fix:`, `docs:`, `test:`, `chore:`.
- JSON CLI output via `print()` (pas `console.print()`) — évite les ANSI codes qui cassent `json.loads()`.

---

## Bots IA surveillés (`robots_ai_bots`)

`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `CCBot`, `MistralAI-User`

---

## Pièges connus

```
⚠️ json_reporter.py   → nommé ainsi (pas json.py) — conflit avec stdlib json si renommé
⚠️ console.print()    → ne jamais utiliser pour la sortie JSON CLI — insère ANSI + wrapping
                        qui casse json.loads() ; utiliser print() natif
⚠️ audit_html()       → sans base_url, les checks structure (llms_txt, llms_full_txt, sitemap)
                        retournent SKIP gracieusement — comportement voulu, pas un bug
⚠️ generate-llms      → nécessite un sitemap accessible (robots.txt Sitemap: ou /sitemap.xml)
                        — suit un seul niveau d'indirection (sitemap index)
⚠️ page-type auto     → détection sur le path URL uniquement — "/" ou vide = homepage
                        — ne pas se fier au contenu HTML pour la détection automatique
⚠️ weight intra-cat   → llms_full_txt_present=0.5, canonical_url=0.75, autres=1.0
                        — ne pas oublier ces poids dans les calculs de score
⚠️ action.yml tag     → publish.yml matche v*.*.* uniquement (pas v1, v2…)
                        — le floating tag v1 est positionné manuellement après publish
⚠️ .venv/             → venv local (pas venv/) — source .venv/bin/activate
⚠️ hatch build        → génère dans dist/ — ne pas confondre avec pip install -e .
```

---

## Commandes utiles

```bash
cd /root/pythia && source .venv/bin/activate

# Audit rapide
pythia audit https://kryptide.fr --lang fr

# Tests + couverture
pytest tests/ -v --cov=src/pythia --cov-report=term-missing

# Lint
ruff check src/ tests/

# Build wheel + sdist
hatch build

# Git
git log --oneline -5
git add -A && git commit -m "feat: ..." && git push
```

---

## Historique des versions

| Version | Date | Contenu |
|---------|------|---------|
| v0.1.0 | 2026-04-24 | 14 checks, CLI audit, 88 tests — première release PyPI |
| v0.2.0 | 2026-04-25 | Page-type awareness, `canonical_url`, `word_count`, 112 tests |
| v0.2.1 | 2026-04-25 | API publique `audit_url`/`audit_html`, 125 tests |
| v0.3.0 | 2026-04-25 | `pythia generate-llms`, `generate_llms_txt()`, 153 tests |
| v0.4.0 | 2026-04-26 | `pythia fix`, `pythia compare`, `fix_url`/`compare_urls`, 212 tests |
| v0.4.1 | 2026-04-26 | GitHub Action `BigFoot3/pythia@v1`, dual-pass audit, 216 tests |

---

## Instructions pour Claude Code

À la fin de chaque session de travail :
1. Mettre à jour ce CLAUDE.md si l'architecture, l'API, les checks ou la stack ont changé
2. Mettre à jour `CONTEXT_TECHNIQUE.md` (matrice checks + log de session)
3. Synchroniser la copie : `cp /root/pythia/CLAUDE.md /root/CLAUDE_docs/CLAUDE-pythia.md`
4. Lancer les tests : `cd /root/pythia && source .venv/bin/activate && pytest tests/ -v --cov=src/pythia`
5. Commiter et pousser : `git add -A && git commit -m "..." && git push`
