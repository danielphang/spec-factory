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
