Commit: 637e6deaf99ece302297c25b7546e90c7b9f6971 (verified in worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0103-verifier/wt`, detached; `git rev-parse main HEAD` gives 637e6de for both, so this is main at parent close)
Base: cdb1c6769ecc39208e62edc65578f62f5a23908f (fresh `git clone --no-local` of the repo into a scratch directory, detached at the base). `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f` exported for the scenarios that take it.

Method: I saved each WHEN command verbatim to its own file and ran it with `bash` from the checkout root, once on the head and once on the base. Green (`~/dev/nanobot-upstream`) was read only, through `git log`, `git show` and `git cat-file`.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | harness-files-in-repo | ten `missing …` lines, then `agents=0 green_only=0` | `agents=6 green_only=0` | PASS
- NEW | harness-history-carried | `24` | `0` | PASS
- NEW | harness-suite-passes-after-uv-sync | `sync=2`, `no tests ran in 0.00s` | `sync=0`, `116 passed in 128.85s (0:02:08)` | PASS
- NEW | role-prompt-text-unchanged | `changed=14 of 14` | `changed=0 of 14` | PASS
- NEW | init-creates-instance-in-throwaway-target | `init=127`, `instance=[] agents=0 restart=0` | `init=0`, `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` | PASS
- NEW | store-command-from-subdirectory-uses-target-instance | `init=127`, `new=127 tickets=[] harness_changes=0` | `init=0`, `new=0 tickets=[T-0001.yaml] harness_changes=0` | PASS
- NEW | command-outside-any-instance-refused | `exit=127 created=0 names_instance=0` | `exit=2 created=0 names_instance=1` | PASS
- NEW | factory-instance-override-from-elsewhere | `init=127`, `found=0` | `init=0`, `found=1` | PASS
- NEW | composed-input-opens-with-instance-context | `init=127`, `first=[]` | `init=0`, `first=[CTX-MARKER for demo]` | PASS
- NEW | run-system-prompt-names-instance | `init=127`, `line1=[] placeholders= protects_instance=` | `init=0`, `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` | PASS
- NEW | paths-name-harness-workflows-and-instance | `init=127`, `no paths` | `init=0`, `True True True True` | PASS
- NEW | lock-mismatch-refused | `init=127`, `exit=127 tickets=0 hint=0` | `init=0`, `exit=2 tickets=0 hint=1` | PASS
- NEW | accept-current-revision-rewrites-lock | `init=127`, `exit=127 lock_is_rev=no logged=0` | `init=0`, `exit=0 lock_is_rev=yes logged=1` | PASS
- NEW | accept-other-revision-refused | `init=127`, `exit=127 lock= tickets=0` | `init=0`, `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` | PASS
- NEW | throwaway-store-ignores-lock | `init=127`, `exit=127 ticket=[]` | `init=0`, `exit=0 ticket=[T-0001.yaml]` | PASS
- NEW | dirty-harness-refused | `init=127`, `exit=127 tickets=0 names=0` (stderr also shows uv's `No pyproject.toml found` and a missing `factory/__init__.py`, as verification.md predicted) | `init=0`, `exit=2 tickets=0 names=1` | PASS
- NEW | docs-moved-and-split | seven `missing …` lines, then `old_tracked=15` | `old_tracked=0` | PASS
- NEW | changelog-moved-verbatim | `DIFFERENT`, `declined= numbering=NONE in_design=` | `SAME`, `declined=1 numbering=CONTIGUOUS in_design=0` | PASS
- NEW | design-text-kept | `570` | `0` | PASS
- NEW | prompt-copies-moved-unchanged | `changed=10 of 10 DRIFT` | `changed=0 of 10 VERBATIM` | PASS
- NEW | no-old-paths-in-live-files | `exit=0` | `exit=1` | PASS
- NEW | readme-has-install-and-layout | seven `missing: …` lines, then `checked` | `checked` | PASS
- NEW | design-doc-instance-text | `kept=0 open= piece8=0 logged=0` | `kept=1 open=0 piece8=1 logged=1` | PASS
- NEW | build-spec-render-paths | `stale=0 new= d8=0` (the `stale=0` means nothing here: no file was read) | `stale=0 new=3 d8=1` | PASS
- NEW | intake-holds-only-live-store | `left=168` | `left=0` | PASS
- NEW | pilot-store-and-answers-kept-byte-identical | `kept=0 of 135` | `kept=135 of 135` | PASS. The spec's literal text is `134 of 134`, but its criterion is "both numbers equal". The count is 135 because the base (cdb1c67) is later than the spec's "today" (f082708). `git diff --name-status f082708 cdb1c67 -- intake ':(exclude)intake/state'` shows one added file, `A intake/answers/T-0012-gate-edit.md`, and `git ls-tree -r f082708 -- intake/green-pilot intake/answers | awk '{print $3}' | sort -u | wc -l` gives 134. The same file explains `left=168` on the base, against 167 in verification.md.
- NEW | instance-b-opens-every-ticket | `tickets=0 failed=0` | `tickets=18 failed=0` (needs N ≥ 12) | PASS. `.factory/harness.lock` = `010d1b00c5835c7022a72771c63f63f8b6ab3707`, which equals `git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock` at the head, so instance B passes its own lock.
- NEW | instance-b-config | `no instance config`, `context=` | `True True True`, `context=3` | PASS
- REGRESSION | green-harness-still-present | `green keeps its harness` | `green keeps its harness` | PASS
- REGRESSION | whitespace-clean (operator-amended range, excludes `intake/state` and `.factory/state`) | `exit=0` | `exit=0` | PASS

Every NEW criterion fails on the base for the reason the spec gives (`bin/factory`, the files or the moved paths are absent) and passes on the head. Both REGRESSION criteria pass on both.

Gate suite: PASS
- `git diff --check main...HEAD` printed nothing and exited 0. It checks nothing here: at parent close `main` is HEAD, so the range is empty. Over the whole parent, whitespace is covered by whitespace-clean above.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` exited 0 with `116 passed in 84.20s (0:01:24)`. A second run also gave `116 passed`.
- After all the runs, `git status --porcelain` in the worktree prints 0 lines.

Probes (all on throwaway targets with the head's `bin/factory`, plus scratch clones of the head for the dirty-harness cases):
- `factory paths` from a directory with no instance → `"instance": null, "state": null`, exit 0, nothing created → OK
- `init --repo-name x` outside a git work tree → exit 2 (`… is not inside a git work tree`), nothing created → OK
- `init` with no `--repo-name` and no instance → exit 2 (`… instance.yaml does not exist; pass --repo-name NAME`), nothing created → OK
- `init` run again bare, then again with `--repo-name other` → both exit 0. The md5 of all 14 files under `.factory` and `.claude` is unchanged, `repo_name` stays `"demo"`, and the output shows `"written": []` → OK
- `init` after deleting one agent file → only that file is restored (6 agents) and the restart hint is printed once → OK
- Walk-up from `$T/a/b/c/d/e`, where `$T/a/b/c/.factory/` exists with no `instance.yaml` → it skips that directory, finds `$T/.factory`, and writes the ticket there; the empty `.factory` stays empty → OK
- Lock mismatch with `FACTORY_STATE` set to the instance's own store spelled `$T/.factory/state/` (trailing slash), or reached through a symlink → exit 2 with the accept-harness hint; the lock is still checked → OK
- Lock missing → exit 2, `(none)` in the message. Lock holding the revision with no trailing newline → exit 0 → OK
- `--accept-harness` with the first 7 characters of the revision, or the full revision in upper case → exit 2, lock unchanged → OK
- An instance with two `protected_paths` classes → system-prompt line 38 is `  infra (.factory/**, intake/**), credentials (~/.nanobot/**)` with no placeholder left (B.4 format). The fill is not tied to the tested values → OK
- Dirty runtime: a new untracked `factory/new_untracked.py` → refused, exit 2, path named. With `--accept-harness <rev>` as well → still refused (C.4). An edit to `agents/factory-stub.md` → refused, path named. A `__pycache__` left by `uv sync` and imports is not counted. An edit to `README.md` only → runs (exit 0). A dirty runtime with a throwaway `FACTORY_STATE` → runs (exit 0) → OK
- `FACTORY_STATE` given as a relative path (`../.factory/state`, from `$T/a`, meaning the instance's own store) → exit 0 and no lock check. The store was created relative to the harness checkout, not the caller's directory: it landed at `/Users/dphang/dev/spec-factory/intake/state/runs/run-0103-verifier/.factory/state/`. Cause: `bin/factory` runs `cd "$HERE"`, and `factory/store.py:40` / `factory/instance.py` resolve `FACTORY_STATE`, `FACTORY_INSTANCE` and `FACTORY_REPO` with `Path(env).expanduser().resolve()` against the process cwd. Only the walk-up uses `FACTORY_CWD`. → CONCERN. No criterion covers relative overrides, and every workflow and test passes absolute paths, so this is not a FAIL; it is escalated below.

STATUS: VERIFIED
CONFIDENCE: high. All 30 scenarios and both gate commands ran as written on the head and on the base with the outputs above, and the probes found no special-casing to the tested inputs.
ESCALATIONS:
- My relative-`FACTORY_STATE` probe left an untracked directory, `/Users/dphang/dev/spec-factory/intake/state/runs/run-0103-verifier/.factory/` (a throwaway store holding T-0001). The harness created it there because of the concern above. My attempt to delete it was denied by the permission system, so the operator should remove it. It is untracked and not part of the verified commit.
- A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` resolves against the harness checkout, not the caller's working directory. As a result, a relative `FACTORY_STATE` meant to name the instance's own store skips the lock and modified-harness checks (C.2/C.4) and writes a store under or beside the harness checkout. `FACTORY_STATE` had the same relative-path behaviour before this change, but the lock now gives it a safety cost. The fix would be to resolve these against `FACTORY_CWD`, as the walk-up does. That needs a follow-up ticket and is not part of this parent's criteria.
- The spec's literal counts drifted because the base (cdb1c67) is later than "today" (f082708). pilot-store-and-answers-kept-byte-identical gives `kept=135 of 135`, not 134, and the base's `left` is 168, not 167. Both differences come from the added `intake/answers/T-0012-gate-edit.md`. The criterion's intent ("both numbers equal") holds.
- The gate command `git diff --check main...HEAD` is empty at parent close (main = HEAD), so the parent's whitespace evidence rests on the amended whitespace-clean scenario, which excludes the stores.
