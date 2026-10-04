Sub-ticket: T-0012.4 (parent `intake/state/specs/T-0012/v3.md`, design part C.2–C.5). Branch `factory/T-0012.4` in worktree `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.4`, base `bed7e28`, head `954eff7d789a831dab3132a075fff053da11359e`. There is no remote; the branch is the PR.

Commits on the branch (`git log --oneline main..HEAD`):
- `7a89605` test(T-0012.4): harness lock tests (C.2-C.5), red before the guard
- `fe6303c` harness(T-0012.4): harness lock — refuse an unaccepted or modified harness on the instance's own store, --accept-harness (C.2-C.4)
- `954eff7` test(T-0012.4): changed paths are listed in git's order; compare them as a set

**Blocked in one place.** One existing T-0012.3 test fails under C.2 exactly as the spec words it. The sub-ticket says "Tests to change: none". It also requires the suite to pass with no `failed`. Both cannot be true at once. Details are under Escalations. Every C scenario and every listed regression scenario passes.

## What changed (per lettered part)

- **C.2: lock check on the instance's own store.**
  - `factory/instance.py:129` `guard()` runs only when `is_own_store()` holds. That means `FACTORY_STATE` is unset or resolves to the instance's `state_dir`.
  - It compares the stripped first line of `<instance>/harness.lock` (`read_lock`, line 120) with `harness_revision()` (C.1, from T-0012.3).
  - On a mismatch, or a missing or empty lock, it raises `Refused` with exactly: `harness <rev> is not the revision this instance accepted (<lock>|none); rerun with --accept-harness <rev> to accept it`. `main` then exits 2. The guard runs before `a.fn`, so nothing is written.
  - `factory/cli.py:1046-1049`: `main()` resolves the instance, loads its config, takes the store root, then calls `instance.guard(...)` before the command.
  - `init` and `paths` still return through the existing early branch, so they are exempt.
- **C.3: `--accept-harness SHA`.**
  - It is a top-level argparse option (`factory/cli.py:897`), so it is written before the subcommand.
  - In `guard()`, the SHA must match `[0-9a-f]{40}` and equal the running revision. Otherwise the command exits 2, the lock is unchanged and nothing is logged.
  - On a match, the guard writes `<rev>\n` to the lock and appends a `harness.accepted` event (`instance`, `old`, `new`) to the instance's store log. Then the command runs.
- **C.4: uncommitted harness edits.**
  - `harness_changes()` (`factory/instance.py:110`) runs `git -C <HARNESS> status --porcelain -- factory bin/factory agents pyproject.toml uv.lock`. Files that `.gitignore` excludes do not count, by git's own rules.
  - If it prints anything, the command is refused with `harness <path> has uncommitted changes:` plus one changed path per line.
  - This check runs before the accept step, so `--accept-harness` cannot override it.
  - `<HARNESS>` is the running checkout (`instance.HARNESS`), as the plan reads C.4.
  - If `git status` itself fails, or the revision cannot be read, the command is refused (exit 2). It is not allowed to pass.
- **C.5: new test file** `tests/factory/test_harness_lock.py` (24 cases). No existing test file was changed.

## Acceptance results

Each WHEN was run verbatim with bash from the worktree (the checkout under test) after `uv sync --frozen`. I extracted the commands from input.md with `sed` rather than retyping them. missing-lock-refused is the lock-mismatch command with the `printf … > $T/.factory/harness.lock` part swapped for `rm -f $T/.factory/harness.lock`. I did the swap with a Python `str.replace` and asserted that the original text was present first.

| Scenario | Before (base `bed7e28`) | After (`954eff7`) |
|---|---|---|
| lock-mismatch-refused | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` |
| accept-current-revision-rewrites-lock | `init=0` / `exit=2 lock_is_rev=no logged=0` | `init=0` / `exit=0 lock_is_rev=yes logged=1` |
| accept-other-revision-refused | `init=0` / `exit=2 lock=000…0 tickets=0` (already passes: argparse rejects the unknown option) | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` |
| throwaway-store-ignores-lock | `init=0` / `exit=0 ticket=[T-0001.yaml]` (already passes: no check exists) | `init=0` / `exit=0 ticket=[T-0001.yaml]` |
| dirty-harness-refused | `init=0` / `exit=0 tickets=1 names=0` | `init=0` / `exit=2 tickets=0 names=1` |
| missing-lock-refused | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` |
| init-and-paths-exempt | `paths=0 init=0 lock=000…0` (already passes) | `paths=0 init=0 lock=0000000000000000000000000000000000000000` |
| accept-does-not-override-dirty | `exit=2 lock_same=yes tickets=0` (already passes: argparse rejects the unknown option) | `exit=2 lock_same=yes tickets=0` |
| harness-files-in-repo (T-0012.3) | — | `agents=6 green_only=0` |
| role-prompt-text-unchanged (T-0012.3) | — | `changed=0 of 14` |
| init-creates-instance-in-throwaway-target | — | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` |
| store-command-from-subdirectory-uses-target-instance | — | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` |
| command-outside-any-instance-refused | — | `exit=2 created=0 names_instance=1` |
| factory-instance-override-from-elsewhere | — | `init=0` / `found=1` |
| composed-input-opens-with-instance-context | — | `init=0` / `first=[CTX-MARKER for demo]` |
| run-system-prompt-names-instance | — | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` |
| paths-name-harness-workflows-and-instance | — | `init=0` / `True True True True` |
| harness-suite-passes-after-uv-sync | `sync=0` / `92 passed in 112.21s` | `sync=0` / **`1 failed, 115 passed in 77.35s`**. Fails the criterion; see Escalations. |
| green-harness-still-present | — | `green keeps its harness` |
| whitespace (`git diff --check main...HEAD`) | — | `exit=0` |

The worktree was clean (`git status --porcelain` empty) for every "after" run. That matters because C.4 would otherwise refuse the T-0012.3 scenarios, which the sub-ticket notes is by design.

Gate commands, run from the worktree exactly as written:
- `git diff --check main...HEAD` → exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `FAILED tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides` / `1 failed, 115 passed in 88.72s`.

## Tests added/changed

`tests/factory/test_harness_lock.py` is a new file with 24 cases. It was committed before the guard. Against the base code, 18 failed and 6 passed. The 6 that passed are the "must not refuse" cases: fresh lock runs, stripped first line, init/paths exempt, throwaway store, ignored and non-harness edits, and a modified harness still running throwaway stores/init/paths. With the guard, all 24 pass. The cases:
- **C.2:**
  - The lock set to another revision, left empty, or missing is refused with the exact message (`(none)` for the last two), and the target tree is unchanged.
  - Five different commands (`ticket show`, `config`, `log tail`, `ticket transition`, `run start`) are refused with the exact mismatch message, run from inside `.factory/`.
  - `init` and `paths` are exempt and leave the lock as it was.
  - A throwaway `FACTORY_STATE` runs whatever the lock says.
  - `FACTORY_STATE` pointing at the instance's own store is still checked.
  - The lock compares its stripped first line.
- **C.3:**
  - Accepting the current revision rewrites the lock, logs one `harness.accepted` event with `old`/`new` before `ticket.created`, and later commands run without the option.
  - A missing lock is logged as `old: null`.
  - An abbreviated SHA, another 40-hex value, a 12-character prefix and an uppercase SHA are all refused, and the tree is unchanged.
- **C.4** (each on a local `git clone` of this checkout, so this checkout is never edited; the clone's `.venv` is a symlink to the suite's own `sys.prefix`):
  - A modified tracked file plus an untracked file under `agents/` are refused, and both paths are named.
  - `--accept-harness` does not override a modified harness.
  - Gitignored `__pycache__` files and edits outside the harness paths do not count.
  - A modified harness still runs throwaway stores, `init` and `paths`.
- **Upgrade flow (C.1 with C.2/C.3):**
  - A docs-only commit in the harness does not trip the lock.
  - A commit to `factory/` does trip it, with the exact old and new revisions in the message.
  - `--accept-harness <new>` clears it.

No existing test was changed.

## Known gaps and uncertainties

- **One existing test fails.** See Escalations. I did not change it, and I did not exempt `config` from the lock, because either one would mean improvising around C.2.
- **Four "NEW" criteria already passed at base.** These are accept-other-revision-refused, throwaway-store-ignores-lock, init-and-paths-exempt and accept-does-not-override-dirty.
  - Two of them say what must not be refused, so no check at all satisfies them.
  - The other two passed only because argparse rejected the unknown `--accept-harness` option with exit 2.
  - They prove nothing about C on their own. The discriminating evidence is the new tests that failed at base: the exact refusal messages, the lock-unchanged cases and the clone-based C.4 cases.
  - The process says to escalate when a NEW criterion behaves otherwise. I record it here instead of stopping, because the input itself warns that such passes are vacuous, and the spec is not wrong.
- **`--accept-harness` is silently ignored in two cases where the guard does not apply:**
  - with `init` or `paths`, which are exempt (`paths` must write nothing, B.6);
  - when the store in use is not the instance's own.

  The spec does not say what should happen there. A reviewer may prefer a refusal.
- Changed paths in the C.4 message are in `git status --porcelain` order (tracked changes first, then untracked) and taken as `line[3:]`. For a rename this prints `old -> new`, and paths with special characters appear quoted, as git prints them.
- The lock is written as `<rev>\n`, the same format `init` uses. The log event is named `harness.accepted`; the spec does not name it.
- `harness_revision()` and the dirty check use the running checkout (`instance.HARNESS`), not `instance.yaml`'s `harness:` value. This follows the plan's reading, and the sub-ticket marks a mismatch refusal as out of scope.
- **Operational effect on this build itself.** Every store command against an instance's own store now runs `git status` on the harness. Any later sub-ticket whose test run, or whose operator, uses a dirty harness checkout against a real instance's own store will be refused by design. The suite is unaffected because it uses throwaway stores, except where it deliberately builds own-store targets from a clean checkout.

## Out-of-scope observations

- The `factory/workflows/*.js` header comments do not mention `--accept-harness` or the upgrade step. This sub-ticket does not cover them (E.6 covers README).

## Escalations

1. **C.2 contradicts an existing test that this sub-ticket may not change.**
   - The test is `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides`, at line 240, added in T-0012.3.
   - It builds an instance directory `alt` from only `instance.yaml` and `context.md`, with no `harness.lock`. Then it runs `config` twice on that instance's own store: first with `FACTORY_INSTANCE=alt`, then with `FACTORY_REPO=target`.
   - C.2 says every command except `init` and `paths` exits 2 when "the lock is missing". So the first call now fails: `harness fe6303c56536389c668e37ccba0e73b98077d44e is not the revision this instance accepted (none); rerun with --accept-harness fe6303c… to accept it` / `assert 2 == 0` (line 247).
   - The sub-ticket says "Tests to change: none" and requires harness-suite-passes-after-uv-sync to report no `failed`.
   - Proposed resolution, for a human: add this test to "Tests to change" with one added line after `(alt / "context.md").write_text("x\n")`: `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`. I applied that line temporarily: the test passed (`1 passed, 21 deselected`). I then reverted it with `git checkout tests/factory/test_instance.py`, so the branch does not carry it.
   - Alternative: exempt `config` from the lock. That contradicts C.2's "every command except `init` and `paths`", so I did not do it.
2. **Informational.** Four NEW criteria passed vacuously at base (see Known gaps). They are not a spec defect, but by the process rule they are reported here.

STATUS: BLOCKED
CONFIDENCE: high. The C implementation passes every C scenario and all 24 new tests, and the single failure is reproduced and traced to the spec-versus-existing-test conflict, with the fix verified.
ESCALATIONS: (1) The existing test `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides` fails under C.2's missing-lock refusal; "Tests to change: none" forbids the one-line fix, so it needs a human ruling to add it to Tests to change, or to amend C.2. (2) Four NEW criteria (accept-other-revision-refused, throwaway-store-ignores-lock, init-and-paths-exempt, accept-does-not-override-dirty) already passed at base, vacuously.
