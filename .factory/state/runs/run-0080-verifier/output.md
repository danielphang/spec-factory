Commit: 010d1b00c5835c7022a72771c63f63f8b6ab3707 (worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0080-verifier/wt`, `git status --porcelain` empty before and after every run)

Base: 68e89456939ac7939ef659975dfbb37812bd6f83 (`main`). I checked it in a fresh `git clone` of `~/dev/spec-factory`, detached at that SHA, in my scratchpad, after its own `uv sync --frozen` (exit 0). `git diff --stat bed7e28 68e8945 -- . ':!intake/state'` is empty, so the base's harness code is identical to the branch's merge-base `bed7e28`.

Method: I extracted every WHEN from input.md with a script. It slices between the backticks, so nothing was retyped. For missing-lock-refused, the script substituted `rm -f $T/.factory/harness.lock` for the single occurrence of `printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock` in lock-mismatch-refused, after asserting that the text occurs exactly once. Each command ran with `bash` from the checkout root, after `uv sync --frozen` (exit 0 on both trees).

Per criterion: label | command | base | PR | result
- NEW | lock-mismatch-refused | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS. Fails at base because no lock check exists.
- NEW | accept-current-revision-rewrites-lock | `init=0` / `exit=2 lock_is_rev=no logged=0` | `init=0` / `exit=0 lock_is_rev=yes logged=1` | PASS. Fails at base because the option does not exist (argparse rejects it).
- REGRESSION (operator relabel) | accept-other-revision-refused | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` | same | PASS. Passes at base vacuously, as the relabel says.
- REGRESSION (operator relabel) | throwaway-store-ignores-lock | `init=0` / `exit=0 ticket=[T-0001.yaml]` | same | PASS
- NEW | dirty-harness-refused | `init=0` / `exit=0 tickets=1 names=0` | `init=0` / `exit=2 tickets=0 names=1` | PASS
- NEW | missing-lock-refused (derived WHEN) | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS
- REGRESSION (operator relabel) | init-and-paths-exempt | `paths=0 init=0 lock=0000000000000000000000000000000000000000` | same | PASS
- REGRESSION (operator relabel) | accept-does-not-override-dirty | `exit=2 lock_same=yes tickets=0` | same | PASS
- REGRESSION | harness-files-in-repo | `agents=6 green_only=0` | same | PASS
- REGRESSION | role-prompt-text-unchanged | `changed=0 of 14` | same | PASS
- REGRESSION | init-creates-instance-in-throwaway-target | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` | same | PASS
- REGRESSION | store-command-from-subdirectory-uses-target-instance | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` | same | PASS
- REGRESSION | command-outside-any-instance-refused | `exit=2 created=0 names_instance=1` | same | PASS
- REGRESSION | factory-instance-override-from-elsewhere | `init=0` / `found=1` | same | PASS
- REGRESSION | composed-input-opens-with-instance-context | `init=0` / `first=[CTX-MARKER for demo]` | same | PASS
- REGRESSION | run-system-prompt-names-instance | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` | same | PASS
- REGRESSION | paths-name-harness-workflows-and-instance | `init=0` / `True True True True` | same | PASS
- REGRESSION | harness-suite-passes-after-uv-sync | base, with only the new test file added (see below): `18 failed, 98 passed` | `sync=0` / `116 passed in 96.45s (0:01:36)` | PASS. 116 ≥ 70, the new C tests are included, and there is no `failed`/`error`.
- REGRESSION | green-harness-still-present | `green keeps its harness` | same | PASS
- REGRESSION | whitespace (sub-ticket diff): `git diff --check main...HEAD; echo "exit=$?"` | n/a | `exit=0` | PASS. Also `git diff --check "$BASE" HEAD` with `BASE=$(git rev-parse main)` → `exit=0`.

Discriminating evidence for the relabelled REGRESSION items:
- I copied `tests/factory/test_harness_lock.py` from head into the base clone and committed it there. The file is outside the harness paths, so the revision is unchanged. Running the file against base code gave `18 failed, 6 passed in 6.74s`. The full suite there gave `18 failed, 98 passed`.
- At head, all 24 cases pass, inside the 116.

Tests to change:
- The diff touches `tests/factory/test_instance.py` with exactly one added line, `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`, after `(alt / "context.md").write_text("x\n")`. That is the operator's ruling verbatim.
- No other existing test changed (`git diff --stat 68e8945...HEAD`: `factory/cli.py`, `factory/instance.py`, `tests/factory/test_harness_lock.py` (new), `tests/factory/test_instance.py` +1).

Code check against design C.2–C.4:
- The refusal messages match the spec text: `harness <rev> is not the revision this instance accepted (<lock>|none); rerun with --accept-harness <rev> to accept it` and `harness <path> has uncommitted changes:` followed by the paths.
- The dirty check runs `git -C HARNESS status --porcelain -- factory bin/factory agents pyproject.toml uv.lock` (`HARNESS_PATHS`, `factory/instance.py:33`), and it runs before the accept step.
- `init` and `paths` return before `guard` (`factory/cli.py` `main`).
- `is_own_store` compares resolved paths.

Gate suite: PASS
- `git diff --check main...HEAD` → no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 87.92s (0:01:27)`, exit 0.

Probes (on head):
- `FACTORY_STATE` names the own store in other spellings: trailing slash, `/var` instead of `/private/var`, the realpath, and `.../state/../state`. Mismatched lock in all four. → `exit=2 tickets=0 hint=1` each time → OK. The own-store test is not tied to one spelling.
- `FACTORY_INSTANCE=$T/.factory`, run from an unrelated directory, mismatched lock → `exit=2 tickets=0 hint=1` → OK.
- Lock written with a CRLF ending (`<REV>\r\n`) → `exit=0` → OK.
- `--accept-harness "<REV> "` (trailing space) → `exit=2`, lock unchanged → OK.
- `--accept-harness <REV>` written after the subcommand → `exit=2` (argparse), lock unchanged → OK. C.3 says the option goes before the subcommand.
- `--accept-harness <REV>` when the lock already holds REV → `exit=0`. It still logs a `harness.accepted` event (old = new) → OK. The spec does not forbid this.
- In a clone, a staged deletion (`git rm --cached agents/factory-stub.md` plus the file removed) → `exit=2 tickets=0`, and the path is named → OK.
- In a clone, a staged `git mv pyproject.toml pyproject2.toml` → `exit=2 tickets=0`, `pyproject.toml` named. After restoring, the same target runs (`exit=0`) → OK.
- Suite run from a dirty checkout: a clone of head with `# dev edit` appended to `factory/__init__.py` → `23 failed, 93 passed` (17 in `test_harness_lock.py`, 6 in `test_instance.py`) → CONCERN, outside the criteria. See ESCALATIONS.

None of the probes shows special-casing to the tested inputs.

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance command verbatim on head and on a fresh base clone. The NEW items fail at base for the stated reason and pass at head. The REGRESSION items pass on both. Both gates exit 0 (116 passed). Eight probes behave correctly.
ESCALATIONS:
- Non-blocking design/test-ergonomics question, already reported by the implementer, and I confirmed it. The suite fails from any harness checkout that has an uncommitted edit under the harness paths (`23 failed, 93 passed`). The cause is that the T-0012.3 and T-0012.4 tests drive own-store targets with this checkout's `bin/factory`, which C.4 refuses by design. Design C.4 says "a harness under development, which is uncommitted by definition, still runs its own tests against throwaway stores". That is true for the imported suite but not for these tests, so a developer must commit before the suite goes green. The gate runs on committed branches and is unaffected. A product decision is needed on whether the B/C tests should run on a clean clone or a throwaway store; that would be a later ticket.
