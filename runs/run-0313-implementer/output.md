Sub-ticket: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030.3/subticket.md (T-0030.3, part C of T-0030; parent spec /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md)

Branch: `factory/T-0030.3` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0030.3`, base `d226a4d`, head `67b61a5` (two commits: `ef9a74b` the change, `67b61a5` drops a blank line at the end of the new test file).

## What changed

The four roles that build and check code no longer receive the spec's two longest write-ups they never use. The planner, implementer, reviewer and verifier get the approved spec without its `## Evidence` section (captured command output) and its `## Responses` section (the spec writer's replies to the critic). Each input's heading now gives the absolute path of the full spec file, so the role can still open it. A critic in its second round (the critic is the role that reviews a spec draft; in round 2 it re-reviews a revised draft) now gets a diff of what changed when that is smaller than the previous draft. All changes are in `factory/compose.py`, the code that writes each role's input file.

- **C1.** New `without_evidence(text)` in `factory/compose.py` (lines 94–104). It drops each section that starts at a line `## Evidence` or `## Responses`, trailing spaces ignored. A section runs up to the next line starting `## ` or `=== `. It reuses the existing fence-aware line reader `specstore.lines_outside_fences`, so a line inside a fenced code block neither starts nor ends a section. A heading such as `## Evidence of something else` is not cut.
- **C2.** A new local `add_spec(rel, heading)` calls the existing `add()` with the cut. `add()` gains an optional `edit` argument that defaults to returning the text unchanged, so every other caller composes exactly as before. `add_spec` replaces `add` at the four places the sub-ticket names: the planner's "Approved spec", the implementer's "Parent spec", the checkers' "Parent spec" and the parent-close verifier's "Parent spec … verify every scenario on main". The parent-close verifier is the verifier run on the integration branch once every sub-ticket has merged. Each heading keeps its words and appends: `. Its Evidence and Responses sections are left out; the full spec is \`<absolute path>\``. `input_sources` (the list of store files each run records as its input) is unchanged, because `add()` still appends the same `specs/<id>/v<n>.md` path. `specs/<id>/subticket.md` still goes through plain `add()`, uncut.
- **C3.** Round-2 critic: the harness builds `difflib.unified_diff` from `v<n-1>` to `v<n>`, with 3 lines of context, labelled `specs/<id>/v<n-1>.md` and `specs/<id>/v<n>.md`. When the diff's byte length is less than `v<n-1>`'s, the input holds the diff under `## Previous spec version (v<n-1>), as a unified diff to v<n>`. Otherwise it holds `v<n-1>` whole under `## Previous spec version (v<n-1>), whole: the diff to v<n> is not smaller`. `input_sources` still lists `specs/<id>/v<n-1>.md`.
- **C4.** The triage and spec writer inputs, the critic's current spec ("Spec under review") and every other input are unchanged.

Callers (coding standard, rule 2): `compose()` is called only from `run_compose` in `factory/cli.py:325`. `add` is a closure inside `compose()`. Every existing call to it passes two arguments and so takes the identity `edit`.

## Acceptance results

All commands ran from the worktree inside the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`, with `TMPDIR` set to this run's scratch directory. The fixtures `t0030-spec.sh` and `t0030-critic.sh` were written from the parent spec's GIVEN block, and `diff` against input.md lines 377–427 and 430–450 printed nothing for either.

1. NEW, "Downstream roles get every spec section but Evidence and Responses, and the full spec's path".
   - Before, on `d226a4d`: `planner: evidence=1 responses=1 kept=9 full=0`, and the same for implementer, reviewer, verifier and parent-close. This matches the spec's "today" line: all five inputs carried both sections and no path.
   - After, on `67b61a5`: `planner: evidence=0 responses=0 kept=9 full=1`, `implementer: evidence=0 responses=0 kept=9 full=1`, `reviewer: evidence=0 responses=0 kept=9 full=1`, `verifier: evidence=0 responses=0 kept=9 full=1`, `parent-close: evidence=0 responses=0 kept=9 full=1`. Every input lost both sections, kept all nine other marked sections, and names the full spec's path on exactly one line.
2. NEW, "A round-2 critic receives a small revision as a diff".
   - Before: `removed=0 added=0 keep100=2 prior_findings=1`. This matches the spec's "today" line: v1 arrived whole.
   - After: `removed=1 added=1 keep100=1 prior_findings=1`. The input holds the `-OLD-ONLY` and `+NEW-ONLY` diff lines. `keep line 100` appears once, in the current spec only, and the prior findings are still there.
3. REGRESSION, "A round-2 critic receives a rewritten spec's previous version whole".
   - After: `removed=0 keep100=1 other100=1 prior_findings=1`. The rewrite's diff is larger than v1, so v1 arrives whole. Before the change it printed the same line.
4. REGRESSION, the gate suite.
   - `git diff --check main...HEAD`: exit 0 on `67b61a5`. The first run, on `ef9a74b`, failed with `tests/factory/test_role_inputs.py:198: new blank line at EOF.`; commit `67b61a5` fixed it.
   - `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `364 passed in 223.69s` on `67b61a5`. This includes `tests/factory/test_p0_cli.py` and `tests/factory/test_shepherd.py`, with their round-2 critic and `input_sources` assertions, unchanged.

I also composed one planner input and one small-diff critic input and read them by eye. The planner's spec runs from `=== proposal.md` to `## Acceptance` with no Evidence or Responses text. The critic's diff section is 9 lines: the two file labels, one `@@` hunk header, three context lines before the change, `-OLD-ONLY`, `+NEW-ONLY` and one context line after it, which is the file's last line.

## Tests added/changed

New file `tests/factory/test_role_inputs.py`, 4 tests. No existing test changed.
- `test_the_cut_drops_evidence_and_responses_and_keeps_every_other_section` covers the helper's edges. A `## Evidence` with trailing spaces is cut. Fenced `## ` and `=== ` lines inside Evidence do not end it. A `###` sub-heading stays inside Evidence. A fenced `## Evidence` elsewhere is kept as text, and so is `## Evidence of something else`. `=== ` ends a section, and text with nothing to cut comes back byte-identical. The tests' own `factory` package shadows the harness package, so the helper runs in a subprocess from the harness checkout.
- `test_planner_implementer_checkers_and_parent_close_get_the_spec_without_evidence_or_responses` drives the shepherd fixture (the existing end-to-end test harness in `test_shepherd.py`) through a whole ticket. It uses a marked copy of the accept-approve spec stub with a fenced block inside Evidence. For all five inputs it checks: no Evidence or Responses text, every other section present, the heading naming the full path, and the path in `input_sources`. It also checks that the critic's current spec still carries both sections.
- `test_a_round2_critic_gets_a_small_revision_as_a_diff` checks the heading, the two labels, the changed lines, exactly 3 lines of context and unchanged `input_sources`.
- `test_a_round2_critic_gets_a_rewritten_spec_s_previous_version_whole` checks the "whole" heading and that no diff appears.

All four failed before the change. The first failed with `AttributeError: module 'factory.compose' has no attribute 'without_evidence'`. The second failed with `EVIDENCE-MARK` in the planner input. The other two failed on the missing heading.

## Known gaps and uncertainties

- An unclosed code fence inside a spec's Evidence section would hide every line after it from these four roles. `lines_outside_fences` treats an unclosed fence as running to the end of the text. I checked this repository's 60 stored spec versions (`/Users/dphang/dev/spec-factory/.factory/store/specs/*/v*.md`) and none has an odd number of fence lines. The spec store's own parsing has the same exposure, and nothing here guards it.
- A section is cut only when its heading is exactly `## Evidence` or `## Responses`. A writer who titles it `## Evidence (round 2)` would have it passed through uncut. That matches C1 as written.
- `## Responses` runs to the next `## ` or `=== ` line, so a trailer such as `STATUS: READY-FOR-CRITIC` directly after it is cut too. This happens in the fixture. Stored specs pass through `spec add`, and I did not check whether it strips that trailer. Either way, no role in scope reads the trailer.
- The diff compares the stored files line by line with `splitlines()`. A missing final newline therefore does not show up as a change. This only affects the size comparison by a byte or two.
- factory: markers added: none.

## Out-of-scope observations

- None that need action. Parts A, B and D of T-0030 are untouched: agent definitions, effort, and documents including the design doc routing table and changelog.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command printed its expected lines on the head, the full suite passed there, and the new tests failed before the change for the intended reason.
ESCALATIONS: none. One process note, not an escalation: the session's permission classifier refused to run the spec's GIVEN block when I extracted it from input.md with `sed`. I wrote the two fixtures this sub-ticket uses with the Write tool instead, after reading them in full, and confirmed with `diff` that they match the spec text byte for byte. The other six GIVEN fixtures belong to other sub-tickets and were not written.
