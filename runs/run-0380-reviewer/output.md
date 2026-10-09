Commit: d085ca0b1cd5f084c4065c186c5467d6fd82b9ae (branch `factory/T-0027.2`, base 89290547a33a6091860c850fdda7ff285b409fa0)

## What I checked

1. Test integrity. `git diff --stat 8929054..d085ca0` lists five files: `docs/design.md` (+4), `docs/prompts/03-spec-critic.md` (+4), `factory/compose.py` (+28), `factory/prompts/critic.md` (+4) and the new `tests/factory/test_critic_approved_changes.py` (+184). No existing test file changed; no assertion weakened, skipped or hard-coded. Clean.

2. Correctness against the spec's part B (`factory/compose.py:236-259`).
   - Gate on `<store>/openspec/changes/` existing: `specstore.root_dir(root) / "changes"` is `root/openspec/changes` (`specstore.py:48-49`); `is_dir()` false → return, so the section is left out. Matches "left out when the store has no spec store".
   - Directories in name order: `sorted(... if p.is_dir())`. Skips `archive`, the reviewed ticket (`tid`, bound at `compose.py:170`), an id with no record (`store.ticket_path(root, cid).exists()`, `store.py:109`) and the four states named in Decisions. All four skip rules match the spec.
   - Entry format: `### <id>: <title> (<status>)`, `Change folder: \`<absolute path>\``, `Changes: <cap>: <OP> <name>; ...` or `none`, then `Decisions:` with one `- <line>` each. `d` is absolute because `store.state_root` resolves `FACTORY_STATE` through `instance.env_path`, which calls `.resolve()` (`instance.py:52`). `delta_ops_of_change` returns `{cap: {op: {name: block}}}` (`specstore.py:363-369`, via `parse_delta`), and the comprehension iterates `by_op.items()` then the names, so the join is `cap: OP name`.
   - Each listed `proposal.md` goes into `sources` as a root-relative path, the same form `add()` records (`compose.py:194`); `sources` is only stored in `meta["input_sources"]` and echoed in the JSON (`cli.py:325-329`), so nothing downstream rejects it.
   - Placement: the call sits after `add_decisions()` in the critic branch (`compose.py:297`) and nowhere else.
   - Empty-decisions case: the implementer writes `Decisions: none`. The spec gives no text for this case, and the PR's Known gaps says so. Not a finding.

3. Scope. The design-doc diff is exactly the four rubric lines at `docs/design.md:463-466`; `git diff ... -- docs/design.md | grep -c '^[+-][^+-]'` prints `4`, so no part-E edit leaked in. Nothing touches `cli.py`, `specstore.py` or the drift check.

4. Part C copies. I ran the regression check: `diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md` → `copies=same`, so the runtime prompt is still the documented prompt with its round placeholder filled. `grep -c 'whichever of the two merges first'` prints `1` for each of the three files: each carries the rule once. The whole `docs/prompts/03-spec-critic.md` is still a verbatim substring of `docs/design.md` (checked with a Python `find`), so the "re-copied from the block" rule holds.

5. Silent behaviour changes. Only critic runs on a store with `openspec/changes/` get a new input section; every other role's input is unchanged. The implementer's Known gaps notes it is added on every critic round, which the design does not restrict.

6. Security and data safety. Reads only under the store root; no writes, no shell, no external input beyond store files.

7. Protected paths. `factory/compose.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`: all three are declared in the sub-ticket and in the parent spec's Risk section. Listed under ESCALATIONS for the record; the merge gate needs no further approval for them.

8. Coding standard. The helper is a local closure beside `add_decisions()`, the pattern the function already uses; it calls the existing `specstore.root_dir`, `store.ticket_path`, `store.load_ticket`, `specstore.delta_ops_of_change` and `specstore.decisions_of` rather than re-parsing anything. The test file follows the repo's per-file `Store`/`Fixture` class pattern (`test_empty_output.py:22`, `test_run_scratch.py:24`, `test_sibling_tests.py:59`); there is no shared helper in `conftest.py` to reuse. No test patches a path (rule 6). Lean already.

9. PR description. What changed glosses the critic and the change folder on first use and says in words what the section holds and when it is omitted; Known gaps names each choice the design left open (empty decisions, missing `proposal.md`, every round) and the marker count. Readable at the gate.

## Findings

none

## Prior findings

none (round 1)

STATUS: APPROVE
CONFIDENCE: high. The diff is small, every rule of parts B and C is traceable to a line I read, and the two document regression checks printed `copies=same` and `1` per file on this head.
ESCALATIONS: protected paths touched, all declared in the sub-ticket and the approved spec's Risk section, listed for the record: `factory/compose.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`.
