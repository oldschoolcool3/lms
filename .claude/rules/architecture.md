# Architecture

A Frappe Framework app (Python, MariaDB) with a Vue 3 single-page app frontend.
The Frappe site serves the SPA at `/lms`; everything else (auth, ORM, jobs,
realtime, email) comes from the framework.

## Backend (`lms/`)

- **DocTypes** (`lms/lms/doctype/<name>/`) are the data model. Each directory
  owns `<name>.json` (schema), `<name>.py` (controller), and usually
  `test_<name>.py`. Schema changes happen by editing the JSON via the Frappe
  desk or carefully by hand — never with manual DDL; `bench migrate` applies
  them.
- **API surface**: methods decorated with `@frappe.whitelist()` — concentrated
  in `lms/lms/api.py`, `lms/lms/utils.py`, and DocType controllers. These are
  the only entry points the frontend may call.
- **`lms/hooks.py`** is the app's registry: scheduled jobs, doc events,
  overrides, website routes, fixtures. If a behavior seems to come from
  nowhere, look here first.
- **Patches** (`lms/patches/` + `lms/patches.txt`) are one-off data migrations,
  run in order by `bench migrate`. New patch → new line in `patches.txt`.
- **Portal pages** (`lms/www/`, `lms/templates/`) are server-rendered Jinja —
  legacy surface; new UI belongs in the SPA.

## Frontend (`frontend/`)

- Vue 3 + Vite + Tailwind + [frappe-ui](https://github.com/frappe/frappe-ui)
  (also vendored as the `frappe-ui/` git submodule for development).
- `src/pages/` (routed views, see `src/router.js`), `src/components/`,
  `src/stores/` (Pinia), `src/utils/`, `src/types/` (TypeScript types for
  DocTypes and API), `src/tests/` (Vitest).
- Data access goes through frappe-ui's `createResource`/`createListResource`
  against whitelisted methods — no hand-rolled fetch layers.
- Realtime: `src/socket.js` (socket.io against the Frappe site).
- Production build lands in `lms/public/frontend` with the HTML entry copied
  to `lms/www/_lms.html` (see `frontend/package.json` build script).

## Tooling seams

- **Nx** orchestrates lint/test/build with caching (`nx.json`,
  `frontend/project.json`, `lms/project.json`). **Taskfile** is the
  human-facing entry point (`task --list`).
- Server code cannot run from this checkout alone — it needs a bench with a
  site. Anything that imports `frappe` runs inside the bench, not in a repo
  venv.

## Fork posture

This is a fork of `frappe/lms`. Differentiating work (AI layer, analytics,
interop) should attach via new DocTypes, new whitelisted methods, and new
frontend pages/components — not by rewriting upstream modules — so upstream
merges stay cheap. See `docs/000-overview/explanation/002-fork-strategy-and-roadmap.md`.
