Commit: 41417c1789d40b26370b10f2bdcae6a84f903a9d (branch `factory/T-0043.2`; base `a0f77c9ffdb638dfcb77ec1dde702a861e6796d4`, which is also `main`)

How I ran it. The PR head was checked out in the given worktree. Its tracked tree was clean before and after the runs: `git status` lists only ignored `.venv/` and `__pycache__/`. The base came from a local `git clone` of the worktree, checked out at `a0f77c9` in my scratch directory (`scratch/base`). Both checkouts got `uv sync --frozen` through the wrapper. I copied both GIVEN blocks byte for byte from input.md (lines 314-384 and 445-499), ran each once with `bash`, and confirmed with `diff` that the fixture file matches the block. I then cut each WHEN command from its input.md line without editing it, wrapped it in the briefing's wrapper and ran it with `bash` from the checkout root. The fixtures went to the default `$TMPDIR` (`/var/folders/...`), as `${TMPDIR:-/tmp}` in the commands says. I did not point `TMPDIR` at the scratch directory: that directory lies inside this repo's own instance, so the scratch target that `t0024-inflight.sh` makes with `mktemp -d` would have found that instance when it ran `init`. Outputs are saved in `scratch/pr-*.out`, `scratch/base-*.out` and `scratch/probe1.out`.

Per criterion:
- NEW | Runs and verdicts by role and model (section A, fixture, `--transcripts $F/tx --until 2026-10-08`) | base: `exit=2` (the log says `invalid choice: 'stats'`) | PR: `exit=0` and the seven rows exactly as specified, from `| triage | opus | 3 | 0 | 0 | ACCEPT 2, NEEDS-HUMAN 1 | - | - |` to `| verifier | opus | 1 | 0 | 1 | SPEC-DEFECT 1 | - | - |` | PASS
- NEW | A window bounds the count and writes nothing (`--since 2026-10-03`, with `cksum` before and after) | base: `exit=2 store=unchanged since=0` | PR: `exit=0 store=unchanged since=1` | PASS
- NEW | Parks by normalised reason, with gate and merge decisions (section B) | base: `exit=2` | PR: all seventeen lines exactly as specified, from `exit=0` through `| all parks | 9 |` to `| archive refused | 2 |` | PASS
- NEW | Each downstream spec catch names its writer and critic (section C) | base: `exit=2` | PR: `exit=0`, `| run-0007-implementer | BLOCKED | T-0001.1 | 2 | run-0005-spec_writer | run-0006-critic | 1 |`, `| run-0011-verifier | SPEC-DEFECT | T-0001.1 | 3 | human | none | 1 |`, `| yes | 1 | 1 |`, `| no | 1 | 0 |` | PASS
- NEW | Cost from the record, else the transcript, counted once per call (section D) | base: `exit=2` | PR: all eight lines exactly as specified, ending `| verifier | opus | 1 | 120 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |` | PASS
- NEW | Stats reproduces the hand count on the two live stores (`--until 2026-10-07T12:00`) | base: `exit=2` | PR: `exit=0`, then the critic, implementer, reviewer and two verifier rows, `| NEEDS-HUMAN from triage | 30 |` and `| all parks | 82 |`, all eight lines exactly as specified | PASS. There was no mismatch, so the stores needed no check.
- NEW | Stats reads a live store with a run in flight and an unaccepted harness | base: `here=2 inside=2 store=unchanged own=0 locked=2` (this matches verification.md) | PR: `here=0 inside=0 store=unchanged own=1 locked=2` | PASS
- REGRESSION | Unmarked writes from inside the target are refused while a run is in flight | base: not run | PR: `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` | PASS
- REGRESSION | The refusal names the throwaway store and not the marker | base: not run | PR: `rule=1 state=1 marker=0 json=1 inside=1` | PASS
- REGRESSION | A harness acceptance is refused while a run is in flight | base: not run | PR: `accept=2 store=unchanged` | PASS
- REGRESSION (ST-1) | `.venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |'` | base: not run | PR: `| critic | fable-5 | 1 | 2 | 310 | 17 |` | PASS
- NEW (intermediate) | `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_stats.py` | base, as written: exit 4, `no tests ran` (the file is new). I then copied the PR's file onto the base clone and ran it against base code: `20 failed in 3.57s`, 17 of the log lines being `invalid choice: 'stats'`. That is the failure this sub-ticket's scope implies. Run-0438 handled ST-1's new test file the same way. | PR: `20 passed in 1.76s` | PASS. I read the file, and it covers every item the sub-ticket lists:
  - each section's rows on a port of the fixture;
  - the window, with `--since` inclusive, `--until` exclusive and events windowed by `ts`;
  - each normalisation step;
  - the correction rule: a matching correction, one dated after `--until`, one whose `previous` matches no park, and one dated before every park;
  - the three refusals;
  - an own store with a triage run in flight, read from the target and from `runs/<run>/` under a lock of all zeros, built with `test_live_store_guard`'s `target` and `start_triage`. That test also checks that the store is unchanged and that `ticket show` is still refused.
- REGRESSION (intermediate) | `uv run --frozen pytest -q -p no:cacheprovider tests/factory` | base: not run | PR: `577 passed in 347.35s (0:05:47)`, exit 0 | PASS. This was also the second gate's run.

Gate suite: PASS
  `git diff --check main...HEAD` exited 0 with no output. The harness suite printed `577 passed`, exit 0.

Diff scope: `git diff --stat a0f77c9...HEAD` shows `factory/cli.py` (+45/-3), `factory/stats.py` (new, 235 lines) and `tests/factory/test_stats.py` (new). `factory/cost.py` is not touched; `stats.py` only imports from it (`_records`, `_when`, `gate_failures`, `match_transcripts`, `transcript_usage`). No existing test file changed. The sub-ticket declares both changed protected paths, `factory/cli.py` and `factory/stats.py`.

Special-casing check: I read `factory/stats.py` in full. No fixture value, run id, ticket id or expected figure appears in it. The figures come from general rules: `CHANGED`, the `BLOCKING` regex, `PARK_RULES`, role order from `cli.ROLES`, and the cost source chosen per run.

Probes (on an extended copy of the fixture; script and output in `scratch/probe1.sh` and `scratch/probe1.out`):
- More runs in s1: a planner, two runs of an unknown role `retro` (models `zeta` and `alpha`), a second critic REVISE on T-0002 (a ticket with no approval), and a reviewer output holding `* [BLOCKING]`, `  1. [BLOCKING]`, `2. [BLOCKING]`, `BLOCKING d`, `  [BLOCKING]` and `- [BLOCKING] f RESOLVED`. Result:
  - rows are ordered triage, spec_writer, critic, planner, implementer, reviewer, verifier, then `retro | alpha` and `retro | zeta`;
  - critic becomes `4 | 0 | 2 | APPROVE 2, REVISE 2`;
  - reviewer BLOCKING goes from 1 to 4: the three marker forms the spec allows count, and `2.`, the bare word and the RESOLVED line do not;
  - section C's yes/no rows are unchanged, because T-0002 has no approval.
  → OK. The counts follow the rules, not the fixture.
- The same instant given as `--until 2026-10-03T11:00:00+00:00`, as `--until 2026-10-03T12:00+01:00`, and as `2026-10-03T11:00` with no zone → identical tables → OK. A zone is honoured, and a WHEN with no zone is read as UTC.
- `normalise()` boundaries:
  - 6-character hex and all-digit 7-character strings are kept;
  - a 41-character hex string is kept;
  - a 40-character hex string becomes `<sha>`;
  - `T-0001.1.2` becomes `<ticket>` and `run-0440-verifier` becomes `<run>`;
  - `a: b: c: d` becomes `a: b`, `archive: ` becomes `archive`, and a multi-line reason keeps only its first line.
  → OK
- Malformed input:
  - `--until 2026-13-01` exits 2 with `--until '2026-13-01' is not an ISO date or date-time`;
  - an empty directory exits 2;
  - a missing path exits 2;
  - a directory with only `log/` exits 0 with `| all parks | 0 |`;
  - a `--transcripts` directory that does not exist exits 0 and places no transcript;
  - a run record with no `started` is left out of every section and does not crash the command.
  → OK
- `--since ''` (an empty WHEN) exits 0 and is treated as no lower bound, not refused → CONCERN (minor). `stats_cmd` tests `if a.since`, so an empty string skips parsing. No acceptance criterion pins this and it is not special-casing, so it is not a FAIL.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command printed its exact THEN lines on the PR head and failed on base for the reason verification.md states, both gates passed, and probes off the fixture show the counts follow the rules.
ESCALATIONS:
- Minor, outside the acceptance criteria: an empty `--since ''` or `--until ''` is accepted as no bound rather than refused as an unparsable WHEN. The Decisions say an unparsable WHEN is refused with exit 2. Whether an empty value counts as unparsable is the operator's call; it could be tightened in ST-3 or later.
