# T-0015 (#20): spec gate pre-approved by the operator

Operator, 2026-10-03, in the Green session: "a 2" — pre-approves the spec gate. When the critic approves, the Green session runs `approve-spec T-0015` with a gate edit that adds the acceptance test as operator step 0: before the runtime moves, real implementer diffs are rewritten under `docs/coding.md` (with a reviewer check), and the operator's approval of the side-by-side result is the acceptance. A critic ESCALATE or a round-cutoff park still comes back to the operator.
