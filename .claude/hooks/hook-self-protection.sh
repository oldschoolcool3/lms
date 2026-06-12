#!/usr/bin/env bash
# Hook: PreToolUse → Bash, Edit, Write
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
# Prevents modification of Claude hooks and settings without explicit approval.
#
# The Bash branch is a best-effort heuristic (a shell can always be made to
# write a file in ways no substring check catches); the Edit/Write branch is
# the reliable one.
set -eo pipefail

INPUT=$(cat) || exit 0
if ! command -v jq &>/dev/null; then
	echo "hook-self-protection: jq not found — guard disabled" >&2
	exit 0
fi
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null) || {
	echo "hook-self-protection: could not parse hook input — guard disabled" >&2
	exit 0
}

PROTECTED_PATHS=(
	".claude/hooks/"
	".claude/settings.json"
)
# Same paths as an ERE fragment (dots escaped) for the redirect check.
PROTECTED_RE='\.claude/(hooks/|settings\.json)'

deny_with_reason() {
	local reason="$1"
	jq -n \
		--arg name "PreToolUse" \
		--arg reason "$reason" \
		'{hookSpecificOutput: {hookEventName: $name, permissionDecision: "deny", permissionDecisionReason: $reason}}'
	exit 0
}

check_path() {
	local path="$1"
	for protected in "${PROTECTED_PATHS[@]}"; do
		if [[ $path == *"$protected"* ]]; then
			deny_with_reason "Protected path '$protected' cannot be modified without explicit user permission. Ask the user before changing Claude hooks or settings."
		fi
	done
}

case "$TOOL" in
Bash)
	COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
	for protected in "${PROTECTED_PATHS[@]}"; do
		if [[ $COMMAND == *"$protected"* ]]; then
			# Write-capable command anchored at a command position (start of
			# string or after ;, &, |, or an opening paren) — `yarn install`
			# or `task install` never match because the token before
			# `install` is a space, not a separator.
			if [[ $COMMAND =~ (^|[\;\&\|\(][[:space:]]*)(sudo[[:space:]]+)?(rm|mv|cp|chmod|sed|tee|truncate|install|perl|ln)[[:space:]] ]]; then
				deny_with_reason "Protected path '$protected' cannot be modified via shell commands. Ask the user for explicit permission before modifying Claude hooks or settings."
			fi
			# Redirect targeting the protected path specifically (a redirect
			# elsewhere in the command, e.g. '> /tmp/x', is fine).
			if [[ $COMMAND =~ \>+[[:space:]]*[^[:space:]]*$PROTECTED_RE ]]; then
				deny_with_reason "Protected path '$protected' cannot be modified via shell redirection. Ask the user for explicit permission before modifying Claude hooks or settings."
			fi
		fi
	done
	;;
Edit | Write)
	FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null) || exit 0
	check_path "$FILE_PATH"
	;;
esac

exit 0
