---
title: Nx Monorepo Architecture
description: Why Nx is layered over this Frappe + Vue repository, how caching and affected analysis work, and what is deliberately kept out of the task graph.
type: explanation
module: null
tags: [nx, monorepo, caching, architecture, development]
---

# Nx Monorepo Architecture

## Why Nx?

This repository holds two projects with completely different toolchains: a Frappe Framework app in `lms/` (Python, linted with ruff via `uvx`) and a Vue 3 SPA in `frontend/` (yarn classic, Vite, Vitest, Prettier). Nx is not here to replace either toolchain — it wraps them. What it adds is **caching** (a lint or test run with unchanged inputs is replayed instantly) and **affected analysis** (a frontend-only change does not need to run ruff, and vice versa).

The graph is deliberately flat: two projects, no cross-project `dependsOn` edges. The interesting coupling between them happens at the *output* level, not the task level — see [Where build output goes](#where-build-output-goes).

## The two projects

| Nx project | Directory | Targets | Notes |
|------------|-----------|---------|-------|
| `backend` | `lms/` | `lint`, `format`, `format-check`, `test` | All Python tooling runs via `uvx ruff`; `test` is uncached |
| `frontend` | `frontend/` | `serve`, `build`, `test`, `lint` | `serve`/`build`/`test` wrap yarn scripts; `lint` invokes Prettier directly |

Each project declares its targets in a `project.json` (`lms/project.json`, `frontend/project.json`); workspace-wide defaults live in `nx.json`. The full field-by-field breakdown is in the [Nx configuration reference](../reference/001-nx-configuration.md).

## Why backend tests are not cached

`nx.json` sets `test` targets to `cache: true` by default, and `frontend:test` (Vitest in jsdom) honors that — it is hermetic, so replaying a cached pass is safe. `backend:test` explicitly overrides it with `cache: false`, and this is the most important caching decision in the repo.

The backend test command is `bash scripts/test-backend.sh`, which changes directory *out of this checkout* into a Frappe bench (`BENCH_DIR`, default `~/frappe-bench`) and runs `bench --site "$SITE" run-tests --app lms`. The outcome depends on state Nx cannot see or hash: which apps are installed in the bench, the site's database, pending migrations. A cache hit would replay a stale green result against a bench that may have changed. So the target runs every time. See [Install with bench](../how-to-guides/003-install-with-bench.md) for setting up that runtime.

## Named inputs

Three named inputs in `nx.json` drive cache keys:

- **`default`** — everything under the project root, plus `sharedGlobals`.
- **`sharedGlobals`** — the runtime output of `node --version`. A Node bump invalidates every cache whose inputs include `default` — `frontend:build` (via `production`) and `frontend:test`; targets that override their inputs — `backend:lint`, `backend:format-check`, and `frontend:lint` — are unaffected. (The backend pins its toolchain via `uvx ruff@<version>`, so the Python runtime is deliberately *not* a shared global — it would only over-invalidate the frontend caches.)
- **`production`** — `default` minus test files (`*.test.*`, `*.spec.*`, `test_*.py`, `tests/**`). Build targets use it, so editing a test never forces a rebuild.

Backend targets do not use `default` at all — `backend:lint` and `backend:format-check` hash only `lms/**/*.py` plus `pyproject.toml`. That narrowing matters because of what lands in `lms/` from the other project, which brings us to:

## Where build output goes

`frontend:build` runs Vite, but its declared outputs live inside the *backend's* directory:

```text
{workspaceRoot}/lms/public/frontend    # compiled SPA assets
{workspaceRoot}/lms/www/_lms.html      # the SPA's HTML entry point
```

This cross-project output is unusual for a monorepo, but it is how Frappe works: the bench serves whatever sits in an app's `public/` and `www/` directories, so for the site to serve the SPA at all, the build must land inside `lms/`. Declaring these as workspace-rooted `outputs` lets Nx restore the built assets on a cache hit instead of rebuilding.

The build is also bench-*coupled*, not just bench-targeted: `src/socket.js` statically imports `../../../../sites/common_site_config.json`, which exists only when the frontend sits at `bench/apps/lms/frontend`. So `frontend:build` runs inside a bench (as upstream CI does, via `bench build --app lms`) — it is not a standalone target like `lint` and `test`. The Nx wrapper provides caching and output tracking; it does not remove the bench dependency.

Two consequences worth internalizing:

1. Files under `lms/public/frontend` and `lms/www/_lms.html` are **artifacts, not source** — never edit them by hand.
2. Because backend targets hash only `*.py` files, a frontend build dropping assets into `lms/` does **not** invalidate backend caches. If you ever widen backend inputs to `default`, you will reintroduce that churn.

## Affected analysis

`defaultBase` in `nx.json` is `develop` — the fork's default branch. `npx nx affected -t lint test` diffs your branch against `develop`, maps changed files to projects, and runs targets only for those projects. With two projects the payoff is simple but real: a backend-only PR skips Vitest and Prettier entirely; a frontend-only PR skips ruff. Day-to-day usage is covered in [Run tasks with Nx](../how-to-guides/001-run-tasks-with-nx.md).

## What is deliberately outside the graph

`.nxignore` excludes six paths from Nx's file watching and affected analysis:

| Path | Why it is excluded |
|------|--------------------|
| `docs/` | Prose. A docs edit should never mark a project affected or bust a cache |
| `cypress/` | E2E tests run against a live site (`task test:e2e`), not as an Nx target |
| `docker/` | Packaging for the containerized install, not part of either project's build |
| `frappe-ui/` | A git submodule of the UI library — a separate repository this graph does not build |
| `.github/` | Workflow edits are validated by CI itself, not by local task caches |
| `.claude/` | Agent configuration, irrelevant to builds and tests |

The rule of thumb: if a path belongs to neither `backend` nor `frontend` and cannot change the result of their targets, it stays out so that touching it costs nothing.

## Nx, Taskfile, and bench

Three tools, three distinct roles:

| Tool | Role |
|------|------|
| **Taskfile** | The human entry point — `task lint`, `task build`, `task test:frontend`. Most targets delegate to Nx (`npx nx run backend:lint`) so they inherit caching for free |
| **Nx** | Build intelligence — task graph, cache, `affected` |
| **bench** | The Frappe *runtime*. Serving the site, migrations, and server tests all happen inside a bench. Nx never manages it — `backend:test` just shells out to it via `scripts/test-backend.sh` |

The Taskfile bypasses Nx exactly where caching makes no sense: `task test:backend` calls the bench script directly (and accepts CLI args), `task format:frontend` runs `prettier --write` (side-effectful), `task dev:frontend` starts a long-running Vite server, and `task precommit` runs `uvx pre-commit` across the whole tree (see [Pre-commit and quality gates](002-pre-commit-and-quality-gates.md)). The full command catalog is in the [task commands reference](../reference/002-task-commands.md).
