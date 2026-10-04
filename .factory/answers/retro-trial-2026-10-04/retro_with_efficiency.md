# Retro 1: spec-factory instance B, 2026-10-01 to 2026-10-04 (138 runs, 16 tickets, 25 parks)

This is the first retro of the spec factory's own instance (instance B, the design repo at `~/dev/spec-factory`). It is for the operator who approves changes to the role prompts, the repo briefing and the harness. It proposes five prompt or briefing changes and reports nine harness or process defects it may not fix by prompt text.

## What the period says, in one paragraph

Agent output quality was not the problem. Of 27 runs that did not end in their role's success status, 8 were triage asking a design question, 3 were the planner refusing to plan specs already applied by hand, and 2 were the spec writer's expected NEEDS-SPLIT on a six-part ticket. Only 4 critic REVISE rounds, 1 implementer BLOCKED and 5 verifier non-passes came from the work itself, and every one of those was a correct call on the input it had. What cost time was the harness and the process around the agents: checkers run on heads that cannot merge (10 checker runs re-done), sub-ticket labels the planner copied from the parent (3 parks, 6 checker runs re-done), a parser that misses a markdown heading (one approved head sent back for a fix round), a store committed to `main` mid-build (4 of 5 merge refusals and the parent's whitespace defect), and a clerk agent that makes 87% of all agent calls. The ticket that carried all of this, T-0012 (the harness move), took 389 of the period's 821 role-run minutes.

Denominators (section 5 of the inputs): triage 24 runs, spec writer 22, critic 20, planner 7, implementer 17, reviewer 21, verifier 26. Role-run agent time: 821 min. Clerk calls: 991 of 1,143 agent calls (Green session's count, outside the store).

## Causal chains, grouped by systemic cause

**A. Wrong or missing instruction (planner): a parent scenario's NEW label was copied into sub-tickets where it cannot fail on base.**
- run-0057-verifier (T-0012.2): `records-untouched`, a `main...HEAD` diff count, labelled NEW as an intermediate check; empty on base by construction → SPEC-DEFECT → park → operator relabelled and redispatched → run-0061/0062 (707 s).
- run-0071-verifier (T-0012.5): `responses-unchanged`, a diff of `main`'s section against the tree, labelled NEW → SPEC-DEFECT → park → redispatch → run-0073/0074 (457 s; 0074 killed).
- run-0092-verifier (T-0012.6): parent scenario `no-old-paths-in-live-files` labelled NEW in the sub-ticket; the files it guards were already clean on base after .2 and .5 merged → SPEC-DEFECT → park → gate edit relabelled it → run-0094/0095 (941 s).
- Also noted, not parked: run-0060 (T-0012.1) saw the same shape in `cut-anchor-still-valid` and chose not to apply the rule; run-0069 (T-0012.4) listed four NEW criteria that passed vacuously at base.
Why the agents did it: the planner prompt says intermediate checks are "labelled NEW or REGRESSION the same way" but never says what NEW means for a sub-ticket (fails on *this* sub-ticket's base), and the verifier prompt makes a NEW that passes on both a SPEC-DEFECT. The verifier was right each time.

**B. Harness defect: checkers dispatched on a head that does not contain `main`.** `build.js` dispatches the reviewer and verifier, and only `factory merge` refuses "head does not contain main"; the join then sends a conflict run and both checkers run again on the merged head.
- run-0062-verifier (T-0012.2) FAILED: the branch forked before T-0012.1 added the test gate; the gate could not pass on that head. Park → redispatch → conflict run 0063 → 0064/0065.
- merge.refused ×5 (T-0012.5 at 14:55, T-0012.4 at 15:01 and 15:14, T-0012.6 at 16:23, T-0014.1 at 22:39). In four of the five, `main` had moved *before* the checkers were dispatched (store commits 68e8945 and 600b8d4, issue-index commit 431e349). The fifth (T-0012.4 at 15:14) was a sibling merge during the checks, which the planner prompt already prices in.
Checker runs re-done after a refusal or stale base: 0061, 0062, 0078, 0079, 0080, 0081, 0097, 0098, 0120, 0121 = 4,031 s agent time, about 2,370 s wall. Systemic cause: harness ordering, reported under ESCALATIONS (H1), not a prompt problem.

**C. Process defect: the live store and the issue index are committed to `main` while sub-tickets are in flight.** 797 store files are tracked on `main`. Each store commit moves `main` under every in-flight branch (cause of 4 of the 5 refusals in B), and the committed run records embed diffs whose blank context lines are a single space, so `git diff --check <parent base> HEAD` exits 2 on `main` itself: run-0102-verifier parked the T-0012 parent as SPEC-DEFECT on `whitespace-clean` (29 files, all under the store), the operator amended the scenario, and the parent verifier ran again (run-0103, 598 s). Every future parent with a whitespace scenario over the parent range hits this. Design piece 1 suggests a `tickets` branch for the store. ESCALATIONS (H2).

**D. Harness defect: the verifier's `Gate suite:` line is read with `^Gate suite:` (cli.py:477), which misses a markdown heading.** Three verifier runs wrote `## Gate suite: PASS` (0073, 0094, 0102). For 0094 the harness recorded `ci FAIL / missing Gate suite line` on a head the reviewer had approved and the verifier had verified, and sent it back as a fix round: run-0096 (405 s) + 0097 (626 s) + 0098 (332 s) = 1,363 s. The implementer's PR description names the regex and DISAGREEs with the "failure"; it was right. ESCALATIONS (H3).

**E. Missing context, then wrong assumption (human process): approved specs applied by hand, tickets left open.** run-0030/0031/0032-planner ESCALATE (T-0002, T-0003, T-0001): each found its spec already on `main` and refused to plan an empty PR. Correct behaviour; 324 s of planner time and three parks. The operator closed T-0001..T-0007 at 21:10. ESCALATIONS (H7), process only.

**F. Design decision with a recurring human cost: every parent close on instance B parks at `archive`.** T-0012, T-0013, T-0014 and T-0015 (4 of 4 parent closes) parked with `archive: no spec store (factory init not run)` (T-0014's reason was empty) and the operator closed each by hand. T-0012's Decisions say instance B gets no `openspec/`, and T-0010's answer (a) says this park resolves by closing as applied. So the design guarantees one human stop per parent here. ESCALATIONS (H4).

**G. Triage and spec writer NEEDS-HUMAN where the operator took the role's own recommendation.** run-0027 (T-0008, lean (a)), run-0040 (T-0010, "suggested default (a)"), run-0126 (T-0015, "recommended (b)"), run-0024 (T-0007 writer, "(b) recommended"), run-0029 (T-0008 writer, four defaults). All five answers in `.factory/answers/` say "taken by default under the operator's standing take-the-recommendation rule". Re-runs: 0028 (72 s), 0041 (70 s), 0127 (81 s), 0025 (180 s), 0033 (329 s) = 732 s plus five human stops. In the other five triage parks (T-0001, T-0005, T-0006, T-0007, T-0013) triage gave no recommendation and the operator chose; in T-0001 the operator's choice differed from the requester's proposal. Systemic cause: the standing rule lives in the operator's head and in answer files, not in any instruction the roles read.

**H. Over-reporting in the escalation channel.** Of 139 items queued to the human during the period, 25 are the harness's park notices, 38 are "protected path touched, as declared" lists, and 5 are "none" or "no prompt-injection found" statements. 26 of the 38 declared-path lists come from the implementer (16) and the verifier (10), which no instruction asks to produce them; the reviewer's check 6 asks the reviewer to. The same list was queued up to three times per head (T-0012.6: runs 0093, 0095, 0096, 0097, 0098, 0099, 0100, 0101). The operator reads this queue; real items (run-0094's three) sit between repeats.

**I. Critic REVISE, 4 of 20.** run-0036 (rubric 5/6: the design named a mechanism the build spec did not carry) and run-0043 (rubric 4/6: an acceptance setup leaned on unstated reference behaviour) are real spec defects the critic caught; correct and cheap. run-0051 and run-0115 are rubric-6 writing-standard blocks (a Problem paragraph that did not say what is wrong, an unglossed "runtime" in Operator steps); each cost a writer round plus a critic round (0052+0053: 503 s; 0116+0117: 300 s). Two incidents: below the threshold, recorded under "Below threshold".

**J. Implementer BLOCKED, 1 of 17 (run-0069, T-0012.4).** An existing T-0012.3 test fails under the spec's missing-lock refusal and "Tests to change: none" forbade the one-line fix. The implementer verified the fix, reverted it, and escalated. Correct; the planner could not have foreseen a test added by a sibling that merged two hours earlier. No proposal.

**K. KILLED reviewer ×2 (run-0074 at 116 s, run-0076 at 19 s).** Both coincide with an API credits outage (store commit 68e8945: "credits restored; .4 and .5 checks re-dispatched"). The harness parked both tickets as "budget kill: reviewer" after the sibling verifier had finished (0073 VERIFIED 341 s, 0077 VERIFIED 553 s); the redispatch superseded those verifier rows and ran both checkers again. Wall from park to redispatch: about 5 hours. ESCALATIONS (H5).

## Proposals

### P1. Planner labels are per sub-ticket (prevents group A)
Change: add, `/Users/dphang/dev/spec-factory-harness/factory/prompts/planner.md` (and its block in `docs/design.md`, re-copied to `docs/prompts/04-planner.md`), one bullet under RULES after "Each sub-ticket gets a subset…":
```
+ - Labels are per sub-ticket, not inherited. NEW means the WHEN fails on this
+   sub-ticket's own base (main when it is dispatched). A parent NEW scenario
+   that an earlier sibling already satisfies is REGRESSION here. A check that
+   compares the branch with main (`main...HEAD`, `git diff main`) is empty on
+   base by construction: label it REGRESSION, never NEW. The verifier parks a
+   NEW that passes on base as a SPEC-DEFECT, and the park costs both checkers.
```
Incidents: run-0057, run-0071, run-0092 (chains in A); run-0060 and run-0069 noted the same shape without parking.
Counterfactual: 0057 yes (a `main...HEAD` count, named case); 0071 yes (a diff against `main`, named case); 0092 yes (a parent NEW satisfied by earlier siblings, named case); 0060 yes; 0069's four vacuous NEWs: two yes (they say what must not be refused), two unclear (they passed only because argparse rejected an unknown flag).
Metric: verifier SPEC-DEFECT on sub-ticket runs, caused by a NEW label that passes on base. Today 3 of 22 sub-ticket verifier runs (0057, 0071, 0092). Expected: 0. Secondary: checker runs superseded by a label park, today 6 (0057, 0058, 0071, 0072, 0092, 0093), about 2,100 s.
Risk: a planner that over-applies it labels a genuinely new behaviour REGRESSION, and the verifier then reports a REGRESSION failing on base as SPEC-DEFECT anyway, so the failure stays visible; nothing is loosened.

### P2. The briefing says where the store and green are today (step 5: stale instruction)
Change: edit, `/Users/dphang/dev/spec-factory/.factory/context.md`. Every role reads this file first; three statements in it are false since 2026-10-03 and a wrong briefing misleads authors and checkers alike.
```
- `harness.lock`, and closed records (`answers/`, `green-pilot/`). Its live store is still
- `intake/state/` until an operator step moves it.
+ `harness.lock`, its live store `state/`, and closed records (`answers/`, `green-pilot/`).
```
```
- Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3`), is instance A: it
- still runs its own in-tree copy of the harness, from which this repo's harness was imported. Read
+ Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`), is instance A: it
+ runs this harness from its own `.factory/`; its old in-tree copy, from which this repo's harness
+ was imported, is gone. Read
```
Evidence: `.factory/instance.yaml` `state_dir: .factory/state` and commit 95c1acf ("the live store moves to .factory/state; intake/ retired"); `git -C ~/dev/nanobot-upstream branch --show-current` → `feat/lionbot-v3.5`; `~/dev/nanobot-upstream/factory` does not exist and `~/dev/nanobot-upstream/.factory` does.
Incidents: none yet attributable; 4 of the 34 runs since the move still mention `intake/state` (as history, so far).
Metric: role outputs after this edit that cite `intake/state/` as a live path or green's `factory/` as existing. Today unmeasured (0 known). Expected: 0.
Risk: none to any check. The second edit's wording about green needs the Driver session's confirmation of what green runs today.

### P3. Efficiency: a gate command is not repeated as a sub-ticket check
Change: add, `planner.md` (same three copies as P1), one bullet under RULES:
```
+ - A parent scenario whose WHEN is one of the gate commands (the instance's
+   `gate_commands`, given under "Where you work") is mapped to the one
+   sub-ticket where it is NEW. Later siblings do not list it again as a
+   REGRESSION: the gate runs that command on every head and a failure already
+   refuses the merge. The parent-close run covers it for the parent.
```
Incidents (no failures; waste): sub-tickets T-0012.3, .4 and .6 list `harness-suite-passes-after-uv-sync` as REGRESSION next to the gate that runs the same `uv run --frozen pytest … tests/factory`. Verifier runs 0067, 0077, 0080, 0086, 0089, 0092, 0094, 0097, 0100 each ran the suite 2–4 times (73–131 s each: base, PR, gate, sometimes a probe); 19 of those runs are beyond the one gate run, about 30 min of the nine runs' 3,895 s. Implementer runs on the same sub-tickets ran it before and after as well (0069 three times, 0075 twice, 0091 three times), about 9 min more. Green's measurement of T-0015.1's implementer (190 of 431 s in suite and acceptance checks) has the same shape.
Counterfactual: all nine verifier runs lose their base and PR suite runs and keep the gate run: yes.
Metric: median verifier wall on sub-tickets that touch harness code. Today 515 s (the eight .4/.6 runs: 279–693 s). Expected: about 350 s. Refusals kept: a suite failure on the head still fails the gate (FAILED); the parent-close run still runs the NEW scenario on the parent base.
Risk: one refusal changes label. Today a REGRESSION suite scenario that fails on base is a SPEC-DEFECT (base broken); after, a broken base shows only if the head still fails the gate. If a PR incidentally repairs `main`'s suite, that goes unflagged by the verifier; the reviewer's scope check (3) is the remaining guard. The operator should weigh that residual before taking this.

### P4. Efficiency: a recommended default is taken and reported, not parked (instance-scoped)
Change: add, `/Users/dphang/dev/spec-factory/.factory/context.md`, a paragraph after "The request is an issue draft…". Path-scoped to this instance, because it encodes this operator's standing rule and no other repo's:
```
+ Standing rule (operator, 2026-10-01): a design or scope question that has a
+ recommended, reversible option is not a stop. Triage and the spec writer
+ write the question and its options as they do today, take the recommended
+ option, record it under Assumptions (triage) or Decisions (spec, marked
+ "default, operator to confirm at the gate"), put the question under
+ ESCALATIONS so it reaches the human queue, and continue (ACCEPT or
+ READY-FOR-CRITIC). A question with no recommendation, or whose options differ
+ in what ships to a protected path, still goes to NEEDS-HUMAN.
```
Incidents: run-0027, run-0040, run-0126 (triage), run-0024, run-0029 (spec writer); each answer in `.factory/answers/` (T-0008-2, T-0010, T-0015-answer-1, T-0007-2, T-0008-3) records the recommendation taken by default.
Counterfactual: 5 of 5 yes; the roles had already written the spec or ticket against the default (run-0029: "taking all four leaves it ready for the critic unchanged"; run-0024: "The spec then goes to the critic unchanged").
Metric: triage and spec-writer NEEDS-HUMAN parks resolved by taking the role's own recommendation. Today 5 of 10 such parks; re-runs 732 s and five human stops. Expected: 0. Guard metric: spec-gate edits or rejections that reverse a default so taken. Today 0 of 5. If this rises above 1 in 5 over the next two retros, revert.
Risk: this is the one proposal that trades a blocking stop for a non-blocking one, and the anti-Goodharting rule warns against making agents escalate less. Three things keep the human in the loop: the question still reaches the queue (a non-empty ESCALATIONS line is copied without blocking, design §Harness), the spec gate is a hard human stop before any code, and the rule applies only where the operator already declared the stop unnecessary. A wrong default costs a spec round or a gate edit instead of a one-minute answer. The operator decides; the retro notes that in the five cases the one-minute answer was available only because the Green session was watching.

### P5. Efficiency: declared protected paths are the reviewer's notice, once
Change: edit, `implementer.md` and `verifier.md` (and their design-doc blocks and `docs/prompts/` copies), one bullet each under RULES:
```
+ - A protected path the sub-ticket declares is not an escalation: the reviewer
+   lists declared paths for the merge gate (its check 6). You escalate a
+   protected path only when it is not declared, or when the spec does not
+   cover what you did to it.
```
Incidents: 26 declared-path lists queued by the implementer (16) and the verifier (10) out of 139 queued items; the same list from three roles per head on T-0012.6 (runs 0093–0101), T-0013.1 (0109, 0110, 0111) and T-0015.1 (0133 plus the implementer).
Counterfactual: 26 of 26 yes; none of these items carried anything the reviewer's list did not.
Metric: declared-path items in the human queue from roles other than the reviewer. Today 26 of 139 (19%). Expected: 0. Refusals kept: an undeclared protected path still escalates from every role (preamble), and the reviewer's ESCALATE on an undeclared path is unchanged.
Risk: a reviewer run that is killed leaves no declared-path notice for that head; the merge gate's human-approval requirement does not depend on the notice (it reads the sub-ticket's declaration), so the gate is unaffected.

## Below threshold (recorded, not proposed)
- **Planner head-line format (1 incident).** run-0118 wrote `ID / Title: ST-1 / Add rules…`, the OUTPUT block's field label verbatim; `subtickets.py` HEAD_RE wants `<id> / <title>` at column 0, found nothing, and the park reason was empty (`harness-bug: subticket add: `). The operator normalised the plan by hand (ba4618a). If it recurs, change the OUTPUT line to `<ID> / <Title>  (one line, e.g. T-0014.1 / Add rules 9–12)`. The empty reason is H4's defect.
- **Rubric-6 blocks on otherwise sound specs (2 incidents, run-0051 and run-0115).** A spec-writer self-check line ("read Problem and Operator steps as the gate operator; every factory-made name glossed at first use") might have caught both; 2 incidents and the writing standard landed between them. INSUFFICIENT-DATA; re-check next retro.
- **The change is built three times before the implementer.** 17 of 22 spec-writer runs and 12 of 20 critic runs applied the proposed change to a scratch clone to get "after" outputs. The critic's is an independent check and stays. The writer's yields exact THEN values and plausibly fewer critic rounds; dropping it would trade writer minutes for rounds, and this period has no data on the trade. Observation only. Spec-writer time is the period's largest role total (222 min); six runs over 800 s hold 129 min of it (0047: 2,306 s, which ran the critic model ten times as an acceptance trial; 0050; 0128; 0136; 0106; 0029).

## Prior proposals
none (first retro).

## Marker ledger
One row, `factory/cli.py:1081`, is a stderr prefix in a string literal (`print(f"factory: {type(e).__name__}: {e}", file=sys.stderr)`), not a `factory:` shortcut comment. Real markers: 0. No implementer run has yet executed under the coding standard (runtime accepted d81a684 at 17:25 on 2026-10-03; T-0015.1 was implemented at 16:52). INSUFFICIENT-DATA (0 runs). The ledger producer should match comments only, as `docs/coding.md` rule 3's grep does (`(#|//|/\*) ?factory:`).

## Efficiency appendix: where the 821 role-run minutes and the wall clock went
| Source of waste | Evidence | Size | Fix lives in |
|---|---|---|---|
| Checkers run on heads that cannot merge | group B: 10 checker runs re-done | 4,031 s agent, ~2,370 s wall | harness (H1) and process (H2) |
| Clerk agent per store command | 991 of 1,143 agent calls, ~6 s and ~30k tokens each (Green's count) | ~99 min wall, ~30M tokens | harness; issue #24 filed (e2acde4) |
| Sub-ticket NEW labels copied from the parent | group A: 3 parks, 6 checker runs superseded | ~2,100 s agent + 3 human stops | P1 |
| Gate suite repeated as acceptance | 19 extra suite runs in 9 verifier runs; ~8 in implementer runs | ~39 min | P3 |
| `## Gate suite:` unparsed | group D: one fix round on an approved head | 1,363 s agent | harness (H3) |
| Recommended defaults parked | group G: 5 re-runs | 732 s + 5 human stops | P4 (operator's call) |
| Archive park at every parent close | group F: 4 of 4 parents | 4 human stops | design/harness (H4) |
| Credits outage read as budget kill | group K: 2 verifier results superseded | 894 s agent, ~5 h wall latency | harness (H5) |
| Human queue noise | group H: 38 declared-path lists, 25 park notices of 139 items | operator reading time | P5 |

Context size is a cost the retro cannot move by prompt: every T-0012 sub-ticket run carried the 66 KB parent spec (the "Proposed change" section alone is 17 KB) in its input, 23 runs, about 1.4 MB; checker inputs on T-0012.6 were 168–186 KB and run-0059/0060's 398 KB input was 308 KB of diff for a byte-identical import verified mechanically. The design's routing table declares these inputs; issue #24 ("role-specific inputs") is the place for it.

STATUS: PROPOSED
CONFIDENCE: medium. Every count above comes from the store log, the run `meta.yaml` files and the cited outputs, which I read in full; the clerk figures are the Green session's, not re-measured here; P3's residual-refusal analysis and P4's anti-Goodharting trade are judgments the operator should weigh, not facts.
ESCALATIONS:
- H1 (harness, `factory/workflows/build.js`): run `ticket join`'s contains-main test before dispatching the checkers, so a moved integration branch becomes a conflict run first and the checkers run once. Cost this period: 10 checker runs (4,031 s) re-done and one FAILED park (run-0062). The merge refusal itself stays.
- H2 (process and gate scoping, operator decision): the live store (797 files) and `dev/issues.md` are committed to `main` during builds. This caused 4 of 5 merge refusals (68e8945, 600b8d4, 431e349) and the T-0012 parent's `whitespace-clean` SPEC-DEFECT (29 store files). Options: a `tickets` branch for the store as design piece 1 suggests; commit the store only between tickets; or a `.gitattributes` `-whitespace` rule for `.factory/state/**`. The last narrows a gate's range and is the human's call, not the retro's.
- H3 (harness, `factory/cli.py:477`): the `Gate suite:` regex misses a markdown heading (`## Gate suite: PASS`, runs 0073, 0094, 0102); 0094 sent an approved, verified head back for a fix round (1,363 s). Accept an optional `#{1,4}\s+` prefix as `subtickets.py` HEAD_RE already does. The FAIL-on-missing-line behaviour stays.
- H4 (design decision, operator): instance B has no spec store by T-0012's decision, so every parent close parks at `archive` (4 of 4) for the operator to close by hand; T-0014's park reason was empty (`archive: `, and `subticket add: `), so the clerk relayed no stderr for two refusals. Decide: run `factory init` for B, or close "no spec store" as applied automatically per T-0010 (a). Separately, a park reason must carry the CLI's stderr.
- H5 (harness): the two KILLED reviewer runs (0074 at 116 s, 0076 at 19 s) were an API credits outage, labelled "budget kill". On redispatch of the same head the surviving verifier rows (0073, 0077; 894 s) were superseded though recorded against that head. Design §Harness says a budget-killed run re-dispatches the same role on the same inputs; the redispatch re-ran both.
- H6 (harness, token cost): the clerk makes 87% of agent calls at ~30k tokens and ~6 s each (~30M tokens, ~99 min wall this period). The model table cannot go below Haiku; the design's own answer is "Code where possible". Issue #24 covers it; no prompt change helps.
- H7 (process): T-0001, T-0002, T-0003 were applied by hand with the store left at `ready-for-planner`; three planner runs (324 s) and three parks found it. A hand-applied ticket is closed in the store before the build half runs.
- H8 (environment): run-0062 created `/Users/dphang/dev/spec-factory/.venv` because the worktree had no `pyproject.toml` and `uv` walked up; run-0103 left an untracked throwaway store under the dev checkout; run-0134 found a stale `scratchpad/base` from another run. Checkers need a scratch directory the harness owns and clears.
- H9 (marker ledger): the ledger's grep matches a string literal (`cli.py:1081`); it should match comments only.
