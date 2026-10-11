Sub-ticket: T-0042.1, branch `factory/T-0042.1`, commit `8f9c2a9` on base `98dd74c` (worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0042.1`). Parent: T-0042, approved spec v2.

## What changed

An operator can now start `factory drive` on one ticket while another ticket has a run in flight, with no marker typed. A second drive of a ticket that is already being worked is refused. Some terms: a run is "in flight" from `run start` until its result is recorded. The live-store fence is the harness check that refuses writes to an instance's own store while any run is in flight, unless the command carries the dispatcher marker `FACTORY_DISPATCH=1`. `factory drive` is the dispatcher, the one process meant to write the store while runs work.

- **A, the exemption (`factory/cli.py`).** `fence()` gains a keyword-only `in_flight: bool = True`. When it is false, `fence()` returns after the location rule, which refuses a caller under the own store's `runs/` or `worktrees/`, and before the marker and in-flight checks. `main()` now passes `in_flight=a.cmd != "drive" or bool(a.accept_harness)`. So `drive` keeps the location rule and the harness lock, and a `drive` given `--accept-harness` is fenced in full. Callers of `fence`, from `grep -rn "fence(" factory tests bin`: `cli.py:1428`, which is `init`, unchanged, and `cli.py:1981`, which is `main()`. The fix goes in `main()` because the exemption depends on the command, and only `main()` knows the command.
- **B, the same-ticket guard (`factory/drive.py`).** `_same_ticket_guard(root, tid)` is the first call in `drive()`. It runs before the marker is set and before the status file is written. It runs whether or not the caller has the marker, and on any store, a throwaway store included. A missing ticket passes, so the existing "no such ticket" result is unchanged. The guard refuses in two cases:
  - The ticket or one of its sub-tickets has runs in flight. It collects `in_flight` the way `spec_amend` does (`cli.py:606-607`) and raises `store.Refused("<T> has runs in flight on it or its sub-tickets: <ids>; drive it again once they finish")`.
  - `drive/<T>.yaml` has `ended` absent or null, and its `pid` is live. It raises `store.Refused("<T> is already being driven by pid <n> (<path>); stop that driver or wait for it to end")`.

  `_live(pid)` sends signal 0 with `os.kill(pid, 0)`. `ProcessLookupError` counts as dead. `PermissionError` counts as live. A pid that is not a positive integer counts as not live, and so does a bool. One addition goes beyond the spec: `OverflowError`, raised for a pid past the platform's range, also counts as dead, where it would otherwise exit 1. `main()` already turns `Refused` into exit 2 with `{"ok": false, "error": ...}`. The module docstring and `drive()`'s docstring now describe the exemption and the guard.
- **C, tests.** One new file, `tests/factory/test_drive_guard.py`, with 16 cases. They reuse `test_drive.STANDIN` (the stand-in `claude`), `test_drive.Store`, `test_drive_build.BuildStore`, and the own-store `target` fixture and helpers from `test_live_store_guard`.
- **D, documents.**
  - `README.md`, in "Driving a ticket from a shell with `factory drive`": step 2, which told the operator to type the marker, is deleted, and the steps are renumbered 1-4. A new paragraph covers what the spec lists: no marker needed, why, the same-ticket refusals, the location rule, SIGKILL leaving runs in flight, and deleting a status file whose pid is not a driver.
  - `README.md`, other sections:
    - The "Live-store fence" bullet now says `drive` is exempt and guards its own ticket.
    - "Where a human decides" gains one sentence after the read-only list, and its first line is unchanged.
    - The `drive/<ticket>.yaml` row of the file table now says the next drive reads the file.
    - The status date moves to 2026-10-11.
  - `docs/design.md:64`: the "meets the fence and the lock like any write when it starts" clause is replaced with the exemption, the location rule and lock, full fencing under `--accept-harness`, and the "same ticket" guard. The sentences on the marker and the role processes are kept.
  - `dev/build-harness.spec.md:295`: one sentence added.
  - `docs/changelog.md`: entry 69 for issue #86. It names the exemption, the guard, the overturned T-0040 decision (entry 67) and the three rejected alternatives.
  - No file under `docs/prompts/` or `factory/prompts/` changed.

## Acceptance results

Every command ran from the worktree through the briefing's wrapper, with `TMPDIR` set to this run's scratch directory (`scratch/tmp`), after writing the GIVEN fixtures there. The fixtures came from current truth: live-store-guard lines 13-67, which are identical to the spec's block (`diff` empty), and build-dispatch lines 53-100 and 277-414. Raw output is in `scratch/before.txt` and `scratch/after.txt`.

NEW, before the change (base `98dd74c`). Each line matches the verification.md "Today it prints" line exactly:
- An unmarked drive starts beside another ticket's run… → `inside_unmarked=2 inside_marked=2 accept=2 unmarked=2 ready-for-triage calls=0 effort=0 dispatch=0`
- A drive of a ticket with its own run in flight is refused… → `unmarked=2 marked=0 named=1 marker=0 json=0 calls=0 store=changed parked`
- A drive of a parent whose sub-ticket has a run in flight… → `exit=0 named=0 calls=0 store=changed`
- A recorded live driver blocks a second drive… → `live=0 pid=0 file=changed closed ended=0 closed dead=0 closed calls=3`
- The documents describe the driver's exemption… → `changelog=CONTIGUOUS last=no step=1 drive=no,no fence=no human=no design=no,no,1 buildspec=no,no whitespace=clean`

NEW, after the change (`8f9c2a9`). Each line equals its THEN line exactly:
- `inside_unmarked=2 inside_marked=2 accept=2 unmarked=0 closed calls=1 effort=1 dispatch=1`: the unmarked drive of T-0002 ran to `closed` beside T-0001's run. It was refused from the run's directory, marked or not, and refused with `--accept-harness`.
- `unmarked=2 marked=2 named=2 marker=0 json=1 calls=0 store=unchanged ready-for-triage`: both drives of T-0001 were refused, naming its run. Nothing was written and no role started.
- `exit=2 named=1 calls=0 store=unchanged`: the parent drive was refused, naming the sub-ticket's implementer run.
- `live=2 pid=1 file=unchanged ready-for-triage ended=0 closed dead=0 closed calls=2`: the live recorded driver blocked the drive. The ended record and the dead record did not.
- `changelog=CONTIGUOUS last=yes step=0 drive=yes,yes fence=yes human=yes design=yes,yes,0 buildspec=yes,yes whitespace=clean`

REGRESSION, after only. Each line equals its THEN line:
- Unmarked writes from inside the target are refused… → `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`
- The refusal names the throwaway store and not the marker → `rule=1 state=1 marker=0 json=1 inside=1`
- A harness acceptance is refused while a run is in flight → `accept=2 store=unchanged`

Gates, each run exactly as written from the worktree on `8f9c2a9`:
- `git diff --check main...HEAD` exited 0, so the change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `546 passed in 363.07s`. The timing test that the spec's Out-of-scope observations call possibly flaky passed in this run.

## Tests added/changed

- Added `tests/factory/test_drive_guard.py`, a new file with 16 cases:
  - an unmarked drive of T-0002 finishes (`closed`) beside T-0001's in-flight run on an own store, and T-0001's run stays in flight;
  - a drive given `--accept-harness` is refused by the full fence while a run is in flight;
  - a drive from under `runs/` or `worktrees/` is refused, marked or not (4 cases);
  - a drive of a ticket with its own run in flight is refused, marked or not, with an unchanged tree and no role call (2 cases);
  - a drive of a parent whose sub-ticket has an implementer run in flight is refused;
  - a live recorded driver blocks a drive (2 cases): the test process's own pid, and pid 1, which exercises the `PermissionError` branch for a non-root user;
  - a status file whose pid is dead, `ended` set, `"abc"`, `0` or `2**70` does not block (5 cases).
- With `factory/` stashed, on the base code, the file ran `6 failed, 10 passed`. The 6 failures are the exemption case and the guard's refusal cases. The 10 that already passed pin behaviour that must not change: the location rule, the `--accept-harness` fence, and the records that must not block.
- No existing test changed. The spec's Tests to change says none.

## Known gaps and uncertainties

- Markers added with the `factory:` prefix (coding standard rule 3): none.
- A status file holding valid YAML that is not a mapping would make the guard raise `AttributeError`, so the drive exits 1 rather than exit 2. The driver itself always writes a mapping. I did not add handling, because the spec does not cover it.
- Guarding against two drives of the same ticket started in the same instant is out of scope by the spec's decision. The guard is checked once.
- Checking that a live pid really is a `factory drive` process is rejected in the spec. A pid reused after a SIGKILLed driver blocks the drive until the operator deletes the status file, as README now says.
- Test design choices:
  - The "dead pid" case spawns a process inside the test and waits for it. If the OS reused that pid within milliseconds, the case would fail spuriously. This is unlikely, and I have not seen it.
  - The pid-1 case assumes pid 1 exists, which holds on macOS and Linux.
  - The `target` fixture is imported from `test_live_store_guard` with `# noqa: F401`. No other test in the repo imports a fixture across modules yet. I chose it over copying the fixture.
- README's "Ground truth only" rule says a behaviour appears above "Where this can go" only after it has run on a real ticket. The driver section already sits there, and the spec directs these edits. The new guard has run only in tests and scenarios, not on a real ticket.
- `_same_ticket_guard` builds the status-file path `root / "drive" / f"{tid}.yaml"` itself rather than reusing `Driver.status_path`. The guard has to run before a `Driver` is constructed, so this is one repeated expression.

## Out-of-scope observations

- README's driver section still says "The driver is tested, and has not yet run a real ticket". The spec notes the driver has since run T-0035 and T-0036 on the Nanobot instance. I left that sentence unchanged, as the spec says.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN line exactly, both gates passed on the commit, and the new tests failed on the base code for the expected reasons.
ESCALATIONS: none. The protected paths `factory/cli.py` and `factory/drive.py` are declared in the spec's Risk section, and the change does only what Proposed change A and B describe.
