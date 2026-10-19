Commit: 17fba148d8ecf5475b7aa7ddef46193437886317 (branch `factory/T-0049.1`; base 81482fe9967ad8219e44f192032a75c5f2d5c2a9)

How I ran the checks: I copied the nine WHEN commands into `scratch/acc.sh`, then checked the copy against the spec mechanically. I extracted every `- WHEN` line from `.factory/store/specs/T-0049/v1.md` and ran `diff` against the script's command lines, and diff reported them identical. Each command ran from the root of a checkout, under the fresh-HOME wrapper. For the PR that was the worktree at `17fba14`; for the base it was a detached worktree at `81482fe` under `scratch/base`, removed afterwards. I ran them under `bash`, and again under `zsh -f` on the PR to rule out shell dependence. Both shells gave the same output.

Per criterion:
- NEW | The spec's-life diagram draws every route after the critic | base: `classes=0 request=no edit=no amend=no respec=no replan=no ruling=no planned=no drift=no truth=no log=no writers=no later=0` (as verification.md predicts) | PR: `classes=3 request=yes edit=yes amend=yes respec=yes replan=yes ruling=yes planned=yes drift=yes truth=yes log=yes writers=yes later=4` | PASS
- NEW | The clerk node names the Workflow-script path, the launch copy and factory drive | base: `clerk=1 workflow=0 launch=0 drive=0` (as predicted) | PR: `clerk=1 workflow=1 launch=1 drive=1` | PASS
- NEW | Both diagrams of How a ticket moves have balanced quotes and brackets | base: `blocks=1 bad=0` (as predicted) | PR: `blocks=2 bad=0` | PASS
- NEW | The How a ticket moves row names the five modules | base: `row=1 names=0` (as predicted) | PR: `row=1 names=5` | PASS
- REGRESSION | README is at most 1,185 lines | base: not required (I ran it anyway: `readme=within`, 1,109 lines) | PR: `readme=within` (1,174 lines) | PASS
- REGRESSION | README describes init's report of a differing agent copy | base: not required (ran: `row=1 step=1 missing=1`) | PR: `row=1 step=1 missing=1` | PASS
- REGRESSION | The changelog records issue 108 in one entry without a numbering gap | base: not required (ran: `CONTIGUOUS`, `1`, `3`) | PR: `CONTIGUOUS`, `1`, `3` | PASS
- REGRESSION | README stays within its line budget and both documents pass the whitespace check | base: not required (ran: `readme=within`, `check=0`) | PR: `readme=within`, `check=0` | PASS
- REGRESSION | The README, the design doc and the changelog describe the launch copy and the route back to checks | base: not required (ran: same as PR) | PR: `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within`, `CONTIGUOUS`, `entries=1 terms=3`, `exit=0` | PASS

Gate suite: PASS
- `git diff --check main...HEAD` (wrapped, run from the worktree): no output, exit 0. `main` resolves to `81482fe`, the base.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` (wrapped): exit 0, `615 passed in 165.90s (0:02:45)`. The full log is in `scratch/pytest.log`.

Probes:
- Part A requires the diagram to stay exactly as the spec gives it. I extracted the spec's Mermaid block from v1.md part A and README's block under the new heading, and ran `diff` on the two 37-line files. They are identical, so the edges, all three `classDef` lines and the subgraph title match → OK.
- Parts B and C require exact lines. I ran `diff` on the spec's line and README's for the clerk node (`CL["clerk …`) and for the `| How a ticket moves |` row. Both are identical. The PR's diff shows no other change in the first diagram, and one blank line sits before `### Ticket states` (README:285-286) → OK.
- Does the balance check actually catch errors? On a scratch copy of README I made three breaks in the new diagram: a missing `]` on the `SB` node, an unclosed quote on the `PK` node, and a dropped closing fence. Each one changed the output to `blocks=2 bad=1` → OK; the PASS is not vacuous.
- Does the route check actually catch errors? I removed the `resolve --replan F` edge from a copy, and the check then printed `replan=no` with everything else unchanged → OK; the check reads the edges themselves.
- The implementer changed two sentences of the spec's prose; are they true at the base? First, "a human approves a version, the newest by default". `approve-spec` takes `--version` (`factory/cli.py:787`), and `approve_spec` falls back to the newest version (`factory/human.py:135`, `n = a.version or t["spec"]["version"]`) → OK. Second, "its planner receives the decision log but no current truth". The planner's inputs are the approved spec plus the decision log (`factory/compose.py:324-325`, with the comment "no current truth for the planner") → OK; the reworded sentence is more accurate than the spec's "only".
- Spot-check of the implementer's corrected line numbers at the base. In `factory/specstore.py`, the fold into current truth is the loop at 407-415, line 405 writes `verification.md`, and the Decisions lines are at 416-418. In `factory/drift.py`, the ruling or finished-run skip is at line 50, and the refusal "BLOCKED from harness: spec drift" is at 57-58. On the clerk node, `factory/workflows/build.js:18-20` says the launch copy carries the settings and "no clerk relays them", and `factory/drive.py:1` says "with no clerk" → OK, the corrections are right.
- Status date: README:9 reads "as of 2026-10-19", which is today, and it already did at the base. So part D needs no edit, as the PR says → OK.
- Not probed: an actual Mermaid render. `mmdc` is not installed, and the spec rejected a network install of mermaid-cli. The spec's operator step covers this: after merge, open `README.md` on GitHub and confirm that both diagrams render.

Protected paths: the diff touches only `README.md`, and the spec's Risk section declares none.

STATUS: VERIFIED
CONFIDENCE: high. All nine commands are verbatim from the spec and gave the expected output in two shells, all four NEW criteria fail on the base exactly as verification.md predicts, both gates pass, and mutation probes show the structural checks catch real breakage. The only unverified part is the GitHub render, which the spec assigns to the operator.
ESCALATIONS: none
