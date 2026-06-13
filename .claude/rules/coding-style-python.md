# Python Coding Style (Frappe app)

- Python 3.12+ (matches `requires-python` in `pyproject.toml`)
- **Spaces, not tabs** — 4-space indent, line length 120 (ruff defaults, set in
  `[tool.ruff]` in `pyproject.toml`). This **diverges from upstream's tabs**: the
  backend modernization adopted the org-standard ruff config repo-wide. The
  one-time reformat is isolated in a `.git-blame-ignore-revs` commit so `git
  blame` and upstream merges stay manageable.
- Linter/formatter: **ruff** — `task lint:backend` / `task format:backend` (the
  Nx target runs `uv run --only-group lint ruff`; ruff is pinned in
  `[dependency-groups]` in `pyproject.toml`, and the `.pre-commit-config.yaml`
  ruff `rev` must stay in sync with that pin)
- Python tooling runs through **uv** (`uv run` for ruff, `uvx pre-commit`) —
  never bare `pip`
- Modern typing where it doesn't fight the framework: `str | None`, not
  `Optional[str]`
- Use Frappe primitives, not workarounds:
  - ORM: `frappe.get_doc`, `frappe.get_all`, `frappe.db.get_value`,
    `frappe.qb` — no raw SQL unless parameterized and justified
  - Errors to users: `frappe.throw(_("message"))` — never bare exceptions for
    user-facing failures
  - Logging: `frappe.logger()` / `frappe.log_error` — no `print()`
  - Background work: `frappe.enqueue` + scheduler entries in `hooks.py`
- All user-facing strings wrapped in `_()` for translation
- DocType controllers stay thin; shared logic lives in `lms/lms/utils.py` or a
  focused module — not duplicated across controllers
- New endpoints: `@frappe.whitelist()` with an explicit permission check (see
  security.md)
