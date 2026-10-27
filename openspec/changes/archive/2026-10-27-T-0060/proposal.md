## Problem

The spec factory is a pipeline of AI agent roles that turns a written request into merged code. A human, the operator, approves each spec (the plan an implementer builds from) before any code is written, and handles every stop. Every bar the factory holds itself to today is its own. One agent, the critic, scores specs against a rubric. A writing standard governs prose. A fixed set of past tickets is replayed whenever a prompt changes. The store records what each capability must do. The store is the factory's record of tickets and runs: a directory of files kept on its own git branch. None of these bars says whether sending a change through the factory beats giving the same request to one ordinary Claude Code session. So the operator has no evidence for or against the factory's main claim: more correct changes per hour of their attention.

The north star (`docs/north-star.md`, the page that says what the factory is for and how it is measured) already names the outside test: the upstream benchmark. It takes merged fix pull requests from the public upstream Nanobot project, runs each through the factory and through a plain session, and scores each result by that pull request's own tests. The two ways of doing the work are its two arms. Two things are missing. Nothing writes down how to run the benchmark fairly. And nothing can compute one of its measures, operator time. The store timestamps each approval and ruling the operator makes, and Claude Code timestamps each message the operator types into a session. No command turns those timestamps into minutes, and adding them up by hand would break the north star's rule that nobody types a scorecard number.

This change writes the method as `docs/benchmark.md`. It adds a read-only command that computes an arm's operator time, operator messages, elapsed time and session tokens from those timestamps. It also points to both from the README. Running the ten tasks is the operator's work after the merge, and its spend is approved at this gate.

## Evidence

- Request: issue #118 (operator, 2026-10-19), "Uses #117's measures where they exist". #117 is the scorecard in `factory stats`, merged as T-0056.
- Answer 1 (Green for the operator, 2026-10-26; the operator may strike it here): operator time is derived from timestamps, with no hand count. The factory arm uses the throwaway store's gate and ruling events and its session transcripts. The baseline arm uses the timestamps of the operator's messages in its transcript. The method must say that this measures interactions, not attention, and undercounts reading and review time. It is standing for this benchmark only.
- Answer 2 (Green for the operator, 2026-10-27; the operator may strike it here) chose option (a) of my earlier question, sittings. Interactions no more than 15 minutes apart form one sitting, counted from its first interaction to its last plus one minute. The method states what this misses: reading before a sitting's first interaction, review without typing, and waits inside a sitting counted as attention. It is standing for this benchmark only.
- The method does not exist. `ls docs/benchmark.md` prints `ls: docs/benchmark.md: No such file or directory` (dev checkout, `main` at `9e8f4d3`, after T-0059's merge).
- Nothing computes a plain session's measures. `.venv/bin/python -m factory.benchmark $F/base.jsonl` prints `No module named factory.benchmark` and exits 1. Here `$F/base.jsonl` is the plain-session fixture in the factory-stats part of this change. The existing transcript cost report, `python -m factory.cost`, reads only Workflow agent files, `agent-*.meta.json` (`factory/cost.py:102`, in `tally()` at :98), so it finds nothing in a plain session's transcript.
- The scorecard counts decisions, not time: "The store records operator decisions, not operator time" (`docs/north-star.md:36`). It counts `approval.recorded` and `human.resolved` as decisions (`factory/stats.py:46`). Those are the gate and ruling events Answer 1 names.
- What an operator message looks like in a transcript. On the earlier round I surveyed the user records of the 300 most recently modified transcripts under `~/.claude/projects`, reading only record kinds. Typed prompts carry `promptSource` `typed` (348) or `queued` (256), with one `suggestion_accepted`. Tool results (10,903) carry none. `system` (535 task notifications, 419 meta) and `sdk` (221 headless prompts) are not the operator. Older records carry no `promptSource`: 41 plain prompts, against 61 local-command caveats, 59 command outputs and a few dozen slash-command lines, each of which starts with `<`. I did not re-run the survey this round.
- There are enough candidate tasks. On the earlier round, `gh pr list --repo HKUDS/nanobot --state merged --search "fix in:title" --limit 400 --json number,title,mergedAt,closingIssuesReferences,files` returned 400 PRs back to 2026-07-14. 376 of them touch a path containing `test`, and 39 of those carry a closing-issue link (for example #6071 → issue #6070, #6232 → #6231). I did not re-run it this round.
- `factory init` works unchanged on a bare checkout, so store-setup needs no change. On the earlier round I made an empty git repo in scratch and ran `bin/factory init --repo-name upstream` with `FACTORY_STATE` unset. It exited 0 and created `.factory/` with `instance.yaml`, `context.md`, `harness.lock` and the store. `factory init` then exited 0 again with `FACTORY_STATE` naming a new directory, and created that store too.
- The scorecard reads a throwaway store, but names it by path when it finds no instance for it. On the earlier round, on the scratch `FACTORY_STATE` store, `bin/factory stats --scorecard --store <it> --since 2026-10-20` printed `## /Users/dphang/…/scratch/initcheck/tstore: target changes (no instance found)`. A review is public, so the method points `FACTORY_STATE` at the bench checkout's own store, whose instance the scorecard finds (design part C).
- README's budget. With T-0059 merged, `wc -l < README.md` prints `1224`. Current truth caps README at 1,225 lines (harness-docs, "README is at most 1,225 lines"), and the gate now replays that scenario on every change. So this change can add exactly one net line.
- The gate now replays current truth. T-0059 made `factory truth check` this repo's last gate command (`.factory/instance.yaml`, `gate_commands`). It runs each current-truth scenario's WHEN under `bash` with a fresh HOME and TMPDIR, after the GIVEN blocks it names, and passes it only if the output equals the THEN's quoted lines (`factory/truth.py`, `expected()` and `_run_capability()`). Once this change is archived, its scenarios are replayed on every later change. I wrote them so the check can run them: each THEN is an exact print, and the two scenarios that reuse the fixture name it as "the GIVEN block of" its scenario. Evidence that this works is in verification.md.
- No current-truth check breaks on the edits. The "Where things live" checks count rows naming `docs/standards.md`, `` `STATUS.md` ``, `` `docs/reviews/` `` and `CONTRIBUTING.md` (harness-docs current truth); the new row names none of them in backticks. The checks on "What depends on Claude Code" look for `claude -p`, `factory stats`, the "Six pieces assume Claude Code" sentence and a row naming `run finish --transcripts`; the edit keeps each.
- A prototype of design part A, in this run's scratch directory (`scratch/repo/factory/benchmark.py`, 90 lines, in a copy of `main`), printed exactly the THEN lines of the three factory-stats scenarios, under bash and under zsh, through the briefing's wrapper, and `factory truth check` passed all seven runnable scenarios of this change on it (verification.md).

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

