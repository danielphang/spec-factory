Commit: 6f4d8658252556ed62bd19e130b09634f119f454 (branch `factory/T-0058.1`, base 788a201a34fb3a416b394a14fba65583989c24c9)

How I ran it:
- Each WHEN was taken from the input by `sed` into `scratch/when/NN.sh`, not retyped. That text is byte-identical to the WHENs in the pinned `.factory/store/specs/T-0058/v3.md` (checked with `diff`, which printed nothing).
- Each script ran under `/bin/sh` (GNU bash 3.2.57), from the checkout, inside the running-code wrapper. That wrapper is a fresh temporary HOME, via `scratch/run.sh`.
- PR head: the given worktree, after `uv sync --frozen`.
- Base: a local `git clone` of the repo checked out at `788a201`, in `scratch/baseclone`, after `uv sync --frozen`.
  - My first base attempt used a `git archive` tree with no `.git`. On that tree, `init` refused, so criteria 9 and 10 failed for a reason unrelated to the spec. I discarded those results and reran on the clone. Only the clone's results appear below.
- Shell is uid 501 (not root), which the GIVEN of the unreadable-copy scenario needs.

Per criterion:
1. NEW | A none trailer followed by the attribution footer finishes with no escalation and queues nothing | base: `finish=["none", "🤖 Generated with [Claude Code](https://claude.com/claude-code)"]`, `queued=1 meta=1` | PR: `finish=[]`, `queued=0 meta=0` | PASS
2. NEW | A real item above the attribution footer stays, and the footer is dropped | base: `["none", "the auth path needs review", "🤖 Generated with [Claude Code](https://claude.ai/code)"]` | PR: `["none", "the auth path needs review"]` | PASS
3. REGRESSION | Real item lines, and a line that only mentions Claude Code, are still read by rule (b) | base: not run | PR: `["none. x", "extra line"]`, `["one", "two"]`, `["none", "Generated with Claude Code, says the footer"]`, `[]` | PASS
4. REGRESSION | Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance | base: not run | PR: `intake: where=own-dir changed=2 revision=1 instance=1 writable=no`, `build: where=own-dir changed=2 revision=1 instance=1 writable=no`, `checkout=unchanged store=unchanged dirs=2` | PASS
   - This ran the restated, parenthesised text under `/bin/sh`.
   - I also confirmed the #113 claim. I extracted the same scenario from current truth (`.factory/store/openspec/specs/build-dispatch/spec.md`) and ran it under `/bin/sh` on the PR head. It printed `syntax error near unexpected …` and `intake: where= echo own-dir;; *) echo none;; esac) …`. So the restated text is what fixes the scenario under that shell.
5. REGRESSION | launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy | base: not run | PR: `config=2 launch=2 same=yes lock=1 copies=0` | PASS
6. REGRESSION | launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy | base: not run | PR: `old=gone other=kept fresh=kept new=written dirs=3` | PASS
7. REGRESSION | init reports an edited agent copy and leaves it as it is | base: not run | PR: `exit=0 stale=factory-planner.md kept=yes named=1 others=0` | PASS
8. REGRESSION | init still creates a missing agent copy and lists no matching copy | base: not run | PR: `exit=0 created=factory-triage.md stale=0 same=6 differs=0` | PASS
9. NEW | init lists an agent copy it cannot read, says so, exits 0 and leaves it as it is | base: `exit=1 stale=absent kept=yes named=1 unread=0 others=0` | PR: `exit=0 stale=factory-planner.md kept=yes named=1 unread=1 others=0` | PASS
10. NEW | The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance | base: `init: exit=0 named=0 hint=0 json=0`, `paths: exit=0 named=0 hint=0 json=0`, `stats: exit=0 named=0 hint=0 json=0`, `target=unchanged`, `fresh: exit=0 files=16` | PR: `init: exit=2 named=1 hint=1 json=1`, `paths: exit=2 named=1 hint=1 json=1`, `stats: exit=2 named=1 hint=1 json=1`, `target=unchanged`, `fresh: exit=2 files=0` | PASS
11. REGRESSION | Without the flag paths and stats still run under another lock, and config still accepts a revision | base: not run | PR: `paths=0 stats=0 config=2 accept=0 lock=accepted` | PASS
12. NEW | README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy | base: `accepting=0 upgrade=0 stats=0 row=0` | PR: `accepting=1 upgrade=1 stats=1 row=1` | PASS
13. NEW | The design doc states the footer rule and the refusal in the lock clause | base: `footer=0 lock=0` | PR: `footer=1 lock=1` | PASS
14. NEW | The changelog records the four issues in one entry without a numbering gap | base: `CONTIGUOUS`, `0`, `0` | PR: `CONTIGUOUS`, `1`, `4` | PASS
15. REGRESSION | The harness suite passes | base: not run | PR: last line `627 passed in 102.25s (0:01:42)`, with no `failed` and no `error` | PASS
   - This is the gate 2 run below, made exactly as written, as the process allows. I did not run it twice.
16. REGRESSION | The only existing test file changed is the stats test | base: not run | PR: `tests/factory/test_stats.py` | PASS

Every base output above matches the "Today it prints" line in the spec's verification.md. So each NEW criterion fails on base for the reason the spec states.

Gate suite: PASS
- `git diff --check main...HEAD` printed nothing and exited 0. Here `main` resolves to `788a201`, the same commit as the base.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `627 passed in 102.25s (0:01:42)` and exited 0.

Probes. The first group is `status parse` under the PR head:
- Footer followed by trailing spaces → `[]` → OK. Lines are stripped before matching.
- CRLF line endings, with a blank line before the footer → `[]` → OK.
- Footer twice → `[]` → OK.
- Real ESCALATIONS head, then a blank line, then the footer → `["the auth path"]` → OK. The footer is dropped and the real item kept.
- `* ` marker before the footer → `[]` → OK. This matches design step A.2.
- Footer with an empty link `()` → kept as an item → OK. The pattern needs a non-empty link.
- `🤖 Generated with Claude Code` with no link → kept → OK. That is the standing decision: only the exact footer is dropped.
- Footer with ` and more` after it → kept → OK.
- Footer, then `Co-Authored-By: …` → `["none", "Co-Authored-By: …"]` → OK. `Co-Authored-By` lines are out of scope, and rule (b) still applies to them.
- Footer as the text of the ESCALATIONS line itself → kept as the head item → OK. The spec covers only lines below the ESCALATIONS line.

So the parser drops exactly one line form and is not special-cased to the two links the tests use: any non-blank link is dropped.

Probes of `init` and `--accept-harness`:
- `init` with three copies at once, one at mode `000`, one edited and one in a matching state → exit 0, `ok: true`, `stale_agents` lists the planner and triage copies, one `could not be read (Permission denied)` line and one `differs` line → OK. The unreadable copy's mode was still `000` afterwards and its bytes were unchanged: init never chmods it.
- `--accept-harness=<sha>` (the `=` form) with each of `paths`, `stats` and `init` → exit 2, with the `config` hint → OK.
- `--accept-harness <sha> paths` from a directory that is not a repository → exit 2, with the hint → OK. It is refused before anything else runs.
- `--accept-harness "" paths` → exit 0 → OK. An empty sha is falsy, and every other command treats it as no flag too (`cli.py:862`, `cli.py:866`), so this is consistent.
- `--accept-harness <sha> stats --help` → exit 0 → OK. argparse prints the help before `main()` reaches the refusal.
- `.claude/agents` directory itself at mode `000` → exit 1, `PermissionError` on the PR head, and the same on base → CONCERN, outside the criteria. The spec covers a copy that cannot be read, not the directory. This change does not cause it. See ESCALATIONS.

Other checks:
- The only protected paths changed are `factory/status.py`, `factory/setup.py` and `factory/cli.py`, each declared in the spec's Risk section. `git diff --name-only` over `.factory`, `docs/prompts`, `agents`, `bin`, `pyproject.toml` and `uv.lock` printed nothing.
- The PR description says README is 1,174 lines. `wc -l README.md` on the PR head prints `1176`. This is still within the 1,185-line budget, so no criterion is affected, but the description's figure is off by two.

STATUS: VERIFIED
CONFIDENCE: high. Each of the 16 commands was run as written from the spec's own text, and each matches its THEN on the PR head. Each NEW command fails on a real base checkout exactly as verification.md predicts. Both gates pass, and the probes show the parser fix is not tied to the tested inputs.
ESCALATIONS:
- Outside the criteria, and present on base too: `factory init` still exits 1 with `PermissionError` when the `.claude/agents` directory itself cannot be read (mode `000`), not just one copy in it. #114's fix covers only an unreadable copy. Whether the directory case should be handled is a separate ticket's decision.
