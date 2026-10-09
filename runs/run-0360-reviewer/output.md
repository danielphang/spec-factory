Commit: 9aa97bf43d815b288ca4dd1cf89cbde4dac55103

## What I checked

Read the whole diff `f4ea041...9aa97bf` against the sub-ticket's parts A-G and the parent spec's Decisions and Out of scope. Confirmed in the worktree, by narrow commands:

- `git diff --name-only f4ea041...9aa97bf -- tests | grep -v test_superseded_plan.py` prints nothing: no existing test file changed. The only test change is the new file. `git diff --stat` lists 8 files: README.md, dev/build-harness.spec.md, docs/changelog.md, docs/design.md, factory/cli.py, factory/compose.py, factory/subtickets.py, tests/factory/test_superseded_plan.py. No prompt, workflow or agent file.
- `factory/store.py:228-235` `subtickets_of` returns records sorted by sub-ticket number, so `after` in `subticket_add` and the `subtickets.superseded` event are in id order, as Decision 7 requires.
- `factory/compose.py:288-301` (planner branch): `av` is the parent's `spec.approved_version`, refused when None, and `subs` is every sub-ticket, so `superseded_by_plan(subs, av)` is D's `after` set for the parent. The existing list and its sentence are untouched; the new line is appended only when `gone` is non-empty.
- `factory/cli.py:97-106` `_set_dotted` refuses a key that is not already on the record. `ticket set T-0001.x planned_from=` works after this change only because `_create_subtickets` now writes the key; `v == ""` becomes None (`cli.py:117`), which `planned_from()` treats as absent. The null-fallback test therefore exercises the path it claims to.
- `factory/cli.py:560-583` `ticket_ready_implementers`: `ready`, the waiting-sibling release loop and every list but `subtickets` iterate `subs` (current); `subtickets` iterates `every`. Matches part C and Decision 8.
- `superseded_by_plan` with `version=None` (a parent without an approved version) yields no plan version for the probe record, so it supersedes nothing and does not raise.

Test integrity: clean. Correctness: each part A-G is present where the spec places it; the edge cases the spec implies (merged never superseded; same-version plan supersedes nothing; moved `spec` record ignored; fallback for missing field) are each covered by a black-box test in the new file. Scope: no change outside A-G. Silent behavior changes: none beyond the intended one; `store.subtickets_of`, the merge release, the sibling-tests check and `_planner_needed` are unchanged, as Out of scope requires. Security: no new input reaches a shell or a path; `Refused` paths write nothing. Coding standard: `planned_from`, `split_plan` and `superseded_by_plan` are the one rule the spec asks for, in the module the spec names, with the rule written once and reused by D and E; callers of every changed function are named in the PR description from a grep. Lean already.

## Findings

[NIT] README.md:9: part G says "Bump the status date"; the header already reads `2026-10-09`, today's UTC date, and was left as is → nothing a reader would notice; the Known gaps entry explains the choice. No change needed.

## Out-of-scope observations

- `ready_implementers` now sees only current sub-tickets, so a superseded sub-ticket with a run a human started by hand (which Out of scope says is not refused) no longer counts as in flight when a `parallel_safe: false` sibling asks to run alone. The spec's part C asks for exactly this computation; noting it so the operator knows the hand-run case is unguarded.
- `split_plan` compares versions with `<`; a hand-set non-integer `planned_from` would raise. The PR description's Known gaps already says so, and no harness path writes one.

## PR description

What changed opens with the problem and glosses planner, approved version, sub-ticket, spec gate and superseded before using them; each part is stated in words with its file; Known gaps names the README date decision, the archive coverage limit, the type comparison and "factory: markers added: none". It meets the writing standard. No finding.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. Every part of the spec is in the diff where the spec places it, no existing test changed, and the four points I could not settle by reading (test-file list, id ordering, `ticket set` on the new key, compose's `av`) were each confirmed by a command in the worktree.
ESCALATIONS: Protected paths touched, all declared in the parent spec's Risk section: harness `factory/**`, namely `factory/cli.py`, `factory/subtickets.py`, `factory/compose.py`. No file under `factory/workflows/`, `factory/prompts/`, `docs/prompts/`, `agents/`, `bin/factory`, `pyproject.toml`, `uv.lock` or `.factory/` changes. The merge gate needs a human approval for the harness paths.
