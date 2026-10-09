Sub-ticket: T-0027.2 (ST-2, parts B and C of `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`). Branch `factory/T-0027.2`, head `7c21dae` (the merge of `main` at `92e7038` into the reviewed commit `d085ca0`), in worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0027.2`.

## What changed

**B. The critic's input (`factory/compose.py`).** The critic is the role that grades a spec before the operator's sign-off. Its input now has a section headed `## Approved changes not yet archived`. A change folder is the store's copy of a ticket's approved spec, written when the operator approves it and moved away when the ticket is archived. The new section comes right after the decision log. It is written by a new local helper, `add_approved_changes()`, in `compose()`, called only in the critic branch. The helper reads the directories under `<store>/openspec/changes/` in name order. It skips:
- `archive`;
- the reviewed ticket's own id;
- an id with no ticket record;
- a ticket that is `closed`, `ready-for-spec-writer`, `ready-for-critic` or `awaiting-spec-gate`.

Each remaining folder gets one entry: `### <id>: <title> (<status>)`, then `Change folder: `<absolute path>``, then `Changes: <cap>: <OP> <requirement>; ...` from `specstore.delta_ops_of_change` (or `none`), then `Decisions:` with one `- <line>` per `specstore.decisions_of` line. Each listed `proposal.md` is added to the run's `sources`. With no entries the section body is `none`. Without `openspec/changes/` the section is left out.

**C. The critic rule.** The four lines from the spec go under rubric item 5 ("Consistent") in three copies: the design doc's critic block (`docs/design.md:463-466`), `docs/prompts/03-spec-critic.md` and the runtime copy `factory/prompts/critic.md`. The new lines contain no `{2}` placeholder, so all three copies get the same text. The runtime copy still equals the documented one with `{2}` filled. I edited only the critic block of `docs/design.md`.

Callers (coding standard rule 2): no existing function changed signature. The only new call is `add_approved_changes()`, from the critic branch of `compose()`.

## Acceptance results

All commands ran from the worktree, inside the running-code wrapper (a fresh temporary HOME), with `TMPDIR` set to this run's scratch directory. The GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" ran once before the commands.

- NEW: "The critic's input lists approved changes not yet archived, other than its own"
  - before: `listed=0 self=0 decision=0 requirement=0`, `after_archive: heading=0 listed=0` (matches the spec's "fails today")
  - after: `listed=1 self=0 decision=1 requirement=1`, `after_archive: heading=1 listed=0`
- NEW: "A change sent back to the spec writer leaves the critic's list"
  - before: `listed=0 self=0 decision=0 requirement=0`, `respec: heading=0 listed=0`
  - after: `listed=1 self=0 decision=1 requirement=1`, `respec: heading=1 listed=0`
- NEW: "A critic run's system prompt carries the cross-ticket rule"
  - before: `rule=0`
  - after: `rule=1`
- REGRESSION: "The runtime critic prompt stays a copy of the documented one". After: `copies=same`.
- REGRESSION (intermediate): `grep -c 'whichever of the two merges first' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md`. After: `docs/design.md:1`, `docs/prompts/03-spec-critic.md:1`, `factory/prompts/critic.md:1`. Before: `0` in each.
- Gate: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)` printed nothing and exited 0.
- Gate: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` gave `431 passed in 313.56s`, including the 13 new tests.

## Tests added/changed

Added one new file, `tests/factory/test_critic_approved_changes.py`, with 13 tests. They drive `bin/factory` on a throwaway store and a scratch target repo.
- Another approved ticket is listed with its exact entry (folder, `Changes: demo: ADDED Greets`, decision). The reviewed ticket is not listed, and the other ticket's `proposal.md` is in `sources`.
- The entry shows the ticket's state (`planned`).
- After archive, the body reads `none`.
- Each of `closed`, `ready-for-spec-writer`, `ready-for-critic` and `awaiting-spec-gate` is left out (4 parametrized cases).
- A change sent back through park, `resolve --to spec-gate` and `request-changes` leaves the list.
- A folder with no ticket record and the `archive` folder are skipped.
- Entries follow folder-name order, and an empty delta reads `Changes: none`.
- With no other change, the body reads `none`.
- Without a spec store, the section is absent.
- A critic run's system prompt carries the four new rubric lines.

I watched 12 of the 13 fail before the change: the section was absent and the rule missing. The no-spec-store test passed before and after, as it should, because it checks that the section is absent.

Existing tests changed: none.

## Known gaps and uncertainties

- When a listed change's proposal has no Decisions lines, the entry reads `Decisions: none`. The design gives `none` only for an empty Changes list and does not say how to show empty decisions, so this is my choice.
- A change folder with no `proposal.md` is still listed, with `Decisions: none`, and nothing is added to `sources`.
- The section is composed for every critic run on a store with a spec store, round 1 and later rounds alike. The design names no round condition.
- factory: markers added: none.

## Out-of-scope observations

- The parent spec says this repo's live store still has change folders for closed tickets T-0026 and T-0030. Part B skips closed tickets, so the critic never sees them. I did not look into why they were never archived.
- `uv run` printed a warning that the inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` does not match the project's `.venv` and was ignored. The suite ran in the project environment. T-0031 deals with this inherited environment.

## Conflict resolution (merge of `main`)

The merge gate refused the branch because it did not contain `main`: sub-tickets T-0027.1 (part A, `factory spec amend`) and T-0027.3 (part D, the spec drift check) merged after this branch forked at `8929054`. I merged `main` (`92e7038`) into the branch with `git merge --no-ff main`; the merge commit is `7c21dae`. Git reported no conflicts, and I edited no file during the merge. The two sides share no file: `main`'s new commits change `factory/cli.py`, `factory/specstore.py`, `factory/subtickets.py` and add `tests/factory/test_spec_amend.py` and `tests/factory/test_spec_drift.py`, while this branch changes `factory/compose.py`, the three critic prompt copies and adds `tests/factory/test_critic_approved_changes.py`. `git diff --stat main...HEAD` still shows only this branch's five files, 224 insertions and no deletions.

I re-ran everything on `7c21dae`, with the same wrapper and `TMPDIR` set to this run's scratch directory. The GIVEN block ran first and exited 0.
- "The critic's input lists approved changes not yet archived, other than its own": `listed=1 self=0 decision=1 requirement=1`, `after_archive: heading=1 listed=0`.
- "A change sent back to the spec writer leaves the critic's list": `listed=1 self=0 decision=1 requirement=1`, `respec: heading=1 listed=0`.
- "A critic run's system prompt carries the cross-ticket rule": `rule=1`.
- "The runtime critic prompt stays a copy of the documented one": `copies=same`.
- `grep -c 'whichever of the two merges first' ...`: `1` in each of the three files.
- Gate `git diff --check main...HEAD`: no output, exit 0.
- Gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `486 passed in 373.35s`. The suite now also holds the tests that came in from `main` (431 before the merge).

The reviewer's one NIT (gloss `sources`) is on the description, not the code. A conflict run changes nothing beyond the merge and this note, so I left the NIT for the next fix round. For a reader new to the project: `sources` is the list of store files the composed input was built from, which is recorded with the run.

## Protected paths touched

All three are declared in this sub-ticket: `factory/compose.py`, `factory/prompts/critic.md` and `docs/prompts/03-spec-critic.md`.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The merge of `main` was conflict-free and touched no file this branch changes, and every acceptance command and both gates passed again on the merged head 7c21dae.
ESCALATIONS: none
