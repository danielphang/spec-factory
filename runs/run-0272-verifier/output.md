Commit: a8d6326dbb20513274b5508fdaee6aae15ebd888 (main, after T-0025.1 and T-0025.2 merged; base 0b1abad474cb9c583ed8445fc33617f9f0bdc37b)

How it ran: the PR head was the given worktree, and the base was a detached worktree at 0b1abad (removed afterwards). I ran `uv sync --frozen` in each. Before running anything, I diffed the GIVEN block and all 17 WHEN commands against the spec text in input.md and found them identical (`diff` printed nothing). Each tree then ran the GIVEN block once and every WHEN under `bash`, with a fresh HOME from the wrapper. TMPDIR was left at its default, so the fixtures' `mktemp -d` behaved as written. git 2.54.0.

Per criterion:
- NEW | init creates the store on the factory-store branch, out of the integration checkout's sight | base: `branch=main seen_by_main=6` | PR: `branch=factory-store seen_by_main=0` | PASS
- NEW | init on a clone restores the store from the pushed branch | base: `On branch main` / `nothing to commit, working tree clean` / `exit=1 branch=main restored=1` | PR: `exit=0 branch=factory-store restored=1` | PASS
- NEW | init on a clone with two remotes carrying the store branch refuses and names both | base: `exit=0 store=written local_branch=0 names=0,0` | PR: `exit=2 store=none local_branch=0 names=1,1` | PASS
- NEW | init from a scratch directory inside the store checkout refuses and leaves the store unchanged | base: `exit=0 phantom=written store=changed` / `found=` | PR: `exit=2 phantom=none store=unchanged` / `found=ready-for-triage` | PASS
- NEW | init from the store checkout on a detached HEAD refuses | base: `exit=0 detached=yes phantom=written store=changed` / `found=` | PR: `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage` | PASS
- REGRESSION | init in a separate repository under a run's scratch directory still creates its instance | base: `exit=0 instance=written live=ready-for-triage` (ran anyway) | PR: `exit=0 instance=written live=ready-for-triage` | PASS
- NEW | init refuses a once-tracked store path and writes nothing | base: `exit=0 instance=written names_path=0` | PR: `exit=2 instance=none names_path=1` | PASS
- NEW | store migrate carries the store to factory-store at the new path | base: `exit=2` / `branch= same_tree=no scratch= old=kept main_tracks=9 seen_by_main=0` / `state_dir=.factory/state ticket=ready-for-triage` | PR: `exit=0` / `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0` / `state_dir=.factory/store ticket=ready-for-triage` | PASS
- NEW | store migrate refuses an uncommitted store and a run in flight | base: `uncommitted: exit=2 names=0 branch=0` / `in flight: exit=2 names=0 branch=0 new=none` (argparse rejects `store`, as the spec states) | PR: `uncommitted: exit=2 names=1 branch=0` / `in flight: exit=2 names=1 branch=0 new=none` | PASS
- NEW | A checkout of an older commit leaves the moved store untouched | base: `live=lost on=main` | PR: `live=live on=main` | PASS
- NEW | A sub-ticket merges after a store commit | base: `exit=2 refused=1` | PR: `exit=0 refused=0` | PASS
- REGRESSION | A sub-ticket is refused after a code commit to main | base: `exit=2 refused=1` (ran anyway) | PR: `exit=2 refused=1` | PASS
- NEW | The design doc names the store branch and the path rule | base: `store_branch=0 tickets_branch=2 never_tracked=0` | PR: `store_branch=1 tickets_branch=0 never_tracked=1` | PASS
- NEW | The build spec calls the store branch factory-store | base: `old_name=16 new_name=0` | PR: `old_name=0 new_name=1` | PASS
- NEW | The changelog records the store branch in one contiguous entry | base: `CONTIGUOUS` / `0` | PR: `CONTIGUOUS` / `1` | PASS
- NEW | The README describes the store branch and the move | base: `store_branch=0 migrate=0 ffdx=0 premove=0 old_cost=1 old_refs=4` | PR: `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0` | PASS
- REGRESSION | The store-branch change adds no whitespace errors (`git diff --check main...HEAD`) | base: not run | PR: `exit=0` | PASS

Every base output matches the "today" output in verification.md, character for character. Every NEW criterion fails on the base for the reason the spec gives and passes on the PR.

Gate suite: PASS
  `git diff --check main...HEAD`: no output, exit 0. On a parent close HEAD is main, so this range is empty and proves nothing. As a probe, `git diff --check 0b1abad HEAD` (the whole parent change) also printed nothing and exited 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `300 passed in 388.11s`. A second run, to capture the exit code, gave `300 passed in 209.35s` and `exit=0`.

Probes (on the PR head, fresh HOME, same fixtures):
- `init` run from the store worktree's own root `.factory/state` (store on `factory-store`) → exit 2, no phantom, store status unchanged → OK
- `init` from `.factory/state/tickets` with the store on `factory-store` → exit 2, `phantom=none store=unchanged` → OK
- Store worktree on a third branch `other` (neither `factory-store` nor detached), then `init` from its `tickets/` → exit 2, `... is inside the store <tgt>/.factory/state of the instance <tgt>/.factory; run init from the repository root`, no phantom, store unchanged. Condition A.1.2 covers more than the tested detached case. → OK
- `store migrate --to .factory/records` (not the path the tests use) → exit 0, branch `factory-store`, `state_dir=.factory/records`, ticket still found, old path gone, exclude line `/.factory/records/` written. Not special-cased to `.factory/store`. → OK
- `store migrate --to .factory/state` (the tracked old path) → exit 2, no branch. With a local `factory-store` branch already present → exit 2, no new path, `state_dir` unchanged. → OK
- `store migrate` with a 5 MB random ignored file in a run scratch directory under `sub dir/big file.bin` (spaces in the path) → exit 0, and `cmp` shows the copy is byte-identical. → OK
- A second `store migrate --to .factory/other` after a successful move → exit 2, nothing written → OK
- A new `init` with the repository root on a detached HEAD (spec A.3.1 says to use `HEAD`) → exit 0, store on `factory-store` → OK

Out-of-scope observations:
- Commit 878c68b changes the existing test file `tests/factory/test_live_store_guard.py`, although the spec's "Tests to change" says none. This is the case the spec anticipated. It is authorized by `.factory/state/approvals/T-0025.1/ruling-1.md`, which names the two tests and says only their `init` assertion may change. I read the diff: only the `init` branch of each loop changes, to exit 2 plus A.1's message, and `assert snapshot(target) == before` is kept. That matches the ruling.
- README line 281 still names `.factory/state`, but only as the default path for a new instance in the commit how-to. It does not give the live store's location.

STATUS: VERIFIED
CONFIDENCE: high. All 17 scenarios ran verbatim on both trees and matched the spec's expected outputs, the gate suite passed twice, and 8 probes past the tested inputs held.
ESCALATIONS: none
