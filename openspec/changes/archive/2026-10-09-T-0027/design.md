## Proposed change

NEEDS-SPLIT. The prototype's harness code is about 275 changed lines before tests and documents. With them the change is about 550 lines, over one reviewable PR. The seams are the lettered parts. A stands alone. B and C go together and stand alone. D needs A for the scenario where an amendment clears drift. E lands with each part, or last.

**A. `factory spec amend` (`factory/cli.py`, `factory/specstore.py`).** Add `amend` under the `spec` subparser: positional `id`, `--file` (required), `--reason` (required), `--intent` (required, `unchanged` or `changed`). Add `spec_amend(a, root, cfg)`. It runs these checks in this order. Each refusal raises `Refused`, so it exits 2 with `{"ok": false, "error": ...}` and nothing written.

1. The ticket has a `parent`: refuse, naming the parent.
2. `spec.approved_version` is None, or the status is `awaiting-spec-gate` or `closed`: refuse. At the gate, point to `approve-spec --edit`.
3. `--reason`, stripped, is empty or more than one line: refuse.
4. Any run id is in the `in_flight` list of the ticket or of any sub-ticket (`store.subtickets_of`): refuse, naming each run id.
5. `--intent changed`: refuse with `intent changed: ...` and the restart note.
6. `specstore.intent_changes(old, new)` is not empty: refuse with `intent changed (<each change>; ...)`, saying what `--intent unchanged` keeps, and the restart note.
7. With `specstore.is_active(root)`: the change folder `specstore.change_dir(root, id)` must exist (if it is gone, the ticket was archived). Then run `specstore.validate(text)` and `specstore.applies(root, deltas)` exactly as `approve_spec` runs them, and refuse with `spec not amended: <errors>`. The validator's own error texts, such as `has no NEW/REGRESSION label`, pass through.

The restart note is one paragraph that starts `Restart instead of amending.`. It lists the merged sub-tickets as `<id> / <title> (merge <main_after, 9 chars>)` and the rest that are not closed as `<id> / <title>: <status>[, branch <branch>]`, `none` for an empty list. It ends with the two restart paths in Decisions, naming the ticket id in each command.

Then write, in this order:
- Read the old pinned text, `specs/<id>/v<approved_version>.md`.
- Call `_add_spec_version(root, t, text, f"amend {file}", cfg)`.
- With a spec store: read `tasks.md` from the change folder if it exists, call `specstore.pin(root, id, text)`, then write `tasks.md` back.
- Set `spec.approved_version = n` and save.
- For each sub-ticket that is neither `merged` nor `closed`, set its `spec` to `{"version": n, "approved_version": n}` and save. Leave `planned_from` alone.
- Write `approvals/<id>/amendment-<k>.md`, with `k` from `_next_n(d, "amendment")`, so a hand-written `amendment-1.md` is counted. Content: a heading naming the ticket and `v<old> to v<n>`; `By <user> at <ts>.`; `Reason: <reason>`; `Intent: unchanged`; `## Scenarios changed`, one line per scenario as in Decisions, or `none`; `## Sub-tickets merged before this amendment`, one `- <id> / <title>: merged` line each, or `none`; `## Diff`, a fenced `difflib.unified_diff` of the old and new texts.
- Log `spec.amended` with `ticket`, `by`, `previous`, `version`, `reason` and `record`.
- Print `{"ok": true, "id", "version", "record"}`.

New helpers in `factory/specstore.py`:
- `scenario_blocks(text) -> dict[name, block]`: over every delta part (`split_parts`, `DELTA_RE`), each `#### Scenario:` block, from its heading line through the line before the next `##`, `###` or `####` heading, outside fences (`lines_outside_fences`, `SCEN_RE`, `_heading`). A scenario is changed when its name is in both versions and its block differs.
- `intent_of(text)` and `intent_changes(old, new) -> list[str]`. The intent is three things: the `## Problem` body of `proposal.md`; the `decisions_of` lines; and per delta part, per op, per requirement (`parse_delta`), the requirement block up to its first `#### Scenario:` line outside fences. Each is compared with whitespace runs collapsed. The result names `the Problem section`, `Decisions line removed: ...`, `Decisions line added: ...`, `requirement removed: <cap> <OP> <name>`, `requirement added: ...` and `requirement restated: ...`.

**B. The critic's input (`factory/compose.py`, critic branch, after `add_decisions()`).** When `<store>/openspec/changes/` exists, append a section headed exactly `## Approved changes not yet archived`. Go through the directories under it in name order. Skip `archive`, the reviewed ticket's own id, any id with no ticket record, and any id whose ticket is `closed`, `ready-for-spec-writer`, `ready-for-critic` or `awaiting-spec-gate`. Write one entry per remaining directory:

```
### <id>: <title> (<status>)
Change folder: `<absolute path>`
Changes: <capability>: <ADDED|MODIFIED|REMOVED> <requirement name>; ...
Decisions:
- <each line from specstore.decisions_of(proposal.md)>
```

Use `specstore.delta_ops_of_change` for the changes, and write `none` for an empty list. Add each listed `proposal.md` to the run's `sources`. With no entries, the section body is `none`. With no `openspec/changes/`, the section is left out.

**C. The critic rule (design doc block, `docs/prompts/03-spec-critic.md`, `factory/prompts/critic.md`).** Under rubric item 5, after its first line, add these four lines in all three copies. Keep each copy's existing differences: the runtime copy has `2` where the others have `{2}`.

```
   For each scenario, check whether it depends on behaviour that an
   approved change not yet archived (listed in your input) changes. If
   so, its setup must hold whichever of the two merges first; if it
   would not, that is BLOCKING: name that ticket and its decision.
```

**D. The drift check (`factory/cli.py`, `factory/subtickets.py`).**
1. Record. `_add_spec_version` takes `cfg` and, after writing the version, writes `specs/<id>/v<n>.yaml` with `integration_head`: `gitops.rev` of the integration branch in the target repo, or null when the repo or branch does not resolve. All three callers pass `cfg`: `spec_add`, `approve_spec --edit` and `spec_amend`.
2. Field text. Add `subtickets.field_text(text, name)`, the lines of one plan field, found the same way `sibling_tests` finds "Tests to change": from the field's own line to the next field in `PLAN_FIELDS`, or the next heading.
3. Check. In `run_start`, for the implementer on a sub-ticket, call `_check_drift(root, cfg, t)` before `_check_sibling_tests`. Return at once when the sub-ticket has a finished implementer run (`compose._runs_for`) or any `approvals/<id>/ruling-*` file. Otherwise collect findings:
   - Sibling rule. Take the current plan's sub-tickets (`subtickets.split_plan(store.subtickets_of(...))[0]`). Take the sub-ticket's dependency closure over their `depends_on`. For each other current sibling that is not `merged` and not in the closure, a finding when its id or `label` appears as a whole token in the Acceptance field text. A whole token is not preceded by a word character, `.` or `-`, and not followed by a word character, `-` or `.<digit>`. The finding reads `its Acceptance names <id> (<status>), which has not merged and is not one of its dependencies`.
   - Test rule. `base` is the `integration_head` recorded for the parent's approved version. Skip this rule when it is null or not a commit in the target repo. `tip` is the integration branch's head. Named files are the backticked tokens of the pinned spec's `design.md` part that exist as files at `tip`, are not test files, and do not end `.md`. Listed files are the backticked tokens, cut at `::`, of the design part's `## Tests to change` section and of the sub-ticket's "Tests to change" field. For each commit in `git rev-list --first-parent --reverse base..tip` whose `git diff --name-only --no-renames <c>^1 <c>` includes a named file, each test file it changes that is not listed is a finding, keeping the last such commit. A test file matches `(^|/)test_[^/]*$`, `_test\.[A-Za-z0-9]+$` or `\.test\.[A-Za-z0-9]+$`. The finding reads `<file> changed by <commit, 9 chars> since spec v<n> was written at <base, 9 chars>`.
   - With any finding, raise `Refused("BLOCKED from harness: spec drift: <findings joined by '; '>. Amend the spec (`spec amend <parent>`) or rule (`resolve <id> --ruling F`)")`. This happens before a run id is reserved, so nothing is written.
4. No workflow change. `factory/workflows/build.js:81-83` already parks any implementer run start refused with an error starting `BLOCKED `, with the error as the reason. `resolve --ruling` already accepts that park (`cli.py`, `resolve`).

**E. Documents.**
- `docs/design.md`:
  1. The rubric block in C.
  2. A paragraph `**Spec drift.**` after the `**Tests a sibling added.**` paragraph. It gives the record, when the check runs, both rules, the refusal and how the human resolves it.
  3. In the Spec store paragraph, after the sentence ending "work from the delta the human approved", say that after the gate only `factory spec amend <ticket id> --file F --reason "<line>" --intent unchanged` changes the pinned version. Say who runs it and when, what `--intent unchanged` keeps, that a change of intent is refused with a restart note, and that the re-pin keeps `tasks.md` and is recorded under `approvals/`.
  4. In line 113, after "amend the sub-ticket or the pinned spec", add "(`factory spec amend`, intent unchanged)".
  5. In the routing-table row `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic |`, add "every other approved change not yet archived, with its decisions" to Receives.
- `docs/changelog.md`: one new numbered entry, continuing the numbering. It names `factory spec amend` and `--intent`, says it refuses while a run is in flight and keeps `tasks.md`, describes the spec drift check, says the critic receives approved changes not yet archived, and gives the rule that a scenario's setup must hold whichever ticket merges first. If the parts land as separate sub-tickets, the first adds the entry and each later one extends it.
- `dev/build-harness.spec.md`: in the `factory resolve` bullet (line 315), mark `--amend-spec` as built instead as `factory spec amend PARENT --file F --reason LINE --intent unchanged` (doc §Spec store), and say `resolve` has no `--amend-spec`. In the Spec store paragraph (line 193), add that `run compose` gives the critic the approved changes not yet archived, and that a sub-ticket's first implementer `run start` checks spec drift (doc §Harness, Spec drift).
- `README.md`:
  - In "Where a human decides", add an **Amend** row to the table: `factory spec amend T-n --file F --reason "<line>" --intent unchanged`. Its "What you decide" cell names the three triggers: another ticket merged first, a checker found a scenario that cannot pass as written, or you changed your mind. It gives the rule: amend only when the Problem, the Decisions and every requirement's statement stay as approved; otherwise restart, by re-spec and re-plan or by close and re-file. `--intent changed` prints what a restart keeps and discards.
  - In the Unstick row's `--ruling F` list, add "the harness parked a sub-ticket for spec drift".
  - In "What is built and what is not", under Built, add a bullet `**Spec amendment and drift.**` that says what the command and the check do and ends "It is tested, and has not yet fired on a real ticket."
  - Bump the status date.

New tests, in new files under `tests/factory/`, driving `bin/factory` on a throwaway `FACTORY_STATE` and a scratch target, as `tests/factory/test_sibling_tests.py` does. Cover A's writes, each refusal and the intent check; B's section with and without other changes; and D's two rules, the ruling skip and the amendment that clears drift.

## Tests to change

none. The prototype ran the full suite (`408 passed`, the same count as on `main`), with the critic block edited in all three copies. The current-truth scenarios of the sibling-tests check printed the same lines on the prototype as on `main`.
