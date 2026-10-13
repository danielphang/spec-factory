Commit: 5e00a1f5261b2576ae6243b46ac8895f71042ff9 (branch `factory/T-0051.1`, base `88c65e147495debccaef62986a15df1ee54b59f4`; two commits, `ac71304` the change and `5e00a1f` one `factory:` comment)

## Review, round 1

What I checked, in the prescribed order, by reading the diff (13 files, +109/-28, 27 of the added lines in `uv.lock`) and the surrounding code in the worktree.

**1. Test integrity.** Two existing test files change, both exactly as the spec's Tests to change lists them:
- `tests/factory/test_drive.py:57`: the expected reason gains the waiting suffix. The stand-in triage in that test says "still waiting on my commands", so the new reason is the one the spec's Decision requires. No other assertion in the function changes.
- `tests/factory/test_empty_output.py:63`: the expected object gains `"waiting": True`; the text under test says "still running". Nothing else in the assertion loosens (it is still `==` on the whole object).
- `tests/factory/test_empty_output.py:67-71`: one new test, `test_last_message_that_is_not_about_waiting_prints_waiting_false`, as Part D.4 asks, using that file's `Store`, no import from another test file, asserting `is False` (not merely falsy).
- `tests/factory/_fixtures.py` changes under Part C. It does not match the harness's test-file rule `TEST_FILE_RE` at `factory/drift.py:38` (`test_*`, `*_test.*`, `*.test.*`), as the spec's Risk says. Nothing else in either stand-in changed: the log line, plays, sleep, reply and times file are the same lines as before.
- No test removed, no skip or xfail, no swallowed error, nothing hard-coded. `tests/factory/test_drive_build.py` is untouched, as Part C requires.

**2. Correctness against the spec's intent.**
- Part A (`pyproject.toml:8-17`): `pytest-xdist>=3.8.0` in the `dev` group, `[tool.pytest.ini_options] addopts = "-n auto"` under a one-line comment. `uv.lock` adds exactly `execnet` 2.1.2 and `pytest-xdist` 3.8.0 plus the dev-group references.
- Part B: no edit, and none needed; `addopts` reaches the gate command (`uv run --frozen pytest ...`) and every scenario command. `.factory/instance.yaml` untouched.
- Part C (`_fixtures.py:228-233` and `:301-306`): exclusive `fcntl.flock` on `<log>.lock` around read, increment and write of `.n-<role>`. The lock is released when the `with` closes the file; `nf.write_text` happens inside it, so the truncate-then-write window the Root cause names is covered. Opening the lock file with `"w"` truncates an empty file; harmless.
- Part D.1 (`factory/cli.py:298-301, 311-312`): `WAITING` is the spec's regex, case-insensitive; `re` was already imported (`cli.py:11`); `--text` is `required=True` (`cli.py:725`), so `WAITING.search(a.text)` never sees `None`. File is 891 lines, under the 900 cap.
- Part D.2 (`factory/drive.py:51-53, 185-186, 245-250`): `run_once` sets `waiting = False`, then `call(...).get("waiting") is True` only on the EMPTY-OUTPUT-and-said path. `call()` (`drive.py:57-83`) always returns a dict and never raises, so a refused or failed `run last-message` yields `False`, as the Decision requires. `run_role` reads `first["waiting"] or second["waiting"]` only after both have been confirmed non-None dicts, so no `KeyError`/`TypeError` on the park path.
- Part D.3 (`build.js:66-68, 78-79, 135-141, 145`; `intake.js:75-77, 87-88, 131-137, 141`): same shape. `clerk()` in both scripts always returns an object (`build.js:46-57`, `intake.js:55-66`), so `kept.waiting === true` is safe on failure. `first.waiting || second.waiting ? WAITING_REASON : ''` parses as `(a || b) ? x : y`, the intended reading. Every other `return` in both `runOnce` functions is `null`, which `runRole` already handles.
- Part E: design doc sentence appended to the right bullet (`docs/design.md:106`); build spec lines 206 and 306 updated; README "Installing the harness" names pytest-xdist and where it is set, the Empty output bullet gives the phrase verbatim and drops "has not yet fired" with no ticket id; status date bumped; changelog entry 71 follows 70 with no gap and names all five terms the scenario greps for. No `docs/prompts/` or `factory/prompts/` file in the diff.
- Edge cases the spec implies: a run whose last message is blank sends nothing to `run last-message` (guarded by `and said`), so `test_drive_build.py:60`'s plain reason is preserved, as Tests to change predicts. `factory stats` (`factory/stats.py:50-56`, `normalise`) keeps the first two `: `-separated fields, so the waiting form becomes its own row, exactly as the Risk section states; no parser there expects a fixed EMPTY-OUTPUT shape.

**3. Scope.** Every changed file is covered by a lettered part. No extra refactor, no renamed identifier, no unrelated line.

**4. Silent behavior changes.** `run last-message` prints one more key. Its only consumers (grep over `factory/`, `bin/`, `agents/`: `drive.py:247`, `build.js:137`, `intake.js:133`) are the three callers this change updates. `-n auto` now applies to every `pytest` invocation from the repo root, including a single-test run; that is the spec's stated design (Decisions, Part B), not a surprise.

**5. Security and data safety.** Nothing new reaches outside the store or the repo. The lock file sits beside the test log in `tmp_path`. The `--text` value was already shell-quoted in both scripts; the quoting is unchanged.

**6. Protected paths.** Touched: `pyproject.toml`, `uv.lock`, `factory/cli.py`, `factory/drive.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`. All six are on the approved spec's Risk `Protected paths:` line. Listed under ESCALATIONS for the record; not an escalation.

**7. Coding standard.** Rule 1: `fcntl` is stdlib, taken at rung 2; no new helper or abstraction added; `WAITING_REASON` is one constant per runtime as the spec asks. Rule 2: the PR names the callers of `run_once`/`runOnce` and `run last-message` from a grep, and I confirmed the list above. Rule 3: the one heuristic (`WAITING`) carries a `factory:` comment naming its limit and upgrade trigger (`cli.py:299-300`), and Known gaps lists it. Rule 5: `waiting` is the spec's term, used as the JSON key, the Python and JS field, and the doc wording. Over-building pass: Lean already.

**8. PR description.** What changed opens with the problem for the reader (suite time, stand-in crash, park reason), glosses "harness suite" and "park" at first use, then walks the lettered parts in words. Known gaps names the timing-machine caveat, the `uv sync` step, the heuristic's limit with its marker, the README placement tension, and the one build-spec paragraph it left. Readable at the gate as it stands.

## Findings

- [NIT] dev/build-harness.spec.md:276: the `runRole` paragraph still says a second EMPTY-OUTPUT "parks `EMPTY-OUTPUT from <role>`" with no mention of the waiting form → a reader who stops at that paragraph sees only one form of the reason. It points to item I.5 (line 306), which now gives both, and the spec's Part E listed only lines 206 and 306, so this stays a nit and the implementer already disclosed it in Known gaps. Not a reason to hold the merge.

Prior findings: n/a (round 1)

STATUS: APPROVE
CONFIDENCE: high. Every lettered part is present and matches the spec's Decisions line for line; the two assertion changes are exactly those listed; the failure paths (`call()`, `clerk()`) were read and never throw, so the new `waiting` read is safe; no undeclared protected path is touched.
ESCALATIONS: none. For the record (declared on the spec's Risk line, so the merge gate accepts them): `pyproject.toml`, `uv.lock`, `factory/cli.py`, `factory/drive.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`.
