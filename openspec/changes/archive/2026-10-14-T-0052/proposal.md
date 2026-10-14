## Problem

Four of the factory's six role agent definitions cannot be loaded by Claude Code, and fixing them in this repository would not fix the copies already installed in a target repository.

A role agent template is a Claude Code agent definition kept in `agents/`: a Markdown file whose YAML header (its frontmatter) gives the agent's name, a one-line description, the model it runs on and the tools it may use. `factory init`, the command that sets a repository up to use the factory (a target), copies each template into that repository's `.claude/agents/`, where Claude Code registers it when a session starts.

In the planner, spec critic, spec writer and triage templates, the description is an unquoted YAML value that contains a colon followed by a space (`Spec factory Planner role: splits …`). YAML reads that as the start of a second key, so the whole header fails to parse. The operator saw Claude Code report this for the spec writer on 2026-10-13. No run has failed yet, because every workflow run passes `inlineRoles: true` (run every role as a general-purpose agent that reads its prompt from a file) and `factory drive` (the shell-driven runner) starts each role as a `claude -p` process with its prompt inline. Any run that uses the registered agents would fail at the first of these four roles.

Nothing in the harness's test suite reads these headers, which is how the break went unnoticed. And `factory init` copies a template only when the target has no file of that name, so a target that already has a broken copy keeps it after the template is fixed, and nothing tells its operator. The Nanobot target, the factory's other live user, holds byte-identical copies of all six templates, broken four included.

This change quotes the four descriptions, adds a suite test that parses every template's header, and makes `factory init` name each installed copy that differs from its template while still leaving that copy as it is.

## Evidence

- Parsing each template's header with PyYAML `safe_load` (lines between the opening `---` and the next `---`), run with `uv run --frozen python` under the harness's running-code wrapper (which gives the command a throwaway HOME, so it cannot write the operator's real home directory), gives:

  | Template | Result |
  |---|---|
  | `factory-clerk.md`, `factory-stub.md` | parses; keys `description, model, name, omitClaudeMd, tools` |
  | `factory-planner.md` | `mapping values are not allowed here`, line 2 column 39 |
  | `factory-spec-critic.md` | same error, line 2 column 43 |
  | `factory-spec-writer.md` | same error, line 2 column 43 |
  | `factory-triage.md` | same error, line 2 column 38 |

  Each column is the `: ` right after `Planner role`, `Spec critic role`, `Spec writer role` or `Triage role`: the place YAML starts reading a second key.
- The suite does not catch a broken header. I copied this checkout (`git archive HEAD`) into a throwaway repo, broke the clerk's header with `Spec factory store clerk: broken.` and removed the stub's `tools:` line, and ran the whole suite there: `584 passed in 93.22s`. The suite passes with two more broken templates.
- `factory/setup.py:180-184` (`init_cmd`): the loop over `instance.AGENTS.glob("factory-*.md")` copies a template only `if not (dest / src.name).exists()`. An existing copy is never read. The command's JSON output lists only the copies it created, under `agents` (line 204).
- `cmp` of each `agents/*.md` against `~/dev/nanobot-upstream/.claude/agents/` (read only): all six print `same`. This repository has no `.claude/agents/` of its own.
- `git log -- agents/`: `9b45041` (2026-10-01) and `f5d8203` (2026-10-03). The templates have not changed since.
- Why nothing failed: `factory/workflows/intake.js:29-32` reads `inlineRoles` and, when set, runs every role as general-purpose. README line 706 tells the operator to pass `inlineRoles: true` on every target.
- README line 463 says `.claude/agents/factory-*.md` is written by "`factory init`, when they are missing", and step 1 of "Adopting the factory in a repo" (README lines 579-587) says init "copies the role agents into `.claude/agents/`". Neither mentions a copy that differs. `docs/design.md` does not describe init's agent copies at all (grep for `.claude` finds only the agent-hosts table at line 880).
- Prototype, in my scratch directory only: the four descriptions double-quoted, a parametrized frontmatter test, and a four-line report in `init_cmd`. The five store-setup scenarios below printed their expected result on the prototype and their "today" result on this checkout. The prototype did not edit README or the changelog, so I ran the three harness-docs scenarios on this checkout only. The full suite on the prototype printed `590 passed`: the 584 existing tests plus six new cases, with no existing test changed.
- Capabilities read: `store-setup` and `harness-docs`, both given in full in my input.
- Not verified: Claude Code's own frontmatter parser. The failure is confirmed with PyYAML. That Claude Code rejects these files, and accepts a double-quoted description, rests on the operator's report and on standard YAML.

## Root cause

- `agents/factory-planner.md`, `agents/factory-spec-critic.md`, `agents/factory-spec-writer.md`, `agents/factory-triage.md`, line 2: a plain (unquoted) YAML scalar containing `: `.
- `tests/factory/`: no test reads `agents/*.md` frontmatter. `tests/factory/test_instance.py:57-59` compares the copied bytes with the templates. That passes whatever the bytes are.
- `factory/setup.py` `init_cmd`, lines 180-184: the copy loop has no branch for an existing copy, so it never compares one.

## Out of scope

- Refreshing Nanobot's four broken copies. That repo is a protected path here. The Driver (the session that runs the Nanobot target) does it after this merges; see Operator steps.
- Overwriting, deleting or refusing on a differing copy. `factory init` keeps its rule of never touching an existing copy.
- Comparing files in `.claude/agents/` that have no template (for example a target's own `factory-foo.md`).
- Checking that each template's `name` matches its file name, or that its `model` and `tools` values are valid. The request asks only that the header parse and carry the four keys.
- Registering agents for the build roles (issue #24), and the advice to pass `inlineRoles: true`.
- `docs/design.md`, which does not describe init's agent copies.
- `dev/issues.md`, which the operator updates when the issue closes.

## Open questions

none

## Decisions

- The four descriptions are wrapped in double quotes with their words unchanged. Rejected: rephrasing them without `: `, which changes what each agent's description says.
- The suite test checks every `agents/*.md`, one case per template, and each failure names its template. It requires a parseable header that is a mapping with `name`, `description`, `model` and `tools`.
- `factory init` reports an existing copy that differs from its template in a new JSON field, `stale_agents` (each copy's path, as `agents` gives created copies' paths), and with one stderr line per copy naming the copy and its template. The exit stays 0 and the copy is left byte for byte as it was. Rejected: overwriting it, which would discard an operator's deliberate edit. Rejected: refusing with exit 2, because a stale copy does not stop a run that uses `inlineRoles`.
- "Differs" means any byte difference. A copy the operator edited on purpose is reported too: that is a report, not a refusal.
- The comparison runs only where init installs copies: for the target's own store (the directory under the target's `.factory/` that holds the factory's tickets and run records). An init pointed at another store by the `FACTORY_STATE` environment variable, as the tests do with a throwaway store, does not read `.claude/agents/`, and its `stale_agents` is `[]`.
- A run of init that only reports differing copies writes no `store.initialised` log event and prints no "restart the session" line, because it wrote nothing.
- Standing rule for later tickets: `factory init` never overwrites a target's existing agent copy; it reports one that differs from its template.

## Risk

Small. The template change alters four header lines that no run reads today (every run uses `inlineRoles` or `factory drive`). The init change adds one output field and stderr lines. It changes no exit code, writes no new file, and the existing init tests that read the JSON output still pass on the prototype (590 passed). Callers that read init's JSON by key (the tests, the operator) are unaffected by an added key.

The merge moves the harness revision, because `agents/` and `factory/` are harness paths. The factory runs from a separate runtime checkout pinned to an accepted harness revision, so no target runs the new code until the operator moves that checkout to the merged revision and accepts it with `--accept-harness` (the usual upgrade step).

`README.md` is at 1,106 lines against its 1,110-line budget. The README edits below must add at most four lines net.

Protected paths: `agents/**`, `factory/**`

## Operator steps

- After the merge, and after the factory's runtime checkout (the separate worktree the factory runs from) has been moved to the merged revision and accepted with `--accept-harness`, the Driver (the session that runs the Nanobot target) copies the four fixed templates (planner, spec-critic, spec-writer, triage) from `~/dev/spec-factory/agents/` over the copies in `~/dev/nanobot-upstream/.claude/agents/` and commits them there. Check, read only: `for f in ~/dev/spec-factory/agents/factory-*.md; do cmp -s "$f" ~/dev/nanobot-upstream/.claude/agents/$(basename "$f") && echo same || echo "differs $(basename "$f")"; done` prints `same` six times.

