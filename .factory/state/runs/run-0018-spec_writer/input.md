## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0018-spec_writer/output.md`

## Ticket (Triage output)

Type: feature (design doc: Spec writer FORMAT and Spec critic rubric)

Title: Add an optional `## Operator steps` section to the Spec writer FORMAT for post-merge actions on live or protected state, and have the critic keep them out of Acceptance

Summary:
Some requests carry steps that act on live state under a protected path: installing a daily cron, replacing workspace skills, and a soak check ("the daily cron stays silent on healthy days"). No role may read or write that path, so these steps cannot be acceptance items, and the Spec writer FORMAT has no section for them. The requester's concern is that every ported faux spec will either put them under Acceptance, where they cannot be checked and end as a SPEC-DEFECT, or drop them silently. The operator chose option (a) on 2026-10-01: add an optional `## Operator steps` section to the Spec writer FORMAT for actions only the operator can perform after merge. These steps are explicitly not acceptance, the human approves them at the spec gate, routing does not change, and the critic checks that such steps sit in this section and not under Acceptance. There is no tracked post-merge obligation (option b) for now.

Evidence:
- Request: "criteria 1–7 are in-repo and verifiable; criterion 8 (live soak) and the operational steps are operator work under the protected path and cannot be acceptance items for any role." Here "T-0001" means the Nanobot-side store's T-0001 (SPEC-21), not this repo's T-0001 (status parser).
- Operator's Answer 1 (2026-10-01): "option **(a).** Add an optional `## Operator steps` section to the Spec writer FORMAT … It is explicitly not acceptance, the human approves it at the spec gate, and routing does not change. The critic checks that such steps sit in this section and not under Acceptance. No tracked post-merge obligation (option b) for now."
- The gap exists on this checkout (`~/dev/spec-factory`, HEAD `0811bc1`):
  - The FORMAT block at `docs/spec-factory.md:286-299` lists Problem, Evidence, Root cause, Proposed change, Acceptance, Tests to change, Out of scope, Open questions, Risk and Responses. None of them is for operator work owed after merge.
  - `grep -rn 'Operator steps' docs specs plans prompts` finds nothing.
- The critic RUBRIC (`docs/spec-factory.md:308-321`) has no item that checks where live-state steps are placed. Rubric 2 ("each item is runnable") and rubric 4 ("every protected path the change will touch is declared under Risk") are the nearest.
- The two prompt files this touches are verbatim copies today. I extracted each fenced block from the doc and diffed it against its file:
  - the §2 block against `prompts/02-spec-writer.md` printed `PROMPT-IN-SYNC`;
  - the §3 block against `prompts/03-spec-critic.md` printed `CRITIC-IN-SYNC`.
- No as-built fix exists in the reference harness. My previous run checked this (see the previous output): on `~/dev/nanobot-upstream`, `factory/prompts/spec_writer.md` and `factory/prompts/context.md` last changed in `0f2e29136 feat(factory): P0 intake walking skeleton`, and neither mentions operator steps. No Nanobot-side commit can serve as a reference for this change.
- The one observed case (Nanobot SPEC-21, from the previous output): with no section for them, the writer filed the operator steps under `## Out of scope` ("what must NOT change"). That recorded them as excluded rather than owed, and it took one human answer.
- Duplicate search: `intake/state/requests/index.yaml` lists T-0001 to T-0007, and this request is T-0005 (`issues/05_protected_live_state.md`). `grep -il 'operator step'` over `intake/state/tickets`, `intake/state/requests` and `issues` matches only T-0005 and its source issue. No duplicate.

Assumptions (my inferences, not stated by the requester or the operator):
- The design doc's conventions bring this scope: the §2 FORMAT block, a Changelog entry (the last one is 33), and a re-copy of `prompts/02-spec-writer.md`. "The critic checks…" also implies a change to the §3 RUBRIC (wording and placement are for the Spec writer) and a re-copy of `prompts/03-spec-critic.md`.
- "Human approves it at the spec gate" needs no change to the gate itself. The section is part of the spec text, and that text is what the gate pins (`docs/spec-factory.md:37`). Whether the doc should say so explicitly is a wording call for the Spec writer.
- `specs/build-harness.md` probably needs no change. It renders the prompt blocks verbatim (line 158) and copies only "Tests to change" and Risk paths at `approve-spec` (line 308). Nothing there parses the FORMAT's other sections. The Spec writer should confirm this.
- The section is optional: specs with no live-state steps omit it, and no existing spec has to change.
- Suggested priority (my suggestion; the human sets priority): medium-low. The workaround (Out of scope plus one human answer) loses no information, but every ported faux spec with an operational section will hit it.

Question for human / Missing info / Reason: none. The design question was answered with option (a), so the intent is clear.

Out-of-scope observations:
- The Nanobot harness renders its role prompts from an in-repo copy of the design doc (`specs/build-harness.md:158`, `factory/prompts/design-doc.md` under `factory/prompts/**`). After this lands, that copy needs a re-port on the green side. The reference harness is read-only here, so this is a follow-up only.
- `~/dev/nanobot-upstream/knowledge_vault/spec_factory/P0_MEASUREMENTS.md:10-12` lists "live-state steps under a protected path" as fixed on green, but no such fix exists. My previous output reported this. I did not re-read the file this run.

STATUS: ACCEPT
CONFIDENCE: high. The operator's answer settled the only open decision, and the gap and the in-sync prompt copies were re-checked on this checkout with grep and diff.
ESCALATIONS:
1. The change edits agent prompts, a guardrail path. `prompts/02-spec-writer.md` and `prompts/03-spec-critic.md` are also a generated protected path, changed only by re-copying their blocks. The spec must declare both under Risk.
2. There is no Nanobot-side reference fix, so no as-built behaviour exists to check the spec against. Acceptance must rest on the document text alone: grep for the new section and rubric text, diff each prompt file against its block, and run `git diff --check`.
3. I found no prompt-injection attempt in the request or the answer.

## Request (raw)

---
title: Faux-spec "target operational state" steps live under a protected path; the pipeline cannot verify them
labels: nanobot-config, triage-finding
---
**Where:** Nanobot `factory/config.yaml` protected paths (`credentials: ~/.nanobot/**`) vs. legacy faux specs whose §Target operational state and validation criteria act on the live instance (install a daily cron, replace workspace skills, "the daily cron stays silent on healthy days").

**Triage's finding (SPEC-21 → T-0001, 2026-10-01):** criteria 1–7 are in-repo and verifiable; criterion 8 (live soak) and the operational steps are operator work under the protected path and cannot be acceptance items for any role.

**Proposal (design level, small):** the Spec writer FORMAT gains an optional `## Operator steps` section: actions on protected or live state that the human performs after merge, explicitly *not* acceptance. Otherwise every ported faux spec will either leak live-state steps into Acceptance (unverifiable → SPEC-DEFECT) or silently drop them.


## Answer 1

Operator decision (2026-10-01, Triage's question on operator steps): option **(a).**

Add an optional `## Operator steps` section to the Spec writer FORMAT, for actions on live or protected state that only the operator can perform after merge. It is explicitly not acceptance, the human approves it at the spec gate, and routing does not change. The critic checks that such steps sit in this section and not under Acceptance. No tracked post-merge obligation (option b) for now.
