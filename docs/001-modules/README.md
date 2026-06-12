---
title: Module documentation
description: Convention for per-module Diataxis folders under 001-modules/ — when to create one and what goes in it.
type: index
tags: [index, modules, diataxis]
---

# Module documentation

Each substantial feature area gets its own folder here, with the four
Diataxis subsections added as needed:

```
001-modules/<module-name>/
├── tutorials/
├── how-to-guides/
├── reference/
└── explanation/
```

Only create the subsections a module actually needs — an `explanation/`
doc alone is a fine starting point. Files inside follow the repo-wide
convention: numeric-prefixed kebab-case names (`001-grading-flow.md`),
with YAML frontmatter (`title`, `description`, `type`, `tags`).

## Naming

- Folder names are kebab-case, matching how the feature is referred to
  in the codebase: `courses/`, `batches/`, `quizzes/`, `certificates/`.
- One folder per feature area, not per DocType — a module folder covers
  the DocTypes, endpoints, and frontend pages that ship together.

## What goes here

Two kinds of modules earn a folder:

1. **Existing upstream feature areas**, documented as we touch them.
   Upstream `frappe/lms` ships courses, batches, quizzes, assignments,
   certificates, payments, and SCORM playback — document a module here
   once we change or build on it, rather than mirroring upstream docs
   wholesale.
2. **Roadmap modules built by this fork** — the planned AI layer,
   analytics dashboards, standards interop, and engagement features.
   Each gets its folder here *before* implementation starts, opening
   with an ADR-style `explanation/` doc that records the design
   decision.

For what's planned and in what order, see
[Fork strategy and roadmap](../000-overview/explanation/002-fork-strategy-and-roadmap.md).

This directory being sparse is expected: it fills in as modules land,
not ahead of them.
