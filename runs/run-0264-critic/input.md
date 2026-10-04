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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0264-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0264-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v1)

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

## Current truth: build-dispatch

# build-dispatch

## Requirements

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

### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

## Current truth: harness-docs

# harness-docs

## Requirements

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

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 dirs=1 prompts=0`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

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

## Current truth: live-store-guard

# live-store-guard

## Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Writes from inside a store's run directories or code checkouts are refused, marked or not
Every `factory` command on an instance's own store except the read-only list above MUST be refused with exit 2, writing nothing, when the caller's directory lies under that store's `runs/` or `worktrees/`, whether or not its environment has `FACTORY_DISPATCH=1` and whether or not any run is in flight.

#### Scenario: Marked writes from a run's scratch directory or a worktree directory are refused, init included
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && mkdir -p $S/worktrees/T-0001/sub && S0=$(snap); cd $W && FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B init --repo-name x >/dev/null 2>&1; i=$?; cd $S/worktrees/T-0001/sub && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "scratch_decision=$d scratch_init=$i worktree_new=$n store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`

#### Scenario: Writes from a finished run's scratch directory are refused with no run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1) && S0=$(snap); cd $W && $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "idle=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]') new=$n decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `idle=1 new=2 decision=2 store=unchanged`

### Requirement: Reads, marked commands from outside the store, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands SHALL succeed from anywhere, a command with `FACTORY_DISPATCH=1` run from outside the store's `runs/` and `worktrees/` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced from any directory; with no run in flight, unmarked writes from outside those directories SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; cd $W && $B ticket show T-0001 >/dev/null 2>&1; w=$?; echo "show=$s config=$c log=$l results=$r inside=$w")`
- THEN it prints exactly `show=0 config=0 log=0 results=0 inside=0`

#### Scenario: A marked write from the repository root still writes while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && cd $T/tgt && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced, even from a run's scratch directory
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_STATE=$T/s $B init >/dev/null 2>&1); i=$?; cd $W && FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

### Requirement: The marker does not lift the harness lock
A command with `FACTORY_DISPATCH=1` on an instance's own store MUST still be refused by the harness lock's uncommitted-edit check, with exit 2 and nothing written, whether or not a run is in flight.

#### Scenario: A marked write from a harness checkout with an uncommitted edit is still refused
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $T/c/bin/factory ticket new --file $T/req.md >/dev/null && $T/c/bin/factory run start --role triage --ticket T-0001 >/dev/null && echo '# uncommitted edit' >> $T/c/factory/status.py && S0=$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum) && FACTORY_DISPATCH=1 $T/c/bin/factory decision add T-0001 x >/dev/null 2>$T/err; echo "exit=$? lock=$(head -1 $T/err | grep -c 'has uncommitted changes:$') store=$([ "$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 lock=1 store=unchanged`

## Current truth: store-setup

# store-setup

## Requirements

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

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)
2026-10-04 T-0024 Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
2026-10-04 T-0024 While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
2026-10-04 T-0024 A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
2026-10-04 T-0024 The location rule is checked first, then the marker, then the in-flight list.
2026-10-04 T-0024 The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
2026-10-04 T-0024 The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
2026-10-04 T-0024 The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
2026-10-04 T-0024 A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
2026-10-04 T-0024 The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
2026-10-04 T-0024 A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
2026-10-04 T-0024 The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
2026-10-04 T-0024 The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
2026-10-04 T-0024 Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
2026-10-04 T-0024 Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.
2026-10-04 T-0022 Removing clearly redundant work (a step, run or check that cannot change any outcome) is pre-approved, provided every refusal the pipeline gives today still fires (operator, 2026-10-04: 'slashing clearly redundant work is always going to be OK, if we trust our process')
2026-10-04 T-0022 Under a sub-ticket's Tests to change, the planner may list tests an earlier sibling of the same parent added, with a harness check that each first appeared in a sibling's merge; pre-existing tests still need the approved spec (operator, #40)
