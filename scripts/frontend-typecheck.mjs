#!/usr/bin/env node
// Ratcheting frontend type-checker.
//
// The SPA is `strict: true` and ~60% TypeScript but was never type-checked in
// CI, so it carries a backlog of pre-existing `vue-tsc` errors in upstream-
// derived components. Fixing them all at once would mean a large, churny diff
// across dozens of `frappe/lms` files — exactly the merge-conflict surface this
// fork avoids (see .claude/rules/working-posture.md, "Surgical changes").
//
// Instead we ratchet: `vue-tsc --noEmit` runs over the whole program, but its
// output is diffed against a committed baseline of known errors. CI fails only
// when a *new* error appears (in new or changed code). The backlog is burned
// down incrementally (Track A, PR-A3); regenerate the baseline as it shrinks:
//
//     node scripts/frontend-typecheck.mjs --update
//
// Errors are keyed by `file | code | message` (line/column are intentionally
// dropped) so that unrelated edits above an existing error don't masquerade as
// new failures.
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const frontendDir = join(repoRoot, "frontend");
const baselinePath = join(frontendDir, "typecheck-baseline.json");
const update = process.argv.includes("--update");

const vueTsc = join(
	frontendDir,
	"node_modules",
	".bin",
	process.platform === "win32" ? "vue-tsc.cmd" : "vue-tsc"
);

if (!existsSync(vueTsc)) {
	console.error(
		"vue-tsc not found — run `yarn install` in frontend/ before type-checking."
	);
	process.exit(2);
}

const result = spawnSync(vueTsc, ["-p", "tsconfig.json", "--noEmit"], {
	cwd: frontendDir,
	encoding: "utf8",
	maxBuffer: 64 * 1024 * 1024,
});

if (result.error) {
	console.error("Failed to run vue-tsc:", result.error.message);
	process.exit(2);
}

// `path(line,col): error TSxxxx: message` — continuation lines (indented
// overload details) don't match and are ignored.
const ERROR_RE = /^(.+?)\((\d+),(\d+)\): error (TS\d+): (.*)$/;
const output = `${result.stdout || ""}\n${result.stderr || ""}`;

// Some messages (e.g. TS2306) embed absolute paths. Strip the checkout root so
// signatures are identical locally and on CI (/home/runner/work/...).
const stripRoot = (s) =>
	s.split(`${frontendDir}/`).join("").split(`${repoRoot}/`).join("");

/** signature -> { count, lines: string[] } */
const current = new Map();
for (const line of output.split("\n")) {
	const m = ERROR_RE.exec(line);
	if (!m) continue;
	const [, file, , , code, message] = m;
	const signature = `${stripRoot(file)} | ${code} | ${stripRoot(message)}`;
	const entry = current.get(signature) || { count: 0, lines: [] };
	entry.count += 1;
	entry.lines.push(line);
	current.set(signature, entry);
}

const currentTotal = [...current.values()].reduce((n, e) => n + e.count, 0);

if (update) {
	const signatures = Object.fromEntries(
		[...current.entries()]
			.sort(([a], [b]) => a.localeCompare(b))
			.map(([s, e]) => [s, e.count])
	);
	writeFileSync(
		baselinePath,
		`${JSON.stringify({ total: currentTotal, signatures }, null, 2)}\n`
	);
	console.log(
		`Wrote ${baselinePath} with ${currentTotal} grandfathered error(s).`
	);
	process.exit(0);
}

if (!existsSync(baselinePath)) {
	console.error(
		`No baseline found at ${baselinePath}.\n` +
			"Generate one with: node scripts/frontend-typecheck.mjs --update"
	);
	process.exit(2);
}

const baseline =
	JSON.parse(readFileSync(baselinePath, "utf8")).signatures || {};

const newErrors = [];
for (const [signature, entry] of current) {
	const allowed = baseline[signature] || 0;
	if (entry.count > allowed) newErrors.push(...entry.lines.slice(allowed));
}

if (newErrors.length) {
	console.error(
		`✖ ${newErrors.length} new type error(s) not in the baseline:\n`
	);
	for (const line of newErrors) console.error(`  ${line}`);
	console.error(
		"\nFix them, or — if intentional — refresh the baseline with:\n" +
			"  node scripts/frontend-typecheck.mjs --update"
	);
	process.exit(1);
}

const baselineTotal = Object.values(baseline).reduce((n, c) => n + c, 0);
console.log(
	`✓ No new type errors (${currentTotal} known error(s) grandfathered in the baseline).`
);
if (currentTotal < baselineTotal) {
	console.log(
		`  ${baselineTotal - currentTotal} baselined error(s) are now fixed — refresh with ` +
			"`node scripts/frontend-typecheck.mjs --update` to lock in the gain."
	);
}
process.exit(0);
