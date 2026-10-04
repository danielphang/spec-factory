## Critic review of T-0019 (v2, round 2)

Reviewed per convergence rules: prior findings and changed text only.

Spot-checks on `main` at `17efb50` (`git rev-parse --short main` prints `17efb50`; `git log` shows no commit after it):
- `factory/workflows/intake.js` line 150 accepts both `READY-FOR-CRITIC` and `NEEDS-SPLIT` from the spec writer and goes on to `spec add`, as the Responses and Evidence claim.
- Operator step 3's paths: `uv python dir` prints `/Users/dphang/.local/share/uv/python`, `uv cache dir` prints `/Users/dphang/.cache/uv`; `.venv/bin/python` resolves to `.../uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12` (`Python 3.12.13`); `/opt/homebrew/opt/python@3.14/bin/python3.14` exists; `pyproject.toml` line 4 is `requires-python = ">=3.11"`, so a 3.14 fallback would be accepted by uv. `.factory/instance.yaml` has no `run_env` key today. The Evidence paragraph and step 3 hold.
- Acceptance "A sub-ticket with no Depends on line is refused", run with the GIVEN parent fixture on a scratch store: prints the success JSON with `T-0001.2` at `"depends_on": []`, `exit=0`, then `T-0001.1.yaml T-0001.2.yaml T-0001.yaml`. Matches the "today" line.
- The 157 vs 171 gap the writer could not explain: `pytest --collect-only` on `17efb50` in the dev checkout collects `171 tests`; the runtime checkout `~/dev/spec-factory-harness` is at `61ccf8d` and collects `157 tests`. So v1's figure was measured in the runtime checkout, not at `17efb50` as v1 recorded. The v2 figure is the correct one for the cited commit.
- Part D now says "eight lines"; the block has eight. The two preamble lines the scenario greps for (`- Run every test, script or prototype with HOME set to a fresh`, `  run anything that could write a protected path outside the`) are unchanged by the "every test or check command" edit.

Prior findings (round 1):
- [BLOCKING] 6 Operator steps gloss of "runtime": RESOLVED. First paragraph now reads "once the runtime (the pinned checkout of the harness that runs tickets) has moved", and `--accept-harness` is explained there.
- [SHOULD-FIX] 4 No `run_env` for this repo: RESOLVED. Operator step 3 and a Decision added; the Python-version reason is verified above.
- [SHOULD-FIX] 3 Two faults in one PR: RESOLVED. "Size and seams (NEEDS-SPLIT)" names S1/S2, each lettered part carries its seam, the shared changelog entry has a first-writer rule (E1), and the seams are declared not parallel-safe because both edit `docs/design.md` and `docs/changelog.md`.
- [NIT] 6 "parked" unglossed: RESOLVED.
- [NIT] 2 Suite run twice: RESOLVED. Bare scenario dropped; wrapped one annotated as the handed gate command.
- [NIT] 4 "every command": RESOLVED. Part A and B3 now say "every test or check command".

Findings:

[NIT] 1 verification.md, note after the Acceptance list
Problem: the note leaves the 157-vs-171 discrepancy unexplained, and Evidence still says v1 ran on `17efb50`, which the counts show it did not.
Evidence: `pytest --collect-only` at `17efb50` collects 171; the runtime checkout at `61ccf8d` collects 157 (commands above).
Suggested fix: replace "I did not find out why the counts differ" with "v1's 157 was measured in the runtime checkout at `61ccf8d`; 171 is the count at `17efb50`", or let the implementer carry this note; it does not change any criterion.

Out-of-scope observations:
- None new. The writer's three (stale `agents/factory-planner.md`, the `harness-bug:` label on a refused plan, `UV_CONFIG_FILE`) stand and are correctly out of scope.

STATUS: APPROVE
CONFIDENCE: high; every round-1 finding is resolved in the text as claimed, the new Evidence and Operator step 3 check out against this machine, and the one open discrepancy in the verification note is explained by the two checkouts and changes no criterion.
ESCALATIONS: none
