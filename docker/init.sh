#!/bin/bash
# Provision a local Frappe bench running THIS fork's lms app (from the mounted
# checkout at /workspace/lms-src), then start it. Re-runs are idempotent: an
# existing bench is just started.
set -euo pipefail

say() { echo ">>>>> [$(date +%H:%M:%S)] $*"; }
say "LMS dev bench init starting"

# Resume fast if the bench already exists (survives stop/start).
if [ -d /home/frappe/frappe-bench/apps/frappe ]; then
  say "Existing bench detected — starting it (skip provisioning)"
  cd /home/frappe/frappe-bench
  exec bench start
fi

# cairocffi (certificate rendering) dlopens libcairo at runtime; the base image
# ships frappe's deps but not this one. lxml/libxml2 already come with frappe.
say "Installing runtime system libs (libcairo for cairocffi)"
sudo apt-get update -qq && sudo apt-get install -y -qq \
  libcairo2 libpango-1.0-0 libpangocairo-1.0-0 || say "WARN: apt step failed (continuing)"

# Node: the image leaves NODE_VERSION_DEVELOP empty, so put a concrete node on PATH.
export NVM_DIR="${NVM_DIR:-/home/frappe/.nvm}"
# shellcheck disable=SC1091
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
# frappe's develop branch (what bench init clones) requires node >=24; CI uses 24 too.
nvm use 24 >/dev/null 2>&1 || nvm use node >/dev/null 2>&1 || true
say "node $(node --version 2>&1) | python $(python3 --version 2>&1) | bench $(bench --version 2>&1)"

cd /home/frappe
say "[1/6] bench init (frappe framework)"
bench init --skip-redis-config-generation --python "$(command -v python3)" frappe-bench
cd frappe-bench

say "[2/6] point bench at the service containers"
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379
sed -i '/redis/d;/watch/d' ./Procfile

say "[3/6] get apps — payments (upstream) + lms (OUR fork, from the mount)"
bench get-app payments
git config --global --add safe.directory /workspace/lms-src
bench get-app /workspace/lms-src

say "[4/6] create site lms.localhost"
bench new-site lms.localhost \
  --force \
  --mariadb-root-password 123 \
  --admin-password admin \
  --no-mariadb-socket

say "[5/6] install apps + dev config"
bench --site lms.localhost install-app payments
bench --site lms.localhost install-app lms
bench --site lms.localhost set-config developer_mode 1
bench --site lms.localhost set-config mute_emails 1
# Dev-only: the vite dev server serves a raw index.html with no Frappe boot data,
# so it has no CSRF token and every authenticated API call 400s (CSRFTokenError).
# Disabling CSRF on this throwaway local site lets logged-in views (Settings,
# Coupons, …) be tested through a worktree dev server. NEVER for a real site.
bench --site lms.localhost set-config ignore_csrf 1
bench --site lms.localhost clear-cache
bench use lms.localhost

say "[6/6] build the LMS Vue SPA assets"
bench build --app lms || say "WARN: 'bench build --app lms' failed (SPA assets may be stale)"

say "init complete — starting bench (web :8000, socketio :9000)"
exec bench start
