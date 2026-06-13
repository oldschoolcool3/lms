---
title: Run Tasks with Nx
description: How to use Nx to run, cache, and selectively execute lint, test, and build targets across the monorepo.
type: how-to
tags: [nx, tasks, caching, development]
---

# Run Tasks with Nx

## Run a single target for one project

```bash
npx nx run <project>:<target>
```

Project names match the `name` field in each `project.json`:

| Project | Directory | Targets |
|---------|-----------|---------|
| `backend` | `lms/` | `lint`, `format`, `format-check`, `test` |
| `frontend` | `frontend/` | `serve`, `build`, `test`, `lint` |

Examples:

```bash
npx nx run backend:lint      # ruff check via uvx
npx nx run frontend:test     # Vitest via yarn
npx nx run frontend:build    # Vite build into lms/public/frontend (needs a bench — see caveat)
```

## Run a target across all projects

```bash
npx nx run-many -t lint
npx nx run-many -t test
npx nx run-many -t build
```

Nx runs the target in every project that defines it and parallelizes
automatically. Note that `run-many -t test` includes `backend:test`, and
`run-many -t build` includes `frontend:build` — both need a Frappe bench
(see the caveats below).

## Run only affected projects

After making changes on a feature branch:

```bash
npx nx affected -t lint
npx nx affected -t test
```

Nx compares your branch against `develop` (configured as `defaultBase` in
`nx.json`) and only runs targets for projects whose inputs changed. Editing
only `frontend/src/` means `backend:lint` is skipped entirely.

CI runs the same thing: `.github/workflows/nx.yml` executes
`nx affected -t lint typecheck test` against the `nx-set-shas` base on every
pull request (the backend `test` target is bench-coupled, so it is excluded and
covered by `ci.yml` instead).

## Caching

`build`, `lint`, and `test` are cached by default (`targetDefaults` in
`nx.json`). Re-running a target with unchanged inputs replays the cached
result instantly. Targets with side effects opt out: `backend:format`
(writes files), `backend:test` (runs in an external bench), and
`frontend:serve` (long-running dev server) are never cached.

If you suspect a stale cache, clear it:

```bash
npx nx reset
```

## Caveat: backend:test needs a Frappe bench

`backend:test` wraps `scripts/test-backend.sh`, which runs
`bench run-tests --app lms` inside a bench — Frappe server tests cannot run
from this repo checkout alone. Configure it with environment variables:

```bash
BENCH_DIR=~/benches/lms SITE=lms.test npx nx run backend:test
```

`BENCH_DIR` defaults to `~/frappe-bench` and `SITE` to `lms.localhost`. The
target is never cached because its result depends on the bench, not on files
Nx can hash. If you have no bench yet, see
[Install with bench](003-install-with-bench.md).

## Caveat: frontend:build needs a Frappe bench too

`frontend:build` runs upstream's `yarn build` (Vite), and `src/socket.js`
statically imports `../../../../sites/common_site_config.json` — a file that
only exists when the frontend lives inside a bench (`bench/apps/lms/frontend`,
with `bench/sites/` alongside). A standalone `yarn build` / `nx run
frontend:build` in this checkout fails to resolve that import. Assets are
built the way upstream builds them: `bench build --app lms` inside the bench
(see `.github/workflows/ci.yml`). The standalone-runnable frontend targets are
`lint` and `test` (Vitest needs no bench).

## See also

- [Nx configuration reference](../reference/001-nx-configuration.md) — every
  target, input set, and output, in detail.
- [Task commands reference](../reference/002-task-commands.md) — the
  Taskfile wrappers (`task lint`, `task test:frontend`, ...) that call these
  same Nx targets.
