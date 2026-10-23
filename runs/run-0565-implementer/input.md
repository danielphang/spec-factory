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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0565-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0565-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0055.1` (branch `factory/T-0055.1`, base `1321c1710aa703876eac6c66df7e38d1dd92d10a`, head `1321c1710aa703876eac6c66df7e38d1dd92d10a`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0055.1

T-0055.1 / North star: a primary metric, a two-weekly review and a rule for choosing factory work, shown on the repo's front page
Depends on: none
Parallel-safe: yes

Parent: T-0055, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- The north star holds the measurement section and keeps its measures and target sentence
- The north star's working rules include the rule for factory work
- README opens with the north-star paragraph and stays within its budget
- The filing section states the rule for factory work
- Where things live has a row for each new file
- CONTRIBUTING.md gives the three steps and the rule, and links the north star
- STATUS.md has its sections and links, and quotes only the baseline review's figures
- The review template's sections are the six the request lists, in order
- The baseline review matches the operator's text after its first line
- No relative link in the three new pages is broken
- The changelog records issue 116 in one entry without a numbering gap
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v3, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0055/v3.md`

=== proposal.md
## Problem

The spec factory is an AI pipeline that turns a written request into merged code. A human, the operator, approves each design at the spec gate before any code is written. The factory works on two kinds of repository. One is its own code, here in this repository. The other is a target: a product it builds, today a port of the Nanobot chat bot. Work on the factory itself is called factory work. Each repository the factory runs on is an instance, and each instance keeps a store: the factory's record of every ticket, run and decision, on a git branch of its own.

Nothing measures factory work against a bar set outside the factory. The north-star page, `docs/north-star.md`, is where the operator records what the factory is for. It names four success measures, but it sets no target for any of them, nothing reports them, and nobody reviews them. So the operator has chosen factory work in answer to the factory's own incidents, not by whether it helps the product. The operator's hand count for 2026-10-12 to 2026-10-19 shows 12 factory changes merged against 1 change to the Nanobot port. The north star is also hard to find. The repository's front page opens with how the system works, and the repository has no contributor guide.

The operator asked for five things:
- a primary metric with a constraint, and a scorecard of named numbers;
- a rule that factory work must serve the product or move a number;
- a review every two weeks;
- a one-page status file;
- the north star placed where GitHub visitors see it.

The operator also counted a baseline by hand, so that the first review has real figures to compare against. This change writes all of it as documents, and adds the baseline as the first review. It changes no harness code and no role prompt.

## Root cause

The north star sets measures but no targets, no scorecard and no review (`docs/north-star.md:14-19`). No document states a rule for choosing factory work. The front page (`README.md:1-12`) and the repository root give no path to the north star beyond one row in README's "Where things live" table (`README.md:1091`).

## Out of scope

- No change to harness code (`factory/`, `bin/factory`), role prompts (`docs/prompts/`, `agents/`), `docs/design.md`, `docs/writing.md`, `docs/standards.md` or `pyproject.toml`. No role or harness check enforces the rule for factory work. The operator applies it at the spec gate.
- Computing the scorecard. That is T-0056 (#117). This change names the numbers, and records the operator's hand-counted baseline.
- The upstream benchmark and `docs/benchmark.md`. That is T-0060 (#118).
- The first review written from the template (`docs/reviews/2026-11-02.md`), and changes to issue #96 or to `dev/issues.md`. These are operator work after the merge.
- Any edit to the baseline's figures or wording beyond its first line.
- A licence file. The request leaves it to the operator.
- The north star's four success measures, its eight non-negotiables, its "Where it is heading" list, and its sentence on whom the factory serves. All stay word for word.

## Open questions

none. Both questions from round 1 are answered (Answer 1, 2026-10-19/20), and the answers are under Decisions.

## Decisions

- Operator decisions and interventions per change stand in for hours of operator attention until the store records operator time, and the north star says so. This is the operator's answer (a) to round-1 question 1, which asked how an hour of operator attention is counted. Standing: T-0056, the ticket that adds the scorecard to `factory stats` (#117), follows it. `factory stats` is the harness's read-only report on what each run did and cost.
- Each instance decides whether its merges are target changes. The Nanobot port's are. Spec-factory's are factory work, reported on a line of their own and never counted as target changes. Operator's answer, recorded in decisions.md on 2026-10-19. Standing.
- The operator's baseline becomes `docs/reviews/2026-10-19.md`, the baseline review, copied byte for byte from `02e403f:requests/T-0055.md`. Only its first line changes, to `# Review 2026-10-19: baseline scorecard, 2026-10-03 to 2026-10-19`. That keeps the operator's window in the title and the "Review <date>" form of later reviews. The template's six sections are omitted there, as the answer allows. Operator's answer to round-1 question 2, on what `STATUS.md` holds before the first review.
- The baseline review is the one review whose numbers were counted by hand. Every later review pastes `factory stats` output, and writes "not yet computed" for a number it does not compute yet. Standing.
- The baseline names four commit SHAs from the Nanobot fork. This run's briefing bars a spec from copying such SHAs. They stay, because the operator asked for the baseline verbatim. No acceptance check reads them.
- `STATUS.md` quotes six of the baseline's figures for each instance: changes merged, escapes, operator touches per change, median wall time, median lead time, and runs with a cost record. It gives the date 2026-10-19, says the figures were counted by hand, and says that `factory stats` computes them from #117 on. Which six to show is my call, and the operator may change it at this gate. Each cell must stay a copy of a cell in that instance's table of the review.
- `STATUS.md`'s top of the queue copies issue #96 as re-ordered on 2026-10-19, after its row 1, which is this change: #117, #105, #118.
- The rule for factory work becomes a fourth working rule in the north star's "How it decides where effort goes", beside "Measure before and after". README's "Filing a request from an issue tracker" and `CONTRIBUTING.md` restate it in short. Standing: every later factory ticket's request says which half of the rule it meets, and the operator applies the rule at the spec gate.
- The north star's scorecard table names the five numbers the scorecard request asks `factory stats` to compute. Change failure rate is escapes divided by target changes merged. It is defined under the outside comparisons, not added as a sixth row.
- README's first screen names the folder `docs/reviews/`, not one named review, so a review never has to edit README. `STATUS.md`, which every review rewrites anyway, links the latest review by name and the folder.
- README stays within its 1,185-line budget, with room left for T-0058. This change adds 8 lines to README, so README ends at 1,182. T-0058, the bug ticket at this same gate, adds about one line and also requires 1,185 or fewer, so both fit in either merge order. To fit, the rule in "Filing a request from an issue tracker" joins that section's first paragraph rather than taking a paragraph of its own, and the north-star paragraph takes three lines. Rejected: raising the budget. T-0058's spec checks the 1,185 figure itself, so a higher budget here would not stop it parking if it merged second, and it would modify three current-truth requirements this change does not otherwise need.
- README's north-star paragraph names its three pages as code, `docs/north-star.md`, `STATUS.md` and `docs/reviews/`, not as Markdown links. README has no Markdown links anywhere. The new pages, which are short and read on GitHub, use links.
- The first-screen block is a paragraph that opens with the bold label "North star.", not a heading, because README's "Headings are the contract" rule keeps its section names and order fixed.
- One changelog entry records the change, because it rewrites the north star's position. The changelog has recorded such a change before: entry 73 (issue #110, commit `21f90c4`) changed `docs/north-star.md` and README and left `docs/design.md` alone. T-0049 declined an entry because its change left `docs/design.md` alone and did not touch the north star either.
- The review template reminds the writer that this repository is public: name a change by ticket id, give counts, and name no private product.

## Risk

The change is documents only: seven files, about 300 lines, 100 of them the operator's baseline. A wrong number or a misleading rule would steer which factory work gets approved, so the operator reads the north-star text and `STATUS.md` at this gate. No harness code, prompt or test changes, and no role's input changes, because role inputs carry neither README nor `docs/north-star.md`. README ends at 1,182 of its 1,185 lines, which leaves room for T-0058 (see Decisions). The baseline review cites commit SHAs from the Nanobot fork in a public repository (see Decisions). Every changed path is unprotected.
Protected paths: none

## Operator steps

1. Create the label: `gh label create experiment -R danielphang/spec-factory --description "Side work that tries an idea; each review reports its result"`.
2. The About description already states the purpose: "A spec-driven AI software pipeline: a written request becomes merged, verified code with as little operator attention as the work allows." Keep it, which meets the request. Or, if you prefer wording that matches README's new paragraph, overwrite it: `gh repo edit danielphang/spec-factory --description "An AI software pipeline that turns a written request into merged, verified code, with as little of the operator's attention as the work allows."`.
3. Open https://github.com/danielphang/spec-factory and check that GitHub shows `CONTRIBUTING.md` as a tab or link on the overview. I could not confirm the tab layout from GitHub's documentation.
4. On 2026-11-02, write the first review from the template, `docs/reviews/2026-11-02.md`. Then re-order issue #96 and rewrite `STATUS.md` from that review.

=== design.md
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

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The north star says how the factory's work is measured and reviewed
`docs/north-star.md` SHALL hold, as its second `## ` section, "How we know it is working". That section SHALL name the primary metric, its constraint, cost as the second measure, operator decisions and interventions standing in for hours of operator attention, spec-factory's merges reported on a line of their own, the scorecard's five numbers as table rows, the plain-session baseline, the upstream benchmark, change failure rate, the baseline review `docs/reviews/2026-10-19.md`, and a review every two weeks from `docs/reviews/TEMPLATE.md` that rewrites `STATUS.md`, the first from the template on 2026-11-02. The file MUST keep its four success measures and its sentence on whom the factory serves.

#### Scenario: The north star holds the measurement section and keeps its measures and target sentence
- WHEN `(N=docs/north-star.md; X=$(awk '/^## How we know it is working$/{f=1;next} f&&/^## /{f=0} f' $N); S=$(printf '%s' "$X" | tr '\n' ' ' | tr -s ' '); echo "heading=$(grep -cx '## How we know it is working' $N) second=$(grep '^## ' $N | sed -n 2p | grep -cx '## How we know it is working') terms=$(printf '%s' "$S" | grep -oF -e 'correct target changes per hour of operator attention' -e 'escaped defects do not rise' -e 'tokens and wall time per change' -e 'in place of hours of operator attention' -e 'on a line of their own' -e 'plain-session baseline' -e 'upstream benchmark' -e 'change failure rate' -e 'every two weeks' -e 'docs/reviews/TEMPLATE.md' -e 'docs/reviews/2026-10-19.md' -e 'STATUS.md' -e '2026-11-02' | sort -u | grep -c .) rows=$(printf '%s\n' "$X" | grep -cE '^\| (Target changes merged|Escapes|Operator decisions and interventions per change|Tokens and wall time per change|Lead time) \|') measures=$(sed -n '/^Success is measured as:$/,/^$/p' $N | grep -c '^- ') serves=$(grep -cxF 'The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).' $N)")`
- THEN it prints exactly `heading=1 second=1 terms=13 rows=5 measures=4 serves=1`

### Requirement: The north star holds the rule for factory work
`docs/north-star.md`'s "How it decides where effort goes" SHALL introduce four working rules, and one of them SHALL be "Factory work serves a target or a number". That rule SHALL admit a factory ticket only if it fixes a defect that hit a target ticket, or names the scorecard number it moves and re-measures that number after it ships, and SHALL say that the operator applies it at the spec gate.

#### Scenario: The north star's working rules include the rule for factory work
- WHEN `(N=docs/north-star.md; B=$(sed -n '/^## How it decides where effort goes$/,/^## Where it is heading$/p' $N | awk '/^- \*\*Factory work serves a target or a number\.\*\*/{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' | tr '\n' ' ' | tr -s ' '); echo "rule=$(printf '%s' "$B" | grep -c 'Factory work serves') terms=$(printf '%s' "$B" | grep -oF -e 'fixes a defect that hit a target ticket' -e 'names the scorecard number it moves' -e 're-measures that number after it ships' -e 'spec gate' | sort -u | grep -c .) four=$(grep -cx 'And four working rules that follow from them:' $N) three=$(grep -cx 'And three working rules that follow from them:' $N)")`
- THEN it prints exactly `rule=1 terms=4 four=1 three=0`

### Requirement: README shows the north star on its first screen
`README.md` SHALL hold one paragraph opening `**North star.**`, placed before "What problem it solves", that states the primary metric per hour of operator attention and names `docs/north-star.md`, `STATUS.md` and `docs/reviews/`. README MUST stay within its 1,185-line budget.

#### Scenario: README opens with the north-star paragraph and stays within its budget
- WHEN `(H=$(grep -n '^## What problem it solves$' README.md | cut -d: -f1); B=$(awk -v h="$H" 'NR>=h{exit} /^\*\*North star\.\*\*/{f=1} f&&/^$/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "block=$(grep -c '^\*\*North star\.\*\*' README.md) top=$(printf '%s' "$B" | grep -c '^\*\*North star\.\*\*') metric=$(printf '%s' "$B" | grep -c 'per hour of operator attention') links=$(printf '%s' "$B" | grep -oF -e 'docs/north-star.md' -e 'STATUS.md' -e 'docs/reviews/' | sort -u | grep -c .) readme=$(wc -l < README.md | awk '{print ($1 <= 1185 ? "within" : "over")}')")`
- THEN it prints exactly `block=1 top=1 metric=1 links=3 readme=within`

### Requirement: README's filing steps state the rule for factory work
README's "Filing a request from an issue tracker" SHALL say that a request to change the factory itself goes ahead only if it fixes a defect that hit a ticket of the product the factory builds, or names the scorecard number it moves and re-measures it after it ships. It SHALL also say that the operator applies the rule at the spec gate.

#### Scenario: The filing section states the rule for factory work
- WHEN `(F=$(sed -n '/^### Filing a request from an issue tracker$/,/^### Running many tickets/p' README.md | tr '\n' ' ' | tr -s ' '); echo "terms=$(printf '%s' "$F" | grep -oF -e 'change the factory itself goes ahead only if' -e 'fixes a defect that hit a ticket of the product' -e 'names the scorecard number it moves' -e 're-measures it after it ships' -e 'spec gate' | sort -u | grep -c .)")`
- THEN it prints exactly `terms=5`

### Requirement: README's Where things live names the new files
README's "Where things live" table SHALL have exactly one row naming `STATUS.md`, one naming `docs/reviews/` and one naming `CONTRIBUTING.md`.

#### Scenario: Where things live has a row for each new file
- WHEN `(Q=$(printf '\140'); W=$(sed -n '/^## Where things live$/,/^## Related work and history$/p' README.md | grep '^| '); echo "status=$(printf '%s\n' "$W" | grep -c "${Q}STATUS.md${Q}") reviews=$(printf '%s\n' "$W" | grep -c "${Q}docs/reviews/${Q}") contributing=$(printf '%s\n' "$W" | grep -c "${Q}CONTRIBUTING.md${Q}")")`
- THEN it prints exactly `status=1 reviews=1 contributing=1`

### Requirement: CONTRIBUTING.md says how work is proposed and chosen
`CONTRIBUTING.md` SHALL exist at the repository root. It SHALL give the steps Issue, Factory ticket and Spec gate as a numbered list in that order, state the rule for factory work, link `docs/north-star.md`, and carry no whitespace error.

#### Scenario: CONTRIBUTING.md gives the three steps and the rule, and links the north star
- WHEN `(C=CONTRIBUTING.md; [ -f $C ] || { echo "missing=$C"; exit 0; }; T=$(tr '\n' ' ' < $C | tr -s ' '); E=$(git hash-object -t tree /dev/null); echo "steps=$(grep -E '^[0-9]+\. \*\*' $C | sed -E 's/^[0-9]+\. \*\*([^*]*)\*\*.*/\1/' | tr '\n' '|') rule=$(printf '%s' "$T" | grep -oF -e 'fixes a defect that hit a target ticket' -e 'names the scorecard number it moves' -e 're-measures that number after it ships' -e 'spec gate' | sort -u | grep -c .) northstar=$(grep -c '](docs/north-star.md)' $C | awk '{print ($1 > 0)}') ws=$(git diff --check $E HEAD -- $C >/dev/null && echo clean || echo errors)")`
- THEN it prints exactly `steps=Issue.|Factory ticket.|Spec gate.| rule=4 northstar=1 ws=clean`

### Requirement: STATUS.md holds the north star, the baseline's figures, the focus, the queue and the experiments
`STATUS.md` SHALL exist at the repository root, at most 60 lines long. It SHALL open its body with the north star in one line, and hold the sections Scorecard, Current focus, Top of the queue, Open experiments and Links, in that order. It SHALL link `docs/north-star.md`, the latest review `docs/reviews/2026-10-19.md`, the folder `docs/reviews/`, the repository's issues and the store branch, and carry no whitespace error. Its Scorecard section SHALL link the baseline review, say its figures were counted by hand, and name `factory stats`. Its Scorecard table SHALL hold six rows with a column for the Nanobot port and one for spec-factory. Each cell MUST appear as a cell of that instance's table in `docs/reviews/2026-10-19.md`, and each figure in the section's prose MUST appear in that review.

#### Scenario: STATUS.md has its sections and links, and quotes only the baseline review's figures
- WHEN `(F=STATUS.md; R=docs/reviews/2026-10-19.md; [ -f $F ] || { echo "missing=$F"; exit 0; }; E=$(git hash-object -t tree /dev/null); C=$(sed -n '/^## Scorecard$/,/^## /p' $F | sed '1d;$d'); P=$(sed -n '/^## The Nanobot port$/,/^## Spec-factory/p' $R 2>/dev/null); G=$(sed -n '/^## Spec-factory/,/^## Escapes$/p' $R 2>/dev/null); cells=$(printf '%s\n' "$C" | grep -E '^\| [A-Z]' | sed 1d | while IFS='|' read -r _ _ a b _; do a=$(printf '%s' "$a" | sed 's/^ *//; s/ *$//'); b=$(printf '%s' "$b" | sed 's/^ *//; s/ *$//'); printf '%s\n' "$P" | grep -qF -e "| $a |" -e "| $a (" || echo x; printf '%s\n' "$G" | grep -qF -e "| $b |" -e "| $b (" || echo x; done | grep -c x); U=0; for t in $(printf '%s\n' "$C" | grep -v '^|' | sed -E 's/\[[^]]*\]\([^)]*\)//g; s/#[0-9]+//g; s/[0-9]{4}-[0-9]{2}-[0-9]{2}//g' | grep -oE '[0-9]+(\.[0-9]+)?'); do grep -qE "(^|[^0-9.])$(printf '%s' "$t" | sed 's/\./\\./')([^0-9.]|\$)" $R 2>/dev/null || U=$((U+1)); done; echo "lines=$(wc -l < $F | awk '{print ($1 <= 60 ? "within" : "over")}') sections=$(grep '^## ' $F | tr '\n' '|') northstar=$(grep -c '^\*\*North star:\*\* correct target changes per hour of operator attention' $F) links=$(grep -oF -e '](docs/north-star.md)' -e '](docs/reviews/)' -e '](docs/reviews/2026-10-19.md)' -e 'https://github.com/danielphang/spec-factory/issues' -e 'https://github.com/danielphang/spec-factory/tree/factory-store' $F | sort -u | grep -c .) scorecard=$(printf '%s' "$C" | tr '\n' ' ' | grep -oF -e '](docs/reviews/2026-10-19.md)' -e 'counted by hand' -e '`factory stats`' | sort -u | grep -c .) rows=$(printf '%s\n' "$C" | grep -E '^\| [A-Z]' | sed 1d | grep -c .) cells_unsourced=$cells prose_unsourced=$U ws=$(git diff --check $E HEAD -- $F >/dev/null && echo clean || echo errors)")`
- THEN it prints exactly `lines=within sections=## Scorecard|## Current focus|## Top of the queue|## Open experiments|## Links| northstar=1 links=5 scorecard=3 rows=6 cells_unsourced=0 prose_unsourced=0 ws=clean`

### Requirement: The review template holds the six sections a review fills in
`docs/reviews/TEMPLATE.md` SHALL hold six numbered `## ` sections in this order:
1. the scorecard against the last review, taken from `factory stats`, naming the baseline review as the one counted by hand;
2. what was worked on;
3. what was chosen not to do, linking `docs/decided-against.md`;
4. successes and failures;
5. experiments and side work, naming the `experiment` label;
6. decisions and the new queue order.

It SHALL also link `STATUS.md`.

#### Scenario: The review template's sections are the six the request lists, in order
- WHEN `(F=docs/reviews/TEMPLATE.md; [ -f $F ] || { echo "missing=$F"; exit 0; }; Q=$(printf '\140'); grep '^## ' $F; y() { [ "$1" -gt 0 ] && echo yes || echo no; }; echo "decided=$(y $(sed -n '/^## 3\. /,/^## 4\. /p' $F | grep -c '](../decided-against.md)')) experiment=$(y $(sed -n '/^## 5\. /,/^## 6\. /p' $F | grep -c "${Q}experiment${Q}")) stats=$(y $(sed -n '/^## 1\. /,/^## 2\. /p' $F | grep -c 'factory stats')) baseline=$(y $(sed -n '/^## 1\. /,/^## 2\. /p' $F | grep -c '](2026-10-19.md)')) status=$(y $(grep -c '](../../STATUS.md)' $F))")`
- THEN it prints exactly `## 1. Scorecard against the last review`, `## 2. What we worked on`, `## 3. What we chose not to do`, `## 4. Successes and failures`, `## 5. Experiments and side work`, `## 6. Decisions and the new queue order`, `decided=yes experiment=yes stats=yes baseline=yes status=yes`, one per line

### Requirement: The baseline review is the operator's baseline, verbatim
`docs/reviews/2026-10-19.md` SHALL exist. Its first line SHALL be `# Review 2026-10-19: baseline scorecard, 2026-10-03 to 2026-10-19`. Every line after the first SHALL be byte for byte the operator's baseline after its own title line, as recorded on the store branch at `02e403f` in `requests/T-0055.md`. The file SHALL carry no whitespace error.

#### Scenario: The baseline review matches the operator's text after its first line
- WHEN `(F=docs/reviews/2026-10-19.md; [ -f $F ] || { echo "missing=$F"; exit 0; }; E=$(git hash-object -t tree /dev/null); a=$(sed 1d $F | git hash-object --stdin); b=$(git show 02e403f:requests/T-0055.md | sed -n '/^--- baseline begins ---$/,/^--- baseline ends ---$/p' | sed '1,2d;$d' | git hash-object --stdin); echo "head=$(head -1 $F)"; echo "body=$([ "$a" = "$b" ] && echo verbatim || echo differs) ws=$(git diff --check $E HEAD -- $F >/dev/null && echo clean || echo errors)")`
- THEN it prints exactly `head=# Review 2026-10-19: baseline scorecard, 2026-10-03 to 2026-10-19`, then `body=verbatim ws=clean`

### Requirement: The new pages' relative links resolve
Every relative Markdown link in `STATUS.md`, `CONTRIBUTING.md` and `docs/reviews/TEMPLATE.md` SHALL name a path that exists, resolved from the linking file's directory, and each of the three SHALL hold at least one such link.

#### Scenario: No relative link in the three new pages is broken
- WHEN `(for f in STATUS.md CONTRIBUTING.md docs/reviews/TEMPLATE.md; do [ -f "$f" ] || { echo "$f missing"; continue; }; d=$(dirname "$f"); n=0; bad=0; for l in $(grep -oE '\]\([^)#]+\)' "$f" | sed -E 's/^\]\(//; s/\)$//' | grep -v '^[a-z]*:'); do n=$((n+1)); [ -e "$d/$l" ] || bad=$((bad+1)); done; echo "$f relative=$([ $n -gt 0 ] && echo some || echo none) broken=$bad"; done)`
- THEN it prints exactly `STATUS.md relative=some broken=0`, `CONTRIBUTING.md relative=some broken=0`, `docs/reviews/TEMPLATE.md relative=some broken=0`, one per line

### Requirement: The changelog records issue 116
`docs/changelog.md` SHALL hold exactly one entry opening `<n>. After issue #116 `. The entry SHALL name `docs/north-star.md`, `STATUS.md`, `CONTRIBUTING.md`, `docs/reviews/TEMPLATE.md`, `docs/reviews/2026-10-19.md`, the primary metric and the spec gate. The entries SHALL stay numbered without a gap, and the changelog SHALL end with its `Declined:` line.

#### Scenario: The changelog records issue 116 in one entry without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #116 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e 'docs/north-star.md' -e 'STATUS.md' -e 'CONTRIBUTING.md' -e 'docs/reviews/TEMPLATE.md' -e 'docs/reviews/2026-10-19.md' -e 'per hour of operator attention' -e 'spec gate' | sort -u | grep -c .) last=$(tail -1 docs/changelog.md | grep -c '^Declined:')")`
- THEN it prints `CONTIGUOUS`, then `entries=1 terms=7 last=1`

=== verification.md
## Acceptance

Run every command from the repository root of the checkout under test, through the HOME wrapper. "Today" means `main` at `788a201`, run on 2026-10-20. The baseline-review scenario reads commit `02e403f` on the store branch, which every checkout of this repository shares.

- The north star holds the measurement section and keeps its measures and target sentence → NEW. Today it prints `heading=0 second=0 terms=0 rows=0 measures=4 serves=1`: there is no measurement section, while the four measures and the target sentence are already there.
- The north star's working rules include the rule for factory work → NEW. Today it prints `rule=0 terms=0 four=0 three=1`: the section still introduces three working rules, and none of them is the rule for factory work.
- README opens with the north-star paragraph and stays within its budget → NEW. Today it prints `block=0 top=0 metric=0 links=0 readme=within`: README has no north-star paragraph.
- The filing section states the rule for factory work → NEW. Today it prints `terms=0`.
- Where things live has a row for each new file → NEW. Today it prints `status=0 reviews=0 contributing=0`.
- CONTRIBUTING.md gives the three steps and the rule, and links the north star → NEW. Today it prints `missing=CONTRIBUTING.md`.
- STATUS.md has its sections and links, and quotes only the baseline review's figures → NEW. Today it prints `missing=STATUS.md`.
- The review template's sections are the six the request lists, in order → NEW. Today it prints `missing=docs/reviews/TEMPLATE.md`.
- The baseline review matches the operator's text after its first line → NEW. Today it prints `missing=docs/reviews/2026-10-19.md`.
- No relative link in the three new pages is broken → NEW. Today it prints `STATUS.md missing`, `CONTRIBUTING.md missing`, `docs/reviews/TEMPLATE.md missing`.
- The changelog records issue 116 in one entry without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `entries=0 terms=0 last=1`: there is no entry for issue #116.

On the prototype (Proposed change A to G applied to a clone of this repository at `788a201`, in this run's scratch directory; the clone carries the store branch's commits), every scenario printed exactly its THEN line. The STATUS.md scenario's prose check matches figures one number at a time, so it is weak: a mistyped 6 for 5 passes it, because 6 occurs elsewhere in the review. Its table check is strict, and it caught both mistyped cells I tried (Evidence). The current-truth harness-docs scenarios still apply after this change, among them README's 1,185-line budget (the prototype has 1,182 lines), the whitespace check over `README.md`, `docs/` and `dev/`, and the north star's target sentence. All 76 that need no harness run printed the same on the prototype as on `788a201` (Evidence).
