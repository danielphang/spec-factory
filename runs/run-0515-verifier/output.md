Commit: 08ad85edf30076259c47b7fc816976f45270e805 (branch `factory/T-0048.1`, base 7231670f2303856db8c1ed709a402be43c251754)

How I ran it: I extracted all 55 WHEN commands verbatim from the pinned spec delta in my input with a script (`scratch/extract.py`). I ran each one under bash from the checkout root, through the fresh-HOME wrapper, with `TMPDIR` set to a scratch directory. The PR checkout is the worktree `wt` at 08ad85e. The base checkout is a local clone at 7231670 (`scratch/base`, with `main` set to 7231670). Before running anything I ran `uv sync --frozen` in each checkout. The GIVEN blocks for scenario 20 came from current truth: "A ruling on a BLOCKED park..." in human-resolution and "A reviewer that ends its turn waiting..." in build-dispatch. I ran each once per TMPDIR. Logs are `scratch/pr.txt`, `scratch/base.txt`, `scratch/later.txt`, `scratch/later20.txt` and `scratch/gate.txt`.

Per criterion (all PR outputs equal the THEN exactly; base: not run for the REGRESSION rows, since every one passed on the PR):
- REGRESSION | The changelog records the change in order | base: not run | `CONTIGUOUS`, `9` | PASS
- REGRESSION | The README describes the new resolve verbs | base: not run | `replan=1 gap=0` | PASS
- REGRESSION | The README says relative paths resolve from the caller's directory | base: not run | `1` | PASS
- REGRESSION | The changelog records the guard in one entry | base: not run | `CONTIGUOUS`, `1`, `5` | PASS
- REGRESSION | The design doc names the marker and the run-directory rule | base: not run | `design=1 dirs=1` | PASS
- REGRESSION | README tells the operator how to write during a run, first thing under Where a human decides | base: not run | as THEN | PASS
- REGRESSION | README says the final verifier run is listed as in flight | base: not run | as THEN | PASS
- REGRESSION | README no longer says the factory's capabilities never entered the spec store | base: not run | as THEN | PASS
- REGRESSION | The design doc names the store branch and the path rule | base: not run | as THEN | PASS
- REGRESSION | The changelog records the store branch in one contiguous entry | base: not run | as THEN | PASS
- REGRESSION | The README describes the store branch and the move | base: not run | as THEN | PASS
- REGRESSION | The design doc describes the check | base: not run | as THEN | PASS
- REGRESSION | The changelog records issue 40's change without a numbering gap | base: not run | as THEN | PASS
- REGRESSION | README describes the sibling tests check and its ruling | base: not run | as THEN | PASS
- REGRESSION | The design blocks and their copies carry the rule and stay in step | base: not run | `implementer copy=SAME rule=1 fill=unchanged`, `verifier copy=SAME rule=1 fill=unchanged` | PASS
- REGRESSION | The changelog records the declared-path rule in a contiguous entry | base: not run | `CONTIGUOUS`, `1` | PASS
- REGRESSION | The changelog records the small-change lane in one entry | base: not run | as THEN | PASS
- REGRESSION | The design doc and README describe both skips | base: not run | as THEN | PASS
- REGRESSION | Every reviewer copy carries the rule and the copies stay in step | base: not run | three lines of `judge=1 narrow=1`, then `copy=SAME fill=unchanged` | PASS
- REGRESSION | The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do | base: not run | `reviewer gates=0 told=1`, `verifier gates=1 told=0`, `implementer gates=1 told=0` | PASS
- REGRESSION | The design doc states the EMPTY-OUTPUT rule, its rows and its park | base: not run | as THEN | PASS
- REGRESSION | README drops the budget park and describes the empty-output retry | base: not run | as THEN | PASS
- REGRESSION | The changelog records issue 41 without a numbering gap | base: not run | as THEN | PASS
- REGRESSION | Principle 2 names the critic's no-suite rule and no longer its build ban | base: not run | as THEN | PASS
- REGRESSION | The changelog records the revert in one entry | base: not run | as THEN | PASS
- REGRESSION | The Spiking section allows a small scratch check and records the replay | base: not run | as THEN | PASS
- REGRESSION | The prompt copies, design, README and changelog name the capability index | base: not run | as THEN | PASS
- REGRESSION | The design, README and changelog describe the whole decision log and no decision index | base: not run | `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1` | PASS
- REGRESSION | The design doc, README and changelog record superseded plans | base: not run | `design=1 readme=1 changelog=3 CONTIGUOUS` | PASS
- REGRESSION | The design doc drops the per-PR approval for protected paths | base: not run | `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0` | PASS
- REGRESSION | The changelog records issue 57's change without a numbering gap | base: not run | `CONTIGUOUS`, `5` | PASS
- REGRESSION | README describes the protected-path check and the new resolve verb | base: not run | as THEN | PASS
- REGRESSION | The changelog records the reading rules for the five roles in one entry | base: not run | as THEN | PASS
- REGRESSION | The changelog records the change in one contiguous entry | base: not run | as THEN | PASS
- REGRESSION | The design doc names the amend command, its intent flag, spec drift and the critic's new input | base: not run | as THEN | PASS
- REGRESSION | README lists the amend command and the drift check | base: not run | as THEN | PASS
- REGRESSION | The design doc, template and README name the sync and the dropped virtual environment | base: not run | as THEN | PASS
- REGRESSION | The changelog records the environment sync in one entry | base: not run | as THEN | PASS
- REGRESSION | The documents describe the driver | base: not run | as THEN | PASS
- REGRESSION | The design doc, README and changelog record both changes | base: not run | as THEN | PASS
- REGRESSION | The documents describe the driver's exemption and its same-ticket guard | base: not run | as THEN | PASS
- REGRESSION | The documents record factory stats | base: not run | as THEN | PASS
- REGRESSION | The README describes the model check | base: not run | as THEN | PASS
- REGRESSION | The design doc names the waiting park reason | base: not run | as THEN | PASS
- REGRESSION | The README names pytest-xdist and the waiting reason | base: not run | as THEN | PASS
- REGRESSION | The changelog records issue 106 as entry 71, without a numbering gap | base: not run | as THEN | PASS
- REGRESSION | The maintained documents pass git's whitespace check in full | base: not run | `exit=0` | PASS
- NEW | Each build document carries the header and is otherwise unchanged | `header=0 rest=changed` for each of the three files | `header=1 rest=same` for each of the three files | PASS
- NEW | The briefing no longer asks a change to keep the build spec in step | `buildspec=3 frozen=0 readme=0` | `buildspec=0 frozen=1 readme=1` | PASS
- NEW | README no longer calls run features untried, and keeps the claims that are still true | `stale=7 replan=1 paths=1 drive=1 tripwire=1 sibling=1 effort=1` | `stale=0 replan=0 paths=0 drive=0 tripwire=1 sibling=1 effort=1` | PASS
- NEW | The Built rule asks for run status, and the design doc's date line points to the changelog | `rule=0 date=0 old=1` | `rule=1 date=1 old=0` | PASS
- NEW | Each Built entry is a short pointer, and each mechanism's detail has one home | `fence=long driver=long tripwire=long sibling=long drift=long empty=long paths=long stats=long host=long skip=2 store=3 drivefence=1 notbuilt=5` | `fence=pointer driver=pointer tripwire=pointer sibling=pointer drift=pointer empty=pointer paths=pointer stats=pointer host=pointer skip=1 store=1 drivefence=0 notbuilt=0` | PASS
- NEW | The glossary points to Where it runs and defines protected path once | `rows=4 pointer=0 protected=0 merge=1 record=1` | `rows=0 pointer=1 protected=1 merge=0 record=0` | PASS
- NEW | README keeps its issue references and drops the moved history, and the changelog records the move | `history=5 refs=19 figures=1 pointer=0 entries=0 terms=0`, `CONTIGUOUS` | `history=0 refs=19 figures=0 pointer=1 entries=1 terms=6`, `CONTIGUOUS` | PASS
- NEW | README is at most 1,110 lines | `readme=over` | `readme=within` | PASS

Each NEW base output equals the "today it prints" value in verification.md, so each one fails on base for the reason the spec gives.

Gate suite: PASS
- `git diff --check main...HEAD` (main = 7231670): exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `584 passed in 98.19s`, exit 0.

Probes:
- A simulated later change → OK. This tests part F's purpose: the rewritten checks keep passing after later changes. In a clone with `main` at 08ad85e, I committed one more change on a branch. It added changelog entry `73. After issue #999 ...` before the "Declined:" line, and inserted one line into the verifier prompt in all three copies: the design block, `docs/prompts/07-verifier.md` and `factory/prompts/verifier.md`. All 55 scenarios still print their THEN. Scenario 20 first failed with an import traceback because I had not created that clone's `.venv`. After `uv sync --frozen` it printed the THEN.
- Scope of the diff → OK. 7 files changed: README, `docs/changelog.md`, `docs/design.md` (line 3 and the paragraph at line 70 only, checked with a word diff), the three `dev/` files (two lines each), and `.factory/context.md`. That file is the only protected path touched, and the spec's Risk section declares it. README's headings are byte-identical to base, and so are its mermaid diagram blocks. No code, test or prompt file changes.
- Figures and claims in the docs against the store → OK, with one note below.
  - The cited log events exist in `.factory/store/log/2026-10.jsonl`:
    - `merge.refused` "protected paths not declared" for T-0044.1 at 2026-10-12T02:14:17;
    - `subtickets.superseded` for T-0031 at 2026-10-09T18:11:03.
  - `plan.skipped` events cover 16 tickets, T-0031 through T-0051. The implementer's "T-0031", which departs from the spec's "T-0032", is correct.
  - The runtime commit `9dbd4f8` matches `~/dev/spec-factory-harness` HEAD, and `5e00a1f` matches `.factory/harness.lock`.
  - README's "51 tickets and 64 sub-tickets" was true at the commit (18:20:53Z). T-0052 was filed at 18:30:41Z, so the store now holds 52 parent tickets. The implementer flagged this in Known gaps 7, and no criterion reads the figure.

STATUS: VERIFIED
CONFIDENCE: high. I ran all 55 acceptance commands verbatim on the PR head, ran the 8 NEW ones on base (each matched its stated before-output), ran both gate commands on the PR head, and all 55 still passed on a simulated later change.
ESCALATIONS: none
