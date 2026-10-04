# Human ruling: how the code reviewer works on this piece (operator, 2026-10-04)

Two reviewer runs on this head (run-0288, run-0290) started the test suite in the background, ended the turn to wait for it, and returned no review. That is spec-factory #41 (T-0032), not yet live.

For this review:
- Judge the diff, the PR description and the spec. Do not run the test suite or the gate commands: the verifier ran both on this head and passed (run-0287, VERIFIED, 310 passed). A narrow command that confirms one specific finding is fine, run in the foreground.
- Never start a command in the background, and never end your turn while one is running. Your final message is your review; finish it in this turn.

Operator's choice in the Green session ("Ruling for #49 and #41"). Placed by hand because `resolve --ruling` does not accept a budget-kill park; no checker result was changed.
