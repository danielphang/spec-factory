# Critic review, round 2: T-0059 v3 (#120), `factory truth check` and the gate's replay of current truth

Round 2. I checked whether round 1's findings were resolved and read the text v3 changed. One new BLOCKING finding comes from a change in the repo since round 1, not from text I missed: T-0057.1 merged into `main` at `7bfbe8f` and T-0057 was archived, so T-0057's scenarios are now current truth, and one of them fails under this spec's own exact-print rule on `main` and on any branch that adds more than one line to README.

What I checked:
- `main` is at `7bfbe8f` (`Merge factory/T-0057.1`), not `11080b1`; the store's `tickets/T-0057.yaml` says `status: closed`, `T-0057.1.yaml` says `status: merged`, and `openspec/changes/archive/2026-10-25-T-0057/` exists. Current truth now holds 325 scenarios (`grep -c '^#### Scenario'` summed over the 15 capability files; the spec says 316).
- `factory/cli.py` is 899 lines on `main` and on `factory/T-0057.1`; README is 1,213 on both, so the spec's size arithmetic (about 903 under 910; 1,213 plus at most 11 under 1,225) still holds.
- T-0057's one harness-docs scenario, "README, the design doc and the changelog describe the refusal route", computes `growth` as `git diff --numstat $(git merge-base HEAD main) HEAD -- README.md | awk '{print ($1 - $2 <= 1 ? "ok" : "over")}'`. I ran its WHEN from `~/dev/spec-factory` on `main`, through the running-code wrapper with stdin closed: it prints `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=` (empty, because the diff is empty and awk prints nothing), then `CONTIGUOUS`, then `entries=1 terms=3`. The THEN requires `growth=ok`, so the exact-print rule fails it on `main` today. On a branch that adds more than one net line to README it prints `growth=over` and fails again.
- The other scenarios in current truth that diff the checkout against `main` have prose THENs and are skipped by the rule: harness-code's "Every definition keeps its exact text, and the split adds at most 100 lines" ("one line, `pairs=<n> ...`, with n at least 1") and harness-suite's "The only existing test file changed is the stats test" ("prints nothing, or only ..."). I did not run the other seven exact-print scenarios T-0057 added (build-dispatch 2, role-inputs 1, spec-format-check 4); they are fixture-based `bin/factory` runs, and the spec's evidence never ran them under the rule.
- Acceptance commands re-run as written from `~/dev/spec-factory` at `7bfbe8f` through the wrapper: the gate-entry sed prints `  - "uv run --frozen pytest -q -p no:cacheprovider tests/factory"`; the documents grep prints `readonly=no section=no built=no accepting=no design=no design-fence=no changelog=0`. Both still match the Acceptance section's "today" text.
- Part A's new Folding sentence is present and says what round 1 asked. Part B states the expected `cli.py` count. The Problem's first paragraph now says what is wrong and for whom; "design part A" is gone from Evidence; the only section letters in human-facing sections are inside "Proposed change", which the operator is not held to.

## Findings

[BLOCKING] 5 proposal.md, Decisions (last bullet) and Risk (sixth bullet); specs/gate-commands/spec.md, "The truth check on this checkout reports no failure in the capabilities this change restates"; verification.md, Operator steps, step 1
Problem: T-0057 is archived, so its harness-docs scenario is current truth now, and it fails under this spec's exact-print rule on `main` (`growth=` empty) and on this change's own branch (`growth=over`, because README grows by up to 11 lines); the new gate-commands scenario replays harness-docs and requires `failed=0`, so it cannot pass on this change's checkout, and Operator step 1's replay on `main` after the merge would report 1 failed, which the spec says breaks every later gate.
Evidence: The run quoted above, on `main` at `7bfbe8f`; the scenario's THEN at `openspec/specs/harness-docs/spec.md:622`; the gate-commands scenario's THEN `exit=0 failed=0`; Risk's "T-0057's delta adds requirements only, so neither change's delta touches the other's", which was true while T-0057 was a folded delta whose scenarios the check skips, and is not true now that they are current truth.
Suggested fix: Add a MODIFIED harness-docs requirement that restates "The documents record the format check at spec add and its route back to the spec writer" with `growth` measured across the `Merge factory/T-0057.1` commit against its first parent, as harness-suite's T-0045 and T-0051 scenarios do (or with the growth clause dropped), note in Decisions and Risk that this change now restates a T-0057 requirement, and re-measure the replay on `main` at `7bfbe8f` and from a branch checkout that carries this change's README growth.

[SHOULD-FIX] 1 proposal.md, Evidence (first paragraph and "Size limits this change meets") and Responses (last item)
Problem: The Evidence names `11080b1` as `main`'s current tip and says T-0057.1 is "now at its checks", but `main` is at `7bfbe8f`, T-0057 is closed and archived, and current truth has 325 scenarios, nine of which (eight with exact-print THENs) were never run under the rule.
Evidence: `git log --oneline -1 main`, the store's `tickets/T-0057.yaml` and `tickets/T-0057.1.yaml`, the archive directory, and the scenario count above.
Suggested fix: Re-measure `run-gate.txt`, `run-fixed.txt`, `run-four.txt` and `run-nested.txt` on `7bfbe8f`, state the new counts, and describe T-0057 as archived.

[SHOULD-FIX] 2 proposal.md, Evidence, "Result on `main`" and "The fix works"
Problem: Every replay figure was measured on a checkout of `main`, where `git merge-base HEAD main` equals HEAD and every scenario that diffs the checkout against `main` sees an empty diff, but the gate runs the replay on a branch checkout, where those scenarios see this change's own diff.
Evidence: Three current-truth scenarios diff against `main` (named above); two are prose and skipped, and the third is the one the BLOCKING finding runs. The spec's gate-commands scenario and its Risk bullets describe the replay as run "on this change's checkout" with no evidence from one.
Suggested fix: Run the prototype once from a branch checkout that carries this change's edits (a scratch worktree of `main` with the README and `factory/` changes committed) and report that run beside the `main` runs, so the operator sees the gate's result where the gate runs.

Prior findings (round 1):
- [BLOCKING] 6 Problem and Evidence: RESOLVED. The Problem's first paragraph says what is wrong (a merged change can quietly break required behaviour) and for whom (the operator, who approves on the understanding that it holds); "design part A" is replaced by "the exact-print rule under Decisions".
- [SHOULD-FIX] 2 "Spec pinning and planner-run refusals keep their text" label: WITHDRAWN. The writer is right that the verifier runs the item in the spec's form, whose `run start` passes no `--model`, and that form passes on base today; the item's new text says which form fails and why, which is what the operator needs.
- [SHOULD-FIX] 4 nested run's cost: RESOLVED. Decisions and Risk give the four-capability run's figure (12 s nested, 16 s alone, replay at 125 s) and name build-dispatch as the capability that sets the wall time.
- [SHOULD-FIX] 6 Operator steps, step 1: RESOLVED. The wrapper clause is gone.
- [NIT] 6 "sub-ticket": RESOLVED, glossed at first use.
- [NIT] 6 design part A, Folding: RESOLVED. The sentence at design.md's Folding paragraph covers a missing `openspec/changes`, a missing `tickets` and a capability current truth lacks.
- [NIT] 5 `cli.py` limit: RESOLVED. The Decision gives the expected count (about 903 from 899); I confirmed 899 on `main` and on `factory/T-0057.1`. The premise "T-0057.1 at its checks" is stale (see the first SHOULD-FIX), but the conclusion holds: `main` is at 899 with T-0057.1 merged.

STATUS: REVISE
CONFIDENCE: high; the BLOCKING finding rests on a scenario I ran on `main` at `7bfbe8f` and on the ticket and archive files in the store, and the rest of v3's changes resolve round 1's findings as stated.
ESCALATIONS: none
