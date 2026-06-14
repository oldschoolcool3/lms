---
title: Fork strategy and roadmap
description: Why this is an independent hard fork of frappe/lms rather than a rebuild or a tracked soft-fork, and where future differentiating features attach.
type: explanation
tags: [fork, roadmap, strategy, ai]
---

# Fork strategy and roadmap

## The decision: fork, don't rebuild

This repository is a fork of [frappe/lms](https://github.com/frappe/lms). A
file-level assessment (June 2026) concluded the upstream codebase is modern and
maintainable, not legacy: ~60 well-modeled DocTypes encoding years of solved
edge cases (enrollment states, batch/cohort logic, certificate evaluation,
payments, coupons, permissions), a typed Vue 3 frontend with Vitest coverage,
websockets, SCORM playback, i18n/RTL, and a payments integration. Rebuilding
that from scratch is months of undifferentiated work.

The upstream maintainers ship production features on this codebase with
AI-assisted development, which is direct evidence the codebase is amenable to
it. The one real cost of forking is commitment to the Frappe Framework's
opinionated stack (DocType/ORM system, bench tooling) — accepted deliberately.

## Fork posture: independent hard fork

**As of June 2026 this is a hard fork** — we no longer track or merge
`frappe/lms` wholesale, and we optimize for our own code quality over
merge-compatibility. The earlier "soft fork" hygiene (no reformatting/refactoring
of upstream code, attach-only-via-new-DocTypes) **no longer applies**:

- Reformatting, refactoring, **retyping**, and removing dead/legacy upstream
  surfaces are all sanctioned — do them as focused, reviewable changes.
- Differentiating work still *often* attaches cleanly via new DocTypes, new
  whitelisted methods, and new frontend pages/components, but rewriting upstream
  modules is fair game when it improves the codebase.
- Repo-level tooling this fork added (Nx, Taskfile, `.claude/`, `docs/`, stricter
  pre-commit, ratcheted type-checks) is ours to evolve freely.

**The one obligation cutting the cord creates:** we own app security
maintenance. The Frappe *framework* is a separate bench-installed dependency and
still updates normally, but `frappe/lms` (the app) no longer feeds us fixes — so
**watch upstream for security advisories and manually cherry-pick critical ones**
(e.g. the SCORM/media path-traversal hardening). See `.claude/rules/security.md`.

## What upstream already gives us (don't rebuild these)

Several "gaps" visible in the UI are presentation gaps, not data gaps:

- **Video engagement is already captured** per learner
  (`lms_video_watch_duration` DocType) — the thin Statistics page is a
  dashboard problem.
- **Gamification primitives exist in the schema** (`lms_badge`,
  `lms_badge_assignment`) but are barely surfaced in the UI.
- **Programming exercises have real grading infrastructure**
  (`lms_test_case`, `lms_test_case_submission`,
  `lms_programming_exercise_submission`).
- **SCORM import/playback exists** (see `SCORMChapter.vue` and the hardened
  SCORM media serving) — xAPI/cmi5 do not.
- Payments, coupons, billing, and data import are built
  (`lms_payment`, `lms_coupon`, `Billing.vue`, `DataImport.vue`).

## Roadmap (in priority order — none of this is built yet)

### 1. AI layer

There is no LLM/embedding integration anywhere in upstream. Planned surface,
in rough build order:

| Capability | Attaches to |
|------------|-------------|
| RAG tutor / Q&A grounded in course content | `course_lesson` content + a new vector index; new whitelisted query methods |
| AI authoring assist (draft lessons, outlines) | course editor frontend + new generation endpoints |
| Auto-generated quizzes from lesson content | `course_lesson` → `lms_quiz` / `lms_question` |
| AI grading of open-ended quiz answers | `lms_quiz_submission` |
| AI feedback on code submissions | `lms_programming_exercise_submission`, `lms_test_case_submission` |
| Semantic search (current search is title-based) | embeddings over lessons/courses |

Implementation posture: a new `ai` module inside this app (new DocTypes for
prompts/runs/feedback, new whitelisted endpoints), with model calls behind a
thin provider abstraction. These are *new services beside* the LMS, not
rewrites of it.

### 2. Real analytics

The data already exists (`lms_course_progress`, `lms_video_watch_duration`,
quiz/assignment submissions, enrollments). Build cohort analysis, per-learner
progress, drop-off/funnel views, and at-risk-learner flagging as new dashboard
pages over new read-only reporting endpoints.

### 3. Standards interop

xAPI/cmi5 emission and import, building on the existing SCORM support —
matters mainly for organizational/L&D buyers.

### 4. Engagement surfacing

Streaks/leaderboards/notifications built on the existing badge DocTypes rather
than a new gamification engine.

## Prerequisites this repo has already done

- Nx + Taskfile + pre-commit + `.claude/` agent guidance (this modernization)
- `docs/` Diataxis structure for documenting modules as they land

## Explicitly out of scope for now

No AI feature scaffolding exists yet — this document is the prep. When work
starts on a roadmap item, give it a module folder under `docs/001-modules/`
and an ADR-style explanation doc here first.
