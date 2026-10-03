Commit: 70c32abf41484b631a157641649492ad6b271b76

What it means: the harness move, the instances, the lock and the document re-layout all work on main. Every NEW scenario fails on base and passes on main. The gate suite passes. The one miss is the REGRESSION scenario whitespace-clean. It prints `exit=2` on main because of run records that the harness itself committed to the live store (`intake/state/runs/*/diff.patch` and `input.md`). None of the six sub-tickets' changes cause it. The same range with `intake/state` excluded exits 0. The scenario as written can't be met without rewriting records, which the spec forbids, or adding a change no sub-ticket owns. So this is reported as SPEC-DEFECT, and the operator needs to make a call (see ESCALATIONS).

Method: the head is the given worktree `wt` (detached at 70c32ab; `git -C ~/dev/spec-factory rev-parse main` = 70c32ab, so this is a parent-close run on main). The base is a fresh `git clone` of the repo in my scratchpad, detached at cdb1c6769ecc39208e62edc65578f62f5a23908f. That is the first parent of the first T-0012 merge, 02e8c8d, and its local `main` was set to the same SHA. I extracted the 30 WHEN commands byte-for-byte from input.md with a script, ran each one in a fresh `bash` from the checkout root with `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, and ran them in spec order on both trees. On main, the venv came from the scenario's own `uv sync --frozen`; there was no `.venv` beforehand.

## Per criterion

| # | Criterion | Type | Base (cdb1c67) | PR / main (70c32ab) | Result |
|---|---|---|---|---|---|
| 1 | harness-files-in-repo | NEW | 10 `missing …` + `agents=0 green_only=0` | `agents=6 green_only=0` | PASS |
| 2 | harness-history-carried | NEW | `24` | `0` | PASS |
| 3 | harness-suite-passes-after-uv-sync | NEW | `sync=2` / `no tests ran in 0.00s` | `sync=0` / `116 passed in 127.65s` | PASS |
| 4 | role-prompt-text-unchanged | NEW | `changed=14 of 14` | `changed=0 of 14` | PASS |
| 5 | init-creates-instance-in-throwaway-target | NEW | `init=127` / `instance=[] agents=0 restart=0` | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` | PASS |
| 6 | store-command-from-subdirectory-uses-target-instance | NEW | `init=127` / `new=127 tickets=[] harness_changes=0` | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` | PASS |
| 7 | command-outside-any-instance-refused | NEW | `exit=127 created=0 names_instance=0` | `exit=2 created=0 names_instance=1` | PASS |
| 8 | factory-instance-override-from-elsewhere | NEW | `init=127` / `found=0` | `init=0` / `found=1` | PASS |
| 9 | composed-input-opens-with-instance-context | NEW | `init=127` / `first=[]` | `init=0` / `first=[CTX-MARKER for demo]` | PASS |
| 10 | run-system-prompt-names-instance | NEW | `init=127` / `line1=[] placeholders= protects_instance=` | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` | PASS |
| 11 | paths-name-harness-workflows-and-instance | NEW | `init=127` / `no paths` | `init=0` / `True True True True` | PASS |
| 12 | lock-mismatch-refused | NEW | `init=127` / `exit=127 tickets=0 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS |
| 13 | accept-current-revision-rewrites-lock | NEW | `init=127` / `exit=127 lock_is_rev=no logged=0` | `init=0` / `exit=0 lock_is_rev=yes logged=1` | PASS |
| 14 | accept-other-revision-refused | NEW | `init=127` / `exit=127 lock= tickets=0` | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` | PASS |
| 15 | throwaway-store-ignores-lock | NEW | `init=127` / `exit=127 ticket=[]` | `init=0` / `exit=0 ticket=[T-0001.yaml]` | PASS |
| 16 | dirty-harness-refused | NEW | `uv` error (no pyproject.toml), `init=127` / `exit=127 tickets=0 names=0` | `init=0` / `exit=2 tickets=0 names=1` | PASS |
| 17 | docs-moved-and-split | NEW | 7 `missing …` + `old_tracked=15` | `old_tracked=0` | PASS |
| 18 | changelog-moved-verbatim | NEW | `DIFFERENT` / `declined= numbering=NONE in_design=` | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | PASS |
| 19 | design-text-kept | NEW | `570` | `0` | PASS |
| 20 | prompt-copies-moved-unchanged | NEW | `changed=10 of 10 DRIFT` | `changed=0 of 10 VERBATIM` | PASS |
| 21 | no-old-paths-in-live-files | NEW | `exit=0` | `exit=1` | PASS |
| 22 | readme-has-install-and-layout | NEW | 7 `missing: …` + `checked` | `checked` | PASS |
| 23 | design-doc-instance-text | NEW | `kept=0 open= piece8=0 logged=0` | `kept=1 open=0 piece8=1 logged=1` | PASS |
| 24 | build-spec-render-paths | NEW | `stale=0 new= d8=0` | `stale=0 new=3 d8=1` | PASS |
| 25 | intake-holds-only-live-store | NEW | `left=168` | `left=0` | PASS |
| 26 | pilot-store-and-answers-kept-byte-identical | NEW | `kept=0 of 135` | `kept=135 of 135` | PASS |
| 27 | instance-b-opens-every-ticket | NEW | `tickets=0 failed=0` | `tickets=18 failed=0` | PASS |
| 28 | instance-b-config | NEW | `no instance config` / `context=` | `True True True` / `context=3` | PASS |
| 29 | green-harness-still-present | REGRESSION | `green keeps its harness` | `green keeps its harness` | PASS |
| 30 | whitespace-clean | REGRESSION | `exit=0` | about 70 KB of `trailing whitespace.` reports, then `exit=2` | SPEC-DEFECT (see below) |

Notes on the counts:
- #25 and #26 differ from verification.md's "today" figures (167 and 134). verification.md measured at f082708. The pinned base cdb1c67 has one more tracked file under `intake/answers/`. #26 only requires the two numbers to be equal.
- #27's 18 tickets are T-0001 to T-0012 plus T-0012.1 to T-0012.6, which meets N ≥ 12.
- #13 matches `N ≥ 1`. #24 matches `N ≥ 3`. #28 matches `N ≥ 2`.

### whitespace-clean: why it is a SPEC-DEFECT and not a FAILED
- Every reported path is a store run record under `intake/state/runs/run-00{57..93}-*/` (`diff.patch` and `input.md` of reviewer, verifier and implementer runs). They embed verbatim diffs. A diff's blank context line is a single space, and `git diff --check` flags that as trailing whitespace. Example: `sed -n l intake/state/runs/run-0057-verifier/diff.patch` shows ` $` lines.
- Outside the store the range is clean: `git diff --check cdb1c67 HEAD -- . ':(exclude)intake/state'` gives exit 0. `-- intake/state/tickets intake/state/log` also gives exit 0.
- Per first-parent commit on main, `git diff --check $c^1 $c`:
  - All six `Merge factory/T-0012.N` commits: exit 0.
  - The four harness store commits: exit 2. These are 20849b6, f809c69, e725a5c and 600b8d4 ("intake(T-0012): …").
  - 68e8945: exit 0.
- At base, the store had no such records: `git diff --check <empty tree> cdb1c67 -- intake/state` prints nothing. This is the first parent whose build half ran in this repo.
- The spec says these records are not changed by the PRs and are never rewritten (Risk, "Protected paths touched"; Out of scope, "Rewriting records"). So the command measures harness-written records, not "the parent's combined change" that the requirement targets. No correct implementation of the six parts could make it print `exit=0`. verification.md expected `exit=0` only because the range was empty at intake.

## Gate suite: PASS
Run from `wt` exactly as written:
- `git diff --check main...HEAD`: exit 0, no output. The range is empty because main = HEAD.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `116 passed in 87.70s (0:01:27)`, exit 0. The earlier pipe-free run inside scenario 3 gave `116 passed in 127.65s`.
- Afterwards, `git status --porcelain` in `wt` was empty.

## Probes
Each probe uses `wt/bin/factory` against a throwaway git target in `mktemp -d` unless stated.
- `init` with no `--repo-name` in a target with no instance → exit 2, nothing under `.factory/`, stderr `… instance.yaml does not exist; pass --repo-name NAME to create it` → OK
- `init --repo-name x` outside any git work tree → exit 2, nothing created, stderr `… is not inside a git work tree` → OK
- `init` run again on an existing instance with an edited `context.md` → exit 0, `instance.yaml` byte-identical, the edit kept, no restart notice (no agent file written) → OK
- `init` after `harness.lock` was deleted → exit 0, the lock is recreated with the current revision 010d1b0… → OK (B.5 "creates only what is missing")
- `harness.lock` = `<rev>  \r\n` plus a second line → `ticket new` exit 0 (stripped first line compared) → OK
- Empty `harness.lock`, and a missing lock, each checked on a read-only command (`ticket show`) → exit 2, `… accepted (none); rerun with --accept-harness <rev> …`, no lock created → OK (C.2 applies to every command, not just writes)
- `--accept-harness` with the right SHA in UPPERCASE → exit 2, lock unchanged (still none), message names the running revision. The exact lowercase SHA → exit 0 and the lock is rewritten → OK
- `paths` from a directory with no instance → `instance` and `state` are `null`, `harness_revision` has 40 characters, no refusal → OK
- `FACTORY_INSTANCE=<proj>/conf`, a directory not named `.factory`, run from an unrelated cwd → ticket written to `<proj>/.factory/state/tickets/T-0001.yaml`: the repo root is the parent of the instance directory, and the copied template's `state_dir: .factory/state` is relative to it → OK (B.2)
- Nested git repo with its own instance inside an outer instance, command run from `inner/deep` → the ticket goes to the inner store only (inner=1, outer unchanged) → OK
- Throwaway target given instance B's `protected_paths`, then `run start --role triage` → line 37 of `system-prompt.txt` is `  infra (.factory/**, intake/**), harness (factory/**, bin/factory, agents/**, pyproject.toml, uv.lock), generated (docs/prompts/**), reference_harness (~/dev/nanobot-upstream/**), credentials (~/.nanobot/**)`; `placeholders=0`. A diff against `factory/prompts/preamble.md` + `triage.md` differs only on that line, plus one blank separator line → OK (B.4, multi-class and multi-glob, not special-cased to the one-class `init` template)
- Dirty-harness variants on a fresh clone of `wt` with `uv sync`:
  - An ignored `factory/__pycache__/zz.pyc` → not refused (exit 0).
  - An untracked `agents/new.md` → exit 2, `has uncommitted changes:` then `agents/new.md`.
  - The same dirty clone with `FACTORY_STATE` set to a throwaway store → exit 0, ticket written.
  - The same dirty clone with `--accept-harness <rev>` → still exit 2.
  - An untracked `docs/scratch.md`, outside the harness paths → exit 0.
  → OK (C.4 covers untracked files, respects `.gitignore`, is scoped to the instance's own store, and `--accept-harness` does not override it)
- Instance B, run from the subdirectory `wt/docs/prompts`: `ticket show T-0012` → exit 0. `paths` → instance `…/wt/.factory`, state `…/wt/intake/state` → OK
- E.3: `wt/.factory/harness.lock` = `010d1b00c5835c7022a72771c63f63f8b6ab3707`, which equals `git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock` at HEAD. No harness-path commit landed after the lock was written → OK

## Out-of-scope observations
- Every future parent in this repo will hit the whitespace-clean problem for as long as the store is tracked on main. The checkers' run records always embed diffs with ` ` context lines. After the post-close move the paths become `.factory/state/runs/…`.
- `~/dev/spec-factory-harness`, which `.factory/instance.yaml` names as `harness:`, does not exist yet. That is expected: operator step 2 creates it. Until then, instance B commands have to run through a checkout's own `bin/factory`.
- Footprint of this run, all outside tracked content:
  - `.venv/` and `__pycache__/` in `wt` (gitignored).
  - A briefly created and then removed/pruned worktree registration on `~/dev/spec-factory`, done before I switched the base to a scratch clone.
  - One loose empty-tree object (`4b825dc…`) written to the shared object store by `git hash-object -w`.
  - Nothing was written in `~/dev/nanobot-upstream`. `~/.nanobot` was not touched.

STATUS: SPEC-DEFECT
CONFIDENCE: high. All 30 commands ran verbatim on both trees and every result is quoted above. The single non-pass is traced to its exact files and commits, and the same range with the store excluded is clean.
ESCALATIONS:
- whitespace-clean (REGRESSION) prints `exit=2` on main. Every error comes from harness-written store records committed on main by 20849b6, f809c69, e725a5c and 600b8d4, which the spec says must not be rewritten. Operator decision needed:
  - (a) re-scope the scenario to the parent's own change, e.g. `git diff --check "$BASE" HEAD -- . ':(exclude)intake/state'`, which gives exit 0 today; or
  - (b) declare store records whitespace-exempt in the harness or the store, e.g. a `.gitattributes` `-whitespace` rule. That is an infra and harness-path change outside this parent's sub-tickets.
  Every other criterion is satisfied, so after (a) this parent would verify as-is.
