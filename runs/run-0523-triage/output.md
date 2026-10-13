Type: chore

Title: Add `docs/standards.md`, the operator's writing and design standards in one self-contained file, point to it from README, and stop `docs/north-star.md` naming the private port (spec-factory #110)

Summary:
The operator's standards for writing specs, design pages, reports and records are split today across `docs/writing.md`, the spec-writer prompt, a target repo's `AGENTS.md`, and corrections that exist only in session memory. The operator wants them collected into one new file, `docs/standards.md`, with exactly the appendix text. Only its title line may change. The file must make sense when copied out of the repo. The change must leave role behaviour alone: no edit to `docs/writing.md`, `docs/prompts/`, any role prompt, or `factory/**`. Two smaller changes go in the same ticket. A reader of `docs/` must find the new file from README's "Where things live" table or a similar place. `docs/north-star.md:21` must stop naming the private port's product. A changelog entry records the change.

Evidence:
- `docs/standards.md` does not exist (`ls docs/` lists changelog, coding, decided-against, design, golden, north-star, principles, prompts, writing).
- Every role is pointed at `docs/writing.md` through the `{writing standard}` placeholder, filled in `factory/instance.py:174-176` (`fill_standards`). That is why the request adds a new file instead of editing this one: an edit would be a prompt change.
- `docs/north-star.md:21` reads: "The factory serves its own development (spec-factory) and its targets (today, the Lionbot v3.5 port)." This repo is public, so naming the private port's product there is the privacy problem the request describes.
- README is 1,106 lines (`wc -l README.md`). The harness-docs requirement "README stays within its line budget" caps it at 1,110, so 4 lines are free at this commit. The "Where things live" table starts at `README.md:1015` and already has a row for `docs/writing.md`.
- Requested order: after T-0052 (#108, status `planned`) and #109.

Capabilities: harness-docs

Assumptions:
- (Inference) "Exactly the text in the appendix" means the appendix block from "# Writing and design standards" to the end of section 7. The "Capability index" heading below it was added by the harness and is not part of the file.
- (Inference) The appendix's section 2 is described as "unchanged from `docs/writing.md`", but its table wording differs slightly from that file's rule headings. Two examples: rule 4 reads "with a caption stating its one claim" where `docs/writing.md:51` reads "with a caption that states its one claim"; rule 9 drops "and" compared with `docs/writing.md:94`. The operator's rule that the text is exact wins, so the spec should keep the appendix wording, and these differences are not defects to fix.
- (Inference) A one-line README row fits within the budget today (1,106 + 1 ≤ 1,110). T-0052, #109 or T-0049 may use the free lines first. The request already covers that case: the spec either replaces a line or asks the operator at the gate to raise the budget.
- (Inference) The north-star rewording uses the operator's example, "its targets (today, a port of the Nanobot chat bot)". `docs/north-star.md` is the operator's document (README's table says changes to it are the operator's decision), and this request carries that decision.
- (Suggestion, not a priority call) p2: documentation only, with no change to role behaviour.

Missing info: none blocking. #109 is not in the `dev/issues.md` index (`grep "issues/109)"` matches nothing), so the triage run could not confirm what it is or whether it has merged. The planner or operator should check it before scheduling, because the request orders this ticket after it.

STATUS: ACCEPT
CONFIDENCE: high. The request gives the exact text, files and limits; no duplicate exists (T-0053 is this request; T-0013/#23 created `docs/writing.md` and is closed); and every cited path and line was checked.
ESCALATIONS: none
