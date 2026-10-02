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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0047-spec_writer/output.md`

## Ticket (Triage output)

Type: feature (design-doc change: the spec gate cannot do its job when the Problem section is unreadable to the person approving it, but no rule is broken today, because no rule exists)

Title: Spec writer and critic: the Problem section must be readable, in plain language, by the operator who approves the spec at the gate

Summary:
The operator approves every spec at the spec gate and reads the Problem section first. Today the design doc only asks the Problem section for "what's wrong or missing, for whom". Nothing in the writer's rules or the critic's rubric checks that the operator can actually read it. On T-0010 the approved Problem opened with harness terms of art that were never explained (pinned, parent-close VERIFIED, archive, exit 2, parks). The operator could not tell what it meant and approved only after someone translated it. The requester wants the Spec writer FORMAT and RULES (§2, re-copied to `prompts/02-spec-writer.md`) to require a plain-language Problem written for the operator at the gate, with each term of art glossed in plain words the first time it appears and the detail moved to Evidence and Root cause. They also want the Spec critic rubric (§3, re-copied to `prompts/03-spec-critic.md`) to check this, so a spec like T-0010 v2 would get a finding.

Evidence:
- Request: on 2026-10-02 at the T-0010 gate the operator said "the problem's prose is incomprehensible. what does it mean". After the translation ("the factory has no handler for a ticket whose spec predates the spec store; when such a ticket finishes, it parks and the documents don't say what you do"), the operator approved it. The quote is not recorded in the repo, so I am relying on the request for it.
- Verified: `intake/state/specs/T-0010.md` line 3 (the Problem body) begins exactly as the request quotes: "Some specs were pinned before `factory init` created `openspec/`. A parent whose spec was pinned that way has no `openspec/changes/<ID>/` folder. Its parent-close VERIFIED runs `factory archive`, which exits 2, and `build.js` parks the parent (build spec part H)."
- Verified: critic round 2 (`intake/state/runs/run-0045-critic/output.md`) ends `STATUS: APPROVE`, and none of its findings is about whether the Problem reads clearly. In round 1 (`run-0043-critic/output.md` line 22) one finding said a sentence was garbled, but it was about the proposed design-doc text, not the Problem section. Gate approval: `intake/state/approvals/T-0010/spec-v2.yaml` (`by: dphang`, `at: '2026-10-02T07:38:42+00:00'`, `version: 2`).
- Verified: `docs/spec-factory.md` line 308 and `prompts/02-spec-writer.md` line 45 both read `## Problem          what's wrong or missing, for whom`. The writer's RULES (§2, from line 261) do not mention readability. Critic RUBRIC items 1–6 in `prompts/03-spec-critic.md` (lines 5–18: Grounded, Testable, Scoped, No hidden decisions, Consistent, Sufficient) say nothing about who the reader is or plain language. `grep -n -i "plain language\|terms of art"` over the doc, prompts and build spec → no matches.
- Verified: `prompts/02-spec-writer.md` is currently identical to the §2 block in the doc (the diff of the extracted block against the file printed nothing). The reference harness has no existing fix: `grep -rn -i "plain language\|terms of art" ~/dev/nanobot-upstream/factory/` → no matches. This matches the request's "Fix as implemented on the Nanobot side: none".
- Duplicate search: the ticket titles T-0001–T-0010 in `intake/state/tickets/`, the issue index `issues/README.md` (#1–#10), and a grep of `intake/state/tickets` and `intake/state/specs` for plain/readab/terms of art/gloss found no ticket on Problem-section readability. T-0005 also changed the writer FORMAT, but it added `## Operator steps`, a different subject. I could not search GitHub directly: `gh issue list` → `HTTP 401: Requires authentication`.

Assumptions (inferences, labeled):
- A1 (inference): the rule is about the Problem section only. The request does not ask for plain language in Evidence, Root cause or design.md, and it explicitly sends the technical detail there.
- A2 (inference): the four bullets under "Proposed fix" are the requester's suggestion, not required wording. What is required is that (a) the writer is told who the Problem's reader is and to gloss terms of art, and (b) the critic checks it. The writer picks the wording and whether the check goes in rubric 1 or 6 (the request offers either), and records the choice under Decisions, as T-0005 did.
- A3 (inference): the "count harness terms of art in Problem" metric is measurement only and does not gate, as the request states. The request gives no list of terms or counting method beyond five examples (pinned, parent-close, archive, park, exit codes). If the spec adds the metric, the writer must define the list and method and show it to the gate as a Decision or an open question, not decide it silently. If the metric is added to the P0 metric table, that is a change to `plans/P0-intake-skeleton.md` (table at line 57).
- A4 (inference): a doc change also adds a Changelog entry, keeps `specs/build-harness.md` consistent, and re-copies `prompts/02-spec-writer.md` and `prompts/03-spec-critic.md` from the changed blocks, as the run context's conventions require. `prompts/**` is a protected (generated) path, changed only by re-copying, so the spec's Risk section must declare it.
- A5 (inference): acceptance must not be satisfied only by greps showing that the new words exist in the doc. Those checks would pass the moment the text is pasted in and prove nothing about readability. Good acceptance also exercises the critic rule on a real example: given the T-0010 v2 Problem text, the critic rubric as written must produce a finding on it.
- Priority (suggestion only; priority is a human call): p0, as the requester labeled it and as the operator restated when they asked for it to be filed as a p0 GitHub issue. Every future spec passes this gate.

Reason: ACCEPT. The intent is clear and stated in the requester's terms: the Problem section must be readable by the operator who approves it, and the critic must catch it when it is not. The evidence checks out against the repo. No product decision is needed beyond the wording and placement choices the writer can make and show at the gate.

Out-of-scope observations:
- The relayed user request also asks for this to be filed as a GitHub issue with priority p0. Triage cannot do that, and `gh` is unauthenticated here (HTTP 401). The HEAD commit `e183f71` already says the issue body is waiting in `intake/requests/` (`11_plain_language_problem.md`) for gh auth. Once it is filed, `issues/README.md` needs a row #11.
- T-0011's ticket title is the filename (`title: 11_plain_language_problem` in `intake/state/tickets/T-0011.yaml`), not a readable title. That is an intake-harness quirk under the protected `intake/**` path. I did not change it.

STATUS: ACCEPT
CONFIDENCE: high. I checked every citation in the request against the repo (the Problem text, the critic round-2 verdict, the gate approval, the FORMAT line, the rubric, that the prompt copy matches the doc, and that the reference harness has no fix). The one gap: I could not search GitHub issues directly because gh auth failed, so the duplicate check relied on the local issue index.
ESCALATIONS: none

## Request (raw)

---
title: Spec writer: the Problem section must be readable by the operator who approves it, in plain language
labels: p0, design-doc
---
**Where:** `docs/spec-factory.md` §2 Spec writer, the FORMAT line `## Problem          what's wrong or missing, for whom` and the RULES; `prompts/02-spec-writer.md` (copy of that block); §3 Spec critic rubric (nothing checks readability for the gate's reader).

**What happened (2026-10-02, spec-factory intake T-0010):** the operator read the approved spec at the gate and said "the problem's prose is incomprehensible. what does it mean". The Problem section opened: "Some specs were pinned before `factory init` created `openspec/`. A parent whose spec was pinned that way has no `openspec/changes/<ID>/` folder. Its parent-close VERIFIED runs `factory archive`, which exits 2, and `build.js` parks the parent (build spec part H)." Five terms of art in three sentences (pinned, parent-close VERIFIED, archive, exit 2, parks), none defined, written for the harness builder. The critic approved it in round 2 without a finding on it. Once translated ("the factory has no handler for a ticket whose spec predates the spec store; when such a ticket finishes, it parks and the documents don't say what you do"), the operator approved it.

**Why it matters:** the spec gate is the one place the human decides, and the Problem section is what they read first. A Problem the operator cannot read without a translator defeats the gate: they approve on the translator's word, not the spec's. Every spec the factory writes passes this gate.

**Proposed fix (design doc §2 and §3, re-copy prompts/02 and 03):**
- FORMAT: `## Problem          what's wrong or missing, for whom, in plain language for the human who approves this spec: no harness terms of art (pinned, parent-close, archive, park, exit codes) without a plain gloss on first use; the detail belongs under Evidence and Root cause`.
- RULES, Spec writer: "The Problem section is written for the operator at the gate, not for the harness builder or the next role. If a reader who has not seen the design doc could not say what is wrong and for whom, rewrite it."
- Critic rubric: add to rubric 1 or 6: "Problem reads without the design doc: a plain statement of what is wrong and for whom; terms of art are glossed."
- Acceptance for the writer's own output (P0-5 style measurement, not gating): count harness terms of art in Problem; report in the P0 metric table.

**Fix as implemented on the Nanobot side:** none; prompts re-copy on green follows the doc change.
