Type: feature

Title: Scorecard: `factory stats` reports the north star's measures per window, with escapes as a store record and a cost record for every run

Summary:
The operator cannot read the north star's measures from the store, so no factory ticket can say which number it moves. The store is the factory's record of every ticket and run, kept on its own branch. The north star is the project's goal and measures, in `docs/north-star.md`. The operator asks for four things:
- A. A scorecard section in `factory stats`, the harness's read-only report on the store. It compares two windows. For each window and instance it gives five numbers: target changes merged, escapes, operator decisions and interventions per change, cost and wall time per change, and lead time from a request's creation to its merge. A review pastes its Markdown output in unchanged.
- B. A new command, `factory escape add <ticket> --issue <url> [--note]`, that records that a merged change later needed a fix or a revert. The scorecard counts these records. It shows only counts and ticket ids, because the issue may sit in a private tracker.
- C. A cost record for every role run, whether a Workflow script started it or `factory drive` did. The Workflow scripts are the Claude Code Workflow files that run intake and build. `factory drive` is the driver that starts each role as its own `claude` process. The spec must find why most runs have no cost record and fix it where the record is written.
- D. Tests: a fixture store with known runs, merges and escapes gives known scorecard figures.

The operator decided how target changes are counted (answer 1, standing). Each instance declares whether its target is the factory itself, for example with an `instance.yaml` setting. That instance's merges are counted as factory work, on a line of their own. Every merge in any other instance is counted as a target change. The existing sections A to D of `factory stats` stay as they are.

Evidence:
- The request: issue https://github.com/danielphang/spec-factory/issues/117, filed by the operator on 2026-10-19.
- The operator's answer, recorded in `tickets/T-0056.yaml` history at 2026-10-20T07:23:01: "a target change is decided by instance; an instance whose target is the factory itself counts its merges as factory work, on a line of their own".
- In round 1 I reproduced the request's cost figures exactly. I ran `bin/factory stats --store <this store> --store <Nanobot store> --since 2026-10-08 --until 2026-10-14` from the runtime checkout, with no `--transcripts`. Section D printed `triage | opus | 26 | … | record 3, transcript 0, none 23` and `implementer | opus | 66 | … | record 2, transcript 0, none 64`. I did not re-run it this round.
- `README.md:975-981` states the immediate cause. Only a run started by `factory drive` carries a cost record, in its `meta.yaml`. Any other run has its tokens only in Claude Code's transcript, and transcripts carry no dollars.
- No scorecard or escape code exists yet. In round 1, `grep -rni "escape\|scorecard" factory/*.py bin/factory`, with regex-escape calls filtered out, found nothing.
- T-0055 (#116, the north star's metric and review) has spec v3 approved (store commit `06d821a`). Its approved text binds this ticket:
  - `specs/T-0055/v3.md:55`: decisions and interventions per change stand in for hours of operator attention until the store records operator time. "Standing: T-0056 … follows it."
  - `specs/T-0055/v3.md:95-97`: "Each instance decides whether its merges are target changes. The Nanobot port's are. Spec-factory's are factory work … on a line of their own".
  - `specs/T-0055/v3.md:114-120`: the scorecard table names the five numbers. "Target changes merged", "Escapes", "Operator decisions and interventions per change", "Tokens and wall time per change", "Lead time".
  - `specs/T-0055/v3.md:63`: change failure rate is escapes divided by target changes merged. It is defined in the north star, not added as a sixth row.
- Duplicate search: no open or closed ticket covers a scorecard, escapes or a cost record on the Workflow path. T-0043 (closed) built `factory stats` itself, and T-0030 (closed) built the per-role agent definitions. The queued T-0057, T-0059 and T-0060 cover other things: the spec validator, the gate replaying scenarios, and the benchmark.

Capabilities: factory-stats, build-dispatch, live-store-guard, harness-docs

Assumptions:
- Inference: "target" in the request means one instance, which is a repository the factory builds with its own store. Today there are two instances, this repository and the Nanobot fork.
- Inference: `factory escape add` writes to the store, so the live-store guard's rules for writes apply to it. That guard refuses unmarked writes while a role run is in flight. `factory stats` stays read-only.
- Inference: the new instance setting lives in `instance.yaml`, which `factory init` writes and checks. If the spec changes init or its checks, the store-setup capability is touched as well.
- Inference: the fix under C covers new runs only. Past runs keep "none" unless the spec finds a source for them.
- Unverified: requirement C may be hard on the Workflow-script path. A Workflow run is an agent inside a Claude Code session. I did not check whether the script can read that agent's tokens and dollars. If it cannot, the spec should report the gap and not record an estimate.
- Wording gap, for the spec writer to settle: the request says "cost and wall time per change", but T-0055's approved table says "Tokens and wall time per change". Requirement C's records may carry dollars, tokens or both. The scorecard should keep T-0055's row name and say which units it reports.
- Operator instruction (answer 1): interventions made outside the CLI leave no CLI event, so they need a record. The spec writer offers options at the gate and does not pick one silently. One candidate is operator commits to the store branch.
- Inference: a parent ticket's `merge.main_after` can be null while its sub-tickets record the merge (for example `tickets/T-0054.yaml`). So the spec must state which record makes a ticket "closed with a merge", and which timestamp ends its lead time.
- Suggested priority, a suggestion only: high. T-0055's approved spec puts #117 second on the queue, after T-0055 itself (`specs/T-0055/v3.md:25`).

Question for human / Missing info / Reason: none. The round-1 question is answered (answer 1, option a, standing).

STATUS: ACCEPT
CONFIDENCE: high. The operator answered the only open product question, and T-0055's approved spec confirms the answer and names the five numbers.
ESCALATIONS: none
