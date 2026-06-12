#!/usr/bin/env bash
# Hook: PostToolUse → Write, Edit
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
# Auto-formats files after modification: ruff for Python, prettier for frontend.
set -eo pipefail

INPUT=$(cat) || exit 0
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || exit 0

if [ -z "$FILE_PATH" ]; then
	exit 0
fi

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")

if [[ $FILE_PATH == *.py ]]; then
	# Prefer the pinned version (matches the ruff rev in
	# .pre-commit-config.yaml and lms/project.json) so output can't drift
	# from CI; fall back to whatever ruff is on PATH.
	if command -v uvx &>/dev/null; then
		uvx ruff@0.13.3 format "$FILE_PATH" 2>/dev/null || true
		uvx ruff@0.13.3 check --fix "$FILE_PATH" 2>/dev/null || true
	elif command -v ruff &>/dev/null; then
		ruff format "$FILE_PATH" 2>/dev/null || true
		ruff check --fix "$FILE_PATH" 2>/dev/null || true
	fi
elif [[ $FILE_PATH == *.vue || $FILE_PATH == *.js || $FILE_PATH == *.ts ]]; then
	# Prettier lives in frontend/node_modules; skip silently when not installed.
	if [ -x "$REPO_ROOT/frontend/node_modules/.bin/prettier" ]; then
		"$REPO_ROOT/frontend/node_modules/.bin/prettier" --write "$FILE_PATH" 2>/dev/null || true
	fi
fi

exit 0
