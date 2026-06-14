---
title: Install with Docker
description: How to run this fork's LMS app locally with Docker, including demo data, backend tests, and teardown.
type: how-to
module: null
tags: [docker, docker-compose, installation, setup, development]
---

# Install with Docker

The Docker setup runs **this fork's** code (mounted from your checkout) on a
local Frappe bench — MariaDB + Redis + the `lms` app on a site at
`lms.localhost`. It is the quickest way to exercise the backend and SPA end to
end without installing a bench natively (see
[Install with bench](003-install-with-bench.md) for the native path).

> It installs the app from your **local checkout**, not the published
> `frappe/lms` — so it always reflects your branch.

**Step 1:** Clone the fork and enter it

```bash
$ git clone https://github.com/oldschoolcool3/lms.git
$ cd lms
```

**Step 2:** Bring up the stack (from the repo root)

```bash
$ docker compose -f docker/docker-compose.yml up -d
$ docker compose -f docker/docker-compose.yml logs -f frappe   # watch provisioning
```

The first run provisions everything — `bench init`, the `lms`/`payments` apps,
the `lms.localhost` site, and the Vue SPA build — so it takes a few minutes.
Wait for `init complete — starting bench` in the logs.

**Step 3:** Open the app at **http://lms.localhost:8000/lms**

Chrome resolves `*.localhost` to `127.0.0.1` automatically; if your browser does
not, map it in `/etc/hosts`:

```
127.0.0.1 lms.localhost
```

Log in for full access (the SPA is otherwise guest-limited):

```
Username: Administrator
Password: admin
```

These credentials and the MariaDB root password (`123`) are for local
development only — never reuse them outside a local test environment.

## Loading demo data

A fresh site has no courses. To populate the sample course, instructor,
learners, lessons, quizzes, and progress:

```bash
$ docker compose -f docker/docker-compose.yml exec frappe \
    bash -lc "cd frappe-bench && bench --site lms.localhost execute lms.demo.demo_data.create_demo_data"
```

To remove it later, open the user menu in the LMS interface and choose **Clear
Demo Data**.

## Running backend tests

The bench-only server tests run inside the container:

```bash
$ docker compose -f docker/docker-compose.yml exec frappe \
    bash -lc "cd frappe-bench && bench --site lms.localhost run-tests --app lms"
```

Scope to a module with `--module lms.lms.test_utils`.

## Stopping and resetting

```bash
$ docker compose -f docker/docker-compose.yml stop    # pause (bench preserved)
$ docker compose -f docker/docker-compose.yml start   # resume — no re-provision
```

`stop`/`start` keep the bench. A full reset (re-provisions on the next `up`):

```bash
$ docker compose -f docker/docker-compose.yml down --volumes
$ docker compose -f docker/docker-compose.yml up -d
```
