# Pythia — CLAUDE.md

CLI et bibliothèque Python d'audit GEO/AEO (Generative Engine Optimization) — local-first, sans clé API requise.

Asymétrie de nommage : le paquet PyPI s'appelle `pythia-geo`, le module s'importe `pythia`, la commande CLI est `pythia`.
Ne pas « corriger » l'un vers l'autre.

## Où se trouve le reste

- Comportements non évidents des checks (SKIP en masse sans `base_url`, page-type détecté sur le path de l'URL seul, poids intra-catégorie non standard), matrice, seuils et scoring : `/root/pythia/CONTEXT_TECHNIQUE.md`
- Historique des versions : `/root/pythia/CHANGELOG.md`

## Directives

Écrire les tests en même temps que le code, jamais après.

> Directive, pas un piège : elle n'a pas de `fichier:ligne` à produire. Restaurée le
> 2026-07-29 — la réduction du 2026-07-28 l'avait retirée alors qu'elle n'a aucun autre
> domicile (0 occurrence dans le CLAUDE.md global, le rituel `/fin-session` et les
> 6 skills, sur 6 motifs distincts).

## Pièges

⚠️ Un audit remonte une exception au lieu d'un rapport → les checks sont appelés sans `try/except`, donc une exception dans `run()` fait tomber l'audit entier → dans un check, retourner `self._skip("raison")`, ne jamais lever [src/pythia/api.py:16]

⚠️ Un `CheckResult` porte un score qui contredit son statut → le score n'est dérivé du statut que si le résultat passe par `_result()` → construire tout résultat via `self._result(status, ctx)` ou `self._skip()`, jamais à la main [src/pythia/checks/base.py:34]

⚠️ `json.loads()` échoue sur la sortie de `pythia audit --format json` → `console.print()` (rich) colorise et enveloppe le texte, ce qui corrompt le JSON → réserver `console.print()` au Markdown et aux messages, sortir le JSON avec `print()` natif [src/pythia/cli.py:60 contre cli.py:62]

⚠️ `pythia generate-llms` ne rend qu'une fraction des pages du site → devant un sitemapindex, le code ne suit que le premier sitemap enfant et ignore les autres → inspecter la structure du sitemap avant de conclure à un bug de crawl [src/pythia/generators/llms_txt.py:94-102]

⚠️ `BigFoot3/pythia@v1` sert encore l'ancienne version après une publication → `publish.yml` ne se déclenche que sur les tags `v*.*.*`, personne ne déplace le tag flottant `v1` → repositionner `v1` à la main après chaque publication [.github/workflows/publish.yml:6]
