Sub-ticket: T-0030.1 (ST-1 / A registered agent definition for every role, a file-tool fence on the reviewer and verifier, and `run start --inline`). Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md

What changed: nothing. The branch `factory/T-0030.1` is still at its base, `d226a4d03ca94bab45bd4221972285a4d16ee0bb`, with a clean tree. No commits were made and no PR is ready. This session's permission system blocked the run before step 2 of the implementer process (see ESCALATIONS).

What I did before the block (read only):
- Read the role prompt, the input, the coding standard (`~/dev/spec-factory-harness/docs/coding.md`), and every file in the worktree's `agents/` directory. It holds six files and none for the implementer, reviewer or verifier, which matches the spec.
- Located the code part A changes:
  - `run_start` is at `factory/cli.py:198`, and the `run start` parser at `factory/cli.py:1441`. It has `--model` and no `--inline`.
  - Each workflow sends `run start` from one line: `factory/workflows/intake.js:88` and `factory/workflows/build.js:79`.
  - The `inlineRoles` comments are at `intake.js:17` and `intake.js:29-31`, and at `build.js:10`. The one at `intake.js:31` says "Model per role is unchanged; tool fences are not."

Acceptance results: none run. Every NEW and REGRESSION command needs one of these:
- the spec's GIVEN fixture files (`t0030-wf.mjs`, `t0030-throw.mjs`, `t0030-e2e.mjs`, `t0030-fence.py` and the two JSON files);
- the existing test suite. Its files could not be listed.

The permission system blocked writing those fixtures. The gate commands were not run either.

Tests added/changed: none.

Known gaps and uncertainties:
- All of part A (A1 to A5) is still to do. No `factory:` markers were added.
- I read the GIVEN block in full in the input (spec section "Every agent type the workflows ask for has a definition"). It only writes six fixture files under `${TMPDIR:-/tmp}`. The scripts it writes call the workflow scripts with stub agents, and run `bin/factory` against scratch stores and scratch target repos. I found nothing in it that writes outside a temporary directory, but I could not run it to confirm.

Out-of-scope observations: none.

STATUS: BLOCKED
CONFIDENCE: high, because nothing was changed and the block happened three times, each refusal quoted below.
ESCALATIONS:
- This session's permission system (Claude Code's auto-mode classifier) refused three commands in a row, each with the reason "Code from External":
  1. Running the spec's GIVEN block, extracted from `input.md` into this run's scratch directory, under the throwaway-HOME wrapper with `TMPDIR` set to the scratch directory.
  2. Saving that block to the scratch directory and printing it, with no execution.
  3. A read-only `ls tests/factory`, `grep` for workflow tests, and `sed -n 70,100p tests/factory/test_instance.py` in the worktree.
  The refusal says the outcome must not be pursued through another tool, so I stopped and changed nothing. Part A cannot be built and checked as the role requires: tests first, then the acceptance commands, then the gate suite. To unblock, the operator either adds a permission rule that lets this run read the worktree and run the spec's fixtures and the gate suite, or re-dispatches T-0030.1 from a session where the classifier allows them. The ticket can go back to the implementer unchanged: the base, branch and sub-ticket are all still valid.
