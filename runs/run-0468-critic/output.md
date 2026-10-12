## Critic review: T-0046 spec v2 (round 2)

Scope of this round: whether the three round-1 findings are resolved, and the text the v1→v2 diff changed. Unchanged text was reviewed in round 1 and is not re-reviewed.

What I checked, on `~/dev/spec-factory` at `6ac73f1` (`HEAD` = `main`; `git log 6ac73f1..main` is empty and `git diff --stat 2b9baf5 main -- factory/` prints nothing, so the spec's base still describes the code):

- The two revised NEW WHENs, run as written from the repo root, print the "today" values the spec states: the integration-tip check prints `4 0`; the park-format check prints `18 3 0`. `grep -c 'harness-bug:' factory/drive.py` still prints `24`, matching the Evidence paragraph that explains the 18-of-24.
- `drive.py:664` is `def _fail(result: dict) -> None:`, as the new Decision says; nothing in `factory/drive.py` or `tests/factory/` defines or names `_harness_bug` or `_failed`, so the renamed helper collides with nothing and no test pins either name (the three greps that match "harness_bug" are test-function names about park reasons, not the helper).
- The corrected line ranges hold: `cli.py:818-821` is the ready-implementers release (status set, history append, save, `ticket.transition` log with by `ready-implementers`); `cli.py:1000-1003` is the dependant release in `merge` with by `merge`.
- Read as the gate operator: the first Decision now says "record file" and "scratch clean-up" before it names `meta.yaml` and `clear_scratch`, and glosses both in the same sentence. Problem bullet 7 glosses the dispatcher, a store command and the store. Evidence's new second paragraph defines NEW and REGRESSION checks before the table uses them. The second Decision now says what `factory log tail`, the cost report, the stats report and `test_cost_once.py` are. No new unglossed system term was introduced by the changed text.
- Open tickets: unchanged from round 1. T-0045 edits `tests/` only; this spec edits `factory/` only; the suite scenario's `main...HEAD` diff is merge-base relative and holds in either merge order.

### Findings

No blocking issues.

[NIT] 6 — Problem, bullet 2
Problem: "the store's event log" names the store one bullet before bullet 7 glosses it ("the directory of tickets, runs and logs").
Evidence: Problem bullets 2 and 7. Not a first paragraph, and "store" is near enough to a general term that a technical reader does not stall; recorded so the writer can move the gloss if touching the text anyway.
Suggested fix: Optionally move "the store, the directory of tickets, runs and logs" to its first mention in bullet 2, or leave as is.

### Prior findings (round 1)

- [BLOCKING] 6 — Decisions, first paragraph: unglossed `meta.yaml` and `clear_scratch` → RESOLVED. Both are glossed at first mention in Decisions and again in Evidence.
- [SHOULD-FIX] 6 — Problem (bullet 7), Evidence: "dispatcher", "store command", NEW/REGRESSION → RESOLVED. All three glossed where first used.
- [NIT] 2 — integration-tip and park-format checks pin "at most one" → RESOLVED. Each WHEN now also counts the helper definition; THENs `1 1` and `1 1 2`; today's values `4 0` and `18 3 0` confirmed by running them.

### Out-of-scope observations
- none new. The round-1 observation (`999-1003` → `1000-1003`) is fixed, and the writer's extra correction (`817-821` → `818-821`) is right.

STATUS: APPROVE
CONFIDENCE: high — all three round-1 findings verified fixed against the file and by running the two changed checks; the changed text introduces no new behaviour and no unglossed term in a first paragraph; `factory/` is unchanged since the spec's base.
ESCALATIONS: none
