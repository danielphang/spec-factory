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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0466-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0466-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v1)

=== proposal.md
## Problem

The harness is the Python code under `factory/` that runs the factory: it records tickets, starts role runs and parks tickets for a human. In that code, eight small operations are written out by hand in two to eighteen places each. Each copy is a place a later fix can miss: a fix to one copy leaves the others with the old behaviour, and nobody notices until a run takes the unfixed path. The cost falls on whoever next changes one of these operations, usually an implementer agent working from a spec, and on the operator who reviews that change.

The eight operations are:
- listing the runs of one ticket, a run being one agent's attempt at one role;
- reading the store's event log, an append-only record of everything the harness did;
- recording a status change on a ticket;
- listing the runs still in flight on a ticket and its sub-tickets;
- reading the newest commit of the integration branch, the branch that finished work merges into;
- four smaller repeats in the command-line module;
- the text the dispatcher writes when a store command fails and it parks the ticket, a park being a stop that waits for a human, with a reason;
- two kinds of walk over spec Markdown, one that collects a section and one that collects a block under a heading.

This change gives each operation one definition and points every copy at it. Nothing a user or operator sees changes. Every refusal message, park reason, logged event and parse result stays as it is, and the existing tests pass without edits.

## Evidence

I measured everything on `~/dev/spec-factory` at `2b9baf5`, the head of `main`. Every command ran through the run's fresh-HOME wrapper. The request took its line numbers at `927bc53`. De-bloat A (T-0044.1) has merged since, so some lines have moved by a few places. Every pattern is still there.

**Copies today.** These are the counts that the NEW scenarios under Acceptance print on `2b9baf5`:

| Operation | Where the copies are | Count today |
|---|---|---|
| 1. Runs of a ticket | `compose.py:16` `_runs_for`, `compose.py:413` (re-reads each meta), `specstore.py:269` `critic_rounds`, `cli.py:1712` `_parent_close_verified`, `store.py:116` `clear_scratch` | 3 runs-directory listings outside `store.py` |
| 2. Event log | `cli.py:671` `_recorded_plan_run`, `cli.py:1760` `log_tail`, `stats.py:72`, `cost.py:129` | 3 `"*.jsonl"` log globs in `cli.py` and `stats.py` |
| 3. Status transition | `cli.py:174-177`, `817-821`, `999-1003`, `1063-1067`; `approve_spec` at `cli.py:1115-1122` stays as it is | 5 `"ticket.transition"` events in `cli.py` |
| 4. In-flight runs | `cli.py:603`, `drive.py:626` | 2 |
| 5. Integration-branch tip | `cli.py:254`, `328`, `545`, `1693` | 4 |
| 6. Smaller `cli.py` repeats | record copies at `1132-1133`, `1198-1199`, `1206-1207`, `1219-1220`, `1248-1249`; set-aside rows plus `results.superseded` at `1196-1197`, `1234-1235`; PLANNED planner-run check at `692-695`, `1651-1654`; validate-and-applies at `620-623`, `1102-1105` | `5 2 2 2` |
| 7. Dispatcher parks | 18 park reasons of the form `harness-bug: <what>: <stderr>` in `drive.py`; checker cleanup at `drive.py:225-226`, `233-234`, `574-575` | `18 3` |
| 8. Spec Markdown walks | section walks in `acceptance_labels` (`specstore.py:158`), `decisions_of` (`:305`), `intent_of` (`:350`); block walks in `requirement_blocks` (`:102`) and `scenario_blocks` (`:324`) | `3 8` |

The request said the `drive.py` park pattern appears 18 times. `grep -c 'harness-bug:' factory/drive.py` prints 24, because that count also matches the five "unknown STATUS" parks and the `wait` park at `drive.py:529`, which do not carry a command's error text. The 18 that do are the ones this change shares.

**Copies that differ today.** The copies are not all identical, and the design keeps each caller's behaviour:
- The block values differ. `requirement_blocks` ends each block with `rstrip() + "\n"` and stops at a `##` or `###` heading. `scenario_blocks` ends with `rstrip()` alone and also stops at `####`.
- Malformed log lines are handled differently. `cost._records` (`cost.py:33-39`) skips a line that is not JSON, and `stats._load` reads through it. `_recorded_plan_run` and `log_tail` call `json.loads` and raise. `log_tail` prints each line's raw text, not a re-encoded event.
- Fenced lines are treated differently. `acceptance_labels` skips every line inside a code fence. `decisions_of` and the Problem walk in `intent_of` keep fenced lines that fall inside their section.
- The run filters differ. `_parent_close_verified` does not require `finished`, and the others do. `clear_scratch` skips a run whose `meta.yaml` is empty. The other three call `.get` on what `read_yaml` returns, so an empty `meta.yaml` raises `AttributeError` there. `store.write_text` (`store.py:73-75`) is not atomic, so a reader can see an empty `meta.yaml` while a run is being started.

**Behaviour that must not change, measured on the base.** Each REGRESSION scenario under Acceptance was run on `2b9baf5` and printed the output its THEN states:
- The status-transition scenario prints seven `ticket.transition` events and seven history entries. Four of each come from `ticket transition`, and one each from `ready-implementers` and `parent-check`. The seventh comes from `approve-spec`, which this change leaves alone.
- The refusal scenario prints the "spec not pinned" refusal, the "no recorded planner run" refusal, and the PLANNED refusal from both `subticket add` and `spec tasks`.
- The dispatcher scenario parks three tickets: `harness-bug: run start implementer: …`, `harness-bug: no head for the checkers: …` and `harness-bug: plan whole-spec: …`. Each reason ends in the store command's newline.
- The spec-parser comparison printed `files=264 checks=3918 differ=0`. To show that it can fail, I ran it against a copy of `specstore.py` whose `scenario_blocks` appends one space to each block. It printed `files=264 checks=3918 differ=74`, starting with `scenario_blocks specs/T-0012/v1.md`.
- `uvx ruff check --select F401,F841 factory tests` printed `All checks passed!`.
- The suite scenario printed `577 passed in 296.17s (0:04:56)` and no file names.

**What the tests reach.** No test under `tests/factory/` names any function this change replaces or deletes (`grep -rnE "_runs_for|_recorded_plan_run|critic_rounds|_parent_close_verified|clear_scratch|_set_aside_failed_rows|_integration_head|lines_outside_fences|requirement_blocks|scenario_blocks|_records\b" tests/factory` matches only three test function names). `tests/factory/test_cost_once.py:19` loads `factory/cost.py` by its file path, as module `factory_cost`, and `cost.py` imports nothing from the `factory` package today. The request lets it keep its own log reader for that reason. I did not test whether an import from `factory` would load there. `docs/`, `dev/` and `README.md` name none of these functions.

Current truth: `openspec/specs/harness-code/spec.md` (given in full in my input); the related capabilities are those triage named. No other capability was opened.

## Root cause

Each copy was written when its caller was written, and a later copy did not reuse the earlier one. For example, `cli._parent_close_verified` re-implements `compose._runs_for` with a different filter. The definitions this change adds and the callers each one replaces are listed in design.md.

## Out of scope

- Splitting `cli.py` into modules (T-0047, De-bloat D), which follows this ticket.
- The STATUS-trailer search shared by `status.py` and `subtickets.py` (issue #68).
- The Workflow scripts `factory/workflows/intake.js` and `factory/workflows/build.js` (issue #89). Their park reasons stay byte-identical because `drive.py`'s reasons stay byte-identical.
- `approve_spec`'s transition record (`cli.py:1115-1122`). `test_shepherd.py:79` checks that `approval.recorded` comes before `change.pinned`, and the transition event comes after both.
- The run listing in `stats._load` (`stats.py:66`). It reads every run of a store given by path, in flight or not, and adds fields of its own, so it is not a copy of operation 1.
- The other history appends (`cli.py:988` merge, `:1137` request-changes, `:1166` resolve, `store.py:139` park). They log a different event or none.
- Any change to a refusal message, park reason, event field, verdict, command or document.
- Edits to existing test files. New test files are allowed but not required.

## Open questions

none

## Decisions

- The shared run iterator skips a run whose `meta.yaml` is empty, as `clear_scratch` does today. Three callers would otherwise crash with `AttributeError` while a parallel run start is writing that file. This is the one difference from today's behaviour, and it can happen only during that write. Rejected: an iterator that hands back an empty meta for each caller to handle, which would leave the ticket, role and finished filters copied at every caller.
- The event log gets two readers. `store.log_lines` yields raw lines and leaves malformed-line handling to the caller, so `log_tail` still prints raw text and the CLI readers still raise. A new `cost._log_records` keeps cost's skip-malformed behaviour and is shared with `stats.py`. `cost.py` stays free of `factory` imports, as the request allows, because `test_cost_once.py` loads it by file path. Rejected: one strict reader for all four callers, which would change what `factory stats` does with a malformed line.
- The dispatcher's shared piece is a function that formats the reason, not one that parks. Three of the 18 sites pick their reason inside a conditional expression (`drive.py:192`, `453`, `517`), and a helper cannot `return` from its caller.
- The helpers' names and modules follow the request where it gave them (`store.record_transition`, `store.in_flight_runs`, a gitops helper, `section(text, heading)`). Where it did not, design.md names them.

## Risk

The change refactors eight harness modules: `cli.py`, `compose.py`, `cost.py`, `drive.py`, `gitops.py`, `specstore.py`, `stats.py` and `store.py`. Every ticket, run and archive passes through this code, so a slip changes live behaviour on both instances once the runtime is upgraded.

The highest-risk part is H. `apply_delta` writes current truth by replacing the exact text of a requirement block, so a one-character change in a block's text corrupts an archive. The spec-parser comparison under Acceptance checks part H's functions against the base over every spec in this repo's store, and the suite's `test_spec_store`, `test_spec_amend` and `test_decision_log` cover the archive path.

The next highest is G. `resolve --ruling` matches the park prefix `harness-bug: run start implementer:` (`cli.py:1187`), so that reason's text must not change.

Estimated size: about 250 to 350 changed lines, with a net fall of about 90.

Protected paths: `factory/**`

=== design.md
## Proposed change

Every part keeps each caller's refusal text, park reason, event fields, field order and result exactly. The parts are listed in the order to build them. H goes last, as the request asks, because it touches the archive path. Every function this change makes unused is deleted: `compose._runs_for`, and `stats.py`'s import of `_records`. The harness-code requirement that the harness keeps no unused definition applies.

**A. One run iterator (`factory/store.py`).**
Add `ticket_runs(root: Path, ticket: str, role: str | None = None, finished: bool = False)`.
- It yields `(run_id, meta)` for each `runs/<run_id>/meta.yaml`, in run-id (directory name) order.
- It skips a directory with no `meta.yaml`, or with an empty one (see Decisions).
- It yields only runs whose meta has `ticket == ticket`. When `role` is given, it also requires `role == role`. When `finished` is true, it also requires a truthy `finished`.
- A missing `runs/` yields nothing.

Its callers:
- `compose.py`: delete `_runs_for`. Its two uses become `[r for r, _ in store.ticket_runs(root, tid, role, finished=True) if r != run_id]`. The round filter at `compose.py:413` reads `round` from the yielded meta and does not re-read the file.
- `specstore.critic_rounds`: `ticket_runs(root, tid, "critic", finished=True)`. It reads `output.md` from `root / "runs" / run_id`.
- `cli._parent_close_verified`: `ticket_runs(root, t["id"], "verifier")`, with no finished filter, keeping its own `status == "VERIFIED"` and `head` checks. It returns the run id.
- `store.clear_scratch`: `ticket_runs(root, tid, finished=True)`. For each run, `runs/<id>/scratch` is unlinked when it is a symlink, removed with `shutil.rmtree` when it is a directory, and otherwise left alone. The comment about read-only directories stays.

`next_run_id` (`store.py:163`) lists run names, not a ticket's runs, and stays as it is.

**B. Event-log readers (`factory/store.py`, `factory/cost.py`, `factory/stats.py`).**
- Add `store.log_lines(root: Path)`. It yields each line (`str.splitlines()`) of each `log/*.jsonl` file, files in sorted name order. A missing `log/` yields nothing.
- `cli._recorded_plan_run` loops over `store.log_lines(root)` with `json.loads`. `cli.log_tail` builds its list from it. Both keep their own parsing, filtering and printing.
- Add `cost._log_records(store: str)`. It yields `_records(lf)` for each `log/*.jsonl` file of `store`, in sorted name order.
- `cost._store_paths` and `stats._load` loop over `_log_records`. `stats._load` keeps its `isinstance(e, dict) and e.get("ts")` filter and its sort.
- `stats.py` imports `_log_records` in place of `_records`.

**C. One transition record (`factory/store.py`).**
Add `record_transition(root, t, to, by, history=None, event=None) -> str`. It does the following, in order, and returns `frm`:
1. Set `frm = t["status"]` and `t["status"] = to`.
2. Append `{"ts": now(), "from": frm, "to": to, "by": by, **(history or {})}` to `t["history"]`.
3. `save_ticket(root, t)`.
4. `log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": to, "by": by, **(event or {})})`.

Its callers:
- `cli.ticket_transition`. It sets `t["parked"] = None` when `a.to != "parked"` before the call. It passes `history={"round": dict(t["round"]), **({"verified_by": verified_by} if verified_by else {})}` and `event={"round": t["round"]}`.
- `ticket_ready_implementers` (`cli.py:817-821`), with by `"ready-implementers"`.
- the dependant release in `merge` (`cli.py:999-1003`), with by `"merge"`.
- `parent_check` (`cli.py:1063-1067`), with by `"parent-check"`.

`approve_spec` is not changed.

**D. In-flight runs (`factory/store.py`).**
Add `in_flight_runs(root, t) -> list[str]`, which returns `[r for x in (t, *subtickets_of(root, t["id"])) for r in x.get("in_flight") or []]`. `cli.spec_amend` (`cli.py:602-605`) and `drive._same_ticket_guard` (`drive.py:626`) use it. `spec_amend` keeps its own `subs` for its later lines. Both refusal texts are unchanged.

**E. Integration-branch tip (`factory/gitops.py`).**
Add `integration_tip(cfg, repo) -> str`, which returns `rev(repo, integration_branch(cfg, repo))`. The four `cli.py` sites (`254`, `328`, `545`, `1693`) call it.

**F. Smaller `cli.py` repeats (`factory/cli.py`).** Four helpers:
- `_copy_record(d: Path, kind: str, src) -> Path` sets `dest = d / f"{kind}-{_next_n(d, kind)}.md"`, runs `shutil.copyfile(src, dest)` and returns `dest`. It is used for the changes notes (`request_changes`) and the four ruling copies in `resolve`.
- `_supersede(root, t) -> tuple` reads `head = t.get("head")` and `moved = _set_aside_failed_rows(root, t)`, logs `results.superseded` with `ticket`, `head` and `roles=moved`, and returns `(head, moved)`. It is used by the reviewer-ESCALATE ruling and by `--redispatch`, at the same point in each branch as today.
- `_planner_run(root, run: str, tid: str) -> Path` returns `_run_dir(root, run)`. When that run's meta is not a PLANNED planner run of `tid`, it raises `Refused(f"{run} is not a PLANNED planner run of {tid}")`. `subticket_add` and `spec_tasks` use it, each at the point where it checks today.
- `_refuse_unless_applies(root, text, refusal: str)` runs `specstore.validate` and then, when that is clean, `specstore.applies`. On any error it raises `Refused(f"{refusal}: " + "; ".join(errors))`. `approve_spec` passes `"spec not pinned"` and `spec_amend` passes `"spec not amended"`, each inside its existing `is_active` block.

**G. Dispatcher parks (`factory/drive.py`).** Two module-level helpers:
- `_failed(what: str, res: dict) -> str` returns `f"harness-bug: {what}: {res.get('stderr') or ''}"`, written on one line. All 18 reasons of that form use it, including the three inside conditional expressions (`192`, `453`, `517`) and the loop at `353`, which passes its `what`. Each `what` is the text between `harness-bug: ` and `: {` today, so `run start {role}`, `run compose {role}`, `run finish {role}`, `results record {role}`, `spec add`, `transition to critic`, `round increment refused`, `plan whole-spec`, `ready-implementers`, `ticket head`, `join`, `transition to checks`, `no head for the checkers`, `results show` and `merge` keep their current text.
- `_cleanup_checker(role: str, rid: str)` calls `call("run", "cleanup", rid)` when `role in CHECKERS`. It is used at `drive.py:225-226`, `233-234` and `574-575`.

The five "unknown STATUS" parks and the `wait` park (`drive.py:529`) do not carry a command's error text and stay as they are.

**H. Spec Markdown walks (`factory/specstore.py`).** Two helpers:
- `section(text: str, heading: str)` walks `lines_outside_fences(text)`. A line outside a fence that starts with `"## "` ends the current section, and starts a new one when it starts with `heading`. The function yields `(line, in_fence)` for each line inside a section whose heading matched, and never yields the heading line itself. Its callers:
  - `acceptance_labels` uses `section(verification, "## Acceptance")` and still skips fenced lines.
  - `decisions_of` uses `section(proposal, "## Decisions")` and still processes fenced lines, as today.
  - `intent_of`'s Problem walk uses `section(parts.get("proposal.md", ""), "## Problem")`.
- `_blocks(text: str, head_re, level: int) -> dict[str, str]` walks `lines_outside_fences(text)`. A line outside a fence that starts with `"##"`, `"###"` (and, when `level` is 4, `"####"`) followed by a space ends the current block. That line starts a new block when `head_re` matches it. The function maps each name to `"\n".join(block_lines).rstrip()`, and a later block with the same name replaces an earlier one, as today. Its callers:
  - `requirement_blocks(text)` returns `{n: b + "\n" for n, b in _blocks(text, REQ_RE, 3).items()}`.
  - `scenario_blocks(text)` updates its result with `_blocks(body, SCEN_RE, 4)` for each delta part, in part order.

`_heading` stays, because `cli.py:358` uses it. `parse_delta`, `scenario_names`, `apply_delta` and the requirement-statement loop in `intent_of` keep their own code.

**PR description.** It reports `git diff --stat main...HEAD -- factory` (the line change per file), as the request asks.

## Tests to change

none

=== specs/harness-code/spec.md
## ADDED Requirements

### Requirement: Each operation the harness repeated has one definition
The harness SHALL define once each of the following: listing a ticket's runs, reading the event log (one reader for the CLI, one inside the standalone cost script), recording a status transition outside spec approval, listing the runs in flight on a ticket and its sub-tickets, reading the integration-branch tip, copying a resolution record, setting aside failed result rows, checking for a PLANNED planner run, refusing a spec that does not validate and apply, formatting a dispatcher park for a failed store command, cleaning up a checker run, and walking a spec's sections and heading blocks. Every caller MUST use that definition.

#### Scenario: Only the store module lists a ticket's runs
- WHEN `cat factory/cli.py factory/compose.py factory/specstore.py | grep -cE 'runs\.(iterdir|glob)\(|"runs"\)\.(iterdir|glob)\('`
- THEN it prints `0`

#### Scenario: The CLI and the stats report read the event log through a shared reader
- WHEN `echo "$(cat factory/cli.py factory/stats.py | grep -c '"\*\.jsonl"') $(grep -c '"\*\.jsonl"' factory/store.py)"`
- THEN it prints `0 1`

#### Scenario: One function records a status transition outside spec approval
- WHEN `echo "$(grep -c '"ticket\.transition"' factory/cli.py) $(grep -c '"ticket\.transition"' factory/store.py)"`
- THEN it prints `1 1`

#### Scenario: Neither spec amend nor the dispatcher builds the in-flight list itself
- WHEN `cat factory/cli.py factory/drive.py | grep -cE 'for \w+ in \(t, \*'`
- THEN it prints `0`

#### Scenario: One function reads the integration-branch tip
- WHEN `cat factory/*.py | grep -cE 'rev\(repo, (gitops\.)?integration_branch\('`
- THEN it prints `1`

#### Scenario: Record copies, row set-asides, planner-run checks and spec apply checks each have one definition
- WHEN `echo "$(grep -c 'shutil\.copyfile(a\.' factory/cli.py) $(grep -c '"results\.superseded"' factory/cli.py) $(grep -c 'is not a PLANNED planner run' factory/cli.py) $(grep -c 'specstore\.applies(root, deltas)' factory/cli.py)"`
- THEN it prints `0 1 1 1`

#### Scenario: One line formats a failed-command park and one call cleans up a checker
- WHEN `echo "$(grep -cE "harness-bug: .*stderr" factory/drive.py) $(grep -c 'call("run", "cleanup"' factory/drive.py)"`
- THEN it prints `1 1`

#### Scenario: Spec sections and heading blocks are each walked by one function
- WHEN `echo "$(grep -cE 'startswith\("## (Acceptance|Decisions|Problem)' factory/specstore.py) $(grep -c 'in lines_outside_fences(' factory/specstore.py)"`
- THEN it prints `0 5`

### Requirement: Sharing an operation changes no refusal, park reason, event or parse result
After the operations above are shared, every command MUST print the same refusals, write the same events, history entries and park reasons, and parse every spec the same way as before, and the existing harness tests SHALL pass with no existing test file changed.

#### Scenario: Status transitions write the same events and history entries
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0046-store.sh <<'EOF'
# Sourced from the repo root: a throwaway store (the suite's fixture instance) whose T-0001 is
# awaiting the spec gate with a one-line spec, and a stand-in `claude` that fails if ever called.
# Leaves T set. Every command's output is discarded.
T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/s FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance
export FACTORY_REPO=$T/none FACTORY_INTEGRATION_BRANCH=main PYTHONDONTWRITEBYTECODE=1 LOGNAME=op; unset FACTORY_DISPATCH
mkdir $T/bin && printf '#!/bin/sh\necho "{}"; exit 1\n' > $T/bin/claude && chmod +x $T/bin/claude && export PATH=$T/bin:$PATH
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && printf '## Problem\nx\n' > $T/spec.md
bin/factory ticket new --file $T/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0046-reason.py <<'EOF'
# uv run --frozen python t0046-reason.py <store> <ticket>: the ticket's park reason, as a Python
# literal, with the store's scratch directory written as <T>.
import os, sys, yaml
t = yaml.safe_load(open(os.path.join(sys.argv[1], "tickets", sys.argv[2] + ".yaml")))
print(sys.argv[2], repr((t.get("parked") or {}).get("reason")).replace(os.path.dirname(sys.argv[1]), "<T>"))
EOF
cat > ${TMPDIR:-/tmp}/t0046-specstore.py <<'EOF'
# uv run --frozen python t0046-specstore.py, from the repo root: runs the spec parser of the merge
# base of HEAD and main and the checkout's own over every spec version, change part and
# current-truth file in this repo's store, and counts the calls whose result (or raised exception
# type) differs. Prints `files=<n> checks=<m> differ=<k>`, then up to five differing calls.
import glob, importlib.util, os, subprocess, sys, tempfile
sys.path.insert(0, os.getcwd())
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
def load(name, src):
    p = os.path.join(tempfile.mkdtemp(), name + ".py"); open(p, "w").write(src)
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old = load("t0046_old", git("show", git("merge-base", "HEAD", "main").strip() + ":factory/specstore.py"))
new = load("t0046_new", open("factory/specstore.py", encoding="utf-8").read())
S = os.path.join(os.path.dirname(git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()), ".factory", "store")
files = sorted(glob.glob(S + "/specs/*/v*.md") + glob.glob(S + "/openspec/**/*.md", recursive=True))
truths = sorted(glob.glob(S + "/openspec/specs/*/spec.md"))
def res(m, fn, a):
    try: return repr(getattr(m, fn)(*a))
    except Exception as e: return "raised " + type(e).__name__
checks, differ = 0, []
for path in files:
    t = open(path, encoding="utf-8").read(); parts = dict(old.split_parts(t)); ops = old.parse_delta(t)[0]
    calls = [("validate", (t,)), ("intent_of", (t,)), ("scenario_blocks", (t,)), ("requirement_blocks", (t,)),
             ("parse_delta", (t,)), ("decisions_of", (parts.get("proposal.md", t),)),
             ("acceptance_labels", (parts.get("verification.md", t),))]
    if any(ops.values()):
        calls += [("apply_delta", (open(c, encoding="utf-8").read(), os.path.basename(os.path.dirname(c)), ops)) for c in truths]
    for fn, a in calls:
        checks += 1
        if res(old, fn, a) != res(new, fn, a):
            differ.append(f"{fn} {os.path.relpath(path, S)}")
print(f"files={len(files)} checks={checks} differ={len(differ)}")
for d in differ[:5]: print(d)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && bin/factory approve-spec T-0001 >/dev/null && printf 'ST-1 / A\nDepends on: none\nParallel-safe: yes\n\nST-2 / B\nDepends on: ST-1\nParallel-safe: yes\n' > $T/plan.md && bin/factory subticket add T-0001 --file $T/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket ready-implementers T-0001 >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null && bin/factory ticket parent-check T-0001 >/dev/null && bin/factory log tail --event ticket.transition -n 50 | sed 's/^{"ts": "[^"]*", /{/' && uv run --frozen python -c "import glob, sys, yaml; [print(p.rsplit('/', 1)[1][:-5], {k: v for k, v in h.items() if k != 'ts'}) for p in sorted(glob.glob(sys.argv[1] + '/tickets/*.yaml')) for h in yaml.safe_load(open(p))['history']]" $FACTORY_STATE)`
- THEN it prints exactly these 14 lines:

```
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-triage", "to": "ready-for-spec-writer", "by": "t", "round": {"spec": 0, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-spec-writer", "to": "ready-for-critic", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-critic", "to": "awaiting-spec-gate", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "awaiting-spec-gate", "to": "ready-for-planner", "by": "op"}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-planner", "to": "planned", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001.2", "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"}
{"event": "ticket.transition", "ticket": "T-0001", "from": "planned", "to": "ready-for-parent-verify", "by": "parent-check"}
T-0001.2 {'from': 'waiting-dependencies', 'to': 'ready-for-implementer', 'by': 'ready-implementers'}
T-0001 {'from': 'ready-for-triage', 'to': 'ready-for-spec-writer', 'by': 't', 'round': {'spec': 0, 'pr': 0}}
T-0001 {'from': 'ready-for-spec-writer', 'to': 'ready-for-critic', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'ready-for-critic', 'to': 'awaiting-spec-gate', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'awaiting-spec-gate', 'to': 'ready-for-planner', 'by': 'op', 'approved_version': 1}
T-0001 {'from': 'ready-for-planner', 'to': 'planned', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'planned', 'to': 'ready-for-parent-verify', 'by': 'parent-check'}
```

#### Scenario: Spec pinning and planner-run refusals keep their text
Needs the GIVEN block of "Status transitions write the same events and history entries" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && mkdir $T/s/openspec && bin/factory approve-spec T-0001 2>/dev/null | tail -1; rmdir $T/s/openspec && bin/factory approve-spec T-0001 >/dev/null && bin/factory ticket new --file $T/req2.md >/dev/null && R=$(bin/factory run start --role triage --ticket T-0002 --model m | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p') && bin/factory subticket add T-0001 2>/dev/null | tail -1; bin/factory subticket add T-0001 --run $R 2>/dev/null | tail -1; bin/factory spec tasks T-0001 --run $R 2>/dev/null | tail -1)`
- THEN it prints exactly these 4 lines:

```
{"ok": false, "error": "spec not pinned: no `=== <path>` part lines"}
{"ok": false, "error": "no recorded planner run found for T-0001 (latest plan.added source: none); pass --run RUN or --file F"}
{"ok": false, "error": "run-0001-triage is not a PLANNED planner run of T-0001"}
{"ok": false, "error": "run-0001-triage is not a PLANNED planner run of T-0001"}
```

#### Scenario: The dispatcher parks a refused store command with the same reason
Needs the GIVEN block of "Status transitions write the same events and history entries" run once. `factory drive` runs for real on the throwaway store. T-0001.1's implementer run start is refused because the target repository does not exist. T-0001.2 sits at its checks with no branch. T-0002 is at its planner with no approved spec.
- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && bin/factory approve-spec T-0001 >/dev/null && printf 'ST-1 / A\nDepends on: none\nParallel-safe: yes\n\nST-2 / B\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && bin/factory subticket add T-0001 --file $T/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.2 status=checks-in-flight >/dev/null && bin/factory ticket new --file $T/req2.md >/dev/null && bin/factory ticket set T-0002 status=ready-for-planner >/dev/null && bin/factory drive T-0001 --phase build >/dev/null 2>&1; bin/factory drive T-0002 --phase build >/dev/null 2>&1; for x in T-0001.1 T-0001.2 T-0002; do uv run --frozen python ${TMPDIR:-/tmp}/t0046-reason.py $FACTORY_STATE $x; done)`
- THEN it prints exactly these 3 lines:

```
T-0001.1 "harness-bug: run start implementer: factory: FileNotFoundError: [Errno 2] No such file or directory: PosixPath('<T>/none')\n"
T-0001.2 'harness-bug: no head for the checkers: T-0001.2 has no branch yet\n'
T-0002 'harness-bug: plan whole-spec: T-0002 has no approved spec\n'
```

#### Scenario: The spec parser gives the same result as the base on every spec in the store
Needs the GIVEN block of "Status transitions write the same events and history entries" run once.
- WHEN `(uv run --frozen python ${TMPDIR:-/tmp}/t0046-specstore.py)`
- THEN it prints one line, `files=<n> checks=<m> differ=0`, with n and m above 0, and nothing after it

#### Scenario: The refactored harness has no unused imports or variables
- WHEN `uvx ruff check --select F401,F841 factory tests`
- THEN it prints `All checks passed!` and exits 0

#### Scenario: The harness suite passes and no existing test file changes
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0046-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=DMR main...HEAD -- tests)`
- THEN it prints one line, which reports a number of passed tests and no `failed` or `error`, and nothing after it

=== verification.md
## Acceptance

- Only the store module lists a ticket's runs → NEW; on `2b9baf5` it prints `3` (`compose.py:20`, `specstore.py:276`, `cli.py:1722`).
- The CLI and the stats report read the event log through a shared reader → NEW; prints `3 0` today (`cli.py:674`, `cli.py:1761` and `stats.py:72` glob the log, and `store.py` has no reader).
- One function records a status transition outside spec approval → NEW; prints `5 0` today.
- Neither spec amend nor the dispatcher builds the in-flight list itself → NEW; prints `2` today (`cli.py:603`, `drive.py:626`).
- One function reads the integration-branch tip → NEW; prints `4` today.
- Record copies, row set-asides, planner-run checks and spec apply checks each have one definition → NEW; prints `5 2 2 2` today.
- One line formats a failed-command park and one call cleans up a checker → NEW; prints `18 3` today.
- Spec sections and heading blocks are each walked by one function → NEW; prints `3 8` today.
- Status transitions write the same events and history entries → REGRESSION
- Spec pinning and planner-run refusals keep their text → REGRESSION
- The dispatcher parks a refused store command with the same reason → REGRESSION
- The spec parser gives the same result as the base on every spec in the store → REGRESSION
- The refactored harness has no unused imports or variables → REGRESSION
- The harness suite passes and no existing test file changes → REGRESSION

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

### Requirement: An implementer starts only when each sibling-added test it may change came from a merged sibling
`factory run start --role implementer` on a sub-ticket MUST refuse with exit 2, writing no run, worktree, branch or in-flight entry, with an error that starts `BLOCKED from harness: ` and names the file, when a line `` `<file>` (added by <ID>) `` inside its "Tests to change" field names a file that existed at the parent's base, or whose first adding commit on the integration branch since that base lies inside no merged sibling's recorded merge. It SHALL accept a file a merged sibling's merge added, and SHALL ignore such a line outside that field.

#### Scenario: A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0022-sib.sh <<'EOF'
# Sourced from the repo root with E set to a test file path. Builds a scratch store whose parent
# T-0001 is planned as ST-1 and ST-2: ST-2 depends on ST-1 and lists `$E` under Tests to change as
# added by ST-1. Builds a scratch target whose main holds tests/test_old.py from before the plan,
# tests/test_interim.py from ST-1's recorded merge, and tests/test_operator.py from a later direct
# commit that is no sibling's merge. ST-2's Scope line mentions tests/test_old.py in the same form.
# T-0001.1 is merged; T-0001.2 is ready for its implementer.
T22=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T22/store FACTORY_REPO=$T22/t FACTORY_INTEGRATION_BRANCH=main
printf '# Fixture\n\nThe bot should do the thing.\n' > $T22/req.md && printf '## Problem\nx\n' > $T22/spec.md
bin/factory ticket new --file $T22/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T22/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T22/t && mkdir $T22/t/tests && echo 'def test_old(): pass' > $T22/t/tests/test_old.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm base && A=$(git -C $T22/t rev-parse HEAD)
git -C $T22/t checkout -qb sib && echo 'def test_interim(): pass' > $T22/t/tests/test_interim.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm interim && git -C $T22/t checkout -q main
git -C $T22/t -c user.email=f@x -c user.name=f merge -q --no-ff -m 'Merge ST-1' sib && B=$(git -C $T22/t rev-parse HEAD)
echo 'def test_operator(): pass' > $T22/t/tests/test_operator.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm operator
printf 'ST-1 / Interim\nDepends on: none\nParallel-safe: yes\nInterim tests: `tests/test_interim.py`, broken by ST-2\n\nST-2 / Final\nDepends on: ST-1\nParallel-safe: yes\nScope: B, which reads `tests/test_old.py` (added by the base commit)\nTests to change:\n- `%s` (added by ST-1): ST-2 replaces the interim behaviour\nProtected paths: none\n' "$E" > $T22/plan.md
bin/factory subticket add T-0001 --file $T22/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket set T-0001.1 status=merged "merge.base_before='$A'" "merge.main_after='$B'" >/dev/null
bin/factory ticket set T-0001 "parent_base='$A'" >/dev/null
bin/factory ticket set T-0001.2 status=ready-for-implementer >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0022-build.mjs <<'EOF'
// node t0022-build.mjs, from the checkout under test after sourcing t0022-sib.sh: runs
// factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE. Each clerk command runs
// for real (sh -c, from this checkout, environment unchanged); each role run returns an empty
// output, which the workflow records as a killed run. Prints each park, as `park <id>: <reason>`.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return ''
  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
}
const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p') runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `exit=0 ready-for-implementer runs=1`

#### Scenario: A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(for E in tests/test_old.py tests/test_operator.py tests/test_never.py; do (. ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >$T22/o 2>/dev/null; x=$?; J=$(tail -1 $T22/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: ') names=$(echo "$J" | grep -cF "$E") runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) branch=$(git -C $FACTORY_REPO branch --list 'factory/T-0001.2' | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"); done)`
- THEN it prints three lines, each exactly `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`

### Requirement: The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it
When an implementer's run start is refused with an error that starts `BLOCKED `, the build workflow SHALL park the sub-ticket with that error, verbatim, as the reason, so that `factory resolve <id> --ruling F` MUST accept the park and return the sub-ticket to `ready-for-implementer`.

#### Scenario: The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(E=tests/test_old.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(BLOCKED from harness:\).*/\1/'; printf 'Ruling: x\n' > $T22/r.md; bin/factory resolve T-0001.2 --ruling $T22/r.md >/dev/null 2>&1; echo "ruling=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')")`
- THEN it prints exactly `park T-0001.2: BLOCKED from harness:`, then `ruling=0 ready-for-implementer`

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

### Requirement: A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT
When a role run ends without an output file, or with a blank one, whatever the agent call returned, `run finish` MUST record it as `EMPTY-OUTPUT` and never as `KILLED`. The workflow MUST keep the agent's non-blank last message as that run's `last-message.md` and re-dispatch the same role once. A second `EMPTY-OUTPUT` in a row SHALL park the ticket as `EMPTY-OUTPUT from <role>`, with no result row for that run.

#### Scenario: A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0032-checks.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh: T-0001 is planned as one sub-ticket, T-0001.1,
# whose branch factory/T-0001.1 holds one commit; T-0001.1 is at checks-in-flight on that head $H,
# with no result rows, so the build runs both checkers on it.
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md
bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
git -C $T23/t checkout -qb factory/T-0001.1 && echo x > $T23/t/x.txt && git -C $T23/t add x.txt
git -C $T23/t -c user.email=f@x -c user.name=f commit -qm work && git -C $T23/t checkout -q main
H=$(git -C $T23/t rev-parse factory/T-0001.1)
bin/factory ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0032-build.mjs <<'EOF'
// node t0032-build.mjs '<plays JSON>', from the checkout under test after sourcing t0023-parent.sh
// and t0032-checks.sh: runs factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE.
// Each clerk command runs for real (sh -c, from this checkout, environment unchanged). Each role
// run plays the next entry of its role's list in <plays> (the last one repeats):
//   {"say": "<text>"}     returns <text> (or null) as its final message and writes no output file;
//   {"write": "<STATUS>"} writes an output with the run's head as its Commit: line (and, for the
//                         verifier, "Gate suite: PASS") and that STATUS, and returns the same text.
// Prints each park, as `park <id>: <reason>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const plays = JSON.parse(process.argv[2]), n = {}
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const list = plays[r[2]] || [{ say: '' }]
  n[r[2]] = (n[r[2]] || 0) + 1
  const p = list[Math.min(n[r[2]], list.length) - 1]
  if ('say' in p) return p.say
  const head = (readFileSync(`${r[1]}/meta.yaml`, 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = `Commit: ${head}\n` + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') + `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(M="Both suite runs are still in progress; I'll write the review once the monitor reports their final lines."; . ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs "{\"reviewer\": [{\"say\": \"$M\"}], \"verifier\": [{\"write\": \"VERIFIED\"}]}"; for r in reviewer verifier; do echo "$r: $(for d in $(ls -d $FACTORY_STATE/runs/*-$r); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')"; done; echo "kept=$(find $FACTORY_STATE/runs -path '*-reviewer/last-message.md' -exec grep -lxF "$M" {} + | grep -c .) $(bin/factory results show T-0001.1 | tail -1 | grep -o '"rows": {[^}]*}')")`
- THEN it prints exactly `park T-0001.1: EMPTY-OUTPUT from reviewer`, then `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` (two reviewer runs, both empty), then `verifier: VERIFIED `, then `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` (both last messages kept verbatim, apostrophe included; no reviewer row, so a `--redispatch` re-runs only the reviewer)

#### Scenario: One empty reviewer run followed by a real one routes on the real one
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once. The first reviewer call returns `null`; the verifier's SPEC-DEFECT gives the join a fixed stop.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"say": null}, {"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: EMPTY-OUTPUT APPROVE `

#### Scenario: An implementer that returns nothing twice parks as EMPTY-OUTPUT
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once. In that fixture every role run returns an empty string.
- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs; echo "implementer: $(for d in $(ls -d $FACTORY_STATE/runs/*-implementer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.2: EMPTY-OUTPUT from implementer`, then `implementer: EMPTY-OUTPUT EMPTY-OUTPUT `

#### Scenario: An intake role's second empty output in a row parks as EMPTY-OUTPUT
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once. The stub store answers every `run finish` with `EMPTY-OUTPUT`.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": {"out": {"ok": true, "run_id": "run-0009-x", "status": "EMPTY-OUTPUT", "escalations": []}}}')`
- THEN it prints exactly `start: triage`, then `start: triage`, then `park: EMPTY-OUTPUT from triage`

### Requirement: A role run that writes its output runs once and routes on its STATUS
A role run whose output file holds a STATUS MUST NOT be re-dispatched, and the build SHALL route on that STATUS as before.

#### Scenario: A reviewer that writes its output runs once
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: APPROVE `

### Requirement: The build counts only the current plan's sub-tickets
The build MUST NOT park a parent for a superseded sub-ticket the human closed, and SHALL dispatch the current plan's ready sub-tickets. A closed sub-ticket of the current plan MUST still park the parent with `sub-ticket closed by a human: <id>`.

#### Scenario: The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored", "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once. In `t0022-build.mjs` every role run returns an empty string, so the implementer of the dispatched sub-ticket ends EMPTY-OUTPUT twice.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; node ${TMPDIR:-/tmp}/t0022-build.mjs)`
- THEN it prints exactly `park T-0001.4: EMPTY-OUTPUT from implementer`

#### Scenario: A sub-ticket of the current plan that a human closed still parks the parent
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" and "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' > $T23/plan1.md && bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket transition T-0001.2 --to closed --by t >/dev/null; node ${TMPDIR:-/tmp}/t0022-build.mjs)`
- THEN it prints exactly `park T-0001: sub-ticket closed by a human: T-0001.2`

### Requirement: A parent's final check and close count only the current plan's sub-tickets
`factory ticket parent-check` SHALL move a planned parent to `ready-for-parent-verify` when every current sub-ticket has merged, and `ticket transition <parent> --to closed` MUST accept a VERIFIED final check whatever its superseded sub-tickets' states.

#### Scenario: With the new plan merged, the re-planned parent reaches its final check and closes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.4 status=merged >/dev/null; echo "check: $(bin/factory ticket parent-check T-0001 | tail -1 | grep -o '"state": "[^"]*"')"; R=$(bin/factory run start --role verifier --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); if [ -n "$R" ]; then H=$(sed -n "s/^head: '*\([0-9a-f]*\).*/\1/p" $FACTORY_STATE/runs/$R/meta.yaml); printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $FACTORY_STATE/runs/$R/output.md; bin/factory run finish $R >/dev/null 2>&1; fi; bin/factory ticket transition T-0001 --to closed --by t >/dev/null 2>&1; echo "close=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `check: "state": "ready-for-parent-verify"`, then `close=0 closed`

### Requirement: The build parks a merge the gate blocked, with the gate's reason
When `factory merge` is refused with an error that starts `BLOCKED `, `factory/workflows/build.js` MUST park the sub-ticket with that error, verbatim, as the reason, and SHALL NOT record it as a harness bug.

#### Scenario: The build parks a merge refused for protected paths with the gate's reason
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "ticket join": {"out": {"ok": true, "decision": "merge", "reason": "ci PASS + APPROVE + VERIFIED on the current head"}}, "merge": {"out": {"ok": false, "error": "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"}, "exit": 2}}')`
- THEN it prints exactly `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`

### Requirement: A sub-ticket whose spec drifted parks before its first implementer run
`factory run start --role implementer` on a sub-ticket with no implementer run and no ruling on file MUST refuse with exit 2, writing no run, with an error that starts `BLOCKED from harness: spec drift: `, when its Acceptance field names a sibling of the current plan that has not merged and is not among its dependencies, or when a test file changed on the integration branch since the parent's approved version was written, in a first-parent commit that changed a file that version's design names and that is not the recorded merge of a merged sub-ticket of the same parent, and no Tests to change list names it; the build SHALL park it with that error, and a ruling SHALL let the next run start.

#### Scenario: A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\nAcceptance:\n- REGRESSION: ST-1 scenarios still pass\n' && J=$(bin/factory run start --role implementer --ticket T-0001.2 2>/dev/null | tail -1); echo "unmerged: blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: spec drift: ') names=$(echo "$J" | grep -c 'T-0001.1') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"; bin/factory ticket set T-0001.1 status=merged >/dev/null; bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "merged: exit=$? runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `unmerged: blocked=1 names=1 runs=0 ready-for-implementer`, then `merged: exit=0 runs=1`

#### Scenario: A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start
Needs the GIVEN blocks of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" and of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" (current truth, build-dispatch) run once. In `t0022-build.mjs` every role run returns an empty string.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && land src/greet.py tests/test_greet.py && land src/other.py tests/test_other.py && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(spec drift:\).*/\1/'; R=$(bin/factory ticket show T-0001.1 --json | tail -1); echo "greet=$(echo "$R" | grep -c 'tests/test_greet.py') other=$(echo "$R" | grep -c 'tests/test_other.py') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"; printf 'Ruling: the new test may change.\n' > $T27/r.md; bin/factory resolve T-0001.1 --ruling $T27/r.md >/dev/null 2>&1; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "ruled: exit=$? runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `park T-0001.1: BLOCKED from harness: spec drift:`, then `greet=1 other=0 runs=0`, then `ruled: exit=0 runs=1`

#### Scenario: A merged sibling's merge is not drift, and a later commit or merge from elsewhere still is
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell. Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" (current truth, spec-amendment) run once. In each case, part ST-1's branch adds `tests/test_greet.py` and changes `src/greet.py`, which the spec's design names, and is merged with `--no-ff` and recorded as T-0001.1's merge; T-0001.2 depends on it. Case `none` adds nothing more. Case `other` then commits `src/greet.py` with `tests/test_other.py` directly on main. Case `greet` then commits `src/greet.py` with `tests/test_greet.py` directly on main. Case `merge` then merges, with `--no-ff`, a branch `ext` that is no sub-ticket's recorded merge and that commits `src/greet.py` with `tests/test_merge.py`.
- WHEN `(for c in none other greet merge; do (. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' && A=$(git -C $T27/t rev-parse HEAD) && git -C $T27/t checkout -qb st1 && land src/greet.py tests/test_greet.py && git -C $T27/t checkout -q main && git -C $T27/t -c user.email=f@x -c user.name=f merge -q --no-ff -m 'Merge ST-1' st1 && bin/factory ticket set T-0001.1 status=merged "merge.base_before='$A'" "merge.main_after='$(git -C $T27/t rev-parse HEAD)'" >/dev/null && bin/factory ticket set T-0001.2 status=ready-for-implementer >/dev/null && case $c in none) ;; merge) git -C $T27/t checkout -qb ext && land src/greet.py tests/test_merge.py && git -C $T27/t checkout -q main && git -C $T27/t -c user.email=f@x -c user.name=f merge -q --no-ff -m 'Merge ext' ext ;; *) land src/greet.py tests/test_$c.py ;; esac && J=$(bin/factory run start --role implementer --ticket T-0001.2 2>/dev/null | tail -1); echo "$c: drift=$(echo "$J" | grep -c '"error": "BLOCKED from harness: spec drift: ') greet=$(echo "$J" | grep -c 'tests/test_greet.py changed') named=$(echo "$J" | grep -c "tests/test_$c.py changed by $(git -C $T27/t rev-parse HEAD | cut -c1-9)") runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"); done)`
- THEN it prints exactly `none: drift=0 greet=0 named=0 runs=1`, then `other: drift=1 greet=0 named=1 runs=0`, then `greet: drift=1 greet=1 named=1 runs=0`, then `merge: drift=1 greet=0 named=1 runs=0`

### Requirement: Changes that leave a sub-ticket's spec intact do not park it
A sub-ticket's first implementer run SHALL start when the commits since its parent's approved version was written change no file that version's design names, when every test they change is listed under Tests to change, or when an amendment was written after them.

#### Scenario: Unrelated changes, a listed test and an amendment written after the change let the implementer start
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(for c in other listed amended; do (. ${TMPDIR:-/tmp}/t0027-amend.sh && T='\nTests to change: none\n'; [ $c = listed ] && T='\nTests to change:\n- \140tests/test_greet.py\140: pins the old greeting\n'; plan "ST-1 / First\nDepends on: none\nParallel-safe: yes$T" && if [ $c = other ]; then land src/other.py tests/test_other.py; else land src/greet.py tests/test_greet.py; fi && if [ $c = amended ]; then bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; fi; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "$c: exit=$? runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"); done)`
- THEN it prints exactly `other: exit=0 runs=1`, then `listed: exit=0 runs=1`, then `amended: exit=0 runs=1`

### Requirement: The driver takes a ticket through intake on the intake script's route
`factory drive TICKET --phase intake` MUST take a ticket from its stored intake state to the same end state, with the same ticket records, runs, result rows and log events, apart from ids and times, as `factory/workflows/intake.js` does when given the same role outputs, and it SHALL start no process other than one `claude` per role run.

#### Scenario: The driver takes the intake fixtures through the same routes as the intake script
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario also needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- GIVEN the six fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0040-claude <<'EOF'
#!/usr/bin/env node
// Stands in for `claude`. Run from a role run's directory (runs/run-NNNN-<role>). Appends one JSON line
// to $T40_LOG: its argv, its working directory, its pid and FACTORY_DISPATCH. Plays the next entry of
// its role's list in $T40_PLAYS (the last one repeats), counted in $T40_LOG.n-<role>. An entry may
// first sleep ("sleep": seconds), then:
//   {"write": "<STATUS>"}  writes output.md (a Commit: line with the run's head when meta.yaml has one;
//                          "Gate suite: PASS" for a verifier) and replies with the same text;
//   {"say": "<text>"}      writes nothing and replies with <text>;
//   {"fail": "<text>"}     writes nothing, replies with is_error and <text>, and exits 1.
// The reply is one JSON object on stdout, shaped like `claude -p --output-format json`. Each finished
// call appends "<start> <end>" (seconds) to $T40_LOG.times.
const fs = require('fs'), path = require('path')
const cwd = process.cwd(), log = process.env.T40_LOG, t0 = Date.now() / 1000
fs.appendFileSync(log, JSON.stringify({ argv: process.argv.slice(2), cwd, pid: process.pid, dispatch: process.env.FACTORY_DISPATCH || null }) + '\n')
const role = (path.basename(cwd).match(/^run-\d+-([a-z_]+)$/) || [])[1]
const list = (JSON.parse(process.env.T40_PLAYS || '{}')[role]) || [{ say: '' }]
const nf = `${log}.n-${role}`, n = (fs.existsSync(nf) ? +fs.readFileSync(nf, 'utf8') : 0) + 1
fs.writeFileSync(nf, String(n))
const p = list[Math.min(n, list.length) - 1]
if (p.sleep) Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, p.sleep * 1000)
let text = '', err = false
if ('write' in p) {
  const head = (fs.readFileSync('meta.yaml', 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  text = (head ? `Commit: ${head}\n` : '') + (role === 'verifier' ? 'Gate suite: PASS\n' : '') +
    `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  fs.writeFileSync('output.md', text)
} else if ('fail' in p) { text = p.fail; err = true } else { text = p.say }
fs.appendFileSync(`${log}.times`, `${t0} ${Date.now() / 1000}\n`)
process.stdout.write(JSON.stringify({ type: 'result', subtype: err ? 'error_during_execution' : 'success', is_error: err,
  result: text, session_id: `stub-${path.basename(cwd)}`, total_cost_usd: 0.25, num_turns: 1,
  usage: { input_tokens: 10, cache_creation_input_tokens: 20, cache_read_input_tokens: 30, output_tokens: 5 } }) + '\n')
process.exit(err ? 1 : 0)
EOF
chmod +x ${TMPDIR:-/tmp}/t0040-claude && mkdir -p ${TMPDIR:-/tmp}/t0040-bin && ln -sf ${TMPDIR:-/tmp}/t0040-claude ${TMPDIR:-/tmp}/t0040-bin/claude
cat > ${TMPDIR:-/tmp}/t0040-wf.mjs <<'EOF'
// node t0040-wf.mjs <workflow script> <ticket>, from the checkout under test: runs that Workflow-tool
// script on <ticket> of the store $FACTORY_STATE. Each clerk command runs for real (sh -c, from this
// checkout). Each role call runs t0040-claude from the run's directory and returns its reply's
// `result`; a reply with is_error is thrown, as a failed agent call is.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket] = process.argv.slice(2)
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const run = prompt.match(/(\S+\/runs\/run-\d+-[a-z_]+)\/input\.md/)[1]
  const cp = spawnSync(`${process.env.TMPDIR || '/tmp'}/t0040-claude`, ['-p', prompt], { cwd: run, encoding: 'utf8' })
  const reply = JSON.parse(cp.stdout)
  if (reply.is_error) throw new Error(reply.result)
  return reply.result
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: process.env.FACTORY_INTEGRATION_BRANCH, inlineRoles: true }, agent, () => {}, () => {},
  async (fs) => Promise.all(fs.map(f => f())))
EOF
cat > ${TMPDIR:-/tmp}/t0040-records.py <<'EOF'
# .venv/bin/python t0040-records.py <store>: prints the store's records in an order-free form, so two
# stores that took the same route print the same lines: each ticket's state, rounds and park reason;
# each run as role, ticket and status (no ids or times); each result row; log events counted by kind
# and ticket.
import collections, json, pathlib, sys, yaml
s = pathlib.Path(sys.argv[1]); y = lambda p: yaml.safe_load(p.read_text())
for p in sorted((s / "tickets").glob("*.yaml")):
    t = y(p); print("ticket", t["id"], t["status"], "spec=%s pr=%s" % (t["round"].get("spec"), t["round"].get("pr")),
                    "reason=" + str((t.get("parked") or {}).get("reason") or "").strip())
for line in sorted("run %s %s %s" % (m["role"], m["ticket"], m["status"]) for m in map(y, s.glob("runs/*/meta.yaml"))):
    print(line)
for line in sorted("result %s %s %s" % (r.get("ticket"), r.get("role"), r.get("status")) for r in map(y, s.glob("results/*/*.yaml"))):
    print(line)
ev = collections.Counter((e["event"], e.get("ticket")) for f in sorted(s.glob("log/*.jsonl")) for e in map(json.loads, f.read_text().splitlines()))
for (k, t), n in sorted(ev.items(), key=str):
    print("event", k, t, n)
EOF
cat > ${TMPDIR:-/tmp}/t0040-parity.sh <<'EOF'
# Sourced from the repo root with PHASE (intake or build) and P (plays, as for t0040-claude) set.
# Builds two identical fixtures: for intake, a throwaway store whose T-0001 is ready for triage; for
# build, t0023-parent.sh's store, whose T-0001 is ready for its planner. Runs the Workflow-tool script
# on one (under node) and `factory drive T-0001 --phase $PHASE` on the other, each role played by
# t0040-claude. Leaves in $D, per side (script, drive): <side>.records, <side>.log (t0040-claude's
# calls), <side>.out and <side>.err (stdout and stderr) and <side>.state (the store's path). Prints
# `<T-0001's state after drive> script=<calls>/<runs> drive=<calls>/<runs> same|differ`.
D=$(cd "$(mktemp -d)" && pwd -P)
for side in script drive; do (
  if [ $PHASE = intake ]; then T40=$(mktemp -d); export FACTORY_STATE=$T40/store
    printf '# Fixture\n\nThe bot should do the thing.\n' > $T40/req.md && bin/factory ticket new --file $T40/req.md >/dev/null
  else . ${TMPDIR:-/tmp}/t0023-parent.sh; T40=$T23; fi
  export T40_LOG=$D/$side.log T40_PLAYS="$P"; : > $T40_LOG; echo $FACTORY_STATE > $D/$side.state
  if [ $side = script ]; then node ${TMPDIR:-/tmp}/t0040-wf.mjs factory/workflows/$PHASE.js T-0001 > $D/$side.out 2> $D/$side.err
  else PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH bin/factory drive T-0001 --phase $PHASE > $D/$side.out 2> $D/$side.err; fi
  .venv/bin/python ${TMPDIR:-/tmp}/t0040-records.py $FACTORY_STATE > $D/$side.records
  echo "$(grep -c . $T40_LOG)/$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .)" > $D/$side.count ); done
echo "$(sed -n 's/^ticket T-0001 \([^ ]*\) .*/\1/p' $D/drive.records) script=$(cat $D/script.count) drive=$(cat $D/drive.count) $(cmp -s $D/script.records $D/drive.records && echo same || echo differ)"
EOF
cat > ${TMPDIR:-/tmp}/t0040-calls.py <<'EOF'
# .venv/bin/python t0040-calls.py <t0040-claude log>: one line per call, sorted: `<role> ok`, or
# `<role> bad: <what>`. A call is ok when it ran from its run's directory without FACTORY_DISPATCH,
# with argv `-p <prompt>` then options given once each: --model (the run's model), --output-format
# json, --permission-mode auto, --append-system-prompt-file <run>/system-prompt.txt, --tools and
# --allowedTools (one comma-separated argument each), and optionally --add-dir and --effort; no
# --bare and no --system-prompt-file. The prompt names only the run's input and output files. Every
# Edit allow rule covers only <run>/output.md, <run>/scratch/, the temporary directory, or for the
# implementer its worktree, which one rule covers; Edit is a tool only for the implementer.
import json, os, re, sys, tempfile, yaml
R = os.path.realpath; out = []
for c in map(json.loads, open(sys.argv[1]).read().splitlines()):
    run = R(c["cwd"]); m = yaml.safe_load(open(os.path.join(run, "meta.yaml"))); role = m["role"]; bad = []
    a = c["argv"]; opts = {}
    if a[:1] != ["-p"] or len(a) < 2: bad.append("no -p prompt")
    p = re.fullmatch(r"Your entire input is the file (\S+)/input\.md; read it first and follow it\. "
                     r"Write your complete output to (\S+)/output\.md and return the same text\.", a[1] if len(a) > 1 else "")
    if not p or R(p[1]) != run or R(p[2]) != run: bad.append("prompt")
    for k, v in zip(a[2::2], a[3::2]):
        if k in opts: bad.append("twice " + k)
        opts[k] = v
    if len(a[2:]) % 2: bad.append("odd options")
    want = {"--model": m["model"], "--output-format": "json", "--permission-mode": "auto"}
    bad += ["%s=%s" % (k, opts.get(k)) for k, v in want.items() if opts.get(k) != v]
    if R(opts.get("--append-system-prompt-file", "/")) != os.path.join(run, "system-prompt.txt"): bad.append("system prompt")
    bad += [k for k in opts if k not in ("--model", "--output-format", "--permission-mode", "--append-system-prompt-file",
                                         "--tools", "--allowedTools", "--add-dir", "--effort")]
    if c["dispatch"] is not None: bad.append("FACTORY_DISPATCH")
    tools = opts.get("--tools", "").split(","); allow = opts.get("--allowedTools", "").split(",")
    if ("Edit" in tools) != (role == "implementer"): bad.append("Edit tool")
    ok = [os.path.join(run, "output.md"), os.path.join(run, "scratch") + "/**", R(tempfile.gettempdir()) + "/**"]
    wt = R(m["worktree"]) + "/**" if m.get("worktree") else None
    edits = [R("/" + e[7:-1].rstrip("*").rstrip("/")) + ("/**" if e.endswith("/**)") else "") for e in allow if e.startswith("Edit(//")]
    if any(e.startswith("Edit") and not e.startswith("Edit(//") for e in allow): bad.append("Edit rule form")
    bad += ["edit " + e for e in edits if e not in ok and not (role == "implementer" and e == wt)]
    if role == "implementer" and wt not in edits: bad.append("no worktree edit")
    out.append("%s %s" % (role, "ok" if not bad else "bad: " + ", ".join(bad)))
print("\n".join(sorted(out)))
EOF
```

- WHEN `(for P in '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}' '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}]}' '{"triage": [{"say": "still waiting on my commands"}]}' '{"triage": [{"fail": "usage limit reached"}]}'; do (PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
- THEN it prints exactly `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same`, one per line

### Requirement: The driver takes an approved ticket through the build on the build script's route
`factory drive TICKET --phase build` MUST take an approved parent from its stored build state to the same end state, with the same ticket records, runs, result rows and log events, apart from ids and times, as `factory/workflows/build.js` does when given the same role outputs.

#### Scenario: The driver takes the build fixtures through the same routes as the build script
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(for P in '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "REQUEST-CHANGES"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"say": ""}], "verifier": [{"write": "SPEC-DEFECT"}]}' '{"implementer": [{"write": "BLOCKED"}]}'; do (PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
- THEN it prints exactly `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`, one per line

### Requirement: Each role run is one headless claude process with its role's prompt, model and tool limits
For every role run, the driver MUST start exactly one `claude` process from the run's directory, without `FACTORY_DISPATCH` in its environment, with argv `-p` and a prompt naming only the run's input and output files, then `--model` with the run's model, `--output-format json`, `--permission-mode auto`, `--append-system-prompt-file <run>/system-prompt.txt`, `--tools` and `--allowedTools`, and no `--bare`. Its `Edit` allow rules SHALL cover only the run's `output.md`, its `scratch/`, the temporary directory and, for the implementer alone, its worktree, and only the implementer SHALL have the `Edit` tool.

#### Scenario: Each role runs as one claude process with its prompt, model and tool limits
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python ${TMPDIR:-/tmp}/t0040-calls.py $D/drive.log; P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python ${TMPDIR:-/tmp}/t0040-calls.py $D/drive.log)`
- THEN it prints exactly `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`, one per line

### Requirement: A role process's reply is recorded with its run
After each role process ends, the run's directory MUST hold the process's stdout as `reply.json`, and the run's `meta.yaml` SHALL record its `session_id`, `total_cost_usd`, `num_turns` and `usage` under `claude:`.

#### Scenario: Each role run records its process's reply
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python -c 'import json,pathlib,sys,yaml; s=pathlib.Path(sys.argv[1]); ms=[yaml.safe_load(p.read_text()) for p in sorted(s.glob("runs/*/meta.yaml"))]; ok=lambda m,c: c.get("session_id")=="stub-"+m["run_id"] and c.get("total_cost_usd")==0.25 and c.get("num_turns")==1 and (c.get("usage") or {}).get("output_tokens")==5 and json.loads((s/"runs"/m["run_id"]/"reply.json").read_text())["session_id"]==c["session_id"]; print(" ".join("%s=%s" % (m["role"], "ok" if ok(m, m.get("claude") or {}) else "missing") for m in ms) or "none")' $(cat $D/drive.state))`
- THEN it prints exactly `triage=ok spec_writer=ok critic=ok`

### Requirement: The checkers run at once, and sub-tickets run concurrently up to a limit
The driver MUST run a head's reviewer and verifier as two concurrent processes, and SHALL build ready sub-tickets concurrently, at most `--parallel N` at a time, 2 when the option is not given.

#### Scenario: The checkers run at once, and sub-tickets up to the parallel limit
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once. Two sub-tickets with no dependency wait at `checks-in-flight`, each on its own commit; every checker sleeps 4 seconds, and the verifier's SPEC-DEFECT parks each one.
- WHEN `(for par in 1 default; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / One\nDepends on: none\nParallel-safe: yes\n\nST-2 / Two\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && for i in 1 2; do git -C $T23/t checkout -qb factory/T-0001.$i main && echo $i > $T23/t/f$i.txt && git -C $T23/t add f$i.txt && git -C $T23/t -c user.email=f@x -c user.name=f commit -qm w$i && git -C $T23/t checkout -q main && bin/factory ticket set T-0001.$i status=checks-in-flight branch=factory/T-0001.$i head=$(git -C $T23/t rev-parse factory/T-0001.$i) >/dev/null; done; export T40_LOG=$T23/claude.log T40_PLAYS='{"reviewer": [{"sleep": 4, "write": "APPROVE"}], "verifier": [{"sleep": 4, "write": "SPEC-DEFECT"}]}'; : > $T40_LOG; : > $T40_LOG.times; A=; [ $par = 1 ] && A='--parallel 1'; PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH bin/factory drive T-0001 --phase build $A >/dev/null 2>&1; echo "parallel=$par: calls=$(grep -c . $T40_LOG) max=$(.venv/bin/python -c 'import sys; t=[tuple(map(float, l.split())) for l in open(sys.argv[1])]; print(max([sum(a <= s < b for a, b in t) for s, _ in t] or [0]))' $T40_LOG.times) $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"); done)`
- THEN it prints exactly `parallel=1: calls=4 max=2 parked parked`, then `parallel=default: calls=4 max=4 parked parked`

### Requirement: The driver reports each step on one line and in a status file
Every line the driver prints on stdout before its last MUST have the form `<ticket id> "<title>": <step>`, naming the ticket the step concerns, a sub-ticket included. The last line SHALL be the result as one JSON object, and the store's `drive/<ticket>.yaml` SHALL hold the ticket, its title, the role processes still running and, once the driver ends, its result under `ended`; the store's `.gitignore` SHALL exclude `drive/`.

#### Scenario: Every intake step line names its ticket and title, and the status file shows the end
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; O=$D/drive.out; echo "steps=$([ $(sed '$d' $O | grep -c .) -ge 10 ] && echo yes || echo no) untagged=$(sed '$d' $O | grep -vcE '^T-0001 "Fixture": ') last=$(tail -1 $O | grep -c '"state": "awaiting-spec-gate"') status=$(.venv/bin/python -c 'import sys,yaml; d=yaml.safe_load(open(sys.argv[1])); print(d["ticket"], d["title"], d["ended"]["state"], len(d["running"]))' $(cat $D/drive.state)/drive/T-0001.yaml 2>/dev/null) ignored=$(cat $(cat $D/drive.state)/.gitignore 2>/dev/null | grep -cx 'drive/')")`
- THEN it prints exactly `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1`

#### Scenario: Build step lines name the sub-ticket they concern
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; O=$D/drive.out; echo "untagged=$(sed '$d' $O | grep -vcE '^T-0001(\.1)? "[^"]+": ') sub=$([ $(grep -cE '^T-0001\.1 "[^"]+": ' $O) -ge 6 ] && echo yes || echo no) last=$(tail -1 $O | grep -c '"state": "parked"')")`
- THEN it prints exactly `untagged=0 sub=yes last=1`

### Requirement: A stopped driver ends its role processes and resumes from the stored state
On SIGTERM or SIGINT the driver MUST end every role process it started, record each of its in-flight runs as `KILLED`, leave the ticket in its stored state unparked with nothing in flight, print a last line with `"stopped"` and exit with 128 plus the signal number; `factory drive TICKET` run again SHALL continue from the stored state, choosing the phase from that state when `--phase` is not given.

#### Scenario: A stopped driver ends its role process, records the run as killed and resumes from the stored state
Needs the GIVEN block of "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(T40=$(mktemp -d); export FACTORY_STATE=$T40/store T40_LOG=$T40/claude.log PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH; printf '# Fixture\n\nThe bot should do the thing.\n' > $T40/req.md && bin/factory ticket new --file $T40/req.md >/dev/null; T40_PLAYS='{"triage": [{"sleep": 60, "write": "ACCEPT"}]}' bin/factory drive T-0001 > $T40/out 2>/dev/null & p=$!; for i in $(seq 50); do [ -s $T40_LOG ] && break; sleep 0.2; done; sleep 1; r=$(grep -c '^- run: run-0001-triage' $FACTORY_STATE/drive/T-0001.yaml 2>/dev/null); kill -TERM $p 2>/dev/null; wait $p; x=$?; c=$(sed -n 's/.*"pid":\([0-9]*\).*/\1/p' $T40_LOG 2>/dev/null); echo "stop: exit=$x running=${r:-0} run=$(sed -n 's/^status: //p' $FACTORY_STATE/runs/run-0001-triage/meta.yaml 2>/dev/null) $(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml) $(grep '^in_flight' $FACTORY_STATE/tickets/T-0001.yaml) child=$(kill -0 ${c:-999999} 2>/dev/null && echo alive || echo gone) last=$(tail -1 $T40/out | grep -c '"stopped": "SIGTERM"')"; T40_PLAYS='{"triage": [{"write": "REJECT"}]}' bin/factory drive T-0001 >/dev/null 2>&1; echo "resumed: exit=$? $(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml) calls=$(grep -c . $T40_LOG 2>/dev/null)")`
- THEN it prints exactly `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, then `resumed: exit=0 closed calls=2`

### Requirement: The driver marks its own store calls, never its role processes, and passes a configured effort
`factory drive` MUST start unmarked while a run of another ticket is in flight on the target's own store. It MUST be refused from inside that store's `runs/` or `worktrees/`, marked or not, and refused while a run is in flight when given `--accept-harness`. Once started, its store calls SHALL carry the dispatcher marker, its role processes SHALL NOT, and a role with a level under `effort:` in `instance.yaml` SHALL get `--effort <level>`.

#### Scenario: An unmarked drive starts beside another ticket's run, is refused from a run's directory, and marks only its own store calls
Needs the GIVEN blocks of "Unmarked writes from inside the target are refused while a run is in flight, init included" (live-store-guard) and "The driver takes the intake fixtures through the same routes as the intake script" run once. T-0001's triage run stays in flight throughout; T-0002 is driven.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null && printf 'effort:\n  triage: low\n' >> $T/tgt/.factory/instance.yaml && export T40_LOG=$T/claude.log T40_PLAYS='{"triage": [{"write": "REJECT"}]}' PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH && : > $T40_LOG && cd $W && $B drive T-0002 --phase intake >/dev/null 2>&1; iu=$?; FACTORY_DISPATCH=1 $B drive T-0002 --phase intake >/dev/null 2>&1; im=$?; cd $T/tgt && $B --accept-harness $(cat $T/tgt/.factory/harness.lock) drive T-0002 --phase intake >/dev/null 2>&1; ac=$?; $B drive T-0002 --phase intake >/dev/null 2>&1; u=$?; echo "inside_unmarked=$iu inside_marked=$im accept=$ac unmarked=$u $($B ticket show T-0002 | sed -n 's/^status: //p') calls=$(grep -c . $T40_LOG) effort=$(grep -c '"--effort","low"' $T40_LOG) dispatch=$(grep -c '"dispatch":null' $T40_LOG)")`
- THEN it prints exactly `inside_unmarked=2 inside_marked=2 accept=2 unmarked=0 closed calls=1 effort=1 dispatch=1`

### Requirement: The Workflow scripts keep working beside the driver
`factory/workflows/intake.js` and `factory/workflows/build.js` SHALL still take a ticket through their routes unchanged until a later ticket retires them.

#### Scenario: The Workflow scripts still take both fixtures to the end of their routes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; grep '^ticket' $D/script.records | cut -d' ' -f2,3 | paste -sd' ' -; P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; grep '^ticket' $D/script.records | cut -d' ' -f2,3 | paste -sd' ' -)`
- THEN it prints exactly `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`

### Requirement: A drive refuses to start on a ticket that is already being worked
`factory drive T` MUST be refused with exit 2, writing nothing to the store and starting no role process, while T or any of its sub-tickets has a run in flight, or while the store's `drive/T.yaml` has no `ended` value and names in `pid` a live process, whether or not the caller has `FACTORY_DISPATCH=1` and on any store. The refusal SHALL name the runs in flight or the pid, and SHALL NOT name the marker. A status file whose `pid` is dead, or whose `ended` is set, SHALL NOT block a drive.

#### Scenario: A drive of a ticket with its own run in flight is refused, marked or not, and writes nothing
Needs the GIVEN blocks of "Unmarked writes from inside the target are refused while a run is in flight, init included" (live-store-guard) and "The driver takes the intake fixtures through the same routes as the intake script" run once. T-0001's triage run is in flight on the target's own store.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && S0=$(snap); cd $T/tgt && export T40_LOG=$T/claude.log T40_PLAYS='{"triage": [{"write": "ACCEPT"}]}' PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH && : > $T40_LOG; $B drive T-0001 >$T/o 2>$T/e; u=$?; FACTORY_DISPATCH=1 $B drive T-0001 >$T/o2 2>$T/e2; m=$?; echo "unmarked=$u marked=$m named=$(grep -l run-0001-triage $T/e $T/e2 | grep -c .) marker=$(cat $T/e $T/e2 $T/o $T/o2 | grep -c FACTORY_DISPATCH) json=$(tail -1 $T/o2 | grep -c '"ok": false') calls=$(grep -c . $T40_LOG) store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) $($B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `unmarked=2 marked=2 named=2 marker=0 json=1 calls=0 store=unchanged ready-for-triage`

#### Scenario: A drive of a parent whose sub-ticket has a run in flight is refused and writes nothing
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" and "The driver takes the intake fixtures through the same routes as the intake script" run once. T-0001.2's implementer run is in flight on a throwaway store; its parent T-0001 has none.
- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1 && export T40_LOG=$T22/claude.log PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH && : > $T40_LOG && S0=$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum); bin/factory drive T-0001 --phase build >/dev/null 2>$T22/e; x=$?; echo "exit=$x named=$(grep -c 'run-0001-implementer' $T22/e) calls=$(grep -c . $T40_LOG) store=$([ "$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 named=1 calls=0 store=unchanged`

#### Scenario: A recorded live driver blocks a second drive, and an ended or dead one does not
Needs the GIVEN block of "The driver takes the intake fixtures through the same routes as the intake script" run once. On a throwaway store, T-0001's status file names a live process with no `ended`, T-0002's names the same live process with `ended` set, and T-0003's names a process that has exited.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store T40_LOG=$T/claude.log T40_PLAYS='{"triage": [{"write": "REJECT"}]}' PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH; : > $T40_LOG; for i in 1 2 3; do printf '# Fixture %s\n\nThe bot should do thing %s.\n' $i $i > $T/req$i.md && bin/factory ticket new --file $T/req$i.md >/dev/null; done; sleep 60 >/dev/null 2>&1 & L=$!; sh -c 'exit 0' & G=$!; wait $G; mkdir -p $FACTORY_STATE/drive; printf 'ticket: T-0001\npid: %s\nended: null\n' $L > $FACTORY_STATE/drive/T-0001.yaml; printf 'ticket: T-0002\npid: %s\nended: {ok: true}\n' $L > $FACTORY_STATE/drive/T-0002.yaml; printf 'ticket: T-0003\npid: %s\nended: null\n' $G > $FACTORY_STATE/drive/T-0003.yaml; S0=$(cksum < $FACTORY_STATE/drive/T-0001.yaml); bin/factory drive T-0001 >/dev/null 2>$T/e; a=$?; bin/factory drive T-0002 >/dev/null 2>&1; b=$?; bin/factory drive T-0003 >/dev/null 2>&1; c=$?; kill $L; echo "live=$a pid=$(grep -cE "pid $L([^0-9]|$)" $T/e) file=$([ "$(cksum < $FACTORY_STATE/drive/T-0001.yaml)" = "$S0" ] && echo unchanged || echo changed) $(bin/factory ticket show T-0001 | sed -n 's/^status: //p') ended=$b $(bin/factory ticket show T-0002 | sed -n 's/^status: //p') dead=$c $(bin/factory ticket show T-0003 | sed -n 's/^status: //p') calls=$(grep -c . $T40_LOG)")`
- THEN it prints exactly `live=2 pid=1 file=unchanged ready-for-triage ended=0 closed dead=0 closed calls=2`

### Requirement: A role run does not start on a ticket that already has a run in flight
`factory run start` for triage, spec_writer, critic, planner or implementer SHALL refuse, with exit 2 and nothing written, when the ticket already has a run in flight. The error MUST read `<ticket id> already has run <first in-flight run id> in flight`.

#### Scenario: A second intake run on a ticket is refused with the same text
The second start carries `FACTORY_DISPATCH=1`, the marker that lets a command past the live-store fence, so the command reaches the run-start check rather than the fence.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && FACTORY_DISPATCH=1 $B run start --role triage --ticket T-0001 2>&1 >/dev/null; echo "exit=$?"; ls $T/tgt/.factory/state/runs)`
- THEN it prints `T-0001 already has run run-0001-triage in flight`, then `exit=2`, then `run-0001-triage` as the only run directory

## Current truth: factory-stats

# factory-stats

## Requirements

### Requirement: factory stats counts runs and verdicts per role and model
`factory stats` MUST print, for each role and model over every store given, the runs with a verdict other than `KILLED`, the `KILLED` runs, the runs whose verdict changed an outcome, the verdicts by status, the BLOCKING findings of reviewer and critic runs, and for implementer runs the gate commands that failed and then passed before hand-off. It SHALL count only runs that started inside the `--since`/`--until` window, SHALL leave out runs in flight, and SHALL write nothing.

#### Scenario: Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0043-fixture.sh <<'EOF'
# Sourced from the repo root: builds two fixture stores, $F/s1 and $F/s2, and a directory of
# transcripts, $F/tx, whose counts the t0043 scenarios state. Leaves F set.
F=$(cd "$(mktemp -d)" && pwd -P); mkdir -p $F/s1/log $F/s2/log $F/tx/a $F/tx/b $F/tx/c $F/tx/d
run() { f="'$7'"; [ $7 = null ] && f=null; mkdir -p $F/$1/runs/$2 && printf 'run_id: %s\nrole: %s\nticket: %s\nmodel: %s\nround: 0\nspec_version: %s\nstarted: %s\nfinished: %s\nwall_s: %s\nstatus: %s\n' $2 ${2#run-????-} $3 $4 $5 "'$6'" "$f" $8 $9 > $F/$1/runs/$2/meta.yaml; }
run s1 run-0001-triage T-0001 opus 0 2026-10-01T10:00:00+00:00 2026-10-01T10:05:00+00:00 100 NEEDS-HUMAN
run s1 run-0002-triage T-0001 opus 0 2026-10-01T11:00:00+00:00 2026-10-01T11:05:00+00:00 50 ACCEPT
run s1 run-0003-spec_writer T-0001 opus 0 2026-10-01T12:00:00+00:00 2026-10-01T12:30:00+00:00 300 READY-FOR-CRITIC
run s1 run-0004-critic T-0001 fable 1 2026-10-01T13:00:00+00:00 2026-10-01T13:10:00+00:00 60 REVISE
run s1 run-0005-spec_writer T-0001 opus 1 2026-10-01T14:00:00+00:00 2026-10-01T14:20:00+00:00 200 READY-FOR-CRITIC
run s1 run-0006-critic T-0001 fable 2 2026-10-01T15:00:00+00:00 2026-10-01T15:10:00+00:00 70 APPROVE
run s1 run-0007-implementer T-0001.1 opus 2 2026-10-02T10:00:00+00:00 2026-10-02T10:30:00+00:00 600 BLOCKED
run s1 run-0008-implementer T-0001.1 opus 3 2026-10-03T10:00:00+00:00 2026-10-03T10:30:00+00:00 400 READY-FOR-REVIEW
run s1 run-0009-reviewer T-0001.1 fable 3 2026-10-03T11:00:00+00:00 2026-10-03T11:05:00+00:00 90 REQUEST-CHANGES
run s1 run-0010-reviewer T-0001.1 fable 3 2026-10-03T12:00:00+00:00 2026-10-03T12:05:00+00:00 116 KILLED
run s1 run-0011-verifier T-0001.1 opus 3 2026-10-03T11:00:00+00:00 2026-10-03T11:10:00+00:00 120 SPEC-DEFECT
run s1 run-0012-verifier T-0001.1 fable 3 2026-10-03T13:00:00+00:00 2026-10-03T13:10:00+00:00 80 VERIFIED
run s1 run-0013-triage T-0002 opus 0 2026-10-04T10:00:00+00:00 null null running
run s1 run-0014-reviewer T-0001.1 fable 3 2026-10-09T10:00:00+00:00 2026-10-09T10:05:00+00:00 95 APPROVE
run s2 run-0001-triage T-0005 opus 0 2026-10-01T10:00:00+00:00 2026-10-01T10:05:00+00:00 40 ACCEPT
run s2 run-0002-critic T-0005 fable 1 2026-10-01T11:00:00+00:00 2026-10-01T11:05:00+00:00 30 APPROVE
printf 'claude:\n  session_id: s-0003\n  total_cost_usd: 1.5\n  num_turns: 10\n  usage: {input_tokens: 10, cache_read_input_tokens: 1000, cache_creation_input_tokens: 90, output_tokens: 50}\n' >> $F/s1/runs/run-0003-spec_writer/meta.yaml
printf '%s\n' '[BLOCKING] 6 proposal.md, Problem' '- [SHOULD-FIX] 1 design.md' 'STATUS: REVISE' > $F/s1/runs/run-0004-critic/output.md
printf '%s\n' '- [BLOCKING] 6 proposal.md, Problem: RESOLVED.' 'STATUS: APPROVE' > $F/s1/runs/run-0006-critic/output.md
printf '%s\n' '- [BLOCKING] reuse: a.py:1: copies b.py:2' 'No BLOCKING or SHOULD-FIX findings beyond that one.' 'STATUS: REQUEST-CHANGES' > $F/s1/runs/run-0009-reviewer/output.md
printf '%s\n' '## Where you work' 'Worktree: `/w`. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME=/tmp/h; git diff --check main...HEAD)`, `(export HOME=/tmp/h; pytest -q tests)`' > $F/s1/runs/run-0008-implementer/input.md
ev() { s=$1; shift; printf '{"ts": "%s", "event": "%s", "ticket": "%s"%s}\n' "$@" >> $F/$s/log/2026-10.jsonl; }
ev s1 2026-10-01T10:06:00+00:00 ticket.parked T-0001 ', "reason": "NEEDS-HUMAN from triage"'
ev s1 2026-10-01T12:31:00+00:00 spec.added T-0001 ', "version": 1, "source": "run-0003-spec_writer"'
ev s1 2026-10-01T14:21:00+00:00 spec.added T-0001 ', "version": 2, "source": "run-0005-spec_writer"'
ev s1 2026-10-01T16:00:00+00:00 approval.recorded T-0001 ', "kind": "spec", "version": 2'
ev s1 2026-10-02T10:31:00+00:00 ticket.parked T-0001.1 ', "reason": "BLOCKED from implementer"'
ev s1 2026-10-02T12:00:00+00:00 human.resolved T-0001.1 ', "kind": "ruling"'
ev s1 2026-10-02T13:00:00+00:00 spec.added T-0001 ', "version": 3, "source": "gate edit /x/answers/T-0001-gate-edit.md"'
ev s1 2026-10-02T14:00:00+00:00 ticket.parked T-0001.1 ', "reason": "harness-bug: run start implementer: BLOCKED from harness: spec drift: tests/test_a.py changed by 2ad4d8c52 since spec v3 was written at 37848dbb0"'
ev s1 2026-10-02T15:00:00+00:00 park.corrected T-0001.1 ', "previous": "harness-bug: run start implementer: BLOCKED from harness: spec drift: tests/test_a.py changed by 2ad4d8c52 since spec v3 was written at 37848dbb0", "reason": "BLOCKED from harness: spec drift: tests/test_a.py changed by 2ad4d8c52 since spec v3 was written at 37848dbb0"'
ev s1 2026-10-03T11:11:00+00:00 human.resolved T-0001.1 ', "kind": "request-changes"'
ev s1 2026-10-03T12:06:00+00:00 ticket.parked T-0001.1 ', "reason": "budget kill: reviewer"'
ev s1 2026-10-03T14:00:00+00:00 merge.refused T-0001.1 ', "reason": "head does not contain main"'
ev s1 2026-10-03T14:10:00+00:00 merge.refused T-0001.1 ', "reason": "head does not contain main"'
ev s1 2026-10-03T14:20:00+00:00 merge.refused T-0001.1 ', "reason": "protected paths not declared"'
ev s1 2026-10-03T15:00:00+00:00 ticket.parked T-0001 ', "reason": "archive: no spec store (factory init not run)\n{'"'"'ok'"'"': false}"'
ev s1 2026-10-03T15:10:00+00:00 ticket.parked T-0001 ', "reason": "archive: "'
ev s1 2026-10-03T15:20:00+00:00 ticket.parked T-0001.1 ', "reason": "sub-ticket closed by a human: T-0001.1"'
ev s1 2026-10-03T15:30:00+00:00 ticket.parked T-0002 ', "reason": "operator hold: T-0002 waits on run-0009-reviewer"'
ev s1 2026-10-03T15:40:00+00:00 human.resolved T-0002 ', "kind": "answer"'
ev s1 2026-10-09T11:00:00+00:00 ticket.parked T-0003 ', "reason": "NEEDS-HUMAN from triage"'
ev s1 2026-10-09T12:00:00+00:00 park.corrected T-0001.1 ', "previous": "budget kill: reviewer", "reason": "budget kill of reviewer after 900 s"'
ev s2 2026-10-01T10:06:00+00:00 ticket.parked T-0005 ', "reason": "NEEDS-HUMAN from triage"'
ev s2 2026-10-01T12:00:00+00:00 approval.recorded T-0005 ', "kind": "spec", "version": 1'
msg() { printf '{"type": "user", "timestamp": "%s", "message": {"role": "user", "content": "%s"}}\n' "$2" "$3" >> $1; }
use() { printf '{"type": "assistant", "timestamp": "%s", "message": {"id": "%s", "model": "claude-fable-5", "usage": {"input_tokens": %s, "cache_read_input_tokens": %s, "cache_creation_input_tokens": %s, "output_tokens": %s}}}\n' $2 $3 $4 $5 $6 $7 >> $1; }
A=$F/tx/a/agent-a1.jsonl; echo '{}' > $F/tx/a/agent-a1.meta.json
msg $A 2026-10-01T13:00:05Z "[Workflow harness — user request] see $F/s1/runs/run-0001-triage/output.md"
msg $A 2026-10-01T13:00:06Z "[Workflow harness — computed task] First read $F/s1/runs/run-0004-critic/system-prompt.txt"
use $A 2026-10-01T13:01:00Z m1 5 100 0 3; use $A 2026-10-01T13:01:00Z m1 5 100 0 3; use $A 2026-10-01T13:01:01Z m1 5 100 0 7
use $A 2026-10-01T13:02:00Z m2 1 200 4 10; use $A 2026-10-01T13:02:01Z m2 1 200 4 10
B=$F/tx/b/agent-b1.jsonl
msg $B 2026-10-03T10:00:05Z "[Workflow harness — computed task] Your input is $F/s1/runs/run-0008-implementer/input.md"
tool() { printf '{"type": "assistant", "timestamp": "2026-10-03T10:0%s:00Z", "message": {"id": "t%s", "content": [{"type": "tool_use", "id": "u%s", "name": "Bash", "input": {"command": "%s"}}]}}\n{"type": "user", "timestamp": "2026-10-03T10:0%s:30Z", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "u%s", "is_error": %s, "content": "%s"}]}}\n' $1 $1 $1 "$2" $1 $1 $3 "$4" >> $B; }
tool 1 '(export HOME=/tmp/h; pytest -q tests) 2>&1 | tail -3' true 'Exit code 1\n1 failed'
tool 2 '(export HOME=/tmp/h; pytest -q tests) 2>&1 | tail -3' false '3 passed'
tool 3 'git diff --check main...HEAD' false ''
use $B 2026-10-03T10:09:00Z m9 2 50 8 4
C=$F/tx/c/agent-c1.jsonl
msg $C 2026-10-01T10:00:05Z "[Workflow harness — computed task] First read $F/s2/runs/run-0001-triage/system-prompt.txt"
use $C 2026-10-01T10:01:00Z m5 1 9 0 2
D=$F/tx/d/s-0003.jsonl
msg $D 2026-10-01T12:00:05Z "Read $F/s1/runs/run-0003-spec_writer/input.md and write $F/s1/runs/run-0003-spec_writer/output.md"
use $D 2026-10-01T12:01:00Z m7 100 100000 0 500
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --transcripts $F/tx --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## A\./,/^## B\./p' $F/out | grep '^| [a-z]' | grep -v '^| role |')`
- THEN it prints exactly these eight lines, one per line: `exit=0`, `| triage | opus | 3 | 0 | 0 | ACCEPT 2, NEEDS-HUMAN 1 | - | - |`, `| spec_writer | opus | 2 | 0 | 0 | READY-FOR-CRITIC 2 | - | - |`, `| critic | fable | 3 | 0 | 1 | APPROVE 2, REVISE 1 | 1 | - |`, `| implementer | opus | 2 | 0 | 1 | BLOCKED 1, READY-FOR-REVIEW 1 | - | 1 in 1 read, 1 not recorded |`, `| reviewer | fable | 1 | 1 | 1 | REQUEST-CHANGES 1 | 1 | - |`, `| verifier | fable | 1 | 0 | 0 | VERIFIED 1 | - | - |`, `| verifier | opus | 1 | 0 | 1 | SPEC-DEFECT 1 | - | - |`

#### Scenario: A window bounds the count and the command writes nothing
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once. From 2026-10-03 on, with no end, store s1 holds two reviewer runs with verdicts (one REQUEST-CHANGES, one APPROVE on 2026-10-09) and one killed.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && S0=$(find $F -type f -exec cksum {} + | sort | cksum); bin/factory stats --store $F/s1 --since 2026-10-03 --transcripts $F/tx > ${TMPDIR:-/tmp}/t0043-since.txt 2>&1; x=$?; echo "exit=$x store=$([ "$(find $F -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed) since=$(sed -n '/^## A\./,/^## B\./p' ${TMPDIR:-/tmp}/t0043-since.txt | grep -c '^| reviewer | fable | 2 | 1 | 1 | APPROVE 1, REQUEST-CHANGES 1 | 1 | - |$')")`
- THEN it prints exactly `exit=0 store=unchanged since=1`

### Requirement: factory stats groups parks by normalised reason and counts gate and merge decisions
`factory stats` MUST group the parks in its window by reason, taking a park's reason from the latest correction of it dated before `--until` when there is one, after replacing run ids with `<run>`, ticket ids with `<ticket>` and commit hashes with `<sha>`, and keeping the reason's first line up to its first two `: `-separated fields, and SHALL print the total, the spec approvals, the requests for spec changes, each other kind of human resolution, each merge-refusal reason and the archive refusals.

#### Scenario: Parks are grouped by normalised reason, with gate and merge decisions
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once. Store s1's `harness-bug: ...` park was corrected on 2026-10-02 to `BLOCKED from harness: spec drift: ...`, and its `budget kill: reviewer` park was corrected on 2026-10-09, after the `--until` below.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## B\./,/^## C\./p' $F/out | grep '^| ' | grep -vE '^\| (park reason|gate or merge decision) \|')`
- THEN it prints exactly these seventeen lines, one per line: `exit=0`, `| NEEDS-HUMAN from triage | 2 |`, `| BLOCKED from harness: spec drift | 1 |`, `| BLOCKED from implementer | 1 |`, `| archive | 1 |`, `| archive: no spec store (factory init not run) | 1 |`, `| budget kill: reviewer | 1 |`, `| operator hold: <ticket> waits on <run> | 1 |`, `| sub-ticket closed by a human: <ticket> | 1 |`, `| all parks | 9 |`, `| spec approved | 2 |`, `| spec changes requested | 1 |`, `| resolved: answer | 1 |`, `| resolved: ruling | 1 |`, `| merge refused: head does not contain main | 2 |`, `| merge refused: protected paths not declared | 1 |`, `| archive refused | 2 |`

### Requirement: factory stats ties each spec defect caught downstream to the runs that wrote and critiqued the spec
For each verifier run with `SPEC-DEFECT` and each implementer run with `BLOCKED` in its window, `factory stats` MUST print the spec version the run worked from, the run that wrote it (or `human` for a human's version, or `unknown`), the latest critic run of that version (or `none`) and the number of critic REVISE runs on the ticket, and SHALL print how many approved tickets with and without a REVISE later had such a catch.

#### Scenario: Each downstream spec catch names the runs that wrote and critiqued its spec
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## C\./,/^## D\./p' $F/out | grep '^| ' | grep -vE '^\| (caught by|critic REVISE on the ticket) \|')`
- THEN it prints exactly these five lines, one per line: `exit=0`, `| run-0007-implementer | BLOCKED | T-0001.1 | 2 | run-0005-spec_writer | run-0006-critic | 1 |`, `| run-0011-verifier | SPEC-DEFECT | T-0001.1 | 3 | human | none | 1 |`, `| yes | 1 | 1 |`, `| no | 1 | 0 |`

### Requirement: factory stats reports each role's cost from run records first and transcripts second
`factory stats` MUST report, per role and model, the runs including killed ones, their wall time, and their context and output tokens, taking each run's tokens from its cost record when it has one and otherwise from the one transcript under `--transcripts` that the matching rule assigns to it, counting each message id once, and SHALL say per row how many runs used each source.

#### Scenario: Cost comes from the run record, else the transcript of that store's run, counted once per call
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once. Store s1's spec writer run 3 has a cost record and also a transcript; the transcript that names s2's `run-0001-triage` overlaps s1's run of the same id; the critic transcript's first message relays a user request naming another run.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --transcripts $F/tx --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## D\./,$p' $F/out | grep '^| [a-z]' | grep -v '^| role |')`
- THEN it prints exactly these eight lines, one per line: `exit=0`, `| triage | opus | 3 | 190 | 10 | 2 | 0.00 | record 0, transcript 1, none 2 |`, `| spec_writer | opus | 2 | 500 | 1100 | 50 | 1.50 | record 1, transcript 0, none 1 |`, `| critic | fable | 3 | 160 | 310 | 17 | 0.00 | record 0, transcript 1, none 2 |`, `| implementer | opus | 2 | 1000 | 60 | 4 | 0.00 | record 0, transcript 1, none 1 |`, `| reviewer | fable | 2 | 206 | 0 | 0 | 0.00 | record 0, transcript 0, none 2 |`, `| verifier | fable | 1 | 80 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |`, `| verifier | opus | 1 | 120 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |`

### Requirement: The transcript cost report counts each message once
`python -m factory.cost DIR` MUST count each transcript message id once, using its last record's usage, so that its calls, context tokens and output tokens SHALL equal those of one record per model call.

#### Scenario: The transcript cost report counts each message once
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once. The critic transcript holds two model calls, written as five records.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && .venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |')`
- THEN it prints exactly `| critic | fable-5 | 1 | 2 | 310 | 17 |`

### Requirement: factory stats reproduces the hand count on the two live stores
Over this repository's store and the Nanobot target's store, up to 2026-10-07 12:00 UTC, `factory stats` MUST print the request's figures for the code reviewer, spec critic, implementer and parks, and SHALL keep the verifier's two models in separate rows.

#### Scenario: Stats reproduces the hand count on the two live stores
Reads both live stores; writes only its output file under the temporary directory. The expected lines are the two stores' records as they stood on 2026-10-11, when the prototype printed them. The stores live outside the checkout under test, so a mismatch is first checked against them before it is called a defect: a `park.corrected` event dated after the cut does not move these lines (the correction rule), but a hand edit to a run record or log line dated before the cut, or a store moved away from these paths, would, and the verifier names which in its report.
- WHEN `(bin/factory stats --store /Users/dphang/dev/spec-factory/.factory/store --store /Users/dphang/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 > ${TMPDIR:-/tmp}/t0043-live.txt 2>&1; echo "exit=$?"; sed -n '/^## A\./,/^## B\./p' ${TMPDIR:-/tmp}/t0043-live.txt | grep -E '^\| (critic|implementer|reviewer|verifier) \| '; sed -n '/^## B\./,/^## C\./p' ${TMPDIR:-/tmp}/t0043-live.txt | grep -E '^\| (NEEDS-HUMAN from triage|all parks) \|')`
- THEN it prints exactly these eight lines, one per line: `exit=0`, `| critic | fable | 84 | 0 | 19 | APPROVE 65, REVISE 19 | 19 | - |`, `| implementer | opus | 111 | 3 | 18 | BLOCKED 18, READY-FOR-REVIEW 92, UNKNOWN 1 | - | 0 in 0 read, 111 not recorded |`, `| reviewer | fable | 94 | 5 | 4 | APPROVE 90, ESCALATE 1, REQUEST-CHANGES 3 | 3 | - |`, `| verifier | fable | 5 | 0 | 1 | SPEC-DEFECT 1, VERIFIED 4 | - | - |`, `| verifier | opus | 108 | 0 | 8 | FAILED 4, SPEC-DEFECT 4, VERIFIED 100 | - | - |`, `| NEEDS-HUMAN from triage | 30 |`, `| all parks | 82 |`

## Current truth: harness-code

# harness-code

## Requirements

### Requirement: The harness keeps no definition, setting or comment that nothing uses or that is no longer true
The harness source under `factory/` SHALL carry no definition that nothing calls or reads, no instance setting that no code reads, and no comment or message that describes behaviour the harness no longer has. It MUST keep every behaviour that a command can reach.

#### Scenario: The four dead definitions are gone and nothing names them
- WHEN `echo "$(grep -nE '^(def run_gates\(|STATES = |OPS = |def load_config\()' factory/gitops.py factory/store.py factory/specstore.py | wc -l | tr -d ' ') $(grep -rnF --include='*.py' -e 'gitops.run_gates' -e 'store.STATES' -e 'specstore.OPS' -e 'store.load_config' factory tests | wc -l | tr -d ' ')"`
- THEN it prints `0 0`

#### Scenario: No harness or test file names the force-push setting
- WHEN `grep -rn --exclude-dir=__pycache__ force_push_allowed factory tests | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write
- WHEN `echo "$(grep -c prompt_name factory/cli.py) $(grep -c "already has run {t\[.in_flight.\]\[0\]} in flight" factory/cli.py) $(grep -c 'store.ensure_gitignore(root)' factory/cli.py)"`
- THEN it prints `0 2 2`

#### Scenario: No harness module has three blank lines in a row
- WHEN `awk 'FNR==1{n=0} /^$/{n++; if(n==3) print FILENAME":"FNR; next} {n=0}' factory/*.py | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: The three stale texts are gone
- WHEN `grep -nF -e 'commit-and-push' -e 'live pilot store is unaffected' -e 'not supported yet' factory/*.py | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: The repo-root helper takes no argument and every caller passes none
- WHEN `echo "$(grep -n 'repo_root(cfg' factory/*.py | wc -l | tr -d ' ') $(grep -o 'gitops.repo_root()' factory/*.py | wc -l | tr -d ' ') $(grep -c '^def repo_root() -> Path:$' factory/gitops.py)"`
- THEN it prints `0 12 1`

#### Scenario: The harness has no unused imports or variables
- WHEN `uvx ruff check --select F401,F841 factory tests`
- THEN it prints `All checks passed!` and exits 0

#### Scenario: The harness suite passes, and only the force-push test lines change under tests
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0044-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only main...HEAD -- tests)`
- THEN the first line reports a number of passed tests and no `failed` or `error`, and every later line, if any, is `tests/factory/fixtures/instance/instance.yaml` or `tests/factory/test_instance.py`

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
`factory resolve <parent> --replan F` on a parked parent whose current sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; a sub-ticket that a later plan superseded SHALL NOT count, and with any current sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

#### Scenario: A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.4 status=merged >/dev/null && bin/factory ticket set T-0001 status=ready-for-parent-verify >/dev/null && bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null && echo 'Re-plan: one more fix.' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=0 ready-for-planner`

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

### Requirement: Accepting the refused paths returns the sub-ticket to its checks, which then merge
`factory resolve <id> --accept-paths F`, on a park whose reason starts `BLOCKED from merge gate:`, MUST write F as the ticket's next ruling, add the head's undeclared protected paths to the ticket's `accepted_paths`, keep every result row, and return the ticket to `checks-in-flight`; `factory merge` SHALL then merge it. On any other park it MUST refuse with exit 2, writing nothing, with an error containing `--accept-paths applies to`.

#### Scenario: Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The scenario parks the sub-ticket with the gate's own error, as the build does.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: core/b.py is part of the approved design.\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>&1; echo "accept=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') rows=$(ls $FACTORY_STATE/results/$H | grep -c yaml) ruling=$(cmp -s $T/ru.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo kept || echo missing)"; $B merge T-0001.1 >/dev/null 2>&1; echo "merge=$? on_main=$(git -C $T/t diff --name-only $M main | grep -c 'core/b\.py')")`
- THEN it prints exactly `accept=0 checks-in-flight rows=3 ruling=kept`, then `merge=0 on_main=1`

#### Scenario: Accepting paths is refused on any other park and writes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: x\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>$T/err; echo "accept=$? refused=$(grep -c 'accept-paths applies to' $T/err) $($B ticket show T-0001.1 | sed -n 's/^status: //p') rulings=$(ls $FACTORY_STATE/approvals/T-0001.1 2>/dev/null | grep -c ruling)")`
- THEN it prints exactly `accept=2 refused=1 parked rulings=0`

### Requirement: A ruling on a merge gate's refusal sends the sub-ticket back to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts `BLOCKED from merge gate:` SHALL return the sub-ticket to `ready-for-implementer` at the same round, and the next implementer input SHALL contain F.

#### Scenario: A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: take core/b.py out of this change.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "ruling=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') reason=$(echo "$E" | grep -c '^BLOCKED from merge gate: ')"; R=$($B run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take core/b.py out of this change.')")`
- THEN it prints exactly `ruling=0 ready-for-implementer reason=1`, then `in_input=1`

### Requirement: A ruling on a reviewer's escalation returns the sub-ticket to its checks
`factory resolve <id> --ruling F` on a park whose reason starts `ESCALATE from reviewer` MUST write F as the ticket's next ruling and return the ticket to `checks-in-flight` at the same round. It MUST set aside the head's rows that did not pass, by the rule `--redispatch` uses, and the next reviewer input SHALL contain F.

#### Scenario: A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'docs/d.md' && printf "Commit: $H\nSTATUS: ESCALATE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/e.md && $B results record T-0001.1 --head $H --role reviewer --output $T/e.md --run run-0003-reviewer >/dev/null && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: the escalation is settled.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')"; R=$($B run start --role reviewer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: the escalation is settled.')")`
- THEN it prints exactly `exit=0 checks-in-flight kept: ci.yaml verifier.yaml ` (the reviewer's ESCALATE row set aside, the passing verifier and gate rows kept), then `in_input=1`

### Requirement: A ruling returns a sub-ticket whose implementer run failed to start
`factory resolve <id> --ruling F` on a park whose reason starts `harness-bug: run start implementer:` and that was parked from `ready-for-implementer` MUST write F as the ticket's next ruling and return it to `ready-for-implementer` at the same round; on a harness-bug park of any other kind it MUST still refuse with exit 2, writing nothing.

#### Scenario: A ruling on a harness-bug park from an implementer's run start returns the sub-ticket, and its implementer then starts
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" (current truth, spec-amendment) run once. The park reason is the spec drift refusal wrapped as the Workflow script's clerk wrapped it for the sub-ticket that showed this problem.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && land src/greet.py tests/test_greet.py && E=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p') && bin/factory ticket park T-0001.1 --reason "harness-bug: run start implementer: $E" >/dev/null && printf 'Ruling: the new test may change.\n' > $T27/r.md; bin/factory resolve T-0001.1 --ruling $T27/r.md >/dev/null 2>&1; echo "ruling=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') kept=$(cmp -s $T27/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo yes || echo no) drift=$(echo "$E" | grep -c '^BLOCKED from harness: spec drift: ')"; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "start=$? runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)")`
- THEN it prints exactly `ruling=0 ready-for-implementer kept=yes drift=1`, then `start=0 runs=1`

#### Scenario: A ruling on a checker's or a compose step's harness-bug park is still refused
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(for r in 'harness-bug: run start reviewer: x' 'harness-bug: run compose implementer: x'; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && { case "$r" in *reviewer*) bin/factory ticket set T-0001.1 status=checks-in-flight >/dev/null;; esac; } && bin/factory ticket park T-0001.1 --reason "$r" >/dev/null && printf 'Ruling: x\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>$T23/err; echo "exit=$? refused=$(grep -c -- '--ruling applies to' $T23/err) $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') rulings=$(ls $FACTORY_STATE/approvals/T-0001.1 2>/dev/null | grep -c ruling)"); done)`
- THEN it prints two lines, each exactly `exit=2 refused=1 parked rulings=0`

## Current truth: spec-amendment

# spec-amendment

## Requirements

### Requirement: A human amends a pinned spec whose intent is unchanged
`factory spec amend PARENT --file F --reason LINE --intent unchanged`, on a ticket with an approved spec, before archive, with no run in flight on it or its sub-tickets, MUST write F as the next spec version and make it the approved one, re-pin the change folder from F while keeping its `tasks.md`, and SHALL leave merged sub-tickets merged.

#### Scenario: An intent-unchanged amendment re-pins the change and keeps the plan's tasks
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0027-amend.sh <<'EOF'
# Sourced from the repo root: a scratch store with a spec store, and a target repo whose main holds
# src/greet.py and src/other.py. T-0001's spec v1 was added with main at that commit, then approved.
# Its design names `src/greet.py`; its one requirement, "Greets", has one scenario, "Greeting is
# printed", running `echo hi`. $T27/v2.md differs from v1 only in that scenario (`echo hello`);
# $T27/v3.md also changes the Decisions line. T-0001 has no sub-tickets yet. Defines `plan TEXT`
# (adds the plan TEXT and moves T-0001 to planned) and `land FILE...` (one commit on main that
# writes each FILE).
T27=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T27/store FACTORY_REPO=$T27/t FACTORY_INTEGRATION_BRANCH=main
land() { for f in "$@"; do mkdir -p $T27/t/$(dirname $f) && echo "# $f" >> $T27/t/$f; done; git -C $T27/t add -A && git -C $T27/t -c user.email=f@x -c user.name=f commit -qm "land $*"; }
git init -q -b main $T27/t && land src/greet.py src/other.py
bin/factory init >/dev/null 2>&1
spec() { printf '=== proposal.md\n## Problem\nx\n## Decisions\n- %s\n=== design.md\n## Proposed change\nEdit `src/greet.py`.\n## Tests to change\nnone\n=== specs/demo/spec.md\n## ADDED Requirements\n### Requirement: Greets\nThe tool SHALL greet.\n\n#### Scenario: Greeting is printed\n- WHEN `%s`\n- THEN it prints `%s`\n=== verification.md\n## Acceptance\n- Greeting is printed → NEW\n' "$1" "$2" "$3"; }
spec 'Greet by default.' 'echo hi' 'hi' > $T27/v1.md && spec 'Greet by default.' 'echo hello' 'hello' > $T27/v2.md && spec 'Greet only when asked.' 'echo hello' 'hello' > $T27/v3.md
printf '# Fixture\n\nGreet.\n' > $T27/req.md
bin/factory ticket new --file $T27/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T27/v1.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
plan() { printf "$1" > $T27/plan.md && bin/factory subticket add T-0001 --file $T27/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; }
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' && bin/factory ticket set T-0001.1 status=merged >/dev/null && printf 'planner tasks\n' > $FACTORY_STATE/openspec/changes/T-0001/tasks.md; bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 --json | tail -1 | grep -o '"approved_version": [0-9]*') pinned=$(grep -c 'echo hello' $FACTORY_STATE/openspec/changes/T-0001/specs/demo/spec.md) tasks=$(grep -c 'planner tasks' $FACTORY_STATE/openspec/changes/T-0001/tasks.md) first=$(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged`

### Requirement: Later runs receive the amended spec, and the record names what changed
After an amendment, a role run that reads the pinned spec SHALL receive the amended version, and the amendment record MUST list each changed scenario and each sub-ticket merged before it, with the reason, and the log MUST record a `spec.amended` event.

#### Scenario: A later implementer run receives the amended spec, and the record lists what changed
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' && bin/factory ticket set T-0001.1 status=merged >/dev/null; bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; A=$FACTORY_STATE/approvals/T-0001/amendment-1.md; echo "changed=$(cat $A 2>/dev/null | grep -cxF -- '- changed: Greeting is printed') merged=$(cat $A 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged') reason=$(cat $A 2>/dev/null | grep -c 'Seed the greeting.') logged=$(bin/factory log tail --event spec.amended | grep -c '"ticket": "T-0001"')"; R=$(bin/factory run start --role implementer --ticket T-0001.2 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "amended=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'echo hello') old=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -cw 'echo hi') run_version=$(sed -n 's/^spec_version: //p' $FACTORY_STATE/runs/${R:-none}/meta.yaml 2>/dev/null)")`
- THEN it prints exactly `changed=1 merged=1 reason=1 logged=1`, then `amended=1 old=0 run_version=2`

### Requirement: Archive writes the amended version into current truth
`factory archive` after an amendment SHALL write the amended version's scenarios into current truth, not the version first approved.

#### Scenario: Archive after an amendment writes the amended scenario
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; bin/factory archive T-0001 >/dev/null 2>&1; echo "archive=$? hello=$(grep -c 'echo hello' $FACTORY_STATE/openspec/specs/demo/spec.md) hi=$(grep -cw 'echo hi' $FACTORY_STATE/openspec/specs/demo/spec.md)")`
- THEN it prints exactly `archive=0 hello=1 hi=0`

### Requirement: An amendment that changes intent is refused with a restart note
`factory spec amend` MUST refuse with `"ok": false` and exit 2, writing nothing, when `--intent changed` is given or when the amended version changes the Problem, a Decisions line, or a requirement's name, operation or statement, and the refusal SHALL name each such change and say which sub-tickets have merged, which a restart would discard, and the commands to re-spec or to close and re-file.

#### Scenario: An amendment declared or found to change intent is refused, naming what a restart keeps and discards
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' && bin/factory ticket set T-0001.1 status=merged >/dev/null; for x in "v2.md changed" "v3.md unchanged"; do set -- $x; E=$(bin/factory spec amend T-0001 --file $T27/$1 --reason "r" --intent $2 2>/dev/null | tail -1); echo "intent=$2 exit_json=$(echo "$E" | grep -c '"ok": false') restart=$(echo "$E" | grep -c 'Restart instead') decision=$(echo "$E" | grep -c 'Decisions line') merged=$(echo "$E" | grep -c 'T-0001.1 / First') pending=$(echo "$E" | grep -c 'T-0001.2 / Second: ready-for-implementer') paths=$(echo "$E" | grep -c 'resolve T-0001 --to spec-gate.*resolve T-0001 --close')"; done; echo "$(bin/factory ticket show T-0001 --json | tail -1 | grep -o '"approved_version": [0-9]*') versions=$(ls $FACTORY_STATE/specs/T-0001 | grep -c '\.md$') records=$(ls $FACTORY_STATE/approvals/T-0001 | grep -c '^amendment-')")`
- THEN it prints exactly `intent=changed exit_json=1 restart=1 decision=0 merged=1 pending=1 paths=1`, then `intent=unchanged exit_json=1 restart=1 decision=1 merged=1 pending=1 paths=1`, then `"approved_version": 1 versions=1 records=0`

### Requirement: An amendment that cannot be applied is refused and writes nothing
`factory spec amend` MUST refuse with `"ok": false` and exit 2, writing no version, record or pin, when the ticket was archived, when it is a sub-ticket, when the reason is not one line, when the version fails the gate's checks, or while a run is in flight on the ticket or one of its sub-tickets, and the in-flight refusal SHALL name the run.

#### Scenario: An amendment after archive is refused
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; bin/factory archive T-0001 >/dev/null 2>&1; echo "late=$(bin/factory spec amend T-0001 --file $T27/v1.md --reason "Too late." --intent unchanged 2>/dev/null | tail -1 | grep -c '"ok": false') changes=$(ls $FACTORY_STATE/openspec/changes | tr '\n' ' ')hello=$(grep -c 'echo hello' $FACTORY_STATE/openspec/specs/demo/spec.md)")`
- THEN it prints exactly `late=1 changes=archive hello=1`

#### Scenario: A malformed amendment, a sub-ticket target and a two-line reason are refused and write nothing
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && grep -v '→ NEW' $T27/v2.md > $T27/bad.md; m=$(bin/factory spec amend T-0001 --file $T27/bad.md --reason "r" --intent unchanged 2>/dev/null | tail -1 | grep -c 'no NEW/REGRESSION label'); s=$(bin/factory spec amend T-0001.1 --file $T27/v2.md --reason "r" --intent unchanged 2>/dev/null | tail -1 | grep -c '"ok": false'); r=$(bin/factory spec amend T-0001 --file $T27/v2.md --reason "$(printf 'two\nlines')" --intent unchanged 2>/dev/null | tail -1 | grep -c '"ok": false'); echo "malformed=$m subticket=$s reason=$r $(bin/factory ticket show T-0001 --json | tail -1 | grep -o '"approved_version": [0-9]*') v2=$(ls $FACTORY_STATE/specs/T-0001 | grep -c '^v2.md$') records=$(ls $FACTORY_STATE/approvals/T-0001 | grep -c '^amendment-')")`
- THEN it prints exactly `malformed=1 subticket=1 reason=1 "approved_version": 1 v2=0 records=0`

#### Scenario: An amendment is refused while a sub-ticket's run is in flight, naming the run
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; e=$(bin/factory spec amend T-0001 --file $T27/v2.md --reason "r" --intent unchanged 2>&1 >/dev/null); echo "exit=$? names_run=$(echo "$e" | grep -c 'run-0001-implementer') $(bin/factory ticket show T-0001 --json | tail -1 | grep -o '"approved_version": [0-9]*') v2=$(ls $FACTORY_STATE/specs/T-0001 | grep -c '^v2.md$') pinned_old=$(grep -cw 'echo hi' $FACTORY_STATE/openspec/changes/T-0001/specs/demo/spec.md) records=$(ls $FACTORY_STATE/approvals/T-0001 | grep -c '^amendment-')")`
- THEN it prints exactly `exit=2 names_run=1 "approved_version": 1 v2=0 pinned_old=1 records=0`

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

### Requirement: A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets
A sub-ticket SHALL record the parent's approved version it was planned from, and that record MUST NOT follow later changes to its `spec` record. Once a parent has a sub-ticket planned from a later version, each of its sub-tickets that is not merged and was planned from an earlier version MUST be listed as superseded and left out of every other list `ticket ready-implementers` returns except `subtickets`. Its record SHALL be kept. `subticket add` SHALL report and log the sub-tickets it supersedes. A record with no plan version SHALL fall back to its `spec.approved_version`.

#### Scenario: After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0038-respec.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh. T-0001 was planned at approved spec v1 as
# T-0001.1 (merged), T-0001.2 (closed by a human with no commits) and T-0001.3 (waiting on
# T-0001.2, never started). The human parked the parent, sent it back to the spec gate and approved
# an edited spec, v2, so T-0001 is ready for its planner again, as Nanobot T-0024 was.
printf 'ST-1 / Base\nDepends on: none\nParallel-safe: yes\n\nST-2 / Dropped\nDepends on: none\nParallel-safe: yes\n\nST-3 / Unstarted\nDepends on: ST-2\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null
bin/factory ticket transition T-0001.2 --to closed --by t >/dev/null
bin/factory ticket park T-0001 --reason "sub-ticket closed by a human: T-0001.2" >/dev/null
bin/factory resolve T-0001 --to spec-gate >/dev/null
printf '## Problem\nx, amended\n' > $T23/spec2.md
bin/factory approve-spec T-0001 --edit $T23/spec2.md >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && A=$(bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1) && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; R=$(bin/factory ticket ready-implementers T-0001 | tail -1); echo "add: $(echo "$A" | grep -o '"superseded": \[[^]]*\]')"; for k in ready closed superseded; do echo "$k: $(echo "$R" | grep -o "\"$k\": \[[^]]*\]")"; done; echo "kept=$(ls $FACTORY_STATE/tickets | tr '\n' ' ')logged=$(cat $FACTORY_STATE/log/*.jsonl | grep '"event": "subtickets.superseded"' | grep -c '"T-0001.2", "T-0001.3"')")`
- THEN it prints exactly `add: "superseded": ["T-0001.2", "T-0001.3"]`, `ready: "ready": ["T-0001.4"]`, `closed: "closed": []`, `superseded: "superseded": ["T-0001.2", "T-0001.3"]`, `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=1`, one per line

#### Scenario: The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once. The first part moves T-0001.3's `spec` record to v2, as an amendment under approved T-0027 would. The second part clears `planned_from` on every record, as on a record made before this change.
- WHEN `( (. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && bin/factory ticket set T-0001.3 spec.version=2 spec.approved_version=2 >/dev/null && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; echo "moved: $(bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"superseded": \[[^]]*\]')"); (. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; for i in 1 2 3 4; do bin/factory ticket set T-0001.$i planned_from= >/dev/null 2>&1; done; echo "unrecorded: $(bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"superseded": \[[^]]*\]')"))`
- THEN it prints exactly `moved: "superseded": ["T-0001.2", "T-0001.3"]`, then `unrecorded: "superseded": ["T-0001.2", "T-0001.3"]`

#### Scenario: A second plan at the same approved version supersedes nothing
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' > $T23/plan1.md && bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null && bin/factory ticket set T-0001.1 status=merged >/dev/null && printf 'ST-1 / Extra\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; echo "exit=$?"; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]\|"remaining": \[[^]]*\]')`
- THEN it prints exactly `exit=0`, then `"ready": ["T-0001.2"]`, then `"remaining": ["T-0001.2", "T-0001.3"]`

### Requirement: A new plan may not depend on a sub-ticket it supersedes
`factory subticket add` MUST refuse with exit 2, writing no sub-ticket, a plan whose `Depends on:` line names a sub-ticket that the plan supersedes, and the refusal SHALL name that sub-ticket.

#### Scenario: A plan that depends on an old unmerged sub-ticket is refused and writes nothing
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.3\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>$T23/err; echo "exit=$? names=$(grep -c 'T-0001.3' $T23/err) $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints exactly `exit=2 names=1 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.yaml `

### Requirement: The planner is told which sub-tickets its plan will supersede
When a plan made at the parent's approved version would supersede existing sub-tickets, the planner's input SHALL name them on one line after the existing sub-ticket list, and that list SHALL be unchanged.

#### Scenario: A re-specced parent's planner input names the sub-tickets its plan supersedes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "said=$(cat $I 2>/dev/null | grep -cxF 'Not merged and planned from an earlier approved version, so a new plan supersedes them and may not depend on them: T-0001.2, T-0001.3') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / Base: merged' -e '- T-0001.2 / Dropped: closed' -e '- T-0001.3 / Unstarted: waiting-dependencies')")`
- THEN it prints exactly `said=1 listed=3`

## Capability index: current truth not given in full above

This list is complete: every current-truth capability not given in full above has one line here. Open a capability at its path before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, sends that capability in full to the critic, so cite under Evidence each capability you open.

- gate-commands, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/gate-commands/spec.md`: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them; A skipped command is recorded on the gate result, and the merge still needs that result to pass; The implementer is given every gate command; A malformed gate entry refuses every build role's run start
- harness-docs, 67 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-docs/spec.md`: The documents record the change; The documents record the live-store guard; The documents describe the store branch; The planner labels checks per sub-ticket and may list tests an earlier sibling added; The spec writer lists the tests a decision overturns, and the critic checks for one left off; The preamble and the code reviewer accept a checked sibling entry; Role runs receive the new rules; The documents record the sibling-tests check; The documents record the declared-path rule; The documents record the small-change lane; Every role is told to wait for its own commands; The code reviewer judges the diff and leaves the suite and the gate to the verifier; The documents record the empty-output route; The spec writer and the critic carry the turn-economy rules; Spec writer and critic runs receive the turn-economy rules; Nothing else in the two prompts changes; The documents record the turn-economy change; The documents record the critic revert; The documents record the capability index; The documents describe the whole decision log for the spec writer, critic and planner; The documents record superseded plans; The prompts tell the reviewer what the gate checks and the spec writer how to declare; The documents record the protected-path rule at merge; The implementer, verifier, code reviewer, planner and triage carry the reading rules; The reading rules are the only change to the role prompts; Runs of the five roles receive the reading rules; The documents record the reading rules for the five roles; The critic's rubric asks about cross-ticket dependencies; The documents record spec amendment, spec drift and the cross-ticket check; The documents record the environment sync and the dropped virtual environment; The documents describe the driver; The documents record the sibling-merge exception and the start-failure ruling; The documents record the driver's exemption and its same-ticket guard; The documents record factory stats
- harness-suite, 2 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-suite/spec.md`: The harness suite runs mid-edit without loosening the lock
- live-store-guard, 14 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/live-store-guard/spec.md`: Unmarked writes to a live store are refused while a role run is in flight there; Writes from inside a store's run directories or code checkouts are refused, marked or not; Reads, marked commands from outside the store, throwaway stores and idle stores stay open; The marker does not lift the harness lock; factory stats reads any store under any harness revision and writes nothing
- merge-gate, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/merge-gate/spec.md`: A store commit does not hold back a merge; A commit to the integration branch still holds back a merge; The merge gate refuses a changed protected path the pinned spec does not declare; A declared or unprotected path merges with no further approval
- role-escalations, 5 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-escalations/spec.md`: The implementer and verifier leave declared protected paths out of ESCALATIONS; Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
- role-inputs, 15 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-inputs/spec.md`: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest; A ticket whose triage output names no capabilities receives today's inputs; Triage receives the capability index and is asked to name the capabilities a request touches; The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names; The critic sees approved changes not yet archived
- run-environment, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/run-environment/spec.md`: The running-code wrapper drops an inherited virtual environment; Each build checkout is synced before its role starts; A failed sync stops the run before it starts; Without environment_sync, run start and the input are unchanged
- store-setup, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/store-setup/spec.md`: Run records are exempt from whitespace checks; No half instance, and a missing briefing refuses; Relative environment paths resolve from the caller's directory; A new instance's store is a checkout of its own branch; init refuses when more than one remote carries the store branch; init refuses to run from inside the store checkout; init refuses a store path the integration branch has tracked; store migrate moves a tracked store onto its branch and keeps every record; store migrate refuses while the store is in use or uncommitted; A checkout of an older commit leaves a moved store untouched

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
2026-10-05 T-0028 Part A overturns the cut in T-0016's spec. The path-scoped gate skip is built as the operator pre-approved it, with no repository's configuration changed. Rejected: cutting it again because it would have skipped almost no past run. The request expects a small saving here and still asks for the mechanism. Part A is a separate part, so the operator can delete it and its scenarios at the gate.
2026-10-05 T-0028 A gate command's `paths` are git pathspecs. A command is skipped when `git diff --name-only <base>...<head> -- <paths>` lists no file. Include entries (`src/`) and exclude entries (`:(exclude)dev/`) both work. Rejected: a glob matcher of our own, a second matching rule that could disagree with git's. Standing: later tickets and instance configs use pathspec semantics.
2026-10-05 T-0028 If this repository's suite is ever scoped, its paths should exclude what it does not read rather than list what it does: `:(exclude)dev/` and `:(exclude)README.md`. Rejected: the requester's inclusion list, which leaves out `.gitignore` and any new top-level file, so it would skip the suite on changes that fail it.
2026-10-05 T-0028 The harness decides the skip when a reviewer or verifier run starts on a sub-ticket. It reads the live instance's configuration and that run's base and head. The verifier is told which commands are skipped, so it does not decide. Rejected: letting the verifier judge relevance, which no record could check.
2026-10-05 T-0028 Each skipped command is recorded twice: in the checker run's `meta.yaml` (`gate_skipped`) and on the `ci` row (`skipped`). Each entry has the command, `status: SKIPPED` and the reason. The row's PASS or FAIL still comes from the verifier's `Gate suite:` line, over the commands that ran.
2026-10-05 T-0028 A malformed gate entry refuses every implementer, reviewer and verifier run start with exit 2, before a run is created. A malformed entry is anything other than a string, or a mapping with a non-empty string `command` and an optional non-empty list of non-empty strings `paths`, with no other key. Rejected: treating a typo such as `path:` as unscoped. The operator would believe a scope is in force that is not.
2026-10-05 T-0028 An empty `paths` list is refused. Rejected: reading it as "covers nothing", which would skip the command on every diff.
2026-10-05 T-0028 The planner is skipped when all of these hold, and otherwise runs as today: the parent has no sub-ticket and no earlier planner run; its latest spec-writer run did not end NEEDS-SPLIT; and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that contains the word seam or seams. This sorts all thirteen past parents as they were built (Evidence). Rejected: the requester's "exactly one lettered part", which would have skipped none of the nine. Rejected: NEEDS-SPLIT alone, which would have built T-0025's two parts, about 470 lines, as one sub-ticket. Standing: the planner runs only for a spec that is split, re-planned or already planned once.
2026-10-05 T-0028 To force the planner on a spec that meets every condition, the operator adds a `### Size and seams` heading in a gate edit (`approve-spec --edit`). No new flag.
2026-10-05 T-0028 The whole-spec sub-ticket is `<parent>.1`, at `ready-for-implementer`, with no dependency. Its text names every scenario of the approved spec, one `- <name>` line each. For everything else it points to the spec: every lettered part, the spec's labels, its Tests to change and its Risk list. Because it names every scenario, the parent closes on its VERIFIED run under the existing rule (part C).
2026-10-05 T-0028 The store records the skip three ways: a `plan.skipped` event in the log with its reason, the parent's plan file (`plans/<parent>.md`), and the change folder's `tasks.md` when the repository has a spec store. A planner-made plan writes the same two files.
2026-10-05 T-0028 A spec already applied on `main`, the planner's most frequent ESCALATE, is caught after the skip by the implementer's step 2 and by the verifier's base run of NEW checks (design part B, table). The catch costs an implementer run in place of a planner run. Rejected: a harness check of "already applied", which would need the agents' judgment of what the spec asks for.
2026-10-07 T-0032 Retry-once-then-park on a role's unusable output (#41's EMPTY-OUTPUT) is the general mechanism: later refusal kinds (#68 format, #67 spec-lint) register with it rather than adding their own. resolve --ruling should also accept a budget-kill or EMPTY-OUTPUT park (rulings had to be placed by hand on T-0029.1 and T-0028.1).
2026-10-07 T-0032 An empty output is `EMPTY-OUTPUT`, never a budget kill. That covers a missing or empty output file, an agent call that returns blank text, and one that returns `null` (a user skip or a terminal API error). Rejected: keeping a budget-kill path for some of these. The harness enforces no budget, and the agent call reports no reason (Evidence).
2026-10-07 T-0032 Standing, from the operator's answer, already in `decisions.md` as the 2026-10-04 T-0032 line, for both parts: the empty-output route, and the reviewer leaving the suite and the gate to the verifier. Later changes follow both.
2026-10-07 T-0032 `EMPTY-OUTPUT` is decided in one place, `run finish`. The workflows no longer send `--status-override KILLED` for an empty return, so `run finish` reads the output file for every run. Rejected: a second override value in the scripts. It would label a run empty even when its output file was written.
2026-10-07 T-0032 The retry is counted inside one workflow run: one re-dispatch, then a park. Rejected: a counter in the store. It would add a ticket field for a case that a human already watches, because a workflow that stops is restarted by hand.
2026-10-07 T-0032 A thrown agent call is not re-dispatched. It carries its own error text, including the error thrown when the turn's token ceiling is spent, so it is the one stop the harness can name.
2026-10-07 T-0032 The last message is kept by a new command, `factory run last-message RUN --text=…`, called only after `run finish` has returned `EMPTY-OUTPUT`. The text is the last 4000 characters, as one shell single-quoted word. Rejected: passing it on every `run finish`, which would put each role's whole output through every clerk command.
2026-10-07 T-0032 A second empty output parks as `EMPTY-OUTPUT from <role>`, in the same form as the other role parks, and lists both runs. The last messages stay in the run directories, not in the reason.
2026-10-07 T-0032 A checker's second empty output parks before any result row is recorded for it. `resolve --redispatch` then re-runs only that checker, because the other checker's passing rows stand. Rejected: an `EMPTY-OUTPUT` result row and a join rule for it, a new row status for the same outcome.
2026-10-07 T-0032 The reviewer's input no longer lists the gate commands. It says that the verifier runs them, as the design's routing table already declares (`docs/design.md:126`).
2026-10-07 T-0032 The `budget kill` join reason is kept for hand-recorded `KILLED` rows. Rejected: renaming it, which would change three existing tests for a case no one reported.
2026-10-07 T-0032 `build.js:137` (the implementer's `budget kill` park) is removed. `run finish` can no longer return `KILLED` to the workflow, so the line would never run.
2026-10-07 T-0033 Protected paths at merge (#57, T-0033): the pinned spec's Risk list is the authorization; an undeclared changed protected path is refused at merge and parks for a ruling; no per-head approval step. All instances.
2026-10-08 T-0034 The critic keeps its minimum check, at least 2 cited paths and 1 acceptance command per review. It gains a cap of at most 2 paths and 1 command for any one claim. Rejected: replacing the minimum with the cap, which would let a critic approve having checked nothing. `docs/principles.md`'s Spiking section states the bound per claim ("Grounding a claim … two paths, one command").
2026-10-08 T-0034 The critic runs no test suite and builds nothing (no clone, worktree or prototype of the change). It runs an acceptance command only as the spec gives it, and picks one that runs no test suite. Standing: a later change to the critic prompt keeps this rule, as principle 2 requires.
2026-10-08 T-0034 A claim the critic could settle only by running a test suite or building the change is a finding for the writer, or a question, and the critic says what it could not check. The finding's severity follows the existing rubric. Rubric item 2 ("NEW items fail today") stays unchanged.
2026-10-08 T-0034 The writer and the critic get the same three reading sentences: batch independent reads and commands, read a line range once grep has found it, and send long output to a scratch file and grep or tail it. Only the writer gets "write the spec in as few writes as you can". The critic writes one verdict and needs no such rule.
2026-10-08 T-0034 No shared preamble line. The rules go only in the two role prompts. Rejected: a preamble line, which would reach every role, including the implementer and verifier, which the request does not cover.
2026-10-08 T-0034 The rules are added as new lines only, so no existing line of either prompt changes. The writer's rule is the last RULES bullet of the documented copy. The critic's rules follow its existing PROCESS line.
2026-10-08 T-0034 `docs/principles.md` records the critic's new rule under principle 2 and corrects principle 2's status line, which says "reader roles run no suites" was done by #41 alone.
2026-10-08 T-0034 The request's acceptance, a replay of 2–3 approved intakes with old and new prompts, is an Operator step. Running it needs live model runs, and judging spec quality side by side is a human call. The scenarios check the text the roles receive.
2026-10-08 T-0035 This change overturns part of a standing decision, one that later tickets must keep, recorded on 2026-10-08 for T-0034, the ticket that applied #73: "The critic runs no test suite and builds nothing ... Standing: a later change to the critic prompt keeps this rule". The no-test-suite half stands. The no-build half and the per-claim cap (T-0034's other 2026-10-08 decision) are removed. Authority: the operator's choice in `.factory/answers/T-0034-acceptance-2026-10-08.md`. Standing: later changes to the critic prompt keep the no-suite rule and do not re-add a per-claim cap or a no-build rule without new evidence.
2026-10-08 T-0035 The critic prompt gains one sentence that allows a small experiment in its scratch directory to confirm a finding. Without it, the kept sentence "A claim you could settle only by ... building the change is a finding" reads as the old ban. The kept sentence still covers building or trying out the change itself, which the request's item C (its `docs/principles.md` change) leaves to the writer or to a spike, a ticket built only to test whether an approach works. Rejected: deleting the kept sentence. The triage role, which sorts a request before the spec writer sees it, asked to keep it, and it still tells the critic what to do with a claim it cannot check.
2026-10-08 T-0035 The no-suite line gains its reason, "the implementer and the verifier run it", as the request's item B (its list of what the critic keeps) gives. `Pick an acceptance command that runs no test suite, and run it as the spec gives it.` and the Turn economy paragraph stay word for word.
2026-10-08 T-0035 The Spiking section records the replay result, as the request's item C asks ("Record the replay result"). The changelog entry records it too.
2026-10-08 T-0035 Of the current-truth requirements that #73 added, four are restated (MODIFIED), because each states the rule being removed or forbids removing a critic line. Other current-truth requirements that check the diff of their own change (for example "The documents record the live-store guard", which expects no prompt copy to change) are left as they are, as #73 left them. Their scenarios describe their own change, not standing behaviour.
2026-10-08 T-0035 "Writer unchanged from #73" is checked as no difference from `05cf8f9` in either writer prompt file, plus the writer's design block equal to its `docs/prompts/` copy. Together these mean the design block is unchanged too.
2026-10-09 T-0036 Triage names the capabilities on a new output line, `Capabilities:`, chosen from a capability index added to its input. A token that names no current-truth capability, such as `none` or `new`, is ignored.
2026-10-09 T-0036 Which capabilities a role receives in full: the names on triage's line, plus each existing capability whose `specs/<name>/spec.md` path appears in the spec the role works from. For the writer that is its previous version on a revision round. For the critic it is the version under review. For the planner it is the approved version, read whole, Evidence included. A writer that opens a capability and cites its path under Evidence therefore hands it to the critic. This keeps the request's rule that the critic sees the writer's list plus whatever the writer opened.
2026-10-09 T-0036 A ticket whose latest finished triage output has no `Capabilities:` line gets today's inputs, the whole of current truth and the whole log. This covers tickets triaged before this change, T-0036 among them. Rejected: sending only the index in that case, which would cut those tickets' inputs with no list to cut by.
2026-10-09 T-0036 An index line for a capability gives its name, its size, the absolute path of its spec and its requirement names. Rejected: the request's "one-sentence purpose", because no capability spec on either store has a purpose paragraph (Evidence).
2026-10-09 T-0036 A decision line goes in full when it is logged against this ticket, or when its text names a capability sent in full as a whole word. The log's other lines are indexed one line per ticket: ticket id, number of decisions, first and last date, and the ticket's title. The index heading gives the command `grep ' <ticket id> ' <absolute path of decisions.md>`. Rejected: one index line per decision, which comes to tens of kilobytes on Nanobot (240 lines, median 278 bytes).
2026-10-09 T-0036 A role opens deferred items by path, with its own file reads or `grep`. No `factory spec show` or `factory decision show` command is added. Rejected: those commands, because a command run from inside a role must clear the live-store fence and find the instance from the role's working directory. A path needs neither, and it is how compose already points at full specs (Evidence).
2026-10-09 T-0036 The instructions live in the index headings. They say the list is complete, that anything in it is opened by its path, and that citing a path hands the capability to the critic. Rejected: editing the writer and critic prompts, which would put the same words in two more protected copies.
2026-10-09 T-0036 A run's `input_sources` lists only the files sent in full. An index adds no source.
2026-10-09 T-0036 The standing 2026-10-04 T-0024 decision says that `decisions.md` "keeps reaching the spec writer, critic and planner". It still does: in full for the lines this ticket touches, and line by line for the rest through the index and its `grep` command.
2026-10-09 T-0036 Acceptance does not hold this change to the request's 40 kB mean and 100 kB maximum. The projection gives a mean of 101 kB and a maximum of 167 kB for the Nanobot store's last ten tickets, and the remainder lies outside this change (Problem, Evidence). The operator steps measure the real figures after the change runs.
2026-10-09 T-0036 The docs use one name for the new index, "capability index".
2026-10-09 T-0037 Decision log in role inputs (#78, T-0037): the spec writer, critic and planner get decisions.md whole; #75's decision filter is removed; any future scoping must not be able to drop a cross-cutting standing decision (see #54).
2026-10-09 T-0037 The spec writer, critic and planner receive `decisions.md` whole whenever it holds any text, whatever capabilities their ticket names. The decision index and its `grep` instruction are removed. This is the operator's Answer 1, already standing in `decisions.md` as the 2026-10-09 T-0037 line. Rejected: the request's rule of sending lines that name no capability in full and filtering the rest. On today's logs it sends every line anyway, and it could still hide a cross-cutting decision that happens to name a capability.
2026-10-09 T-0037 The capability index note loses its clause ", and the decisions that name it to the critic and the planner,"; the rest of the note stays word for word. Rejected: keeping the clause, which would tell the writer that citing a path is how decisions reach the critic and planner. That is no longer so. This edits one sentence of #75's capability half, which the triage assumption kept byte for byte.
2026-10-09 T-0037 The planner's decision part no longer reads triage's capability names or the approved spec's citations. It reads the whole log, as before #75.
2026-10-09 T-0037 The decision part is measured in this spec's Evidence, before and after, on both stores. No new file or harness command records it.
2026-10-09 T-0038 Each sub-ticket records `planned_from`, the parent's approved version when the sub-ticket was created. Nothing changes it afterwards. Rejected: reading `spec.approved_version`, which approved T-0027 moves forward on amendment.
2026-10-09 T-0038 Superseded is computed whenever sub-tickets are read, not stored. A sub-ticket is superseded when it has not merged and its `planned_from` is lower than the highest `planned_from` among its parent's sub-tickets. Rejected: the request's mark written at re-plan time. That needs a write on every path that adds a plan and a migration for stores that already hold such sub-tickets, such as Nanobot T-0024. Also rejected: comparing with the parent's current approved version. That would supersede the live plan after a T-0027 amendment that keeps it.
2026-10-09 T-0038 A record without `planned_from`, or with it null, falls back to its `spec.approved_version`. With neither, the sub-ticket counts as current.
2026-10-09 T-0038 A plan made from the same approved version supersedes nothing. This covers `resolve --replan` after a failed final check, and a second plan added by hand. The design ties a new plan to an amended spec (`docs/design.md:109`). To replace a plan without changing intent, the operator approves with `approve-spec --edit`, which always makes a new version. This is a standing decision.
2026-10-09 T-0038 Merged sub-tickets are never superseded. They count toward the close, the final check must contain their merges, and a new plan may depend on them.
2026-10-09 T-0038 `subticket add` refuses, writing nothing, a plan whose `Depends on:` names a sub-ticket that the plan supersedes. Rejected: accepting it. The dependant would wait forever, because a superseded sub-ticket is never dispatched.
2026-10-09 T-0038 `subticket add` reports the sub-ticket ids it newly supersedes under `superseded` and logs a `subtickets.superseded` event. Nothing is deleted, and every id stays taken.
2026-10-09 T-0038 `ticket ready-implementers` keeps `subtickets` as every sub-ticket id. `build.js` reads an empty list as "planned with none", and `dev/build-harness.spec.md:286` documents it that way. Every other list there leaves superseded sub-tickets out, and the new `superseded` list names them.
2026-10-09 T-0038 The planner is told which sub-tickets its plan will supersede, on one line after the existing list. With none, its input is byte-identical to today.
2026-10-09 T-0038 The name is "superseded", as the request and triage use it, and in the same sense as `results/<head>/superseded-<n>/`: a record kept but no longer counted.
2026-10-09 T-0033 The authorization is the pinned spec's Risk section. The pinned spec is the version the operator approved at the spec gate. For a sub-ticket, that is its parent's approved version (`specs/<parent>/v<approved_version>.md`). A ticket with no parent uses its own approved version. A ticket with no approved spec declares nothing. This is standing for every instance, from the operator's 2026-10-05 answer. It is already the 2026-10-07 T-0033 line in `decisions.md`, the factory's log of standing decisions that later tickets must follow.
2026-10-09 T-0033 The gate reads declarations from one fixed line in the Risk section: `Protected paths: none`, or `Protected paths: ` followed by one or more backticked paths or globs, separated by commas. An optional list marker (`- ` or `* `) may come before it, and an optional full stop after it. Each entry is one path or one glob. A brace list such as `factory/prompts/{a,b}.md` is one literal entry, which git does not expand, so it matches no file and declares nothing. A Risk line in any other shape declares nothing, and so does a line inside a fenced code block. Several such lines declare their union. Standing: specs declare protected paths only this way. Rejected: reading every backticked path in Risk, because today's Risk sections also put the paths they promise not to touch in backticks (Evidence). Rejected: the planner's per-sub-ticket `Protected paths:` field, which an agent writes and no human approves.
2026-10-09 T-0033 A changed path is "protected" when it matches one of the instance's in-repo `protected_paths` globs. It is "declared" when it matches a declared entry. Both matches use git's glob pathspecs (`:(glob)<pattern>`, so `**` crosses directories and `*` does not). This follows the 2026-10-05 T-0028 decision that the harness never adds a glob matcher of its own. Patterns that start with `~` or `/` are skipped.
2026-10-09 T-0033 The changed paths are those of `git diff --name-only --no-renames <integration branch>...<head>`, measured from the merge base; the head is the commit the gate is judging. Once the head contains the integration branch, that is exactly what the merge adds. `--no-renames` lists both sides of a move (Evidence). Rejected: the triage's "parent base". A catch-up run is an implementer run that merges the integration branch into a sub-ticket's branch that has fallen behind. After one, a diff from the parent's base counts other tickets' merged changes against this sub-ticket.
2026-10-09 T-0033 The gate runs this check after the three recorded results and before the containment check and the merge lock. A change that will be refused costs no catch-up run.
2026-10-09 T-0033 A refusal exits 2 and changes no ticket field. It logs one `merge.refused` event with the paths. Its error starts `BLOCKED from merge gate: ` and names each undeclared path, sorted and comma-separated. It names no declared path and uses no backtick, `$` or double quote, because the build workflow passes the reason through a shell command.
2026-10-09 T-0033 The build workflow parks the sub-ticket with that error, verbatim, as the reason. It already does the same for the harness's `BLOCKED from harness:` refusal at run start.
2026-10-09 T-0033 The human answers that park with one of two commands. `resolve --ruling F` sends the change back. It uses the existing BLOCKED route: the sub-ticket returns to its implementer with F in its input, and its round count (the number of fix cycles it may use) is not reset. The new `resolve --accept-paths F` accepts the paths under the approved design. It records F as the sub-ticket's next ruling. It adds the undeclared paths, recomputed on the current head, to a ticket field `accepted_paths`, which the gate treats as declared. It returns the sub-ticket to `checks-in-flight`, the state in which the reviewer and verifier judge it, with its recorded results kept, so the build merges it on its next pass. Rejected: one acceptance per head, because a catch-up run makes a new head and the same paths would park again. Rejected: amending the pinned spec's Risk section, because no command amends a pinned spec yet (T-0027 asks for one). An acceptance adds paths only for that sub-ticket and leaves every other merge condition in force.
2026-10-09 T-0033 `--accept-paths` refuses, with exit 2 and nothing written, on a park whose reason does not start `BLOCKED from merge gate:`. Its error starts `--accept-paths applies to`. It also refuses when the head is not the branch tip, or when no undeclared protected path remains.
2026-10-09 T-0033 A ruling on a park whose reason starts `ESCALATE from reviewer` returns the sub-ticket to `checks-in-flight`, round count unchanged. Its recorded results are set aside as `--redispatch` sets them aside: an APPROVE reviewer result is kept, and a VERIFIED verifier result with a PASS gate result is kept. Every other result moves to `superseded-<n>/`. The reviewer and verifier runs that follow receive the ruling, as they already do (`factory/compose.py` lines 278 and 300). This overturns `docs/design.md` line 109, which sends a reviewer ESCALATE to the implementer with the round count reset. Rejected: that route, because the 2026-10-05 escalation needed no code change. The re-run reviewer can still return REQUEST-CHANGES when a ruling asks for a fix.
2026-10-09 T-0033 Check 6 of the reviewer prompt keeps its first two sentences and adds "for the record" to the list of declared paths. Its last sentence says what the gate does: it merges a declared path with no further approval, and refuses and parks one the approved spec does not declare.
2026-10-09 T-0033 No per-head approval is added for paths that change the factory's own rules (option 3 of the operator's answer). The answer leaves it open for this spec gate. Adding it is a gate edit to this spec (a new lettered part) or a later ticket.
2026-10-09 T-0030 T-0030 (#24 A+C) closed as partly applied: part C merged (T-0030.3); parts A, B and per-role effort moved to #65 (backlog review 2026-10-09). Current truth was not folded for this ticket.
2026-10-09 T-0026 T-0026 (#47) withdrawn: merged into #65 at the backlog review 2026-10-09; the Workflow scripts it would change retire with #65.
2026-10-09 T-0039 All five roles get the critic's form of the paragraph, word for word, as one bullet starting `- Turn economy: `. It carries the three reading rules and the sentence saying why they matter. The spec writer's "as few writes as you can" stays out, as the request says. The writer's "such as a suite run" example also stays out, because the code reviewer must not run the suite. With one text, one check covers all five prompts.
2026-10-09 T-0039 The paragraph goes into each role's own prompt, not into the shared preamble. A preamble line would also reach the spec writer and critic, which already carry the rules, and T-0034 rejected a preamble line for the same reason. The request names the five prompts.
2026-10-09 T-0039 New lines only: no existing line of any prompt changes. Placement: in the implementer and verifier, a RULES bullet directly before the declared-path bullet, so that bullet stays last under RULES where T-0029 put it. In the code reviewer, the last bullet of WHAT YOU RUN, which is about the commands it runs. In the planner and triage, the last RULES bullet. In triage's run copy, that is before the instance-added "Acceptance items" block.
2026-10-09 T-0039 Acceptance checks the text each role receives: all three prompt copies and the composed run prompt. The request's own acceptance, the operator replaying past implementer and verifier runs with old and new prompts, is an Operator step. It needs live model runs and a human judgement of verdict quality (as in T-0034 and T-0029).
2026-10-09 T-0039 `docs/changelog.md` gains entry 64 after entry 63 and before the closing "Declined:" line. The entry cites the #74 replay result as entry 59.
2026-10-09 T-0027 The command is `factory spec amend <parent> --file <F> --reason "<one line>" --intent unchanged|changed`, run by a human. Rejected: the build spec's unbuilt `resolve --amend-spec`. Each `resolve` mode acts on a ticket the pipeline has stopped, and an amendment may be needed while a ticket is `planned` and not stopped.
2026-10-09 T-0027 `--intent` is required. With `unchanged`, the harness checks the claim: the amended version must keep the Problem section, every Decisions line, and each requirement's name, operation and statement (its text before its first scenario), whitespace aside. Scenarios, setup, Evidence, design text and Tests to change may change. Any other difference is refused as a change of intent, naming each one. `--intent changed` is always refused. Rejected: issue #50's critic run on every amendment, which needs a new route from the command to the critic; the mechanical check covers the same three things. Rejected: no flag, which lets a human make an intent change without saying so. This is a standing decision.
2026-10-09 T-0027 A refused change of intent prints a restart note. The note lists each merged sub-ticket with its merge commit, which stays on the integration branch. It lists each unmerged one with its state and branch, which a restart discards. It names both ways to restart. The first re-specs and re-plans: `factory ticket park`, `factory resolve <id> --to spec-gate`, then `factory approve-spec <id> --edit F`, after which the new plan supersedes the unmerged sub-tickets. The second closes the ticket and re-files it: `factory resolve <id> --close` and `factory ticket new`. The factory never restarts by itself. This is a standing decision.
2026-10-09 T-0027 An amendment changes no ticket state. The operator resumes the ticket with the routes that exist. Rejected: an amendment that also moves the ticket, which would duplicate those routes.
2026-10-09 T-0027 `spec amend` refuses while any run is in flight on the parent or one of its sub-tickets. A parked or waiting sub-ticket does not block it. Rejected: refusing while any sub-ticket is unmerged, which would block the motivating case of a sub-ticket parked BLOCKED on a scenario it cannot pass. This is a standing decision.
2026-10-09 T-0027 Human-only means that no workflow script and no role prompt names the command. A role run on the parent or a sub-ticket is in flight while it runs, so the in-flight refusal stops it. There is no identity check, because the harness runs under one identity.
2026-10-09 T-0027 `spec amend` refuses, with exit 2 and nothing written, in these cases: a sub-ticket; a ticket with no approved version; a ticket at `awaiting-spec-gate`, where `approve-spec --edit` is the route; a closed ticket; a reason that is not one non-blank line; and, with a spec store, a ticket whose change folder is gone because it was archived. An amended version must pass the gate's own checks: it is well-formed, and its deltas apply to current truth.
2026-10-09 T-0027 The re-pin keeps the planner's `tasks.md` in the change folder. The rest of the folder is rewritten as the gate writes it.
2026-10-09 T-0027 Each sub-ticket that is neither merged nor closed has its spec record moved to the new version, so later runs record the version they received. Its `planned_from`, the version its plan was made from, does not change, so an amendment never supersedes a plan.
2026-10-09 T-0027 The record is `approvals/<parent>/amendment-<n>.md`, numbered after any amendment file already there. It holds who, when, the reason, `Intent: unchanged`, the old and new version, and one line per scenario that differs: `- changed: <name>`, `- added: <name>` or `- removed: <name>`. It also holds a `- <id> / <title>: merged` line per sub-ticket merged before the amendment, and the unified diff. The log gets a `spec.amended` event. The amendment record is that version's approval record; no gate approval file is written.
2026-10-09 T-0027 Every spec version records the integration branch's head when it was stored, in `specs/<id>/v<n>.yaml`; that covers `spec add`, a gate edit and `spec amend`. Drift is counted from the record of the parent's approved version. Rejected: counting from the pin, because T-0032.1's test arrived between writing and pinning. A version stored before this change has no record, so its sub-tickets get only the sibling rule.
2026-10-09 T-0027 The drift check runs at `run start` of a sub-ticket's implementer, before the sibling-tests check. It runs only while the sub-ticket has no implementer run and no ruling on file. On drift it refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build already parks any `BLOCKED ` refusal with it as the reason. The human then amends the spec, rules, or both, and `resolve --ruling` returns the sub-ticket; the ruling also stops the check from repeating. Rejected: a new SPEC-DRIFT park status, as issue #50 proposed, which needs a new `resolve` route.
2026-10-09 T-0027 Sibling rule: drift when the sub-ticket's Acceptance field names, by id or by plan label, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. This is a standing decision.
2026-10-09 T-0027 Test rule: drift for each test file changed on the integration branch since the version's recorded head, by a first-parent commit that also changed a file the spec's design part names, and that neither the spec's Tests to change nor the sub-ticket's Tests to change lists. A test file's name starts with `test_`, or ends `_test.<ext>`, or contains `.test.`. Named files are the design part's backticked paths that exist at the integration head, except test files and `.md` documents, which every ticket here edits. This approximates "pins behaviour the spec changes": measured above, it catches 9 of 10 known incidents and would park about half the sub-tickets. Rejected: running each NEW scenario at build start and comparing it with the spec's "fails today" output (issue #50, part D). That output is prose, not something a program can compare. Rejected: a judge run per sub-ticket, which needs a new role and route.
2026-10-09 T-0027 The critic's input gains a section, `## Approved changes not yet archived`. It lists each change folder whose ticket is neither closed nor back in the spec loop (`ready-for-spec-writer`, `ready-for-critic`, `awaiting-spec-gate`), other than the reviewed ticket's own. Each entry gives the ticket id, title, state, folder path, the requirements its deltas add, modify or remove, and its Decisions lines. The section reads `none` when the list is empty, and is left out when the store has no spec store. Rejected: whole proposals, which would multiply the critic's input.
2026-10-09 T-0027 The cross-ticket rule extends the critic's rubric item 5 (Consistent). A scenario whose setup would not hold under one of the two merge orders is a BLOCKING finding that names the other ticket and its decision. This is a standing decision.
2026-10-09 T-0031 The wrapper fully deactivates an inherited virtual environment. It removes the exact entry `$VIRTUAL_ENV/bin` from `PATH`, then unsets `VIRTUAL_ENV` and `PYTHONHOME`, all before it sets HOME. Rejected: unsetting only the two variables, as the requester proposed. The activating shell also put the environment's `bin/` first on `PATH`, so a bare `python` or `pytest` would still run the other repository's environment (Evidence).
2026-10-09 T-0031 The deactivation is built into the wrapper for every instance, not configured per instance. Rejected: a way to unset variables through `run_env`. Every instance needs the deactivation, and opting in would leave it off by default. `run_env` is the list of variables an instance gives the wrapper to export after the throwaway HOME. Its exports still come after the deactivation, so an instance that wants a particular environment can still name it there.
2026-10-09 T-0031 `environment_sync` is one optional shell command, given as a string in `instance.yaml`. If it is absent or null, nothing runs, as today. Any other non-string or empty value is refused at run start, before any checkout is made.
2026-10-09 T-0031 The sync runs at every build-role run start, for the implementer, reviewer and verifier, including the verifier that checks the parent ticket after all its sub-tickets merge. It runs in that run's checkout, after the environment files are copied, through the same wrapper as role commands, so it gets the throwaway HOME, the `run_env` exports and no inherited environment. Rejected: syncing only when the implementer's worktree is first created. The environment files are copied again at every run start. A conflict run, which is an implementer run after the merge step refused the branch, merges in the integration branch, the branch that finished tickets merge into. Either can change the lock file the environment was built from. The reviewer is synced too, although it no longer runs the gate commands: its prompt still lets it run one test to confirm a finding (Evidence).
2026-10-09 T-0031 Changed from version 2: a failed sync refuses the run start with exit 2 and a one-line error, `environment_sync failed (exit <code>) in <checkout>; its command and output are in <log>`. The log is `runs/<id>/environment-sync.log`, in the run directory that run start had already reserved. It holds the command, the exit code and the command's full output. The error carries neither the command nor its output. No run is recorded or put in flight, and a checker checkout made for the run is removed. The implementer's worktree is kept for the next dispatch. The build workflow, the script that dispatches the build roles in turn, then parks the ticket: it stops the ticket and leaves it for a human. It uses its existing park reason `harness-bug: run start <role>: …`, so a broken environment never reaches a checker as a code failure. Rejected: version 2's error with the command and its last 20 output lines. The workflow passes the reason to the shell in double quotes, which expand the backticks that uv's errors contain, and the command is the operator's free text (Evidence). Rejected: starting the role anyway with a note. The role would then rediscover the broken environment, which is the cost this change removes.
2026-10-09 T-0031 When the sync ran, the run's record file, `meta.yaml`, stores the command under `environment_sync`. Changed from version 2: the role's input gains one line at the end of its "Where you work" section, after any SKIPPED lines. The line says the command ran, the environment is already synced, and the role should not sync again unless its change alters the files the environment is built from. Rejected: version 2's "after the gate-commands line", which the reviewer's input no longer has (Evidence).
2026-10-09 T-0031 This change sets `environment_sync` on neither instance. The operator sets it after the runtime, the separate checkout the factory runs from, has moved to the new harness revision (Operator steps). Rejected: setting it on this instance in the PR. That writes the protected `.factory/**`, and the key has no effect until the runtime runs the new harness anyway.
2026-10-10 T-0040 The driver is a harness subcommand, `factory drive TICKET [--phase intake|build] [--parallel N] [--prompt-mode append|replace]`, in a new module `factory/drive.py`, run as its own foreground process. A runner session may start it in the background. Rejected: running it inside the Workflow tool, which is the limit this change removes.
2026-10-10 T-0040 Store calls go through the CLI's own entry point, `factory.cli.main(argv)`, in the driver's process, with stdout and stderr captured, one call at a time on the driver's main thread. Every guard, refusal, fence check and lock check runs exactly as for `bin/factory`. Rejected: a `bin/factory` subprocess per call, which the requester ruled out. Rejected: calling store functions below `main`, which would skip the fence and the lock.
2026-10-10 T-0040 `factory drive` is a write command like any other, so the fence and the lock apply when it starts. Under the standing 2026-10-04 T-0024 decision, a runner that starts it while any run is in flight on the target puts `FACTORY_DISPATCH=1` in front of it. Once started, the driver marks its own store calls whether or not it was started marked. Its role processes never inherit the marker. Rejected: exempting `drive` from the fence, which would change the current-truth requirement that every unmarked write is refused while a run is in flight.
2026-10-10 T-0040 Each role runs as `claude -p <prompt> --model <models[role]> --output-format json --permission-mode auto --append-system-prompt-file <run>/system-prompt.txt --tools <list> --allowedTools <list>`, plus `--add-dir <worktree>` for the implementer and `--effort <level>` when the instance sets one. The process runs from the run directory with stdin closed. The `-p` prompt is the fixed text that names the run's input and output files and nothing else. That also removes the operator's chat message from every role's task (#28, absorbed).
2026-10-10 T-0040 `--permission-mode auto` with explicit allowlists: the classifier keeps checking each call that no rule allows, as it does for role agents today. Rejected: `dontAsk`. It is strict (Evidence), but it removes the classifier while roles run with no operating-system isolation (#37); operator ruling, 2026-10-09, to revisit once #37 lands. Build spec row R6's "nor `dontAsk`" therefore stays. Rejected: `bypassPermissions`, which R6 rightly forbids.
2026-10-10 T-0040 Tool limits. `--tools` is `Read,Grep,Glob,Bash,Write,WebFetch,WebSearch` for every role, and the implementer's list adds `Edit`. `--allowedTools` is `Read,Grep,Glob,Bash,WebFetch,WebSearch` plus three `Edit` rules on absolute real paths: `Edit(/<run>/output.md)`, `Edit(/<run>/scratch/**)` and `Edit(/<temporary directory>/**)`. The implementer's list adds `Edit(/<worktree>/**)`. The checkers therefore cannot use a file tool on the checkout under their run directory, which is the limit #24 part A wanted, absorbed. Bash stays unrestricted, so these limits cover the file tools only (Risk). Web tools are kept because role agents have them today. Every other tool the session offers today, such as sub-agents, task lists and notebook edits, is withheld: no role prompt in `factory/prompts/` asks for one. Rejected: withholding `Write` from the checkers, who must write `output.md`.
2026-10-10 T-0040 `--append-system-prompt-file` is the default. `--prompt-mode replace` passes `--system-prompt-file` instead, so the operator can measure the difference on a real ticket (Operator step 3). Rejected: deciding by measurement in this spec, which needs real model runs.
2026-10-10 T-0040 No `--bare`: it needs an API key and does not use the operator's subscription.
2026-10-10 T-0040 Effort per role comes from an optional `effort:` map in `instance.yaml`, keyed by role. An absent role gets no `--effort` flag. Values are passed through unchecked: Claude Code rejects a bad value before the run starts, which the driver records as a failed call. Neither instance sets `effort` in this change (Operator step 4). Per-role effort (#22) is absorbed.
2026-10-10 T-0040 A role process's reply is kept whole, as printed, in `runs/<id>/reply.json`. `run finish` gains `--reply FILE`, which records `session_id`, `total_cost_usd`, `num_turns` and `usage` under a `claude:` key in the run's `meta.yaml`. The reply's `result` text is not copied into `meta.yaml`, because it repeats `output.md`. This departs from the request's wording, which listed `result` too.
2026-10-10 T-0040 A failed call is a role process that exits non-zero or prints no JSON object on stdout. It is treated as a thrown `agent()` call is today: `run finish --status-override KILLED`, then a cleanup of a checker's checkout, then a park with `agent call failed: <role>: <message>`, and no retry. The message is the reply's `result` when there is one, else the last non-blank line of stderr, else `exit <code>`. A process that exits 0 with `is_error` set is routed on its output file like any other.
2026-10-10 T-0040 The two checkers run as concurrent processes, and both finish and record their results before the join, as `parallel()` does today. Ready sub-tickets build concurrently up to `--parallel N`, default 2. Rejected: unbounded, as `build.js` runs today, while concurrent `claude -p` processes are untested (Operator step 2).
2026-10-10 T-0040 On SIGINT or SIGTERM the driver sends SIGTERM to each role process it started. It sends SIGKILL to any still running 10 seconds later. It finishes each of its in-flight runs with `--status-override KILLED`, and runs a checker's cleanup. It parks nothing. It writes the stop to its status file, prints `{"ok": false, "ticket": "<id>", "stopped": "SIGINT"|"SIGTERM"}` as its last line and exits with 128 plus the signal number. Running `factory drive` again resumes from the stored state, as re-running a script does today. Rejected: parking on a stop, because a human stop is not a pipeline failure.
2026-10-10 T-0040 Without `--phase`, the phase follows the stored state. `ready-for-triage`, `ready-for-spec-writer` and `ready-for-critic` are intake. `ready-for-planner`, `planned` and `ready-for-parent-verify` are build. Any other state ends at once with "nothing to dispatch", as the scripts do. The driver never crosses the spec gate.
2026-10-10 T-0040 Progress output: one stdout line per step, `<ticket id> "<ticket title>": <step>`, where the ticket is the one the step concerns. A build step on a sub-ticket names the sub-ticket and its title (#47, absorbed). The last stdout line is one JSON object, the result the matching script returns, with `"ok": true` added. The status file is `drive/<parent id>.yaml` in the store, with keys `ticket`, `title`, `phase`, `pid`, `started`, `updated`, `running` (a list of `{run, role, ticket, pid}`), `last` (the last step line) and `ended` (null while running, then the result object). Rejected: changing `ticket show`, which `factory report` (#17) is meant to cover.
2026-10-10 T-0040 The status file is never committed. Part A appends `drive/` to the store's `.gitignore` block, under its own comment line, as `runs/*/tripwire.yaml` is. The file is a live view of one driver process: its `pid`, `updated` time and `running` list change at every step, and what lasts (each run's status, reply and cost, the ticket's state) is already in the run and ticket records. Rejected: committing it, which adds a churning file to every store commit. Rejected: a `drive/.gitignore` that ignores its own directory, which would put a second list of never-committed paths beside the store's block.
2026-10-10 T-0040 The driver has no stub mode. Tests put a stand-in `claude` first on `PATH`. Rejected: porting the scripts' `stubs` argument, whose stub agent needs Claude Code.
2026-10-10 T-0040 Park reasons and log events are the same as the scripts produce, so the parity scenarios compare records byte for byte, apart from ids, times and the order of the two checkers.
2026-10-10 T-0040 Retiring the scripts (the request's part F) is a separate ticket. A sub-ticket of this spec cannot wait for the operator's real runs, so the build would retire the scripts before the driver had run a real ticket.
2026-10-10 T-0040 The suite tests use a Python stand-in `claude`, so the suite needs nothing new. The acceptance scenarios also run the scripts under node, side by side with the driver, as earlier tickets' scenarios do.
2026-10-10 T-0040 The change is NEEDS-SPLIT, in three lettered parts (design.md).
2026-10-11 T-0041 1 (which commits are not drift): the test rule skips a first-parent commit that is the recorded merge (`merge.main_after`) of any merged sub-ticket of the same parent, from the current plan or an earlier one. Rejected: only the current plan's siblings. An earlier plan's merged sub-ticket is also this parent's own work, and the sibling-tests check already counts it the same way.
2026-10-11 T-0041 2 (later commits still count): only the sibling's exact merge commit is skipped, never merge commits in general. A later direct commit or merge from anywhere else that changes a test beside a design-named file is still drift, and the refusal names that commit.
2026-10-11 T-0041 3 (the resolve route): `resolve <id> --ruling F` also accepts a park whose reason starts `harness-bug: run start implementer:` and that was parked from `ready-for-implementer`. It writes F as the next ruling and returns the sub-ticket to `ready-for-implementer` at the same round, as a ruling on a `BLOCKED` park does. As with any ruling on file, the drift check does not run again for that sub-ticket. Rejected: widening `--redispatch` to this park. `--redispatch` re-runs the checkers today, and with no ruling on file a drift refusal would park the sub-ticket again. Rejected: accepting every harness-bug park from `ready-for-implementer`. A failed `run compose` leaves its run in flight, so the next run start would be refused again.
2026-10-11 T-0041 4 (refusal text): `--ruling` on any other park is refused with `--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an implementer's run start; <id> is <state> (<reason or 'no park'>)`, so the operator sees the new case.
2026-10-11 T-0042 The dispatcher (factory drive, and any later runner command) is exempt from the live-store fence's in-flight check, keeps the runs/ and worktrees/ refusal, and carries its own same-ticket guard (refuse while the ticket or a sub-ticket has a run in flight, or a live driver is recorded); overturns T-0040's rejection (operator, 2026-10-11, T-0042)
2026-10-11 T-0042 `factory drive` skips the fence's in-flight rule and keeps its location rule, which refuses a caller under the own store's `runs/` or `worktrees/`, marked or not. This is the operator's answer of 2026-10-11 (option A). It overturns T-0040's 2026-10-10 rejection of exempting `drive`. It is standing for every later runner command: the dispatcher is exempt from the in-flight rule and carries its own same-ticket guard.
2026-10-11 T-0042 `factory drive` given `--accept-harness` is fenced in full, in-flight rule included, because an acceptance rewrites the harness lock. This keeps the standing 2026-10-04 T-0024 rule that any command given `--accept-harness` is a write.
2026-10-11 T-0042 The same-ticket guard refuses `drive T`, with exit 2 and nothing written, in two cases. The first is when T or any of its sub-tickets has a run in flight. The second is when `drive/T.yaml` exists, has no `ended` value, and its `pid` is a live process. These are the operator's terms of 2026-10-11.
2026-10-11 T-0042 The guard runs whether or not the caller carries the marker, and on any store, a throwaway store included. Rejected: applying it only on an own store, as the fence is. The guard protects a ticket's records from two drivers, which matters on any store.
2026-10-11 T-0042 The guard runs inside the `drive` command, after the fence and the harness lock and before the driver sets its marker or writes its status file. A missing ticket skips the guard, so the existing "no such ticket" result is unchanged.
2026-10-11 T-0042 A pid counts as live when signal 0 reaches it, or is refused for permission. A missing, non-integer or dead pid does not block. A dead pid not blocking is the operator's term.
2026-10-11 T-0042 Rejected: checking that a live pid is a `factory drive` process. That would add a platform-dependent process query for a rare case, a pid reused after a SIGKILLed driver. The refusal names the pid and the status file instead, and README tells the operator to delete that file when the pid is not a driver.
2026-10-11 T-0042 The refusals read `<T> has runs in flight on it or its sub-tickets: <run ids>; drive it again once they finish` and `<T> is already being driven by pid <n> (<status file>); stop that driver or wait for it to end`. Neither names the marker, as the standing 2026-10-04 T-0024 decision requires of the fence's refusal.
2026-10-11 T-0042 README's driver step that told the operator to type the marker is removed. In its place README says why the driver needs no marker, and what it refuses instead. This is the operator's direction of 2026-10-11.
2026-10-12 T-0043 The command is `factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...`. - With no `--store`, it reads the store of the instance found from the caller's directory. As other commands do, it honours `FACTORY_STATE`, the environment variable that points a command at another store (tests use it to point at a throwaway one). With neither, it is refused with exit 2. A `--store` path with neither `runs/` nor `log/` is refused with exit 2.
2026-10-12 T-0043 `--until` is added beyond the request, so that a past figure can be reproduced on a store that keeps growing. - WHEN is an ISO date or date-time, taken as UTC when it has no zone. `--since` is inclusive and `--until` exclusive. - Runs are windowed by `started` and events by `ts`. Looking up who wrote and who critiqued a spec ignores the window.
2026-10-12 T-0043 The output is Markdown with fixed section headings and column orders, given in design.md part B. Rejected: JSON (Out of scope).
2026-10-12 T-0043 `stats` is handled like `paths`: no instance needed, no live-store fence (the guard against role runs writing the store), no harness lock check, and `--accept-harness` ignored. - Why: it writes nothing, and it must read a live store while runs are in flight and from a checkout the instance has not accepted, such as a verifier's. - The fence's read-only list in the documents gains `stats`. This follows the standing 2026-10-04 rule that a new command is fenced until it is added to that list. - Rejected: adding it only to `READ_ONLY`, as triage assumed. The lock would still refuse it everywhere but the accepted runtime.
2026-10-12 T-0043 The rows are keyed by role and model, summed over every store given, and ordered triage, spec_writer, critic, planner, implementer, reviewer, verifier, then any other role by name, and models by name within a role.
2026-10-12 T-0043 A row's "runs" counts runs with a verdict other than `KILLED`. `KILLED` runs have their own column, and runs still in flight (status `running` or none) are left out. This is how the request counted (94 reviewer runs plus 5 killed).
2026-10-12 T-0043 A changed outcome is a verdict of `REQUEST-CHANGES`, `ESCALATE`, `FAILED`, `SPEC-DEFECT`, `REVISE` or `BLOCKED`, from any role. This is the request's list.
2026-10-12 T-0043 BLOCKING findings are counted for the reviewer and the critic only. A finding is a line of `output.md` that starts with `[BLOCKING]`, after optional leading spaces and an optional `-`, `*` or `1.` marker, and that does not contain `RESOLVED`. - Rejected: counting every mention of the word, which counts "No BLOCKING findings". - Rejected: counting round-2 restatements of a fixed finding.
2026-10-12 T-0043 Park reasons are normalised by a fixed list in the module, extended when a new reason appears. The steps are: 1. take the first line; 2. replace run ids with `<run>`, ticket ids with `<ticket>`, and 7-to-40-character hex strings that contain a letter with `<sha>`; 3. keep the first two `: `-separated fields; 4. trim, and drop a trailing colon.
2026-10-12 T-0043 A park counts under its corrected reason. A `park.corrected` event replaces the reason of the latest earlier `ticket.parked` event of the same ticket whose reason equals the correction's `previous`. A correction that matches no park changes nothing. - Only corrections dated before `--until` apply, so a past figure stays repeatable after a later correction. The park itself is windowed by its own `ts`. - Why: the operator corrects a reason because the recorded one was wrong, as on T-0040.3, where a refusal was mis-filed as a harness bug. Counting the original would report the error the human fixed. - Rejected: ignoring corrections. Rejected: applying every correction whatever its date, which lets a later correction move a figure quoted for a past cut.
2026-10-12 T-0043 Section B's decision rows are: - `spec approved`: `approval.recorded` events with `kind: spec`; - `spec changes requested`: `human.resolved` events with `kind: request-changes`; - one `resolved: <kind>` row per other `human.resolved` kind; - one `merge refused: <reason>` row per `merge.refused` reason (`head does not contain main` is the conflict case); - `archive refused`: parks whose normalised reason is `archive` or starts with `archive:`.
2026-10-12 T-0043 Section C is built as follows: - Each catch is a verifier run with `SPEC-DEFECT` or an implementer run with `BLOCKED`. - Its spec is the parent ticket's (the ticket id without a trailing `.N`) at the run's `spec_version`. - "Written by" is that version's `spec.added` source when the source is a run id. It is `human` when the source is anything else (a gate edit or an amendment), and `unknown` when the version has no `spec.added` event. - "Critiqued by" is the latest critic run of the parent at that `spec_version`, or `none`. - The REVISE count is all critic REVISE runs of the parent. - A second table splits approved tickets by whether they had a REVISE and counts those with a later catch. This answers the REVISE question with no further tool.
2026-10-12 T-0043 Cost per run comes from the run's cost record (`claude.usage`, `claude.total_cost_usd`) when present, else from its transcript, else nothing. Each row names how many runs used each source. This is the owner's proposal. - Context tokens are input + cache-read + cache-creation tokens, the definition `factory/cost.py` already uses. - Dollars come only from cost records, because transcripts carry none. - Killed runs count, because they spent tokens.
2026-10-12 T-0043 Transcripts are searched only under the `--transcripts` directories, for every `*.jsonl` file at any depth. - Rejected: searching `~/.claude/projects` by default. That ties the command to one machine's layout and costs about 12 seconds on every call.
2026-10-12 T-0043 A transcript is matched to a run R of a store S as follows: - Its first user message that names a run directory, `<P>/runs/<R>/`, gives the candidate. A user message is skipped when it starts with `[Workflow harness — user request]`, which relays the operator's words. - The transcript's first timestamp must lie between R's `started` and `finished`. - A P that is the path of another store given on the command line rules the transcript out. - A candidate whose P is S's path, or S's path before a `store.migrated` event, wins. Otherwise a single remaining candidate is taken. Otherwise there is none. - Rejected: requiring S's path. That loses every run from before an unrecorded move (this store's first 103).
2026-10-12 T-0043 Usage counts each message id once, taking its last record. A record with no id counts alone. The `calls` column of `factory/cost.py` then counts message ids. This fix applies to `factory/cost.py` itself and absorbs issue #61, the report of the double count.
2026-10-12 T-0043 Implementer gate failures fixed before hand-off are read from the transcript. - The gate commands are the backticked commands on the "Gate commands" line of the run's `input.md`. Each is matched by its own text: what follows the wrapper's last `; `, with the closing `)` removed. - A gate counts once per run when a Bash call containing it returned an error (`is_error: true`) and a later call returned none. - A run with no transcript or no gate line is "not recorded", not zero. - Rejected: the implementer's output, which states only the final results. - The text match can miss a command the implementer ran in another form. That is a known limit, stated in README.
2026-10-12 T-0043 `docs/design.md`'s model-per-role paragraph cites `factory stats` and the reviewer, critic, verifier and implementer figures from sections A and D, for `--until 2026-10-07T12:00` with `--transcripts`. This is part E of the request. Its retro half moves to the retro's own issue, #42 (Out of scope).
2026-10-12 T-0043 `docs/principles.md` §4 gets the command's figure, 3 BLOCKING findings, in place of 1 (Evidence), and its "Implemented by" line names `factory stats`.
2026-10-12 T-0044 Every change must add or change at least one requirement in the spec store, the folder of requirement files that says what the harness does. That folder holds one file per capability, a named area of behaviour. For example, build-dispatch covers how role runs are started and routed. The store refuses a change with no such addition (`factory/specstore.py:202`: "no delta part"). Triage, the first role, which accepts the request, named no capability, because nothing here changes behaviour. This change therefore adds a new capability, `harness-code`, to hold the checks that the removed code stays gone. It also adds to build-dispatch one requirement that pins the in-flight refusal this change merges, since no existing requirement covers it. Rejected: putting the removal checks in build-dispatch, which describes how runs are started, not what the source contains.
2026-10-12 T-0044 `gitops.repo_root` keeps its name and loses its parameter. All 12 callers become `gitops.repo_root()`. Rejected: deleting the wrapper and calling `instance.repo_root()`, which would also move imports in `compose.py` and `gitops.py` for no gain.
2026-10-12 T-0044 Of the two writes of the store's `.gitignore` block when a build role starts, the one inside the build-role setup function `_start_build_run` (`cli.py:377`) goes. The call at `:229` covers every role. Rejected: removing `:229`, which would leave triage, spec writer, critic and planner runs without the write.
2026-10-12 T-0044 The two in-flight refusals become one condition over the five roles, written as an explicit list: `("triage", "spec_writer", "critic", "planner", "implementer")`. Rejected: `a.role not in ("reviewer", "verifier")`, which would silently cover a role added later.
2026-10-12 T-0044 The refusal in compose, the step that writes a run's input file, keeps its place at `compose.py:420` and changes its text to `compose: unknown role {role}`. Rejected: deleting that branch, because a hand-edited run record would then get an empty input and no error.
2026-10-12 T-0044 The store module's docstring keeps only its first line. Rejected: keeping "Every write goes through here", a claim this ticket did not verify.
2026-10-12 T-0044 The design documents that still describe `force_push_allowed` stay as they are, and the gap is recorded here. Changing `docs/design.md` would need a changelog entry and a re-copied `docs/prompts/05-implementer.md`, and prompts are out of this round. In practice the setting has done nothing since the shipped prompt hardcoded "never rebase".
2026-10-12 T-0044 A change to factory/**, bin/factory, agents/**, pyproject.toml or uv.lock touches the protected class harness and must declare it on the spec's Protected paths line; T-0044 wrote 'none' and its merge was refused (operator accepted with resolve --accept-paths, 2026-10-11)

## Approved changes not yet archived

### T-0045: De-bloat B: one shared helper module for the harness tests, shared fixture helpers, and the duplicate test removed (planned)
Change folder: `/Users/dphang/dev/spec-factory/.factory/store/openspec/changes/T-0045`
Changes: harness-suite: ADDED Test files share code only through helper modules; harness-suite: ADDED Each shared test helper is written once; harness-suite: ADDED The refactor keeps every test and assertion but the one duplicate; harness-suite: ADDED A suite run writes nothing into the checkout
Decisions:
- Test files never import from another test file. Shared code lives in two non-test modules. `tests/factory/_cli.py` holds the generic helpers: constants, wrappers, the JSON readers, the ticket reader and the two setups. `tests/factory/_fixtures.py` holds the scenario fixtures that more than one test file uses. Standing: a later ticket that needs a helper in a second file moves it to one of these two modules. Rejected: one module for everything, which would put the 190-line fixture in `test_shepherd.py` that drives a ticket through a whole build beside eight-line wrappers. Also rejected: `conftest.py` fixtures, whose names apply to every file, while four files define their own `target`.
- The JSON reader comes in two forms. `js` only parses. `js_ok` asserts exit 0 and then parses. Each file imports the form its own copy had, under the name `js`, so no call site changes and the exit check stays opt-in per caller. Rejected: a `check=` argument at each call, which touches every call site.
- `conftest.py` sets both `PYTHONDONTWRITEBYTECODE=1` in the environment and `sys.dont_write_bytecode = True`. Rejected: adding `env=` at each Python start, the request's suggestion. It misses the two in-process loads, as the prototype showed.
- The check that nothing is written into the checkout leaves out `tests/factory/__pycache__`. pytest writes two files there before `conftest.py` can act. Only the person running pytest can stop that.
- The removed test is `test_p0_cli.py`'s KILLED-override test. The test in `test_empty_output.py` keeps all three of its checks.
- The approved-parent helper takes a caller's `ok` function, the ticket id and a spec file. It runs the five calls and returns the ticket id. Ticket creation stays with the caller. Sites that use `spec add --from-run`, assert a step, or put other work between steps keep their own calls. Cut: the request's `plan` argument. A plan is not part of the repeated five calls.
- The class-level `cli`/`ok` pair comes from one base class. Each class still builds its own environment, so the instance copy, the venv and the PATH stand-in stay where they are. A class whose `cli` differs overrides `cli` only.
- The acceptance checks name helper names (`REPO`, `js`, and so on) and the one test this change removes. The subject of this ticket is the suite's own structure, so those names are the behaviour being checked.
- Changed in round 2: the checks that compare with a base compare across each of this ticket's own merges into `main` (each `Merge factory/T-0045.<n>` commit against its first parent), plus the unmerged commits of the checked-out branch (`git merge-base HEAD main` against `HEAD`), and add up the results. Other tickets' changes to the same files are therefore never counted, whichever order they merge in. Rejected: v1's single base, the commit before this ticket's first merge, which counts T-0044's two assertion changes if T-0044 merges in between (critic, round 1). Rejected: the critic's suggested THEN with a second outcome when T-0044 has merged. Three more de-bloat tickets in the same sweep (T-0046, T-0047, T-0048) edit the same files and would each need a clause of their own.
