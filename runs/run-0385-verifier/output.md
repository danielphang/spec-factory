Commit: 49cc429424c1eb02708268bf4ecb0f251bfe8ae7 (branch `factory/T-0027.3`, base 8dfc64b61f9d927e9f82fa9704f382cffefa60cf, which is also `main`)

How I ran it. I ran every command from the worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0385-verifier/wt` (PR) and from a `git archive` copy of base 8dfc64b in `scratch/base`, after `uv sync --frozen` in each. Each command ran through the fresh-HOME wrapper, with `TMPDIR` set to `scratch/tmp`. I copied the GIVEN blocks out of the documents with awk: the `t0027-amend.sh` block from `specs/T-0027/v3.md`, and the `t0022-sib.sh` and `t0022-build.mjs` blocks from `openspec/specs/build-dispatch/spec.md`. I ran them once. I also extracted each WHEN line verbatim from the same files and ran it with `bash`. Logs: `scratch/acceptance.log`, `scratch/acceptance-base2.log`, `scratch/pytest.log`, `scratch/probes.log`.

A note on the base copy. My first base pass ran from a copy that sat inside the store checkout. There, `bin/factory init` refuses ("is inside the store checkout ... run init from the repository root"), so that store had no spec store. I ran `git init` on the copy so it is its own repository root, then re-ran every base result that depends on init. The base results below come from that second pass.

Per criterion:
- NEW | Acceptance names an unmerged sibling it does not depend on, refused until that sibling merges | base: `unmerged: blocked=0 names=0 runs=1 ready-for-implementer` / `merged: exit=2 runs=1` (the spec's "fails today" output) | PR: `unmerged: blocked=1 names=1 runs=0 ready-for-implementer` / `merged: exit=0 runs=1` | PASS
- NEW | A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start | base: `park T-0001.1: EMPTY-OUTPUT from implementer` / `greet=0 other=0 runs=2` / `ruled: exit=2 runs=2` (the spec's "fails today" output) | PR: `park T-0001.1: BLOCKED from harness: spec drift:` / `greet=1 other=0 runs=0` / `ruled: exit=0 runs=1` | PASS
- NEW (intermediate) | `spec add` writes `v1.yaml` with `integration_head` = main | base: `sed: .../specs/T-0001/v1.yaml: No such file or directory`, `0` (the file does not exist yet, the expected reason) | PR: `1` | PASS
- REGRESSION | Unrelated changes, a listed test, an amendment written after the change | base: not run | PR: `other: exit=0 runs=1` / `listed: exit=0 runs=1` / `amended: exit=0 runs=1` | PASS
- REGRESSION | Intent-unchanged amendment re-pins and keeps tasks | base: not run | PR: `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged` | PASS
- REGRESSION | A later implementer run receives the amended spec; the record lists what changed | base: not run | PR: `changed=1 merged=1 reason=1 logged=1` / `amended=1 old=0 run_version=2` | PASS
- REGRESSION (intermediate) | Harness suite passes; the current-truth sibling-tests scenarios in build-dispatch print the same lines as on base | base: `exit=0 ready-for-implementer runs=1`; three lines `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`; `park T-0001.2: BLOCKED from harness:` / `ruling=0 ready-for-implementer` | PR: identical lines | PASS (the suite result is under Gate suite)
- REGRESSION (intermediate) | `git diff --check main...HEAD` exits 0 | base: not run | PR: exit 0, no output | PASS (the same run as the gate)

Gate suite: PASS
- `(export HOME=...; git diff --check main...HEAD)`: exit 0, no output.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: exit 0, `473 passed in 305.08s (0:05:05)`.

Probes (PR head, on the `t0027-amend.sh` fixture):
- One `--no-ff` merge onto main whose branch changes `src/greet.py` and `tests/test_greet.py` in separate commits → refused: `spec drift: tests/test_greet.py changed by 61f5a1ac9 since spec v1 was written at d5b5023bc`, naming the merge commit. No run was written. The first-parent diff covers the whole merge, not only the tested single commits → OK
- `src/greet.py` and `tests/test_greet.py` changed in two separate direct commits on main → `exit=0 runs=1`. Not drift, as the spec's same-commit rule says → OK
- Acceptance `the scenarios of ST-1.` (label at the end of a sentence, followed by `.` with no digit) → `blocked=1 runs=0`, naming T-0001.1. The token rule is not tied to the tested `REGRESSION: ST-1 scenarios` wording → OK
- 300 unrelated commits, then one drift commit → `blocked=1` in about 2 s. The per-commit `git diff` loop is acceptable at this size → OK
- Drift parks the sub-ticket (`exit=2`). A further drift commit lands, then an intent-unchanged amendment → `exit=0`. `v2.yaml`'s `integration_head` equals the current main (`b03b974b6`), so the amendment re-bases the count → OK

Scope check: the diff touches `factory/cli.py` and `factory/subtickets.py` (both declared protected paths) and adds `tests/factory/test_spec_drift.py`. It changes no existing test, no workflow and not `factory/gitops.py`. The refactor of `sibling_tests` through the new `field_text` sits inside the declared `factory/subtickets.py`. Its behaviour held: the build-dispatch sibling-tests scenarios printed identical lines on base and PR, and the suite passed.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command printed its expected lines on the PR, both NEW criteria and the intermediate record check failed on base for the reason the spec states, both gates passed on 49cc429, and five off-test probes behaved as the design describes.
ESCALATIONS: none
