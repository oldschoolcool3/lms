# LMS

A fork of [frappe/lms](https://github.com/frappe/lms) — an open-source Learning
Management System — being extended toward AI-era features (tutor, authoring,
analytics, interop). The fork stays close to upstream; see
`docs/000-overview/explanation/002-fork-strategy-and-roadmap.md`.

## Services

| Service | Stack | Directory |
|---------|-------|-----------|
| Backend | Frappe Framework, Python 3.10+, MariaDB, Redis | `lms/` |
| Frontend | Vue 3, Vite, Tailwind, frappe-ui, Pinia | `frontend/` |

Versions above are orientation only — `pyproject.toml` and
`frontend/package.json` are the source of truth. The backend runs inside a
[Frappe bench](https://docs.frappe.io/framework/user/en/bench), not from this
checkout alone.

## Dev Environment

- **Runtime**: a bench with a site that has the `lms` app installed
  (`docs/002-development/how-to-guides/003-install-with-bench.md`)
- **Task runner**: [Taskfile](https://taskfile.dev/) — run `task --list` for all targets
- **Monorepo**: [Nx](https://nx.dev/) — task caching and affected analysis
  (projects: `backend` = `lms/`, `frontend` = `frontend/`)
- **Pre-commit**: ruff, prettier, eslint, gitleaks, commitlint —
  `uvx pre-commit run --all-files`
- **Package managers**: `yarn` (classic) for JS, `uv`/`uvx` for Python tooling

## Commands

```bash
task install          # Install all dependencies (yarn root + frontend)
task dev:frontend     # Vite dev server (needs a running bench site behind it)
task lint             # Lint all projects (ruff + prettier, via Nx, cached)
task test             # All tests (frontend Vitest; backend needs a bench)
task test:backend     # Server tests inside a bench (env: BENCH_DIR, SITE)
task precommit        # Run every pre-commit hook against the full tree
```

Nx directly (with caching and affected analysis):

```bash
npx nx run-many -t lint              # Lint everything (cached)
npx nx affected -t test              # Test only what changed vs develop
npx nx run frontend:build            # Vite build → lms/public/frontend (needs a bench)
npx nx graph                         # Project dependency graph
```

The frontend `build` (and `test:backend`) only run inside a Frappe bench —
upstream builds assets with `bench build --app lms`. Standalone-runnable
targets are `lint` and the frontend `test` (Vitest). See
`docs/002-development/how-to-guides/001-run-tasks-with-nx.md`.

## Project Structure

```
lms/                  # Frappe app (Python)
  lms/doctype/        #   Data model — one dir per DocType (JSON + controller + tests)
  lms/api.py          #   Whitelisted API methods
  hooks.py            #   App registry: doc events, scheduler, routes, fixtures
  patches/            #   One-off migrations (ordered by patches.txt)
  www/, templates/    #   Server-rendered portal pages (legacy surface)

frontend/src/
  pages/              # Routed views (registered in router.js)
  components/         # Shared Vue components
  stores/             # Pinia stores
  types/              # TypeScript types for DocTypes + API
  tests/              # Vitest specs
```

## Testing

- **Backend**: Frappe test runner — `task test:backend` (requires bench + site;
  see `scripts/test-backend.sh`). CI: `.github/workflows/ci.yml`.
- **Frontend**: Vitest + Vue Test Utils (jsdom) — `task test:frontend`.
- **E2E**: Cypress against a running site — `task test:e2e`.

## Code Standards

- Python: tabs, line length 110, ruff (config in `pyproject.toml`); Frappe
  ORM/primitives over raw SQL; user-facing strings in `_()`
- Frontend: Vue 3 `<script setup>`, TypeScript for new code, prettier
  (`frontend/.prettierrc.json`), frappe-ui components and resources first;
  strings in `__()`; RTL-safe Tailwind (logical `ms-`/`me-` classes)
- Conventional commits (types enumerated in `commitlint.config.js`)

## Rules

@.claude/rules/working-posture.md
@.claude/rules/architecture.md
@.claude/rules/security.md
@.claude/rules/coding-style-python.md
@.claude/rules/coding-style-frontend.md
@.claude/rules/testing.md
@.claude/rules/git-workflow.md
@.claude/rules/worktree-sessions.md

## Documentation

- `docs/` follows the [Diataxis](https://diataxis.fr/) framework — see
  `docs/README.md` for the index
- Fork strategy and feature roadmap: `docs/000-overview/explanation/`
- Development tooling (Nx, pre-commit, installs): `docs/002-development/`
- Upstream product docs: <https://docs.frappe.io/learning>

## Keeping these instructions honest

These files are re-read every session, so a stale fact here misleads every
session. Keep them drift-resistant:

- **State behavior, not transcribed facts.** Prefer "open the file and match
  it" over copying its contents (which rot on the next edit).
- **A volatile fact belongs here only if it's guarded.** Unguarded lists —
  DocType names, file paths, dependency versions — drift fast; point to the
  source of truth (`lms/lms/doctype/`, `pyproject.toml`,
  `frontend/package.json`) instead of enumerating them.
- **Never cite line numbers.** Cite the file and the named section.
- **One fact, one home.** Don't repeat a version or path across files; they
  drift apart.
