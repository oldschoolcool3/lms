#!/usr/bin/env bash
# Hook: PreToolUse → Bash
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
# Enforces project-specific rules for shell commands.
set -eo pipefail

INPUT=$(cat) || exit 0
if ! command -v jq &>/dev/null; then
	echo "enforce-project-rules: jq not found — guard disabled" >&2
	exit 0
fi
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || {
	echo "enforce-project-rules: could not parse hook input — guard disabled" >&2
	exit 0
}

if [ -z "$COMMAND" ]; then
	exit 0
fi

deny_with_reason() {
	local reason="$1"
	jq -n \
		--arg name "PreToolUse" \
		--arg reason "$reason" \
		'{hookSpecificOutput: {hookEventName: $name, permissionDecision: "deny", permissionDecisionReason: $reason}}'
	exit 0
}

ask_with_reason() {
	local reason="$1"
	jq -n \
		--arg name "PreToolUse" \
		--arg reason "$reason" \
		'{hookSpecificOutput: {hookEventName: $name, permissionDecision: "ask", permissionDecisionReason: $reason}}'
	exit 0
}

# Block git status -uall (can cause memory issues on large repos)
if [[ $COMMAND == *"git status"*"-uall"* ]]; then
	deny_with_reason "Do not use 'git status -uall' — it can cause memory issues on large repos. Use 'git status' without -uall."
fi

# Git config: reads are fine; writes need user confirmation. A write is an
# explicit write flag, or the `git config [scope] key value` shape.
if [[ $COMMAND == *"git config"* ]]; then
	if [[ $COMMAND =~ git\ config[^\;\&\|]*--(unset|add|replace-all|edit|remove-section|rename-section) ]] ||
		[[ $COMMAND =~ git\ config([[:space:]]+--(global|system|local|worktree))?[[:space:]]+[A-Za-z0-9._-]+\.[A-Za-z0-9._-]+[[:space:]]+[^-[:space:]] ]]; then
		ask_with_reason "This modifies git configuration. Confirm with the user before changing git config."
	fi
fi

# mv as an actual command (start of string or after ;, &, |, or an opening
# paren; optional sudo/command/path prefix). `git mv` never matches this
# anchor. Multi-line commands are not caught — this is an accident guard,
# not a sandbox.
if [[ $COMMAND =~ (^|[\;\&\|\(][[:space:]]*)(sudo[[:space:]]+)?(command[[:space:]]+)?(/usr/bin/|/bin/)?mv[[:space:]] ]]; then
	ask_with_reason "Use 'git mv' instead of 'mv' for files tracked in git so history is preserved. Plain 'mv' is fine for untracked files (check with 'git ls-files <path>') — confirm to proceed."
fi

# Block destructive bench site commands
if [[ $COMMAND == *"bench drop-site"* ]] || [[ $COMMAND == *"bench reinstall"* ]]; then
	deny_with_reason "Destructive: this bench command erases site data. Ask the user for explicit confirmation."
fi

exit 0
