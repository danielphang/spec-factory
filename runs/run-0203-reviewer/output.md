Commit: fa09a10f700a44ab7ce5881bf3daf5615ecbbb57 (branch `factory/T-0023.1`, base `1ab9540c9f5f53b505d2d7d8d8942438a71bc5e9`; `main` is still at the base, checked with `git rev-parse main`)

## Checks, in order

1. Test integrity. `git diff --stat main...HEAD` lists four files: `docs/changelog.md` (+1), `tests/factory/clean_harness_cli.py` (new, 28 lines), `tests/factory/test_harness_lock.py` (+22/-4), `tests/factory/test_instance.py` (+7/-1). Both edited test files are named under the sub-ticket's "Tests to change", and the edits are the `cli` helper, the module docstring lines 8-10 and one import, as listed. The intermediate check `git diff main...HEAD -- tests/factory/test_harness_lock.py tests/factory/test_instance.py | grep -cE '^[-+][[:space:]]*assert'` printed `0`: no assertion line added or removed. No test skipped, deleted or weakened. No error swallowed.

2. Correctness, against part G of the parent spec.
   - G1, the launcher (`tests/factory/clean_harness_cli.py`). It sets `FACTORY_CWD` from `os.getcwd()` (line 22), changes into `parents[2]` of the file (line 23), puts that checkout first on `sys.path` (line 24), replaces `factory.instance.harness_changes` (line 27) and exits with `cli.main(sys.argv[1:])` (line 28). `guard` reads `harness_changes` as a module global at call time (`factory/instance.py:137`), and `grep -rn "from factory.instance import" factory tests` finds no by-name import of it, so the replacement reaches the one production caller. The lambda accepts `*args, **kwargs`, so the real signature `harness_changes(harness=HARNESS)` is covered. `pytest --collect-only -q tests/factory | grep -c clean_harness_cli` printed `0` and the collection total is `215 tests collected`, so pytest does not collect it.
   - I probed the launcher on a clone with an uncommitted edit, against an instance created with that clone's `bin/factory`: with `harness.lock` set to forty zeros, `clean_harness_cli.py config` exited 2 with `harness 82d516be… is not the revision this instance accepted (000…)`, so design item C.2 still refuses; `--accept-harness 1111…` exited 2 with `is not the running harness revision`, so C.3 still checks the SHA; `--accept-harness <running revision>` exited 0 and rewrote the lock to that revision. Only the uncommitted-edit refusal (C.4) is stubbed, as the spec requires. From a subdirectory of the instance, `clean_harness_cli.py paths` reported the instance at `<tgt>/.factory`, so the caller's directory is handed over as `bin/factory` does.
   - G2 (`test_harness_lock.py:34-50`). `subcommand` skips `--accept-harness` and its value; `cli` picks the launcher when `harness == REPO` and the subcommand is not `init` or `paths`. I read every `cli(` call in the file: the REPO calls with `--accept-harness` first (lines 190, 208, 226) correctly resolve to `ticket`/`config`; the parametrized `argv` at line 152 starts with `ticket`, `config`, `log` or `run`; lines 160 and 163 (`paths`, `init`) keep `bin/factory`. Every `clone` call keeps the clone's real `bin/factory`, including the three C.4 refusal tests. Docstring lines 8-12 state the rule.
   - G3 (`test_instance.py:25-31`). `argv[:1] in (("init",), ("paths",))` chooses `bin/factory`; every other call runs the launcher. No call in the file starts with `--accept-harness` (grep), so the `argv[0]` rule the spec gives is sufficient. `import sys` added at line 12.
   - J1, S4 clause. Entry 51 sits after entry 50 and before the blank line above `Declined:` (`docs/changelog.md:56-58`), one line, with the prescribed opening text and the S4 clause wording from the parent's step J1.
   - Edge case the spec implies: the launcher runs on `sys.executable` rather than `.venv/bin/python`. In the gate and in the suite scenario both are the worktree's venv (the clone symlinks it), and `pyproject.toml` has `[tool.uv] package = false`, so neither `bin/factory` nor the launcher relies on an installed `factory` package; both import it from the checkout they run in. The clone's edited `factory/status.py` is therefore the one the clone's tests see, which is what the scenario needs.

3. Scope. The diff is tests and the changelog only; no harness code changed (`git diff --stat main...HEAD` shows nothing under `factory/`, `bin/`, `agents/`, `pyproject.toml`, `uv.lock`). The implementer's Known gaps asks whether the `subcommand` helper (`test_harness_lock.py:34`) and the `CLEAN_CLI` constants go beyond the literal "cli helper". They implement the subcommand rule that step G2 itself spells out, live beside the helper, and touch no assertion. Accepted as part of the listed change; no finding.

4. Silent behavior changes: none. Production code is untouched, so no caller, user or other service sees a difference.

5. Security and data safety: nothing new is written outside temporary directories; the launcher is not reachable from the production CLI, which honours no such switch.

6. Protected paths: none touched. `tests/factory/**` and `docs/changelog.md` are not in the protected list, matching the sub-ticket's "Protected paths: none".

7. Coding standard. Rule 1: `subcommand` is a six-line loop on the standard library with no existing helper to reuse; `CLEAN_CLI` beside `REPO`/`BIN` follows the two files' existing pattern of per-file constants. Rule 2: callers of `cli` and of `harness_changes` are named in the PR description and match my grep. Rule 3: no shortcut needing a `factory:` marker; the PR says "markers added: none". Rule 6: the test launcher patches `instance.harness_changes` as a module attribute, and the production lookup is through the module global, which is exactly the rule. Lean already.

8. PR description. What changed glosses "harness lock" and "instance" and says in words what changed; Known gaps names each uncertainty. One finding below.

## Acceptance I ran (worktree root, throwaway HOME, `uv sync --frozen` done first, Python 3.14.5)

- The harness suite passes with an uncommitted harness edit (NEW): the WHEN as written printed `215 passed in 203.30s (0:03:23)`; the clone's `git status --porcelain` showed ` M factory/status.py` first, so the edit was in place. A `/tmp/t0023-suite.*` directory present afterwards belongs to the concurrent run-0202-verifier (born 07:38:58, its `pytest-0` still being written at 07:40), not to this run.
- The uncommitted-edit refusal still holds on an instance's own store (REGRESSION): printed `exit=2`, then `has uncommitted changes:`.
- Changelog intermediate check: printed `51 CONTIGUOUS`, then `1`.
- No-assertion-change intermediate check: printed `0`.
- `git diff --check main...HEAD; echo "exit=$?"`: printed only `exit=0`.
- Gate suite in the worktree: `215 passed in 206.84s (0:03:26)`, exit 0.

Findings:
- [NIT] PR description: What changed: "design items C.2 and C.3" and "design item C.4" are used without saying what they are → a reader new to this project cannot tell from the description which check is stubbed and which two still run; one clause such as "C.4, the refusal of a checkout with uncommitted harness edits; C.2 and C.3, the lock comparison and `--accept-harness`" would fix it (writing standard rule 6).

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. I ran all five acceptance commands and both gates on `fa09a10` and read every `cli(` call site in both edited files; the only probe beyond the spec (lock mismatch and wrong/right `--accept-harness` through the launcher) confirmed C.2 and C.3 still run.
ESCALATIONS: none
