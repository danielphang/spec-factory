## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0039-critic/output.md`

## Spec under review (v3)

## Problem

The factory's spec is shaped like a change: it says what a ticket will do and how to check it. Nothing in the store says what a capability does now. After a ticket ships, a later writer, critic or operator who wants current behaviour has to replay every spec that ever touched it. This affects every reader downstream of the spec gate, and the gap grows with each merged ticket.

The operator adopted OpenSpec's storage model and lifecycle as a forked `spec-factory` schema, with layout (a) (Answer 1). That means:
- current truth per capability;
- one change folder per ticket, holding proposal, design, a delta, tasks, and a factory-only `verification.md`;
- the spec gate pins the delta;
- parent close becomes archive;
- a repo-level `decisions.md`.

Roles, round limits, gates and harness pieces 1–12 stay. The scope is limited to `docs/spec-factory.md`, `specs/build-harness.md`, the re-copied `prompts/` files and the Changelog. Green-side migration is out (A1), and specs T-0001..T-0007 are not migrated (A4).

## Evidence

Checkout: `~/dev/spec-factory` `main` at `b4d0f90`. `git diff --stat 4cd8d12 HEAD -- docs specs prompts README.md plans` prints nothing, so the documents are the same as at `4cd8d12`, the commit v2 was written against. I re-checked every OLD anchor below on `b4d0f90` with `grep -c -F`: each matches exactly once, including the three anchors new in v3 (`with input = ticket + request (+ on round ≥ 2:`, `with input = spec vN (+ round ≥ 2:` and `Acceptance line itself, which the verifier runs verbatim on both base`). Every edit is anchored on text, never on a line number.

- **No current-truth layer exists.**
  - `grep -rniE 'openspec' docs specs plans prompts README.md | wc -l` → `0`.
  - `grep -rliE 'openspec|decisions\.md' ~/dev/nanobot-upstream/factory | wc -l` → `0`. No reference-harness fix exists to verify against, so every acceptance item below is checked against the documents.
- **Where the spec format is defined today:**
  - §2 FORMAT is one flat list: Problem, Evidence, Root cause, Proposed change, Acceptance, Tests to change, Out of scope, Open questions, Risk, Operator steps (T-0005, merged as `ac66b2c`), Responses. The RULES above it say "give the check as an inline script in the / Acceptance line itself".
  - The §4 Planner OUTPUT has `  Acceptance: commands + expected results` and `Coverage map: parent criterion → sub-ticket ID`.
  - The Merge gate routing row says "VERIFIED closes the parent; FAILED or SPEC-DEFECT parks the parent in the human queue".
  - `specs/build-harness.md` part B says "Spec text `specs/<ID>/v<N>.md`; sub-ticket text `specs/<ID>/subticket.md`."
  - Part B, `factory run compose`: "writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares … — the 'with input =' lists in H". Part H `intake.js` step 2: the writer's input is "ticket + request (+ on round ≥ 2: …)" and the critic's is "spec vN (+ round ≥ 2: …)". So a role receives only what those lists name.
  - Item 42 says the critic's `input_sources` is "exactly `[specs/T-0001/v1.md]`" and the file "contains neither the triage output nor the writer's `CONFIDENCE:` line". The stored spec text therefore has no trailer. The reference harness does the same: `factory/cli.py` `_text_from` returns `status.strip_trailer(...)` of the run's `output.md`, and `factory/status.py` `strip_trailer` returns "the text above the final STATUS/CONFIDENCE/ESCALATIONS block".
  - Part H `build.js` step 2 has "`VERIFIED` → `closed`;".
  - Part K `approve-spec` exports the pinned text to `knowledge_vault/sanitized_specs/<ID>.md`.
- **OpenSpec facts, checked rather than taken from the request.** For v0 I downloaded `README.md`, `docs/concepts.md` and `docs/customization.md` from `raw.githubusercontent.com/Fission-AI/OpenSpec/main`. For v1 I re-fetched `concepts.md`, `customization.md` and `package.json`. `git ls-remote` gave repo HEAD `3a34ea309d80` for v0 and `760584ba9a6e` for v1. At that HEAD every cited line contains the quoted text. I cannot tell whether line 397's continuation, quoted below, was there at v0's HEAD. The round-1 critic re-fetched the same files and confirmed lines 46, 393–397, 547–549 and `customization.md:184`. `package.json` gives `"name": "@fission-ai/openspec"`, `"version": "1.14.0"`, `"license": "MIT"`. Quotes from `concepts.md`:
  - Specs: "**Specs** are the source of truth — they describe how your system currently behaves." (`concepts.md:46`)
  - Grammar: "`### Requirement:` | A specific behavior the system must have", "`#### Scenario:` | A concrete example of the requirement in action", with WHEN/THEN bullets (`:88-120`).
  - Deltas: `## ADDED Requirements` "Appended to main spec", `## MODIFIED Requirements` "Replaces existing requirement", `## REMOVED Requirements` "Deleted from main spec" (`:393-397`). Line 397 now continues: "removing the last requirement retires the capability and deletes its spec file, when the change declares `retire_capabilities: true`". This spec does not adopt retirement (see Out-of-scope observations).
  - Archive: "Merge deltas… Move to archive. The change folder moves to `changes/archive/` with a date prefix" (`:547-549`).
  - One correction to the request: the built-in schema is named `spec-driven`, not "default". `customization.md:184` gives `openspec schema fork spec-driven my-workflow`. Schema artifact fields are `id`, `generates`, `requires`, `template` and `instruction` (`:222-252`). `openspec/config.yaml` takes `schema:`, `context:` and `rules:` (`:32-41`).
  - `command -v openspec` → `openspec: not found`.
- **Trial apply (v3).** I wrote a Python script that applies parts A–L. It asserts that each OLD string occurs exactly once and replaces it with the NEW text quoted below. I ran it on a scratch clone of `main` (`b4d0f90`), re-copied the two prompts with the part G commands, and committed. `git diff --stat main...HEAD` → `4 files changed, 97 insertions(+), 29 deletions(-)`: `docs/spec-factory.md` 60, `prompts/02-spec-writer.md` 29, `prompts/04-planner.md` 8, `specs/build-harness.md` 29. `git diff --check main...HEAD` exits 0 with no output. Under Acceptance I quote the result of every Acceptance command, run as written, on that clone and on `main`.
- **T-0005 already applies the new FORMAT.** T-0005's criterion-1 command prints `6` on `main` and on the trial clone (Acceptance 12). The Operator steps section moves into `proposal.md` without losing its meaning (A5).

## Root cause

This is a design gap, not a defect. The design doc defines the spec only as the writer's output (§2 FORMAT) and the store only as "spec text and version" (piece 1). Neither the doc nor `specs/build-harness.md` part B/K has an artifact that outlives the ticket. Parent close (the Merge gate row; build spec H `build.js` step 2) closes the parent and writes nothing back. The roles' input lists (build spec H, `intake.js` step 2) name no artifact that describes current behaviour.

## Proposed change

The change touches four files, about 125 changed lines, as one PR. The main text sits in two places. One new Harness paragraph carries the schema. The writer and planner prompts carry the per-role format. Everything else is a one-clause consistency edit.

Constraints on the design:
- The writer stays read-only, because piece 4 gives it no write access. Its output stays one text, and the harness splits that text into the change folder at the gate.
- The writer and the critic gain one declared input source: current truth, which is every `openspec/specs/<capability>/spec.md` in the store (parts C and K). The planner, implementer and verifier keep consuming "the pinned spec", which is the same pinned version, so their composed inputs (build spec H, item 77) do not change.
- The critic, implementer and verifier prompts do not change. The sub-ticket still carries runnable commands with NEW/REGRESSION labels. "Acceptance", "Tests to change", "Risk" and "Operator steps" keep their names inside the artifacts, so every existing reference still resolves: piece 8, the Human gates row and critic rubric 2.

Every replacement is given verbatim. OLD text must match exactly once, and Acceptance checks the NEW text.

**A. `docs/spec-factory.md`, Harness section: new paragraph.** Insert the block below directly before the paragraph that starts `**Routing table.** The dispatcher`, with one blank line between them. The block is a paragraph, a table and a paragraph.
```text
**Spec store: the `spec-factory` schema.** The ticket store (piece 1) keeps specs in OpenSpec's tree (Fission-AI, MIT; layout and grammar as its `docs/concepts.md` and `docs/customization.md` give them), under a schema forked from OpenSpec's built-in `spec-driven` and named `spec-factory` (`openspec/schemas/spec-factory/schema.yaml`, selected by `openspec/config.yaml`). Current truth is `openspec/specs/<capability>/spec.md`: what each capability does now, as `### Requirement: <name>` blocks, each one SHALL or MUST sentence followed by `#### Scenario: <name>` items whose WHEN is a runnable command and THEN its expected result. A ticket's change is the folder `openspec/changes/<ticket id>/`:

| Artifact | Holds | Author |
|---|---|---|
| `proposal.md` | Problem, Evidence, Root cause, Out of scope, Open questions, Decisions, Risk, Operator steps | Spec writer |
| `design.md` | Proposed change, Tests to change | Spec writer |
| `specs/<capability>/spec.md` (delta) | Requirements under `## ADDED Requirements`, `## MODIFIED Requirements` or `## REMOVED Requirements`; its scenarios are the Acceptance items | Spec writer; the critic reviews it |
| `tasks.md` | The sub-tickets and coverage map | Planner |
| `verification.md` (the artifact the fork adds) | The NEW or REGRESSION label of each scenario and the writer's Responses; every critic round's output; at archive, every verifier result recorded per head for the parent and its sub-tickets | Spec writer (labels, Responses), critic, verifier |

`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. A delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing) writes nothing and parks the parent. Only the archive step writes current truth and `decisions.md`. The spec writer and the critic receive every current-truth spec with their input (routing table).
```
The Author column differs from the request's table in two cells:
- `design.md` is authored by the spec writer only; the request said "Spec writer / Planner". The planner's one artifact is `tasks.md`. Its OUTPUT (§4) has no design section, and the planner rules say "Don't redesign".
- `verification.md` adds the spec writer, alongside the critic and verifier. The §2 rules already make the writer label each item NEW or REGRESSION and answer each finding, so the writer authors those labels and Responses. The critic and verifier still own their rounds and results.

Roles cannot write, so "author" means the role whose output the harness copies in. The last sentence of the block is carried by part C (Receives) and part K (the compose lists).

**B. `docs/spec-factory.md`, routing rules (parking).** Two replacements:
```text
OLD: a budget kill (piece 3), and a parent-close FAILED park the ticket.
NEW: a budget kill (piece 3), a parent-close FAILED, and an archive that does not apply (Spec store) park the ticket.
OLD:   - A parent-close FAILED or SPEC-DEFECT, or a sub-ticket closed by the human, parks the parent:
NEW:   - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent:
```
The rest of that bullet does not change: the human amends the spec and re-plans, or closes the parent (Open question 4).

**C. `docs/spec-factory.md`, routing table.** Only "Receives" and "Next" cells change. No row is added or removed, and no From or STATUS cell changes (Acceptance 16).
```text
OLD: | Triage | ACCEPT | Spec writer | The ticket |
NEW: | Triage | ACCEPT | Spec writer | The ticket; current truth (Spec store), read-only |
OLD: | Critic | Spec, repo read-only; round 2+:
NEW: | Critic | Spec, repo and current truth read-only; round 2+:
OLD: one verifier run on main against the parent's full Acceptance list: VERIFIED closes the parent; FAILED or SPEC-DEFECT parks the parent in the human queue |
NEW: one verifier run on main against the parent's full Acceptance list (every scenario of its pinned delta, with its `verification.md` label): VERIFIED archives the change (Spec store), then closes the parent; FAILED, SPEC-DEFECT or an archive that does not apply parks the parent in the human queue |
```
The second OLD is in the `Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT` row, the row that feeds the critic. The doc already says "'Receives' adds to the INPUT the role prompt already declares", so the prompts' INPUT lines need no edit. The build spec's compose lists, which deliver this input, change in part K.

**D. `docs/spec-factory.md`, §2 Spec writer block.** There are two replacements, both inside the Spec writer block.

D1, the RULES bullet on inline scripts. This is one line; the lines around it stay.
```text
OLD:   Acceptance line itself, which the verifier runs verbatim on both base
NEW:   WHEN line of its scenario, which the verifier runs verbatim on both base
```
The rule now reads "give the check as an inline script in the WHEN line of its scenario, which the verifier runs verbatim on both base and PR". The rest of RULES does not change. "Acceptance criteria", "NEW" and "REGRESSION" refer to scenarios and their `verification.md` labels.

D2, FORMAT. Replace the block from the line `FORMAT` through the line `                    DISAGREE <evidence>` with the text below. The `STATUS:` and `CONFIDENCE / ESCALATIONS` lines after it stay as they are.
```text
FORMAT
One document in four parts, each opened by a line `=== <file>`. At the
spec gate the harness writes each part to that file of the change folder
openspec/changes/<ticket id>/ (schema spec-factory).
=== proposal.md
## Problem          what's wrong or missing, for whom
## Evidence         actual output, logs, metrics, repro steps
## Root cause       files and functions, if known; "unknown" is allowed
## Out of scope     what must NOT change
## Open questions   none | list
## Decisions        none | one line per design call this change makes,
                    including each answered open question
## Risk             blast radius; every protected path this will touch
## Operator steps   (optional) actions or checks on live or protected state
                    that only the operator can perform, after merge; not
                    acceptance; the human approves them at the spec gate
=== design.md
## Proposed change  lettered parts (A, B, C), specific enough to follow
## Tests to change  none | existing tests the intended change breaks, and why
=== specs/<capability>/spec.md
                    one part per capability changed; reuse a current-truth
                    capability where the behaviour already lives
## ADDED Requirements | ## MODIFIED Requirements | ## REMOVED Requirements
### Requirement: <name>   one sentence with SHALL or MUST
#### Scenario: <name>     one Acceptance item; names unique in the change
- WHEN `command`          (GIVEN lines first, if it needs a fixture)
- THEN expected result
                    MODIFIED restates the whole requirement. MODIFIED and
                    REMOVED name a requirement in current truth; behaviour
                    current truth lacks is ADDED. REMOVED gives the name
                    and a one-line reason.
=== verification.md
## Acceptance       - <scenario name> → NEW | REGRESSION; for NEW, how it
                    fails today
## Responses        (round 2+) per finding: FIXED <what changed> |
                    DISAGREE <evidence>
```
The three Operator steps lines move into the `proposal.md` part verbatim (A5), so T-0005's check still holds (Acceptance 12). Decisions is a new section (Open question 3).

**E. `docs/spec-factory.md`, §4 Planner OUTPUT.** Make three replacements, all inside the Planner block. The `OUTPUT` line to change is the one that comes after the RULES line `  siblings to re-verify, so parallel sub-tickets are not free.` and one blank line. Anchor on those three lines together, because `OUTPUT` alone occurs 8 times in the doc.
```text
OLD: OUTPUT
NEW: OUTPUT (the harness writes it to the change's tasks.md)
OLD:   Acceptance: commands + expected results
NEW:   Acceptance: the parent's scenarios it covers, each as its WHEN command,
           THEN result and verification.md label, plus any intermediate checks
           it needs, labelled NEW or REGRESSION the same way
OLD: Coverage map: parent criterion → sub-ticket ID
NEW: Coverage map: parent scenario → sub-ticket ID
```
In the file, the two continuation lines are indented 4 spaces (`    THEN result …`, `    it needs, …`). Above they are shown with 11 spaces so that they line up under `NEW:`.

**F. `docs/spec-factory.md`, Changelog.** Append one entry directly after the last numbered entry, with no blank line between them. The blank line before `Declined:` stays. The entry's number is the last entry's number plus one at merge time: 39 on `b4d0f90`, where T-0007's entry holds 38.
```text
39. Specs live in an OpenSpec tree under a forked `spec-factory` schema (Harness, Spec store): current truth per capability, one change folder per ticket (proposal, design, delta, tasks, and the factory-only `verification.md`), and a repo-level `decisions.md`. The spec writer's FORMAT is one document in those parts, and the delta's scenarios are the Acceptance items; the spec writer and the critic receive current truth; the planner's output is the change's `tasks.md`; the spec gate pins the change folder; parent close archives it (apply the deltas, move the folder, append the decisions). Roles, round limits, gates and harness pieces 1–12 are unchanged.
```

**G. Re-copy the two prompt blocks** from the edited doc. Do not hand-edit them.
- `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md > prompts/02-spec-writer.md`
- `awk '/^ROLE: Planner\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md > prompts/04-planner.md`

`prompts/03-spec-critic.md` and `prompts/07-verifier.md` are not re-copied, because their blocks do not change:
- The critic's rubric names (Tests to change, Risk, Operator steps, Acceptance) all still exist inside the artifacts.
- The verifier already runs "every acceptance command from the sub-ticket", and part E keeps the commands and labels on the sub-ticket.

**H. `specs/build-harness.md`, store listing.** This is the `State on branch \`tickets\`` paragraph under Proposed change.
```text
OLD: `tickets/`, `specs/`, `requests/`,
NEW: `tickets/`, `specs/`, `openspec/`, `decisions.md`, `requests/`,
```

**I. `specs/build-harness.md` part B.** Replace the line `Spec text \`specs/<ID>/v<N>.md\`; sub-ticket text \`specs/<ID>/subticket.md\`.` with the two paragraphs below, separated by a blank line.
```text
Spec text `specs/<ID>/v<N>.md` (every version the writer returns, with its STATUS/CONFIDENCE/ESCALATIONS trailer removed: the text above its last `STATUS:` line, as item 42 requires); sub-ticket text `specs/<ID>/subticket.md`.

**Spec store** (doc §Harness, Spec store). `factory init` creates `openspec/config.yaml` (`schema: spec-factory`), `openspec/schemas/spec-factory/schema.yaml` (the artifacts of OpenSpec's `spec-driven`, `proposal`, `specs` with `generates: specs/**/*.md`, `design` and `tasks`, plus `verification` with `generates: verification.md` and `requires: [specs]`), an empty `openspec/specs/` and an empty `decisions.md`. Pinning a version (K) splits it on its `=== <path>` lines (the path is the first token after `=== `; text before the first such line is dropped) into `openspec/changes/<ID>/<path>`. A version is **well-formed** when every path is `proposal.md`, `design.md`, `verification.md` or `specs/<capability>/spec.md` with a kebab-case capability, each at most once; every delta part has at least one `## ADDED Requirements`, `## MODIFIED Requirements` or `## REMOVED Requirements` heading, and every `### Requirement:` line sits under one of them and has a name unique within its part; and the `## Acceptance` of `verification.md` labels every `#### Scenario:` name of the delta parts exactly once, `NEW` or `REGRESSION`, and labels no other name. Any other version is malformed. `verification.md` is the writer's part plus `## Critic rounds`: per critic run of the ticket, oldest first, `round <n> · spec v<N> · <run_id> · <STATUS>` and its findings verbatim. `tasks.md` comes from `factory spec tasks`. No role writes `openspec/` or `decisions.md`, and only `factory archive` (K) writes `openspec/specs/` and `decisions.md`.
```
The stored text has no trailer, so the `verification.md` part ends at its `## Responses` section.

Then make two more edits, one in part B and one in part C.
```text
OLD (B, CLI): → `spec.version += 1`, `specs/ID/v<N>.md`;
NEW:          → `spec.version += 1`, `specs/ID/v<N>.md`; `factory spec tasks PARENT --run RUN` → writes that planner run's `output.md`, trailer removed as for spec text (above), to `openspec/changes/<PARENT>/tasks.md` (exit 2 unless RUN is a `PLANNED` planner run of PARENT);
OLD (C, events): `harness-bug`, `spec.exported`.
NEW:             `harness-bug`, `spec.exported`, `change.pinned`, `change.archived`.
```

**J. `specs/build-harness.md` part K.** Make two replacements and add one new bullet. The export to `knowledge_vault/sanitized_specs/<ID>.md` stays as it is. It exports the pinned text, which now contains all four parts, so items 48, 60 and 61 still hold.
```text
OLD: copies "Tests to change" and Risk paths into the ticket, `approvals/ID/spec-v<N>.yaml`,
NEW: copies "Tests to change" and Risk paths into the ticket, `approvals/ID/spec-v<N>.yaml`, writes the pinned version as the change folder (B; event `change.pinned`; exit 2 with nothing written when the version is malformed (B) or a delta does not apply to current truth: an ADDED requirement name already in `openspec/specs/<capability>/spec.md`, or a MODIFIED or REMOVED name not in it),
OLD: re-pins `approved_version`, writes `approvals/<parent>/spec-v<N+1>.yaml`,
NEW: re-pins `approved_version` and rewrites the change folder as `approve-spec` does (`## Critic rounds` kept), writes `approvals/<parent>/spec-v<N+1>.yaml`,
```
Add a new last bullet to part K. Put it directly after the `factory resolve` bullet, with no blank line between them, and keep the blank line before `### L. Verifier as gate runner (piece 11)`.
```text
- `factory archive ID` (harness identity; `build.js` runs it on the parent-close VERIFIED, H): (1) appends `## Verifier results` to `openspec/changes/<ID>/verification.md`, one line per verifier row in `results/` for the parent's and its sub-tickets' heads, oldest first, `<head> · <ticket> · <STATUS> · <run_id>`; (2) applies every delta to `openspec/specs/<capability>/spec.md` (created with `# <capability>` and `## Requirements` when absent): ADDED appends the requirement block, MODIFIED replaces the block whose `### Requirement:` name matches, REMOVED deletes it; (3) moves `openspec/changes/<ID>` to `openspec/changes/archive/<YYYY-MM-DD>-<ID>` (UTC date); (4) appends `<YYYY-MM-DD> <ID> <line>` to `decisions.md` per line of `proposal.md`'s `## Decisions` other than `none`. One commit, event `change.archived`. A delta that does not apply → exit 2, nothing written.
```

**K. `specs/build-harness.md` part H** (`intake.js` and `build.js`). Five replacements. The first two are in `intake.js` step 2. They add current truth to the writer's and the critic's "with input =" lists, which are the sources `factory run compose` (B) is defined to read.
```text
OLD: with input = ticket + request (+ on round ≥ 2:
NEW: with input = ticket + request + current truth (every `openspec/specs/<capability>/spec.md` in the store, in path order, each one of `input_sources:`) (+ on round ≥ 2:
OLD: with input = spec vN (+ round ≥ 2:
NEW: with input = spec vN + current truth (as for the writer) (+ round ≥ 2:
OLD: `PLANNED` → clerk `subticket add` per sub-ticket
NEW: `PLANNED` → clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add` per sub-ticket
OLD: the pinned parent spec (its full `## Acceptance` list)
NEW: the pinned parent spec (every delta scenario with its `## Acceptance` label)
OLD: `VERIFIED` → `closed`;
NEW: `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`;
```
How this fits the existing build spec:
- `run compose` itself does not change. It still reads exactly the H lists, from the store, and the `openspec/` tree is on `tickets`, which is the store. Current truth therefore reaches the writer and the critic without their read-only clone of `main`.
- Item 42 still holds as written. `factory init` leaves `openspec/specs/` empty, so in case `accept-approve` current truth adds no source, and the writer's and critic's `input_sources` are unchanged. The new item 89 (part L) covers a non-empty current truth.
- Items 37 and 86 assert only that `input_sources` "lists" a source, so they are unaffected.
- The parent-close run still reads `specs/<ID>/v<N>.md`, which holds every part, so item 77 is unchanged.

**L. `specs/build-harness.md` Acceptance: three new items.** Insert a heading `### Spec store [S3, S4]` and the three items directly before `### Gates (every seam)`, with a blank line around the heading and one before `### Gates`. Number the items one, two and three past the highest Acceptance item number at merge time. On `b4d0f90` they are 87, 88 and 89, because T-0003 holds 86. If the numbers move, update the cross-references "item 87's" (in 88) and "item 88" (in 89) to match.
```text
87. ⟨bare⟩ **Change folder at the gate:** `specs/T-0001/v1.md` in the four-part FORMAT of doc §2, its delta part `=== specs/status-parser/spec.md` holding `## ADDED Requirements` with `### Requirement: trailer-read` and one scenario: `AS daniel factory approve-spec T-0001 --version 1` → `openspec/changes/T-0001/` holds `proposal.md`, `design.md`, `specs/status-parser/spec.md` and `verification.md`, each equal to its part of `v1.md` except that `verification.md` also ends with `## Critic rounds`, one entry per critic run of T-0001; `change.pinned` logged; `openspec/specs/` and `decisions.md` unchanged. A `v2.md` whose delta has `## MODIFIED Requirements` with `### Requirement: no-such-req`: `AS daniel factory approve-spec T-0001 --version 2` → exit 2, stderr names `no-such-req`, `approved_version: 1`, no `approvals/T-0001/spec-v2.yaml` [NEW]
88. ⟨wf⟩⟨bare⟩ **Archive at parent close:** case `plan-three` on item 87's T-0001, after item 77's VERIFIED: `openspec/changes/T-0001` is gone; `openspec/changes/archive/<date>-T-0001/` holds item 87's four files and `tasks.md`, equal to the planner run's `output.md` above its last `STATUS:` line; its `verification.md` ends with `## Verifier results`, one line per verifier row of `T-0001.1`–`.3` and `T-0001`; `openspec/specs/status-parser/spec.md` contains `### Requirement: trailer-read` and its scenario; `decisions.md` gained one `<date> T-0001 …` line per `## Decisions` line of the proposal; in the log `change.archived` precedes the transition to `closed`. A second parent, pinned before T-0001 archived with a delta that also ADDs `trailer-read`, reaching its parent-close VERIFIED → `status: parked`, `parked.reason` starts `archive:`, and `openspec/specs/`, `decisions.md` and its change folder are unchanged [NEW]
89. ⟨wf⟩⟨bare⟩ **Current truth in writer and critic input:** after item 88, `factory request new --file r.md` (a new ticket `T-000k`) and case `accept-approve` run on `T-000k` → its spec writer run's and its critic run's `input.md` each contain `### Requirement: trailer-read`, and each of those runs' `meta.yaml` `input_sources` lists `openspec/specs/status-parser/spec.md` besides the sources item 42 names for that role. Item 42 holds as written because `openspec/specs/` is empty after `factory init` [NEW]
```
In the line `Items needing the bare repo: …`, append the three new numbers after `84`: `…, 83, 84, 87, 88, 89.`.

**M. Nothing else changes.** In particular:
- `specs/build-harness.md` keeps its own old-shape sections. It is not migrated (A4).
- The plan files under `plans/` are not changed.

## Acceptance

Run every command from `~/dev/spec-factory` with bash, on the PR branch, with `main` as the base. "Today" means `main` at `b4d0f90`, whose documents are the same as at `4cd8d12`. I ran each command, as written, on that commit and on the trial clone with A–L applied. Both results are quoted.

Four commands contain a backtick: 3, 6, 10 and 11. They are delimited by double backticks. The command is the text between them, without the one space of padding at each end.

1. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | grep '^=== ' | tr '\n' ';'` → `=== proposal.md;=== design.md;=== specs/<capability>/spec.md;=== verification.md;`. The writer's FORMAT is one document in the four parts, in that order. [NEW: prints nothing today, because the FORMAT has no parts]
2. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | awk '/^FORMAT$/{f=1} /^STATUS:/{f=0} f&&/^=== /{part=$2} f&&/^## /{s=$0; sub(/^## /,"",s); sub(/  +.*/,"",s); print part ":" s}' | tr '\n' ';'` → `proposal.md:Problem;proposal.md:Evidence;proposal.md:Root cause;proposal.md:Out of scope;proposal.md:Open questions;proposal.md:Decisions;proposal.md:Risk;proposal.md:Operator steps;design.md:Proposed change;design.md:Tests to change;specs/<capability>/spec.md:ADDED Requirements | ## MODIFIED Requirements | ## REMOVED Requirements;verification.md:Acceptance;verification.md:Responses;`. Each section sits in the artifact the operator's mapping gives it, and Operator steps is in `proposal.md` (A5). A section that is dropped or placed in the wrong part changes this string. [NEW: today prints `:Problem;:Evidence;:Root cause;:Proposed change;:Acceptance;:Tests to change;:Out of scope;:Open questions;:Risk;:Operator steps;:Responses;`, with no section belonging to a part]
3. `` printf '%s %s\n' "$(awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | grep -o -e '^### Requirement: <name>' -e '^#### Scenario: <name>' -e '^- WHEN `command`' -e '^- THEN expected result' -e 'SHALL or MUST' -e 'MODIFIED restates the whole requirement' -e 'WHEN line of its scenario, which the verifier runs verbatim' | sort -u | wc -l | tr -d ' ')" "$(awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | grep -c 'Acceptance line itself')" `` → `7 0`. The delta part states the requirement and scenario grammar, says a scenario's WHEN is a command, and says a MODIFIED requirement is restated whole. The RULES put the inline script in the scenario's WHEN line, and the stale "Acceptance line" wording is gone. [NEW: prints `0 1` today]
4. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | diff - prompts/02-spec-writer.md && grep -c '^=== ' prompts/02-spec-writer.md` → no diff output, then `4`, exit 0. The writer prompt is a verbatim re-copy that includes the parts. [NEW: the diff is clean today, but grep prints `0` and exits 1]
5. `awk '/^ROLE: Planner\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | diff - prompts/04-planner.md && tr -s ' \n' '  ' < prompts/04-planner.md | grep -o -e "OUTPUT (the harness writes it to the change's tasks.md)" -e 'Coverage map: parent scenario → sub-ticket ID' -e 'THEN result and verification.md label' | sort -u | wc -l | tr -d ' '` → no diff output, then `3`. The planner prompt is a verbatim re-copy. Its output is the change's `tasks.md`, its sub-tickets carry scenarios with labels, and its coverage map is keyed by scenario. [NEW: today the diff is clean and the count is `0`]
6. `` awk '/^## Harness: functional pieces/{f=1} /^## Human gates/{f=0} f' docs/spec-factory.md | grep -o -F -e 'openspec/specs/<capability>/spec.md' -e 'openspec/changes/<ticket id>/' -e '`verification.md`' -e '`decisions.md`' -e '`spec-driven`' -e 'openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/' -e 'ADDED appends the requirement' -e 'MODIFIED replaces the requirement of that name whole' -e 'REMOVED deletes it' -e 'Only the archive step writes current truth' | sort -u | wc -l | tr -d ' ' `` → `10`. The Harness section defines the layout, names the fork's base schema, gives the three delta operations and the archive path, and says only archive writes current truth. [NEW: prints `0` today]
7. `grep '^| Merge gate | CI green' docs/spec-factory.md | grep -o -e 'VERIFIED archives the change' -e 'then closes the parent' -e 'an archive that does not apply parks the parent' | wc -l | tr -d ' '` → `3`. Parent close archives the change before the parent closes, and a failed archive parks the parent. [NEW: prints `0` today; the row says "VERIFIED closes the parent"]
8. `grep -c -F -e 'a parent-close FAILED, and an archive that does not apply (Spec store) park the ticket.' -e '  - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent:' docs/spec-factory.md` → `2`. An archive refusal is a parking state with the parent-park resolution. [NEW: prints `0` today]
9. `grep -E '^\| (Triage \| ACCEPT|Spec writer \| READY-FOR-CRITIC)' docs/spec-factory.md | grep -c 'current truth'` → `2`. The routing table gives the writer and the critic current truth, read-only. [NEW: prints `0` today]
10. `` awk '/^## Changelog/{f=1} /^## Appendix/{f=0} f' docs/spec-factory.md | grep '^[0-9][0-9]*\. ' | awk -F. '$1!=NR{gap=1} {last=$0} END{print (gap?"GAP":"CONTIGUOUS"), (last ~ /spec-factory` schema/ && last ~ /decisions/ && last ~ /archive/ ? "LAST-IS-SPEC-STORE" : "LAST-IS-OTHER")}' `` → `CONTIGUOUS LAST-IS-SPEC-STORE`, whichever number the entry gets. [NEW: prints `CONTIGUOUS LAST-IS-OTHER` today]
11. `` printf '%s %s %s\n' "$(grep -o -F -e '**Spec store** (doc §Harness, Spec store)' -e 'plus `verification` with `generates: verification.md`' -e 'A version is **well-formed** when' -e 'with its STATUS/CONFIDENCE/ESCALATIONS trailer removed' -e '- `factory archive ID`' -e 'clerk `factory archive PARENT` (K), then `closed`' -e 'clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add`' -e 'with input = ticket + request + current truth (every `openspec/specs/<capability>/spec.md` in the store' -e 'with input = spec vN + current truth (as for the writer)' specs/build-harness.md | sort -u | wc -l | tr -d ' ')" "$(grep -cE '^[0-9]+\. (⟨[a-z]+⟩)+ \*\*(Change folder at the gate|Archive at parent close|Current truth in writer and critic input):\*\*' specs/build-harness.md)" "$(grep -c -F '`VERIFIED` → `closed`;' specs/build-harness.md)" `` → `9 3 0`. The first number counts nine build-spec texts:
    - the store layout, with the forked schema's `verification` artifact;
    - the well-formedness rule;
    - spec text stored with its trailer removed;
    - the archive command;
    - `build.js` writing `tasks.md` at PLANNED and archiving at VERIFIED;
    - the writer's and critic's compose lists including current truth.

    The second number counts the three new acceptance items. The third shows that a VERIFIED parent no longer goes straight to `closed`. Leaving the compose lists unchanged makes the first number `7`. [NEW: prints `0 0 1` today]
12. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | awk '/^## Operator steps /{f=1;print;next} f&&/^                    [^ ]/{print;next} {f=0}' | tr -s ' \n' '  ' | grep -o -e '(optional)' -e 'live or protected state' -e 'only the operator' -e 'after merge' -e 'not acceptance' -e 'at the spec gate' | sort -u | wc -l | tr -d ' '` → `6`. This is T-0005's criterion 1: Operator steps keeps its full meaning after the move. [REGRESSION: `6` today and on the trial clone]
13. `for rf in 'Triage:01-triage' 'Spec writer:02-spec-writer' 'Spec critic:03-spec-critic' 'Planner:04-planner' 'Implementer:05-implementer' 'Code reviewer:06-code-reviewer' 'Verifier:07-verifier' 'Retro:08-retro'; do r=${rf%%:*}; f=${rf##*:}; awk "/^ROLE: $r\\./{p=1} p{print} p&&/^CONFIDENCE \\/ ESCALATIONS\$/{exit}" docs/spec-factory.md | cmp -s - prompts/$f.md || echo "DIFF $f"; done` → no output. Every role prompt file is still a verbatim copy of its block. [REGRESSION]
14. `git diff -U0 main...HEAD -- prompts/00-preamble.md prompts/01-triage.md prompts/03-spec-critic.md prompts/05-implementer.md prompts/06-code-reviewer.md prompts/07-verifier.md prompts/08-retro.md | wc -l | tr -d ' '` → `0`. No other prompt changes. [REGRESSION]
15. `diff <(git show main:docs/spec-factory.md | grep '^STATUS: ') <(grep '^STATUS: ' docs/spec-factory.md)` → no output. No role's STATUS vocabulary changes. [REGRESSION]
16. `diff <(git show main:docs/spec-factory.md | awk '/^\| From \| STATUS \|/,/^Any STATUS not in this table/' | awk -F' [|] ' '{print $1 " | " $2}') <(awk '/^\| From \| STATUS \|/,/^Any STATUS not in this table/' docs/spec-factory.md | awk -F' [|] ' '{print $1 " | " $2}')` → no output. Routing has the same rows, in the same order, with the same From and STATUS cells. [REGRESSION]
17. `git show main:specs/build-harness.md | awk '/^## Acceptance/{f=1} /^## Tests to change/{f=0} f' | grep -E '^[0-9]+\. ' | grep -vxF -f <(awk '/^## Acceptance/{f=1} /^## Tests to change/{f=0} f' specs/build-harness.md)` → no output, exit 1. Every existing build-spec acceptance item (86 today) survives verbatim, item 42 included. [REGRESSION]
18. `awk '/^## Acceptance/{f=1} /^## Tests to change/{f=0} f' specs/build-harness.md | grep -oE '^[0-9]+\. ' | sort -n | uniq -d` → no output. No acceptance item number is duplicated. [REGRESSION]
19. `git diff --name-only main...HEAD | grep -v -x -e docs/spec-factory.md -e specs/build-harness.md -e prompts/02-spec-writer.md -e prompts/04-planner.md` → no output, exit 1. No other path is touched, including `plans/`, `README.md`, the approved specs and `intake/**`. [REGRESSION]
20. `git diff --check main...HEAD` → no output, exit 0 [REGRESSION]

Results captured, with each command run as written:
- `main` (`b4d0f90`), items 1–20: (empty); the `:Problem;…` string; `0 1`; clean diff, then `0` (exit 1); clean diff, then `0`; `0`; `0`; `0`; `0`; `CONTIGUOUS LAST-IS-OTHER`; `0 0 1`; `6`; empty output for 13; `0`; empty for 15, 16, 17 (exit 1), 18 and 19 (exit 1); clean, exit 0, for 20.
- Trial clone, items 1–20: the four parts; the mapped string; `7 0`; clean diff, then `4` (exit 0); clean diff, then `3`; `10`; `3`; `2`; `2`; `CONTIGUOUS LAST-IS-SPEC-STORE`; `9 3 0`; `6`; empty output for 13; `0`; empty for 15, 16, 17 (exit 1), 18 and 19 (exit 1); clean, exit 0, for 20.

Wrong fixes these items catch:
- A section left in the wrong part fails 2.
- A prompt edited by hand instead of re-copied fails 4, 5 and 13.
- A parent that closes without archiving fails 7 and 11.
- Current truth declared in the doc but not added to the compose lists fails 11.

## Tests to change

none. This repo holds documents and has no test files. Build-spec items 1–86 are kept verbatim (Acceptance 17).

## Out of scope

- **These must not change:**
  - the critic, implementer, reviewer, verifier, triage and retro prompt blocks and their `prompts/` copies;
  - the preamble;
  - the From and STATUS cells of every routing row, the round limits, and the human gates table;
  - harness pieces 1–12 as table rows;
  - the `run compose` mechanism (build spec B). Only the writer's and the critic's declared source lists in H gain current truth.
- **No migration:** no existing spec is rewritten into the new shape. That covers `intake/state/specs/T-0001..T-0007` (A4) and `specs/build-harness.md`. The green-side pilot specs (SPEC-21, SPEC-27) and green's ROADMAP register are Nanobot-side follow-ups (A1).
- **Paths not touched:** `plans/` (including `plans/build-harness.md`), `README.md`, and `intake/**`, apart from this output file.
- **No new export target:** `knowledge_vault/sanitized_specs/<ID>.md` keeps exporting the pinned text.
- **No new tooling:** no `openspec` CLI call, install or dependency (Open question 1), and no `openspec/` tree created in this repo. The tree is described for the store; the harness's `factory init` creates it, which is green-side build work.
- **No new routing STATUS or ticket state:** an archive refusal parks the parent with a reason, as other parent parks do.

## Open questions

none open. Answer 2 answered the four questions of v0 by taking each recommended default. The operator can overturn any of them at the spec gate; question 2 is flagged as the one most worth a second look. Every part above is written against these answers.

1. (A3) Nothing depends on the `openspec` CLI at runtime. Archive and the gate's apply check are the harness's own code (parts I and J). The tree stays readable by OpenSpec tooling, but reading it with that tooling is an optional manual check, never a gate. Reasons:
   - `openspec` is not installed (`command -v openspec` → not found).
   - It is a Node package (`@fission-ai/openspec` 1.14.0), and the harness is Python.
   - The implementer rules say "No new dependencies without escalation".
2. The `openspec/` tree lives in the ticket store on the `tickets` branch (parts H and I). The writer and the critic receive current truth through the routing table (part C) and the compose lists (part K). The alternative not taken was the target repo's `main`. That would need a new kind of no-sub-ticket PR through the merge gate, both for the gate's change folder and for each archive.
3. Decision-log lines come from a new `## Decisions` section in `proposal.md`. The spec writer writes it, it is approved at the spec gate, and archive appends its lines verbatim (parts A, D and J).
4. An archive refusal reuses the existing parent-park resolution: amend the spec and re-plan, or close (part B). There is no new resolution edge.

## Risk

**Blast radius.** The diff touches four document files, about 125 changed lines. Every future spec writer and planner run reads the changed blocks, so a wording mistake shapes every later spec. Criteria 1–5 pin the structure, and criterion 12 shows that T-0005's meaning survives. Once built, every writer and critic input grows by the size of current truth. That size is zero at `factory init` and grows by one archived delta per closed parent. The build spec sets no cap. Piece 3's per-run budget is the only bound, and it is recorded but not enforced in v0 (E7).

**Concurrent archives.** Two parents that both MODIFY the same requirement can both pass their gates. The second archive then replaces the first one's version whole. OpenSpec's model has the same property. Nothing here detects it; the critic and the human gate are the check.

**Protected and guardrail paths, declared for the gate:**
- generated (protected): `prompts/02-spec-writer.md` and `prompts/04-planner.md`. They change only by re-copying (part G; criteria 4, 5 and 13).
- guardrail ("these prompts"): the §2 and §4 prompt blocks in `docs/spec-factory.md`, and the same two `prompts/` files. These need a human approval record on the PR (piece 8).
- infra (`intake/**`): not touched, beyond this output file.
- `~/dev/nanobot-upstream/**`: only read, with `grep` and `sed` on `factory/`.
- `~/.nanobot/**`: not read.

**Merge order:**
- T-0005 has merged (`ac66b2c`), and part D carries its Operator steps lines verbatim.
- T-0007 has merged (`b9379ec`). Part A inserts before the Routing table paragraph, which keeps T-0007's sentence "Both follow the role-context block (above)." No OLD text here overlaps T-0007's lines. Part K edits the H input lists, and T-0007 edited B's `run compose` bullet and item 42; Acceptance 17 keeps item 42 as it is on `main`. The Changelog entry is therefore 39.
- T-0009 (request `issues/09_run_id_allocation.md`) names build-spec part B's `factory run start` bullet and part I. This change edits neither, so either merge order works textually.
- T-0003 took build-spec item 86, which is why part L numbers its items past the highest number at merge time (87–89 on `b4d0f90`).

**Follow-up, not acceptance.** The `plans/build-harness.md` coverage map does not list the new build-spec items, just as it does not list T-0003's item 86. Covering them needs a re-plan, outside this ticket.

## Responses

Critic round 1 (on v2):

1. [BLOCKING] Part C/K: current truth is declared but never composed. **FIXED.**
   - Part K now has two more replacements in build-spec H `intake.js` step 2. The writer's input becomes "ticket + request + current truth (every `openspec/specs/<capability>/spec.md` in the store, in path order, each one of `input_sources:`)", and the critic's becomes "spec vN + current truth (as for the writer)".
   - The v2 sentence "`run compose` and its `input_sources` do not change" is gone. Part K now explains why `compose` itself needs no edit: it reads the H lists from the store, and `openspec/` is on `tickets`.
   - Part K also explains why item 42 still holds: `factory init` leaves `openspec/specs/` empty.
   - New build-spec item 89 checks that a non-empty current truth reaches both roles' `input.md` and `input_sources`.
   - Acceptance 11 now also matches both compose texts and counts three items: `9 3 0`. Without the K edits the first number is `7`.
   - Part A's last sentence now reads "receive every current-truth spec with their input", and Out of scope says that the mechanism stays and only the lists change.
2. [SHOULD-FIX] Part I: "verbatim" contradicts the stored, trailer-less text. **FIXED.**
   - Part I now says "with its STATUS/CONFIDENCE/ESCALATIONS trailer removed: the text above its last `STATUS:` line, as item 42 requires". The reference harness's `strip_trailer` does exactly that (see Evidence).
   - `factory spec tasks` writes the planner output "trailer removed as for spec text".
   - Item 88's `tasks.md` is now "equal to the planner run's `output.md` above its last `STATUS:` line".
   - A note after the part I block says the `verification.md` part therefore ends at `## Responses`.
3. [NIT] Part A: two Author cells deviate from the request, not one. **FIXED.** The text after the table now names both: `design.md` drops the planner, and `verification.md` adds the spec writer. Each comes with its reason.
4. [NIT] Part J: "malformed" is undefined. **FIXED.**
   - Part I now defines a **well-formed** version: the path rule, each path at most once, a delta heading in every delta part, every `### Requirement:` under a heading and with a name unique in its part, and exactly one NEW/REGRESSION label per scenario name with no stray labels. Anything else is malformed.
   - Part J's refusal says "malformed (B)".
   - Acceptance 11 matches `A version is **well-formed** when`.
5. [NIT] Part D: the stale RULES phrase "inline script in the Acceptance line". **FIXED.**
   - New replacement D1 changes the RULES line to "WHEN line of its scenario, which the verifier runs verbatim on both base".
   - Acceptance 3 now checks that the new phrase is present and that "Acceptance line itself" is gone: `7 0`, today `0 1`.
   - The re-copy is covered by Acceptance 4 and 13.

Out-of-scope observations:
- `README.md` describes `specs/<ticket>.md` as "a spec: the Spec writer's output". That stays true for this design repo's own files, which are not migrated (A4). If the operator wants this repo to use the new shape for new specs, that needs a separate ticket.
- The request says "OpenSpec's default schema". The built-in schema is named `spec-driven` (`customization.md:184`), and part A uses that name.
- OpenSpec now lets a change retire a capability when its last requirement is REMOVED (`retire_capabilities: true`, `concepts.md:397`). Part J's archive deletes the requirement and leaves a capability file with no requirements. Whether the factory adopts retirement is a later design call, not taken here.
- From the critic: the reference harness already stores the planner's output as `plans/<ID>.md` via `factory plan add`, which the build spec does not mention. Part I's `factory spec tasks` would make a second copy. That is build-spec/reference drift, not this ticket's change. Whoever builds the spec store should keep one of the two.
- From the critic: the spec-approval row of the Human gates table does not name the `## Decisions` lines among what the human approves. The gate approves the whole pinned version, Decisions included, so this is wording only. It is left unchanged because Out of scope keeps the Human gates table.

## Your prior findings (round 1)

Critic, round 1 (spec v2; v0/v1 went NEEDS-HUMAN, no earlier critic run).

What I checked myself:
- `~/dev/spec-factory` `main` is at `b4d0f90`; `git diff --stat 4cd8d12 HEAD -- docs specs prompts README.md plans` is empty, so "today" = `4cd8d12` still holds.
- Every OLD anchor in parts A–L (22 strings) matches exactly once on `main` (`grep -c -F`).
- I applied parts A–L with my own script to a scratch clone at `4cd8d12`, re-copied the two prompts per part G, and committed: `4 files changed, 93 insertions(+), 26 deletions(-)` (doc 58, writer prompt 27, planner prompt 8, build spec 26), `git diff --check` clean. I ran all 20 Acceptance commands on the clone before and after. Before: 1 prints nothing, 2 prints the `:Problem;…` string, 3–9 print `0`, 10 `CONTIGUOUS LAST-IS-OTHER`, 11 `0 0 1`, 12 `6`, 13–19 empty, 20 clean. After: the four parts; the mapped string; `6`; clean + `4`; clean + `3`; `10`; `3`; `2`; `2`; `CONTIGUOUS LAST-IS-SPEC-STORE`; `5 2 0`; `6`; 13–19 empty; 20 clean. Identical to the spec's quoted results.
- OpenSpec quotes: fetched `docs/concepts.md` and `docs/customization.md` from `raw.githubusercontent.com/Fission-AI/OpenSpec/main`; lines 46, 393–397, 547–549 and `customization.md:184` contain the quoted text.
- `grep -rniE openspec docs specs plans prompts README.md | wc -l` → `0`; same for `~/dev/nanobot-upstream/factory` → `0`.
- Operator answers read from `intake/state/requests/T-0008.md` (`## Answer 1`, `## Answer 2`); the spec's A1/A3/A4/A5 and the four defaults match them.

Findings:

[BLOCKING] 5, 6 — Part C (routing-table Receives) together with part K ("`run compose` and its `input_sources` do not change")
Problem: The design doc will say the spec writer and critic receive current truth, but the build spec's compose lists, which are what delivers a role's input, are left unchanged, so the built harness never gives either role current truth and the FORMAT's "reuse a current-truth capability" / "MODIFIED and REMOVED name a requirement in current truth" cannot be followed.
Evidence: `specs/build-harness.md` part B, `factory run compose`: "writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares … the 'with input =' lists in H"; H intake.js step 2: writer input = "ticket + request (+ round ≥ 2 …)", critic input = "spec vN (+ round ≥ 2 …)", which today mirror the Receives cells part C edits; doc Harness: "composing each role's input from *only* its declared sources"; piece 3: "only its declared inputs". Part A's last sentence ("The spec writer and the critic read current truth (routing table)") has no mechanism behind it once K says compose does not change. The `openspec/` tree lives on `tickets` (Q2), which the roles' read-only clone of `main` does not contain.
Suggested fix: In part K, also edit H's intake.js step 2 so the writer's and the critic's "with input =" lists include current truth (every `openspec/specs/<capability>/spec.md` present, recorded in `input_sources:`), and state that item 42 still holds because `openspec/specs/` is empty in case `accept-approve` (fresh `factory init`); add a check for the new compose text to Acceptance 11.

[SHOULD-FIX] 1, 5 — Part I, first paragraph: "Spec text `specs/<ID>/v<N>.md` (every version the writer returns, verbatim)"
Problem: "verbatim" contradicts the build spec and the as-built harness, which store the writer's output with its STATUS/CONFIDENCE/ESCALATIONS trailer stripped, and the spec is silent on whether the split (part I) and `tasks.md` (part I, `factory spec tasks`; item 88 "equal to the planner run's `output.md`") carry a trailer.
Evidence: Build-spec item 42 (kept verbatim by Acceptance 17): the critic's input, composed from `specs/T-0001/v1.md` alone, "contains neither the triage output nor the writer's `CONFIDENCE:` line", so `v1.md` has no trailer. Reference harness `factory/cli.py` `_text_from` (used by `spec add --from-run` and `plan add`) returns `status.strip_trailer(output.md)`.
Suggested fix: Replace "verbatim" with "trailer stripped, as `spec add` stores it", and define `tasks.md` the same way (the planner run's output with its trailer stripped) in part I and item 88.

[NIT] 4 — Part A, paragraph after the table: "The Author column follows the operator's table, with one addition."
Problem: Two cells differ from the request's table, not one: `design.md` drops "/ Planner" and `verification.md` adds the spec writer; the first is undeclared.
Evidence: `issues/08_openspec_schema.md` table rows `design.md` → "Spec writer / Planner", `verification.md` → "Critic, Verifier".
Suggested fix: Say both deviations in that sentence (the planner's only artifact is `tasks.md`).

[NIT] 6 — Part J, `approve-spec`: "exit 2 with nothing written when a part is malformed"
Problem: "Malformed" is defined only for an unknown `=== <path>` (part I); a delta part with no `## ADDED|MODIFIED|REMOVED Requirements` heading, a block without a `### Requirement:` name, or a scenario with no label in `verification.md` is left to the implementer.
Evidence: Parts I and J text; the archive step (J, step 2) needs named requirement blocks to apply MODIFIED/REMOVED.
Suggested fix: One clause in I listing what a well-formed part is (the path rule, a delta heading per part, a named requirement per block, one `## Acceptance` label per scenario name), and J's "malformed" points to it.

[NIT] 6 — Part D, the unchanged RULES above FORMAT: "give the check as an inline script in the Acceptance line itself"
Problem: After the change there is no "Acceptance line" holding a command; the command is the scenario's WHEN line, so the writer prompt carries a stale phrase.
Evidence: `docs/spec-factory.md` §2 RULES (lines 19–26 of the writer block) vs. the new FORMAT.
Suggested fix: Either change that phrase to "in the scenario's WHEN line itself" (and let Acceptance 2–4 cover the re-copy) or say in the spec that the stale wording is accepted.

Rubric items with no finding: 2 (all NEW items fail today for the stated reason and pass after; 12 holds on both; 4/5/13 catch a hand-edited prompt; 2 catches a misplaced section), 3 (one PR, ~120 lines, out-of-scope list sensible, Tests to change none is correct for a documents repo), T-0009 overlap claim checked (it names B's `run start` bullet and build-spec part I; this spec edits neither).

Out-of-scope observations:
- The reference harness already stores the planner's output as `plans/<ID>.md` via `factory plan add` (ticket key `plan:`, seen in `intake/state/tickets/T-0008.yaml`), which the build spec does not mention (`grep -F 'plans/' specs/build-harness.md` → nothing). `factory spec tasks` (part I) would be a second copy of the same text. Build-spec/reference drift, not this ticket's defect; whoever builds the spec store should reuse one of them.
- The spec-approval row of the Human gates table does not name the new `## Decisions` lines among what the human approves; Answer 2 Q3 says they are approved at the gate. The whole pinned version is what the gate approves, so this is wording, not behaviour.

Prior findings: none (round 1).

STATUS: REVISE
CONFIDENCE: high — every anchor and all 20 commands reproduced on my own clone; the BLOCKING finding rests on quoted build-spec text (part B compose, H input lists) that the spec leaves unchanged.
ESCALATIONS: none

## Previous spec version (v2)

## Problem

The factory's spec is shaped like a change: it says what a ticket will do and how to check it. Nothing in the store says what a capability does now. After a ticket ships, a later writer, critic or operator who wants current behaviour has to replay every spec that ever touched it. This affects every reader downstream of the spec gate, and the gap grows with each merged ticket.

The operator adopted OpenSpec's storage model and lifecycle as a forked `spec-factory` schema, with layout (a) (Answer 1). That means:
- current truth per capability;
- one change folder per ticket, holding proposal, design, a delta, tasks, and a factory-only `verification.md`;
- the spec gate pins the delta;
- parent close becomes archive;
- a repo-level `decisions.md`.

Roles, round limits, gates and harness pieces 1–12 stay. The scope is limited to `docs/spec-factory.md`, `specs/build-harness.md`, the re-copied `prompts/` files and the Changelog. Green-side migration is out (A1), and specs T-0001..T-0007 are not migrated (A4).

## Evidence

Checkout: `~/dev/spec-factory` `main` at `4cd8d12`. Spec v0 (NEEDS-HUMAN) was written against `366d469`. Since then T-0007 merged (`b9379ec`), and `d858f9f` (T-0006 fix, `plans/` only) and intake/issues commits landed. `git diff --stat 366d469 4cd8d12 -- docs specs prompts` → `docs/spec-factory.md` 5 lines, `specs/build-harness.md` 6 lines, no prompt. I re-checked every OLD anchor below on `4cd8d12`: each matches exactly once. Every edit is anchored on text, never on a line number.

- **No current-truth layer exists.**
  - `grep -rniE 'openspec' docs specs plans prompts README.md | wc -l` → `0`.
  - `grep -rliE 'openspec|decisions\.md' ~/dev/nanobot-upstream/factory | wc -l` → `0`. No reference-harness fix exists to verify against, so every acceptance item below is checked against the documents.
- **Where the spec format is defined today** (text on `4cd8d12`, unchanged since `366d469`):
  - §2 FORMAT is one flat list: Problem, Evidence, Root cause, Proposed change, Acceptance, Tests to change, Out of scope, Open questions, Risk, Operator steps (T-0005, merged as `ac66b2c`), Responses.
  - The §4 Planner OUTPUT has `  Acceptance: commands + expected results` and `Coverage map: parent criterion → sub-ticket ID`.
  - The Merge gate routing row says "VERIFIED closes the parent; FAILED or SPEC-DEFECT parks the parent in the human queue".
  - `specs/build-harness.md` part B says "Spec text `specs/<ID>/v<N>.md`; sub-ticket text `specs/<ID>/subticket.md`."
  - Part H `build.js` step 2 has "`VERIFIED` → `closed`;".
  - Part K `approve-spec` exports the pinned text to `knowledge_vault/sanitized_specs/<ID>.md`.
- **OpenSpec facts, checked rather than taken from the request.** I downloaded `README.md`, `docs/concepts.md` and `docs/customization.md` from `raw.githubusercontent.com/Fission-AI/OpenSpec/main` for v0, and re-fetched `concepts.md`, `customization.md` and `package.json` for v1. `git ls-remote` gave repo HEAD `3a34ea309d80` for v0 and `760584ba9a6e` today; at that HEAD every cited line still contains the quoted text (I cannot tell whether line 397's continuation, quoted below, was there at v0's HEAD). `package.json` gives `"name": "@fission-ai/openspec"`, `"version": "1.14.0"`, `"license": "MIT"`. Quotes from `concepts.md`:
  - Specs: "**Specs** are the source of truth — they describe how your system currently behaves." (`concepts.md:46`)
  - Grammar: "`### Requirement:` | A specific behavior the system must have", "`#### Scenario:` | A concrete example of the requirement in action", with WHEN/THEN bullets (`:88-120`).
  - Deltas: `## ADDED Requirements` "Appended to main spec", `## MODIFIED Requirements` "Replaces existing requirement", `## REMOVED Requirements` "Deleted from main spec" (`:393-397`). Today's line 397 continues: "removing the last requirement retires the capability and deletes its spec file, when the change declares `retire_capabilities: true`" (a per-change `.openspec.yaml` field, `:193`). This spec does not adopt retirement; see Out-of-scope observations.
  - Archive: "Merge deltas… Move to archive. The change folder moves to `changes/archive/` with a date prefix" (`:547-549`).
  - One correction to the request: the built-in schema is named `spec-driven`, not "default". `customization.md:184` gives `openspec schema fork spec-driven my-workflow`, which "copies the entire `spec-driven` schema to `openspec/schemas/my-workflow/`". Schema artifact fields are `id`, `generates`, `requires`, `template` and `instruction` (`:222-252`), and `openspec/config.yaml` takes `schema:`, `context:` and `rules:` (`:32-41`).
  - `command -v openspec` → `openspec: not found`.
- **Trial apply.** I applied parts A–M below with a script to a scratch clone of `4cd8d12` and committed them. `git diff --stat main...HEAD` → `4 files changed, 93 insertions(+), 26 deletions(-)` (`docs/spec-factory.md` 58, `prompts/02-spec-writer.md` 27, `prompts/04-planner.md` 8, `specs/build-harness.md` 26). `git diff --check` was clean. The results of every Acceptance command on that clone and on `main` are quoted under Acceptance.
- **T-0005 already applies the new FORMAT.** Its criterion-1 command, which checks that the Operator steps text keeps its meaning, prints `6` on both `main` and the trial clone (Acceptance 12). The section moves into `proposal.md` without losing its meaning (A5).

## Root cause

This is a design gap, not a defect. The design doc defines the spec only as the writer's output (§2 FORMAT) and the store only as "spec text and version" (piece 1). Neither the doc nor `specs/build-harness.md` part B/K has an artifact that outlives the ticket. Parent close (Merge gate row; build spec H step 2) closes the parent without writing anything back.

## Proposed change

The change touches four files, about 120 changed lines, as one PR. The text sits in two places: one new Harness paragraph carries the schema, and the writer and planner prompts carry the per-role format. Everything else is a one-clause consistency edit.

Constraints on the design:
- The writer stays read-only: piece 4 gives it no write access.
- Its output stays one text, and the harness splits that text into the change folder at the gate.
- The planner, implementer and verifier keep consuming "the pinned spec", which is the same pinned version, so the composed inputs (build spec H, item 77) do not change.
- The critic, implementer and verifier prompts do not change. The sub-ticket still carries runnable commands with NEW/REGRESSION labels, and "Acceptance", "Tests to change", "Risk" and "Operator steps" keep their names inside the artifacts, so every existing reference (piece 8, the Human gates row, critic rubric 2) still resolves.

Every replacement is given verbatim. OLD text must match exactly once, and Acceptance checks the NEW text.

**A. `docs/spec-factory.md`, Harness section: new paragraph.** Insert the block below directly before the paragraph that starts `**Routing table.** The dispatcher`. Put one blank line between the block and that paragraph. The block holds a paragraph, a table and a paragraph.
```text
**Spec store: the `spec-factory` schema.** The ticket store (piece 1) keeps specs in OpenSpec's tree (Fission-AI, MIT; layout and grammar as its `docs/concepts.md` and `docs/customization.md` give them), under a schema forked from OpenSpec's built-in `spec-driven` and named `spec-factory` (`openspec/schemas/spec-factory/schema.yaml`, selected by `openspec/config.yaml`). Current truth is `openspec/specs/<capability>/spec.md`: what each capability does now, as `### Requirement: <name>` blocks, each one SHALL or MUST sentence followed by `#### Scenario: <name>` items whose WHEN is a runnable command and THEN its expected result. A ticket's change is the folder `openspec/changes/<ticket id>/`:

| Artifact | Holds | Author |
|---|---|---|
| `proposal.md` | Problem, Evidence, Root cause, Out of scope, Open questions, Decisions, Risk, Operator steps | Spec writer |
| `design.md` | Proposed change, Tests to change | Spec writer |
| `specs/<capability>/spec.md` (delta) | Requirements under `## ADDED Requirements`, `## MODIFIED Requirements` or `## REMOVED Requirements`; its scenarios are the Acceptance items | Spec writer; the critic reviews it |
| `tasks.md` | The sub-tickets and coverage map | Planner |
| `verification.md` (the artifact the fork adds) | The NEW or REGRESSION label of each scenario and the writer's Responses; every critic round's output; at archive, every verifier result recorded per head for the parent and its sub-tickets | Spec writer (labels, Responses), critic, verifier |

`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. A delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing) writes nothing and parks the parent. Only the archive step writes current truth and `decisions.md`. The spec writer and the critic read current truth (routing table).
```
The Author column follows the operator's table, with one addition. The spec writer also authors the labels and Responses in `verification.md`, because the existing §2 rules already make the writer label each item NEW or REGRESSION and answer each finding. The critic and verifier still own their rounds and results. Because roles cannot write, "author" means whose output the harness copies in.

**B. `docs/spec-factory.md`, routing rules (parking).** Two replacements:
```text
OLD: a budget kill (piece 3), and a parent-close FAILED park the ticket.
NEW: a budget kill (piece 3), a parent-close FAILED, and an archive that does not apply (Spec store) park the ticket.
OLD:   - A parent-close FAILED or SPEC-DEFECT, or a sub-ticket closed by the human, parks the parent:
NEW:   - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent:
```
The rest of that bullet does not change: the human amends the spec and re-plans, or closes the parent. See Open question 4.

**C. `docs/spec-factory.md`, routing table.** Only the "Receives" and "Next" cells change. No row is added or removed, and no From or STATUS cell changes (Acceptance 16).
```text
OLD: | Triage | ACCEPT | Spec writer | The ticket |
NEW: | Triage | ACCEPT | Spec writer | The ticket; current truth (Spec store), read-only |
OLD: | Critic | Spec, repo read-only; round 2+:
NEW: | Critic | Spec, repo and current truth read-only; round 2+:
OLD: one verifier run on main against the parent's full Acceptance list: VERIFIED closes the parent; FAILED or SPEC-DEFECT parks the parent in the human queue |
NEW: one verifier run on main against the parent's full Acceptance list (every scenario of its pinned delta, with its `verification.md` label): VERIFIED archives the change (Spec store), then closes the parent; FAILED, SPEC-DEFECT or an archive that does not apply parks the parent in the human queue |
```
The second OLD is in the `Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT` row, which feeds the critic. The doc already says "'Receives' adds to the INPUT the role prompt already declares", so giving the writer and critic read access to current truth needs no edit to their prompts' INPUT lines.

**D. `docs/spec-factory.md`, §2 FORMAT.** Replace the block from the line `FORMAT` through the line `                    DISAGREE <evidence>` with the text below. The `STATUS:` and `CONFIDENCE / ESCALATIONS` lines after it stay as they are.
```text
FORMAT
One document in four parts, each opened by a line `=== <file>`. At the
spec gate the harness writes each part to that file of the change folder
openspec/changes/<ticket id>/ (schema spec-factory).
=== proposal.md
## Problem          what's wrong or missing, for whom
## Evidence         actual output, logs, metrics, repro steps
## Root cause       files and functions, if known; "unknown" is allowed
## Out of scope     what must NOT change
## Open questions   none | list
## Decisions        none | one line per design call this change makes,
                    including each answered open question
## Risk             blast radius; every protected path this will touch
## Operator steps   (optional) actions or checks on live or protected state
                    that only the operator can perform, after merge; not
                    acceptance; the human approves them at the spec gate
=== design.md
## Proposed change  lettered parts (A, B, C), specific enough to follow
## Tests to change  none | existing tests the intended change breaks, and why
=== specs/<capability>/spec.md
                    one part per capability changed; reuse a current-truth
                    capability where the behaviour already lives
## ADDED Requirements | ## MODIFIED Requirements | ## REMOVED Requirements
### Requirement: <name>   one sentence with SHALL or MUST
#### Scenario: <name>     one Acceptance item; names unique in the change
- WHEN `command`          (GIVEN lines first, if it needs a fixture)
- THEN expected result
                    MODIFIED restates the whole requirement. MODIFIED and
                    REMOVED name a requirement in current truth; behaviour
                    current truth lacks is ADDED. REMOVED gives the name
                    and a one-line reason.
=== verification.md
## Acceptance       - <scenario name> → NEW | REGRESSION; for NEW, how it
                    fails today
## Responses        (round 2+) per finding: FIXED <what changed> |
                    DISAGREE <evidence>
```
The RULES above the block do not change. "Acceptance criteria", "NEW", "REGRESSION" and "inline script in the Acceptance line" now refer to scenarios and their labels. The three Operator steps lines move into the `proposal.md` part verbatim (A5), so T-0005's check still holds (Acceptance 12). Decisions is new. See Open question 3.

**E. `docs/spec-factory.md`, §4 Planner OUTPUT.** Make these replacements inside the Planner block only. The `OUTPUT` line to change is the one directly after the RULES line `  siblings to re-verify, so parallel sub-tickets are not free.` and a blank line.
```text
OLD: OUTPUT
NEW: OUTPUT (the harness writes it to the change's tasks.md)
OLD:   Acceptance: commands + expected results
NEW:   Acceptance: the parent's scenarios it covers, each as its WHEN command,
           THEN result and verification.md label, plus any intermediate checks
           it needs, labelled NEW or REGRESSION the same way
OLD: Coverage map: parent criterion → sub-ticket ID
NEW: Coverage map: parent scenario → sub-ticket ID
```
The two continuation lines are indented 4 spaces in the file (`    THEN result …`, `    it needs, …`). They are shown with 11 spaces above only so that they line up under `NEW:`.

**F. `docs/spec-factory.md`, Changelog.** Append one entry after the last numbered entry and before the `Declined:` line. Its number is the last entry's number plus one at merge time: 39 on `4cd8d12`, where T-0007's entry holds 38. Use this text:
```text
Specs live in an OpenSpec tree under a forked `spec-factory` schema (Harness, Spec store): current truth per capability, one change folder per ticket (proposal, design, delta, tasks, and the factory-only `verification.md`), and a repo-level `decisions.md`. The spec writer's FORMAT is one document in those parts, and the delta's scenarios are the Acceptance items; the planner's output is the change's `tasks.md`; the spec gate pins the change folder; parent close archives it (apply the deltas, move the folder, append the decisions). Roles, round limits, gates and harness pieces 1–12 are unchanged.
```

**G. Re-copy the two prompt blocks** from the edited doc. Do not hand-edit them:
- `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md > prompts/02-spec-writer.md`
- `awk '/^ROLE: Planner\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md > prompts/04-planner.md`

`prompts/03-spec-critic.md` and `prompts/07-verifier.md` are not re-copied because their blocks do not change. The critic's rubric names (Tests to change, Risk, Operator steps, Acceptance) all survive inside the artifacts. The verifier already runs "every acceptance command from the sub-ticket", and part E keeps the commands and labels on the sub-ticket.

**H. `specs/build-harness.md`, store listing** (the `State on branch \`tickets\`` paragraph under Proposed change):
```text
OLD: `tickets/`, `specs/`, `requests/`,
NEW: `tickets/`, `specs/`, `openspec/`, `decisions.md`, `requests/`,
```

**I. `specs/build-harness.md` part B.** Replace the line `Spec text \`specs/<ID>/v<N>.md\`; sub-ticket text \`specs/<ID>/subticket.md\`.` with the two paragraphs below, separated by a blank line:
```text
Spec text `specs/<ID>/v<N>.md` (every version the writer returns, verbatim); sub-ticket text `specs/<ID>/subticket.md`.

**Spec store** (doc §Harness, Spec store). `factory init` creates `openspec/config.yaml` (`schema: spec-factory`), `openspec/schemas/spec-factory/schema.yaml` (the artifacts of OpenSpec's `spec-driven`, `proposal`, `specs` with `generates: specs/**/*.md`, `design` and `tasks`, plus `verification` with `generates: verification.md` and `requires: [specs]`), an empty `openspec/specs/` and an empty `decisions.md`. Pinning a version (K) splits it on its `=== <path>` lines (the path is the first token after `=== `; text before the first such line is dropped) into `openspec/changes/<ID>/<path>`; a path other than `proposal.md`, `design.md`, `verification.md` or `specs/<capability>/spec.md` with a kebab-case capability refuses the pin. `verification.md` is the writer's part plus `## Critic rounds`: per critic run of the ticket, oldest first, `round <n> · spec v<N> · <run_id> · <STATUS>` and its findings verbatim. `tasks.md` comes from `factory spec tasks`. No role writes `openspec/` or `decisions.md`, and only `factory archive` (K) writes `openspec/specs/` and `decisions.md`.
```
Then make three more edits in part B and part C:
```text
OLD (B, CLI): → `spec.version += 1`, `specs/ID/v<N>.md`;
NEW:          → `spec.version += 1`, `specs/ID/v<N>.md`; `factory spec tasks PARENT --run RUN` → copies that planner run's `output.md` to `openspec/changes/<PARENT>/tasks.md` (exit 2 unless RUN is a `PLANNED` planner run of PARENT);
OLD (C, events): `harness-bug`, `spec.exported`.
NEW:             `harness-bug`, `spec.exported`, `change.pinned`, `change.archived`.
```

**J. `specs/build-harness.md` part K.** Make two insertions and add one new bullet. The export to `knowledge_vault/sanitized_specs/<ID>.md` stays as it is: it exports the pinned text, which now contains all four parts. Items 48, 60 and 61 therefore still hold.
```text
OLD: copies "Tests to change" and Risk paths into the ticket, `approvals/ID/spec-v<N>.yaml`,
NEW: copies "Tests to change" and Risk paths into the ticket, `approvals/ID/spec-v<N>.yaml`, writes the pinned version as the change folder (B; event `change.pinned`; exit 2 with nothing written when a part is malformed or a delta does not apply to current truth: an ADDED requirement name already in `openspec/specs/<capability>/spec.md`, or a MODIFIED or REMOVED name not in it),
OLD: re-pins `approved_version`, writes `approvals/<parent>/spec-v<N+1>.yaml`,
NEW: re-pins `approved_version` and rewrites the change folder as `approve-spec` does (`## Critic rounds` kept), writes `approvals/<parent>/spec-v<N+1>.yaml`,
```
Add a new last bullet of part K, directly before `### L. Verifier as gate runner (piece 11)`:
```text
- `factory archive ID` (harness identity; `build.js` runs it on the parent-close VERIFIED, H): (1) appends `## Verifier results` to `openspec/changes/<ID>/verification.md`, one line per verifier row in `results/` for the parent's and its sub-tickets' heads, oldest first, `<head> · <ticket> · <STATUS> · <run_id>`; (2) applies every delta to `openspec/specs/<capability>/spec.md` (created with `# <capability>` and `## Requirements` when absent): ADDED appends the requirement block, MODIFIED replaces the block whose `### Requirement:` name matches, REMOVED deletes it; (3) moves `openspec/changes/<ID>` to `openspec/changes/archive/<YYYY-MM-DD>-<ID>` (UTC date); (4) appends `<YYYY-MM-DD> <ID> <line>` to `decisions.md` per line of `proposal.md`'s `## Decisions` other than `none`. One commit, event `change.archived`. A delta that does not apply → exit 2, nothing written.
```

**K. `specs/build-harness.md` part H** (`build.js`). Three replacements:
```text
OLD: `PLANNED` → clerk `subticket add` per sub-ticket
NEW: `PLANNED` → clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add` per sub-ticket
OLD: the pinned parent spec (its full `## Acceptance` list)
NEW: the pinned parent spec (every delta scenario with its `## Acceptance` label)
OLD: `VERIFIED` → `closed`;
NEW: `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`;
```
`run compose` and its `input_sources` do not change. The parent-close run still reads `specs/<ID>/v<N>.md`, which holds every part, so item 77 is unchanged.

**L. `specs/build-harness.md` Acceptance: two new items.** Insert a heading `### Spec store [S3, S4]` and the two items directly before `### Gates (every seam)`, with a blank line around the heading. Number the items one and two past the highest Acceptance item number at merge time: 87 and 88 on `4cd8d12`, where T-0003 holds 86. If the numbers move, update the cross-references "item 87's" in the second item to match.
```text
87. ⟨bare⟩ **Change folder at the gate:** `specs/T-0001/v1.md` in the four-part FORMAT of doc §2, its delta part `=== specs/status-parser/spec.md` holding `## ADDED Requirements` with `### Requirement: trailer-read` and one scenario: `AS daniel factory approve-spec T-0001 --version 1` → `openspec/changes/T-0001/` holds `proposal.md`, `design.md`, `specs/status-parser/spec.md` and `verification.md`, each equal to its part of `v1.md` except that `verification.md` also ends with `## Critic rounds`, one entry per critic run of T-0001; `change.pinned` logged; `openspec/specs/` and `decisions.md` unchanged. A `v2.md` whose delta has `## MODIFIED Requirements` with `### Requirement: no-such-req`: `AS daniel factory approve-spec T-0001 --version 2` → exit 2, stderr names `no-such-req`, `approved_version: 1`, no `approvals/T-0001/spec-v2.yaml` [NEW]
88. ⟨wf⟩⟨bare⟩ **Archive at parent close:** case `plan-three` on item 87's T-0001, after item 77's VERIFIED: `openspec/changes/T-0001` is gone; `openspec/changes/archive/<date>-T-0001/` holds item 87's four files and `tasks.md`, equal to the planner run's `output.md`; its `verification.md` ends with `## Verifier results`, one line per verifier row of `T-0001.1`–`.3` and `T-0001`; `openspec/specs/status-parser/spec.md` contains `### Requirement: trailer-read` and its scenario; `decisions.md` gained one `<date> T-0001 …` line per `## Decisions` line of the proposal; in the log `change.archived` precedes the transition to `closed`. A second parent, pinned before T-0001 archived with a delta that also ADDs `trailer-read`, reaching its parent-close VERIFIED → `status: parked`, `parked.reason` starts `archive:`, and `openspec/specs/`, `decisions.md` and its change folder are unchanged [NEW]
```
In the line `Items needing the bare repo: …`, append the two new numbers after `84`, for example `…, 83, 84, 87, 88.`.

**M. Nothing else changes.** In particular:
- `specs/build-harness.md` keeps its own old-shape sections: it is not migrated (A4).
- The plan files under `plans/` are not changed.

## Acceptance

Run every command from `~/dev/spec-factory` with bash, on the PR branch, with `main` as the base. "Today" means `main` at `4cd8d12`. I ran each command on that commit and on the trial clone with A–L applied, and quote both results. Commands that contain a backtick (3, 6, 10, 11) are delimited by double backticks; the command is the text between them, without the one space of padding at each end.

1. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | grep '^=== ' | tr '\n' ';'` → `=== proposal.md;=== design.md;=== specs/<capability>/spec.md;=== verification.md;`. The writer's FORMAT is one document in the four parts, in that order. [NEW: prints nothing today, because the FORMAT has no parts]
2. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | awk '/^FORMAT$/{f=1} /^STATUS:/{f=0} f&&/^=== /{part=$2} f&&/^## /{s=$0; sub(/^## /,"",s); sub(/  +.*/,"",s); print part ":" s}' | tr '\n' ';'` → `proposal.md:Problem;proposal.md:Evidence;proposal.md:Root cause;proposal.md:Out of scope;proposal.md:Open questions;proposal.md:Decisions;proposal.md:Risk;proposal.md:Operator steps;design.md:Proposed change;design.md:Tests to change;specs/<capability>/spec.md:ADDED Requirements | ## MODIFIED Requirements | ## REMOVED Requirements;verification.md:Acceptance;verification.md:Responses;`. Each section sits in the artifact the operator's mapping gives it, and Operator steps is in `proposal.md` (A5). A section dropped or placed in the wrong part changes this string. [NEW: today prints `:Problem;:Evidence;:Root cause;:Proposed change;:Acceptance;:Tests to change;:Out of scope;:Open questions;:Risk;:Operator steps;:Responses;`, every section belonging to no part]
3. `` awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | grep -o -e '^### Requirement: <name>' -e '^#### Scenario: <name>' -e '^- WHEN `command`' -e '^- THEN expected result' -e 'SHALL or MUST' -e 'MODIFIED restates the whole requirement' | sort -u | wc -l | tr -d ' ' `` → `6`. The delta part states the requirement and scenario grammar, says a scenario's WHEN is a command, and says a MODIFIED requirement is restated whole. [NEW: prints `0` today]
4. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | diff - prompts/02-spec-writer.md && grep -c '^=== ' prompts/02-spec-writer.md` → no diff output, then `4`, exit 0. The writer prompt is a verbatim re-copy that includes the parts. [NEW: the diff is clean today, but grep prints `0` and exits 1]
5. `awk '/^ROLE: Planner\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | diff - prompts/04-planner.md && tr -s ' \n' '  ' < prompts/04-planner.md | grep -o -e "OUTPUT (the harness writes it to the change's tasks.md)" -e 'Coverage map: parent scenario → sub-ticket ID' -e 'THEN result and verification.md label' | sort -u | wc -l | tr -d ' '` → no diff output, then `3`. The planner prompt is a verbatim re-copy. Its output is the change's `tasks.md`, its sub-tickets carry scenarios with labels, and its coverage map is keyed by scenario. [NEW: today the diff is clean and the count is `0`]
6. `` awk '/^## Harness: functional pieces/{f=1} /^## Human gates/{f=0} f' docs/spec-factory.md | grep -o -F -e 'openspec/specs/<capability>/spec.md' -e 'openspec/changes/<ticket id>/' -e '`verification.md`' -e '`decisions.md`' -e '`spec-driven`' -e 'openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/' -e 'ADDED appends the requirement' -e 'MODIFIED replaces the requirement of that name whole' -e 'REMOVED deletes it' -e 'Only the archive step writes current truth' | sort -u | wc -l | tr -d ' ' `` → `10`. The Harness section defines the layout, names the fork's base schema, gives the three delta operations and the archive path, and says only archive writes current truth. [NEW: prints `0` today]
7. `grep '^| Merge gate | CI green' docs/spec-factory.md | grep -o -e 'VERIFIED archives the change' -e 'then closes the parent' -e 'an archive that does not apply parks the parent' | wc -l | tr -d ' '` → `3`. Parent close archives the change before it closes, and a failed archive parks the parent. [NEW: prints `0` today; the row says "VERIFIED closes the parent"]
8. `grep -c -F -e 'a parent-close FAILED, and an archive that does not apply (Spec store) park the ticket.' -e '  - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent:' docs/spec-factory.md` → `2`. An archive refusal is a parking state with the parent-park resolution. [NEW: prints `0` today]
9. `grep -E '^\| (Triage \| ACCEPT|Spec writer \| READY-FOR-CRITIC)' docs/spec-factory.md | grep -c 'current truth'` → `2`. The writer and the critic receive current truth read-only. [NEW: prints `0` today]
10. `` awk '/^## Changelog/{f=1} /^## Appendix/{f=0} f' docs/spec-factory.md | grep '^[0-9][0-9]*\. ' | awk -F. '$1!=NR{gap=1} {last=$0} END{print (gap?"GAP":"CONTIGUOUS"), (last ~ /spec-factory` schema/ && last ~ /decisions/ && last ~ /archive/ ? "LAST-IS-SPEC-STORE" : "LAST-IS-OTHER")}' `` → `CONTIGUOUS LAST-IS-SPEC-STORE`, whichever number the entry gets. [NEW: prints `CONTIGUOUS LAST-IS-OTHER` today]
11. `` printf '%s %s %s\n' "$(grep -o -F -e '**Spec store** (doc §Harness, Spec store)' -e 'plus `verification` with `generates: verification.md`' -e '- `factory archive ID`' -e 'clerk `factory archive PARENT` (K), then `closed`' -e 'clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add`' specs/build-harness.md | sort -u | wc -l | tr -d ' ')" "$(grep -cE '^[0-9]+\. (⟨[a-z]+⟩)+ \*\*(Change folder at the gate|Archive at parent close):\*\*' specs/build-harness.md)" "$(grep -c -F '`VERIFIED` → `closed`;' specs/build-harness.md)" `` → `5 2 0`. The build spec now has the following, and a VERIFIED parent no longer goes straight to `closed`:
    - the store layout with the forked schema's `verification` artifact;
    - the archive command;
    - `build.js` writing `tasks.md` at PLANNED and archiving at VERIFIED;
    - two acceptance items covering both.

    [NEW: prints `0 0 1` today]
12. `awk '/^ROLE: Spec writer\./{p=1} p{print} p&&/^CONFIDENCE \/ ESCALATIONS$/{exit}' docs/spec-factory.md | awk '/^## Operator steps /{f=1;print;next} f&&/^                    [^ ]/{print;next} {f=0}' | tr -s ' \n' '  ' | grep -o -e '(optional)' -e 'live or protected state' -e 'only the operator' -e 'after merge' -e 'not acceptance' -e 'at the spec gate' | sort -u | wc -l | tr -d ' '` → `6`. This is T-0005's criterion 1: Operator steps keeps its full meaning after the move. [REGRESSION: `6` today and on the trial clone]
13. `for rf in 'Triage:01-triage' 'Spec writer:02-spec-writer' 'Spec critic:03-spec-critic' 'Planner:04-planner' 'Implementer:05-implementer' 'Code reviewer:06-code-reviewer' 'Verifier:07-verifier' 'Retro:08-retro'; do r=${rf%%:*}; f=${rf##*:}; awk "/^ROLE: $r\\./{p=1} p{print} p&&/^CONFIDENCE \\/ ESCALATIONS\$/{exit}" docs/spec-factory.md | cmp -s - prompts/$f.md || echo "DIFF $f"; done` → no output. Every role prompt file is still a verbatim copy of its block. [REGRESSION]
14. `git diff -U0 main...HEAD -- prompts/00-preamble.md prompts/01-triage.md prompts/03-spec-critic.md prompts/05-implementer.md prompts/06-code-reviewer.md prompts/07-verifier.md prompts/08-retro.md | wc -l | tr -d ' '` → `0`. No other prompt changes. [REGRESSION]
15. `diff <(git show main:docs/spec-factory.md | grep '^STATUS: ') <(grep '^STATUS: ' docs/spec-factory.md)` → no output. No role's STATUS vocabulary changes. [REGRESSION]
16. `diff <(git show main:docs/spec-factory.md | awk '/^\| From \| STATUS \|/,/^Any STATUS not in this table/' | awk -F' [|] ' '{print $1 " | " $2}') <(awk '/^\| From \| STATUS \|/,/^Any STATUS not in this table/' docs/spec-factory.md | awk -F' [|] ' '{print $1 " | " $2}')` → no output. Routing has the same rows, in the same order, with the same From and STATUS cells. [REGRESSION]
17. `git show main:specs/build-harness.md | awk '/^## Acceptance/{f=1} /^## Tests to change/{f=0} f' | grep -E '^[0-9]+\. ' | grep -vxF -f <(awk '/^## Acceptance/{f=1} /^## Tests to change/{f=0} f' specs/build-harness.md)` → no output, exit 1. Every existing build-spec acceptance item (86 today) survives verbatim. [REGRESSION]
18. `awk '/^## Acceptance/{f=1} /^## Tests to change/{f=0} f' specs/build-harness.md | grep -oE '^[0-9]+\. ' | sort -n | uniq -d` → no output. No acceptance item number is duplicated. [REGRESSION]
19. `git diff --name-only main...HEAD | grep -v -x -e docs/spec-factory.md -e specs/build-harness.md -e prompts/02-spec-writer.md -e prompts/04-planner.md` → no output, exit 1. No other path is touched, including `plans/`, `README.md`, the approved specs and `intake/**`. [REGRESSION]
20. `git diff --check main...HEAD` → no output, exit 0 [REGRESSION]

Results captured:
- `main` (`4cd8d12`), items 1–20: (empty); the `:Problem;…` string; `0`; clean + `0`; clean + `0`; `0`; `0`; `0`; `0`; `CONTIGUOUS LAST-IS-OTHER`; `0 0 1`; `6`; then empty output for 13–19 and clean for 20.
- Trial clone, items 1–20: the four parts; the mapped string; `6`; clean + `4`; clean + `3`; `10`; `3`; `2`; `2`; `CONTIGUOUS LAST-IS-SPEC-STORE`; `5 2 0`; `6`; then empty output for 13–19 and clean for 20.

Wrong fixes these items catch:
- A section left in the wrong part fails 2.
- A prompt edited by hand instead of re-copied fails 4, 5 and 13.
- A parent that closes without archiving fails 7 and 11.

## Tests to change

none. This repo holds documents and has no test files. Build-spec items 1–86 are kept verbatim (Acceptance 17).

## Out of scope

- **These must not change:**
  - the critic, implementer, reviewer, verifier, triage and retro prompt blocks and their `prompts/` copies;
  - the preamble;
  - the From and STATUS cells of every routing row, the round limits, and the human gates table;
  - harness pieces 1–12 as table rows.
- **No migration:** no existing spec is rewritten into the new shape. That covers `intake/state/specs/T-0001..T-0007` (A4) and `specs/build-harness.md`. The green-side pilot specs (SPEC-21, SPEC-27) and green's ROADMAP register are Nanobot-side follow-ups (A1).
- **Paths not touched:** `plans/` (including `plans/build-harness.md`), `README.md`, and `intake/**` (apart from this output file).
- **No new export target:** `knowledge_vault/sanitized_specs/<ID>.md` keeps exporting the pinned text.
- **No new tooling:** no `openspec` CLI call, install or dependency (Open question 1), and no `openspec/` tree created in this repo. The tree is described for the store; the harness's `factory init` creates it, which is green-side build work.
- **No new routing STATUS or ticket state:** an archive refusal parks the parent with a reason, as other parent parks do.

## Open questions

none open. The four questions of v0 were answered in Answer 2, each by taking the recommended default; the operator can overturn any of them at the spec gate, and question 2 is flagged there as the one most worth a second look. Every part above was already written against these defaults, so no part changed.

1. (A3) No runtime dependency on the `openspec` CLI. Archive and the gate's apply check are the harness's own code (parts I, J); the tree stays readable by OpenSpec tooling, which is an optional manual check, never a gate. Why v0 recommended it: `openspec` is not installed (`command -v openspec` → not found), it is a Node package (`@fission-ai/openspec` 1.14.0) and the harness is Python, and the implementer rules say "No new dependencies without escalation".
2. The `openspec/` tree lives in the ticket store on the `tickets` branch (parts H, I). The writer and critic receive current truth through the routing table (part C). The alternative not taken: the target repo's `main`, which would need a new no-sub-ticket PR kind through the merge gate for the gate's change folder and for each archive.
3. Decision-log lines come from a new `## Decisions` section in `proposal.md`, written by the spec writer and approved at the spec gate; archive appends them verbatim (parts A, D, J).
4. An archive refusal reuses the existing parent-park resolution: amend the spec and re-plan, or close (part B). No new resolution edge.

## Risk

**Blast radius.** The diff touches four document files and about 120 lines. Every future spec writer and planner run reads the changed blocks, so a wording mistake shapes every later spec. Criteria 1–5 pin the structure, and criterion 12 shows that T-0005's meaning survives.

**Concurrent archives.** Two parents that both MODIFY the same requirement can both pass their gates. The second archive then replaces the first one's version whole. OpenSpec's model has the same property. Nothing here detects it, and the critic and human gate are the check.

**Protected and guardrail paths, declared for the gate:**
- generated (protected): `prompts/02-spec-writer.md` and `prompts/04-planner.md`. They are changed only by re-copying (part G; criteria 4, 5 and 13).
- guardrail ("these prompts"): the §2 and §4 prompt blocks in `docs/spec-factory.md` and the same two `prompts/` files. These need a human approval record on the PR (piece 8).
- No `intake/**` path (infra) is touched beyond this output file.
- `~/dev/nanobot-upstream/**` was read only, by `grep`.
- `~/.nanobot/**` was not read.

**Merge order:**
- T-0005 has merged (`ac66b2c`), and part D carries its Operator steps lines verbatim.
- T-0007 has merged (`b9379ec`). It inserted the Role-context block paragraph after "What the harness itself owns", appended "Both follow the role-context block (above)." to the Routing table paragraph, and edited part B's `run compose` bullet, part I and item 42. Part A inserts before the Routing table paragraph, which keeps T-0007's sentence; no OLD text here overlaps T-0007's lines, and Acceptance 17 keeps item 42 as it is on `main`. The Changelog entry is therefore 39.
- T-0009 (`ready-for-triage`, request `issues/09_run_id_allocation.md`) names build-spec part B's `factory run start` bullet and part I. This change edits neither, so either merge order works textually.
- T-0003 took build-spec item 86, which is why part L numbers its items one past the highest at merge time (87, 88 on `4cd8d12`).

**Follow-up, not acceptance.** The `plans/build-harness.md` coverage map does not list the new build-spec items, as it does not list T-0003's item 86. Covering them is a re-plan, outside this ticket.

## Responses

(round 1: none; no critic has run on this ticket. The operator's answers to v0's open questions are recorded under Open questions.)

Out-of-scope observations:
- `README.md` describes `specs/<ticket>.md` as "a spec: the Spec writer's output". That stays true for this design repo's own files, which are not migrated (A4). If the operator wants this repo to use the new shape for new specs, that is a separate ticket.
- The request says "OpenSpec's default schema". The built-in schema is named `spec-driven` (`customization.md:184`), and part A uses that name.
- OpenSpec now lets a change retire a capability when its last requirement is REMOVED (`retire_capabilities: true`, `concepts.md:397`). Part J's archive deletes the requirement and leaves a capability file with no requirements. Whether the factory adopts retirement is a later design call, not taken here.
- Acceptance commands in spec v0 used single-backtick code spans around commands that themselves contain backticks (items 3, 6, 10, 11), so the rendered Markdown split them. v1 delimits those four with double backticks; the command text is unchanged.
