# Testing

- **Backend**: Frappe test runner — tests live next to each DocType
  (`test_<name>.py`) and in `lms/lms/test_*.py`, using `UnitTestCase` /
  `IntegrationTestCase` from `frappe.tests` (shared fixtures via
  `BaseTestUtils` in `lms/lms/test_helpers.py`). They need a bench +
  site: `task test:backend` (env: `BENCH_DIR`, `SITE` — see
  `scripts/test-backend.sh`). CI runs them in `.github/workflows/ci.yml`.
- **Frontend**: Vitest + Vue Test Utils (jsdom) — tests in
  `frontend/src/tests/`. Run `task test:frontend` (no bench needed).
- **End-to-end**: Cypress at the repo root (`cypress/`) against a running
  site — `task test:e2e`.
- **All cached targets**: `npx nx run-many -t test` (frontend) — backend test
  target is uncached because it depends on external bench state.
- New backend features ship with DocType tests; new frontend logic
  (composables, stores, non-trivial components) ships with Vitest specs.
- Don't mock Frappe in backend tests — the framework's test runner provides a
  real site context; use `frappe.get_doc(...).insert()` fixtures and clean up.
