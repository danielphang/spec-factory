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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0439-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0439-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0043.2` (branch `factory/T-0043.2`, base `a0f77c9ffdb638dfcb77ec1dde702a861e6796d4`, head `a0f77c9ffdb638dfcb77ec1dde702a861e6796d4`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0043.2

## ST-2 / Add `factory stats` and exempt it from the instance lookup, the live-store fence and the harness lock
Depends on: ST-1
Parallel-safe: no (depends on ST-1's functions; ST-3 depends on this command)

Parent: T-0043, spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B (`factory/stats.py`, a new file: `report()`, the module constants `CHANGED`, `BLOCKING` and `PARK_RULES`, and sections A to D in the spec's exact headings, column orders and row orders), part C (the `stats` subparser, `stats_cmd`, refusals that raise `Refused` and exit 2, handling `stats` before `instance.require()`, the fence and `instance.guard()` in `main()`, `("stats", None)` added to `READ_ONLY`, and the `fence()` and `main()` comments), and part D's `tests/factory/test_stats.py`. Every rule under the spec's Decisions applies here: store resolution and `FACTORY_STATE`, the window, the row order, the definition of runs and kills, changed outcomes, BLOCKING lines, park normalisation and corrections, section B's rows, section C's attribution, the cost source, and the transcript matching (through ST-1's `match_transcripts`, `transcript_usage` and `gate_failures`).

Acceptance (run each scenario's fixture GIVEN block once first, as the spec writes it; each WHEN runs in a subshell through the briefing's wrapper):
- NEW. "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures". WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --transcripts $F/tx --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## A\./,/^## B\./p' $F/out | grep '^| [a-z]' | grep -v '^| role |')` THEN it prints exactly the eight lines the spec gives, starting `exit=0` and ending `| verifier | opus | 1 | 0 | 1 | SPEC-DEFECT 1 | - | - |`.
- NEW. "A window bounds the count and the command writes nothing". WHEN the spec's command (`bin/factory stats --store $F/s1 --since 2026-10-03 --transcripts $F/tx` with the before-and-after `cksum` of `$F`) THEN it prints exactly `exit=0 store=unchanged since=1`.
- NEW. "Parks are grouped by normalised reason, with gate and merge decisions". WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## B\./,/^## C\./p' $F/out | grep '^| ' | grep -vE '^\| (park reason|gate or merge decision) \|')` THEN it prints exactly the seventeen lines the spec gives, from `exit=0` through `| archive refused | 2 |`.
- NEW. "Each downstream spec catch names the runs that wrote and critiqued its spec". WHEN the spec's section C command THEN it prints exactly `exit=0`, `| run-0007-implementer | BLOCKED | T-0001.1 | 2 | run-0005-spec_writer | run-0006-critic | 1 |`, `| run-0011-verifier | SPEC-DEFECT | T-0001.1 | 3 | human | none | 1 |`, `| yes | 1 | 1 |`, `| no | 1 | 0 |`.
- NEW. "Cost comes from the run record, else the transcript of that store's run, counted once per call". WHEN the spec's section D command (with `--transcripts $F/tx --until 2026-10-08`) THEN it prints exactly the eight lines the spec gives, from `exit=0` through `| verifier | opus | 1 | 120 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |`.
- NEW. "Stats reproduces the hand count on the two live stores". WHEN `(bin/factory stats --store /Users/dphang/dev/spec-factory/.factory/store --store /Users/dphang/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 > ${TMPDIR:-/tmp}/t0043-live.txt 2>&1; echo "exit=$?"; ...)` as the spec writes it THEN it prints exactly the eight lines the spec gives, from `exit=0` through `| all parks | 82 |`. This reads both live stores and writes only under the temporary directory. A mismatch is checked against the stores first, as the scenario says.
- NEW. "Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing". GIVEN live-store-guard's `t0024-inflight.sh` block, run once. WHEN the spec's command (the lock overwritten to `0000…`, `stats` run from the target and from `$W`, then `ticket show`) THEN it prints exactly `here=0 inside=0 store=unchanged own=1 locked=2`.
- REGRESSION. "Unmarked writes from inside the target are refused while a run is in flight, init included". WHEN the spec's command THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`.
- REGRESSION. "The refusal names the throwaway store and not the marker". WHEN the spec's command THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`.
- REGRESSION. "A harness acceptance is refused while a run is in flight". WHEN the spec's command THEN it prints exactly `accept=2 store=unchanged`.
- REGRESSION (made true by ST-1). "The transcript cost report counts each message once": WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && .venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |')` THEN it prints exactly `| critic | fable-5 | 1 | 2 | 310 | 17 |`.
- NEW (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_stats.py` THEN it passes. The file covers what part D lists for it: each section's rows on a fixture like the acceptance fixture; the window; each normalisation rule; the correction rule (a matching correction, one dated after `--until`, one whose `previous` matches no park); the refusals (no store found, a path with neither `runs/` nor `log/`, an unparsable WHEN); and a run on an instance's own store with a run in flight, from inside the store's `runs/`, under a lock that names another revision, built the way `tests/factory/test_live_store_guard.py` builds one.
- REGRESSION (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory` THEN the whole suite passes, `tests/factory/test_cost_once.py` from ST-1 included.

Interim tests: none
Tests to change: none
Protected paths: `factory/cli.py`, `factory/stats.py`
Out of scope: any change to `factory/cost.py` beyond calling ST-1's functions. If one of them has to change, report it as a gap rather than editing it here. Also out of scope: every document (README, `docs/design.md`, `docs/principles.md`, `dev/build-harness.spec.md`, `docs/changelog.md`), which ST-3 changes; a JSON output; the fence and lock behaviour of every other command; and the loose wording of live-store-guard's second requirement (the spec's Out-of-scope observations). README will not mention `stats` until ST-3 merges. The spec's split puts that page change in ST-3.

---

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v2) already names its three seams (design.md, "Proposed change": ST-1 is part A, ST-2 is parts B and C, ST-3 is part E, with part D's tests split between them). This plan follows those seams and does not split further: each one is a single reviewable change, and a fourth would only add a re-verify cycle. The three run in a chain, because each needs the previous one's code or output.

Checked on this checkout (`main` at `5215c5f`, the revision verification.md was captured on): `factory/cost.py` exists and has `tally()` at line 47 and no `transcript_usage`, `match_transcripts` or `gate_failures`; `factory/cli.py` has `build_parser()` at line 1753, `READ_ONLY` at line 1939, `main()` at line 1969 and no `"stats"`; `factory/stats.py`, `tests/factory/test_cost_once.py` and `tests/factory/test_stats.py` do not exist; `tests/factory/test_live_store_guard.py` exists; no file under `tests/factory/` mentions `factory.cost`, `tally` or `READ_ONLY`; and the log shows no earlier plan or sub-ticket for T-0043.

---

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`

=== proposal.md
## Problem

The operator cannot see which of the factory's checks pay for themselves, or what each one costs. The records that would show it are already kept, but nothing reads them as a whole, and the one cost report the factory has counts most tokens about twice.

Some terms. The factory turns a written request into merged code through a chain of AI agents. Each request is a ticket. Each step on a ticket is a role run: one agent doing one job, such as triage (accepting the request), writing the spec (the design the code must meet), critiquing the spec, implementing it, reviewing the code or verifying it by running its checks. Every run ends with a verdict on a `STATUS:` line. Some verdicts change what happens next: the critic's REVISE sends a spec back, the code reviewer's REQUEST-CHANGES sends code back, the verifier's SPEC-DEFECT or FAILED stops a merge, and the implementer's BLOCKED says the spec cannot be built as written. A finding marked BLOCKING is one the critic or reviewer says must be fixed. A park sets a ticket aside for a human, with a one-line reason. The store is the factory's record for one target repository, kept as plain files: each run's record (its role, model, verdict and wall time), each run's output, and an append-only event log. Since 2026-10-10 a run started by `factory drive` (the command that runs a ticket's roles one after another) also records its token use and dollar cost. Earlier runs have that only in their transcript, the log file Claude Code keeps for each agent session outside the store.

Counting these records takes a hand-written script today. One such count over both stores, made on 2026-10-07, found that the code reviewer, which runs on the most expensive model, changed an outcome 4 times in 94 runs, and that 30 of 82 parks were triage asking a human. The operator decides from figures like these which model each role runs and whether a check is worth its cost. The design's model-per-role table says a change to it needs that evidence. The existing token report, `factory/cost.py`, counts most model calls about twice (1.9 times over both stores), because a transcript repeats one call's usage once for each block the reply streamed.

This change adds `factory stats`, a command that reads one or more stores, writes nothing, and prints four tables:
- runs and verdicts by role and model, with the verdicts that changed an outcome, BLOCKING findings, runs killed for running out of budget, and the check commands an implementer saw fail and then fixed before handing off;
- parks by reason, with the human decisions at the spec gate (where the operator approves a spec) and the merge refusals;
- each spec defect caught downstream, against the run that wrote that spec and the run that critiqued it;
- each role's wall time and tokens, taken from the run's cost record or else its transcript, counting each model call once.

It also fixes the double count in `factory/cost.py`. It serves the operator. It will also serve the retro, a planned role that proposes changes to the agents' rules from failure rates, which is built after this change and reads the same figures.

## Root cause

- No command reads the store as a whole. `factory/cli.py` `build_parser()` (lines 1753-1934) has no `stats` subparser.
- `factory/cost.py` `tally()` (lines 47-71) adds `usage` from every transcript record that has it. Claude Code writes one record for each streamed block of a reply, and each carries the whole call's usage, so a call is counted once per block.
- `factory/cli.py` `main()` (lines 1969-1985) puts every command except `init` and `paths` through the instance lookup, the fence and the harness lock.

## Out of scope

- Feeding these figures into the retro's input. The retro role does not exist yet. The operator decided on 2026-10-11 that the retro is built after this change and reads from it, so the request's "the retro's input.md contains the stats section" moves to that work (issue #42).
- The retro's prompt block in `docs/design.md` §8 and its copy `docs/prompts/08-retro.md`. The block already asks for per-role run and outcome counts by model, and no prompt file changes.
- Post-merge reverts. No store records them, and a revert event is a separate ticket if wanted.
- Acting on the figures: the reviewer trial (issue #64), detecting a stuck run, and a trained critic.
- A JSON output. Cut: no consumer needs one yet. The REVISE question (issue #94) is answered by a table this change prints, and the retro can call the module directly.
- Breaking BLOCKING findings down by rubric item, as the request's "14 of 16 were rubric 6" does. Cut: the command is not asked for it.
- Any change to what runs, records or the log store. Cost from transcripts that Claude Code has already deleted is reported as missing, not estimated.
- Every other command's place in the fence and the harness lock.

## Open questions

none

## Decisions

- The command is `factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...`.
  - With no `--store`, it reads the store of the instance found from the caller's directory. As other commands do, it honours `FACTORY_STATE`, the environment variable that points a command at another store (tests use it to point at a throwaway one). With neither, it is refused with exit 2. A `--store` path with neither `runs/` nor `log/` is refused with exit 2.
- `--until` is added beyond the request, so that a past figure can be reproduced on a store that keeps growing.
  - WHEN is an ISO date or date-time, taken as UTC when it has no zone. `--since` is inclusive and `--until` exclusive.
  - Runs are windowed by `started` and events by `ts`. Looking up who wrote and who critiqued a spec ignores the window.
- The output is Markdown with fixed section headings and column orders, given in design.md part B. Rejected: JSON (Out of scope).
- `stats` is handled like `paths`: no instance needed, no live-store fence (the guard against role runs writing the store), no harness lock check, and `--accept-harness` ignored.
  - Why: it writes nothing, and it must read a live store while runs are in flight and from a checkout the instance has not accepted, such as a verifier's.
  - The fence's read-only list in the documents gains `stats`. This follows the standing 2026-10-04 rule that a new command is fenced until it is added to that list.
  - Rejected: adding it only to `READ_ONLY`, as triage assumed. The lock would still refuse it everywhere but the accepted runtime.
- The rows are keyed by role and model, summed over every store given, and ordered triage, spec_writer, critic, planner, implementer, reviewer, verifier, then any other role by name, and models by name within a role.
- A row's "runs" counts runs with a verdict other than `KILLED`. `KILLED` runs have their own column, and runs still in flight (status `running` or none) are left out. This is how the request counted (94 reviewer runs plus 5 killed).
- A changed outcome is a verdict of `REQUEST-CHANGES`, `ESCALATE`, `FAILED`, `SPEC-DEFECT`, `REVISE` or `BLOCKED`, from any role. This is the request's list.
- BLOCKING findings are counted for the reviewer and the critic only. A finding is a line of `output.md` that starts with `[BLOCKING]`, after optional leading spaces and an optional `-`, `*` or `1.` marker, and that does not contain `RESOLVED`.
  - Rejected: counting every mention of the word, which counts "No BLOCKING findings".
  - Rejected: counting round-2 restatements of a fixed finding.
- Park reasons are normalised by a fixed list in the module, extended when a new reason appears. The steps are:
  1. take the first line;
  2. replace run ids with `<run>`, ticket ids with `<ticket>`, and 7-to-40-character hex strings that contain a letter with `<sha>`;
  3. keep the first two `: `-separated fields;
  4. trim, and drop a trailing colon.
- A park counts under its corrected reason. A `park.corrected` event replaces the reason of the latest earlier `ticket.parked` event of the same ticket whose reason equals the correction's `previous`. A correction that matches no park changes nothing.
  - Only corrections dated before `--until` apply, so a past figure stays repeatable after a later correction. The park itself is windowed by its own `ts`.
  - Why: the operator corrects a reason because the recorded one was wrong, as on T-0040.3, where a refusal was mis-filed as a harness bug. Counting the original would report the error the human fixed.
  - Rejected: ignoring corrections. Rejected: applying every correction whatever its date, which lets a later correction move a figure quoted for a past cut.
- Section B's decision rows are:
  - `spec approved`: `approval.recorded` events with `kind: spec`;
  - `spec changes requested`: `human.resolved` events with `kind: request-changes`;
  - one `resolved: <kind>` row per other `human.resolved` kind;
  - one `merge refused: <reason>` row per `merge.refused` reason (`head does not contain main` is the conflict case);
  - `archive refused`: parks whose normalised reason is `archive` or starts with `archive:`.
- Section C is built as follows:
  - Each catch is a verifier run with `SPEC-DEFECT` or an implementer run with `BLOCKED`.
  - Its spec is the parent ticket's (the ticket id without a trailing `.N`) at the run's `spec_version`.
  - "Written by" is that version's `spec.added` source when the source is a run id. It is `human` when the source is anything else (a gate edit or an amendment), and `unknown` when the version has no `spec.added` event.
  - "Critiqued by" is the latest critic run of the parent at that `spec_version`, or `none`.
  - The REVISE count is all critic REVISE runs of the parent.
  - A second table splits approved tickets by whether they had a REVISE and counts those with a later catch. This answers the REVISE question with no further tool.
- Cost per run comes from the run's cost record (`claude.usage`, `claude.total_cost_usd`) when present, else from its transcript, else nothing. Each row names how many runs used each source. This is the owner's proposal.
  - Context tokens are input + cache-read + cache-creation tokens, the definition `factory/cost.py` already uses.
  - Dollars come only from cost records, because transcripts carry none.
  - Killed runs count, because they spent tokens.
- Transcripts are searched only under the `--transcripts` directories, for every `*.jsonl` file at any depth.
  - Rejected: searching `~/.claude/projects` by default. That ties the command to one machine's layout and costs about 12 seconds on every call.
- A transcript is matched to a run R of a store S as follows:
  - Its first user message that names a run directory, `<P>/runs/<R>/`, gives the candidate. A user message is skipped when it starts with `[Workflow harness — user request]`, which relays the operator's words.
  - The transcript's first timestamp must lie between R's `started` and `finished`.
  - A P that is the path of another store given on the command line rules the transcript out.
  - A candidate whose P is S's path, or S's path before a `store.migrated` event, wins. Otherwise a single remaining candidate is taken. Otherwise there is none.
  - Rejected: requiring S's path. That loses every run from before an unrecorded move (this store's first 103).
- Usage counts each message id once, taking its last record. A record with no id counts alone. The `calls` column of `factory/cost.py` then counts message ids. This fix applies to `factory/cost.py` itself and absorbs issue #61, the report of the double count.
- Implementer gate failures fixed before hand-off are read from the transcript.
  - The gate commands are the backticked commands on the "Gate commands" line of the run's `input.md`. Each is matched by its own text: what follows the wrapper's last `; `, with the closing `)` removed.
  - A gate counts once per run when a Bash call containing it returned an error (`is_error: true`) and a later call returned none.
  - A run with no transcript or no gate line is "not recorded", not zero.
  - Rejected: the implementer's output, which states only the final results.
  - The text match can miss a command the implementer ran in another form. That is a known limit, stated in README.
- `docs/design.md`'s model-per-role paragraph cites `factory stats` and the reviewer, critic, verifier and implementer figures from sections A and D, for `--until 2026-10-07T12:00` with `--transcripts`. This is part E of the request. Its retro half moves to the retro's own issue, #42 (Out of scope).
- `docs/principles.md` §4 gets the command's figure, 3 BLOCKING findings, in place of 1 (Evidence), and its "Implemented by" line names `factory stats`.

## Risk

Blast radius:
- `factory/cost.py`'s output roughly halves for the same transcripts. Figures quoted from it before this change, such as changelog entries 58 and 67, stay as history and are not restated.
- `factory stats` runs under any harness revision and on a live store. A defect in it can print a wrong figure or fail, but it cannot write. The command opens files only for reading, and scenario "Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing" checks the store.
- A wrong park normalisation misleads the operator. The fixture's reasons cover each rule, and its two corrections cover the correction rule (one applied, one dated after `--until`).
- Every other command's fence and lock behaviour is unchanged. The three restated live-store-guard scenarios check that.

Protected paths: `factory/cli.py`, `factory/cost.py`, `factory/stats.py`

## Operator steps

none
=== design.md
## Proposed change

This is too large for one reviewable change (about 650 lines with tests and documents), so it is marked NEEDS-SPLIT. There are three seams:
- ST-1 is part A and its tests.
- ST-2 is parts B and C and their tests, and depends on ST-1.
- ST-3 is part E, and depends on ST-2.

Part D lists the tests of each. The acceptance scenarios split the same way:
- ST-1 owns "The transcript cost report counts each message once".
- ST-3 owns "The documents record factory stats".
- ST-2 owns every other scenario, the three restated live-store-guard scenarios included.

A. Transcript reading (`factory/cost.py`).
   - Count each message id once. Change `tally()` to keep, for each transcript, the last usage seen for each `message.id`, counting a record without an id on its own. Make `calls` the number of ids kept. Put this in a function `transcript_usage(path) -> (calls, ctx, out)`, which `tally()` and part B both use. Update the module docstring, which today says nothing of the double count.
   - Add `match_transcripts(dirs, stores) -> {(store, run_id): path}`, implementing the matching rule under Decisions. It reads at most the opening records of each file it needs to place: up to the first user message naming a run directory.
   - Add `gate_failures(transcript, input_md) -> int | None`, implementing the gate rule under Decisions. It returns None when the input has no "Gate commands" line.
   - `python -m factory.cost DIR...` keeps its interface and table, so `| role | model | agents | calls | ctx tokens | out tokens |` is unchanged.

B. The command (`factory/stats.py`, new). `report(stores, since, until, transcripts) -> str` builds the text below. A store is read from `runs/*/meta.yaml`, `runs/*/output.md`, `runs/*/input.md` and `log/*.jsonl`. Parse `started`, `finished` and `ts` whether YAML gives a string or a datetime. Keep the names `CHANGED`, `BLOCKING` and `PARK_RULES` (the normalisation list) as module constants. The output, in this order:
   - `# factory stats`, then `Stores: <absolute resolved path>[, <path>]...`, then a line naming the window and the number of runs left out as in flight.
   - `## A. Runs and verdicts by role and model`, then a table with the header `| role | model | runs | killed | changed outcome | verdicts | BLOCKING findings | gate fails fixed before hand-off |` and a `|---|` separator row.
     - Verdicts are `<STATUS> <n>` pairs, joined by `, ` and sorted by status.
     - BLOCKING is a number for reviewer and critic rows, else `-`.
     - The gate column is `<fails> in <read> read, <n> not recorded` for implementer rows, else `-`.
     - A row with no runs and no kills is not printed.
   - `## B. Where tickets stop`. Park reasons are taken after the correction rule under Decisions (`park.corrected`), then normalised. First `| park reason | parks |`, with rows by count descending and then reason in code-point order, and a last row `| all parks | <n> |`. Then a blank line and `| gate or merge decision | count |`, with rows in this order:
     - `spec approved` and `spec changes requested`, always printed;
     - `resolved: <kind>`, by kind;
     - `merge refused: <reason>`, by reason;
     - `archive refused`, always printed.
   - `## C. Where spec defects were caught and where they came from`. First `| caught by | status | ticket | spec version | written by | critiqued by | critic REVISE on the ticket |`, one row per catch, ordered by the catching run's `started`. Then a blank line and `| critic REVISE on the ticket | approved specs | caught downstream |`, with rows `yes` and then `no`. Both count tickets, per store, with a spec approval in the window.
   - `## D. What each role costs`, with `| role | model | runs | wall s | context tokens | output tokens | USD from records | cost from |`.
     - Runs include killed runs.
     - Numbers are plain integers, and USD has two decimals.
     - `cost from` reads `record <n>, transcript <n>, none <n>`.
     - Rows follow section A's order.

C. CLI (`factory/cli.py`).
   - Add the `stats` subparser with `--store` (repeatable), `--since`, `--until` and `--transcripts` (repeatable), and a `stats_cmd(a)` that resolves the stores (Decisions), calls `stats.report` and prints it.
   - Refusals (no store found, a path that is not a store, an unparsable WHEN) raise `Refused`, so they exit 2.
   - In `main()`, line 1972, handle `stats` as `init` and `paths` are, before `instance.require()`, the fence and `instance.guard()`.
   - Add `("stats", None)` to `READ_ONLY` (line 1939), so the code's list matches the documents. Update `fence()`'s and `main()`'s comments.

D. Tests, in new files only, in each sub-ticket that adds the code they test.
   - `tests/factory/test_cost_once.py` (ST-1) covers:
     - `tally()` on a transcript with repeated message ids;
     - the matching rule (path preference, the relay message skipped, another store's path ruled out, the time window, a unique fallback);
     - `gate_failures()` for a fixed failure, a failure never fixed, and an input with no gate line.
   - `tests/factory/test_stats.py` (ST-2) covers:
     - each section's rows on a fixture like the acceptance fixture;
     - the window;
     - each normalisation rule, and the correction rule (a matching correction, one dated after `--until`, one whose `previous` matches no park);
     - the refusals;
     - a run on an own store with a run in flight, from the store's `runs/`, and under a harness lock that names another revision. Use `tests/factory/test_live_store_guard.py`'s way of building one.

E. Documents (ST-3).
   - `README.md`:
     - In "Where a human decides", the sentence listing the commands that are not writes ends "`log tail`, `paths` and `stats`".
     - In "Accepting a harness revision", one sentence says that `paths` and `stats` skip both checks because they write nothing.
     - A new how-to subsection, `### Counting what each role catches and costs`, after "What you read at each stop", says:
       - what `factory stats` prints;
       - its options;
       - that `--transcripts ~/.claude/projects` adds cost for runs without a cost record;
       - that `--until` makes a past figure repeatable;
       - the gate-failure limit (a command run in another form is missed).
     - In "What depends on Claude Code", a row says `factory stats` reads the store with no Claude Code, and Claude Code transcripts only for `--transcripts`.
     - A **Built** bullet names `factory stats`.
     - Bump the status date.
   - `docs/design.md`:
     - The fence paragraph's read-only list ends "`log tail`, `paths` and `stats`".
     - The role-context paragraph's lock clause says that `paths` and `stats`, which only read, run under any revision.
     - The model-per-role paragraph gains one or two sentences citing `factory stats` and the figures it prints for the reviewer, critic, verifier and implementer rows of sections A and D. Use `--until 2026-10-07T12:00 --transcripts ~/.claude/projects` over both stores, give the date and the command, and compare with the figures under Evidence.
     - The §8 prompt block is unchanged.
   - `docs/principles.md` §4: line 60's "1 BLOCKING finding in total" becomes "3 BLOCKING findings in total". The "Implemented by:" line (68) names `factory stats` and drops "double-counts", and the "Planned:" line keeps only the evidence ladder (#79).
   - `dev/build-harness.spec.md`: after the `**`factory drive`**` paragraph (line 295), add a `**`factory stats`**` paragraph. It gives `factory/stats.py`, the options, the four sections, that the command reads and never writes, and that it skips the instance lookup, the fence and the lock as `paths` does.
   - `docs/changelog.md`: entry 70, in the "After issue #N (date), where ...:" form of entries 66-69. It names issues #70 and #61, the once-per-message-id count, the measured 1.89 and 1.94 factors, `factory stats` and its exemption, and the rejected alternatives under Decisions.
   - No file under `docs/prompts/` or `factory/prompts/` changes.

## Tests to change

none. No suite test calls `factory.cost`, asserts the read-only list, or runs a command that is not one of `init` and `paths` outside the lock. I checked with `grep -rn 'cost\|tally\|READ_ONLY' tests/factory/*.py`. `tests/factory/test_harness_lock.py:48` names `("init", "paths")` only to choose how its helper runs the CLI, and no test there calls `stats`. The one current-truth requirement that the new behaviour contradicts, live-store-guard's list of commands exempt from the in-flight refusal, is restated below as a MODIFIED requirement.
=== specs/factory-stats/spec.md
## ADDED Requirements

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
=== specs/live-store-guard/spec.md
## MODIFIED Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths`, `drive` and `stats`, none of them given `--accept-harness`, MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

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

## ADDED Requirements

### Requirement: factory stats reads any store under any harness revision and writes nothing
`factory stats` MUST run on an instance's own store while a run is in flight there, from inside that store's `runs/`, and when the instance's `harness.lock` names another revision, exiting 0 and writing nothing, and with no `--store` it SHALL read the store of the instance found from the caller's directory.

#### Scenario: Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. T-0001's triage run is in flight on the target's own store, and the lock is overwritten to name another revision, so an ordinary read is refused.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && echo 0000000000000000000000000000000000000000 > $T/tgt/.factory/harness.lock && S0=$(snap); $B stats > $T/o1 2>/dev/null; a=$?; cd $W && $B stats > $T/o2 2>/dev/null; b=$?; cd $T/tgt && $B ticket show T-0001 >/dev/null 2>&1; c=$?; echo "here=$a inside=$b store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) own=$(grep -cxF "Stores: $S" $T/o1) locked=$c")`
- THEN it prints exactly `here=0 inside=0 store=unchanged own=1 locked=2`
=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record factory stats
README SHALL list `stats` among the commands that are not writes, say under "Accepting a harness revision" that it skips the lock, describe it in a how-to subsection "Counting what each role catches and costs", in "What depends on Claude Code" and under **Built**; `docs/design.md` SHALL list it in the fence paragraph's read-only list, name it in the lock clause, and cite it in the model-per-role paragraph; `docs/principles.md` §4 SHALL name it as implemented and no longer say "1 BLOCKING finding in total"; `dev/build-harness.spec.md` SHALL give it a paragraph; `docs/changelog.md` SHALL gain one entry naming issues #70 and #61 as its last numbered entry, numbered without a gap; no prompt copy SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The documents record factory stats
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; j() { tr '\n' ' ' | tr -s ' '; }; r=README.md; H=$(sed -n '/^## Where a human decides/,/^```/p' $r | j); L=$(sed -n '/^### Accepting a harness revision/,/^### Upgrading the runtime/p' $r | j); echo "readonly=$(y $(echo "$H" | grep -c '`paths` and `stats`')) howto=$(y $(sed -n '/^### Counting what each role catches and costs/,/^##/p' $r | grep -c 'factory stats')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory stats')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'factory stats')) lock=$(y $(echo "$L" | grep -c '`stats`')) design-fence=$(y $(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md | grep -c '`paths` and `stats`')) design-lock=$(y $(grep '^\*\*Role-context block\.\*\*' docs/design.md | grep -c '`stats`')) design-model=$(y $(grep '^\*\*Model per role, starting point\.\*\*' docs/design.md | grep -c 'factory stats')) principles=$(y $(sed -n '/^### 4\. Measure catch beside cost\./,/^##/p' docs/principles.md | grep '^Implemented by:' | grep -c '`factory stats`')) principles-old=$(y $(grep -c '1 BLOCKING finding in total' docs/principles.md)) buildspec=$(y $(grep -c '^\*\*`factory stats`\*\*' dev/build-harness.spec.md)) prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e '#70' -e '#61' -e 'factory stats' -e 'message id' | sort -u | grep -c .; git diff --check main...HEAD >/dev/null && echo clean || echo dirty)`
- THEN it prints exactly `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no buildspec=yes prompts=0`, then `CONTIGUOUS`, then `4`, then `clean`
=== verification.md
## Acceptance

Run every command from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper. The fixture GIVEN block and live-store-guard's GIVEN block are each run once first. Every NEW item's output on `main` `5215c5f` below was captured by running it there.

- Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures → NEW. Today it prints only `exit=2`: `stats` is not a command (`invalid choice: 'stats'`).
- A window bounds the count and the command writes nothing → NEW. Today it prints `exit=2 store=unchanged since=0`.
- Parks are grouped by normalised reason, with gate and merge decisions → NEW. Today it prints only `exit=2`.
- Each downstream spec catch names the runs that wrote and critiqued its spec → NEW. Today it prints only `exit=2`.
- Cost comes from the run record, else the transcript of that store's run, counted once per call → NEW. Today it prints only `exit=2`.
- The transcript cost report counts each message once → NEW. Today it prints `| critic | fable-5 | 1 | 5 | 725 | 33 |`: five records counted as five calls, with 725 context and 33 output tokens in place of 310 and 17.
- Stats reproduces the hand count on the two live stores → NEW. Today it prints only `exit=2`.
- Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing → NEW. Today it prints `here=2 inside=2 store=unchanged own=0 locked=2`: `stats` is not a command, while the lock does refuse `ticket show` (`locked=2`), which shows the fixture's lock is in force.
- Unmarked writes from inside the target are refused while a run is in flight, init included → REGRESSION
- The refusal names the throwaway store and not the marker → REGRESSION
- A harness acceptance is refused while a run is in flight → REGRESSION
- The documents record factory stats → NEW. Today it prints `readonly=no howto=no built=no depends=no lock=no design-fence=no design-lock=no design-model=no principles=no principles-old=yes buildspec=no prompts=0`, then `CONTIGUOUS`, then `0`, then `clean`.

Round 1's prototype printed the expected THEN lines of the four fixture table scenarios, the window scenario's row and the live-store scenario's lines. This round, on the fixture with its two new corrections, `scratch/p.py` printed the section A rows and the window scenario's row unchanged and the new section B lines, and on the live stores the A and park lines of the live-store scenario. The two new log events touch no section C or D input (those read `spec.added`, `approval.recorded`, run records and transcripts). The parks scenario and the cost-report scenario were rerun on `main` `5215c5f` this round with the new fixture and print `exit=2` and `| critic | fable-5 | 1 | 5 | 725 | 33 |`, as stated. The cost-report and guard scenarios need the real change, and were run only on `main`.

## Out-of-scope observations

- live-store-guard's second requirement, "Writes from inside a store's run directories or code checkouts are refused, marked or not", exempts "the read-only list above". Since `drive` joined that list, the wording also exempts `drive` from the location rule, which `drive` still obeys. The code is right and the wording is loose. This change restates only the first requirement and does not touch that wording.
- `README.md:109` says `factory/cost.py` "reads the Workflow tool's transcript files". After part A it still does, so that row stays true, and part E adds a row for `factory stats` beside it.
