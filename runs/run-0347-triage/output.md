Type: bug

Title: Send the whole decision log to the spec writer, critic and planner again, removing #75's decision filter (#75 follow-up)

Summary:
Issue #75 cut what the spec writer, critic and planner receive each turn, and in doing so it can hide a standing decision that every ticket must follow. The decision log, `decisions.md`, holds one line per standing decision with its date and ticket id. Since #75, a line reaches these three roles in full only if it was logged against their ticket or names a capability they get in full. Every other line is reduced to a "decision index" entry. (A capability is one current-truth spec, `openspec/specs/<name>/spec.md`.) The operator has now chosen to drop that decision filter. The three roles receive `decisions.md` whole, as before #75. The decision index and its `grep` instruction are removed. #75's capability half stays as built: triage names capabilities, the writer and critic get those in full, and a capability index covers the rest. The requester also wants the size of the decision part measured on both stores, before and after, and recorded. #75 and this fix then reach the runtime together in one move.

Evidence:
- Requester: in the operator's replay of #75 on Nanobot ticket T-0032, the new writer put its code in a new module, `nanobot/cron/session_sweep.py`. Standing decision T-0003 rules that out. The original writer, given the whole log, followed T-0003, and the original critic confirmed it. The replay critic missed the conflict, because it did not get T-0003 in full either.
- Operator's answer (Answer 1, 2026-10-09): "Option 2: drop #75's decision-log filter. The spec writer, critic and planner receive the whole decision log, `decisions.md`, in full, as before #75. The decision index and its `grep` instruction are removed. #75's capability half stays as built." The reason given: no decision line in either store names a capability, so the filter kept nothing in full. The operator's estimate of writer input after the change is about 518 → 235 kB on Nanobot and about 187 → 135 kB on spec-factory.
- The answer is already a standing decision. It is line 109 of `~/dev/spec-factory/.factory/store/decisions.md`: "2026-10-09 T-0037 Decision log in role inputs (#78, T-0037): the spec writer, critic and planner get decisions.md whole; #75's decision filter is removed; any future scoping must not be able to drop a cross-cutting standing decision (see #54)."
- The filter is `add_decisions` in `factory/compose.py` (lines 226–261 on `main` at `51e2af7`). It already has the whole-log branch: when the selection is `None` (no `Capabilities:` line), it adds `decisions.md` whole (lines 232–234). The filtering and the "Decision index" section follow (lines 235–261). It is called for the spec writer (line 272), the critic (from the selection on line 290) and the planner (line 315).
- From the earlier triage run, measured with a whole-word match against every current-truth capability and checked with `grep -c`: 0 of 254 decision lines on Nanobot and 0 of 108 on spec-factory name a capability. Today `wc -c` gives 76,342 bytes for the Nanobot log and 35,991 bytes for spec-factory's (109 lines, now including the T-0037 line).
- The docs that state #75's decision rule today:
  - the requirement "The spec writer, critic and planner receive in full only the decisions of their ticket and its capabilities, and a decision index for the rest", with its scenario, in `.factory/store/openspec/specs/role-inputs/spec.md` (lines 53–59);
  - the "decision index" sentence in `docs/design.md` line 94;
  - the spec writer, critic and planner rows of `README.md` (lines 85–87).
- Duplicate search: T-0037 is this ticket (issue #78, indexed in `dev/issues.md` line 83). T-0036 is #75 itself, which is merged and held from the runtime. T-0038 is about sub-tickets after a re-plan. No other open or recent ticket covers this.

Assumptions:
- (Inference) The role-inputs requirement on lines 53–59 is removed or replaced, and its scenario no longer expects a decision index. The writer, critic and planner then hold every decision line whether or not the ticket has a `Capabilities:` line. The requirement on lines 61–66 ("A ticket whose triage output names no capabilities receives today's inputs") stays true. Its words "as before this change" for the decision log may need to change, because the log is then always whole.
- (Inference) The triage-input requirement (lines 74–79, "no capability body or decision") is unchanged. Triage still receives no decision lines.
- (Inference) `docs/design.md` line 94, the README rows on lines 85–87, and the README terms row on line 128 change in the same ticket, with a `docs/changelog.md` entry. Line 128 already says every later spec writer, critic and planner reads the decision log, so it may need no edit. Any `docs/prompts/` file whose block changes is re-copied from it, as the briefing requires.
- (Inference) "Record it" in the request's item D means a measurement in the spec's Evidence or the PR description: the decision part's size per role input, before and after, on both stores. It does not mean a new file or a new harness command.
- (Inference) The capability-index note and anything else #75 added for capabilities stay byte-for-byte as built. Only the decision half is removed.
- Suggested priority: p1, because #75 is held from the runtime until this fix merges. This is a suggestion; priority is the operator's call.

Reason: The operator's answer settles the open choice. The intent is clear: remove the decision filter and keep the capability filter. No further product decision is needed.

STATUS: ACCEPT
CONFIDENCE: high. The answer chooses one option explicitly and is already logged as a standing decision (`decisions.md` line 109). I re-read the filter code, the role-inputs spec and the docs lines on this checkout.
ESCALATIONS: none
