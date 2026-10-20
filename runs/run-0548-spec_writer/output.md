=== proposal.md
## Problem

The spec factory is an AI pipeline that turns a written request into merged code. A human, the operator, approves each design at the spec gate before any code is written. The factory works on two kinds of repository. One is its own code, here in this repository. The other is a target: a product it builds, today a port of the Nanobot chat bot. Work on the factory itself is called factory work.

Nothing measures factory work against a bar set outside the factory. The north-star page, `docs/north-star.md`, is where the operator records what the factory is for. It names four success measures, but it sets no target for any of them, nothing reports them, and nobody reviews them. So the operator has chosen factory work in answer to the factory's own incidents, not by whether it helps the product. Since 2026-10-10 this repository has merged into `main` 22 times, against 3 tickets built on the Nanobot port. The north star is also hard to find. The repository's front page opens with how the system works, and the repository has no contributor guide.

The operator asked for five things:
- a primary metric with a constraint, and a scorecard of named numbers;
- a rule that factory work must serve the product or move a number;
- a review every two weeks;
- a one-page status file;
- the north star placed where GitHub visitors see it.

This change writes them as documents. It changes no harness code and no role prompt.

## Evidence

Checked on `main` at `788a201`:
- `docs/north-star.md:14-19` lists the four success measures and sets no target. The nearest rule, "Measure before and after" (`docs/north-star.md:61-62`), covers efficiency changes only. `docs/north-star.md:21` already uses "targets" for the products the factory builds, separate from "its own development". This spec keeps that meaning.
- `ls` at the repository root shows `README.md agents bin dev docs factory pyproject.toml tests uv.lock`. There is no `CONTRIBUTING.md`, no `STATUS.md` and no `docs/reviews/`. `docs/decided-against.md` exists, so the review template can link it.
- `README.md` has 1,174 lines. The current-truth requirement "README stays within its line budget" caps it at 1,185. The scenarios of two other current-truth requirements, the ones for issues #108 and #109, also check `<= 1185`.
- `git ls-remote origin factory-store` prints `04e234c… refs/heads/factory-store`. The store branch, which holds the factory's record of every ticket and run, is on GitHub, so `STATUS.md` can link it.
- `grep -rlE 'north-star|STATUS\.md|CONTRIBUTING|1185|docs/reviews' tests factory agents` prints nothing (exit 1). No harness test or code reads these documents.
- The scorecard request, T-0056 (issue #117), asks `factory stats` to compute five numbers: target changes merged, escapes, operator decisions and interventions per change, cost and wall time per change, and lead time. The north star's scorecard table names those five, so the later ticket has one source to build from.
- Prototype. I applied Proposed change A to F to a copy of `main` in my scratch directory. The result is 174 lines added and 1 deleted, and README ends at exactly 1,185 lines. Every scenario in this spec prints its expected result on the prototype. On `main` each NEW scenario fails as `verification.md` records.
- I also ran the 76 current-truth scenario commands that need no harness run (none of them call `bin/factory`, pytest or node) on both trees. 75 printed the same on `main` and on the prototype. The other one compares files against commit `7231670`, which the prototype's fresh history lacks. My edits do not touch the files it checks. So this change breaks no current-truth document check.
- Not verified: the request says GitHub shows a Contributing tab next to README on a repository's overview. I searched and found no official GitHub page on the tab layout. The file is useful either way. Operator step 3 checks the tab.
- Not verified: the request's figure of 3 Nanobot tickets since 2026-10-10. Triage did not check it either. No part of the spec depends on it.

## Root cause

The north star sets measures but no targets, no scorecard and no review (`docs/north-star.md:14-19`). No document states a rule for choosing factory work. The front page (`README.md:1-12`) and the repository root give no path to the north star beyond one row in README's "Where things live" table (`README.md:1090`).

## Out of scope

- No change to harness code (`factory/`, `bin/factory`), role prompts (`docs/prompts/`, `agents/`), `docs/design.md`, `docs/writing.md`, `docs/standards.md` or `pyproject.toml`. No role or harness check enforces the rule for factory work. The operator applies it at the spec gate.
- Computing the scorecard. That is T-0056 (#117). This change names the numbers only.
- The upstream benchmark and `docs/benchmark.md`. That is T-0060 (#118).
- The first review (`docs/reviews/2026-11-02.md`), and changes to the queue issue #96 or to `dev/issues.md`. These are operator work after the merge.
- A licence file. The request leaves it to the operator.
- The north star's four success measures, its eight non-negotiables, its "Where it is heading" list, and its sentence on whom the factory serves. All stay word for word.

## Open questions

1. **How is "an hour of operator attention" counted?** The store records operator decisions, not operator time. The scorecard request asks `factory stats` to count "operator decisions and interventions per change", not hours. The request also says nobody types the numbers. So the primary metric's denominator has no source today. Options:
   - (a) Recommended. Until the store records operator time, the scorecard reports decisions and interventions per change in place of hours, and says so. Proposed change A then adds one sentence to that effect.
   - (b) The operator records time per change by hand. This conflicts with "nobody types them".
   - (c) `factory stats` estimates time from the timestamps of the operator's commands. This undercounts reading time.

   Standing: yes. The scorecard ticket, T-0056, must follow the answer.
2. **What should `STATUS.md` say before the first review?** It may quote only a review's numbers, and no review has run yet. Triage asked that the operator confirm this wording. Proposed (Proposed change D gives the full text):
   - Scorecard: "No scorecard yet". No review has run, `factory stats` does not compute it yet, and the first review is on 2026-11-02.
   - Current focus: the scorecard, then the upstream benchmark.
   - Top of the queue: #117, then #118, as of 2026-10-19, taken from the request's Order line.
   - Open experiments: none yet.

   Rejected: quoting today's hand counts, such as the 22 merges. Requirement D forbids numbers typed between reviews. Standing: no.

## Decisions

- A target change is a change merged into a target's repository. A change to the factory itself is factory work and does not count as one. This follows the request's contrast between factory tickets and Nanobot tickets, and `docs/north-star.md:21`. Standing: the scorecard counts target changes this way.
- The four existing success measures stay. The new section, "How we know it is working", says how they are scored. Rejected: replacing them. The request asks for a new section, not a rewrite.
- The rule for factory work becomes a fourth working rule in the north star's "How it decides where effort goes", beside "Measure before and after". README's "Filing a request from an issue tracker" and `CONTRIBUTING.md` restate it in short. Standing: every later factory ticket's request says which half of the rule it meets, and the operator applies the rule at the spec gate.
- The scorecard table names the five numbers the scorecard request asks `factory stats` to compute. Change failure rate is escapes divided by target changes merged. It is defined under the outside comparisons, not added as a sixth row. Rejected: a sixth row, which would add a requirement the scorecard ticket did not ask for.
- Until `factory stats` computes a number, a review writes "not yet computed". Nobody counts a number by hand.
- README's first screen and `STATUS.md` link the folder `docs/reviews/`, not one named review, so a review never has to edit README. The folder lists every review, named by date, beside the template.
- README stays within 1,185 lines: four lines for the north-star paragraph, three for the rule, and two table rows, with `STATUS.md` and `docs/reviews/` sharing one row. Rejected: raising the budget to 1,200. That would modify three current-truth requirements that pin 1,185, for lines this change does not need. README then sits exactly at its budget, so the next change that adds a line to README raises the budget in its own spec.
- The first-screen block is a paragraph that opens with the bold label "North star.". It is not a heading, because README's "Headings are the contract" rule keeps its section names and order fixed.
- One changelog entry records the change, as issue #110's earlier north-star change had one.
- The review template reminds the writer that this repository is public. A review names a change by ticket id and gives counts. It names no private product and links no private issue. This follows the scorecard request's note that an escape's issue may be in a private tracker, and the current-truth requirement that the north star names no private product.

## Risk

The change is documents only: five files, about 175 lines. A wrong number or a misleading rule would steer which factory work gets approved, so the operator reads the north-star text at this gate. No harness code, prompt or test changes, and no role's input changes. Role inputs carry neither README nor `docs/north-star.md`. README sits exactly at its 1,185-line budget afterwards. Every changed path is unprotected.
Protected paths: none

## Operator steps

1. Create the label: `gh label create experiment -R danielphang/spec-factory --description "Side work that tries an idea; each review reports its result"`.
2. Set the About description: `gh repo edit danielphang/spec-factory --description "An AI software pipeline that turns a written request into merged, verified code, with as little of the operator's attention as the work allows."`. Change the wording if you like. It should state the purpose.
3. Open https://github.com/danielphang/spec-factory and check that GitHub shows `CONTRIBUTING.md` as a tab or link on the overview. I could not confirm the tab layout from GitHub's documentation.
4. On 2026-11-02, write the first review, `docs/reviews/2026-11-02.md`, from `docs/reviews/TEMPLATE.md`. Then re-order issue #96 and rewrite `STATUS.md` from that review.

=== design.md
## Proposed change

One sub-ticket. The texts below are the prototype's, checked by every scenario. The implementer may reword any sentence. It must keep verbatim each phrase a scenario greps for, and README must end at no more than 1,185 lines.

**A. `docs/north-star.md`.**

A1. Insert a new section directly after the line `The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).` and before `## What it will not trade away`. The paragraph marked [Q1] is for open question 1's recommended answer (a). Drop or change it to match the operator's answer.

```
## How we know it is working

The measures above are judged against a bar set outside the factory: what it delivers to its
targets, not how closely it follows its own rules. A target change is a change merged into a
target's repository. A change to the factory itself is factory work, and does not count as one.

- **Primary metric:** correct target changes per hour of operator attention. A change is correct
  when no escape is recorded against it.
- **Constraint:** escaped defects do not rise. An escape is a merged change that later needed a fix
  or a revert.
- **Second measure:** cost, as tokens and wall time per change.

The scorecard gives these numbers for a window of time, per target, beside the same numbers for the
window before. `factory stats` computes them from the store, and nobody types them. Until it does, a
review writes "not yet computed" rather than count a number by hand.

| Number | What it counts |
|---|---|
| Target changes merged | tickets closed with a merge |
| Escapes | merged changes that later needed a fix or a revert |
| Operator decisions and interventions per change | each gate decision, ruling or resolve, and each intervention made outside the CLI |
| Tokens and wall time per change | the cost of the role runs behind each merged change |
| Lead time | the time from a request's creation to its merge |

[Q1] The store records operator decisions, not operator time. Until it records time, the scorecard
counts operator decisions and interventions per change in place of hours of operator attention.

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
latest review. The first review is on 2026-11-02.
```

A2. In "How it decides where effort goes", change `And three working rules that follow from them:` to `And four working rules that follow from them:`, and insert this bullet as the first of the list:

```
- **Factory work serves a target or a number.** A factory ticket goes ahead only if it fixes a defect
  that hit a target ticket, or names the scorecard number it moves and re-measures that number after
  it ships. Its request says which. The operator applies this rule at the spec gate; no role prompt
  or harness check enforces it.
```

Nothing else in the file changes.

**B. `README.md`.** Nine lines added. The prototype ends at exactly 1,185.

B1. Between the opening paragraph (which ends `"Where it runs" and "Starting a run".`) and the status table, insert the following, followed by a blank line:

```
**North star.** The factory turns a written request into merged, verified code with as little of the
operator's attention as the work allows. Its primary metric is correct changes to the product it builds,
today a port of the Nanobot chat bot, per hour of operator attention, while escaped defects do not rise.
More in `docs/north-star.md`; the latest numbers and focus in `STATUS.md`; reviews in `docs/reviews/`.
```

It says "the product it builds", not "target". README's glossary uses "target" for any repository the factory runs on, and that includes this one.

B2. In "Filing a request from an issue tracker", after the paragraph ending `kept by hand in both directions.`, insert the following, followed by a blank line:

```
A request to change the factory itself goes ahead only if it fixes a defect that hit a ticket of the
product the factory builds, or names the scorecard number it moves and re-measures that number after it
ships. The request says which. The operator applies the rule at the spec gate; see `docs/north-star.md`.
```

B3. In "Where things live", after the `docs/north-star.md` row, insert:

```
| `STATUS.md`, `docs/reviews/` | The latest scorecard, focus and queue, rewritten only at a review; each review, written from `docs/reviews/TEMPLATE.md` |
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

**D. New `STATUS.md`** at the repository root, at most 60 lines. This is the pre-review version that open question 2 asks the operator to confirm:

```
# Status

This page is rewritten only at a review, and every number on it is as of the review it names.
Last rewritten: 2026-10-19, before the first review.

**North star:** correct target changes per hour of operator attention, while escaped defects do
not rise. The full position is [docs/north-star.md](docs/north-star.md).

## Scorecard

No scorecard yet: no review has run, and `factory stats` does not yet compute the scorecard. The
first review is on 2026-11-02.

## Current focus

Measuring the north star: the scorecard in `factory stats`, then the upstream benchmark.

## Top of the queue

The queue is [issue #96](https://github.com/danielphang/spec-factory/issues/96), re-ordered at
each review. Its top as of 2026-10-19:

1. The scorecard in `factory stats` ([#117](https://github.com/danielphang/spec-factory/issues/117)).
2. The upstream benchmark ([#118](https://github.com/danielphang/spec-factory/issues/118)).

## Open experiments

None yet. Experiments are issues labelled
[`experiment`](https://github.com/danielphang/spec-factory/issues?q=is%3Aopen+label%3Aexperiment).

## Links

- Latest review: none yet; reviews and their template are in [docs/reviews/](docs/reviews/).
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
type or adjust a number. Write "not yet computed" for a number it does not compute yet.

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

**F. `docs/changelog.md`.** Add one entry after the last numbered entry and before the closing `Declined:` line, numbered next without a gap (76 on `788a201`). Prototype text:

```
76. After issue #116 (2026-10-19), where the factory's own work had no outside bar: `docs/north-star.md` named four success measures but set no target for any of them, nothing reported them and nobody reviewed them, so factory work was chosen in answer to the factory's own incidents. `docs/north-star.md` gains "How we know it is working": the primary metric, correct target changes per hour of operator attention; its constraint, that escaped defects do not rise; cost as the second measure; the scorecard's numbers by name, which `factory stats` is to compute so that nobody types them; three outside comparisons, a plain-session baseline, the upstream benchmark and DORA-style lead time and change failure rate; and a review every two weeks. A fourth working rule admits a factory ticket only if it fixes a defect that hit a target ticket, or names the scorecard number it moves and re-measures it after it ships; the operator applies it at the spec gate, and no role prompt or harness check does. New files: `docs/reviews/TEMPLATE.md`, which each review copies; `STATUS.md`, which each review rewrites; and `CONTRIBUTING.md`, which says how work is proposed and chosen. README gains a north-star paragraph on its first screen, the rule in "Filing a request from an issue tracker" and two rows in "Where things live", and stays within its 1,185-line budget. Rejected: a role prompt or harness check that enforces the rule, which the request rules out; and quoting today's hand counts in `STATUS.md`, which may quote only a review's numbers.
```

If the operator's answer to open question 1 is not (a), the entry names the answer instead.

## Tests to change

none. No decision overturns behaviour a test pins. `grep -rlE 'north-star|STATUS\.md|CONTRIBUTING|1185|docs/reviews' tests factory agents` finds nothing.

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The north star says how the factory's work is measured and reviewed
`docs/north-star.md` SHALL hold, as its second `## ` section, "How we know it is working". That section SHALL name the primary metric, its constraint, cost as the second measure, the scorecard's five numbers as table rows, the plain-session baseline, the upstream benchmark, change failure rate, and a review every two weeks from `docs/reviews/TEMPLATE.md` that rewrites `STATUS.md`, the first on 2026-11-02. The file MUST keep its four success measures and its sentence on whom the factory serves.

#### Scenario: The north star holds the measurement section and keeps its measures and target sentence
- WHEN `(N=docs/north-star.md; X=$(awk '/^## How we know it is working$/{f=1;next} f&&/^## /{f=0} f' $N); S=$(printf '%s' "$X" | tr '\n' ' ' | tr -s ' '); echo "heading=$(grep -cx '## How we know it is working' $N) second=$(grep '^## ' $N | sed -n 2p | grep -cx '## How we know it is working') terms=$(printf '%s' "$S" | grep -oF -e 'correct target changes per hour of operator attention' -e 'escaped defects do not rise' -e 'tokens and wall time per change' -e 'plain-session baseline' -e 'upstream benchmark' -e 'change failure rate' -e 'every two weeks' -e 'docs/reviews/TEMPLATE.md' -e 'STATUS.md' -e '2026-11-02' | sort -u | grep -c .) rows=$(printf '%s\n' "$X" | grep -cE '^\| (Target changes merged|Escapes|Operator decisions and interventions per change|Tokens and wall time per change|Lead time) \|') measures=$(sed -n '/^Success is measured as:$/,/^$/p' $N | grep -c '^- ') serves=$(grep -cxF 'The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).' $N)")`
- THEN it prints exactly `heading=1 second=1 terms=10 rows=5 measures=4 serves=1`

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
README's "Filing a request from an issue tracker" SHALL say that a request to change the factory goes ahead only if it fixes a defect that hit a ticket of the product, or names the scorecard number it moves and re-measures that number after it ships. It SHALL also say that the operator applies the rule at the spec gate, and SHALL point to `docs/north-star.md`.

#### Scenario: The filing section states the rule and points to the north star
- WHEN `(F=$(sed -n '/^### Filing a request from an issue tracker$/,/^### Running many tickets/p' README.md | tr '\n' ' ' | tr -s ' '); echo "terms=$(printf '%s' "$F" | grep -oF -e 'goes ahead only if' -e 'fixes a defect that hit a ticket' -e 'names the scorecard number it moves' -e 're-measures that number after it ships' -e 'spec gate' -e 'docs/north-star.md' | sort -u | grep -c .)")`
- THEN it prints exactly `terms=6`

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

### Requirement: STATUS.md holds the north star, the scorecard, the focus, the queue and the experiments
`STATUS.md` SHALL exist at the repository root, at most 60 lines long. It SHALL open its body with the north star in one line, and hold the sections Scorecard, Current focus, Top of the queue, Open experiments and Links, in that order. It SHALL link `docs/north-star.md`, `docs/reviews/`, the repository's issues and the store branch, and carry no whitespace error. Before the first review, its Scorecard section MUST quote no number and SHALL name the first review's date.

#### Scenario: STATUS.md has its sections and links, and quotes no number before the first review
- WHEN `(F=STATUS.md; [ -f $F ] || { echo "missing=$F"; exit 0; }; E=$(git hash-object -t tree /dev/null); echo "lines=$(wc -l < $F | awk '{print ($1 <= 60 ? "within" : "over")}') sections=$(grep '^## ' $F | tr '\n' '|') northstar=$(grep -c '^\*\*North star:\*\* correct target changes per hour of operator attention' $F) links=$(grep -oF -e '](docs/north-star.md)' -e '](docs/reviews/)' -e 'https://github.com/danielphang/spec-factory/issues' -e 'https://github.com/danielphang/spec-factory/tree/factory-store' $F | sort -u | grep -c .) first=$(sed -n '/^## Scorecard$/,/^## /p' $F | tr '\n' ' ' | grep -c 'No scorecard yet.*2026-11-02') numbers=$(sed -n '/^## Scorecard$/,/^## /p' $F | sed '1d;$d' | sed 's/2026-11-02//g' | grep -c '[0-9]') ws=$(git diff --check $E HEAD -- $F >/dev/null && echo clean || echo errors)")`
- THEN it prints exactly `lines=within sections=## Scorecard|## Current focus|## Top of the queue|## Open experiments|## Links| northstar=1 links=4 first=1 numbers=0 ws=clean`

### Requirement: The review template holds the six sections a review fills in
`docs/reviews/TEMPLATE.md` SHALL hold six numbered `## ` sections in this order:
1. the scorecard against the last review, taken from `factory stats`;
2. what was worked on;
3. what was chosen not to do, linking `docs/decided-against.md`;
4. successes and failures;
5. experiments and side work, naming the `experiment` label;
6. decisions and the new queue order.

It SHALL also link `STATUS.md`.

#### Scenario: The review template's sections are the six the request lists, in order
- WHEN `(F=docs/reviews/TEMPLATE.md; [ -f $F ] || { echo "missing=$F"; exit 0; }; Q=$(printf '\140'); grep '^## ' $F; y() { [ "$1" -gt 0 ] && echo yes || echo no; }; echo "decided=$(y $(sed -n '/^## 3\. /,/^## 4\. /p' $F | grep -c '](../decided-against.md)')) experiment=$(y $(sed -n '/^## 5\. /,/^## 6\. /p' $F | grep -c "${Q}experiment${Q}")) stats=$(y $(sed -n '/^## 1\. /,/^## 2\. /p' $F | grep -c 'factory stats')) status=$(y $(grep -c '](../../STATUS.md)' $F))")`
- THEN it prints exactly `## 1. Scorecard against the last review`, `## 2. What we worked on`, `## 3. What we chose not to do`, `## 4. Successes and failures`, `## 5. Experiments and side work`, `## 6. Decisions and the new queue order`, `decided=yes experiment=yes stats=yes status=yes`, one per line

### Requirement: The new pages' relative links resolve
Every relative Markdown link in `STATUS.md`, `CONTRIBUTING.md` and `docs/reviews/TEMPLATE.md` SHALL name a path that exists, resolved from the linking file's directory, and each of the three SHALL hold at least one such link.

#### Scenario: No relative link in the three new pages is broken
- WHEN `(for f in STATUS.md CONTRIBUTING.md docs/reviews/TEMPLATE.md; do [ -f "$f" ] || { echo "$f missing"; continue; }; d=$(dirname "$f"); n=0; bad=0; for l in $(grep -oE '\]\([^)#]+\)' "$f" | sed -E 's/^\]\(//; s/\)$//' | grep -v '^[a-z]*:'); do n=$((n+1)); [ -e "$d/$l" ] || bad=$((bad+1)); done; echo "$f relative=$([ $n -gt 0 ] && echo some || echo none) broken=$bad"; done)`
- THEN it prints exactly `STATUS.md relative=some broken=0`, `CONTRIBUTING.md relative=some broken=0`, `docs/reviews/TEMPLATE.md relative=some broken=0`, one per line

### Requirement: The changelog records issue 116
`docs/changelog.md` SHALL hold exactly one entry opening `<n>. After issue #116 `. The entry SHALL name `docs/north-star.md`, `STATUS.md`, `CONTRIBUTING.md`, `docs/reviews/TEMPLATE.md`, the primary metric and the spec gate. The entries SHALL stay numbered without a gap, and the changelog SHALL end with its `Declined:` line.

#### Scenario: The changelog records issue 116 in one entry without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #116 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e 'docs/north-star.md' -e 'STATUS.md' -e 'CONTRIBUTING.md' -e 'docs/reviews/TEMPLATE.md' -e 'per hour of operator attention' -e 'spec gate' | sort -u | grep -c .) last=$(tail -1 docs/changelog.md | grep -c '^Declined:')")`
- THEN it prints `CONTIGUOUS`, then `entries=1 terms=6 last=1`

=== verification.md
## Acceptance

Run every command from the repository root of the checkout under test. "Today" means `main` at `788a201`, run through the HOME wrapper on 2026-10-19.

- The north star holds the measurement section and keeps its measures and target sentence → NEW. Today it prints `heading=0 second=0 terms=0 rows=0 measures=4 serves=1`: there is no measurement section, while the four measures and the target sentence are already there.
- The north star's working rules include the rule for factory work → NEW. Today it prints `rule=0 terms=0 four=0 three=1`: the section still introduces three working rules, and none of them is the rule for factory work.
- README opens with the north-star paragraph and stays within its budget → NEW. Today it prints `block=0 top=0 metric=0 links=0 readme=within`: README has no north-star paragraph.
- The filing section states the rule and points to the north star → NEW. Today it prints `terms=0`.
- Where things live has a row for each new file → NEW. Today it prints `status=0 reviews=0 contributing=0`.
- CONTRIBUTING.md gives the three steps and the rule, and links the north star → NEW. Today it prints `missing=CONTRIBUTING.md`.
- STATUS.md has its sections and links, and quotes no number before the first review → NEW. Today it prints `missing=STATUS.md`.
- The review template's sections are the six the request lists, in order → NEW. Today it prints `missing=docs/reviews/TEMPLATE.md`.
- No relative link in the three new pages is broken → NEW. Today it prints `STATUS.md missing`, `CONTRIBUTING.md missing`, `docs/reviews/TEMPLATE.md missing`.
- The changelog records issue 116 in one entry without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `entries=0 terms=0 last=1`: there is no entry for issue #116.

On the prototype (Proposed change A to F applied to a copy of `788a201`, in this run's scratch directory), every scenario printed exactly its THEN line. The current-truth harness-docs scenarios still apply after this change. They include README's 1,185-line budget, the whitespace check over `README.md`, `docs/` and `dev/`, and the north star's target sentence. 75 of the 76 that need no harness run printed the same on the prototype as on `main` (Evidence).

Out-of-scope observations:
- README's "Related work and history" says "The store holds 54 tickets and 68 sub-tickets". `ls .factory/store/tickets` counts 60 ticket files and 68 sub-ticket files. That figure belongs to whichever change next re-derives it, not to this one.

STATUS: NEEDS-HUMAN
CONFIDENCE: medium. Every NEW scenario fails on `main` and passes on a prototype that fits README's budget, and no current-truth document check changed. But the primary metric's denominator (open question 1) has no source in the store, and the operator must choose how it is counted before the scorecard ticket builds on it.
ESCALATIONS: none
