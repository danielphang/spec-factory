## Critic review, round 2 (spec v2, T-0023)

What I checked. `main` is still at `67447b1`. Every cited symbol and line the changed text adds exists: `store.subtickets_of(root, parent)` (`factory/store.py` line 214, returns the records in id order, so step I4's "one line per sub-ticket, in id order" needs no sort); `compose`'s `planner` branch adds the rulings at lines 152-159, so "after the rulings" has a place; `run_start` calls `store.ensure_gitignore(root)` after its last refusal and after `meta.yaml` is written (`factory/cli.py` line 222), so step C2's "runs after every refusal" is right. Every line the new Tests-to-change paragraph cites holds what the spec says: `test_spec_store.py` 151 (second `init` writes `[]`), `test_instance.py` 42 (tree snapshot), 79 (`.factory/` listing), 147 and 157 (`written` on a second `init`), `test_harness_lock.py` 47 and 69 (tree and directory listings), `test_run_scratch.py` 163 and `test_tripwire.py` 230 (one run directory each). `git check-attr whitespace -- .factory/state/runs/run-0102-verifier/input.md` prints `.factory/state/runs/run-0102-verifier/input.md: whitespace: unspecified` today, as Operator step 1 says, and the file exists.

I ran six acceptance commands verbatim, under a throwaway `HOME`, with `TMPDIR` set to this run's scratch directory inside the repository, to test the writer's unverified claim that the scenarios no longer depend on where `TMPDIR` lies. Each printed the spec's stated "today" result: the re-plan scenario `exit=2 parked` and `in_input=0 listed=0`; init-refuses `exit=0 instance=written store=written names_state=0`; missing briefing `exit=1 input=none names_context=1`; relative paths `state=0 instance=0 repo=0`; whitespace `runs=2` and `other=2`; the suite scenario `23 failed, 192 passed in 136.67s (0:02:16)`, after which no `/tmp/t0023-suite.*` directory remained. `git status` of this repository was identical before and after, so the throwaway-store scenarios touched no live instance: `init_cmd` picks its instance from the git top level of the caller's directory (`factory/cli.py` line 829), and each scenario's `cd $T/tgt` is its own repository.

### Prior findings

- [BLOCKING] 6, Operator steps glosses: RESOLVED. The first paragraph now says what the runtime, an instance and `--accept-harness <commit>` are before any step uses them; step 2 glosses the Driver session.
- [SHOULD-FIX] 6/3, H1-H5 used for two things: RESOLVED. Items keep H1-H9; parts are A-G, I, J with no part H, and the seam table, Evidence, Root cause, Risk and every step reference agree.
- [SHOULD-FIX] 2, the suite scenario and `TMPDIR`: RESOLVED. The WHEN gives pytest `mktemp -d /tmp/t0023-suite.XXXXXX` and removes it; run verbatim today it prints the H8 baseline, not the spurious 27. The writer's reason for not taking the test fix (three of the four tests fail on the instance walk-up, not on git) matches `instance.find` (`factory/instance.py` lines 42-53, an unbounded walk-up). The remaining `TMPDIR` dependency the writer did not re-run is gone: see the six runs above.
- [SHOULD-FIX] 4, the planner does not know what merged: RESOLVED. Step I4 lists the existing sub-tickets in the planner's input, a Decision records it, and the re-plan scenario checks the list.
- [NIT] 6, Operator step 1 names a missing file: RESOLVED.
- [NIT] 6, Evidence H2 and H3 glosses: RESOLVED. The writer's correction on H4 is right: `.factory/answers/retro-trial-2026-10-04/inputs.md` line 1 reads "Retro inputs: spec-factory instance B store".

### Findings

No blocking issues.

[NIT] 6 — Evidence, bullet "H8, where the suite's temporary files go"
Problem: the bullet names four test functions, which an operator does not need and which the rubric keeps out of acceptance items; here it is Evidence, so it is allowed, and the names are useful to the implementer who must leave them alone.
Evidence: the bullet as written; the same four names appear under Out-of-scope observations in verification.md.
Suggested fix: none required; leave it.

### Not findings, noted so the writer does not change them
- The GIVEN fixture files go to `${TMPDIR:-/tmp}`, so a role with `TMPDIR` set to its scratch directory writes them there; only the suite scenario writes under `/tmp`, by the Decision that records it.
- The REGRESSION scenario "A plan that reuses an existing sub-ticket id" prints the same text today and after; the writer says why it still guards the change (the label must not silently become `T-0001.3`). Acceptable.

STATUS: APPROVE
CONFIDENCE: high — every prior finding is fixed in the text, every new cited line matches, and six acceptance commands, including the two the round-1 escalation turned on, reproduce the spec's "today" results from inside the repository's work tree.
ESCALATIONS:
- Round 1 asked a human whether a role may write under the system temp directory for the suite scenario. The writer chose yes and wrote it into the command and a Decision; no human ruling is in my input. Approving this spec at the gate is that ruling: the verifier will create and remove one `/tmp/t0023-suite.*` directory, outside its scratch directory.
