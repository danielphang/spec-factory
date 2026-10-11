## Acceptance

Run every command from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper.

- Unmarked writes from inside the target are refused while a run is in flight, init included → REGRESSION
- The refusal names the throwaway store and not the marker → REGRESSION
- A harness acceptance is refused while a run is in flight → REGRESSION
- An unmarked drive starts beside another ticket's run, is refused from a run's directory, and marks only its own store calls → NEW. Today it prints `inside_unmarked=2 inside_marked=2 accept=2 unmarked=2 ready-for-triage calls=0 effort=0 dispatch=0`: the fence refuses the unmarked drive of T-0002 because T-0001 has a run in flight.
- A drive of a ticket with its own run in flight is refused, marked or not, and writes nothing → NEW. Today it prints `unmarked=2 marked=0 named=1 marker=0 json=0 calls=0 store=changed parked`: the marked drive goes ahead and parks T-0001.
- A drive of a parent whose sub-ticket has a run in flight is refused and writes nothing → NEW. Today it prints `exit=0 named=0 calls=0 store=changed`: the drive starts and writes its status file and records.
- A recorded live driver blocks a second drive, and an ended or dead one does not → NEW. Today it prints `live=0 pid=0 file=changed closed ended=0 closed dead=0 closed calls=3`: the drive of T-0001 ignores the live driver, overwrites its status file and closes the ticket.
- The documents describe the driver's exemption and its same-ticket guard → NEW. Today it prints `changelog=CONTIGUOUS last=no step=1 drive=no,no fence=no human=no design=no,no,1 buildspec=no,no whitespace=clean`.

## Out-of-scope observations

- `tests/factory/test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight` failed once in a full serial suite run on the prototype (`seen` held fewer than four running entries), then passed in three reruns. It samples the status file every 50 ms while two checkers each sleep 2 s, so a slow moment can miss the four-entry window. It may be flaky on a loaded machine, independent of this change.
- README's driver section still says "The driver is tested, and has not yet run a real ticket", but the report shows it driving T-0035 and T-0036 on the Nanobot instance on 2026-10-10. Updating that claim is the README's own maintenance rule and is not part of this ticket's intent.

## Critic rounds

round 1 · spec v1 · run-0426-critic · APPROVE

## Critic review, round 1

What I checked (all on `~/dev/spec-factory`, `main` at `98dd74c`):

- Code citations. `factory/cli.py:1939-1940` is `READ_ONLY` and `drive` is not in it; `1943-1946` is `_in_flight()`; `1949-1963` is `fence()` with the location rule first, then the marker, then the in-flight list; `1976-1977` is the call in `main()`; `1428` is the other call, in `init`; `207-212` are `run_start`'s same-ticket refusals; `606-609` is `spec_amend`'s sub-ticket in-flight collection. `factory/drive.py:601-619`: `drive()` sets `FACTORY_DISPATCH=1` at 605 and writes the status file with `ended: None` at 617-619 without reading an existing one. `store.subtickets_of` (`store.py:230`) and `store.Refused` (`store.py:25`) exist. `main()` turns `Refused` into stderr text plus a last stdout line `{"ok": false, "error": ...}` and exit 2 (`cli.py:1981-1984`), as design B states. `Driver.end()` writes `ended` on both a stop and a normal end (`drive.py:574-579`), so the pid guard does not block the current-truth resume-after-SIGTERM scenario.
- Document citations. `README.md:737-740` (driver step 2, the marker instruction), `824-830` ("Where a human decides" opening), `906-913` (the fence bullet), `docs/design.md:64` ("meets the fence and the lock like any write when it starts"), `dev/build-harness.spec.md:295`, `openspec/specs/live-store-guard/spec.md:5-7`, changelog last entry 68 in the "After issue #N (date), where ...:" form. Issue #86 is in `dev/issues.md:90`; #89 (line 93) says "after #86". Decision log: the T-0040 line "`factory drive` is a write command like any other ... Rejected: exempting `drive` from the fence" (`decisions.md:168`), the 2026-10-04 T-0024 lines on the refusal never naming the marker and on `--accept-harness` being a write, and the 2026-10-11 T-0042 replacement.
- Tests for the old behaviour. `grep` of `tests/factory/test_drive.py`, `test_drive_build.py`, `test_live_store_guard.py` and `grep -rl '"drive"' tests/factory/`: no test starts a drive on an own store with a run in flight; `test_drive.py:170` sets the marker on a throwaway store, which the fence never covers. "Tests to change: none" holds. The only pin is the current-truth scenario, restated as MODIFIED.
- Acceptance command. I ran the documents scenario as written, through the wrapper: it printed `changelog=CONTIGUOUS last=no step=1 drive=no,no fence=no human=no design=no,no,1 buildspec=no,no whitespace=clean`, the base line the spec states. Its `sed` anchors resolve (`README.md:717`, `754`, `822`, first fence at 832; `914` for the fence bullet's end).
- Fixture dependencies. `t0022-sib.sh` (line 382 of my input) leaves T-0001.2 `ready-for-implementer` on a throwaway store and uses `$E`, so the parent scenario's `E=tests/test_interim.py; . t0022-sib.sh && run start --role implementer --ticket T-0001.2` is sound.
- Rubric 5: no approved changes awaiting archive; no open ticket in the decision log conflicts.

Not checked: the four behaviour NEW scenarios' base output and the prototype's suite result. Both need the stand-in `claude` fixtures and a drive run; the implementer and verifier run them. The spec's stated base lines are consistent with the code I read (an unmarked drive meets `fence()` before line 605 sets the marker; a marked drive of a ticket with its own run in flight reaches `run_start`'s refusal at `cli.py:211-212` and parks).

## Findings

[SHOULD-FIX] 6 proposal.md, Problem paragraph 2 / Decisions bullets 1 and 4
Problem: "own store" (the store an instance's config names, which the fence covers) and "throwaway store" (a store named by `FACTORY_STATE`, which it never covers) are used in Evidence ("On a throwaway store the fence never applies") and Decisions ("on any store, a throwaway store included"; "Rejected: applying it only on an own store, as the fence is") without a gloss, and the reader cannot tell what the rejected alternative would have excluded.
Evidence: The Problem glosses ticket, role run, in flight, drive, dispatcher, store, fence, marker and park; it never says the fence applies only to the instance's own store, nor what a throwaway store is. The first Decisions bullet still reads correctly without the distinction, so I do not block on it.
Suggested fix: Add one sentence to the Problem's second paragraph: the fence covers only the instance's own store, the one its configuration names; a throwaway store, named by the environment variable `FACTORY_STATE`, is never fenced.

[NIT] 6 proposal.md, Problem paragraph 3; Evidence paragraph 1
Problem: "(option A)" names an option from an answer the reader has not seen, and `--phase intake`, `--phase build --parallel 1` and "recorded KILLED" are copied from the report without a gloss.
Evidence: The reader can follow the paragraph from the command shapes and "as designed", so this does not need a translator.
Suggested fix: Drop "(option A)" or say "the first of the two options the operator was given", and gloss `--phase` once as the half of the route the driver runs, intake or build.

[NIT] 1 proposal.md, Evidence paragraph 2
Problem: The reproductions are dated at `main` `ba09ba7`; `main` is now `98dd74c`, one commit later.
Evidence: `git diff --stat ba09ba7..HEAD`: `docs/golden.md` added, `docs/north-star.md` 2 lines, `README.md` +1 line. Every cited line number in `cli.py`, `drive.py`, `README.md`, `design.md` and `build-harness.spec.md` still matches at HEAD, so nothing an implementer reads is stale.
Suggested fix: None required; the implementer may note that line numbers were verified at `98dd74c`.

No blocking issues. The scenarios would fail against a stub (a guard that always refuses fails "An unmarked drive starts beside another ticket's run" and the ended/dead cases; one that never refuses fails the three refusal scenarios), the exemption is bounded to `drive` with `--accept-harness` kept fenced in full, the overturned T-0040 decision and its replacement are both named, and the two protected paths are declared under Risk.
