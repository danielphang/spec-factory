Type: feature

Title: Scorecard: `factory stats` reports the north star's measures per window, with escapes as a store record and a cost record for every run

Summary:
The operator cannot read the north star's measures from the store, so no factory ticket can say which number it moves. The store is the factory's record of every ticket and run. The north star is the project's stated goal and measures, in `docs/north-star.md`. The operator asks for four things:
- A. A scorecard section in `factory stats`. It compares two windows, per target, and gives five numbers: target changes merged, escapes, operator decisions and interventions per change, cost and wall time per change, and lead time from request to merge. The output is Markdown that a review pastes in unchanged.
- B. A new command, `factory escape add <ticket> --issue <url> [--note]`, that records a merged change that later needed a fix or a revert. The scorecard counts these records, and shows only counts and ticket ids, because the issue may sit in a private tracker.
- C. A cost record for every role run, whether the run was started by a Workflow script or by `factory drive`. The Workflow scripts are the Claude Code Workflow files that run intake and build. `factory drive` is the driver that starts each role as its own `claude` process. The spec must find why most runs have no cost record and fix that where the record is written.
- D. Tests: a fixture store with known runs, merges and escapes produces known scorecard figures.

The existing sections A to D of `factory stats` stay as they are.

Evidence:
- The request: issue https://github.com/danielphang/spec-factory/issues/117, filed by the operator on 2026-10-19.
- I reproduced the request's cost figures exactly. I ran `bin/factory stats --store <this store> --store <Nanobot store> --since 2026-10-08 --until 2026-10-14` from the runtime checkout, with no `--transcripts`. Section D printed `triage | opus | 26 | … | record 3, transcript 0, none 23` and `implementer | opus | 66 | … | record 2, transcript 0, none 64`. So 23 of 26 triage runs and 64 of 66 implementer runs have no cost source, as the request says. The other roles show the same pattern in that window: 41 of 44 spec writer runs and 59 of 61 reviewer runs have none.
- README already states the immediate cause, at `README.md:975-981`. Only a run started by `factory drive` carries a cost record, in its `meta.yaml`. Any other run has its tokens only in Claude Code's transcript, and transcripts carry no dollars. Requirement C asks for the fix at the source. This means the Workflow-script path must write a cost record. A transcript fallback in the report is not enough.
- No scorecard or escape code exists yet. `grep -rni "escape\|scorecard" factory/*.py bin/factory`, with regex-escape calls filtered out, finds nothing.
- The store already holds the inputs for lead time and merges. Each ticket file has `created` and a `history` of state changes, and `merge.main_after` records the merge commit. For example, `tickets/T-0054.yaml` has `created: '2026-10-19T05:14:33+00:00'` and `to: closed`. Its parent has `main_after: null`, so the merge has to be read from the sub-ticket. The spec has to decide this rule.
- A related ticket, T-0055 (issue #116, the north star's metric and review), is parked waiting on the operator. Its spec draft (`runs/run-0548-spec_writer/output.md`) contains two items this ticket must follow:
  - Open question 1 is marked "Standing: yes. The scorecard ticket, T-0056, must follow the answer." That draft's option (a) matches this request's wording: count decisions and interventions per change in place of hours.
  - Its first Decision says: "A change to the factory itself is factory work and does not count as [a target change]." That decision is not approved yet.

Capabilities: factory-stats, build-dispatch, live-store-guard, harness-docs

Assumptions:
- "Target" means one factory instance: a repository the factory builds, with its own store. This repository and the Nanobot fork are the two instances today. (Inference.)
- `factory escape add` writes to the store, so the live-store guard's rules for writes apply to it. That guard refuses unmarked writes while a role run is in flight. (Inference.)
- A fix under requirement C applies to new runs only. Past runs keep "none" unless the spec finds a source for them. (Inference.)
- Requirement C may be harder than it looks on the Workflow-script path. A Workflow run is an agent inside a Claude Code session, and I did not check whether the script can read that agent's tokens and dollars. If it cannot, the spec writer should report the gap, not record an estimate. (Unverified.)
- "Operator interventions made outside the CLI" leave no CLI event by definition. The spec writer must name the record that counts them, for example operator commits to the store branch. The spec writer should offer options rather than pick one silently. (Inference.)
- Suggested priority, a suggestion only: high. T-0055's draft names this ticket as the current focus and the top of the queue.

Question for human:
How should the scorecard decide which merged tickets count as "target changes"?

The request defines target changes merged as "tickets closed with a merge", per target. T-0055's draft says a change to the factory itself is not a target change. Every ticket in this repository's store changes the factory. So under T-0055's rule, this store's scorecard row always shows 0 target changes. Under the request's words, it shows every merge.
- (a) Recommended: decide by instance. Each instance declares whether its target is the factory itself. For example, `instance.yaml` could gain a setting for this. The scorecard counts that instance's merges as factory work, on their own line, and counts every merge in any other instance as a target change. This matches T-0055's draft and needs no per-ticket field.
- (b) Every ticket closed with a merge counts as a target change in its own instance's row, as the request's words say. A review reads this repository's row as factory work. T-0055's draft decision is then reworded to match.
- (c) Decide by ticket. Triage marks each ticket as factory work or target work, and the scorecard counts only target work. This adds a ticket field and a triage step, but would handle a target ticket that also changes the harness.

Is the answer a standing decision that later tickets must follow? If yes, T-0055's spec should state it too.

A related note, needing no answer here: if the operator answers T-0055's open question 1 with (a), this request stays as written. With (b) or (c), this ticket gains a requirement to record or estimate operator time.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. I reproduced the request's cost figures exactly from the stores, and the target-change conflict appears verbatim in T-0055's draft spec.
ESCALATIONS: none
