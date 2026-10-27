Type: feature

Title: Benchmark the factory against one plain Claude Code session on about 10 upstream Nanobot fix PRs, each scored by that PR's own tests

Summary:
Every quality bar the factory has today is its own: the critic's rubric, `docs/writing.md`, the golden set and current truth (the store's record of what each capability must do). None of them shows whether using the factory beats working without it. The operator wants an outside bar with known answers: about 10 merged fix PRs from the public upstream project, HKUDS/nanobot, each of which fixes a stated issue and adds or changes tests. Each task is the issue's text, run against a throwaway checkout of upstream at the PR's parent commit. Two arms run it, and neither ever sees the PR's diff or tests. The factory arm runs in a throwaway store (a store that `FACTORY_STATE` points to, never a live one). The baseline arm is one plain Claude Code session, whose result the operator reviews the way they review a merge. After the run, the PR's own tests decide pass or fail. Beside the score, each arm records operator time, operator decisions, tokens and wall time. Operator time is derived from timestamps, with no hand count: the factory arm uses the throwaway store's gate and ruling events and its session transcripts, and the baseline arm uses the timestamps of the operator's messages in its session transcript. The method goes in a new `docs/benchmark.md`. It says how tasks are chosen, how the arms are kept blind, how a task is scored and how a result goes into a review, and it says that the timestamp measure counts interactions, not attention, so it undercounts reading and review time. The results go in a review, not in this repo's docs. The spend, about 10 factory intakes and builds plus 10 plain sessions, is approved at the spec gate.

Evidence:
- Request: issue #118 (https://github.com/danielphang/spec-factory/issues/118), operator, 2026-10-19. It says "Uses #117's measures where they exist". #117 is the scorecard in `factory stats`, built as T-0056 and merged (`main` at db28eb1: "#117 (T-0056) and #105 (T-0057) merged and closed").
- Answer 1 (2026-10-26) chose option 2 of my earlier question: operator time comes from timestamps. It is standing for this benchmark only. Whether the store ever records operator time is left to a later ticket.
- The benchmark is already named as an outside comparison. `docs/north-star.md:56-57` reads: "The upstream benchmark: merged fix pull requests from the public upstream Nanobot project, each run by the factory and by a plain session, and scored by that pull request's own tests." `STATUS.md:42` lists it third in the queue.
- No duplicate exists. Re-checked on this run: the only ticket in `.factory/store/tickets/` that mentions "benchmark" is this one, T-0060, and `docs/benchmark.md` does not exist yet.
- There are enough candidate tasks. On my earlier run I listed the last 400 merged upstream PRs with "fix" in the title, back to 2026-07-14, using `gh pr list --repo HKUDS/nanobot --state merged --search "fix in:title" --limit 400`. 379 touch a file with "test" in its path. 39 of those also carry a closing-issue link, for example #6071 → issue #6070 and #6232 → issue #6231. I did not re-run this listing today.
- A throwaway store is supported today. `factory/instance.py:14` reads: "FACTORY_STATE overrides it".
- The answer fits the north star's rule. `docs/north-star.md:39-41` reads: "`factory stats` computes them from the store, and nobody types them. Until it computes a number, a review writes 'not yet computed' rather than count it by hand." `docs/changelog.md` entry 77 lists "recording operator time by hand, which would mean typing a number" as rejected.

Capabilities: harness-docs, factory-stats, store-setup

Assumptions:
- Answer 1 was given by Green on the operator's behalf, and the operator may strike it at the gate. I have treated it as settled for this ticket.
- This is my inference: the ticket's change is `docs/benchmark.md`, plus the doc updates the repo's conventions require. Those are a row in README's "Where things live" and a `docs/changelog.md` entry. Running the 10 tasks needs the operator at both arms' gates, so the runs would be operator steps after the merge, not implementer work. The spec writer should state this split for the gate to confirm.
- This is my inference: "derived from timestamps, with no hand count" means something computes the figure, not that the operator reads timestamps and adds them up. The request does not say whether that is a new script or command in this ticket, or an existing one such as `factory stats` reading the throwaway store. The spec writer should name which, and keep any new code inside what the request asks for.
- This is my inference: "results go in the review, not in this repo's docs" means a review file under `docs/reviews/`, written from `docs/reviews/TEMPLATE.md`.
- This is my inference: the factory arm needs a factory instance on each throwaway upstream checkout, set up with `factory init`. That is why store-setup is named. I have not checked whether `init` works unchanged on a bare upstream checkout.
- Keeping the arms blind is in scope as the request states it. I see two ways the answer could leak, which the method will have to address. A full clone of upstream contains every later commit, including the PR's own. Both arms' sessions can also reach GitHub and the local Nanobot fork, whose history holds upstream's commits. I name these as risks, not as added requirements.
- Choosing about 10 from the 39 linked candidates is part of the method. I have not checked whether each candidate's tests fail at the parent commit and pass after the fix.
- Suggested priority, which is the operator's call: p1, matching its third place in the queue on `STATUS.md`.

Reason: The intent and the deliverable are clear, and the one product decision, how to measure operator time, is answered.

STATUS: ACCEPT
CONFIDENCE: medium. The request, the answer and the evidence are clear and re-checked. Two splits are my inference: that the runs are operator steps after the merge, and what computes the timestamp figure.
ESCALATIONS: none
