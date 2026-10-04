## Proposed change

The prototype was about 100 changed lines of harness code. With tests and documents, the change is roughly 250 lines, so it fits one PR.

**A. `factory spec amend` (`factory/cli.py`, `factory/specstore.py`).** Add `amend` under the `spec` subparser: positional `id`, `--file` (required), `--reason` (required). Add a `spec_amend(a, root, cfg)` that does these checks in this order. Each refusal raises `Refused`, so it exits 2 with `{"ok": false, "error": ...}` and nothing written:

1. The ticket has a `parent`: refuse, naming the parent.
2. `spec.approved_version` is None, or the status is `awaiting-spec-gate` or `closed`: refuse. At the gate, point to `approve-spec --edit`.
3. `--reason`, stripped, is empty or more than one line: refuse.
4. Any run id is in the `in_flight` list of the ticket or of any sub-ticket (`store.subtickets_of`): refuse, naming each run id.
5. With `specstore.is_active(root)`: the change folder `specstore.change_dir(root, id)` must exist (if it is gone, the ticket was archived); then `specstore.validate(text)` and `specstore.applies(root, deltas)` exactly as `approve_spec` runs them. Refuse with `spec not amended: <errors>`. The validator's own error texts, such as `has no NEW/REGRESSION label`, pass through.

Then write, in this order:

- Read the old pinned text, `specs/<id>/v<approved_version>.md`.
- Call `_add_spec_version(root, t, text, f"amend {file}")`. It writes `specs/<id>/v<n>.md` and the copy `specs/<id>.md`, and logs `spec.added`.
- When the store has a spec store: read `tasks.md` from the change folder if it exists, call `specstore.pin(root, id, text)`, and then write `tasks.md` back.
- Set `spec.approved_version = n` and save.
- For each sub-ticket whose status is neither `merged` nor `closed`, set its `spec` to `{"version": n, "approved_version": n}` and save.
- Write `approvals/<id>/amendment-<k>.md`, with `k` from `_next_n(d, "amendment")`, so a hand-written `amendment-1.md` is counted. Content: a heading naming the ticket and `v<old> to v<n>`; `By <user> at <ts>.`; `Reason: <reason>`; `## Scenarios changed` with one line per scenario, `- changed: <name>`, `- added: <name>` or `- removed: <name>`, or `none`; `## Sub-tickets merged before this amendment` with one `- <id> / <title>: merged` line each, or `none`; `## Diff` with a fenced `difflib.unified_diff` of the old and new texts.
- Log `spec.amended` with `ticket`, `by`, `previous`, `version`, `reason` and `record`.
- Print `{"ok": true, "id", "version", "record"}`.

Scenario comparison needs a new helper in `factory/specstore.py`, `scenario_blocks(text) -> dict[name, block]`. Over every delta part of one version (`split_parts`, `DELTA_RE`), it returns each `#### Scenario:` block: the heading line through the line before the next `##`, `###` or `####` heading, outside fences (reuse `lines_outside_fences`, `SCEN_RE` and `_heading`). A scenario is changed when its name is in both versions and its block differs.

**B. The critic's input (`factory/compose.py`, critic branch, after `add_decisions()`).** When `<store>/openspec/changes/` exists, append a section headed exactly `## Approved changes not yet archived`. For each directory under it, in name order, skip `archive`, the reviewed ticket's own id, and any id whose ticket is `closed`. Write one entry per remaining directory:

```
### <id>: <title> (<status>)
Change folder: `<absolute path>`
Changes: <capability>: <ADDED|MODIFIED|REMOVED> <requirement name>; ...
Decisions:
- <each line from specstore.decisions_of(proposal.md)>
```

Use `specstore.delta_ops_of_change` for the changes. Write `none` for an empty list. Add each listed `proposal.md` to the run's `sources`. With no entries, the section body is `none`. With no `openspec/changes/`, the section is left out.

**C. The critic rule (design doc block, `docs/prompts/03-spec-critic.md`, `factory/prompts/critic.md`).** Under rubric item 5, after its first line, add these four lines in all three copies. Keep each copy's existing differences: the runtime copy has `2` where the others have `{2}`.

```
   For each scenario, check whether it depends on behaviour that an
   approved change not yet archived (listed in your input) changes. If
   so, its setup must hold whichever of the two merges first; if it
   would not, that is BLOCKING: name that ticket and its decision.
```

**D. Documents.**
- `docs/design.md`: (1) the rubric block in C. (2) In the Spec store paragraph (line 88), after the sentence ending "work from the delta the human approved", add a sentence saying that after the gate only `factory spec amend <ticket id> --file <F> --reason "<line>"` changes the pinned version. A human runs it before archive, with no run in flight on the ticket or its sub-tickets. It writes a new version, re-pins the change folder keeping `tasks.md`, and records the amendment under `approvals/`. (3) The routing-table row `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic |` (line 113): add "every other approved change not yet archived, with its decisions" to Receives.
- `docs/changelog.md`: one new numbered entry, continuing the numbering, naming `spec amend`, that it refuses while a run is in flight, that it keeps `tasks.md`, that the critic receives approved changes not yet archived, and the rule that a scenario's setup must hold whichever ticket merges first.
- `dev/build-harness.spec.md`: in the `factory resolve` bullet (line 314), mark `--amend-spec` as built instead as `factory spec amend PARENT --file F --reason LINE` (doc §Spec store), and say `resolve` has no `--amend-spec`. In the Spec store paragraph (line 193), add that `run compose` gives the critic the approved changes not yet archived.
- `README.md`: in "Where a human decides", add an **Amend** row to the table: `factory spec amend T-n --file F --reason "<line>"`, for changing the pinned spec after the gate when a scenario cannot pass as written. Say it refuses while a run is in flight on the ticket, that the ticket's state does not change, and that it is tested but has not been used on a real ticket. Bump the status date if it changes.

**E. Tests.** Add one new file, `tests/factory/test_spec_amend.py`, driving `bin/factory` on a throwaway `FACTORY_STATE`, as `tests/factory/test_spec_store.py` does. It should cover A's writes and each refusal, and B's section with and without other changes.

## Tests to change

none. The prototype ran the full suite. The only failure was the existing check that the design doc's critic block equals `docs/prompts/03-spec-critic.md`, which passes once part C edits both copies, as it must.
