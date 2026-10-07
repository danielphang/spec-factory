# Human ruling for the code reviewer on this piece (operator, 2026-10-04, standing for #49 and #41)

For the code reviewer: judge the diff, the PR description and the spec. Do not run the test suite or the gate commands; the verifier runs both on the same commit. A narrow command that confirms one finding is fine, in the foreground. Never end your turn while a command you started is running; your final message is your review, finished in this turn.

The implementer and the verifier work as usual; this ruling changes nothing for them. Placed before the build by the Green session, because the bug this ticket fixes would otherwise stall its own review.
