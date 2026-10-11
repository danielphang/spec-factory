Commit: 654f523b997af69c9896cb06bdd9ac36fc04469c (branch `factory/T-0041.1`, base `cce3d6f43a2126c54141f67c377ac92b908880d6`; the worktree was clean and `git merge-base main HEAD` is the base)

How I ran things. The three GIVEN fixture blocks were extracted verbatim from the store's current truth (`.factory/store/openspec/specs/{spec-amendment,build-dispatch,human-resolution}/spec.md`) into `scratch/given.sh`; the seven WHEN commands were copied into `scratch/acc.sh` and diffed against the sub-ticket text (`diff` printed nothing). Every run went through the running-code wrapper from the checkout root after `uv sync --frozen`, with `TMPDIR` set to a directory under this run's scratch (`tmp-pr`, `tmp-base`). The PR run is `scratch/acc-pr.txt`; the base run is a clone of the worktree checked out at `cce3d6f` (`scratch/base`, with a local `main` at that commit), output in `scratch/acc-base.txt`. Both runs wrote nothing to stderr.

Per criterion:

- REGRESSION | A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges | base: not run | PR: `unmerged: blocked=1 names=1 runs=0 ready-for-implementer` / `merged: exit=0 runs=1` | PASS
- REGRESSION | A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start | base: not run | PR: `park T-0001.1: BLOCKED from harness: spec drift:` / `greet=1 other=0 runs=0` / `ruled: exit=0 runs=1` | PASS
- NEW | A merged sibling's merge is not drift, and a later commit or merge from elsewhere still is | base: `none: drift=1 greet=1 named=0 runs=0` / `other: drift=1 greet=1 named=1 runs=0` / `greet: drift=1 greet=1 named=1 runs=0` / `merge: drift=1 greet=1 named=1 runs=0` (the spec's stated "today", word for word) | PR: `none: drift=0 greet=0 named=0 runs=1` / `other: drift=1 greet=0 named=1 runs=0` / `greet: drift=1 greet=1 named=1 runs=0` / `merge: drift=1 greet=0 named=1 runs=0` | PASS
- NEW | A ruling on a harness-bug park from an implementer's run start returns the sub-ticket, and its implementer then starts | base: `ruling=2 parked kept=no drift=1` / `start=2 runs=0` (as the spec states) | PR: `ruling=0 ready-for-implementer kept=yes drift=1` / `start=0 runs=1` | PASS
- REGRESSION | A ruling on a checker's or a compose step's harness-bug park is still refused | base: not run | PR: two lines, each `exit=2 refused=1 parked rulings=0` | PASS
- NEW | The design doc, build spec, README and changelog record both changes, and no prompt copy changes | base: `design-drift=no design-ruling=no buildspec=no unstick=no bullet-sibling=no bullet-stale=yes prompts=0` / `CONTIGUOUS` / `0` (as the spec states) | PR: `design-drift=yes design-ruling=yes buildspec=yes unstick=yes bullet-sibling=yes bullet-stale=no prompts=0` / `CONTIGUOUS` / `3` | PASS
- REGRESSION | The sibling-merge change adds no whitespace errors | base: not run | PR: `exit=0` | PASS

Gate suite: PASS
- `git diff --check main...HEAD` from the worktree: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` from the worktree, default `TMPDIR`: exit 0, `530 passed in 352.18s`. Log: `scratch/suite.log`.

Probes (PR head, `scratch/probe.sh`, output `scratch/probe.txt`):
- Three-part plan, ST-1 and ST-2 each merged `--no-ff` adding a test beside `src/greet.py` and recorded with `main_after`; ST-3 starts → `drift=0 runs=1` → OK. The skip is a set, not a single sibling.
- ST-1's `main_after` recorded by hand as a 9-character abbreviation → `drift=1 greet=1 runs=0` → OK. The skip matches the exact recorded id, as Decision 1 asks; this fails safe by parking. `factory merge` records `gitops.rev`, which is `git rev-parse` (`factory/gitops.py:38-39`, used at `factory/cli.py:991`), so a real merge records the full id the walk compares against. The implementer's Known gaps already names this.
- Sibling merged as above, then a direct commit on main that changes only `tests/test_greet.py` and no design-named file → `drift=0 runs=1` → OK. The named-file condition still gates the rule; the skip did not widen or narrow it.
- `--ruling` on a park whose reason is exactly `harness-bug: run start implementer: ` with nothing after it, from `ready-for-implementer` → `exit=0 ready-for-implementer round={"spec": 0, "pr": 0}` → OK. The prefix match accepts the degenerate reason and keeps the round, consistent with Decision 3; no criterion speaks to the empty tail.

Diff footprint, read from `git diff --name-only cce3d6f...654f523`: `README.md`, `dev/build-harness.spec.md`, `docs/changelog.md`, `docs/design.md`, `factory/cli.py`, `tests/factory/test_drift_siblings.py` (new), `tests/factory/test_resolve_rulings.py`. The one existing test changed is the one the parent's Tests to change lists, and only its refusal-text assertion moved (diff lines 644-646 of the input). `factory/cli.py` is the protected path the spec's Risk section declares. No file under `docs/prompts/` or `factory/prompts/` changed (`prompts=0` above).

Out-of-scope observations:
- `tests/factory/test_drift_siblings.py::test_a_merged_subticket_of_an_earlier_plan_is_not_drift` rewrites `specs/T-0001/v2.yaml`'s `integration_head` by hand so the walk passes over the earlier plan's merge. That is the only suite case for Decision 1's "from an earlier plan" clause, and it depends on that hand edit rather than on how `approve-spec --edit` records the head. It passes, and the design asks for exactly this case, so this is a note for a later reader, not a finding.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command printed its expected text on the PR head; each NEW command printed the spec's stated "today" output on the base; both gates exited 0 (530 passed); four probes near the tested inputs behaved as the decisions describe.
ESCALATIONS: none
