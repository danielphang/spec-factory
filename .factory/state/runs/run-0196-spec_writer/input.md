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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0196-spec_writer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0196-spec_writer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Ticket (Triage output)

Type: bug (a batch of nine harness defects. H3 and H8 are closer to chores.)

Title: Harness hygiene batch: ruling on a BLOCKED park, park reasons with the error, run-record whitespace, redispatch keeps valid rows, marker ledger, init half instance, relative env paths, clean-checkout tests, re-plan after a parent-close FAILED

Summary:
The harness strands tickets in states a human can only leave by hand-editing the store or calling raw store commands. It also produces records and test results that mislead. The requester wants nine small fixes in one ticket. In the factory's terms, a ticket is "parked" when it stops and waits for a human. `resolve` is the command a human uses to move a parked ticket on.
- H1: `resolve --ruling` should accept a park caused by an implementer's BLOCKED as well as one caused by ESCALATE. It should write `approvals/<id>/ruling-<n>.md` and return the sub-ticket to `ready-for-implementer`.
- H2: every park reason should carry the failing command's error text, never a blank `archive: ` or `subticket add: `.
- H3: committed run records should not fail git whitespace checks; the requester proposes `init` writing a store `.gitattributes` with `runs/** -whitespace`.
- H4: a redispatch re-runs the checkers on the same commit. It should set aside only the result rows of the roles being re-run, and keep a verifier row that is still valid on that commit.
- H5: the marker ledger lists every `factory:` shortcut comment in the code for the retro. It should match comments only, not string literals.
- H6 (issue #30): `init` on a throwaway store should not leave a half-written instance. A missing `context.md` should be refused with exit 2, not crash.
- H7: a relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` should resolve against the caller's directory, not the harness checkout.
- H8: the harness's own suite should pass while the checkout running it has an uncommitted edit.
- H9: after a parent-close verifier FAILED, a human needs a supported way to add fix sub-tickets under the same parent and send the parent back to Build. The design already prescribes this re-plan (`docs/design.md` line 100). The requester proposes three parts: (a) `subticket add` keeps numbering after the existing sub-tickets, or accepts explicit ids that don't collide, and their dependencies may name merged siblings; (b) a new `resolve <parent> --replan --file <plan>`; (c) a routing edge `parked → planned` that only that resolve can use.
Out of scope, by the requester: moving the store off `main`, which waits for the operator.

Evidence (each item checked on `main` at 67447b1 unless noted):
- H1: `factory/cli.py:747-750` refuses `--ruling` unless the park reason starts with `ESCALATE`. The routing edge `parked → ready-for-implementer` already exists (`.factory/instance.yaml` line 61), so H1 needs no routing change. Design line 98 already says BLOCKED returns to its role with the ruling. The Nanobot instance has the hand-written `approvals/T-0002.2/ruling-1.md`.
- H2: `factory/workflows/build.js:202` builds `harness-bug: subticket add: ${subs.stderr || ''}` and line 256 builds `archive: ${arch.stderr || ''}`. When stderr is empty, the reason is blank. The store log has four blank `archive: ` parks (T-0014, T-0016, T-0018, T-0020) and one blank `harness-bug: subticket add: ` park (T-0014, log line 605). The requester lists T-0018 nowhere; it is a fifth instance of the same defect.
- H3: `grep -n gitattributes factory/*.py` prints nothing: no code writes a store `.gitattributes` today. The whitespace failure itself is the requester's report from T-0012's parent close (run-0102); I did not reproduce it.
- H4: in `factory/cli.py:761-779`, `--redispatch` moves every `results/<head>/*.yaml` into `superseded-<n>/`, whatever the role.
- H5: no ledger producer exists in the harness. `git grep -i 'marker ledger'` outside the store finds only answers and the changelog. Changelog entry 44 (`docs/changelog.md:48`) says the ledger "is design only, and the harness code that builds the ledger waits for the ticket that builds the retro". The retro trial's ledger row (`.factory/answers/retro-trial-2026-10-04/inputs.md` line 283) was produced outside the harness. See ESCALATIONS.
- H6: `init_cmd` (`factory/cli.py:821-865`) writes `instance.yaml` even when the store in use is not the instance's own, but writes `context.md` only for the instance's own store. `compose.py:85` reads `context.md` with no existence check, so a later compose raises an uncaught `FileNotFoundError`. I found this by reading the code, not by running it.
- H7: `bin/factory` does `cd "$HERE"` (the harness checkout) before running Python. `store.py:40`, `instance.py:46`, `instance.py:72` and `instance.py:89` then call `Path(env).expanduser().resolve()`. That resolves a relative value against the harness checkout, not the caller's directory, which `bin/factory` saves as `FACTORY_CWD`. I found this by reading the code.
- H8: reproduced. In a clone under this run's scratch directory, `uv run --frozen pytest -q -p no:cacheprovider tests/factory` (HOME set to a fresh temp directory) printed `215 passed`. After appending one comment line to `factory/status.py`, it printed `23 failed, 192 passed`. The cause is the harness-lock guard (`instance.py:136-139`), which refuses any uncommitted harness edit. That matches the requester's 23.
- H9: `subtickets.parse` numbers sub-tickets from 1 (`factory/subtickets.py:48`, `enumerate(heads, 1)`). `build.js:208` enters Build only from `planned`. The routing table has no `parked → planned` edge (`.factory/instance.yaml` line 61, `factory/instance.template.yaml` line 63, and the Nanobot instance's `instance.yaml` line 71). The Nanobot store has the hand-made `T-0002.9`.
- Duplicates: none. I searched the store's tickets T-0001 to T-0023 and `dev/issues.md`. Issue #30 (H6) is listed there as "not in intake" and is folded into this batch (#39).

Assumptions (mine, not the requester's):
- The operator's note ("pre-approved under the queue policy, except the store-on-main design change") was written after the H9 comment, so I read it as covering H9. ESCALATIONS item 1 says why that reading needs confirming.
- H3's fix may be any change that keeps committed run records passing `git diff --check`. `.gitattributes` is the requester's suggestion, not the requirement.
- For H8, "set the uncommitted-edit check off explicitly" means a test-side change, such as a fixture that stubs the check for test-built instances. It does not mean a switch the production CLI would honour.
- H4: a surviving row is "still valid" when it was recorded on the same head commit and its role is not among those re-run.
- Suggested priority (a suggestion; priority is the operator's call): H9 and H1 first, because each currently needs a hand edit of the store to unstick a ticket. H5 last.

Reason: ACCEPT. The intent of each item is clear, the evidence checks out against the code, and the operator pre-approved the batch. The operator also said a split into one sub-ticket per H-item is expected, which is the planner's job.

STATUS: ACCEPT
CONFIDENCE: medium. Eight items are confirmed in code or by reproduction, but H5 has no code to fix and H9(c) may sit outside the pre-approval, which the operator should confirm.
ESCALATIONS:
- H9(c) is a routing change, and the queue policy excludes routing changes from "small". The policy (`.factory/answers/queue-preapproval-policy.md`) defines a small fix as "no routing, gate or merge-rule change". H9(c) adds an edge to the routing table, which lives in `.factory/instance.yaml`, a protected path. The same edge goes in `factory/instance.template.yaml`, and the Nanobot instance's `instance.yaml` needs it too, which this repo's ticket cannot write. "Reachable only through that resolve" also needs a mechanism the harness lacks: the routing table allows an edge for every command, and the design says the CLI refuses any transition not in it. So the spec must choose between opening `parked → planned` to raw `ticket transition` too, or adding a per-command limit on that edge. Decide at the spec gate: does H9 ride this batch's pre-approval, or wait for your review as a routing change?
- H5 asks to fix code that does not exist. No harness code builds the marker ledger. Changelog entry 44 records it as design only, waiting for the ticket that builds the retro. The design text already says "one row per `factory:` comment". The wrong row came from a ledger made outside the harness for the retro trial. Suggested handling: drop H5 from this ticket and carry "match comment leaders only, per `docs/coding.md` rule 3" into the ticket that builds the retro.
- H8 must not weaken the harness-lock guard. A switch the production CLI honours would let a real run on the instance's own store skip the uncommitted-edit refusal, which the policy calls a loosened check. The fix should stay test-side.
- My H8 reproduction ran with `UV_CACHE_DIR` set to the real `~/.cache/uv` so that `uv sync` would not re-download packages. That directory is not protected, and the run wrote nothing else outside this run's scratch directory.

## Request (raw)

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
