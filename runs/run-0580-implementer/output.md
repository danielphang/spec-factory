Sub-ticket: T-0056.1, Record every run's tokens: `run finish --transcripts`, passed by both Workflow scripts and the driver (parent `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0056/v3.md`). Branch `factory/T-0056.1`, commit `6991572` on base `3e4705a`.

## What changed

Before this change, a run's cost record (its tokens and dollars, kept under `claude:` in the run's `meta.yaml`) came only from the reply of a `claude -p` process. Only `factory drive` gets such a reply. Runs started by the Workflow scripts, and drive runs whose process failed or was stopped, recorded nothing. Their tokens were only in the transcript Claude Code writes for each agent.

**A1, `factory/cost.py`.**
- New `transcript_record(dirs, store, run_id, started)`. It calls `match_transcripts(dirs, [store], modified_since=started)`, which applies the existing matching rule for that one store, and takes the entry for the run. It then sums the four usage fields, counting each message id once, and returns `{"source": "transcript", "transcript": <path>, "usage": {…four fields…}, "total_cost_usd": None}`, or `None` when no transcript matches.
- `match_transcripts` gains an optional `modified_since`: when it is set, a file modified before it is not opened. When it is `None` the function behaves as before. Its callers are `factory/stats.py:116` and `tests/factory/test_cost_once.py`, and none of them pass the new argument.
- The per-message-id loop that was inside `transcript_usage` moved into a new helper, `_usages`, so the new function reuses it instead of copying it. `transcript_usage` returns the same values as before. Its callers are `cost.py` `tally` and `stats.py:225`.
- `cost.py` still imports nothing from the `factory` package.

**A2, `factory/cli.py`.**
- `run finish` gains `--transcripts DIR` (`action="append"`, default `[]`).
- The transcript record is used only when a directory was given and the `claude` value has no `usage` mapping: no `--reply`, or a reply that is not a JSON object or has no `usage`. A reply with usage keeps its current shape. An unusable reply with no matching transcript still records `claude: null`. A run with no reply and no transcript gets no `claude` key, as today. My first draft wrote `claude: null` in that last case. The new test `test_run_finish_opens_no_transcript_modified_before_the_run_started` caught it, and I fixed it before committing.
- **`cli.py` grew by 5 lines (880 to 885): one changed import line, 3 lines in `run_finish`, 2 in the parser. That leaves 14 of the 19-line allowance for T-0056.2.**

**A3, `factory/workflows/intake.js` and `build.js`.** Each script gets `const TRANSCRIPTS = '"${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"'`. It is a single-quoted string, so JavaScript passes the text through unchanged and the clerk's shell expands it. ` --transcripts ${TRANSCRIPTS}` is appended to both `run finish` commands in each script: the normal one and the KILLED one. I also added a one-line comment above the constant explaining why it is a plain string. The design says "change nothing else", so the reviewer may want that comment gone.

**A4, `factory/drive.py`.** New `_transcripts()` returns `$CLAUDE_CONFIG_DIR/projects` when that variable is set and non-empty, else `os.path.expanduser("~/.claude/projects")`. It reads the driver's own environment, which its role processes inherit. All three `run finish` calls pass `--transcripts _transcripts()`: the failed-call KILLED one, the normal one, and the one in `stop()`.

**D (A's share): `tests/factory/test_transcript_record.py`**, a new file.

**E1, README "What depends on Claude Code".** `Five pieces` becomes `Six pieces`, and the row worded in E1 now follows the `| Catch and cost per role …` row.

**E3, README "Counting what each role catches and costs".** The paragraph that began "A run started by `factory drive` carries a cost record" is replaced with E3's text, word for word. On `3e4705a` it was at `README.md:983-989`, not at the `977-983` the spec cites.

**README budget and date.** README grows from 1,184 to 1,189 lines, inside both the raised 1,225 bound and the 30-line allowance for the whole change. The status header date (`README.md:13`) moves from 2026-10-23 to 2026-10-25, because `run finish` changed (see Known gaps).

## Acceptance results

I wrote each GIVEN block to my scratch directory, taken from the parent spec (`t0056-wf.mjs`, `t0056-bin/claude`) and from `openspec/specs/factory-stats/spec.md` (`t0043-fixture.sh`). Each WHEN ran from the worktree through the briefing's wrapper, with `TMPDIR` set to the scratch directory so that `${TMPDIR:-/tmp}` found those files.

- **NEW: run finish records the transcript's tokens for a run with no reply, and keeps a reply's record.**
  - Before: `finish=2 2`, `none`, then a Python `FileNotFoundError` traceback. This matches the spec's "today".
  - After: `finish=0 0` / `transcript None None 6 300 4 13 agent-1.jsonl` / `None s2 0.5 1 None None 2 -` / `record 2, transcript 0, none 0`. Expected output, exactly.
- **NEW: A run the intake script starts carries its transcript's tokens.**
  - Before: `state=parked` / `triage none`.
  - After: `state=parked` / `triage transcript 7 70 0 3`. Expected.
- **NEW: A drive run whose claude process failed records its transcript's tokens.**
  - Before: `state=parked` / `triage KILLED none`.
  - After: `state=parked` / `triage KILLED transcript 2 20 0 1`. Expected.
- REGRESSION, README at most 1,225 lines: `readme=within`.
- REGRESSION, README describes init's report of a differing agent copy: `row=1 step=1 missing=1`.
- REGRESSION, changelog records issue 108: `CONTIGUOUS` / `1` / `3`.
- REGRESSION, README within budget and whitespace check: `readme=within` / `check=0`.
- REGRESSION, launch copy and route back to checks: `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within` / `CONTIGUOUS` / `entries=1 terms=3` / `exit=0`.
- REGRESSION, north-star paragraph: `block=1 top=1 metric=1 links=3 readme=within`.
- Intermediate REGRESSION, `cli.py` size: `885 3`.
- Intermediate REGRESSION, stats without `--scorecard`: the four headings `## A. …`, `## B. …`, `## C. …`, `## D. …`, exactly.
- Intermediate REGRESSION, `test_drive.py` on its own: `15 passed in 3.01s`.
- Gate `git diff --check main...HEAD`: exit 0.
- Gate, the full suite: `633 passed in 144.66s (0:02:24)`, exit 0. That is under the three-minute bound.

No REGRESSION command failed, so none needed re-running on the base.

## Tests added/changed

Added `tests/factory/test_transcript_record.py`, six tests:
- `test_run_finish_records_the_runs_transcript_and_passes_over_its_two_decoys`: the record's exact shape and path. The matching transcript repeats message `m1`, which is counted once. The two decoys are a transcript naming `run-9999-triage` and one dated 2026-01-01.
- `test_run_finish_opens_no_transcript_modified_before_the_run_started`: a transcript that would match, with its modification time set to 1970, is not taken. This tests the modification-time floor, and also that a run with no reply and no transcript gets no `claude` key.
- `test_a_reply_with_usage_wins_over_the_transcript`: the reply is recorded exactly as before.
- `test_an_unusable_reply_takes_the_transcript_and_keeps_null_without_one`.
- `test_build_js_passes_transcripts_on_the_normal_run_finish` and `test_build_js_passes_transcripts_on_the_killed_run_finish`. These run build.js under node, as `_fixtures.BUILD_DRIVER` does, on the `f` store fixture with a single sub-ticket. The role stand-in writes a transcript under `$CLAUDE_CONFIG_DIR/projects`, then either returns nothing or throws. Each `run finish` clerk command must end with the `--transcripts` argument, and each implementer run must record its own agent's transcript. The normal case re-dispatches the empty output once, so it checks that two runs each get their own transcript.

All six failed before the code change and pass after it. No existing test changed.

## Known gaps and uncertainties

- **Status date.** README's rule says to bump the status header to the merge date. I don't know the merge date, so I used today's date, 2026-10-25. If the merge lands on another day, the line needs that date.
- **The comment line in each script.** As noted under A3, the comment above `TRANSCRIPTS` goes beyond the letter of "change nothing else".
- **Coding rule 6 guard not added.** Rule 6 asks that a new path outside the repository ship with an autouse fixture that fails any test resolving that path outside `tmp_path`. A4's `~/.claude/projects` is such a path. The fixture would have to go in `tests/factory/conftest.py`, an existing test file this sub-ticket may not touch. The risk is a read, not a write. The suite runs with a throwaway HOME, but if `CLAUDE_CONFIG_DIR` is set in the shell that runs the suite, the drive tests would scan the operator's real transcript directory, read-only. Nothing there names a test's run, so nothing would match. It was unset when I ran the suite.
- **Cost of each `run finish` not measured on a real store.** With `--transcripts`, every `run finish` now reads the store's event log (as `match_transcripts` already does, to follow `store.migrated`), lists every `*.jsonl` under the transcript directory, and checks each file's modification time. It opens only files modified since the run started. I did not time this against the real `~/.claude/projects`, because that would read the operator's home directory. Operator step 3 (a real Workflow run and a real drive run after the upgrade) is the first real measurement.
- **Not checked against real Claude Code.** The scenarios use stand-ins for Claude Code. That the real Workflow agent's transcript lands under `$CLAUDE_CONFIG_DIR/projects` or `~/.claude/projects`, and that its first user message names the run's `input.md`, rests on the existing `match_transcripts` rule and the spec's evidence. Operator step 3 confirms it.
- **The suite has 35 seconds of margin.** It took 145 s against a bound of 180 s. T-0056.2 adds more tests.
- factory: markers added: none.

## Out-of-scope observations

- The spec's E3 cites `README.md:977-983` from `1321c17`. On `main` (`3e4705a`) the paragraph is at `983-989`. The text was unchanged, so the replacement applied as written.
- Launch copies written before this merge still call `run finish` without `--transcripts`. Operator step 2 already covers this: write fresh copies with `factory launch-script` after the upgrade.

## Protected paths

`factory/cost.py`, `factory/cli.py`, `factory/drive.py`, `factory/workflows/intake.js` and `factory/workflows/build.js`. All five are under `factory/**`, which the sub-ticket declares. No other protected path changed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, all three NEW acceptance commands print the expected lines after the change (and the spec's "today" lines before it), and every REGRESSION command and both gates pass on commit 6991572
ESCALATIONS: none
