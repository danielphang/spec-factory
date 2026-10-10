Round 1 review of the `factory drive` spec (v1), checkout `bb410c0`.

What I checked myself (no suite run, no build):
- Cited paths and lines: `factory/cli.py:390` is `wt = d / "wt"` inside `_start_build_run`; `fence` is at `factory/cli.py:1898–1913` and does what Evidence says (location rule, then marker, then in-flight list); `docs/design.md:44` is piece 2 with limit (1); `docs/design.md:64` is the fence paragraph; `dev/build-harness.spec.md:118` is row R6 with "Never `bypassPermissions` (nor `dontAsk`)"; `grep -c 'clerk('` prints 12 and 31; `tests/factory/test_sibling_tests.py`, `test_spec_drift.py`, `test_merge_protected_paths.py` exist; `factory/workflows/intake.js` has `// --- start` (line 138), `runRole`/`runOnce` (77/87) and "nothing to dispatch from this state" (199); `build.js` has `// --- start` (217), `buildOne` (145) and `parallel(` (181, 274); `run last-message`, `run cleanup`, `ticket set`, `ticket transition`, `store.write_yaml`, `config_cmd` (returns `models` and `max_rounds`) all exist; a ticket record has top-level `branch` and `head` (`store.py:209`), so `ticket set ... branch=... head=...` is a known key; `dev/issues.md` has row 65; README has every heading the documents scenario anchors on and the "none has an effort level" line; `docs/changelog.md` ends at entry 66 before "Declined:".
- Acceptance command run as given (documents scenario, through the HOME wrapper): prints `starting=no depends=no built=no effort-gap=yes design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean`, as verification.md says. `FACTORY_STATE=<throwaway> bin/factory drive T-0001 --phase intake` prints argparse's usage line with no `drive`, as Evidence says.
- Tests pinning old behaviour: `run finish` gains an optional flag only, no test reads `instance.template.yaml` byte for byte (`test_instance.py:103, 351` parse it with yaml, so a comment line changes nothing), no test reads README, the changelog or the build spec as text. "Tests to change: none" holds for what I could check.
- `run start` leaves the ticket's status unchanged and only appends to `in_flight` (`cli.py:239`), so the stop scenario's `ready-for-triage in_flight: []` after a `KILLED` finish is consistent with today's records.
- `ticket new --file` takes the title from the first `#` line (`cli.py:75–76`), so `"Fixture"` in the step-line scenario is right.
- Not checked, as they need the suite or the built change: that `build.js` starts 4 calls on the two-sub-ticket `checks-in-flight` fixture (writer says observed), and that the parity records match byte for byte once `drive` exists.

Findings

[BLOCKING] 6 proposal.md, Problem, first paragraph
Problem: The first paragraph is background (what the roles, the harness and the two scripts are) and never says what is wrong or who has it; the problem arrives in paragraph two ("The operator who runs the factory pays for that relay in tokens, in time and in failures").
Evidence: Read as the gate operator against `docs/writing.md` rule 1 ("a reader who stops after the first paragraph can say what the problem is and who has it"). The rubric names this case as blocking.
Suggested fix: Open with one sentence of the kind "The operator who runs the spec factory pays a relay tax on every step: the scripts that choose the next role cannot touch the store, so each store call costs an extra agent (the clerk), and that agent is the largest single cost and a source of failures", then keep the glossary sentences.

[BLOCKING] 6 proposal.md, Decisions first bullet and Operator steps step 1
Problem: First paragraphs of two human-facing sections use system terms that none of Problem, Evidence or Decisions has glossed: "runner session" (Decisions bullet 1), and in Operator step 1 "the runtime", "accept it (`--accept-harness`)", "this instance" and "spec gate".
Evidence: Grepped the spec text; "spec gate" first appears unglossed in Decisions bullet 14 and Operator step 1, "runtime"/"--accept-harness"/"instance" only in Operator step 1, "runner session" in Decisions bullet 1 and 3. `--accept-harness` is the very example `docs/writing.md` rule 2 uses.
Suggested fix: One short gloss each at first use, for example "a runner session (the operator's Claude Code session that starts pipeline runs)", "the spec gate (the point where the operator approves a spec before code is written)", and in step 1 "the runtime (the separate checkout the factory runs from) ... accept the new harness commit there with `--accept-harness`, which each target repository requires before it runs a new harness revision".

[SHOULD-FIX] 4 proposal.md Decisions (status file) / design.md A.7
Problem: The status file `drive/<parent id>.yaml` lives in the store, which the operator commits, but the spec does not say whether `drive/` is committed or ignored; it holds a `pid` and an `updated` time that churn on every step, so left unsaid it becomes a decision the implementer makes.
Evidence: `STORE_GITIGNORE` (`factory/store.py:49–52`) lists `worktrees/`, `runs/*/wt/`, `runs/*/tripwire.yaml`, `runs/*/scratch/` and nothing else; `ensure_gitignore` runs at every `run start`, and the T-0024 decisions say it writes a fixed block.
Suggested fix: State one choice in Decisions (I would add `drive/` to the store's `.gitignore` block, as a per-process scratch record like `tripwire.yaml`), and if that block changes, check whether a live-store-guard test pins its exact text and list it under Tests to change if so.

[NIT] 1 proposal.md Evidence bullet 3 and Root cause
Problem: The `clerk` function is at `intake.js:50` and `build.js:41`, not 48 and 42, so the "lines 48–64" and "42–58" ranges are off by two and one.
Evidence: `grep -n 'async function clerk' factory/workflows/*.js`.
Suggested fix: Correct the four line numbers.

[NIT] 4 proposal.md Decisions (tool fences)
Problem: The `--tools` list silently drops every tool role agents have today beyond the seven named (sub-agent spawning, task lists, notebook edits); the spec says why web tools are kept but not that the rest go.
Evidence: No role prompt in `factory/prompts/` mentions sub-agents or those tools (grep), so nothing breaks; it is still an unstated choice.
Suggested fix: Add half a sentence: "Every other tool the session offers today is withheld; no role prompt asks for one."

Everything else holds: the parity scenarios compare records order-free and byte for byte, which a stub or a routing shortcut would fail; the NEW items fail today for the stated reason; protected path `factory/**` is declared; the change conflicts with no open approved change (none listed) and respects the T-0024 fence decisions (drive is fenced, marks its own calls, roles never inherit the marker); the split into A/B/C has natural seams and each part is needed. The technical content is ready; round 2 should need only the two text fixes and the `drive/` decision.

STATUS: REVISE
CONFIDENCE: high, every cited path, line and anchor I spot-checked exists as stated except the two clerk line numbers, and the one acceptance command I ran printed exactly the stated baseline; the blocking items are writing-standard findings the rubric defines as blocking, not design defects.
ESCALATIONS: none
