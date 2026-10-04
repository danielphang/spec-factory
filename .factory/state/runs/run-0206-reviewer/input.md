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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0206-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0206-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0206-reviewer/wt` (branch `factory/T-0023.2`, base `2e61b852d1da27a85208eb94c8d10b8a5557e2c7`, head `a78de4b5a03a3c2f87e9976542035fb4a1ab0f07`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0023.2

## T-0023-S1 / Resolve verbs: a ruling on a BLOCKED park, and re-plan after a failed parent close (parts A and I)
Depends on: T-0023-S4
Parallel-safe: no (edits `factory/cli.py` `resolve`, `factory/compose.py`, `README.md` and `docs/changelog.md`, which siblings also edit)

Parent: T-0023 approved spec v2 (issue #39). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A (H1), A1 to A3; part I (H9), I1 to I5; part J1's S1 clause; J2; J4 for this merge.

Notes for the implementer, checked on `main` at `1ab9540`:
- A1. `resolve` starts at `factory/cli.py:705`. The `--ruling` branch is `:746-754`. Its refusal text is at `:750`, and the target is chosen at `:751`.
- I3. The `--decision` refusal is at `:709`. The "resolve needs one of" message is at `:785`. The resolve options are defined at `:1129-1133`. Add `--replan` after `--redispatch` and before `--close`, as I3 says.
- I1. `subtickets.parse` is at `factory/subtickets.py:33`. The numbering is the `enumerate(heads, 1)` at `:48`. The "not a sub-ticket of this plan" refusal is at `:84-85`. Update the module docstring.
- I2. `subticket_add` is at `factory/cli.py:392`, and it calls `subtickets.parse` at `:407`. `store.subtickets_of` is at `factory/store.py:214`.
- I4. The planner branch of `compose` is at `factory/compose.py:152`. Add nothing to the planner input when the parent has no sub-tickets. I5 tests that.
- J2. In `README.md`, the Unstick row is at `:317`, the "Gap, as of today" paragraph starts at `:321`, and the status-header date is at `:9`. Read "Maintaining this page" (`:421`) before you edit.
- A3 and I5 are new files, `tests/factory/test_resolve_rulings.py` and `tests/factory/test_replan.py`. Drive them through `bin/factory` on scratch stores (`FACTORY_STATE`), never on an instance's own store, so they pass mid-edit. The suite scenario below checks this.

Acceptance (each WHEN verbatim from the parent, run through the wrapper from the worktree root):
- A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
  THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`
- A ruling on a critic ESCALATE still returns the ticket to the critic. REGRESSION.
  WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
  THEN it prints `exit=0 ready-for-critic`
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
  THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`
- A re-plan is refused while a sub-ticket is not merged. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
  THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)
- A later plan's sub-tickets take the next free ids and may depend on a merged sibling. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
  THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`
- A plan that reuses an existing sub-ticket id is refused and writes nothing. REGRESSION.
  WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
  THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `
- The README describes the new resolve verbs. NEW.
  WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
  THEN it prints `replan=1 gap=0`
- Intermediate check, the changelog entry carries this seam's clause. NEW.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
  THEN it prints `51 CONTIGUOUS`, then `4` (`uncommitted`, plus `BLOCKED`, `--replan` and `next free`).
- Intermediate check, the new test files pass. NEW.
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_resolve_rulings.py tests/factory/test_replan.py`
  THEN it exits 0. The files cover the cases listed in A3 and I5, including a first plan still numbered from `.1` and a first plan's planner input with no sub-ticket section.
- The harness suite passes with an uncommitted harness edit. REGRESSION.
  WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
  THEN it prints one line reporting a number of passed tests and no `failed` or `error`
- The change adds no whitespace errors. REGRESSION.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`

Tests to change: none.
Protected paths: harness: `factory/cli.py`, `factory/subtickets.py`, `factory/compose.py`.
Out of scope: the `--redispatch` branch (T-0023-S2); `init_cmd` and the `context.md` check in `compose` (T-0023-S3); `build.js` (I4: no change); a re-plan while any sub-ticket is not merged; `--amend-spec`; the requester's `parked → planned` edge; keeping the first plan's `plans/<id>.md` and `tasks.md`; the reviewer-ESCALATE route (parent Out-of-scope observations); `docs/design.md` and `dev/build-harness.spec.md` (J5: no change).

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: the approved spec v2 of T-0023 (issue #39), in this run's input and at `.factory/state/specs/T-0023.md` with its directory `.factory/state/specs/T-0023/`.

Four sub-tickets, one per seam in the parent's design.md table ("Size and seams"). The parent sizes the change at about 665 lines, half of them tests, and names the seams itself. Each seam holds whole items that touch the same code, so each is one reviewable PR that can be rolled back alone. I did not split further: a sub-ticket per lettered part would add three more merges, and every merge makes the next sibling re-verify.

Order. None of the seams needs another seam's code (parent design.md). But every seam edits `docs/changelog.md` entry 51, three of them edit `factory/cli.py` (S1, S2, S3), two edit `factory/compose.py` (S1, S3) and two edit `README.md` (S1, S3). So none is parallel-safe, and I chain them in one fixed order: S4, then S1, then S2, then S3. The `Depends on:` lines express that order, not a code dependency. A fixed order gives each sub-ticket's changelog check one exact expected count. S4 goes first for two reasons:
- After it merges, an implementer can run the harness suite in a worktree that has uncommitted edits. Today 23 tests fail there (parent Evidence, H8).
- The parent's scenario "The harness suite passes with an uncommitted harness edit" then becomes a REGRESSION check for S1, S2 and S3. That catches any new test file of theirs that would break the suite mid-edit, so S4 does not have to repair siblings' tests later.
The cost: if one seam parks, the seams after it wait.

The store numbers sub-tickets in plan order, so `T-0023-S4` becomes `T-0023.1`, `T-0023-S1` becomes `.2`, `T-0023-S2` becomes `.3` and `T-0023-S3` becomes `.4`. The labels keep the parent's seam names.

I checked the parent's anchors on `main` at `1ab9540`. `git diff --stat 67447b1 HEAD -- factory bin tests docs dev README.md agents` prints nothing, so the parent's evidence, taken at `67447b1`, still holds. A few line numbers have moved by one or two; each sub-ticket's notes give the current ones.

Rules for every sub-ticket:
- Run every command from the root of your worktree, after `uv sync --frozen`, through the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`, with `node` on `PATH`.
- Scenarios that name `t0023-parent.sh`, `t0023-closed.sh` or `t0023-wf.mjs` need the GIVEN block of the parent's first scenario, "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (`specs/human-resolution/spec.md`), run once, verbatim, at column 0. It writes the three files under `${TMPDIR:-/tmp}`. Setting `TMPDIR` to your scratch directory is fine (parent verification.md, round 2).
- The suite scenario "The harness suite passes with an uncommitted harness edit" sets its own `TMPDIR` under `/tmp` and removes it. Run it exactly as written.
- Changelog entry 51 is a single line, like entry 50 (`docs/changelog.md:54`). The parent's changelog scenario reads only the line that starts with `51. `, so each seam appends its clause to that same line. Use the clause wording of parent step J1. The first seam to merge (S4) creates the line after entry 50 and before the blank line above `Declined:` (`:56`). It starts with `51. After issue #39 (2026-10-04), a batch of harness defects found in real runs:`.
- New tests go in new files. Edit an existing test only where your "Tests to change" line names it.

## Parent spec (v2, pinned)

=== proposal.md
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

=== design.md
## Proposed change

### Size and seams (NEEDS-SPLIT)

About 665 changed lines in all, roughly half of them new tests. That is over one reviewable PR. The parts are lettered A to G, then I and J. There is no part H, so that a step id such as I1 never reads as one of the requester's items H1 to H9. The planner may build one sub-ticket per lettered part. The suggested grouping is four seams, each holding whole items that touch the same code:

| Seam | Parts (items) | About | Scenarios |
|---|---|---|---|
| S1, resolve verbs and re-plan | A (H1), I (H9), J1-J2 | 235 lines | every `human-resolution` scenario except the two redispatch ones; both `sub-ticket-planning` scenarios; "The README describes the new resolve verbs" |
| S2, dispatcher and redispatch | B (H2), D (H4), J1 | 170 lines | every `build-dispatch` scenario; "A redispatch after a killed reviewer keeps the verifier's passing rows"; "A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval" |
| S3, store and instance setup | C (H3), E (H6), F (H7), J1, J3 | 190 lines | every `store-setup` scenario; "The README says relative paths resolve from the caller's directory" |
| S4, suite on an edited checkout | G (H8), J1 | 60 lines | both `harness-suite` scenarios |

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
- C2. Call it from `init_cmd`, beside `ensure_gitignore`. Put `.gitattributes` first in `written` when it was absent, as `.gitignore` already is. Also call it from `run_start`, beside `ensure_gitignore` (line 222), which runs after every refusal of `run start`.
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
- G1. New file `tests/factory/clean_harness_cli.py`, not collected because it is not named `test_*`. It runs the CLI as `bin/factory` does. It sets `FACTORY_CWD` to the working directory, changes into the harness checkout (two levels above the file), and puts it first on `sys.path`. It replaces `factory.instance.harness_changes` with a function that returns `[]`, then exits with `factory.cli.main(sys.argv[1:])`. Its docstring says it is test-only and stubs only the uncommitted-edit refusal (design item C.4). The lock comparison (design items C.2 and C.3) still runs.
- G2. `tests/factory/test_harness_lock.py` `cli`: when `harness` is this checkout and the subcommand is neither `init` nor `paths`, run `[sys.executable, <clean_harness_cli.py>, *argv]`. The subcommand is the first argument that is not `--accept-harness` or its value. Otherwise run `harness/bin/factory`, as today. Clone cases, including the uncommitted-edit refusal tests, keep the clone's real `bin/factory`. Replace module docstring lines 8-10 with that rule.
- G3. `tests/factory/test_instance.py` `cli`: run the launcher unless `argv[0]` is `init` or `paths`. Those two commands are exempt from the lock and keep exercising `bin/factory`'s own hand-over of the caller's directory. Add `import sys`.
- G4. A prototype of G1-G3 in a clone with an uncommitted edit printed `215 passed` (Evidence).

**I. Re-plan after a failed parent-close check** (H9; `factory/subtickets.py`, `factory/cli.py`, `factory/compose.py`)
- I1. `subtickets.parse(planner_output, parent, existing=())`. `existing` holds the ids of the parent's sub-tickets already in the store. Number new sub-tickets from the highest existing index plus 1, or from 1 when there are none. Refuse a head label that is in `existing`: `<label>: <label> is already a sub-ticket of <parent>; give the new sub-ticket another id`. In `Depends on:`, a reference that names an existing sub-ticket is kept as a dependency. Check that after the new-id and label lookups and before the "not a sub-ticket of this plan" refusal. Update the module docstring.
- I2. `subticket_add` passes the parent's existing sub-ticket ids, from `store.subtickets_of`. Its other checks are unchanged.
- I3. `resolve`: add `--replan FILE`, tried after `--redispatch` and before `--close`. Refuse unless the ticket is parked. Refuse when it has no sub-tickets: `--replan applies to a parent with sub-tickets; <id> has none`. Refuse when any sub-ticket is not `merged`, naming each one with its state: `--replan needs every sub-ticket merged: T-0001.2 is closed`. Otherwise copy FILE to the next `approvals/<id>/ruling-<n>.md` and move the ticket to `ready-for-planner` with kind `replan`, the ruling path in the record, and the round unchanged. Add `a.replan` to the modes that `--decision` refuses. Add `--replan F` to the "resolve needs one of" message.
- I4. `compose`, the `planner` branch: when `store.subtickets_of(root, tid)` is not empty, append, after the rulings, a section headed `## Sub-tickets already under <tid>`. Its first line reads: "A new plan's sub-tickets are numbered after these. A `Depends on:` line may name any of these ids." Then one line per sub-ticket, in id order: `- <id> / <title>: <status>`. With no sub-tickets, the planner's input is unchanged. No change to `build.js`: it runs Plan from `ready-for-planner`, then `subticket add --run`, which now numbers after the merged sub-tickets.
- I5. New test file `tests/factory/test_replan.py`. It covers: the re-plan move, the ruling, the planner input with its sub-ticket list, the not-all-merged refusal and the no-sub-tickets refusal; a first plan's planner input with no sub-ticket section; numbering after existing sub-tickets; a dependency on a merged sibling; the reused-label refusal with nothing written; and a first plan still numbered from `.1`.

**J. Documents**
- J1. `docs/changelog.md`: after entry 50 and before `Declined:`, add entry `51. After issue #39 (2026-10-04), a batch of harness defects found in real runs:`. Each seam adds one clause. The seam that merges first creates the entry, and later seams add their clause to it without a new number. Between them the clauses must use each of these words: `BLOCKED`, `--replan`, `next free`, `error text`, `redispatch`, `-whitespace`, `context.md`, `relative` and `uncommitted`.
  - S1: `resolve --ruling` also takes an implementer's BLOCKED park and returns the sub-ticket to its implementer at the same round, with the ruling in its input. `resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner, with F as a ruling and the existing sub-tickets listed in its input. Sub-tickets that a later plan adds take the next free ids and may depend on merged ones.
  - S2: a park reason always ends with the failing command's error text. The workflows fall back to the refusal's JSON `error`, then to the exit code. A redispatch sets aside only the rows that did not pass, and the build re-runs only the checkers with no row on the commit.
  - S3: the store's `.gitattributes` marks run records `-whitespace`, written by `init` and `run start`. `init` refuses to create an instance on a throwaway store, and a missing `context.md` refuses a compose with exit 2. A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory.
  - S4: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested.
- J2. (S1) `README.md`, "Where a human decides", Unstick row: `--ruling F` (a role escalated) becomes `--ruling F` (a role escalated, or an implementer reported itself blocked). Add `` · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) ``. In the "Gap, as of today" paragraph, delete its first two sentences. The tripwire sentence then reads: "A ticket the tripwire parked returns with a plain `ticket transition` to the state its record names as `parked.from`, once the operator has checked the named files; a checker park can use `resolve --redispatch` instead."
- J3. (S3) `README.md`, the "How the harness finds a target" paragraph: append "A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` is taken from the directory the command runs in."
- J4. Each seam that edits `README.md` sets the status-header date to its merge date.
- J5. `docs/design.md` and `dev/build-harness.spec.md`: no change. The design already states the BLOCKED ruling (line 98), the re-plan under the same parent (line 100), re-dispatching only the killed role (line 102) and comment-only ledger rows (line 696). The build spec's line 314 already sends a re-plan through `ready-for-planner`. Its `--amend-spec` stays unbuilt and out of scope.

## Tests to change

- `tests/factory/test_shepherd.py` `test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix`. Part D keeps a reviewer row that passed, so:
  - line 585 expects `f.results(st) == {"reviewer": "APPROVE"}` and `superseded-1` holding `["ci.yaml", "verifier.yaml"]`;
  - line 587, which re-runs the reviewer, is removed;
  - the docstring's "the old rows are set aside" becomes "the rows that did not pass are set aside".
- `tests/factory/test_harness_lock.py`: the `cli` helper and module docstring lines 8-10 (part G2). No assertion changes.
- `tests/factory/test_instance.py`: the `cli` helper and one import (part G3). No assertion changes.

I read the other tests that touch what this change affects, and grepped the suite for every listing of a store's or instance's files (`iterdir`, `rglob`, `written`). None needs a change:
- `tests/factory/test_spec_store.py` line 151 checks only that a second `init` writes nothing, which stays true.
- `tests/factory/test_instance.py` line 79 lists `.factory/`, not the store; lines 147 and 157 check `written` on an `init` that runs after the store already has `.gitattributes`.
- `tests/factory/test_harness_lock.py` lines 47 and 69 and `tests/factory/test_instance.py` line 42 snapshot a tree around a refused command, which stops before `run start` writes anything.
- `tests/factory/test_run_scratch.py` line 163 and `tests/factory/test_tripwire.py` line 230 list one run's directory, not the store root.
- Every plan in the suite starts a parent's sub-tickets at `.1`, which part I keeps. No suite test composes a planner input for a ticket that already has sub-tickets.

=== specs/human-resolution/spec.md
## ADDED Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

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
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

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
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
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

Every scenario that names `t0023-parent.sh`, `t0023-closed.sh` or `t0023-wf.mjs` needs the first scenario's GIVEN block run once; it writes those three files under `${TMPDIR:-/tmp}`. Every command runs from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each "today" result below came from running the GIVEN block and then the WHEN verbatim on `main` at `67447b1`, under a throwaway `HOME`. The exceptions are noted. In round 2 I re-ran the changed re-plan scenario and both `harness-suite` scenarios with `TMPDIR` set to my scratch directory, which lies inside this repository, to confirm they hold for a role that follows its scratch rule.

- A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling → NEW. Today it prints `exit=2 parked pr=0`, `ruling=missing`, `in_input=0`. The ruling is refused, and the implementer cannot start on a parked ticket.
- A ruling on a critic ESCALATE still returns the ticket to the critic → REGRESSION. Today it prints `exit=0 ready-for-critic`.
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list → NEW. Today it prints `exit=2 parked` and `in_input=0 listed=0`, because `--replan` is not an option, so the planner cannot start on the parked parent. Run in round 2.
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
- The harness suite passes with an uncommitted harness edit → NEW. Today the WHEN, run verbatim in round 2, prints `23 failed, 192 passed in 135.15s (0:02:15)`. Those 23 are the harness-lock refusals of H8, and the count matches the clone-and-`uv sync` run in Evidence. The `/tmp/t0023-suite.*` directory was gone afterwards.
- The uncommitted-edit refusal still holds on an instance's own store → REGRESSION. Today it prints `exit=2`, then `has uncommitted changes:`. Re-run in round 2.
- The changelog records the change in order → NEW. Today it prints `50 CONTIGUOUS` and then `0`. The `0` is derived, not run in this exact form: with no entry 51, `sed` prints nothing and `grep -c .` counts 0.
- The README describes the new resolve verbs → NEW. Today it prints `replan=0 gap=1`.
- The README says relative paths resolve from the caller's directory → NEW. Today it prints `0`.
- The change adds no whitespace errors → REGRESSION. Today it prints `exit=0` (empty range).

## Responses

- [BLOCKING] 6, Operator steps glosses: FIXED. Operator steps now opens by saying what the runtime is (the pinned copy of the harness), what an instance is (a repository the factory serves, with its own settings and store), and what `--accept-harness <commit>` does. The Driver session is glossed too.
- [SHOULD-FIX] 6/3, H1-H5 used for two things: FIXED. The items keep the requester's ids H1 to H9, and the Problem says so. The parts are now A to G, then I (re-plan, steps I1 to I5) and J (documents, steps J1 to J5). design.md says there is no part H, and why. The seam table, Risk and every step reference use the new letters.
- [SHOULD-FIX] 2, the suite scenario needs `TMPDIR` outside any work tree: FIXED by the second of the critic's options, with the choice written into the command so that no role has to make it. The WHEN now gives pytest a fresh `mktemp -d /tmp/t0023-suite.XXXXXX` as its `TMPDIR` and removes it at the end. I did not take the first option. Bounding git with `GIT_CEILING_DIRECTORIES` fixes only one of the four affected tests. A clean clone run with `TMPDIR` inside this repository printed `4 failed, 211 passed`, and three of those four fail because the instance walk-up finds this repository's `.factory/instance.yaml`, not because of git. Fixing all four needs its own design, so it is an out-of-scope observation. Run verbatim in round 2 with my own `TMPDIR` inside this repository, the new WHEN printed `23 failed, 192 passed`, the H8 baseline, with no extra failures. I also dropped the general "`TMPDIR` outside any git work tree" requirement from the first scenario and from Risk. The critic ran seven scenarios with `TMPDIR` inside the repository and got the stated results. I re-ran three more the same way. Each remaining scenario either builds its own git repository under `mktemp -d` or names its instance and store explicitly, so where `TMPDIR` lies does not change what it finds. I did not run those remaining scenarios that way.
- [SHOULD-FIX] 4, the re-planning planner does not know what merged: FIXED by the second suggestion. New step I4 makes `compose` list the parent's existing sub-tickets, with title and state, in the planner's input. The planner needs the list anyway: without the ids it cannot write the `Depends on: T-0001.2` that step I1 now accepts. A new Decision records this, and rejects asking the human to restate in the note what merged. The re-plan scenario now also checks the list (`listed=2`). Today it prints `in_input=0 listed=0`.
- [NIT] 6, Operator step 1 names a file that does not exist: FIXED. The check names `run-0102-verifier/input.md`, which exists. It quotes the full output line, `….input.md: whitespace: unset`, and the `unspecified` answer before the file is written. Both answers come from a scratch repo in round 2.
- [NIT] 6, Evidence H2 and H3: FIXED. H3 now says exit 2 means `git diff --check` found whitespace errors and exit 0 means none. H2 says T-0014, T-0016, T-0018 and T-0020 are four parent tickets that parked at their close. For "the retro" in H4 I did not use the suggested gloss "the retrospective trial on the Nanobot instance". `.factory/answers/retro-trial-2026-10-04/inputs.md` line 1 reads "Retro inputs: spec-factory instance B store", so the trial reviewed this repository's own store. H4 now says so.

Out-of-scope observations:
- `resolve --ruling` on a park reason `ESCALATE from reviewer` sends the sub-ticket to `ready-for-critic`, because every non-planner ESCALATE goes there (`factory/cli.py`, the `--ruling` branch). The design returns a reviewer ESCALATE to the implementer with the round reset (`docs/design.md` line 102).
- Four tests in `tests/factory/test_instance.py` assume their temporary directory lies outside every git repository and instance: `test_init_refused_outside_a_git_work_tree` (line 126), `test_command_outside_any_instance_refused_and_writes_nothing` (line 203), `test_no_fallback_even_with_a_store_named` (line 213) and `test_paths_outside_any_instance` (line 326). With `TMPDIR` inside an instance's repository, they act on that live instance. The first one runs `init` there, which is how the round-1 writer's run created this repository's `.claude/agents/`, `.factory/state/openspec/` and `.factory/state/decisions.md` (ESCALATIONS).
- `dev/build-harness.spec.md` line 314 describes `--amend-spec` on a parked parent, which is not built. This change adds `--replan` beside it without amending that text.

## PR description (the implementer's output)

Sub-ticket: T-0023.2 (plan label T-0023-S1), "Resolve verbs: a ruling on a BLOCKED park, and re-plan after a failed parent close (parts A and I)". Parent: T-0023, approved spec v2 (issue #39). Branch `factory/T-0023.2`, commit `a78de4b` on base `2e61b85`.

## What changed

A ticket is "parked" when the harness stops and waits for a human, and `factory resolve` is the command a human runs to move it on. Before this change, two common parks had no supported way out. An implementer (the agent that writes the code for one sub-ticket) that reported BLOCKED could not be given a ruling. A parent ticket whose final whole-spec check failed after all its sub-tickets merged could not be sent back for a fix plan. Both now have a `resolve` mode, and both use state changes the routing table already allows.

**Part A (H1): `--ruling` accepts a BLOCKED park.** `factory/cli.py` `resolve`, the `--ruling` branch (lines 750-757):
- A park whose reason starts with `BLOCKED` now returns the sub-ticket to `ready-for-implementer`.
- The round is left as it was. The ruling is copied to the next `approvals/<id>/ruling-<n>.md`, as for ESCALATE. No compose change was needed: the implementer's input already includes every ruling file (`factory/compose.py`, the implementer branch).
- ESCALATE parks route as before: to the planner if the reason names the planner, otherwise to the critic.
- NEEDS-HUMAN and CLARIFY parks are still told to `use --answer`.
- Every other refusal now reads `--ruling applies to an ESCALATE or BLOCKED park; <id> is <state> (<reason>)`.

**Part I (H9): re-plan after a failed parent-close check.** The parent-close check is the last verifier run, on the merged result, after every sub-ticket has merged.
- I1, `factory/subtickets.py` `parse(planner_output, parent, existing=())`. `existing` is the list of the parent's sub-ticket ids already in the store.
  - New sub-tickets are numbered from the highest existing index plus 1. With no existing sub-tickets they still start at 1.
  - A plan head line that reuses an existing id is refused: `<label>: <label> is already a sub-ticket of <parent>; give the new sub-ticket another id`.
  - A `Depends on:` reference that names an existing sub-ticket is kept as a dependency. That check comes after the new-id and label lookups and before the "not a sub-ticket of this plan" refusal.
  - The module docstring now says this.
- I2, `factory/cli.py` `subticket_add` (line 407): it passes the existing ids from `store.subtickets_of`. Its other checks are unchanged.
- I3, `factory/cli.py` `resolve`: new `--replan F`, tried after `--redispatch` and before `--close` (lines 783-796; the option is at line 1149).
  - It is refused unless the ticket is parked: `--replan applies to a parked parent; <id> is <state>`.
  - It is refused when the ticket has no sub-tickets: `--replan applies to a parent with sub-tickets; <id> has none`.
  - It is refused when any sub-ticket has not merged. The message names each one with its state, for example `--replan needs every sub-ticket merged: T-0001.2 is closed`.
  - Otherwise it copies F to the next `approvals/<id>/ruling-<n>.md` and moves the ticket to `ready-for-planner`. The record has kind `replan` and the ruling path. The round is unchanged.
  - `--decision` now refuses `--replan` too, and the "resolve needs one of" message lists `--replan F`.
- I4, `factory/compose.py`, the planner branch (lines 160-164): when the parent has sub-tickets, a section is appended after the rulings. It is headed `## Sub-tickets already under <tid>` and its first line is the one in the spec. Then comes one line per sub-ticket, `- <id> / <title>: <status>`, in id order. With no sub-tickets the planner's input is unchanged. `build.js` is unchanged, as I4 says.

**J1, J2, J4 (documents).**
- `docs/changelog.md`, entry 51: the S1 clause from J1 is appended to the existing single line. There is no new entry number.
- `README.md`, "Where a human decides", Unstick row: `--ruling F` now says "(a role escalated, or an implementer reported itself blocked)". After `--redispatch` there is the J2 text for `--replan F`.
- `README.md`, "Gap, as of today" paragraph: its first two sentences are deleted, and the tripwire sentence is the J2 wording.
- One addition the spec did not spell out: the row's "What you decide" cell gains "a re-plan", so that it matches the new verb.
- J4: the status-header date is already `2026-10-04`, which is today and the expected merge date, so it is unchanged.

**Callers checked (coding rule 2).** `subtickets.parse` has one production caller, `cli.subticket_add`. Its test callers in `tests/factory/test_subtickets.py` (lines 185 and 209) use the default `existing=()`, so their behaviour is the same. `resolve` is reached only from the CLI: `grep -n resolve factory/workflows/*.js` finds nothing. `compose.compose` has one caller, `cli.run_compose`.

## Acceptance results

All commands ran from the worktree root, inside the HOME wrapper. Where a command needed the fixture scripts, `TMPDIR` pointed to my scratch directory, and I first wrote `t0023-parent.sh` and `t0023-closed.sh` there from the parent's GIVEN block, verbatim. I did not write `t0023-wf.mjs`, because none of this sub-ticket's scenarios uses it. Unless noted, the outputs below are from bash. See "Known gaps" for one zsh difference.

| Scenario | Kind | Before (base `2e61b85`) | After (`a78de4b`) |
|---|---|---|---|
| A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling | NEW | `exit=2 parked pr=0` / `ruling=missing` / `in_input=0` | `exit=0 ready-for-implementer pr=0` / `ruling=kept` / `in_input=1` |
| A ruling on a critic ESCALATE still returns the ticket to the critic | REGRESSION | | `exit=0 ready-for-critic` |
| A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list | NEW | `exit=2 parked` / `in_input=0 listed=0` | `exit=0 ready-for-planner` / `in_input=1 listed=2` |
| A re-plan is refused while a sub-ticket is not merged | NEW | `names=0` / `parked spec-v1.yaml ` | `names=1` / `parked spec-v1.yaml ` under bash and sh. zsh prints `names=2` (Known gaps). |
| A later plan's sub-tickets take the next free ids and may depend on a merged sibling | NEW | `"ready": []` only | `"id": "T-0001.3"` / `"depends_on": ["T-0001.2"]` / `"ready": ["T-0001.3"]` |
| A plan that reuses an existing sub-ticket id is refused and writes nothing | REGRESSION | | `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `. The refusal now comes from the reused-label check. `test_replan.py` asserts its text. |
| The README describes the new resolve verbs | NEW | `replan=0 gap=1` | `replan=1 gap=0` |
| Intermediate check: the changelog entry carries this seam's clause | NEW | `51 CONTIGUOUS` / `1` (only S4's `uncommitted`) | `51 CONTIGUOUS` / `4` |
| Intermediate check: the new test files pass | NEW | 14 failed, 6 passed. The 6 that pass are the unchanged behaviours: the two ESCALATE routes, the NEEDS-HUMAN refusal, a first plan's input, first-plan numbering and the unknown-dependency refusal. | `20 passed in 11.25s` |
| The harness suite passes with an uncommitted harness edit | REGRESSION | | `235 passed in 191.97s (0:03:11)`. Afterwards no `/tmp/t0023-suite.*` directory was left. |
| The change adds no whitespace errors | REGRESSION | | `exit=0` |

How the meanings above were read:
- `pr=0` means the round was not touched.
- `ruling=kept` means the ruling file is byte-identical to F.
- `in_input=1` means the ruling text is in the implementer's composed input.
- `listed=2` means both sub-ticket lines appear exactly as specified.
- `4` means the entry contains `BLOCKED`, `--replan`, `next free` and `uncommitted`.

For the "Before" column of the new test files, I copied both files into a clean clone at the base commit and ran them there.

Gate commands, each run exactly as written on `a78de4b`:
- `(export HOME=…; git diff --check main...HEAD)` exited 0. No whitespace errors.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `235 passed in 158.95s (0:02:38)`. That is the 215 tests from before this change plus the 20 new ones.

## Tests added/changed

- New: `tests/factory/test_resolve_rulings.py`, 7 tests (A3).
  - A BLOCKED ruling: the state, the round left at its pre-set value of 1, `parked` cleared, the ruling file, and the ruling in the composed implementer input and its sources.
  - A second BLOCKED ruling takes `ruling-2`.
  - ESCALATE from the critic and ESCALATE from the planner route as before.
  - NEEDS-HUMAN still says `use --answer`.
  - The new refusal text, on another park reason and on an unparked ticket. In both cases nothing is written.
- New: `tests/factory/test_replan.py`, 13 tests (I5).
  - The re-plan move: the JSON result, the history and resolve record, the round unchanged, merged sub-tickets still merged, the ruling file, and the planner input. The input has the ruling before the sub-ticket section and the section's exact text.
  - The refusals: a sub-ticket not merged (nothing written), every unmerged sub-ticket named, no sub-tickets (nothing written), the parent not parked, `--decision` with `--replan`, and the "needs one of" message.
  - A first plan's planner input has no sub-ticket section, and a first plan is still numbered from `.1`.
  - A later plan takes `.3` and `.4`. Its dependencies on a merged sibling, by full id and by the `.1` shorthand, are kept, and `ready-implementers` releases `.3`.
  - Numbering follows the highest existing index, not the count.
  - A reused label is refused with the exact message, and no ticket or spec file is written.
  - A dependency on a sub-ticket that does not exist is still refused.
- Both files drive `bin/factory` on throwaway stores (`FACTORY_STATE` under `tmp_path`), as the plan asks. The suite scenario confirms they pass in a checkout with an uncommitted harness edit.
- Changed: none. No existing test file was touched.

## Known gaps and uncertainties

- **The not-merged refusal scenario prints `names=2` under zsh.** Under bash and sh it prints `names=1`, as specified. The reason is zsh's MULTIOS option: zsh sends stdout both to `/dev/null` and into the pipe in `2>&1 >/dev/null |`. A refused command prints its refusal on stderr and also as the `error` field of a JSON line on stdout, so grep counts two lines. That stdout behaviour already existed (the parent's Evidence for H2). With `setopt NO_MULTIOS`, zsh prints `names=1`. The code is correct; the expected output holds only in a POSIX shell. A verifier that runs scenarios in zsh, as this environment's tool shell does, will see `names=2`.
- **The README now describes behaviour that has not yet run on a real ticket.** "Maintaining this page" says a thing appears above "Where this can go" only after that. I made the J2 edit because the approved spec orders it, and the old "Gap" sentence would otherwise be false once this merges.
- **A pre-existing ambiguity, not introduced here.** If a plan uses `T-0001.n` labels that do not match the ids the store assigns, a `Depends on: T-0001.n` resolves to the assigned id first. An example is labels `T-0001.4` then `T-0001.3`, numbered `.3` and `.4`. With this change that can also happen in a re-plan. The parent's Decisions rejected honouring explicit ids, so I did not change this.
- `factory:` markers added: none.

## Out-of-scope observations

- The parent's own out-of-scope note still holds: `resolve --ruling` on `ESCALATE from reviewer` sends the sub-ticket to `ready-for-critic`. The design (`docs/design.md` line 102) returns it to the implementer instead. I did not touch that route.
- `resolve --replan` writes F as a ruling, and the planner already receives every ruling of the parent, so the planner also sees older rulings from the first plan. That is consistent with how rulings work today. I note it only because a re-plan's input may now include stale rulings.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates were run on the committed head, with the outputs above, and the new tests were shown to fail on base. The one exception is the not-merged refusal scenario, which matches only under a POSIX shell.
ESCALATIONS:
- The scenario "A re-plan is refused while a sub-ticket is not merged" prints `names=2` instead of `names=1` when run under zsh. A verifier using zsh would report a false failure. Under bash or sh, it prints `names=1`. Decide: run this change's scenarios with bash, or, at the next spec revision, amend the scenario to send stderr to a file and grep that file, for example `2>$T23/err >/dev/null; grep -c T-0001.2 $T23/err`, as other scenarios in this spec already do. The harness behaviour that causes it, refusals echoed as JSON on stdout, is by design and out of scope.

## Diff `2e61b852d1da27a85208eb94c8d10b8a5557e2c7...a78de4b5a03a3c2f87e9976542035fb4a1ab0f07`

diff --git a/README.md b/README.md
index 3c085a0..e52cc3f 100644
--- a/README.md
+++ b/README.md
@@ -314,16 +314,14 @@ runs from the same runtime. Each target's runner then accepts the new revision b
 |---|---|---|
 | **File** | `factory ticket new --file <abs path>` | that this request is worth a ticket |
 | **Gate** | `factory approve-spec T-n [--edit F]` · `factory request-changes T-n F` · close | the spec's intent, risk declarations, operator steps, "tests to change"; a gate edit becomes a new spec version and is what gets pinned |
-| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated) · `--redispatch` (re-run the checks on the same commit after an outside fix) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, a re-check, a re-scope, or closing |
+| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, or an implementer reported itself blocked) · `--redispatch` (re-run the checks on the same commit after an outside fix) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, a re-check, a re-plan, a re-scope, or closing |
 | **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included. It appends one dated line to the target's decision log, `decisions.md`, which the spec writer, critic and planner receive with their input | that a decision binds later tickets |
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
-Gap, as of today: an implementer that reports itself blocked has no `resolve` verb. A plain
-`ticket transition --to ready-for-implementer` returns it. A ticket the tripwire parked returns the
-same way, to the state its record names as `parked.from`, once the operator has checked the named
-files; a checker park can use `resolve --redispatch` instead. Everything else is the harness's and
-the scripts': which role runs next, how many rounds, what the checkers receive, when a merge is
-allowed, when the ticket closes.
+A ticket the tripwire parked returns with a plain `ticket transition` to the state its record
+names as `parked.from`, once the operator has checked the named files; a checker park can use
+`resolve --redispatch` instead. Everything else is the harness's and the scripts': which role runs
+next, how many rounds, what the checkers receive, when a merge is allowed, when the ticket closes.
 
 ## What is built and what is not
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 5e0c128..cc1d631 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -52,6 +52,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 48. After issue #36 (2026-10-04): a role's test run overwrote the Nanobot bot's live permission file, so every role now runs tests, scripts and prototypes through a wrapper the composer hands it, which sets a throwaway `HOME`, with gate commands already wrapped and `run_env` for tool caches; and the preamble forbids running anything that could write a protected path outside the repository. A plan's bulleted field lines lost every sub-ticket's dependencies, so the harness now reads `Depends on:` and `Parallel-safe:` lines that start with a list bullet and refuses a sub-ticket with no `Depends on:` line; and the planner prompt shows the three parsed lines at the start of a line and says `yes` means alongside every sibling.
 49. After the 2026-10-04 Nanobot incident, where a role's tests overwrote the live bot's permission file and nothing in the factory noticed: an instance may list files outside the repository under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list, files only, with `~` meaning the account's home and never `HOME`. `run start` records a SHA-256 of each file, or that it is absent, in a per-run baseline that the store's `.gitignore` excludes, and refuses a directory or an entry that is neither absolute nor `~/`. Each run is compared once, when it leaves the in-flight list: at `run finish`, killed runs included, or at a `ticket set` that drops it. A changed `park` file parks the ticket with `tripwire: <files> changed during <run>`, "during" because overlapping runs and the operator's own edits cannot be told apart; on a ticket already parked or closed the reason is queued as an escalation instead. A changed `escalate` file queues an escalation and the run goes on. Nothing prints a file's contents, and the workflow scripts stop on a `run finish` that parked the ticket instead of routing on the role's STATUS. The tripwire detects a write after the fact; it does not prevent one. The incident's code-level cause, a test module that imported a path function by name before the fixture replaced it, gives the coding standard rule 6: a test reaches a patched path through its module's attribute, and a new path outside the repository ships with a test guard that fails any test resolving it outside `tmp_path`; rule 4 lists rule 6 among the rules whose findings take no tag.
 50. After issue #35 (2026-10-04), where runs at the same time shared one session scratchpad and a verifier mixed another run's stale checkout into its base results (`23 failed, 103 passed` from two trees): every run gets its own scratch directory, `runs/<run id>/scratch/` in the store. `run start` creates it for every role after every guard has passed, and always makes sure the store's `.gitignore` excludes it; `ensure_gitignore` now writes its commented block only to an absent or empty file and otherwise appends only the lines a file lacks, never a second copy. The composer names the directory's absolute path in a "Scratch directory" section after "Running code". The shared preamble gains SCRATCH FILES, between RUNNING CODE and GUARDRAIL PATHS: put every file made for the run's own use there, never in a session scratchpad, a repository checkout or another run's directory, and this takes precedence over any other instruction to use a session scratchpad. Saving a ticket whose status changes to anything but `parked` removes the scratch directory of each finished run of that ticket, so a parked ticket keeps its files for the human and they go once it moves on.
-51. After issue #39 (2026-10-04), a batch of harness defects found in real runs: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested.
+51. After issue #39 (2026-10-04), a batch of harness defects found in real runs: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested. `resolve --ruling` also takes an implementer's BLOCKED park and returns the sub-ticket to its implementer at the same round, with the ruling in its input. `resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner, with F as a ruling and the existing sub-tickets listed in its input. Sub-tickets that a later plan adds take the next free ids and may depend on merged ones.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/factory/cli.py b/factory/cli.py
index e0e1eb2..718093c 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -404,7 +404,7 @@ def subticket_add(a, root, cfg):
     else:
         text = Path(a.file).read_text(encoding="utf-8")
     try:
-        subs = subtickets.parse(text, parent["id"])
+        subs = subtickets.parse(text, parent["id"], [s["id"] for s in store.subtickets_of(root, parent["id"])])
     except ValueError as e:
         raise Refused(str(e)) from None
     if not subs:
@@ -705,7 +705,7 @@ def request_changes(a, root, cfg):
 def resolve(a, root, cfg):
     if a.decision is not None:  # refuse before anything is written, so a decision is never dropped
         # the branch below that will run: --answer wins, and --close runs only with no other mode
-        if not (a.answer or (a.close and not (a.ruling or a.to or a.redispatch))):
+        if not (a.answer or (a.close and not (a.ruling or a.to or a.redispatch or a.replan))):
             raise Refused("--decision applies only with --answer or --close")
         specstore.decision_text(a.decision)
     t = store.load_ticket(root, a.id)
@@ -744,11 +744,14 @@ def resolve(a, root, cfg):
             fh.write(f"\n\n## Answer {n}\n\n{Path(a.answer).read_text(encoding='utf-8').rstrip()}\n")
         move(to, "answer", {"answer": n, **decided("resolve --answer")})
     elif a.ruling:
-        if st != "parked" or not reason.startswith("ESCALATE"):
+        if st != "parked" or not reason.startswith(("ESCALATE", "BLOCKED")):
             if st == "parked" and (reason.startswith("NEEDS-HUMAN") or "CLARIFY" in reason):
                 raise Refused("use --answer")
-            raise Refused(f"--ruling applies to an ESCALATE park; {t['id']} is {st} ({reason or 'no park'})")
-        to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
+            raise Refused(f"--ruling applies to an ESCALATE or BLOCKED park; {t['id']} is {st} ({reason or 'no park'})")
+        if reason.startswith("BLOCKED"):  # an implementer's BLOCKED: back to it, same round, ruling in its input
+            to = "ready-for-implementer"
+        else:
+            to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
         dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
         shutil.copyfile(a.ruling, dest)
         move(to, "ruling", {"ruling": _rel(root, dest)})
@@ -777,12 +780,26 @@ def resolve(a, root, cfg):
                     moved.append(f.stem)
         store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
         move("checks-in-flight", "redispatch", {"head": head, "superseded": moved})
+    elif a.replan:
+        # After a failed parent-close check: back to the planner with F as a ruling. Its new
+        # sub-tickets take the next free ids under this parent; the merged ones stay merged.
+        if st != "parked":
+            raise Refused(f"--replan applies to a parked parent; {t['id']} is {st}")
+        subs = store.subtickets_of(root, t["id"])
+        if not subs:
+            raise Refused(f"--replan applies to a parent with sub-tickets; {t['id']} has none")
+        unmerged = [f"{s['id']} is {s['status']}" for s in subs if s["status"] != "merged"]
+        if unmerged:
+            raise Refused(f"--replan needs every sub-ticket merged: {', '.join(unmerged)}")
+        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
+        shutil.copyfile(a.replan, dest)
+        move("ready-for-planner", "replan", {"ruling": _rel(root, dest)})
     elif a.close:
         if st == "closed":
             raise Refused(f"{t['id']} is already closed")
         move("closed", "close", decided("resolve --close"))
     else:
-        raise Refused("resolve needs one of --answer F | --ruling F | --to spec-gate | --redispatch | --close")
+        raise Refused("resolve needs one of --answer F | --ruling F | --to spec-gate | --redispatch | --replan F | --close")
 
 
 def decision_add(a, root, cfg):
@@ -1129,6 +1146,7 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("--ruling")
     p.add_argument("--to")
     p.add_argument("--redispatch", action="store_true")
+    p.add_argument("--replan", metavar="F", help="a parked parent whose sub-tickets all merged: back to the planner with F as a ruling")
     p.add_argument("--close", action="store_true")
     p.add_argument("--decision", metavar="TEXT", help="with --answer or --close: also log TEXT to decisions.md")
     p.set_defaults(fn=resolve)
diff --git a/factory/compose.py b/factory/compose.py
index a90ec24..5f6cc70 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -157,6 +157,11 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         add_decisions()
         for p in _approvals(root, tid, "ruling"):
             add(str(p.relative_to(root)), "Human ruling")
+        subs = store.subtickets_of(root, tid)
+        if subs:  # a re-plan: the new plan numbers after these and may depend on them
+            parts.append(f"\n## Sub-tickets already under {tid}\n\nA new plan's sub-tickets are numbered after these. "
+                         "A `Depends on:` line may name any of these ids.\n\n"
+                         + "".join(f"- {s['id']} / {s['title']}: {s['status']}\n" for s in subs))
     elif role in ("implementer", "reviewer", "verifier"):
         parent = t.get("parent") or tid  # the parent-close verifier runs on the parent itself
         pt = store.load_ticket(root, parent) if parent != tid else t
diff --git a/factory/subtickets.py b/factory/subtickets.py
index a2238c3..8064317 100644
--- a/factory/subtickets.py
+++ b/factory/subtickets.py
@@ -8,6 +8,11 @@ The planner prompt asks for "ID / Title" without fixing the id's form, so real p
 `T-0001-A`, `ST-1` or `T-0001.1`, usually under a `##` heading, with bold field names. The store
 numbers them <PARENT>.1, .2, … in plan order and keeps the planner's own id as `label`.
 
+A later plan for the same parent (a re-plan after a failed parent-close check) continues that
+numbering: its sub-tickets take the next free ids after the parent's existing ones, its
+`Depends on:` lines may name an existing sub-ticket, and a head line that reuses an existing
+sub-ticket's id is refused.
+
 A field line may start with a `- ` or `* ` list bullet, before any bold marks. Every sub-ticket
 needs a `Depends on:` line (`Depends on: none` when it depends on nothing); a plan with a
 sub-ticket that has none is refused with that sub-ticket's label.
@@ -29,10 +34,12 @@ def _is_heading(line: str) -> bool:
     return bool(re.match(r"^#{1,4}\s+\S", line))
 
 
-def parse(planner_output: str, parent: str) -> list[dict]:
+def parse(planner_output: str, parent: str, existing=()) -> list[dict]:
     """Split a PLANNED planner output into sub-tickets, in plan order. Each: id (<parent>.<n>),
-    label (the planner's id), title, depends_on (sibling ids, plus other parents' ids for a
-    cross-ticket dependency), parallel_safe, text (its block, then the plan's shared sections)."""
+    label (the planner's id), title, depends_on (sibling ids, existing sub-ticket ids, plus other
+    parents' ids for a cross-ticket dependency), parallel_safe, text (its block, then the plan's
+    shared sections). `existing` holds the ids of the parent's sub-tickets already in the store;
+    new ones are numbered after the highest of them."""
     lines = planner_output.splitlines()
     for i, line in enumerate(lines):
         if line.startswith("STATUS:"):
@@ -45,7 +52,12 @@ def parse(planner_output: str, parent: str) -> list[dict]:
     dup = sorted({x for x in labels if labels.count(x) > 1})
     if dup:
         raise ValueError(f"sub-ticket id used more than once in the plan: {', '.join(dup)}")
-    alias = {m.group(1): f"{parent}.{n}" for n, (_, m) in enumerate(heads, 1)}
+    existing = set(existing)
+    for label in labels:
+        if label in existing:
+            raise ValueError(f"{label}: {label} is already a sub-ticket of {parent}; give the new sub-ticket another id")
+    first = max((int(x.rsplit(".", 1)[1]) for x in existing), default=0) + 1
+    alias = {m.group(1): f"{parent}.{n}" for n, (_, m) in enumerate(heads, first)}
 
     def block_end(start: int) -> int:
         for j in range(start + 1, len(lines)):
@@ -79,6 +91,8 @@ def parse(planner_output: str, parent: str) -> list[dict]:
                             dep = ref
                         elif ref in alias:
                             dep = alias[ref]
+                        elif ref in existing:
+                            dep = ref  # a sub-ticket of an earlier plan, usually merged
                         elif ref[:6] != parent and re.fullmatch(r"T-\d{4}.*", ref):
                             dep = ref[:6]  # another parent ticket (or one of its sub-tickets): wait for that parent
                         elif re.fullmatch(re.escape(parent) + r"\.\d+", ref):
diff --git a/tests/factory/test_replan.py b/tests/factory/test_replan.py
new file mode 100644
index 0000000..adf55e1
--- /dev/null
+++ b/tests/factory/test_replan.py
@@ -0,0 +1,212 @@
+"""Re-plan after a failed parent-close check (spec-factory T-0023, part I, item H9).
+
+`resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner
+with F as its next ruling; the planner's input then lists the parent's existing sub-tickets. A
+later plan's sub-tickets take the next free ids, may depend on an existing sub-ticket, and may not
+reuse one's id. A first plan is unchanged: numbered from `.1`, and no sub-ticket section.
+
+Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_decision_log.py does.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+NOTE = "Re-plan: add one fix for the case-insensitive path.\n"
+SECTION = "## Sub-tickets already under T-0001"
+FIRST_PLAN = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n"
+
+
+def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
+    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+
+def js(cp: subprocess.CompletedProcess) -> dict:
+    assert cp.returncode == 0, cp.stderr
+    return json.loads(cp.stdout.strip().splitlines()[-1])
+
+
+def ticket(store: Path, tid: str) -> dict:
+    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
+
+
+def files(d: Path) -> list[str]:
+    return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()) if d.exists() else []
+
+
+def add_plan(store: Path, tmp_path: Path, text: str, name: str = "plan.md") -> subprocess.CompletedProcess:
+    (tmp_path / name).write_text(text)
+    return run(store, "subticket", "add", "T-0001", "--file", str(tmp_path / name))
+
+
+@pytest.fixture
+def store(tmp_path: Path) -> Path:
+    """T-0001 past the spec gate (no spec store), with no sub-tickets yet."""
+    s = tmp_path / "store"
+    (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+    (tmp_path / "spec.md").write_text("## Problem\nx\n")
+    js(run(s, "ticket", "new", "--file", str(tmp_path / "req.md")))
+    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
+    js(run(s, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
+    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
+    js(run(s, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
+    js(run(s, "approve-spec", "T-0001"))
+    return s
+
+
+@pytest.fixture
+def closed(store: Path, tmp_path: Path) -> Path:
+    """T-0001 split into T-0001.1 and T-0001.2, both merged, then parked by a FAILED parent-close run."""
+    js(add_plan(store, tmp_path, FIRST_PLAN, "plan1.md"))
+    js(run(store, "ticket", "set", "T-0001.1", "status=merged"))
+    js(run(store, "ticket", "set", "T-0001.2", "status=merged"))
+    js(run(store, "ticket", "transition", "T-0001", "--to", "planned", "--by", "t"))
+    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-parent-verify", "--by", "t"))
+    js(run(store, "ticket", "park", "T-0001", "--reason", "FAILED from parent-close verifier"))
+    return store
+
+
+def note(tmp_path: Path) -> Path:
+    p = tmp_path / "note.md"
+    p.write_text(NOTE)
+    return p
+
+
+def planner_input(store: Path) -> tuple[list[str], str]:
+    rid = js(run(store, "run", "start", "--role", "planner", "--ticket", "T-0001"))["run_id"]
+    sources = js(run(store, "run", "compose", rid))["sources"]
+    return sources, (store / "runs" / rid / "input.md").read_text()
+
+
+# ----- resolve --replan ----------------------------------------------------------------------
+
+def test_a_replan_sends_the_parent_to_its_planner_with_the_note_and_the_sub_ticket_list(closed, tmp_path):
+    rounds = ticket(closed, "T-0001")["round"]
+    res = js(run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path))))
+    assert res == {"ok": True, "id": "T-0001", "state": "ready-for-planner", "kind": "replan",
+                   "ruling": "approvals/T-0001/ruling-1.md"}
+    t = ticket(closed, "T-0001")
+    assert t["status"] == "ready-for-planner" and t["parked"] is None
+    assert t["round"] == rounds
+    assert t["history"][-1]["resolve"] == "replan" and t["history"][-1]["ruling"] == "approvals/T-0001/ruling-1.md"
+    assert (closed / "approvals" / "T-0001" / "ruling-1.md").read_text() == NOTE
+    assert yaml.safe_load((closed / "approvals" / "T-0001" / "resolve-1.yaml").read_text())["kind"] == "replan"
+    assert [ticket(closed, s)["status"] for s in ("T-0001.1", "T-0001.2")] == ["merged", "merged"]
+
+    sources, text = planner_input(closed)
+    assert sources[-1] == "approvals/T-0001/ruling-1.md"
+    assert "## Human ruling\n\n" + NOTE.rstrip() in text
+    assert text.index("## Human ruling") < text.index(SECTION)
+    assert text.endswith(f"{SECTION}\n\nA new plan's sub-tickets are numbered after these. A `Depends on:` line may "
+                         "name any of these ids.\n\n- T-0001.1 / First: merged\n- T-0001.2 / Second: merged\n")
+
+
+def test_a_replan_is_refused_while_a_sub_ticket_is_not_merged_and_writes_nothing(closed, tmp_path):
+    js(run(closed, "ticket", "set", "T-0001.2", "status=closed"))
+    before = files(closed / "approvals")
+    cp = run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path)))
+    assert cp.returncode == 2
+    assert "--replan needs every sub-ticket merged: T-0001.2 is closed" in cp.stderr
+    assert ticket(closed, "T-0001")["status"] == "parked"
+    assert files(closed / "approvals") == before
+
+
+def test_a_replan_names_every_sub_ticket_that_is_not_merged(closed, tmp_path):
+    js(run(closed, "ticket", "set", "T-0001.1", "status=closed"))
+    js(run(closed, "ticket", "set", "T-0001.2", "status=parked"))
+    cp = run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path)))
+    assert cp.returncode == 2
+    assert "--replan needs every sub-ticket merged: T-0001.1 is closed, T-0001.2 is parked" in cp.stderr
+
+
+def test_a_replan_is_refused_for_a_parent_with_no_sub_tickets(store, tmp_path):
+    js(run(store, "ticket", "park", "T-0001", "--reason", "FAILED from parent-close verifier"))
+    before = files(store / "approvals")
+    cp = run(store, "resolve", "T-0001", "--replan", str(note(tmp_path)))
+    assert cp.returncode == 2
+    assert "--replan applies to a parent with sub-tickets; T-0001 has none" in cp.stderr
+    assert ticket(store, "T-0001")["status"] == "parked"
+    assert files(store / "approvals") == before
+
+
+def test_a_replan_is_refused_unless_the_parent_is_parked(closed, tmp_path):
+    js(run(closed, "ticket", "set", "T-0001", "status=ready-for-parent-verify", "parked=null"))
+    cp = run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path)))
+    assert cp.returncode == 2
+    assert "--replan applies to a parked parent; T-0001 is ready-for-parent-verify" in cp.stderr
+    assert not list((closed / "approvals" / "T-0001").glob("ruling-*"))
+
+
+def test_decision_is_refused_with_replan(closed, tmp_path):
+    cp = run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path)), "--close", "--decision", "x")
+    assert cp.returncode == 2
+    assert "--decision applies only with --answer or --close" in cp.stderr
+    assert ticket(closed, "T-0001")["status"] == "parked"
+
+
+def test_resolve_with_no_mode_lists_replan(closed):
+    cp = run(closed, "resolve", "T-0001")
+    assert cp.returncode == 2
+    assert "--redispatch | --replan F | --close" in cp.stderr
+
+
+# ----- planner input -------------------------------------------------------------------------
+
+def test_a_first_plans_planner_input_has_no_sub_ticket_section(store):
+    js(run(store, "ticket", "set", "T-0001", "status=ready-for-planner"))
+    sources, text = planner_input(store)
+    assert sources == ["specs/T-0001/v1.md"]
+    assert "Sub-tickets already under" not in text
+
+
+# ----- a later plan's numbering --------------------------------------------------------------
+
+def test_a_first_plan_is_still_numbered_from_one(store, tmp_path):
+    subs = js(add_plan(store, tmp_path, FIRST_PLAN))["subtickets"]
+    assert [(s["id"], s["label"], s["depends_on"]) for s in subs] == [
+        ("T-0001.1", "ST-1", []), ("T-0001.2", "ST-2", ["T-0001.1"])]
+
+
+def test_a_later_plan_takes_the_next_free_ids_and_may_depend_on_a_merged_sibling(closed, tmp_path):
+    js(run(closed, "resolve", "T-0001", "--replan", str(note(tmp_path))))
+    plan = ("ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n\n"
+            "ST-2 / Cover it\nDepends on: ST-1, .1\nParallel-safe: yes\n")
+    subs = js(add_plan(closed, tmp_path, plan, "plan2.md"))["subtickets"]
+    assert [(s["id"], s["label"], s["depends_on"]) for s in subs] == [
+        ("T-0001.3", "ST-1", ["T-0001.2"]), ("T-0001.4", "ST-2", ["T-0001.3", "T-0001.1"])]
+    assert ticket(closed, "T-0001.3")["status"] == "waiting-dependencies"
+    assert [ticket(closed, s)["status"] for s in ("T-0001.1", "T-0001.2")] == ["merged", "merged"]
+    js(run(closed, "ticket", "transition", "T-0001", "--to", "planned", "--by", "t"))
+    assert js(run(closed, "ticket", "ready-implementers", "T-0001"))["ready"] == ["T-0001.3"]
+
+
+def test_numbering_follows_the_highest_existing_index(closed, tmp_path):
+    (closed / "tickets" / "T-0001.2.yaml").rename(closed / "tickets" / "T-0001.7.yaml")
+    t = ticket(closed, "T-0001.7")
+    t["id"] = "T-0001.7"
+    (closed / "tickets" / "T-0001.7.yaml").write_text(yaml.safe_dump(t))
+    subs = js(add_plan(closed, tmp_path, "ST-1 / Next\nDepends on: none\nParallel-safe: yes\n"))["subtickets"]
+    assert [s["id"] for s in subs] == ["T-0001.8"]
+
+
+def test_a_plan_that_reuses_an_existing_sub_ticket_id_is_refused_and_writes_nothing(closed, tmp_path):
+    before = files(closed / "tickets") + files(closed / "specs")
+    cp = add_plan(closed, tmp_path, "T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n", "plan3.md")
+    assert cp.returncode == 2
+    assert "T-0001.1: T-0001.1 is already a sub-ticket of T-0001; give the new sub-ticket another id" in cp.stderr
+    assert files(closed / "tickets") + files(closed / "specs") == before
+
+
+def test_a_dependency_on_a_sub_ticket_that_does_not_exist_is_still_refused(closed, tmp_path):
+    cp = add_plan(closed, tmp_path, "ST-1 / Fix\nDepends on: T-0001.9\nParallel-safe: yes\n")
+    assert cp.returncode == 2
+    assert "ST-1: depends on T-0001.9, which is not a sub-ticket of this plan" in cp.stderr
+    assert not (closed / "tickets" / "T-0001.3.yaml").exists()
diff --git a/tests/factory/test_resolve_rulings.py b/tests/factory/test_resolve_rulings.py
new file mode 100644
index 0000000..f58225c
--- /dev/null
+++ b/tests/factory/test_resolve_rulings.py
@@ -0,0 +1,128 @@
+"""`resolve --ruling` on an implementer's BLOCKED park (spec-factory T-0023, part A, item H1): the
+ruling becomes the sub-ticket's next ruling file, the sub-ticket returns to its implementer at the
+same round, and the implementer's next input carries the ruling. ESCALATE rulings route as before.
+
+Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_decision_log.py does.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+RULING = "Ruling: take the second approach.\n"
+
+
+def run(env: dict, *argv: str) -> subprocess.CompletedProcess:
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True,
+                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **env}, cwd=REPO)
+
+
+def js(cp: subprocess.CompletedProcess) -> dict:
+    assert cp.returncode == 0, cp.stderr
+    return json.loads(cp.stdout.strip().splitlines()[-1])
+
+
+def ticket(store: Path, tid: str) -> dict:
+    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
+
+
+@pytest.fixture
+def env(tmp_path: Path) -> dict:
+    """A scratch store and target repo: T-0001 past the spec gate (no spec store)."""
+    store = tmp_path / "store"
+    target = tmp_path / "target"
+    subprocess.run(["git", "init", "-q", "-b", "main", str(target)], check=True)
+    subprocess.run(["git", "-C", str(target), "-c", "user.email=f@x", "-c", "user.name=f",
+                    "commit", "-q", "--allow-empty", "-m", "init"], check=True)
+    e = {"FACTORY_STATE": str(store), "FACTORY_REPO": str(target), "FACTORY_INTEGRATION_BRANCH": "main"}
+    (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+    (tmp_path / "spec.md").write_text("## Problem\nx\n")
+    js(run(e, "ticket", "new", "--file", str(tmp_path / "req.md")))
+    js(run(e, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
+    js(run(e, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
+    js(run(e, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
+    return e
+
+
+def approved(env: dict, tmp_path: Path) -> Path:
+    """T-0001 approved and split into one sub-ticket, T-0001.1; returns the store."""
+    js(run(env, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
+    js(run(env, "approve-spec", "T-0001"))
+    (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
+    js(run(env, "subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md")))
+    return Path(env["FACTORY_STATE"])
+
+
+def write_ruling(tmp_path: Path) -> Path:
+    p = tmp_path / "r.md"
+    p.write_text(RULING)
+    return p
+
+
+def test_a_ruling_on_a_blocked_park_returns_the_sub_ticket_to_its_implementer(env, tmp_path):
+    store = approved(env, tmp_path)
+    js(run(env, "ticket", "set", "T-0001.1", "round.pr=1"))
+    js(run(env, "ticket", "park", "T-0001.1", "--reason", "BLOCKED from implementer"))
+    res = js(run(env, "resolve", "T-0001.1", "--ruling", str(write_ruling(tmp_path))))
+    assert res["state"] == "ready-for-implementer" and res["kind"] == "ruling"
+    assert res["ruling"] == "approvals/T-0001.1/ruling-1.md"
+    t = ticket(store, "T-0001.1")
+    assert t["status"] == "ready-for-implementer"
+    assert t["parked"] is None
+    assert t["round"]["pr"] == 1  # same round: a ruling is not a review round
+    assert (store / "approvals" / "T-0001.1" / "ruling-1.md").read_text() == RULING
+
+    rid = js(run(env, "run", "start", "--role", "implementer", "--ticket", "T-0001.1"))["run_id"]
+    sources = js(run(env, "run", "compose", rid))["sources"]
+    assert "approvals/T-0001.1/ruling-1.md" in sources
+    text = (store / "runs" / rid / "input.md").read_text()
+    assert "## Human ruling\n\n" + RULING.rstrip() in text
+
+
+def test_a_second_blocked_ruling_takes_the_next_ruling_number(env, tmp_path):
+    store = approved(env, tmp_path)
+    for n in (1, 2):
+        js(run(env, "ticket", "park", "T-0001.1", "--reason", "BLOCKED from implementer"))
+        assert js(run(env, "resolve", "T-0001.1", "--ruling", str(write_ruling(tmp_path))))["ruling"] == \
+            f"approvals/T-0001.1/ruling-{n}.md"
+    assert sorted(p.name for p in (store / "approvals" / "T-0001.1").glob("ruling-*")) == ["ruling-1.md", "ruling-2.md"]
+
+
+@pytest.mark.parametrize("reason, to", [("ESCALATE from critic", "ready-for-critic"),
+                                        ("ESCALATE from planner", "ready-for-planner")])
+def test_escalate_rulings_route_as_before(env, tmp_path, reason, to):
+    store = Path(env["FACTORY_STATE"])
+    js(run(env, "ticket", "park", "T-0001", "--reason", reason))
+    assert js(run(env, "resolve", "T-0001", "--ruling", str(write_ruling(tmp_path))))["state"] == to
+    assert ticket(store, "T-0001")["status"] == to
+    assert (store / "approvals" / "T-0001" / "ruling-1.md").read_text() == RULING
+
+
+def test_a_needs_human_park_still_asks_for_an_answer(env, tmp_path):
+    store = Path(env["FACTORY_STATE"])
+    js(run(env, "ticket", "park", "T-0001", "--reason", "NEEDS-HUMAN from spec writer"))
+    cp = run(env, "resolve", "T-0001", "--ruling", str(write_ruling(tmp_path)))
+    assert cp.returncode == 2
+    assert "use --answer" in cp.stderr
+    assert ticket(store, "T-0001")["status"] == "parked"
+    assert not list((store / "approvals" / "T-0001").glob("ruling-*"))
+
+
+@pytest.mark.parametrize("park", ["budget kill: reviewer", None])
+def test_a_ruling_on_any_other_state_is_refused_and_names_both_park_kinds(env, tmp_path, park):
+    store = Path(env["FACTORY_STATE"])
+    if park:
+        js(run(env, "ticket", "park", "T-0001", "--reason", park))
+    cp = run(env, "resolve", "T-0001", "--ruling", str(write_ruling(tmp_path)))
+    assert cp.returncode == 2
+    state = "parked" if park else "ready-for-critic"
+    assert f"--ruling applies to an ESCALATE or BLOCKED park; T-0001 is {state} ({park or 'no park'})" in cp.stderr
+    assert ticket(store, "T-0001")["status"] == state
+    assert not list((store / "approvals" / "T-0001").glob("ruling-*"))
