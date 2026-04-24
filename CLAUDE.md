# Pythia — CLAUDE.md

Package Python open source d'audit GEO/AEO (Generative Engine Optimization).
CLI local-first, sans API key requise. Distribué sur PyPI sous `pythia-geo`.

> Mettre à jour après chaque check implémenté.
> Dernière mise à jour : 2026-04-24

---

## Distribution

| Attribut | Valeur |
|----------|--------|
| Nom PyPI | `pythia-geo` |
| Import Python | `pythia` |
| Commande CLI | `pythia` |
| Repo | `git@github.com:BigFoot3/pythia.git` |
| Path VPS | `/root/pythia/` |

---

## Stack

| Package | Version | Rôle |
|---------|---------|------|
| typer | >=0.12 | CLI entrypoint |
| rich | >=13 | Affichage terminal |
| httpx | >=0.27 | HTTP async |
| beautifulsoup4 | >=4.12 | Parsing HTML |
| lxml | >=5 | Parser HTML (backend BS4) |
| pydantic | >=2.7 | Modèles de données |

Dev uniquement : `pytest`, `pytest-asyncio`, `pytest-cov`, `respx`, `ruff`.

---

## Structure

```
src/pythia/
  __init__.py         # __version__
  cli.py              # Typer app — commandes audit / list-checks / version
  fetcher.py          # httpx async — fetch_page(), fetch_robots(), fetch_url()
                      # cache in-memory dans AuditContext._cache
  models.py           # CheckResult, Report, AuditContext (pydantic)
  scoring.py          # score_results(), build_report() — pondération 40/30/30
  i18n.py             # get_message(check_name, status, lang) — FR et EN
  checks/
    __init__.py       # ALL_CHECKS : list[type[BaseCheck]] — registre statique
    base.py           # BaseCheck ABC — _result(status, ctx), _skip(reason)
    structure.py      # checks 1–4 : llms_txt, llms_full_txt, robots_ai_bots, sitemap
    schema.py         # check 5 : jsonld_present_valid
    html.py           # checks 6–10 : single_h1, heading_hierarchy, title_length,
                      #               meta_description, opengraph_minimal
    content.py        # checks 11–14 : generic_headings, faq_pattern, eeat_signals,
                      #                structured_content
  reporters/
    markdown.py       # render_markdown(report) -> str
    json_reporter.py  # render_json(report) -> str  (pas json.py — conflit stdlib)
```

---

## Contrat d'interface

```python
# BaseCheck
class BaseCheck(ABC):
    name: str          # identifiant snake_case
    category: Literal["structure", "html", "content"]
    weight: float = 1.0

    @abstractmethod
    async def run(self, ctx: AuditContext) -> CheckResult: ...

    def _result(self, status, ctx, details=None, recommendation=None) -> CheckResult: ...
    def _skip(self, reason="") -> CheckResult: ...

# CheckResult
class CheckResult(BaseModel):
    name: str
    category: Literal["structure", "html", "content"]
    status: Literal["PASS", "WARN", "FAIL", "SKIP"]
    score: int          # PASS=100, WARN=50, FAIL=0, SKIP=0
    weight: float = 1.0
    message: str        # i18n via get_message()
    details: dict
    recommendation: str | None

# AuditContext
class AuditContext(BaseModel):
    url: str
    lang: Literal["fr", "en"] = "en"
    html: str           # contenu HTML de la page principale
    robots_txt: str     # contenu de /robots.txt
    _soup: PrivateAttr  # BeautifulSoup — accès via ctx.get_soup()
    _cache: PrivateAttr # {url: httpx.Response} — in-memory
```

---

## Scoring

| Catégorie | Poids |
|-----------|-------|
| structure | 40% |
| html | 30% |
| content | 30% |

Score par check : PASS=100, WARN=50, FAIL=0, SKIP=exclu du calcul.
Score catégorie = moyenne pondérée des checks non-SKIP (weight intra-catégorie).
Score global = Σ(score_cat × poids_cat).
Exit code CLI : 0 si score ≥ threshold (défaut 70), 1 sinon.

---

## Invariants

- `BaseCheck.run()` ne lève jamais d'exception — retourner SKIP avec un message explicatif.
- `CheckResult.score` est toujours cohérent avec `status` via `_result()`.
- `reporters/json_reporter.py` (pas `json.py`) — éviter conflit avec `import json` stdlib.
- Tests écrits EN MÊME TEMPS que le code — jamais après.
- Commit messages conventionnels : `feat:`, `fix:`, `docs:`, `test:`, `chore:`.

---

## Bots IA surveillés (check `robots_ai_bots`)

`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `CCBot`, `MistralAI-User`

---

## Commandes utiles

```bash
cd /root/pythia
source .venv/bin/activate

# CLI
pythia audit https://example.com
pythia audit https://example.com --format json --lang fr --threshold 70 --output report.md
pythia list-checks
pythia version

# Tests
pytest tests/ -v --cov=src/pythia
pytest tests/test_checks/test_html.py -v  # un module spécifique

# Lint
ruff check src/ tests/

# Build
hatch build

# Git
git add -A && git commit -m "feat: ..." && git push
```

---

## CI/CD

- CI : `.github/workflows/ci.yml` — Linux + macOS, Python 3.11 + 3.12, lint + tests
- Publish : `.github/workflows/publish.yml` — tag `v*` → PyPI via trusted publishing (OIDC)
  - Setup PyPI trusted publisher : pypi.org → pythia-geo → Publishing → Add trusted publisher
  - Owner: BigFoot3 | Repo: pythia | Workflow: publish.yml

---

## Instructions pour Claude Code

À la fin de chaque session de travail :
1. Mettre à jour ce CLAUDE.md si l'architecture, l'API ou la stack ont changé
2. Mettre à jour CONTEXT_TECHNIQUE.md (statuts checks + session log)
3. Lancer les tests : `pytest tests/ -v --cov=src/pythia`
4. Commiter et pousser : `git add -A && git commit -m "..." && git push`
