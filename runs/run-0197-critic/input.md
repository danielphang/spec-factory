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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0197-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0197-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v1)

=== proposal.md
## Problem

The spec factory runs each requested change through a chain of AI agents. The harness is the code that moves a piece of work, a ticket, from agent to agent and keeps its records in a folder called the store. Eight harness defects strand the operator's tickets or produce records that mislead them. All eight were hit in real runs on 2026-10-03 and 2026-10-04. A ninth item asks for a fix to code that does not exist, and it is cut.

A ticket is parked when the harness stops and waits for a human. `factory resolve` is the command a human runs to move a parked ticket on. A sub-ticket is one unit of a ticket's plan, built on its own branch and merged on its own. The parent-close check is one final verifier run on the merged result. It checks the whole spec after every sub-ticket has merged.

| Item | What goes wrong today | Who it hits |
|---|---|---|
| H1 | An implementer, the agent that writes the code, can report BLOCKED. `resolve` refuses to accept a human ruling on that park. | The operator. They write the ruling file by hand and move the ticket with a raw state change. |
| H2 | Some park reasons end in a blank where the failing command's error should be, such as `archive: `. | The operator. They have to dig through run logs to learn why a ticket stopped. |
| H3 | Run records committed with the store fail git's whitespace check, because they embed verbatim diffs. | Every parent-close check whose range includes store commits. |
| H4 | Re-running a sub-ticket's checks after an outside fix throws away a verifier result that is still valid for that commit. | The operator's budget: one verifier run, about 10 minutes, is repeated for nothing. |
| H6 | `init`, run on a throwaway test store, writes half an instance. A later run then crashes on the missing briefing file. | Anyone testing against a scratch store. |
| H7 | A relative path in `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` resolves against the harness's own checkout, not the directory the command ran in. | Anyone who points the factory at a store with a relative path. |
| H8 | The harness's own test suite fails 23 tests whenever the checkout running it has an uncommitted edit. | Whoever edits the harness. They cannot run the suite mid-edit. |
| H9 | After a parent-close check fails, there is no supported way to add a fix sub-ticket and resume. New sub-tickets are numbered from 1 again and collide with the old ones. No resolve mode sends the parent back to planning. | The operator. On the Nanobot target they built the fix sub-ticket by hand. |

The fix gives H1 and H9 their own `resolve` modes. H9's re-plan uses a state change the routing table already allows. The routing table is the list of allowed state changes. H2, H3, H4, H6 and H7 are corrected where they happen. H8 is a test-side change: the check that refuses a dirty harness checkout stays exactly as it is.

## Evidence

Checked on `main` at `67447b1`. Every "prints" below comes from running the command on that commit, unless it says otherwise.

- **H1.** `factory/cli.py` lines 748-751 refuse `--ruling` unless the park reason starts with `ESCALATE`. The store log shows the hand path. Line 353 parks `T-0012.4` with `"reason": "BLOCKED from implementer"`. Line 370 moves it `parked → ready-for-implementer` `by dphang` with a plain transition. No ruling file was written. The scenario "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" prints `exit=2 parked pr=0`, `ruling=missing` and `in_input=0` today. That means the refusal, no file, and nothing reaches the implementer. Composing already hands every `approvals/<id>/ruling-*.md` file to the implementer (`factory/compose.py` lines 190-191), so only the refusal is missing. The design already says BLOCKED returns to its role with the ruling, at the same round (`docs/design.md` line 98).
- **H2.** Five parks in this store's log have a blank reason. Line 605 has `harness-bug: subticket add: `. Lines 639, 727, 827 and 932 have `archive: ` (T-0014, T-0016, T-0018, T-0020). The store has no `openspec/` tree, so each archive was refused with `no spec store (factory init not run)`. A refusal prints that text on stderr. It also prints it as the `error` field of a JSON line on stdout (`factory/cli.py` lines 1170-1173). The workflow scripts build each reason from the clerk's relayed stderr only. The clerk is the small agent that runs one store command and relays its output. The relevant lines are `` `archive: ${arch.stderr || ''}` `` (`factory/workflows/build.js` line 256), 18 more sites in `build.js` and 7 in `intake.js`. I ran each workflow script under node, with a stub clerk that relays stdout but an empty stderr. It printed `park: archive: `, `park: harness-bug: subticket add: ` and `park: harness-bug: run start triage: `. Each reason is blank even though the refusal text was on stdout.
- **H3.** The parent-close verifier for T-0012 (`runs/run-0102-verifier/output.md` lines 47-49) reported its whitespace scenario `exit=2`. Every reported path was a store run record (`diff.patch`, `input.md`), and the same range with the store excluded exited 0. A blank context line in a diff is a single space, which `git diff --check` reports as trailing whitespace. No code writes a store `.gitattributes` today. In a scratch repo, I committed a run record with trailing spaces. `git diff --check` exited 2. After a committed `.factory/state/.gitattributes` holding `runs/** -whitespace`, the record was exempt, and a trailing space in a file outside `runs/` was still reported. The rule works as intended. The scenario "Run records in a store pass whitespace checks and other store files do not" prints `runs=2` and `other=2` today.
- **H4.** `resolve --redispatch` moves every `results/<head>/*.yaml` into `superseded-<n>/`, whatever its status (`factory/cli.py` lines 761-779). The build then runs both checkers again (`build.js` lines 146-155). For T-0012.4 the store holds `results/010d1b0…/superseded-1/` with `reviewer.yaml` `KILLED` (run-0076), `verifier.yaml` `VERIFIED` and `ci.yaml` `PASS` (both run-0077). That verifier result was valid for that commit and was thrown away. The retro's second case, T-0012.5 (run-0073), had `ci.yaml` `FAIL`. That gate row was itself wrong, because of a parser bug fixed since, so the rule below re-runs it. So one of the two runs was wasted, not both.
- **H6.** Reproduced in a scratch git repo. `FACTORY_STATE=$T/s bin/factory init --repo-name demo` exited 0 and created `.factory/instance.yaml` with no `context.md`. It wrote `context.md` only for the instance's own store (`factory/cli.py` lines 841-850). `run compose` then printed `factory: FileNotFoundError: … .factory/context.md` and exited 1. That crash comes from `factory/compose.py` line 85, which reads the file with no check.
- **H7.** Reproduced with `factory paths`, which writes nothing. From a temporary directory `$T`, `FACTORY_STATE=rel/store` printed `"state": "/Users/dphang/dev/spec-factory/rel/store"`. That is the harness checkout, not `$T`. `FACTORY_REPO=rel` gave `…/spec-factory/rel/.factory/state`. Running from `tests/factory/fixtures` with `FACTORY_INSTANCE=instance` printed `"instance": null`, so the instance was not found. The cause is that `bin/factory` changes into the harness checkout before Python runs. The caller's directory survives only as `FACTORY_CWD`.
- **H8.** Reproduced. In a clone of `67447b1`, under a throwaway `HOME` and after `uv sync --frozen`, the suite printed `215 passed` clean. After one appended comment line in `factory/status.py`, it printed `23 failed, 192 passed in 139.24s`: 17 in `test_harness_lock.py` and 6 in `test_instance.py`. All 23 run this checkout's `bin/factory` against an instance's own store. The harness-lock check refuses every such command while the running checkout has an uncommitted harness edit (`factory/instance.py` lines 137-139). The test module says so by design (`tests/factory/test_harness_lock.py` lines 8-10). I prototyped the change described in part G in that clone, with the edit still in place. It printed `215 passed in 137.07s`.
- **H9.** `subtickets.parse` numbers a plan's sub-tickets from 1 (`factory/subtickets.py` line 48, `enumerate(heads, 1)`). It refuses a dependency on `<parent>.<n>` that is not in the same plan (lines 84-85). The scenario "A later plan's sub-tickets take the next free ids and may depend on a merged sibling" prints only `"ready": []` today, because the add is refused. No `resolve` mode leaves a parked parent for planning. `build.js` runs the planner only from `ready-for-planner` (line 191). The routing table already allows `parked → ready-for-planner` (`.factory/instance.yaml` line 61). `dev/build-harness.spec.md` line 314 already describes the re-plan as going back to `ready-for-planner`, with "the planner's new sub-tickets take the next free ids under the same parent, merged ones stay `merged`".
- **H5 (cut).** No harness code builds the marker ledger. Changelog entry 44 (`docs/changelog.md` line 48) records it as design only. The design text already says "one row per `factory:` comment" (`docs/design.md` line 696). The wrong row came from a ledger built outside the harness for the retro trial.

## Root cause

- H1: `factory/cli.py` `resolve`, the `--ruling` branch (lines 747-755). Only `ESCALATE` parks are accepted.
- H2: `clerk()` in `factory/workflows/build.js` (lines 41-56) and `factory/workflows/intake.js` (lines 50-64). Neither falls back to the JSON `error` field or to the exit code when the relayed stderr is empty.
- H3: `factory/store.py` writes the store's `.gitignore` (`ensure_gitignore`) and nothing that exempts `runs/` from whitespace checks.
- H4: `factory/cli.py` `resolve`, the `--redispatch` branch, sets every row aside. `build.js` `buildOne` runs both checkers whenever it reaches `checks-in-flight`.
- H6: `factory/cli.py` `init_cmd` writes `instance.yaml` before it knows whether the store is the instance's own. `factory/compose.py` `compose` line 85 reads `context.md` with no existence check.
- H7: `factory/instance.py` lines 46, 72 and 89, `factory/store.py` line 40 and `factory/cli.py` line 829 call `Path(env).expanduser().resolve()`. That resolves a relative path against the process's working directory, which `bin/factory` has set to the harness checkout.
- H8: `factory/instance.py` `guard`, C.4, by design. The tests run the real check for cases that are not about it.
- H9: `factory/subtickets.py` `parse` numbers from 1 and knows nothing of existing sub-tickets. `factory/cli.py` `resolve` has no mode that moves a parked parent to `ready-for-planner`.

## Out of scope

- Moving the store off `main`. The requester excluded it, and it waits for the operator.
- H5, the marker ledger matching only comments. No harness code builds the ledger. The rule goes to the ticket that builds the retro: match comment leaders only, per `docs/coding.md` rule 3.
- The requester's `parked → planned` edge and a human-written plan that skips the planner (Decisions).
- Re-planning while any sub-ticket is not merged, for example after a human closed one. Spec amendment during a re-plan (`--amend-spec` in `dev/build-harness.spec.md` line 314).
- Forcing a re-run of a checker whose row passed.
- Keeping the first plan in `plans/<id>.md` and the change folder's `tasks.md` after a re-plan. Both hold the latest plan. The earlier plan stays in its planner run's `output.md`.
- `bin/factory`, `.factory/**`, `factory/instance.template.yaml` and the routing table: no change. Also out: `docs/design.md`, which already prescribes each behaviour here (lines 98, 100, 102 and 696), `docs/prompts/**` and every agent prompt.
- The Nanobot instance's files, including its hand-made `T-0002.9`.

## Open questions

none

## Decisions

- `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
- `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
- Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
- A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
- A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
- The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
- `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
- A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
- The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
- The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
- The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.

## Risk

Blast radius, by part:
- A/H (resolve): two new paths out of a park, through an existing routing edge each. Every existing `resolve` mode keeps its refusals.
- B (park reasons): only the text of a failure reason changes. Routing is unchanged.
- C (whitespace rule): one new file in every store, written at the next `run start`. Only paths under `runs/` lose whitespace checking.
- D (redispatch): a redispatched or resumed sub-ticket now runs only the checkers with no row on its commit. The merge rule is unchanged: CI `PASS`, `APPROVE` and `VERIFIED`, all on the current head. A row is kept only for the same commit, and a sub-ticket with every row passing goes straight to the merge.
- E (init and compose): a throwaway-store `init` that would have created an instance is now refused. A missing briefing now gives exit 2, not exit 1.
- F (relative paths): absolute values are unchanged. A relative value moves from the harness checkout to the caller's directory. A caller that relied on the old behaviour would now find a different store. The workflows pass absolute paths.
- G (suite): test files only.

Protected paths this change touches:
- harness: `factory/cli.py`, `factory/store.py`, `factory/instance.py`, `factory/compose.py`, `factory/subtickets.py`, `factory/workflows/build.js` and `factory/workflows/intake.js`.

Not touched: `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `factory/instance.template.yaml`, `factory/prompts/**`, `docs/prompts/**`, `.factory/**`, `~/dev/nanobot-upstream/**` and `~/.nanobot/**`.

Guardrail paths: three existing test files change, listed under Tests to change. That is part G's own request (H8) plus one assertion that part D changes on purpose. New tests go in new files. No agent prompt or skill changes.

Gate policy: within the small-fix pre-approval. There is no routing, gate or merge-rule change, and no check is loosened. The harness-lock refusal is untouched and keeps its tests. Every part is reversed by moving the runtime back. The runtime is the pinned checkout of the harness that runs tickets.

Acceptance needs `node` on `PATH` (checked with v24.14.0) and `TMPDIR` outside any git work tree. The second need is real: the suite's test of `init` outside a git repo writes into whatever repo encloses its temporary directory (ESCALATIONS).

## Operator steps

These steps come after the merge, once the runtime has moved to a revision with this change and each instance has accepted it with `--accept-harness <revision>`.

1. This repo: the next `run start` writes `.factory/state/.gitattributes`. Commit it with the store. Check: `git check-attr whitespace -- .factory/state/runs/run-0102-verifier/diff.patch` prints `whitespace: unset`.
2. Nanobot instance: its next `run start` writes its store's `.gitattributes`. The Driver session that runs that instance commits it with that store.

=== design.md
## Proposed change

### Size and seams (NEEDS-SPLIT)

About 650 changed lines in all, roughly half of them new tests. That is over one reviewable PR. Each H-item is a natural seam. The planner may build one sub-ticket per lettered part. The suggested grouping is four seams, each holding whole H-items that touch the same code:

| Seam | Parts | About | Scenarios |
|---|---|---|---|
| S1, resolve verbs and re-plan | A (H1), H (H9), I1-I2 | 220 lines | every `human-resolution` scenario except the two redispatch ones; both `sub-ticket-planning` scenarios; "The README describes the new resolve verbs" |
| S2, dispatcher and redispatch | B (H2), D (H4), I1 | 170 lines | every `build-dispatch` scenario; "A redispatch after a killed reviewer keeps the verifier's passing rows"; "A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval" |
| S3, store and instance setup | C (H3), E (H6), F (H7), I1, I3 | 190 lines | every `store-setup` scenario; "The README says relative paths resolve from the caller's directory" |
| S4, suite on an edited checkout | G (H8), I1 | 60 lines | both `harness-suite` scenarios |

Every seam adds its clause to changelog entry 51 and runs "The change adds no whitespace errors". "The changelog records the change in order" passes only once all four clauses are in, so it is NEW for the last seam to merge. Every seam edits `docs/changelog.md`, and S1, S2 and S3 all edit `factory/cli.py`, so no seam is parallel-safe. None depends on another's code.

**A. `--ruling` accepts a BLOCKED park** (H1; `factory/cli.py` `resolve`)
- A1. In the `--ruling` branch, accept a parked ticket whose reason starts with `ESCALATE` or `BLOCKED`. For `BLOCKED` the target is `ready-for-implementer`. `ESCALATE` keeps today's targets. Keep the `use --answer` refusal for NEEDS-HUMAN and CLARIFY parks. The other refusal becomes `--ruling applies to an ESCALATE or BLOCKED park; <id> is <state> (<reason>)`.
- A2. Nothing else changes. The ruling is copied to the next `approvals/<id>/ruling-<n>.md`, the round is not touched, and compose already hands the ruling to the implementer.
- A3. New test file `tests/factory/test_resolve_rulings.py`, driven through `bin/factory` on scratch stores. It covers the BLOCKED ruling's state, unchanged round, ruling file and implementer input, and the ESCALATE routes as before.

**B. A park reason always carries the error** (H2; `factory/workflows/build.js` and `factory/workflows/intake.js`, `clerk()` only)
- B1. In the no-JSON branch, `stderr` becomes `res.stderr || \`exit ${res.exit}, no JSON on stdout\``.
- B2. After the existing line that copies `res.stderr`, add: when `parsed.ok === false` and `parsed.stderr` is empty, set `parsed.stderr` to `parsed.error`, else `` `exit ${res.exit}, no error text` ``.
- B3. Leave every reason template (`<prefix>: ${x.stderr || ''}`) as it is. With B1 and B2 none of them can end blank. A refused archive now parks as `archive: no spec store (factory init not run)`.

**C. Run records are exempt from whitespace checks** (H3; `factory/store.py` and `factory/cli.py`)
- C1. Add `STORE_GITATTRIBUTES`: a comment line saying run records embed verbatim diffs and outputs whose whitespace is not the store's to fix, then the line `runs/** -whitespace`. Add `ensure_gitattributes(root)` with the same semantics as `ensure_gitignore`. An absent or empty file gets the block. An existing file keeps its own lines and gains only the non-comment lines it lacks.
- C2. Call it from `init_cmd`, beside `ensure_gitignore`. Put `.gitattributes` first in `written` when it was absent, as `.gitignore` already is. Also call it from `run_start`, beside `ensure_gitignore` (line 222).
- C3. New test file `tests/factory/test_store_setup.py`, shared with parts E and F. It covers: the file written by `init` and by `run start`; existing lines kept and nothing duplicated; and `git diff --check` exempting a committed `runs/` record but not another store file.

**D. A redispatch keeps rows that passed** (H4; `factory/cli.py` `resolve`, `factory/workflows/build.js` `buildOne`)
- D1. In the `--redispatch` branch, set aside `reviewer.yaml` unless its status is `APPROVE`. Set aside `verifier.yaml` and `ci.yaml` together unless the verifier is `VERIFIED` and ci is `PASS`. Keep the `superseded-<n>/` naming. Create the directory only when something moves. Log `results.superseded` with the roles moved. Update the comment above the branch.
- D2. In `buildOne`, record whether the implementer ran in this pass of the loop. When it did, run both checkers, as today. When the loop entered at `checks-in-flight` (a redispatch or a resumed sub-ticket), first run `results show ST` through the clerk. Run the reviewer when `missing` contains `reviewer`. Run the verifier when `missing` contains `verifier` or `ci`. A refused `results show` parks with `harness-bug: results show: <error>`. With no checker to run, go straight to `ticket join`.
- D3. New test file `tests/factory/test_redispatch_rows.py`. It covers a KILLED reviewer with a passing verifier, a SPEC-DEFECT verifier with an approving reviewer, all rows passing (nothing moved, no directory created) and no rows at all.

**E. No half instance; a missing briefing refuses** (H6; `factory/cli.py` `init_cmd`, `factory/compose.py` `compose`)
- E1. In `init_cmd`, when `instance.yaml` does not exist, build its text, load it in memory and compute the store in use from it. If that is not the instance's own store, refuse with exit 2 before writing anything: `factory init: <instance> has no instance.yaml, and FACTORY_STATE names another store (<store>); create the instance with FACTORY_STATE unset, then init that store`. Update the docstring.
- E2. In `compose`, before reading the briefing, refuse with `store.Refused` when `<instance>/context.md` is not a file: `<path> is missing: it is the role-context block every role reads first; run factory init with FACTORY_STATE unset to create it from the template`. No `input.md` is written.
- E3. Tests in `tests/factory/test_store_setup.py`.

**F. Relative environment paths resolve from the caller's directory** (H7; `factory/instance.py`, `factory/store.py`, `factory/cli.py`)
- F1. Add `instance.env_path(name) -> Path | None`. It returns None when the variable is unset or empty. Otherwise it applies `expanduser()`, joins a still-relative path onto `caller_cwd()`, and returns `.resolve()`.
- F2. Use it for `FACTORY_INSTANCE` in `find` and `init_cmd`, for `FACTORY_REPO` in `repo_root`, and for `FACTORY_STATE` in `instance.state_root` and `store.state_root`. `not_found_message` keeps quoting the raw value. Update the module docstring of `factory/instance.py`.
- F3. Tests in `tests/factory/test_store_setup.py`, through `factory paths`.

**G. The suite runs mid-edit** (H8; tests only)
- G1. New file `tests/factory/clean_harness_cli.py`, not collected because it is not named `test_*`. It runs the CLI as `bin/factory` does. It sets `FACTORY_CWD` to the working directory, changes into the harness checkout (two levels above the file), and puts it first on `sys.path`. It replaces `factory.instance.harness_changes` with a function that returns `[]`, then exits with `factory.cli.main(sys.argv[1:])`. Its docstring says it is test-only and stubs only the uncommitted-edit refusal (C.4). The lock comparison (C.2, C.3) still runs.
- G2. `tests/factory/test_harness_lock.py` `cli`: when `harness` is this checkout and the subcommand is neither `init` nor `paths`, run `[sys.executable, <clean_harness_cli.py>, *argv]`. The subcommand is the first argument that is not `--accept-harness` or its value. Otherwise run `harness/bin/factory`, as today. Clone cases, including the uncommitted-edit refusal tests, keep the clone's real `bin/factory`. Replace module docstring lines 8-10 with that rule.
- G3. `tests/factory/test_instance.py` `cli`: run the launcher unless `argv[0]` is `init` or `paths`. Those two commands are exempt from the lock and keep exercising `bin/factory`'s own hand-over of the caller's directory. Add `import sys`.
- G4. A prototype of G1-G3 in a clone with an uncommitted edit printed `215 passed` (Evidence).

**H. Re-plan after a failed parent-close check** (H9; `factory/subtickets.py`, `factory/cli.py`)
- H1. `subtickets.parse(planner_output, parent, existing=())`. `existing` holds the ids of the parent's sub-tickets already in the store. Number new sub-tickets from the highest existing index plus 1, or from 1 when there are none. Refuse a head label that is in `existing`: `<label>: <label> is already a sub-ticket of <parent>; give the new sub-ticket another id`. In `Depends on:`, a reference that names an existing sub-ticket is kept as a dependency. Check that after the new-id and label lookups and before the "not a sub-ticket of this plan" refusal. Update the module docstring.
- H2. `subticket_add` passes the parent's existing sub-ticket ids. Its other checks are unchanged.
- H3. `resolve`: add `--replan FILE`, tried after `--redispatch` and before `--close`. Refuse unless the ticket is parked. Refuse when it has no sub-tickets: `--replan applies to a parent with sub-tickets; <id> has none`. Refuse when any sub-ticket is not `merged`, naming each one with its state: `--replan needs every sub-ticket merged: T-0001.2 is closed`. Otherwise copy FILE to the next `approvals/<id>/ruling-<n>.md` and move the ticket to `ready-for-planner` with kind `replan`, the ruling path in the record, and the round unchanged. Add `a.replan` to the modes that `--decision` refuses. Add `--replan F` to the "resolve needs one of" message.
- H4. No change to `compose` or `build.js`. The planner already receives every ruling, and `build.js` runs Plan from `ready-for-planner`, then `subticket add --run`, which now numbers after the merged sub-tickets.
- H5. New test file `tests/factory/test_replan.py`. It covers: the re-plan move, the ruling, the planner input, the not-all-merged refusal and the no-sub-tickets refusal; numbering after existing sub-tickets; a dependency on a merged sibling; the reused-label refusal with nothing written; and a first plan still numbered from `.1`.

**I. Documents**
- I1. `docs/changelog.md`: after entry 50 and before `Declined:`, add entry `51. After issue #39 (2026-10-04), a batch of harness defects found in real runs:`. Each seam adds one clause. The seam that merges first creates the entry, and later seams add their clause to it without a new number. Between them the clauses must use each of these words: `BLOCKED`, `--replan`, `next free`, `error text`, `redispatch`, `-whitespace`, `context.md`, `relative` and `uncommitted`.
  - S1: `resolve --ruling` also takes an implementer's BLOCKED park and returns the sub-ticket to its implementer at the same round, with the ruling in its input. `resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner, with F as a ruling. Sub-tickets that a later plan adds take the next free ids and may depend on merged ones.
  - S2: a park reason always ends with the failing command's error text. The workflows fall back to the refusal's JSON `error`, then to the exit code. A redispatch sets aside only the rows that did not pass, and the build re-runs only the checkers with no row on the commit.
  - S3: the store's `.gitattributes` marks run records `-whitespace`, written by `init` and `run start`. `init` refuses to create an instance on a throwaway store, and a missing `context.md` refuses a compose with exit 2. A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory.
  - S4: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested.
- I2. (S1) `README.md`, "Where a human decides", Unstick row: `--ruling F` (a role escalated) becomes `--ruling F` (a role escalated, or an implementer reported itself blocked). Add `` · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) ``. In the "Gap, as of today" paragraph, delete its first two sentences. The tripwire sentence then reads: "A ticket the tripwire parked returns with a plain `ticket transition` to the state its record names as `parked.from`, once the operator has checked the named files; a checker park can use `resolve --redispatch` instead."
- I3. (S3) `README.md`, the "How the harness finds a target" paragraph: append "A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` is taken from the directory the command runs in."
- I4. Each seam that edits `README.md` sets the status-header date to its merge date.
- I5. `docs/design.md` and `dev/build-harness.spec.md`: no change. The design already states the BLOCKED ruling (line 98), the re-plan under the same parent (line 100), re-dispatching only the killed role (line 102) and comment-only ledger rows (line 696). The build spec's line 314 already sends a re-plan through `ready-for-planner`. Its `--amend-spec` stays unbuilt and out of scope.

## Tests to change

- `tests/factory/test_shepherd.py` `test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix`. Part D keeps a reviewer row that passed, so:
  - line 585 expects `f.results(st) == {"reviewer": "APPROVE"}` and `superseded-1` holding `["ci.yaml", "verifier.yaml"]`;
  - line 587, which re-runs the reviewer, is removed;
  - the docstring's "the old rows are set aside" becomes "the rows that did not pass are set aside".
- `tests/factory/test_harness_lock.py`: the `cli` helper and module docstring lines 8-10 (part G2). No assertion changes.
- `tests/factory/test_instance.py`: the `cli` helper and one import (part G3). No assertion changes.

I read the other tests that touch what this change affects. `tests/factory/test_spec_store.py` line 151 checks only that a second `init` writes nothing, which stays true. The `init` tests in `test_instance.py` lines 74-123 check `.gitignore` entries and named files, not the store's full file list. Every plan in the suite starts a parent's sub-tickets at `.1`, which part H keeps. I could not grep the whole suite for exact listings of a store's files after `run start`, because shell access ended mid-investigation. The scratch-directory change made the same kind of write at `run start` (`.gitignore`, changelog 50) and changed no test.

=== specs/human-resolution/spec.md
## ADDED Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Run with `node` on `PATH` and with `TMPDIR` unset or outside any git work tree. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, which the next planner input SHALL contain; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Re-plan: add one fix')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

=== specs/sub-ticket-planning/spec.md
## ADDED Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

=== specs/store-setup/spec.md
## ADDED Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

=== specs/harness-suite/spec.md
## ADDED Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
Run with `TMPDIR` unset or outside any git work tree: the suite's own `init` tests expect a temporary directory that is not inside a repository.
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1)`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Every scenario after the first needs the first scenario's GIVEN block run once. It writes `${TMPDIR:-/tmp}/t0023-parent.sh`, `t0023-closed.sh` and `t0023-wf.mjs`. Every command runs from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH` and `TMPDIR` outside any git work tree. Each "today" result below came from running the GIVEN block and then the WHEN verbatim on `main` at `67447b1`, under a throwaway `HOME`. The exceptions are noted.

- A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling → NEW. Today it prints `exit=2 parked pr=0`, `ruling=missing`, `in_input=0`. The ruling is refused, and the implementer cannot start on a parked ticket.
- A ruling on a critic ESCALATE still returns the ticket to the critic → REGRESSION. Today it prints `exit=0 ready-for-critic`.
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note → NEW. Today it prints `exit=2 parked` and `in_input=0`, because `--replan` is not an option.
- A re-plan is refused while a sub-ticket is not merged → NEW. Today it prints `names=0`: the refusal is argparse's unknown-option error, which names no sub-ticket. Then it prints `parked spec-v1.yaml `.
- A redispatch after a killed reviewer keeps the verifier's passing rows → NEW. Today it prints `kept: ` and `set aside: ci.yaml reviewer.yaml verifier.yaml `.
- A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval → NEW. Today it prints `kept: ` and `set aside: ci.yaml reviewer.yaml verifier.yaml `.
- A later plan's sub-tickets take the next free ids and may depend on a merged sibling → NEW. Today it prints only `"ready": []`. The add is refused (`ST-1: depends on T-0001.2, which is not a sub-ticket of this plan`), so no id or dependency line is printed.
- A plan that reuses an existing sub-ticket id is refused and writes nothing → REGRESSION. Today it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml ` (refused as `T-0001.1 already exists`). After the change it is refused by the reused-label check, not by `already exists`, and the reused label must never silently become `T-0001.3`.
- A refused archive or sub-ticket add parks with the refusal text → NEW. Today it prints `park: archive: `, `start: planner`, `park: harness-bug: subticket add: `.
- A refused run start during intake parks with the refusal text → NEW. Today it prints `start: triage`, `park: harness-bug: run start triage: `.
- A command that prints no JSON parks with its exit code → NEW. Today it prints `park: archive: `.
- A redispatched sub-ticket runs only the checker whose row was set aside → NEW. Today it prints `start: reviewer`, `start: verifier`, `park: stub stop`.
- After an implementer run both checkers run → REGRESSION. Today it prints `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`.
- Run records in a store pass whitespace checks and other store files do not → NEW. Today it prints `runs=2`, `other=2`.
- A run start adds the whitespace rule to an existing store → NEW. Today it prints `rule=0`.
- init refuses to create an instance on a throwaway store and writes nothing → NEW. Today it prints `exit=0 instance=written store=written names_state=0`.
- A missing briefing refuses the compose with exit 2 → NEW. Today it prints `exit=1 input=none names_context=1`, from the uncaught `FileNotFoundError`.
- Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory → NEW. Today it prints `state=0 instance=0 repo=0`.
- An absolute FACTORY_STATE is used as given → REGRESSION. Today it prints `absolute=1`.
- The harness suite passes with an uncommitted harness edit → NEW. Today it fails 23 tests. That figure is from the Evidence run, which used a fresh clone and `uv sync --frozen` instead of the symlinked `.venv`, and printed `23 failed, 192 passed`. I also ran this WHEN verbatim. That run is invalid, because `TMPDIR` pointed inside this repository (ESCALATIONS). It printed `27 failed, 188 passed`. The extra four come from that mistake, so I do not quote 27 as the baseline.
- The uncommitted-edit refusal still holds on an instance's own store → REGRESSION. Today it prints `exit=2`, then `has uncommitted changes:`.
- The changelog records the change in order → NEW. Today it prints `50 CONTIGUOUS` and then `0`. The `0` is derived, not run in this exact form: with no entry 51, `sed` prints nothing and `grep -c .` counts 0.
- The README describes the new resolve verbs → NEW. Today it prints `replan=0 gap=1`.
- The README says relative paths resolve from the caller's directory → NEW. Today it prints `0`.
- The change adds no whitespace errors → REGRESSION. Today it prints `exit=0` (empty range).

Out-of-scope observations:
- `resolve --ruling` on a park reason `ESCALATE from reviewer` sends the sub-ticket to `ready-for-critic`, because every non-planner ESCALATE goes there (`factory/cli.py`, the `--ruling` branch). The design returns a reviewer ESCALATE to the implementer with the round reset (`docs/design.md` line 102).
- `tests/factory/test_instance.py` `test_init_refused_outside_a_git_work_tree` (lines 126-131) assumes `tmp_path` is outside any repository. When it is not, `init` succeeds against the enclosing repository's instance and writes into it.
- `dev/build-harness.spec.md` line 314 describes `--amend-spec` on a parked parent, which is not built. This change adds `--replan` beside it without amending that text.
