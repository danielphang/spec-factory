## Proposed change

A. Exempt `drive` from the fence's in-flight rule (`factory/cli.py`).
   - Give `fence(inst, cfg, root)` a keyword `in_flight: bool = True`. When it is false, return after the location check (`runs/`, `worktrees/`) and before the marker and `_in_flight()` checks. Update its docstring.
   - In `main()`, call `fence(inst, cfg, root, in_flight=a.cmd != "drive" or bool(a.accept_harness))`. The other call, in `init` (`cli.py:1428`), is unchanged.

B. The same-ticket guard (`factory/drive.py`).
   - Add `_same_ticket_guard(root, tid)`, called first in `drive()`, before `os.environ["FACTORY_DISPATCH"] = "1"`.
   - It returns at once when `tickets/<tid>.yaml` does not exist.
   - It collects `in_flight` from the ticket and from `store.subtickets_of(root, tid)`, as `spec_amend` does at `cli.py:606-609`. If any run is listed, it raises `store.Refused` with the first text under Decisions.
   - It reads `drive/<tid>.yaml` when the file exists. If `ended` is absent or null and `pid` is a live process, it raises `store.Refused` with the second text.
   - Liveness: `os.kill(pid, 0)`. `ProcessLookupError` means dead and `PermissionError` means live. A pid that is not a positive integer means not live.
   - `main()` already turns `Refused` into exit 2 with `{"ok": false, "error": ...}` as the last stdout line, and nothing has been written at that point.
   - Update the module docstring and `drive()`'s docstring to say the driver is exempt from the in-flight rule and guards its ticket.

C. Suite tests in a new file, `tests/factory/test_drive_guard.py`. Use the stand-in `claude` pattern of `tests/factory/test_drive.py`, and an own-store target where the fence matters, as `tests/factory/test_live_store_guard.py` builds one. Cases:
   - an unmarked drive of T2 starts and finishes while T1 has a run in flight on the own store;
   - a drive of T1 is refused with exit 2, marked or not, while T1 has a run in flight, and the store is unchanged;
   - a drive of a parent is refused while one of its sub-tickets has a run in flight;
   - a drive is refused while `drive/T.yaml` names a live pid with no `ended`;
   - a drive is not refused for a dead pid, or for a live pid whose `ended` is set;
   - a drive started from under the store's `runs/` or `worktrees/` is refused, marked or not;
   - a drive given `--accept-harness` is refused while a run is in flight.

D. Documents.
   - `README.md` "Driving a ticket from a shell with `factory drive`": delete step 2 and renumber the rest. Add a paragraph that says:
     - the driver needs no `FACTORY_DISPATCH=1`, even while other tickets' runs are in flight;
     - why: it is the dispatcher, so the live-store fence exempts it from its in-flight check;
     - it refuses, with exit 2 and nothing written, to start on the same ticket while that ticket or one of its sub-tickets has a run in flight, or while `drive/<ticket>.yaml` shows another driver of it still running;
     - from inside the store's `runs/` or `worktrees/` it is refused like any write;
     - a driver killed without a chance to stop, by SIGKILL, leaves its runs in flight, and they are cleared as "Where a human decides" says;
     - if the refusal names a pid that is not a driver, delete that status file.
   - `README.md` "Live-store fence" bullet: say `factory drive` is exempt from the in-flight check and guards its own ticket instead.
   - `README.md` "Where a human decides", after the list of read-only commands: one sentence that `factory drive` is exempt and needs no marker. Keep the paragraph's first line as it is, because current truth's "README tells the operator how to write during a run, first thing under Where a human decides" checks it.
   - `README.md`: the `drive/<ticket>.yaml` row of the store's file table says the driver also reads the file to refuse a second driver of that ticket. Bump the date in the status header.
   - `docs/design.md:64`: replace "`factory drive` meets the fence and the lock like any write when it starts; once past them, it sets the marker" with text saying that `factory drive` is exempt from the in-flight rule, keeps the location rule and the lock, and is fenced in full when given `--accept-harness`. The text also states the same-ticket guard, saying "same ticket" in those words, and keeps the existing sentences on the marker and role processes.
   - `dev/build-harness.spec.md`, the `**`factory drive`**` paragraph (line 295): add one sentence that it is exempt from the fence's in-flight rule when it starts, keeps the location rule, and refuses to start on the same ticket as a run in flight or a live driver.
   - `docs/changelog.md`: entry 69, in the "After issue #N (date), where ...:" form of entries 66-68. It names issue #86, the exemption, the guard, the overturned T-0040 rejection, and the rejected alternatives under Decisions.
   - No file under `docs/prompts/` or `factory/prompts/` changes.

## Tests to change

none. No suite test pins the old behaviour (Evidence). The one current-truth scenario that does, build-dispatch's "The driver marks its own store calls, never its roles', and passes a configured effort", is restated below as a MODIFIED requirement.

