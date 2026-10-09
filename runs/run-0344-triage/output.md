Type: bug

Title: Standing decisions that name no capability must reach the spec writer, critic and planner in full (#75 follow-up)

Summary:
Issue #75 cut what the spec writer, critic and planner receive each turn. A line in the decision log (`decisions.md`, one line per standing decision with its date and ticket id) now reaches them in full only if it was logged against their ticket or names a capability they get in full. A capability is one current-truth spec, `openspec/specs/<name>/spec.md`. Every other line is reduced to one entry per ticket in a "decision index". A cross-cutting decision names no capability, so the writer and critic can miss a rule that every ticket must follow. That happened in the operator's replay of #75. The requester wants decision lines that name no capability sent in full again (their A). Lines that name a capability keep #75's rule (B), and the ticket's own lines stay in full (C). They also want the size of the decision part measured on both stores, before and after, and recorded (D). #75 and this fix then ship together in one runtime move.

Evidence:
- Requester: in the replay of #75 on Nanobot ticket T-0032, the new writer put its code in a new module, `nanobot/cron/session_sweep.py`. Standing decision T-0003 rules that out. The original writer, given the whole log, followed T-0003, and the original critic confirmed it. The replay critic missed the conflict.
- `.factory/answers/T-0036-acceptance-2026-10-09.md` records the replay. Writer input fell from 518 to 162 kB on Nanobot and from 187 to 100 kB on spec-factory, and quality was the same on both tickets. It records one miss: T-0003 "names no capability and was filtered into the index". It records the operator's choice: "Fix the filter first, then ship". The follow-up "sends every decision line that names no capability in full".
- I confirmed T-0003 names no capability. It is line 5 of `~/dev/nanobot-upstream/.factory/store/decisions.md`: "Where lionbot code lives: lionbot behaviours attach through upstream's extension points first …; `nanobot/agent/lionbot.py` holds only plain helpers …". None of the 23 Nanobot capability names appears in it.
- The filter is `add_decisions` in `factory/compose.py` (lines 226–261). A line goes in full when `f[1] == tid` or when its text matches one of the selected capability names as a whole word. Otherwise it goes into the index (lines 239–244).
- New finding, measured with the same whole-word match against every current-truth capability (not only the selected ones), and checked again with a plain `grep -c <name>` for each capability:

  | Store | Decision lines | Lines that name any capability | Size of the log |
  |---|---|---|---|
  | Nanobot (`~/dev/nanobot-upstream/.factory/store`) | 254 | 0 | 76,342 bytes |
  | spec-factory (`~/dev/spec-factory/.factory/store`) | 108 | 0 | 35,747 bytes |

  No line in either log names a capability. Decisions cite tickets and code paths, not spec names. So, with today's logs, A as written sends every line in full to every writer, critic and planner. The decision index is then always empty, and B's capability rule picks out nothing. On the decision part, this is the same as removing #75's filter. It restores about 76 kB per input on Nanobot and about 36 kB on spec-factory. By a rough sum, Nanobot writer input rises from 162 kB to about 238 kB, still about 54% below the 518 kB before #75. That figure is my estimate, not a measurement; D measures the real one.
- Current truth already states #75's rule. The requirement "The spec writer, critic and planner receive in full only the decisions of their ticket and its capabilities, and a decision index for the rest" is in `.factory/store/openspec/specs/role-inputs/spec.md` (lines 53–59). Its scenario expects `other=0` for `OTHER-LINE logs rotate weekly.`, a line that names no capability. Under A, that line goes in full.

Assumptions:
- (Inference) The fix changes the existing role-inputs requirement and its scenario rather than adding a new one beside them. The `OTHER-LINE` expectation flips from `other=0` to `other=1`, and the requirement's title and SHALL text change with it.
- (Inference) The design doc paragraph (`docs/design.md` line 94) and the README's spec writer, critic and planner rows (`README.md` lines 85–87) describe #75's rule. They change in the same ticket, with a changelog entry, as the briefing requires.
- (Inference) "Record it" in D means a measurement in the spec's Evidence or the PR description, not a new file or a new harness command.
- (Inference) A line with no date and ticket id keeps its current treatment: it is always sent in full.
- Suggested priority: p1, because #75 is held from the runtime until this fix merges. This is a suggestion; priority is the operator's call.

Question for human:
No line in either store's decision log names a capability (0 of 254 on Nanobot, 0 of 108 on spec-factory). So the rule you chose ("send every decision line that names no capability in full") sends the whole log to the spec writer, critic and planner on every ticket today. That is about 76 kB per input on Nanobot and 36 kB on spec-factory, as before #75. Capability specs stay filtered as #75 built them. Which do you want?
1. Build A–D as written. Today's behaviour is the whole log in full. The capability rule (B) only starts to filter if later decisions name capabilities. This matches your recorded choice and fixes the T-0003 miss. (Suggested.)
2. Drop the decision filter and send the whole log, as before #75. The result is the same as option 1 today, with less code and no decision index. Only the capability-spec half of #75 ships.
3. Keep the filter and mark cross-cutting decisions explicitly. For example, a "standing for every ticket" flag on `factory decision add`, set on T-0003 and the others like it. Only marked lines, the ticket's own lines and lines naming its capabilities go in full. This keeps more of #75's savings, but it needs a new flag and someone to go back and mark the existing logs, so #75 ships later.
Is the answer a standing decision that later tickets must follow, for example on how decisions are scoped in any role input?

STATUS: NEEDS-HUMAN
CONFIDENCE: high. The duplicate search found only this ticket (T-0037 is #78). I measured the zero-match finding on both stores and checked it a second way.
ESCALATIONS: none
