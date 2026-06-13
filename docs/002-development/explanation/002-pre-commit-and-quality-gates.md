---
title: Pre-commit Hooks and Quality Gates
description: How pre-commit hooks, Nx-cached lint targets, and CI workflows layer together to keep the fork clean without mass-rewriting upstream code.
type: explanation
tags: [pre-commit, linting, quality, hooks, ci, development]
---

# Pre-commit Hooks and Quality Gates

## Defense in depth

Quality is enforced at four levels, each catching what the previous one missed:

1. **Editor** -- ruff and prettier both read checked-in config (`pyproject.toml` for ruff; the root `.prettierrc.json` for repo-wide files and `frontend/.prettierrc.json` for the SPA), so editor integrations agree with every later gate.
2. **Pre-commit hooks** -- `.pre-commit-config.yaml` runs on staged files before anything enters git history. Install once with `uvx pre-commit install` (see [Set up pre-commit hooks](../how-to-guides/002-set-up-pre-commit-hooks.md)).
3. **Nx caching** -- `task lint` runs the `backend:lint` (ruff) and `frontend:lint` (ESLint flat config + prettier `--check`) targets through Nx, and `task typecheck` runs `frontend:typecheck` (vue-tsc), so unchanged projects return cached results instantly (see [Nx monorepo architecture](001-nx-monorepo-architecture.md)).
4. **CI** -- GitHub Actions workflows enforce the lint/test gates described here. `.github/workflows/nx.yml` is the primary lint/test gate: it runs `nx affected -t lint typecheck test` (backend ruff, frontend ESLint/Prettier, `vue-tsc`, and Vitest) against the `nx-set-shas` base, so only affected projects run and Nx caches the rest. `linters.yml` re-runs the full pre-commit suite, the frappe semgrep ruleset, and a Tailwind RTL semgrep scan (`.github/semgrep/tailwind-rtl.yml`); `ci.yml` runs server tests inside a provisioned Frappe bench (the backend `test` target is bench-coupled, so the Nx job excludes it). Pull requests are additionally gated by `ui-tests.yml` (Cypress UI tests) and `semantic.yml` (PR-title validation).

A developer who skips the local hooks still hits the same checks in `linters.yml` -- pre-commit is a convenience for fast feedback, not the only enforcement point.

## The hook pipeline

`default_install_hook_types: [pre-commit, commit-msg]` means installing once wires up both the staged-file hooks and the commit-message check.

### Standard hooks (`pre-commit-hooks`)

Whitespace and syntax checks (`trailing-whitespace`, `end-of-file-fixer`, `check-json`, `check-yaml`, `check-toml`, `check-ast`, `debug-statements`), safety checks (`detect-private-key`, `check-added-large-files` at a 1 MB threshold, `check-merge-conflict`, `check-case-conflict`), and branch protection. Notable scoping:

- `end-of-file-fixer` skips minified assets and `lms/public/js/lib/` -- an upstream `frappe/lms` vendored-library path not currently in this tree, excluded defensively in case a future merge reintroduces it.
- `check-json` skips `tsconfig*.json` -- those are JSONC; the TypeScript compiler validates them.
- `no-commit-to-branch` blocks direct commits to **both `main` and `develop`** -- all work lands via feature branches and pull requests.

### Secret scanning (`gitleaks`)

Scans staged content for credentials. It reads `.gitleaks.toml` from the repo root, which extends the upstream default ruleset (`useDefault = true`) and allowlists paths where secret-shaped strings are expected but harmless: `docs/`, `.claude/`, `cypress/fixtures/`, `lms/demo/`, `lms/fixtures/`, Python and JS test files, and the yarn lockfiles. The philosophy: allowlist by path, never by disabling rules, so a real key pasted into application code is still caught.

Note the division of labor: the pre-commit hook scans only the **staged diff** (fast, catches secrets at commit time), which is a no-op on a clean CI checkout. CI coverage comes from the dedicated `gitleaks` job in `linters.yml`, which scans the full working tree (`gitleaks dir`) with the same `.gitleaks.toml` and a version pinned to match the hook rev.

### Python (`ruff`)

Two hooks from `ruff-pre-commit`: `ruff` (lint with `--fix --exit-non-zero-on-fix`) and `ruff-format`. Configuration lives in `pyproject.toml` -- line length 120, 4-space indentation, the org-standard ruff style the backend modernization adopted (a deliberate divergence from upstream's tabs, isolated in a `.git-blame-ignore-revs` reformat commit). The pinned hook `rev` must match the ruff version in `pyproject.toml` `[dependency-groups]`, which the Nx targets (`uv run --only-group lint ruff`) and CI resolve too, so pre-commit, `task lint:backend`, and CI can never disagree.

### JavaScript and Vue (`prettier`)

Uses the `rbubley/mirrors-prettier` mirror (the official mirror is archived) to get prettier 3. `trailingComma: "es5"` is pinned in both the root `.prettierrc.json` (which files outside `frontend/` resolve when the hook runs repo-wide) and `frontend/.prettierrc.json` (which adds the SPA's `semi: false` and `singleQuote: true`, used by `frontend:lint` and editor integrations) because prettier 3 changed the default to `"all"` -- accepting the new default would mass-reformat upstream-authored files and poison every future merge from `frappe/lms`. The hook excludes built bundles (`lms/public/dist/`), boilerplate, and upstream paths that may reappear on merges from `frappe/lms` (vendored `lms/public/js/lib/`, Jinja-bearing `lms/templates/includes/` and `lms/www/website_script.js` -- none currently present in this tree).

### Legacy desk JS (`eslint`)

ESLint runs only on plain JavaScript (`types_or: [javascript]`) with `--quiet`, using the permissive root `.eslintrc`. It exists for the legacy Frappe desk scripts; the Vue SPA carries its own, much stricter ESLint (see below), and the exclusions (dist bundles, `cypress/`, vendored libs, Jinja templates, boilerplate) mirror prettier's. The two never overlap -- ESLint 8 here reads `.eslintrc` and ignores the SPA's flat `eslint.config.js`.

## SPA lint and type-check (`frontend:lint`, `frontend:typecheck`)

The Vue SPA (`frontend/`) is gated separately from the pre-commit suite, because it needs the modern toolchain (ESLint 9 flat config, typescript-eslint, `vue-tsc`) and its own dependency tree:

- **`frontend:lint`** runs `eslint .` (flat config in `frontend/eslint.config.js`: typescript-eslint + eslint-plugin-vue, formatting deferred to prettier) followed by `prettier --check src`.
- **`frontend:typecheck`** runs `vue-tsc --noEmit` over the whole program. Because `frappe-ui` ships its types as raw Vue source, it is treated as an untyped boundary (`frontend/src/types/frappe-ui-shim.d.ts`) so the checker doesn't descend into a dependency it can't fix.

Both gates were **ratcheted** rather than retrofitted. The SPA predated any type-checking, so it carried a backlog of pre-existing findings in upstream-derived components; fixing them all at once would have been exactly the upstream-churning diff this fork avoids. So they were burned down incrementally (Track A, PR-A3), and that burn-down is now essentially complete:

- `vue-tsc` output is diffed against `frontend/typecheck-baseline.json` by `scripts/frontend-typecheck.mjs`, failing only on **new** type errors. **The baseline is now empty (`total: 0`)** -- `vue-tsc --noEmit` passes with zero errors across the whole SPA. The wrapper stays in place (now enforcing zero) and can be simplified to a plain `vue-tsc --noEmit` whenever convenient.
- ESLint grandfathers existing violations in `frontend/eslint-suppressions.json` (ESLint's native bulk-suppressions) and fails only on **new** ones. This is down from ~480 to a small residue: only `vue/no-mutating-props` (plus one coupled `vue/no-dupe-keys`) in four form components that edit a passed-in reactive object in place. That is an intentional upstream pattern whose removal needs a deliberate prop -> `v-model` refactor -- and the Coupons form is payment-sensitive -- so it is tracked as a separate, reviewed change rather than forced.

With the JS->TS migration complete -- every `frontend/src/**/*.js` is now `.ts` except `socket.js` (which statically imports a bench-only `sites/common_site_config.json`), and every SFC uses `<script setup lang="ts">` -- **`vue/block-lang` is enabled (`error`)** so new SFCs must be TypeScript. Regenerate the ledgers after a change with `cd frontend && eslint . --prune-suppressions` / `yarn typecheck:update`.

### YAML and Markdown (`yamllint`, `markdownlint-cli2`)

`yamllint` uses `.yamllint.yaml`, which sets `truthy: check-keys: true` to catch YAML's `on`/`yes`/`no` booleans -- and therefore excludes `.github/workflows/`, where the `on:` trigger key is legitimate. `markdownlint-cli2` excludes `.claude/` -- AI rule and command files are not user-facing documentation.

### Commit messages (`commitlint`)

Runs at the `commit-msg` stage against `commitlint.config.js` (conventional commits, with a project-specific `deprecate` type). The `linters.yml` workflow re-validates every commit title in a pull request, so squash-merge titles stay release-note-clean.

### Local hook: `block-merge-artifacts`

A repo-local system hook that fails the commit if any tracked file (Markdown excluded) contains unresolved conflict markers, or if `*.rej` patch-reject files exist anywhere outside `.git/` and `node_modules/`. This is fork insurance: upstream merges are routine here, and a half-resolved merge must never land silently.

## Fork hygiene as a design constraint

Every hook above is scoped deliberately. This repository tracks upstream `frappe/lms` (see [Fork strategy and roadmap](../../000-overview/explanation/002-fork-strategy-and-roadmap.md)), so a hook that reformatted vendored libraries, built assets, or upstream-styled code would create permanent merge conflicts. The rule of thumb when adding hooks: exclude anything upstream owns, pin formatter behavior to what upstream already produces, and let new code carry the stricter standards.

## Running the whole gate locally

```bash
task precommit   # uvx pre-commit run --all-files
task lint        # Nx-cached ruff + (ESLint + prettier) across both projects
task typecheck   # Nx-cached vue-tsc over the SPA (ratcheted)
```

See [Task command reference](../reference/002-task-commands.md) for the full command list and [Run tasks with Nx](../how-to-guides/001-run-tasks-with-nx.md) for affected-only runs.
