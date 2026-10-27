Type: feature

Title: Benchmark the factory against one plain Claude Code session on about 10 upstream Nanobot fix PRs, each scored by that PR's own tests

Summary:
Every quality bar the factory has today is its own: the critic's rubric, `docs/writing.md`, the golden set and current truth (the store's record of what each capability must do). None of them shows whether using the factory beats working without it. The operator wants an outside bar with known answers. The bar is about 10 merged fix PRs from the public upstream project, HKUDS/nanobot. Each PR fixes a stated issue and adds or changes tests. Each task is given as the issue's text, against a throwaway checkout of upstream at the PR's parent commit. Two arms run it, and neither ever sees the PR's diff or tests. The factory arm runs in a throwaway store (a store pointed to by `FACTORY_STATE`, never a live one). The baseline arm is one plain Claude Code session, whose result the operator reviews the way they review a merge. After the run, the PR's own tests decide pass or fail. Beside the score, each arm records operator time, operator decisions, tokens and wall time. The method goes in a new `docs/benchmark.md`, which says how tasks are chosen, how the arms are kept blind, how a task is scored and how a result goes into a review. The results go in a review, not in this repo's docs. The spend, about 10 factory intakes and builds plus 10 plain sessions, is approved at the spec gate.

Evidence:
- Request: issue #118 (https://github.com/danielphang/spec-factory/issues/118), operator, 2026-10-19. It says "Uses #117's measures where they exist". #117 is the scorecard in `factory stats`, built as T-0056.
- The benchmark is already named as an outside comparison. `docs/north-star.md:56` reads: "The upstream benchmark: merged fix pull requests from the public upstream Nanobot project, each run by the factory and by a plain session, and scored by that pull request's own tests." `STATUS.md:42` lists it third in the queue.
- No duplicate exists. The only ticket for #118 is this one, T-0060 (`dev/issues.md:121`). T-0055's spec lists the benchmark as out of scope and points to T-0060. No other open or closed ticket in `.factory/store/tickets/` has "benchmark" in it.
- There are enough candidate tasks. I listed the last 400 merged upstream PRs with "fix" in the title, back to 2026-07-14, using `gh pr list --repo HKUDS/nanobot --state merged --search "fix in:title" --limit 400`. 379 touch a file with "test" in its path. 39 of those also carry a closing-issue link, for example #6071 → issue #6070 and #6232 → issue #6231. That is enough to choose about 10.
- A throwaway store is supported today. `factory/instance.py:14` reads: "FACTORY_STATE overrides it". `README.md:616` describes a throwaway store as "`FACTORY_STATE` pointing elsewhere, as every test does".
- Operator time is not in the store. `docs/north-star.md:36-37` reads: "The store records operator decisions, not operator time. Until it records time, the scorecard counts operator decisions and interventions per change in place of hours of operator attention." Lines 40-41 read: "Until it computes a number, a review writes 'not yet computed' rather than count it by hand." The baseline review of 2026-10-19 is the one stated exception.

Capabilities: harness-docs, factory-stats, store-setup

Assumptions:
- This is my inference: the ticket's code change is `docs/benchmark.md`, plus the doc updates the repo's conventions require. Those are a row in README's "Where things live" and a `docs/changelog.md` entry. Running the 10 tasks needs the operator at both arms' gates. So the runs would be operator steps after the merge, and an implementer would not do them. The spec writer should confirm this split at the gate.
- This is my inference: "results go in the review, not in this repo's docs" means a review file under `docs/reviews/`, written from `docs/reviews/TEMPLATE.md`. It does not mean `docs/benchmark.md` or `docs/design.md`.
- This is my inference: the factory arm needs a factory instance on each throwaway upstream checkout, set up with `factory init`. That is why store-setup is named. I have not checked whether `init` works unchanged on a bare upstream checkout.
- Keeping the arms blind is in scope as the request states it. I noticed two leak paths the method will have to address. First, a full clone of upstream contains every later commit, including the PR's own. Second, both arms' sessions can reach GitHub and the local Nanobot fork, whose history holds upstream's commits. I am naming these as risks. I am not adding them as requirements.
- Choosing 39 linked candidates down to about 10 is part of the method (requirement B). I have not checked whether each candidate's tests fail at the parent commit and pass after the fix.
- Suggested priority, which is the operator's call: p1, matching its third place in the queue on `STATUS.md`.

Question for human:
How should each arm's operator time be measured? The request asks for operator time beside the score. The store does not record operator time. `docs/north-star.md` also says a review writes "not yet computed" rather than count a number by hand. The baseline arm has no store at all, so even its operator decisions would have to be counted from somewhere else. The spec writer cannot settle this without overruling the north star.
1. The operator logs it by hand. For each task and arm, the operator writes down the start and end of each stretch of attention in a benchmark log. `docs/benchmark.md` records this as a second stated exception to the "not by hand" rule, alongside the baseline review. This is the most accurate option. It costs the operator a little time on every task.
2. It is derived from timestamps, with no hand count. The factory arm uses the throwaway store's gate and ruling events plus its session transcripts. The baseline arm uses the timestamps of the operator's messages in the session transcript. This keeps the "not by hand" rule. It measures interactions rather than attention, so it can undercount reading and review time.
3. The benchmark reports operator time as "not yet computed" in both arms. The arms are compared on decisions and interventions only, as the scorecard does today, until the store records time. This changes the request as written, which names operator time.
Is the answer a standing decision, so that later tickets measuring operator time follow it too, for example a future store record of operator time?

STATUS: NEEDS-HUMAN
CONFIDENCE: medium. The intent, the deliverable and the task supply are clear and checked. How to measure operator time is a real conflict with a written rule. Whether the runs themselves belong to this ticket is my inference.
ESCALATIONS: none
