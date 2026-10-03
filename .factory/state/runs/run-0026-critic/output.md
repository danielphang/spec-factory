## Critic review — T-0007 spec v2 (role-context block)

### What I checked

Repo: `~/dev/spec-factory`, `main` now at `de3c542` (two intake commits after the spec's `172a71e`); `git diff --stat 172a71e HEAD -- docs specs plans prompts README.md` prints nothing, so every cited line still holds. Reference harness: `~/dev/nanobot-upstream` at `2cb06b783` on `feat/lionbot-v3`, read with `grep`/`sed` only.

Cited paths, all confirmed by reading them:
- `docs/spec-factory.md:50` is the "**What the harness itself owns** … from *only* its declared sources" paragraph; `:52` is "**Model per role, starting point.**" (so part A's insertion point is unambiguous); `:68` begins `**Routing table.**` and ends with the "Receives" sentence part B appends to; `:641` is Changelog item 33, followed by a blank line and `Declined:`; piece 3 (`:39`) is "Isolated run per role … preamble + role prompt as the system prompt and the inputs on stdin", so part A's "(piece 3), not in the system prompt" is consistent.
- `specs/build-harness.md:127` is the D8 row; `:158` is the `factory render` bullet naming `factory/prompts/**` as guardrail; `:201`, `:294`, `:393` contain exactly the anchor strings parts D.1–D.3 replace or append to (each anchor occurs once in the file; asserted while applying).
- `factory/compose.py:11,35,39,42` in the reference: `PROMPTS/"context.md"` is read into `parts` first and only `add()` appends to `sources` (E3 holds).
- `intake/state/runs/{run-0019-critic,run-0022-critic,run-0023-triage,run-0024-spec_writer,run-0025-spec_writer}`: `input.md` line 1 is `## Context for this run …` and `meta.yaml` `input_sources` lists only the store paths the spec quotes (E4 holds).
- Pending specs: `intake/state/specs/T-000{1,2,3,5}/v1.md` each append a Changelog entry after item 33 (E5 holds). T-0002 edits `specs/build-harness.md` at `:195`, `:268`, `:272`, `:276`, `:495`, none of the three lines part D changes; T-0004 and T-0006 touch neither document. The merge-order note is accurate.

Acceptance: I ran all 13 commands verbatim with bash on `main`, and again on a scratch clone with parts A–D applied by scripted replacement of the spec's exact strings (`2 files changed, 7 insertions(+), 4 deletions(-)`, matching the spec's count).
- `main`: `0`; `0` (exit 1); `CONTIGUOUS LAST-IS-OTHER`; `0` (exit 1); `begins with the text of|`; `0` (exit 1); 7–10 clean; `docs/spec-factory.md:0` / `specs/build-harness.md:0` (exit 1); 13 clean. Matches the spec's "today" column.
- Scratch clone: `5`; `1`; `CONTIGUOUS LAST-IS-ROLE-CONTEXT`; `2`; `critic run>/input.md\` — the file \`factory run compose\` wrote — begins with the role-context block|spec_writer run>/input.md\` begins with the role-context block|`; `1`; 7–10 clean; 11 as above; 12 empty (exit 1); 13 clean. Every NEW criterion flips for the stated reason; every REGRESSION criterion stays clean.

### Findings

[SHOULD-FIX] 4/5 — Proposed change A ("Its text is the same for every role and every run against that repo") and D.1 ("the block is the same for every run against the repo, so it is not one of the `input_sources:`")
Problem: the reason given for exempting the block from `input_sources` is that it never varies between runs, but the spec's own Out-of-scope bullet ("Recording which version of the block a run saw … Until then the version is visible only in each run's `input.md`") says it does vary over time, so the design text would record a justification the same spec contradicts.
Evidence: spec v2 lines 101, 122, 165; `intake/instance/context.md` is an editable file with no version pin, and nothing in the reference harness freezes it per run (`factory/compose.py:35` reads it fresh on every compose).
Suggested fix: ground the exemption in what Open questions already says — the block is not a store path, and `input_sources` lists declared store paths only — e.g. D.1 "… ahead of those sources; it is not a store path, so it is not one of the `input_sources:` (its text is in `input.md`)", and in A "Its text does not vary by role or by run" or simply "Its text is the same for every role"; criterion 6 still passes as long as "not one of the `input_sources:`" is kept verbatim.

[NIT] 2 — Acceptance criterion 1
Problem: the five-phrase grep passes against a stub that pastes just the five phrases (I tried it: prints `5`), so it checks presence of wording, not the paragraph.
Evidence: scratch run on `main` with the five phrases inserted as a bare line after `:50`.
Suggested fix: none needed; part A gives the paragraph verbatim and the gate human reads a 7-line diff, so this technical rubric miss does not matter. Noting it so no one mistakes criterion 1 for a semantic check.

[NIT] 1/5 — Acceptance preamble and Risk › Merge order
Problem: `main` has moved to `de3c542` and T-0001…T-0006 are now `status: ready-for-planner` (commit `de3c542`, "operator approves T-0001..T-0006 spec v1 at the gate"), so "today means `main` at `172a71e`" and "all awaiting the gate" are stale.
Evidence: `git log --oneline 172a71e..HEAD`; `intake/state/tickets/T-000{1,2,3,5}.yaml`.
Suggested fix: no text change required because the documents are byte-identical and criteria 3 and 9 already tolerate any merge order; if the writer touches the spec for the SHOULD-FIX, refresh the SHA and say the four specs are approved and ahead in the queue.

No other findings. Scope is one small PR; "Tests to change: none" is right for a documents-only repo and the item-42 rewrite is correctly surfaced under Risk for the gate rather than hidden; the only product choice (option (b) on `input_sources`) is stated, attributed to Answer 2, and marked as overturnable at the gate; `prompts/` is untouched because the new text is outside every fenced block (criterion 8 confirms). An implementer can apply parts A–D from the spec text alone — I did.

### Prior findings
None (round 1).

STATUS: APPROVE
CONFIDENCE: high — every cited line, the reference composer, five live run directories, and all 13 acceptance commands were re-checked by command on `main` and on a scratch application of A–D, with outputs matching the spec.
ESCALATIONS: none
