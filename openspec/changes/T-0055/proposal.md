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

## Evidence

Checked on `main` at `788a201`, which is still the tip on 2026-10-20:
- `docs/north-star.md:14-19` lists the four success measures and sets no target. The nearest rule, "Measure before and after" (`docs/north-star.md:60-61`), covers efficiency changes only. `docs/north-star.md:21` already uses "targets" for the products the factory builds, separate from "its own development".
- `ls` at the repository root shows no `CONTRIBUTING.md`, no `STATUS.md` and no `docs/reviews/`. `docs/decided-against.md` exists, so the review template can link it.
- `README.md` has 1,174 lines. The current-truth requirement "README stays within its line budget" caps it at 1,185. README's prose is wrapped at about 100 characters, and it writes paths as code, never as Markdown links (`grep -c '](' README.md` prints 0).
- T-0058, a bug ticket for four small harness defects, is at the same spec gate (`.factory/store/tickets/T-0058.yaml`: `awaiting-spec-gate`). Its Proposed change E (`.factory/store/specs/T-0058.md:107-112`) edits README in four places and requires README to stay within 1,185 lines. By my reading, one of those edits wraps to a second line, at README line 611, and the other three keep their line count. So T-0058 adds about one line to README. I did not build T-0058's change.
- The operator's baseline is on the store branch at commit `02e403f`, in `requests/T-0055.md`, between the lines `--- baseline begins ---` and `--- baseline ends ---`. That text is identical to the baseline in this run's input. Its spec-factory table gives 30 changes merged from 10-03 to 10-11 and 12 from 10-12 to 10-19. Its Nanobot table gives 26 and 1.
- Issue #96, the work queue, was re-ordered on 2026-10-19 (`gh issue view 96`): row 1 is #116 (this change), then #117 (the scorecard), #105 (the spec validator, "a defect that parked a target-side ticket") and #118 (the benchmark).
- The store branch is on GitHub (`git ls-remote origin factory-store`, round 1), so `STATUS.md` can link it.
- `gh repo view danielphang/spec-factory --json description` prints the repository's current About text: "A spec-driven AI software pipeline: a written request becomes merged, verified code with as little operator attention as the work allows." It already states the purpose.
- `docs/changelog.md` entry 73 (issue #110) was added by commit `21f90c4`, which changed `README.md`, `docs/changelog.md`, `docs/north-star.md` and the new `docs/standards.md`, and not `docs/design.md`. T-0049, which declined an entry, merged as `1058db5`, which changed `README.md` alone.
- `grep -rlE 'north-star|STATUS\.md|CONTRIBUTING|1185|docs/reviews' tests factory agents` prints nothing and exits 1. No harness test or code reads these documents.
- Prototype. I applied Proposed change A to G to a clone of this repository at `788a201`, in this run's scratch directory. `git diff --stat 788a201 HEAD` there reports 7 files changed, 299 insertions and 2 deletions; 100 of the added lines are the operator's baseline. README ends at 1,182 lines. Every scenario prints its THEN line on the prototype. On `788a201` each fails as `verification.md` records.
- Negative checks on the prototype. Changing one figure in `STATUS.md`'s table (27 to 28, or 5 + 3 to 5 + 2) makes the STATUS.md scenario print `cells_unsourced=1`. Appending one line to the baseline review makes its scenario print `body=differs`.
- I ran the 76 current-truth harness-docs scenario commands that need no harness run (none calls `bin/factory`, pytest, node or uv) on both trees. All 76 printed the same on the prototype as on `788a201`, apart from the checkout's path in two error messages. Those two need a fixture file their GIVEN lines create, and they fail the same way on both trees. The three README budget scenarios print `readme=within` on the prototype, and `git diff --check` over `README.md`, `docs`, `dev`, `STATUS.md` and `CONTRIBUTING.md` exits 0.
- Not verified: that GitHub shows `CONTRIBUTING.md` as a tab on the overview. I found no official GitHub page on the tab layout. Operator step 3 checks it.

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

