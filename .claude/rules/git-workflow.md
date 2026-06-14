# Git Workflow

- **`develop` is our canonical line / default branch** — all PRs target it
  (this is "our main"; see `docs/002-development/explanation/003-branching-and-release-model.md`).
- **`main` is the stable release line** — `develop` promotes into it, and
  `on_release.yml` runs semantic-release there (version bump + GitHub release +
  container build). `main` does not exist yet; create it when ready to cut the
  first release.
- Releases and the container image build from **our fork** (`oldschoolcool3/lms`),
  never upstream `frappe/lms` — the release workflows were repointed for this.
- Conventional commits, enforced by commitlint (`commitlint.config.js`):
  `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`,
  `style`, `revert`, `deprecate`
- Atomic commits — one logical change per commit
- PR branches: `feat/<name>`, `fix/<name>`, `chore/<name>`
- No force-push to `main` or `develop`; no direct commits to either (enforced
  by pre-commit `no-commit-to-branch`)
- Use `git mv` (never plain `mv`) when moving tracked files — preserves history
- Run `task lint` and let pre-commit pass before pushing
- **Hard fork — we don't track upstream.** Reformatting, refactoring, retyping,
  and removing legacy `frappe/lms` code are all fair game (optimize for our
  quality). Keep diffs surgical and commits atomic for *review/bisect* clarity,
  not merge-avoidance (see working-posture.md, "Surgical changes"). Still
  cherry-pick critical upstream *security* fixes (see security.md)
