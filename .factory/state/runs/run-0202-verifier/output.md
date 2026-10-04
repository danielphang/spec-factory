Commit: fa09a10f700a44ab7ce5881bf3daf5615ecbbb57 (branch `factory/T-0023.1`, base 1ab9540c9f5f53b505d2d7d8d8942438a71bc5e9, which is also `main`)

How I ran it: the PR head was run from the worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0202-verifier/wt`, after `uv sync --frozen`, at a clean tree (`git status` showed nothing to commit). The base was run from a clone at 1ab9540 under this run's `scratch/base`, also after `uv sync --frozen`. Every command ran exactly as written through the throwaway-HOME wrapper, with node v24.14.0 on PATH.

Per criterion:
- NEW | The harness suite passes with an uncommitted harness edit (the `mktemp -d /tmp/t0023-suite.XXXXXX` clone-and-pytest WHEN) | base: `23 failed, 192 passed in 198.74s (0:03:18)` | PR: `215 passed in 189.43s (0:03:09)` | PASS. It fails on base for the reason the spec gives (the H8 baseline of 23 harness-lock failures) and passes on the PR. Afterwards I found one `/tmp/t0023-suite.660att` directory. It was created 83 s after my run started, so it was not this run's directory; it was gone when I checked again later. It came from another process running at the same time, not from a leak in the scenario.
- REGRESSION | The uncommitted-edit refusal still holds on an instance's own store | base: not run | PR: `exit=2`, then `has uncommitted changes:` | PASS
- NEW | Intermediate check: the changelog entry exists with this seam's clause (awk/sed/grep WHEN) | base: `50 CONTIGUOUS`, then `0` | PR: `51 CONTIGUOUS`, then `1` (the matched word is `uncommitted`) | PASS
- REGRESSION | Intermediate check: the two edited test files change no assertion (`git diff main...HEAD -- … | grep -cE '^[-+][[:space:]]*assert'`) | base: not run | PR: `0` | PASS
- REGRESSION | The change adds no whitespace errors (`git diff --check main...HEAD; echo "exit=$?"`) | base: not run | PR: only `exit=0` | PASS

Gate suite: PASS
  `git diff --check main...HEAD`: exit 0, no output.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `215 passed in 199.82s (0:03:19)`, with no failures or errors. (My trailing `${PIPESTATUS[0]}` printed blank because the shell is zsh, so I read the result from pytest's summary line.)

Probes:
- The lock comparison still runs through the launcher. I made a clone with an uncommitted edit and an instance initialised from it, then ran `tests/factory/clean_harness_cli.py`, the test-only launcher this PR adds. With a matching lock, `config` gave exit 0. With `harness.lock` set to 40 zeros, it gave exit 2 and `harness 82d516b… is not the revision this instance accepted (0000…)`, which is the C.2 check. With `--accept-harness 1111…`, it gave exit 2 and `--accept-harness 1111… is not the running harness revision …; …/harness.lock is unchanged`, which is the C.3 check. The clone's real `bin/factory config` still gave exit 2 and `harness … has uncommitted changes:`. The launcher stubs only C.4, as G1 requires. → OK
- Other kinds of dirty checkout. The suite scenario edits only `factory/status.py`. I ran the same command shape on a clone that also had an edited `bin/factory` and an untracked `factory/zz_untracked.py`. Its `git status --short` showed ` M bin/factory`, ` M factory/status.py` and `?? factory/zz_untracked.py`. The run printed `215 passed in 181.59s`. The fix is not special-cased to the tested edit. → OK
- Edge cases of the new `subcommand` helper in `test_harness_lock.py`. I loaded the module and called the helper directly. `()` and `('--accept-harness',)` returned `None`; `('--accept-harness','X','init')` returned `init`; `('--accept-harness','X','config')` returned `config`; `('init','--accept-harness','X')` returned `init`. With `('--accept-harness','paths')` it returned `None`, because `paths` is taken as the SHA value, so the launcher would be used. That matches the CLI parser, where `--accept-harness` takes a value (`factory/cli.py:1008`). → OK
- Code read. The C.4 refusal tests (`test_modified_harness_refused_naming_the_paths` :234, `test_accept_does_not_override_a_modified_harness` :248 and `test_modified_harness_still_runs_throwaway_stores_init_and_paths` :270) all call `cli(clone, …)`. Because `harness != REPO` there, they still run the clone's real `bin/factory`. `guard` calls `harness_changes()` through the module globals (`factory/instance.py:137`), so the launcher's replacement `instance.harness_changes = …` takes effect. Nothing else imports that function by name: `grep -rn harness_changes factory/` finds only `instance.py:110` and `:137`. → OK

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command and both gates ran on the stated head. Both NEW criteria fail on base for the stated reason and pass on the PR, and the probes show the launcher stubs only C.4.
ESCALATIONS: none
