# Critic review: T-0060 spec v2 (round 2)

## What I checked

- Cited paths and lines, on the dev checkout at `main` `9e8f4d3`: `factory/cost.py` `_records` (:34), `_log_records` (:43), `_user_text` (:49), `transcript_usage` (:81), `tally()` (:98) with its `agent-*.meta.json` glob (:102) and `_when` (:113) are where the spec says. `factory/stats.py:46` is `DECISIONS = ("approval.recorded", "human.resolved")`. `docs/north-star.md:36` reads "The store records operator decisions, not operator time". `wc -l < README.md` prints `1224`. README has the `## Where things live`, `## Related work and history`, `### What depends on Claude Code` and `## Terms used on this page` headings, the `STATUS.md`, `docs/reviews/` row (:1140), the cost row (:113, "Token cost per role (`factory/cost.py`) | yes | reads the Workflow tool's transcript files") and the status header date (:13). `.factory/instance.yaml` has `factory truth check` as its last gate command and `implementer: opus`. `docs/writing.md`, `docs/reviews/TEMPLATE.md` and `docs/north-star.md` exist; `docs/benchmark.md` and `factory/benchmark.py` do not. The only README mentions under `tests/factory/` are `_fixtures.py:478` and `test_harness_lock.py:253`, `:274`, as stated.
- Acceptance commands, run as the spec gives them through the briefing's wrapper from `~/dev/spec-factory`: the README scenario printed `where=0 depends=0 shared=0`; after the GIVEN block, the plain-session WHEN printed `/Users/dphang/dev/spec-factory/.venv/bin/python: No module named factory.benchmark` then `exit=1`; the refusals WHEN printed `none=1+msg missing=1+msg nolog=1+msg store=unchanged`. All three match verification.md's "Today" lines.
- The fixture: `base.jsonl` has 11 parseable lines and 1 unparseable, `runner.jsonl` 4, the store log 4. I re-derived every exact THEN by hand from the fixture and the design's rules: 3 operator messages (10:00, 10:15 queued, 10:40 with no `promptSource`), sittings of 16 and 1 minutes (the 900 s gap stays in one sitting), elapsed 41 min = 0.68 h, context 1100 + 2050 = 3150, output 20 + 40 = 60. The 60 depends on `cost._usages` keeping the last usage per message id (`factory/cost.py:70-77`), which it does. The factory-arm figures (3 sittings: 1 + 1.5 + 1 = 3.5 min; elapsed 09:00:00 to 12:05:00 = 3.08 h; 510 + 620 = 1130; 5 + 7 = 12) also hold.
- Tests to change: no test enumerates `factory/` modules or reads README's tables (grep of `tests/factory/` for module globs, `listdir`, `README.md`). Harness-code's "only the entry point, the driver and the stats report import the CLI module" is respected by design A's "Do not import `factory.cli`".
- Rubric 5: the input lists no approved change not yet archived, so no scenario can collide on merge order. The T-0055 decisions (decisions stand in for hours until the store records time) are consistent with this change, which leaves the scorecard alone.
- Design C.4's factory-arm setup: exporting `FACTORY_STATE=$PWD/.factory/state` before `factory init` works because `.factory/state` is the template's default `state_dir` (`factory/instance.template.yaml:10`), so `instance.is_own_store` is true and init does not hit the T-0023 refusal at `factory/setup.py:155`.
- Not re-run: the writer's prototype run and the `factory truth check` replays (7 passed in the clone, 110 passed for current truth). Those claims rest on verification.md; I checked only that the scenarios' THENs are what the rules give.

## Findings

[SHOULD-FIX] 6 Evidence, second bullet; Operator steps, step 1
Problem: "Green" is a name this system made up and no human-facing section says what it is, yet step 1 asks the operator to strike answers Green gave.
Evidence: "Answer 1 (Green for the operator, 2026-10-26 ...)" and "Answers 1 and 2 were given by Green for the operator" are the only uses; `docs/writing.md` rule 2 asks that such a name be glossed at first use. I am not blocking on it: the decision log uses the same phrase as a standing convention (T-0055, T-0056, T-0057, T-0059 entries), "for the operator" names the role, and the operator can add the gloss as a gate amendment.
Suggested fix: at the first use, gloss it, for example "Green, the operator's own Claude session, answering on the operator's behalf".

[SHOULD-FIX] 4 design C.2, filter (4), against C.3
Problem: filter (4) has the operator fetch and run the PR's tests before the arms run, while C.3 says the operator does not open the PR or its tests until both arms have ended; the page does not say how to do the first without breaking the second.
Evidence: C.2 "(4) The PR's tests fail at the parent commit and pass at the merge commit, run with upstream's test command" and C.3 "The operator does not open the PR, its diff or its tests until both arms of the task have ended" are both in the spec as written. Running the check by hand shows the operator the test files' names and content before the task.
Suggested fix: state that filter (4) is run by one script over the candidate list that fetches both commits and prints only the PR number and pass/fail, and that the operator does not read the test files or the diff while choosing.

[NIT] 2 factory-stats, refusals scenario
Problem: "writes nothing" is checked only under `$F`, so a module that wrote a file into the working directory on refusal would still pass.
Evidence: the WHEN compares `find $F -type f` checksums before and after.
Suggested fix: none needed for the gate; the implementer's unit test for the refusals can assert the working directory is unchanged.

[NIT] 6 Decisions, first bullet
Problem: "the split triage proposed" uses triage, the factory's intake role, without a gloss.
Evidence: no earlier human-facing section names triage; README :40 glosses it as the role that "decides whether a request is a real ticket".
Suggested fix: "which is the split triage (the intake role) proposed".

[NIT] 6 design C.4, factory arm
Problem: the page should say why the exported store path is `.factory/state`, so an operator who changes it is not surprised by init's refusal.
Evidence: `factory/setup.py:155` refuses to create an instance while `FACTORY_STATE` names a store other than the instance's own; `.factory/state` is the template's default, so the step works as written.
Suggested fix: one clause: "`.factory/state` is the store init creates by default, so init treats it as the instance's own".

## Prior findings

Round 1 recorded no critic findings, so there is nothing to mark resolved.

STATUS: APPROVE
CONFIDENCE: high, every cited line and three acceptance commands checked on the checkout, and every exact THEN re-derived from the fixture against cost.py's dedup rule; the truth-check replays rest on the writer's report
ESCALATIONS: none
