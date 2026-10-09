Type: chore

Title: Give the implementer, verifier, code reviewer, planner and triage the reading rules the spec writer and critic already have (#76, prompt part)

Summary:
Issue #73 added three reading rules to the spec writer and critic prompts. A turn is one call to the model, and each turn re-sends everything read so far. The rules are: put independent reads and commands in one turn; once grep has found the lines you need, read only that line range; and send long command output to a file in the run's scratch directory, then grep or tail it. The requester wants the same paragraph in the other five role prompts (implementer, verifier, code reviewer, planner, triage). The paragraph also goes into each prompt's block in the design document (`docs/design.md`) and its verbatim copy in `docs/prompts/`. The spec writer's extra sentence, "Write the spec in as few writes as you can, ideally one", stays out. Nothing else changes: no rubric, routing, round limit or required section. The enforcing hook, #76 part B, stays with #65. The build is accepted on two checks: the prompt files and their copies stay in step and all carry the paragraph, and the operator then replays past build runs with the old and new prompts before the runtime moves.

Evidence:
- From the request: "On the replay, the spec writer's tokens fell about 37% with spec quality held (changelog 58)." The 37% figure is in changelog entry 59, the #74 entry, not 58: "found that #73's spec writer rules cut its tokens by about 37% at the same quality" (`docs/changelog.md`, line 63). Entry 58 (line 62) records the #73 change and the 309M of 866M spec-writer token share.
- From the request: "The implementer is 18% and the verifier 13% of all workflow context tokens (2026-10-05, 866M total)." The 866M total matches changelog 58. I found no source in this repo for the 18% and 13% shares (`grep -rn -E '18%|13%' dev/issues.md docs/changelog.md` returned nothing).
- The paragraph exists in two forms today:
  - Critic, `factory/prompts/critic.md` lines 50-55 and `docs/design.md` lines 485-490, starting "Turn economy: every turn re-sends everything read so far".
  - Spec writer, `factory/prompts/spec_writer.md` lines 59-65 and `docs/design.md` lines 378-384. This form adds "such as a suite run or a scenario's output" and the one-write sentence.
- None of the five target prompts carries the paragraph yet. `grep -c -i 'turn economy'` returns 0 on `factory/prompts/{implementer,verifier,reviewer,planner,triage}.md`.
- The issue index (`dev/issues.md`, line 81) records #76 as "Bounded reads and searches: preamble rule plus a PreToolUse hook ...", not in intake, p1.
- No Nanobot-side harness fix is claimed. This is a prompt-only change.

Capabilities: harness-docs

Assumptions:
- (Inference) "The same reading paragraph as #73's" means the critic's form: the three rules and the sentence about why they matter, without the spec writer's one-write sentence. The spec writer settles the exact wording. The suite-run example in the writer's form fits the implementer and verifier well, so either form serves the request.
- (Inference) Each paragraph goes in the role's own prompt, not once in the shared preamble, as the requester proposes. The issue index describes #76 as a "preamble rule". A preamble line would also reach the spec writer and critic, which already carry the rules. The request names the five role prompts, and the operator approved it in that form, so I take the per-role placement as intended. The spec writer may still raise the preamble as an alternative.
- (Inference) "The copies stay in step" means each changed `docs/prompts/` file is re-copied from its design-doc block. It does not mean that `factory/prompts/` and `docs/prompts/` are byte-identical. They already differ where the harness fills placeholders: for example, `{gate commands}` in `docs/prompts/05-implementer.md` against the filled-in text in `factory/prompts/implementer.md`.
- (Inference) The documents keep their usual conventions: a changelog entry in `docs/changelog.md`, and `dev/build-harness.spec.md` updated to match. The current harness-docs scenario "Nothing else in the two prompts changes" covers only the spec writer and critic. The new scenarios cover the five other roles.
- (Inference) The operator's replay after the build is a step for the operator, not an acceptance command the factory runs. The procedure for that replay is a separate open issue, #80.
- Suggested priority (a suggestion, not a decision): p1, the priority the issue index gives #76.

Reason: The intent is clear and needs no product decision. I found no duplicate. T-0034 (#73) and T-0035 (#74) are closed and covered only the spec writer and critic. No open or recently closed ticket adds reading rules to the other five roles. T-0039 is this ticket.

Out-of-scope observations:
- The request cites changelog 58 for the 37% replay result. The figure is in changelog 59.

STATUS: ACCEPT
CONFIDENCE: high. The scope is narrow and stated exactly, the gap is confirmed by grep on all five prompts, and the operator has approved it.
ESCALATIONS: none
