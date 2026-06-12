---
title: Branching and release model
description: How develop and main relate on our fork, how releases flow, and why the release workflows point at our repo rather than upstream.
type: explanation
tags: [git, branching, release, fork, ci]
---

# Branching and release model

## Our fork is the repo of record

This repository is a fork of [frappe/lms](https://github.com/frappe/lms), but
`oldschoolcool3/lms` is **our canonical repository** — every commit, PR, and
release builds up *our* repo. Upstream `frappe/lms` is a merge *source* only
(see [Fork strategy and roadmap](../../000-overview/explanation/002-fork-strategy-and-roadmap.md)),
never a target. We keep `develop` as our default branch precisely because
upstream's default is also `develop`, which keeps `git pull upstream develop`
clean and 1:1.

## The two branches

| Branch | Role |
|--------|------|
| `develop` | **Default / integration branch — "our main".** Every PR targets it. It is what `nx affected` compares against (`defaultBase` in `nx.json`) and what most CI workflows run on. |
| `main` | **Stable release line.** `develop` is promoted into `main` to cut a release. Pushing to `main` triggers semantic-release (version bump + GitHub release) and the container image build. |

`main` does **not exist yet** on our fork (a GitHub fork copies only the
upstream default branch, `develop`). Create it from `develop` when you are
ready to cut the first release — see "Cutting a release" below.

```
feature branch ──PR──▶ develop ──promote──▶ main ──▶ semantic-release + container image
   (feat/fix/chore)     (default)            (release line)
```

Upstream also carries a `main-hotfix` staging branch and a weekly
`main-hotfix → main` auto-PR (`make_release_pr.yml`). That heavier three-branch
cadence is **inherited but dormant** here — the weekly cron is commented out.
Adopt it later only if you want that flow; the two-branch `develop → main`
model above is the default.

## What runs where

| Workflow | Trigger | Notes |
|----------|---------|-------|
| `linters.yml`, `ci.yml`, `frontend-tests.yml`, `ui-tests.yml` | PRs (and pushes to `develop`/`main`) | Lint, server tests, Vitest, Cypress — the everyday gates |
| `on_release.yml` | push to `main` | semantic-release: analyses commits, bumps `lms/__init__.py`, creates a GitHub release |
| `build.yml` | push to `main`, tags | Builds and publishes the container image to `ghcr.io/oldschoolcool3/lms` |
| `make_release_pr.yml` | manual (`workflow_dispatch`) | Weekly cron disabled until the release cadence is opted into |
| `release_notes.yml` | release published | Regenerates and tidies release notes |

## Pointed at our repo, not upstream

The inherited release/build workflows originally hardcoded the **original
authors' repo**. They have been repointed to ours:

- `build.yml` now builds the image from `github.com/oldschoolcool3/lms`
  (it previously pulled `frappe/lms`, so our released image would not have
  contained our code).
- `make_release_pr.yml` opens its release PR on `oldschoolcool3/lms`
  (was `owner: frappe`).
- `release_notes.yml` reads/writes releases under `/repos/oldschoolcool3/lms/`.
- `on_release.yml` commits the version bump as `github-actions[bot]` rather
  than the upstream bot identity.

## Prerequisites before the first release

1. **Create `main`** from `develop`. Note this is what *activates* the release
   automation — the first push to `main` fires `on_release.yml`
   (semantic-release) and `build.yml` (container publish to GHCR).
2. **Add a `RELEASE_TOKEN` secret** (a PAT with `repo` scope) — `on_release.yml`,
   `make_release_pr.yml`, and `release_notes.yml` use it to push the version-bump
   commit and manage releases. (`GITHUB_TOKEN` works for simple same-repo cases
   but won't trigger downstream workflows on the bump commit.)
3. Decide whether you want the weekly `make_release_pr.yml` cadence; if so,
   re-enable its cron and create a `main-hotfix` branch.

## Cutting a release (two-branch model)

1. Land all work on `develop` via PRs (green CI).
2. Promote `develop` into `main` (a `develop → main` PR, or fast-forward).
3. `on_release.yml` runs semantic-release on `main` and `build.yml` publishes
   the image. Conventional-commit types drive the version bump (`feat` → minor,
   `fix` → patch, `chore`/`docs`/`ci` → no release).
