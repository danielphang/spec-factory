Commit: e033e2752bc1202be70c51bed01967c2bb1c19da (main; base 5215c5f8449c4e09e89acd27bd99f64fb3fc1ba9)

How this was run. This is a parent close, so I verified the merged `main` head in the run worktree. For the base, I made a local clone in my scratch directory, checked out 5215c5f and pointed its `main` at 5215c5f. I ran `uv sync --frozen` in both. I extracted both GIVEN blocks and all 12 WHEN commands verbatim from `.factory/store/specs/T-0043/v2.md`, and built each expected output from the backticked items of its THEN line. Each GIVEN and WHEN ran through the briefing's wrapper, from the checkout root, with `TMPDIR` set to a per-checkout directory under `scratch/`, and was compared with `diff`. Every PR result below is an exact match. Every base result is the output that `verification.md` predicts.

Per criterion:
- NEW | Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures | base: `exit=2` (`invalid choice: 'stats'`) | PR: the 8 expected lines exactly | PASS
- NEW | A window bounds the count and the command writes nothing | base: `exit=2 store=unchanged since=0` | PR: `exit=0 store=unchanged since=1` | PASS
- NEW | Parks are grouped by normalised reason, with gate and merge decisions | base: `exit=2` | PR: the 17 expected lines exactly | PASS
- NEW | Each downstream spec catch names the runs that wrote and critiqued its spec | base: `exit=2` | PR: the 5 expected lines exactly | PASS
- NEW | Cost comes from the run record, else the transcript of that store's run, counted once per call | base: `exit=2` | PR: the 8 expected lines exactly | PASS
- NEW | The transcript cost report counts each message once | base: `| critic | fable-5 | 1 | 5 | 725 | 33 |` | PR: `| critic | fable-5 | 1 | 2 | 310 | 17 |` | PASS
- NEW | Stats reproduces the hand count on the two live stores | base: `exit=2` | PR: the 8 expected lines exactly, run against both live stores as they stand now | PASS
- REGRESSION | Unmarked writes from inside the target are refused while a run is in flight, init included | base: not run | PR: `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` | PASS
- REGRESSION | The refusal names the throwaway store and not the marker | base: not run | PR: `rule=1 state=1 marker=0 json=1 inside=1` | PASS
- REGRESSION | A harness acceptance is refused while a run is in flight | base: not run | PR: `accept=2 store=unchanged` | PASS
- NEW | Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing | base: `here=2 inside=2 store=unchanged own=0 locked=2` | PR: `here=0 inside=0 store=unchanged own=1 locked=2` | PASS
- NEW | The documents record factory stats | base: every flag `no`, `principles-old=yes`, then `CONTIGUOUS`, `0`, `clean` | PR: `readonly=yes ... principles-old=no buildspec=yes prompts=0`, then `CONTIGUOUS`, `4`, `clean` | PASS

On this head `main` equals HEAD (e033e27), so `main...HEAD` is an empty range. That makes the `prompts=0` and `clean` parts of the last scenario, and the first gate command, pass without checking anything. To give them a real range, I also ran them against the base: `git diff --check 5215c5f...HEAD` exited 0, and `git diff --name-only 5215c5f...HEAD -- docs/prompts factory/prompts` listed 0 files.

Gate suite: PASS
  `git diff --check main...HEAD` exited 0 (empty range, see above).
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `577 passed in 345.23s` and exited 0.

Probes (my own small store under `scratch/probe`, through the wrapper):
- Window boundaries: `--since 2026-10-05 --until 2026-10-06`, with a run that started exactly at `--until` and a run whose `started` has no zone. The run at `--until` is left out, because the window excludes its end. The run with no zone is read as UTC and counted. → OK
- A park correction dated exactly at `--until` is not applied ("dated before"). → OK
- Park normalisation: `spec drift at abcdef1 and 1234567 by run-0042-planner on T-12.3.4` becomes `spec drift at <sha> and 1234567 by <run> on <ticket>`, since an all-digit hex string has no letter and is kept. `a: b: c: d` becomes `a: b`. → OK, rules applied in general, not only to fixture strings.
- BLOCKING markers: in one review output, `  * [BLOCKING]`, `1. [BLOCKING]`, `2. [BLOCKING]`, `[BLOCKING] ... RESOLVED` and a mid-line `[BLOCKING]` count as 2. That is the spec's literal rule, which allows only a `-`, `*` or `1.` marker (`factory/stats.py:30`). So a `2.`-numbered finding is not counted. → CONCERN, see ESCALATIONS. Not a FAIL: it matches the approved Decision.
- Refusals: a `--store` with neither `runs/` nor `log/` gives exit 2. A missing path gives exit 2. `--since yesterday` gives exit 2. No `--store` and no `FACTORY_STATE`, from a directory outside any instance, gives exit 2 with a message naming the three options. `FACTORY_STATE=<store>` with no `--store` reads that store. → OK
- An empty store (only `runs/`) gives exit 0 and prints all four section headings. → OK
- `python -m factory.cost` on two usage records with no message id counts them as 2 calls (each counted alone). → OK

Out-of-scope observations:
- `python -m factory.cost` labels the role `?` when the transcript's opening lacks the role pattern it looks for. This behaviour predates this change and is not in its criteria.

STATUS: VERIFIED
CONFIDENCE: high. All 12 scenarios were run verbatim from the pinned spec on both base and head, every result matched exactly, and the full suite passed. The only weak spot is that the `main...HEAD` checks are empty on a parent close, and I covered them with the base range.
ESCALATIONS:
- BLOCKING findings in a numbered list are undercounted. The approved rule (Decisions, and `factory/stats.py:30`) accepts only `1.` as a numbered-list marker. A reviewer or critic that writes `2. [BLOCKING] ...` for its second finding has that finding left out of section A's BLOCKING column. The shipped code follows the spec, so this is not a defect of the change. If reviewers write numbered findings, the figure the operator relies on will read low. The operator decides whether to widen the rule to any `N.` marker.
