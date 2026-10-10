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

STATUS: APPROVE
CONFIDENCE: high, every revised citation I spot-checked (clerk lines, the `.gitignore` block and its three pinning tests, the membership reads, `_ignored_files`, the README table) exists as stated, the acceptance command I ran printed the stated baseline exactly, and the round-1 blocking items are fixed in the text itself.
ESCALATIONS: none
