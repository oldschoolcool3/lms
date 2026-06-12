---
title: Set up pre-commit hooks
description: How to install the git hooks, run them against the whole tree, and fix the most common failures.
type: how-to
tags: [pre-commit, hooks, linting, commitlint, setup]
---

# Set up pre-commit hooks

Local commit-time linting and formatting in this repo runs through
[pre-commit](https://pre-commit.com/), configured in `.pre-commit-config.yaml`
at the repo root. (For cached full-tree lint runs outside the commit path, use
the Nx-backed `task lint`.) You invoke pre-commit through `uvx` (bundled with
[uv](https://docs.astral.sh/uv/)), so there is nothing to pip-install. One hook
— gitleaks — builds from Go source on first run; pre-commit downloads a Go
toolchain automatically if you don't have one, so the first run is slower but
no manual Go install is needed.

For the reasoning behind each hook, see
[Pre-commit and quality gates](../explanation/002-pre-commit-and-quality-gates.md).

## Install the hooks

```bash
uvx pre-commit install
```

Because the config sets `default_install_hook_types: [pre-commit, commit-msg]`,
this single command registers two hooks: the `pre-commit` stage (linters,
formatters, secret scanning) and the `commit-msg` stage (commitlint).

## Run against the whole tree

After installing, or any time you want a full sweep:

```bash
uvx pre-commit run --all-files
```

The same command is wrapped as a task:

```bash
task precommit
```

The first run is slow while pre-commit builds its hook environments; later runs
use the cache.

## What happens on commit

On `git commit`, the pre-commit stage runs against your staged files: whitespace
and file-format checks, gitleaks secret scanning, ruff (lint + format) for
Python, prettier for JavaScript/Vue and eslint for plain JavaScript, yamllint, markdownlint, a local
check for unresolved merge markers and `.rej` files, and `no-commit-to-branch`,
which blocks direct commits to `main` and `develop`. Then the commit-msg stage
runs commitlint on your message. CI (`.github/workflows/linters.yml`) runs the
same hooks, so anything you skip locally fails there instead.

## Fix common failures

### ruff or prettier modified files

ruff runs with `--fix --exit-non-zero-on-fix`, and prettier rewrites files in
place. Both fail the commit so you can review what changed. Re-stage and retry:

```bash
git add -u
git commit
```

### commitlint rejected your message

Messages must follow Conventional Commits: `type(scope): subject`, with a
lower-case type and a non-empty subject. The allowed types (from
`commitlint.config.js`) are `build`, `chore`, `ci`, `docs`, `feat`, `fix`,
`perf`, `refactor`, `revert`, `style`, `test`, and `deprecate`.

```bash
git commit -m "fix(lesson): handle missing video duration"
```

### no-commit-to-branch blocked you

You are committing directly to `main` or `develop`. Create a branch first:

```bash
git checkout -b fix/your-change
```

## Skip a hook in an emergency

If a hook misfires and is blocking urgent work, skip it by id:

```bash
SKIP=gitleaks git commit -m "fix(api): ..."
```

Avoid this except as a last resort: CI runs the full hook set on every pull
request (re-triggered on each push to the PR branch), so a skipped failure
resurfaces as a red `linters` check on your pull request.
Prefer fixing the underlying issue or the hook configuration.
