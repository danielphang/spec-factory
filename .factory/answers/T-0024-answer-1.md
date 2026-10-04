Operator, 2026-10-04: take the recommendations, and run the result through intake with a design-review critic.

1. Keep the spec store that run-0196 created on this instance. Tickets here close by archive into current truth; decisions.md stays and keeps reaching the spec writer, critic and planner. README's stale "never entered the spec store" line is corrected by the ticket that next touches README (or #21).
2. While a role run is in flight on the live store, the operator or a runner session writes it by prefixing that one command with `FACTORY_DISPATCH=1`. README documents this; the refusal message does not name it.

For the critic (Fable): beyond the rubric, review the design itself. Does the in-flight-only fence leave a gap, for example a write after a run dies or between runs? Is "every command except a read-only list" the right default? Is the marker's copyability acceptable as stated? Does the design interact with #46 (store on its own branch) and #38 (tripwire)? Raise design findings with severity, not only rubric findings.
