## Problem

The spec factory runs each requested change through a chain of AI agents. The harness is the code that moves a piece of work, a ticket, from agent to agent and keeps its records in a folder called the store. Eight harness defects strand the operator's tickets or produce records that mislead them. All eight were hit in real runs on 2026-10-03 and 2026-10-04. A ninth item asks for a fix to code that does not exist, and it is cut.

A ticket is parked when the harness stops and waits for a human. `factory resolve` is the command a human runs to move a parked ticket on. A sub-ticket is one unit of a ticket's plan, built on its own branch and merged on its own. The parent-close check is one final verifier run on the merged result. It checks the whole spec after every sub-ticket has merged. The items keep the requester's ids, H1 to H9.

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

Checked on `main` at `67447b1`, which is still the head of `main`. Every "prints" below comes from running the command on that commit, unless it says otherwise.

- **H1.** `factory/cli.py` lines 748-751 refuse `--ruling` unless the park reason starts with `ESCALATE`. The store log shows the hand path. Line 353 parks `T-0012.4`, a sub-ticket of this repository, with `"reason": "BLOCKED from implementer"`. Line 370 moves it `parked → ready-for-implementer` `by dphang` with a plain transition. No ruling file was written. The scenario "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" prints `exit=2 parked pr=0`, `ruling=missing` and `in_input=0` today. That means the ruling is refused, no file is written, and nothing reaches the implementer. Composing an agent's input already hands every `approvals/<id>/ruling-*.md` file to the implementer (`factory/compose.py` lines 190-191), so only the refusal is missing. The design already says BLOCKED returns to its role with the ruling, at the same round (`docs/design.md` line 98).
- **H2.** Five parks in this store's log have a blank reason. Line 605 has `harness-bug: subticket add: `. Lines 639, 727, 827 and 932 have `archive: `. They belong to T-0014, T-0016, T-0018 and T-0020, four parent tickets that parked at their close. The store has no `openspec/` tree, so each archive was refused with `no spec store (factory init not run)`. A refusal prints that text on stderr. It also prints it as the `error` field of a JSON line on stdout (`factory/cli.py` lines 1170-1173). The workflow scripts build each reason from the clerk's relayed stderr only. The clerk is the small agent that runs one store command and relays its output. The relevant lines are `` `archive: ${arch.stderr || ''}` `` (`factory/workflows/build.js` line 256), 18 more sites in `build.js` and 7 in `intake.js`. I ran each workflow script under node, with a stub clerk that relays stdout but an empty stderr. It printed `park: archive: `, `park: harness-bug: subticket add: ` and `park: harness-bug: run start triage: `. Each reason is blank even though the refusal text was on stdout.
- **H3.** The parent-close verifier for T-0012 (`runs/run-0102-verifier/output.md` lines 47-49) reported its whitespace scenario `exit=2`. Exit 2 means `git diff --check` found whitespace errors. Every reported path was a store run record (`diff.patch`, `input.md`), and the same range with the store excluded exited 0, which means no errors. A blank context line in a diff is a single space, which `git diff --check` reports as trailing whitespace. No code writes a store `.gitattributes` today. In a scratch repo, I committed a run record with trailing spaces, and `git diff --check` exited 2. After a committed `.factory/state/.gitattributes` holding `runs/** -whitespace`, the record was exempt, and a trailing space in a file outside `runs/` was still reported. The rule works as intended. The scenario "Run records in a store pass whitespace checks and other store files do not" prints `runs=2` and `other=2` today: both commits report whitespace errors.
- **H4.** `resolve --redispatch` moves every `results/<head>/*.yaml` into `superseded-<n>/`, whatever its status (`factory/cli.py` lines 761-779). The build then runs both checkers again (`build.js` lines 146-155). The requester's evidence comes from the retrospective trial of 2026-10-04, a trial review of this repository's own store. For T-0012.4 the store holds `results/010d1b0…/superseded-1/` with `reviewer.yaml` `KILLED` (run-0076), `verifier.yaml` `VERIFIED` and `ci.yaml` `PASS` (both run-0077). That verifier result was valid for that commit and was thrown away. The trial's second case, T-0012.5 (run-0073), had `ci.yaml` `FAIL`. That gate row was itself wrong, because of a parser bug fixed since, so the rule below re-runs it. So one of the two runs was wasted, not both.
- **H6.** Reproduced in a scratch git repo. `FACTORY_STATE=$T/s bin/factory init --repo-name demo` exited 0 and created `.factory/instance.yaml` with no `context.md`. It wrote `context.md` only for the instance's own store (`factory/cli.py` lines 841-850). `run compose` then printed `factory: FileNotFoundError: … .factory/context.md` and exited 1. That crash comes from `factory/compose.py` line 85, which reads the file with no check.
- **H7.** Reproduced with `factory paths`, which writes nothing. From a temporary directory `$T`, `FACTORY_STATE=rel/store` printed `"state": "/Users/dphang/dev/spec-factory/rel/store"`. That is the harness checkout, not `$T`. `FACTORY_REPO=rel` gave `…/spec-factory/rel/.factory/state`. Running from `tests/factory/fixtures` with `FACTORY_INSTANCE=instance` printed `"instance": null`, so the instance was not found. The cause is that `bin/factory` changes into the harness checkout before Python runs. The caller's directory survives only as `FACTORY_CWD`.
- **H8.** Reproduced. In a clone of `67447b1`, under a throwaway `HOME` and after `uv sync --frozen`, the suite printed `215 passed` clean. After one appended comment line in `factory/status.py`, it printed `23 failed, 192 passed in 139.24s`: 17 in `test_harness_lock.py` and 6 in `test_instance.py`. All 23 run this checkout's `bin/factory` against an instance's own store. The harness-lock check refuses every such command while the running checkout has an uncommitted harness edit (`factory/instance.py` lines 137-139). The test module says so by design (`tests/factory/test_harness_lock.py` lines 8-10). I prototyped the change described in part G in that clone, with the edit still in place. It printed `215 passed in 137.07s`. The acceptance scenario's exact command, run today, prints `23 failed, 192 passed in 135.15s`.
- **H8, where the suite's temporary files go.** Four tests in `test_instance.py` assume their temporary directory lies outside every git repository and every instance. A clean clone run with `TMPDIR` inside this repository printed `4 failed, 211 passed`. The four are `test_init_refused_outside_a_git_work_tree`, `test_command_outside_any_instance_refused_and_writes_nothing`, `test_no_fallback_even_with_a_store_named` and `test_paths_outside_any_instance`. The suite scenario therefore gives the suite its own temporary directory under `/tmp`.
- **H9.** `subtickets.parse` numbers a plan's sub-tickets from 1 (`factory/subtickets.py` line 48, `enumerate(heads, 1)`). It refuses a dependency on `<parent>.<n>` that is not in the same plan (lines 84-85). The scenario "A later plan's sub-tickets take the next free ids and may depend on a merged sibling" prints only `"ready": []` today, because the add is refused. No `resolve` mode leaves a parked parent for planning. `build.js` runs the planner only from `ready-for-planner` (line 191). The routing table already allows `parked → ready-for-planner` (`.factory/instance.yaml` line 61). `dev/build-harness.spec.md` line 314 already describes the re-plan as going back to `ready-for-planner`, with "the planner's new sub-tickets take the next free ids under the same parent, merged ones stay `merged`". The planner's input today holds the approved spec, the decision log and the rulings (`factory/compose.py`, the `planner` branch). It does not list the parent's existing sub-tickets, so a re-planning planner could not name a merged sibling as a dependency.
- **H5 (cut).** No harness code builds the marker ledger. Changelog entry 44 (`docs/changelog.md` line 48) records it as design only. The design text already says "one row per `factory:` comment" (`docs/design.md` line 696). The wrong row came from a ledger built outside the harness for the retrospective trial.

## Root cause

- H1: `factory/cli.py` `resolve`, the `--ruling` branch (lines 747-755). Only `ESCALATE` parks are accepted.
- H2: `clerk()` in `factory/workflows/build.js` (lines 41-56) and `factory/workflows/intake.js` (lines 50-64). Neither falls back to the JSON `error` field or to the exit code when the relayed stderr is empty.
- H3: `factory/store.py` writes the store's `.gitignore` (`ensure_gitignore`) and nothing that exempts `runs/` from whitespace checks.
- H4: `factory/cli.py` `resolve`, the `--redispatch` branch, sets every row aside. `build.js` `buildOne` runs both checkers whenever it reaches `checks-in-flight`.
- H6: `factory/cli.py` `init_cmd` writes `instance.yaml` before it knows whether the store is the instance's own. `factory/compose.py` `compose` line 85 reads `context.md` with no existence check.
- H7: `factory/instance.py` lines 46, 72 and 89, `factory/store.py` line 40 and `factory/cli.py` line 829 call `Path(env).expanduser().resolve()`. That resolves a relative path against the process's working directory, which `bin/factory` has set to the harness checkout.
- H8: `factory/instance.py` `guard`, design item C.4, by design. The tests run the real check for cases that are not about it.
- H9: `factory/subtickets.py` `parse` numbers from 1 and knows nothing of existing sub-tickets. `factory/cli.py` `resolve` has no mode that moves a parked parent to `ready-for-planner`. `factory/compose.py` gives the planner no list of the parent's existing sub-tickets.

## Out of scope

- Moving the store off `main`. The requester excluded it, and it waits for the operator.
- H5, the marker ledger matching only comments. No harness code builds the ledger. The rule goes to the ticket that builds the retro: match comment leaders only, per `docs/coding.md` rule 3.
- The requester's `parked → planned` edge and a human-written plan that skips the planner (Decisions).
- Re-planning while any sub-ticket is not merged, for example after a human closed one. Spec amendment during a re-plan (`--amend-spec` in `dev/build-harness.spec.md` line 314).
- Forcing a re-run of a checker whose row passed.
- Keeping the first plan in `plans/<id>.md` and the change folder's `tasks.md` after a re-plan. Both hold the latest plan. The earlier plan stays in its planner run's `output.md`.
- The four `test_instance.py` tests that assume their temporary directory lies outside every repository and instance. The suite scenario avoids that assumption; it does not fix it (Out-of-scope observations in verification.md).
- `bin/factory`, `.factory/**`, `factory/instance.template.yaml` and the routing table: no change. Also out: `docs/design.md`, which already prescribes each behaviour here (lines 98, 100, 102 and 696), `docs/prompts/**` and every agent prompt.
- The Nanobot instance's files, including its hand-made `T-0002.9`.

## Open questions

none

## Decisions

- `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
- `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
- On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
- Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
- A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
- A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
- The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
- `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
- A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
- The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
- The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
- The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
- The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.

## Risk

Blast radius, by part:
- A and I (resolve): two new paths out of a park, through an existing routing edge each. Every existing `resolve` mode keeps its refusals. The planner's input gains one section, only for a ticket that already has sub-tickets.
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

Acceptance needs `node` on `PATH` (checked with v24.14.0). The suite scenario writes one temporary directory under `/tmp` and removes it.

## Operator steps

The factory runs from a pinned copy of the harness, called the runtime. Each repository the factory serves is an instance, with its own settings and store. An instance adopts a new harness commit only when the operator accepts it with `--accept-harness <commit>`; until then the harness refuses to run there. These steps come after the merge, once the runtime has moved to a commit with this change and each instance has accepted it.

1. This repository: the next `run start` writes `.factory/state/.gitattributes`. Commit it with the store. Check: `git check-attr whitespace -- .factory/state/runs/run-0102-verifier/input.md` prints `.factory/state/runs/run-0102-verifier/input.md: whitespace: unset`. That means git no longer checks whitespace in run records. Before the file exists it prints `whitespace: unspecified`.
2. Nanobot instance: its next `run start` writes its store's `.gitattributes`. The Driver session, the Claude Code session that runs that instance, commits it with that store.

