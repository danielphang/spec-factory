## Proposed change
NEEDS-SPLIT. The four parts below are the seams. A, B and C are independent of each other. D depends on all three and lands last. One changelog entry covers all four.

**A. A registered definition for every role, and a fence on the checkers** (`agents/`, `factory/workflows/*.js`, `factory/cli.py`).
1. Add `agents/factory-implementer.md`, `agents/factory-reviewer.md` and `agents/factory-verifier.md`. Their frontmatter follows the existing files: `name` equal to the file name without `.md`, a one-line `description`, and `model` taken from the template's `models:` (implementer `opus`, reviewer `fable`, verifier `opus`). The implementer's `tools` is `Read, Grep, Glob, Bash, Write, Edit`. The reviewer's and verifier's `tools` is `Read, Grep, Glob, Bash, Write`.
2. The reviewer and verifier frontmatter also declares `hooks.PreToolUse`, with one entry whose `matcher` is `Write|Edit|MultiEdit|NotebookEdit` and one `type: command` hook. The command:
   - runs under `sh`, using `python3` from `PATH`;
   - reads the hook JSON from stdin and takes `tool_input.file_path`, or `tool_input.notebook_path`;
   - resolves the path with `os.path.realpath`;
   - exits 0 only when the resolved path matches `/runs/run-<digits>-<role>/output.md` or `/runs/run-<digits>-<role>/scratch/<one or more characters>`, where `<role>` is that file's own role;
   - otherwise exits 2, with a one-line stderr message naming the two allowed places.

   Any failure to decide must also exit 2, for example a shell form like `python3 -c '…' || exit 2`.
3. Replace the body of `agents/factory-triage.md`, `factory-spec-writer.md`, `factory-spec-critic.md` and `factory-planner.md` with the same single paragraph the three new files use. It says to read `system-prompt.txt` in the run directory that holds the input file before anything else, because it holds the role and rules for the run, preamble first. No body may contain a `ROLE:` line. Their frontmatter is unchanged.
4. `run start` gains `--inline` (a flag). It records `inline: true` with the flag and `inline: false` without it in `meta.yaml`. Both workflow scripts add `--inline` to their `run start` command when `INLINE` is set. Update the scripts' `inlineRoles` comments: inline mode is the fallback for a session that has not registered the definitions, and it runs with no tool fence.
5. `init` keeps its rule of copying only missing files. Its log line and its "restart the session so the agents register" message do not change.

**B. Effort per role** (`factory/cli.py`, `factory/instance.template.yaml`, `factory/workflows/*.js`).
1. `run_start` reads `cfg.get("effort")`. Absent or null means an empty map. It refuses with exit 2 before reserving a run id, so nothing is written, when the value is not a mapping, when a key is not one of `ROLES`, or when a value is not one of `low`, `medium`, `high`, `xhigh`, `max`. The refusal names the bad key or value.
2. `run_start` records `effort: <the role's level or null>` in `meta.yaml` and adds `"effort"` (the same value) to its JSON output.
3. In `runRole` in both workflow scripts, the real role call (not the stub call) passes `effort: start.effort` when that is set, and passes no `effort` key otherwise. The store-command agent and stub calls keep `effort: 'low'`.
4. `factory/instance.template.yaml`: add a commented example `# effort: {verifier: high}` after `models:`. Explain in a comment that an absent role gets the session default, and list the allowed levels. Add no live key, so a new instance's keys are unchanged.

**C. Each role's input cut to the sections it uses** (`factory/compose.py`).
1. Add a helper that returns a spec text without its `## Evidence` and `## Responses` sections. A section starts at a line `## Evidence` or `## Responses`, ignoring trailing spaces. It runs up to, but not including, the next line that starts with `## ` or `=== `. Lines inside a fenced code block do not count as that next line.
2. Use the cut text for the planner's "Approved spec", for the implementer's, reviewer's and verifier's "Parent spec", and for the parent-close verifier's spec. Each heading keeps its current words, so the parent-close heading still contains "verify every scenario on main". Each heading adds that the Evidence and Responses sections are left out, and gives the absolute path of the full spec file. `input_sources` keeps listing the same `specs/<id>/v<n>.md` paths. The sub-ticket text, `specs/<id>/subticket.md`, is not cut.
3. Round-2 critic: in place of the whole previous version, build `difflib.unified_diff` from `v<n-1>` to `v<n>` with 3 lines of context, labelled with the two store paths. Use it when its byte length is less than `v<n-1>`'s. Otherwise add the previous version whole, as today. Name in the heading which one the input holds. `input_sources` is unchanged.
4. The triage and spec writer inputs, the critic's current spec, and every other input are unchanged.

**D. Documents** (`docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md`, `README.md`, `.factory/README.md`).
1. `docs/design.md` routing table, "Receives" column:
   - The Spec writer → Critic row's round 2+ input says the previous spec version arrives as a diff when that is smaller, and whole otherwise.
   - The "Human spec gate | Approved", "Planner | PLANNED", "Implementer | READY-FOR-REVIEW" and "Merge gate | CI green" rows each say the spec arrives without its Evidence and Responses sections.
2. `dev/build-harness.spec.md`: make the critic's round-2 input in H's intake step (the sentence with "round ≥ 2: prior findings") match the design doc, naming the diff.
3. `docs/changelog.md`: one entry, the next number with no gap, after any entry already on `main`. It names the seven definitions (`factory-implementer` among them), the reviewer and verifier fence and its limit, the `agent call failed` park, `inlineRoles` as the fallback, the `effort` map, and the inputs without Evidence and with a diff for a round-2 critic.
4. `README.md`, following "Maintaining this page":
   - "Starting a run": replace the "Add `inlineRoles: true` on every target for now" passage. Say that roles run as their registered agents, and when inline mode is still needed. Say what happens without the definitions: the `agent call failed` park, or a stop at the first store command. Give how to recover (Decisions).
   - Describe the checker fence and its limit, with the `python3` and workspace-trust requirement.
   - Describe the `effort:` map (with that literal key in backticks) and remove the "Per-role effort settings" bullet from the list of what is not built.
   - Re-derive figures; add this ticket and issues #24 and #22 under "Related work and history"; bump the status date.
5. `.factory/README.md` "Running": dispatch without `inlineRoles`, and drop "this repo adds no `.claude/agents/`". Keep `inlineRoles: true` only for a session started before `.claude/agents/` was installed.

## Tests to change
- `tests/factory/test_instance.py::test_init_creates_the_instance_at_the_git_top_level` asserts `len(agents) == 6` for `agents/factory-*.md`. Part A makes it nine, so the assertion becomes `== 9`. The rest of that test, that every template is copied byte for byte and the restart message is printed once, is unchanged.

