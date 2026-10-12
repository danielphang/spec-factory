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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0444-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0444-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0444-reviewer/wt` (branch `factory/T-0043.3`, base `ebc5773ef696d25c58159c61a7531e7ee3b61b3f`, head `608a62ced66a5f32cb0e3e090d43ef75dd2a6618`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0043.3

## ST-3 / Record `factory stats` in README, the design, the principles, the build spec and the changelog
Depends on: ST-2
Parallel-safe: no (its design-doc figures are printed by ST-2's command)

Parent: T-0043, spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part E, all of it.
- `README.md`: the read-only list in "Where a human decides", the sentence in "Accepting a harness revision", the new `### Counting what each role catches and costs` subsection, the "What depends on Claude Code" row, the **Built** bullet and the status date. Read its "Maintaining this page" section first.
- `docs/design.md`: the fence paragraph's read-only list, the role-context paragraph's lock clause, and the model-per-role paragraph's citation of `factory stats`, with the figures it prints over both stores with `--until 2026-10-07T12:00 --transcripts <transcripts dir>`. The §8 prompt block is unchanged.
- `docs/principles.md` §4: 3 BLOCKING findings in place of 1; the "Implemented by:" and "Planned:" lines.
- `dev/build-harness.spec.md`: the `**`factory stats`**` paragraph after the `**`factory drive`**` paragraph.
- `docs/changelog.md`: entry 70, in the form of entries 66 to 69.

Acceptance:
- NEW. "The documents record factory stats". WHEN the spec's command (the `y()`/`j()` greps over README.md, docs/design.md, docs/principles.md and dev/build-harness.spec.md, the changelog numbering `awk`, the last entry's `#70`/`#61`/`factory stats`/`message id` count, and `git diff --check main...HEAD`) THEN it prints exactly `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no buildspec=yes prompts=0`, then `CONTIGUOUS`, then `4`, then `clean`.
- REGRESSION (made true by ST-2). "Stats reproduces the hand count on the two live stores": the spec's command and its eight THEN lines, unchanged. It confirms that the command whose figures the design doc quotes still prints them.
- REGRESSION (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory` THEN the whole suite passes.

Interim tests: none
Tests to change: none
Protected paths: none
Out of scope: any code or test change; any file under `docs/prompts/` or `factory/prompts/`, including the §8 retro block and its copy; feeding the figures into the retro's input (issue #42); restating figures quoted from `factory/cost.py` before this change, such as changelog entries 58 and 67.

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

## PR description (the implementer's output)

Sub-ticket: T-0043.3 (ST-3 of T-0043, spec v2: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`), branch `factory/T-0043.3`, head `608a62c`, base `ebc5773`

## What changed

ST-3 adds no code. It records the new `factory stats` command in the five documents that describe the harness. `factory stats` is the read-only command, added by the two earlier sub-tickets, that counts each role's verdicts, parks and token cost from a store, the factory's file-based record of runs and events. The commit is `608a62c` and changes only `README.md`, `docs/design.md`, `docs/principles.md`, `dev/build-harness.spec.md` and `docs/changelog.md`. `git diff --stat main...HEAD -- factory tests bin agents pyproject.toml uv.lock` prints nothing.

Part E, file by file:
- `README.md`:
  - In "Where a human decides", the list of commands that are not writes now ends "`log tail`, `paths` and `stats`".
  - "Accepting a harness revision" gains one sentence: "`paths` and `stats` skip both checks on any store, because they write nothing." This matches `factory/cli.py` `main()`, which runs `init`, `paths` and `stats` before `instance.require()`, the fence and `instance.guard()`.
  - New how-to subsection, `### Counting what each role catches and costs`, after "What you read at each stop". It gives the command line, a table of the options and a table of the four sections. It explains cost records against transcripts and suggests `--transcripts ~/.claude/projects`, which took 12.3 s when I ran it. It also says why `--until` makes a figure repeatable, and states the gate-column limit: a gate command run in another form is missed, so the column can undercount.
  - "What depends on Claude Code" gains a row. `factory stats` reads the store with no Claude Code, and reads Claude Code's transcripts only when given `--transcripts`.
  - **Built** gains a `factory stats` bullet. It says the command has run over both targets' stores, which I did.
  - "Related work and history" gains one sentence: `factory stats` answers #70, absorbs #61, and the retro feed is #42.
- `docs/design.md`:
  - The fence paragraph's read-only list now ends "`log tail`, `paths` and `stats`".
  - The role-context paragraph's `harness.lock` clause now adds "`paths` and `stats`, which only read, run under any revision".
  - The model-per-role paragraph gains two sentences that cite `factory stats` and the command I ran (`--until 2026-10-07T12:00 --transcripts ~/.claude/projects`, over both stores, on 2026-10-11). They give the reviewer, critic, verifier (both models) and implementer figures from sections A and D, and how these differ from the request's hand count.
  - No prompt block changed, §8 included.
- `docs/principles.md` §4:
  - "1 BLOCKING finding in total" becomes "3 BLOCKING findings in total".
  - "Implemented by:" now names `factory stats` and no longer says "double-counts".
  - "Planned:" keeps only the evidence ladder (#79).
- `dev/build-harness.spec.md`: a `**`factory stats`**` paragraph follows the `**`factory drive`**` paragraph. It gives `factory/stats.py`, the options, the refusals, the window rules, the four sections, that the command reads and never writes, and that `main()` runs it, like `paths`, before the instance lookup, the fence and the lock. It also says `stats` is listed in `READ_ONLY`.
- `docs/changelog.md`: entry 70 follows the "After issue #N (date), where ...:" form of entries 66 to 69. It names issues #70 and #61, the once-per-message-id count, the measured 1.89 and 1.94 factors, `factory stats` with its four tables and its exemption, the corrected BLOCKING figure, and the alternatives rejected under the spec's Decisions. It says that figures quoted from `factory/cost.py` before this change (entries 58 and 67) are history and are not restated.

The design doc's figures come from `bin/factory stats --store /Users/dphang/dev/spec-factory/.factory/store --store /Users/dphang/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 --transcripts /Users/dphang/.claude/projects`. I ran it under the wrapper on this branch and it exited 0. I gave the transcripts directory as an absolute path because the wrapper's HOME is a temporary directory. The rows it printed:
- A: `| reviewer | fable | 94 | 5 | 4 | APPROVE 90, ESCALATE 1, REQUEST-CHANGES 3 | 3 | - |`, `| critic | fable | 84 | 0 | 19 | APPROVE 65, REVISE 19 | 19 | - |`, `| implementer | opus | 111 | 3 | 18 | BLOCKED 18, READY-FOR-REVIEW 92, UNKNOWN 1 | - | 0 in 111 read, 0 not recorded |`, `| verifier | opus | 108 | 0 | 8 | ... |` and `| verifier | fable | 5 | 0 | 1 | ... |`.
- D: reviewer 99 runs and 94,860,442 context tokens; critic 84 and 66,027,675; implementer 114 and 372,507,821; verifier on Opus 108 and 232,945,610; verifier on Fable 5 and 5,189,563.

These equal the spec's Evidence figures: the A rows, and the totals of 94,860,442, 372,507,821 and 232,945,610 context tokens, with the run counts of 99, 114 and 108. Evidence also said the gate column found 0 fixed failures in 111 implementer runs, and the command prints `0 in 111 read`.

I re-checked two claims the changelog repeats from the spec's Evidence:
- That a once-per-id count equals a cost record. `transcript_usage()` on `run-0413-spec_writer`'s transcript (`4730aa67-….jsonl`) returns `(61, 13959978, 74126)`. That run's `meta.yaml` cost record gives 122 + 178,311 + 13,781,545 = 13,959,978 context tokens.
- The double-count factors, with `scratch/factor.py`. For the Nanobot store it printed 2,016,972,806 tokens counting every record against 1,069,416,588 counting once (1.886), the same as Evidence. For this store it printed 1.95 over 443 matched runs, against the 1.94 that Evidence measured on fewer runs. So the changelog says the factors were "measured ... when the change was specified".

## Acceptance results

All commands ran from the worktree through the briefing's wrapper, after `uv sync --frozen`.

- NEW "The documents record factory stats". I ran the spec's command verbatim from `scratch/docs-check.sh`.
  - Before (base `ebc5773`): `readonly=no howto=no built=no depends=no lock=no design-fence=no design-lock=no design-model=no principles=no principles-old=yes buildspec=no prompts=0`, `CONTIGUOUS`, `0`, `clean`. This matches the "today" output in verification.md: nothing was documented yet.
  - After (`608a62c`): `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no buildspec=yes prompts=0`, then `CONTIGUOUS`, then `4`, then `clean`. This is exactly the expected output: every document records `stats`, the old figure is gone, no prompt copy changed, the changelog has no numbering gap, its last entry has all four markers, and the diff has no whitespace errors.
- REGRESSION "Stats reproduces the hand count on the two live stores", run on `608a62c` with `TMPDIR` set to the scratch directory. It printed `exit=0`, `| critic | fable | 84 | 0 | 19 | APPROVE 65, REVISE 19 | 19 | - |`, `| implementer | opus | 111 | 3 | 18 | BLOCKED 18, READY-FOR-REVIEW 92, UNKNOWN 1 | - | 0 in 0 read, 111 not recorded |`, `| reviewer | fable | 94 | 5 | 4 | APPROVE 90, ESCALATE 1, REQUEST-CHANGES 3 | 3 | - |`, `| verifier | fable | 5 | 0 | 1 | SPEC-DEFECT 1, VERIFIED 4 | - | - |`, `| verifier | opus | 108 | 0 | 8 | FAILED 4, SPEC-DEFECT 4, VERIFIED 100 | - | - |`, `| NEEDS-HUMAN from triage | 30 |` and `| all parks | 82 |`. These are the eight expected lines, exactly. The command whose figures the design doc quotes still prints them.
- REGRESSION and gate: `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, as written.
  - First run on `608a62c`: exit 1, `1 failed, 576 passed in 348.15s`. The failure was `tests/factory/test_drive_build.py::test_the_checkers_run_at_once_and_subtickets_up_to_the_parallel_limit`, with `assert (4 == 4 and 3 == 4)`: a timing assertion on how many stub role processes ran at once.
  - The branch changes no code, so the code under test is the base's. Run alone three times on `608a62c`, that test passed each time (`1 passed, 8 deselected`, in 6.8 to 8.7 s).
  - Second full run on `608a62c`: exit 0, `577 passed in 346.30s`. I take the first failure to be load-dependent flakiness, not a regression; see Known gaps.
- Gate `git diff --check main...HEAD`, as written: exit 0, no output, so no whitespace errors.

## Tests added/changed

None. The sub-ticket lists no interim tests and no tests to change, and it changes documents only.

## Known gaps and uncertainties

- The status date in README's header already read 2026-10-11, which is today. "Bump the status date" therefore left it unchanged.
- The design doc's command line writes `--transcripts ~/.claude/projects`, as part E specifies. I ran it with the absolute path `/Users/dphang/.claude/projects`, the same directory, because the wrapper's HOME is a temporary directory. Its D figures depend on transcripts Claude Code still keeps. If Claude Code deletes old transcripts, a rerun may print fewer tokens, and those runs move to the `none` source column.
- The design paragraph says the implementer had "no gate failure found fixed before hand-off". That rests on the text match README states as a limit, so the true count may be higher.
- The full suite failed once on a timing assertion in `test_drive_build.py` and then passed. I did not investigate that test, because this branch touches no code.
- README's "Related work and history" paragraph had overlong lines before this change. I added one sentence to it without reflowing the paragraph, so it stays ragged.

## Out-of-scope observations

- `test_the_checkers_run_at_once_and_subtickets_up_to_the_parallel_limit` (`tests/factory/test_drive_build.py:194`) asserts an exact peak concurrency of stub processes. Under the load of the full suite it saw 3 where 4 were expected. A sound fix is out of this ticket's scope.
- Over every matched run, this store's double-count factor is now 1.95, against the spec's 1.94, because the store has grown. The changelog keeps the measured figure and says when it was measured.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The NEW check prints exactly its expected output, the live-store regression prints its eight lines, and both gates pass on `608a62c` (the suite on its second run).
ESCALATIONS: none

## Diff `ebc5773ef696d25c58159c61a7531e7ee3b61b3f...608a62ced66a5f32cb0e3e090d43ef75dd2a6618`

diff --git a/README.md b/README.md
index b08658d..9ed5981 100644
--- a/README.md
+++ b/README.md
@@ -107,6 +107,7 @@ Most of the factory is plain files and a Python program. Five pieces assume Clau
 | Role processes of `factory drive` (`factory/drive.py`) | yes | each role runs as one headless `claude -p` process with `--output-format json` and `--permission-mode auto`, its role's prompt file, model and optional `--effort`, and its tool limits given by `--tools` and `--allowedTools` |
 | Model names (`models` in `instance.yaml`) | yes | Claude model aliases |
 | Token cost per role (`factory/cost.py`) | yes | reads the Workflow tool's transcript files |
+| Catch and cost per role (`factory stats`, `factory/stats.py`) | no | reads the store's files with no Claude Code; reads Claude Code's transcript files only when given `--transcripts` |
 
 `inlineRoles: true` in the workflow's arguments skips the registered agents: every role runs as a
 general-purpose agent that reads its prompt from the run's `system-prompt.txt`, with no per-role
@@ -544,7 +545,7 @@ can accept a revision while another stays on the old one.
 The flag cannot clear the other refusal. A runtime with uncommitted edits to the harness code is
 refused outright; commit or discard them first. Both checks apply only when a command uses the
 instance's own store. A throwaway store (`FACTORY_STATE` pointing elsewhere, as every test does)
-skips them.
+skips them. `paths` and `stats` skip both checks on any store, because they write nothing.
 
 ### Upgrading the runtime
 
@@ -832,9 +833,9 @@ runs from the same runtime. Each target's runner then accepts the new revision b
 A run is in flight from `run start` until `run finish` records its result. While any run on a
 target is in flight, the harness refuses every write to that target's store that lacks this
 marker. A write is any command except `ticket show`, `ticket join`, `results show`, `config`,
-`status parse`, `log tail` and `paths`; a command given `--accept-harness` is always a write.
-`factory drive` is exempt from this check and needs no marker, because it is the dispatcher; it
-guards its own ticket instead ("Driving a ticket from a shell with `factory drive`"). The
+`status parse`, `log tail`, `paths` and `stats`; a command given `--accept-harness` is always a
+write. `factory drive` is exempt from this check and needs no marker, because it is the
+dispatcher; it guards its own ticket instead ("Driving a ticket from a shell with `factory drive`"). The
 workflow scripts already put the marker on their own commands. Put it in front of one command at
 a time:
 
@@ -881,6 +882,49 @@ next, how many rounds, what the checkers receive, when a merge is allowed, when
 `factory ticket show <T>` prints a ticket's state, rounds, park reason and runs in flight; every
 path above is relative to the store.
 
+### Counting what each role catches and costs
+
+`factory stats` counts, from the store's records, how often each role's verdict changed what
+happened next and what each role cost. Use it before deciding which model a role runs, or whether
+a check is worth its cost. It reads one or more stores and writes nothing. It needs no marker and
+no `--accept-harness`, so it runs while a build is in flight and from any checkout.
+
+```
+$RUNTIME/bin/factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...
+```
+
+| Option | What it does |
+|---|---|
+| `--store PATH` | a store to read; repeat it to sum several stores. With none, it reads the store `FACTORY_STATE` names, else the store of the instance found from the current directory, and is refused with exit 2 when there is neither |
+| `--since WHEN`, `--until WHEN` | count only runs started, and log events dated, inside the window. WHEN is an ISO date or date-time, taken as UTC when it has no zone. `--since` is inclusive and `--until` exclusive |
+| `--transcripts DIR` | a directory of Claude Code transcripts, searched for `*.jsonl` files at any depth; repeatable |
+
+It prints four Markdown tables. A changed outcome is a verdict that sends work back or stops it:
+REQUEST-CHANGES, ESCALATE, FAILED, SPEC-DEFECT, REVISE or BLOCKED. A BLOCKING finding is a finding
+the critic or the code reviewer says must be fixed.
+
+| Section | One row per | What it shows |
+|---|---|---|
+| A. Runs and verdicts by role and model | role and model | runs, runs killed before they finished, runs with a changed outcome, the verdicts by status, the critic's and reviewer's BLOCKING findings, and the gate commands an implementer saw fail and then fixed before it handed off |
+| B. Where tickets stop | park reason, then gate or merge decision | parks by reason, with run, ticket and commit ids replaced by `<run>`, `<ticket>` and `<sha>`; then spec approvals, requests for spec changes, other human resolutions, merge refusals by reason, and archive refusals |
+| C. Where spec defects were caught and where they came from | verifier SPEC-DEFECT or implementer BLOCKED run | the spec version the run worked from, the run that wrote it, the critic run that last checked it, and the ticket's REVISE count; then how many approved specs, with and without a REVISE, were caught later |
+| D. What each role costs | role and model | runs including killed ones, wall time, context and output tokens, dollars, and how many runs took their cost from a cost record, a transcript or neither |
+
+A run started by `factory drive` carries a cost record: its tokens and dollars, kept in its
+`meta.yaml`. Any other run has its tokens only in the transcript Claude Code kept for its agent.
+Add `--transcripts ~/.claude/projects` to count those runs; reading that directory takes about
+12 seconds on this machine. Each model call is counted once. Context tokens are the input,
+cache-read and cache-creation tokens together. Dollars come only from cost records, because
+transcripts carry none. Without `--transcripts`, such a run counts under `none` in section D, and
+section A lists it as "not recorded" in the gate column.
+
+Give `--until` to make a figure repeatable, because the store keeps growing. A park reason that a
+human corrected later changes the figure only if the correction is dated before `--until`.
+
+The gate column has one known limit. It finds a gate command by its exact text among the
+implementer's shell calls, so a gate command the implementer ran in another form is missed, and
+the column can undercount.
+
 ## What is built and what is not
 
 **Built**
@@ -978,6 +1022,13 @@ path above is relative to the store.
   role an effort level, which `factory drive` passes to that role's process. A role not listed gets
   Claude Code's default. The workflow scripts ignore the map, so a role they run has a model and no
   effort level. Neither target sets it yet.
+- **Counting catch and cost, `factory stats`.** A command that reads one or more stores and
+  prints, per role and model, the runs, verdicts, outcome changes, BLOCKING findings and tokens;
+  where tickets park; and which runs wrote and critiqued each spec a later role found defective
+  ("Counting what each role catches and costs"). It takes a run's tokens from its cost record,
+  else from its Claude Code transcript, and counts each model call once. `factory/cost.py` now
+  counts the same way; it used to count most calls about twice. `factory stats` writes nothing,
+  and it skips the live-store fence and the harness lock. It has run over both targets' stores.
 
 **Not built**
 
@@ -1073,7 +1124,8 @@ filing from an issue tracker, what you read at each stop, other agent hosts) wer
 the build roles, which `inlineRoles` works around today (#24); a stopped run that stays in flight
 (#53). The driver, `factory drive`, answers #65 and absorbs per-role effort (#22), the operator's
 latest chat message reaching every role agent (#28), titles beside ticket ids in progress output
-(#47) and the checkers' tool limits (#24 part A); retiring the workflow scripts is a later ticket. Earlier sources: prompt changes borrowed from the ponytail project (#20); the documentation
+(#47) and the checkers' tool limits (#24 part A); retiring the workflow scripts is a later ticket. `factory stats` answers #70 and absorbs the double count in `factory/cost.py` (#61);
+feeding its figures to the retro is #42. Earlier sources: prompt changes borrowed from the ponytail project (#20); the documentation
 standard this page follows (#23); each run's scratch directory (#35); the store branch (#46). The
 design document is `docs/design.md`, its changelog `docs/changelog.md`; the working documents from
 building the harness are under `dev/`; the issue index is `dev/issues.md`. The store holds 42
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index f226933..45f634a 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -294,6 +294,8 @@ Resumption after a human decision: the `/factory` skill re-runs `build.js` for t
 
 **`factory drive`** (`factory/drive.py`) does the same routing outside the Workflow tool. It ports both scripts from `// --- start`, `build.js` with its `buildOne`, branch for branch, with the same commands, transitions, round limits and park reasons, so a ticket it drives leaves the records the scripts leave. In place of the clerk it calls `factory.cli.main` in its own process, one call at a time, so every guard, the fence and the harness lock run as for `bin/factory`. When it starts it is exempt from the fence's in-flight rule, keeps the location rule, and refuses to start on the same ticket as a run in flight, on that ticket or a sub-ticket, or as a live driver. Each role runs as one `claude -p` process from the run's directory; its reply is kept as `runs/<run_id>/reply.json` and recorded by `run finish --reply`. A head's two checkers run at once, ready sub-tickets build at once up to `--parallel N`, and the driver stops at the spec gate. Its permissions are in R6 and I.4.
 
+**`factory stats`** (`factory/stats.py`) counts what each role catches and costs: `factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...`. With no `--store` it reads `FACTORY_STATE`, else the store of the instance found from the caller's directory; no store found, a path with neither `runs/` nor `log/`, or an unparsable WHEN is refused with exit 2. WHEN is an ISO date or date-time, UTC when it has no zone; `--since` is inclusive and `--until` exclusive; runs are windowed by `started` and log events by `ts`, and a `park.corrected` event applies only when dated before `--until`. It prints four Markdown sections, summed over every store given: A, runs and verdicts by role and model, with kills, changed outcomes (`CHANGED`), the critic's and reviewer's BLOCKING findings and the implementer's gate failures fixed before hand-off (`cost.gate_failures`); B, parks by reason normalised by `PARK_RULES`, then spec approvals, requests for changes, other `human.resolved` kinds, merge refusals by reason and archive refusals; C, each verifier SPEC-DEFECT and implementer BLOCKED run against the runs that wrote and last critiqued its spec version, then approved tickets with and without a critic REVISE against later catches; D, each role's wall time, context and output tokens and recorded dollars, from the run's `claude:` cost record, else from the transcript `cost.match_transcripts` places on it under `--transcripts`, counting each message id once (`cost.transcript_usage`). It reads and never writes. Like `paths`, `main()` runs it before the instance lookup, the fence and the harness lock, so it ignores `--accept-harness`; it is also in `READ_ONLY`, so the code's read-only list matches the design's.
+
 ### I. Isolated run per role (piece 3) — worktree v0
 
 1. System prompt = the agent definition (`factory/prompts/preamble.md` is read by its first instruction); the clerk records it in `runs/<run_id>/system-prompt.txt`.
diff --git a/docs/changelog.md b/docs/changelog.md
index 7cf9e63..124f7bc 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -71,5 +71,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 67. After issue #65 (2026-10-05), where the dispatcher, a Workflow-tool script that can run no command and read no file, sent every store read and write through a clerk agent: the requester counted 2,236 clerk agents and 4,476 calls over 97 runs, 143M of 866M workflow context tokens (17%), and the clerk was most of the wait between steps. On 2026-10-09 the clerk also returned a correct `run finish` reply pretty-printed across lines, so T-0027.2's build parked as `harness-bug: run finish reviewer:` although the reviewer's run had succeeded. `factory drive TICKET [--phase intake|build] [--parallel N] [--prompt-mode append|replace]` (`factory/drive.py`) now does the scripts' job as an ordinary Python process. It ports both scripts branch for branch, with the same routes, round limits, refusals and park reasons, and stops at the spec gate. It calls the store CLI's entry point in its own process, one call at a time, so it has no clerk and every guard, the fence and the lock run as for `bin/factory`. It marks its own store calls with `FACTORY_DISPATCH=1` once started and never its role processes. Each role runs as one `claude -p` process from its run directory, with `--output-format json`, `--permission-mode auto`, the role's prompt file, model and an optional `--effort` from a new `effort:` map in `instance.yaml`, and `--tools`/`--allowedTools` lists whose `Edit` rules cover only the run's output file, its scratch directory and the temporary directory, plus the implementer's worktree. The reply is kept as `reply.json`, and `run finish --reply` records its session id, cost, turns and usage under `claude:` in `meta.yaml`. Progress is one line per step naming the ticket or sub-ticket and its title, and a status file, `drive/<ticket>.yaml`, which the store's `.gitignore` excludes. SIGINT or SIGTERM ends the role processes, records their runs `KILLED`, parks nothing, and a second run resumes. Absorbed: #22 (per-role effort), #28 (the operator's latest chat message reaching every role agent as overriding its task), #47 (a title beside every ticket id in progress output) and #24 part A (the checkers' tool limits). The workflow scripts stay unchanged until the driver has taken a real ticket through each half; retiring them and the clerk is a later ticket. Rejected: `dontAsk`, which removes the permission classifier while roles have no operating-system isolation (#37); the build spec's "nor `dontAsk`" stays. Rejected: a `bin/factory` subprocess per store call, and calling store functions below the CLI's entry point, which would skip the fence and the lock.
 68. After issue #85 (2026-10-10), where the spec drift check parked two sub-tickets of the driver ticket T-0040 for their own siblings' merges, and the second park had no command to clear it: the test rule walked every first-parent commit on the integration branch since the spec was written, so the `--no-ff` merge of T-0040.1, which changed `factory/cli.py` and added `tests/factory/test_drive.py`, parked T-0040.2, and the merges of T-0040.1 and T-0040.2 parked T-0040.3. The Workflow script recorded T-0040.3's drift refusal as `harness-bug: run start implementer: …`, which `resolve --ruling` refused, so the operator edited the stored park reason by hand before the ruling. The test rule now skips a first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans; every other commit and merge still counts. `resolve --ruling F` now also accepts a `harness-bug: run start implementer:` park from `ready-for-implementer`, which means the harness failed to start an implementer run: F becomes the next ruling and the sub-ticket returns to its implementer at the same round, as for BLOCKED, and the ruling on file keeps the drift check from running again. Any other harness-bug park, such as a failed `run compose` or a checker's failed run start, is still refused, and the refusal text names the new case. Rejected: skipping only the current plan's siblings, since an earlier plan's merged sub-ticket is also the parent's own work; skipping merge commits in general; widening `--redispatch`, which re-runs the checkers and would meet the same drift refusal with no ruling on file; accepting every harness-bug park from `ready-for-implementer`, since a failed `run compose` leaves its run in flight.
 69. After issue #86 (2026-10-11), where an operator driving two tickets of the Nanobot target at once could not restart one drive while the other had a run in flight: `factory drive` met the live-store fence when it started, before it set its marker, so a re-run of the T-0036 drive was refused, naming an implementer run of T-0035. Typing the marker in front of the command got past the fence, but the fence's in-flight rule was also the only thing that stopped a second drive of the same ticket, and a marked second drive of a ticket with a run in flight parked that ticket. `factory drive` is now exempt from the fence's in-flight rule: it starts unmarked beside other tickets' runs. It keeps the location rule, so it is refused from inside the own store's `runs/` or `worktrees/`, marked or not. It keeps the harness lock, and given `--accept-harness` it is fenced in full, because an acceptance rewrites the lock. In place of the in-flight rule it has a same-ticket guard, checked before it sets its marker or writes its status file, whether or not the caller is marked and on any store, a throwaway store included. It refuses with exit 2, writing nothing, while the ticket or one of its sub-tickets has a run in flight, naming the runs. It also refuses while `drive/<ticket>.yaml` has no `ended` and its `pid` is live, meaning signal 0 reaches it or is refused for permission, naming the pid and the file. A dead, missing or non-integer pid does not block, and neither refusal names the marker. README's driver how-to no longer tells the operator to type the marker. This overturns T-0040's decision of 2026-10-10 (entry 67) that the driver is a write like any other, and its rejection of exempting it; the operator made the exemption standing for every later runner command. Rejected: applying the guard only on an own store, as the fence is, since two drivers damage a ticket's records on any store; checking with a process query that a live pid is a `factory drive` process, a platform-dependent query for the rare pid reused after a SIGKILLed driver, so the refusal names the pid and README says to delete the status file when it is not a driver; and a lock against two drives of the same ticket started in the same instant, since the reported case was two different tickets and the window is a few store reads long.
+70. After issue #70 (2026-10-11), where the operator could not tell which checks pay for themselves: the figures behind a model choice, such as the code reviewer changing an outcome in 4 of 94 runs, came from a hand-written count over both stores, and the one token report, `factory/cost.py`, counted most model calls about twice, because Claude Code writes one transcript record per streamed block of a reply and each record carries the whole call's usage (issue #61). `factory/cost.py` now counts each message id once, from its last record, and its `calls` column counts message ids. Measured over every transcript matched to a run when the change was specified, the old count was 1.89 times the new one for the Nanobot store and 1.94 times for this one; the new count of a driver run's transcript equals that run's cost record. A new command, `factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...` (`factory/stats.py`), reads one or more stores and prints four tables: runs and verdicts by role and model, with kills, changed outcomes, BLOCKING findings and the implementer's gate failures fixed before hand-off; parks by normalised reason, taking a park's corrected reason when the correction is dated before `--until`, with the spec gate, resolution and merge decisions; each spec defect a verifier or implementer caught, against the runs that wrote and critiqued that spec; and each role's wall time and tokens, from the run's cost record, else its transcript under `--transcripts`, else none. `--until` makes a past figure repeatable on a growing store. `stats` writes nothing and must read a live store during a run and from a checkout the instance has not accepted, so, like `paths`, it skips the instance lookup, the live-store fence and the harness lock and ignores `--accept-harness`; the fence's read-only list gains it. Its count corrects one figure in `docs/principles.md` §4: the reviewer's BLOCKING findings are 3, one in each REQUEST-CHANGES run, not 1. Rejected: JSON output, which no consumer needs yet; adding `stats` only to the fence's read-only list, since the lock would still refuse it outside the accepted runtime; searching `~/.claude/projects` by default, which ties the command to one machine's layout and costs about 12 seconds a call; counting every mention of BLOCKING, which counts "No BLOCKING findings", or the round-2 restatements marked RESOLVED; matching a transcript only by the store's current path, which loses every run from before an unrecorded store move; ignoring park corrections, which reports the error a human fixed, and applying corrections dated after `--until`, which moves a past figure; and reading gate failures from the implementer's output, which states only final results. Figures quoted from `factory/cost.py` before this change, such as those in entries 58 and 67, stay as history and are not restated.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index c8ceede..f04e077 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -61,13 +61,13 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Spec drift.** Between the writing of a spec and the build of one of its sub-tickets, other tickets merge, and a sibling that the sub-ticket's checks rely on may not have merged yet. The harness checks for this before the implementer spends a run on it. Every spec version the store keeps, from `spec add`, a gate edit or `spec amend`, records the integration branch's head when it was stored, as `integration_head` in `specs/<ticket id>/v<n>.yaml`; the value is null when the target repo or branch does not resolve. Before a sub-ticket's implementer run, `run start` checks for drift, ahead of the sibling-tests check. It checks only while the sub-ticket has no finished implementer run and no ruling on file. Two rules find drift. The sibling rule: the sub-ticket's Acceptance field names, by id or by plan label as a whole token, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. The test rule counts from the head recorded with the parent's approved version. It is skipped when that version has no record, because it was stored before the record existed, or when the head is null or not a commit in the target repo. For each first-parent commit on the integration branch since that head that changed a file the version's design part names, each test file the commit changed is a finding, unless the design's `## Tests to change` or the sub-ticket's "Tests to change" lists it. A first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans, is not counted, because the plan expects its siblings' changes. Every other commit and merge still counts. Named files are the design part's backticked paths that exist at the integration branch's head, other than test files and `.md` documents, which nearly every ticket edits. A test file's name starts with `test_`, ends `_test.<ext>`, or contains `.test.`. The test rule approximates "a test pins behaviour the spec changes". Measured on two stores' history, it would have caught 9 of 10 known breaks, and it parks about half of all sub-tickets. On drift, `run start` refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build parks the sub-ticket with that error as the reason. The human amends the spec (`factory spec amend`, Spec store below), rules, or both; `resolve --ruling` returns the sub-ticket to its implementer, and the ruling on file stops the check from repeating.
 
-**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` is the dispatcher, so it is exempt from the in-flight rule: it starts unmarked while runs of other tickets are in flight. It keeps the location rule and the lock, and given `--accept-harness` it is fenced in full, in-flight rule included. In place of the in-flight rule it has a same-ticket guard: it refuses to start on the same ticket, marked or not and on any store, while that ticket or one of its sub-tickets has a run in flight, or while the ticket's status file `drive/<ticket>.yaml` has no `ended` and names a live pid. Once started, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
+**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths` and `stats`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` is the dispatcher, so it is exempt from the in-flight rule: it starts unmarked while runs of other tickets are in flight. It keeps the location rule and the lock, and given `--accept-harness` it is fenced in full, in-flight rule included. In place of the in-flight rule it has a same-ticket guard: it refuses to start on the same ticket, marked or not and on any store, while that ticket or one of its sub-tickets has a run in flight, or while the ticket's status file `drive/<ticket>.yaml` has no `ended` and names a live pid. Once started, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
-**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), the command that installs each build checkout's environment (`environment_sync`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell that first drops a Python virtual environment inherited from the launching shell (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset), then sets `HOME` to a fresh temporary directory and exports any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. When the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the command and its output in the run's `environment-sync.log`), and the role's input says the environment is already synced. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
+**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), the command that installs each build checkout's environment (`environment_sync`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance; `paths` and `stats`, which only read, run under any revision) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell that first drops a Python virtual environment inherited from the launching shell (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset), then sets `HOME` to a fresh temporary directory and exports any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. When the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the command and its output in the run's `environment-sync.log`), and the role's input says the environment is already synced. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
 
-**Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception.
+**Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception. `factory stats` prints the evidence a change to this table needs; run on 2026-10-11 over this repo's store and the Nanobot target's as `factory stats --store .factory/store --store ~/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 --transcripts ~/.claude/projects`, it shows that up to 2026-10-07 12:00 UTC the code reviewer (Fable) changed an outcome in 4 of 94 runs, with 3 BLOCKING findings, for 94,860,442 context tokens over its 99 runs including killed ones; the critic (Fable) in 19 of 84, for 66,027,675; the verifier in 8 of 108 on Opus, for 232,945,610, and in 1 of 5 on Fable, for 5,189,563; and the implementer (Opus) in 18 of 111, with no gate failure found fixed before hand-off, for 372,507,821 over 114 runs. These are the hand count's figures, except that the reviewer's BLOCKING findings are 3, not 1, and the verifier's two models are counted apart.
 
 | Role | Default | Why |
 |---|---|---|
diff --git a/docs/principles.md b/docs/principles.md
index 14f4e80..1ed1bcb 100644
--- a/docs/principles.md
+++ b/docs/principles.md
@@ -57,7 +57,7 @@ contract module (#68) and a spec lint run before the critic (#67).
 ### 4. Measure catch beside cost.
 
 A checker that never disagrees with the author is cost, and it stays invisible until counted. The
-code reviewer changed the outcome in 4 of 94 runs, with 1 BLOCKING finding in total.
+code reviewer changed the outcome in 4 of 94 runs, with 3 BLOCKING findings in total.
 External test: 14% of human code-review comments address defects (Bacchelli and Bird, ICSE 2013,
 https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf).
 Automated reviewers recall 20 to 57% of defects (https://arxiv.org/html/2603.23448v2).
@@ -65,8 +65,8 @@ A field every run fills the same way is not a signal: every recorded CONFIDENCE
 replacement must vary in practice: the evidence ladder (#79 C) says whether a finding was stated,
 pointed at, shown, run or reproduced. An unenforced claim, like the retro's "mandatory" status with zero
 runs (#83 B), is a documentation defect, not a rule.
-Implemented by: nothing yet beyond `factory/cost.py`, which reports cost only and double-counts.
-Planned: `factory stats`, catch rate and cost by role (#70); the evidence ladder (#79).
+Implemented by: `factory stats`, catch rate and cost by role and model, each model call counted once (#70).
+Planned: the evidence ladder (#79).
 
 ## Separation and record
