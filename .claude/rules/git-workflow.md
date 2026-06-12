# Git Workflow

- Default branch: `develop` (PRs target it; `main` is the release branch —
  releases flow via semantic-release / Mergify, see `.releaserc` and
  `.mergify.yml`)
- Conventional commits, enforced by commitlint (`commitlint.config.js`):
  `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`,
  `style`, `revert`, `deprecate`
- Atomic commits — one logical change per commit
- PR branches: `feat/<name>`, `fix/<name>`, `chore/<name>`
- No force-push to `main` or `develop`; no direct commits to either (enforced
  by pre-commit `no-commit-to-branch`)
- Use `git mv` (never plain `mv`) when moving tracked files — preserves history
- Run `task lint` and let pre-commit pass before pushing
- Keep upstream mergeable: no mass reformatting or drive-by refactors of
  `frappe/lms` code (see working-posture.md, "Surgical changes")
