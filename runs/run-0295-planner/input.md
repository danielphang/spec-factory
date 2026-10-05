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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0295-planner/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0295-planner/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Approved spec (v1, pinned)

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
2026-10-04 T-0025 The store lives on its own branch, `factory-store`, checked out as a git worktree at the store's path (B1). This is for the operator to confirm at the spec gate. Rejected: B2, the branch written through git plumbing with no working copy. It needs new harness commands to snapshot, show and restore the store, and `git clean -fdx` in the integration checkout deletes the store (Evidence). Rejected: A, a gate exception (operator, 2026-10-04).
2026-10-04 T-0025 A store path must be one the integration branch has never tracked. Both existing stores move from `.factory/state` to `.factory/store`. Rejected: keeping `.factory/state`, where checking out an older commit overwrote an uncommitted record and checking `main` out again deleted it (Evidence).
2026-10-04 T-0025 The branch is named `factory-store`, and the design doc and build spec drop the name `tickets` for it. Rejected: `tickets`, a generic name in a target repo whose branches serve other work, such as the Nanobot repo, which shares its objects with another checkout.
2026-10-04 T-0025 `init` creates a new store as a worktree on an unborn `factory-store` branch, and the operator makes the first commit. On a clone where the branch already exists, `init` checks it out, which restores the store. Rejected: `init` committing, which needs a git identity, and the suite runs under a throwaway HOME that has none.
2026-10-04 T-0025 When no local `factory-store` exists and more than one remote carries it, `init` refuses and names each `<remote>/factory-store`. The operator picks one with `git branch factory-store <remote>/factory-store` and runs `init` again. Rejected: creating a new empty branch, which would silently start a second store history beside the pushed one. Also rejected: preferring `origin`, a guess about which remote is canonical.
2026-10-04 T-0025 With `FACTORY_INSTANCE` unset, `init` refuses, writing nothing, when the caller's git top level is a checkout of `factory-store`. It also refuses when the instance found by walking up from the caller's directory has a store that is that top level, or that contains it in the same repository (the same git common directory). These are the cases where it would build a phantom instance inside the live store. The second condition does not depend on which branch or commit the store has checked out, so a detached store HEAD does not open the route again (operator, round 2 change request N2). The same-repository qualifier keeps `init` working in a separate throwaway repository under a run's scratch directory (Evidence). Rejected: "contains" without that qualifier, which would refuse every suite `init` run with pytest's temporary directory inside a store. Rejected: taking the repository from the parent of `--git-common-dir`. That is the main worktree, which for the Nanobot instance is `~/dev/nanobot`, another checkout on another branch, and for the runtime checkout is `~/dev/spec-factory` (Evidence).
2026-10-04 T-0025 In `init`, every refusal and the store-worktree step come before any instance file is written, so a failed worktree step (for example, git's "already used by worktree" when `init` runs in a code checkout of a repo whose store branch is checked out elsewhere) leaves nothing behind.
2026-10-04 T-0025 The integration checkout ignores the store through the repo's git exclude file, which `init` and `store migrate` write. Rejected: a line in the target's tracked `.gitignore`. That would change the target's code to record a fact about one clone.
2026-10-04 T-0025 A new command, `factory store migrate --to PATH`, moves an existing store. It refuses unless the store is idle and committed, and it leaves the integration-branch side uncommitted for the operator to review. Rejected: a hand procedure, untested, run once on each repo by a different session.
2026-10-04 T-0025 `store migrate` deletes the old store directory only after it has checked that every ignored file (run scratch directories, tripwire baselines) was copied byte for byte. If the check fails, it undoes its own worktree and branch and leaves the old store as it was. Rejected: relying on `git status` in the new checkout, which cannot see ignored files.
2026-10-04 T-0025 The store branch starts with one commit whose tree is the store as last committed on the integration branch, and whose message names that commit. Earlier history stays readable with `git log <that commit> -- .factory/state`. Rejected: rewriting history with a subtree split. It would follow only part of the store's past, which began at `intake/state`, and it adds nothing that `main`'s history does not already keep.
2026-10-04 T-0025 An instance whose store is still a plain directory keeps working unchanged. `init` leaves such a store alone and points to `store migrate`. The harness reads and writes the store only through `state_dir`, so it runs with either layout.
2026-10-04 T-0022 A sub-ticket's "Tests to change" may list a test file that an earlier sibling of the same parent added, one line each: `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The harness reads only lines of that form inside the "Tests to change" field, and checks the file, not the test function. Rejected: checking test functions. The implementer rule puts new tests in new files, so a file is what a sibling adds, and git records files.
2026-10-04 T-0022 A listed file counts as added by a sibling when it is absent at the parent's `parent_base`, and the first commit since then on the integration branch that added it lies inside one merged sibling's recorded merge (reachable from its `main_after`, not from its `base_before`). Any merged sibling of the parent counts, including those from an earlier plan. The sibling ID on the line is for the reader and is not matched. Rejected: matching the named ID, because the planner's IDs (`ST-1`) differ from the store's (`T-0001.1`) and the operator's rule names no particular sibling.
2026-10-04 T-0022 The check runs in `run start` for every implementer run of a sub-ticket: first dispatch, fix rounds and catch-up runs. Every dispatch passes through that one place. Rejected: checking when the plan is added, when no sibling has merged yet. Rejected: checking at the merge gate, after the implementer has already edited the test. Rejected: checking where a waiting sub-ticket is released, which happens in two places and never for a sub-ticket with no dependencies.
2026-10-04 T-0022 A failed check refuses the run start with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness:` and names the file. The build workflow parks the sub-ticket with that error as the reason, so `resolve --ruling` handles it like an implementer's BLOCKED. That is what the operator's "parks for the operator, as today" describes. Rejected: a new kind of park with its own resolve verb. Rejected: having `run start` park the ticket itself, which would break the rule that a refusal writes nothing.
2026-10-04 T-0022 The preamble's guardrail sentence and the code reviewer's test-integrity check also accept a sibling entry that the harness has checked. Without them, the implementer and reviewer would still treat the edit as forbidden, and the park would remain.
2026-10-04 T-0022 The earlier sibling names the tests a later sibling will break under a new planner field, "Interim tests". The harness does not read it.
2026-10-04 T-0022 The critic's check for an omitted test goes under rubric 1 (Grounded), where the requester asked for it.
2026-10-04 T-0022 The requester's acceptance, a re-plan and re-spec of Nanobot T-0002 that the operator compares side by side, is an Operator step, not an acceptance scenario. Running it needs the Nanobot store and real agents, which a verifier must not touch.
2026-10-04 T-0032 Empty role output (#41, T-0032): labelled EMPTY-OUTPUT with the last message, re-dispatched once automatically, parked on a second; the code reviewer judges the diff and leaves the test suite and gates to the verifier.
2026-10-04 T-0029 Only the code reviewer lists declared protected paths, once for each head it reviews. The implementer and verifier may name them in their output, but not under ESCALATIONS. This is a standing decision: a later prompt change should not give another role a declared-path notice. The operator pre-approved it on 2026-10-04 (`.factory/answers/operator-decisions-2026-10-04.md`), under the standing decision that removing clearly redundant work is allowed when every refusal still fires.
2026-10-04 T-0029 A fix round makes a new head, so it gets its own reviewer notice, as today. Rejected: one notice per sub-ticket. A fix round can change a declared path again, and the operator would not hear about it.
2026-10-04 T-0029 The new rule also keeps one escalation for a declared path: when the change does something to it that the spec does not describe. An undeclared path still escalates as well. Rejected: the retro's wording "the reviewer lists declared paths for the merge gate". No local merge check reads the declaration, so that sentence would teach the roles something false.
2026-10-04 T-0029 The implementer and verifier get the same bullet word for word, as the last bullet under RULES. That way one text is checked in both prompts.
2026-10-04 T-0029 The changelog records the count re-derived from the store log (10 runs, 30 of 205 items). Rejected: the retro's 26 of 139, which its own table contradicts with 38.
2026-10-04 T-0029 Acceptance checks the composed run prompts and the document copies. The request's own check (on the next build, one notice per head, from the reviewer) is kept as an operator step. Rejected: an acceptance item that waits for a real build. The verifier cannot run one, and how a model follows a prompt rule is not something a check on one commit can prove.
