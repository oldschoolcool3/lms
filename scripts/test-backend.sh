#!/usr/bin/env bash
# Run the Frappe (server-side) test suite for the lms app.
#
# Frappe tests must run inside a bench with a site that has the lms app
# installed — they cannot run from this repo checkout alone. Configure:
#
#   BENCH_DIR  path to the bench (default: ~/frappe-bench)
#   SITE       site with lms installed (default: lms.localhost)
#
# Examples:
#   bash scripts/test-backend.sh
#   BENCH_DIR=~/benches/lms SITE=lms.test bash scripts/test-backend.sh
#   SITE=lms.test bash scripts/test-backend.sh --module lms.lms.doctype.lms_quiz.test_lms_quiz
set -euo pipefail

BENCH_DIR="${BENCH_DIR:-$HOME/frappe-bench}"
SITE="${SITE:-lms.localhost}"

if ! command -v bench &>/dev/null; then
	echo "ERROR: 'bench' CLI not found on PATH."
	echo "Server tests require a Frappe bench — see docs/002-development/how-to-guides/003-install-with-bench.md"
	exit 1
fi

if [ ! -d "$BENCH_DIR/sites" ]; then
	echo "ERROR: '$BENCH_DIR' does not look like a bench (no sites/ directory)."
	echo "Set BENCH_DIR to your bench path, e.g.: BENCH_DIR=~/benches/lms bash scripts/test-backend.sh"
	exit 1
fi

cd "$BENCH_DIR"
exec bench --site "$SITE" run-tests --app lms "$@"
