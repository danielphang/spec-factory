Commit: 010d1b00c5835c7022a72771c63f63f8b6ab3707 (branch `factory/T-0012.4`, worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0077-verifier/wt`, `git status --porcelain` empty before and after every run)

Base: f809c694fed21286bd2c1c234943c3dd96656db3. I checked it out in a fresh scratch clone (`git clone /Users/dphang/dev/spec-factory` then `checkout --detach f809c69`), and ran `uv sync --frozen` there and in the worktree. The branch's merge-base is `bed7e28`. `git diff --stat bed7e28 f809c69 -- factory bin agents pyproject.toml uv.lock tests` is empty, so the base has the same harness code as the merge-base.

Method: a script pulled every WHEN out of input.md verbatim, without retyping. For missing-lock-refused it swapped the single occurrence of `printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock` for `rm -f $T/.factory/harness.lock`, after asserting that the text occurs exactly once. Each command ran with `bash` from the root of the checkout under test.

Per criterion: label | command | base (f809c69) | PR (010d1b0) | verdict
- NEW | lock-mismatch-refused | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS
- NEW | accept-current-revision-rewrites-lock | `init=0` / `exit=2 lock_is_rev=no logged=0` (argparse rejects the unknown option: the feature is absent, which is the right reason) | `init=0` / `exit=0 lock_is_rev=yes logged=1` | PASS
- REGRESSION (operator relabel) | accept-other-revision-refused | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` | same | PASS
- REGRESSION (operator relabel) | throwaway-store-ignores-lock | `init=0` / `exit=0 ticket=[T-0001.yaml]` | same | PASS
- NEW | dirty-harness-refused | `init=0` / `exit=0 tickets=1 names=0` | `init=0` / `exit=2 tickets=0 names=1` | PASS
- NEW | missing-lock-refused (the substituted command) | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS
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
- REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `92 passed in 73.34s` | `sync=0` / `116 passed in 78.16s (0:01:18)` (≥ 70, includes the new C tests, no failed/error) | PASS
- REGRESSION | green-harness-still-present | `green keeps its harness` | same | PASS
- REGRESSION | whitespace (sub-ticket diff), `git diff --check main...HEAD` | exit 0 (empty range) | no output, `exit=0` | PASS

The nine T-0012.3 scenarios above are the ones T-0012.3 lists as NEW in `intake/state/plans/T-0012.md`: harness-files-in-repo, role-prompt-text-unchanged and the seven factory-instance scenarios. I ran them in the clean worktree. Each one does a fresh `init` and none is refused.

The discriminating evidence behind the four relabelled REGRESSIONs:
- I committed the PR's `tests/factory/test_harness_lock.py` into the scratch base clone and ran it against base code: `18 failed, 6 passed in 5.88s`.
- At head the file passes as part of the 116.
- This matches the implementer's claim.

Tests to change: `git diff main...HEAD -- tests/factory/test_instance.py` is exactly the one ruled line, `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`, placed after `(alt / "context.md").write_text("x\n")`. No assertion changed. The diff touches no other existing test. In total it changes 4 files: `factory/cli.py`, `factory/instance.py`, the new `tests/factory/test_harness_lock.py` and `tests/factory/test_instance.py`.

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `116 passed in 79.41s (0:01:19)`, exit 0.

Probes: all against the PR harness, `REV=010d1b00c5835c7022a72771c63f63f8b6ab3707`. The script is in my scratchpad at `v77/probes.sh`.
- Own store named non-canonically, `FACTORY_STATE=$T/sub/../.factory/state/`, with a mismatched lock → `exit=2 tickets=0 hint=1`. It is still treated as the own store and refused. OK
- Own store reached through a symlink `FACTORY_STATE` → `exit=2 tickets=0 hint=1`. OK
- Lock holding the right rev with CRLF → exit 0. Without a trailing newline → exit 0. Stripped first line, as C.2 says. OK
- Lock holding the rev in uppercase → exit 2. The comparison is exact, which is consistent with C.2. OK
- `--accept-harness REV` from an unrelated cwd with `FACTORY_INSTANCE=$T/.factory` → `exit=0 lock_is_rev=yes tickets=1 stray=0`. It writes the named instance's lock and nothing in the cwd. OK
- `--accept-harness` placed after the subcommand → exit 2, lock unchanged (C.3: a global option, written before the subcommand). OK
- 40 non-hex characters as the SHA → `exit=2 lock=000…0 tickets=0`. OK
- Accepting when the lock already matches → exit 0, logged again (2 `harness.accepted` events in total for that instance). This is allowed by C.3. OK
- Dirty-harness variants, each in a fresh clone of the head:
  - a staged-only edit to `factory/__init__.py` → exit 2, path named;
  - `uv.lock` removed from the index → exit 2, path named;
  - `agents/factory-stub.md` deleted from the work tree → exit 2, and stderr is `harness <clone> has uncommitted changes:` / `agents/factory-stub.md`;
  - after restoring the file → exit 0. The fix is not special-cased to `factory/__init__.py`. OK
- Running the suite from a dirty harness: a fresh clone of head plus `# dev edit` appended to `factory/__init__.py` gives `23 failed, 93 passed` (17 in `test_harness_lock.py`, 6 in `test_instance.py`). This matches the implementer's disclosed gap. It does not break a stated criterion, because the suite criterion and the gate both run on a committed tree. It does conflict with a sentence in C.4's prose, so it is listed under ESCALATIONS. CONCERN (outside the criteria)

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance command verbatim (extracted by script, not retyped) on a clean head and on a fresh base clone. Every NEW criterion fails at base because the feature is missing and passes on the PR, and every REGRESSION passes on both. Both gates pass, and the probes show the guard is not special-cased to the tested inputs.
ESCALATIONS:
- The suite fails from a dirty dev checkout, against design C.4's prose. C.4 says a harness under development "still runs its own tests against throwaway stores", but 23 of the B/C tests drive this checkout's `bin/factory` against own-store targets, so any uncommitted edit under `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock` makes `pytest tests/factory` fail with the C.4 refusal. I reproduced this: `23 failed, 93 passed`. Committed-tree gates are unaffected. Fixing it is a test-design decision: the own-store tests would drive a clean clone, as the C.4 tests already do. That choice belongs to the operator or a later ticket, not to this sub-ticket.
- `--accept-harness` is silently ignored with `init`/`paths` and on a non-own store. The spec does not say what should happen there, and the implementer already disclosed it. It is a product decision whether to refuse it there instead.
