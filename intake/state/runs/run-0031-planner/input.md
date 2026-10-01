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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0031-planner/output.md`

## Approved spec (v1, pinned)

## Problem

When Triage or the Spec writer parks a ticket with a question (NEEDS-HUMAN, or Triage's CLARIFY) and the answer comes back, the design doc returns the ticket to that role with the answer and nothing else. The re-run never sees the question it asked or the options it offered, so it has to rebuild the investigation behind them before it can read the answer as an answer. In the P0 run the requester cites, that was a three-option scope question backed by about 3M context tokens of investigation. Two groups are affected: whoever builds a harness from the doc and `specs/build-harness.md`, and every answered ticket, which pays for a full re-investigation.

The critic loop already hands the re-entering writer its own earlier spec. The human-question path should do the same.

## Evidence

All commands were run from `~/dev/spec-factory` on `main` at `1384157`.

- `sed -n 76p docs/spec-factory.md` →
  `  - A question returns to the role that asked, with the answer; a requester's CLARIFY answer returns to Triage the same way.`
  `sed -n 84p` → `| New request | — | Triage | The request, ticket search |`. Line 68 says "Receives" adds to the INPUT the role prompt already declares. The Triage prompt INPUT is "One raw request, plus search access to open and recently closed tickets". The Spec writer prompt INPUT is "An accepted triage ticket, read access to the repo, and (on revision rounds) the critic's findings and your previous spec". No row, rule or prompt gives a role that re-enters after an answer its own earlier output.
- Routing table rows (lines 84–110) that do give an author its earlier output, all on the critic loop: `| Critic | REVISE | Spec writer (round +1) … | Findings, the spec version they apply to |` and `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic | … round 2+: prior findings, the writer's responses, previous spec version |`.
- `specs/build-harness.md:311` (`factory resolve … --answer`) has the same gap: "appended to `requests/<ID>.md` under `## Answer <n>`, ticket back to the asking role's ready state". No earlier output is added. `:275` (`phase('Triage')`) declares no input list. `:276` declares the writer's input as "ticket + request (+ on round ≥ 2: critic findings, previous spec)". Item 37 (`:388`) checks only that the re-run's `input.md` "contains the answer".
- Reference harness, read only: `git -C ~/dev/nanobot-upstream log --oneline feat/lionbot-v3 -- factory/compose.py` → one commit, `0f2e29136 feat(factory): P0 intake walking skeleton …`. In `git show feat/lionbot-v3:factory/compose.py`:
  - Lines 47–51 cover Triage. The composer adds the request, then `runs/<last finished triage run>/output.md` under "Your previous Triage output (the question you asked is answered above)". This is the as-built Triage half. It fires on every Triage re-run that has an earlier finished run, not only after an answer.
  - Lines 52–65 cover the Spec writer. The composer adds the Triage output and the request. It adds the critic output and `specs/<id>/v<version>.md` only when `rnd >= 1 and version >= 1`. It also adds the `changes-*` and `ruling-*` approvals. It never adds the writer's own NEEDS-HUMAN output, so the Spec writer half has no as-built fix. Nothing here relies on `0f2e29136` as evidence for that half.
- Every NEW acceptance check below was run on this checkout and failed as stated. Every REGRESSION check was run and passed. Outputs are quoted with each item.

## Root cause

The resolution rule at `docs/spec-factory.md:76` names one input, the answer. The routing table has no row for a re-entry after an answer, so nothing declares what that re-run receives beyond the role prompt's INPUT, and no role prompt's INPUT includes a question it asked earlier. `specs/build-harness.md` copies the gap into `resolve --answer` (K, `:311`), the dispatcher input lists (H, `:275–276`) and item 37.

## Proposed change

Two files change: `docs/spec-factory.md` and `specs/build-harness.md`. The diff is about 10 lines. No prompt block changes, so nothing under `prompts/` is re-copied.

**A. Resolution rule** (`docs/spec-factory.md:76`). Replace the bullet with:
`  - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way.`
"The same way" now carries Triage's CLARIFY output, its missing-info list, back as well. This is ticket assumption A1.

**B. Routing table rows** (`docs/spec-factory.md`). Insert these two rows directly after `| Critic | ESCALATE | Human queue | Findings |` (line 93) and before `| Human spec gate | Approved | … |`. Change no existing row.
```
| Human queue, or requester (CLARIFY) | Answered (Triage asked) | Triage | The request with the answer, Triage's previous output (the question or missing-info list the answer is for) |
| Human queue | Answered (Spec writer asked) | Spec writer | The ticket, the answer, the writer's previous output (the spec whose open questions the answer is for) |
```
These rows say what rule A says, so the dispatcher, which is the table and nothing else, carries it too. Writing rule A alone would leave the table silent. Adding the rows alone would leave rule A contradicting them.

**C. Changelog** (`docs/spec-factory.md`). Append after item 33, before the `Declined:` line:
`34. After the P0 run (2026-10-01): a question returns to the role that asked with the answer and that role's previous output, so a re-run Triage or Spec writer reads the answer against the question it asked instead of re-deriving it; a requester's CLARIFY answer follows the same rule, and two Answered rows in the routing table carry the same inputs.`
Leave the Changelog's intro sentence as it is.

**D. `specs/build-harness.md`, consistent with A and B.** "Previous output" means the `output.md` of the role's most recent finished run on that ticket. This is ticket assumption A2: the run that parked the ticket.
1. K, `:311`. After "ticket back to the asking role's ready state", insert:
   `, with the asking role's previous output (the `output.md` of its most recent finished run on the ticket) added to that role's next input (doc §Routing rules)`
2. H, `:275`. Change "`runRole('triage', …)`;" to:
   "`runRole('triage', …)` with input = request, answers appended (+ after an `--answer`: Triage's previous output, K);"
3. H, `:276`. Change "(+ on round ≥ 2: critic findings, previous spec)" to:
   "(+ on round ≥ 2: critic findings, previous spec; + after an `--answer`: the writer's previous output, K)"
4. Item 37, `:388`. Append before ` [NEW]`:
   `; that input also contains Triage's previous output, the first Triage run's text (`Missing info: - which OS`), and its `meta.yaml` `input_sources` lists `runs/<first triage run>/output.md``
5. Add a new subsection directly before `### Gates (every seam)`:
   ```
   ### Answered questions (doc §Routing rules; seam in brackets)

   85. ⟨wf⟩ **Answered question carries the asker's output [S1, S3, S4]:** case `writer-needs-human` (`triage-1.md` ACCEPT; `spec_writer-1.md` `STATUS: NEEDS-HUMAN` whose `## Open questions` lists `- A or B?`) → `status: parked`; `AS daniel factory resolve T-0001 --answer ans.md` → `status: ready-for-spec-writer`; re-running the case → the new spec writer run's `input.md` contains `ans.md`'s text and the writer's previous output (`- A or B?`), and its `meta.yaml` `input_sources` lists `runs/<first spec_writer run>/output.md`; the first spec writer run's `input.md` contains no earlier writer output [NEW]
   ```

## Acceptance

All commands run as written from `~/dev/spec-factory`. On the base, `main...HEAD` is empty.

1. `grep -cF "A question returns to the role that asked, with the answer and that role's previous output" docs/spec-factory.md` → `1` [NEW. Today it prints `0` and exits 1: line 76 ends at "with the answer;"]
2. `awk '/^\*\*Routing table\.\*\*/,/^Any STATUS not in this table/' docs/spec-factory.md | grep -E '^\| [^|]+ \| Answered \(Triage asked\) \| Triage \|' | grep -c "Triage's previous output"` → `1` [NEW. Today `0`: no table row routes an answer to Triage]
3. `awk '/^\*\*Routing table\.\*\*/,/^Any STATUS not in this table/' docs/spec-factory.md | grep -E '^\| [^|]+ \| Answered \(Spec writer asked\) \| Spec writer \|' | grep -c "the writer's previous output"` → `1` [NEW. Today `0`]
4. `awk '/^## Changelog/,/^## Appendix/' docs/spec-factory.md | grep -E '^34\. ' | grep -c "previous output"` → `1` [NEW. Today `0`: the Changelog ends at item 33]
5. `grep -F 'factory resolve ID (--answer' specs/build-harness.md | grep -c "the asking role's previous output"` → `1` [NEW. Today `0`: `:311` stops at "the asking role's ready state"]
6. `grep -F "phase('Triage')" specs/build-harness.md | grep -c "Triage's previous output"; grep -F "runRole('spec_writer')" specs/build-harness.md | grep -c "the writer's previous output"` → `1` then `1` [NEW. Today `0` then `0`]
7. `grep -E '^37\. ' specs/build-harness.md | grep -c "Triage's previous output"; grep -E '^85\. ' specs/build-harness.md | grep -c "writer's previous output"` → `1` then `1` [NEW. Today `0` then `0`: item 37 checks only the answer, and no item 85 exists]
8. `grep -c "a requester's CLARIFY answer returns to Triage the same way" docs/spec-factory.md; grep -c "BLOCKED, a critic ESCALATE, and a planner ESCALATE return to the role that emitted them with the ruling, same round" docs/spec-factory.md` → `1` then `1` [REGRESSION. The CLARIFY clause and the ruling bullet are unchanged. Today `1`, `1`]
9. `git diff main...HEAD -- docs/spec-factory.md | grep -E '^-\|'` → no output, exit 1 [REGRESSION. No existing routing-table row is removed or edited. Today no output]
10. `for f in 01-triage:"## 1. Triage" 02-spec-writer:"## 2. Spec writer"; do n=${f%%:*}; h=${f#*:}; awk -v h="$h" '$0==h{s=1;next} s&&/^```text$/{p=1;next} p&&/^```$/{exit} p' docs/spec-factory.md | diff -q - prompts/$n.md >/dev/null && echo "$n same" || echo "$n differs"; done; git diff --quiet main...HEAD -- prompts/ && echo "prompts untouched"` → `01-triage same`, `02-spec-writer same`, `prompts untouched` [REGRESSION. No prompt block changed and `prompts/` is still a verbatim copy. Today it prints all three lines]
11. `git diff --check main...HEAD` → no output, exit 0 [REGRESSION. Today exit 0]

## Tests to change

none. This repo has no test suite. Item 37 in `specs/build-harness.md` is an acceptance item of another spec, not a test file, and D.4 tightens it on purpose.

## Out of scope

- The other resolution bullets (`docs/spec-factory.md:77–80`). These are BLOCKED, critic or planner ESCALATE, max rounds, SPEC-DEFECT and budget kill, and they stay unchanged, including whether a ruled-on role gets its own earlier output. See the observations below.
- Round counting on an answered re-entry. The existing rule at line 72 already applies, and the new rows add no round annotation.
- Every prompt block, and so every `prompts/` file. This change only adds to Receives, which builds on the prompt's INPUT.
- `plans/P0-intake-skeleton.md`. It is the built skeleton's plan. Its P0-4 still checks only the answer, and line 42 says "the spec's 1–84". With item 85 added that count is stale, but P0-n numbering still cannot collide with it.
- The `specs/build-harness.md` header (`Spec version: 4 · Round: 4`) and its Responses section. They stay as they are.
- `issues/03_triage_reask_input.md`. Under `issues/README.md` it is deleted when the issue is filed, not by this change.
- Anything under `~/dev/nanobot-upstream`.

## Open questions

none. Where the change goes, which is ticket assumption A3, is settled in B as both the rule and the rows. Neither placement is a product decision.

## Risk

The change touches only documents. `docs/spec-factory.md` is the source of truth that harness builders read. The new rows and the tightened item 37 / new item 85 in `specs/build-harness.md` set requirements for the next build:
- The reference composer already meets the Triage half.
- It does not meet the Spec writer half: lines 52–65 never add the writer's NEEDS-HUMAN output. Item 85 will fail against it until the Nanobot side ports that half.

Protected paths touched:
- `intake/**`: only this run's own `output.md`, which the harness designates as the output file.
- `prompts/**`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`: none.

Guardrail note: `docs/spec-factory.md` holds the agent prompt blocks. This change edits only text outside them, and Acceptance item 10 checks that the Triage and Spec writer blocks still match `prompts/` byte for byte.

## Out-of-scope observations

- The ruling path has the same shape of gap. Line 77 returns BLOCKED, critic ESCALATE and planner ESCALATE "with the ruling" and does not say whether the role gets its own escalating output. In the reference composer, a critic re-run after an ESCALATE ruling gets the spec and the ruling but not its own findings. This was raised by Triage and not requested.
- The reference composer adds Triage's previous output on every Triage re-run, including a budget-kill redispatch. That is broader than rule A, which covers re-runs after an answer. It is harmless but not required by the doc.
- On the Nanobot side, a fix here creates a re-port obligation for the Spec writer half of `factory/compose.py`. It is noted here for the operator, not acted on.
