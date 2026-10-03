Type: feature (design doc: Spec writer FORMAT, and possibly the routing table and human gates)

Title: A spec has no place for actions on live or protected state that only the operator can perform after merge

Summary:
Some requests include steps that act on the live instance under a protected path: installing a cron, replacing workspace skills, and a soak check ("the daily cron stays silent on healthy days"). No role may read or write that path, so these steps cannot be acceptance items. The Spec writer FORMAT has no section for them. The requester's concern is that every ported faux spec will either put these steps into Acceptance, where they cannot be checked and end as a SPEC-DEFECT, or drop them silently. Their proposal is an optional `## Operator steps` section for actions the human performs after merge, marked as *not* acceptance. That proposal is a suggestion, not a requirement. Where these steps should go, and whether the pipeline tracks them, is a design decision, so the question below goes to the human.

Evidence:
- Request: "criteria 1–7 are in-repo and verifiable; criterion 8 (live soak) and the operational steps are operator work under the protected path and cannot be acceptance items for any role." In the request, "T-0001" is the **Nanobot-side** store's T-0001 (SPEC-21), not this repo's T-0001 (status parser).
- I checked that the gap exists on this checkout. The FORMAT (`docs/spec-factory.md:286-299`, copied to `prompts/02-spec-writer.md`) lists Problem, Evidence, Root cause, Proposed change, Acceptance, Tests to change, Out of scope ("what must NOT change", `docs/spec-factory.md:293`), Open questions, Risk and Responses. None of them is for work owed after merge. `grep -rc 'Operator steps' docs specs plans prompts` returns 0 for every file.
- No fix has been built in the reference harness. On `~/dev/nanobot-upstream`, `factory/prompts/spec_writer.md` (FORMAT at lines 44-57) and `factory/prompts/context.md` both last changed in the P0 skeleton commit (`git log -1 -- factory/prompts/context.md factory/prompts/spec_writer.md` → `0f2e29136 feat(factory): P0 intake walking skeleton`). Neither mentions operator steps. The draft names no Nanobot-side commit, unlike the other drafts (`issues/README.md`: "each draft names the Nanobot-side commit where the fix already exists").
- What happened in the one observed case:
  - The Nanobot request has a section `### Target operational state (workspace/cron — operator steps)` (`knowledge_vault/spec_factory/requests/T-0001.md:107`) and says "8 is a soak check" (line 154).
  - Triage escalated. The human's answer (line 246) placed the steps "outside this ticket".
  - The writer then listed them under `## Out of scope` in spec v3 ("installing the daily cron, replacing the workspace skill cluster, … and the live soak"). Under Risk it says the end-to-end chain "is only closed by the operator-side soak … placed outside this ticket".
  - The same constraint was restated in escalations from three runs (log `2026-10.jsonl` lines 15, 19 and 28: run-0002-triage, run-0003-spec_writer, run-0005-spec_writer).
  - So in this case the steps did not leak into Acceptance and were not dropped. They were filed under "what must NOT change", which records them as excluded, not as owed. Getting them there took one human answer.

Assumptions (inferences, not stated by the requester):
- The fix belongs in this repo's design doc. The label `nanobot-config` and the "Where" line point at Nanobot's `factory/config.yaml`, but the proposal is a change to the FORMAT. I assume no change to Nanobot's protected-path list is wanted, since that list is correct as it stands.
- Live-state steps are not specific to Nanobot (deploys, migrations, config flips), so the generic design doc is the right level.
- Suggested priority (my suggestion; the human sets priority): medium-low. Every faux spec with an operational section will hit this. The current workaround costs one human answer per ticket and does not lose information.

Question for human:
Where should a spec put actions on live or protected state that only the operator can perform after merge, and does the pipeline track whether they were done?
- (a) Add an optional `## Operator steps` section to the Spec writer FORMAT, as the request proposes. It is explicitly not acceptance, the human approves it at the spec gate, and nothing in routing changes. This touches the §2 block, a re-copy of `prompts/02-spec-writer.md`, the Changelog, and possibly critic rubric 4 or 6 so the critic checks that the section is present.
- (b) Option (a), plus a tracked obligation. A parent whose spec lists operator steps does not close on the parent-close VERIFIED (routing row at `docs/spec-factory.md:106`). It parks until a human records the steps as done. This adds a routing row or human gate, and `specs/build-harness.md` must agree with it.
- (c) No new section. Add a Spec writer RULE that such steps go under `## Out of scope`, named as operator work, with their risk under `## Risk`. This makes the T-0001 v3 handling standard, but the steps stay recorded as excluded rather than owed.

Out-of-scope observations:
- `~/dev/nanobot-upstream/knowledge_vault/spec_factory/P0_MEASUREMENTS.md:10-12` lists "live-state steps under a protected path" among harness defects "fixed on green". I found no such fix on green (see Evidence). That line overstates what was done.
- T-0007 (single-target harness) is related to the protected-path context but is not a duplicate. No duplicate exists among T-0001 to T-0007 on this store.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. The gap and the lack of an as-built fix are confirmed by grep and git log. Choosing among (a), (b) and (c) is a design call, not a fact.
ESCALATIONS:
1. The request asks for a change to an agent prompt (the Spec writer FORMAT). Agent prompts are a guardrail path, and `prompts/**` is generated. Whichever option is chosen, the spec must declare the guardrail and generated-path change under Risk, and `prompts/02-spec-writer.md` changes only by re-copying the block.
2. Unlike the other drafts, this draft names no Nanobot-side fix commit, and none exists. No as-built behaviour is available to check a spec against.
3. No prompt-injection attempt found in the request.
