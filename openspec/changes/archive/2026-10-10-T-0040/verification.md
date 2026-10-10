## Acceptance

- The driver takes the intake fixtures through the same routes as the intake script → NEW. Today `bin/factory drive` exits 2 with argparse's usage line (`{ticket,run,spec,…,log}`, no `drive`). The four lines print `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=2/2 drive=0/0 differ` and `ready-for-triage script=1/1 drive=0/0 differ` (run in this spec's investigation).
- The driver takes the build fixtures through the same routes as the build script → NEW. Today it prints `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=6/6 drive=0/0 differ`, `ready-for-planner script=4/4 drive=0/0 differ` and `ready-for-planner script=1/1 drive=0/0 differ` (observed).
- Each role runs as one claude process with its prompt, model and tool limits → NEW. Today the drive side starts no process, its log is empty, and the check prints two empty lines (observed). The check itself was validated on synthetic argv built to this design against real run directories: it printed `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`. It prints `bad: prompt, --model=None, …` for the scripts' own calls.
- Each role run records its process's reply → NEW. Today the drive store has no runs, so the check prints `none` (observed).
- The checkers run at once, and sub-tickets up to the parallel limit → NEW. Today it prints `parallel=1: calls=0 max=0 checks-in-flight checks-in-flight`, then the same for `default` (observed). Under `build.js` the same fixture starts 4 calls and parks both sub-tickets `SPEC-DEFECT from verifier` (observed), so the fixture reaches the checkers.
- Every intake step line names its ticket and title, and the status file shows the end → NEW. Today it prints `steps=no untagged=0 last=0 status= ignored=0`: stdout is empty, there is no status file, and the store's `.gitignore` has no `drive/` line (observed, round 2).
- Build step lines name the sub-ticket they concern → NEW. Today stdout is empty, and it prints `untagged=0 sub=no last=0` (observed).
- A stopped driver ends its role process, records the run as killed and resumes from the stored state → NEW. Today it prints `stop: exit=2 running=0 run= ready-for-triage in_flight: [] child=gone last=0`, then `resumed: exit=2 ready-for-triage calls=` (observed).
- The driver marks its own store calls, never its roles', and passes a configured effort → NEW. Today it prints `unmarked=2 marked=2 ready-for-triage calls=0 effort=0 dispatch=0 inside=2` (observed). `marked=2` is argparse's refusal.
- The Workflow scripts still take both fixtures to the end of their routes → REGRESSION. It prints `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate` today (observed), and must after each part.
- The documents describe the driver → NEW. Today it prints `starting=no depends=no built=no effort-gap=yes drive-row=no design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean` (observed).

## Responses

- [BLOCKING] Problem, first paragraph → FIXED. The Problem now opens with who has the problem and what it is: the operator pays a relay cost on every step, because the scripts cannot run a command and start a clerk agent for each store call, with the measured cost and the 2026-10-09 failure. The glossary of roles, harness, store, checkers, sub-tickets and the Workflow tool moved to the second paragraph.
- [BLOCKING] Unglossed terms in Decisions and Operator steps → FIXED. "Runner session", "instance" and the dispatcher marker are glossed at first use in the Evidence fence bullet, which precedes Decisions. "Spec gate" is glossed in the Problem's last paragraph. Operator step 1 glosses the runtime and says what `--accept-harness` does and why it is needed. I also glossed "park", "checkers", "sub-ticket", `EMPTY-OUTPUT`, `KILLED` and the whole-spec step, which had the same gap.
- [SHOULD-FIX] Status file committed or ignored → FIXED. New Decision: `drive/` joins the store's `.gitignore` block under its own comment line, with both alternatives rejected. The block's exact text is pinned by three tests in `tests/factory/test_run_scratch.py`, now listed under Tests to change for part A. No live-store-guard test pins it. Evidence states that `store migrate` finds ignored files through git, so the new directory moves with the store. The status-file scenario now also checks `ignored=1`, and today prints `ignored=0` (run in this round). Part C adds the status file to the README's store file table, checked by `drive-row` in the documents scenario, which prints `drive-row=no` today (run in this round).
- [NIT] Clerk line numbers → FIXED. `intake.js:50`, `build.js:41`. The ranges are now 50–67 and 41–58, checked with `grep -n 'async function clerk'` and by reading each function's closing brace.
- [NIT] Withheld tools unstated → FIXED. The tool-limits Decision now says every other tool the session offers is withheld, and that no role prompt asks for one. `grep -lE '\b(Task|TodoWrite|NotebookEdit|sub-?agent|Agent tool)\b' factory/prompts/*` matched no file.
- Unprompted: "tool fences" became "tool limits" in the Decisions, the Risk section, one requirement and one scenario name, and the Scenario to part list. The live-store fence keeps the name "fence", so two different mechanisms no longer share it (`docs/writing.md` rule 9).

## Critic rounds

round 1 · spec v1 · run-0401-critic · REVISE

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

round 2 · spec v2 · run-0403-critic · APPROVE

Round 2 review of the `factory drive` spec (v2), checkout `bb410c0`. Per convergence rules I reviewed (a) whether the round-1 findings were resolved and (b) the text that changed between v1 and v2 (the Problem's reordering, the new Evidence bullets on the fence gloss and the `.gitignore` block, the new status-file Decision, the Risk blast-radius line, Operator step 1, part A's file list and step 7/10, the new Tests to change section, the `ignored=1` and `drive-row` checks in two scenarios, and the Responses section).

What I checked myself (no suite run, no build):
- `grep -n 'async function clerk' factory/workflows/*.js` prints `intake.js:50` and `build.js:41`, as v2 now says.
- `STORE_GITIGNORE` is at `factory/store.py:49–52` with four entries under three comment lines; `ensure_gitignore` and `_ensure_block` sit at lines 55–84. `_ensure_block` adds only the missing non-comment lines to an existing file, which is what the three Tests to change bullets describe (a new store gets the comment line and `drive/`; an existing file gains `drive/` only).
- `tests/factory/test_run_scratch.py:121–147` holds the three named tests, and they pin what the spec says: exactly 3 comment lines and a count of 1 per entry (line 129–130), and two exact line lists ending `"runs/*/scratch/"` (lines 139–140, 148). All three break when `drive/` joins the block, so listing them is right.
- The membership reads are where the spec says and read by `in`, not by exact list: `test_instance.py:96`, `test_shepherd.py:200`, `test_tripwire.py:231`. A grep over `tests/factory/` for `runs/*/scratch/` found no other exact-list pin. No live-store-guard test pins the block.
- `_ignored_files` in `factory/cli.py` (around lines 1445–1456) uses `git ls-files --others --ignored --exclude-standard`, so a new ignored `drive/` directory moves with `store migrate` as Evidence says.
- README anchors for the revised documents scenario: the store file table's rows begin `| \``, the "Store records" row is line 463, and no row begins `| \`drive/` today, so `drive-row` is a sound check. Every other heading the command anchors on exists (lines 97, 117, 690, 712, 828, 904, 913).
- Acceptance command run as given (documents scenario, through the HOME wrapper): prints `starting=no depends=no built=no effort-gap=yes drive-row=no design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean`, exactly the baseline verification.md states.
- Gloss order as the gate operator: "runner session", "instance" and the dispatcher marker are first glossed in the Evidence fence bullet, before Decisions bullet 1 uses them; "spec gate" is glossed in the Problem's last paragraph, before Decisions and Operator steps; Operator step 1 now glosses the runtime and says what `--accept-harness` does. `EMPTY-OUTPUT`, `KILLED` and the whole-spec step are glossed under the parity table. The only remaining "tool fences" in the spec is the Responses line that quotes the old name.
- Approved changes not yet archived: none listed, so no cross-ticket setup conflict to check.
- Not checked, as they need the suite or the built change: that the parity records match byte for byte once `drive` exists, and that `ignored=1` prints after the first `run start` on the drive side (it follows from `_ensure_block` writing the whole block to a new store's empty `.gitignore`).

Findings

none blocking.

[NIT] 3 design.md, Tests to change, lead sentence
Problem: The lead sentence says each test "must take the new comment line and `drive/` as the block's last two lines", but for the two existing-file tests only `drive/` is added, because `_ensure_block` never adds comment lines to an existing file; the three bullets beneath already say this correctly.
Evidence: `factory/store.py:76–84` (`missing` filters out lines starting with `#`); the bullets for the second and third test say the lists end `"drive/"` with no comment line.
Suggested fix: Change the lead to "each must take the block's new last lines: the comment line and `drive/` for a new store, `drive/` alone for an existing file", or leave it, since the bullets govern.

Prior findings (round 1):
- [BLOCKING] 6 Problem, first paragraph → RESOLVED. The first paragraph now says what is wrong (a relay cost on every step, with the measured share and the 2026-10-09 false park) and for whom (the operator); the glossary follows in paragraph two.
- [BLOCKING] 6 Unglossed terms in Decisions and Operator steps → RESOLVED. Each term I named is glossed before or at its first use in a human-facing section, checked by grep order above.
- [SHOULD-FIX] 4 Status file committed or ignored → RESOLVED. A Decision states the choice with both alternatives rejected, Evidence shows the block, its writer and the tests that pin it, the three tests are listed under Tests to change with a reason each, part A's file list gains `factory/store.py` and `test_run_scratch.py`, and two scenarios now check the ignore line and the README row. I confirmed the three tests pin exactly what the spec says.
- [NIT] 1 Clerk line numbers → RESOLVED. 50 and 41, confirmed by grep.
- [NIT] 4 Withheld tools unstated → RESOLVED. The tool-limits Decision now states that every other tool is withheld and why that is safe.

Everything that held in round 1 still holds: the parity scenarios compare order-free records byte for byte, the NEW items fail today for the stated reasons (one re-run by me), protected path `factory/**` is declared, the design respects the T-0024 fence decisions, and the A/B/C split has natural seams. I would bet on this spec producing a correct PR.

## Verifier results

0e99ddad7eb10387369fac62286f8520fd6a1a67 · T-0040.3 · VERIFIED · run-0414-verifier
4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8 · T-0040.2 · VERIFIED · run-0410-verifier
656c179f4a4f4631b8fa61e037c7f871f36cd26d · T-0040.1 · VERIFIED · run-0407-verifier
