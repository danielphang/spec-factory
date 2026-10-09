## Proposed change
A. **Triage names the capabilities.** This part touches triage's input and its prompt.
   1. In `factory/compose.py`, the `triage` branch appends the capability index after the request. It lists every capability in current truth, built as in B2, under the heading `## Capability index: every capability in current truth`. Its first paragraph says: "Name the capabilities this request touches on your `Capabilities:` line. The spec writer receives those in full and this index for the rest." With no current truth, nothing is appended.
   2. The triage prompt changes in the `docs/design.md` §1 block. `docs/prompts/01-triage.md` is re-copied from that block, and `factory/prompts/triage.md` gets the same edit:
      - INPUT reads "One raw request, the capability index (one line per current-truth capability), plus search access to open and recently closed tickets."
      - Step 4 adds a sentence: "Name the current-truth capabilities the request touches, from the capability index."
      - OUTPUT gains a line after `Evidence:` that starts at column 0, `Capabilities: (names from the capability index, comma-separated; none if the request touches none)`. The block's line width stays at 72 characters.

B. **Compose sends only the named capabilities, and an index of the rest.** All of this part is in `factory/compose.py`.
   1. `triage_capabilities(root, tid)` reads the latest finished triage run of the ticket (`_runs_for`). It returns the names on that output's first line starting `Capabilities:`. The rest of the line is split on commas and whitespace, with backticks and trailing periods stripped, and only the names of existing current-truth capabilities are kept. It returns None when there is no such run or no such line.
   2. `cited_capabilities(root, text)` returns the existing current-truth capabilities whose `specs/<name>/spec.md` appears anywhere in `text`.
   3. The capability index part is headed `## Capability index: current truth not given in full above`. Its first paragraph is one line, with these exact words:

      > This list is complete: every current-truth capability not given in full above has one line here. Open a capability at its path before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, sends that capability in full to the critic, and the decisions that name it to the critic and the planner, so cite under Evidence each capability you open.

      The third sentence states what B4 to B7 do: the critic gets a cited capability in full, and the planner gets only the decision lines that name it (B7). Acceptance counts the phrase `sends that capability in full to the critic`.

      Then comes one line per capability, in path order: `- <name>, <size in kB, rounded up> kB, `<absolute path of its spec.md>`: <requirement name>; <requirement name>; …`. Each requirement name is the text after `### Requirement: ` in that spec.
   4. The selected set S is the following:
      - writer: triage's names, plus those cited in `specs/<tid>/v<version>.md` when version ≥ 1;
      - critic: triage's names, plus those cited in the version under review;
      - planner: triage's names, plus those cited in the approved version, read whole.

      When `triage_capabilities` returns None, S is "everything" for that role. `add_truth` and `add_decisions` then behave exactly as today.
   5. With a selected S, `add_truth` adds each capability in S in full, as today, under `Current truth: <name>`. It then appends the capability index (B3) for every other capability, or nothing when none is left. Only the capabilities sent in full go into `input_sources`.
   6. With a selected S, `add_decisions` keeps a log line in full when its second field is the ticket id, or when its text contains the name of a capability in S. A match must not be bordered by a letter, digit, `-` or `_`.
      - The kept lines go under `## Decision log (decisions.md): the standing decisions logged against this ticket or naming a capability given in full, read-only. The full log is `<absolute path>``. `decisions.md` is a source only when at least one line is kept.
      - The other lines are grouped by ticket id under `## Decision index: decisions not given in full above`. Its first paragraph is one line, with these exact words, `<absolute path of decisions.md>` replaced by that path:

        > This list is complete: every ticket with a decision not given in full above has one line here. Read a ticket's decisions with `grep ' <ticket id> ' <absolute path of decisions.md>`.

        `<ticket id>` stays literal. Acceptance counts the text `grep ' <ticket id> ' <absolute path>`.
      - Then comes one line per ticket in first-appearance order: `- <ticket id> (<n> decision(s), <first date> to <last date>): <title>`. The title is the ticket's `title` from `tickets/<id>.yaml`, or empty when the store has no such ticket.
      - An empty or whitespace-only log still adds nothing, as today.
   7. The planner gets no capability index. B6 applies to the planner's log.

C. **Documents.**
   - `docs/design.md`, §Harness "Spec store" paragraph (`:94`). The last two sentences become a description of B. Triage receives the capability index and names capabilities. The spec writer and critic receive those capabilities in full, plus the ones their spec cites, and the capability index for the rest. They and the planner receive the decision log's lines for the ticket and its capabilities, and a decision index for the rest. A ticket with no `Capabilities:` line gets the whole of both.
   - `docs/design.md`, routing table. Row "New request" (`:115`) gains "the capability index". The "Triage ACCEPT" (`:116`) and "Spec writer READY-FOR-CRITIC" (`:120`) rows say "current truth and the decision log, as the Spec store paragraph describes".
   - `docs/changelog.md`: one new numbered entry, "After issue #75 (2026-10-08), where …", with the Evidence figures and the change in two or three sentences.
   - `dev/build-harness.spec.md:280`. The writer's input reads "current truth as doc §Harness, Spec store gives it (in full for the capabilities triage named or the spec cites, the capability index for the rest; all of it when triage's output has no `Capabilities:` line)". The critic's input reads "(as for the writer)". Item 90 holds as written, because its stub triage output has no `Capabilities:` line. Add one clause to item 90 saying so.
   - `README.md`:
     - the Triage row (`:84`) adds "the capability index";
     - the Spec writer row (`:85`) reads "current truth in full for the capabilities triage named, and the capability index for the rest; the decision log's lines for this ticket and those capabilities, and a decision index for the rest";
     - the Spec critic row (`:86`) follows the same pattern as the Spec writer row, with "the capability index" in it;
     - the Planner row (`:87`) gains only the decision-index clause, "the decision log's lines for this ticket and its capabilities, and a decision index for the rest", and no capability index (B7);
     - bump the status date (`:9`) under "Maintaining this page".

## Tests to change
none. Every existing test that pins a writer, critic or planner input composes without a finished triage run, or with a stub triage output that has no `Capabilities:` line. B4's fallback keeps their inputs and `input_sources` unchanged: `tests/factory/test_spec_store.py:54-71` and `:281-293`, `tests/factory/test_decision_log.py:200-237`, and `tests/factory/test_shepherd.py:40-48`. The triage input gains only an index part, which adds no source and no decision text. So `test_decision_log.py:207` and `:211` still hold. `test_decision_log.py:248-255` checks that the §1 block equals `docs/prompts/01-triage.md`, and A2 edits both. `tests/factory/test_instance.py:292-293` reads `factory/prompts/triage.md` at test time.

