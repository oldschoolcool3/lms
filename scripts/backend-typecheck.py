#!/usr/bin/env python3
"""Ratcheting backend type-checker (pyright).

The Frappe app is almost entirely untyped, inherited ``frappe/lms`` code, and
the framework's dynamic ORM (``frappe.db.get_value`` returning ``dict | None``,
``frappe._dict`` attribute access) makes a clean ``pyright`` pass impossible
without a large, churny diff across upstream files — exactly the merge-conflict
surface this fork avoids (see ``.claude/rules/working-posture.md``, "Surgical
changes"). ``frappe``/``payments`` are bench-injected and never resolvable in
the uv tool env, so their import errors are suppressed in ``[tool.pyright]``.

Instead we ratchet — the same model as ``scripts/frontend-typecheck.mjs``:
``pyright`` runs over the whole program, but its output is diffed against a
committed baseline of known errors. The gate fails only when a *new* error
appears (in new or changed code), so net-new fork modules are type-checked
while the inherited backlog is grandfathered. Burn it down and refresh:

    uv run --only-group typecheck python scripts/backend-typecheck.py --update

Errors are keyed by ``file | rule | message`` (line/column are intentionally
dropped) so that unrelated edits above an existing error — e.g. inserting a
docstring — don't masquerade as new failures.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_ROOT / "backend-typecheck-baseline.json"
UPDATE = "--update" in sys.argv[1:]


def run_pyright() -> dict:
    """Run pyright in JSON mode and return the parsed report."""
    pyright = shutil.which("pyright")
    if not pyright:
        print(
            "pyright not found — run via `uv run --only-group typecheck python "
            "scripts/backend-typecheck.py` so the typecheck group is on PATH.",
            file=sys.stderr,
        )
        sys.exit(2)
    # `pyright` is a resolved absolute path (shutil.which) and the argv is a fixed
    # literal list (no shell, no untrusted input), so S603 is a false positive here.
    proc = subprocess.run(  # noqa: S603
        [pyright, "--outputjson"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    # pyright exits non-zero when diagnostics exist; that is expected. Only a
    # missing/garbled JSON payload is a real failure.
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("Failed to parse pyright JSON output:", file=sys.stderr)
        print(proc.stdout[-2000:], file=sys.stderr)
        print(proc.stderr[-2000:], file=sys.stderr)
        sys.exit(2)


def signatures(report: dict) -> dict[str, int]:
    """Reduce pyright errors to stable ``file | rule | message`` signatures."""
    counts: dict[str, int] = {}
    for diag in report.get("generalDiagnostics", []):
        if diag.get("severity") != "error":
            continue
        raw = diag.get("file", "")
        try:
            rel = Path(raw).resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = raw
        rule = diag.get("rule", "")
        message = " ".join(diag.get("message", "").split())
        sig = f"{rel} | {rule} | {message}"
        counts[sig] = counts.get(sig, 0) + 1
    return counts


def main() -> int:
    """Compare the current pyright errors against the committed baseline."""
    current = signatures(run_pyright())
    current_total = sum(current.values())

    if UPDATE:
        ordered = {sig: current[sig] for sig in sorted(current)}
        BASELINE_PATH.write_text(json.dumps({"total": current_total, "signatures": ordered}, indent=2) + "\n")
        print(f"Wrote {BASELINE_PATH.name} with {current_total} grandfathered error(s).")
        return 0

    if not BASELINE_PATH.exists():
        print(
            f"No baseline found at {BASELINE_PATH.name}.\n"
            "Generate one with: uv run --only-group typecheck python "
            "scripts/backend-typecheck.py --update",
            file=sys.stderr,
        )
        return 2

    baseline = json.loads(BASELINE_PATH.read_text()).get("signatures", {})

    new_errors = []
    for sig, count in current.items():
        allowed = baseline.get(sig, 0)
        if count > allowed:
            new_errors.append(f"{sig}  (x{count - allowed} new)")

    if new_errors:
        print(f"✖ {len(new_errors)} new type error(s) not in the baseline:\n", file=sys.stderr)
        for line in new_errors:
            print(f"  {line}", file=sys.stderr)
        print(
            "\nFix them, or — if intentional — refresh the baseline with:\n"
            "  uv run --only-group typecheck python scripts/backend-typecheck.py --update",
            file=sys.stderr,
        )
        return 1

    baseline_total = sum(baseline.values())
    print(f"✓ No new type errors ({current_total} known error(s) grandfathered in the baseline).")
    if current_total < baseline_total:
        print(
            f"  {baseline_total - current_total} baselined error(s) are now fixed — refresh with "
            "`uv run --only-group typecheck python scripts/backend-typecheck.py --update` to lock in the gain."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
