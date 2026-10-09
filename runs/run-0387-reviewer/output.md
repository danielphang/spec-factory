Commit: d085ca0b1cd5f084c4065c186c5467d6fd82b9ae (branch `factory/T-0027.2`, forked from `8929054`; merge-base with the given base `92e7038` is `8929054`, so the reviewed diff is the five files the three-dot diff shows: `docs/design.md`, `docs/prompts/03-spec-critic.md`, `factory/compose.py`, `factory/prompts/critic.md`, new `tests/factory/test_critic_approved_changes.py`, 224 insertions, 0 deletions)

Findings:

- [NIT] PR description: What changed: "Each listed `proposal.md` is added to the run's `sources`" uses `sources` without saying what it is → a reader new to the project cannot tell whether this is a file, a list the harness records, or something the critic sees. One clause would do: "the list of store files the composed input was built from, recorded with the run".

No BLOCKING or SHOULD-FIX findings. Lean already.

What I checked, in the rubric's order:

1. Test integrity. No existing test file is in the diff (`git diff --stat 92e7038...d085ca0`: one new test file, no deletions). The two-dot `git diff 92e7038..HEAD` shows deletions in `factory/cli.py`, `factory/specstore.py`, `factory/subtickets.py`, `tests/factory/test_spec_amend.py` and `tests/factory/test_spec_drift.py`; those are ST-1 and ST-3 landing on `main` after this branch forked, not changes on this branch. A trial merge of `d085ca0` onto `92e7038` (`git merge-tree --write-tree`) is clean: neither sibling touched `factory/compose.py`, the three prompt copies or the new test file.

2. Correctness against part B (design.md, "B. The critic's input"), read at `factory/compose.py:233-259` in the worktree:
   - Section only when `<store>/openspec/changes/` is a directory (`specstore.root_dir(root) / "changes"`, `root_dir` is `root / "openspec"` at `factory/specstore.py:48`); otherwise the helper returns and the section is left out. Matches "With no `openspec/changes/`, the section is left out".
   - Directories in name order (`sorted(... iterdir() if p.is_dir())`). Skips `archive`, the reviewed ticket (`tid`, bound at `compose.py:172` to `t["id"]`), an id with no ticket record (`store.ticket_path(...).exists()`, `factory/store.py:109`), and the four statuses the design names. Matches the skip list exactly.
   - Entry: `### <id>: <title> (<status>)`, `Change folder: \`<absolute path>\`` (`d` is under `root`, which comes from `FACTORY_STATE`; the acceptance scenario and the new tests pass an absolute path), `Changes:` from `specstore.delta_ops_of_change` (`factory/specstore.py:363`, returning capability → op → {name: block}; the comprehension iterates the inner dict's keys, so it lists names) with `none` for an empty list, `Decisions:` from `specstore.decisions_of(proposal.md)` (`factory/specstore.py:306`). Each listed `proposal.md` is appended to `sources` as a store-relative path, the same form `add()` uses at `compose.py:194`.
   - Body `none` with no entries; the part string begins `\n## ` and ends with a newline, consistent with every other `parts.append` in the file (joined by `"".join(parts)` at `compose.py:399`).
   - Placement: critic branch, directly after `add_decisions()` (`compose.py:296-297`), before the round-2 prior-findings block. Matches "after `add_decisions()`".
   - `Decisions: none` for a proposal with no Decisions lines is the implementer's declared choice (Known gaps); the design gives no format for that case, and `none` is the word it uses for the empty Changes list. Not a finding.
   Part C: the four lines are identical in all three copies and sit after the first line of rubric item 5; none contains `{2}`, so the runtime copy's only difference from the documented one remains the round placeholder, which is what the REGRESSION scenario `copies=same` checks. Only the critic block of `docs/design.md` changed (`@@ -460,6 +460,10 @@`).

3. Scope. Nothing outside parts B and C. No edit to `docs/changelog.md`, `dev/build-harness.spec.md`, `README.md` or the design doc outside the critic block (those are ST-4's).

4. Silent behaviour changes. Every critic run on a store with a spec store gets one more input section, which the parent spec's Risk section declares. No other role's input changes; no state, routing, gate or archive behaviour changes.

5. Security and data safety. Read-only over the store; no shell, no network, no writes outside the composed `input.md` the run already writes.

6. Protected paths. `factory/compose.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`: all three declared in the sub-ticket and in the parent spec's Risk section. Listed under ESCALATIONS for the record.

7. Coding standard. Rule 1: `add_approved_changes()` is a local closure beside `add_decisions()` and `add_truth()`, the pattern this function already uses; it reuses `specstore.root_dir`, `store.ticket_path`, `store.load_ticket`, `specstore.delta_ops_of_change` and `specstore.decisions_of` rather than re-reading YAML or parsing deltas itself. Rule 2: no existing function changed signature; the PR description says so and names the one new call. Rule 3: no shortcut with a known limit; "factory: markers added: none" is stated. Rule 5: the identifiers (`changes`, `proposal`, `decisions`, the heading text) are the spec's names. Rule 6: the tests patch nothing and drive `bin/factory` with `FACTORY_STATE` and `FACTORY_REPO` under `tmp_path`, as `test_sibling_tests.py` does. net: Lean already.

8. PR description. What changed glosses "critic" and "change folder" at first use and says in words what the section holds and when it is omitted. Known gaps names the three choices the design left open (empty Decisions, a folder with no `proposal.md`, every round). The one gap is the NIT above.

Tests (new file, 13 tests): they cover the sub-ticket's "with and without other changes" requirement: an entry's exact lines, the state in the heading, archive → `none`, each of the four skipped statuses, the request-changes route, a stray folder and `archive`, folder-name order and `Changes: none`, no other change → `none`, no spec store → section absent, and the rubric lines in the system prompt. Assertions are exact (list equality on the section's non-blank lines), not substring-loosened.

Prior findings: none (round 1).

Out-of-scope observations:
- The branch forks from `8929054` while `main` is at `92e7038` (ST-1 and ST-3 merged since). The trial merge is clean, so this is for the merge gate's record, not a change request.

STATUS: APPROVE
CONFIDENCE: high. The diff is 224 added lines in five files, every behaviour the design's part B and C name is present at a cited line, the trial merge onto current `main` is clean, and the new tests assert exact section contents.
ESCALATIONS: Protected paths touched, all declared in the sub-ticket and the approved spec's Risk section: `factory/compose.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`. For the record only; no approval needed.
