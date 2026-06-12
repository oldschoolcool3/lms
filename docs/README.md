---
title: Documentation hub
description: Top-level index using the Diataxis framework — tutorials, how-to guides, reference, explanation.
type: index
tags: [index, diataxis]
---

# Documentation

Organised with the [Diataxis framework](https://diataxis.fr/):

| Type | Purpose | Reader's Mode |
| ---- | ------- | ------------- |
| **Tutorials** | Learn by doing — walk through a complete experience | "I'm learning" |
| **How-to Guides** | Achieve a specific goal — direct, actionable steps | "I need to do X" |
| **Reference** | Look up technical details — commands, config, targets | "I need the facts" |
| **Explanation** | Understand why — design decisions, architecture, tradeoffs | "I want to understand" |

## Structure

```
docs/
├── 000-overview/          Cross-cutting architecture and fork strategy
│   └── explanation/
├── 001-modules/           Per-module documentation (add one dir per module)
├── 002-development/       Development tooling, installation, quality gates
│   ├── explanation/
│   ├── how-to-guides/
│   └── reference/
```

## Start here

- **Setting up a machine?** Follow
  [Install with bench](002-development/how-to-guides/003-install-with-bench.md)
  (or [Install with Docker](002-development/how-to-guides/004-install-with-docker.md)
  for a containerised trial).
- **Why is this repo a fork, and what gets built on it?**
  [Fork strategy and roadmap](000-overview/explanation/002-fork-strategy-and-roadmap.md).
- **How the pieces fit** (Frappe app in `lms/`, Vue 3 SPA in `frontend/`):
  [Architecture](000-overview/explanation/001-architecture.md).
- **Dev tooling**: [002-development/](002-development/) covers the Nx
  monorepo, Taskfile commands, and pre-commit hooks — start with
  [Run tasks with Nx](002-development/how-to-guides/001-run-tasks-with-nx.md)
  and [Set up pre-commit hooks](002-development/how-to-guides/002-set-up-pre-commit-hooks.md).

## Per-module docs (`001-modules/`)

Each functional area you add or substantially extend (a new DocType module in
`lms/`, a new feature surface in `frontend/`) should get its own folder under
`001-modules/` with the Diataxis sub-sections it needs. There is no generator
for these — create the folder by hand when the module's public surface
stabilises, and give roadmap work an explanation doc before code lands. See
[001-modules/README.md](001-modules/README.md) for the convention.

## Contributing

1. **Identify the Diataxis type.** Don't mix types in a single file.
2. **Place it in the right section.** Module docs live under
   `001-modules/<name>/`; tooling docs under `002-development/`.
3. **Naming:** `###-kebab-case-description.md` with a numeric prefix.
4. **Match tone to type** — encouraging for tutorials, direct for how-tos,
   precise for reference, conversational for explanation.
