# T-0033 (#57): answer to triage's question

Option 1: the approved Risk list is the authorization. At merge, the gate refuses any changed protected path that the pinned spec's Risk list does not declare, names each one, and parks the ticket for a human ruling. A declared path merges with no further approval. The design doc's per-PR approval text (lines 21, 23, 48, 154) and the reviewer's check 6 are reworded to match, with a changelog entry and re-copied prompt files.

Standing: yes. It is harness behaviour, so it applies to every instance, including the Nanobot fork.

Source: the operator approved this rule on 2026-10-05, when approving the follow-ups to the #56 review ("Yes, do it"). The rule approved was: "the approved spec's Risk list *is* the authorization. At merge, refuse any changed protected path the pinned spec didn't declare." Measured cost of the alternative: 19 of the last 20 merges here touched a protected path. Because this changes a documented human gate, the spec goes to the operator at the spec gate and is not covered by the pre-approval policy. Option 3 (a per-head approval for paths that change the factory's own rules) remains open to the operator there.

Answered by the Green session on the operator's 2026-10-05 approval.
