## Critic review — spec v1 (answered question carries the asker's previous output)

Checked from `~/dev/spec-factory` on `main` at `1384157` (`git rev-parse --short HEAD` → `1384157`; `git diff main...HEAD --stat` → empty). Reference harness read only via `git show feat/lionbot-v3:factory/compose.py`.

### What I spot-checked

Cited paths and lines (all exist and read as the spec quotes them):
- `docs/spec-factory.md:76` → `  - A question returns to the role that asked, with the answer; a requester's CLARIFY answer returns to Triage the same way.` Line 68 is the "Receives adds to the INPUT" sentence; line 72 the round rule; lines 77–80 the other four resolution bullets; line 84 `| New request | — | Triage | The request, ticket search |`; line 93 `| Critic | ESCALATE | Human queue | Findings |`; table body is lines 84–110, terminated by `Any STATUS not in this table` at 112.
- Triage prompt INPUT at `:210`, Spec writer INPUT at `:251–252` ("…and (on revision rounds) the critic's findings and your previous spec."). Writer output format has `## Open questions   none | list` (used by item 85's stub). Triage output has `Question for human / Missing info / Reason:`.
- Changelog: item 33 is the last numbered entry, followed by `Declined: …`, then `## Appendix: reviewer prompt`.
- `specs/build-harness.md:275` begins `1. \`phase('Triage')\`: \`runRole('triage', …)\`;`; `:276` contains `runRole('spec_writer')` with input = ticket + request (+ on round ≥ 2: critic findings, previous spec)`; `:311` is the `factory resolve ID (--answer FILE | …` bullet ending the answer clause at "the asking role's ready state"; `:388` is item 37 and checks only that the re-run `input.md` "contains the answer"; item 84 is at `:454` and `### Gates (every seam)` at `:456`, so D.5's insertion point is unambiguous.
- `input_sources` in `meta.yaml` is already a requirement (`specs/build-harness.md:201`, `:294`, items 9, 42, 77), so D.4 and item 85 assert on an existing field, not a new one.
- Reference composer: `git log --oneline feat/lionbot-v3 -- factory/compose.py` → one commit `0f2e29136`. Lines 47–51: `if role == "triage":` adds the request, then `runs/{prior[-1]}/output.md` under "Your previous Triage output (the question you asked is answered above)". Lines 52–65: `elif role == "spec_writer":` adds triage output, request, critic output + `specs/<id>/v<version>.md` only when `rnd >= 1 and version >= 1`, then `changes-*` and `ruling-*` approvals; nothing adds a prior writer `output.md`. `_runs_for` (line 14) filters on `m.get("finished")`. The spec's reading of both halves is accurate, including that the Spec writer half has no as-built fix.
- `issues/03_triage_reask_input.md`, `plans/P0-intake-skeleton.md:42` ("the spec's 1–84") and P0-4 (`:45`) exist as described.

Acceptance commands, run as written today:
- 1 → `0`, exit 1. 2 → `0` (the `awk` range is non-empty, 45 lines, so the `0` is a real miss, not an empty range). 3 → `0`. 4 → `0` (Changelog range 41 lines). 5 → `0`, and the base pattern `factory resolve ID (--answer` matches exactly one line. 6 → `0` then `0`, with both anchors (`phase('Triage')`, `runRole('spec_writer')`) each matching one line. 7 → `0` then `0`. All NEW items fail today for the reason stated.
- 8 → `1` then `1`. 9 → no output, exit 1. 10 → `01-triage same`, `02-spec-writer same`, `prompts untouched` (and the extracted blocks are 35 and 53 lines, matching `prompts/01-triage.md` and `prompts/02-spec-writer.md` line for line, so the awk extraction is doing real work). 11 → exit 0. All REGRESSION items pass today.

### Rubric judgement

1. Grounded: yes. Every path, line and symbol I checked exists; the quoted text matches; the compose.py reading is correct.
2. Testable: yes. Each item is a runnable grep/awk/git command with an exact expected count; the NEW ones fail today and their anchors (`^\| [^|]+ \| Answered \(Triage asked\) \| Triage \|`, `^34\. `, `^85\. `, the K bullet's `factory resolve ID (--answer`) pin the change to the right place, so a row in the wrong table, a Changelog entry under the wrong number, or a K edit on a different bullet would not pass. No item names a test function or internal symbol; item 85 uses the build spec's own stub-fixture vocabulary (`triage-1.md`, `spec_writer-1.md`, `meta.yaml` `input_sources`), consistent with items 35–42.
3. Scoped: yes. Two documents, ~10 lines, one PR. Out-of-scope list is present and the exclusions are sound (other resolution bullets, round counting, prompt blocks, the plan's stale "1–84", the build-spec header). "Tests to change: none" is correct: there is no test suite, and item 37 is an acceptance item the change is meant to tighten.
4. No hidden decisions: the three assumptions (A1 CLARIFY output returned too, A2 "previous output" = `output.md` of the most recent finished run on the ticket, A3 rule + rows) are named and justified rather than made silently. A2 is the right locator: H.2 parks on `NEEDS-HUMAN` without `spec add`, so a writer's NEEDS-HUMAN output exists only at `runs/<id>/output.md`, never under `specs/`. Risk declares the only protected path touched (this run's own `output.md`) and the build-side consequence (item 85 will fail against the reference until the Spec writer half is ported).
5. Consistent: rule A and rows B say the same thing; neither conflicts with line 72 (an answered re-entry is not REVISE/REQUEST-CHANGES/FAILED, so no round increment), with H.4's re-entry states, or with item 42's `input_sources` for a first writer run.
6. Sufficient: insertion points, verbatim row text, verbatim Changelog text and verbatim build-spec edits are all given. An implementer can start without a question.

I also looked for the "passes the rubric but produces the wrong outcome" case and did not find one: the intent (the re-run reads the answer against the question it asked) is exactly what "that role's previous output" delivers, for both Triage paths and the writer path.

### Findings

[NIT] 2 Acceptance items 9, 11 and the `prompts untouched` leg of 10
Problem: these three checks compare `main...HEAD` and pass vacuously if the implementer commits on `main` instead of a branch.
Evidence: on this checkout `git diff main...HEAD` is empty, which is also exactly the state that makes 9, 10c and 11 print the expected result with no change made; items 1–8 and 10a/10b are not affected.
Suggested fix: none required (the spec already states the branch assumption in the Acceptance preamble); if the implementer runs on a branch, as the pipeline intends, the items are real.

No BLOCKING or SHOULD-FIX findings.

### Out-of-scope observations

- D.1's insertion yields two adjacent parentheticals on `:311` ("…(doc §Routing rules) (CLARIFY and NEEDS-HUMAN are questions: …)"). Unambiguous, just clumsy; the implementer may reorder without changing meaning and item 5 still passes.
- The spec's own observation that the reference composer adds Triage's prior output on every re-run (not only after an answer) is correct and, as it says, harmless under rule A.

STATUS: APPROVE
CONFIDENCE: high — every cited path, line and reference-harness claim checked out, and all 11 acceptance commands behaved today exactly as the spec states (NEW fail, REGRESSION pass).
ESCALATIONS: none
