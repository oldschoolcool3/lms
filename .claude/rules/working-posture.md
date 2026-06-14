# Working Posture (every task)

Evergreen behavioral defaults — they describe *how to work*, not *what the repo
contains*, so they never go stale. They bias toward caution over speed; for
trivial changes, use judgment.

## Think before coding

- Verify against the code; don't assume. Frappe is convention-heavy — a DocType's
  JSON schema, its Python controller, and its client usage must stay in sync, and
  a confident wrong guess about one of them passes review and fails at runtime.
- If a request has more than one reasonable reading, state the options and ask —
  don't silently pick one.
- If a simpler approach exists, say so before building the complex one. Push back
  when warranted.
- Name what's unclear instead of guessing. This matters most for cross-cutting
  invariants — permission checks on whitelisted endpoints, enrollment/progress
  state transitions, payment flows, certificate evaluation — where a
  plausible-but-wrong change ships silently.

## Simplicity first

- Write the minimum that satisfies the request. No speculative abstractions,
  configuration, or generality that wasn't asked for; no error handling for
  impossible states; no flexibility "for later."
- Prefer the smallest change that fits the existing shape — Frappe and frappe-ui
  almost always already have the primitive you need (DocType hooks, `frappe.qb`,
  frappe-ui components). Check before writing a new one.
- Ask: "would a senior engineer call this overcomplicated?" If yes, cut it.

## Scoped changes (for review clarity, not merge-avoidance)

- We're an independent hard fork of `frappe/lms` — no longer kept mergeable. So
  reformatting, refactoring, retyping, and removing legacy code are all
  sanctioned; just do them as their *own* focused commits/PRs, not smuggled into
  unrelated work.
- Within a given change, stay scoped: every changed line should trace to that
  change's stated goal, so diffs stay reviewable and bisectable.
- Match the local style (spaces in Python, prettier in the frontend) — unless the
  change *is* a deliberate, repo-wide restyle.
- Don't delete code you merely suspect is dead as a drive-by; confirm it, then
  remove it as a deliberate cleanup change (now allowed) with that as its goal.

## Goal-driven, verified

- Restate the task as an explicit, checkable success criterion before starting.
- For a bug, write a failing repro test first, then make it pass.
- For multi-step work, state a brief plan with a verification step per step.
- Then actually run the checks and loop until green — don't declare done on
  "looks right":
  - `task lint` / `task test:frontend` for code
  - `task test:backend` (needs a bench) for server-side changes
  - `uvx pre-commit run --all-files` before handing off
- "Looks right" and "is right" diverge silently for permissions, payments, and
  enrollment state — verify those explicitly.
