Commit: 9a99851bd15fe781c814231bb952513d1b597438 (branch `factory/T-0027.1`, base 8929054, one commit)

## What I checked

1. Test integrity. `git diff --name-status 8929054..9a99851 -- tests/` lists one added file, `tests/factory/test_spec_amend.py`; no existing test file is changed, skipped or deleted. The new file's `refused()` helper asserts exit 2, `ok: false` and a byte-identical store snapshot for every refusal, and the write tests assert the exact JSON result, the record's exact section bodies and the event's fields. No assertion is hard-coded to output I could not derive from the spec.
2. Correctness against part A of the parent spec, read against the code in the worktree:
   - The seven refusals run in the spec's order (`factory/cli.py:437-470`): parent, gate / no approved version / closed, reason, in-flight on parent and sub-tickets, `--intent changed`, `intent_changes`, then with a spec store the change folder, `validate` and `applies`. The `validate`/`applies` call is the same two lines `approve_spec` uses (`cli.py:945-946`), so the validator's own text passes through. Every refusal raises `Refused` before the first write; `_approval_dir`, which creates a directory, is first called after the writes (`cli.py:493`).
   - The writes follow the spec's order (`cli.py:471-502`): `_add_spec_version` with four arguments, `tasks.md` read before `pin` and written back after, `approved_version`, the sub-ticket `spec` records for those neither merged nor closed with `planned_from` untouched, `amendment-<k>.md` numbered by `_next_n(d, "amendment")`, the `spec.amended` event with the six fields, the JSON result with `id`, `version`, `record`.
   - `_add_spec_version` also rewrites `specs/<id>.md` (`cli.py:398`), which `approve_spec` does separately (`cli.py:956`), so the current-spec file follows the amendment too.
   - `scenario_blocks` ends a block at the next `##`, `###` or `####` heading outside fences via the existing `_heading` (`specstore.py:89`); `validate` already refuses a scenario name used twice in a change (`specstore.py:205`), so the name-keyed dict loses nothing.
   - `intent_of` cuts each requirement block at its first `#### Scenario:` outside fences; `requirement_blocks` ends a block at `##`/`###`, so scenarios are inside the block and the cut is what the spec asks. Renaming a requirement or moving it between ops reports removed + added, which the spec's result vocabulary covers.
   - The restart note has the merged list with 9-char merge sha, the unmerged list with status and branch, `none` for empty lists, and both routes with the ticket id in each command. `ticket park --reason` is a real required flag (`cli.py:1615`).
3. Scope. Only `factory/cli.py`, `factory/specstore.py` and the new test file change. No `cfg` parameter, no `v<n>.yaml`, no drift check, no document edits.
4. Silent behaviour changes. No existing function changed; `_add_spec_version`, `approve_spec` and `spec_add` are byte-identical to base. The only new caller-visible surface is the new subcommand.
5. Security and data safety. The command reads one file the human names and writes only under the store. `pin` already does `rmtree` of the change folder on `main`; the amendment's extra risk is the planner's `tasks.md`, which is read before `pin` and written back, and `test_amendment_repins_keeps_tasks_and_moves_unmerged_subtickets` and `test_amendment_without_tasks_md_writes_none` cover both cases.
6. Protected paths. `factory/cli.py` and `factory/specstore.py` are declared by the sub-ticket and by the parent spec's Risk section. Listed under ESCALATIONS for the record.
7. Coding standard. See the findings. `net: -5 lines possible`.
8. PR description. What changed opens with the missing capability and the operator who gets it, glosses "pinned spec", "spec store" and "change folder" at first use, and Known gaps lists real uncertainties with their consequence. Readable by the operator at the gate.

## Findings

- [NIT] factory/specstore.py:355-363: the `## Problem` body loop in `intent_of` is a fourth copy of the "body of one `## ` section" pattern that `decisions_of` (`specstore.py:309-310`) and `acceptance_labels` (`specstore.py:168-169`) already hand-roll → the next fix to how a section is found, such as a `## Problem` heading inside a fence or a trailing space, has to land in four places. No shared helper exists on `main`, so there is nothing to reuse yet; extracting one would touch two functions outside this sub-ticket, which is why this is a NIT and not a `reuse:` finding. If a later ticket touches those functions, a `_section_body(text, heading)` helper would take about 5 lines out.
- [NIT] PR description: What changed: the bullet "`import difflib` (standard library, already used by `factory/compose.py`)" is a file-list item, not a change a reader needs; the Reuse paragraph already covers it.

Nothing BLOCKING or SHOULD-FIX. I would merge this into code I own.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. I read every changed line against the spec's part A and the helpers it names in the worktree, confirmed the refusal order and write order line by line, and confirmed no existing test or function changed; the verifier runs the suite and the acceptance commands on this head.
ESCALATIONS: protected paths touched, both declared by the sub-ticket and the parent spec's Risk section: `factory/cli.py` (new `spec amend` subparser and `spec_amend`, `_restart_note`), `factory/specstore.py` (new `scenario_blocks`, `intent_of`, `intent_changes`). No further approval needed at the merge gate.
