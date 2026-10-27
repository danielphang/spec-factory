## Acceptance

- A plain session's transcript gives its operator messages, operator time, elapsed time and tokens → NEW. Today it prints `/Users/dphang/dev/spec-factory/.venv/bin/python: No module named factory.benchmark`, then `exit=1`.
- A factory arm's store events and runner session give one operator time → NEW. Today it prints the same `No module named factory.benchmark` line, then `exit=1`.
- The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing → NEW. Today it prints `none=1+msg missing=1+msg nolog=1+msg store=unchanged`: each call fails with exit 1 on the missing module, not 2 on a refusal.
- The suite passes and no existing test file is modified or deleted → REGRESSION.
- The benchmark page has its eight sections in order → NEW. Today it prints only `exit=2`, because the file does not exist.
- The benchmark page states its selection, blinding, setup, measures, review and spend rules → NEW. Today it prints `caveat=no selection=no blind=no arms=no measures=no review=no spend=no`.
- No relative link in the benchmark page is broken → NEW. Today it prints `docs/benchmark.md missing`.
- README names the benchmark page and puts its report in the cost row → NEW. Today it prints `where=0 depends=0 shared=0`.

README's line budget is checked by current truth's harness-docs scenario "README is at most 1,225 lines", which the gate's `factory truth check` replays on this change. It passes today, at 1,224 lines, and must pass after, at 1,225.

How I checked, on the dev checkout at `main` `9e8f4d3`:
- I ran each NEW WHEN above verbatim, under bash and zsh, through the briefing's wrapper, and saw the "Today" output given.
- I ran the three factory-stats WHENs, after the GIVEN block, in a copy of `main` with the prototype installed as `factory/benchmark.py`, under bash and zsh, through the briefing's wrapper. They printed the THEN lines exactly.
- I replayed this change's eight scenarios with `factory truth check` itself, from `main`'s `bin/factory`, with `--skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'` as the gate passes it. The store was a scratch store whose current truth held only these two delta parts. The checkout was a `git clone --shared` of `main` with one commit on top: the prototype as `factory/benchmark.py`, design part D's two README rows, and a stub `docs/benchmark.md` holding the eight headings, the quoted phrases and two links (a stub, so this checks the scenarios, not the page). It printed `8 scenarios: 7 passed, 0 failed, 1 skipped`, the skip being the suite scenario. From `~/dev/spec-factory` on `main` the same run printed `0 passed, 7 failed, 1 skipped`.
- I replayed current truth's harness-docs and factory-stats from the live store, as the gate would, in that clone and on `main`. Both printed `114 scenarios: 110 passed, 0 failed, 4 skipped`, and "README is at most 1,225 lines" passed at 1,225 lines in the clone. So the README edits break no existing check.
- I did not run the suite scenario: the gate runs the suite on every change, and the gate's replay skips this scenario because its WHEN holds the suite command.

## Responses

(Round 1 had no critic findings: the spec went to NEEDS-HUMAN on its open question, now answered by Answer 2.)
- Answer 2 → the open question moves to Decisions; design part A's formula is unchanged, as it already implemented option (a); design part C's "The measures" now names the three things the sittings rule misses, and the page scenario checks the phrase "first interaction".
- T-0059 merged since round 1 → README's base is 1,224 lines, so the change adds exactly one; the separate budget scenario is dropped in favour of current truth's own, which the gate replays; the README scenario checks only what this change adds; Evidence states how the gate's replay reads these scenarios.

## Critic rounds

round 1 · spec v2 · run-0603-critic · APPROVE

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

## Verifier results

37c867e6881221552f4b86efe47fcbb04fabd929 · T-0060.1 · VERIFIED · run-0606-verifier
