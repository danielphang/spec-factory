Commit: e375b16232346cc46947937e750c4f3be25a7472 (branch `factory/T-0043.1`, base 5215c5f8449c4e09e89acd27bd99f64fb3fc1ba9)

Setup. The PR head is the run worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0438-verifier/wt`, which had a clean status at e375b16. The base is a `git archive` export of 5215c5f, made in `scratch/base`. Running `uv sync --frozen` succeeded in both. The spec's fixture GIVEN block was copied verbatim from input.md lines 304-374 to `scratch/given.sh` and run once (exit 0). It wrote `$TMPDIR/t0043-fixture.sh`. Every command below ran through the briefing's wrapper.

Per criterion:
- NEW | `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && .venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |')` | base: `| critic | fable-5 | 1 | 5 | 725 | 33 |` (as the spec states) | PR: `| critic | fable-5 | 1 | 2 | 310 | 17 |` (exactly the THEN line) | PASS
- NEW (intermediate) | `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_cost_once.py` | base: the file does not exist on base, so the PR's file was copied into the base export and run against base `factory/cost.py`. Result: `11 failed in 0.07s`, each on a missing attribute (AttributeError), which is the failure the sub-ticket's scope implies. | PR: `11 passed in 0.04s` | PASS. I read the file, and it covers each item the sub-ticket lists:
  - `tally()` on repeated ids, plus records with no id;
  - the own path preferred, including the path before a `store.migrated`;
  - the relay message skipped;
  - another given store's path ruled out;
  - the started/finished window, both edges;
  - a single remaining candidate taken, and two not taken;
  - `gate_failures()` for a failure fixed later, one never fixed, and no gate line (returns None).
- REGRESSION (intermediate) | `uv run --frozen pytest -q -p no:cacheprovider tests/factory` | base: not run | PR: `557 passed in 389.46s (0:06:29)`, exit 0 | PASS. This was also the second gate's run.

I checked the unchanged-interface condition with `git diff 5215c5f HEAD -- factory/cost.py | grep '^[-+].*print'`, which prints nothing. No header or row print line changed. Running `python -m factory.cost` on all four fixture transcript dirs still prints the same header and total row.

Gate suite: PASS
  `git diff --check main...HEAD`: exit 0, no output. `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: 557 passed, exit 0 (scratch/suite.log).

Probes (script `scratch/probe.py`, run on the PR's `factory/cost.py`):
- Interleaved ids (m1, m2, then m1 again with larger usage), plus a malformed JSON line and a blank line → `transcript_usage` = `(2, 12, 12)`: it kept m1's last record and m2, and skipped the bad lines → OK
- Empty transcript → `(0, 0, 0)` → OK
- `meta.yaml` with unquoted, zone-less `started`/`finished` (YAML gives a naive datetime), and a run in flight (`finished: null`) whose transcript starts four days after `started` → both matched to their transcripts; the transcript's first message uses list-form content → OK
- Gate line present but naming no backticked command → `None` (not recorded), as the PR's Known gaps says → OK
- A test-driven "red then green" run of one new test file, `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_new.py` failing and then passing, with the gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `gate_failures` = 1 → CONCERN, outside this sub-ticket's criteria; see ESCALATIONS. The code follows the spec's rule ("a Bash call containing it"), so this is not a special case and not a FAIL.
- `python -m factory.cost` on the base gave 5 calls for the same input where the PR gives 2. The fix is the general once-per-id rule, not a hard-coded fixture value: the interleaved and no-id probes above give the counts the rule predicts → OK

Protected path touched: `factory/cost.py`. The sub-ticket declares it, and the change stays inside part A.

STATUS: VERIFIED
CONFIDENCE: high. The NEW criterion fails on base exactly as stated and passes on the PR. The new tests fail on base code and pass on the PR. The full suite and both gates pass. Probes off the tested inputs behave as the spec's rules say.
ESCALATIONS:
- The gate rule overcounts test-driven work. ST-2's "gate fails fixed before hand-off" column comes from `gate_failures()` here. That function counts any Bash call whose command *contains* a gate command's text, which is what the spec's Decisions say. A gate such as `pytest ... tests/factory` is a prefix of the implementer's own one-file runs, such as `pytest ... tests/factory/test_new.py`. So the "red" step of test-first work (a new test written to fail, then made to pass) counts as a gate failure fixed before hand-off. My probe shows exactly that: one red/green run of a single test file returned 1. The README limit planned for ST-3 names only the opposite error, a gate run in another form being missed. For the operator or the spec owner: either accept this inflation and state it beside that limit, or tighten the match (for example, require the gate text to be followed by end of command, a space, `)`, `|` or `;`). This is a design question for ST-2/ST-3. It does not affect this sub-ticket's criteria.
