Commit: 771ee0ec14ec755265f969c709ee3a4099d5160d (branch `factory/T-0022.1`, worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0280-verifier/wt`, clean tree before and after every run)

How it ran: each WHEN command was copied byte for byte from the sub-ticket into its own file in `scratch/`, the parent's GIVEN block was run once, and `scratch/tmp/t0022-sib.sh` was checked with `diff` to match the spec's text. Every command ran in zsh through the fresh-HOME wrapper with `TMPDIR=scratch/tmp`. The PR ran from the worktree after `uv sync --frozen`. The base ran from a clone of this repo at `c2750bf9c` (`scratch/base`), also after `uv sync --frozen`. `main` is `c2750bf9`, the same commit as the given base. The three build-dispatch scenarios were also run in bash on the PR, with the same output.

Per criterion:
- REGRESSION | merged sibling's file accepted, Scope mention ignored (`E=tests/test_interim.py … run start …`) | base: not run | PR `exit=0 ready-for-implementer runs=1` | PASS
- NEW | predates plan / no sibling / never added (`for E in tests/test_old.py …`) | base: three lines of `exit=0 blocked=0 names=0 runs=1 branch=1 ready-for-implementer` | PR: three lines of `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer` | PASS
- NEW | build parks with harness reason, ruling returns it (`node …t0022-build.mjs` then `resolve --ruling`) | base `park T-0001.2: budget kill: implementer` / `ruling=2 parked` | PR `park T-0001.2: BLOCKED from harness:` / `ruling=0 ready-for-implementer` | PASS
- NEW | every planner copy | base: three lines of `own=0 sibling=0 interim=0 copied=1`, then `verbatim` | PR: three lines of `own=1 sibling=1 interim=1 copied=0`, then `verbatim` | PASS
- NEW | spec writer and critic copies | base `writer=0 critic=0` on all three lines | PR `design: writer=1 critic=1` / `docs/prompts: writer=1 critic=1` / `factory/prompts: writer=1 critic=1` | PASS
- NEW | preamble and reviewer copies | base `guard=0 review=0` on all three lines | PR `design: guard=1 review=1` / `docs/prompts: guard=1 review=1` / `factory/prompts: guard=1 review=1` | PASS
- NEW | system prompts of planner, spec writer and critic runs | base `planner own=0 sibling=0 guard=0 writer=0 critic=0` | PR `planner own=1 sibling=1 guard=1 writer=1 critic=1` | PASS
- NEW | design doc and build spec | base `piece8=0 gate=0 stale=1 check=0 build=0` | PR `piece8=1 gate=1 stale=0 check=1 build=1` | PASS
- NEW | changelog | base `CONTIGUOUS` / `0` | PR `CONTIGUOUS` / `5` | PASS
- NEW | README | base `built=0 ruling=0` | PR `built=1 ruling=1` | PASS
- REGRESSION | `(git diff --check main...HEAD; echo "exit=$?")` | base: not run | PR `exit=0` | PASS
- NEW (new test file's cases) | `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_sibling_tests.py -rA`, TMPDIR under `/tmp` | base: not run (the file does not exist on base) | PR `10 passed`. It includes the build-dispatch cases, the unmerged-sibling refusal, the re-add-counts-by-first-add case and the T-0002.6-style Parallel-safe mention | PASS

On base, every NEW command printed exactly the failing output that `verification.md` gives, for the reason it states.

Gate suite: PASS
  `(export HOME=…; git diff --check main...HEAD)` → exit 0, no output.
  `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` → `310 passed in 331.71s`, rc=0 (`scratch/gate2.txt`).
  The same with `TMPDIR=/tmp/t0022-verif.weRls2`, as the sub-ticket asks for the parent's gate → `310 passed`, rc=0 (`scratch/gate2-tmp.txt`). The two runs were concurrent, which explains their identical wall time.

Probes (each through a copy of the spec's fixture with only the plan text changed, `scratch/probe-sib.sh`):
- `Tests to change:` written inline on one line with `tests/test_old.py` (added by ST-1) → exit 2, `BLOCKED from harness: … tests/test_old.py …`, runs=0 → OK
- Inline one-line entry for `tests/test_interim.py` → exit 0, run started → OK
- `Tests to change: none`, then the same entry form for `tests/test_old.py` in an `Interim tests:` line and for `tests/test_never.py` in an `Out of scope:` line → exit 0; the field ends at the next plan field → OK
- `./tests/test_interim.py` (leading `./`) → exit 0, an equivalent path accepted → OK
- Two entries, one good (`test_interim.py`) and one predating the plan (`tests/test_old.py::test_old`) → exit 2, names `tests/test_old.py` → OK. The check is not special-cased to one entry.
- An entry with no space before `(added by`, followed by a directory entry `tests/` → exit 2, names `tests/` (the directory existed at base) → OK
- A path holding shell syntax, `` `tests/$(touch${IFS}<scratch>/tmp/pwned).py` (added by ST-1) ``, run through the spec's build driver → run start refuses correctly, but the park's clerk command ran the `$(…)` and created `scratch/tmp/pwned`. The stored park reason reads `tests/.py`, not the error verbatim → CONCERN (outside this sub-ticket's criteria; see ESCALATIONS)

Spec deviations I checked and accept:
- `is_ancestor` (B.2) was not added. `gitops.head_contains(repo, head, base)` runs the same `git merge-base --is-ancestor` (`factory/gitops.py:80`).
- Sibling merge records are also required to have `base_before`. `merge_cmd` always writes both fields (`factory/cli.py:582`), so this only tightens the check.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command printed its THEN on 771ee0e, and every NEW one printed the stated failing output on c2750bf. Both gate runs passed. Probes near the tested inputs behaved as the spec describes, except the shell-quoting concern, which is outside the criteria.
ESCALATIONS:
- Planner-written path text reaches a shell when the build parks. A sub-ticket's "Tests to change" entry can hold `$(…)`, because `SIBLING_TEST_RE` only excludes backticks and whitespace. The refusal names that path. `park()` in `factory/workflows/build.js` puts the reason in a double-quoted `sh -c` string and escapes only `"`. So the clerk's shell runs the substitution. I reproduced it: a `touch` inside the entry created a file in this run's scratch directory, and the stored reason lost the path. This is planner-controlled text, and the implementer named it under Known gaps. It is not covered by any acceptance criterion. A human should decide whether to fix `park()` quoting, or restrict the path pattern, before this merges or in a follow-up.
