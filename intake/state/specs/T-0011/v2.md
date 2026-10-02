## Problem

The operator approves every spec before any work on it starts. This approval step is called the spec gate, and the first part of the spec the operator reads there is the Problem section. Two agents produce what the operator reads: the spec writer, which writes the spec, and the spec critic, which reviews it before it reaches the operator. Neither agent's instructions say that the Problem section has to make sense to the operator.

On 2026-10-02 this went wrong. The Problem section of ticket T-0010's spec was written in the factory's internal vocabulary. The operator could not tell what it meant ("the problem's prose is incomprehensible. what does it mean") and approved it only after someone translated it into plain words. The critic had approved the same text without comment. If the operator can only follow a spec through a translator, they are approving the translator's account and not the spec, and the approval step stops doing its job.

This affects the operator, who approves every spec the factory writes, and everyone who relies on that approval meaning something.

## Evidence

All commands were run from `~/dev/spec-factory`, branch `main`, HEAD `f0f7fa8`, unless noted.

**What the operator read and approved**
- The operator's quote and the translation come from the request. The repo does not record them.
- `sed -n 3p intake/state/specs/T-0010/v2.md` starts: "Some specs were pinned before `factory init` created `openspec/`. A parent whose spec was pinned that way has no `openspec/changes/<ID>/` folder. Its parent-close VERIFIED runs `factory archive`, which exits 2, and `build.js` parks the parent (build spec part H)."
- `intake/state/approvals/T-0010/spec-v2.yaml` reads `by: dphang`, `at: '2026-10-02T07:38:42+00:00'`, `version: 2`.
- The round-2 critic output, `intake/state/runs/run-0045-critic/output.md`, has one finding: `[SHOULD-FIX] 2, 6 — Proposed change C, item 91 (a) setup` (line 17). Line 30 is `STATUS: APPROVE`. No finding mentions the Problem section.

**What the instructions say today**
- The writer's FORMAT line for Problem is `## Problem          what's wrong or missing, for whom` at `docs/spec-factory.md:309` and `prompts/02-spec-writer.md:45`.
- The writer's RULES (`docs/spec-factory.md:279-302`) say nothing about who reads the Problem section.
- The critic's RUBRIC (`docs/spec-factory.md:350-364`) has six items. Item 6, at line 364 and `prompts/03-spec-critic.md:18`, is `6. Sufficient: an implementer could start without asking a question.` No item mentions the operator or plain language.
- A finding below BLOCKING changes nothing before the gate. `docs/spec-factory.md:147` says "SHOULD-FIX and NIT ride with APPROVE; the author may address them". So the spec reaches the operator with its text unchanged.
- `grep -rn -i "plain language\|plain words\|terms\? of art\|plain gloss" docs specs plans prompts` prints nothing (exit 1).
- The prompt copies are verbatim today. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | diff - prompts/02-spec-writer.md` prints nothing (exit 0). The same command for `ROLE: Spec critic\.` against `prompts/03-spec-critic.md` also prints nothing (exit 0).
- No reference fix exists. `grep -rn -i "plain language\|plain words\|terms\? of art" ~/dev/nanobot-upstream/factory/` (branch `feat/lionbot-v3`) prints nothing (exit 1). This agrees with the request ("Fix as implemented on the Nanobot side: none").

**What a critic rule actually does (trials)**
The question is whether adding a rubric line makes the critic flag T-0010's Problem. I ran the critic prompt as a system prompt with `claude -p --safe-mode --model fable --tools "" --max-turns 1`. `fable` is the critic's model in `intake/instance/config.yaml`. The input was the T-0010 v2 spec with its `## Responses` section removed, so that the critic reviews it as round 1. A run counts as a hit when it has a `[BLOCKING]` finding located at the Problem section. As a control I used the same spec with only the Problem replaced by a plain rewrite of the same content; the rewrite is given in full in Acceptance.

| Critic rubric item 6 | T-0010 Problem | Plain control |
|---|---|---|
| Unchanged (today) | 0 of 11 runs; the real round-2 run also approved | 0 of 9 |
| Outcome only ("the operator could say what is wrong and for whom … glossed … that is BLOCKING"), no reader framing | 0 of 2 (one NIT, otherwise no finding) | not run |
| Reader framing ("read it as that operator, who has not read the design doc …"), no examples | 0 of 2 (SHOULD-FIX both times, so APPROVE) | 0 of 1 |
| Reader framing plus T-0010's own five words as examples | 3 of 3 | 0 of 2 |
| **Proposed wording (Proposed change C): reader framing plus generic categories of terms of art** | **9 of 10** (2/2, 2/3, 5/5) | **0 of 10** |

Two conclusions follow. First, the request's suggested rubric line, which states only the outcome, did not produce a finding the operator would ever see. What works is telling the critic to read the section as the operator, who has not read the design doc. Second, a rule that names T-0010's own words blocks T-0010 but drifts toward matching those words. On T-0009, a spec those words do not appear in, that variant gave SHOULD-FIX 2 of 2. The proposed wording names categories of terms instead of T-0010's words.

**Size and other documents**
- I applied Proposed change A–E in a scratch clone (`git clone ~/dev/spec-factory`, branch `ticket/T-0011` off `f0f7fa8`). `git diff --stat main...HEAD` showed `docs/spec-factory.md | 20 ++++++++++++++++++--`, `prompts/02-spec-writer.md | 11 ++++++++++-` and `prompts/03-spec-critic.md | 8 +++++++-`: 35 insertions and 4 deletions. I ran every Acceptance command on that branch and on a clean clone of `main`, and each item records the result.
- `specs/build-harness.md` needs no change. `factory render` (line 158) renders the doc's prompt blocks verbatim. `grep -c "Sufficient" specs/build-harness.md` → `0`, so the build spec quotes no rubric text. `docs/spec-factory.md:74` lists the Problem section only by name in `proposal.md`, and that stays true.

## Root cause

The design doc's §2 Spec writer block defines the Problem section by its content only ("what's wrong or missing, for whom") and does not say who reads it. The FORMAT line is `docs/spec-factory.md:309`, and the RULES are lines 279-302. The §3 Spec critic rubric (lines 350-364) has no item that judges the Problem section from the operator's side. Item 6 judges sufficiency only for the implementer. The critic is steeped in harness context, so it finds that vocabulary readable unless it is told to read as someone who lacks the context (see the trials). `prompts/02-spec-writer.md` and `prompts/03-spec-critic.md` are verbatim copies of those blocks and have the same gap.

## Proposed change

Three files change: `docs/spec-factory.md` and the two prompt files re-copied from it. The diff is 35 lines added and 4 removed. Wrap each block's text at the same width and indent as its neighbours.

**A. §2 FORMAT, the Problem line** (`docs/spec-factory.md:309`, under `=== proposal.md`). Replace the line `## Problem          what's wrong or missing, for whom` with:
```
## Problem          what's wrong or missing, for whom, in plain words for
                    the operator who approves it at the spec gate (a
                    software engineer or product manager: keep the
                    technical substance); each term of art glossed on
                    first use; the detail goes under Evidence and Root
                    cause
```

**B. §2 RULES, a new bullet** (`docs/spec-factory.md`). Insert it after the bullet "Open questions stay open. …" and before "Anti-Goodharting: the critic scores you …":
```
- Write the Problem section for the operator who approves the spec at
  the gate, not for the harness builder or the next role. That reader is
  technical, a software engineer or product manager: keep the technical
  substance, and drop only this pipeline's internal vocabulary. A reader
  who has not read the design doc, the build spec or the rest of the
  spec must be able to say what is wrong and for whom. Use plain words,
  gloss each term of art on first use, and leave the detail to Evidence
  and Root cause.
```

**C. §3 RUBRIC item 6** (`docs/spec-factory.md:364`). Replace `6. Sufficient: an implementer could start without asking a question.` with:
```
6. Sufficient: an implementer could start without asking a question, and
   the operator at the gate could read the Problem section. Read it as
   that operator, a software engineer or product manager who has not read
   the design doc, the build spec or the rest of this spec. Terms of art
   (names of harness parts, commands, states, files, exit codes, section
   letters) need a plain gloss on first use; ordinary software vocabulary
   does not. If that reader would need a translator to say what is wrong
   and for whom, that is BLOCKING.
```
Use this wording as given. The trials in Evidence show that the "read it as that operator" framing and the explicit BLOCKING are what make the check fire. Each design call here is visible to the gate and can be overridden:
- **Rubric 6, not rubric 1 and not a new item 7.** The request offered 1 or 6. Item 6 already asks whether a reader could act "without asking a question", and this extends it to a second reader. In trials, a separate item 7 behaved like the same text inside item 6 (both tried with T-0010's example words: BLOCKING 2 of 2 on T-0010, 0 of 1 on the control), so the choice is about structure, not effect.
- **BLOCKING.** A lower severity rides with APPROVE (line 147), so the operator would get the same unreadable text. That would not meet the request ("a Problem the operator cannot read without a translator defeats the gate"). The rule is bounded: BLOCKING applies only when the reader "would need a translator". An unglossed term that does not stop them is left to the critic's ordinary judgment.
- **Categories instead of the request's five words.** The request's example terms (pinned, parent-close, archive, park, exit codes) are T-0010's own words. Putting them in the rubric would fit the rule to the test case (see Evidence). The FORMAT line (A) and the rule (B) say "term of art" for the same reason.

**D. Changelog** (`docs/spec-factory.md`, `## Changelog`). Append one entry numbered one past the last entry at merge time. That is `41` on `main` today. The text:
`41. After the T-0010 spec gate (2026-10-02), where the operator could not read an approved Problem section without a translation: the spec writer writes the Problem section in plain words for the operator who approves the spec at the gate (a software engineer or product manager, so it stays technical), with each term of art glossed on first use and the detail left to Evidence and Root cause; critic rubric 6 reads the Problem as that operator, and one they would need a translator for is BLOCKING.`

**E. Re-copy the two prompt blocks.** Regenerate each file from its edited block and do not hand-edit it:
- `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md > prompts/02-spec-writer.md`
- `awk '/^ROLE: Spec critic\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md > prompts/03-spec-critic.md`

**Not proposed: the term-count metric.** The request suggested counting harness terms of art in each Problem section and reporting the count in the P0 metric table (`plans/P0-intake-skeleton.md`, "What you measure"). It was a measurement, not a gate. I left it out for three reasons:
- The P0 run it would report into has already happened (Changelog 36, "After the P0 run").
- That table already has the row that measures this directly: "Would you approve it at the gate unedited?".
- A count needs a fixed word list. The request gives none, and a fixed list rewards swapping words rather than writing plainly. The trials show the same effect on the critic.

The gate can ask for the metric as a follow-up ticket.

## Acceptance

Run every command with bash from the root of the PR branch's checkout of `spec-factory`, with `main` as the base. "Today" means `main` at `f0f7fa8`. Results for both were recorded in the scratch clones described in Evidence.

1. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | awk '/^## Problem /{f=1;print;next} f&&/^                    [^ ]/{print;next} {f=0}' | tr -s ' \n' '  ' | grep -o -e 'plain words' -e 'operator who approves' -e 'spec gate' -e 'term of art' -e 'Evidence and Root cause' | sort -u | wc -l | tr -d ' '` → `5`. The writer's FORMAT defines the Problem section as plain words for the operator at the spec gate, with terms of art glossed and the detail sent to Evidence and Root cause. [NEW: prints `0` today, because the Problem line is only "what's wrong or missing, for whom"]
2. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | awk '/^RULES/{f=1} /^FORMAT/{f=0} f' | tr -s ' \n' '  ' | grep -o -e 'Problem section for the operator who approves the spec' -e 'has not read the design doc' -e 'say what is wrong and for whom' -e 'gloss each term of art on first use' | sort -u | wc -l | tr -d ' '` → `4`. The writer's RULES name the operator as the Problem's reader and give the test: someone who has not read the design doc can say what is wrong and for whom. [NEW: prints `0` today]
3. `awk '/^ROLE: Spec critic\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | awk '/^RUBRIC/{f=1} /^PROCESS/{f=0} f' | tr -s ' \n' '  ' | grep -o -e 'Read it as that operator' -e 'has not read the design doc' -e 'plain gloss on first use' -e 'would need a translator' -e 'that is BLOCKING' | sort -u | wc -l | tr -d ' '` → `5`. The critic rubric reads the Problem as the operator and blocks one they could not follow. [NEW: prints `0` today]
4. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | diff - prompts/02-spec-writer.md && awk '/^ROLE: Spec critic\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | diff - prompts/03-spec-critic.md && cat prompts/02-spec-writer.md prompts/03-spec-critic.md | tr -s ' \n' '  ' | grep -o -e 'Problem section for the operator who approves the spec' -e 'would need a translator' | sort -u | wc -l | tr -d ' '` → no diff output, then `2`. Both prompt files are verbatim re-copies that carry the new text. [NEW: both diffs are clean today, but the count prints `0`]

Items 5 and 6 run the critic itself on the spec the operator could not read. The check below runs the critic prompt from `prompts/03-spec-critic.md` five times on the T-0010 v2 spec as approved (its `## Responses` section removed, so the critic reviews it as round 1). It runs it five more times on the same spec with only the Problem replaced by a plain rewrite of the same content. It then prints how many runs in each set have a BLOCKING finding located at the Problem section. Run it verbatim. It needs an authenticated `claude` CLI, makes 10 parallel calls to the critic's configured model (`fable`), and took a few minutes per run of the check.
```bash
d=$(mktemp -d)
cat > "$d/plain.txt" <<'EOF'
Some tickets had their specs approved before their repo had a spec store, the folder where the factory keeps every approved spec. When the work on such a ticket is finished, the factory's closing step tries to file the ticket's spec into that store, finds nothing to file, and stops the ticket so that a person has to look at it. The factory's design documents describe only one other reason the closing step can stop, and they say nothing about this one. So the operator who finds the stopped ticket has no instructions. It looks like a bug in the factory, and each time the operator must decide again whether to send the spec through the factory again or file it by hand. This affects every repo that started using a spec store after its first tickets. Today that means three tickets on the Nanobot port: SPEC-21, SPEC-26 and SPEC-27.

The operator chose the first of the options offered. The design documents will name both cases (a spec approved before its repo had a spec store, and a repo with no spec store at all) as their own reasons for the stop. The operator closes such a ticket as done without filing its spec, and sends the spec through the factory again only if the store should keep it. The design document records the change in its changelog, and the plan for the first factory run lists the three tickets as that group.
EOF
awk '/^## Responses/{exit} {print}' intake/state/specs/T-0010/v2.md > "$d/jargon.md"
awk -v f="$d/plain.txt" '/^## Responses/{exit} /^## Problem/{print; print ""; while ((getline l < f) > 0) print l; print ""; skip=1; next} /^## /{skip=0} !skip' intake/state/specs/T-0010/v2.md > "$d/plain.md"
for s in jargon plain; do for i in 1 2 3 4 5; do
  claude -p --safe-mode --model fable --tools "" --max-turns 1 --system-prompt "$(cat prompts/03-spec-critic.md)" "Below is a spec for review. This session has no access to the repo, so do not spot-check, and raise no finding about a path, symbol or output you cannot check; judge everything else.

$(cat "$d/$s.md")" </dev/null > "$d/$s-$i.out" 2>&1 &
done; done; wait
for s in jargon plain; do n=0; for i in 1 2 3 4 5; do grep -qE '\[BLOCKING\][^A-Za-z]*(and [0-9][^A-Za-z]*)?Problem' "$d/$s-$i.out" && n=$((n+1)); done; echo "$s $n/5"; done
echo "outputs: $d"
```
5. The check's `jargon` line → `jargon N/5` with N ≥ 3. Given the Problem the operator could not read, the critic now blocks it in most runs, so the writer revises it before it reaches the operator. [NEW: today it printed `jargon 0/5`. The real round-2 critic run approved the same text (`run-0045-critic`, `STATUS: APPROVE`). With the change it printed `jargon 5/5`.]
6. The check's `plain` line → `plain M/5` with M ≤ 1. The same spec with a plain Problem is not blocked on its Problem, so the rule does not block every Problem. [REGRESSION: `plain 0/5` today and `plain 0/5` with the change]
7. `awk '/^## Changelog/{f=1} /^## Appendix/{f=0} f' docs/spec-factory.md | grep '^[0-9][0-9]*\. ' | awk -F. '$1!=NR{gap=1} {last=$0} END{print (gap?"GAP":"CONTIGUOUS"), (last ~ /Problem section/ && last ~ /plain words/ && last ~ /BLOCKING/ ? "LAST-IS-PLAIN-PROBLEM" : "LAST-IS-OTHER")}'` → `CONTIGUOUS LAST-IS-PLAIN-PROBLEM`. The newest Changelog entry records this change, and the numbering has no gap, whatever number the entry gets. [NEW: prints `CONTIGUOUS LAST-IS-OTHER` today]
8. `git diff -U0 main...HEAD -- prompts/ | grep '^-[^-]' | grep -v -x -F -e "-## Problem          what's wrong or missing, for whom" -e '-6. Sufficient: an implementer could start without asking a question.'` → no output, exit 1. The only lines removed from the prompts are the old Problem line and the old rubric 6 line, so every other rule, rubric item, FORMAT line and STATUS line stays as it is. [REGRESSION]
9. `git diff --name-only main...HEAD | grep -v -x -e docs/spec-factory.md -e prompts/02-spec-writer.md -e prompts/03-spec-critic.md` → no output, exit 1. No other path is touched, including `specs/build-harness.md`, `plans/`, the other `prompts/` files and `intake/**`. [REGRESSION]
10. `git diff --check main...HEAD` → no output, exit 0. [REGRESSION]

On the scratch branch with A–E applied, items 1–10 gave: `5`; `4`; `5`; clean diffs then `2`; `jargon 5/5`; `plain 0/5`; `CONTIGUOUS LAST-IS-PLAIN-PROBLEM`; nothing (exit 1); nothing (exit 1); clean (exit 0). On `main` they gave: `0`; `0`; `0`; clean diffs then `0`; `jargon 0/5`; `plain 0/5`; `CONTIGUOUS LAST-IS-OTHER`; nothing (exit 1); nothing (exit 1); clean (exit 0).

## Tests to change

none. This repo holds documents and has no test files.

## Out of scope

- The other sections the writer produces (Evidence, Root cause, design, delta, verification) are not held to the plain-words rule (ticket assumption A1). Their detail is where the Problem's detail moves to.
- The other rubric items, the other FORMAT lines, the routing table, the convergence rules and every other role's prompt stay unchanged.
- `specs/build-harness.md` and `plans/` stay unchanged. That includes the P0 metric table: no term-count metric is added (see Proposed change, "Not proposed").
- Specs already written (T-0001 to T-0010) are not rewritten.
- The prompt copies the running harnesses use are not changed here: green's `~/dev/nanobot-upstream/factory/prompts/spec_writer.md` and `critic.md` (read-only reference), and this repo's intake copies under `intake/harness/factory/prompts/` (protected infra). Re-porting to them is follow-up work; see Out-of-scope observations.
- Updating the `issues/README.md` row for #11 when this lands is the usual post-merge bookkeeping, not part of this change.

## Decisions

- The readability check sits in critic rubric 6, not rubric 1 or a new item 7.
- A Problem the operator would need a translator for is BLOCKING.
- The rubric names categories of terms, not T-0010's words.
- The term-count metric the issue suggested is left out.
- At the gate (operator, 2026-10-02): the reader is a software engineer or product manager, so the Problem stays technical and drops only the pipeline's internal vocabulary.

## Open questions

none. Three wording and placement choices are delegated to the writer, as triage assumption A2 allows. Each is explained in Proposed change C, and the gate can override any of them:
- the check sits in rubric 6;
- it is BLOCKING;
- the rubric names categories of terms, not T-0010's words.

The writer also chose to leave out the term-count metric, explained under "Not proposed". The gate can ask for it.

## Risk

The blast radius is prompt and document text: 35 lines added and 4 removed in three files. Every future writer and critic run reads the changed blocks, so a mistake in wording affects every spec. There are three specific risks:
- **The critic blocks plain Problems and costs extra rounds.** On the fixture, the false-positive rate was 0 of 10 runs (item 6 guards it). The rule blocks only when a reader "would need a translator".
- **Writers pad the Problem with glossaries to satisfy the critic.** The rule asks for plain words first and a gloss only where a term of art stays. The doc's weekly audit sign "Specs growing longer without fewer revision rounds" (`docs/spec-factory.md`, Goodharting signs) is the existing tripwire.
- **Items 5 and 6 depend on a model and are statistical.** They need the `claude` CLI and the `fable` model, and a different critic model could move the counts. The thresholds (≥3 of 5, ≤1 of 5) were chosen against observed rates of 9 of 10 and 0 of 10. The writer-side rule (A, B) is checked only as text (items 1, 2, 4). Its effect on what writers produce is not measured here. The critic check is the backstop.

Protected and guardrail paths this change touches, declared for the gate:
- **generated** (protected): `prompts/02-spec-writer.md` and `prompts/03-spec-critic.md`. They change only by re-copying their edited blocks (Proposed change E; item 4).
- **guardrail** (agent prompts): the §2 and §3 prompt blocks in `docs/spec-factory.md` and the same two `prompts/` files. These need the human approval record on the PR (piece 8).

Paths read but not written:
- `intake/**`: items 5 and 6 read `intake/state/specs/T-0010/v2.md`, and I read run outputs and `intake/instance/config.yaml` while investigating. Nothing there is written, except this output file, which the harness designates.
- `~/dev/nanobot-upstream/**`: read with `grep` only.
- `~/.nanobot/**`: not read.

## Responses

n/a (round 1)

## Out-of-scope observations

- **The fix does not reach running agents on its own.** The intake harness that runs these roles reads its own prompt copies, `intake/harness/factory/prompts/spec_writer.md` and `critic.md`, and line 45 of `spec_writer.md` still has the old Problem line. Green has another copy at `~/dev/nanobot-upstream/factory/prompts/`. Until those are re-ported, writers and critics keep the old behaviour, even after this merges. Both paths are protected or read-only for this role, so a follow-up ticket should carry the re-port.
- **This run's own prompt is an older FORMAT.** It is the single-document layout with no `=== proposal.md` parts, no Decisions section and no Operator steps section. This spec follows that format, and so does the T-0010 spec. The intake copy evidently predates Changelog 37 and 39. That is the same re-port gap.
- **The GitHub issue already exists.** The relayed operator request asks for this ticket to be filed as a p0 GitHub issue. It is already filed: commit `f0f7fa8` records it as #11 (`issues/README.md` line 19, "(p0) | T-0011 | in intake"), with #12 closed as its duplicate. Nothing more is needed from this role.
- **Earlier specs share the pattern.** In trials the critic also flagged T-0009's Problem (SHOULD-FIX). Several earlier Problems (T-0001, T-0002, T-0009) open with build-spec part letters and command names. Those specs are approved and out of scope here.
