Commit: 656c179f4a4f4631b8fa61e037c7f871f36cd26d

## What I checked, in the review order

1. Test integrity. `git diff --stat 37848db..656c179` touches six files; the only existing test file changed is `tests/factory/test_run_scratch.py`, and only the three tests the sub-ticket lists under Tests to change (lines 127, 129, 139 and 147 of the diff). Each change is exactly the one the spec describes: 4 comment lines instead of 3, `drive/` counted once, and the two exact line lists ending `"drive/"`. No assertion was weakened, no skip added, no other test touched. `tests/factory/test_drive.py` is new. Its tests go through `bin/factory` with a stand-in `claude`, patch nothing, and assert exact argv, exact result objects, exact run status lists and exact park reasons. No test pins the interim build-phase refusal, as the sub-ticket asks.

2. Correctness against the spec.
   - Routing: `Driver.intake` (`factory/drive.py:239-312`) matches `factory/workflows/intake.js` from `// --- start` (lines 138-199) branch for branch: the five triage outcomes, the writer's NEEDS-HUMAN `spec add` then park, unknown-status parks, `spec:init` and `spec:+1` round operations with the same refusal reasons, `max rounds`, `ESCALATE from critic`, and the `nothing to dispatch from this state` result. `run_role`/`run_once` (`drive.py:160-235`) match `runRole`/`runOnce` (`intake.js:81-128`): one EMPTY-OUTPUT re-dispatch, `run last-message` with the last 4000 characters, `harness-bug: run finish …`, the tripwire `parked` short-circuit, and the failed-call path (`run finish --status-override KILLED`, then park `agent call failed: <role>: <message>`). The `"`-to-`'` replacement in `park()` matches the script's. The ACCEPT title re-read is there (`drive.py:249-251`).
   - `call()` (`drive.py:46-72`) reproduces `clerk()`'s four normalisations (`intake.js:57-67`), and `cli.main` (`cli.py:1955-1977`) converts `Refused` into stderr text plus a JSON `error` line with exit 2, so `stderr` is never blank on a refusal. `SystemExit` from argparse is caught; the driver's own `SystemExit(code)` from `drive()` is not raised inside `call()`, so it propagates out of `main` to the process exit, giving 143 on SIGTERM.
   - Fence and lock: `("drive", None)` is not in `READ_ONLY` (`cli.py:1927`), so `fence()` and `instance.guard()` run before `drive_cmd`. `fence()` reads `FACTORY_DISPATCH` at call time (`cli.py:1947`), so `os.environ["FACTORY_DISPATCH"] = "1"` set in `drive()` (`drive.py:378`) marks every later nested `main()` call, and the role process env drops the key (`drive.py:191`).
   - Argv (`role_argv`, `drive.py:83-102`): the design's order, one value per option, real paths, `Edit(//…)` rules, `Edit` tool and worktree rule and `--add-dir` for the implementer only, `--effort` only when set. `--prompt-mode replace` swaps in `--system-prompt-file`.
   - `run finish --reply` (`cli.py:471-472`, `_claude_record` at 497-507): records the four keys, each `None` when absent, and `claude: null` for a file that is not one JSON object; it runs for `--status-override KILLED` too. Nothing else in `run_finish` changed.
   - Phase and interim refusal (`drive.py:388-392`): `--phase build`, or a stored build state with no `--phase`, raises `Refused` after only two read-only calls (`config`, `ticket show`) and before `write_status`, so `main` exits 2 and the store is unchanged. A state in neither phase with no `--phase` falls through to `intake()`'s `nothing to dispatch` return, as the script does.
   - Stop (`Driver.run`, `_on_signal`, `stop`, `drive.py:315-359`): SIGTERM to each live process, SIGKILL after 10 s, `run finish --status-override KILLED` for each run still in `self.running`, cleanup for a checker, no park, `ended` written, the `"stopped"` line last, exit 128 + signal. A cancellation that lands inside `create_subprocess_exec` is covered by asyncio's own transport close, so no child is orphaned. An unexpected exception runs the same sequence and exits 1.
   - Status file and `.gitignore`: `write_status` goes through `store.write_yaml`, which creates `drive/` (`store.py:89-95`); `STORE_GITIGNORE` gains the comment line and `drive/` after `runs/*/scratch/` (`store.py:49-55`).

3. Scope. Every file is on part A's list. No change under `factory/workflows/`, `agents/`, `docs/`, `README.md` or either `.factory/`.

4. Silent behaviour changes. `run finish` without `--reply` is unchanged (the `claude` key is only written under `if a.reply`). Every store gets `drive/` in its `.gitignore` at its next `run start`, which the spec's Risk section declares. Nothing else a caller would notice.

5. Security and data safety. Role processes get the driver's environment minus the marker; the fence still refuses writes from inside `runs/`. Park reasons and `--text` are passed as single arguments, so nothing goes through a shell. No secrets, no destructive operation added.

6. Protected paths. `factory/drive.py`, `factory/cli.py`, `factory/store.py` and `factory/instance.template.yaml`, all under `factory/**`, which both the sub-ticket and the approved spec's Risk section declare. Listed under ESCALATIONS for the record.

7. Coding standard. Each new helper sits on a rung no earlier one holds: no last-JSON-line parser or at-least-one argparse type exists in `factory/` (grep of `json.loads` and `ArgumentTypeError` in `factory/*.py` shows only the new ones); `store.write_text`, `store.write_yaml` and `store.now` are reused rather than repeated; the per-file `Store` test helper follows the pattern every other suite file uses (`test_run_scratch.py:24`, `test_tripwire.py:29`, `test_shepherd.py:598`; `conftest.py` has no shared one). The one `factory:` marker (`drive.py:389`) names its limit and its upgrade trigger, and Known gaps lists it. No name is a synonym for an existing one. Lean already.

8. PR description. What changed says in words what each of the ten items does and glosses the fence, the harness lock and the dispatcher marker. Known gaps is honest about untested build-only branches and the stdout-capture limit. One gloss is missing (finding below).

## Findings

- [SHOULD-FIX] PR description: What changed, item 3: "a tripwire `parked`" and "EMPTY-OUTPUT" are factory terms used without a gloss, and "spec gate" in the opening paragraph says where the driver stops but not what the gate is → a reader new to the project cannot tell from the description what parks a run on a finish, or what an EMPTY-OUTPUT run is. One clause each is enough: the tripwire is the check that a run did not change a listed live file; EMPTY-OUTPUT is a run that ended with a blank or missing `output.md`; the spec gate is the operator's approval of a spec before code is written.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. I read the whole diff against the spec's design items 1-10 and against `intake.js` line by line, and confirmed every store-command key and parser option the driver relies on in `factory/cli.py` and `factory/store.py`; I did not run the suite or the acceptance commands, which the verifier runs on this head.
ESCALATIONS:
- Protected paths touched, for the record: `factory/drive.py` (new), `factory/cli.py`, `factory/store.py`, `factory/instance.template.yaml`. All are under `factory/**`, which the sub-ticket and the approved spec's Risk section declare, so the merge gate needs no further approval for them.
