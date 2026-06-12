# Python Coding Style (Frappe app)

- Python 3.10+ (matches `requires-python` in `pyproject.toml`)
- **Tabs, not spaces** — Frappe convention, enforced by ruff
  (`indent-style = "tab"`, line length 110 in `pyproject.toml`)
- Linter/formatter: **ruff** — `task lint:backend` / `task format:backend`
  (runs the `uvx ruff@<version>` pinned in `lms/project.json`; keep that pin
  in sync with the ruff rev in `.pre-commit-config.yaml`)
- Python tooling runs through **uv** (`uvx ruff`, `uvx pre-commit`) — never
  bare `pip`
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
