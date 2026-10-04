# Retro 1: spec-factory instance B, 2026-10-01 to 2026-10-04

Scope: every non-success run in `inputs.md` §1 (27 runs, all read in full), the 25 parks, the 30 human resolutions, the escalation queue, the eight role prompts, the two standards, the briefing and `instance.yaml`. Store root `/Users/dphang/dev/spec-factory/.factory/state`; harness `/Users/dphang/dev/spec-factory-harness`.

A note on the question that triggered this run ("is the retro also looking for inefficiencies?"): the role prompt asks for failure patterns, but most of what this period lost was not model mistakes; it was rounds the harness forced on correct work. Those are reported below under ESCALATIONS because they are harness and process defects, which the role rules say get no prompt text. The one figure to carry away: of 17 implementer runs in the period, 9 were first rounds and 8 were extra; 6 of the 8 extra rounds (and the 12 checker runs paired with them) were caused by the harness or the store layout, not by any defect in the code or the spec.

## 1. Causal chains, grouped by systemic cause

Vocabulary: a **park** is the harness stopping a ticket for a human; the **store** is the folder of ticket records and run outputs; a **sub-ticket** is one PR-sized piece of an approved spec; a scenario label **NEW** means "must fail before the change", **REGRESSION** "must pass before and after".

### Group A: wrong or missing instruction (planner labelling). 3 incidents + 1 partial. Proposal P1.
- run-0057-verifier (T-0012.2, SPEC-DEFECT): `records-untouched` passed on base and PR → the planner (run-0054) had labelled this intermediate guard NEW → the planner prompt says to label intermediate checks "NEW or REGRESSION the same way" and gives no rule for a guard that holds trivially before the change → **wrong/missing instruction**. Cost: park, operator relabel, redispatch.
- run-0071-verifier (T-0012.5, SPEC-DEFECT): `responses-unchanged` diffs `main` against an unchanged tree; labelled NEW by the planner → same cause. Park, relabel, redispatch.
- run-0092-verifier (T-0012.6, SPEC-DEFECT): `no-old-paths-in-live-files`, the parent's NEW scenario, passed on .6's base because siblings .2 and .5 had already cleaned the files; the planner assigned it to .6 as NEW while itself writing narrowed intermediates for .2/.3/.5 → labels were copied from the parent's base instead of re-derived for the sub-ticket's base → same cause. Park, relabel, redispatch.
- run-0069-implementer (T-0012.4, ESCALATIONS item 2) and run-0060-verifier (T-0012.1, "judgment call"): four and one NEW criteria passing on base vacuously; the four verifier runs on .4 (0077, 0080, 0086, 0089) accepted the operator's relabel. Two of the four passed for a different reason than stated (argparse rejecting an unknown flag), which is a spec-writer weakness, not the planner's; counted as partial.

### Group B: missing context (stale briefing). 0 incidents in the period, 1 severe by the design's own classification. Proposal P2.
`.factory/context.md` (the per-repo text every role reads first) states two things that are false on the current tree: "Its live store is still `intake/state/` until an operator step moves it" (the store moved to `.factory/state/` in `95c1acf`, 2026-10-03 09:59 -0700; `intake/` no longer exists; 797 files are tracked under `.factory/state`) and "Green ... (branch `feat/lionbot-v3`) ... still runs its own in-tree copy of the harness" (`git -C ~/dev/nanobot-upstream branch --show-current` → `feat/lionbot-v3.5`; `factory/` and `bin/factory` absent). The briefing was edited twice after the move (`e6b56d1`, `a01eee0`) without correcting these. `docs/design.md:54`: "A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it." No run after the move cited the wrong store path (runs 0100–0103 cite `intake/state` and ran before it), so this is preventive.

### Group C: harness defect. Reported under ESCALATIONS, no prompt text.
- C1 store committed to the integration branch → "head does not contain main" conflict runs on correct heads: run-0082 (.5), run-0085 (.4), run-0099 (.6), run-0122 (T-0014.1); plus run-0062 FAILED (gate run on a head that predates a sibling, passes on the trial merge) and run-0102 SPEC-DEFECT (parent `whitespace-clean` trips on committed run records).
- C2 verifier `## Gate suite: PASS` written as a heading; parser `^Gate suite:` records `ci FAIL "missing Gate suite line"` → an approved and verified head (302f70b) sent back as a fix round: run-0096, run-0097, run-0098. Also run-0073 (superseded by a redispatch before it cost a round).
- C3 "budget kill: reviewer" ×2 (run-0074 19 s, run-0076 116 s): the agent returned empty output because Fable credits were exhausted (store commit `e725a5c`); the harness labels any empty output a budget kill and keeps no error text.
- C4 archive refused ×4 at parent close (T-0012, T-0013, T-0015: "no spec store"; T-0014: blank reason). The instance has no `openspec/` tree, so every parent close parks; `park(... arch.stderr || '')` and `subticket add: ` lose the clerk's stderr.
- C5 planner head line `ID / Title: ST-1 / …` (run-0118) rejected by `subtickets.HEAD_RE`; the planner followed the OUTPUT template's field label literally; park reason blank; operator hand-normalised the plan.
- C6 gate command `git diff --check main...HEAD` is empty on every parent-close run (run-0112, run-0103): it checks nothing there.
- C7 marker ledger: its one row, `factory/cli.py:1081`, is a `print()` string, not a `factory:` comment; the composer matched a literal, not a comment leader (coding.md rule 3 gives the pattern). No real markers exist.

### Group D: process / store out of sync. No rule.
- run-0030/0031/0032-planner ESCALATE (T-0002, T-0003, T-0001) and six operator closes from `ready-for-planner` (T-0004..T-0007, T-0009, T-0008): pilot specs were applied by hand on `main` while the tickets stayed queued. Each planner correctly escalated. One-off from the pilot.
- run-0069-implementer BLOCKED (T-0012.4): a test added by sibling .3 became an "existing test" for .4 with "Tests to change: none"; needed a ruling (`f809c69`). Design question, not a prompt one (ESCALATIONS).

### Group E: working as designed. No change.
- Critic REVISE ×4 (0036, 0043, 0051, 0115): each had a real BLOCKING finding; 0051 and 0115 are rubric-6 readability blocks, which is the T-0011 rule firing (2 of 20 critic runs). The spec writer's own RULES bullet names only "the Problem section" while rubric 6 and the preamble cover five sections (0115's block was in Operator steps); 2 incidents is below threshold, watch for the next retro.
- Triage NEEDS-HUMAN ×8 of 24 and spec writer NEEDS-HUMAN ×2 of 22: every question was a product or design call with 2–3 options, as the prompt requires. 5 of the 10 were resolved by the operator's standing take-the-default rule without a fresh decision (T-0007 writer, T-0008 triage and writer, T-0010, T-0015). Per the anti-goodharting rule, no agent-side change is proposed; the harness-side option is under ESCALATIONS.
- Spec writer NEEDS-SPLIT ×2 (0050, 0052): T-0012 was six parts; correct.

## 2. Proposals

### P1. Planner: label each sub-ticket's criteria against its own base; a guard that cannot fail before the change is REGRESSION
Change: edit. `factory/prompts/planner.md` OUTPUT, the `Acceptance:` lines (same text in `docs/design.md` §4 block and `docs/prompts/04-planner.md`, which are identical to the harness copy today, `diff` empty).
```
-  Acceptance: the parent's scenarios it covers, each as its WHEN command,
-    THEN result and verification.md label, plus any intermediate checks
-    it needs, labelled NEW or REGRESSION the same way
+  Acceptance: the parent's scenarios it covers, each as its WHEN command,
+    THEN result and verification.md label, plus any intermediate checks
+    it needs, labelled NEW or REGRESSION the same way. Labels are
+    relative to this sub-ticket's own base (main when it starts), not
+    the parent's: a parent NEW scenario an earlier sibling already
+    satisfies is REGRESSION here, and a guard that cannot fail before the
+    change (a path untouched, a section unchanged, main diffed against
+    itself) is always REGRESSION. A NEW label that passes on base parks
+    the sub-ticket as a SPEC-DEFECT.
```
Incidents: run-0057, run-0071, run-0092 (chains in Group A); run-0069 item 2 and run-0060 as partials.
Counterfactual: 0057 yes (planner-authored guard); 0071 yes (planner-authored guard); 0092 yes (the planner knew .2 and .5 clean the paths: it wrote narrowed intermediates for them); 0069's four: two yes (`throwaway-store-ignores-lock`, `init-and-paths-exempt` are "must not refuse" guards), two unclear (pass on base for a reason the planner could not run); 0060 unclear.
Metric: verifier SPEC-DEFECT on sub-ticket runs caused by a NEW label passing on both: 3 of 21 sub-ticket verifier runs (14%); sub-tickets needing an operator relabel: 4 of 9. Expected: 0 in the next window. Reversion check needs ≥5 planner runs across two retros (5 PLANNED runs this period, incl. T-0016).
Risk: the planner over-applies REGRESSION to a scenario that should be NEW; the verifier cannot detect that (a REGRESSION passing on both looks fine), so real NEW evidence is lost. The wording limits the relabel to guards and sibling-satisfied scenarios. Prompt grows by six lines.

### P2. Briefing: remove two false statements in `.factory/context.md`
Change: edit `/Users/dphang/dev/spec-factory/.factory/context.md`.
```
-- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
-  `harness.lock`, and closed records (`answers/`, `green-pilot/`). Its live store is still
-  `intake/state/` until an operator step moves it.
+- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
+  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
+  The store is tracked on `main` and the operator commits it between steps, so `main` moves
+  even when no ticket merges.
```
```
-Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3`), is instance A: it
-still runs its own in-tree copy of the harness, from which this repo's harness was imported. Read
-it only to observe what a fix does there today; never write there, and never copy its test names,
+Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`), is instance A.
+Its tree no longer carries a copy of the harness (`factory/`, `bin/factory` absent); this repo's
+harness was imported from its earlier branch. Read it only to observe behaviour there; never write
+there, and never copy its test names,
```
Incidents: none in the period; 1 severe by `docs/design.md:54` (a wrong briefing misleads every role and both checkers alike). Evidence in Group B, all from commands run today.
Counterfactual: n/a (preventive).
Metric: role outputs in the window that cite `intake/state` as the live store or green's `factory/` as present: 0 today (no run after the move did), expected to stay 0; secondary: instance-B runs that fail to find or write the store: 0 → 0.
Risk: the replacement green sentence states only what was verified (branch name, absent paths); if the operator intends a fuller description of instance A's new status, the operator writes it. Every other sentence is unchanged.

### Prior proposals
none (first retro). Model-per-role table (`instance.yaml` `models`): no change proposed. Rates by model: critic fable 16 APPROVE / 4 REVISE, all four REVISE with a defensible BLOCKING; reviewer fable 19 APPROVE / 0 REQUEST-CHANGES / 2 KILLED (credit outage); verifier opus 20 VERIFIED / 3 SPEC-DEFECT (all label defects) / 1 FAILED (stale base); verifier fable 1 / 1. 19 of 19 reviewer approvals with no BLOCKING finding cannot be told apart from rubber-stamping without the human audit sampling reviewer runs; recommend the audit draws its sample there.

### Rule-deletion check (process step 5)
No prompt rule targets a code path, tool or step that no longer exists. The two false briefing sentences are the only instruction text whose subject is gone (P2). Rubric 6 (T-0011) fired on 2 of 20 critic runs and both blocks were real: keep.

STATUS: PROPOSED
CONFIDENCE: medium. Every count is from `log/2026-10.jsonl`, the ticket files or `git`, and every cited run was read in full; P1's counterfactual holds cleanly for 3 incidents and is a judgment on the partials; P2 is preventive and rests on the design doc's own severity claim, not on an incident.
ESCALATIONS:
1. **Store on the integration branch makes correct work re-run.** The gate rule "head contains current main" is sound, but the harness and operator commit the store to `main` between steps (`store(...)`/`intake(...)` commits), so in-flight branches go stale without any code change. Of 5 `merge.refused` events, 4 were caused by commits that could not conflict with the branch: run-0082 (.5: 3 store commits), run-0085 (.4: the same 3), run-0099 (.6: `600b8d4`, store only), run-0122 (T-0014.1: `431e349`, `dev/issues.md`); 1 was a sibling merge (run-0088, `.5` merged, by design). Each cost an implementer run plus a reviewer and a verifier re-run: 12 agent runs. The same layout caused run-0062 FAILED (gate run on the head, passes on the trial merge) and run-0102 SPEC-DEFECT (`whitespace-clean` trips on committed run records; the operator had to amend the scenario). Decide: keep the store off `main` (the design's "`tickets` branch of YAML", `docs/design.md:70`, or an ignored path), or have the gate test "contains main" against a trial merge when the gap is store-only.
2. **A verifier heading turns an approved head into a fix round.** `results record` reads `^Gate suite:` (`factory/cli.py:477`); verifiers wrote `## Gate suite: PASS` in run-0073, run-0094 and run-0102. Run-0094's `ci FAIL "missing Gate suite line"` sent 302f70b (reviewer APPROVE, verifier VERIFIED, suite 116 passed) to fix round 2: run-0096, 0097, 0098. The parser should accept a heading or bold prefix (as `subtickets.HEAD_RE` already does) and a missing line should park as `harness-bug`, not be recorded as a gate failure the implementer must answer. A prompt line was considered and rejected: the parser is the deterministic fix, and T-0001 (STATUS trailer) was the same lesson.
3. **"budget kill" is not a budget kill.** Both KILLED reviewer runs (19 s and 116 s) were a Fable credit outage (`e725a5c`); `build.js:93` labels any empty agent output KILLED and saves no error, so this retro could not see the cause from the store. Record the agent's error text; distinguish a provider failure (retry) from a budget kill (park). Model-table note: critic and reviewer both run on Fable, so one outage stalls every build; a fallback model is a config decision.
4. **Every parent close parks on archive.** 4 of 5 parents hit "archive: no spec store" (T-0012, T-0013, T-0015; T-0014's reason was blank). `openspec/` does not exist in the repo. Either run `factory init` so parents archive, or make parent close skip the fold when the instance has no spec store (a design change; T-0010 named the refusal but kept the park). Separately, `park(..., arch.stderr || '')` and `subticket add: ` record a blank reason when the clerk relays no stderr: keep the clerk's full reply.
5. **Planner head line vs parser.** run-0118 wrote `ID / Title: ST-1 / …`, following the OUTPUT template's field label; `HEAD_RE` requires `ST-1 / Title` at column 0 or as a heading. Accept an optional `ID / Title:` prefix in the parser (one line) rather than lengthen the prompt; 1 incident, below the proposal threshold.
6. **The whitespace gate is empty at parent close.** `git diff --check main...HEAD` with `main` = `HEAD` checks nothing (run-0112, run-0103 said so). Not loosening it; flagging that `gate_commands` in `instance.yaml` needs a parent-close form (e.g. against the parent's recorded base, excluding the store).
7. **Marker ledger false positive.** Its one row is a `print(f"factory: …")` string (`factory/cli.py:1081`), not a shortcut marker. The composer should match comment leaders only (`(#|//|/\*) ?factory:`, coding.md rule 3). No real markers exist on `main`.
8. **Harness prompt copies diverge from the design blocks beyond placeholder fills.** `factory/prompts/spec_writer.md` and `triage.md` carry an "Acceptance items describe behaviour…" bullet absent from `docs/design.md`; the design doc is the stated source of truth and `role-prompt-text-unchanged` compares against green, not the design. Decide which copy is canonical, then make the check compare the two.
9. **Half the NEEDS-HUMAN parks were answered by a standing default.** 5 of 10 (T-0007 writer, T-0008 triage and writer, T-0010, T-0015) were resolved by the operator's "take the recommended, reversible option" rule, each after a park, a relay and a re-ask run. No agent-side change is proposed (the questions were real design calls, and reducing escalations is not the goal). Decide whether the harness should carry the standing rule: when a NEEDS-HUMAN names a recommended option, take it, record it as a default in the store, continue, and leave the spec gate as the point of reversal.
10. **Sibling-added tests become guardrail tests mid-parent.** run-0069 (T-0012.4) was BLOCKED because a test added by T-0012.3 minutes earlier could not be touched under "Tests to change: none"; the ruling took one park. Design question: may a later sub-ticket of the same parent change tests an earlier sibling added, with the spec gate's approval of the parent standing in for the row? Flagged, not proposed (it loosens a guardrail).
11. **Label-only SPEC-DEFECTs cost a human round each.** All 3 sub-ticket SPEC-DEFECTs this period were a NEW/REGRESSION label and were resolved by a one-word relabel and redispatch; run-0060 chose not to apply the rule to an identical case. P1 removes the cause at the planner; whether a label-only defect should park at all is a gate question for the human, not a rule to loosen here.
