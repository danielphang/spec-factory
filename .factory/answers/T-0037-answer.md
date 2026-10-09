# T-0037 (#78): answer to triage's question

Option 2: drop #75's decision-log filter. The spec writer, critic and planner receive the whole decision log, `decisions.md`, in full, as before #75. The decision index and its `grep` instruction are removed. #75's capability half stays as built: the capabilities triage names in full, plus the capability index.

Why: no decision line in either store names a capability (0 of 254 on Nanobot, 0 of 108 here), so the filter kept nothing in full. A cross-cutting standing decision (T-0003, where lionbot code lives) reached the writer and critic only as an index line, and the replay's writer broke it. The whole log is the simplest correct behaviour. Estimated writer input after this change: Nanobot about 518 → 235 kB, spec-factory about 187 → 135 kB.

Standing: yes. Decisions reach these roles in full until a scoping scheme exists that cannot drop a cross-cutting rule. #54's product/implementation tagging is where that scheme belongs.

Operator's choice in the Green session, 2026-10-09.
