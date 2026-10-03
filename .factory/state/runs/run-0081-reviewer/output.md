Commit: 010d1b00c5835c7022a72771c63f63f8b6ab3707 (branch `factory/T-0012.4`; `main` = 68e8945, merge-base bed7e28; worktree `git status --porcelain` empty before and after my runs)

## What I checked, in order

1. **Test integrity.** One existing test file changed: `tests/factory/test_instance.py` (+1 line, `git diff main...HEAD -- tests/factory/test_instance.py`). The added line is byte-for-byte the operator's ruled line at the ruled position (after `(alt / "context.md").write_text("x\n")`, line 246). No assertion changed, nothing skipped or deleted, `config` not exempted. Listed under "Tests to change", so allowed. `tests/factory/test_harness_lock.py` is new. I re-ran it against base code myself: cloned the worktree at merge-base `bed7e28`, copied the file in, ran only that file → `18 failed, 6 passed in 8.65s`; the six passes are the "must not refuse" cases. Matches the PR description; the file is genuinely red before the guard.
2. **Correctness** (read `factory/instance.py` 1–169 and `factory/cli.py` `main()` 1043–1060 in full, plus `store.write_text`/`log_event`/`state_root`):
   - C.2: `guard()` runs for every command that reaches `a.fn(a, root, cfg)`; `init`/`paths` return through the pre-existing early branch (cli.py:1044–1046). `is_own_store` compares `root.resolve()` with `(repo_root/state_dir).resolve()`, so `FACTORY_STATE` naming the own store is still checked (test covers it). Message text matches the spec exactly, `none` for a missing/empty lock.
   - C.3: top-level argparse option (cli.py:897–899); 40-lowercase-hex and equal to the running revision, else refused with lock unchanged; on match writes `<rev>\n` and logs `harness.accepted {instance, old, new}` to the own store before the command runs.
   - C.4: `git -C <HARNESS> status --porcelain -- factory bin/factory agents pyproject.toml uv.lock` (instance.py:113), the sub-ticket's exact command; `ln[3:]` is correct for porcelain v1. Dirty check precedes the accept step, so `--accept-harness` cannot override it. A failing `git status` or unreadable revision refuses rather than falls through.
   - "Writes nothing": everything before `guard()` (`require`, `load_config`, `state_root`) only reads. Confirmed by the `tree(target) == before` assertions and my scenario runs below.
   - `store.load_config()` → `instance.load_config()` and `store.state_root()` → `instance.state_root()`, so swapping the first for the second in `main()` is behaviour-neutral.
3. **Scope.** Diff touches only `factory/cli.py`, `factory/instance.py`, the new test file and the ruled line. All within C.2–C.5. `010d1b0` only restores whitespace `fe6303c` broke on `PROTECTED_PLACEHOLDER`; the line is identical to `main`.
4. **Silent behaviour changes.** Two git subprocesses per store command on an own store (intended). `--accept-harness` is ignored where the guard does not apply (NIT below).
5. **Security/data safety.** Subprocess args are lists; the SHA is validated before use and appears only in messages; no secrets; no destructive ops; nothing under `~/.nanobot/` or `~/dev/nanobot-upstream/` read or written.
6. **Protected paths.** None of instance B's current classes (`intake/**`, `prompts/**`, reference harness, credentials) are touched. The `harness` class does not exist until E.
7. **Maintainability.** The local `from factory import store` inside `guard()` mirrors the existing lazy import on the store side; acceptable.

## Acceptance I re-ran (from the worktree after `uv sync --frozen`, env stripped of `FACTORY_*`)

| Scenario | Result |
|---|---|
| lock-mismatch-refused | `init=0` / `exit=2 tickets=0 hint=1` |
| missing-lock-refused | `init=0` / `exit=2 tickets=0 hint=1`; stderr `… accepted (none); rerun with --accept-harness 010d1b0… to accept it` |
| accept-current-revision-rewrites-lock | `init=0` / `exit=0 lock_is_rev=yes logged=1`; event `{"event": "harness.accepted", "old": "000…", "new": "010d1b0…"}` |
| accept-other-revision-refused | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` |
| throwaway-store-ignores-lock | `init=0` / `exit=0 ticket=[T-0001.yaml]` |
| dirty-harness-refused | `init=0` / `exit=2 tickets=0 names=1`; stderr `harness <clone> has uncommitted changes:` newline `factory/__init__.py` |
| init-and-paths-exempt | `paths=0 init=0 lock=0000000000000000000000000000000000000000` |
| accept-does-not-override-dirty | `exit=2 lock_same=yes tickets=0` |

Gate commands, from the worktree exactly as written:
- `git diff --check main...HEAD` → no output, `exit=0`.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 141.97s (0:02:21)`, exit 0 (slower than the implementer's 77s because my scenario runs and base-clone test ran concurrently; `uv` warned that an inherited `VIRTUAL_ENV` was ignored and used the worktree's `.venv`).

Reviewer probes beyond the listed scenarios:
- `--accept-harness <rev> config` when the lock already equals `<rev>` → exit 0 and one `harness.accepted` event with old == new. Spec-literal ("if it matches, the harness writes … and appends a log event"); fine.
- `--accept-harness deadbeef paths` → `exit=0`, lock untouched, stderr empty.
- `FACTORY_STATE=<elsewhere> --accept-harness deadbeef ticket new` → `exit=0`, ticket created in the throwaway store, lock untouched, stderr empty.
- A plain `config` on an own store with a matching lock → exit 0, zero bytes on stderr (no `git status` noise leaks).

## Findings

- [NIT] factory/instance.py:135–136 (with cli.py:1049): `--accept-harness SHA` is accepted and silently ignored whenever the guard does not apply — `init`, `paths`, or a store other than the instance's own. Observed: `--accept-harness deadbeef paths` → exit 0; `FACTORY_STATE=<tmp> --accept-harness deadbeef ticket new` → exit 0 with a ticket written. → An operator who runs `--accept-harness` with `FACTORY_STATE` exported, or who types it before `init`, gets a success exit and an unchanged lock, and discovers it on the next own-store command. The spec is silent here; the implementer flagged it. Not blocking; a later ticket could refuse or warn.

No BLOCKING or SHOULD-FIX findings.

Prior findings: none (round 1).

## Out-of-scope observations

- The B/C tests drive this checkout's `bin/factory` against own stores, so the suite passes only from a harness tree that is clean under the harness paths (the implementer's first known gap; I did not reproduce it, the worktree was clean). The sub-ticket says to run from a clean checkout "by design", so it is accepted here, but C.4's sentence "a harness under development … still runs its own tests against throwaway stores" is now only true of the imported suite. Spec/test-design question for a later ticket.
- Pre-existing from B, not this diff: a relative `--file` is resolved against the harness checkout, because `bin/factory` does `cd "$HERE"` and `cli.py:40` does `Path(a.file).expanduser().resolve()` without `instance.caller_cwd()`. Observed `no such file …/run-0081-reviewer/wt/r.md` for `ticket new --file r.md` run from a target repo. The parent's scenarios all pass absolute paths, so no acceptance item catches it.
- `factory/workflows/*.js` header comments do not mention `--accept-harness` or the upgrade step (also noted by the implementer).

STATUS: APPROVE
CONFIDENCE: high. Every C scenario and both gates reproduced on the head commit; the new tests are red at base (18/24) and green at head; the only existing-test change is the operator's ruled line.
ESCALATIONS: none
