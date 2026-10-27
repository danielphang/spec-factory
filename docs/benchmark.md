# The upstream benchmark

This page is how to test, on outside work, whether the spec factory is worth its cost. The factory
is the pipeline of AI agent roles in this repository that turns a written request into merged code.
The operator is the person who approves each spec (the plan an implementer builds from) and handles
every stop. The benchmark gives the factory and one ordinary Claude Code session the same real bug
reports, and scores each fix by the tests its project's own maintainers wrote for it. It is written
for the operator who runs it and for a technical reader judging its results.

## What the benchmark compares

The question is whether the factory beats one plain Claude Code session at turning a real issue into
a correct fix, and at what cost in operator attention. The north star,
[docs/north-star.md](north-star.md), names this test: it is the page that says what the factory is
for and how it is measured.

Each task is a merged fix pull request (PR) from the public upstream Nanobot project,
`https://github.com/HKUDS/nanobot`. Its issue goes to two arms, each working from the same commit:

| Arm | What does the work |
|---|---|
| The factory arm | The factory, on its own throwaway instance: intake, the spec gate and the build, as for any ticket |
| The baseline arm | One plain Claude Code session, given the issue's text and reviewed by the operator |

The score of an arm is whether the PR's own tests pass on its result. Beside the score, four measures
give the cost of reaching it: operator decisions, operator time, tokens and wall time. "The measures"
says where each comes from.

## Choosing the tasks

1. Fix a cut-off date before the first task starts, and record it in the benchmark's issue.
2. List upstream's merged fix PRs:

   ```sh
   gh pr list --repo HKUDS/nanobot --state merged --search "fix in:title" --limit 400 \
     --json number,title,mergedAt,closingIssuesReferences,files
   ```

3. Keep a PR merged before the cut-off only if it passes these filters, applied in this order:
   1. It has exactly one closing issue.
   2. It adds or changes at least one file whose path contains `test`. Those files are "the PR's
      tests".
   3. The issue's title and body hold no patch and no link to the PR. A patch is any line starting
      `diff --git`, `@@`, `+++ ` or `--- a/`.
   4. The PR's tests fail at the parent commit and pass at the merge commit, each run with upstream's
      test command. The parent commit is the first parent of the PR's merge commit. Upstream's test
      command is the one its CI configuration runs at that commit.
4. Take the 10 most recently merged PRs that pass. Number them 1 to 10, newest first.

The rule is fixed before any result is seen, so nobody picks tasks that favour one arm.

## Keeping the arms blind

An arm that sees the fix proves nothing about fixing. Five measures keep the fix out of both arms.

1. **Checkouts hold only the parent commit.** Make each arm's checkout this way, with `<parent>` the
   first parent of the merge commit:

   ```sh
   git init -b main
   git fetch --depth 1 https://github.com/HKUDS/nanobot <parent>
   git reset --hard FETCH_HEAD
   ```

   No remote is added. Later commits, the fix's among them, are not in the checkout and cannot be
   fetched by name.
2. **Both arms get the same task text.** Write it once per task, as `# <issue title>`, a blank line,
   the preface below, a blank line, then the issue body. Leave out the issue's comments. The preface:

   > Fix the issue below in this checkout. Work only from this checkout and the issue's text: do not
   > look up the issue, its pull request or this project's repository online, and do not read any
   > other copy of this project on this machine.

   Give both arms this file unchanged.
3. **The operator does not see the fix.** Do not open the PR, its diff or its tests until both arms
   of the task have ended.
4. **Arm order alternates.** Odd-numbered tasks run the factory arm first; even-numbered tasks run
   the baseline arm first. Whatever the operator learns from the first arm then falls on each arm
   equally often.
5. **Each task ends with an audit.** After both arms end, search their transcripts:

   ```sh
   grep -rlF -e pull/<PR> -e issues/<issue> -e <first 12 characters of the merge commit> \
     -e nanobot-upstream ~/.claude/projects/*bench-<PR>-*/
   ```

   Any file it lists marks that arm leaked. Then read each `WebFetch` or `WebSearch` call, and each
   `gh` or `git fetch` command, in those transcripts. One that reached the issue, the PR or upstream's
   later code also marks the arm leaked, and the review names the call. A leaked arm is reported and
   not scored.

## Running a task

Each arm has its own checkout, outside every live repository: `~/bench/bench-<PR>-factory` and
`~/bench/bench-<PR>-plain`. Make both as "Keeping the arms blind" says.

**Factory arm.** In its checkout:

1. Point every factory command in this shell at the checkout's own instance and store:

   ```sh
   export FACTORY_INSTANCE=$PWD/.factory FACTORY_STATE=$PWD/.factory/state
   ```

   With `FACTORY_INSTANCE` and `FACTORY_STATE` set, no command in this shell can reach a live
   store, and the scorecard names the instance instead of printing a path.
2. Follow README's "Adopting the factory in a repo" ([README.md](../README.md)), with
   `--repo-name bench-<PR>-factory`. Take `gate_commands` and `environment_sync` from upstream's CI
   configuration at the parent commit. Take `models` from this repository's `.factory/instance.yaml`.
   Write `context.md` from upstream's own README and CI only.
3. File the task text with `factory ticket new --file`.
4. Take the ticket through intake and the build as any real ticket, from a shell or a runner session.
   A runner session is a Claude Code session in which the operator drives the factory.

**Baseline arm.** In its checkout, start `claude --model <model>`. The model is the one this
repository's `.factory/instance.yaml` gives the implementer. Paste the task text. Review the result
the way you review a merge: read the diff, then ask for changes or accept. Commit the result.

**Both arms.** Make no hand edits to code. In the factory arm a gate edit or a ruling is allowed, and
the scorecard counts it as an intervention or a decision. An arm ends when its ticket closes or when
the operator accepts the session's result. The operator may instead abandon an arm; its result is
then scored as it stands.

## Scoring a task

After both arms end, in each arm's checkout:

```sh
git fetch --depth 1 https://github.com/HKUDS/nanobot <merge commit>
git checkout FETCH_HEAD -- <the PR's tests>
```

The checkout puts the PR's tests over the arm's result: the factory arm's `main`, or the baseline
arm's committed tree. Then run upstream's test command on those files. The arm passes when the
command exits 0. Keep the command's last line for the review.

## The measures

| Measure | Factory arm | Baseline arm |
|---|---|---|
| Operator decisions | the scorecard's "Operator decisions and interventions per change" | the operator messages after the first, from `python -m factory.benchmark`; filing a ticket is not a decision in the scorecard either |
| Operator time | `python -m factory.benchmark --store $FACTORY_STATE` with the runner sessions' transcripts | `python -m factory.benchmark` with the session's transcript |
| Tokens | the scorecard's tokens per change, plus the runner sessions' tokens from `python -m factory.benchmark` | the session tokens from `python -m factory.benchmark` |
| Wall time | the scorecard's lead time, with its summed run time beside it | the elapsed time from `python -m factory.benchmark` |

The scorecard is the north star's table of measures, printed by `factory stats`. For the factory
arm, run it in the arm's shell, with `$R` the factory's runtime checkout:

```sh
$R/bin/factory stats --scorecard --store $FACTORY_STATE --since <the day the task started> \
  --transcripts ~/.claude/projects
```

Run the report from the dev checkout, `~/dev/spec-factory`, at a commit that contains it:

```sh
uv run --frozen python -m factory.benchmark [--store $FACTORY_STATE] <session transcript>...
```

A session's transcript is `<session id>.jsonl` under
`~/.claude/projects/<the session's start directory, with / and . as ->`. The report reads only the files it is given and writes nothing.

**Operator messages.** An operator message is a `user` record that is not `isMeta` or `isSidechain`
and holds no `tool_result`. Its `promptSource` must be `typed`, `queued` or `suggestion_accepted`. A
record with no `promptSource`, as older transcripts write, counts when its text does not start with
`<`. Task notifications, headless prompts and slash-command lines are not the operator.

**Operator time.** Interactions are the operator messages and the store's spec approvals and
rulings. Interactions are grouped into sittings: an interaction more than 15 minutes after the one
before starts a new sitting. A sitting counts from its first interaction to its last, and each
sitting adds one minute. Operator time is the sum, in minutes.

Operator time measures interactions, not attention. It undercounts reading and review time. The
sittings rule misses three things:

- reading done before a sitting's first interaction;
- review done without typing anything;
- waits inside a sitting, which it counts as attention.

## Putting a result in a review

1. Results go in the next review, `docs/reviews/<date>.md`, written from
   [docs/reviews/TEMPLATE.md](reviews/TEMPLATE.md). They are not part of this page.
2. Section 5 of the review, "Experiments and side work", gets one row for the benchmark's issue.
3. Under it goes a subsection with one block per task. Each block gives the PR number. Then, for
   each arm: whether it passed, failed or leaked; the test command's last line; and the scorecard's
   and the report's output, pasted as printed.
4. No number is typed or adjusted. A total, median or comparison across tasks is written
   "not yet computed", because no command computes it.
5. This repository is public. Name upstream PRs by number, and name no private product.

## Spend

One full run is about 10 factory intakes and builds and 10 plain sessions. That spend was approved
at the spec gate of the ticket that added this page. A larger or repeated run is a new decision.
