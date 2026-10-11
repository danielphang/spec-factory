Commit: 8f9c2a96193e4aef8207f6dfd750c334e78f43a5 (branch `factory/T-0042.1`, base `98dd74c2ec5165f70bf7f08d9ed38d808ade01e4`)

Checked, in the role's order, by reading the diff and confirming each referenced name in the worktree.

1. Test integrity. `git diff --stat 98dd74c..HEAD` lists seven files; the only test file is the new `tests/factory/test_drive_guard.py` (157 lines added). No existing test changed, no assertion weakened. The new file's imports resolve: `cli`, `js`, `tree` at `tests/factory/test_instance.py:26,36,48`; `target` (fixture), `state`, `start_triage`, `snapshot`, `request`, `assert_refused` at `tests/factory/test_live_store_guard.py:24-55`; `STANDIN`, `Store` at `tests/factory/test_drive.py:28,53`; `BuildStore` at `tests/factory/test_drive_build.py:54`. `Store.cli` takes `plays=` and `Store.drive` returns `(cp, json)` as the tests use them.

2. Correctness. Part A: `factory/cli.py:1949` adds keyword-only `in_flight`; line 1961 returns before `_in_flight()` when it is false, after the location loop at 1956-1959. `main()` at 1981 passes `in_flight=a.cmd != "drive" or bool(a.accept_harness)`, and the fence still runs for `drive` because `drive` is not in `READ_ONLY`. The `init` call at 1428 is untouched. Part B: `_same_ticket_guard` (`factory/drive.py:610-624`) is the first statement of `drive()` (line 636), before `os.environ["FACTORY_DISPATCH"] = "1"` (637) and before the status file is written (658). It uses `store.ticket_path`, `store.load_ticket`, `store.subtickets_of`, `store.read_yaml`, `store.Refused` (`factory/store.py:111,115,230,98,25`), all existing. `main()` turns `Refused` into exit 2 with the JSON line at `cli.py:1985-1988`, as the spec relies on. The driver's own status file carries `pid: os.getpid()` and `ended: None` (`drive.py:656-657`) and sets `ended` at 584, so the guard reads the keys the driver writes. A missing ticket returns from the guard and reaches the existing "no such ticket" `_fail` at 652. `_live` treats `ProcessLookupError` as dead and `PermissionError` as live per Decisions; the extra `OverflowError` branch is disclosed in the PR and only turns a would-be exit 1 into "not live" for a pid past the platform range, which is the spec's "not a positive integer in range" intent. Edge cases the spec implies: a sub-ticket id passed as the ticket (`subtickets_of` returns nothing, so only its own `in_flight` counts), `ended` present with a non-null value (passes, as "ended is set" requires), and a status file left by a SIGKILLed driver (pid dead, passes; runs in flight still block, as documented). All behave as the spec says.

3. Scope. Every hunk maps to a lettered part A-D. No file outside them.

4. Silent behavior changes. None found. The fence on every other command, the location rule, the refusal texts and the harness lock are unchanged; `drive` on a throwaway store already skipped the fence (`is_own_store` returns false at 1953).

5. Security and data safety. `os.kill(pid, 0)` sends no signal. The guard reads the store only; nothing is written before a refusal.

6. Protected paths. `factory/cli.py` and `factory/drive.py` are both declared in the spec's Risk section; listed under ESCALATIONS for the record.

7. Coding standard. `grep -rn "os.kill" factory/` finds no earlier liveness helper, so `_live` sits on rung 2 (stdlib). Lean already.

8. PR description. What changed says in words what changed and glosses run, in flight, fence, dispatcher and marker at first use. Known gaps lists the non-mapping YAML case, the same-instant window, the pid-reuse case and the test design choices. Readable at the gate.

Findings:
- [NIT] factory/drive.py:620: the status-file path `root / "drive" / f"{tid}.yaml"` repeats `Driver.__init__` at line 138 → a renamed status directory would need two edits. The implementer's Known gaps already names it; a two-line module function used by both would remove the repeat. Not blocking: there is no existing helper to reuse, only an instance attribute the guard cannot construct a `Driver` to read.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. Every name the diff relies on exists where the PR says; the guard runs before the marker and the status write, the fence keeps its location rule for `drive`, and the new tests cover each scenario of the spec without touching an existing test. I did not run the suite or the acceptance commands; the verifier does, on this head.
ESCALATIONS: none. For the record under check 6: the change edits the protected harness paths `factory/cli.py` and `factory/drive.py`, both declared in the approved spec's Risk section, so the merge gate needs no further approval for them.
