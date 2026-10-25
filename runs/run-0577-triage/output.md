Type: feature

Title: `factory truth check` replays every current-truth scenario, and the gate runs it

Summary:
"Current truth" is the set of capability specs in the store (`.factory/store/openspec/specs/`). Each spec holds scenarios: a shell command (the WHEN) and the output it must print (the THEN). When a ticket closes, its archive step folds the ticket's approved delta (its ADDED, MODIFIED and REMOVED requirements) into current truth. Today nothing re-runs those scenarios. The merge gate runs only `git diff --check` and the harness suite, and the verifier runs only its own spec's acceptance, so a change that breaks another capability's scenario can still merge. The operator wants a `factory truth check` command that runs every scenario's WHEN under `bash` in the checkout under test and compares the output with the THEN. On a ticket's branch it should apply that ticket's approved delta first. It should list scenarios it cannot run mechanically as skipped, with a reason, and report its wall time. This instance then adds the command to its `gate_commands`.

Evidence:
- Request, issue #120 (https://github.com/danielphang/spec-factory/issues/120, operator, 2026-10-19). Requirements A–E are quoted from the operator:
  - A: "`factory truth check` runs every scenario's WHEN in the checkout under test, always under `bash` … prints pass or fail for each scenario, a total, and exits non-zero on any failure. `--capability <name>` limits the run."
  - B: "When the check runs on that ticket's branch, it uses current truth with the ticket's approved delta applied … The spec says how. Archive's own fold is the obvious source."
  - C: scenarios with a prose THEN or a live-service dependency "are listed as skipped with a reason and counted, never silently passed."
  - D: "This instance adds the check to `gate_commands`. Adopting it on another target is that target's owner's decision."
  - E: "The check reports its wall time. The spec states the figure on this repo, against the suite's current 119 s."
- Cited incidents: a change made outside the factory broke 3 current-truth scenarios on the Nanobot target, and nobody saw it until a later ticket (#87). T-0049's spec writer ran all 80 `harness-docs` scenarios by hand. #113: one scenario failed under macOS `/bin/sh`.
- Checked on this checkout today:
  - The gate today is `git diff --check main...HEAD` plus `uv run --frozen pytest -q -p no:cacheprovider tests/factory` (`.factory/instance.yaml`, `gate_commands`). That matches the request.
  - Current truth now holds 306 scenarios across 15 capabilities. The request says 284; the figure is from 2026-10-19, and T-0055 and T-0058 were archived on 2026-10-23. Command: `grep -c '^#### Scenario'` per `spec.md`.
  - Every scenario has a backticked WHEN. 213 of the 306 THENs read `it prints exactly …`. Most of the other 93 read `it prints \`…\``, possibly with `, then \`…\``. About 15 are prose, such as "reports a number of passed tests" or "two numbers: the first below 900". Requirement C covers those.
  - The fold exists as code: `apply_delta` at `factory/specstore.py:385`, used by `archive` at `factory/specstore.py:398`.
  - The dependency is met. #113 was fixed by T-0058, merged `1321c17` and live since 2026-10-23 at runtime `c42d167` (`dev/issues.md:116`).

Capabilities: gate-commands, spec-amendment, harness-suite, harness-docs

Assumptions (my inferences, not stated by the requester):
- No duplicate. The only matching ticket is T-0059 itself, the ticket for this request. #87 (`factory fast-track`, not in intake) also wants "touched capabilities' current-truth scenarios" run. It would likely reuse this command, but it is a separate request, and this ticket should not take it on.
- The verifier has no written rule for checking "an exact print". Its prompt (`factory/prompts/verifier.md`) says only to run each command "exactly as written" and record the output, and `docs/design.md` and `factory/*.py` have no comparison rule either. So the spec has to define the rule: for example, whether trailing newlines and whitespace count, and how a THEN with `, then \`…\`` maps to lines. The operator then approves that rule at the spec gate, rather than the spec treating an existing rule as the source.
- Wall time may be well above the suite's 119 s. 17 WHENs call `pytest`, and about 15 of those run the whole `tests/factory` suite, so a serial run could cost several suite runs. The operator asked for the figure to be measured and stated rather than for a budget, so I read them as deciding at the spec gate. Two things are worth showing next to the figure: the existing requirement "The gate's suite command finishes in under three minutes" (gate-commands), which covers only the suite command; and the fact that the gate runs for every sub-ticket's checkers.
- Many scenarios depend on a GIVEN block from another scenario, sometimes in another capability ("Needs the GIVEN block of … run once"). Many also depend on per-capability preconditions ("after `uv sync --frozen`, with `node` on `PATH`"). Running scenarios mechanically has to honour both, or list a scenario as skipped under C.
- Current truth lives in the store, a checkout of the `factory-store` branch, not on `main`. A checker's detached checkout therefore has no copy of it. The command must find the store through the instance config rather than the checkout under test.
- D edits `.factory/instance.yaml`, and the command lives in `factory/`. Both are protected paths (infra, harness), which the spec's Risk section must declare.
- Suggested priority (a suggestion; priority is the operator's call): p1, as `dev/issues.md:122` already records.

Question for human / Missing info / Reason: none. The intent and requirements A–E are specific, and the open design points (the comparison rule, how B applies the delta, and the skip criteria) are ones the operator has handed to the spec, which they will review at the gate.

Out-of-scope observations:
- The first full run may fail scenarios that later tickets broke without modifying them, beyond #113's case. Whether such a failure blocks the first gate run, or must be fixed first, is a question for the spec to raise. It is not a triage call.

STATUS: ACCEPT
CONFIDENCE: medium. The intent is clear and the codebase facts are verified, but there is no codified "exact print" rule to reuse, and the gate cost could be large; both need the spec writer's attention.
ESCALATIONS: none
