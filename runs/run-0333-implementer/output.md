Sub-ticket: T-0035.1 (parent T-0035, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0035/v2.md`). Branch `factory/T-0035.1`, head `9a87c3e`, base `49ea4c7`.

## What changed

This change takes two of issue #73's limits back out of the critic. The critic is the agent that reviews a spec against a rubric before a human approves it. The two limits are the per-claim cap (at most two file paths and one command to settle any one claim) and the no-build rule (no clone, worktree or prototype). The operator's replay of three past intakes found that these limits saved no tokens and caused the critic to miss real defects. The critic keeps its minimum spot-check, its no-test-suite rule and its reading rules. The spec writer prompt does not change.

- **A. Critic PROCESS, all three copies.** In `docs/design.md` (the "## 3. Spec critic" block), `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md`, I replaced the seven lines from `Spot-check at least 2 cited paths ...` through `what you could not check.` with the spec's eight lines, word for word. The `Turn economy:` paragraph after them did not change. The run copy's existing `round 2` / `round {2}` difference also stayed, as the s1 output `fill=unchanged` shows. I applied the same replacement to all three files with one script (`scratch/edit_a.py`), and the script asserted that each file held the old text exactly once.
- **B. `docs/principles.md` principle 2.** "which runs no test suite and builds nothing (#73, ..." is now "which runs no test suite (#73, kept by #74, ...". The status line did not change.
- **C. `docs/principles.md` Spiking section.** I replaced its paragraph, which ran to the end of the file, with the spec's text word for word.
- **D. `docs/changelog.md`.** Entry 59 now follows entry 58, word for word from the spec. The `Declined:` line still comes after it.

Size: `git diff --stat main...HEAD` prints `5 files changed, 31 insertions(+), 20 deletions(-)`. This matches the size the spec gives for its prototype.

## Acceptance results

I ran every command from the worktree with bash, under a throwaway HOME. Each scenario's WHEN text was copied out of the input file with sed.

| Scenario | Kind | Before (base `49ea4c7`) | After (`9a87c3e`) |
|---|---|---|---|
| Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules | NEW | `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged` / `critic copy=SAME doc=7/8 run=7/8 gone=6 fill=unchanged` | `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged` / `critic copy=SAME doc=8/8 run=8/8 gone=0 fill=unchanged` |
| A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban | NEW | `spec_writer batch=1 writes=1` / `critic batch=1 suite=1 scratch=0 cap=1 build=1` | `spec_writer batch=1 writes=1` / `critic batch=1 suite=1 scratch=1 cap=0 build=0` |
| The writer prompt is as #73 left it, and only the critic's PROCESS changes | REGRESSION | `sections_changed=0 writer=0 others=0` | `sections_changed=0 writer=0 others=0` |
| Principle 2 names the critic's no-suite rule and no longer its build ban | NEW | `CONTIGUOUS` / `entries73=1 implemented=0 builds=1 status=1` | `CONTIGUOUS` / `entries73=1 implemented=1 builds=0 status=1` |
| The changelog records the revert as its last entry | NEW | `CONTIGUOUS` / `1` | `CONTIGUOUS` / `7` |
| The Spiking section allows a small scratch check and records the replay | NEW | `bound=1 nobuild=1 scratch=0 whole=0 replay=0` | `bound=0 nobuild=0 scratch=1 whole=1 replay=1` |
| The critic revert adds no whitespace errors | REGRESSION | `exit=0` | `exit=0` |

What the results mean:

- Before the change, every NEW command failed exactly as `verification.md` says it would.
- After the change, every command prints its THEN line exactly.
- In the first scenario, `copy=SAME` means each design block is byte-identical to its `docs/prompts/` copy. `gone=0` means none of the removed phrases is left in either the documented copy or the run copy.
- In the second scenario, `run start` is the harness command that writes a run's prompt, and the critic prompt it writes now has the scratch allowance and neither removed rule.

Gate commands, run from the worktree exactly as written:
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `364 passed in 225.62s (0:03:45)` and exited 0.

I checked that the removed phrases are gone everywhere except the changelog. `git grep -nE "build nothing|Ground any one claim|no clone, worktree|two paths, one command|at most 2 paths" -- . ':!docs/changelog.md'` found no match (exit 1). This confirms the spec's claim that `README.md` and `dev/build-harness.spec.md` do not name the removed rules.

## Tests added/changed

None.
- The spec lists no tests to change, and I changed no existing test file.
- I added no new test file. The acceptance scenarios already check the changed behaviour, which is prompt and document text. The two existing tests that compare each design block with its `docs/prompts/` copy pass, inside the 364 above.

## Known gaps and uncertainties

- `factory:` markers added: none. This change touches no code.
- I did not re-run the operator's critic replay on #51 and #57. The spec makes that an optional operator step after merge, not an acceptance check, so whether the reverted critic finds those two defects again is unverified.
- The live runtime (the pinned checkout of the harness that actually runs tickets) is unchanged until the operator moves it. Until then, live critic runs use the runtime's own prompt. That prompt predates #73.

## Out-of-scope observations

- The worktree has no `AGENTS.md`. Step 1 of my process says to read it, so I worked from the briefing in the run input instead.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The change is a word-for-word text replacement from the spec. All seven acceptance commands print their THEN lines, both gates pass, and I ran each command myself on head `9a87c3e`.
ESCALATIONS: none. The change touches two protected paths, `factory/prompts/critic.md` (harness) and `docs/prompts/03-spec-critic.md` (generated; re-copied from the design block). The spec's Risk section declares both.
