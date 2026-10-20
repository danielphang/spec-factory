Type: chore (documentation and process: no harness, prompt or code change)

Title: North star: a primary metric, a two-weekly review and a rule for choosing factory work, shown on the repo's front page

Summary:
The operator wants the factory's own work measured against a bar set outside the factory. Today it is chosen in response to the factory's own incidents. `docs/north-star.md` gains a section with five parts: the primary metric (correct target changes per hour of operator attention), its constraint (escaped defects do not rise), cost as the second measure, the scorecard's numbers by name, and three outside comparisons (a plain-session baseline, the upstream benchmark, and DORA-style lead time and change failure rate). A factory ticket goes ahead only if it fixes a defect that hit a target ticket, or if it names the scorecard number it moves and re-measures that number after it ships. README's "Filing a request from an issue tracker" states this rule. Reviews run every two weeks (monthly when there is little to discuss) from a new `docs/reviews/TEMPLATE.md`. Each review re-orders the queue issue #96 and rewrites a new root `STATUS.md`. The operator also wants the north star easy to find on GitHub: a short block on README's first screen, a new `CONTRIBUTING.md` that GitHub shows as its own tab, and the repo's About description, which is an operator step.

Evidence:
- Issue https://github.com/danielphang/spec-factory/issues/116 (operator, 2026-10-19; Discussion #119). Requirements A to E and the operator steps are quoted in the request.
- Checked on `main` at 788a201:
  - `docs/north-star.md:14-19` lists four success measures and sets no target for any of them. The closest rule, "Measure before and after" at `docs/north-star.md:61-62`, covers efficiency changes only.
  - `CONTRIBUTING.md`, `STATUS.md`, `docs/reviews/` and `LICENSE` do not exist. `docs/decided-against.md` exists, so requirement C's link has a target.
  - README is 1,174 lines. The harness-docs requirement "README stays within its line budget" caps it at 1,185 (`.factory/store/openspec/specs/harness-docs/spec.md:417-422`), which leaves 11 lines.
  - README's first section is "What problem it solves" (`README.md:14`). "Filing a request from an issue tracker" is at `README.md:834`.
- The request says that since 2026-10-10 this repo has "merged 22 times into main" and "closed 14 factory tickets". `git log main --since=2026-10-10 --merges` counts 22 merge commits. A rough count of parent tickets in the store that are closed or archived and carry an October timestamp on or after 10-10 gives 15 (T-0040 to T-0054). That count is a heuristic, not close dates, so the two figures agree within it. I did not check the figure of "3 tickets built on the Nanobot port".
- No harness fix is involved, so there is no Nanobot-side commit to check.

Capabilities: harness-docs

Assumptions (inferences, not stated by the requester):
- This ticket writes `STATUS.md` once, before any review has happened. Because STATUS.md quotes only numbers from a review, the first version would say that no scorecard exists yet and that the first review is on 2026-11-02, rather than quote any numbers. The spec writer should confirm this wording with the operator.
- This ticket writes the template, not the first review. The first review (2026-11-02) is operator work done after the merge.
- The scorecard names in `docs/north-star.md` are the source that T-0056 (#117, the scorecard in `factory stats`) implements. They are written here as names only, with no computed values. T-0056 and T-0060 (#118, the benchmark) come after this ticket, as the request's Order line says.
- Rule B is written guidance that the operator enforces at the spec gate. No harness check or role prompt enforces it, matching "No role prompt changes" and "no harness or prompt change".
- The new north-star text keeps meeting the current-truth requirement "The north star names its target without the private product".
- The new files and the README changes follow README's "Maintaining this page" rules, including the "Where things live" table, a `docs/changelog.md` entry and no whitespace errors. If the new block does not fit in the 11 lines left, the spec raises the 1,185 budget, which the request allows.
- Suggested priority, a suggestion only: first in the queue. The operator already put #116 in row 1 of #96 and named it the base for #117 and #118.

Missing info: none blocking. One detail goes to the spec writer: what `STATUS.md` holds before the first review (see the first assumption).

STATUS: ACCEPT
CONFIDENCE: high. The operator wrote concrete requirements A to E, the out-of-scope items and the order, and every repo fact the request relies on checks out on `main`, apart from the Nanobot ticket count, which I did not verify.
ESCALATIONS: none
