---
title: Task Command Reference
description: Quick reference for every Taskfile target — aggregate, backend, and frontend tasks, with prerequisites and environment variables.
type: reference
tags: [taskfile, task, commands, reference, development]
---

# Task Command Reference

Run targets with `task <name>`. The live source of truth is always:

```bash
task --list
```

Tasks are defined in the root `Taskfile.yml` plus two split files,
`tasks/backend.yml` and `tasks/frontend.yml`. Both are included with
`flatten: true`, so every task name lives at the root namespace — you run
`task test:backend`, never `task backend:test:backend`.

## Aggregate tasks (Taskfile.yml)

| Task | What it does | Prerequisites |
|------|--------------|---------------|
| `task install` | Install all dependencies (`yarn install`; frontend installs via postinstall) | Node + yarn classic |
| `task build` | Build all projects via `npx nx run-many -t build` | A bench — `frontend:build` resolves `sites/common_site_config.json`; outside a bench use `bench build --app lms` |
| `task test` | Run all tests via `npx nx run-many -t test` | Backend tests need a bench (see below); frontend Vitest does not |
| `task lint` | Lint all projects via `npx nx run-many -t lint` | None beyond install |
| `task precommit` | Run all pre-commit hooks against the full tree (`uvx pre-commit run --all-files`) | `uv` installed (hooks run via `uvx`) |
| `task test:e2e` | Run Cypress end-to-end tests (`npx cypress run --e2e`) | A running site — see `cypress.config.js` |

## Backend tasks (tasks/backend.yml)

| Task | What it does | Prerequisites |
|------|--------------|---------------|
| `task lint:backend` | Ruff lint of the Frappe app (`npx nx run backend:lint`) | None — ruff runs via `uvx` |
| `task format:backend` | Ruff format, writes changes (`npx nx run backend:format`) | None — ruff runs via `uvx` |
| `task test:backend` | Run server tests inside a bench (`bash scripts/test-backend.sh`) | A Frappe bench with a site that has lms installed |

### Backend test environment variables

`scripts/test-backend.sh` cannot run tests from this repo checkout alone — it
changes into a bench and runs `bench --site "$SITE" run-tests --app lms`.
Configure it with:

| Variable | Meaning | Default |
|----------|---------|---------|
| `BENCH_DIR` | Path to the Frappe bench | `~/frappe-bench` |
| `SITE` | Site with the lms app installed | `lms.localhost` |

Extra arguments pass through to `bench run-tests`:

```bash
task test:backend
BENCH_DIR=~/benches/lms SITE=lms.test task test:backend
task test:backend -- --module lms.lms.doctype.lms_quiz.test_lms_quiz
```

The script exits with an error if the `bench` CLI is not on `PATH` or if
`$BENCH_DIR/sites` does not exist. To set up a bench, see
[Install with bench](../how-to-guides/003-install-with-bench.md).

## Frontend tasks (tasks/frontend.yml)

| Task | What it does | Prerequisites |
|------|--------------|---------------|
| `task dev:frontend` | Start the Vite dev server (`yarn dev` in `frontend/`) | A running bench site to proxy to |
| `task build:frontend` | Build the SPA into `lms/public/frontend` (`npx nx run frontend:build`) | A bench — `src/socket.js` imports `sites/common_site_config.json`; outside a bench use `bench build --app lms` |
| `task test:frontend` | Run Vitest unit tests (`npx nx run frontend:test`) | None beyond install |
| `task lint:frontend` | Prettier check on `frontend/src` (`npx nx run frontend:lint`) | None beyond install |
| `task format:frontend` | Prettier write on `frontend/src` | None beyond install |

## How tasks relate to Nx

Most tasks are thin wrappers over Nx targets on the `backend` and `frontend`
projects, so they benefit from Nx caching. For running Nx directly (including
`nx affected` against the `develop` base), see
[Run tasks with Nx](../how-to-guides/001-run-tasks-with-nx.md). For the
target definitions and cache inputs, see
[Nx configuration](001-nx-configuration.md).
