## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0195-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0195-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Harness hygiene batch: ruling on BLOCKED, park reasons, run-record whitespace, redispatch rows, marker ledger, init half instance, relative paths, clean-checkout tests"
labels: "harness"
---
**Small harness fixes, batched into one ticket to pay the ticket overhead once.** Pre-approved under the queue policy, except the item marked otherwise. Sources: the retro trial (`.factory/answers/retro-trial-2026-10-04/`) and the Nanobot v3.5 Driver's reports.

| # | Fix | Evidence |
|---|---|---|
| H1 | `resolve --ruling` accepts a BLOCKED park as well as ESCALATE. It writes `approvals/<id>/ruling-<n>.md`, which compose already hands to the implementer, and returns the sub-ticket to `ready-for-implementer`. Today the human writes the file by hand and runs a raw `ticket transition`. | spec-factory T-0012.4 (2026-10-03); Nanobot T-0002.2 (2026-10-04, `approvals/T-0002.2/ruling-1.md`) |
| H2 | A park reason always carries the failing command's error. Today some reasons are blank: `archive: `, `subticket add: ` | spec-factory T-0014 (two parks), T-0016, T-0020 |
| H3 | Committed run records do not fail whitespace checks: `init` writes a store `.gitattributes` with `runs/** -whitespace`. | spec-factory T-0012 parent close (run-0102), amendment 1 |
| H4 | A redispatch supersedes only the rows of the role(s) being re-run. Today a re-run discards a surviving verifier row that was still valid on the same head. | retro H5 (run-0073, run-0077) |
| H5 | The marker ledger matches `factory:` comments only, not string literals. Today it matches `cli.py:1081`'s `print`. | retro C7 / H9 |
| H6 | #30: `init` on a throwaway store writes a half instance, and a later run crashes on the missing `context.md`. Fix: refuse, or gate the write; a missing `context.md` refuses with exit 2. | #30 |
| H7 | A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` resolves against the caller's directory, not the harness checkout. | T-0012 parent-close verifier probe (run-0103) |
| H8 | The harness's own tests do not depend on the checkout running them being clean. Tests that build an instance on their own store set the uncommitted-edit check off explicitly, so the suite can run in the middle of an edit. | spec-factory, 2026-10-03: 23 failures from a single uncommitted edit |

**Not in this ticket (waits for the operator):** the store is committed to the integration branch, so `main` moves even when no ticket merges, which costs catch-up runs (retro C1: four of them). Moving the store off `main` is a design change.


---

**Comment on the issue:**

H9, added 2026-10-04 from the Nanobot v3.5 Driver: **no path to add a fix after a parent-close FAILED.** Nanobot T-0002's parent-close verifier (run-0158) passed all 15 scenarios and the gate, then FAILED on a real probe finding: on macOS's case-insensitive filesystem, `write_file` to `POLICIES.json` bypasses the store guard. The design says the human re-plans with new sub-tickets under the same parent, but neither step works:
- (1) `subticket add --file` numbers sub-tickets from 1 (`subtickets.parse`), so a one-entry fix plan becomes `T-0002.1` and is refused as already existing;
- (2) routing has no `parked → planned` edge, and `build.js` enters Build only from `planned`.

The Driver created T-0002.9 by hand with the harness's own functions, and moved the parent back with `ticket set`.

Fix:
- (a) `subticket add` continues numbering after the parent's existing sub-tickets, or honours explicit ids that don't collide, and their dependencies may name merged siblings;
- (b) `resolve <parent> --replan --file <plan>` adds the fix sub-tickets and moves the parked parent to `planned` in one logged step;
- (c) the routing edge `parked → planned`, reachable only through that resolve.

---

Operator: spec gate pre-approved under the queue policy (`.factory/answers/queue-preapproval-policy.md`), except the store-on-main design change, which is out of scope here. NEEDS-SPLIT along the H-items is expected.
