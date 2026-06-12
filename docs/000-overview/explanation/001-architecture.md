---
title: Architecture
description: How the LMS is put together — a Frappe Framework app providing the data model and API, with a Vue 3 single-page app served by the Frappe site at /lms.
type: explanation
tags: [architecture, frappe, doctype, vue, spa, frappe-ui, realtime]
---

# Architecture

This repository is two halves of one application: a Frappe Framework app
(Python, in `lms/`) that owns the data model, business logic, and API, and a
Vue 3 single-page app (in `frontend/`) that owns nearly all of the user
interface. The Frappe site serves the built SPA at `/lms`.

## What a Frappe app is

Frappe is a batteries-included framework: authentication, the ORM, permissions,
background jobs, scheduled tasks, realtime (socket.io), and email all come from
the framework, not from this codebase. The app contributes DocTypes, controller
logic, and whitelisted API methods on top.

The practical consequence: the backend cannot run from this checkout alone. It
is installed as an app on a [bench](https://docs.frappe.io/framework/user/en/bench)
site, and anything that imports `frappe` — including server tests — executes
inside that bench, not in a repo-local venv. See
[../../002-development/how-to-guides/003-install-with-bench.md](../../002-development/how-to-guides/003-install-with-bench.md).

## DocTypes: the data model

Each DocType lives in its own directory under `lms/lms/doctype/<name>/`.
Take `lms_quiz` as a representative example:

- **`lms_quiz.json`** — the schema. Declares fields with Frappe fieldtypes:
  `title` is a required `Data` field, `max_attempts` an `Int`, `questions` a
  `Table` of child rows (`LMS Quiz Question`), and `lesson` a `Link` to
  `Course Lesson` with `course` fetched from it. Frappe generates the MariaDB
  table from this JSON; schema changes mean editing the JSON (via the Frappe
  desk, or carefully by hand) and running `bench migrate` — never manual DDL.
- **`lms_quiz.py`** — the controller. `class LMSQuiz(Document)` hooks the
  document lifecycle: its `validate()` rejects duplicate questions, computes
  `total_marks`, and enforces open-ended-question rules. The same module also
  defines `@frappe.whitelist()` functions like `submit_quiz` and
  `check_answer` — the HTTP-callable API for this DocType.
- **`test_lms_quiz.py`** — server tests (`unittest`-style, run by the Frappe
  test runner inside a bench).

A `lms_quiz.js` file customizes the desk (admin) form, but most DocType
directories are just that JSON + controller + test trio. One-off data
migrations live in `lms/patches/`, ordered by `lms/patches.txt`.

## hooks.py: the app registry

`lms/hooks.py` is where the app plugs into the framework. If a behavior seems
to come from nowhere, look here first. It registers, among other things:

- **`doc_events`** — e.g. every document's `on_change` runs badge processing,
  and `Notification Log` changes trigger `publish_notifications`.
- **`scheduler_events`** — hourly course statistics, daily payment and batch
  reminders, and similar background jobs.
- **`website_route_rules`** — the rules that map `/lms` and `/lms/<path>` to
  the SPA entry (below).
- **`fixtures`** and **`override_doctype_class`** — seed records and a small
  number of framework overrides.

## How the SPA is served

The frontend's build script (`frontend/package.json`) runs
`vite build --base=/assets/lms/frontend/`, landing the bundle in
`lms/public/frontend`, then copies the generated `index.html` to
`lms/www/_lms.html`. The companion `lms/www/_lms.py` injects boot data
(session, settings) into that page. `website_route_rules` in `hooks.py` route
`/lms` and everything under it to `_lms`, so the Frappe site serves the SPA
and Vue Router takes over client-side.

## Frontend data flow

The SPA never hand-rolls a fetch layer. Data access goes through
[frappe-ui](https://github.com/frappe/frappe-ui)'s `createResource` and
`createListResource`, whose `url` is the dotted Python path of a whitelisted
method — for example, `frontend/src/components/Quiz.vue` submits answers via
`lms.lms.doctype.lms_quiz.lms_quiz.submit_quiz`. Methods decorated with
`@frappe.whitelist()` (concentrated in `lms/lms/api.py`, `lms/lms/utils.py`,
and DocType controllers) are the only entry points the frontend may call;
the framework handles sessions, CSRF, and permission checks around them.

## Realtime

`frontend/src/socket.js` opens a socket.io connection to the Frappe site
(using the bench's configured socketio port). The backend publishes through
the framework — for instance, the `Notification Log` doc event in `hooks.py`
pushes notifications to connected clients without any polling.

## The legacy server-rendered surface

`lms/www/` and `lms/templates/` are server-rendered Jinja pages (certificates,
sign-up, email templates) that predate the SPA. They still work and some are
load-bearing — `certificate.html` is the public certificate page — but they
are a legacy surface: new UI belongs in the SPA.

## Where this fork is heading

This codebase is a fork of `frappe/lms`. New differentiating work attaches via
new DocTypes, new whitelisted methods, and new frontend pages — not rewrites
of upstream modules — so upstream merges stay cheap. The reasoning and roadmap
live in [002-fork-strategy-and-roadmap.md](002-fork-strategy-and-roadmap.md).
