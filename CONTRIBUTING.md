# Contributing to Pythia

Thanks for your interest in contributing. This document covers the essentials.

## Setup

```bash
git clone git@github.com:BigFoot3/pythia.git
cd pythia
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running tests

```bash
pytest tests/ -v                          # all tests
pytest tests/test_checks/test_html.py -v  # one module
pytest tests/ --cov=src/pythia            # with coverage
```

Coverage must stay above 80%. In practice we target 95%+.

## Lint

```bash
ruff check src/ tests/        # check
ruff check src/ tests/ --fix  # auto-fix
```

## Adding a check

1. Pick the right file: `src/pythia/checks/{structure,schema,html,content}.py`
2. Subclass `BaseCheck`, implement `async def run(self, ctx: AuditContext) -> CheckResult`
3. Use `self._result(status, ctx, details, recommendation)` — never raise exceptions
4. Register the class in the file's `CHECKS` list
5. Add i18n messages (PASS/WARN/FAIL) in `src/pythia/i18n.py` for both `en` and `fr`
6. Write tests in `tests/test_checks/` — minimum 3 cases per check (PASS, WARN or FAIL, edge case)
7. Update `CONTEXT_TECHNIQUE.md` — mark the check ✅ DONE

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new_check_name check
fix: handle edge case in robots_ai_bots
test: add missing WARN case for title_length
docs: update CONTRIBUTING
chore: bump httpx to 0.28
```

## Pull requests

- One PR per check or per fix — keep diffs reviewable
- All CI checks must pass (lint + tests + coverage)
- Update `CHANGELOG.md` under `[Unreleased]`

## Reporting issues

Open an issue on [GitHub](https://github.com/BigFoot3/pythia/issues).
Include the URL you audited (if public), the command you ran, and the full output.
