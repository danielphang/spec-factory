## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the
  P0 walking skeleton, frozen as history from building the harness, which no change updates;
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
own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose
block changed re-copied from it.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0605-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0605-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0605-reviewer/wt` (branch `factory/T-0060.1`, base `9e8f4d3c14d352bf058b1532814d5ff83b6dd14e`, head `37c867e6881221552f4b86efe47fcbb04fabd929`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0060.1

T-0060.1 / Benchmark the factory against one plain Claude Code session on about 10 upstream Nanobot fix PRs, each scored by that PR's own tests
Depends on: none
Parallel-safe: yes

Parent: T-0060, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A plain session's transcript gives its operator messages, operator time, elapsed time and tokens
- A factory arm's store events and runner session give one operator time
- The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing
- The suite passes and no existing test file is modified or deleted
- The benchmark page has its eight sections in order
- The benchmark page states its selection, blinding, setup, measures, review and spend rules
- No relative link in the benchmark page is broken
- README names the benchmark page and puts its report in the cost row
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0060/v2.md`

=== proposal.md
## Problem

The spec factory is a pipeline of AI agent roles that turns a written request into merged code. A human, the operator, approves each spec (the plan an implementer builds from) before any code is written, and handles every stop. Every bar the factory holds itself to today is its own. One agent, the critic, scores specs against a rubric. A writing standard governs prose. A fixed set of past tickets is replayed whenever a prompt changes. The store records what each capability must do. The store is the factory's record of tickets and runs: a directory of files kept on its own git branch. None of these bars says whether sending a change through the factory beats giving the same request to one ordinary Claude Code session. So the operator has no evidence for or against the factory's main claim: more correct changes per hour of their attention.

The north star (`docs/north-star.md`, the page that says what the factory is for and how it is measured) already names the outside test: the upstream benchmark. It takes merged fix pull requests from the public upstream Nanobot project, runs each through the factory and through a plain session, and scores each result by that pull request's own tests. The two ways of doing the work are its two arms. Two things are missing. Nothing writes down how to run the benchmark fairly. And nothing can compute one of its measures, operator time. The store timestamps each approval and ruling the operator makes, and Claude Code timestamps each message the operator types into a session. No command turns those timestamps into minutes, and adding them up by hand would break the north star's rule that nobody types a scorecard number.

This change writes the method as `docs/benchmark.md`. It adds a read-only command that computes an arm's operator time, operator messages, elapsed time and session tokens from those timestamps. It also points to both from the README. Running the ten tasks is the operator's work after the merge, and its spend is approved at this gate.

## Root cause

Nothing is broken. The method and the computation do not exist yet.
- `docs/benchmark.md` is absent.
- No harness code reads a plain session's transcript for operator messages or elapsed time. `factory/cost.py` has the readers the new command needs: `_records` (:34), `_log_records` (:43), `_user_text` (:49), `transcript_usage` (:81) and `_when` (:113). Its `tally()` (:98) only counts Workflow agent files.
- `factory/stats.py` `scorecard()` counts the operator's decisions in the window, never their timing.

## Out of scope

- Running the ten tasks, choosing them and writing their review. These are operator steps after the merge.
- Recording operator time in the store. Answer 1 leaves that to a later ticket.
- Any change to `factory stats`, the scorecard, `factory/cost.py`, `factory init` or store setup. Init works unchanged on a bare checkout (Evidence).
- `docs/north-star.md`, `STATUS.md` and `docs/reviews/TEMPLATE.md`. The north star already describes the benchmark, and `STATUS.md` changes only at a review.
- `docs/design.md`, `docs/prompts/` and `docs/changelog.md`.
- Raising README's 1,225-line budget. This change fits within it.
- A harness check that enforces blindness, such as blocking web tools for role runs.
- Scoring by anything other than the pull request's own tests, such as upstream's full suite or a quality judgment.
- A command that sums or compares results across tasks.
- The private fork. Only public upstream code and issues are used.

## Open questions

none

## Decisions

- The change is the method page, a read-only command and two README edits. Running the tasks is operator work after the merge, which is the split triage proposed.
- The figures come from a new command, `python -m factory.benchmark`, in `factory/benchmark.py`, beside `python -m factory.cost`, whose readers it reuses. Rejected: a shell recipe in the page, which no test would cover. Also rejected: a `factory stats` option, which would change a command every review pastes, and whose store-only model has no place for a session.
- Operator time is counted in sittings (Answer 2). Interactions no more than 15 minutes apart form one sitting. Each sitting counts from its first interaction to its last, plus one minute. Operator time is the sum. Standing for this benchmark only, as Answer 1 is. A later ticket that records operator time in the store decides afresh.
- An operator message is a `user` record that is not `isMeta` or `isSidechain` and holds no `tool_result`. Its `promptSource` must be `typed`, `queued` or `suggestion_accepted`. A record with no `promptSource` counts when its text does not start with `<`. The rule rests on the survey in Evidence.
- The store's interactions are exactly the scorecard's CLI decisions, `approval.recorded` and `human.resolved`. These are Answer 1's "gate and ruling events".
- The factory arm takes #117's measures from `factory stats --scorecard`: operator decisions and interventions, tokens and wall time per change, and lead time. Operator time and the runner sessions' tokens come from the new command. A runner session is a Claude Code session in which the operator drives the factory. The baseline arm takes everything from the new command. Its operator decisions are its operator messages after the first, because filing a ticket is not a decision in the scorecard either.
- Tasks are the 10 most recently merged pull requests that pass four filters (design part C). The rule is fixed in advance, so nobody picks tasks after seeing results.
- The arms are kept blind in five ways. Each checkout holds only the parent commit, fetched shallow with no remote. Both arms get identical task text. The operator does not open the pull request until both arms have ended. Arm order alternates across tasks. A transcript audit follows each task, and an arm that leaked is reported as leaked and not scored.
- Each arm has its own checkout. The factory arm exports `FACTORY_INSTANCE` and `FACTORY_STATE` to the checkout's own instance and store. Every command in that shell then reaches only the throwaway store, and the scorecard names the instance instead of printing a path (Evidence).
- The plain session runs on the model this repository's `instance.yaml` gives the implementer, today `opus`.
- A task's score is the pull request's added or changed test files, checked out from its merge commit over the arm's result and run with upstream's test command. It passes when that command exits 0.
- Results go in the next review's section 5, as each command's output pasted as printed. A total or median across tasks is written "not yet computed", because nothing computes it.
- README grows by exactly one net line, from 1,224 to 1,225, which fills its budget. That is one new "Where things live" row, with the cost row of "What depends on Claude Code" edited in place. There is no "Built" entry: the row says the command has not yet run on a benchmark task. The budget is checked by current truth's own scenario, which the gate replays, not by a new one. So a later change that raises the budget has none of this change's scenarios to restate.
- This change's scenarios are written for `factory truth check` to replay after the archive: exact-print THENs, and fixture reuse named as "the GIVEN block of" a scenario. The README scenario checks only what this change adds, so a later edit elsewhere in those tables does not fail it.
- No changelog entry. `docs/design.md` does not change, as in T-0049 and T-0056.
- The spend, about 10 factory intakes and builds and 10 plain sessions, is approved at this gate (request part C).

## Risk

The new module only reads the files it is given and writes nothing, and no existing code calls it. The README edits are one new table row and one row reworded in place. After the merge README is at its 1,225-line budget, so the next change that adds a README line must raise the budget in its own spec, as T-0056 did. Adding `factory/benchmark.py` moves the harness revision, so the next runtime upgrade needs the usual `--accept-harness`. The factory arm has never run on a fresh upstream checkout. Init works there (Evidence), but `factory drive` on such an instance is first tried on the first task, and a failure there is filed as a defect, not worked around.

Protected paths: `factory/benchmark.py`

## Operator steps

1. At this gate: approve the spend, about 10 factory intakes and builds and 10 plain sessions, or strike it. Answers 1 and 2 were given by Green for the operator; strike either here if it is wrong.
2. After the merge, open an issue labelled `experiment` for the benchmark run.
3. Choose the tasks by `docs/benchmark.md`, "Choosing the tasks", and record the cut-off date in that issue.
4. Run each task by the page, measuring from the dev checkout at a commit that contains this change.
5. Write the results into the next review by "Putting a result in a review".

=== design.md
## Proposed change

**A. `factory/benchmark.py`, run as `python -m factory.benchmark`.** It is a read-only report on one arm of one task.

- Usage: `python -m factory.benchmark [--store PATH] [SESSION.jsonl]...`. SESSION is a Claude Code transcript of a session the operator typed into: the plain session, or the factory arm's runner sessions. `--store` is the factory arm's throwaway store.
- Reuse `factory.cost`: `_records` to read a transcript (unparseable lines skipped), `_log_records` for the store's events, `_user_text`, `_when` and `transcript_usage`. Take the decision events from `factory.stats.DECISIONS`. Do not copy any of these. Do not import `factory.cli`.
- Refusals: exit 2 with one line on stderr starting `factory.benchmark: `, before any output. They cover no `--store` and no session; a SESSION that is not a file (the message names it); and a `--store` with no `log/` directory (the message names it). argparse's own errors also exit 2.
- Operator message: the rule under Decisions, which needs a `timestamp`.
- Interactions: the operator messages' timestamps, plus the `ts` of each store event whose `event` is in `DECISIONS`.
- Operator time (Answer 2). Sort the interactions. A new sitting starts at the first interaction, and at each one more than 15 minutes (900 s) after the one before. A sitting counts its last interaction minus its first, plus 60 s. Operator time is the sum, in minutes.
- Elapsed: the latest minus the earliest timestamp among every session record that has one and every store event that has a `ts`, in hours. It prints `-` when there is none.
- Session tokens: the sum of `transcript_usage` over the sessions, as context tokens and output tokens. Each message id counts once.
- Output, Markdown and nothing else, in this order:
  ```
  | measure | value |
  |---|---|
  | operator messages | <n> |
  | gate and ruling events | <n> |
  | operator time, minutes | <m, one decimal> (<s> sittings) |
  | elapsed, hours | <h, two decimals> |
  | session tokens | <c> context, <o> output |
  ```
- About 90 lines. The module docstring says what the report is for and names `docs/benchmark.md`.

**B. `tests/factory/test_benchmark.py`, a new file.** It covers each part of the operator-message rule: `typed`, `queued`, a text-block prompt, and an older record with no `promptSource` all count. `tool_result`, `isMeta`, `isSidechain`, `system`, `sdk` and a no-source record starting with `<` do not. It also covers the 15-minute boundary (exactly 900 s stays in the sitting, 901 s starts a new one), the one-minute addition, store events outside `DECISIONS` (not interactions, but counted for elapsed), a message id repeated across records (counted once), and the three refusals. It changes no existing test.

**C. `docs/benchmark.md`, a new page.** It is written to `docs/writing.md`, for a technical reader new to the project, and holds exactly these eight `##` headings, in order. Each quoted phrase below appears in the page word for word, because acceptance reads it.

1. `## What the benchmark compares`. The question is whether the factory beats one plain Claude Code session at turning a real issue into a correct fix, and at what cost in operator attention. It names the two arms (the factory arm and the baseline arm), the score, and the four measures. It links `[docs/north-star.md](north-star.md)`.
2. `## Choosing the tasks`.
   - The listing command from Evidence, with `--limit 400`.
   - The filters, in order. (1) Exactly one closing issue. (2) The PR adds or changes at least one file whose path contains `test`. Those files are "the PR's tests". (3) The issue's title and body hold no patch (no line starting `diff --git`, `@@`, `+++ ` or `--- a/`) and no link to the PR. (4) The PR's tests fail at the parent commit and pass at the merge commit, run with upstream's test command. The parent commit is "the first parent" of the PR's merge commit.
   - Take the "10 most recently merged" PRs that pass, as of a cut-off date fixed before the first task starts. Record the date in the benchmark's issue. Number the tasks 1 to 10, newest first.
3. `## Keeping the arms blind`.
   - Each arm's checkout is made with `git init -b main`, then "git fetch --depth 1" of the upstream URL at the parent commit, then `git reset --hard FETCH_HEAD`. No remote is added, so later commits, the fix's among them, are not in the checkout and cannot be fetched by name.
   - The task text is `# <issue title>`, a blank line, this preface, a blank line, then the issue body. Comments are not included. The preface reads: "Fix the issue below in this checkout. Work only from this checkout and the issue's text: do not look up the issue, its pull request or this project's repository online, and do not read any other copy of this project on this machine." Both arms get this file unchanged.
   - The operator does not open the PR, its diff or its tests until both arms of the task have ended.
   - Odd-numbered tasks run the factory arm first and even-numbered tasks run the baseline first, so whatever the operator learns from the first arm falls on each arm equally often.
   - The audit, after both arms end: `grep -rlF -e pull/<PR> -e issues/<issue> -e <first 12 characters of the merge commit> -e nanobot-upstream ~/.claude/projects/*bench-<PR>-*/`. Any hit marks that arm "leaked". The operator also reads each `WebFetch` or `WebSearch` call and each `gh` or `git fetch` command in those transcripts. One that reached the issue, the PR or upstream's later code marks the arm leaked, and the review says which call. A leaked arm is reported and not scored.
4. `## Running a task`. Checkouts are `~/bench/bench-<PR>-factory` and `~/bench/bench-<PR>-plain`, outside every live repository.
   - Factory arm: in its checkout, `export FACTORY_INSTANCE=$PWD/.factory FACTORY_STATE=$PWD/.factory/state`, with both of "FACTORY_INSTANCE" and "FACTORY_STATE" named. Then follow README's "Adopting the factory in a repo" with `--repo-name bench-<PR>-factory`. Take `gate_commands` and `environment_sync` from upstream's CI configuration at the parent commit, and `models` from this repository's `.factory/instance.yaml`. Write `context.md` from upstream's own README and CI only. File the task with `factory ticket new --file`. Take it through intake and the build as any real ticket, from a shell or a runner session.
   - Baseline arm: start `claude --model <model>` in its checkout, where the model is the one this repository's `instance.yaml` "gives the implementer". Paste the task text. Review the result the way you review a merge: read the diff, ask for changes or accept. Commit the result.
   - Both arms: no hand edits to code. In the factory arm, a gate edit or ruling is allowed and the scorecard counts it as an intervention or decision. An arm ends when the ticket closes or the operator accepts the session's result. The operator may instead abandon it, and the result is then scored as it stands.
5. `## Scoring a task`. After both arms end, in each arm's checkout:
   - `git fetch --depth 1 <upstream URL> <merge commit>`;
   - `git checkout FETCH_HEAD -- <the PR's tests>` over the arm's result (the factory arm's `main`, the baseline's committed tree);
   - upstream's test command on those files.

   The arm passes when the command exits 0. Keep the command's last line for the review.
6. `## The measures`. One table, with a row per measure and a column per arm, giving each one's source:
   - operator decisions: the scorecard's "Operator decisions and interventions per change" against the baseline's operator messages after the first;
   - operator time: `python -m factory.benchmark` for both arms, the factory arm with `--store` and its runner sessions;
   - tokens: the scorecard's tokens per change plus the runner sessions' tokens, against the baseline's session tokens;
   - wall time: the scorecard's lead time, with its summed run time beside it, against the baseline's elapsed time.

   It gives `factory stats --scorecard --store $FACTORY_STATE --since <the day the task started> --transcripts ~/.claude/projects` and `python -m factory.benchmark` with where each transcript is found. A session's transcript is `<session id>.jsonl` under `~/.claude/projects/<the session's start directory, with / and . as ->`. It states the operator-message rule, and the sittings rule as "more than 15 minutes" apart starts a new sitting and each sitting adds one minute. It says, in these words, that operator time "measures interactions, not attention" and "undercounts reading and review time". It names the three things the sittings rule misses (Answer 2): reading before a sitting's "first interaction", review without typing, and waits inside a sitting, which it counts as attention.
7. `## Putting a result in a review`.
   - Results go in the next review, `docs/reviews/<date>.md`. They are not part of this page.
   - Section 5 gets one row for the benchmark's issue. Under it goes a subsection with one block per task: the PR number, then for each arm whether it passed, failed or leaked, the test command's last line, and the two commands' outputs pasted as printed.
   - No number is typed or adjusted. A total, median or comparison across tasks is written "not yet computed".
   - The repository is public: name upstream PRs by number and name no private product. It links `[docs/reviews/TEMPLATE.md](reviews/TEMPLATE.md)`.
8. `## Spend`. One full run is about "10 factory intakes and builds" and "10 plain sessions". It was approved at the spec gate of the ticket that added this page. A larger or repeated run is a new decision.

**D. README.** It grows by exactly one net line, from 1,224 to 1,225.

- "Where things live": a new row after the `STATUS.md`, `docs/reviews/` row: ``| `docs/benchmark.md` | The upstream benchmark's method: choosing the tasks, keeping the factory and a plain session blind to the fix, scoring by the fix's own tests, and putting a result in a review; `python -m factory.benchmark` computes each arm's operator time from timestamps, and has not yet run on a benchmark task |``.
- "What depends on Claude Code": reword the `factory/cost.py` row in place to ``| Token cost per role (`factory/cost.py`), and the benchmark's operator time (`factory/benchmark.py`) | yes | read Claude Code's transcript files: the Workflow tool's, and for the benchmark a session's |``. Keep the "Six pieces assume Claude Code" sentence and every other row as they are.
- The status header's date becomes the merge date, in place.

## Tests to change

None. No Decision overturns existing behaviour. No test enumerates `factory/` modules or reads README's rows: the only README mentions in `tests/factory/` are fixture repos writing their own README (`_fixtures.py:478`, `test_harness_lock.py:253`, `:274`).

=== specs/factory-stats/spec.md
## ADDED Requirements

### Requirement: python -m factory.benchmark reports an arm's operator measures from timestamps
`python -m factory.benchmark [--store PATH] [SESSION]...` MUST print, for the session transcripts and the store given, the operator messages, the store's gate and ruling events, the operator time counted in sittings, the elapsed time and the sessions' tokens, and SHALL write nothing.

#### Scenario: A plain session's transcript gives its operator messages, operator time, elapsed time and tokens
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper. Of the plain session's eleven parseable records, three are operator messages, at 10:00, 10:15 (queued) and 10:40. They form a sitting of 15 minutes plus one minute and a sitting of one minute. Its first record is at 10:00:00 and its last at 10:41:00. Message `m1` is written twice and counts once.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0060-fixture.sh <<'EOF'
# Sourced from the repo root: writes a plain session's transcript, $F/base.jsonl, a runner
# session's transcript, $F/runner.jsonl, a throwaway store's event log, $F/store/log/, and a
# directory with no log, $F/nolog. Leaves F set.
F=$(cd "$(mktemp -d)" && pwd -P); mkdir -p $F/store/log $F/nolog
u() { printf '{"type": "user", "timestamp": "%s"%s, "message": {"role": "user", "content": %s}}\n' "$@"; }
a() { printf '{"type": "assistant", "timestamp": "%s", "message": {"id": "%s", "model": "claude-opus-5-5", "usage": {"input_tokens": %s, "cache_read_input_tokens": %s, "cache_creation_input_tokens": 0, "output_tokens": %s}}}\n' "$@"; }
{ u 2026-10-01T10:00:00Z ', "promptSource": "typed"' '"Fix the cron schedule bug."'
  a 2026-10-01T10:00:30Z m1 100 1000 10; a 2026-10-01T10:00:31Z m1 100 1000 20
  u 2026-10-01T10:01:00Z '' '[{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]'
  u 2026-10-01T10:02:00Z ', "isMeta": true' '"<local-command-caveat>x</local-command-caveat>"'
  u 2026-10-01T10:03:00Z ', "promptSource": "system"' '"<task-notification>done</task-notification>"'
  u 2026-10-01T10:05:00Z ', "isSidechain": true, "promptSource": "typed"' '"a subagent prompt"'
  echo 'not json'
  u 2026-10-01T10:15:00Z ', "promptSource": "queued"' '"Also keep the old schedule."'
  a 2026-10-01T10:20:00Z m2 50 2000 40
  u 2026-10-01T10:40:00Z '' '"Looks right; done."'
  u 2026-10-01T10:41:00Z '' '"<command-name>/exit</command-name>"'; } > $F/base.jsonl
{ u 2026-10-02T09:00:10Z ', "promptSource": "typed"' '[{"type": "text", "text": "File this issue and drive it."}]'
  u 2026-10-02T09:49:30Z ', "promptSource": "typed"' '"Approve the spec."'
  a 2026-10-02T09:49:40Z m3 10 500 5
  a 2026-10-02T12:05:00Z m4 20 600 7; } > $F/runner.jsonl
ev() { printf '{"ts": "%s", "event": "%s", "ticket": "T-0001"}\n' "$1" "$2"; }
{ ev 2026-10-02T09:00:00+00:00 ticket.created; ev 2026-10-02T09:50:00+00:00 approval.recorded
  ev 2026-10-02T11:00:00+00:00 human.resolved; ev 2026-10-02T12:00:00+00:00 merge.done; } > $F/store/log/2026-10.jsonl
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0060-fixture.sh && .venv/bin/python -m factory.benchmark $F/base.jsonl; echo "exit=$?")`
- THEN it prints exactly these eight lines, one per line: `| measure | value |`, `|---|---|`, `| operator messages | 3 |`, `| gate and ruling events | 0 |`, `| operator time, minutes | 17.0 (2 sittings) |`, `| elapsed, hours | 0.68 |`, `| session tokens | 3150 context, 60 output |`, `exit=0`

#### Scenario: A factory arm's store events and runner session give one operator time
Needs the GIVEN block of "A plain session's transcript gives its operator messages, operator time, elapsed time and tokens" run once. The runner session has two operator messages, at 09:00:10 and 09:49:30. The store has an approval at 09:50:00 and a ruling at 11:00:00. So the sittings are 09:00:10 alone, 09:49:30 to 09:50:00, and 11:00:00 alone: 1, 1.5 and 1 minutes. Its `ticket.created` and `merge.done` are not interactions, but they count for elapsed time, which runs from the store's 09:00:00 to the session's 12:05:00.
- WHEN `(. ${TMPDIR:-/tmp}/t0060-fixture.sh && .venv/bin/python -m factory.benchmark --store $F/store $F/runner.jsonl; echo "exit=$?")`
- THEN it prints exactly these eight lines, one per line: `| measure | value |`, `|---|---|`, `| operator messages | 2 |`, `| gate and ruling events | 2 |`, `| operator time, minutes | 3.5 (3 sittings) |`, `| elapsed, hours | 3.08 |`, `| session tokens | 1130 context, 12 output |`, `exit=0`

### Requirement: python -m factory.benchmark refuses input it cannot read
`python -m factory.benchmark` MUST exit 2 with a message on stderr, writing nothing, when it is given neither a store nor a session, a session that is not a file, or a store with no `log/` directory.

#### Scenario: The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing
Needs the GIVEN block of "A plain session's transcript gives its operator messages, operator time, elapsed time and tokens" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0060-fixture.sh && S0=$(find $F -type f -exec cksum {} + | sort | cksum); r() { e=$(.venv/bin/python -m factory.benchmark "$@" 2>&1 >/dev/null); echo "$?$([ -n "$e" ] && echo +msg)"; }; echo "none=$(r) missing=$(r $F/missing.jsonl) nolog=$(r --store $F/nolog) store=$([ "$(find $F -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `none=2+msg missing=2+msg nolog=2+msg store=unchanged`

### Requirement: The harness suite passes with the benchmark report, and no existing test file changes
The harness suite SHALL pass with this change, and the change MUST modify or delete no existing file under `tests/`.

#### Scenario: The suite passes and no existing test file is modified or deleted
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0060-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=MD main...HEAD -- tests)`
- THEN it prints one line, which reports a number of passed tests and no `failed` or `error`, and nothing after it

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: docs/benchmark.md holds the upstream benchmark's method
`docs/benchmark.md` MUST give the upstream benchmark's method under its eight sections: how tasks are chosen, how the arms are kept blind, how each arm is run, how a task is scored, what each measure is and where it comes from, how a result goes into a review, and the spend, and SHALL say that operator time measures interactions, not attention, undercounts reading and review time, and is counted in sittings.

#### Scenario: The benchmark page has its eight sections in order
- WHEN `(grep '^## ' docs/benchmark.md 2>/dev/null; echo "exit=$?")`
- THEN it prints exactly these nine lines, one per line: `## What the benchmark compares`, `## Choosing the tasks`, `## Keeping the arms blind`, `## Running a task`, `## Scoring a task`, `## The measures`, `## Putting a result in a review`, `## Spend`, `exit=0`

#### Scenario: The benchmark page states its selection, blinding, setup, measures, review and spend rules
- WHEN `(h() { for p in "$@"; do grep -qF -- "$p" docs/benchmark.md 2>/dev/null || { echo no; return; }; done; echo yes; }; echo "caveat=$(h 'measures interactions, not attention' 'undercounts reading and review time') selection=$(h 'first parent' '10 most recently merged') blind=$(h 'git fetch --depth 1' 'nanobot-upstream' 'leaked') arms=$(h 'FACTORY_STATE' 'FACTORY_INSTANCE' 'gives the implementer') measures=$(h 'python -m factory.benchmark' 'factory stats --scorecard' 'more than 15 minutes' 'first interaction') review=$(h 'docs/reviews/' 'not yet computed') spend=$(h '10 factory intakes and builds' '10 plain sessions')")`
- THEN it prints exactly `caveat=yes selection=yes blind=yes arms=yes measures=yes review=yes spend=yes`

#### Scenario: No relative link in the benchmark page is broken
- WHEN `(f=docs/benchmark.md; [ -f $f ] || { echo "$f missing"; exit 0; }; n=0; bad=0; for l in $(grep -oE '\]\([^)#]+\)' $f | sed -E 's/^\]\(//; s/\)$//' | grep -v '^[a-z]*:'); do n=$((n+1)); [ -e "docs/$l" ] || bad=$((bad+1)); done; echo "relative=$([ $n -gt 0 ] && echo some || echo none) broken=$bad")`
- THEN it prints exactly `relative=some broken=0`

### Requirement: README points to the benchmark's method and its report
README's "Where things live" MUST have one row for `docs/benchmark.md`, and "What depends on Claude Code" SHALL name `factory/benchmark.py` in the row it shares with `factory/cost.py`.

#### Scenario: README names the benchmark page and puts its report in the cost row
- WHEN `(W=$(sed -n '/^## Where things live$/,/^## Related work and history$/p' README.md | grep '^| '); D=$(sed -n '/^### What depends on Claude Code$/,/^## Terms used on this page$/p' README.md | grep '^| '); echo "where=$(printf '%s\n' "$W" | grep -c 'docs/benchmark.md') depends=$(printf '%s\n' "$D" | grep -c 'factory/benchmark.py') shared=$(printf '%s\n' "$D" | grep 'factory/benchmark.py' | grep -c 'factory/cost.py')")`
- THEN it prints exactly `where=1 depends=1 shared=1`

=== verification.md
## Acceptance

- A plain session's transcript gives its operator messages, operator time, elapsed time and tokens → NEW. Today it prints `/Users/dphang/dev/spec-factory/.venv/bin/python: No module named factory.benchmark`, then `exit=1`.
- A factory arm's store events and runner session give one operator time → NEW. Today it prints the same `No module named factory.benchmark` line, then `exit=1`.
- The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing → NEW. Today it prints `none=1+msg missing=1+msg nolog=1+msg store=unchanged`: each call fails with exit 1 on the missing module, not 2 on a refusal.
- The suite passes and no existing test file is modified or deleted → REGRESSION.
- The benchmark page has its eight sections in order → NEW. Today it prints only `exit=2`, because the file does not exist.
- The benchmark page states its selection, blinding, setup, measures, review and spend rules → NEW. Today it prints `caveat=no selection=no blind=no arms=no measures=no review=no spend=no`.
- No relative link in the benchmark page is broken → NEW. Today it prints `docs/benchmark.md missing`.
- README names the benchmark page and puts its report in the cost row → NEW. Today it prints `where=0 depends=0 shared=0`.

README's line budget is checked by current truth's harness-docs scenario "README is at most 1,225 lines", which the gate's `factory truth check` replays on this change. It passes today, at 1,224 lines, and must pass after, at 1,225.

How I checked, on the dev checkout at `main` `9e8f4d3`:
- I ran each NEW WHEN above verbatim, under bash and zsh, through the briefing's wrapper, and saw the "Today" output given.
- I ran the three factory-stats WHENs, after the GIVEN block, in a copy of `main` with the prototype installed as `factory/benchmark.py`, under bash and zsh, through the briefing's wrapper. They printed the THEN lines exactly.
- I replayed this change's eight scenarios with `factory truth check` itself, from `main`'s `bin/factory`, with `--skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'` as the gate passes it. The store was a scratch store whose current truth held only these two delta parts. The checkout was a `git clone --shared` of `main` with one commit on top: the prototype as `factory/benchmark.py`, design part D's two README rows, and a stub `docs/benchmark.md` holding the eight headings, the quoted phrases and two links (a stub, so this checks the scenarios, not the page). It printed `8 scenarios: 7 passed, 0 failed, 1 skipped`, the skip being the suite scenario. From `~/dev/spec-factory` on `main` the same run printed `0 passed, 7 failed, 1 skipped`.
- I replayed current truth's harness-docs and factory-stats from the live store, as the gate would, in that clone and on `main`. Both printed `114 scenarios: 110 passed, 0 failed, 4 skipped`, and "README is at most 1,225 lines" passed at 1,225 lines in the clone. So the README edits break no existing check.
- I did not run the suite scenario: the gate runs the suite on every change, and the gate's replay skips this scenario because its WHEN holds the suite command.

## PR description (the implementer's output)

Sub-ticket: T-0060.1, `/Users/dphang/dev/spec-factory/.factory/store/tickets/T-0060.1.yaml`. Parent: T-0060, spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0060/v2.md`.
Branch: `factory/T-0060.1`. Head: `37c867e6881221552f4b86efe47fcbb04fabd929`, one commit on base `9e8f4d3`.

## What changed

This change adds the method for the upstream benchmark and a command that computes one of its measures. The upstream benchmark gives the same real Nanobot bug reports to the factory and to one plain Claude Code session, then scores each fix by that pull request's own tests. Before this change nothing wrote down how to run it fairly. Nothing could compute operator time either: the operator's attention, derived from timestamps.

**A. `factory/benchmark.py`, run as `python -m factory.benchmark [--store PATH] [SESSION.jsonl]...`.** A new module of 107 lines. It reads the session transcripts and the store's event log it is given, and writes nothing. It prints a seven-row Markdown table:
- operator messages;
- gate and ruling events, meaning the store's `approval.recorded` and `human.resolved` events;
- operator time in sittings;
- elapsed hours;
- session tokens.

It reuses `factory.cost`'s `_records`, `_log_records`, `_user_text`, `_when` and `transcript_usage`, and takes the decision events from `factory.stats.DECISIONS`. It copies none of them. Refusals exit 2 with one stderr line starting `factory.benchmark: ` and nothing on stdout. Each refusal is checked before anything is printed:
- no `--store` and no session;
- a session that is not a file, named in the message;
- a store with no `log/` directory, named in the message.

**B. `tests/factory/test_benchmark.py`, a new file with 11 tests.** These parts of the operator-message rule are covered: `typed`, `queued` and `suggestion_accepted` count, as do a text-block prompt and an older record with no `promptSource`. A `tool_result` does not count, with or without `promptSource`. Nor do `isMeta`, `isSidechain`, `system`, `sdk`, a no-source record starting with `<`, or an unparseable line. The tests also cover these:
- the 900 s boundary: exactly 900 s stays in one sitting, and 901 s starts a new one;
- the one-minute addition;
- store events outside `DECISIONS`, which are not interactions but count for elapsed time;
- a session message and a store decision sharing one sitting;
- a message id repeated across records, counted once;
- `-` for elapsed time when nothing has a timestamp;
- the three refusals.

The tests run the module as a subprocess from the checkout root. `tests/factory` is itself a package named `factory`, so `factory.benchmark` cannot be imported by name in-process.

**C. `docs/benchmark.md`, a new page.** It has the eight `##` sections the spec names, in order. Each quoted phrase that acceptance reads sits on one line. It links `north-star.md`, `reviews/TEMPLATE.md` and `../README.md`.

**D. README.** It grows by one net line, from 1,224 to 1,225, filling its budget. "Where things live" gains the spec's `docs/benchmark.md` row, verbatim, after the `STATUS.md`, `docs/reviews/` row. In "What depends on Claude Code", the `factory/cost.py` row is reworded in place to the spec's text, verbatim. The status header's date is already 2026-10-26, today's date, so it is unchanged. If the merge happens on a later day, that date needs bumping at merge.

## Acceptance results

Each WHEN ran verbatim under `bash`, through the briefing's wrapper, from the worktree, after the spec's GIVEN block and `uv sync --frozen`. Scratch copies: `scratch/given.sh`, `scratch/whens.txt`, `scratch/run_acc.sh`. Outputs are in `scratch/before.txt` and `scratch/after.txt`.

| Scenario | Kind | Before (base `9e8f4d3`) | After (`37c867e`) |
|---|---|---|---|
| A plain session's transcript gives its operator messages, operator time, elapsed time and tokens | NEW | `…/.venv/bin/python: No module named factory.benchmark`, `exit=1` | `\| measure \| value \|`, `\|---\|---\|`, `\| operator messages \| 3 \|`, `\| gate and ruling events \| 0 \|`, `\| operator time, minutes \| 17.0 (2 sittings) \|`, `\| elapsed, hours \| 0.68 \|`, `\| session tokens \| 3150 context, 60 output \|`, `exit=0`: matches the THEN exactly |
| A factory arm's store events and runner session give one operator time | NEW | `No module named factory.benchmark`, `exit=1` | `operator messages \| 2`, `gate and ruling events \| 2`, `operator time, minutes \| 3.5 (3 sittings)`, `elapsed, hours \| 3.08`, `session tokens \| 1130 context, 12 output`, `exit=0`, under the same two header lines: matches the THEN exactly |
| The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing | NEW | `none=1+msg missing=1+msg nolog=1+msg store=unchanged` | `none=2+msg missing=2+msg nolog=2+msg store=unchanged`: matches |
| The suite passes and no existing test file is modified or deleted | REGRESSION | not run before, per the process | `669 passed in 115.95s (0:01:55)`, with nothing after it, so the `git diff --diff-filter=MD … -- tests` lists no file: matches |
| The benchmark page has its eight sections in order | NEW | `exit=2` | the eight headings in order, then `exit=0`: matches |
| The benchmark page states its selection, blinding, setup, measures, review and spend rules | NEW | `caveat=no selection=no blind=no arms=no measures=no review=no spend=no` | `caveat=yes selection=yes blind=yes arms=yes measures=yes review=yes spend=yes`: matches |
| No relative link in the benchmark page is broken | NEW | `docs/benchmark.md missing` | `relative=some broken=0`: matches |
| README names the benchmark page and puts its report in the cost row | NEW | `where=0 depends=0 shared=0` | `where=1 depends=1 shared=1`: matches |

Every "before" output matched verification.md's "Today" line. The first two differ only in the checkout path that the venv's Python prints.

The gates ran on `37c867e`, each exactly as written:
- `git diff --check main...HEAD` printed nothing and exited 0, so no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `669 passed in 119.01s (0:01:59)` and exited 0.
- `bin/factory truth check --store … --skip-when-contains '…'` printed `347 scenarios: 306 passed, 0 failed, 41 skipped; wall time 128 s` and exited 0. That includes `PASS harness-docs: README is at most 1,225 lines` at 1,225 lines, and `PASS harness-docs: Where things live has a row for each new file`. This change's own seven scenarios were SKIPPED there, "in the approved delta of T-0060, which that ticket's verifier checks". That is why I ran them myself, as the table above shows.

## Tests added/changed

- Added: `tests/factory/test_benchmark.py`, 11 tests, which cover design part B as listed under "What changed". Before the module existed, all 11 failed, because the subprocess could not find `factory.benchmark`. After, all 11 pass.
- Changed: none. The parent's "Tests to change" is none.

## Known gaps and uncertainties

- **The baseline's operator decisions need one hand subtraction.** The page takes this measure as "the operator messages after the first", as design part C.6 specifies. The report prints all operator messages, so a reviewer must subtract one by hand. That sits uneasily with the page's rule that "No number is typed or adjusted". I followed the spec and did not add a row the spec does not define. A reviewer could fix it with a later row such as "operator messages after the first", or by pasting the raw count and stating the rule.
- **`factory.cli` is imported indirectly.** `benchmark.py` does not import `factory.cli`, as the spec requires. But `from factory.stats import DECISIONS` loads `factory.stats`, which imports `factory.cli` for `ROLES` (`factory/stats.py:25`). So the module still loads `cli` at import. I followed the spec's instruction to take `DECISIONS` from `factory.stats` rather than copy it.
- **The module is 107 lines, not "about 90".** The docstring states the full counting rule, and the refusals and table rows are written one per line.
- **A bad timestamp is not caught.** A record or event with a timestamp that `datetime.fromisoformat` cannot parse raises `ValueError`, giving a traceback and exit 1. I left this uncaught rather than skip the record silently. Claude Code and the store both write ISO timestamps.
- **Sittings are always plural.** The output prints `1 sittings`, keeping the spec's `<s> sittings` format literally.
- **Upstream's URL and test command are not verified or named.** The page names upstream as `https://github.com/HKUDS/nanobot`, from the spec's `gh pr list --repo HKUDS/nanobot`. I did not fetch it. The page defines "upstream's test command" as the one upstream's CI configuration runs at that commit, without naming a command. I did not read upstream's CI.
- **The factory arm's procedure is untried.** Following the spec's Risk, its first trial is the first benchmark task.
- **Only `bash` was used.** I ran every scenario under bash, the shell the truth check replays with. I did not re-run under zsh, which the spec writer also did.
- **`factory:` markers added:** none.

## Out-of-scope observations

- The process says to read `AGENTS.md`, but this repository has none, at the worktree root or at `~/dev/spec-factory`. I worked from the briefing, the spec, `docs/coding.md` and `docs/writing.md`.
- Gate 3 printed `folded: T-0060` when run from this worktree, yet skipped T-0060's scenarios as "in the approved delta". That is consistent with how the gate treats an open ticket's delta. It does mean the gate itself never checks this change's scenarios before the ticket's verifier runs.

## Protected paths

`factory/benchmark.py`, declared in the parent's Risk. The change also adds `tests/factory/test_benchmark.py` as a new file, as part B specifies. No existing test file changed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All eight acceptance commands print their THEN lines exactly, and the suite and the truth check pass on the commit. The one design tension, the hand subtraction for the baseline's decisions, comes from the spec and is disclosed above.
ESCALATIONS: none

## Diff `9e8f4d3c14d352bf058b1532814d5ff83b6dd14e...37c867e6881221552f4b86efe47fcbb04fabd929`

diff --git a/README.md b/README.md
index 754076a..bb071b6 100644
--- a/README.md
+++ b/README.md
@@ -110,7 +110,7 @@ Most of the factory is plain files and a Python program. Six pieces assume Claud
 | Role agents (`agents/`, copied into a target's `.claude/agents/`) | yes | Claude Code agent definitions, with a tool list per role; Claude Code registers them only when a session starts |
 | Role processes of `factory drive` (`factory/drive.py`) | yes | each role runs as one headless `claude -p` process with `--output-format json` and `--permission-mode auto`, its role's prompt file, model and optional `--effort`, and its tool limits given by `--tools` and `--allowedTools` |
 | Model names (`models` in `instance.yaml`) | yes | Claude model aliases |
-| Token cost per role (`factory/cost.py`) | yes | reads the Workflow tool's transcript files |
+| Token cost per role (`factory/cost.py`), and the benchmark's operator time (`factory/benchmark.py`) | yes | read Claude Code's transcript files: the Workflow tool's, and for the benchmark a session's |
 | Catch and cost per role (`factory stats`, `factory/stats.py`) | no | reads the store's files with no Claude Code; reads Claude Code's transcript files only when given `--transcripts` |
 | A workflow run's token record (`run finish --transcripts`) | yes | reads the token usage in the transcript Claude Code keeps for the run's agent, under `~/.claude/projects` |
 
@@ -1138,6 +1138,7 @@ has not been tried, is in `docs/design.md`, "Running on another agent host".
 | `docs/prompts/` | Each role's prompt block, copied verbatim from the design doc by hand; `00-preamble.md` goes at the top of every role |
 | `docs/north-star.md` | What the factory is for, what it will not trade away, and where it is heading; changes to it are the operator's decision |
 | `STATUS.md`, `docs/reviews/` | The latest scorecard, focus and queue, rewritten only at a review; each review, written from `docs/reviews/TEMPLATE.md`, the first being the hand-counted baseline of 2026-10-19 |
+| `docs/benchmark.md` | The upstream benchmark's method: choosing the tasks, keeping the factory and a plain session blind to the fix, scoring by the fix's own tests, and putting a result in a review; `python -m factory.benchmark` computes each arm's operator time from timestamps, and has not yet run on a benchmark task |
 | `CONTRIBUTING.md` | How work is proposed and chosen: issue, factory ticket, spec gate, under the north star's rule for factory work |
 | `docs/principles.md` | The fourteen learned principles, each with its incident, citation and implementing mechanism |
 | `docs/decided-against.md` | Approaches tried or offered and dropped, with the evidence and what would reopen each |
diff --git a/docs/benchmark.md b/docs/benchmark.md
new file mode 100644
index 0000000..1ac5e10
--- /dev/null
+++ b/docs/benchmark.md
@@ -0,0 +1,195 @@
+# The upstream benchmark
+
+This page is how to test, on outside work, whether the spec factory is worth its cost. The factory
+is the pipeline of AI agent roles in this repository that turns a written request into merged code.
+The operator is the person who approves each spec (the plan an implementer builds from) and handles
+every stop. The benchmark gives the factory and one ordinary Claude Code session the same real bug
+reports, and scores each fix by the tests its project's own maintainers wrote for it. It is written
+for the operator who runs it and for a technical reader judging its results.
+
+## What the benchmark compares
+
+The question is whether the factory beats one plain Claude Code session at turning a real issue into
+a correct fix, and at what cost in operator attention. The north star,
+[docs/north-star.md](north-star.md), names this test: it is the page that says what the factory is
+for and how it is measured.
+
+Each task is a merged fix pull request (PR) from the public upstream Nanobot project,
+`https://github.com/HKUDS/nanobot`. Its issue goes to two arms, each working from the same commit:
+
+| Arm | What does the work |
+|---|---|
+| The factory arm | The factory, on its own throwaway instance: intake, the spec gate and the build, as for any ticket |
+| The baseline arm | One plain Claude Code session, given the issue's text and reviewed by the operator |
+
+The score of an arm is whether the PR's own tests pass on its result. Beside the score, four measures
+give the cost of reaching it: operator decisions, operator time, tokens and wall time. "The measures"
+says where each comes from.
+
+## Choosing the tasks
+
+1. Fix a cut-off date before the first task starts, and record it in the benchmark's issue.
+2. List upstream's merged fix PRs:
+
+   ```sh
+   gh pr list --repo HKUDS/nanobot --state merged --search "fix in:title" --limit 400 \
+     --json number,title,mergedAt,closingIssuesReferences,files
+   ```
+
+3. Keep a PR merged before the cut-off only if it passes these filters, applied in this order:
+   1. It has exactly one closing issue.
+   2. It adds or changes at least one file whose path contains `test`. Those files are "the PR's
+      tests".
+   3. The issue's title and body hold no patch and no link to the PR. A patch is any line starting
+      `diff --git`, `@@`, `+++ ` or `--- a/`.
+   4. The PR's tests fail at the parent commit and pass at the merge commit, each run with upstream's
+      test command. The parent commit is the first parent of the PR's merge commit. Upstream's test
+      command is the one its CI configuration runs at that commit.
+4. Take the 10 most recently merged PRs that pass. Number them 1 to 10, newest first.
+
+The rule is fixed before any result is seen, so nobody picks tasks that favour one arm.
+
+## Keeping the arms blind
+
+An arm that sees the fix proves nothing about fixing. Five measures keep the fix out of both arms.
+
+1. **Checkouts hold only the parent commit.** Make each arm's checkout this way, with `<parent>` the
+   first parent of the merge commit:
+
+   ```sh
+   git init -b main
+   git fetch --depth 1 https://github.com/HKUDS/nanobot <parent>
+   git reset --hard FETCH_HEAD
+   ```
+
+   No remote is added. Later commits, the fix's among them, are not in the checkout and cannot be
+   fetched by name.
+2. **Both arms get the same task text.** Write it once per task, as `# <issue title>`, a blank line,
+   the preface below, a blank line, then the issue body. Leave out the issue's comments. The preface:
+
+   > Fix the issue below in this checkout. Work only from this checkout and the issue's text: do not
+   > look up the issue, its pull request or this project's repository online, and do not read any
+   > other copy of this project on this machine.
+
+   Give both arms this file unchanged.
+3. **The operator does not see the fix.** Do not open the PR, its diff or its tests until both arms
+   of the task have ended.
+4. **Arm order alternates.** Odd-numbered tasks run the factory arm first; even-numbered tasks run
+   the baseline arm first. Whatever the operator learns from the first arm then falls on each arm
+   equally often.
+5. **Each task ends with an audit.** After both arms end, search their transcripts:
+
+   ```sh
+   grep -rlF -e pull/<PR> -e issues/<issue> -e <first 12 characters of the merge commit> \
+     -e nanobot-upstream ~/.claude/projects/*bench-<PR>-*/
+   ```
+
+   Any file it lists marks that arm leaked. Then read each `WebFetch` or `WebSearch` call, and each
+   `gh` or `git fetch` command, in those transcripts. One that reached the issue, the PR or upstream's
+   later code also marks the arm leaked, and the review names the call. A leaked arm is reported and
+   not scored.
+
+## Running a task
+
+Each arm has its own checkout, outside every live repository: `~/bench/bench-<PR>-factory` and
+`~/bench/bench-<PR>-plain`. Make both as "Keeping the arms blind" says.
+
+**Factory arm.** In its checkout:
+
+1. Point every factory command in this shell at the checkout's own instance and store:
+
+   ```sh
+   export FACTORY_INSTANCE=$PWD/.factory FACTORY_STATE=$PWD/.factory/state
+   ```
+
+   With `FACTORY_INSTANCE` and `FACTORY_STATE` set, no command in this shell can reach a live
+   store, and the scorecard names the instance instead of printing a path.
+2. Follow README's "Adopting the factory in a repo" ([README.md](../README.md)), with
+   `--repo-name bench-<PR>-factory`. Take `gate_commands` and `environment_sync` from upstream's CI
+   configuration at the parent commit. Take `models` from this repository's `.factory/instance.yaml`.
+   Write `context.md` from upstream's own README and CI only.
+3. File the task text with `factory ticket new --file`.
+4. Take the ticket through intake and the build as any real ticket, from a shell or a runner session.
+   A runner session is a Claude Code session in which the operator drives the factory.
+
+**Baseline arm.** In its checkout, start `claude --model <model>`. The model is the one this
+repository's `.factory/instance.yaml` gives the implementer. Paste the task text. Review the result
+the way you review a merge: read the diff, then ask for changes or accept. Commit the result.
+
+**Both arms.** Make no hand edits to code. In the factory arm a gate edit or a ruling is allowed, and
+the scorecard counts it as an intervention or a decision. An arm ends when its ticket closes or when
+the operator accepts the session's result. The operator may instead abandon an arm; its result is
+then scored as it stands.
+
+## Scoring a task
+
+After both arms end, in each arm's checkout:
+
+```sh
+git fetch --depth 1 https://github.com/HKUDS/nanobot <merge commit>
+git checkout FETCH_HEAD -- <the PR's tests>
+```
+
+The checkout puts the PR's tests over the arm's result: the factory arm's `main`, or the baseline
+arm's committed tree. Then run upstream's test command on those files. The arm passes when the
+command exits 0. Keep the command's last line for the review.
+
+## The measures
+
+| Measure | Factory arm | Baseline arm |
+|---|---|---|
+| Operator decisions | the scorecard's "Operator decisions and interventions per change" | the operator messages after the first, from `python -m factory.benchmark`; filing a ticket is not a decision in the scorecard either |
+| Operator time | `python -m factory.benchmark --store $FACTORY_STATE` with the runner sessions' transcripts | `python -m factory.benchmark` with the session's transcript |
+| Tokens | the scorecard's tokens per change, plus the runner sessions' tokens from `python -m factory.benchmark` | the session tokens from `python -m factory.benchmark` |
+| Wall time | the scorecard's lead time, with its summed run time beside it | the elapsed time from `python -m factory.benchmark` |
+
+The scorecard is the north star's table of measures, printed by `factory stats`. For the factory
+arm, run it in the arm's shell, with `$R` the factory's runtime checkout:
+
+```sh
+$R/bin/factory stats --scorecard --store $FACTORY_STATE --since <the day the task started> \
+  --transcripts ~/.claude/projects
+```
+
+Run the report from the dev checkout, `~/dev/spec-factory`, at a commit that contains it:
+
+```sh
+uv run --frozen python -m factory.benchmark [--store $FACTORY_STATE] <session transcript>...
+```
+
+A session's transcript is `<session id>.jsonl` under
+`~/.claude/projects/<the session's start directory, with / and . as ->`. The report reads only the files it is given and writes nothing.
+
+**Operator messages.** An operator message is a `user` record that is not `isMeta` or `isSidechain`
+and holds no `tool_result`. Its `promptSource` must be `typed`, `queued` or `suggestion_accepted`. A
+record with no `promptSource`, as older transcripts write, counts when its text does not start with
+`<`. Task notifications, headless prompts and slash-command lines are not the operator.
+
+**Operator time.** Interactions are the operator messages and the store's spec approvals and
+rulings. Interactions are grouped into sittings: an interaction more than 15 minutes after the one
+before starts a new sitting. A sitting counts from its first interaction to its last, and each
+sitting adds one minute. Operator time is the sum, in minutes.
+
+Operator time measures interactions, not attention. It undercounts reading and review time. The
+sittings rule misses three things:
+
+- reading done before a sitting's first interaction;
+- review done without typing anything;
+- waits inside a sitting, which it counts as attention.
+
+## Putting a result in a review
+
+1. Results go in the next review, `docs/reviews/<date>.md`, written from
+   [docs/reviews/TEMPLATE.md](reviews/TEMPLATE.md). They are not part of this page.
+2. Section 5 of the review, "Experiments and side work", gets one row for the benchmark's issue.
+3. Under it goes a subsection with one block per task. Each block gives the PR number. Then, for
+   each arm: whether it passed, failed or leaked; the test command's last line; and the scorecard's
+   and the report's output, pasted as printed.
+4. No number is typed or adjusted. A total, median or comparison across tasks is written
+   "not yet computed", because no command computes it.
+5. This repository is public. Name upstream PRs by number, and name no private product.
+
+## Spend
+
+One full run is about 10 factory intakes and builds and 10 plain sessions. That spend was approved
+at the spec gate of the ticket that added this page. A larger or repeated run is a new decision.
diff --git a/factory/benchmark.py b/factory/benchmark.py
new file mode 100644
index 0000000..caff2b2
--- /dev/null
+++ b/factory/benchmark.py
@@ -0,0 +1,107 @@
+"""One arm's operator measures for the upstream benchmark, read from timestamps. Method: docs/benchmark.md.
+
+  python -m factory.benchmark [--store PATH] [SESSION.jsonl]...
+
+A SESSION is the Claude Code transcript of a session the operator typed into: the baseline arm's
+plain session, or the factory arm's runner sessions. --store is the factory arm's throwaway store.
+Prints a Markdown table of operator messages, the store's gate and ruling events, operator time,
+elapsed time and the sessions' tokens. Writes nothing.
+
+An operator message is a `user` record, not `isMeta` or `isSidechain` and holding no `tool_result`,
+whose `promptSource` is `typed`, `queued` or `suggestion_accepted`; a record with no `promptSource`
+counts when its text does not start with `<`. Interactions are the operator messages and the store's
+decision events (`factory.stats.DECISIONS`). Interactions no more than 15 minutes apart form one
+sitting, counted from its first interaction to its last plus one minute; operator time is the sum.
+It measures interactions, not attention, and undercounts reading and review time.
+"""
+from __future__ import annotations
+
+import argparse
+import os
+import sys
+
+from factory.cost import _log_records, _records, _user_text, _when, transcript_usage
+from factory.stats import DECISIONS
+
+PROMPT_SOURCES = ("typed", "queued", "suggestion_accepted")
+SITTING_GAP = 900  # seconds: a longer gap between interactions starts a new sitting
+SITTING_ADD = 60  # seconds added to each sitting
+
+
+def _operator_message(o: dict) -> bool:
+    text = _user_text(o)
+    if text is None or o.get("isMeta") or o.get("isSidechain") or not o.get("timestamp"):
+        return False
+    content = o["message"]["content"]
+    if isinstance(content, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in content):
+        return False
+    source = o.get("promptSource")
+    return source in PROMPT_SOURCES if source is not None else not text.startswith("<")
+
+
+def sittings(times: list) -> tuple[float, int]:
+    """(operator minutes, sittings) of a list of interaction times."""
+    seconds, count, start, prev = 0.0, 0, None, None
+    for t in sorted(times):
+        if prev is None or (t - prev).total_seconds() > SITTING_GAP:
+            if prev is not None:
+                seconds += (prev - start).total_seconds() + SITTING_ADD
+            start, count = t, count + 1
+        prev = t
+    if prev is not None:
+        seconds += (prev - start).total_seconds() + SITTING_ADD
+    return seconds / 60, count
+
+
+def report(store: str | None, sessions: list[str]) -> list[str]:
+    """The report's table rows, from a store's event log and session transcripts."""
+    messages = decisions = ctx = out = 0
+    interactions, stamps = [], []
+    for path in sessions:
+        for o in _records(path):
+            if o.get("timestamp"):
+                stamps.append(_when(o["timestamp"]))
+            if _operator_message(o):
+                messages += 1
+                interactions.append(_when(o["timestamp"]))
+        _, c, u = transcript_usage(path)
+        ctx, out = ctx + c, out + u
+    for e in _log_records(store) if store else ():
+        when = _when(e.get("ts"))
+        if when is not None:
+            stamps.append(when)
+        if e.get("event") in DECISIONS:
+            decisions += 1
+            if when is not None:
+                interactions.append(when)
+    minutes, count = sittings(interactions)
+    elapsed = f"{(max(stamps) - min(stamps)).total_seconds() / 3600:.2f}" if stamps else "-"
+    return ["| measure | value |", "|---|---|",
+            f"| operator messages | {messages} |",
+            f"| gate and ruling events | {decisions} |",
+            f"| operator time, minutes | {minutes:.1f} ({count} sittings) |",
+            f"| elapsed, hours | {elapsed} |",
+            f"| session tokens | {ctx} context, {out} output |"]
+
+
+def main(argv: list[str]) -> int:
+    ap = argparse.ArgumentParser(prog="factory.benchmark", description=__doc__.splitlines()[0])
+    ap.add_argument("--store")
+    ap.add_argument("sessions", nargs="*", metavar="SESSION.jsonl")
+    args = ap.parse_args(argv)
+    refusal = None
+    if args.store is None and not args.sessions:
+        refusal = "give --store, a session transcript, or both"
+    elif missing := [s for s in args.sessions if not os.path.isfile(s)]:
+        refusal = f"not a file: {missing[0]}"
+    elif args.store is not None and not os.path.isdir(os.path.join(args.store, "log")):
+        refusal = f"store has no log/ directory: {args.store}"
+    if refusal:
+        print(f"factory.benchmark: {refusal}", file=sys.stderr)
+        return 2
+    print("\n".join(report(args.store, args.sessions)))
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1:]))
diff --git a/tests/factory/test_benchmark.py b/tests/factory/test_benchmark.py
new file mode 100644
index 0000000..9b47be2
--- /dev/null
+++ b/tests/factory/test_benchmark.py
@@ -0,0 +1,174 @@
+"""`python -m factory.benchmark`, one arm's operator measures for the upstream benchmark (T-0060 part B).
+
+- An operator message is a `user` record, not `isMeta` or `isSidechain`, holding no `tool_result`,
+  whose `promptSource` is `typed`, `queued` or `suggestion_accepted`; with no `promptSource`, one
+  whose text does not start with `<`.
+- Interactions are the operator messages and the store's `approval.recorded` and `human.resolved`
+  events. Interactions more than 900 s apart start a new sitting; each sitting counts its span plus
+  60 s.
+- Elapsed covers every timestamped session record and every store event; tokens count each message
+  id once.
+- No input, a session that is not a file and a store with no `log/` are refused with exit 2.
+
+The module runs as a subprocess from the harness checkout: tests/factory is itself a package named
+`factory`, so the harness package is not importable by that name here.
+"""
+from __future__ import annotations
+
+import json
+import subprocess
+import sys
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parents[2]
+
+
+def _jsonl(path: Path, records: list) -> Path:
+    path.parent.mkdir(parents=True, exist_ok=True)
+    path.write_text("".join((r if isinstance(r, str) else json.dumps(r)) + "\n" for r in records))
+    return path
+
+
+def _user(ts: str, content, **extra) -> dict:
+    return {"type": "user", "timestamp": ts, **extra, "message": {"role": "user", "content": content}}
+
+
+def _reply(ts: str, mid: str, ctx: int, out: int) -> dict:
+    return {"type": "assistant", "timestamp": ts, "message": {"id": mid, "model": "claude-opus-5-5", "usage": {
+        "input_tokens": ctx, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": out}}}
+
+
+def _event(ts: str, event: str) -> dict:
+    return {"ts": ts, "event": event, "ticket": "T-0001"}
+
+
+def bench(*argv: str) -> subprocess.CompletedProcess:
+    return subprocess.run([sys.executable, "-m", "factory.benchmark", *argv], capture_output=True, text=True,
+                          cwd=ROOT)
+
+
+def measures(cp: subprocess.CompletedProcess) -> dict[str, str]:
+    assert cp.returncode == 0, cp.stderr
+    lines = cp.stdout.splitlines()
+    assert lines[:2] == ["| measure | value |", "|---|---|"]
+    return {k: v for k, v in (ln.strip("| ").split(" | ") for ln in lines[2:])}
+
+
+# --- the operator-message rule ----------------------------------------------------------------------
+
+def test_typed_queued_accepted_text_block_and_older_prompts_count(tmp_path):
+    s = _jsonl(tmp_path / "s.jsonl", [
+        _user("2026-10-01T10:00:00Z", "typed", promptSource="typed"),
+        _user("2026-10-01T10:01:00Z", "queued", promptSource="queued"),
+        _user("2026-10-01T10:02:00Z", "accepted", promptSource="suggestion_accepted"),
+        _user("2026-10-01T10:03:00Z", [{"type": "text", "text": "a text block"}], promptSource="typed"),
+        _user("2026-10-01T10:04:00Z", "an older prompt with no promptSource"),
+    ])
+    assert measures(bench(str(s)))["operator messages"] == "5"
+
+
+def test_tool_results_meta_sidechain_system_sdk_and_bracketed_records_do_not_count(tmp_path):
+    s = _jsonl(tmp_path / "s.jsonl", [
+        _user("2026-10-01T10:00:00Z", "the one prompt", promptSource="typed"),
+        _user("2026-10-01T10:01:00Z", [{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]),
+        _user("2026-10-01T10:02:00Z", [{"type": "tool_result", "tool_use_id": "t2", "content": "ok"}],
+              promptSource="typed"),
+        _user("2026-10-01T10:03:00Z", "caveat", isMeta=True, promptSource="typed"),
+        _user("2026-10-01T10:04:00Z", "a subagent prompt", isSidechain=True, promptSource="typed"),
+        _user("2026-10-01T10:05:00Z", "<task-notification>done</task-notification>", promptSource="system"),
+        _user("2026-10-01T10:06:00Z", "a headless prompt", promptSource="sdk"),
+        _user("2026-10-01T10:07:00Z", "<command-name>/exit</command-name>"),
+        "not json",
+    ])
+    m = measures(bench(str(s)))
+    assert m["operator messages"] == "1"
+    assert m["operator time, minutes"] == "1.0 (1 sittings)"
+
+
+# --- sittings -----------------------------------------------------------------------------------------
+
+def test_exactly_900_seconds_stays_in_the_sitting_and_each_sitting_adds_one_minute(tmp_path):
+    s = _jsonl(tmp_path / "s.jsonl", [
+        _user("2026-10-01T10:00:00Z", "one", promptSource="typed"),
+        _user("2026-10-01T10:15:00Z", "900 s later", promptSource="typed"),
+    ])
+    assert measures(bench(str(s)))["operator time, minutes"] == "16.0 (1 sittings)"
+
+
+def test_901_seconds_starts_a_new_sitting(tmp_path):
+    s = _jsonl(tmp_path / "s.jsonl", [
+        _user("2026-10-01T10:00:00Z", "one", promptSource="typed"),
+        _user("2026-10-01T10:15:01Z", "901 s later", promptSource="typed"),
+    ])
+    assert measures(bench(str(s)))["operator time, minutes"] == "2.0 (2 sittings)"
+
+
+def test_store_decisions_are_interactions_and_other_events_count_only_for_elapsed(tmp_path):
+    store = tmp_path / "store"
+    _jsonl(store / "log" / "2026-10.jsonl", [
+        _event("2026-10-02T08:00:00+00:00", "ticket.created"),
+        _event("2026-10-02T09:00:00+00:00", "approval.recorded"),
+        _event("2026-10-02T09:10:00+00:00", "human.resolved"),
+        _event("2026-10-02T10:00:00+00:00", "merge.done"),
+    ])
+    m = measures(bench("--store", str(store)))
+    assert m["operator messages"] == "0"
+    assert m["gate and ruling events"] == "2"
+    assert m["operator time, minutes"] == "11.0 (1 sittings)"
+    assert m["elapsed, hours"] == "2.00"
+    assert m["session tokens"] == "0 context, 0 output"
+
+
+def test_session_messages_and_store_decisions_share_sittings(tmp_path):
+    store = tmp_path / "store"
+    _jsonl(store / "log" / "2026-10.jsonl", [_event("2026-10-02T09:05:00+00:00", "approval.recorded")])
+    s = _jsonl(tmp_path / "runner.jsonl", [_user("2026-10-02T09:00:00Z", "approve it", promptSource="typed")])
+    m = measures(bench("--store", str(store), str(s)))
+    assert m["operator time, minutes"] == "6.0 (1 sittings)"
+
+
+# --- elapsed and tokens -------------------------------------------------------------------------------
+
+def test_tokens_count_a_repeated_message_id_once_and_elapsed_spans_every_record(tmp_path):
+    a = _jsonl(tmp_path / "a.jsonl", [
+        _user("2026-10-01T10:00:00Z", "go", promptSource="typed"),
+        _reply("2026-10-01T10:00:30Z", "m1", 100, 10),
+        _reply("2026-10-01T10:00:31Z", "m1", 100, 20),
+    ])
+    b = _jsonl(tmp_path / "b.jsonl", [_reply("2026-10-01T13:00:00Z", "m2", 50, 5)])
+    m = measures(bench(str(a), str(b)))
+    assert m["session tokens"] == "150 context, 25 output"
+    assert m["elapsed, hours"] == "3.00"
+
+
+def test_elapsed_is_a_dash_when_nothing_has_a_timestamp(tmp_path):
+    s = _jsonl(tmp_path / "s.jsonl", ["not json"])
+    m = measures(bench(str(s)))
+    assert m["elapsed, hours"] == "-"
+    assert m["operator time, minutes"] == "0.0 (0 sittings)"
+
+
+# --- refusals -----------------------------------------------------------------------------------------
+
+def _refused(cp: subprocess.CompletedProcess, *named: str) -> None:
+    assert cp.returncode == 2
+    assert cp.stdout == ""
+    assert cp.stderr.startswith("factory.benchmark: ")
+    assert cp.stderr.count("\n") == 1
+    for n in named:
+        assert n in cp.stderr
+
+
+def test_no_store_and_no_session_is_refused():
+    _refused(bench())
+
+
+def test_a_session_that_is_not_a_file_is_refused_by_name(tmp_path):
+    good = _jsonl(tmp_path / "good.jsonl", [_user("2026-10-01T10:00:00Z", "go", promptSource="typed")])
+    _refused(bench(str(good), str(tmp_path / "missing.jsonl")), str(tmp_path / "missing.jsonl"))
+    _refused(bench(str(tmp_path)), str(tmp_path))
+
+
+def test_a_store_with_no_log_directory_is_refused_by_name(tmp_path):
+    (tmp_path / "nolog").mkdir()
+    _refused(bench("--store", str(tmp_path / "nolog")), str(tmp_path / "nolog"))
