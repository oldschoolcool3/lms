#!/usr/bin/env bash
# Hook: PreToolUse → Bash
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
# Blocks destructive git commands that could lose work.
#
# Substring/regex heuristics, deliberately simple: they can be bypassed by a
# determined actor and may rarely misfire on commit messages quoting these
# commands — the goal is preventing accidents, not sandboxing.
set -eo pipefail

INPUT=$(cat) || exit 0
if ! command -v jq &>/dev/null; then
	echo "git-safety-check: jq not found — guard disabled" >&2
	exit 0
fi
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || {
	echo "git-safety-check: could not parse hook input — guard disabled" >&2
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

if [[ $COMMAND == *"git checkout -- "* ]]; then
	deny_with_reason "Destructive: 'git checkout --' discards uncommitted changes. Use 'git stash' to save work first, or ask the user for explicit confirmation."
fi
if [[ $COMMAND == *"git checkout ."* ]]; then
	deny_with_reason "Destructive: 'git checkout .' discards uncommitted changes in the working tree. Use 'git stash' or ask the user for explicit confirmation."
fi
# git restore discards working-tree changes in every form except a pure
# --staged invocation (which only unstages, leaving the working tree intact).
if [[ $COMMAND == *"git restore"* ]]; then
	if [[ $COMMAND != *"--staged"* ]] || [[ $COMMAND == *"--worktree"* ]]; then
		deny_with_reason "Destructive: 'git restore' discards uncommitted changes (only a pure --staged invocation is safe). Use 'git stash' or ask the user for explicit confirmation."
	fi
fi
if [[ $COMMAND == *"git reset --hard"* ]]; then
	deny_with_reason "Destructive: 'git reset --hard' permanently discards commits and working tree changes. Use 'git stash', 'git reset --soft', or ask the user for confirmation."
fi
if [[ $COMMAND =~ git\ clean[[:space:]][^\;\&\|]*-[a-zA-Z]*f ]]; then
	deny_with_reason "Destructive: 'git clean -f' permanently deletes untracked files. Preview with 'git clean -n', or ask the user for explicit confirmation."
fi
if [[ $COMMAND == *"git stash drop"* ]]; then
	deny_with_reason "Destructive: 'git stash drop' permanently deletes a stash entry. Ask the user for explicit confirmation before dropping stashes."
fi
if [[ $COMMAND == *"git stash clear"* ]]; then
	deny_with_reason "Destructive: 'git stash clear' permanently deletes ALL stash entries. Ask the user for explicit confirmation."
fi
# Allow the revert subcommands that manage an in-progress revert.
if [[ $COMMAND == *"git revert"* ]] &&
	[[ $COMMAND != *"git revert --abort"* ]] &&
	[[ $COMMAND != *"git revert --continue"* ]] &&
	[[ $COMMAND != *"git revert --quit"* ]]; then
	deny_with_reason "Potentially destructive: 'git revert' creates commits that undo history. Ask the user for explicit confirmation before reverting commits."
fi
# Force-push: --force-with-lease is the recommended safer form and is allowed;
# plain --force / -f / +refspec overwrite remote history unconditionally.
if [[ $COMMAND == *"git push"* ]] && [[ $COMMAND != *"--force-with-lease"* ]]; then
	if [[ $COMMAND == *"--force"* ]] || [[ $COMMAND =~ git\ push[^\;\&\|]*\ -f([[:space:]]|$) ]] || [[ $COMMAND =~ git\ push[^\;\&\|]*\ \+[^[:space:]] ]]; then
		deny_with_reason "Destructive: force-push overwrites remote history and can destroy teammates' work. Use 'git push --force-with-lease' if appropriate, or ask the user for explicit confirmation."
	fi
fi

exit 0
