## Problem

Five of the factory's seven role prompts lack the reading rules that cut the spec writer's token use by about 37% at the same quality. The five are triage, planner, implementer, code reviewer and verifier. The operator pays for those tokens on every ticket. The implementer and the verifier pay the most, because they run test suites and other long commands. The factory runs each step of a ticket as a separate model agent, a "role": triage sorts a request, the spec writer drafts a spec, the critic checks it, the planner splits it into sub-tickets, the implementer writes the code, the code reviewer reads the diff and the verifier re-runs the checks. Each role is steered by its own written prompt.

An agent works in turns. A turn is one call to the model, and every call re-sends everything the agent has read so far in the run. A file read whole, or a test run printed in full, is paid for again on every later turn. Issue #73 gave the spec writer and the critic a short paragraph of reading rules: put independent reads and commands in one turn, read only the line range a search found, and send long command output to a file in the run's scratch directory (a per-run folder for temporary files), then search or tail that file. In the operator's replay of past runs, the spec writer's tokens fell by about 37% with the same spec quality. The same replay found no saving for the critic, whose prompt #73 had also given a cap on how much it could check. That cap made it check less, and it was removed. The reading rules stayed.

This change adds the same paragraph to the five other prompts and to nothing else.

Each prompt exists in three copies that must agree: a block in the design document, a verbatim copy of that block under `docs/prompts/`, and the copy the harness actually sends (`factory/prompts/`), which differs from the documented one only where the harness fills in values. All three copies change. The operator's replay of past build runs then decides whether the running harness moves to the new prompts.

## Evidence

- The paragraph exists today only in the spec writer and critic prompts. Critic form, `factory/prompts/critic.md` lines 50-55 (and `docs/prompts/03-spec-critic.md` lines 50-55, `docs/design.md` lines 485-490):
  "Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full."
  The spec writer's form (`factory/prompts/spec_writer.md` lines 59-65, `docs/design.md` lines 378-384) adds "such as a suite run or a scenario's output" and "Write the spec in as few writes as you can, ideally one."
- `grep -i 'turn economy'` over `factory/prompts/`, `docs/prompts/` and `docs/design.md` matches only those two prompts. The five target prompts have none. Run against this checkout, scenario "The five role prompts carry the critic's reading paragraph in every copy" prints `doc=0 run=0` for all five roles.
- The 37% result is changelog entry 59 (`docs/changelog.md` line 63, the #74 entry: "found that #73's spec writer rules cut its tokens by about 37% at the same quality"). The same entry records the other half: #73's critic rules "saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less". It missed one Nanobot risk and one declaration bug that the earlier prompt had caught. #73 had given the critic more than the reading paragraph: a cap of two paths and one command per claim, and a ban on clones, worktrees and prototypes. Entry 59 (#74, T-0035) removed the cap and the ban and kept "the three reading rules". So the one measured case where #73's rules did not pay came bundled with the cap, and the reading rules have a measured saving only on the spec writer. The request cites entry 58, which records the #73 change itself and the 309M of 866M spec-writer token share. I could not find a source in this repo for the request's 18% (implementer) and 13% (verifier) token shares. They motivate the change but no criterion depends on them.
- The three copies agree today: for triage, planner, implementer, code reviewer and verifier, each design block is byte-identical to its `docs/prompts/` file. The run copies differ from the documented ones only by harness fills: `{gate commands}` and `{force-push allowed}` in the implementer, `{gate commands}` in the verifier, `{2}` in the reviewer, and an instance-added "Acceptance items describe behaviour" block at the end of triage's RULES.
- Every role run, the five included, receives a "Scratch directory" section in its input (`factory/compose.py` lines 186-188), so "your scratch directory" means something to each of them.
- The code reviewer is told "Do not run the test suite or the gate commands" (`factory/prompts/reviewer.md` lines 7-8). The spec writer's example "such as a suite run" would sit badly next to that rule.
- Prototype: I applied the change below in a scratch clone and ran every scenario on base (`b002c95`) and on the prototype. On base: `doc=0 run=0` and `economy=0` for all five roles, changelog `63 CONTIGUOUS` with `terms=2 footer=1`, and scope `extra=0 deleted=0 others=0`. On the prototype every THEN line below printed as written. A mutated prototype (one reworded existing planner line, two words appended to the verifier paragraph, one new file under `agents/`) printed `extra=2 deleted=1 others=1`.
- Harness suite on the prototype: 404 passed, 4 failed. The same 4 tests fail on base in the same clone (`tests/factory/test_instance.py`: `test_init_refused_outside_a_git_work_tree`, `test_command_outside_any_instance_refused_and_writes_nothing`, `test_no_fallback_even_with_a_store_named`, `test_paths_outside_any_instance`; 18 passed, 4 failed on base). The cause is the clone's location inside the store's git checkout, where "outside any git work tree" cannot hold. The change itself does not cause them.
- Tests that read these prompts check that the design block equals its `docs/prompts/` copy (`tests/factory/test_coding_standard.py`, `test_writing_standard.py`, `test_decision_log.py`). One also checks triage's Capabilities line and the 72-character width of its capability lines (`tests/factory/test_capability_index.py` lines 249-259). An added paragraph breaks none of them. The suite run above confirms it.
- The implementer/verifier run-prompt check reuses the fixture in current truth `openspec/specs/role-escalations/spec.md` (scenario "Implementer and verifier run prompts carry the declared-path rule").
- Neither `dev/build-harness.spec.md` nor `README.md` describes the reading rules (`grep -c -i -E 'turn economy|re-sends'` returns 0 for each).

## Root cause

The #73 change (T-0034) scoped the rules to the spec writer and critic, which were the two roles it measured. Its decision log records "No shared preamble line ... which would reach every role, including the implementer and verifier, which the request does not cover." No later ticket added them to the other roles.

## Out of scope

- The spec writer and critic prompts, the shared preamble, the retro and doc-reviewer prompts, and `agents/`.
- Any existing line of the five prompts: no rubric, routing, round limit, required section or output format changes.
- The enforcing hook that refuses whole-file reads and uncapped searches (#76 part B, with #65).
- The replay procedure itself (#80).
- `docs/principles.md` principle 13's "Implemented by" line, which still credits reading rules to #73 only. The operator keeps those status lines up to date (commit `4a34e40`, "statuses updated for #57, #75, #78").
- `README.md` and `dev/build-harness.spec.md`. This change adds no command, state, stop or path, and neither document describes the reading rules.

## Open questions

none

## Decisions

- All five roles get the critic's form of the paragraph, word for word, as one bullet starting `- Turn economy: `. It carries the three reading rules and the sentence saying why they matter. The spec writer's "as few writes as you can" stays out, as the request says. The writer's "such as a suite run" example also stays out, because the code reviewer must not run the suite. With one text, one check covers all five prompts.
- The paragraph goes into each role's own prompt, not into the shared preamble. A preamble line would also reach the spec writer and critic, which already carry the rules, and T-0034 rejected a preamble line for the same reason. The request names the five prompts.
- New lines only: no existing line of any prompt changes. Placement: in the implementer and verifier, a RULES bullet directly before the declared-path bullet, so that bullet stays last under RULES where T-0029 put it. In the code reviewer, the last bullet of WHAT YOU RUN, which is about the commands it runs. In the planner and triage, the last RULES bullet. In triage's run copy, that is before the instance-added "Acceptance items" block.
- Acceptance checks the text each role receives: all three prompt copies and the composed run prompt. The request's own acceptance, the operator replaying past implementer and verifier runs with old and new prompts, is an Operator step. It needs live model runs and a human judgement of verdict quality (as in T-0034 and T-0029).
- `docs/changelog.md` gains entry 64 after entry 63 and before the closing "Declined:" line. The entry cites the #74 replay result as entry 59.

## Risk

Every future run of the five roles reads this paragraph once the runtime moves. The behavioural risk is a role that reads too little. For example, a verifier might tail a suite log and miss a failure printed earlier. The paragraph does not lift the verifier's "Record the actual output" or the implementer's acceptance-result reporting. A role that greps a log still reports what it found. There is a precedent: the #74 replay (changelog entry 59) found that #73's critic rules saved no tokens and made the critic check less. #74 acted on it by removing the cap and the build ban and keeping the reading sentences, but the two were never tested apart. The operator's replay is the check on this risk. A merge into `main` does not change the running harness, so nothing reaches live runs until the operator moves the runtime.

Protected paths: `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `factory/prompts/reviewer.md`, `factory/prompts/planner.md`, `factory/prompts/triage.md`, `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md`, `docs/prompts/06-code-reviewer.md`, `docs/prompts/04-planner.md`, `docs/prompts/01-triage.md`

## Operator steps

1. After merge and before moving the runtime, replay two or three past build runs of the implementer and verifier with the old and the new prompts, on the same inputs and bases. Compare agent calls, tokens and verdict quality. (#80 tracks the replay procedure.)
2. Only if the replay holds quality, move the runtime checkout to the new harness revision and accept it (`--accept-harness`). If it does not, report the result on #76 and leave the runtime where it is.

