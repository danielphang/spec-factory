Type: chore

Title: Shrink the maintained documents: freeze the three `dev/` build documents as history, fix README's stale "not yet run" claims, describe each mechanism once in README, move history to the changelog, and update the `harness-docs` current truth to match

Summary:
The operator reads `README.md` and `docs/design.md` at every spec gate (the human review where a spec is approved), and both have grown. README explains several mechanisms two or three times, says some features have "not yet run" when they have, and keeps history that belongs in `docs/changelog.md`. Three finished working documents under `dev/` describe a design the code never had, yet every ticket must still keep `dev/build-harness.spec.md` in step with the design doc. The requester wants five things. (A) The `dev/` build documents frozen as history. (B) The stale claims corrected. (C) Each mechanism described in one README section, with one-line pointers everywhere else. (D) History moved to the changelog. (E) Duplicate glossary entries removed. Every cut must also come with a change to `harness-docs` (F). That capability is the current truth, meaning the approved scenarios the documents must keep passing, and many of its checks are greps against these documents. The same change rewrites the `harness-docs` scenarios that can only pass on the ticket that wrote them, so that they keep passing on later changes.

Evidence:
- Request: spec-factory issue #101 (https://github.com/danielphang/spec-factory/issues/101), row 2a of the de-bloat round #96. It was found by the 2026-10-11 sweep at `927bc53` and is filed as T-0048 in `dev/issues.md:104`.
- I checked these against the current `main` (`7231670`):
  - `wc -l`: `README.md` 1191 (the request says 1185), `docs/design.md` 923, `dev/build-harness.spec.md` 556, `dev/build-harness.plan.md` 298, `dev/P0-intake-skeleton.md` 118, and `harness-docs/spec.md` 450 (the request says 415).
  - `git diff --stat 927bc53 HEAD -- README.md docs/design.md` reports 17 insertions and 11 deletions. The README line numbers in the request are therefore off by a few lines. For example, the "Running on another agent host" heading is now at line 1072, not 1066, and "Headings are the contract" is at 1163, not 1157.
  - `dev/build-harness.spec.md`:
    - Its header names a `/tmp/.../spec-factory-v5.md` design doc and the branch `feat/lionbot-v3` (lines 1-5).
    - It mentions `bare repo` 15 times, `pre-receive` 9, `FACTORY_KEY` 13, `gate-run` 15 and `retro-input` 8 (counted with `grep -o`). None of those five strings appears in any `factory/*.py` file.
    - It has had 16 commits since 2026-10-04 (the request says 10 as of `927bc53`).
  - `.factory/context.md:34-35` asks every design-doc change to keep `dev/build-harness.spec.md` consistent. `.factory/**` is a protected path.
  - `harness-docs/spec.md` pins "last entry":
    - The requirement at line 25 says the changelog gains this change "as its last numbered entry".
    - The scenario at lines 27-29 checks that by taking the final changelog entry with `tail -1`.
    - Line 142 states the same requirement for another change.
  - `harness-docs/spec.md` diffs against the branch point: `git diff --check main...HEAD` appears at lines 21, 48, 72, 119 and 138, and `git diff --name-only main...HEAD` at 32 and 130.
  - `harness-docs/spec.md` mentions `dev/build-harness.spec.md` 37 times. No other capability's spec names any `dev/` document.
  - Stale claims:
    - Store logs: `.factory/store/log/2026-10.jsonl` has 15 `plan.skipped` events, and Nanobot's store has 5. The log also records `subtickets.superseded` for T-0031 on 2026-10-09.
    - README still says some of these have not run on a real ticket. Lines 158, 728, 822, 978, 992, 1000, 1016 and 1025 all say a feature has "not yet run" or "not yet fired" on a real ticket.
    - `docs/design.md:3` still reads `2026-09-30 · Daniel`.
- The request leaves some parts out of scope:
  - The prompt blocks in `docs/design.md` and its appendix, plus the notes that a prompt change is hand-copied. Those belong to #83 part C.
  - The `store migrate` runbook in README. That belongs to #83 part D.
  - `docs/north-star.md`, `decided-against.md`, `golden.md` and `principles.md`.
  - `dev/issues.md`, which stays the live issue index.
- The request suggests these acceptance checks:
  - `wc -l README.md` falls by at least 150.
  - Each part C mechanism is described in one section, with a one-line pointer everywhere else.
  - None of the part B stale claims remains.
  - Every `harness-docs` scenario passes on the change's head.
  - The changelog gains one entry recording the move.
- Suggested risk and split, from the request: medium risk. The planner splits the work into A+F, B+E, C and D.

Capabilities: harness-docs

Assumptions:
- (Inference) No other capability is touched. Only `harness-docs` greps `README.md`, `docs/design.md`, the changelog or the `dev/` documents (a grep across all 15 capability specs). The doc sections describing other mechanisms, such as `factory drive` (the driver command), the live-store fence and the merge gate, only change wording, so the spec writer needs only the index entries for those.
- (Inference) Because of the drift above, the spec writer re-finds every section and claim on the current `main` rather than relying on the request's line numbers.
- (Inference) The request offers two either-or choices that the spec can settle and the operator approves at the gate. Neither blocks triage:
  - Part A: a frozen-as-history header on the three `dev/` documents, or a move to `dev/archive/`.
  - Part B: relax README's rule that an item is listed as built only after it runs on a real ticket, or move the items that are tested but have not run.
- (Inference) The writer reads part B's "Still true and kept" items as constraints: the tripwire, empty output, protected-path refusal and effort. Each claim is checked against the store logs before it is removed.
- (Inference) The final step only moves the frozen documents' named strings out of the current truth, by removing the scenarios that grep them. The frozen files themselves are not edited to match the code.
- (Inference) Part F's rewritten "last entry" and branch-relative scenarios must still check what they were written to check. For example, a scenario can find the change's entry by its content instead of by its position. Weakening them would breach the anti-Goodharting rule.
- Suggested priority (a suggestion; priority is the operator's call): p2. It goes ahead of #104 (T-0049, the README diagram), which the index says comes after #101.

Question for human / Missing info / Reason: none. The intent is clear and the two open choices are listed under Assumptions for the spec gate. One thing to note: the change edits `.factory/context.md`, a protected path, so the spec's Risk section must declare it, as the request says.

STATUS: ACCEPT
CONFIDENCE: high. The request names its files, its limits and what is out of scope. I checked its evidence against the current `main` and found only small line drift.
ESCALATIONS: none
