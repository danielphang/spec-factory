Commit: a5f13292ab8f2a5655daba442f45d81ed81d8a94 (branch `factory/T-0012.4`; harness revision `010d1b00c5835c7022a72771c63f63f8b6ab3707`). Base: 68e89456939ac7939ef659975dfbb37812bd6f83 (= `main`, an ancestor of head).

Method:
- Two fresh clones in a scratch directory: one detached at head and one at base, each with local `main` set to base. I ran `uv sync --frozen` in each (exit 0). `git status --porcelain` was empty before and after every run.
- A script pulled every WHEN out of input.md as written (the text between the backticks), with no retyping.
- missing-lock-refused is lock-mismatch-refused with its one `printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock` swapped for `rm -f $T/.factory/harness.lock`. The script first asserted that this text appears exactly once.
- Each command ran with `bash` from the checkout root, with `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_STATE` and `FACTORY_INTEGRATION_BRANCH` unset.
- The whitespace criterion was `git diff --check main...HEAD; echo "exit=$?"`.

Per criterion: label | command | base | PR | result
- NEW | lock-mismatch-refused | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS
- NEW | accept-current-revision-rewrites-lock | `init=0` / `exit=2 lock_is_rev=no logged=0` | `init=0` / `exit=0 lock_is_rev=yes logged=1` | PASS
- REGRESSION (operator relabel) | accept-other-revision-refused | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` | same | PASS
- REGRESSION (operator relabel) | throwaway-store-ignores-lock | `init=0` / `exit=0 ticket=[T-0001.yaml]` | same | PASS
- NEW | dirty-harness-refused | `init=0` / `exit=0 tickets=1 names=0` | `init=0` / `exit=2 tickets=0 names=1` | PASS
- NEW | missing-lock-refused | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS
- REGRESSION (operator relabel) | init-and-paths-exempt | `paths=0 init=0 lock=0000000000000000000000000000000000000000` | same | PASS
- REGRESSION (operator relabel) | accept-does-not-override-dirty | `exit=2 lock_same=yes tickets=0` | same | PASS. At base, exit 2 comes from argparse rejecting the unknown `--accept-harness`. That is the vacuous pass the relabel describes. The discriminating test is `test_accept_does_not_override_a_modified_harness`, which passes in the suite at head.
- REGRESSION | harness-files-in-repo | `agents=6 green_only=0` | same | PASS
- REGRESSION | role-prompt-text-unchanged | `changed=0 of 14` | same | PASS
- REGRESSION | init-creates-instance-in-throwaway-target | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` | same | PASS
- REGRESSION | store-command-from-subdirectory-uses-target-instance | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` | same | PASS
- REGRESSION | command-outside-any-instance-refused | `exit=2 created=0 names_instance=1` | same | PASS
- REGRESSION | factory-instance-override-from-elsewhere | `init=0` / `found=1` | same | PASS
- REGRESSION | composed-input-opens-with-instance-context | `init=0` / `first=[CTX-MARKER for demo]` | same | PASS
- REGRESSION | run-system-prompt-names-instance | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` | same | PASS
- REGRESSION | paths-name-harness-workflows-and-instance | `init=0` / `True True True True` | same | PASS
- REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `92 passed in 89.93s (0:01:29)` | `sync=0` / `116 passed in 96.00s (0:01:35)` | PASS. N=116 ≥ 70, and it includes the 24 new cases in `tests/factory/test_harness_lock.py`. No `failed` or `error`.
- REGRESSION | green-harness-still-present | `green keeps its harness` | same | PASS
- REGRESSION | whitespace (sub-ticket diff) | `exit=0` (empty range) | `exit=0` | PASS

The nine T-0012.3 scenarios are harness-files-in-repo, role-prompt-text-unchanged and the seven factory-instance scenarios. I took the list from the T-0012.3 section of `intake/state/plans/T-0012.md`.

Every NEW criterion fails at base for the reason the spec gives: base has no lock enforcement, so the command runs and writes a ticket, or `--accept-harness` is not recognised. Each one passes at head.

Tests to change: `git diff 68e8945...HEAD -- tests` touches only the new `tests/factory/test_harness_lock.py` (+281) and `tests/factory/test_instance.py` (+1). The one added line is exactly the line the operator ruled, placed after `(alt / "context.md").write_text("x\n")`. No assertion changed.

Gate suite: PASS
- Run in the given worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0086-verifier/wt` at `a5f1329`, after `uv sync --frozen -q` (exit 0), with a clean tree before and after.
- `git diff --check main...HEAD` printed nothing, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` gave `116 passed in 115.79s (0:01:55)`, exit 0.

Probes (head clone, absolute paths; a positive control where one was needed):
- Lock = a real older harness revision (`f5d82034…`, base's harness revision), not the all-zero value the tests use → exit 2, tickets=0, exact C.2 message naming both SHAs → OK. The check is not special-cased to zeros.
- Lock = the correct revision with a CRLF ending → exit 0 → OK, the first line is stripped.
- Mismatched lock, with `FACTORY_STATE` naming the own store through a symlink and a trailing slash → exit 2, tickets=0, hint=1. Control: the same path with the correct lock → exit 0, 1 ticket → OK. Own-store detection resolves paths.
- Mismatched lock, with the instance chosen by `FACTORY_INSTANCE` from an unrelated cwd → exit 2, tickets=0 → OK.
- `--accept-harness "<rev> "` (trailing space) → exit 2, lock unchanged → OK. `--accept-harness` written after the subcommand → exit 2 (argparse), lock unchanged, tickets=0 → OK.
- A 1 MB single-line junk lock → exit 2. A lock that is a directory → exit 2 with `(none)` in the message → OK. Concern, not a failure: the 1 MB line is echoed whole into stderr (1,000,178 bytes).
- Staged-only new file `factory/staged_note.py` in a clone of the harness → exit 2, `has uncommitted changes:` / `factory/staged_note.py`. Control after unstaging → exit 0 → OK.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command ran as written on clean base and head clones. NEW criteria fail at base for the stated reason and pass at head. Both gates pass in the worktree (116 passed). Probes away from the tested values (a real older SHA, symlinked own store, override instance, staged file) behave as C.2–C.4 require.
ESCALATIONS:
- Non-blocking, outside the criteria. The implementer recorded, and I did not re-run, that the suite gives `23 failed, 93 passed` from a harness checkout with an uncommitted edit under `factory/`. The B/C tests drive own-store targets with this checkout's `bin/factory`, and C.4 refuses them. C.4's prose says a harness under development "still runs its own tests against throwaway stores". That holds for the imported tests but not for the new own-store tests. This is a spec/test-design question for a later ticket. The gates run on committed trees, so they are not affected.
- Non-blocking. `--accept-harness` is silently ignored for `init`, `paths` and non-own stores; the spec says nothing on this. A refusal message echoes an arbitrarily long lock first line to stderr.
