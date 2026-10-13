## Proposed change

One PR; about 130 changed lines, 27 of them in `uv.lock`.

A. **Parallel suite.**
   - Run `uv add --dev pytest-xdist` (pin `>=3.8.0`). `pyproject.toml`'s `dev` group gains it, and `uv.lock` gains `execnet` and `pytest-xdist` only.
   - Add `[tool.pytest.ini_options]` with `addopts = "-n auto"` to `pyproject.toml`, under a one-line comment: the suite runs across every CPU core so that one run stays well under the 10-minute limit of a single agent tool call.
   - Change no test's code for this part.
   - Confirm that `--collect-only` lists the same test ids as before.

B. **The gate and the verifier's suite checks use the parallel form.** Part A's `addopts` covers them. The gate command in `.factory/instance.yaml` and every scenario command keep their text. Do not edit `.factory/instance.yaml`.

C. **Stand-ins safe to start together.** In `tests/factory/_fixtures.py`, in both `STANDIN` and `BUILD_STANDIN`:
   - Hold an exclusive `fcntl.flock` on a lock file beside the log (for example `log.with_name(log.name + ".lock")`) around the read, increment and write of the `.n-<role>` counter.
   - Import `fcntl` in each stand-in's import line.
   - Change nothing else in either stand-in. Plays, the log line, the times file and the reply stay as they are.
   - Do not change `test_drive_build.py`.

D. **The park reason names a background wait.**
   1. `factory/cli.py`: next to `run_last_message`, add one module constant, a case-insensitive regex for the rule in Decisions: `\bwait(?:ing)?\b|\bstill (?:running|in progress)\b|\bin the background\b`. `run last-message` adds `"waiting": <bool>` to the JSON it prints, from that regex on the `--text` it keeps. Nothing else in the command changes, and the file stays under 900 lines.
   2. `factory/drive.py`:
      - `run_once` keeps the result of its `run last-message` call. It returns `"waiting": True` only when that call returned `waiting` true, and `False` in every other case, including when no call was made or the call failed.
      - `run_role` parks with `EMPTY-OUTPUT from {role}: ended its turn waiting on a background command` when either run returned `waiting` true, and with today's reason otherwise.
      - The phrase is one module constant.
   3. `factory/workflows/intake.js` and `factory/workflows/build.js` make the same change in `runOnce` and `runRole`. `runOnce` returns `waiting` from the `run last-message` clerk reply (`=== true`). `runRole` adds the phrase to the reason when either run's `waiting` is true.
   4. Tests: update the two assertions under Tests to change. Add one new test function to `tests/factory/test_empty_output.py`, using that file's `Store`: a kept message that does not say it is waiting, such as "I could not finish: the input file was missing.", prints `"waiting": false`. Do not import from another test file.

E. **Documents.**
   - `docs/design.md`: at the end of the bullet that starts `- A role run that ends without writing its output is EMPTY-OUTPUT`, add one sentence. It says that when either run's last message says it is still waiting on a command it started, the park reason adds `ended its turn waiting on a background command`, because a plain re-dispatch would end the same way. The routing-table rows stay as they are.
   - `dev/build-harness.spec.md`:
     - In the `factory run last-message` bullet (line 206), add that it also prints `waiting`: whether T says the run is still waiting on a command.
     - In the Empty output item (line 306), add the second reason form next to `EMPTY-OUTPUT from <role>`.
   - `README.md`:
     - Under "Installing the harness", say that the suite runs across every CPU core with pytest-xdist, set in `pyproject.toml`.
     - In the `- **Empty output.**` bullet, add the waiting reason, with the phrase `ended its turn waiting on a background command`. Replace "It is tested, and has not yet fired on a real ticket." with a sentence saying that it has fired on a real ticket. No ticket id goes in the body.
     - Bump the status header's date.
   - `docs/changelog.md`: add entry 71, `71. After issue #106 (2026-10-12), ...`. It records the parallel suite (pytest-xdist), the stand-in lock, the waiting park reason with its phrase, and the rejected in-process route, in the style of entry 57.
   - Do not change any `docs/prompts/` file or role prompt.

## Tests to change

- `tests/factory/test_drive.py:57`, in `test_two_empty_outputs_park_with_both_runs_and_keep_the_last_message`. Its stand-in triage says "still waiting on my commands", and the test asserts `parked["reason"] == "EMPTY-OUTPUT from triage"`. Under the Decision on the park reason it becomes `"EMPTY-OUTPUT from triage: ended its turn waiting on a background command"`.
- `tests/factory/test_empty_output.py:63`, in `test_last_message_is_kept_for_an_empty_output_run`. It asserts that `run last-message` prints exactly `{"ok", "run_id", "last_message"}`. Under the Decision that `run last-message` reports `waiting`, the expected object gains `"waiting": True`, because its text "The suite is still running; ..." is a waiting message. The same file also gains the new test function of Part D.4.

`tests/factory/test_drive_build.py:60` also asserts `== "EMPTY-OUTPUT from reviewer"`, and it does not change. Its stand-in reviewer says `""`, and the driver sends only a non-blank message to `run last-message` (`factory/drive.py:241`, guarded by `and said`), so its reason stays plain. No other existing test pins the old reason or the old `run last-message` output (`grep -rn "EMPTY-OUTPUT from" tests/` lists these three sites). With exactly the two changes above, the full suite passed on the Part D prototype.

