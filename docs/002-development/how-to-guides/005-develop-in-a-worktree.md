---
title: Develop in a worktree against a shared bench
description: Run an isolated frontend dev server from a git worktree, proxied to one shared Docker bench, so parallel sessions test independently without rebuilding.
type: how-to
module: null
tags: [worktree, docker, frontend, vite, dev, parallel]
---

# Develop in a worktree against a shared bench

Multiple sessions/agents work in parallel git worktrees
(`.claude/worktrees/<name>/`, see
[Parallel session hygiene](../../../.claude/rules/worktree-sessions.md)). They
don't each need their own bench: run **one shared Docker bench** as the backend
(see [Install with Docker](004-install-with-docker.md)) and a **per-worktree
Vite dev server** for the frontend. Each dev server serves *its* worktree's code
with HMR (no build) and proxies API/asset/auth requests to the shared bench. Two
worktrees editing the frontend test independently, on different ports, against
the same backend — no rebuilds, no collisions.

## One-time: the shared bench

Bring it up once (any checkout works — it serves `lms.localhost:8000`):

```bash
docker compose -f docker/docker-compose.yml up -d
```

## Per worktree: the dev server

From **your** worktree:

```bash
cd frontend
yarn install          # once per worktree (yarn's global cache makes repeats fast)
yarn dev              # serves on :8080, or the next free port (8081, 8082, …)
```

Open the URL Vite prints, **but on the `lms.localhost` host, not `localhost`**:

```
http://lms.localhost:8080/lms      # (use the port Vite actually chose)
```

This matters: the Vite proxy forwards to the backend **by Host header**
(`http://<host>:8000`), so the host must be `lms.localhost` for the bench to
resolve the site and for the auth cookie to line up. (`*.localhost` resolves to
loopback automatically in browsers and on most Linux resolvers.) Log in at
`/login` as `Administrator` / `admin`.

> **Authenticated views work because the dev bench disables CSRF.** The Vite dev
> server serves a raw `index.html` with no Frappe boot data, so it carries no
> CSRF token — without help, every logged-in API call would `400`
> (`CSRFTokenError`). The Docker dev bench sets `ignore_csrf` (dev-only; see
> `docker/init.sh`), so Settings, Coupons, the profile editor, etc. are testable
> through a worktree dev server. (Guest views never needed CSRF.)

Edit files → HMR updates instantly. **No `bench build` needed** — that full Vue
build only runs when baking assets into the bench (`bench build --app lms`).

## Two (or more) worktrees at once

Just run `yarn dev` in each. Vite serves on 8080, and when that's taken it
auto-increments (8081, 8082, …) — while every dev server still proxies to the
**same** bench on `:8000`. So worktree A is `lms.localhost:8080`, worktree B is
`lms.localhost:8081`, both backed by the one bench. Independent, no extra config.

## Backend changes

The shared bench runs the **committed** backend (`bench get-app` cloned it at
provision time). The frontend dev loop above does **not** pick up a worktree's
uncommitted *Python* changes — they live in the bench's `apps/lms`. Options:

- **Run unit tests** against the bench (they use an isolated `test_` DB):
  `docker exec lms-dev-frappe-1 bash -lc 'cd ~/frappe-bench && bench --site lms.localhost run-tests --app lms'`.
- **Test a worktree's backend changes live:** sync them in —
  `cd ~/frappe-bench/apps/lms && git fetch /workspace/lms-src && git reset --hard <ref>`
  (then restart the bench). One bench = one `apps/lms`, so two **simultaneous**
  different backend versions need a **second bench** (a separate compose project
  name + ports); the frontend dev server is the only part that's cheaply
  per-worktree.

## Knobs

- **`FRAPPE_WEB_SERVER_PORT`** — point a dev server at a different backend port
  (e.g. a second bench): `FRAPPE_WEB_SERVER_PORT=8001 yarn dev`. Default `8000`
  is the shared bench.
- **socket.js** statically imports the bench's `common_site_config.json`, which
  a worktree lacks; `frontend/vite.config.js` aliases it to
  `frontend/dev/common_site_config.stub.json` only when no bench config is
  present, so the dev server loads. Realtime (socket.io) is best-effort in this
  mode; page rendering and API calls work regardless.
