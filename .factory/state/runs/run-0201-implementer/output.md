Sub-ticket: T-0023.1 (T-0023-S4, part G of T-0023 / issue #39). Branch `factory/T-0023.1`, commit `fa09a10` on base `1ab9540`.

## What changed

The harness's own test suite now passes in a checkout that has an uncommitted edit to the harness code. Before this change, 23 tests failed in such a checkout. They failed because the harness lock refuses every store command from a checkout with uncommitted harness edits. (The harness lock is the check that stops an instance, meaning a repository the factory serves, from running harness code it has not accepted.) None of those 23 tests is about that refusal. The refusal itself is unchanged and keeps its own tests.

- **G1.** New file `tests/factory/clean_harness_cli.py`. It is a test-only launcher that runs the CLI the way `bin/factory` does. It sets `FACTORY_CWD` to the working directory, changes into the harness checkout (two levels above the file) and puts that checkout first on `sys.path`. Then it replaces `factory.instance.harness_changes` with a function that returns `[]` and exits with `factory.cli.main(sys.argv[1:])`. It replaces only that one function. `guard` (`factory/instance.py:129`) still reads the lock and compares it with the running revision (design items C.2 and C.3). `guard` looks `harness_changes` up as a module global at call time (`factory/instance.py:137`), so the replacement reaches it (coding standard rule 6). The file is not named `test_*`, so pytest does not collect it.
- **G2.** `tests/factory/test_harness_lock.py`. `cli` (now at line 45) runs `[sys.executable, CLEAN_CLI, *argv]` when `harness == REPO` and the subcommand is neither `init` nor `paths`. Otherwise it runs `harness/bin/factory` as before. A new helper, `subcommand` (line 34), finds the subcommand: the first argument that is not `--accept-harness` or its value. Clone cases still run the clone's real `bin/factory`, because `harness` is the clone. That includes the three uncommitted-edit refusal tests, `test_modified_harness_refused_naming_the_paths`, `test_accept_does_not_override_a_modified_harness` and `test_modified_harness_still_runs_throwaway_stores_init_and_paths`. The module docstring's old lines 8-10 now state this rule (lines 8-12).
- **G3.** `tests/factory/test_instance.py`. `cli` (line 25) runs the launcher unless `argv[0]` is `init` or `paths`. Those two stay on `bin/factory`, so the tests still exercise how `bin/factory` hands over the caller's directory. Added `import sys` and a `CLEAN_CLI` constant.
- **J1 (S4 clause).** `docs/changelog.md` gains entry 51, placed after entry 50 and before the blank line above `Declined:`. It reads: "51. After issue #39 (2026-10-04), a batch of harness defects found in real runs: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested." Later seams (S1, S2, S3) append their clauses to this same line.

No harness code changed. `git diff --stat main...HEAD` prints 4 files, 58 insertions and 5 deletions: `docs/changelog.md`, `tests/factory/clean_harness_cli.py`, `tests/factory/test_harness_lock.py` and `tests/factory/test_instance.py`.

Callers (coding standard rule 2):
- `cli` in each test file is called only inside that same file.
- `factory.instance.harness_changes` has one production caller, `guard` (`factory/instance.py:137`). The grep was `grep -rn harness_changes factory`. No production code changed.

## Acceptance results

Every command ran from the worktree root through the throwaway-HOME wrapper, after `uv sync --frozen`, with node v24.14.0.

- **The harness suite passes with an uncommitted harness edit (NEW).**
  - Before, on base `1ab9540`: `23 failed, 192 passed in 184.44s (0:03:04)`.
  - After, on `fa09a10`: `215 passed in 198.66s (0:03:18)`.
  - Afterwards, `ls -d /tmp/t0023-suite.*` printed `no matches found`, so the scenario removed its temporary directory.
- **The uncommitted-edit refusal still holds on an instance's own store (REGRESSION).** After the change it printed `exit=2`, then `has uncommitted changes:`.
- **Intermediate check, changelog entry 51 exists with this seam's clause (NEW).**
  - Before: `50 CONTIGUOUS`, then `0`.
  - After: `51 CONTIGUOUS`, then `1`.
- **Intermediate check, the two edited test files change no assertion (REGRESSION).** After the change it printed `0`.
- **The change adds no whitespace errors (REGRESSION).** After the change it printed only `exit=0`.

Gates on `fa09a10`, each run exactly as written:
- `git diff --check main...HEAD` exited 0 and printed nothing.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `215 passed in 198.67s (0:03:18)` and exited 0.

## Tests added/changed

- **Added:** `tests/factory/clean_harness_cli.py`. It is a launcher, not a test, and pytest does not collect it.
- **Changed:** `tests/factory/test_harness_lock.py`, the `cli` helper and the module docstring's old lines 8-10. "Tests to change" lists both.
- **Changed:** `tests/factory/test_instance.py`, the `cli` helper and one import. "Tests to change" lists both.
- **Unchanged:** every assertion in both files. The intermediate check printed `0`.

## Known gaps and uncertainties

- The ticket allows changes to the `cli` helper, but `test_harness_lock.py` also gains a small `subcommand` helper (line 34) and a module constant, `CLEAN_CLI`. `test_instance.py` gains the same constant and a three-line comment in `cli`. All of these serve the `cli` change, and none touches an assertion. Even so, this is more than the literal "cli helper" line, so the reviewer should confirm it is acceptable.
- The launcher differs from `bin/factory` in two small ways:
  - It runs on `sys.executable`, the suite's own interpreter, where `bin/factory` uses `.venv/bin/python`. Under `uv run` and in the suite scenario these are the same venv.
  - It sets `FACTORY_CWD` from `os.getcwd()`, where `bin/factory` uses the shell's `$PWD`. `caller_cwd()` resolves the path either way, so the result is the same unless the caller's path runs through a symlink. No test does that.
- `subcommand` recognises only the space-separated form `--accept-harness SHA`. No test uses `--accept-harness=SHA`. If one did, the launcher would still be chosen correctly, unless that test runs `init` or `paths` through REPO.
- `test_instance.py` `cli` checks only `argv[0]`, as G3 says. No call in that file passes `--accept-harness` (grep of the file).
- The 23 previously failing tests now run on the launcher, not on `bin/factory`. A defect in the shell wrapper `bin/factory` would therefore no longer surface through them for commands other than `init` and `paths`. Those two commands, and every clone case, still run the real wrapper. This is the trade-off the parent spec chose.
- factory: markers added: none.

## Out-of-scope observations

- The four `test_instance.py` tests that assume their temporary directory lies outside every repository are untouched, as the parent's Out of scope says. The suite scenario avoids them by setting its own `TMPDIR` under `/tmp`.
- The worktree contains no `AGENTS.md`, so none was read for this repository. The briefing and the parent spec were the instructions.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All five acceptance commands and both gates were run on the committed head, and the NEW suite scenario went from 23 failed to 215 passed with the refusal test still green.
ESCALATIONS: none
