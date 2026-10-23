## Proposed change

One sub-ticket. The texts below are the prototype's, and every scenario passed on them. The implementer may reword any sentence. It must keep verbatim each phrase a scenario greps for, keep every figure in `STATUS.md`'s Scorecard section a copy from the baseline review, and the change must add no more than 8 lines to README.

**A. `docs/north-star.md`.**

A1. Insert this section directly after the line `The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).` and its blank line, before `## What it will not trade away`:

```
## How we know it is working

The measures above are judged against a bar set outside the factory: what it delivers to its
targets, not how closely it follows its own rules. Each instance decides whether its merges are
target changes. The Nanobot port's are. Spec-factory's are factory work, changes to the factory
itself: the scorecard reports them on a line of their own and never counts them as target changes.

- **Primary metric:** correct target changes per hour of operator attention. A change is correct
  when no escape is recorded against it.
- **Constraint:** escaped defects do not rise. An escape is a merged change that later needed a fix
  or a revert.
- **Second measure:** cost, as tokens and wall time per change.

The store records operator decisions, not operator time. Until it records time, the scorecard
counts operator decisions and interventions per change in place of hours of operator attention.

The scorecard gives these numbers for a window of time, per instance, beside the same numbers for
the window before. `factory stats` computes them from the store, and nobody types them. Until it
computes a number, a review writes "not yet computed" rather than count it by hand. The one
exception is the baseline review, `docs/reviews/2026-10-19.md`, counted by hand from both stores,
git, the issues and the session transcripts, with its method written in the review.

| Number | What it counts |
|---|---|
| Target changes merged | tickets closed with a merge |
| Escapes | merged changes that later needed a fix or a revert |
| Operator decisions and interventions per change | each gate decision, ruling or resolve, and each intervention made outside the CLI |
| Tokens and wall time per change | the cost of the role runs behind each merged change |
| Lead time | the time from a request's creation to its merge |

Three comparisons ground these numbers outside the factory:
- **A plain-session baseline:** the same tickets done in one plain Claude Code session, with the
  operator reviewing its result the way they review a merge.
- **The upstream benchmark:** merged fix pull requests from the public upstream Nanobot project,
  each run by the factory and by a plain session, and scored by that pull request's own tests.
- **DORA-style delivery measures:** lead time, and change failure rate, which is escapes divided by
  target changes merged. DORA is the DevOps Research and Assessment programme's set of delivery
  measures.

**Reviews.** A review runs every two weeks, or monthly when there is too little to discuss. Each is
`docs/reviews/<date>.md`, written from `docs/reviews/TEMPLATE.md`. A review re-orders the work queue,
issue #96, and rewrites `STATUS.md` at the repository root, which quotes numbers only as of the
latest review. The baseline review is dated 2026-10-19. The first review written from the template
is on 2026-11-02.
```

A2. In "How it decides where effort goes", change `And three working rules that follow from them:` to `And four working rules that follow from them:`, and insert this bullet as the first of the list:

```
- **Factory work serves a target or a number.** A factory ticket goes ahead only if it fixes a defect
  that hit a target ticket, or names the scorecard number it moves and re-measures that number after
  it ships. Its request says which. The operator applies this rule at the spec gate; no role prompt
  or harness check enforces it.
```

Nothing else in the file changes.

**B. `README.md`.** Eight lines added, one of them blank. The prototype ends at 1,182.

B1. Between the opening paragraph (which ends `"Where it runs" and "Starting a run".`) and the status table, insert these three lines, followed by a blank line:

```
**North star.** Turn a written request into merged, verified code with as little of the operator's
attention as the work allows. Metric: correct changes to the product it builds, per hour of operator
attention, with no rise in escaped defects. See `docs/north-star.md`, `STATUS.md` and `docs/reviews/`.
```

It says "the product it builds", not "target". README's glossary uses "target" for any repository the factory runs on, and that includes this one.

B2. In "Filing a request from an issue tracker", replace the first paragraph's second line, `kept by hand in both directions.`, with these three lines. The paragraph grows by two lines and no blank line is added:

```
kept by hand in both directions. A request to change the factory itself goes ahead only if it fixes
a defect that hit a ticket of the product the factory builds, or names the scorecard number it moves
and re-measures it after it ships. The request says which; the operator applies it at the spec gate.
```

B3. In "Where things live", after the `docs/north-star.md` row, insert:

```
| `STATUS.md`, `docs/reviews/` | The latest scorecard, focus and queue, rewritten only at a review; each review, written from `docs/reviews/TEMPLATE.md`, the first being the hand-counted baseline of 2026-10-19 |
| `CONTRIBUTING.md` | How work is proposed and chosen: issue, factory ticket, spec gate, under the north star's rule for factory work |
```

The status header's date stays 2026-10-19, unless the merge lands on a later day. In that case the implementer bumps it, as "Maintaining this page" asks.

**C. New `CONTRIBUTING.md`** at the repository root:

```
# Contributing

This repository is the spec factory: an AI software pipeline that turns a written request into
merged, verified code, with a human approving each design before any code is written. What the
factory is for, and how its work is measured, is in [docs/north-star.md](docs/north-star.md).
This page says how work on the factory is proposed and chosen.

## The rule for factory work

A change to the factory itself goes ahead only if it does one of two things:

- it fixes a defect that hit a target ticket, a ticket of the product the factory builds (today,
  a port of the Nanobot chat bot); or
- it names the scorecard number it moves, and re-measures that number after it ships.

The request says which. The scorecard's numbers are named in
[docs/north-star.md](docs/north-star.md). The operator applies the rule at the spec gate.

## How work is proposed and chosen

1. **Issue.** Open an issue that says where the problem is, what happened (the evidence), why it
   matters, and which half of the rule it meets. A proposed fix is welcome, as a suggestion.
2. **Factory ticket.** The operator files the issue as a request, which makes it a factory ticket:
   one request, tracked from a file to a closed record. [README.md](README.md)'s "Filing a request
   from an issue tracker" gives the steps. The work queue, issue #96, sets the order, and each
   review re-orders it.
3. **Spec gate.** The factory's agents turn the ticket into a spec: the problem, the decisions,
   and acceptance checks written as commands with expected results. The operator approves or
   returns the spec at the spec gate, before any code is written, and applies the rule there.
   After approval the factory builds, checks and merges the change.

## Where to read more

- [STATUS.md](STATUS.md): the latest scorecard, the current focus and the top of the queue.
- [docs/reviews/](docs/reviews/): each review, and the template a review is written from.
- [docs/decided-against.md](docs/decided-against.md): what was tried and dropped. Read it before
  proposing something that sounds new.
- [README.md](README.md): the system as it runs today.
```

**D. New `STATUS.md`** at the repository root, at most 60 lines (the prototype has 56). Every figure in its Scorecard section is copied from the baseline review (part F): each table cell from that instance's table, and each figure in the prose from the review's text.

```
# Status

This page is rewritten only at a review, and every number on it is as of the review it names.
Last rewritten: 2026-10-19, at the baseline review.

**North star:** correct target changes per hour of operator attention, while escaped defects do
not rise. The full position is [docs/north-star.md](docs/north-star.md).

## Scorecard

From the baseline review, [docs/reviews/2026-10-19.md](docs/reviews/2026-10-19.md), for
2026-10-03 to 2026-10-19. These figures were counted by hand. From #117 on, `factory stats`
computes them, and later reviews quote its figures. Operator touches, the decisions and
interventions per change, stand in for hours of operator attention, which the store does not
record. The Nanobot port's merges are target changes; spec-factory's are factory work.

| Number | Nanobot port | spec-factory |
|---|---|---|
| Changes merged | 27 | 42 |
| Escapes (repaired + open) | 1 + 1 | 5 + 3 |
| Operator touches per change | 5.0 | 3.1 |
| Wall time per change, median | 66 min | 67 min |
| Lead time, median | 21.9 h | 10.6 h |
| Runs with a cost record / runs started | 15 / 436 | 18 / 500 |

The port's escapes count code only; 5 more of its changes needed a fix to the record alone. Most
of the port landed by 2026-10-11, and only 1 of its changes merged after that. Cost per change is
mostly unknown, because few runs carry a cost record.

## Current focus

Measuring the north star: the scorecard in `factory stats`, then the upstream benchmark.

## Top of the queue

The queue is [issue #96](https://github.com/danielphang/spec-factory/issues/96), re-ordered at
each review. Its top as of 2026-10-19, after this page's own change:

1. The scorecard in `factory stats` ([#117](https://github.com/danielphang/spec-factory/issues/117)).
2. The spec validator at `spec add` ([#105](https://github.com/danielphang/spec-factory/issues/105)),
   a defect that parked a target ticket.
3. The upstream benchmark ([#118](https://github.com/danielphang/spec-factory/issues/118)).

## Open experiments

None yet. Experiments are issues labelled
[`experiment`](https://github.com/danielphang/spec-factory/issues?q=is%3Aopen+label%3Aexperiment).

## Links

- Latest review: [the baseline of 2026-10-19](docs/reviews/2026-10-19.md). Every review and the
  template are in [docs/reviews/](docs/reviews/).
- North star: [docs/north-star.md](docs/north-star.md).
- Issues: <https://github.com/danielphang/spec-factory/issues>.
- Store, the factory's record of every ticket and run, on its own branch:
  <https://github.com/danielphang/spec-factory/tree/factory-store>.
```

**E. New `docs/reviews/TEMPLATE.md`.** Its six sections are the request's six, in order:

```
# Review YYYY-MM-DD

Copy this file to `docs/reviews/<date>.md`, named by the review's date, and fill in each section.
A review runs every two weeks, or monthly when there is too little to discuss. The measures and
the rule for factory work are in [docs/north-star.md](../north-star.md). After the review,
re-order the work queue, issue #96, and rewrite [STATUS.md](../../STATUS.md) from this review.

This repository is public. Name a change by its ticket id and give counts; do not name a private
product or link a private issue.

Window: <start date> to <end date>. Previous review: <link>.

## 1. Scorecard against the last review

Paste the scorecard from `factory stats` for this window and the last one, as it prints it. Do not
type or adjust a number. Write "not yet computed" for a number it does not compute yet. The one
review counted by hand is the baseline, [2026-10-19](2026-10-19.md).

## 2. What we worked on

| Ticket | Defect it fixed, or scorecard number it moved | Result after it shipped |
|---|---|---|

## 3. What we chose not to do

One line per item, each linking its row in [docs/decided-against.md](../decided-against.md).
Add the row there first.

## 4. Successes and failures

| What happened | Success or failure | What it cost |
|---|---|---|

## 5. Experiments and side work

One row per issue labelled `experiment`.

| Issue | What it tries | Result or status |
|---|---|---|

## 6. Decisions and the new queue order

The decisions taken, one per line, each with its reason. Then the new order of the queue, as
written to issue #96.
```

**F. New `docs/reviews/2026-10-19.md`**, the baseline review. Generate it from the operator's text on the store branch rather than retyping it. Run this from the repository root:

```
{ echo '# Review 2026-10-19: baseline scorecard, 2026-10-03 to 2026-10-19'; git show 02e403f:requests/T-0055.md | sed -n '/^--- baseline begins ---$/,/^--- baseline ends ---$/p' | sed '1,2d;$d'; } > docs/reviews/2026-10-19.md
```

The result is 100 lines: the new first line, then the baseline's lines 2 to 100 unchanged. The text has no trailing whitespace, so it passes the whitespace check over `docs/`.

**G. `docs/changelog.md`.** Add one entry after entry 75 and before the closing `Declined:` line, numbered 76. Prototype text:

```
76. After issue #116 (2026-10-19), where the factory's own work had no outside bar: `docs/north-star.md` named four success measures but set no target for any of them, nothing reported them and nobody reviewed them, so factory work was chosen in answer to the factory's own incidents. `docs/north-star.md` gains "How we know it is working": the primary metric, correct target changes per hour of operator attention, where each instance decides whether its merges are target changes and spec-factory's are factory work on a line of their own; its constraint, that escaped defects do not rise; cost as the second measure; operator decisions and interventions per change standing in for hours until the store records operator time; the scorecard's numbers by name, which `factory stats` is to compute so that nobody types them; three outside comparisons, a plain-session baseline, the upstream benchmark and DORA-style lead time and change failure rate; and a review every two weeks. A fourth working rule admits a factory ticket only if it fixes a defect that hit a target ticket, or names the scorecard number it moves and re-measures it after it ships; the operator applies it at the spec gate, and no role prompt or harness check does. New files: `docs/reviews/TEMPLATE.md`, which each review copies; `docs/reviews/2026-10-19.md`, the baseline review, counted by hand by the operator and the one review whose numbers are not computed; `STATUS.md`, which each review rewrites and which now quotes the baseline; and `CONTRIBUTING.md`, which says how work is proposed and chosen. README gains a north-star paragraph on its first screen, the rule in "Filing a request from an issue tracker" and two rows in "Where things live", and stays within its 1,185-line budget. Rejected: a role prompt or harness check that enforces the rule, which the request rules out; and recording operator time by hand, which would mean typing a number.
```

## Tests to change

none. No decision overturns behaviour a test pins. `grep -rlE 'north-star|STATUS\.md|CONTRIBUTING|1185|docs/reviews' tests factory agents` finds nothing (exit 1).

