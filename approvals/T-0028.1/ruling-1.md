# Human ruling: the undeclared protected path in T-0028.1 (operator, 2026-10-05)

The reviewer (run-0298) escalated one point and found no defect: `factory/store.py` changes by 3 lines (`record_result` gains an optional `extra` parameter). The approved spec's design part A.5 asks for exactly this change, but its Risk list and the sub-ticket's protected-path list do not name the file.

Ruling: accepted as part of the approved design (part A.5). The undeclared listing is a gap in the spec's Risk list, not a reason to block. Judge the rest of the change on its merits; this escalation is settled.

For this review: judge the diff, the PR description and the spec. Do not run the test suite or the gate commands; the verifier ran them on this head and passed (run-0299, VERIFIED). Run any command in the foreground, never end your turn while one is running, and finish your review in this turn.

Operator's answer in the Green session: "(2) sure", to the recommendation to accept the change under the approved design. Placed by hand because `resolve --ruling` routes a sub-ticket's reviewer escalation to the critic.
