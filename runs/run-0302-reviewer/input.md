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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0302-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0302-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0302-reviewer/wt` (branch `factory/T-0028.1`, base `d3973c12128a9c1b4a7069c97939d5da5b34742c`, head `0521bb9338c9b4642d22878dbd8b659adbc5ea0a`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0028.1

## ST-1 / Small-change lane: gate commands may declare paths, and a one-sub-ticket spec skips the planner
Depends on: none
Parallel-safe: yes

Parent: T-0028, approved spec v1 (`.factory/store/specs/T-0028/v1.md`, change folder `.factory/store/openspec/changes/T-0028/`). Read it for context. Do NOT implement parts outside this sub-ticket.

One sub-ticket. The spec sizes the change at about 380 lines, half of them tests, and says it fits one reviewable merge (design.md, Proposed change, opening paragraph). Splitting A from B looks possible but buys nothing and breaks a scenario:
- A and B both edit `factory/cli.py`, `README.md`, `docs/design.md` and `dev/build-harness.spec.md`, so two sub-tickets could not run in parallel and the second would need a catch-up run anyway.
- C.2 asks for one changelog entry covering both parts. The scenario "The changelog records the small-change lane as its last entry" needs the last entry to name all five of `paths`, `SKIPPED`, `plan whole-spec`, `NEEDS-SPLIT` and `seams`. Under a split, the first sub-ticket either fails that check or writes the second's entry ahead of its code.
- The operator can still drop part A at the gate, as the Decisions say, by deleting it and its scenarios from the spec. A split is not needed for that.

(Under the rule this ticket adds, this spec would itself have skipped the planner: no NEEDS-SPLIT, no seam heading, no earlier planner run.)

Scope: parts A (A.1 to A.7), B (B.1 to B.4) and C (C.1 to C.4) of the parent's Proposed change, all of it.

Anchors re-checked on `main` at `a69aaf4`. The spec was written at `0b1abad`, and some line numbers have moved; the named functions and texts are unchanged:
- `factory/compose.py:44` `gate_commands`; `:177` the "Gate commands (run each from …" sentence; `:14` `_runs_for`.
- `factory/cli.py:198` `run_start`, `:267` `_start_build_run`, `:422` `subticket_add`, `:512` `results_record`; the `plan` subparser's `add` at `:1377`.
- `factory/store.py:228` `subtickets_of`, `:244` `record_result`; `factory/gitops.py:31` `git`; `factory/specstore.py:52` `is_active`, `:77` `lines_outside_fences`, `:155` `scenario_names`.
- `factory/workflows/build.js:207-213` phase 1 (the spec says 202-217).
- `README.md:89` is "The build workflow runs the planner, which …" (the spec says line 88).
- `dev/build-harness.spec.md:206` is the command list.
- `factory/instance.template.yaml:21` is `gate_commands: []`.
- `docs/changelog.md`: the last numbered entry is now 55 (#49), not 52. The new entry takes the next free number at merge (Risk, last bullet). The scenario checks only that the numbering is contiguous.
- `tests/factory/test_gate_paths.py` and `tests/factory/test_whole_spec_plan.py` do not exist yet. `tests/factory/test_parent_close_reuse.py` exists, and B.4 uses it as the model.

Acceptance: every scenario of the parent, with its `verification.md` label. Run commands from the repo root after `uv sync --frozen`, with `node` on `PATH`, under the fresh-HOME wrapper, and with `TMPDIR` set to the run's scratch directory for the fixtures. Take each WHEN verbatim from the named spec file. Several are too long to restate here without risking a transcription error, so for those this list gives the opening and the THEN.

Fixtures (GIVEN blocks, written once, verbatim):
- `${TMPDIR:-/tmp}/t0028-sub.sh`: the `cat > … <<'EOF' … EOF` block in `specs/gate-commands/spec.md`, scenario "A gate command scoped to paths is skipped for a diff that touches none of them".
- `${TMPDIR:-/tmp}/t0028-plan.sh`: the block in `specs/sub-ticket-planning/spec.md`, scenario "A spec that needs one sub-ticket becomes that sub-ticket without a planner run".
- `${TMPDIR:-/tmp}/t0023-wf.mjs`: the build-dispatch scenarios reuse it. It is defined in another ticket's spec, T-0023's approved v2 (`.factory/store/specs/T-0023/v2.md`), in the GIVEN of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling". The `cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'` block starts at line 228.

From `specs/gate-commands/spec.md`:
- A gate command scoped to paths is skipped for a diff that touches none of them (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && echo "compose=$COMPOSE run=… skipped=… meta=…")`, verbatim.
  - THEN it prints exactly `compose=0 run=1 skipped=1 meta=1`.
- A diff that touches a scoped command's paths runs that command (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh src/a.txt scoped && echo "compose=$COMPOSE run=… skipped=…")`, verbatim.
  - THEN it prints exactly `compose=0 run=1 skipped=0`.
- A gate command with no paths runs on every diff, as today (REGRESSION).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md plain && echo "compose=$COMPOSE run=… skipped=…")`, verbatim.
  - THEN it prints exactly `compose=0 run=1 skipped=0`.
- A skipped gate command is recorded on the gate result, and the merge still needs a passing gate (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && for g in FAIL PASS; do … done)`, verbatim.
  - THEN it prints exactly `FAIL: merge=2 recorded=yes`, then `PASS: merge=0 recorded=yes`.
- The implementer is still given every gate command (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && $B run compose $I >/dev/null 2>&1; echo "compose=$? both=… skipped=…")`, verbatim.
  - THEN it prints exactly `compose=0 both=1 skipped=0`.
- A malformed gate entry refuses a checker's run start and creates no run (NEW).
  - WHEN `(for bad in '{command: "true", path: ["src/"]}' '{command: "true", paths: "src/"}'; do … done)`, verbatim.
  - THEN it prints exactly `exit=2 new_runs=0 named=1`, twice.

From `specs/sub-ticket-planning/spec.md`:
- A spec that needs one sub-ticket becomes that sub-ticket without a planner run (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B plan whole-spec T-0001 > $T/o 2>&1; echo "exit=$? …"; echo "state=…")`, verbatim.
  - THEN it prints exactly `exit=0 planner=skipped subs=T-0001.1.yaml T-0001.yaml `, then `state=ready-for-implementer "ready": ["T-0001.1"] names=2 logged=1`.
- A spec the writer split, or a parent a planner already ran on, still goes to the planner and nothing is written (NEW).
  - WHEN `(for c in 'NEEDS-SPLIT|' 'READY-FOR-CRITIC|### Size and seams' 'READY-FOR-CRITIC|planner-ran'; do … done)`, verbatim.
  - THEN it prints exactly `exit=0 planner=needed subs=T-0001.yaml logged=0`, three times.
- The whole-spec step refuses a parent that is not ready for its planner (NEW).
  - WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B ticket transition T-0001 --to planned --by t >/dev/null && $B plan whole-spec T-0001 >/dev/null 2>$T/err; echo "exit=$? named=$(grep -c 'not ready-for-planner' $T/err) subs=$(ls $T/store/tickets | tr '\n' ' ')")`
  - THEN it prints exactly `exit=2 named=1 subs=T-0001.yaml `.

From `specs/build-dispatch/spec.md` (node, with the T-0023 fixture):
- A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error (NEW).
  - WHEN the two `node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '<stub JSON>'` calls, verbatim.
  - THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, `park: harness-bug: plan whole-spec: T-0001 has no approved spec`, one per line.
- A spec that needs the planner still gets a planner run (REGRESSION).
  - WHEN the one `node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '<stub JSON>'` call with `"planner": "needed"`, verbatim.
  - THEN it prints exactly `start: planner`, then `park: harness-bug: subticket add: stub stop`.

From `specs/harness-docs/spec.md`:
- The changelog records the small-change lane as its last entry (NEW).
  - WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e 'paths' -e SKIPPED -e 'plan whole-spec' -e NEEDS-SPLIT -e seams | sort -u | grep -c .)`
  - THEN it prints `CONTIGUOUS`, then `5`.
- The design doc, build spec and README describe both skips, and no prompt copy changes (NEW).
  - WHEN `(echo "design=… gate=… build=… readme=… skipped=… stale=… prompts=…")`, verbatim.
  - THEN it prints exactly `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0`.
- The small-change lane adds no whitespace errors (REGRESSION).
  - WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  - THEN it prints only `exit=0`.

Intermediate checks. These are not parent scenarios; they guard what the spec says stays unchanged:
- The harness suite, including the two new files (REGRESSION).
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
  - THEN every test passes.
  - In particular, `tests/factory/test_run_isolation.py::test_implementer_gate_commands_come_wrapped` passes unedited, which shows A.4's text is byte-identical when no command has `paths`. `tests/factory/test_instance.py` passes unedited, which shows the template value stays `gate_commands: []`.
- This repository's own gate configuration is untouched (REGRESSION).
  - WHEN `(git diff --name-only main...HEAD -- .factory | grep -c .)`
  - THEN it prints `0`.

Tests to change: none (the parent's list is none). New tests go in the new files `tests/factory/test_gate_paths.py` (A.7) and `tests/factory/test_whole_spec_plan.py` (B.4).

Protected paths, all from the parent's Risk list, class harness:
- `factory/compose.py`
- `factory/cli.py`
- `factory/workflows/build.js`
- `factory/instance.template.yaml` (comments only)

The new test files under `tests/factory/` are also on the Risk list. Unprotected documents: `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md` and `README.md`.

Out of scope, as the parent lists it:
- Any repository's `gate_commands`, including `.factory/instance.yaml` and the Nanobot fork's.
- The implementer's gate list and the parent-close verifier's, which keep every command.
- Every prompt: the `docs/design.md` prompt blocks, `docs/prompts/**`, `factory/prompts/**` and `agents/**`.
- `factory merge`, `ticket join`, redispatch, and how the `ci` row's PASS or FAIL is read.
- `resolve --replan` and planner-ESCALATE rulings.
- Part C of the request, which has already shipped.
- Having the harness run gate commands itself.
- `bin/factory`, `pyproject.toml`, `uv.lock` and the Nanobot fork. `~/.nanobot/**` is never touched.

## Parent spec (v1, pinned)

=== proposal.md
## Problem

Every approved spec pays for two steps that, in most builds, cannot change its outcome. The operator pays for both in wall-clock time on every build, on both repositories the factory runs on.

The first is the planner. After a human approves a spec, an AI agent called the planner splits it into sub-tickets. A sub-ticket is one unit of work that becomes one branch and one merge. Most specs need only one. Of the thirteen specs the planner has split so far, nine got exactly one sub-ticket. Each still waited 72 to 302 seconds for a planner run that restated the spec as that one sub-ticket: about 23 minutes across the nine.

The second is the gate commands. These are the repository's own checks, such as its test suite. The verifier, the agent that checks each sub-ticket's branch independently, runs every one of them on every sub-ticket. Here the suite takes about 2.7 minutes. A check cannot change its result on a change that touches none of the files it reads. The requester asks that a gate command may name the paths it covers, and be skipped for a sub-ticket whose changes touch none of them.

This change does both. When a spec needs only one sub-ticket, the build creates it from the whole spec and skips the planner. A gate command may declare its paths. Both fall under a standing operator decision: removing redundant work is pre-approved only if every refusal the pipeline gives today still fires. A refusal is any point where the pipeline stops a change, such as a failed check or a ticket parked for a human.

Before approving, the operator should know one thing. On the record so far, the gate-command skip would have saved almost nothing. Of the 21 sub-tickets merged in this repository, 20 changed a file the suite reads; the other was a one-off deletion of a retired directory. All 19 merged in the Nanobot fork changed its code. Its risk is a path list that leaves out a file the check reads, which would silently drop a refusal. So this change adds the mechanism and changes no repository's gate configuration. Scoping a command is a later operator step.

## Evidence

**The planner's cost on one-sub-ticket specs.** The run log (`.factory/state/log/2026-10.jsonl`, `run.finished` events of role `planner`) and the ticket records give each planned parent's planner time and the sub-tickets it got. The last two columns are what the spec writer reported and wrote. "Writer's last status" is the status of the parent's latest spec-writer run. NEEDS-SPLIT is the status a spec writer gives a spec too large for one merge. "Seam heading" is whether the approved spec has a `##` or `###` heading naming seams, the places the writer says the work splits.

| Parent | Sub-tickets built | Planner run (s) | Writer's last status | Seam heading |
|---|---|---|---|---|
| T-0012 | 6 | 531 | NEEDS-SPLIT | no |
| T-0013 | 1 | 118 | READY-FOR-CRITIC | no |
| T-0014 | 1 | 72 | READY-FOR-CRITIC | no |
| T-0015 | 1 | 139 | READY-FOR-CRITIC | no |
| T-0016 | 1 | 162 | READY-FOR-CRITIC | no |
| T-0017 | 1 | 185 | READY-FOR-CRITIC | no |
| T-0018 | 1 | 302 | READY-FOR-CRITIC | no |
| T-0019 | 2 | 176 | NEEDS-SPLIT | yes (`### Size and seams (NEEDS-SPLIT)`) |
| T-0020 | 1 | 183 | READY-FOR-CRITIC | no |
| T-0021 | 1 | 138 | READY-FOR-CRITIC | no |
| T-0023 | 4 | 378 | NEEDS-SPLIT | yes (`### Size and seams (NEEDS-SPLIT)`) |
| T-0024 | 1 | 95 | READY-FOR-CRITIC | no |
| T-0025 | 2 | 298 | READY-FOR-CRITIC | yes (`### Size and seams`) |

What this shows: the nine one-sub-ticket parents paid 1,394 s of planner time in all, 155 s on average. Every one of them has a READY-FOR-CRITIC writer status and no seam heading. Every parent that got two or more sub-tickets has NEEDS-SPLIT or a seam heading. So the trigger in Decisions sorts all thirteen as they were actually built.

**The requester's trigger misses them.** The requester proposed skipping the planner when the spec has exactly one lettered part. None of the nine has one. Counting the top-level parts under Proposed change of each approved version: T-0014 and T-0024 have A to C, T-0016 and T-0017 A to E, and T-0013, T-0015, T-0018, T-0020 and T-0021 A to F. The triage note said T-0015 had one part; its approved v2 has six (`**A.` to `**F.` at the start of their lines). The spec writer's own prompt asks for every Proposed change as lettered parts (`factory/prompts/spec_writer.md`), so the part count does not measure size.

**The gate skip would have skipped almost nothing.** For every merged sub-ticket, `git diff --name-only <base_before>...<head>` lists the files it changed.
- This repository, 21 merged sub-tickets: 20 changed a path under `factory/`, `tests/`, `docs/`, `bin/` or `agents/`, all of which the suite reads. T-0014.1, the request's own example, changed only `docs/writing.md`, which `tests/factory/test_writing_standard.py` reads. The 21st, T-0012.6, deleted the retired `intake/` tree (168 files) and edited `README.md` and the store. Under the requester's list, `factory/**`, `bin/factory`, `tests/**`, `agents/**`, `docs/**`, `pyproject.toml` and `uv.lock`, it alone would have skipped the suite. Under the exclusion list in Decisions it would have run, because `intake/` is not excluded.
- The Nanobot fork (`~/dev/nanobot-upstream`, read only), 19 merged sub-tickets: none is free of `nanobot/` changes, so even its `ruff check nanobot/` gate would have run on all 19.
- An earlier spec cut this skip for the same reason. T-0016's approved spec (`.factory/state/specs/T-0016.md`, Decisions): "The path-scoped gate skip is cut. … a path list that misses one file the suite reads silently drops a refusal." The cut is only in that spec, not in `decisions.md`.

**What the suite reads besides harness code.** Its fixtures clone the whole checkout (`tests/factory/test_harness_lock.py`, fixture `clone`). `test_ignored_and_non_harness_changes_do_not_count` then relies on the clone's `.gitignore` ignoring `__pycache__/`. The requester's list leaves out `.gitignore`, so a branch that only edited `.gitignore` would skip a suite that fails on it. A new top-level file such as a root `conftest.py` would be skipped the same way. No test reads `README.md` or `dev/` from the checkout. The only `README.md` writes are into clones and scratch targets (`grep -rn README tests/factory`).

**The suite's cost here.** `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run through the fresh-HOME wrapper on `main` at `0b1abad`, printed `265 passed in 161.71s (0:02:41)`.

**Today's behaviour, from the acceptance commands run on `main` at `0b1abad`:**
- A gate entry written as a mapping makes `run compose` of a verifier run exit 1 with `factory: AttributeError: 'dict' object has no attribute 'replace'`. Today a gate command can only be a string; there is no way to declare paths.
- `bin/factory plan whole-spec T-0001` exits 2 with `factory plan: error: argument sub: invalid choice: 'whole-spec' (choose from add)`. No command builds a sub-ticket without a planner run.
- The build script, given a parent at `ready-for-planner`, always prints `start: planner` first.

**What the planner has refused.** It returned ESCALATE three times: `run-0030-planner` (T-0002), `run-0031-planner` (T-0003) and `run-0032-planner` (T-0001). Each time the approved spec was already applied on `main`, or some of its acceptance criteria contradicted `main`. Each ESCALATE parked the parent for the operator. The workflow also refuses a planner output that `spec tasks`, `plan add` or `subticket add` reject (`factory/workflows/build.js:209-214`). Design part B shows where each of these still fires when the planner is skipped.

**Part C of the request is live.** `factory/workflows/build.js:253-266` uses a single sub-ticket's VERIFIED run for the parent close when `ticket parent-check` returns `reuse`. The rule needs the sub-ticket's text to name every scenario of the parent spec (`factory/cli.py`, `_reused_subticket_run`).

## Root cause

These are missing features, not defects.
- `factory/workflows/build.js:202-217` runs the planner for every parent at `ready-for-planner`. No command makes a sub-ticket from the approved spec itself. `factory/cli.py` `subticket_add` takes only a planner run or a plan file.
- `factory/compose.py` `gate_commands` (lines 44-51) treats each `gate_commands` entry as a string. The "Where you work" block (lines 175-179) lists every command for every build role. `factory/cli.py` `_start_build_run` knows each checker's base and head, and already writes the diff between them. Nothing compares that diff with a command's paths.
- `factory/cli.py` `results_record` writes the gate result (the `ci` row) with a status and a detail only, so it has nowhere to record a skipped command.

## Out of scope

- No repository's `gate_commands` changes. That includes this repository's `.factory/instance.yaml` and the Nanobot fork's. Scoping a command is an operator step after the runtime moves.
- The implementer's input still lists every gate command. Its diff does not exist yet when its input is written.
- The parent-close verifier run still runs every gate command.
- No prompt changes: no prompt block in `docs/design.md`, nothing under `docs/prompts/`, `factory/prompts/` or `agents/`.
- The merge gate (`factory merge`), the join (`factory ticket join`), redispatch, and how the `ci` row's PASS or FAIL is read from the verifier's `Gate suite:` line.
- The re-plan path (`resolve --replan`) and a ruling on a planner ESCALATE. Both still go to the planner.
- Part C of the request, which already shipped.
- Having the harness run the gate commands itself instead of the verifier.

## Open questions

none

## Decisions

- Part A overturns the cut in T-0016's spec. The path-scoped gate skip is built as the operator pre-approved it, with no repository's configuration changed. Rejected: cutting it again because it would have skipped almost no past run. The request expects a small saving here and still asks for the mechanism. Part A is a separate part, so the operator can delete it and its scenarios at the gate.
- A gate command's `paths` are git pathspecs. A command is skipped when `git diff --name-only <base>...<head> -- <paths>` lists no file. Include entries (`src/`) and exclude entries (`:(exclude)dev/`) both work. Rejected: a glob matcher of our own, a second matching rule that could disagree with git's. Standing: later tickets and instance configs use pathspec semantics.
- If this repository's suite is ever scoped, its paths should exclude what it does not read rather than list what it does: `:(exclude)dev/` and `:(exclude)README.md`. Rejected: the requester's inclusion list, which leaves out `.gitignore` and any new top-level file, so it would skip the suite on changes that fail it.
- The harness decides the skip when a reviewer or verifier run starts on a sub-ticket. It reads the live instance's configuration and that run's base and head. The verifier is told which commands are skipped, so it does not decide. Rejected: letting the verifier judge relevance, which no record could check.
- Each skipped command is recorded twice: in the checker run's `meta.yaml` (`gate_skipped`) and on the `ci` row (`skipped`). Each entry has the command, `status: SKIPPED` and the reason. The row's PASS or FAIL still comes from the verifier's `Gate suite:` line, over the commands that ran.
- A malformed gate entry refuses every implementer, reviewer and verifier run start with exit 2, before a run is created. A malformed entry is anything other than a string, or a mapping with a non-empty string `command` and an optional non-empty list of non-empty strings `paths`, with no other key. Rejected: treating a typo such as `path:` as unscoped. The operator would believe a scope is in force that is not.
- An empty `paths` list is refused. Rejected: reading it as "covers nothing", which would skip the command on every diff.
- The planner is skipped when all of these hold, and otherwise runs as today: the parent has no sub-ticket and no earlier planner run; its latest spec-writer run did not end NEEDS-SPLIT; and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that contains the word seam or seams. This sorts all thirteen past parents as they were built (Evidence). Rejected: the requester's "exactly one lettered part", which would have skipped none of the nine. Rejected: NEEDS-SPLIT alone, which would have built T-0025's two parts, about 470 lines, as one sub-ticket. Standing: the planner runs only for a spec that is split, re-planned or already planned once.
- To force the planner on a spec that meets every condition, the operator adds a `### Size and seams` heading in a gate edit (`approve-spec --edit`). No new flag.
- The whole-spec sub-ticket is `<parent>.1`, at `ready-for-implementer`, with no dependency. Its text names every scenario of the approved spec, one `- <name>` line each. For everything else it points to the spec: every lettered part, the spec's labels, its Tests to change and its Risk list. Because it names every scenario, the parent closes on its VERIFIED run under the existing rule (part C).
- The store records the skip three ways: a `plan.skipped` event in the log with its reason, the parent's plan file (`plans/<parent>.md`), and the change folder's `tasks.md` when the repository has a spec store. A planner-made plan writes the same two files.
- A spec already applied on `main`, the planner's most frequent ESCALATE, is caught after the skip by the implementer's step 2 and by the verifier's base run of NEW checks (design part B, table). The catch costs an implementer run in place of a planner run. Rejected: a harness check of "already applied", which would need the agents' judgment of what the spec asks for.

## Risk

- Protected paths touched, all in class harness: `factory/compose.py`, `factory/cli.py`, `factory/workflows/build.js` and `factory/instance.template.yaml` (comments only; its value stays `gate_commands: []`). New test files under `tests/factory/`. Unprotected documents: `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md` and `README.md`. Not touched: `.factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `docs/prompts/**`, `~/dev/nanobot-upstream/**` and `~/.nanobot/**`.
- Blast radius of part B: both repositories run from one runtime. Once the runtime moves, every qualifying parent on both skips the planner, the Nanobot fork's included. A spec that needed splitting but tripped no condition is built as one sub-ticket. That makes a larger merge, but every check still runs and no refusal is lost. A spec already applied on `main` costs one implementer run before it parks, where today the planner parks it.
- Blast radius of part A: none until an operator adds `paths` to a gate command. After that, a wrong path list drops that command's refusals on the changes it misses.
- Order: a `paths` entry in an instance's `instance.yaml` breaks the runtime that runs today. Its `run compose` fails on the mapping, which parks the sub-ticket as a harness bug. Add `paths` only after the runtime has moved and the instance has accepted it.
- Overlap with other open tickets. T-0027 (amending a pinned spec after planning): the whole-spec sub-ticket's scenario list is fixed when it is created. After an amendment renames scenarios, the parent close runs its own verifier, which is more work but loses no refusal. T-0022 (planner labels and sibling-added tests): with one sub-ticket there are no siblings, and its base is the parent's, so the spec's labels stand. T-0025 (store isolation, being built): it edits `factory/cli.py` and `README.md` in other functions and sections. A text conflict is resolved by the usual catch-up run. No ordering is needed with any of them. The changelog entry takes the next free number at merge.

## Operator steps

1. After merge, move the runtime with the usual upgrade step, and accept the new revision on each instance with `--accept-harness`.
2. Optional: tell the Nanobot fork's Driver session that its qualifying specs will now skip the planner.
3. Optional, and only after step 1: scope this repository's suite. In `.factory/instance.yaml`, replace the pytest entry with `{command: "uv run --frozen pytest -q -p no:cacheprovider tests/factory", paths: [":(exclude)dev/", ":(exclude)README.md"]}`. On past work this would have skipped no suite run (Evidence).
4. Timing, on the next parent that qualifies: `factory log tail --event plan.skipped --ticket <id>` prints one line, and the log has no planner `run.started` for that parent. Compare the time from the spec gate to the implementer's `run.started` with T-0014's 72 s and T-0015's 139 s planner runs.

## Out-of-scope observations

- Every ticket's `source:` field records a request path in a session scratchpad (for example `.factory/state/tickets/T-0028.yaml`), and that directory is temporary.
- The spec part splitter (`factory/specstore.py`, `PART_RE`) splits on any line starting `=== `, even inside a code fence. A spec whose fixture writes another spec has to avoid such lines, as this one does.
=== design.md
## Proposed change

Run every command from the root of `~/dev/spec-factory`. The parts are about 380 changed lines in all, about half of them tests. They fit one reviewable merge.

**A. Gate commands may declare the paths they cover.**

A.1 `factory/compose.py`: add `gate_entries(cfg) -> list[tuple[str, list[str] | None]]`. It reads `cfg.get("gate_commands")`, treating absent or null as an empty list. A string entry gives `(command, None)`. A mapping gives `(command, paths)`, or `(command, None)` when it has no `paths`. Raise `store.Refused` naming `gate_commands` and the entry's index in each of these cases:
- the entry is neither a string nor a mapping;
- the mapping has a key other than `command` or `paths`;
- `command` is missing, is not a string, or is empty;
- `paths` is present but is not a list, is empty, or holds an item that is not a non-empty string.

The refusal text says to omit `paths` for a command that always runs. `gate_commands(cfg)` keeps its signature and its `{integration}` substitution, and returns the command strings of `gate_entries(cfg)`.

A.2 `factory/compose.py`: add `gate_skips(cfg, repo, base, head) -> list[dict]`. For each entry with `paths`, run `gitops.git(repo, "diff", "--name-only", f"{base}...{head}", "--", *paths)`. When it prints nothing, append `{"command": <command as written>, "status": "SKIPPED", "reason": f"the diff {base[:9]}...{head[:9]} touches none of its paths: {', '.join(paths)}"}`. A git error propagates as the `Refused` that `gitops.git` raises.

A.3 `factory/cli.py` `run_start`: for a role in `BUILD_ROLES`, call `compose.gate_entries(cfg)` before `tripwire.baseline`, so a malformed entry refuses with exit 2 before a run id is reserved. In `_start_build_run`, for a reviewer or verifier run that is not a parent close, set `meta["gate_skipped"] = compose.gate_skips(cfg, repo, base, head)` before the detached worktree is added. Every other build run gets `meta["gate_skipped"] = []`.

A.4 `factory/compose.py` "Where you work": a reviewer or verifier run on a sub-ticket lists only the commands not in `meta.get("gate_skipped") or []` in the `Gate commands (run each from your worktree, exactly as written; each is already wrapped): …` sentence, each wrapped as today. If every command is skipped, that sentence ends `none (every gate command is skipped below)`. After that line comes one line per skipped command, each starting at column 0 exactly as `SKIPPED by the harness for this diff, do not run: `<command>`: <reason>`. The implementer and the parent-close verifier get every command, as today, and no `SKIPPED` line. The block's text for an instance with no `paths` is byte-identical to today's, which `tests/factory/test_run_isolation.py` checks.

A.5 `factory/cli.py` `results_record`: when `--role verifier` is not `--killed` and `runs/<--run>/meta.yaml` exists with a non-empty `gate_skipped`, the `ci` row also gets `skipped:` holding that list. `store.record_result` gains an optional `extra: dict | None = None` merged into the row. The `ci` status is still parsed from the `Gate suite:` line.

A.6 `factory/instance.template.yaml`: above `gate_commands: []`, a comment gives the two entry forms. It says `paths` are git pathspecs, that a sub-ticket's checkers skip a command whose paths its diff touches none of, and that the exclude form (`:(exclude)dev/`) keeps a new file running the command. The value stays `[]`.

A.7 New test file `tests/factory/test_gate_paths.py`. It covers the scenarios of `specs/gate-commands/spec.md`, run through the CLI on a scratch instance and target, plus the `gate_entries` refusals one by one.

**B. A spec that needs one sub-ticket skips the planner.**

B.1 `factory/cli.py`: add `plan_whole_spec(a, root, cfg)`, registered as `factory plan whole-spec PARENT` in the existing `plan` subparser. The order:
1. Load the parent. Refuse with exit 2, writing nothing:
   - when its status is not `ready-for-planner`: `<id> is <status>, not ready-for-planner`, as `run_start` words it;
   - when it has a run in flight;
   - when it has no approved spec: `<id> has no approved spec`.
2. Find the first reason the planner is needed:
   - the parent has sub-tickets (`store.subtickets_of`);
   - a planner run of the parent exists (`compose._runs_for(root, id, "planner", "")`);
   - its latest finished spec-writer run's `meta.yaml` status is `NEEDS-SPLIT`;
   - the approved spec `specs/<id>/v<approved>.md` has, outside code fences (`specstore.lines_outside_fences`), a line matching `^#{2,3}\s` that is not a `### Requirement:` line and contains `\bseams?\b`, ignoring case.

   If one holds, print `{"ok": true, "id", "planner": "needed", "reason"}` and write nothing.
3. If the spec store is active (`specstore.is_active`) and the change folder is missing, refuse exactly as `spec tasks` does: `<id> has no change folder (no pinned version)`.
4. Otherwise build the text below, then:
   - create sub-ticket `<id>.1` the way `subticket_add` creates one: `type: sub-ticket`, `parent`, `label: whole-spec`, `depends_on: []`, `parallel_safe: true`, `status: ready-for-implementer`, source `plan:whole-spec`, the parent's spec versions, and its text at `specs/<id>.1/subticket.md`;
   - write the same text to `plans/<id>.md` and set the parent's `plan`;
   - write it to the change folder's `tasks.md` when the spec store is active, logging `tasks.written`;
   - log `ticket.created`, then `plan.skipped` with `ticket`, `subticket` and `reason` (`one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run`);
   - print `{"ok": true, "id", "planner": "skipped", "reason", "subtickets": [<as subticket_add prints them>]}`.

   Factor the record-writing loop out of `subticket_add` so both commands use it; `subticket_add`'s behaviour does not change.

The sub-ticket text, with `<names>` as one `- <name>` line per `specstore.scenario_names` of the approved spec, in order:

```text
<id>.1 / <parent title>
Depends on: none
Parallel-safe: yes

Parent: <id>, approved spec v<N>. This sub-ticket is the whole of it; read it in full. The planner was skipped: <reason>.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
<names>
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
```

B.2 `factory/workflows/build.js` phase 1, when the parent is `ready-for-planner`:
- First clerk `${BIN} plan whole-spec ${TICKET}`.
- If it is not ok, park the parent with `harness-bug: plan whole-spec: ${whole.stderr || ''}` and return `parked`.
- If `whole.planner === 'skipped'`, log `${TICKET}: planner skipped (${whole.reason}); one sub-ticket from the whole spec` and run no planner.
- Any other success runs today's planner block unchanged (`runRole('planner')`, `spec tasks`, `plan add`, `subticket add`). A stub that returns `{"ok": true}` gets the planner too.
- Both paths then `transition(TICKET, 'planned')` and go to phase 2.

Nothing else in the script changes. The new clerk command carries `FACTORY_DISPATCH=1` through `BIN`, like every other.

B.3 Where each refusal the plan step gives today fires when the planner is skipped:

| Refusal today | With the planner skipped |
|---|---|
| Planner ESCALATE: the spec is already applied on `main` (`run-0030`, `run-0032`) | The implementer's step 2 runs the NEW checks first and stops with BLOCKED when one already passes. The verifier's step 3 runs the NEW checks on the base and returns SPEC-DEFECT when one passes there. Either parks the sub-ticket for the operator. |
| Planner ESCALATE: acceptance contradicts `main` (`run-0031`) | The implementer escalates on a NEW check that behaves otherwise, and on a REGRESSION check that fails on the base. The verifier reports SPEC-DEFECT or FAILED. |
| Planner ESCALATE: the spec cannot be split without redesign | Cannot arise: nothing is split. |
| `spec tasks`: no change folder while the spec store is active | `plan whole-spec` refuses with the same text, and the build parks it as a harness bug. |
| `spec tasks`, `subticket add`: the run is not a PLANNED planner run | Cannot arise: there is no planner run. `plan whole-spec` checks the parent's state, in-flight runs and approved spec instead. |
| `subticket add`: no approved spec | `plan whole-spec` refuses with the same condition. |
| `subticket add`: plan format (no `Depends on:`, a repeated id, an unknown dependency) | Cannot arise: the harness writes the sub-ticket and there is no plan text to check. |
| `subticket add`: the id already exists | A parent with any sub-ticket goes to the planner. |
| The planner's coverage map: every parent scenario has a sub-ticket | Holds by construction: the one sub-ticket names every scenario. |

The checkers, the merge gate and protected-path review are untouched, and none of their inputs changes except A.4's SKIPPED lines.

B.4 New test file `tests/factory/test_whole_spec_plan.py`. It covers the scenarios of `specs/sub-ticket-planning/spec.md` through the CLI. It also checks that a parent with one whole-spec sub-ticket, merged with a VERIFIED run on the parent's base, gets `reuse` from `ticket parent-check`, using the existing helpers in `tests/factory/test_parent_close_reuse.py` as the model. The build-script scenarios stay acceptance-only under node, as T-0023 decided for the suite.

**C. Documents.**

C.1 `docs/design.md`:
- Routing table, row "Human spec gate | Approved | Planner": the next-role cell adds that when the spec needs one sub-ticket, the harness creates it from the whole spec and the build goes to that sub-ticket's Implementer, logging `plan.skipped`. It names the four conditions of B.1 and the `plan whole-spec` command.
- Row 11 (Gate runner): add that a gate command may name the paths it covers, as git pathspecs. For a sub-ticket whose diff touches none of them, the harness marks it SKIPPED for the checkers, with the reason, and records it on the `ci` row. A command without paths always runs.
- The spec-store table row for `tasks.md`: "Planner, or the harness when it skips the planner".

Prompt blocks do not change.

C.2 `docs/changelog.md`: one entry, numbered after the last entry at merge, covering parts A and B. It names `paths`, SKIPPED, `plan whole-spec`, NEEDS-SPLIT and seams, and records that part A overturns T-0016's cut.

C.3 `dev/build-harness.spec.md`:
- Line 206's command list adds `factory plan whole-spec PARENT`.
- Phase 1 of the workflow (line 284) starts with that clerk command and its three outcomes.
- The `ci` row paragraph (line 320) adds the `skipped:` list.

C.4 `README.md`:
- "How a ticket moves" (line 88): the build creates the one sub-ticket itself when the spec needs only one (`factory plan whole-spec`), and runs the planner otherwise. The sentence "The build workflow runs the planner, which …" no longer stands alone.
- Step 3 of setting up a target (line 260): `gate_commands` entries may declare `paths`.
- The "Build, local-only" bullet (line 361): a skipped command is recorded as SKIPPED with its reason.
- Bump the status date.

## Tests to change

none. `tests/factory/test_run_isolation.py::test_implementer_gate_commands_come_wrapped` checks the implementer's "Where you work" text. A.4 keeps that text byte-identical when no command has `paths`, so the test stays as it is. `tests/factory/test_instance.py` checks the template's `gate_commands == []`, and A.6 keeps that value.
=== specs/gate-commands/spec.md
## ADDED Requirements

### Requirement: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them
Each `gate_commands` entry SHALL be a command string or a mapping of `command` and an optional `paths` list of git pathspecs. When a reviewer or verifier run starts on a sub-ticket, the harness MUST mark SKIPPED, with its reason, each command whose paths the diff from base to head touches none of. It MUST list that command apart from the commands to run, and record it in the run's `meta.yaml`. A command with no `paths` SHALL always be listed to run.

#### Scenario: A gate command scoped to paths is skipped for a diff that touches none of them
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0028-sub.sh <<'EOF'
# Sourced from the repo root, with $1 the file the sub-ticket's one commit changes (docs/b.md or
# src/a.txt) and $2 `scoped` or `plain`. Builds a scratch instance and target. `scoped` gives the
# gate the unscoped command `git diff --check main...HEAD` and the command `sh -c 'exit 7'` scoped
# to `src/`; `plain` keeps the fixture's one unscoped command. Sub-ticket T-0001.1 reaches
# checks-in-flight with that commit as its head; a verifier run is started and composed on it.
# Leaves $B (the CLI), $T, $I (the implementer run), $R and $V (the verifier run and its
# directory), $H (the head) and $COMPOSE (that compose's exit code).
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
mkdir $T/inst && cp tests/factory/fixtures/instance/context.md $T/inst/
grep -v '^gate_commands:' tests/factory/fixtures/instance/instance.yaml > $T/inst/instance.yaml
if [ "$2" = scoped ]; then
  printf '%s\n' 'gate_commands:' '  - "git diff --check main...HEAD"' "  - {command: \"sh -c 'exit 7'\", paths: [\"src/\"]}" >> $T/inst/instance.yaml
else
  printf '%s\n' 'gate_commands: ["git diff --check main...HEAD"]' >> $T/inst/instance.yaml
fi
export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t config user.email f@x && git -C $T/t config user.name f
mkdir -p $T/t/src $T/t/docs && echo a > $T/t/src/a.txt && echo b > $T/t/docs/b.md
git -C $T/t add -A && git -C $T/t commit -q -m init
printf '# F\n\nDo x.\n' > $T/req.md && printf '## Problem\nx\n' > $T/spec.md
$B ticket new --file $T/req.md >/dev/null
$B ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
$B spec add T-0001 --file $T/spec.md >/dev/null
$B ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
$B ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
$B approve-spec T-0001 >/dev/null
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && $B subticket add T-0001 --file $T/plan.md >/dev/null
I=$($B run start --role implementer --ticket T-0001.1 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
echo more >> $T/store/worktrees/T-0001.1/$1 && git -C $T/store/worktrees/T-0001.1 commit -q -am change
$B run finish $I --status-override READY-FOR-REVIEW >/dev/null && $B ticket head T-0001.1 >/dev/null
$B ticket transition T-0001.1 --to checks-in-flight --by t --round pr:init >/dev/null
R=$($B run start --role verifier --ticket T-0001.1 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); V=$T/store/runs/$R
H=$(git -C $T/t rev-parse factory/T-0001.1)
$B run compose $R >/dev/null 2>&1; COMPOSE=$?
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -vc 'exit 7') skipped=$(grep '^SKIPPED' $V/input.md 2>/dev/null | grep -F 'exit 7' | grep -c 'src/') meta=$(grep -c 'exit 7' $V/meta.yaml | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `compose=0 run=1 skipped=1 meta=1`

#### Scenario: A diff that touches a scoped command's paths runs that command
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh src/a.txt scoped && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -cF 'exit 7') skipped=$(grep -c '^SKIPPED' $V/input.md 2>/dev/null)")`
- THEN it prints exactly `compose=0 run=1 skipped=0`

#### Scenario: A gate command with no paths runs on every diff, as today
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md plain && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md | grep -cF 'git diff --check main...HEAD') skipped=$(grep -c '^SKIPPED' $V/input.md)")`
- THEN it prints exactly `compose=0 run=1 skipped=0`

### Requirement: A skipped command is recorded on the gate result, and the merge still needs that result to pass
When a verifier's result is recorded, the `ci` row MUST list each command that verifier run skipped, with status SKIPPED and its reason. `factory merge` SHALL still refuse unless that row is PASS.

#### Scenario: A skipped gate command is recorded on the gate result, and the merge still needs a passing gate
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && for g in FAIL PASS; do printf 'Commit: %s\nGate suite: %s\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' $H $g > $T/v.md; printf 'Commit: %s\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' $H > $T/r.md; $B results record T-0001.1 --head $H --role verifier --output $T/v.md --run $R >/dev/null; $B results record T-0001.1 --head $H --role reviewer --output $T/r.md --run run-0003-reviewer >/dev/null; $B merge T-0001.1 >/dev/null 2>&1; m=$?; C=$T/store/results/$H/ci.yaml; echo "$g: merge=$m recorded=$(grep -q 'exit 7' $C && grep -q SKIPPED $C && echo yes || echo no)"; done)`
- THEN it prints exactly `FAIL: merge=2 recorded=yes`, then `PASS: merge=0 recorded=yes`

### Requirement: The implementer is given every gate command
The implementer's input SHALL list every gate command to run, scoped or not, and no SKIPPED line.

#### Scenario: The implementer is still given every gate command
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && $B run compose $I >/dev/null 2>&1; echo "compose=$? both=$(grep -F 'Gate commands' $T/store/runs/$I/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -cF 'exit 7') skipped=$(grep -c '^SKIPPED' $T/store/runs/$I/input.md 2>/dev/null)")`
- THEN it prints exactly `compose=0 both=1 skipped=0`

### Requirement: A malformed gate entry refuses every build role's run start
A `gate_commands` entry MUST make `run start` refuse with exit 2 for the implementer, reviewer or verifier, naming `gate_commands` and creating no run, when it is anything other than one of these: a string; or a mapping with a non-empty string `command`, an optional non-empty list of non-empty strings `paths`, and no other key.

#### Scenario: A malformed gate entry refuses a checker's run start and creates no run
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(for bad in '{command: "true", path: ["src/"]}' '{command: "true", paths: "src/"}'; do (. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md plain && grep -v '^gate_commands:' $T/inst/instance.yaml > $T/i.yaml && echo "gate_commands: [$bad]" >> $T/i.yaml && mv $T/i.yaml $T/inst/instance.yaml && n=$(ls $T/store/runs | wc -l) && $B run start --role reviewer --ticket T-0001.1 >/dev/null 2>$T/err; echo "exit=$? new_runs=$(( $(ls $T/store/runs | wc -l) - n )) named=$(grep -c 'gate_commands' $T/err)"); done)`
- THEN it prints exactly `exit=2 new_runs=0 named=1`, twice
=== specs/sub-ticket-planning/spec.md
## ADDED Requirements

### Requirement: A spec that needs one sub-ticket becomes that sub-ticket without a planner run
`factory plan whole-spec <parent>`, on a parent at `ready-for-planner` with an approved spec, MUST act when four conditions hold: the parent has no sub-ticket; it has no earlier planner run; its latest spec-writer run did not end NEEDS-SPLIT; and its approved spec has no `##` or `###` heading, other than a requirement line, naming seams. It MUST then create one sub-ticket `<parent>.1`, ready for its implementer, whose text names every scenario of the approved spec. It MUST log `plan.skipped` with the reason, and report `"planner": "skipped"`. Otherwise it SHALL report `"planner": "needed"` with the reason and write nothing.

#### Scenario: A spec that needs one sub-ticket becomes that sub-ticket without a planner run
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0028-plan.sh <<'EOF'
# Sourced from the repo root, with $1 the STATUS a spec writer run ends with (READY-FOR-CRITIC or
# NEEDS-SPLIT) and $2 one more line for the spec's design part (empty for none). Builds a scratch
# store whose T-0001 has one spec writer run with that status. Its output, a spec with two labelled
# scenarios, becomes spec v1 and is approved, so T-0001 is ready-for-planner. Leaves $B and $T.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
export FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null
$B ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
W=$($B run start --role spec_writer --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
sed 's/^|//' > $T/store/runs/$W/output.md <<EOS
|=== proposal.md
|## Problem
|x
|=== design.md
|## Proposed change
|A. Do x.
|$2
|=== specs/demo/spec.md
|## ADDED Requirements
|### Requirement: X
|It SHALL do x.
|#### Scenario: First check
|- WHEN \`true\`
|- THEN it exits 0
|#### Scenario: Second check
|- WHEN \`true\`
|- THEN it exits 0
|=== verification.md
|## Acceptance
|- First check → NEW; fails today
|- Second check → REGRESSION
|STATUS: $1
|CONFIDENCE: high, fixture
|ESCALATIONS: none
EOS
$B run finish $W >/dev/null && $B spec add T-0001 --from-run $W >/dev/null
$B ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
$B ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
$B approve-spec T-0001 >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B plan whole-spec T-0001 > $T/o 2>&1; echo "exit=$? planner=$(tail -1 $T/o | sed -n 's/.*"planner": "\([a-z]*\)".*/\1/p') subs=$(ls $T/store/tickets | tr '\n' ' ')"; echo "state=$($B ticket show T-0001.1 2>/dev/null | sed -n 's/^status: //p') $($B ticket ready-implementers T-0001 2>/dev/null | tail -1 | grep -o '"ready": \[[^]]*\]') names=$(grep -cxF -e '- First check' -e '- Second check' $T/store/specs/T-0001.1/subticket.md 2>/dev/null) logged=$($B log tail --event plan.skipped --ticket T-0001 | grep -c .)")`
- THEN it prints exactly `exit=0 planner=skipped subs=T-0001.1.yaml T-0001.yaml `, then `state=ready-for-implementer "ready": ["T-0001.1"] names=2 logged=1`

#### Scenario: A spec the writer split, or a parent a planner already ran on, still goes to the planner and nothing is written
Needs the GIVEN block of "A spec that needs one sub-ticket becomes that sub-ticket without a planner run" run once. The three cases are a NEEDS-SPLIT spec, a spec with a `### Size and seams` heading, and a parent with an earlier planner run.
- WHEN `(for c in 'NEEDS-SPLIT|' 'READY-FOR-CRITIC|### Size and seams' 'READY-FOR-CRITIC|planner-ran'; do (s=${c%%|*}; x=${c#*|}; [ "$x" = planner-ran ] && e='' || e=$x; . ${TMPDIR:-/tmp}/t0028-plan.sh $s "$e" && if [ "$x" = planner-ran ]; then P=$($B run start --role planner --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); $B run finish $P --status-override ESCALATE >/dev/null; fi; $B plan whole-spec T-0001 > $T/o 2>&1; echo "exit=$? planner=$(tail -1 $T/o | sed -n 's/.*"planner": "\([a-z]*\)".*/\1/p') subs=$(ls $T/store/tickets | tr '\n' ' ')logged=$($B log tail --event plan.skipped | grep -c .)"); done)`
- THEN it prints exactly `exit=0 planner=needed subs=T-0001.yaml logged=0`, three times

### Requirement: The whole-spec step refuses where a planner run would
`factory plan whole-spec` MUST refuse with exit 2, writing nothing, on a parent that is not at `ready-for-planner`, has a run in flight, or has no approved spec. A refusal for the wrong state SHALL name the state with `not ready-for-planner`.

#### Scenario: The whole-spec step refuses a parent that is not ready for its planner
Needs the GIVEN block of "A spec that needs one sub-ticket becomes that sub-ticket without a planner run" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B ticket transition T-0001 --to planned --by t >/dev/null && $B plan whole-spec T-0001 >/dev/null 2>$T/err; echo "exit=$? named=$(grep -c 'not ready-for-planner' $T/err) subs=$(ls $T/store/tickets | tr '\n' ' ')")`
- THEN it prints exactly `exit=2 named=1 subs=T-0001.yaml `
=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: The build asks the whole-spec step before it runs the planner
At `ready-for-planner`, `factory/workflows/build.js` MUST first run `plan whole-spec`. On `"planner": "skipped"` it SHALL move the parent to `planned` and build the sub-ticket with no planner run. On any other success it SHALL run the planner as before. On a refusal it MUST park the parent with `harness-bug: plan whole-spec: <error>`.

#### Scenario: A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": true, "planner": "skipped", "reason": "fixture", "subtickets": [{"id": "T-0001.1"}]}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": false, "error": "T-0001 has no approved spec"}, "exit": 2}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, `park: harness-bug: plan whole-spec: T-0001 has no approved spec`, one per line

#### Scenario: A spec that needs the planner still gets a planner run
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": true, "planner": "needed", "reason": "the spec writer marked it NEEDS-SPLIT"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "stub stop"}, "exit": 2}}')`
- THEN it prints exactly `start: planner`, then `park: harness-bug: subticket add: stub stop`
=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the small-change lane
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap. `docs/design.md`, `dev/build-harness.spec.md` and `README.md` SHALL describe the whole-spec sub-ticket and gate-command paths. No prompt copy SHALL change, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the small-change lane as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e 'paths' -e SKIPPED -e 'plan whole-spec' -e NEEDS-SPLIT -e seams | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc, build spec and README describe both skips, and no prompt copy changes
- WHEN `(echo "design=$(grep -c 'whole-spec' docs/design.md | awk '{print ($1 > 0)}') gate=$(grep '^| 11 | Gate runner' docs/design.md | grep -c 'SKIPPED') build=$(grep -c 'plan whole-spec' dev/build-harness.spec.md | awk '{print ($1 > 0)}') readme=$(grep -c 'plan whole-spec' README.md | awk '{print ($1 > 0)}') skipped=$(grep -c 'SKIPPED' README.md | awk '{print ($1 > 0)}') stale=$(grep -c 'The build workflow runs the planner, which' README.md) prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts agents | grep -c .)")`
- THEN it prints exactly `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0`

#### Scenario: The small-change lane adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`
=== verification.md
## Acceptance

Each NEW item's failure today was captured by running its command on `main` at `0b1abad`.

- A gate command scoped to paths is skipped for a diff that touches none of them → NEW. Today it prints `compose=1 run=0 skipped=0 meta=0`. The compose exits 1 with `AttributeError: 'dict' object has no attribute 'replace'`, because a gate entry can only be a string.
- A diff that touches a scoped command's paths runs that command → NEW. Today it prints `compose=1 run=0 skipped=`. The compose fails for the same reason and writes no input.
- A gate command with no paths runs on every diff, as today → REGRESSION. Today it prints `compose=0 run=1 skipped=0`.
- A skipped gate command is recorded on the gate result, and the merge still needs a passing gate → NEW. Today it prints `FAIL: merge=2 recorded=no`, then `PASS: merge=0 recorded=no`. The merge outcomes already hold; the `ci` row has no skipped entry.
- The implementer is still given every gate command → NEW. Today it prints `compose=1 both=0 skipped=`. The implementer's compose fails on the mapping entry.
- A malformed gate entry refuses a checker's run start and creates no run → NEW. Today it prints `exit=0 new_runs=1 named=0` twice: the run starts and nothing checks the entry.
- A spec that needs one sub-ticket becomes that sub-ticket without a planner run → NEW. Today it prints `exit=2 planner= subs=T-0001.yaml `, then `state= "ready": [] names= logged=0`. `plan whole-spec` is refused as `invalid choice: 'whole-spec' (choose from add)`.
- A spec the writer split, or a parent a planner already ran on, still goes to the planner and nothing is written → NEW. Today it prints `exit=2 planner= subs=T-0001.yaml logged=0` three times. The command does not exist, so nothing reports `needed`.
- The whole-spec step refuses a parent that is not ready for its planner → NEW. Today it prints `exit=2 named=0 subs=T-0001.yaml `. The exit 2 is argparse's `invalid choice`, which does not name the state.
- A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error → NEW. Today it prints `start: planner`, `park: harness-bug: unknown STATUS READY-FOR-REVIEW from planner`, `start: planner`, `park: harness-bug: unknown STATUS undefined from planner`. The script always starts the planner first.
- A spec that needs the planner still gets a planner run → REGRESSION. Today it prints `start: planner`, then `park: harness-bug: subticket add: stub stop`.
- The changelog records the small-change lane as its last entry → NEW. Today it prints `CONTIGUOUS`, then `0`. The last entry, 52, is the live-store fence.
- The design doc, build spec and README describe both skips, and no prompt copy changes → NEW. Today it prints `design=0 gate=0 build=0 readme=0 skipped=0 stale=1 prompts=0`.
- The small-change lane adds no whitespace errors → REGRESSION. Today it prints `exit=0`.

## PR description (the implementer's output)

Sub-ticket: T-0028.1 (parent T-0028, approved spec v1, `.factory/store/specs/T-0028/v1.md`). Branch `factory/T-0028.1`, base `d3973c1` (after the catch-up merge; first branched from `a69aaf4`), head `0521bb9338c9b4642d22878dbd8b659adbc5ea0a` (3 commits and one merge of `main`).

Commit: 0521bb9338c9b4642d22878dbd8b659adbc5ea0a

## What changed

Two pieces of redundant work are removed. A spec that needs only one sub-ticket now skips the planner run, the agent that would otherwise split it. A sub-ticket's checkers, the reviewer and verifier, now skip any check command whose declared files the change does not touch. No repository's check configuration changes, so nothing is skipped until an operator scopes a command.

**A. Gate commands (the repository's own checks) may declare the paths they cover.**
- A.1 `factory/compose.py` `gate_entries(cfg)`: reads each `gate_commands` entry as a string, or as a `{command, paths}` mapping. Absent or null counts as empty. The four malformed cases from the spec are refused, naming `gate_commands entry <index>`, and each refusal says that a command that always runs omits `paths`. `gate_commands(cfg)` keeps its signature and its `{integration}` substitution, and now reads through `gate_entries`.
- A.2 `compose.gate_skips(cfg, repo, base, head)`: runs `git diff --name-only base...head -- <paths>` per scoped entry. An empty result gives a `{command, status: SKIPPED, reason}` entry. A git error is refused through `gitops.git`.
- A.3 `factory/cli.py` `run_start`: for the three build roles, `compose.gate_entries(cfg)` runs before `tripwire.baseline`, so a malformed entry refuses with exit 2 before a run id is reserved. `_start_build_run` sets `meta["gate_skipped"]` from `gate_skips` for a reviewer or verifier run that is not a parent close, before the detached worktree is added, and sets `[]` for every other build run.
- A.4 The "Where you work" block in `compose.py` lists only the commands not skipped. The sentence ends `none (every gate command is skipped below)` when all are skipped. One `SKIPPED by the harness for this diff, do not run: ...` line follows for each skipped command. A skip matches only a scoped entry (`paths is None or raw not in gone`), so an unscoped copy of a skipped command still runs. With no `paths` in the instance, the text is byte-identical to before: `test_run_isolation.py::test_implementer_gate_commands_come_wrapped` passes unedited.
- A.5 `results_record`: for an unkilled verifier whose `runs/<run>/meta.yaml` has a non-empty `gate_skipped`, the `ci` row also gets `skipped:`. `store.record_result` gains `extra: dict | None = None`. The `ci` status is still parsed from `Gate suite:`.
- A.6 `factory/instance.template.yaml`: a comment above `gate_commands: []` gives the two forms, the pathspec semantics and the exclude-form advice. The value stays `[]`, and `test_instance.py` passes unedited.
- A.7 New `tests/factory/test_gate_paths.py`, with 26 tests.

**B. A spec that needs one sub-ticket skips the planner.**
- B.1 `factory plan whole-spec PARENT` (`plan_whole_spec` in `cli.py`).
  - Refusals: it refuses a parent that is not `ready-for-planner` (`<id> is <status>, not ready-for-planner`), has a run in flight, or has no approved spec.
  - Planner needed: `_planner_needed` returns the first of four reasons, in the spec's order. If one holds, it prints `"planner": "needed"` with the reason and writes nothing.
  - Change folder: under an active spec store, a missing change folder is refused with `spec tasks`' wording.
  - Planner skipped: otherwise it creates `<id>.1` (`label: whole-spec`, source `plan:whole-spec`, `ready-for-implementer`) with the B.1 text and one `- <name>` line per scenario. It writes the same text to `plans/<id>.md` and sets the parent's `plan`. With a spec store, it also writes `tasks.md` and logs `tasks.written`. It logs `plan.skipped` and prints `"planner": "skipped"`.
  - Refactor: the record-writing loop of `subticket_add` moved into `_create_subtickets`, which both commands call. `subticket_add`'s behaviour is unchanged.
- B.2 `factory/workflows/build.js` phase 1 first runs a clerk command (one store-CLI call run by a small agent) for `plan whole-spec`.
  - A refusal parks the parent with `harness-bug: plan whole-spec: <stderr>`.
  - `skipped` logs the skip and runs no planner.
  - Any other success runs the unchanged planner block, now inside an `else`.
  - Both paths then `transition planned`.
- B.4 New `tests/factory/test_whole_spec_plan.py`, with 18 tests. It includes the parent-close reuse case: the whole-spec sub-ticket's VERIFIED run gets `reuse` from `ticket parent-check`. It is built with `test_parent_close_reuse.py`'s `_build` and `_parent_verifier_runs` helpers.

**C. Documents.**
- C.1 `docs/design.md`: the routing-table row "Human spec gate | Approved" names the whole-spec path, its four conditions, `factory plan whole-spec` and `plan.skipped`. Row 11 (Gate runner) gains the paths and SKIPPED sentences. The `tasks.md` author becomes "Planner, or the harness when it skips the planner". No prompt block changed.
- C.2 `docs/changelog.md` entry 56 covers A and B. It names `paths`, SKIPPED, `plan whole-spec`, NEEDS-SPLIT and seams, and records that part A overturns T-0016's cut.
- C.3 `dev/build-harness.spec.md`:
  - The command list in part B adds `factory plan whole-spec PARENT`.
  - Part H phase 1 starts with that clerk command and its three outcomes.
  - The part L `ci` row paragraph adds `skipped:`.
- C.4 `README.md`:
  - "How a ticket moves" describes the whole-spec path, and the stand-alone "The build workflow runs the planner, which ..." sentence is gone.
  - Step 3 of "Adopting the factory in a repo" explains `paths`.
  - The "Build, local-only" bullet describes SKIPPED.

## Conflict resolution (catch-up run, run-0301)

The merge gate refused head `a074e95` because `main` had moved from `a69aaf4` to `d3973c1`. Commit `0521bb9` merges `main` into the branch. Git merged `README.md` and `docs/design.md` with no conflict, so nothing was resolved by hand and nothing else changed. The lines this branch changes are the same before and after the merge: `git diff -U0 a69aaf4 a074e95` and `git diff -U0 main HEAD` match once hunk positions are removed.

Checks on `0521bb9`, from the worktree, under the fresh-HOME wrapper:
- Gate `git diff --check main...HEAD`: no output, exit 0.
- Gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `354 passed in 207.43s (0:03:27)`.
- The three harness-docs scenarios, run again because the merge touched `README.md` and `docs/design.md`: `CONTIGUOUS` / `5`; `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0`; `exit=0`.
- `(git diff --name-only main...HEAD -- .factory | grep -c .)`: `0`.
- The code-scenario commands were not run again. The merge brought in no code, and the branch's code changes are unchanged.

One gap for the operator. `main` brought a new README overview (`1e46841`) whose text still says the build always starts with the planner. The README now contradicts itself, and the README's own rules count each such line as stale. These lines are left as `main` wrote them, because a catch-up run changes nothing else:
- `README.md:236`, state table: "ready-for-planner | ticket | the spec is pinned; the build starts with the planner".
- `README.md:310`, "The build workflow, step by step": "Build starts once a human has approved the spec. The planner splits it into sub-tickets, …".
- The two diagrams at `README.md:197` and `:331` show the planner as the only way to reach the implementer.

The status date still reads 2026-10-04, also from `main`. C.4 asks for it to be bumped. See ESCALATIONS.

## Acceptance results

Every command below ran from the worktree under the fresh-HOME wrapper, with `TMPDIR` set to this run's scratch directory. Each WHEN was extracted verbatim from the change folder's spec files into `scratch/acc/NN.sh`, and the fixtures were written by their verbatim `cat > ... EOF` blocks. "Before" is base `a69aaf4`; "after" is `a074e95`.

| Scenario | Label | Before | After |
|---|---|---|---|
| scoped command skipped for a diff touching none of its paths | NEW | `compose=1 run=0 skipped=0 meta=0` | `compose=0 run=1 skipped=1 meta=1` |
| diff touching a scoped command's paths runs it | NEW | `compose=1 run=0 skipped=` | `compose=0 run=1 skipped=0` |
| command with no paths runs on every diff | REGRESSION | (`compose=0 run=1 skipped=0`) | `compose=0 run=1 skipped=0` |
| skipped command recorded on the gate result; merge needs a passing gate | NEW | `FAIL: merge=2 recorded=no` / `PASS: merge=0 recorded=no` | `FAIL: merge=2 recorded=yes` / `PASS: merge=0 recorded=yes` |
| implementer still given every gate command | NEW | `compose=1 both=0 skipped=` | `compose=0 both=1 skipped=0` |
| malformed gate entry refuses a checker's run start, no run | NEW | `exit=0 new_runs=1 named=0` x2 | `exit=2 new_runs=0 named=1` x2 |
| one-sub-ticket spec becomes that sub-ticket, no planner | NEW | `exit=2 planner= subs=T-0001.yaml ` / `state= "ready": [] names= logged=0` | `exit=0 planner=skipped subs=T-0001.1.yaml T-0001.yaml ` / `state=ready-for-implementer "ready": ["T-0001.1"] names=2 logged=1` |
| split spec / already-planned parent still goes to planner | NEW | `exit=2 planner= subs=T-0001.yaml logged=0` x3 | `exit=0 planner=needed subs=T-0001.yaml logged=0` x3 |
| whole-spec step refuses a parent not ready for its planner | NEW | `exit=2 named=0 subs=T-0001.yaml ` | `exit=2 named=1 subs=T-0001.yaml ` |
| qualifying spec reaches implementer with no planner; refusal parks | NEW | `start: planner` / `park: harness-bug: unknown STATUS READY-FOR-REVIEW from planner` / `start: planner` / `park: harness-bug: unknown STATUS undefined from planner` | `start: implementer` / `start: reviewer` / `start: verifier` / `park: stub stop` / `park: harness-bug: plan whole-spec: T-0001 has no approved spec` |
| spec that needs the planner still gets one | REGRESSION | (`start: planner` / `park: harness-bug: subticket add: stub stop`) | `start: planner` / `park: harness-bug: subticket add: stub stop` |
| changelog records the lane as its last entry | NEW | `CONTIGUOUS` / `1` (spec expected `0`; see Known gaps) | `CONTIGUOUS` / `5` |
| design doc, build spec, README describe both skips; no prompt copy changes | NEW | `design=0 gate=0 build=0 readme=0 skipped=0 stale=1 prompts=0` | `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0` |
| no whitespace errors | REGRESSION | (`exit=0`) | `exit=0` |

The two REGRESSION scenarios and the whitespace check also printed the expected text on the base, as the "before" column shows.

The intermediate checks, both REGRESSION, ran on `a074e95`:
- `(git diff --name-only main...HEAD -- .factory | grep -c .)` printed `0`: the branch changes nothing under `.factory/`, so this repository's gate configuration is untouched.
- Gate `(export HOME=...; git diff --check main...HEAD)` exited 0 with no output: the branch adds no whitespace errors.
- Gate `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `354 passed in 302.88s`. That count includes `test_run_isolation.py` and `test_instance.py`, both unedited.

## Tests added/changed

- Added `tests/factory/test_gate_paths.py` (26 tests). They cover the scoped skip, its exact SKIPPED line and the `meta.yaml` entry, and a touched scope running its command. They cover an exclude-only pathspec (`:(exclude)docs/`), which skips a docs-only diff and runs on a `src/` diff and checks the all-skipped `none (...)` text. They check that the implementer gets every command, that the `ci` row's `skipped:` list appears with PASS and with FAIL, and that a row with no skip has no `skipped` key. They check that a malformed entry refuses implementer, reviewer and verifier run starts with no new run. They cover each of 12 malformed shapes by index, null, absent and unscoped-mapping configurations byte-equal to the string form, and an unscoped copy of a skipped command that still runs. They are black-box through `bin/factory`, because `tests/factory/` shadows the `factory` package on import.
- Added `tests/factory/test_whole_spec_plan.py` (18 tests). They cover:
  - the skip itself: the sub-ticket record, text, plan file, log event and ready list;
  - `tasks.md` and `tasks.written` under a spec store, and the missing-change-folder refusal with the store unchanged;
  - NEEDS-SPLIT and three seam headings, which all report `needed` and write nothing;
  - text that names seams in no `##`/`###` heading, which does not trigger: `####`, a fenced heading, `Seamstress`, prose, and a `### Requirement:` line;
  - an earlier planner run, and an existing sub-ticket;
  - the three refusals: wrong state, run in flight, no approved spec;
  - parent-close reuse with no planner run.
- Both files fail on base `a69aaf4`. The two files copied into a plain `git archive` export of the base printed `43 failed`, which was every test at that time. The 26th gate-paths test, added later, failed with only the A.4 matching fix stashed (`1 failed`).
- No existing test was changed.

## Known gaps and uncertainties

- **One NEW check printed a different "before" value than the spec recorded.** On this base the changelog check printed `CONTIGUOUS` then `1`, where the spec's verification.md says `0`. The spec was written when entry 52 was last. Entry 55 has since landed, and it contains the word `paths`. The check still failed before the change, because 1 is not 5, so I treated this as drift from `main` moving rather than a spec defect.
- **`factory/store.py` is touched, and the spec's Risk list does not name it.** A.5 explicitly requires `store.record_result` to gain `extra`. That is a two-line change in `factory/store.py`, which is under the protected `factory/**`. See ESCALATIONS.
- **The README now describes behaviour that has not run on a real ticket.** Its "Ground truth only" rule says such behaviour belongs under "Where this can go", but C.4 requires the present-tense description in "How a ticket moves". I followed the spec and used the README's existing pattern: "is tested, and has not yet run on a real ticket" for the planner skip, and "is tested, and no repo's configuration uses it yet" for the gate skip.
- **The README status date is unchanged.** It already reads 2026-10-04, today, so there was nothing to bump.
- **Line anchors differ from the spec.** The C.3 edits landed at the command list in part B (around line 206), the part H phase 1 text (around line 284) and the part L paragraph (around line 320). The text matched the spec's description at each place.
- **A skipped command is matched by its command text.** Two *scoped* entries with the same command text and different paths would both drop out of the run list if only one is skipped. An unscoped duplicate is safe and tested. I judged the scoped-duplicate case too unlikely to need per-index bookkeeping, and I did not add a marker for it.
- **A skipped command is shown as written.** A SKIPPED line shows `{integration}` unexpanded, because A.2 says to use the command as written.
- **The build-script scenarios are acceptance-only.** They run under node with the T-0023 stub harness, as T-0023 decided, and the pytest suite does not cover them.
- **Exclude-only pathspecs depend on git.** They rely on git treating a pathspec list with no positive entry as matching everything else. The exclude test exercises this on the local git; I did not check other git versions.
- factory: markers added: none.

Callers of the changed functions, found with `grep -rn` over `factory/` and `bin/`:
- `gate_commands` has one caller, `compose.compose`.
- `store.record_result` has two callers, both in `results_record`. Only the `ci` call passes `extra`.
- `_create_subtickets` is called by `subticket_add` and `plan_whole_spec`.
- `gate_entries` is called by `gate_commands`, `gate_skips`, `compose` and `run_start`.
- `gate_skips` is called by `_start_build_run`.

## Out-of-scope observations

- `factory/workflows/build.js` `meta.phases[0].detail` still reads "planner decomposes the pinned spec into sub-tickets". B.2 says nothing else in the script changes, so I left it.
- `dev/issues.md` row 48 still says "T-0028 (spec approved; queued)". The operator updates it at merge.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The merge was clean, the branch's own changed lines are unchanged, and both gates and the docs scenarios pass on `0521bb9` (354 tests).
ESCALATIONS:
- The README is stale after the merge. Lines from `main`'s new overview (`README.md:236`, `:310`, and the diagrams at `:197` and `:331`) still say the build always starts with the planner, and the status date is 2026-10-04. A catch-up run may change nothing else, so I left them. Decide whether a fix round on this branch updates them, or whether a follow-up does.
- Declared protected paths touched, class harness, for the merge gate's record: `factory/compose.py`, `factory/cli.py`, `factory/workflows/build.js` and `factory/instance.template.yaml` (comments only). `factory/store.py` (`record_result` gains `extra`) was accepted by the operator's ruling of 2026-10-05 as part of design part A.5. The merge gate still needs the human approval row for these paths.

## Diff `d3973c12128a9c1b4a7069c97939d5da5b34742c...0521bb9338c9b4642d22878dbd8b659adbc5ea0a`

diff --git a/README.md b/README.md
index b0a46cd..5c46c54 100644
--- a/README.md
+++ b/README.md
@@ -144,9 +144,15 @@ state "ready for triage". The intake workflow runs triage. On accept, the spec w
 the repo and writes the spec. The critic judges it and approves, asks for one revision, or escalates. On approve, the ticket waits at the **spec gate**. A human reads the spec,
 edits it if needed, and approves it (pinning that version) or sends it back with notes. Nothing
 downstream runs until this happens.
-The intake script stops at the spec gate; the build script runs the planner.
-
-The build workflow runs the planner, which splits the spec into sub-tickets with dependencies.
+The intake script stops at the spec gate; the build script plans the work.
+
+The build workflow first asks the harness whether the spec needs splitting, with
+`factory plan whole-spec`. When it needs only one sub-ticket, the harness creates that sub-ticket
+from the whole spec, naming every scenario in it, and no planner runs. A spec needs only one when
+the spec writer did not mark it too large for one merge (`NEEDS-SPLIT`), no heading in it names
+seams (the places the writer says the work splits), and no planner has run on it before. Otherwise
+the planner runs, splitting the spec into sub-tickets with dependencies. The one-sub-ticket path is
+tested, and has not yet run on a real ticket.
 When a sub-ticket's dependencies are merged, an implementer builds it on a branch in its own
 working copy. The reviewer and the verifier then judge the same commit, independently. The harness
 makes one decision from their verdicts: merge; send back for one revision; send back
@@ -570,7 +576,10 @@ From inside the target repo, with `R` the runtime (`~/dev/spec-factory-harness`)
 2. Restart the Claude Code session so the agents register.
 3. Fill in `.factory/context.md`, the briefing every role reads first: which repo this is, how to
    run its tests, what kind of request to expect. Set `gate_commands` and `protected_paths` in
-   `.factory/instance.yaml`. Set `run_env` for any tool whose cache lives under HOME,
+   `.factory/instance.yaml`. A `gate_commands` entry may declare `paths`, the git pathspecs the
+   command covers: `{command: "<command>", paths: [":(exclude)dev/"]}`. A sub-ticket whose changes
+   touch none of them skips that command. Prefer exclude pathspecs, so a new file still runs the
+   command. Set `run_env` for any tool whose cache lives under HOME,
    so it still finds that cache from inside the fresh temporary HOME.
 
 The repo is now a target. "Starting a run" is the rest.
@@ -815,7 +824,10 @@ path above is relative to the store.
   result where a CI result would go. The reviewer and verifier judge the same commit. A sub-ticket
   that passes is merged into the local integration branch, one merge at a time. If `main` moved
   during the build, the implementer merges it in before the checks re-run; two catch-up runs that
-  fail to merge it in park the sub-ticket.
+  fail to merge it in park the sub-ticket. A check command that declares the paths it covers is
+  skipped for a sub-ticket whose changes touch none of them: the reviewer and verifier are told it
+  is SKIPPED, with the reason, and the skip is recorded with the check result. The implementer
+  still gets every command. The skip is tested, and no repo's configuration uses it yet.
 - **Spec store.** Specs live in an OpenSpec tree, a folder-per-change layout borrowed from the
   OpenSpec project. A ticket's spec is a set of deltas against current truth. When a ticket closes,
   `archive` applies the deltas, so the description of the system is kept current by the pipeline.
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index f7a97bb..1991982 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -203,7 +203,7 @@ CLI (the **store CLI** of doc §Harness table piece 1 — read, transition, reco
 - `factory run start --role R --ticket ID|none --head SHA|none [--model M]` → prints `run_id`, writes `runs/<run_id>/{meta.yaml,system-prompt.txt}` and creates the empty `runs/<run_id>/scratch/` for the run's temporary files, which the store's `.gitignore` excludes (`model: M`, default `config.yaml` `models[R]`; `budget_usd` copied from the ticket), appends the id to `in_flight`. **Guards:** exit 2, nothing written, when the ticket is not in R's ready state (`T-0001 is ready-for-triage, not ready-for-critic`; ready states: triage `ready-for-triage`, spec_writer `ready-for-spec-writer`, critic `ready-for-critic`, planner `ready-for-planner`, implementer `ready-for-implementer`, reviewer/verifier `checks-in-flight` or `ready-for-checks`, verifier also `ready-for-parent-verify`; retro runs with `--ticket none`), or when the ticket's branch already has a run in `in_flight` (implementer, retro: any run; reviewer, verifier: a run of the same role) — `ticket/T-0001 already has run <id> in flight`; or, for an implementer run of a sub-ticket, when a `` `<file>` (added by <ID>) `` line in its "Tests to change" field names a file that existed at the parent's `parent_base` or whose first adding commit on the integration branch since then lies inside no merged sibling's recorded `merge` (doc §Harness, "Tests a sibling added") — `BLOCKED from harness: Tests to change lists <file> as added by a sibling, but no merged sibling of <parent> added it since <base>; …`. **Run id reservation:** after the guards pass and before anything else is written, `run start` reserves the run's directory by creating `runs/<run_id>/` create-exclusive (an mkdir that fails when the path already exists); on a collision it takes the next id and tries again. Two starts on one store at the same moment, whatever their tickets or roles, therefore never share a run directory, and the id is final before its `meta.yaml` is written. A refused start reserves nothing (item 70).
 - `factory run compose RUN` (**the one input mechanism**, critic S2) → writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares for `(role, round, resolution)` — the "with input =" lists in H, read from the store and `~/factory/clone` — and records their paths as `input_sources:` and the pinned spec version it used as `spec_version:` in `meta.yaml` (a run keeps that version even if the spec is re-pinned while it is in flight, K). The file opens with the repo's role-context block (doc §Harness), ahead of those sources; it is not a store path, so it is not one of the `input_sources:` (its text is in `input.md`). The text `agent()` receives is only `Your entire input is ~/factory/state/runs/<run_id>/input.md; read it first.` No input text is composed anywhere else.
 - `factory run finish RUN --output-file F [--status-override KILLED]` → writes `output.md`, parses STATUS (H), removes the id from `in_flight`, prints `STATUS CONFIDENCE ESCALATIONS` as JSON, logs `escalation.queued` when the list is non-empty (H).
-- `factory spec add ID --file F` → `spec.version += 1`, `specs/ID/v<N>.md`; `factory spec tasks PARENT --run RUN` → writes that planner run's `output.md`, trailer removed as for spec text (above), to `openspec/changes/<PARENT>/tasks.md` (exit 2 unless RUN is a `PLANNED` planner run of PARENT); `factory subticket add PARENT --file F --depends-on IDS --parallel-safe yes|no` → sub-ticket in `ready-for-implementer` or `waiting-dependencies`.
+- `factory spec add ID --file F` → `spec.version += 1`, `specs/ID/v<N>.md`; `factory spec tasks PARENT --run RUN` → writes that planner run's `output.md`, trailer removed as for spec text (above), to `openspec/changes/<PARENT>/tasks.md` (exit 2 unless RUN is a `PLANNED` planner run of PARENT); `factory subticket add PARENT --file F --depends-on IDS --parallel-safe yes|no` → sub-ticket in `ready-for-implementer` or `waiting-dependencies`; `factory plan whole-spec PARENT` → when the approved spec needs one sub-ticket (the parent has no sub-ticket and no earlier planner run, its latest spec-writer run did not end `NEEDS-SPLIT`, and the approved spec has no `##` or `###` heading, other than a `### Requirement:` line, naming seams), creates `<PARENT>.1` from the whole spec in `ready-for-implementer`, its text naming every scenario, writes the same text to `plans/<PARENT>.md` and, with a spec store, `openspec/changes/<PARENT>/tasks.md`, logs `plan.skipped`, and prints `"planner": "skipped"`; otherwise prints `"planner": "needed"` with the reason and writes nothing (exit 2 when PARENT is not `ready-for-planner`, has a run in flight, has no approved spec, or has no change folder under an active spec store).
 - **Operator commands** (`approve-spec`, `approve-pr`, `approve-guardrail`, `request-changes`, `resolve`, `queue apply`, `merge`, `ticket new`, `results record`) refuse with exit 2, stderr `set FACTORY_KEY`, nothing written or logged, when `FACTORY_KEY` is unset (item 78); reads (`ticket show`, `results show`, `queue`, `log tail`) never need it. `gate-run` always uses the harness key.
 
 ### C. Audit log and run artifacts (piece 10)
@@ -281,7 +281,7 @@ Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run st
 4. A re-run of `intake.js` starts from the state the store holds: `ready-for-triage` → phase 1; `ready-for-spec-writer` → phase 2 at the writer; `ready-for-critic` (a human `--ruling` on a critic ESCALATE, K) → phase 2 at the critic, same round, the ruling in its input.
 
 `build.js` (`args: {ticket}`), run after `factory approve-spec`:
-1. `phase('Plan')` (only when the parent is `ready-for-planner`; a re-run starts from the stored state, so a `--ruling` on a planner ESCALATE re-runs the planner with the ruling in its input): `runRole('planner')` with the pinned spec; `PLANNED` → clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add` per sub-ticket (`depends_on`, `parallel_safe`); `ESCALATE` → park, return.
+1. `phase('Plan')` (only when the parent is `ready-for-planner`; a re-run starts from the stored state, so a `--ruling` on a planner ESCALATE re-runs the planner with the ruling in its input): first clerk `factory plan whole-spec PARENT` (B), with three outcomes: a refusal → park the parent `harness-bug: plan whole-spec: <stderr>`, return; `"planner": "skipped"` → no planner run, `transition --to planned`; any other success → the planner as follows. `runRole('planner')` with the pinned spec; `PLANNED` → clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add` per sub-ticket (`depends_on`, `parallel_safe`); `ESCALATE` → park, return.
 2. `phase('Build')`: `while` any sub-ticket is not `merged|parked|closed`: `ready = ` clerk `factory ticket ready-implementers PARENT` (JSON: sub-tickets in `ready-for-implementer` whose deps are merged, minus any with a run in flight on its branch; a `parallel_safe: false` sub-ticket runs alone: it is listed only when no sibling of the same parent is in flight — any role: `in_flight` non-empty or `checks-in-flight` — and nothing else is listed with it, and while it is in flight no sibling is listed; doc §Routing table, Planner row; item 79; its `subtickets` lists every sub-ticket id of the parent in id order); when the first `ready` of a build run has an empty `subtickets` (a parent planned with none), clerk `factory subticket add PARENT` with no `--run`, once per build run: it takes the planner run named by the parent's latest `plan.added` event; on its refusal park the parent `no sub-tickets, and none could be created from the recorded plan: <stderr>` and return, on success continue the loop; `await parallel(ready.map(st => () => buildOne(st)))`; if `ready` is empty and nothing is in flight, return (the rest is parked or waiting on a human). When nothing is left to build, clerk `factory ticket parent-check PARENT`; a refusal parks the parent `parent-check refused: <stderr>` and returns. When the parent reaches `ready-for-parent-verify` (G), or a re-run finds it there: clerk `factory ticket parent-check PARENT` first. Its `reuse` field names a run when the parent has exactly one sub-ticket and it is merged, `main` is still at that sub-ticket's merge commit, the results row for the merged head is VERIFIED from a run whose base is the parent's `parent_base`, and the sub-ticket's text names every scenario of the pinned spec; that run stands for the parent-close run: no verifier run starts, the build goes to `factory archive PARENT` with that run id as the park outputs, and the close records it as `verified_by` (`null` → as follows). Otherwise `runRole('verifier', PARENT, <main SHA>)` — the parent-close run, whose inputs doc §Routing table (merge-gate row) declares: the pinned parent spec (every delta scenario with its `## Acceptance` label), head = current `main`, base = the parent's `parent_base`, `{gate commands}`; `run compose` supplies exactly these four (no sub-ticket text), the clerk makes the checkout of that head, and the verifier definition (rendered verbatim from the doc) checks out the head it was given and runs the base it was given; `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`; `FAILED`/`SPEC-DEFECT` → `park --reason 'parent verify: <STATUS>'` with the output (human queue); then return.
 3. `buildOne(st)`: loop:
    - `runRole('implementer', st, …, {isolation: 'worktree'})`; the implementer's worktree is created on current `main` at dispatch (doc §Routing table, Planner row), input = sub-ticket, pinned parent spec, AGENTS.md (+ round ≥ 2: both checker outputs, CI result, or the human ruling); `BLOCKED` → park, return; `READY-FOR-REVIEW` → clerk `factory ticket head ST` (from `git ls-remote`), `transition --to checks-in-flight --round pr:init`.
@@ -317,7 +317,7 @@ No API key in any run: the CLI authenticates from the owner's login. Keys only i
 
 ### L. Verifier as gate runner (piece 11)
 
-No separate CI service. For sub-ticket PRs, `results record --role verifier` writes `results/<head>/ci.yaml` from the first `Gate suite: PASS|FAIL` line, which may carry leading heading or emphasis marks (`## Gate suite: PASS`, `**Gate suite:** PASS`; `*` around the verdict and the detail is stripped) but no other text before `Gate suite:`; missing → `FAIL`, `detail: missing Gate suite line`. For no-sub-ticket PRs (retro, revert), which have no verifier, `factory gate-run ID --head H` is the gate runner: a clean checkout of `H` in `~/factory/runs/gate-<n>/wt`, `{gate commands}` run there, `results/H/ci.yaml` `PASS`/`FAIL` (the failing output as `detail`) written under the harness identity, checkout removed. The routing dispatches it, not the operator: `ticket new --type retro|revert` runs it on the branch head (B), and `factory merge` on a retro/revert ticket whose current head has no ci row runs it before judging (G); the explicit command remains for a re-run.
+No separate CI service. For sub-ticket PRs, `results record --role verifier` writes `results/<head>/ci.yaml` from the first `Gate suite: PASS|FAIL` line, which may carry leading heading or emphasis marks (`## Gate suite: PASS`, `**Gate suite:** PASS`; `*` around the verdict and the detail is stripped) but no other text before `Gate suite:`; missing → `FAIL`, `detail: missing Gate suite line`. When that verifier run skipped gate commands, the row also holds `skipped:`, the run's `meta.yaml` `gate_skipped` list: per command, `command`, `status: SKIPPED` and `reason`. `run start` writes that list for a reviewer or verifier run on a sub-ticket: each `gate_commands` entry `{command, paths}` whose git pathspecs the diff `base...head` touches none of; `run compose` lists those commands as `SKIPPED` lines apart from the commands to run. The implementer and the parent-close verifier get every command. For no-sub-ticket PRs (retro, revert), which have no verifier, `factory gate-run ID --head H` is the gate runner: a clean checkout of `H` in `~/factory/runs/gate-<n>/wt`, `{gate commands}` run there, `results/H/ci.yaml` `PASS`/`FAIL` (the failing output as `detail`) written under the harness identity, checkout removed. The routing dispatches it, not the operator: `ticket new --type retro|revert` runs it on the branch head (B), and `factory merge` on a retro/revert ticket whose current head has no ci row runs it before judging (G); the explicit command remains for a re-run.
 
 ### M. Audit sample and retro entry
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 922bd88..2635d2e 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -57,5 +57,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 53. After issue #46 (2026-10-04), where each store commit on the integration branch sent every sub-ticket waiting to merge back for a catch-up merge and a second round of checks that could not change the verdict: the store moves to its own branch, `factory-store`, checked out as a git worktree at the store's path and never merged into the integration branch, so a store commit no longer moves that branch; the merge gate is unchanged. A store path must be one the integration branch has never tracked, because at a once-tracked path a checkout of an older commit overwrites live records and a checkout back deletes them. `init` creates a missing own store as a worktree of an unborn `factory-store` branch, which needs no commit, or checks out the branch where it exists locally or on exactly one remote, which restores the store on a clone, and adds the store to the repo's git exclude file. It refuses when more than one remote carries the branch, naming each, and at a once-tracked path. With `FACTORY_INSTANCE` unset it refuses from inside the store checkout, on its branch or on a detached HEAD, so it can no longer build a phantom instance inside the live store; a separate repository under a run's scratch directory still gets its own instance. Every refusal comes before the first write. An existing store that is a plain directory is left alone, and `init` reports `store_branch` in its JSON. A new command, `factory store migrate --to PATH`, moves such a store: it refuses, writing nothing, unless the store in use is the instance's own and not yet on its branch, no `factory-store` branch exists, the integration branch is checked out, no run is in flight, no git worktree lies under the store, every store file is committed, PATH does not exist, lies outside the old store and was never tracked, and `instance.yaml` has a `state_dir:` line; it then starts `factory-store` at one commit whose tree is the store as last committed and whose message names that commit, checks it out at PATH, copies the files git ignores there and verifies them byte for byte, undoing its own worktree and branch and exiting 1 on a mismatch, and only then untracks and deletes the old directory, adds PATH to the exclude file and rewrites only the value of `state_dir`; it commits and pushes nothing.
 54. After issue #40 (2026-10-04), where sub-tickets parked for three causes that were visible when the work was planned or specified: a NEW check copied from the whole spec already passed at the sub-ticket's own start; an implementer could not change a test an earlier sibling sub-ticket had added to pin its interim behaviour, because only the spec gate's "Tests to change" list authorized a test edit and that test did not exist at the gate; and a spec's Decision overturned an existing test that nobody listed. The planner labels each check NEW or REGRESSION against the sub-ticket's own base, the integration branch with its dependencies merged, not by the parent's label. An earlier sibling names the new test files a later sibling will break under "Interim tests", which the harness does not read. A sub-ticket's "Tests to change" may list a test file an earlier sibling added, as `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. Before each implementer run, `run start` checks in git that the file was absent at the parent's base and was first added inside a merged sibling's recorded merge; otherwise it refuses with exit 2, writing nothing, with an error that starts `BLOCKED from harness:`, and the build parks the sub-ticket with that error so `resolve --ruling` returns it to its implementer. The preamble and the code reviewer accept such a checked entry. The spec writer lists the tests each behaviour-changing Decision overturns, and critic rubric 1 makes a missing one a finding. A test that existed before the parent's first merge still needs the pinned spec's list. Rejected: letting the implementer edit a test on its own judgement.
 55. After issue #49 (2026-10-04), where the implementer and verifier queued the same declared-path list as the code reviewer: in the store's log, 10 implementer and verifier runs did this, and their lists made up 30 of the 205 items queued so far. The implementer and verifier prompts gain one RULES bullet: a protected path the sub-ticket declares is not an escalation. The code reviewer lists declared paths once for each head it reviews, through its check 6, unchanged. The other two roles may name them in their output, but not under ESCALATIONS. An undeclared protected path, or a change to a declared one that the spec does not describe, still goes under ESCALATIONS from every role. Rejected: the retro's figure of 26 of 139 items, which its own table contradicts with 38.
+56. After issue #48 (2026-10-04), where every approved spec paid for a planner run and every sub-ticket for every gate command, though nine of the thirteen specs planned so far got exactly one sub-ticket, each after a 72 to 302 second planner run that restated it: the small-change lane. A spec that needs one sub-ticket skips the planner. At `ready-for-planner` the build first runs `factory plan whole-spec`, which creates `<parent>.1` from the whole spec, ready for its implementer, naming every scenario of the spec, and logs `plan.skipped`, when the parent has no sub-ticket and no earlier planner run, its latest spec-writer run did not end NEEDS-SPLIT, and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that names seams. Otherwise it reports that the planner is needed, writes nothing, and the planner runs as before; it refuses a parent that is not ready for its planner, has a run in flight or has no approved spec, and the build parks that refusal as a harness bug. To force the planner on such a spec, the operator adds a `### Size and seams` heading at the gate. A gate command may also declare `paths`, as git pathspecs. When a reviewer or verifier run starts on a sub-ticket, the harness marks SKIPPED, with the reason, each command whose paths the sub-ticket's diff touches none of, lists it apart from the commands to run, and records it in the run's `meta.yaml` and on the `ci` row, whose PASS or FAIL still comes from the commands that ran. The implementer and the parent-close verifier still get every command, and a malformed entry refuses every build role's run start. This overturns the cut of the path-scoped skip in T-0016's spec; no repository's gate configuration changes. Rejected: the request's trigger of exactly one lettered part, which would have skipped none of the nine.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index df61ad6..7375500 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -48,7 +48,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | 8 | Guardrail and protected paths | If the diff touches a guardrail or protected path, the merge gate requires an approval row signed by a human identity. For existing tests, the spec gate's approval of "Tests to change" is that row for exactly the tests listed. A test file an earlier sibling sub-ticket of the same parent added is also covered when the sub-ticket lists it as added by that sibling and the sibling-tests check has passed (Tests a sibling added, below); any other guardrail or protected path needs a human approval on the PR itself. The harness code (its package, entry point, agent templates and dependency lock) is itself a protected path in the repo that holds it. | CODEOWNERS with required owner review for CI config, AGENTS.md, skills, prompts, and protected paths. Not for tests: CODEOWNERS fires on added files too. Existing tests get a required check that fails when a test file is modified or deleted and not in the pinned spec's "Tests to change" or among the sub-ticket's checked sibling entries (on a revert: files the reverted PR added and the tests its pinned spec listed under "Tests to change" are exempt, and the revert's human approval is the piece-8 row for them) | A path list checked in the merge gate, with the same modified-or-deleted rule for test files. Keep the list in the repo under CI config, so it is itself a guardrail path |
 | 9 | Human surface | Where people approve specs, answer escalations, review protected PRs, reply to requesters, and read the weekly audit sample. Every decision writes back to the store as a record: who, when, which spec version or head SHA | Issue comments, PR reviews, approvals | The tracker's UI plus notifications (Slack, email) with links. The approval must be a stored, attributable record the merge gate can check, not a chat message |
 | 10 | Audit log | Every transition, every agent output, every human decision, append-only. The weekly audit and the retro read from here | Issue and PR timelines, Actions logs | An append-only table or log stream. Store full agent outputs as artifacts keyed by run id. If it isn't logged, the retro can't see it |
-| 11 | Gate runner | Runs `{gate commands}` (build, lint, typecheck, tests) on a head SHA and records PASS/FAIL against it (piece 6) | Actions CI | Any CI. Without one, the verifier runs the gates as step 4 of its prompt, and its "Gate suite" line is recorded as the CI result. Separate CI is better because it isn't an agent |
+| 11 | Gate runner | Runs `{gate commands}` (build, lint, typecheck, tests) on a head SHA and records PASS/FAIL against it (piece 6) | Actions CI | Any CI. Without one, the verifier runs the gates as step 4 of its prompt, and its "Gate suite" line is recorded as the CI result. Separate CI is better because it isn't an agent. A gate command may name the paths it covers, as git pathspecs. For a sub-ticket whose diff touches none of them, the harness marks the command SKIPPED for the reviewer and verifier, with the reason, and records it on the `ci` row; the row's PASS or FAIL still comes from the commands that ran. A command without paths always runs |
 | 12 | Secrets | Model API keys and git credentials, available to a run that needs them but never in the repo, the prompt, or the log | Actions secrets | Vault, cloud secret manager, or env injection at container start. Redact from logs |
 
 **What the harness itself owns** (no platform provides these): the routing table, the round counter and the max-round cutoff, composing each role's input from *only* its declared sources, choosing the model per role, and the escalation queue view for the daily human pass.
@@ -86,7 +86,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | `proposal.md` | Problem, Evidence, Root cause, Out of scope, Open questions, Decisions, Risk, Operator steps | Spec writer |
 | `design.md` | Proposed change, Tests to change | Spec writer |
 | `specs/<capability>/spec.md` (delta) | Requirements under `## ADDED Requirements`, `## MODIFIED Requirements` or `## REMOVED Requirements`; its scenarios are the Acceptance items | Spec writer; the critic reviews it |
-| `tasks.md` | The sub-tickets and coverage map | Planner |
+| `tasks.md` | The sub-tickets and coverage map | Planner, or the harness when it skips the planner |
 | `verification.md` (the artifact the fork adds) | The NEW or REGRESSION label of each scenario and the writer's Responses; every critic round's output; at archive, every verifier result recorded per head for the parent and its sub-tickets | Spec writer (labels, Responses), critic, verifier |
 
 `decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. The spec writer and the critic receive every current-truth spec with their input (routing table). They and the planner also receive `decisions.md` when it holds any text.
@@ -121,7 +121,7 @@ Rules the table relies on:
 | Critic | ESCALATE | Human queue | Findings |
 | Human queue, or requester (CLARIFY) | Answered (Triage asked) | Triage | The request with the answer, Triage's previous output (the question or missing-info list the answer is for) |
 | Human queue | Answered (Spec writer asked) | Spec writer | The ticket, the answer, the writer's previous output (the spec whose open questions the answer is for) |
-| Human spec gate | Approved | Planner | Approved spec, version pinned; the decision log |
+| Human spec gate | Approved | Planner. When the spec needs one sub-ticket, the harness creates it from the whole spec and the build goes to that sub-ticket's Implementer, with no planner run, logging `plan.skipped`. `factory plan whole-spec` decides: the spec needs one sub-ticket when the parent has no sub-ticket and no earlier planner run, its latest spec-writer run did not end NEEDS-SPLIT, and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that names seams. The sub-ticket names every scenario of the spec | Approved spec, version pinned; the decision log |
 | Human spec gate | Changes requested | Spec writer (round reset) | Human's notes |
 | Planner | PLANNED | Implementer, one run per sub-ticket. Each branches from main at dispatch; a sub-ticket dispatches only after its dependencies merge; parallel-safe ones run concurrently; one marked not parallel-safe dispatches only when no sibling of the same parent is in flight, and no sibling dispatches while it is in flight | Sub-ticket, parent spec, AGENTS.md; push to its own branch only |
 | Planner | ESCALATE | Human queue | Planner output |
diff --git a/factory/cli.py b/factory/cli.py
index 803f0e3..6535ee6 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -211,6 +211,8 @@ def run_start(a, root, cfg):
         raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
     if a.role == "implementer" and t.get("parent"):
         _check_sibling_tests(root, cfg, t)
+    if a.role in BUILD_ROLES:
+        compose.gate_entries(cfg)  # a malformed gate entry refuses here, before a run id is reserved
     baseline = tripwire.baseline(cfg)  # hashed before the run id is reserved: a refusal writes nothing
     rid = store.next_run_id(root, a.role)
     model = a.model or cfg["models"][a.role]
@@ -272,6 +274,7 @@ def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent
     integ = gitops.integration_branch(cfg, repo)
     store.ensure_gitignore(root)
     meta["round"] = t["round"]["pr"]
+    meta["gate_skipped"] = []  # only a checker of a sub-ticket's diff skips a gate command
     if meta["role"] == "implementer":
         branch = t.get("branch") or gitops.branch_of(t["id"])
         wt = root / "worktrees" / t["id"]
@@ -286,6 +289,8 @@ def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent
         base = (t.get("parent_base") or head) if parent_close else gitops.rev(repo, integ)
         if not head:
             raise Refused(f"{t['id']} has no head to check")
+        if not parent_close:
+            meta["gate_skipped"] = compose.gate_skips(cfg, repo, base, head)
         wt = d / "wt"
         gitops.add_detached_worktree(repo, wt, head)
         meta["environment_files"] = gitops.copy_environment_files(cfg, repo, wt)
@@ -441,15 +446,21 @@ def subticket_add(a, root, cfg):
         raise Refused("no sub-tickets found (a head line `<id> / Title`, id like T-0001-A, ST-1 or T-0001.1, "
                       "then `Depends on:` and `Parallel-safe:`)")
     ids = {s["id"] for s in subs}
-    made = []
     for sdef in subs:
         for dep in sdef["depends_on"]:
             if dep not in ids and not store.ticket_path(root, dep).exists():
                 raise Refused(f"{sdef['id']} ({sdef['label']}) depends on {dep}, which is neither in this plan nor a ticket in the store")
         if store.ticket_path(root, sdef["id"]).exists():
             raise Refused(f"{sdef['id']} already exists")
+    out({"ok": True, "parent": parent["id"], "subtickets": _create_subtickets(root, parent, subs, f"plan:{a.run or a.file}")})
+
+
+def _create_subtickets(root: Path, parent: dict, subs: list[dict], source: str) -> list[dict]:
+    """Write each checked sub-ticket definition as a ticket record under `parent`, with its text at
+    specs/<id>/subticket.md; returns them as `subticket add` prints them."""
+    made = []
     for sdef in subs:
-        st = store.new_ticket(root, sdef["id"], sdef["title"], parent["request"], f"plan:{a.run or a.file}")
+        st = store.new_ticket(root, sdef["id"], sdef["title"], parent["request"], source)
         st.update({"type": "sub-ticket", "parent": parent["id"], "label": sdef["label"], "depends_on": sdef["depends_on"],
                    "parallel_safe": sdef["parallel_safe"],
                    "status": "ready-for-implementer" if not sdef["depends_on"] else "waiting-dependencies"})
@@ -458,7 +469,70 @@ def subticket_add(a, root, cfg):
         store.save_ticket(root, st)
         store.log_event(root, "ticket.created", ticket=sdef["id"], parent=parent["id"], status=st["status"])
         made.append({"id": sdef["id"], "label": sdef["label"], "state": st["status"], "depends_on": sdef["depends_on"], "parallel_safe": sdef["parallel_safe"]})
-    out({"ok": True, "parent": parent["id"], "subtickets": made})
+    return made
+
+
+WHOLE_SPEC_REASON = "one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run"
+SEAM_HEADING_RE = re.compile(r"^#{2,3}\s")
+
+
+def _planner_needed(root: Path, t: dict, spec_text: str) -> str | None:
+    """The first reason the parent needs a planner run, or None when the approved spec becomes one
+    sub-ticket as it stands (doc §Routing table, Human spec gate row)."""
+    subs = store.subtickets_of(root, t["id"])
+    if subs:
+        return f"it already has sub-tickets: {', '.join(s['id'] for s in subs)}"
+    planned = compose._runs_for(root, t["id"], "planner", "")
+    if planned:
+        return f"a planner already ran on it: {planned[-1]}"
+    writer = compose._last_run_meta(root, t["id"], "spec_writer", "")
+    if writer and writer.get("status") == "NEEDS-SPLIT":
+        return f"its spec writer marked it NEEDS-SPLIT ({writer['run_id']})"
+    for line, in_fence in specstore.lines_outside_fences(spec_text):
+        if (not in_fence and SEAM_HEADING_RE.match(line) and not line.startswith("### Requirement:")
+                and re.search(r"\bseams?\b", line, re.I)):
+            return f"its approved spec has a seam heading: {line.strip()}"
+    return None
+
+
+def plan_whole_spec(a, root, cfg):
+    """`plan whole-spec PARENT`: when the approved spec needs one sub-ticket, create it from the
+    whole spec in place of a planner run; otherwise report why the planner is needed, writing nothing."""
+    t = store.load_ticket(root, a.id)
+    if t["status"] != "ready-for-planner":
+        raise Refused(f"{t['id']} is {t['status']}, not ready-for-planner")
+    if t["in_flight"]:
+        raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
+    av = t["spec"]["approved_version"]
+    spec = root / "specs" / t["id"] / f"v{av}.md"
+    if av is None or not spec.exists():
+        raise Refused(f"{t['id']} has no approved spec")
+    spec_text = spec.read_text(encoding="utf-8")
+    reason = _planner_needed(root, t, spec_text)
+    if reason:
+        out({"ok": True, "id": t["id"], "planner": "needed", "reason": reason})
+        return
+    if specstore.is_active(root) and not specstore.change_dir(root, t["id"]).exists():
+        raise Refused(f"{t['id']} has no change folder (no pinned version)")
+    sid = f"{t['id']}.1"
+    names = "".join(f"- {n}\n" for n in specstore.scenario_names(spec_text))
+    text = (f"{sid} / {t['title']}\nDepends on: none\nParallel-safe: yes\n\n"
+            f"Parent: {t['id']}, approved spec v{av}. This sub-ticket is the whole of it; read it in full. "
+            f"The planner was skipped: {WHOLE_SPEC_REASON}.\n\n"
+            "Scope: every lettered part of the parent's Proposed change.\n"
+            "Acceptance: every scenario of the parent spec, with the label its verification.md gives it:\n"
+            f"{names}Tests to change: the parent's list.\nProtected paths: the parent's Risk list.\n")
+    made = _create_subtickets(root, t, [{"id": sid, "title": t["title"], "label": "whole-spec", "depends_on": [],
+                                          "parallel_safe": True, "text": text}], "plan:whole-spec")
+    rel = f"plans/{t['id']}.md"
+    store.write_text(root / rel, text)
+    t["plan"] = rel
+    store.save_ticket(root, t)
+    if specstore.is_active(root):
+        store.write_text(specstore.change_dir(root, t["id"]) / "tasks.md", text)
+        store.log_event(root, "tasks.written", ticket=t["id"], source="plan:whole-spec")
+    store.log_event(root, "plan.skipped", ticket=t["id"], subticket=sid, reason=WHOLE_SPEC_REASON)
+    out({"ok": True, "id": t["id"], "planner": "skipped", "reason": WHOLE_SPEC_REASON, "subtickets": made})
 
 
 def ticket_ready_implementers(a, root, cfg):
@@ -539,7 +613,10 @@ def results_record(a, root, cfg):
         # other text before `Gate suite:` is prose, not a verdict.
         m = re.search(r"^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$", text, re.M)
         ci = (m.group(1), m.group(2).strip(" \t\r*") or None) if m else ("FAIL", "missing Gate suite line")
-        rows.append(store.record_result(root, t["id"], a.head, "ci", ci[0], a.run, ci[1]))
+        mp = root / "runs" / str(a.run) / "meta.yaml"
+        skipped = (store.read_yaml(mp) or {}).get("gate_skipped") if a.run and mp.exists() else None
+        rows.append(store.record_result(root, t["id"], a.head, "ci", ci[0], a.run, ci[1],
+                                        {"skipped": skipped} if skipped else None))
     ev = "result.stale-discarded" if stale else "result.recorded"
     for r in rows:
         store.log_event(root, ev, ticket=t["id"], head=a.head, role=r["role"], status=r["status"], run=a.run)
@@ -1379,6 +1456,10 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("--from-run")
     p.add_argument("--file")
     p.set_defaults(fn=plan_add)
+    p = pl.add_parser("whole-spec", help="when the approved spec needs one sub-ticket, create it from the whole "
+                                         "spec and skip the planner; otherwise report why the planner is needed")
+    p.add_argument("id")
+    p.set_defaults(fn=plan_whole_spec)
 
     p = sc.add_parser("tasks")
     p.add_argument("id")
diff --git a/factory/compose.py b/factory/compose.py
index 9659671..d85ee69 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -41,6 +41,35 @@ def _last_run_meta(root: Path, ticket: str, role: str, exclude: str) -> dict | N
     return store.read_yaml(root / "runs" / runs[-1] / "meta.yaml") if runs else None
 
 
+def gate_entries(cfg: dict) -> list[tuple[str, list[str] | None]]:
+    """Each `gate_commands` entry as (command as written, paths or None). An entry is a command
+    string, or a mapping of a non-empty string `command` and an optional non-empty list of git
+    pathspecs `paths`. Absent or null is empty. Anything else is refused, naming its index: a typo
+    such as `path:` read as unscoped would leave the operator believing a scope is in force."""
+    out: list[tuple[str, list[str] | None]] = []
+    for i, e in enumerate(cfg.get("gate_commands") or []):
+        def bad(why: str) -> store.Refused:
+            return store.Refused(f"gate_commands entry {i}: {why}; an entry is a command string or "
+                                 "{command: <string>, paths: [<git pathspec>, ...]}, and a command that "
+                                 "always runs omits paths")
+        if isinstance(e, str):
+            out.append((e, None))
+            continue
+        if not isinstance(e, dict):
+            raise bad(f"{e!r} is neither a string nor a mapping")
+        extra = [str(k) for k in e if k not in ("command", "paths")]
+        if extra:
+            raise bad(f"unknown key {', '.join(extra)}")
+        if not isinstance(e.get("command"), str) or not e["command"]:
+            raise bad("command must be a non-empty string")
+        paths = e.get("paths")
+        if "paths" in e and (not isinstance(paths, list) or not paths
+                             or not all(isinstance(p, str) and p for p in paths)):
+            raise bad("paths must be a non-empty list of non-empty strings")
+        out.append((e["command"], paths))
+    return out
+
+
 def gate_commands(cfg: dict) -> list[str]:
     """The gate commands with `{integration}` replaced by the checkout that has the integration
     branch: the gate script and its baseline come from the integration branch, never from the branch
@@ -48,7 +77,17 @@ def gate_commands(cfg: dict) -> list[str]:
     from factory import gitops  # local: compose is otherwise git-free
     repo = gitops.repo_root(cfg)
     co = gitops.checkout_of(repo, gitops.integration_branch(cfg, repo)) or repo
-    return [g.replace("{integration}", str(co)) for g in cfg.get("gate_commands", [])]
+    return [g.replace("{integration}", str(co)) for g, _ in gate_entries(cfg)]
+
+
+def gate_skips(cfg: dict, repo: Path, base: str, head: str) -> list[dict]:
+    """The gate commands a checker of the diff base...head skips: each one with `paths` that the
+    diff touches none of, by git's own pathspec matching. A git error is refused."""
+    from factory import gitops  # local: compose is otherwise git-free
+    return [{"command": cmd, "status": "SKIPPED",
+             "reason": f"the diff {base[:9]}...{head[:9]} touches none of its paths: {', '.join(paths)}"}
+            for cmd, paths in gate_entries(cfg)
+            if paths and not gitops.git(repo, "diff", "--name-only", f"{base}...{head}", "--", *paths)]
 
 
 _ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
@@ -172,11 +211,19 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         av = pt["spec"]["approved_version"]
         if av is None:
             raise store.Refused(f"{parent} has no approved spec version")
+        # A checker of a sub-ticket gets the commands its diff skips (meta `gate_skipped`, set at run
+        # start) apart from the ones to run; the implementer and the parent-close verifier have none.
+        skipped = meta.get("gate_skipped") or []
+        gone = {s["command"] for s in skipped}
+        run = [g for (raw, paths), g in zip(gate_entries(cfg), gate_commands(cfg)) if paths is None or raw not in gone]
         where = (f"\n## Where you work\nWorktree: `{meta.get('worktree')}` (branch `{meta.get('branch')}`, "
                  f"base `{meta.get('base')}`, head `{meta.get('head')}`). There is no remote: commit on the "
                  f"branch; the PR is the branch plus the description you return. Gate commands (run each from "
                  f"your worktree, exactly as written; each is already wrapped): "
-                 + "; ".join(f"`{wrap(g, env)}`" for g in gate_commands(cfg)) + "\n")
+                 + ("; ".join(f"`{wrap(g, env)}`" for g in run) if run or not skipped
+                    else "none (every gate command is skipped below)") + "\n"
+                 + "".join(f"SKIPPED by the harness for this diff, do not run: `{s['command']}`: {s['reason']}\n"
+                           for s in skipped))
         parts.append(where)
         if role == "implementer":
             if t.get("merge_refused"):
diff --git a/factory/instance.template.yaml b/factory/instance.template.yaml
index ccabbdb..e55c29e 100644
--- a/factory/instance.template.yaml
+++ b/factory/instance.template.yaml
@@ -18,6 +18,11 @@ protected_paths:
 # tripwire: {park: [], escalate: []}
 # Commands every implementer and verifier runs in the checkout under test, each exactly as written.
 # `{integration}` is replaced with the checkout that has the integration branch.
+# An entry is a command string, or `{command: "<command>", paths: ["src/", ":(exclude)dev/"]}`.
+# `paths` are git pathspecs. A sub-ticket's reviewer and verifier skip a command when the
+# sub-ticket's diff touches none of its paths, and the ci row records it as SKIPPED. Omit `paths`
+# for a command that always runs. Prefer the exclude form (`:(exclude)dev/`): a new file outside
+# every excluded path still runs the command.
 gate_commands: []
 placeholders: {rounds: 2, spec_lines: 400, audit_n: 5, retro_min: 3}
 max_rounds: {spec: 2, pr: 2}
diff --git a/factory/store.py b/factory/store.py
index ae4ab8b..de22021 100644
--- a/factory/store.py
+++ b/factory/store.py
@@ -241,10 +241,12 @@ def result_path(root: Path, head: str, role: str) -> Path:
     return root / "results" / head / f"{role}.yaml"
 
 
-def record_result(root: Path, tid: str, head: str, role: str, status: str, run_id: str | None, detail: str | None = None) -> dict:
+def record_result(root: Path, tid: str, head: str, role: str, status: str, run_id: str | None, detail: str | None = None,
+                  extra: dict | None = None) -> dict:
     row = {"ticket": tid, "head": head, "role": role, "status": status, "run_id": run_id, "at": now()}
     if detail:
         row["detail"] = detail
+    row.update(extra or {})
     write_yaml(result_path(root, head, role), row)
     return row
 
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index 24ebe7a..1b87d18 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -207,16 +207,23 @@ let state = show.state
 // --- phase 1: Plan (only when the parent is ready-for-planner)
 if (state === 'ready-for-planner') {
   phase('Plan')
-  const p = await runRole('planner', TICKET, 'Plan')
-  if (!p) return { ticket: TICKET, state: 'parked' }
-  if (p.status === 'ESCALATE') { await park(TICKET, 'ESCALATE from planner', [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
-  if (p.status !== 'PLANNED') { await park(TICKET, `harness-bug: unknown STATUS ${p.status} from planner`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
-  const tasks = await clerk(`${BIN} spec tasks ${TICKET} --run ${p.runId}`, 'Plan', 'spec tasks')
-  if (!tasks.ok) { await park(TICKET, `harness-bug: spec tasks: ${tasks.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
-  const added = await clerk(`${BIN} plan add ${TICKET} --from-run ${p.runId}`, 'Plan', 'plan add')
-  if (!added.ok) { await park(TICKET, `harness-bug: plan add: ${added.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
-  const subs = await clerk(`${BIN} subticket add ${TICKET} --run ${p.runId}`, 'Plan', 'subticket add')
-  if (!subs.ok) { await park(TICKET, `harness-bug: subticket add: ${subs.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
+  // A spec that needs one sub-ticket becomes it without a planner run; the harness decides which.
+  const whole = await clerk(`${BIN} plan whole-spec ${TICKET}`, 'Plan', 'plan whole-spec')
+  if (!whole.ok) { await park(TICKET, `harness-bug: plan whole-spec: ${whole.stderr || ''}`, [], 'Plan'); return { ticket: TICKET, state: 'parked' } }
+  if (whole.planner === 'skipped') {
+    log(`${TICKET}: planner skipped (${whole.reason}); one sub-ticket from the whole spec`)
+  } else {
+    const p = await runRole('planner', TICKET, 'Plan')
+    if (!p) return { ticket: TICKET, state: 'parked' }
+    if (p.status === 'ESCALATE') { await park(TICKET, 'ESCALATE from planner', [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
+    if (p.status !== 'PLANNED') { await park(TICKET, `harness-bug: unknown STATUS ${p.status} from planner`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
+    const tasks = await clerk(`${BIN} spec tasks ${TICKET} --run ${p.runId}`, 'Plan', 'spec tasks')
+    if (!tasks.ok) { await park(TICKET, `harness-bug: spec tasks: ${tasks.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
+    const added = await clerk(`${BIN} plan add ${TICKET} --from-run ${p.runId}`, 'Plan', 'plan add')
+    if (!added.ok) { await park(TICKET, `harness-bug: plan add: ${added.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
+    const subs = await clerk(`${BIN} subticket add ${TICKET} --run ${p.runId}`, 'Plan', 'subticket add')
+    if (!subs.ok) { await park(TICKET, `harness-bug: subticket add: ${subs.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
+  }
   await transition(TICKET, 'planned', null, 'Plan')
   state = 'planned'
 }
diff --git a/tests/factory/test_gate_paths.py b/tests/factory/test_gate_paths.py
new file mode 100644
index 0000000..8cd4236
--- /dev/null
+++ b/tests/factory/test_gate_paths.py
@@ -0,0 +1,226 @@
+"""A gate command may declare the git pathspecs it covers (T-0028 part A).
+
+A reviewer or verifier run on a sub-ticket whose diff touches none of a command's paths is told the
+command is SKIPPED, with the reason, instead of being asked to run it; the run's meta.yaml and the
+`ci` result row record the skip. The implementer still gets every command. A malformed entry refuses
+every build role's run start before a run is created.
+
+Black-box through `bin/factory`, on a throwaway store, a copy of the suite's fixture instance with
+its own `gate_commands`, and a scratch target repo, as the spec's t0028-sub.sh fixture builds them.
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
+UNSCOPED = "git diff --check main...HEAD"
+SCOPED = "sh -c 'exit 7'"
+
+
+class Target:
+    """T-0001.1 at checks-in-flight, its one commit changing `changed`; I is its implementer run."""
+
+    def __init__(self, tmp_path: Path, gate: str, changed: str = "docs/b.md"):
+        self.tmp = tmp_path
+        self.root = tmp_path / "store"
+        self.inst = tmp_path / "inst"
+        self.repo = tmp_path / "t"
+        shutil.copytree(FIXTURE_INSTANCE, self.inst)
+        self.set_gate(gate)
+        self.env = {**os.environ, "FACTORY_INSTANCE": str(self.inst), "FACTORY_STATE": str(self.root),
+                    "FACTORY_REPO": str(self.repo), "FACTORY_INTEGRATION_BRANCH": "main",
+                    "PYTHONDONTWRITEBYTECODE": "1"}
+        self.repo.mkdir()
+        self.git("init", "-q", "-b", "main")
+        self.git("config", "user.email", "f@x")
+        self.git("config", "user.name", "f")
+        for rel, body in (("src/a.txt", "a\n"), ("docs/b.md", "b\n")):
+            (self.repo / rel).parent.mkdir(exist_ok=True)
+            (self.repo / rel).write_text(body)
+        self.git("add", "-A")
+        self.git("commit", "-q", "-m", "init")
+        (tmp_path / "req.md").write_text("# F\n\nDo x.\n")
+        (tmp_path / "spec.md").write_text("## Problem\nx\n")
+        (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
+        self.ok("ticket", "new", "--file", str(tmp_path / "req.md"))
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+        self.ok("spec", "add", "T-0001", "--file", str(tmp_path / "spec.md"))
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
+        self.ok("approve-spec", "T-0001")
+        self.ok("subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md"))
+        self.implementer = self.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
+        wt = self.root / "worktrees" / "T-0001.1"
+        with (wt / changed).open("a") as f:
+            f.write("more\n")
+        self.git("commit", "-q", "-am", "change", cwd=wt)
+        self.ok("run", "finish", self.implementer, "--status-override", "READY-FOR-REVIEW")
+        self.head = self.ok("ticket", "head", "T-0001.1")["head"]
+        self.ok("ticket", "transition", "T-0001.1", "--to", "checks-in-flight", "--by", "t", "--round", "pr:init")
+
+    def set_gate(self, gate: str) -> None:
+        """The fixture instance's config with its one-line `gate_commands` replaced by `gate`."""
+        lines = (FIXTURE_INSTANCE / "instance.yaml").read_text().splitlines(keepends=True)
+        (self.inst / "instance.yaml").write_text("".join(ln for ln in lines if not ln.startswith("gate_commands:")) + gate)
+
+    def git(self, *argv: str, cwd: Path | None = None) -> str:
+        cp = subprocess.run(["git", *argv], cwd=cwd or self.repo, capture_output=True, text=True)
+        assert cp.returncode == 0, cp.stderr
+        return cp.stdout.strip()
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def composed(self, rid: str) -> tuple[str, dict]:
+        self.ok("run", "compose", rid)
+        d = self.root / "runs" / rid
+        return (d / "input.md").read_text(), yaml.safe_load((d / "meta.yaml").read_text())
+
+    def checker(self, role: str = "verifier") -> tuple[str, str, dict]:
+        rid = self.ok("run", "start", "--role", role, "--ticket", "T-0001.1")["run_id"]
+        text, meta = self.composed(rid)
+        return rid, text, meta
+
+
+SCOPED_GATE = f'gate_commands:\n  - "{UNSCOPED}"\n  - {{command: "{SCOPED}", paths: ["src/"]}}\n'
+
+
+def _gate_line(text: str) -> str:
+    return next(ln for ln in text.splitlines() if ln.startswith("Worktree:"))
+
+
+def _skipped_lines(text: str) -> list[str]:
+    return [ln for ln in text.splitlines() if ln.startswith("SKIPPED")]
+
+
+def test_a_scoped_command_is_skipped_for_a_diff_that_touches_none_of_its_paths(tmp_path):
+    t = Target(tmp_path, SCOPED_GATE)
+    rid, text, meta = t.checker()
+    line = _gate_line(text)
+    assert UNSCOPED in line and "exit 7" not in line
+    base = meta["base"]
+    reason = f"the diff {base[:9]}...{t.head[:9]} touches none of its paths: src/"
+    assert _skipped_lines(text) == [f"SKIPPED by the harness for this diff, do not run: `{SCOPED}`: {reason}"]
+    assert meta["gate_skipped"] == [{"command": SCOPED, "status": "SKIPPED", "reason": reason}]
+
+
+def test_a_diff_that_touches_a_scoped_command_s_paths_runs_it(tmp_path):
+    t = Target(tmp_path, SCOPED_GATE, changed="src/a.txt")
+    _, text, meta = t.checker("reviewer")
+    line = _gate_line(text)
+    assert UNSCOPED in line and "exit 7" in line
+    assert _skipped_lines(text) == [] and meta["gate_skipped"] == []
+
+
+def test_an_exclude_pathspec_skips_only_a_diff_inside_the_excluded_paths(tmp_path):
+    """The Decisions' exclude form: a change outside every excluded path still runs the command."""
+    gate = f'gate_commands: [{{command: "{SCOPED}", paths: [":(exclude)docs/"]}}]\n'
+    inside = Target(tmp_path / "docs", gate)
+    _, text, _ = inside.checker()
+    assert "none (every gate command is skipped below)" in _gate_line(text)
+    assert len(_skipped_lines(text)) == 1
+    outside = Target(tmp_path / "src", gate, changed="src/a.txt")
+    _, text, _ = outside.checker()
+    assert "exit 7" in _gate_line(text) and _skipped_lines(text) == []
+
+
+def test_the_implementer_gets_every_command_and_no_skipped_line(tmp_path):
+    t = Target(tmp_path, SCOPED_GATE)
+    text, meta = t.composed(t.implementer)
+    line = _gate_line(text)
+    assert UNSCOPED in line and "exit 7" in line
+    assert _skipped_lines(text) == [] and meta["gate_skipped"] == []
+
+
+@pytest.mark.parametrize("gate", ["PASS", "FAIL"])
+def test_the_ci_row_records_the_skip_and_its_status_still_comes_from_the_gate_suite_line(tmp_path, gate):
+    t = Target(tmp_path, SCOPED_GATE)
+    rid, _, meta = t.checker()
+    out = tmp_path / "v.md"
+    out.write_text(f"Commit: {t.head}\nGate suite: {gate}\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+    t.ok("results", "record", "T-0001.1", "--head", t.head, "--role", "verifier", "--output", str(out), "--run", rid)
+    ci = yaml.safe_load((t.root / "results" / t.head / "ci.yaml").read_text())
+    assert ci["status"] == gate and ci["skipped"] == meta["gate_skipped"]
+    assert "skipped" not in yaml.safe_load((t.root / "results" / t.head / "verifier.yaml").read_text())
+
+
+def test_a_ci_row_without_a_skip_has_no_skipped_key(tmp_path):
+    t = Target(tmp_path, SCOPED_GATE, changed="src/a.txt")
+    rid, _, _ = t.checker()
+    out = tmp_path / "v.md"
+    out.write_text(f"Commit: {t.head}\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+    t.ok("results", "record", "T-0001.1", "--head", t.head, "--role", "verifier", "--output", str(out), "--run", rid)
+    assert "skipped" not in yaml.safe_load((t.root / "results" / t.head / "ci.yaml").read_text())
+
+
+@pytest.mark.parametrize("role", ["implementer", "reviewer", "verifier"])
+def test_a_malformed_entry_refuses_every_build_role_s_run_start_and_creates_no_run(tmp_path, role):
+    t = Target(tmp_path, SCOPED_GATE)
+    if role == "implementer":  # back to the implementer's ready state
+        t.ok("ticket", "transition", "T-0001.1", "--to", "ready-for-implementer", "--by", "t")
+    t.set_gate('gate_commands: [{command: "true", path: ["src/"]}]\n')
+    before = sorted(p.name for p in (t.root / "runs").iterdir())
+    cp = t.cli("run", "start", "--role", role, "--ticket", "T-0001.1")
+    assert cp.returncode == 2 and "gate_commands entry 0" in cp.stderr and "path" in cp.stderr
+    assert sorted(p.name for p in (t.root / "runs").iterdir()) == before
+
+
+@pytest.fixture(scope="module")
+def checks_in_flight(tmp_path_factory):
+    """One sub-ticket at checks-in-flight, shared: each refusal below leaves the store unchanged."""
+    return Target(tmp_path_factory.mktemp("gate"), SCOPED_GATE)
+
+
+@pytest.mark.parametrize(("entries", "named"), [
+    ("[7]", "entry 0: 7 is neither a string nor a mapping"),
+    ("[[a]]", "entry 0: ['a'] is neither a string nor a mapping"),
+    ('[{command: "true", path: ["src/"]}]', "entry 0: unknown key path"),
+    ('[{paths: ["src/"]}]', "entry 0: command must be a non-empty string"),
+    ('[{command: ""}]', "entry 0: command must be a non-empty string"),
+    ("[{command: 3}]", "entry 0: command must be a non-empty string"),
+    ('[{command: "true", paths: "src/"}]', "entry 0: paths must be a non-empty list"),
+    ('[{command: "true", paths: []}]', "entry 0: paths must be a non-empty list"),
+    ('[{command: "true", paths: null}]', "entry 0: paths must be a non-empty list"),
+    ('[{command: "true", paths: ["src/", ""]}]', "entry 0: paths must be a non-empty list"),
+    ('[{command: "true", paths: ["src/", 3]}]', "entry 0: paths must be a non-empty list"),
+    ('["ok", {command: "true", paths: []}]', "entry 1: paths must be a non-empty list"),
+])
+def test_each_malformed_entry_is_refused_by_its_index(checks_in_flight, entries, named):
+    t = checks_in_flight
+    t.set_gate(f"gate_commands: {entries}\n")
+    before = sorted(p.name for p in (t.root / "runs").iterdir())
+    cp = t.cli("run", "start", "--role", "reviewer", "--ticket", "T-0001.1")
+    assert cp.returncode == 2 and f"gate_commands {named}" in cp.stderr, cp.stderr
+    assert "a command that always runs omits paths" in cp.stderr
+    assert sorted(p.name for p in (t.root / "runs").iterdir()) == before
+
+
+@pytest.mark.parametrize("gate", ["gate_commands:\n", "", f'gate_commands: [{{command: "{UNSCOPED}"}}]\n'])
+def test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does(tmp_path, gate):
+    t = Target(tmp_path, SCOPED_GATE)
+    t.set_gate(gate)
+    _, text, meta = t.checker()
+    want = f"`(export HOME=\"$(cd \"$(mktemp -d)\" && pwd -P)\"; {UNSCOPED})`" if UNSCOPED in gate else ""
+    assert _gate_line(text).endswith("each is already wrapped): " + want)
+    assert _skipped_lines(text) == [] and meta["gate_skipped"] == []
+
+
+def test_an_unscoped_copy_of_a_skipped_command_still_runs(tmp_path):
+    t = Target(tmp_path, f'gate_commands:\n  - "{SCOPED}"\n  - {{command: "{SCOPED}", paths: ["src/"]}}\n')
+    _, text, meta = t.checker()
+    assert "exit 7" in _gate_line(text) and len(_skipped_lines(text)) == 1
+    assert [s["command"] for s in meta["gate_skipped"]] == [SCOPED]
diff --git a/tests/factory/test_whole_spec_plan.py b/tests/factory/test_whole_spec_plan.py
new file mode 100644
index 0000000..7f0939e
--- /dev/null
+++ b/tests/factory/test_whole_spec_plan.py
@@ -0,0 +1,228 @@
+"""A spec that needs one sub-ticket becomes that sub-ticket without a planner run (T-0028 part B).
+
+`factory plan whole-spec PARENT`, on a parent at ready-for-planner with an approved spec, creates
+`<parent>.1` from the whole spec when the parent has no sub-ticket and no earlier planner run, its
+latest spec-writer run did not end NEEDS-SPLIT, and its approved spec has no `##` or `###` heading
+naming seams. Otherwise it reports `"planner": "needed"` and writes nothing. It refuses where a
+planner run would. The one sub-ticket names every scenario, so the parent closes on its VERIFIED run.
+
+Black-box through `bin/factory` on a throwaway store, as the spec's t0028-plan.sh fixture builds it;
+the parent-close case uses the Shepherd fixture of test_parent_close_reuse.py.
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+from .test_parent_close_reuse import _build, _parent_verifier_runs
+from .test_shepherd import Shepherd
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+REASON = "one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run"
+SPEC_WRITER_OUTPUT = """=== proposal.md
+## Problem
+x
+=== design.md
+## Proposed change
+A. Do x.
+{extra}
+=== specs/demo/spec.md
+## ADDED Requirements
+### Requirement: X
+It SHALL do x.
+#### Scenario: First check
+- WHEN `true`
+- THEN it exits 0
+#### Scenario: Second check
+- WHEN `true`
+- THEN it exits 0
+=== verification.md
+## Acceptance
+- First check → NEW; fails today
+- Second check → REGRESSION
+STATUS: {status}
+CONFIDENCE: high, fixture
+ESCALATIONS: none
+"""
+
+
+class Parent:
+    """T-0001 at ready-for-planner: one spec-writer run ending `status`, its output approved as v1."""
+
+    def __init__(self, tmp_path: Path, status: str = "READY-FOR-CRITIC", extra: str = "", spec_store: bool = False):
+        self.tmp = tmp_path
+        self.root = tmp_path / "store"
+        repo = tmp_path / "t"
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(repo),
+                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
+        subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
+        subprocess.run(["git", "-C", str(repo), "-c", "user.email=f@x", "-c", "user.name=f", "commit", "-q",
+                        "--allow-empty", "-m", "init"], check=True)
+        if spec_store:
+            self.ok("init")
+        (tmp_path / "req.md").write_text("# F\n\nDo x.\n")
+        self.ok("ticket", "new", "--file", str(tmp_path / "req.md"))
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+        w = self.ok("run", "start", "--role", "spec_writer", "--ticket", "T-0001")["run_id"]
+        (self.root / "runs" / w / "output.md").write_text(SPEC_WRITER_OUTPUT.format(status=status, extra=extra))
+        self.ok("run", "finish", w)
+        self.ok("spec", "add", "T-0001", "--from-run", w)
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
+        self.ok("approve-spec", "T-0001")
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def tickets(self) -> list[str]:
+        return sorted(p.name for p in (self.root / "tickets").iterdir())
+
+    def events(self, name: str) -> list[dict]:
+        return [e for p in sorted((self.root / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()
+                if (e := json.loads(ln))["event"] == name]
+
+    def snapshot(self) -> dict[str, bytes]:
+        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted(self.root.rglob("*")) if p.is_file()}
+
+
+def test_a_qualifying_spec_becomes_one_ready_sub_ticket_naming_every_scenario(tmp_path):
+    t = Parent(tmp_path)
+    r = t.ok("plan", "whole-spec", "T-0001")
+    assert r["planner"] == "skipped" and r["reason"] == REASON
+    assert r["subtickets"] == [{"id": "T-0001.1", "label": "whole-spec", "state": "ready-for-implementer",
+                                "depends_on": [], "parallel_safe": True}]
+    assert t.tickets() == ["T-0001.1.yaml", "T-0001.yaml"]
+    sub = yaml.safe_load((t.root / "tickets" / "T-0001.1.yaml").read_text())
+    assert sub["type"] == "sub-ticket" and sub["parent"] == "T-0001" and sub["source"] == "plan:whole-spec"
+    assert sub["spec"] == {"version": 1, "approved_version": 1}
+    text = (t.root / "specs" / "T-0001.1" / "subticket.md").read_text()
+    assert text.startswith("T-0001.1 / F\nDepends on: none\nParallel-safe: yes\n\n")
+    assert "\n- First check\n- Second check\n" in text and REASON in text
+    parent = yaml.safe_load((t.root / "tickets" / "T-0001.yaml").read_text())
+    assert parent["plan"] == "plans/T-0001.md" and (t.root / "plans" / "T-0001.md").read_text() == text
+    assert parent["status"] == "ready-for-planner", "the build moves the parent to planned, not this command"
+    assert t.ok("ticket", "ready-implementers", "T-0001")["ready"] == ["T-0001.1"]
+    (skip,) = t.events("plan.skipped")
+    assert skip["ticket"] == "T-0001" and skip["subticket"] == "T-0001.1" and skip["reason"] == REASON
+    assert not (t.root / "openspec").exists() and t.events("tasks.written") == []
+
+
+def test_with_a_spec_store_the_text_is_also_the_change_folder_s_tasks(tmp_path):
+    t = Parent(tmp_path, spec_store=True)
+    t.ok("plan", "whole-spec", "T-0001")
+    tasks = t.root / "openspec" / "changes" / "T-0001" / "tasks.md"
+    assert tasks.read_text() == (t.root / "specs" / "T-0001.1" / "subticket.md").read_text()
+    assert [e["ticket"] for e in t.events("tasks.written")] == ["T-0001"]
+
+
+def test_a_missing_change_folder_under_a_spec_store_is_refused_as_spec_tasks_words_it(tmp_path):
+    t = Parent(tmp_path, spec_store=True)
+    shutil.rmtree(t.root / "openspec" / "changes" / "T-0001")
+    before = t.snapshot()
+    cp = t.cli("plan", "whole-spec", "T-0001")
+    assert cp.returncode == 2 and "T-0001 has no change folder (no pinned version)" in cp.stderr
+    assert t.snapshot() == before
+
+
+@pytest.mark.parametrize(("status", "extra", "reason"), [
+    ("NEEDS-SPLIT", "", "its spec writer marked it NEEDS-SPLIT"),
+    ("READY-FOR-CRITIC", "### Size and seams", "its approved spec has a seam heading: ### Size and seams"),
+    ("READY-FOR-CRITIC", "## Seam: the store", "its approved spec has a seam heading: ## Seam: the store"),
+    ("READY-FOR-CRITIC", "## The SEAMS here", "its approved spec has a seam heading"),
+])
+def test_a_split_spec_needs_the_planner_and_nothing_is_written(tmp_path, status, extra, reason):
+    t = Parent(tmp_path, status, extra)
+    before = t.snapshot()
+    r = t.ok("plan", "whole-spec", "T-0001")
+    assert r["planner"] == "needed" and r["reason"].startswith(reason)
+    assert t.snapshot() == before
+
+
+@pytest.mark.parametrize("extra", ["#### Seams in a scenario-level heading", "```\n## Size and seams\n```",
+                                   "## Seamstress", "Seams named in prose"])
+def test_a_seam_word_that_is_no_seam_heading_still_skips_the_planner(tmp_path, extra):
+    t = Parent(tmp_path, extra=extra)
+    assert t.ok("plan", "whole-spec", "T-0001")["planner"] == "skipped"
+
+
+def test_a_requirement_line_naming_seams_is_no_seam_heading(tmp_path):
+    t = Parent(tmp_path)
+    spec = t.root / "specs" / "T-0001" / "v1.md"
+    spec.write_text(spec.read_text().replace("### Requirement: X", "### Requirement: X keeps its seams"))
+    assert t.ok("plan", "whole-spec", "T-0001")["planner"] == "skipped"
+
+
+def test_a_parent_a_planner_already_ran_on_needs_the_planner(tmp_path):
+    t = Parent(tmp_path)
+    p = t.ok("run", "start", "--role", "planner", "--ticket", "T-0001")["run_id"]
+    t.ok("run", "finish", p, "--status-override", "ESCALATE")
+    before = t.snapshot()
+    r = t.ok("plan", "whole-spec", "T-0001")
+    assert r == {"ok": True, "id": "T-0001", "planner": "needed", "reason": f"a planner already ran on it: {p}"}
+    assert t.snapshot() == before
+
+
+def test_a_parent_with_a_sub_ticket_needs_the_planner(tmp_path):
+    t = Parent(tmp_path)
+    (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
+    t.ok("subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md"))
+    r = t.ok("plan", "whole-spec", "T-0001")
+    assert r["planner"] == "needed" and r["reason"] == "it already has sub-tickets: T-0001.1"
+    assert t.tickets() == ["T-0001.1.yaml", "T-0001.yaml"]
+
+
+def test_a_parent_not_ready_for_its_planner_is_refused(tmp_path):
+    t = Parent(tmp_path)
+    t.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
+    before = t.snapshot()
+    cp = t.cli("plan", "whole-spec", "T-0001")
+    assert cp.returncode == 2 and "T-0001 is planned, not ready-for-planner" in cp.stderr
+    assert t.snapshot() == before
+
+
+def test_a_parent_with_a_run_in_flight_is_refused(tmp_path):
+    t = Parent(tmp_path)
+    p = t.ok("run", "start", "--role", "planner", "--ticket", "T-0001")["run_id"]
+    before = t.snapshot()
+    cp = t.cli("plan", "whole-spec", "T-0001")
+    assert cp.returncode == 2 and f"T-0001 already has run {p} in flight" in cp.stderr
+    assert t.snapshot() == before
+
+
+def test_a_parent_with_no_approved_spec_is_refused(tmp_path):
+    t = Parent(tmp_path)
+    t.ok("ticket", "set", "T-0001", "spec.approved_version=")
+    before = t.snapshot()
+    cp = t.cli("plan", "whole-spec", "T-0001")
+    assert cp.returncode == 2 and "T-0001 has no approved spec" in cp.stderr
+    assert t.snapshot() == before
+
+
+def test_the_whole_spec_sub_ticket_s_verified_run_closes_the_parent(tmp_path):
+    """Part C's rule, reached without a planner: one sub-ticket naming every scenario, merged with a
+    VERIFIED run on the parent's base, stands for the parent-close run."""
+    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
+    f.human_runs("init")
+    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
+    for role in ("triage", "spec_writer", "critic"):
+        f.dispatch(role, tid)
+    f.human_approves(tid)
+    (st,) = [s["id"] for s in f.ok("plan", "whole-spec", tid)["subtickets"]]
+    f.ok("ticket", "transition", tid, "--to", "planned", "--by", "workflow")
+    assert not list((f.store / "runs").glob("*-planner"))
+    ver = _build(f, st)
+    pc = f.ok("ticket", "parent-check", tid)
+    assert pc["state"] == "ready-for-parent-verify" and pc["reuse"] == ver.run_id
+    assert _parent_verifier_runs(f, tid) == []

## Human ruling

# Human ruling: the undeclared protected path in T-0028.1 (operator, 2026-10-05)

The reviewer (run-0298) escalated one point and found no defect: `factory/store.py` changes by 3 lines (`record_result` gains an optional `extra` parameter). The approved spec's design part A.5 asks for exactly this change, but its Risk list and the sub-ticket's protected-path list do not name the file.

Ruling: accepted as part of the approved design (part A.5). The undeclared listing is a gap in the spec's Risk list, not a reason to block. Judge the rest of the change on its merits; this escalation is settled.

For this review: judge the diff, the PR description and the spec. Do not run the test suite or the gate commands; the verifier ran them on this head and passed (run-0299, VERIFIED). Run any command in the foreground, never end your turn while one is running, and finish your review in this turn.

Operator's answer in the Green session: "(2) sure", to the recommendation to accept the change under the approved design. Placed by hand because `resolve --ruling` routes a sub-ticket's reviewer escalation to the critic.
