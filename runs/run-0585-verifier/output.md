Commit: fa0d3b5e26a0c591316cfa2d56b46156f742d293 (branch `factory/T-0056.2`). Base: b863e4ec2b2c147e6133e73fc9ba5d50f2b6f494, the integration branch with T-0056.1 merged, checked out as a separate detached worktree under scratch and removed afterwards.

How I ran the checks: I copied each WHEN command byte for byte from the sub-ticket into its own file (`scratch/cmd/c01.sh` to `c16.sh`). I ran each one under bash through the briefing's wrapper, from the PR worktree and from the base worktree, after `uv sync --frozen` in each. `TMPDIR` pointed at `scratch/tmp`, so the fixture files were private to this run. I wrote the two fixture files, `t0056-fixture.sh` and `t0043-fixture.sh`, by running the heredoc blocks extracted from `specs/T-0056/v3.md:257` and `openspec/specs/factory-stats/spec.md:13`. The first 63 lines of the t0056 block are identical to the block in my input. A script compared the PR output of every command except the `wc -l` one line for line with the backticked THEN text. All 15 compared commands printed `MATCH`; I checked the `wc -l` one by hand.

Per criterion:
- NEW | scorecard, both windows, both kinds, writes nothing | base: `exit=2 store=unchanged` only, because `--scorecard` is an unknown flag | PR: all 25 lines exact, `exit=0 store=unchanged` | PASS
- NEW | scorecard takes tokens from the transcript | base: no output (rc 1) | PR: `… 450 (1 of 1) | 3890 (2 of 2) |` and `… record 2, transcript 0, none 0 | record 4, transcript 2, none 0 |`, exact | PASS
- NEW | refuses a missing --since and a malformed target_is_factory | base: `no-since=2 0 bad-setting=2 0 good=2` | PR: `no-since=2 1 bad-setting=2 1 good=0` | PASS
- REGRESSION | without --scorecard, stats prints sections A to D | base: not run | PR: the four `## A.` to `## D.` headings, exact | PASS
- NEW | escape recorded, link kept only as a hash, counted | base: `… recorded=2 printed=0/0 link-in-store=0`, `events=0 fields= hash=differ`, no Escapes row (`escape` is not a command) | PR: `no-merge=2 sub-ticket=2 unknown=2 empty=2 link-note=2 refused-wrote=0 recorded=0 printed=1/0 link-in-store=0`, `events=1 fields=by,issue_sha256,note,ticket hash=match`, `| Escapes | 0 | 1 (T-0001) |` | PASS
- NEW | intervention counted by the scorecard | base: `unknown=2 recorded=2`, no row | PR: `unknown=2 recorded=0`, `| … interventions | 0 | 1 |` | PASS
- NEW | README and the template describe the scorecard, the two records and the token record | base: `scorecard=no setting=no escape=no hash=no intervene=no record=yes old=no depends=yes pieces=yes template=no`, `built=long`. This is the base the sub-ticket predicts | PR: `scorecard=yes setting=yes escape=yes hash=yes intervene=yes record=yes old=no depends=yes pieces=yes template=yes`, `built=pointer` | PASS
- REGRESSION | drift checks live in factory/drift.py | base: not run | PR: exact list | PASS
- REGRESSION | shared helpers and fence in factory/common.py | base: not run | PR: exact list | PASS
- REGRESSION | setup in factory/setup.py | base: not run | PR: exact list | PASS
- REGRESSION | gates in factory/gates.py | base: not run | PR: exact list | PASS
- NEW | human decisions live in factory/human.py | base: the list without `escape_add intervention_add` | PR: `… decision_add escape_add intervention_add request_changes resolve spec_amend`, exact | PASS
- REGRESSION | cli.py under 900 lines, 3 anchors | base: not run (base printed `885 3` in my full run) | PR: `899 3` | PASS
- REGRESSION | README at most 1,225 lines; whitespace check | base: not run | PR: `readme=within`, `check=0` | PASS
- REGRESSION | the change adds at most 30 lines net to README (≤ 1,214) | base: not run | PR: `net=within` (README has 1,212 lines per the diff stat, +23) | PASS
- REGRESSION | run finish records the transcript's tokens, keeps a reply's record | base: not run | PR: `finish=0 0`, `transcript None None 6 300 4 13 agent-1.jsonl`, `None s2 0.5 1 None None 2 -`, `record 2, transcript 0, none 0` | PASS
- REGRESSION | harness suite passes in under three minutes | base: not run | PR: `647 passed in 113.52s (0:01:53)`, the gate run below | PASS

Every NEW criterion fails on base for the reason the spec gives: the commands, the flag and the README text do not exist yet. None of them passes on both.

Gate suite: PASS
- `git diff --check main...HEAD`, run as written through the wrapper: exit 0. Here `main` is at b863e4e, the base.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run as written through the wrapper: `647 passed in 113.52s (0:01:53)`, exit 0. Load averages were 17.6 to 23.3 during this run. The implementer timed the suite at 248.59 s under load averages of 44 to 50. This run is under the three-minute bound, so their timing escalation does not reproduce here.

Probes:
- The t0056 fixture with `--until 2026-10-17`, a 9-day window, which brings T-0006 in and moves T-0001's escape before the end. I computed the expected values by hand from the fixture before reading the output, and every cell matched:
  - previous window Escapes `1 (T-0001)`, current `1 (T-0002)`;
  - CLI decisions 3 and interventions 3, so 6 / 3 changes = `2.0`;
  - wall time `0.9 h (0.0 to 3.5 h)`;
  - lead time `54.0 h (6.0 to 144.0 h)`;
  - tokens with `--transcripts` `1200 (3 of 3)`, the median of 6580, 1200 and 0.

  The code is not fitted to the scenario's dates. → OK
- The same window, where T-0006 is a closed change that has a merge but no run records. Its wall time counts 0.0 h, and the tokens row counts it as a change "whose every run has tokens", with 0 tokens: `600 (2 of 3)` without transcripts. This follows design C3 literally, since `all()` of no runs is true, and the implementer disclosed it. It still pulls the token median down for a change the store has no runs for. A copy of the real store has no such change, its smallest wall time being 0.3 h. → CONCERN (minor; not a criterion)
- An empty store with no instance: exit 0, the store's path in the heading with "(no instance found)", zero counts and `-` cells. → OK
- `target_is_factory: "true"`, a quoted string: exit 2 with the `must be true or false` message. → OK
- `--since 2026-10-15 --until 2026-10-08`, a reversed window: exit 0, and it prints the windows reversed (`2026-10-22 to 2026-10-15`) instead of refusing. Design C1 does not ask for a refusal. → CONCERN (minor; not a criterion)
- `escape add T-0001` when the only merge is for `T-00011.1`, a prefix decoy: refused, `escape add: T-0001 has no merge`, exit 2. → OK
- `escape add T-0002`, with the merge recorded on the ticket itself and `--issue 'https://tracker.example/é 9 '` (non-ASCII, trailing space): exit 0, empty stderr. The printed and logged `issue_sha256` equals Python's SHA-256 of the UTF-8 text exactly as given (`7d828fcb…33c3`), and `grep -rl tracker.example` finds the link in no file under the store. → OK
- `intervention add`: a whitespace-only `--kind` exits 2, and a `--note` containing `http://x` exits 2. `--kind stop-run` with no ticket prints `{"ok": true, "kind": "stop-run"}` and logs one event with only `kind` and `by`. → OK
- The scorecard over a copy of this repository's real store: its log, its 587 `runs/*/meta.yaml` files and an `instance.yaml` holding only `state_dir`, copied into scratch. Exit 0, the copy's checksums unchanged, and plausible figures: 17 and 16 changes, `record 35, transcript 0, none 115`, `138.78 (35 runs)`. → OK

STATUS: VERIFIED
CONFIDENCE: high. All 17 criteria were run as written on the PR, and the 7 NEW ones also on base. Each NEW one fails on base for the stated reason and matches its THEN text exactly on the PR. Both gates pass, and a wider-window probe matched values I computed independently.
ESCALATIONS:
- A scorecard refusal prints `{"ok": false, "error": …}` on stdout, and design C1 says a refusal prints nothing on stdout. The acceptance scenario sends stdout to /dev/null, so no criterion checks this. The implementer disclosed it: the refusal goes through the CLI's common refusal path, and `cli.py` has no lines left in its budget, at 899 against "under 900". The operator should accept this deviation or ask for a follow-up.
- Two minor scorecard behaviours that no criterion covers. A closed change with no run records counts as 0 tokens and 0 h in the medians. A reversed window (`--since` later than `--until`) prints instead of being refused. Whether either needs a follow-up ticket is the operator's call.
