# Parallel Session Hygiene (Git Worktrees)

Multiple Claude Code sessions may run concurrently in this repo. To avoid file
conflicts, branch collisions, and interrupted work, use git worktrees for
feature development and code changes.

## When to require a worktree

- Feature development (creating/modifying code across multiple files)
- Multi-step refactors
- Anything that will produce a commit on a non-develop branch
- Long-running tasks that touch shared build artifacts (`node_modules`,
  `lms/public/frontend`, Nx cache)

## When a worktree is NOT needed

- Read-only exploration, questions, code review
- Trivial single-file edits
- Running existing commands (tests, lint) without code changes
- Work already happening inside a worktree (`.claude/worktrees/<name>/`)
- Git housekeeping on `develop` (pulling, branch cleanup, stash review)

## Behavior at session start

Check `git rev-parse --show-toplevel`:

- If inside `.claude/worktrees/<name>/` — already isolated, proceed.
- If in the main checkout AND the task qualifies above — pause and tell the
  user: "This looks like feature work. Consider restarting with
  `claude --worktree <name>` so we don't collide with other sessions." Then
  wait for their call — don't silently proceed.

## Worktree conventions

- Location: `.claude/worktrees/<name>/` (auto-created by `claude --worktree`)
- Each worktree needs its own `task install` (fresh deps)
- Cleanup is automatic on session exit (no changes = branch deleted)

## Cross-session coordination

- Never force-delete another session's worktree branch
- Don't rebase/reset a branch another worktree has checked out
- Treat `develop` as shared state — pull before branching, never commit
  directly
