Commit: be292addbee09d9b2709fd84b54e63de8e9f6477 (branch `factory/T-0012.4`; `main` = `6921dfd8` and `git merge-base --is-ancestor main HEAD` succeeds; harness revision `git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock` = `010d1b00c5835c7022a72771c63f63f8b6ab3707`; worktree `git status --porcelain` empty before and after my runs)

## Round

This is the third review of the same code diff. Reviewer run-0081 approved `010d1b0` and run-0087 approved `a5f1329`, each with two NITs. The only new commit since then is the merge `be292ad` (conflict run-0088). Per the convergence rule I checked the prior findings and the changed lines, and re-ran the gates and the C scenarios on this head because the merge changed the tree the tests run against.

## What I checked, in the role's order

1. **Test integrity.** `git diff --stat main...HEAD` touches four files: `factory/cli.py` (+6/-1), `factory/instance.py` (+52), `tests/factory/test_harness_lock.py` (new, +281), `tests/factory/test_instance.py` (+1). The one existing-test change is `tests/factory/test_instance.py:246`, the single line `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`, placed after `(alt / "context.md").write_text("x\n")` exactly as the sub-ticket's "Tests to change" rules. No assertion changed, no skip/xfail, `config` is still guarded (the test runs `config` with `FACTORY_INSTANCE=alt` and now passes because the lock is present, not because the guard is skipped). New tests are in a new file.
2. **What the merge brought.** `git diff --stat a5f1329 be292ad` → `dev/build-harness.spec.md`, `docs/changelog.md`, `docs/design.md` (7 insertions, 6 deletions). None is a harness path; the harness revision is unchanged at `010d1b0`, so the lock value E will write is unaffected by this merge.
3. **Correctness against C.2–C.5** (read `factory/instance.py:106-154` and `factory/cli.py:1043-1052` in full):
   - C.2: `guard()` returns unless `is_own_store()` (store root equals `repo_root/state_dir` resolved, which is `FACTORY_STATE` unset or naming the own store). `read_lock()` takes the stripped first line, `None` when missing or empty. Mismatch message is the spec's string with `none` for a missing lock. `init`/`paths` return on the existing early branch at `cli.py:1044-1046` before `guard` is reached.
   - C.3: `--accept-harness` is a top-level argparse option (`cli.py:897-899`). Accept requires `[0-9a-f]{40}` fullmatch and equality with the running revision; otherwise `Refused` with the lock untouched. On match it writes `<rev>\n` and appends `harness.accepted` with `old`/`new` to the own store's log before the command runs.
   - C.4: `harness_changes()` runs exactly `git -C <running harness> status --porcelain -- factory bin/factory agents pyproject.toml uv.lock`; it runs before the accept step so `--accept-harness` cannot override it. Git failure or an unreadable revision also refuses (exit 2) rather than falling through.
   - All refusals are `Refused` raised before `a.fn(a, root, cfg)`, so nothing is written. The one write on the accept path (lock + log) is what C.3 specifies.
4. **Scope.** Only C.2–C.5 plus the ruled test line. `cli.py` swaps `store.load_config()` for `instance.require()` + `instance.load_config(inst)`; `store.load_config` (`store.py:29-32`) is a thin wrapper over the same call, so behaviour is identical and the instance handle is needed for `guard`.
5. **Silent behaviour changes.** The intended one: every own-store command now checks the lock and the dirty state. Verified exempt: `init`, `paths`, and any `FACTORY_STATE` store elsewhere.
6. **Security / data safety.** Subprocess calls use argv lists, no shell. The lock write is to `<instance>/harness.lock` only. No secrets, no destructive ops.
7. **Protected paths.** The sub-ticket declares none of instance B's current classes; the diff touches none (`intake/**`, `prompts/**`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**` all untouched).

## Gates, run from the worktree with no `FACTORY_*` set

- `git diff --check main...HEAD` → no output, `exit=0`.
- `uv sync --frozen` → `sync=0`; `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 145.81s (0:02:25)`. (116 = 92 at T-0012.3 + 24 new cases; no `failed`/`error`.)

## Acceptance scenarios re-run on `be292ad`, commands copied from the input

| Scenario | Observed |
|---|---|
| lock-mismatch-refused | `init=0` / `exit=2 tickets=0 hint=1` |
| missing-lock-refused (`rm -f` substitution) | `init=0` / `exit=2 tickets=0 hint=1`; stderr `harness 010d1b00… is not the revision this instance accepted (none); rerun with --accept-harness 010d1b00… to accept it` |
| accept-current-revision-rewrites-lock | `init=0` / `exit=0 lock_is_rev=yes logged=1` |
| accept-other-revision-refused | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` |
| throwaway-store-ignores-lock | `init=0` / `exit=0 ticket=[T-0001.yaml]` |
| init-and-paths-exempt | `paths=0 init=0 lock=0000000000000000000000000000000000000000` |
| dirty-harness-refused | `init=0` / `exit=2 tickets=0 names=1`; stderr `harness <clone> has uncommitted changes:` / `factory/__init__.py` |
| accept-does-not-override-dirty | `exit=2 lock_same=yes tickets=0` |
| green-harness-still-present | `green keeps its harness` |

Each matches its THEN. The dirty-harness scenarios ran in fresh clones, so the worktree was never edited (`git status --porcelain` empty afterwards).

## Findings

None new. The two prior NITs stand as noted, not as change requests:

- [NIT] `factory/instance.py:135-136`: `--accept-harness` is silently ignored when the guard does not apply (`init`, `paths`, or a non-own store) → an operator who runs the accept step with `FACTORY_STATE` exported gets exit 0 and an unchanged lock. Spec is silent; a later ticket.
- [NIT] `tests/factory/test_harness_lock.py` own-store cases (and six in `test_instance.py`) fail under C.4 from a dirty dev checkout → the suite needs a committed harness tree locally; the gate runs on committed branches. The sub-ticket accepts this by design.

Prior findings: UNRESOLVED (both NITs; neither was a change request, and the code diff is byte-identical to what run-0081 and run-0087 approved, so no resolution was expected).

## Out-of-scope observations

- The `factory/workflows/*.js` header comments still do not mention `--accept-harness` or the upgrade step (noted by the implementer and both prior reviewers).
- Per the shared plan, T-0012.6 (E) must write `.factory/harness.lock` = `010d1b00c5835c7022a72771c63f63f8b6ab3707` or whatever the harness revision is at E's base; this merge did not move it.

STATUS: APPROVE
CONFIDENCE: high. The code diff is unchanged from two prior approvals; I re-ran both gates (`exit=0`, `116 passed`) and nine acceptance scenarios on this exact head, read the full guard and the changed `main()`, and confirmed the only existing-test change is the operator's ruled line.
ESCALATIONS: none
