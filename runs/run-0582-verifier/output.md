Commit: 6991572ee604bbf88e7b71af43e9233279029fdb (branch `factory/T-0056.1`; base 3e4705ae6af33c83e680a479beef42d58721511b, which equals `main`)

How I ran it: I checked out the PR head in the given worktree and the base in a detached worktree under my scratch directory, and ran `uv sync --frozen` in each. I wrote each GIVEN block (`t0056-wf.mjs` and `t0056-bin/claude` from the parent spec, `t0043-fixture.sh` from `openspec/specs/factory-stats/spec.md`, `t0051-time.py` from `openspec/specs/harness-suite/spec.md`) to `scratch/tmp`, with `TMPDIR` pointing there. I copied each WHEN out of the input file verbatim (no hand retyping), and ran each from the checkout root under test through the briefing's wrapper. Outputs are in `scratch/pr-acc.txt` and `scratch/base-acc.txt`.

Per criterion:
- NEW | run finish records the transcript's tokens for a run with no reply, and keeps a reply's record | base: `T-0001 already has run run-0001-triage in flight` / `finish=2 2` / `none` / a Python `FileNotFoundError` traceback (the base parser rejects `--transcripts`, so neither run finishes, as the spec expects of "today") | PR: `finish=0 0` / `transcript None None 6 300 4 13 agent-1.jsonl` / `None s2 0.5 1 None None 2 -` / `record 2, transcript 0, none 0`, exactly as expected | PASS
- NEW | A run the intake script starts carries its transcript's tokens | base: `state=parked` / `triage none` | PR: `state=parked` / `triage transcript 7 70 0 3`, exactly as expected | PASS
- NEW | A drive run whose claude process failed records its transcript's tokens | base: `state=parked` / `triage KILLED none` | PR: `state=parked` / `triage KILLED transcript 2 20 0 1`, exactly as expected | PASS
- REGRESSION | README is at most 1,225 lines | base: not run | PR: `readme=within` (README has 1,189 lines) | PASS
- REGRESSION | README describes init's report of a differing agent copy | base: not run | PR: `row=1 step=1 missing=1` | PASS
- REGRESSION | The changelog records issue 108 in one entry without a numbering gap | base: not run | PR: `CONTIGUOUS` / `1` / `3` | PASS
- REGRESSION | README stays within its line budget and both documents pass the whitespace check | base: not run | PR: `readme=within` / `check=0` | PASS
- REGRESSION | The README, the design doc and the changelog describe the launch copy and the route back to checks | base: not run | PR: `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within` / `CONTIGUOUS` / `entries=1 terms=3` / `exit=0` | PASS
- REGRESSION | README opens with the north-star paragraph and stays within its budget | base: not run | PR: `block=1 top=1 metric=1 links=3 readme=within` | PASS
- REGRESSION (intermediate) | `factory/cli.py` stays under 900 lines with its parser, entry point and role list | base: not run | PR: `885 3` (cli.py grew by 5 lines, 880 to 885, which matches the PR description and leaves 14 of the 19-line allowance) | PASS
- REGRESSION (intermediate) | Without --scorecard, stats prints sections A to D and no scorecard | base: not run | PR: the four `## A.` to `## D.` headings, exactly | PASS
- REGRESSION (intermediate) | the harness suite passes and one run finishes in under three minutes | base: `627 passed in 111.33s (0:01:51) | under 180 s` (run for comparison) | PR: `633 passed in 126.75s (0:02:06) | under 180 s`, from the harness-suite scenario's own `t0051-time.py 1 180` | PASS. A caveat: the machine was heavily loaded the whole time (load average 26 to 57 on 10 cores). The gate run of the suite below took 185.97 s, still exit 0. The timed scenario run, made a few minutes later, came in under the bound for both heads, and the PR adds 6 tests and about 15 s over base.
- REGRESSION (intermediate) | `pytest tests/factory/test_drive.py` exits 0 | base: not run | PR: `15 passed in 6.15s`, exit 0 | PASS

Gate suite: PASS
  `git diff --check main...HEAD` (wrapped, from the worktree): exit 0, no output.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory` (wrapped, from the worktree): `633 passed in 185.97s (0:03:05)`, exit 0.

Other checks against the sub-ticket's scope:
- E1 and E3: the README text matches the spec's E1 row and E3 paragraph word for word. The new row is at `README.md:115`, directly after the `| Catch and cost per role …` row at `:114`. `Five pieces` now reads `Six pieces`. The status date at `README.md:13` changed from 2026-10-23 to 2026-10-25, and nothing else in README moved.
- A3: in each script the diff adds the `TRANSCRIPTS` constant and appends ` --transcripts ${TRANSCRIPTS}` to both `run finish` commands. Beyond that, each script gains only one comment line, which the PR description discloses. Evaluated in node, the constant is the literal `"${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"`, which shows JavaScript does not interpolate it.
- A4: all three `run finish` calls in `factory/drive.py` (now `:235`, `:242`, `:584`) pass `--transcripts _transcripts()`.
- A1: `factory/cost.py` still imports nothing from the `factory` package. `transcript_record` reuses `match_transcripts`, which gains an optional `modified_since`, and a `_usages` helper split out of `transcript_usage`. Nothing was copied.

Probes, each run under the wrapper against a throwaway store:
- `--transcripts` naming a directory that does not exist → exit 0, no `claude` key, nothing on stderr → OK
- Two `--transcripts` directories with the transcript only in the second. Its first timestamp equals the run's `started` to the second, it has one malformed line, and its two messages each carry only some of the four usage fields → exit 0. Record: `input 4, cache_read 9, cache_creation 0, output 6`. The second directory is searched, the boundary second matches, the bad line is skipped, and missing fields count 0 → OK
- Two transcripts naming the same run, one starting a second later than the other → the earlier one is recorded (2/0/0/2); the later one's tokens are not added → OK. This is `match_transcripts`' existing rule, which the spec tells A1 to reuse; the code already comments on it (`cost.py:195-196`).
- A transcript naming the run through a symlinked path to the store → recorded (3/0/0/3), because a single candidate is taken → OK
- Finishing an already-finished run again with `--transcripts` → exit 2 → OK (unchanged behaviour)
- `--transcripts ''` → exit 0, no `claude` key → OK. A side effect: an empty directory argument globs `**/*.jsonl` under the current directory. No caller passes an empty value.
- `drive._transcripts()` with `CLAUDE_CONFIG_DIR` unset, set to an empty string, and set to `/a b/c` → `$HOME/.claude/projects`, `$HOME/.claude/projects`, and `/a b/c/projects` → OK
- The scripts' `--transcripts` argument expanded by `sh` with `CLAUDE_CONFIG_DIR="/a b/c"` and with it empty → one argument each, `/a b/c/projects` and `$HOME/.claude/projects` → OK
- What this costs on the operator's machine (counted with `find`; I opened no transcript) → `~/.claude/projects` holds 8,828 `*.jsonl` files, and 54 of them (123 MB) changed in the last 60 minutes → CONCERN, not a criterion; see ESCALATIONS.

Nothing I found shows the fix special-cased to the tested inputs. The decoys in the first NEW scenario, and the probes above, take the general path through `match_transcripts`.

STATUS: VERIFIED
CONFIDENCE: high. The three NEW criteria fail on base for the reason the spec gives and pass on the PR exactly; every REGRESSION criterion and both gates pass; and the probes found no special-casing. The one soft spot is suite timing, which depends on machine load.
ESCALATIONS:
- The cost of each `run finish` on a real machine is unmeasured (the PR lists this as a known gap). With `--transcripts`, every `run finish` lists all 8,828 transcript files on this machine and opens each file modified since the run started. On this machine 54 files (123 MB) changed in the last hour, many of them from other Claude Code sessions. `_opening` reads such a file until a user message names a run, so for a session that never names one it reads the whole file. A role run of an hour could make its `run finish` read on the order of 100 MB. This breaks no criterion of this sub-ticket. Operator step 3, the first real Workflow run and drive run after the upgrade, is the place to time it.
- Suite time margin is thin under load. The gate's suite run took 185.97 s (exit 0); the timed scenario run took 126.75 s on the PR and 111.33 s on base, with load averages between 26 and 57 on 10 cores. T-0056.2 adds more tests to the same suite.
