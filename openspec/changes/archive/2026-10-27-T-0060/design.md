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

