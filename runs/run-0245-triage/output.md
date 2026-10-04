Type: feature

Title: Amend a pinned spec after planning, and a critic check for scenarios that depend on another approved, unmerged ticket

Summary:
Once the operator approves a spec at the spec gate (the one human sign-off on a design before code is written), the harness pins it: it freezes that version and copies its scenarios into the ticket's change folder. From then on, no command can change it. Yet its acceptance scenarios can stop passing when another ticket merges first, even though the code is correct. The requester needs two things, which the operator approved as one ticket:
- A, a human-only `factory spec amend <parent> --file <amended spec> --reason "<line>"` command. It works at any state after pinning and before archive (the step that writes a closed ticket's scenarios into the repo's current-truth specs). It writes a new spec version, re-pins the change folder and records the amendment with a diff summary and a log event. Every later role run then receives the amended version. It refuses while a sub-ticket is in flight. Merged sub-tickets keep their results, and the record notes which scenarios changed after they merged.
- B, a critic rule at the spec gate. The critic is the agent that grades a spec before the operator sees it. For each scenario, it asks whether the scenario depends on behaviour that an approved but unmerged ticket changes. If it does, that is a finding: the finding names the ticket and its decision, and the scenario's setup must hold whichever ticket merges first.

Evidence:
- The request names two incidents, and I read the record of each.
  - Nanobot v3.5, 2026-10-04: SPEC-20 (Nanobot ticket T-0002) merged and made WhatsApp groups fail closed when no policy store exists. Two pinned scenarios of SPEC-05 (Nanobot ticket T-0008) create no store, so they cannot pass. The implementer reported itself blocked in run-0166. The workaround is a ruling: a human's written instruction, filed under the ticket's approvals, that the harness passes to later runs. `~/dev/nanobot-upstream/.factory/state/approvals/T-0008.1/ruling-1.md` and `.../T-0008/ruling-1.md` exist. Each says "Test setup only. No behaviour change, and no change to any THEN" and seeds a `policies.json`. The request expects the same seeding in two more Nanobot specs, SPEC-01 and SPEC-04.
  - spec-factory, 2026-10-03: `.factory/state/approvals/T-0012/amendment-1.md` exists. It records that the operator "Applied in place to `specs/T-0012/v3.md` (the pinned version every checker reads)". That was a hand edit; no command produced it.
- In the dev checkout, only the gate can change a spec. `factory/cli.py:669-672`: `approve-spec` refuses unless the ticket is `awaiting-spec-gate`, and `--edit` writes a new version only past that check.
- A ruling reaches later runs, but archive never sees it. `factory/compose.py:141-222` hands `ruling-*` approval files to role runs as "Human ruling". `factory/specstore.py:336-357` (`archive`) applies the deltas from the pinned change folder, so a ruling's change never reaches current truth.
- No amend command exists yet. `grep -n "amendment" factory/*.py` returns nothing in the dev checkout, and `grep -n amend` in the runtime checkout's `factory/cli.py` and `factory/compose.py` returns nothing. The request cites no reference-harness commit, so I had no as-built fix to check.
- The design doc already allows the human to amend: `docs/design.md:102` says "the human amends the spec and re-plans". Line 104 says "The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive". No command implements this.
- The operator approved it: `.factory/answers/operator-decisions-2026-10-04.md` says "#44: approve parts A (spec amend, human-only, logged) and B (critic cross-ticket check) as one ticket, pre-approved." It quotes the operator's words, and the harness relayed the same words verbatim for this run.

Assumptions:
- One claim in the request is narrower than it reads. Only a ticket in the `planned` state has no route back to the gate. A parked ticket that has a spec version does have one: `factory resolve <id> --to spec-gate` (`factory/cli.py:758-764`). But that route goes through `approve-spec`, which moves the ticket to `ready-for-planner`. For a parent with merged sub-tickets, that means re-planning from scratch, not amending, so the need still stands. (inference)
- When the amended spec is "handed to every later role run", I take that to mean the runs that read the pinned spec: implementer, reviewer, verifier and the parent-close run. The amendment record should be handed to them the way a ruling is now. (inference)
- In A, "re-pins the change folder" includes `archive` writing the amended scenarios into current truth. That is the stated harm, so the acceptance tests should check it. (inference)
- Part B works across tickets, and #40 part C (tests a decision overturns, now T-0022, which is in triage) works within one ticket. Both change the critic's prompt. The spec writer should check the two critic edits for conflicts. (inference)
- Part A changes harness code (`factory/**`, `bin/factory`). Part B changes the critic prompt in the design doc and its copy under `docs/prompts/`. Both are protected paths, so the spec's Risk section must declare them. (inference)
- Suggested priority (a suggestion; priority is the human's call): after the small fixes already queued. Today's workaround, a ruling, still lets tickets build. Archive is the only step it breaks.

Reason: ACCEPT. There is no duplicate. Issue #44 in `dev/issues.md` is this request and has no ticket yet. T-0022 (#40) covers only the within-one-ticket case. The intent is clear, and the operator has already approved the product call (A and B as one ticket).

Out-of-scope observations:
- The T-0012 amendment note itself proposes a follow-up: `init` could write a store-level `.gitattributes` with `runs/** -whitespace`, so that run records stop failing `git diff --check`. I found no ticket for it.

STATUS: ACCEPT
CONFIDENCE: high. I read every cited record and the harness lines behind each claim, and the operator's approval is on file in the decisions record.
ESCALATIONS: none
