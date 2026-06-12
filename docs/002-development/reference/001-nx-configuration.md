---
title: Nx Configuration Reference
description: Complete reference for nx.json, the backend and frontend project.json files, .nxignore, and the Nx cache.
type: reference
module: null
tags: [nx, configuration, reference, development]
---

# Nx Configuration Reference

The `project.json` files are the source of truth for every target. If a target's
command, inputs, or outputs change in `lms/project.json` or `frontend/project.json`,
update this document in the same change.

## `nx.json` (workspace root)

| Field | Value | Purpose |
|-------|-------|---------|
| `defaultBase` | `"develop"` | Branch used by `nx affected` for comparison |
| `namedInputs.default` | `["{projectRoot}/**/*", "sharedGlobals"]` | All project files + shared globals |
| `namedInputs.sharedGlobals` | `[{runtime: "node --version"}]` | A Node version change invalidates caches whose inputs include `default` (the Python toolchain is pinned via `uvx ruff@<version>`, so it is intentionally not a shared global) |
| `namedInputs.production` | `["default", "!{projectRoot}/**/*.test.*", "!{projectRoot}/**/*.spec.*", "!{projectRoot}/**/test_*.py", "!{projectRoot}/**/tests/**"]` | Source files minus tests |
| `targetDefaults.build` | `dependsOn: ["^build"], inputs: ["production"], cache: true` | Builds depend on upstream builds, use production inputs |
| `targetDefaults.lint` | `inputs: ["default"], cache: true` | Lint uses all files, cached |
| `targetDefaults.test` | `inputs: ["default"], cache: true` | Test uses all files, cached |
| `targetDefaults.serve` | `cache: false` | Dev servers are never cached |

## Project: `backend` (`lms/project.json`)

The Frappe app under `lms/`. All commands run with `cwd: {workspaceRoot}`.

| Target | Command | Cached | Inputs | Outputs |
|--------|---------|--------|--------|---------|
| `lint` | `uvx ruff@0.13.3 check lms` | Yes | `{projectRoot}/**/*.py`, `{workspaceRoot}/pyproject.toml` | -- |
| `format` | `uvx ruff@0.13.3 format lms` | No | -- | -- (writes in place) |
| `format-check` | `uvx ruff@0.13.3 format --check lms` | Yes | `{projectRoot}/**/*.py`, `{workspaceRoot}/pyproject.toml` | -- |
| `test` | `bash scripts/test-backend.sh` | No | -- | -- |

`backend:test` is deliberately uncached: it runs the Frappe server test suite
inside a bench, outside this checkout, configured via the `BENCH_DIR` and `SITE`
environment variables (defaults: `~/frappe-bench`, `lms.localhost`). See
[Run tasks with Nx](../how-to-guides/001-run-tasks-with-nx.md).

## Project: `frontend` (`frontend/project.json`)

The Vue 3 SPA under `frontend/`. All commands run with `cwd: frontend`.

| Target | Command | Cached | Inputs | Outputs |
|--------|---------|--------|--------|---------|
| `serve` | `yarn dev` | No (via `targetDefaults`) | -- | -- |
| `build` | `yarn build` | Yes | `production`, plus `{projectRoot}/index.html`, `vite.config.js`, `tailwind.config.js`, `postcss.config.js`, `tsconfig.json`, `tsconfig.node.json` | `{workspaceRoot}/lms/public/frontend`, `{workspaceRoot}/lms/www/_lms.html` |
| `test` | `yarn test` | Yes | `default`, `{projectRoot}/vitest.config.ts` | -- |
| `lint` | `npx prettier --check src` | Yes | `{projectRoot}/src/**/*`, `.prettierrc.json`, `.prettierignore`, `package.json`, `yarn.lock`, `{workspaceRoot}/.editorconfig` | -- |

Note that `frontend:build` writes into the backend project's tree
(`lms/public/frontend` and `lms/www/_lms.html`) — that is how the SPA is served
by the Frappe site. Declaring these as outputs lets Nx restore them from cache.

`frontend:build` only runs **inside a Frappe bench**: upstream's `yarn build`
pulls `src/socket.js`, which statically imports
`../../../../sites/common_site_config.json` (present only at `bench/sites/`).
A standalone build in this checkout fails to resolve it — assets are built
with `bench build --app lms`, as upstream CI does. The `lint` inputs include
`package.json`/`yarn.lock` (prettier version) and the root `.editorconfig`
(the sole source of tab indentation) because the lint result depends on them.

## `.nxignore`

Paths Nx excludes from project detection and file hashing:

```text
docs/
cypress/
docker/
frappe-ui/
.github/
.claude/
```

Changes under these paths never invalidate target caches and never make a
project "affected".

## Cache location

Nx stores its computation cache in `.nx/` at the workspace root. The directory
is listed in `.gitignore` and must never be committed. Delete it (or run
`npx nx reset`) to force every target to re-execute.

## Related

- [Nx monorepo architecture](../explanation/001-nx-monorepo-architecture.md) — why the workspace is shaped this way
- [Run tasks with Nx](../how-to-guides/001-run-tasks-with-nx.md) — day-to-day commands
- [Task commands](./002-task-commands.md) — the Taskfile wrappers around these targets
