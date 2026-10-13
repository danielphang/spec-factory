## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the
  P0 walking skeleton, frozen as history from building the harness, which no change updates;
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose
block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0520-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0520-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v2)

=== proposal.md
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

=== design.md
## Proposed change

A. Templates. In `agents/factory-planner.md`, `agents/factory-spec-critic.md`, `agents/factory-spec-writer.md` and `agents/factory-triage.md`, change line 2 from `description: <text>` to `description: "<text>"`. The text stays character for character the same. None of the four contains a `"` or a `\`, so no escaping is needed. Change nothing else in these files, and do not touch `factory-clerk.md` or `factory-stub.md`.

B. Suite test. Add a new file, `tests/factory/test_agent_templates.py`. Add one test, parametrized over `sorted((REPO / "agents").glob("*.md"))` with the file name as the case id (`REPO` from `tests/factory/_cli.py`). Each case:
   1. asserts line 1 is `---`;
   2. takes the lines up to the next `---` and parses them with `yaml.safe_load`;
   3. asserts the result is a dict containing `name`, `description`, `model` and `tools`.

   Each assertion message names the template. A YAML error is left to fail the case (pytest shows it under the case id), not caught. Do not hard-code the list of templates: a seventh template must be checked without editing the test.

C. `factory init` report, in `factory/setup.py` `init_cmd`.
   1. Next to `agents: list[str] = []`, add `stale: list[str] = []`.
   2. In the copy loop (lines 180-184), add an `elif` for an existing copy. When `(dest / src.name).read_bytes() != src.read_bytes()`, append `str(dest / src.name)` to `stale` and print one line to stderr: `factory init: <copy path> differs from its template <template path>; left as it is`.
   3. Never write the copy. Add `"stale_agents": stale` to the final `out({...})` beside `"agents"`. Leave the `store.initialised` event condition and the "restart the session" line as they are.

   In the same new test file, add suite tests for this: an edited copy is listed and kept; a deleted copy is created and not listed; matching copies give `stale_agents == []`. Build each target with the shared helpers in `tests/factory/_cli.py` (`git_repo`, `cli`, `js`), the way `tests/factory/test_instance.py`'s `target` fixture does, and add no new setup code. `_cli.py` says a test file imports helpers from there, never from another test file, so do not import that fixture. Do not add these tests to `test_instance.py`: they overlap `test_init_is_idempotent_and_creates_only_what_is_missing` there, but leave that test as it is.

D. Documents.
   1. `README.md` line 463, the `.claude/agents/factory-*.md` row's "Written by" cell: keep "`factory init`, when they are missing" and add that init reports a copy that differs from its template and leaves it. The row must contain the words `differs from its template`.
   2. Step 1 of "Adopting the factory in a repo" (README lines 579-587): add one sentence saying a copy that differs from its template is listed under `stale_agents` and named on stderr, and is never overwritten.
   3. Net README growth: at most four lines. README's "Maintaining this page" asks a change to a command to bump the date in the status header (line 9, now "Current state as of 2026-10-13"): set it to the merge date if that differs. This changes no line count.
   4. `docs/changelog.md`: append one entry, the next number after the last, starting `<n>. After issue #108 (2026-10-13), `. It says the four headers did not parse and are now quoted, that the suite now parses every template's frontmatter, and that init reports a differing copy in `stale_agents` without overwriting it. It also says Nanobot's copies are refreshed by its Driver. The entry must contain the words `frontmatter`, `stale_agents` and `Nanobot`. If another ticket takes the next number first, take the next free one: the entries must stay numbered without a gap.

Size: about 4 template lines, about 7 lines in `setup.py`, a new test file of about 50 lines, 2 README lines and 1 changelog line.

## Tests to change

none. No existing test pins the old behaviour. `tests/factory/test_instance.py:123` and `:135` assert `agents` on runs where every copy matches or one was deleted, and `tests/factory/test_store_branch.py:269` reads named keys only. On the prototype the full suite passed unchanged (590 passed).

=== specs/store-setup/spec.md
## ADDED Requirements

### Requirement: Every role agent template has valid frontmatter
Each `agents/*.md` template's frontmatter MUST parse as a YAML mapping that carries `name`, `description`, `model` and `tools`. The four templates whose descriptions did not parse SHALL keep their description's words and every other line unchanged.

#### Scenario: Every role agent template's frontmatter parses and carries name, description, model and tools
Run from the repository root after `uv sync --frozen`.
- WHEN `(for f in agents/*.md; do echo "$(basename $f) $(sed -n '2,/^---$/p' $f | sed '$d' | uv run --frozen python -c 'import sys, yaml; m = yaml.safe_load(sys.stdin); print("keys=" + ("ok" if {"name", "description", "model", "tools"} <= set(m) else "missing"))' 2>/dev/null || echo keys=unparsed)"; done)`
- THEN it prints exactly `factory-clerk.md keys=ok`, `factory-planner.md keys=ok`, `factory-spec-critic.md keys=ok`, `factory-spec-writer.md keys=ok`, `factory-stub.md keys=ok`, `factory-triage.md keys=ok`, one per line

#### Scenario: The four fixed templates keep their description's words and every other line
`525d73f` is `main` before this change.
- WHEN `(B=525d73f; for f in planner spec-critic spec-writer triage; do p=agents/factory-$f.md; old=$(git show $B:$p | sed -n 's/^description: //p'); new=$(sed -n '2,/^---$/p' $p | sed '$d' | uv run --frozen python -c 'import sys, yaml; print(yaml.safe_load(sys.stdin)["description"])' 2>/dev/null); echo "$f text=$([ -n "$new" ] && [ "$old" = "$new" ] && echo same || echo changed) rest=$(diff <(git show $B:$p | grep -v '^description: ') <(grep -v '^description: ' $p) >/dev/null && echo same || echo changed)"; done; echo "others=$(git diff --quiet $B -- agents/factory-clerk.md agents/factory-stub.md && echo same || echo changed)")`
- THEN it prints exactly `planner text=same rest=same`, `spec-critic text=same rest=same`, `spec-writer text=same rest=same`, `triage text=same rest=same`, then `others=same`, one per line

### Requirement: The harness suite fails on a role agent template with broken frontmatter
The harness suite MUST fail when any `agents/*.md` template's frontmatter does not parse or lacks one of `name`, `description`, `model` and `tools`, and its output SHALL name each such template.

#### Scenario: The suite fails on a template with broken frontmatter and names it
Copies the committed tree to a throwaway repo, breaks the clerk's header and drops the stub's `tools:` line, and runs the whole suite there with this checkout's environment. About 100 seconds.
- WHEN `(export TMPDIR=$(mktemp -d /tmp/sf.XXXXXX); T=$(cd "$(mktemp -d)" && pwd -P); R=$PWD; mkdir $T/c && git archive HEAD | tar -x -C $T/c && ln -s $R/.venv $T/c/.venv && cd $T/c && git init -q -b main && printf '.venv\n' >> .git/info/exclude && sed 's/^description: Spec factory store clerk\./description: Spec factory store clerk: broken./' $R/agents/factory-clerk.md > agents/factory-clerk.md && grep -v '^tools:' $R/agents/factory-stub.md > agents/factory-stub.md && git add -A && git -c user.email=f@x -c user.name=f commit -qm broken && .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory > $T/log 2>&1; rc=$?; echo "suite=$([ $rc -eq 0 ] && echo passed || echo failed) clerk=$(grep -c 'factory-clerk' $T/log | awk '{print ($1 > 0)}') stub=$(grep -c 'factory-stub' $T/log | awk '{print ($1 > 0)}')"; rm -rf $TMPDIR)`
- THEN it prints exactly `suite=failed clerk=1 stub=1`

### Requirement: init reports an agent copy that differs from its template and never overwrites it
When `factory init` runs for an instance's own store, it SHALL list each existing `.claude/agents/factory-*.md` copy whose bytes differ from its template under `stale_agents` in its JSON output and name it on stderr, MUST leave that copy unchanged and exit 0, and SHALL still create a missing copy without listing any matching copy.

#### Scenario: init reports an edited agent copy and leaves it as it is
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf 'local edit\n' >> .claude/agents/factory-planner.md && cp .claude/agents/factory-planner.md $T/kept && $B init >$T/out 2>$T/err; rc=$?; echo "exit=$rc stale=$(python3 -c 'import json, sys; o = json.load(sys.stdin); print(",".join(p.rsplit("/", 1)[-1] for p in o["stale_agents"]) if "stale_agents" in o else "absent")' < $T/out) kept=$(cmp -s $T/kept .claude/agents/factory-planner.md && echo yes || echo no) named=$(grep -c 'factory-planner\.md' $T/err) others=$(grep -v 'factory-planner\.md' $T/err | grep -c .)")`
- THEN it prints exactly `exit=0 stale=factory-planner.md kept=yes named=1 others=0`

#### Scenario: init still creates a missing agent copy and lists no matching copy
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; A=$PWD/agents; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .claude/agents/factory-triage.md && $B init >$T/out 2>$T/err; rc=$?; echo "exit=$rc $(python3 -c 'import json, sys; o = json.load(sys.stdin); print("created=" + ",".join(p.rsplit("/", 1)[-1] for p in o["agents"]) + " stale=" + str(len(o.get("stale_agents", []))))' < $T/out) same=$(for f in $A/factory-*.md; do cmp -s $f .claude/agents/$(basename $f) && echo x; done | grep -c .) differs=$(grep -c 'differs' $T/err)")`
- THEN it prints exactly `exit=0 created=factory-triage.md stale=0 same=6 differs=0`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the template fix and init's report of a differing agent copy
`README.md`'s `.claude/agents/factory-*.md` row SHALL say that init reports a copy that differs from its template, and step 1 of "Adopting the factory in a repo" SHALL name `stale_agents`. `docs/changelog.md` SHALL hold one entry for issue #108, numbered without a gap, that names `frontmatter`, `stale_agents` and `Nanobot`. README MUST stay within its 1,110-line budget, and both documents MUST carry no whitespace error.

#### Scenario: README describes init's report of a differing agent copy
- WHEN `(echo "row=$(grep '^| .\.claude/agents/factory-\*\.md. |' README.md | grep -c 'differs from its template') step=$(sed -n '/^### Adopting the factory in a repo/,/^2\. /p' README.md | tr '\n' ' ' | grep -c 'stale_agents') missing=$(grep '^| .\.claude/agents/factory-\*\.md. |' README.md | grep -c 'when they are missing')")`
- THEN it prints exactly `row=1 step=1 missing=1`

#### Scenario: The changelog records issue 108 in one entry without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #108 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e frontmatter -e stale_agents -e Nanobot | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `3`

#### Scenario: README stays within its line budget and both documents pass the whitespace check
- WHEN `(E=$(git hash-object -t tree /dev/null); echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1110 ? "within" : "over")}')"; git diff --check $E HEAD -- README.md docs/changelog.md >/dev/null; echo "check=$?")`
- THEN it prints exactly `readme=within`, then `check=0`

=== verification.md
## Acceptance

Run every scenario from the repository root after `uv sync --frozen`, inside the harness's running-code wrapper (a throwaway HOME). I ran each one on this checkout (`525d73f`). I also ran the five store-setup scenarios on a prototype of the change in my scratch directory, where each printed its THEN exactly. The prototype had no README or changelog edits, so the three harness-docs scenarios were run on this checkout only.

- Every role agent template's frontmatter parses and carries name, description, model and tools → NEW. Today the planner, spec-critic, spec-writer and triage lines print `keys=unparsed`.
- The four fixed templates keep their description's words and every other line → NEW. Today each of the four prints `text=changed rest=same`, because its description does not parse. `others=same` already holds.
- The suite fails on a template with broken frontmatter and names it → NEW. Today it prints `suite=passed clerk=0 stub=0`: the suite passes with both templates broken.
- init reports an edited agent copy and leaves it as it is → NEW. Today it prints `exit=0 stale=absent kept=yes named=0 others=0`: there is no `stale_agents` field and nothing on stderr.
- init still creates a missing agent copy and lists no matching copy → REGRESSION. Today it prints `exit=0 created=factory-triage.md stale=0 same=6 differs=0`.
- README describes init's report of a differing agent copy → NEW. Today it prints `row=0 step=0 missing=1`.
- The changelog records issue 108 in one entry without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `0`, then `0`.
- README stays within its line budget and both documents pass the whitespace check → REGRESSION. Today it prints `readme=within`, then `check=0`; README is at 1,106 lines.

## Responses

- [BLOCKING] Operator steps leaves "the Driver" and "the runtime upgrade" unglossed → FIXED. The step now opens with both glosses: the runtime checkout is "the separate worktree the factory runs from", moved to the merged revision and accepted with `--accept-harness`, and the Driver is "the session that runs the Nanobot target". I also replaced the step's check. v1 had the operator run `factory init` in Nanobot, which writes to a live target. The new check is a read-only `cmp` loop over the six templates, which prints `same` six times once the copies are refreshed. I ran it on this checkout: it prints `same` six times today, because the templates are not yet fixed. Risk now glosses the upgrade step the same way.
- [SHOULD-FIX] "fresh-HOME wrapper", "instance's own store" and "throwaway store" go unglossed → FIXED. Evidence's first bullet now says "the harness's running-code wrapper (which gives the command a throwaway HOME, so it cannot write the operator's real home directory)". Decisions bullet 5 now says "the target's own store (the directory under the target's `.factory/` that holds the factory's tickets and run records)" and explains `FACTORY_STATE` as the environment variable that points init at another store. verification.md's opening line uses the same gloss.
- [NIT] Part D does not bump README's status-header date → FIXED. D.3 now says to set line 9's "Current state as of" date to the merge date if it differs, and notes this changes no line count.
- Out-of-scope observation (new init tests overlap `test_instance.py`) → FIXED in design part C. The new tests build their target with `git_repo`, `cli` and `js` from `tests/factory/_cli.py`, as the `target` fixture does. They do not import from another test file, because `_cli.py`'s docstring forbids that. They do not edit `test_instance.py`, an existing test this spec does not list under Tests to change.

The base is unchanged since v1: `main` is still `525d73f`, and `git diff --stat 525d73f HEAD` over `agents`, `factory/setup.py`, `README.md`, `docs/changelog.md` and `tests/factory` is empty. So the "today" results in Acceptance, which both the critic and I ran on `525d73f`, still hold.

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL hold entry 51 covering every part and stay numbered without a gap, and `README.md` SHALL describe the new `resolve` behaviour and relative environment paths.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL hold one entry for issue #45 recording the guard, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store.

#### Scenario: The changelog records the guard in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #45 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `design=1 dirs=1`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule. `docs/changelog.md` SHALL hold one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch, `factory store migrate`, the `git clean -ffdx` hazard and a checkout from before the move, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location.

#### Scenario: The design doc names the store branch and the path rule
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
- THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`

#### Scenario: The changelog records the store branch in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The README describes the store branch and the move
`old_cost` joins the page into one line first, because the retired clause is wrapped across two lines. `old_refs` counts only the places that give the live store's location, so a how-to may still name the path a store moves from.
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`

### Requirement: The planner labels checks per sub-ticket and may list tests an earlier sibling added
Every copy of the planner prompt (the `docs/design.md` §4 block, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`) SHALL tell the planner to label each check against the sub-ticket's own base, to name interim tests, and to list a sibling-added test as `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``; it MUST no longer say to label checks "the same way", and the design block and its `docs/prompts/` copy SHALL stay byte-identical.

#### Scenario: Every planner copy labels per sub-ticket and lists sibling tests
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-planner.txt; sed -n '/^## 4\. Planner/,/^## 5\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/04-planner.md factory/prompts/planner.md; do echo "own=$(grep -c "against this sub-ticket's own base" $f) sibling=$(grep -cF '(added by <sibling ID>)' $f) interim=$(grep -c '^  Interim tests: ' $f) copied=$(grep -c 'labelled NEW or REGRESSION the same way' $f)"; done; cmp -s $X docs/prompts/04-planner.md && echo verbatim || echo differs)`
- THEN it prints three lines, each exactly `own=1 sibling=1 interim=1 copied=0`, then `verbatim`

### Requirement: The spec writer lists the tests a decision overturns, and the critic checks for one left off
Every copy of the spec writer prompt SHALL carry the RULES bullet that starts `- Tests a decision overturns: `, and every copy of the critic prompt SHALL say under rubric 1 that a test pinning the old behaviour and `missing from "Tests to change" is a finding`.

#### Scenario: Every spec writer and critic copy carries the decision-overturns rule
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-sw.txt; for h in '2\. Spec writer' '3\. Spec critic'; do sed -n "/^## $h/,/^## [0-9]/p" docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p"; done > $X; echo "design: writer=$(grep -c '^- Tests a decision overturns: ' $X) critic=$(grep -c 'from "Tests to change" is a finding' $X)"; echo "docs/prompts: writer=$(grep -c '^- Tests a decision overturns: ' docs/prompts/02-spec-writer.md) critic=$(grep -c 'from "Tests to change" is a finding' docs/prompts/03-spec-critic.md)"; echo "factory/prompts: writer=$(grep -c '^- Tests a decision overturns: ' factory/prompts/spec_writer.md) critic=$(grep -c 'from "Tests to change" is a finding' factory/prompts/critic.md)")`
- THEN it prints exactly `design: writer=1 critic=1`, then `docs/prompts: writer=1 critic=1`, then `factory/prompts: writer=1 critic=1`

### Requirement: The preamble and the code reviewer accept a checked sibling entry
Every copy of the preamble SHALL allow an existing test listed `in your sub-ticket as added by an earlier sibling`, and every copy of the code reviewer prompt SHALL not block a test `the sub-ticket lists it there as added by an earlier sibling`.

#### Scenario: Every preamble and reviewer copy accepts a sibling entry
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-pr.txt; for h in 'Shared preamble' '6\. Code reviewer'; do sed -n "/^## $h/,/^## [0-9A-Z]/p" docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p"; done > $X; echo "design: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' $X) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' $X)"; echo "docs/prompts: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' docs/prompts/00-preamble.md) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' docs/prompts/06-code-reviewer.md)"; echo "factory/prompts: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' factory/prompts/preamble.md) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' factory/prompts/reviewer.md)")`
- THEN it prints exactly `design: guard=1 review=1`, then `docs/prompts: guard=1 review=1`, then `factory/prompts: guard=1 review=1`

### Requirement: Role runs receive the new rules
The system prompt that `run start` writes for a planner, spec writer and critic run SHALL contain that role's new rule and the new preamble sentence.

#### Scenario: Planner, spec writer and critic runs get the new rules in their system prompts
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2 3; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-planner >/dev/null; bin/factory ticket set T-0002 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0003 status=ready-for-critic >/dev/null; for p in planner:T-0001 spec_writer:T-0002 critic:T-0003; do bin/factory run start --role ${p%%:*} --ticket ${p##*:} >/dev/null 2>&1; done; P=$(ls $FACTORY_STATE/runs/*-planner/system-prompt.txt); W=$(ls $FACTORY_STATE/runs/*-spec_writer/system-prompt.txt); C=$(ls $FACTORY_STATE/runs/*-critic/system-prompt.txt); echo "planner own=$(grep -c "against this sub-ticket's own base" $P) sibling=$(grep -cF '(added by <sibling ID>)' $P) guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' $P) writer=$(grep -c '^- Tests a decision overturns: ' $W) critic=$(grep -c 'from "Tests to change" is a finding' $C)")`
- THEN it prints exactly `planner own=1 sibling=1 guard=1 writer=1 critic=1`

### Requirement: The documents record the sibling-tests check
`docs/design.md` SHALL describe the check in a paragraph that starts `**Tests a sibling added.**`, in piece 8 and in the spec approval gate row, and SHALL no longer call the gate's list the only authorization to alter an existing test; `docs/changelog.md` SHALL hold an entry for issue #40 and stay numbered without a gap; and `README.md` SHALL describe the check and the new `--ruling` case.

#### Scenario: The design doc describes the check
- WHEN `(echo "piece8=$(grep '^| 8 |' docs/design.md | grep -c 'added by that sibling') gate=$(grep '^| Spec approval |' docs/design.md | grep -c 'a test an earlier sibling added') stale=$(grep -c 'which is the only authorization to alter an existing test' docs/design.md) check=$(grep -c '^\*\*Tests a sibling added\.\*\*.*BLOCKED from harness:' docs/design.md)")`
- THEN it prints exactly `piece8=1 gate=1 stale=0 check=1`

#### Scenario: The changelog records issue 40's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #40 ' docs/changelog.md | grep -oF -e 'own base' -e 'added by' -e 'BLOCKED from harness' -e 'Decision' -e 'critic rubric 1' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the sibling tests check and its ruling
- WHEN `(echo "built=$(grep -c '^- \*\*Sibling tests check\.\*\*' README.md) ruling=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'a test no merged sibling added')")`
- THEN it prints exactly `built=1 ruling=1`

### Requirement: The documents record the declared-path rule
The "## 5. Implementer" and "## 7. Verifier" blocks of `docs/design.md` SHALL carry the declared-path rule and stay verbatim copies of `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`. The run copies under `factory/prompts/` SHALL differ from those files only by the fills they had on `main`. `docs/changelog.md` SHALL hold one entry for issue #49, numbered without a gap.

#### Scenario: The design blocks and their copies carry the rule and stay in step
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); for r in "5. Implementer|05-implementer.md|implementer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) rule=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -c 'A protected path the sub-ticket declares is not an escalation') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `implementer copy=SAME rule=1 fill=unchanged`, then `verifier copy=SAME rule=1 fill=unchanged`. `copy=SAME`: the design block equals its `docs/prompts/` file. `rule=1`: that file carries the rule. `fill=unchanged`: the run copy under `factory/prompts/` differs from the documented copy only where it did on `main`.

#### Scenario: The changelog records the declared-path rule in a contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#49' | grep -c 'ESCALATIONS')`
- THEN it prints `CONTIGUOUS`, then `1`

### Requirement: The documents record the small-change lane
`docs/changelog.md` SHALL hold one entry for issue #48 recording the lane, numbered without a gap. `docs/design.md` and `README.md` SHALL describe the whole-spec sub-ticket and gate-command paths.

#### Scenario: The changelog records the small-change lane in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #48 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e 'paths' -e SKIPPED -e 'plan whole-spec' -e NEEDS-SPLIT -e seams | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

#### Scenario: The design doc and README describe both skips
- WHEN `(echo "design=$(grep -c 'whole-spec' docs/design.md | awk '{print ($1 > 0)}') gate=$(grep '^| 11 | Gate runner' docs/design.md | grep -c 'SKIPPED') readme=$(grep -c 'plan whole-spec' README.md | awk '{print ($1 > 0)}') skipped=$(grep -c 'SKIPPED' README.md | awk '{print ($1 > 0)}') stale=$(grep -c 'The build workflow runs the planner, which' README.md)")`
- THEN it prints exactly `design=1 gate=1 readme=1 skipped=1 stale=0`

### Requirement: Every role is told to wait for its own commands
Every copy of the shared preamble SHALL carry the bullet that starts `- Run every command in the foreground and wait for it to finish.` and says `Never end your turn while a command you started is still running`. The design block and both files MUST stay byte-identical, and every role run's system prompt SHALL carry the bullet.

#### Scenario: Every preamble copy carries the wait rule and the copies stay identical
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-pre.txt; sed -n '/^## Shared preamble/,/^## [0-9]/p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/00-preamble.md factory/prompts/preamble.md; do echo "fg=$(grep -c '^- Run every command in the foreground and wait for it to finish\.$' $f) end=$(tr '\n' ' ' < $f | tr -s ' ' | grep -c 'Never end your turn while a command you started is still running')"; done; cmp -s $X docs/prompts/00-preamble.md && cmp -s docs/prompts/00-preamble.md factory/prompts/preamble.md && echo verbatim || echo differs)`
- THEN it prints three lines, each exactly `fg=1 end=1`, then `verbatim`

#### Scenario: Implementer, reviewer and verifier run prompts carry the wait rule, and only the reviewer's carries the judge-the-diff rule
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer reviewer verifier; do P=$(prompt $r); echo "$r fg=$(echo "$P" | grep -c 'Never end your turn while a command you started is still running') judge=$(echo "$P" | grep -c 'Do not run the test suite or the gate commands')"; done)`
- THEN it prints exactly `implementer fg=1 judge=0`, `reviewer fg=1 judge=1`, `verifier fg=1 judge=0`, one per line

### Requirement: The code reviewer judges the diff and leaves the suite and the gate to the verifier
Every copy of the code reviewer prompt SHALL say `Do not run the test suite or the gate commands: the verifier runs them on the same head`, and SHALL allow a narrow command that confirms a specific finding. The design block SHALL stay a verbatim copy of `docs/prompts/06-code-reviewer.md`, and the run copy SHALL differ from it only by the fills it had on `main`. The reviewer's composed input MUST NOT list the gate commands, while the implementer's and the verifier's inputs still SHALL.

#### Scenario: Every reviewer copy carries the rule and the copies stay in step
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "judge=$(echo "$J" | grep -c 'Do not run the test suite or the gate commands: the verifier runs them on the same head') narrow=$(echo "$J" | grep -c 'You may run a narrow command to confirm a specific finding')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `judge=1 narrow=1`, then `copy=SAME fill=unchanged`

#### Scenario: The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && for r in reviewer verifier implementer; do [ $r = implementer ] && bin/factory ticket set T-0001.1 status=ready-for-implementer 'in_flight=[]' >/dev/null; R=$(bin/factory run start --role $r --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); bin/factory run compose ${R:-none} >/dev/null 2>&1; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "$r gates=$(grep -c 'Gate commands (run each from your worktree' $I 2>/dev/null) told=$(grep -c 'The verifier runs the gate commands on this head; you do not run them' $I 2>/dev/null)"; done)`
- THEN it prints exactly `reviewer gates=0 told=1`, `verifier gates=1 told=0`, `implementer gates=1 told=0`, one per line

### Requirement: The documents record the empty-output route
`docs/design.md` SHALL state the EMPTY-OUTPUT rule and its two routing-table rows, and SHALL list a second EMPTY-OUTPUT among the park reasons. `README.md` SHALL no longer say that a run is parked for exceeding a budget, and SHALL describe the empty-output retry. `docs/changelog.md` SHALL hold an entry for issue #41, numbered without a gap.

#### Scenario: The design doc states the EMPTY-OUTPUT rule, its rows and its park
- WHEN `(echo "rule=$(grep -c '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md) rows=$(grep -c '^| Any role | EMPTY-OUTPUT' docs/design.md) parks=$(grep '^- A non-empty ESCALATIONS line' docs/design.md | grep -c 'a second EMPTY-OUTPUT in a row') kill=$(grep -c 'never recorded as a budget kill' docs/design.md)")`
- THEN it prints exactly `rule=1 rows=2 parks=1 kill=1`

#### Scenario: README drops the budget park and describes the empty-output retry
- WHEN `(echo "budget=$(grep -c 'exceeding its budget\|over budget' README.md) built=$(grep -c '^- \*\*Empty output\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'ended without output twice')")`
- THEN it prints exactly `budget=0 built=1 unstick=1`

#### Scenario: The changelog records issue 41 without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #41 ' docs/changelog.md | grep -oF -e EMPTY-OUTPUT -e foreground -e 'last message' -e 're-dispatched once' -e 'gate commands' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

### Requirement: The spec writer and the critic carry the turn-economy rules
Every copy of the spec writer prompt SHALL tell it to batch independent reads and commands, read line ranges once grep has found them, keep long output in a scratch file, and write the spec in as few writes as it can. Every copy of the critic prompt SHALL carry the same reading rules, its minimum spot-check, a rule that it runs no test suite, the rule for picking an acceptance command, a sentence allowing a small experiment in its scratch directory to confirm a finding, and the rule that turns a claim needing a suite run or a build of the change into a finding or a question; it MUST NOT cap a claim at a number of paths and commands or forbid a clone, worktree or prototype. Each design block MUST stay byte-identical to its `docs/prompts/` copy, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); printf '%s\n' 'Put independent reads and commands in one turn' 'read that line range, not the whole file' 'to a file in your scratch directory and grep or tail it' > $T/both; { cat $T/both; echo 'Write the spec in as few writes as you can'; } > $T/spec_writer; { cat $T/both; printf '%s\n' 'Spot-check at least 2 cited paths and 1 acceptance command yourself' 'Run no test suite' 'Pick an acceptance command that runs no test suite' 'small experiment in your scratch directory' 'is a finding for the writer, or a question'; } > $T/critic; printf '%s\n' 'Ground any one claim' 'build nothing' 'no clone, worktree or prototype' > $T/gone; for r in "2. Spec writer|02-spec-writer.md|spec_writer" "3. Spec critic|03-spec-critic.md|critic"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) gone=$(for g in docs/prompts/$c factory/prompts/$f.md; do tr '\n' ' ' < $g | tr -s ' ' | grep -oF -f $T/gone; done | grep -c .) fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged`, then `critic copy=SAME doc=8/8 run=8/8 gone=0 fill=unchanged`. `doc` and `run` count the kept or added phrases found in the documented copy and the run copy, each joined into one line so a phrase may wrap; `gone` counts the removed phrases found in either.

### Requirement: Spec writer and critic runs receive the turn-economy rules
The system prompt that `run start` writes for a spec writer run SHALL contain the writer's turn-economy rule. The one it writes for a critic run SHALL contain the critic's reading rules, its no-suite rule and the sentence allowing a small scratch experiment, and MUST NOT contain the per-claim cap or the no-build rule.

#### Scenario: A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0002 status=ready-for-critic >/dev/null; bin/factory run start --role spec_writer --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role critic --ticket T-0002 >/dev/null 2>&1; W=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0001-spec_writer/system-prompt.txt | tr -s ' '); C=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0002-critic/system-prompt.txt | tr -s ' '); echo "spec_writer batch=$(printf "%s" "$W" | grep -c 'Put independent reads and commands in one turn') writes=$(printf "%s" "$W" | grep -c 'Write the spec in as few writes as you can')"; echo "critic batch=$(printf "%s" "$C" | grep -c 'Put independent reads and commands in one turn') suite=$(printf "%s" "$C" | grep -c 'Run no test suite') scratch=$(printf "%s" "$C" | grep -c 'small experiment in your scratch directory') cap=$(printf "%s" "$C" | grep -c 'Ground any one claim') build=$(printf "%s" "$C" | grep -c 'build nothing')")`
- THEN it prints exactly `spec_writer batch=1 writes=1`, then `critic batch=1 suite=1 scratch=1 cap=0 build=0`

### Requirement: The documents record the turn-economy change
`docs/changelog.md` SHALL hold one entry for issue #73, numbered without a gap. `docs/principles.md` principle 2 SHALL name the critic's no-suite rule among its mechanisms and SHALL no longer say the critic builds nothing.

#### Scenario: Principle 2 names the critic's no-suite rule and no longer its build ban
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; P=$(sed -n '/^### 2\. /,/^### 3\. /p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "entries73=$(grep -c '^[0-9]*\. After issue #73 ' docs/changelog.md) implemented=$(printf '%s' "$P" | grep -c 'runs no test suite (#73') builds=$(printf '%s' "$P" | grep -c 'builds nothing')")`
- THEN it prints exactly `CONTIGUOUS`, then `entries73=1 implemented=1 builds=0`

### Requirement: The documents record the critic revert
`docs/changelog.md` SHALL hold one entry for issue #74, numbered without a gap, that records the replay result and the two removed rules. The Spiking section of `docs/principles.md` SHALL no longer bound the critic to two paths and one command or say it does not build, SHALL say the critic may run a small scratch check, SHALL say vetting a whole approach belongs to the spec writer or a spike, and SHALL record the replay.

#### Scenario: The changelog records the revert in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #74 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#74' -e replay -e 'per-claim cap' -e 'no-build rule' -e 'no test suite' -e UV_PYTHON_INSTALL_DIR -e brace-list | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `7`

#### Scenario: The Spiking section allows a small scratch check and records the replay
- WHEN `(X=$(sed -n '/^## Spiking/,$p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "bound=$(printf '%s' "$X" | grep -c 'two paths, one command') nobuild=$(printf '%s' "$X" | grep -c 'it does not build') scratch=$(printf '%s' "$X" | grep -c 'small scratch check') whole=$(printf '%s' "$X" | grep -c 'vetting a whole approach belongs to the spec writer') replay=$(printf '%s' "$X" | grep -c 'replay')")`
- THEN it prints exactly `bound=0 nobuild=0 scratch=1 whole=1 replay=1`

### Requirement: The documents record the capability index
The triage prompt's design block, its `docs/prompts/` copy and the runtime prompt SHALL each carry the `Capabilities:` output line. `docs/design.md` and the README's Triage, Spec writer and Spec critic rows MUST describe the capability index. `docs/changelog.md` MUST have an entry for issue #75.

#### Scenario: The prompt copies, design, README and changelog name the capability index
- WHEN `(echo "docs-copy=$(grep -c '^Capabilities:' docs/prompts/01-triage.md) runtime=$(grep -c '^Capabilities:' factory/prompts/triage.md) changelog=$(grep -c '^[0-9]*\. After issue #75 ' docs/changelog.md) design=$(grep -q 'capability index' docs/design.md && echo y || echo n) readme=$(grep -E '^\| (Triage|Spec writer|Spec critic) \(' README.md | grep -c 'capability index')")`
- THEN it prints exactly `docs-copy=1 runtime=1 changelog=1 design=y readme=3`

### Requirement: The documents describe the whole decision log for the spec writer, critic and planner
`docs/design.md` and the README's Spec writer, Spec critic and Planner rows MUST say that those roles receive the whole decision log, and neither MUST mention a decision index. `docs/changelog.md` SHALL have an entry for issue #78.

#### Scenario: The design, README and changelog describe the whole decision log and no decision index
- WHEN `(echo "design-index=$(grep -c 'decision index' docs/design.md) design-whole=$(grep -c 'They and the planner receive the whole decision log' docs/design.md) readme-index=$(grep -c 'decision index' README.md) readme-whole=$(grep -E '^\| (Spec writer|Spec critic|Planner) \(' README.md | grep -c 'the whole decision log') changelog=$(grep -c '^[0-9]*\. After issue #78 ' docs/changelog.md)")`
- THEN it prints exactly `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`

### Requirement: The documents record superseded plans
`docs/design.md` SHALL say, in its rule for a sub-ticket closed by the human, that a new plan from a later approved version supersedes the earlier plan's unmerged sub-tickets. `README.md` SHALL carry a "Re-plan after a re-spec" bullet. `docs/changelog.md` SHALL hold one entry for issue #77, numbered without a gap.

#### Scenario: The design doc, README and changelog record superseded plans
- WHEN `(echo "design=$(grep 'sub-ticket closed by the human' docs/design.md | grep -c supersede) readme=$(grep -c '^- \*\*Re-plan after a re-spec\.\*\*' README.md) changelog=$(grep '^[0-9]*\. After issue #77 ' docs/changelog.md | grep -oF -e superseded -e planned_from -e 'Depends on' | sort -u | grep -c .) $(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)")`
- THEN it prints exactly `design=1 readme=1 changelog=3 CONTIGUOUS`

### Requirement: The prompts tell the reviewer what the gate checks and the spec writer how to declare
Every copy of the code reviewer prompt (the `docs/design.md` §6 block, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`) SHALL carry check 6's new last sentence and MUST NOT say `will require a human approval`. Every copy of the spec writer prompt SHALL give the `Protected paths:` line under Risk and the rule of one path or glob per entry with no brace lists. Each design block and its `docs/prompts/` file MUST stay byte-identical, and each `factory/prompts/` copy SHALL differ from its `docs/prompts/` file only where it did on `main`.

#### Scenario: Every reviewer prompt copy states what the merge gate checks
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "gate=$(echo "$J" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval, and refuses and parks one it does not declare") promise=$(echo "$J" | grep -c 'will require a human approval')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `gate=1 promise=0`, then `copy=SAME fill=unchanged`

#### Scenario: Every spec writer prompt copy gives the declaration line
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-sw.txt; T=$(mktemp -d); sed -n '/^## 2\. Spec writer/,/^## 3\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; do echo "reads=$(grep -c 'declared on one line the merge gate reads:$' $f) form=$(grep -c '^ *Protected paths: none | .<path or glob>., .<path or glob>.$' $f) braces=$(grep -c '^ *one path or glob per entry, no brace lists$' $f)"; done; git show main:factory/prompts/spec_writer.md > $T/a; git show main:docs/prompts/02-spec-writer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/02-spec-writer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/spec_writer.md docs/prompts/02-spec-writer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `reads=1 form=1 braces=1`, then `copy=SAME fill=unchanged`

### Requirement: The documents record the protected-path rule at merge
`docs/design.md` SHALL drop the per-PR approval for protected paths, describe the declared-path rule in piece 8 and the Protected paths gate row, and route a reviewer ESCALATE back to its checks; `docs/changelog.md` SHALL hold an entry for issue #57 and stay numbered without a gap; and `README.md` SHALL describe the check and `--accept-paths`.

#### Scenario: The design doc drops the per-PR approval for protected paths
- WHEN `(echo "gates=$(grep -c 'a PR touching a protected path, the daily escalation queue' docs/design.md) either=$(grep -c 'A change to either needs a human approval record before it merges' docs/design.md) onpr=$(grep -c 'any other guardrail or protected path needs a human approval on the PR itself' docs/design.md) piece8=$(grep '^| 8 |' docs/design.md | grep -c 'Protected paths:') piece9=$(grep -c 'review protected PRs' docs/design.md) gaterow=$(grep '^| Protected paths |' docs/design.md | grep -c -- '--accept-paths') stale=$(grep -c 'records the piece-8 approval; the merge gate does not merge without it' docs/design.md) reviewer_rule=$(grep -c '^  - A reviewer ESCALATE returns to its checks' docs/design.md) old_route=$(grep -c 'or a reviewer ESCALATE returns to the implementer' docs/design.md)")`
- THEN it prints exactly `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0`

#### Scenario: The changelog records issue 57's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #57 ' docs/changelog.md | grep -oF -e 'Risk' -e '--accept-paths' -e 'BLOCKED from merge gate' -e 'checks' -e 'Protected paths:' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the protected-path check and the new resolve verb
- WHEN `(echo "built=$(grep -c '^- \*\*Protected paths at merge\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--accept-paths') merges=$(sed -n '/^- \*\*Merges, one at a time\.\*\*/,/^- \*\*Setting up the store\.\*\*/p' README.md | grep -c 'Risk section' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `built=1 unstick=1 merges=1`

### Requirement: The implementer, verifier, code reviewer, planner and triage carry the reading rules
Every copy of the implementer, verifier, code reviewer, planner and triage prompts (the `docs/design.md` block, its `docs/prompts/` file and the `factory/prompts/` run copy) SHALL carry the Turn economy paragraph in the critic's words, and MUST NOT carry the spec writer's `as few writes as you can`. Each design block MUST stay byte-identical to its `docs/prompts/` file, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: The five role prompts carry the critic's reading paragraph in every copy
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for r in "1. Triage|01-triage.md|triage" "4. Planner / decomposer|04-planner.md|planner" "5. Implementer|05-implementer.md|implementer" "6. Code reviewer|06-code-reviewer.md|reviewer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF "$P" | grep -c .) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF "$P" | grep -c .) writes=$(cat docs/prompts/$c factory/prompts/$f.md | tr '\n' ' ' | tr -s ' ' | grep -c 'as few writes as you can') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly five lines: `triage copy=SAME doc=1 run=1 writes=0 fill=unchanged`, then the same for `planner`, `implementer`, `reviewer` and `verifier`. `copy=SAME`: the design block equals its `docs/prompts/` file. `doc` and `run`: the documented copy and the run copy each carry the whole paragraph once, joined into one line so it may wrap. `writes=0`: neither carries the spec writer's one-write sentence. `fill=unchanged`: the run copy differs from the documented copy only where it did on `main`.

### Requirement: Runs of the five roles receive the reading rules
The system prompt that `run start` writes for an implementer, code reviewer, verifier, triage and planner run SHALL contain the Turn economy paragraph once, and MUST NOT contain `as few writes as you can`.

#### Scenario: Implementer, reviewer and verifier runs receive the reading paragraph
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for r in implementer reviewer verifier; do X=$(prompt $r); echo "$r preamble=$(echo "$X" | grep -c "UNTRUSTED INPUT") economy=$(echo "$X" | grep -cF "$P") writes=$(echo "$X" | grep -c 'as few writes as you can')"; done)`
- THEN it prints exactly `implementer preamble=1 economy=1 writes=0`, `reviewer preamble=1 economy=1 writes=0`, `verifier preamble=1 economy=1 writes=0`, one per line. `preamble=1` shows the run started and its prompt was read.

#### Scenario: Triage and planner runs receive the reading paragraph
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-triage >/dev/null; bin/factory ticket set T-0002 status=ready-for-planner >/dev/null; bin/factory run start --role triage --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role planner --ticket T-0002 >/dev/null 2>&1; for r in triage planner; do X=$(tr '\n' ' ' < $(ls $FACTORY_STATE/runs/*-$r/system-prompt.txt) | tr -s ' '); echo "$r preamble=$(printf '%s' "$X" | grep -c 'UNTRUSTED INPUT') economy=$(printf '%s' "$X" | grep -cF "$P") writes=$(printf '%s' "$X" | grep -c 'as few writes as you can')"; done)`
- THEN it prints exactly `triage preamble=1 economy=1 writes=0`, then `planner preamble=1 economy=1 writes=0`

### Requirement: The documents record the reading rules for the five roles
`docs/changelog.md` SHALL hold one entry for issue #76, numbered without a gap, naming the five roles and the operator's replay, and the changelog SHALL end with its closing "Declined:" line.

#### Scenario: The changelog records the reading rules for the five roles in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #76 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oiF -e '#76' -e implementer -e verifier -e 'code reviewer' -e planner -e triage -e replay | tr A-Z a-z | sort -u | grep -c .) footer=$(tail -1 docs/changelog.md | grep -c '^Declined: a dedicated merge agent')")`
- THEN it prints `CONTIGUOUS`, then `entries=1 terms=7 footer=1`

### Requirement: The critic's rubric asks about cross-ticket dependencies
The critic's system prompt MUST tell it to check each scenario against approved changes not yet archived and to require the scenario's setup to hold whichever of the two merges first, and the runtime critic prompt SHALL stay a copy of `docs/prompts/03-spec-critic.md` with its round placeholder filled.

#### Scenario: A critic run's system prompt carries the cross-ticket rule
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/s; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; R=$(bin/factory run start --role critic --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); echo "rule=$(grep -c 'whichever of the two merges first' $FACTORY_STATE/runs/${R:-none}/system-prompt.txt 2>/dev/null)")`
- THEN it prints exactly `rule=1`

#### Scenario: The runtime critic prompt stays a copy of the documented one
- WHEN `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)`
- THEN it prints exactly `copies=same`

### Requirement: The documents record spec amendment, spec drift and the cross-ticket check
`docs/changelog.md` SHALL hold one entry, numbered without a gap, covering the amend command with its intent flag, the drift check and the critic's cross-ticket check; `docs/design.md` SHALL name `factory spec amend` and `--intent unchanged`, carry a Spec drift paragraph and give the critic the approved changes not yet archived in its routing row; and README SHALL list the command under "Where a human decides" and the feature under Built.

#### Scenario: The changelog records the change in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. ' docs/changelog.md | grep -F 'factory spec amend'); echo "$E" | grep -c .; echo "$E" | grep -oF -e '--intent' -e 'in flight' -e tasks.md -e 'spec drift' -e 'not yet archived' -e whichever | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `6`

#### Scenario: The design doc names the amend command, its intent flag, spec drift and the critic's new input
- WHEN `(echo "amend=$(grep -c 'factory spec amend' docs/design.md | awk '{print ($1 > 0)}') intent=$(grep -c -- '--intent unchanged' docs/design.md | awk '{print ($1 > 0)}') drift=$(grep -c '^\*\*Spec drift\.\*\*' docs/design.md) row=$(grep '^| Spec writer | READY-FOR-CRITIC' docs/design.md | grep -c 'not yet archived')")`
- THEN it prints exactly `amend=1 intent=1 drift=1 row=1`

#### Scenario: README lists the amend command and the drift check
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' README.md); B=$(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' README.md); echo "amend=$(echo "$H" | grep -c 'factory spec amend' | awk '{print ($1 > 0)}') intent=$(echo "$H" | grep -c -- '--intent' | awk '{print ($1 > 0)}') built=$(echo "$B" | grep -c '^- \*\*Spec amendment and drift\.\*\*')")`
- THEN it prints exactly `amend=1 intent=1 built=1`

### Requirement: The documents record the environment sync and the dropped virtual environment
`docs/design.md` SHALL name `environment_sync` and say the wrapper drops `VIRTUAL_ENV`. `factory/instance.template.yaml` SHALL carry an `environment_sync` key. `README.md` SHALL name `environment_sync` and `VIRTUAL_ENV`. `docs/changelog.md` SHALL hold one entry for issue #51 recording the change, numbered without a gap.

#### Scenario: The design doc, template and README name the sync and the dropped virtual environment
- WHEN `(echo "design=$(grep -c environment_sync docs/design.md | awk '{print ($1 > 0)}') design_venv=$(grep -c VIRTUAL_ENV docs/design.md | awk '{print ($1 > 0)}') template=$(grep -c '^environment_sync:' factory/instance.template.yaml) readme=$(grep -c environment_sync README.md | awk '{print ($1 > 0)}') readme_venv=$(grep -c VIRTUAL_ENV README.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `design=1 design_venv=1 template=1 readme=1 readme_venv=1`

#### Scenario: The changelog records the environment sync in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #51 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e environment_sync -e VIRTUAL_ENV -e PYTHONHOME -e 'already synced' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `4`

### Requirement: The documents describe the driver
`README.md` MUST describe `factory drive` under "Starting a run", its `claude -p` role processes under "What depends on Claude Code", the driver among the built pieces and its status file in the store's file table, and SHALL no longer list per-role effort as not built; `docs/design.md` SHALL name the driver, and `docs/changelog.md` SHALL hold an entry for issue #65.

#### Scenario: The documents describe the driver
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; r=README.md; echo "starting=$(y $(sed -n '/^## Starting a run/,/^### Filing a request/p' $r | grep -c 'factory drive')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'claude -p')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory drive')) effort-gap=$(y $(grep -c 'none has an effort level' $r)) drive-row=$(y $(grep -cE '^\| `drive/' $r)) design=$(y $(grep -c 'factory drive' docs/design.md)) changelog=$(y $(grep -cE '^[0-9]+\. After issues? [^(]*#65' docs/changelog.md))")`
- THEN it prints exactly `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes`

### Requirement: The documents record the sibling-merge exception and the start-failure ruling
`docs/design.md`'s Spec drift paragraph SHALL name `main_after` as not drift and its routing rules SHALL name the `harness-bug: run start implementer` ruling; README's Unstick row SHALL name it, and its "Spec amendment and drift" bullet SHALL say a sibling's merge is not drift and SHALL no longer say the check has not yet fired; and `docs/changelog.md` SHALL hold one entry for issue #85, numbered without a gap.

#### Scenario: The design doc, README and changelog record both changes
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; B=$(sed -n '/^- \*\*Spec amendment and drift\.\*\*/,/^- \*\*Re-plan after a re-spec\.\*\*/p' README.md); echo "design-drift=$(y $(grep '^\*\*Spec drift\.\*\*' docs/design.md | grep -c main_after)) design-ruling=$(y $(grep -c 'harness-bug: run start implementer' docs/design.md)) unstick=$(y $(grep '^| \*\*Unstick\*\*' README.md | grep -c 'harness-bug: run start implementer')) bullet-sibling=$(y $(echo "$B" | grep -c 'not drift')) bullet-stale=$(y $(echo "$B" | grep -c 'has not yet fired'))"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #85 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#85' -e main_after -e 'harness-bug: run start implementer' | sort -u | grep -c .)`
- THEN it prints exactly `design-drift=yes design-ruling=yes unstick=yes bullet-sibling=yes bullet-stale=no`, then `CONTIGUOUS`, then `1`, then `3`

### Requirement: The documents record the driver's exemption and its same-ticket guard
`docs/changelog.md` SHALL hold one entry for issue #86, numbered without a gap. README's `factory drive` how-to SHALL no longer tell the operator to put the marker in front of the command, and SHALL say that the driver is exempt and what it refuses on the same ticket. The opening of README's "Where a human decides" SHALL say the driver is exempt. `docs/design.md`'s fence paragraph SHALL state the exemption and the same-ticket guard, and SHALL no longer say the driver meets the fence like any write.

#### Scenario: The documents describe the driver's exemption and its same-ticket guard
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; c() { tr '\n' ' ' | tr -s ' ' | grep -ci -- "$1"; }; r=README.md; D=$(sed -n '/^### Driving a ticket from a shell with `factory drive`/,/^Each role process/p' $r); H=$(sed -n '/^## Where a human decides/,/^```/p' $r); G=$(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md); echo "changelog=$(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md) entry=$(grep -c '^[0-9]*\. After issue #86 ' docs/changelog.md) step=$(echo "$D" | c 'put `FACTORY_DISPATCH=1` in front of the command') drive=$(y $(echo "$D" | c exempt)),$(y $(echo "$D" | c 'same ticket')) human=$(y $(echo "$H" | c exempt)) design=$(y $(echo "$G" | c exempt)),$(y $(echo "$G" | c 'same ticket')),$(echo "$G" | c 'like any write when it starts')")`
- THEN it prints exactly `changelog=CONTIGUOUS entry=1 step=0 drive=yes,yes human=yes design=yes,yes,0`

### Requirement: The documents record factory stats
README SHALL list `stats` among the commands that are not writes, say under "Accepting a harness revision" that it skips the lock, describe it in a how-to subsection "Counting what each role catches and costs", in "What depends on Claude Code" and under **Built**; `docs/design.md` SHALL list it in the fence paragraph's read-only list, name it in the lock clause, and cite it in the model-per-role paragraph; `docs/principles.md` §4 SHALL name it as implemented and no longer say "1 BLOCKING finding in total"; and `docs/changelog.md` SHALL hold one entry for issues #70 and #61, numbered without a gap.

#### Scenario: The documents record factory stats
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; j() { tr '\n' ' ' | tr -s ' '; }; r=README.md; H=$(sed -n '/^## Where a human decides/,/^```/p' $r | j); L=$(sed -n '/^### Accepting a harness revision/,/^### Upgrading the runtime/p' $r | j); echo "readonly=$(y $(echo "$H" | grep -c '`paths` and `stats`')) howto=$(y $(sed -n '/^### Counting what each role catches and costs/,/^##/p' $r | grep -c 'factory stats')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory stats')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'factory stats')) lock=$(y $(echo "$L" | grep -c '`stats`')) design-fence=$(y $(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md | grep -c '`paths` and `stats`')) design-lock=$(y $(grep '^\*\*Role-context block\.\*\*' docs/design.md | grep -c '`stats`')) design-model=$(y $(grep '^\*\*Model per role, starting point\.\*\*' docs/design.md | grep -c 'factory stats')) principles=$(y $(sed -n '/^### 4\. Measure catch beside cost\./,/^##/p' docs/principles.md | grep '^Implemented by:' | grep -c '`factory stats`')) principles-old=$(y $(grep -c '1 BLOCKING finding in total' docs/principles.md))"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #70 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#70' -e '#61' -e 'factory stats' -e 'message id' | sort -u | grep -c .)`
- THEN it prints exactly `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no`, then `CONTIGUOUS`, then `1`, then `4`

### Requirement: The documents name the module that holds each moved gate command
`README.md` and `docs/principles.md` SHALL name `factory/gates.py`, not `factory/cli.py`, for
`ticket_join`, `merge_cmd`, `archive_cmd` and the `merge` guard, and those three functions MUST be
defined in `factory/gates.py`.

#### Scenario: The README and the principles name gates.py for the moved gate commands
- WHEN `echo "$(grep -c 'factory/gates.py. .ticket_join., .merge_cmd., .archive_cmd.' README.md) $(grep -c 'factory/cli.py. .ticket_join.' README.md) $(grep -c 'factory/gates.py. (.merge.)' docs/principles.md) $(grep -c 'guards in .factory/cli.py.:' docs/principles.md) $(grep -cE '^def (ticket_join|merge_cmd|archive_cmd)\(' factory/gates.py 2>/dev/null)"`
- THEN it prints exactly `1 0 1 0 3`

### Requirement: The documents record that run start owns each role's model
`README.md`'s role-call paragraph under "The intake workflow, step by step" SHALL say that `run start` refuses a `--model` the instance does not name.

#### Scenario: The README describes the model check
- WHEN `(echo "readme=$(sed -n '/^### The intake workflow, step by step/,/sequenceDiagram/p' README.md | grep -c -- '--model' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `readme=1`

### Requirement: The documents record the parallel suite and the waiting park reason
`docs/design.md`'s EMPTY-OUTPUT rule SHALL name the waiting park reason. `README.md` SHALL name pytest-xdist, and its Empty output entry SHALL give the waiting reason and no longer say it has not fired on a real ticket. `docs/changelog.md` SHALL hold entry 71 for issue #106, numbered without a gap.

#### Scenario: The design doc names the waiting park reason
- WHEN `(echo "design=$(grep '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md | grep -c 'ended its turn waiting on a background command')")`
- THEN it prints exactly `design=1`

#### Scenario: The README names pytest-xdist and the waiting reason
- WHEN `(B=$(awk '/^- \*\*Empty output\.\*\*/{f=1; print; next} f && /^(- \*\*|$|#)/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "bullet=$(grep -c '^- \*\*Empty output\.\*\*' README.md) waiting=$(echo "$B" | grep -c 'ended its turn waiting on a background command') unfired=$(echo "$B" | grep -c 'has not yet fired') xdist=$(grep -c 'pytest-xdist' README.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `bullet=1 waiting=1 unfired=0 xdist=1`

#### Scenario: The changelog records issue 106 as entry 71, without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #106 ' docs/changelog.md); printf '%s\n' "$E" | grep -c '^71\. '; printf '%s' "$E" | grep -oF -e 'pytest-xdist' -e 'ended its turn waiting on a background command' -e 'EMPTY-OUTPUT' -e 'stand-in' -e 'in-process' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

### Requirement: The maintained documents carry no whitespace errors
`README.md`, every file under `docs/` and `dev/`, and `.factory/context.md` MUST carry no whitespace error, checked over each file in full rather than over one change's diff.

#### Scenario: The maintained documents pass git's whitespace check in full
- WHEN `(E=$(git hash-object -t tree /dev/null); git diff --check $E HEAD -- README.md docs dev .factory/context.md; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The build documents under dev/ are frozen as history
`dev/build-harness.spec.md`, `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md` SHALL each carry, as line 3, a header that starts `> **Frozen as history.**`, followed by a blank line, and SHALL otherwise stay byte for byte as they were at `7231670`. `.factory/context.md` MUST NOT ask a change to keep any of them consistent, and SHALL call them frozen; README's `dev/` row SHALL say they are frozen as history.

#### Scenario: Each build document carries the header and is otherwise unchanged
- WHEN `(for f in dev/build-harness.spec.md dev/build-harness.plan.md dev/P0-intake-skeleton.md; do echo "$f header=$(sed -n 3p $f | grep -c '^> \*\*Frozen as history\.\*\* ') rest=$(sed '3,4d' $f | cmp -s - <(git show 7231670:$f) && echo same || echo changed)"; done)`
- THEN it prints exactly `dev/build-harness.spec.md header=1 rest=same`, then `dev/build-harness.plan.md header=1 rest=same`, then `dev/P0-intake-skeleton.md header=1 rest=same`

#### Scenario: The briefing no longer asks a change to keep the build spec in step
- WHEN `(echo "buildspec=$(grep -c 'build-harness' .factory/context.md) frozen=$(grep -c 'frozen as history' .factory/context.md | awk '{print ($1 > 0)}') readme=$(grep '^| .dev/. |' README.md | grep -c 'frozen as history')")`
- THEN it prints exactly `buildspec=0 frozen=1 readme=1`

### Requirement: README's claims about what has run match the stores
README MUST NOT say that the one-sub-ticket path, the driver, the per-run scratch directory, a gate command's path skip, the re-plan after a re-spec or the protected-path refusal at merge has not yet run, and MUST NOT say that a run with no output is recorded as killed. Its tripwire and sibling-tests entries SHALL still say they have not yet fired, and its per-role effort entry that neither target sets it. Its "Ground truth only above" rule SHALL ask each entry to say whether it has yet run on a real ticket, and line 3 of `docs/design.md` SHALL point to `docs/changelog.md` instead of carrying a date of its own.

#### Scenario: README no longer calls run features untried, and keeps the claims that are still true
- WHEN `(b() { awk -v h="$1" 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(printf '%s' "$R" | grep -oF -e 'one-sub-ticket path is tested' -e 'has not yet run a real ticket' -e 'remains the tested route' -e 'parked; this is tested' -e 'configuration uses it yet' -e 'recorded as killed' | grep -c .) replan=$(b '- **Re-plan after a re-spec.**' | grep -c 'not yet') paths=$(b '- **Protected paths at merge.**' | grep -c 'not yet') drive=$(b '- **The driver, ' | grep -c 'not yet') tripwire=$(b '- **Tripwire on live files.**' | grep -c 'has not yet fired') sibling=$(b '- **Sibling tests check.**' | grep -c 'has not yet fired') effort=$(b '- **Per-role effort' | grep -c 'Neither target sets it yet')")`
- THEN it prints exactly `stale=0 replan=0 paths=0 drive=0 tripwire=1 sibling=1 effort=1`

#### Scenario: The Built rule asks for run status, and the design doc's date line points to the changelog
- WHEN `(echo "rule=$(sed -n '/^- \*\*Ground truth only above/,/^- \*\*Update with the change/p' README.md | tr '\n' ' ' | tr -s ' ' | grep -c 'its entry says whether it has yet run on a real ticket') date=$(sed -n 3p docs/design.md | grep -c 'docs/changelog.md') old=$(sed -n 3p docs/design.md | grep -c '^2026-09-30 · Daniel$')")`
- THEN it prints exactly `rule=1 date=1 old=0`

### Requirement: README describes each mechanism in one section
README SHALL describe the live-store fence under "Where a human decides", the driver under "Driving a ticket from a shell with `factory drive`", the final check's skip under "The build workflow, step by step", the store branch under "How the factory uses git", and other agent hosts only in `docs/design.md`. Elsewhere it SHALL give each a short entry with a pointer: the Built entries for the fence, the driver, the tripwire, the sibling-tests check, spec drift, empty output, protected paths at merge and `factory stats` SHALL each stay within a line budget and name the section or the `docs/design.md` paragraph that describes it, and "Not built" SHALL list nothing that "Where this can go" lists.

#### Scenario: Each Built entry is a short pointer, and each mechanism's detail has one home
`s` prints `pointer` when a Built entry is at most N lines and names its home, and `long` otherwise.
- WHEN `(b() { awk -v h="$1" 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' README.md; }; s() { b "$1" | awk -v n="$2" -v p="$3" '{t=t" "$0} END{gsub(/ +/," ",t); print ((NR>0 && NR<=n && index(t,p)) ? "pointer" : "long")}'; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "fence=$(s '- **Live-store fence.**' 3 'Where a human decides') driver=$(s '- **The driver, ' 4 'Driving a ticket from a shell') tripwire=$(s '- **Tripwire on live files.**' 4 'docs/design.md') sibling=$(s '- **Sibling tests check.**' 4 'docs/design.md') drift=$(s '- **Spec amendment and drift.**' 6 'docs/design.md') empty=$(s '- **Empty output.**' 6 'docs/design.md') paths=$(s '- **Protected paths at merge.**' 4 'Where a human decides') stats=$(s '- **Counting catch and cost' 3 'Counting what each role catches') host=$(sed -n '/^### Running on another agent host/,/^## /p' README.md | sed '1d;$d' | awk '{t=t" "$0} /./{n++} /^\|/{tab=1} END{print ((n<=6 && !tab && index(t,"docs/design.md")) ? "pointer" : "long")}') skip=$(printf '%s' "$R" | grep -o 'has not moved since' | grep -c .) store=$(printf '%s' "$R" | grep -o 'never moves the integration branch' | grep -c .) drivefence=$(sed -n '/^### Driving a ticket from a shell/,/^Each role process/p' README.md | tr '\n' ' ' | grep -c 'refused like any write') notbuilt=$(sed -n '/^\*\*Not built\*\*/,/^## Where this can go/p' README.md | grep -c '^- \*\*')")`
- THEN it prints exactly `fence=pointer driver=pointer tripwire=pointer sibling=pointer drift=pointer empty=pointer paths=pointer stats=pointer host=pointer skip=1 store=1 drivefence=0 notbuilt=0`

### Requirement: README defines each term once
README's "Terms used on this page" SHALL point to "Where it runs" for target, instance, runtime and store branch in one row instead of defining them again, and SHALL give protected path its own row; the merge gate row SHALL no longer define a protected path, and the **Record** row of "Where a human decides" SHALL no longer restate who reads the decision log.

#### Scenario: The glossary points to Where it runs and defines protected path once
- WHEN `(T=$(sed -n '/^## Terms used on this page/,/^## How a ticket moves/p' README.md); echo "rows=$(printf '%s\n' "$T" | grep -cE '^\| (target|instance|runtime|store branch) \|') pointer=$(printf '%s\n' "$T" | grep -c '^| target, instance, runtime, store branch |') protected=$(printf '%s\n' "$T" | grep -c '^| protected path |') merge=$(grep '^| merge gate |' README.md | grep -c 'protected_paths') record=$(grep '^| \*\*Record\*\*' README.md | grep -c 'receive')")`
- THEN it prints exactly `rows=0 pointer=1 protected=1 merge=0 record=0`

### Requirement: History lives in the changelog
README SHALL keep under "Related work and history" the issue references it carries today, and SHALL no longer carry the history this change moves: the 2026-10-04 overlap count, the double count `factory/cost.py` once made, the store moves, the page's own origin story and the regeneration pass's past catches. `docs/design.md`'s model-per-role paragraph SHALL point to changelog entry 70 for the first `factory stats` figures instead of repeating them. `docs/changelog.md` SHALL hold one entry for issue #101 recording the move, numbered without a gap.

#### Scenario: README keeps its issue references and drops the moved history, and the changelog records the move
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); X=$(sed -n '/^## Related work and history/,/^## Maintaining this page/p' README.md | tr '\n' ' ' | tr -s ' '); M=$(grep '^\*\*Model per role, starting point\.\*\*' docs/design.md); E=$(grep '^[0-9]*\. After issue #101 ' docs/changelog.md); echo "history=$(printf '%s' "$R" | grep -oF -e '41 and 11 overlapping' -e 'used to count most calls about twice' -e 'First written 2026-10-03' -e 'today this caught' -e 'were moved onto it' | grep -c .) refs=$(printf '%s' "$X" | grep -oE '#[0-9]+' | sort -u | grep -xcE '#(16|17|18|19|20|21|22|23|24|28|35|42|46|47|53|55|61|65|70)') figures=$(printf '%s' "$M" | grep -c '94,860,442') pointer=$(printf '%s' "$M" | grep -c 'changelog entry 70') entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e frozen -e build-harness.spec.md -e context.md -e '41 and 11' -e harness-docs -e 'not yet' | sort -u | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)`
- THEN it prints exactly `history=0 refs=19 figures=0 pointer=1 entries=1 terms=6`, then `CONTIGUOUS`

### Requirement: README stays within its line budget
`README.md` SHALL be at most 1,110 lines long; a later change that needs more room raises this bound in its own spec, where the operator approves it at the gate.

#### Scenario: README is at most 1,110 lines
- WHEN `(echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1110 ? "within" : "over")}')")`
- THEN it prints exactly `readme=within`

## Current truth: store-setup

# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

### Requirement: A new instance's store is a checkout of its own branch
`factory init` SHALL create a missing own store as a git worktree of branch `factory-store`, which the integration checkout does not see. It SHALL check that branch out when it already exists locally or on exactly one remote, so that a store commit never moves the integration branch.

#### Scenario: init creates the store on the factory-store branch, out of the integration checkout's sight
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; echo "branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/state/')")`
- THEN it prints `branch=factory-store seen_by_main=0`

#### Scenario: init on a clone restores the store from the pushed branch
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/src && cd $T/src && git commit -q --allow-empty -m init && $B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T/src $T/c && cd $T/c && rm -rf .factory/state && $B init >/dev/null 2>&1; echo "exit=$? branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) restored=$(ls .factory/state/decisions.md 2>/dev/null | grep -c .)")`
- THEN it prints `exit=0 branch=factory-store restored=1`

### Requirement: init refuses when more than one remote carries the store branch
`factory init` MUST refuse with exit 2, creating no store and no local branch, when the own store is missing, no local `factory-store` exists and more than one remote carries it; the refusal MUST name each `<remote>/factory-store`.

#### Scenario: init on a clone with two remotes carrying the store branch refuses and names both
- GIVEN the three fixture files written by the block below, run once at column 0 as shown. Every later scenario of this change that names them reuses them.

```sh
cat > ${TMPDIR:-/tmp}/t0025-old.sh <<'EOF'
# Sourced from the repo root: a target whose store is a plain directory tracked on main, as both
# instances keep it today. Leaves the shell in the target; PRE is the commit that last tracked it.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
mkdir -p .factory/state && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
git add -A && git commit -q -m "instance, with its store on main" && PRE=$(git rev-parse HEAD)
EOF
cat > ${TMPDIR:-/tmp}/t0025-b1.sh <<'EOF'
# Sourced from the repo root: a target whose store at .factory/state is already a git worktree of
# an unborn factory-store branch, built with git alone (so it is the same layout whatever the
# harness does), then given an instance by init. Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
git worktree add -q --orphan -b factory-store .factory/state && echo /.factory/state/ >> "$(git rev-parse --git-path info/exclude)"
$B init --repo-name demo >/dev/null 2>&1
EOF
cat > ${TMPDIR:-/tmp}/t0025-gate.sh <<'EOF'
# Sourced from the repo root: a target made by init, its instance committed on main, and T-0001 on
# branch factory/T-0001 with reviewer APPROVE, verifier VERIFIED and gate PASS on its head H.
# Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
$B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance
git checkout -q -b factory/T-0001 && echo x > x.txt && git add x.txt && git commit -q -m work
H=$(git rev-parse HEAD) && git checkout -q main
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
$B ticket set T-0001 status=checks-in-flight branch=factory/T-0001 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/rv.md
$B results record T-0001 --head $H --role verifier --output $T25/v.md --run run-0001-verifier >/dev/null
$B results record T-0001 --head $H --role reviewer --output $T25/rv.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T25/tgt $T25/c && cd $T25/c && git remote add nas $T25/tgt && git fetch -q nas && $B init >/dev/null 2>$T25/err; echo "exit=$? store=$([ -e .factory/state ] && echo written || echo none) local_branch=$(git branch --list factory-store | grep -c .) names=$(grep -c 'origin/factory-store' $T25/err),$(grep -c 'nas/factory-store' $T25/err)")`
- THEN it prints `exit=2 store=none local_branch=0 names=1,1`

### Requirement: init refuses to run from inside the store checkout
`factory init`, run with `FACTORY_INSTANCE` unset from a directory whose git top level is a checkout of `factory-store`, or is the store of the instance found from that directory or a checkout of the same repository inside that store, MUST refuse with exit 2 and write nothing, whichever commit the store has checked out, so that it never creates an instance inside the live store; other commands run from there SHALL still find the live instance, and `init` in a separate repository under the store SHALL still create that repository's instance.

#### Scenario: init from a scratch directory inside the store checkout refuses and leaves the store unchanged
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init from the store checkout on a detached HEAD refuses
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git -C .factory/state checkout -q --detach && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? detached=$(git -C $T25/tgt/.factory/state symbolic-ref -q HEAD >/dev/null && echo no || echo yes) phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 detached=yes phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init in a separate repository under a run's scratch directory still creates its instance
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && cd .factory/state/runs/run-0001-triage/scratch && git init -q -b main other && cd other && git commit -q --allow-empty -m init && $B init --repo-name other >/dev/null 2>&1; echo "exit=$? instance=$([ -f .factory/instance.yaml ] && echo written || echo none) live=$(cd $T25/tgt && $B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 instance=written live=ready-for-triage`

### Requirement: init refuses a store path the integration branch has tracked
`factory init` MUST refuse with exit 2, writing nothing and naming the path, when it would create the own store at a path under which the integration branch has ever tracked a file.

#### Scenario: init refuses a once-tracked store path and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/tgt && cd $T/tgt && mkdir -p .factory/state && echo old > .factory/state/old.md && git add -A && git commit -q -m "old store" && git rm -q -r .factory/state && git commit -q -m "store removed" && $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e .factory ] && echo written || echo none) names_path=$(grep -q '\.factory/state' $T/err && echo 1 || echo 0)")`
- THEN it prints `exit=2 instance=none names_path=1`

### Requirement: store migrate moves a tracked store onto its branch and keeps every record
`factory store migrate --to PATH` on an idle, fully committed own store that is tracked on the integration branch SHALL do all of the following:
- put the store's last committed tree on a new `factory-store` branch, checked out at PATH;
- copy the store's ignored run files to PATH, and verify the copy before removing anything;
- untrack and remove the old path;
- set `state_dir` to PATH, so that later commands use the moved store.

#### Scenario: store migrate carries the store to factory-store at the new path
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && mkdir -p .factory/state/runs/run-0001-triage/scratch && echo n > .factory/state/runs/run-0001-triage/scratch/n.txt && $B store migrate --to .factory/store >/dev/null 2>&1; echo "exit=$?"; echo "branch=$(git -C .factory/store symbolic-ref --short HEAD 2>/dev/null) same_tree=$([ "$(git rev-parse -q --verify 'factory-store^{tree}')" = "$(git rev-parse $PRE:.factory/state)" ] && echo yes || echo no) scratch=$(cat .factory/store/runs/run-0001-triage/scratch/n.txt 2>/dev/null) old=$([ -e .factory/state ] && echo kept || echo gone) main_tracks=$(git ls-files .factory/state | grep -c .) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/store/')"; echo "state_dir=$(sed -n 's/^state_dir: *//p' .factory/instance.yaml) ticket=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0`, then `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0`, then `state_dir=.factory/store ticket=ready-for-triage`

### Requirement: store migrate refuses while the store is in use or uncommitted
`factory store migrate` MUST refuse with exit 2, creating no branch and no new path, when a store file is uncommitted or a run is in flight. The refusal MUST name the uncommitted files or the runs in flight.

#### Scenario: store migrate refuses an uncommitted store and a run in flight
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && echo edit >> .factory/state/decisions.md; $B store migrate --to .factory/store >/dev/null 2>$T25/e1; echo "uncommitted: exit=$? names=$(grep -c 'decisions.md' $T25/e1) branch=$(git branch --list factory-store | grep -c .)"; git checkout -q -- .factory/state/decisions.md && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git add -A && git commit -q -m "run started"; FACTORY_DISPATCH=1 $B store migrate --to .factory/store >/dev/null 2>$T25/e2; echo "in flight: exit=$? names=$(grep -c 'run-0001-triage' $T25/e2) branch=$(git branch --list factory-store | grep -c .) new=$([ -e .factory/store ] && echo written || echo none)")`
- THEN it prints `uncommitted: exit=2 names=1 branch=0`, then `in flight: exit=2 names=1 branch=0 new=none`

### Requirement: A checkout of an older commit leaves a moved store untouched
After `store migrate`, checking out a commit from before the move in the integration checkout, and then checking out the integration branch again, MUST leave every file of the moved store as it was, uncommitted ones included.

#### Scenario: A checkout of an older commit leaves the moved store untouched
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B store migrate --to .factory/store >/dev/null 2>&1 && git commit -q -a -m "store moved to its branch"; (echo live > .factory/store/live.md) 2>/dev/null; git checkout -q $PRE 2>/dev/null && git checkout -q main 2>/dev/null; echo "live=$(cat .factory/store/live.md 2>/dev/null || echo lost) on=$(git symbolic-ref --short HEAD)")`
- THEN it prints `live=live on=main`

## Capability index: current truth not given in full above

This list is complete: every current-truth capability not given in full above has one line here. Open a capability at its path before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, sends that capability in full to the critic, so cite under Evidence each capability you open.

- build-dispatch, 83 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/build-dispatch/spec.md`: A park reason carries the failing command's error; The build runs only the checkers a commit still needs; The workflows' clerk commands carry the dispatcher marker; An implementer starts only when each sibling-added test it may change came from a merged sibling; The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it; The build asks the whole-spec step before it runs the planner; A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT; A role run that writes its output runs once and routes on its STATUS; The build counts only the current plan's sub-tickets; A parent's final check and close count only the current plan's sub-tickets; The build parks a merge the gate blocked, with the gate's reason; A sub-ticket whose spec drifted parks before its first implementer run; Changes that leave a sub-ticket's spec intact do not park it; The driver takes a ticket through intake on the intake script's route; The driver takes an approved ticket through the build on the build script's route; Each role run is one headless claude process with its role's prompt, model and tool limits; A role process's reply is recorded with its run; The checkers run at once, and sub-tickets run concurrently up to a limit; The driver reports each step on one line and in a status file; A stopped driver ends its role processes and resumes from the stored state; The driver marks its own store calls, never its role processes, and passes a configured effort; The Workflow scripts keep working beside the driver; A drive refuses to start on a ticket that is already being worked; A role run does not start on a ticket that already has a run in flight; Run start takes each role's model from the instance and refuses a --model that names another; A Workflow run whose relayed configuration names the wrong model parks at that role's run start; Existing callers of run start keep working; The EMPTY-OUTPUT park says when a role ended its turn waiting on a command
- factory-stats, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/factory-stats/spec.md`: factory stats counts runs and verdicts per role and model; factory stats groups parks by normalised reason and counts gate and merge decisions; factory stats ties each spec defect caught downstream to the runs that wrote and critiqued the spec; factory stats reports each role's cost from run records first and transcripts second; The transcript cost report counts each message once; factory stats reproduces the hand count on the two live stores
- gate-commands, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/gate-commands/spec.md`: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them; A skipped command is recorded on the gate result, and the merge still needs that result to pass; The implementer is given every gate command; A malformed gate entry refuses every build role's run start; The gate's suite command finishes in under three minutes
- harness-code, 26 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-code/spec.md`: The harness keeps no definition, setting or comment that nothing uses or that is no longer true; Each operation the harness repeated has one definition; Sharing an operation changes no refusal, park reason, event or parse result; The command-line code has one module per job; Splitting the command-line code changes no definition; Only the entry point, the driver and the stats report import the CLI module; The split harness passes its suite and its name checks
- harness-suite, 17 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-suite/spec.md`: The harness suite runs mid-edit without loosening the lock; Test files share code only through helper modules; Each shared test helper is written once; The refactor keeps every test and assertion but the one duplicate; A suite run writes nothing into the checkout; One harness-suite run finishes in under three minutes; Two harness-suite runs at once each finish in under five minutes; The suite's stand-in agent replies when several copies of one role start at once; This change keeps every test and assertion but the two the waiting park reason changes
- human-resolution, 21 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/human-resolution/spec.md`: A ruling returns a BLOCKED sub-ticket to its implementer; Existing ruling routes are unchanged; A re-plan returns a fully merged parent to its planner; A redispatch sets aside only rows that did not pass; Accepting the refused paths returns the sub-ticket to its checks, which then merge; A ruling on a merge gate's refusal sends the sub-ticket back to its implementer; A ruling on a reviewer's escalation returns the sub-ticket to its checks; A ruling returns a sub-ticket whose implementer run failed to start
- live-store-guard, 14 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/live-store-guard/spec.md`: Unmarked writes to a live store are refused while a role run is in flight there; Writes from inside a store's run directories or code checkouts are refused, marked or not; Reads, marked commands from outside the store, throwaway stores and idle stores stay open; The marker does not lift the harness lock; factory stats reads any store under any harness revision and writes nothing
- merge-gate, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/merge-gate/spec.md`: A store commit does not hold back a merge; A commit to the integration branch still holds back a merge; The merge gate refuses a changed protected path the pinned spec does not declare; A declared or unprotected path merges with no further approval
- role-escalations, 5 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-escalations/spec.md`: The implementer and verifier leave declared protected paths out of ESCALATIONS; Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
- role-inputs, 15 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-inputs/spec.md`: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest; A ticket whose triage output names no capabilities receives today's inputs; Triage receives the capability index and is asked to name the capabilities a request touches; The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names; The critic sees approved changes not yet archived
- run-environment, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/run-environment/spec.md`: The running-code wrapper drops an inherited virtual environment; Each build checkout is synced before its role starts; A failed sync stops the run before it starts; Without environment_sync, run start and the input are unchanged
- spec-amendment, 12 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/spec-amendment/spec.md`: A human amends a pinned spec whose intent is unchanged; Later runs receive the amended spec, and the record names what changed; Archive writes the amended version into current truth; An amendment that changes intent is refused with a restart note; An amendment that cannot be applied is refused and writes nothing
- sub-ticket-planning, 16 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/sub-ticket-planning/spec.md`: A later plan's sub-tickets continue the parent's numbering; A spec that needs one sub-ticket becomes that sub-ticket without a planner run; The whole-spec step refuses where a planner run would; A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets; A new plan may not depend on a sub-ticket it supersedes; The planner is told which sub-tickets its plan will supersede

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)
2026-10-04 T-0024 Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
2026-10-04 T-0024 While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
2026-10-04 T-0024 A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
2026-10-04 T-0024 The location rule is checked first, then the marker, then the in-flight list.
2026-10-04 T-0024 The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
2026-10-04 T-0024 The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
2026-10-04 T-0024 The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
2026-10-04 T-0024 A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
2026-10-04 T-0024 The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
2026-10-04 T-0024 A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
2026-10-04 T-0024 The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
2026-10-04 T-0024 The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
2026-10-04 T-0024 Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
2026-10-04 T-0024 Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.
2026-10-04 T-0022 Removing clearly redundant work (a step, run or check that cannot change any outcome) is pre-approved, provided every refusal the pipeline gives today still fires (operator, 2026-10-04: 'slashing clearly redundant work is always going to be OK, if we trust our process')
2026-10-04 T-0022 Under a sub-ticket's Tests to change, the planner may list tests an earlier sibling of the same parent added, with a harness check that each first appeared in a sibling's merge; pre-existing tests still need the approved spec (operator, #40)
2026-10-04 T-0025 The store lives on its own branch, `factory-store`, checked out as a git worktree at the store's path (B1). This is for the operator to confirm at the spec gate. Rejected: B2, the branch written through git plumbing with no working copy. It needs new harness commands to snapshot, show and restore the store, and `git clean -fdx` in the integration checkout deletes the store (Evidence). Rejected: A, a gate exception (operator, 2026-10-04).
2026-10-04 T-0025 A store path must be one the integration branch has never tracked. Both existing stores move from `.factory/state` to `.factory/store`. Rejected: keeping `.factory/state`, where checking out an older commit overwrote an uncommitted record and checking `main` out again deleted it (Evidence).
2026-10-04 T-0025 The branch is named `factory-store`, and the design doc and build spec drop the name `tickets` for it. Rejected: `tickets`, a generic name in a target repo whose branches serve other work, such as the Nanobot repo, which shares its objects with another checkout.
2026-10-04 T-0025 `init` creates a new store as a worktree on an unborn `factory-store` branch, and the operator makes the first commit. On a clone where the branch already exists, `init` checks it out, which restores the store. Rejected: `init` committing, which needs a git identity, and the suite runs under a throwaway HOME that has none.
2026-10-04 T-0025 When no local `factory-store` exists and more than one remote carries it, `init` refuses and names each `<remote>/factory-store`. The operator picks one with `git branch factory-store <remote>/factory-store` and runs `init` again. Rejected: creating a new empty branch, which would silently start a second store history beside the pushed one. Also rejected: preferring `origin`, a guess about which remote is canonical.
2026-10-04 T-0025 With `FACTORY_INSTANCE` unset, `init` refuses, writing nothing, when the caller's git top level is a checkout of `factory-store`. It also refuses when the instance found by walking up from the caller's directory has a store that is that top level, or that contains it in the same repository (the same git common directory). These are the cases where it would build a phantom instance inside the live store. The second condition does not depend on which branch or commit the store has checked out, so a detached store HEAD does not open the route again (operator, round 2 change request N2). The same-repository qualifier keeps `init` working in a separate throwaway repository under a run's scratch directory (Evidence). Rejected: "contains" without that qualifier, which would refuse every suite `init` run with pytest's temporary directory inside a store. Rejected: taking the repository from the parent of `--git-common-dir`. That is the main worktree, which for the Nanobot instance is `~/dev/nanobot`, another checkout on another branch, and for the runtime checkout is `~/dev/spec-factory` (Evidence).
2026-10-04 T-0025 In `init`, every refusal and the store-worktree step come before any instance file is written, so a failed worktree step (for example, git's "already used by worktree" when `init` runs in a code checkout of a repo whose store branch is checked out elsewhere) leaves nothing behind.
2026-10-04 T-0025 The integration checkout ignores the store through the repo's git exclude file, which `init` and `store migrate` write. Rejected: a line in the target's tracked `.gitignore`. That would change the target's code to record a fact about one clone.
2026-10-04 T-0025 A new command, `factory store migrate --to PATH`, moves an existing store. It refuses unless the store is idle and committed, and it leaves the integration-branch side uncommitted for the operator to review. Rejected: a hand procedure, untested, run once on each repo by a different session.
2026-10-04 T-0025 `store migrate` deletes the old store directory only after it has checked that every ignored file (run scratch directories, tripwire baselines) was copied byte for byte. If the check fails, it undoes its own worktree and branch and leaves the old store as it was. Rejected: relying on `git status` in the new checkout, which cannot see ignored files.
2026-10-04 T-0025 The store branch starts with one commit whose tree is the store as last committed on the integration branch, and whose message names that commit. Earlier history stays readable with `git log <that commit> -- .factory/state`. Rejected: rewriting history with a subtree split. It would follow only part of the store's past, which began at `intake/state`, and it adds nothing that `main`'s history does not already keep.
2026-10-04 T-0025 An instance whose store is still a plain directory keeps working unchanged. `init` leaves such a store alone and points to `store migrate`. The harness reads and writes the store only through `state_dir`, so it runs with either layout.
2026-10-04 T-0022 A sub-ticket's "Tests to change" may list a test file that an earlier sibling of the same parent added, one line each: `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The harness reads only lines of that form inside the "Tests to change" field, and checks the file, not the test function. Rejected: checking test functions. The implementer rule puts new tests in new files, so a file is what a sibling adds, and git records files.
2026-10-04 T-0022 A listed file counts as added by a sibling when it is absent at the parent's `parent_base`, and the first commit since then on the integration branch that added it lies inside one merged sibling's recorded merge (reachable from its `main_after`, not from its `base_before`). Any merged sibling of the parent counts, including those from an earlier plan. The sibling ID on the line is for the reader and is not matched. Rejected: matching the named ID, because the planner's IDs (`ST-1`) differ from the store's (`T-0001.1`) and the operator's rule names no particular sibling.
2026-10-04 T-0022 The check runs in `run start` for every implementer run of a sub-ticket: first dispatch, fix rounds and catch-up runs. Every dispatch passes through that one place. Rejected: checking when the plan is added, when no sibling has merged yet. Rejected: checking at the merge gate, after the implementer has already edited the test. Rejected: checking where a waiting sub-ticket is released, which happens in two places and never for a sub-ticket with no dependencies.
2026-10-04 T-0022 A failed check refuses the run start with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness:` and names the file. The build workflow parks the sub-ticket with that error as the reason, so `resolve --ruling` handles it like an implementer's BLOCKED. That is what the operator's "parks for the operator, as today" describes. Rejected: a new kind of park with its own resolve verb. Rejected: having `run start` park the ticket itself, which would break the rule that a refusal writes nothing.
2026-10-04 T-0022 The preamble's guardrail sentence and the code reviewer's test-integrity check also accept a sibling entry that the harness has checked. Without them, the implementer and reviewer would still treat the edit as forbidden, and the park would remain.
2026-10-04 T-0022 The earlier sibling names the tests a later sibling will break under a new planner field, "Interim tests". The harness does not read it.
2026-10-04 T-0022 The critic's check for an omitted test goes under rubric 1 (Grounded), where the requester asked for it.
2026-10-04 T-0022 The requester's acceptance, a re-plan and re-spec of Nanobot T-0002 that the operator compares side by side, is an Operator step, not an acceptance scenario. Running it needs the Nanobot store and real agents, which a verifier must not touch.
2026-10-04 T-0032 Empty role output (#41, T-0032): labelled EMPTY-OUTPUT with the last message, re-dispatched once automatically, parked on a second; the code reviewer judges the diff and leaves the test suite and gates to the verifier.
2026-10-04 T-0029 Only the code reviewer lists declared protected paths, once for each head it reviews. The implementer and verifier may name them in their output, but not under ESCALATIONS. This is a standing decision: a later prompt change should not give another role a declared-path notice. The operator pre-approved it on 2026-10-04 (`.factory/answers/operator-decisions-2026-10-04.md`), under the standing decision that removing clearly redundant work is allowed when every refusal still fires.
2026-10-04 T-0029 A fix round makes a new head, so it gets its own reviewer notice, as today. Rejected: one notice per sub-ticket. A fix round can change a declared path again, and the operator would not hear about it.
2026-10-04 T-0029 The new rule also keeps one escalation for a declared path: when the change does something to it that the spec does not describe. An undeclared path still escalates as well. Rejected: the retro's wording "the reviewer lists declared paths for the merge gate". No local merge check reads the declaration, so that sentence would teach the roles something false.
2026-10-04 T-0029 The implementer and verifier get the same bullet word for word, as the last bullet under RULES. That way one text is checked in both prompts.
2026-10-04 T-0029 The changelog records the count re-derived from the store log (10 runs, 30 of 205 items). Rejected: the retro's 26 of 139, which its own table contradicts with 38.
2026-10-04 T-0029 Acceptance checks the composed run prompts and the document copies. The request's own check (on the next build, one notice per head, from the reviewer) is kept as an operator step. Rejected: an acceptance item that waits for a real build. The verifier cannot run one, and how a model follows a prompt rule is not something a check on one commit can prove.
2026-10-05 T-0028 Part A overturns the cut in T-0016's spec. The path-scoped gate skip is built as the operator pre-approved it, with no repository's configuration changed. Rejected: cutting it again because it would have skipped almost no past run. The request expects a small saving here and still asks for the mechanism. Part A is a separate part, so the operator can delete it and its scenarios at the gate.
2026-10-05 T-0028 A gate command's `paths` are git pathspecs. A command is skipped when `git diff --name-only <base>...<head> -- <paths>` lists no file. Include entries (`src/`) and exclude entries (`:(exclude)dev/`) both work. Rejected: a glob matcher of our own, a second matching rule that could disagree with git's. Standing: later tickets and instance configs use pathspec semantics.
2026-10-05 T-0028 If this repository's suite is ever scoped, its paths should exclude what it does not read rather than list what it does: `:(exclude)dev/` and `:(exclude)README.md`. Rejected: the requester's inclusion list, which leaves out `.gitignore` and any new top-level file, so it would skip the suite on changes that fail it.
2026-10-05 T-0028 The harness decides the skip when a reviewer or verifier run starts on a sub-ticket. It reads the live instance's configuration and that run's base and head. The verifier is told which commands are skipped, so it does not decide. Rejected: letting the verifier judge relevance, which no record could check.
2026-10-05 T-0028 Each skipped command is recorded twice: in the checker run's `meta.yaml` (`gate_skipped`) and on the `ci` row (`skipped`). Each entry has the command, `status: SKIPPED` and the reason. The row's PASS or FAIL still comes from the verifier's `Gate suite:` line, over the commands that ran.
2026-10-05 T-0028 A malformed gate entry refuses every implementer, reviewer and verifier run start with exit 2, before a run is created. A malformed entry is anything other than a string, or a mapping with a non-empty string `command` and an optional non-empty list of non-empty strings `paths`, with no other key. Rejected: treating a typo such as `path:` as unscoped. The operator would believe a scope is in force that is not.
2026-10-05 T-0028 An empty `paths` list is refused. Rejected: reading it as "covers nothing", which would skip the command on every diff.
2026-10-05 T-0028 The planner is skipped when all of these hold, and otherwise runs as today: the parent has no sub-ticket and no earlier planner run; its latest spec-writer run did not end NEEDS-SPLIT; and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that contains the word seam or seams. This sorts all thirteen past parents as they were built (Evidence). Rejected: the requester's "exactly one lettered part", which would have skipped none of the nine. Rejected: NEEDS-SPLIT alone, which would have built T-0025's two parts, about 470 lines, as one sub-ticket. Standing: the planner runs only for a spec that is split, re-planned or already planned once.
2026-10-05 T-0028 To force the planner on a spec that meets every condition, the operator adds a `### Size and seams` heading in a gate edit (`approve-spec --edit`). No new flag.
2026-10-05 T-0028 The whole-spec sub-ticket is `<parent>.1`, at `ready-for-implementer`, with no dependency. Its text names every scenario of the approved spec, one `- <name>` line each. For everything else it points to the spec: every lettered part, the spec's labels, its Tests to change and its Risk list. Because it names every scenario, the parent closes on its VERIFIED run under the existing rule (part C).
2026-10-05 T-0028 The store records the skip three ways: a `plan.skipped` event in the log with its reason, the parent's plan file (`plans/<parent>.md`), and the change folder's `tasks.md` when the repository has a spec store. A planner-made plan writes the same two files.
2026-10-05 T-0028 A spec already applied on `main`, the planner's most frequent ESCALATE, is caught after the skip by the implementer's step 2 and by the verifier's base run of NEW checks (design part B, table). The catch costs an implementer run in place of a planner run. Rejected: a harness check of "already applied", which would need the agents' judgment of what the spec asks for.
2026-10-07 T-0032 Retry-once-then-park on a role's unusable output (#41's EMPTY-OUTPUT) is the general mechanism: later refusal kinds (#68 format, #67 spec-lint) register with it rather than adding their own. resolve --ruling should also accept a budget-kill or EMPTY-OUTPUT park (rulings had to be placed by hand on T-0029.1 and T-0028.1).
2026-10-07 T-0032 An empty output is `EMPTY-OUTPUT`, never a budget kill. That covers a missing or empty output file, an agent call that returns blank text, and one that returns `null` (a user skip or a terminal API error). Rejected: keeping a budget-kill path for some of these. The harness enforces no budget, and the agent call reports no reason (Evidence).
2026-10-07 T-0032 Standing, from the operator's answer, already in `decisions.md` as the 2026-10-04 T-0032 line, for both parts: the empty-output route, and the reviewer leaving the suite and the gate to the verifier. Later changes follow both.
2026-10-07 T-0032 `EMPTY-OUTPUT` is decided in one place, `run finish`. The workflows no longer send `--status-override KILLED` for an empty return, so `run finish` reads the output file for every run. Rejected: a second override value in the scripts. It would label a run empty even when its output file was written.
2026-10-07 T-0032 The retry is counted inside one workflow run: one re-dispatch, then a park. Rejected: a counter in the store. It would add a ticket field for a case that a human already watches, because a workflow that stops is restarted by hand.
2026-10-07 T-0032 A thrown agent call is not re-dispatched. It carries its own error text, including the error thrown when the turn's token ceiling is spent, so it is the one stop the harness can name.
2026-10-07 T-0032 The last message is kept by a new command, `factory run last-message RUN --text=…`, called only after `run finish` has returned `EMPTY-OUTPUT`. The text is the last 4000 characters, as one shell single-quoted word. Rejected: passing it on every `run finish`, which would put each role's whole output through every clerk command.
2026-10-07 T-0032 A second empty output parks as `EMPTY-OUTPUT from <role>`, in the same form as the other role parks, and lists both runs. The last messages stay in the run directories, not in the reason.
2026-10-07 T-0032 A checker's second empty output parks before any result row is recorded for it. `resolve --redispatch` then re-runs only that checker, because the other checker's passing rows stand. Rejected: an `EMPTY-OUTPUT` result row and a join rule for it, a new row status for the same outcome.
2026-10-07 T-0032 The reviewer's input no longer lists the gate commands. It says that the verifier runs them, as the design's routing table already declares (`docs/design.md:126`).
2026-10-07 T-0032 The `budget kill` join reason is kept for hand-recorded `KILLED` rows. Rejected: renaming it, which would change three existing tests for a case no one reported.
2026-10-07 T-0032 `build.js:137` (the implementer's `budget kill` park) is removed. `run finish` can no longer return `KILLED` to the workflow, so the line would never run.
2026-10-07 T-0033 Protected paths at merge (#57, T-0033): the pinned spec's Risk list is the authorization; an undeclared changed protected path is refused at merge and parks for a ruling; no per-head approval step. All instances.
2026-10-08 T-0034 The critic keeps its minimum check, at least 2 cited paths and 1 acceptance command per review. It gains a cap of at most 2 paths and 1 command for any one claim. Rejected: replacing the minimum with the cap, which would let a critic approve having checked nothing. `docs/principles.md`'s Spiking section states the bound per claim ("Grounding a claim … two paths, one command").
2026-10-08 T-0034 The critic runs no test suite and builds nothing (no clone, worktree or prototype of the change). It runs an acceptance command only as the spec gives it, and picks one that runs no test suite. Standing: a later change to the critic prompt keeps this rule, as principle 2 requires.
2026-10-08 T-0034 A claim the critic could settle only by running a test suite or building the change is a finding for the writer, or a question, and the critic says what it could not check. The finding's severity follows the existing rubric. Rubric item 2 ("NEW items fail today") stays unchanged.
2026-10-08 T-0034 The writer and the critic get the same three reading sentences: batch independent reads and commands, read a line range once grep has found it, and send long output to a scratch file and grep or tail it. Only the writer gets "write the spec in as few writes as you can". The critic writes one verdict and needs no such rule.
2026-10-08 T-0034 No shared preamble line. The rules go only in the two role prompts. Rejected: a preamble line, which would reach every role, including the implementer and verifier, which the request does not cover.
2026-10-08 T-0034 The rules are added as new lines only, so no existing line of either prompt changes. The writer's rule is the last RULES bullet of the documented copy. The critic's rules follow its existing PROCESS line.
2026-10-08 T-0034 `docs/principles.md` records the critic's new rule under principle 2 and corrects principle 2's status line, which says "reader roles run no suites" was done by #41 alone.
2026-10-08 T-0034 The request's acceptance, a replay of 2–3 approved intakes with old and new prompts, is an Operator step. Running it needs live model runs, and judging spec quality side by side is a human call. The scenarios check the text the roles receive.
2026-10-08 T-0035 This change overturns part of a standing decision, one that later tickets must keep, recorded on 2026-10-08 for T-0034, the ticket that applied #73: "The critic runs no test suite and builds nothing ... Standing: a later change to the critic prompt keeps this rule". The no-test-suite half stands. The no-build half and the per-claim cap (T-0034's other 2026-10-08 decision) are removed. Authority: the operator's choice in `.factory/answers/T-0034-acceptance-2026-10-08.md`. Standing: later changes to the critic prompt keep the no-suite rule and do not re-add a per-claim cap or a no-build rule without new evidence.
2026-10-08 T-0035 The critic prompt gains one sentence that allows a small experiment in its scratch directory to confirm a finding. Without it, the kept sentence "A claim you could settle only by ... building the change is a finding" reads as the old ban. The kept sentence still covers building or trying out the change itself, which the request's item C (its `docs/principles.md` change) leaves to the writer or to a spike, a ticket built only to test whether an approach works. Rejected: deleting the kept sentence. The triage role, which sorts a request before the spec writer sees it, asked to keep it, and it still tells the critic what to do with a claim it cannot check.
2026-10-08 T-0035 The no-suite line gains its reason, "the implementer and the verifier run it", as the request's item B (its list of what the critic keeps) gives. `Pick an acceptance command that runs no test suite, and run it as the spec gives it.` and the Turn economy paragraph stay word for word.
2026-10-08 T-0035 The Spiking section records the replay result, as the request's item C asks ("Record the replay result"). The changelog entry records it too.
2026-10-08 T-0035 Of the current-truth requirements that #73 added, four are restated (MODIFIED), because each states the rule being removed or forbids removing a critic line. Other current-truth requirements that check the diff of their own change (for example "The documents record the live-store guard", which expects no prompt copy to change) are left as they are, as #73 left them. Their scenarios describe their own change, not standing behaviour.
2026-10-08 T-0035 "Writer unchanged from #73" is checked as no difference from `05cf8f9` in either writer prompt file, plus the writer's design block equal to its `docs/prompts/` copy. Together these mean the design block is unchanged too.
2026-10-09 T-0036 Triage names the capabilities on a new output line, `Capabilities:`, chosen from a capability index added to its input. A token that names no current-truth capability, such as `none` or `new`, is ignored.
2026-10-09 T-0036 Which capabilities a role receives in full: the names on triage's line, plus each existing capability whose `specs/<name>/spec.md` path appears in the spec the role works from. For the writer that is its previous version on a revision round. For the critic it is the version under review. For the planner it is the approved version, read whole, Evidence included. A writer that opens a capability and cites its path under Evidence therefore hands it to the critic. This keeps the request's rule that the critic sees the writer's list plus whatever the writer opened.
2026-10-09 T-0036 A ticket whose latest finished triage output has no `Capabilities:` line gets today's inputs, the whole of current truth and the whole log. This covers tickets triaged before this change, T-0036 among them. Rejected: sending only the index in that case, which would cut those tickets' inputs with no list to cut by.
2026-10-09 T-0036 An index line for a capability gives its name, its size, the absolute path of its spec and its requirement names. Rejected: the request's "one-sentence purpose", because no capability spec on either store has a purpose paragraph (Evidence).
2026-10-09 T-0036 A decision line goes in full when it is logged against this ticket, or when its text names a capability sent in full as a whole word. The log's other lines are indexed one line per ticket: ticket id, number of decisions, first and last date, and the ticket's title. The index heading gives the command `grep ' <ticket id> ' <absolute path of decisions.md>`. Rejected: one index line per decision, which comes to tens of kilobytes on Nanobot (240 lines, median 278 bytes).
2026-10-09 T-0036 A role opens deferred items by path, with its own file reads or `grep`. No `factory spec show` or `factory decision show` command is added. Rejected: those commands, because a command run from inside a role must clear the live-store fence and find the instance from the role's working directory. A path needs neither, and it is how compose already points at full specs (Evidence).
2026-10-09 T-0036 The instructions live in the index headings. They say the list is complete, that anything in it is opened by its path, and that citing a path hands the capability to the critic. Rejected: editing the writer and critic prompts, which would put the same words in two more protected copies.
2026-10-09 T-0036 A run's `input_sources` lists only the files sent in full. An index adds no source.
2026-10-09 T-0036 The standing 2026-10-04 T-0024 decision says that `decisions.md` "keeps reaching the spec writer, critic and planner". It still does: in full for the lines this ticket touches, and line by line for the rest through the index and its `grep` command.
2026-10-09 T-0036 Acceptance does not hold this change to the request's 40 kB mean and 100 kB maximum. The projection gives a mean of 101 kB and a maximum of 167 kB for the Nanobot store's last ten tickets, and the remainder lies outside this change (Problem, Evidence). The operator steps measure the real figures after the change runs.
2026-10-09 T-0036 The docs use one name for the new index, "capability index".
2026-10-09 T-0037 Decision log in role inputs (#78, T-0037): the spec writer, critic and planner get decisions.md whole; #75's decision filter is removed; any future scoping must not be able to drop a cross-cutting standing decision (see #54).
2026-10-09 T-0037 The spec writer, critic and planner receive `decisions.md` whole whenever it holds any text, whatever capabilities their ticket names. The decision index and its `grep` instruction are removed. This is the operator's Answer 1, already standing in `decisions.md` as the 2026-10-09 T-0037 line. Rejected: the request's rule of sending lines that name no capability in full and filtering the rest. On today's logs it sends every line anyway, and it could still hide a cross-cutting decision that happens to name a capability.
2026-10-09 T-0037 The capability index note loses its clause ", and the decisions that name it to the critic and the planner,"; the rest of the note stays word for word. Rejected: keeping the clause, which would tell the writer that citing a path is how decisions reach the critic and planner. That is no longer so. This edits one sentence of #75's capability half, which the triage assumption kept byte for byte.
2026-10-09 T-0037 The planner's decision part no longer reads triage's capability names or the approved spec's citations. It reads the whole log, as before #75.
2026-10-09 T-0037 The decision part is measured in this spec's Evidence, before and after, on both stores. No new file or harness command records it.
2026-10-09 T-0038 Each sub-ticket records `planned_from`, the parent's approved version when the sub-ticket was created. Nothing changes it afterwards. Rejected: reading `spec.approved_version`, which approved T-0027 moves forward on amendment.
2026-10-09 T-0038 Superseded is computed whenever sub-tickets are read, not stored. A sub-ticket is superseded when it has not merged and its `planned_from` is lower than the highest `planned_from` among its parent's sub-tickets. Rejected: the request's mark written at re-plan time. That needs a write on every path that adds a plan and a migration for stores that already hold such sub-tickets, such as Nanobot T-0024. Also rejected: comparing with the parent's current approved version. That would supersede the live plan after a T-0027 amendment that keeps it.
2026-10-09 T-0038 A record without `planned_from`, or with it null, falls back to its `spec.approved_version`. With neither, the sub-ticket counts as current.
2026-10-09 T-0038 A plan made from the same approved version supersedes nothing. This covers `resolve --replan` after a failed final check, and a second plan added by hand. The design ties a new plan to an amended spec (`docs/design.md:109`). To replace a plan without changing intent, the operator approves with `approve-spec --edit`, which always makes a new version. This is a standing decision.
2026-10-09 T-0038 Merged sub-tickets are never superseded. They count toward the close, the final check must contain their merges, and a new plan may depend on them.
2026-10-09 T-0038 `subticket add` refuses, writing nothing, a plan whose `Depends on:` names a sub-ticket that the plan supersedes. Rejected: accepting it. The dependant would wait forever, because a superseded sub-ticket is never dispatched.
2026-10-09 T-0038 `subticket add` reports the sub-ticket ids it newly supersedes under `superseded` and logs a `subtickets.superseded` event. Nothing is deleted, and every id stays taken.
2026-10-09 T-0038 `ticket ready-implementers` keeps `subtickets` as every sub-ticket id. `build.js` reads an empty list as "planned with none", and `dev/build-harness.spec.md:286` documents it that way. Every other list there leaves superseded sub-tickets out, and the new `superseded` list names them.
2026-10-09 T-0038 The planner is told which sub-tickets its plan will supersede, on one line after the existing list. With none, its input is byte-identical to today.
2026-10-09 T-0038 The name is "superseded", as the request and triage use it, and in the same sense as `results/<head>/superseded-<n>/`: a record kept but no longer counted.
2026-10-09 T-0033 The authorization is the pinned spec's Risk section. The pinned spec is the version the operator approved at the spec gate. For a sub-ticket, that is its parent's approved version (`specs/<parent>/v<approved_version>.md`). A ticket with no parent uses its own approved version. A ticket with no approved spec declares nothing. This is standing for every instance, from the operator's 2026-10-05 answer. It is already the 2026-10-07 T-0033 line in `decisions.md`, the factory's log of standing decisions that later tickets must follow.
2026-10-09 T-0033 The gate reads declarations from one fixed line in the Risk section: `Protected paths: none`, or `Protected paths: ` followed by one or more backticked paths or globs, separated by commas. An optional list marker (`- ` or `* `) may come before it, and an optional full stop after it. Each entry is one path or one glob. A brace list such as `factory/prompts/{a,b}.md` is one literal entry, which git does not expand, so it matches no file and declares nothing. A Risk line in any other shape declares nothing, and so does a line inside a fenced code block. Several such lines declare their union. Standing: specs declare protected paths only this way. Rejected: reading every backticked path in Risk, because today's Risk sections also put the paths they promise not to touch in backticks (Evidence). Rejected: the planner's per-sub-ticket `Protected paths:` field, which an agent writes and no human approves.
2026-10-09 T-0033 A changed path is "protected" when it matches one of the instance's in-repo `protected_paths` globs. It is "declared" when it matches a declared entry. Both matches use git's glob pathspecs (`:(glob)<pattern>`, so `**` crosses directories and `*` does not). This follows the 2026-10-05 T-0028 decision that the harness never adds a glob matcher of its own. Patterns that start with `~` or `/` are skipped.
2026-10-09 T-0033 The changed paths are those of `git diff --name-only --no-renames <integration branch>...<head>`, measured from the merge base; the head is the commit the gate is judging. Once the head contains the integration branch, that is exactly what the merge adds. `--no-renames` lists both sides of a move (Evidence). Rejected: the triage's "parent base". A catch-up run is an implementer run that merges the integration branch into a sub-ticket's branch that has fallen behind. After one, a diff from the parent's base counts other tickets' merged changes against this sub-ticket.
2026-10-09 T-0033 The gate runs this check after the three recorded results and before the containment check and the merge lock. A change that will be refused costs no catch-up run.
2026-10-09 T-0033 A refusal exits 2 and changes no ticket field. It logs one `merge.refused` event with the paths. Its error starts `BLOCKED from merge gate: ` and names each undeclared path, sorted and comma-separated. It names no declared path and uses no backtick, `$` or double quote, because the build workflow passes the reason through a shell command.
2026-10-09 T-0033 The build workflow parks the sub-ticket with that error, verbatim, as the reason. It already does the same for the harness's `BLOCKED from harness:` refusal at run start.
2026-10-09 T-0033 The human answers that park with one of two commands. `resolve --ruling F` sends the change back. It uses the existing BLOCKED route: the sub-ticket returns to its implementer with F in its input, and its round count (the number of fix cycles it may use) is not reset. The new `resolve --accept-paths F` accepts the paths under the approved design. It records F as the sub-ticket's next ruling. It adds the undeclared paths, recomputed on the current head, to a ticket field `accepted_paths`, which the gate treats as declared. It returns the sub-ticket to `checks-in-flight`, the state in which the reviewer and verifier judge it, with its recorded results kept, so the build merges it on its next pass. Rejected: one acceptance per head, because a catch-up run makes a new head and the same paths would park again. Rejected: amending the pinned spec's Risk section, because no command amends a pinned spec yet (T-0027 asks for one). An acceptance adds paths only for that sub-ticket and leaves every other merge condition in force.
2026-10-09 T-0033 `--accept-paths` refuses, with exit 2 and nothing written, on a park whose reason does not start `BLOCKED from merge gate:`. Its error starts `--accept-paths applies to`. It also refuses when the head is not the branch tip, or when no undeclared protected path remains.
2026-10-09 T-0033 A ruling on a park whose reason starts `ESCALATE from reviewer` returns the sub-ticket to `checks-in-flight`, round count unchanged. Its recorded results are set aside as `--redispatch` sets them aside: an APPROVE reviewer result is kept, and a VERIFIED verifier result with a PASS gate result is kept. Every other result moves to `superseded-<n>/`. The reviewer and verifier runs that follow receive the ruling, as they already do (`factory/compose.py` lines 278 and 300). This overturns `docs/design.md` line 109, which sends a reviewer ESCALATE to the implementer with the round count reset. Rejected: that route, because the 2026-10-05 escalation needed no code change. The re-run reviewer can still return REQUEST-CHANGES when a ruling asks for a fix.
2026-10-09 T-0033 Check 6 of the reviewer prompt keeps its first two sentences and adds "for the record" to the list of declared paths. Its last sentence says what the gate does: it merges a declared path with no further approval, and refuses and parks one the approved spec does not declare.
2026-10-09 T-0033 No per-head approval is added for paths that change the factory's own rules (option 3 of the operator's answer). The answer leaves it open for this spec gate. Adding it is a gate edit to this spec (a new lettered part) or a later ticket.
2026-10-09 T-0030 T-0030 (#24 A+C) closed as partly applied: part C merged (T-0030.3); parts A, B and per-role effort moved to #65 (backlog review 2026-10-09). Current truth was not folded for this ticket.
2026-10-09 T-0026 T-0026 (#47) withdrawn: merged into #65 at the backlog review 2026-10-09; the Workflow scripts it would change retire with #65.
2026-10-09 T-0039 All five roles get the critic's form of the paragraph, word for word, as one bullet starting `- Turn economy: `. It carries the three reading rules and the sentence saying why they matter. The spec writer's "as few writes as you can" stays out, as the request says. The writer's "such as a suite run" example also stays out, because the code reviewer must not run the suite. With one text, one check covers all five prompts.
2026-10-09 T-0039 The paragraph goes into each role's own prompt, not into the shared preamble. A preamble line would also reach the spec writer and critic, which already carry the rules, and T-0034 rejected a preamble line for the same reason. The request names the five prompts.
2026-10-09 T-0039 New lines only: no existing line of any prompt changes. Placement: in the implementer and verifier, a RULES bullet directly before the declared-path bullet, so that bullet stays last under RULES where T-0029 put it. In the code reviewer, the last bullet of WHAT YOU RUN, which is about the commands it runs. In the planner and triage, the last RULES bullet. In triage's run copy, that is before the instance-added "Acceptance items" block.
2026-10-09 T-0039 Acceptance checks the text each role receives: all three prompt copies and the composed run prompt. The request's own acceptance, the operator replaying past implementer and verifier runs with old and new prompts, is an Operator step. It needs live model runs and a human judgement of verdict quality (as in T-0034 and T-0029).
2026-10-09 T-0039 `docs/changelog.md` gains entry 64 after entry 63 and before the closing "Declined:" line. The entry cites the #74 replay result as entry 59.
2026-10-09 T-0027 The command is `factory spec amend <parent> --file <F> --reason "<one line>" --intent unchanged|changed`, run by a human. Rejected: the build spec's unbuilt `resolve --amend-spec`. Each `resolve` mode acts on a ticket the pipeline has stopped, and an amendment may be needed while a ticket is `planned` and not stopped.
2026-10-09 T-0027 `--intent` is required. With `unchanged`, the harness checks the claim: the amended version must keep the Problem section, every Decisions line, and each requirement's name, operation and statement (its text before its first scenario), whitespace aside. Scenarios, setup, Evidence, design text and Tests to change may change. Any other difference is refused as a change of intent, naming each one. `--intent changed` is always refused. Rejected: issue #50's critic run on every amendment, which needs a new route from the command to the critic; the mechanical check covers the same three things. Rejected: no flag, which lets a human make an intent change without saying so. This is a standing decision.
2026-10-09 T-0027 A refused change of intent prints a restart note. The note lists each merged sub-ticket with its merge commit, which stays on the integration branch. It lists each unmerged one with its state and branch, which a restart discards. It names both ways to restart. The first re-specs and re-plans: `factory ticket park`, `factory resolve <id> --to spec-gate`, then `factory approve-spec <id> --edit F`, after which the new plan supersedes the unmerged sub-tickets. The second closes the ticket and re-files it: `factory resolve <id> --close` and `factory ticket new`. The factory never restarts by itself. This is a standing decision.
2026-10-09 T-0027 An amendment changes no ticket state. The operator resumes the ticket with the routes that exist. Rejected: an amendment that also moves the ticket, which would duplicate those routes.
2026-10-09 T-0027 `spec amend` refuses while any run is in flight on the parent or one of its sub-tickets. A parked or waiting sub-ticket does not block it. Rejected: refusing while any sub-ticket is unmerged, which would block the motivating case of a sub-ticket parked BLOCKED on a scenario it cannot pass. This is a standing decision.
2026-10-09 T-0027 Human-only means that no workflow script and no role prompt names the command. A role run on the parent or a sub-ticket is in flight while it runs, so the in-flight refusal stops it. There is no identity check, because the harness runs under one identity.
2026-10-09 T-0027 `spec amend` refuses, with exit 2 and nothing written, in these cases: a sub-ticket; a ticket with no approved version; a ticket at `awaiting-spec-gate`, where `approve-spec --edit` is the route; a closed ticket; a reason that is not one non-blank line; and, with a spec store, a ticket whose change folder is gone because it was archived. An amended version must pass the gate's own checks: it is well-formed, and its deltas apply to current truth.
2026-10-09 T-0027 The re-pin keeps the planner's `tasks.md` in the change folder. The rest of the folder is rewritten as the gate writes it.
2026-10-09 T-0027 Each sub-ticket that is neither merged nor closed has its spec record moved to the new version, so later runs record the version they received. Its `planned_from`, the version its plan was made from, does not change, so an amendment never supersedes a plan.
2026-10-09 T-0027 The record is `approvals/<parent>/amendment-<n>.md`, numbered after any amendment file already there. It holds who, when, the reason, `Intent: unchanged`, the old and new version, and one line per scenario that differs: `- changed: <name>`, `- added: <name>` or `- removed: <name>`. It also holds a `- <id> / <title>: merged` line per sub-ticket merged before the amendment, and the unified diff. The log gets a `spec.amended` event. The amendment record is that version's approval record; no gate approval file is written.
2026-10-09 T-0027 Every spec version records the integration branch's head when it was stored, in `specs/<id>/v<n>.yaml`; that covers `spec add`, a gate edit and `spec amend`. Drift is counted from the record of the parent's approved version. Rejected: counting from the pin, because T-0032.1's test arrived between writing and pinning. A version stored before this change has no record, so its sub-tickets get only the sibling rule.
2026-10-09 T-0027 The drift check runs at `run start` of a sub-ticket's implementer, before the sibling-tests check. It runs only while the sub-ticket has no implementer run and no ruling on file. On drift it refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build already parks any `BLOCKED ` refusal with it as the reason. The human then amends the spec, rules, or both, and `resolve --ruling` returns the sub-ticket; the ruling also stops the check from repeating. Rejected: a new SPEC-DRIFT park status, as issue #50 proposed, which needs a new `resolve` route.
2026-10-09 T-0027 Sibling rule: drift when the sub-ticket's Acceptance field names, by id or by plan label, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. This is a standing decision.
2026-10-09 T-0027 Test rule: drift for each test file changed on the integration branch since the version's recorded head, by a first-parent commit that also changed a file the spec's design part names, and that neither the spec's Tests to change nor the sub-ticket's Tests to change lists. A test file's name starts with `test_`, or ends `_test.<ext>`, or contains `.test.`. Named files are the design part's backticked paths that exist at the integration head, except test files and `.md` documents, which every ticket here edits. This approximates "pins behaviour the spec changes": measured above, it catches 9 of 10 known incidents and would park about half the sub-tickets. Rejected: running each NEW scenario at build start and comparing it with the spec's "fails today" output (issue #50, part D). That output is prose, not something a program can compare. Rejected: a judge run per sub-ticket, which needs a new role and route.
2026-10-09 T-0027 The critic's input gains a section, `## Approved changes not yet archived`. It lists each change folder whose ticket is neither closed nor back in the spec loop (`ready-for-spec-writer`, `ready-for-critic`, `awaiting-spec-gate`), other than the reviewed ticket's own. Each entry gives the ticket id, title, state, folder path, the requirements its deltas add, modify or remove, and its Decisions lines. The section reads `none` when the list is empty, and is left out when the store has no spec store. Rejected: whole proposals, which would multiply the critic's input.
2026-10-09 T-0027 The cross-ticket rule extends the critic's rubric item 5 (Consistent). A scenario whose setup would not hold under one of the two merge orders is a BLOCKING finding that names the other ticket and its decision. This is a standing decision.
2026-10-09 T-0031 The wrapper fully deactivates an inherited virtual environment. It removes the exact entry `$VIRTUAL_ENV/bin` from `PATH`, then unsets `VIRTUAL_ENV` and `PYTHONHOME`, all before it sets HOME. Rejected: unsetting only the two variables, as the requester proposed. The activating shell also put the environment's `bin/` first on `PATH`, so a bare `python` or `pytest` would still run the other repository's environment (Evidence).
2026-10-09 T-0031 The deactivation is built into the wrapper for every instance, not configured per instance. Rejected: a way to unset variables through `run_env`. Every instance needs the deactivation, and opting in would leave it off by default. `run_env` is the list of variables an instance gives the wrapper to export after the throwaway HOME. Its exports still come after the deactivation, so an instance that wants a particular environment can still name it there.
2026-10-09 T-0031 `environment_sync` is one optional shell command, given as a string in `instance.yaml`. If it is absent or null, nothing runs, as today. Any other non-string or empty value is refused at run start, before any checkout is made.
2026-10-09 T-0031 The sync runs at every build-role run start, for the implementer, reviewer and verifier, including the verifier that checks the parent ticket after all its sub-tickets merge. It runs in that run's checkout, after the environment files are copied, through the same wrapper as role commands, so it gets the throwaway HOME, the `run_env` exports and no inherited environment. Rejected: syncing only when the implementer's worktree is first created. The environment files are copied again at every run start. A conflict run, which is an implementer run after the merge step refused the branch, merges in the integration branch, the branch that finished tickets merge into. Either can change the lock file the environment was built from. The reviewer is synced too, although it no longer runs the gate commands: its prompt still lets it run one test to confirm a finding (Evidence).
2026-10-09 T-0031 Changed from version 2: a failed sync refuses the run start with exit 2 and a one-line error, `environment_sync failed (exit <code>) in <checkout>; its command and output are in <log>`. The log is `runs/<id>/environment-sync.log`, in the run directory that run start had already reserved. It holds the command, the exit code and the command's full output. The error carries neither the command nor its output. No run is recorded or put in flight, and a checker checkout made for the run is removed. The implementer's worktree is kept for the next dispatch. The build workflow, the script that dispatches the build roles in turn, then parks the ticket: it stops the ticket and leaves it for a human. It uses its existing park reason `harness-bug: run start <role>: …`, so a broken environment never reaches a checker as a code failure. Rejected: version 2's error with the command and its last 20 output lines. The workflow passes the reason to the shell in double quotes, which expand the backticks that uv's errors contain, and the command is the operator's free text (Evidence). Rejected: starting the role anyway with a note. The role would then rediscover the broken environment, which is the cost this change removes.
2026-10-09 T-0031 When the sync ran, the run's record file, `meta.yaml`, stores the command under `environment_sync`. Changed from version 2: the role's input gains one line at the end of its "Where you work" section, after any SKIPPED lines. The line says the command ran, the environment is already synced, and the role should not sync again unless its change alters the files the environment is built from. Rejected: version 2's "after the gate-commands line", which the reviewer's input no longer has (Evidence).
2026-10-09 T-0031 This change sets `environment_sync` on neither instance. The operator sets it after the runtime, the separate checkout the factory runs from, has moved to the new harness revision (Operator steps). Rejected: setting it on this instance in the PR. That writes the protected `.factory/**`, and the key has no effect until the runtime runs the new harness anyway.
2026-10-10 T-0040 The driver is a harness subcommand, `factory drive TICKET [--phase intake|build] [--parallel N] [--prompt-mode append|replace]`, in a new module `factory/drive.py`, run as its own foreground process. A runner session may start it in the background. Rejected: running it inside the Workflow tool, which is the limit this change removes.
2026-10-10 T-0040 Store calls go through the CLI's own entry point, `factory.cli.main(argv)`, in the driver's process, with stdout and stderr captured, one call at a time on the driver's main thread. Every guard, refusal, fence check and lock check runs exactly as for `bin/factory`. Rejected: a `bin/factory` subprocess per call, which the requester ruled out. Rejected: calling store functions below `main`, which would skip the fence and the lock.
2026-10-10 T-0040 `factory drive` is a write command like any other, so the fence and the lock apply when it starts. Under the standing 2026-10-04 T-0024 decision, a runner that starts it while any run is in flight on the target puts `FACTORY_DISPATCH=1` in front of it. Once started, the driver marks its own store calls whether or not it was started marked. Its role processes never inherit the marker. Rejected: exempting `drive` from the fence, which would change the current-truth requirement that every unmarked write is refused while a run is in flight.
2026-10-10 T-0040 Each role runs as `claude -p <prompt> --model <models[role]> --output-format json --permission-mode auto --append-system-prompt-file <run>/system-prompt.txt --tools <list> --allowedTools <list>`, plus `--add-dir <worktree>` for the implementer and `--effort <level>` when the instance sets one. The process runs from the run directory with stdin closed. The `-p` prompt is the fixed text that names the run's input and output files and nothing else. That also removes the operator's chat message from every role's task (#28, absorbed).
2026-10-10 T-0040 `--permission-mode auto` with explicit allowlists: the classifier keeps checking each call that no rule allows, as it does for role agents today. Rejected: `dontAsk`. It is strict (Evidence), but it removes the classifier while roles run with no operating-system isolation (#37); operator ruling, 2026-10-09, to revisit once #37 lands. Build spec row R6's "nor `dontAsk`" therefore stays. Rejected: `bypassPermissions`, which R6 rightly forbids.
2026-10-10 T-0040 Tool limits. `--tools` is `Read,Grep,Glob,Bash,Write,WebFetch,WebSearch` for every role, and the implementer's list adds `Edit`. `--allowedTools` is `Read,Grep,Glob,Bash,WebFetch,WebSearch` plus three `Edit` rules on absolute real paths: `Edit(/<run>/output.md)`, `Edit(/<run>/scratch/**)` and `Edit(/<temporary directory>/**)`. The implementer's list adds `Edit(/<worktree>/**)`. The checkers therefore cannot use a file tool on the checkout under their run directory, which is the limit #24 part A wanted, absorbed. Bash stays unrestricted, so these limits cover the file tools only (Risk). Web tools are kept because role agents have them today. Every other tool the session offers today, such as sub-agents, task lists and notebook edits, is withheld: no role prompt in `factory/prompts/` asks for one. Rejected: withholding `Write` from the checkers, who must write `output.md`.
2026-10-10 T-0040 `--append-system-prompt-file` is the default. `--prompt-mode replace` passes `--system-prompt-file` instead, so the operator can measure the difference on a real ticket (Operator step 3). Rejected: deciding by measurement in this spec, which needs real model runs.
2026-10-10 T-0040 No `--bare`: it needs an API key and does not use the operator's subscription.
2026-10-10 T-0040 Effort per role comes from an optional `effort:` map in `instance.yaml`, keyed by role. An absent role gets no `--effort` flag. Values are passed through unchecked: Claude Code rejects a bad value before the run starts, which the driver records as a failed call. Neither instance sets `effort` in this change (Operator step 4). Per-role effort (#22) is absorbed.
2026-10-10 T-0040 A role process's reply is kept whole, as printed, in `runs/<id>/reply.json`. `run finish` gains `--reply FILE`, which records `session_id`, `total_cost_usd`, `num_turns` and `usage` under a `claude:` key in the run's `meta.yaml`. The reply's `result` text is not copied into `meta.yaml`, because it repeats `output.md`. This departs from the request's wording, which listed `result` too.
2026-10-10 T-0040 A failed call is a role process that exits non-zero or prints no JSON object on stdout. It is treated as a thrown `agent()` call is today: `run finish --status-override KILLED`, then a cleanup of a checker's checkout, then a park with `agent call failed: <role>: <message>`, and no retry. The message is the reply's `result` when there is one, else the last non-blank line of stderr, else `exit <code>`. A process that exits 0 with `is_error` set is routed on its output file like any other.
2026-10-10 T-0040 The two checkers run as concurrent processes, and both finish and record their results before the join, as `parallel()` does today. Ready sub-tickets build concurrently up to `--parallel N`, default 2. Rejected: unbounded, as `build.js` runs today, while concurrent `claude -p` processes are untested (Operator step 2).
2026-10-10 T-0040 On SIGINT or SIGTERM the driver sends SIGTERM to each role process it started. It sends SIGKILL to any still running 10 seconds later. It finishes each of its in-flight runs with `--status-override KILLED`, and runs a checker's cleanup. It parks nothing. It writes the stop to its status file, prints `{"ok": false, "ticket": "<id>", "stopped": "SIGINT"|"SIGTERM"}` as its last line and exits with 128 plus the signal number. Running `factory drive` again resumes from the stored state, as re-running a script does today. Rejected: parking on a stop, because a human stop is not a pipeline failure.
2026-10-10 T-0040 Without `--phase`, the phase follows the stored state. `ready-for-triage`, `ready-for-spec-writer` and `ready-for-critic` are intake. `ready-for-planner`, `planned` and `ready-for-parent-verify` are build. Any other state ends at once with "nothing to dispatch", as the scripts do. The driver never crosses the spec gate.
2026-10-10 T-0040 Progress output: one stdout line per step, `<ticket id> "<ticket title>": <step>`, where the ticket is the one the step concerns. A build step on a sub-ticket names the sub-ticket and its title (#47, absorbed). The last stdout line is one JSON object, the result the matching script returns, with `"ok": true` added. The status file is `drive/<parent id>.yaml` in the store, with keys `ticket`, `title`, `phase`, `pid`, `started`, `updated`, `running` (a list of `{run, role, ticket, pid}`), `last` (the last step line) and `ended` (null while running, then the result object). Rejected: changing `ticket show`, which `factory report` (#17) is meant to cover.
2026-10-10 T-0040 The status file is never committed. Part A appends `drive/` to the store's `.gitignore` block, under its own comment line, as `runs/*/tripwire.yaml` is. The file is a live view of one driver process: its `pid`, `updated` time and `running` list change at every step, and what lasts (each run's status, reply and cost, the ticket's state) is already in the run and ticket records. Rejected: committing it, which adds a churning file to every store commit. Rejected: a `drive/.gitignore` that ignores its own directory, which would put a second list of never-committed paths beside the store's block.
2026-10-10 T-0040 The driver has no stub mode. Tests put a stand-in `claude` first on `PATH`. Rejected: porting the scripts' `stubs` argument, whose stub agent needs Claude Code.
2026-10-10 T-0040 Park reasons and log events are the same as the scripts produce, so the parity scenarios compare records byte for byte, apart from ids, times and the order of the two checkers.
2026-10-10 T-0040 Retiring the scripts (the request's part F) is a separate ticket. A sub-ticket of this spec cannot wait for the operator's real runs, so the build would retire the scripts before the driver had run a real ticket.
2026-10-10 T-0040 The suite tests use a Python stand-in `claude`, so the suite needs nothing new. The acceptance scenarios also run the scripts under node, side by side with the driver, as earlier tickets' scenarios do.
2026-10-10 T-0040 The change is NEEDS-SPLIT, in three lettered parts (design.md).
2026-10-11 T-0041 1 (which commits are not drift): the test rule skips a first-parent commit that is the recorded merge (`merge.main_after`) of any merged sub-ticket of the same parent, from the current plan or an earlier one. Rejected: only the current plan's siblings. An earlier plan's merged sub-ticket is also this parent's own work, and the sibling-tests check already counts it the same way.
2026-10-11 T-0041 2 (later commits still count): only the sibling's exact merge commit is skipped, never merge commits in general. A later direct commit or merge from anywhere else that changes a test beside a design-named file is still drift, and the refusal names that commit.
2026-10-11 T-0041 3 (the resolve route): `resolve <id> --ruling F` also accepts a park whose reason starts `harness-bug: run start implementer:` and that was parked from `ready-for-implementer`. It writes F as the next ruling and returns the sub-ticket to `ready-for-implementer` at the same round, as a ruling on a `BLOCKED` park does. As with any ruling on file, the drift check does not run again for that sub-ticket. Rejected: widening `--redispatch` to this park. `--redispatch` re-runs the checkers today, and with no ruling on file a drift refusal would park the sub-ticket again. Rejected: accepting every harness-bug park from `ready-for-implementer`. A failed `run compose` leaves its run in flight, so the next run start would be refused again.
2026-10-11 T-0041 4 (refusal text): `--ruling` on any other park is refused with `--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an implementer's run start; <id> is <state> (<reason or 'no park'>)`, so the operator sees the new case.
2026-10-11 T-0042 The dispatcher (factory drive, and any later runner command) is exempt from the live-store fence's in-flight check, keeps the runs/ and worktrees/ refusal, and carries its own same-ticket guard (refuse while the ticket or a sub-ticket has a run in flight, or a live driver is recorded); overturns T-0040's rejection (operator, 2026-10-11, T-0042)
2026-10-11 T-0042 `factory drive` skips the fence's in-flight rule and keeps its location rule, which refuses a caller under the own store's `runs/` or `worktrees/`, marked or not. This is the operator's answer of 2026-10-11 (option A). It overturns T-0040's 2026-10-10 rejection of exempting `drive`. It is standing for every later runner command: the dispatcher is exempt from the in-flight rule and carries its own same-ticket guard.
2026-10-11 T-0042 `factory drive` given `--accept-harness` is fenced in full, in-flight rule included, because an acceptance rewrites the harness lock. This keeps the standing 2026-10-04 T-0024 rule that any command given `--accept-harness` is a write.
2026-10-11 T-0042 The same-ticket guard refuses `drive T`, with exit 2 and nothing written, in two cases. The first is when T or any of its sub-tickets has a run in flight. The second is when `drive/T.yaml` exists, has no `ended` value, and its `pid` is a live process. These are the operator's terms of 2026-10-11.
2026-10-11 T-0042 The guard runs whether or not the caller carries the marker, and on any store, a throwaway store included. Rejected: applying it only on an own store, as the fence is. The guard protects a ticket's records from two drivers, which matters on any store.
2026-10-11 T-0042 The guard runs inside the `drive` command, after the fence and the harness lock and before the driver sets its marker or writes its status file. A missing ticket skips the guard, so the existing "no such ticket" result is unchanged.
2026-10-11 T-0042 A pid counts as live when signal 0 reaches it, or is refused for permission. A missing, non-integer or dead pid does not block. A dead pid not blocking is the operator's term.
2026-10-11 T-0042 Rejected: checking that a live pid is a `factory drive` process. That would add a platform-dependent process query for a rare case, a pid reused after a SIGKILLed driver. The refusal names the pid and the status file instead, and README tells the operator to delete that file when the pid is not a driver.
2026-10-11 T-0042 The refusals read `<T> has runs in flight on it or its sub-tickets: <run ids>; drive it again once they finish` and `<T> is already being driven by pid <n> (<status file>); stop that driver or wait for it to end`. Neither names the marker, as the standing 2026-10-04 T-0024 decision requires of the fence's refusal.
2026-10-11 T-0042 README's driver step that told the operator to type the marker is removed. In its place README says why the driver needs no marker, and what it refuses instead. This is the operator's direction of 2026-10-11.
2026-10-12 T-0043 The command is `factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...`. - With no `--store`, it reads the store of the instance found from the caller's directory. As other commands do, it honours `FACTORY_STATE`, the environment variable that points a command at another store (tests use it to point at a throwaway one). With neither, it is refused with exit 2. A `--store` path with neither `runs/` nor `log/` is refused with exit 2.
2026-10-12 T-0043 `--until` is added beyond the request, so that a past figure can be reproduced on a store that keeps growing. - WHEN is an ISO date or date-time, taken as UTC when it has no zone. `--since` is inclusive and `--until` exclusive. - Runs are windowed by `started` and events by `ts`. Looking up who wrote and who critiqued a spec ignores the window.
2026-10-12 T-0043 The output is Markdown with fixed section headings and column orders, given in design.md part B. Rejected: JSON (Out of scope).
2026-10-12 T-0043 `stats` is handled like `paths`: no instance needed, no live-store fence (the guard against role runs writing the store), no harness lock check, and `--accept-harness` ignored. - Why: it writes nothing, and it must read a live store while runs are in flight and from a checkout the instance has not accepted, such as a verifier's. - The fence's read-only list in the documents gains `stats`. This follows the standing 2026-10-04 rule that a new command is fenced until it is added to that list. - Rejected: adding it only to `READ_ONLY`, as triage assumed. The lock would still refuse it everywhere but the accepted runtime.
2026-10-12 T-0043 The rows are keyed by role and model, summed over every store given, and ordered triage, spec_writer, critic, planner, implementer, reviewer, verifier, then any other role by name, and models by name within a role.
2026-10-12 T-0043 A row's "runs" counts runs with a verdict other than `KILLED`. `KILLED` runs have their own column, and runs still in flight (status `running` or none) are left out. This is how the request counted (94 reviewer runs plus 5 killed).
2026-10-12 T-0043 A changed outcome is a verdict of `REQUEST-CHANGES`, `ESCALATE`, `FAILED`, `SPEC-DEFECT`, `REVISE` or `BLOCKED`, from any role. This is the request's list.
2026-10-12 T-0043 BLOCKING findings are counted for the reviewer and the critic only. A finding is a line of `output.md` that starts with `[BLOCKING]`, after optional leading spaces and an optional `-`, `*` or `1.` marker, and that does not contain `RESOLVED`. - Rejected: counting every mention of the word, which counts "No BLOCKING findings". - Rejected: counting round-2 restatements of a fixed finding.
2026-10-12 T-0043 Park reasons are normalised by a fixed list in the module, extended when a new reason appears. The steps are: 1. take the first line; 2. replace run ids with `<run>`, ticket ids with `<ticket>`, and 7-to-40-character hex strings that contain a letter with `<sha>`; 3. keep the first two `: `-separated fields; 4. trim, and drop a trailing colon.
2026-10-12 T-0043 A park counts under its corrected reason. A `park.corrected` event replaces the reason of the latest earlier `ticket.parked` event of the same ticket whose reason equals the correction's `previous`. A correction that matches no park changes nothing. - Only corrections dated before `--until` apply, so a past figure stays repeatable after a later correction. The park itself is windowed by its own `ts`. - Why: the operator corrects a reason because the recorded one was wrong, as on T-0040.3, where a refusal was mis-filed as a harness bug. Counting the original would report the error the human fixed. - Rejected: ignoring corrections. Rejected: applying every correction whatever its date, which lets a later correction move a figure quoted for a past cut.
2026-10-12 T-0043 Section B's decision rows are: - `spec approved`: `approval.recorded` events with `kind: spec`; - `spec changes requested`: `human.resolved` events with `kind: request-changes`; - one `resolved: <kind>` row per other `human.resolved` kind; - one `merge refused: <reason>` row per `merge.refused` reason (`head does not contain main` is the conflict case); - `archive refused`: parks whose normalised reason is `archive` or starts with `archive:`.
2026-10-12 T-0043 Section C is built as follows: - Each catch is a verifier run with `SPEC-DEFECT` or an implementer run with `BLOCKED`. - Its spec is the parent ticket's (the ticket id without a trailing `.N`) at the run's `spec_version`. - "Written by" is that version's `spec.added` source when the source is a run id. It is `human` when the source is anything else (a gate edit or an amendment), and `unknown` when the version has no `spec.added` event. - "Critiqued by" is the latest critic run of the parent at that `spec_version`, or `none`. - The REVISE count is all critic REVISE runs of the parent. - A second table splits approved tickets by whether they had a REVISE and counts those with a later catch. This answers the REVISE question with no further tool.
2026-10-12 T-0043 Cost per run comes from the run's cost record (`claude.usage`, `claude.total_cost_usd`) when present, else from its transcript, else nothing. Each row names how many runs used each source. This is the owner's proposal. - Context tokens are input + cache-read + cache-creation tokens, the definition `factory/cost.py` already uses. - Dollars come only from cost records, because transcripts carry none. - Killed runs count, because they spent tokens.
2026-10-12 T-0043 Transcripts are searched only under the `--transcripts` directories, for every `*.jsonl` file at any depth. - Rejected: searching `~/.claude/projects` by default. That ties the command to one machine's layout and costs about 12 seconds on every call.
2026-10-12 T-0043 A transcript is matched to a run R of a store S as follows: - Its first user message that names a run directory, `<P>/runs/<R>/`, gives the candidate. A user message is skipped when it starts with `[Workflow harness — user request]`, which relays the operator's words. - The transcript's first timestamp must lie between R's `started` and `finished`. - A P that is the path of another store given on the command line rules the transcript out. - A candidate whose P is S's path, or S's path before a `store.migrated` event, wins. Otherwise a single remaining candidate is taken. Otherwise there is none. - Rejected: requiring S's path. That loses every run from before an unrecorded move (this store's first 103).
2026-10-12 T-0043 Usage counts each message id once, taking its last record. A record with no id counts alone. The `calls` column of `factory/cost.py` then counts message ids. This fix applies to `factory/cost.py` itself and absorbs issue #61, the report of the double count.
2026-10-12 T-0043 Implementer gate failures fixed before hand-off are read from the transcript. - The gate commands are the backticked commands on the "Gate commands" line of the run's `input.md`. Each is matched by its own text: what follows the wrapper's last `; `, with the closing `)` removed. - A gate counts once per run when a Bash call containing it returned an error (`is_error: true`) and a later call returned none. - A run with no transcript or no gate line is "not recorded", not zero. - Rejected: the implementer's output, which states only the final results. - The text match can miss a command the implementer ran in another form. That is a known limit, stated in README.
2026-10-12 T-0043 `docs/design.md`'s model-per-role paragraph cites `factory stats` and the reviewer, critic, verifier and implementer figures from sections A and D, for `--until 2026-10-07T12:00` with `--transcripts`. This is part E of the request. Its retro half moves to the retro's own issue, #42 (Out of scope).
2026-10-12 T-0043 `docs/principles.md` §4 gets the command's figure, 3 BLOCKING findings, in place of 1 (Evidence), and its "Implemented by" line names `factory stats`.
2026-10-12 T-0044 Every change must add or change at least one requirement in the spec store, the folder of requirement files that says what the harness does. That folder holds one file per capability, a named area of behaviour. For example, build-dispatch covers how role runs are started and routed. The store refuses a change with no such addition (`factory/specstore.py:202`: "no delta part"). Triage, the first role, which accepts the request, named no capability, because nothing here changes behaviour. This change therefore adds a new capability, `harness-code`, to hold the checks that the removed code stays gone. It also adds to build-dispatch one requirement that pins the in-flight refusal this change merges, since no existing requirement covers it. Rejected: putting the removal checks in build-dispatch, which describes how runs are started, not what the source contains.
2026-10-12 T-0044 `gitops.repo_root` keeps its name and loses its parameter. All 12 callers become `gitops.repo_root()`. Rejected: deleting the wrapper and calling `instance.repo_root()`, which would also move imports in `compose.py` and `gitops.py` for no gain.
2026-10-12 T-0044 Of the two writes of the store's `.gitignore` block when a build role starts, the one inside the build-role setup function `_start_build_run` (`cli.py:377`) goes. The call at `:229` covers every role. Rejected: removing `:229`, which would leave triage, spec writer, critic and planner runs without the write.
2026-10-12 T-0044 The two in-flight refusals become one condition over the five roles, written as an explicit list: `("triage", "spec_writer", "critic", "planner", "implementer")`. Rejected: `a.role not in ("reviewer", "verifier")`, which would silently cover a role added later.
2026-10-12 T-0044 The refusal in compose, the step that writes a run's input file, keeps its place at `compose.py:420` and changes its text to `compose: unknown role {role}`. Rejected: deleting that branch, because a hand-edited run record would then get an empty input and no error.
2026-10-12 T-0044 The store module's docstring keeps only its first line. Rejected: keeping "Every write goes through here", a claim this ticket did not verify.
2026-10-12 T-0044 The design documents that still describe `force_push_allowed` stay as they are, and the gap is recorded here. Changing `docs/design.md` would need a changelog entry and a re-copied `docs/prompts/05-implementer.md`, and prompts are out of this round. In practice the setting has done nothing since the shipped prompt hardcoded "never rebase".
2026-10-12 T-0044 A change to factory/**, bin/factory, agents/**, pyproject.toml or uv.lock touches the protected class harness and must declare it on the spec's Protected paths line; T-0044 wrote 'none' and its merge was refused (operator accepted with resolve --accept-paths, 2026-10-11)
2026-10-12 T-0045 Test files never import from another test file. Shared code lives in two non-test modules. `tests/factory/_cli.py` holds the generic helpers: constants, wrappers, the JSON readers, the ticket reader and the two setups. `tests/factory/_fixtures.py` holds the scenario fixtures that more than one test file uses. Standing: a later ticket that needs a helper in a second file moves it to one of these two modules. Rejected: one module for everything, which would put the 190-line fixture in `test_shepherd.py` that drives a ticket through a whole build beside eight-line wrappers. Also rejected: `conftest.py` fixtures, whose names apply to every file, while four files define their own `target`.
2026-10-12 T-0045 The JSON reader comes in two forms. `js` only parses. `js_ok` asserts exit 0 and then parses. Each file imports the form its own copy had, under the name `js`, so no call site changes and the exit check stays opt-in per caller. Rejected: a `check=` argument at each call, which touches every call site.
2026-10-12 T-0045 `conftest.py` sets both `PYTHONDONTWRITEBYTECODE=1` in the environment and `sys.dont_write_bytecode = True`. Rejected: adding `env=` at each Python start, the request's suggestion. It misses the two in-process loads, as the prototype showed.
2026-10-12 T-0045 The check that nothing is written into the checkout leaves out `tests/factory/__pycache__`. pytest writes two files there before `conftest.py` can act. Only the person running pytest can stop that.
2026-10-12 T-0045 The removed test is `test_p0_cli.py`'s KILLED-override test. The test in `test_empty_output.py` keeps all three of its checks.
2026-10-12 T-0045 The approved-parent helper takes a caller's `ok` function, the ticket id and a spec file. It runs the five calls and returns the ticket id. Ticket creation stays with the caller. Sites that use `spec add --from-run`, assert a step, or put other work between steps keep their own calls. Cut: the request's `plan` argument. A plan is not part of the repeated five calls.
2026-10-12 T-0045 The class-level `cli`/`ok` pair comes from one base class. Each class still builds its own environment, so the instance copy, the venv and the PATH stand-in stay where they are. A class whose `cli` differs overrides `cli` only.
2026-10-12 T-0045 The acceptance checks name helper names (`REPO`, `js`, and so on) and the one test this change removes. The subject of this ticket is the suite's own structure, so those names are the behaviour being checked.
2026-10-12 T-0045 Changed in round 2: the checks that compare with a base compare across each of this ticket's own merges into `main` (each `Merge factory/T-0045.<n>` commit against its first parent), plus the unmerged commits of the checked-out branch (`git merge-base HEAD main` against `HEAD`), and add up the results. Other tickets' changes to the same files are therefore never counted, whichever order they merge in. Rejected: v1's single base, the commit before this ticket's first merge, which counts T-0044's two assertion changes if T-0044 merges in between (critic, round 1). Rejected: the critic's suggested THEN with a second outcome when T-0044 has merged. Three more de-bloat tickets in the same sweep (T-0046, T-0047, T-0048) edit the same files and would each need a clause of their own.
2026-10-12 T-0046 The shared run lister skips a run whose record file is empty, as the scratch clean-up does today. (The record file is `meta.yaml`, which each run's directory holds; the clean-up is `clear_scratch`, the function that deletes finished runs' scratch directories.) The other three callers would otherwise crash with `AttributeError` if they read the record while a run started in parallel is still writing it. This is the one difference from today's behaviour, and it can happen only during that write. Rejected: an iterator that hands back an empty meta for each caller to handle, which would leave the ticket, role and finished filters copied at every caller.
2026-10-12 T-0046 The event log gets two readers. `store.log_lines` yields raw lines and leaves malformed-line handling to the caller, so `factory log tail` still prints raw text and the command-line readers still raise on a line that is not JSON. A new `cost._log_records` keeps the cost report's skip-malformed behaviour and is shared with the stats report (`stats.py`). `cost.py` stays free of imports from the `factory` package, as the request allows, because a test (`test_cost_once.py`) loads it by file path. Rejected: one strict reader for all four callers, which would change what `factory stats` does with a malformed line.
2026-10-12 T-0046 The dispatcher's shared piece is a function that formats the park reason, not one that parks. Three of the 18 sites pick their reason inside a conditional expression (`drive.py:192`, `453`, `517`), and a helper cannot `return` from its caller. It is named `_harness_bug` so that it is not confused with `drive.py`'s existing `_fail` (`drive.py:664`), which prints a failure and exits.
2026-10-12 T-0046 Part H of v2, one walker for spec sections and heading blocks, is cut (operator, spec gate, 2026-10-12): the most risk for the least saving. The spec-parser comparison stays as a REGRESSION check, because part A changes `specstore.critic_rounds`.
2026-10-12 T-0046 The helpers' names and modules follow the request where it gave them (`store.record_transition`, `store.in_flight_runs`, a gitops helper, `section(text, heading)`). Where it did not, design.md names them.
2026-10-12 T-0047 1. The command-line code becomes six modules. `factory/cli.py` keeps the parser, the entry point, the role lists and the ticket, run, spec and plan commands. The five new modules are: - `factory/drift.py` for the spec-drift checks; - `factory/setup.py` for `init`, `store migrate` and `paths`; - `factory/gates.py` for results, the merge gate, join, the parent check and archive; - `factory/human.py` for `approve-spec`, `request-changes`, `resolve`, `decision add` and `spec amend`; - `factory/common.py` for the helpers more than one module calls, and the live-store fence. The fence refuses a write to the live store from inside a role run. The names follow the request. `setup.py` is kept because no build tool reads it (Evidence).
2026-10-12 T-0047 2. `fence` and `_in_flight` go to `factory/common.py`. Rejected: `factory/instance.py`, where the body of `fence` would change (Evidence). Also rejected: a sixth module, which would add a header for two functions.
2026-10-12 T-0047 3. `ticket_head` goes to `factory/gates.py`. It reports the commit that the checkers review and verify, and the gates record their results against that commit. Without it, `factory/cli.py` ends at about 906 lines (Evidence).
2026-10-12 T-0047 4. `stats_cmd` stays in `factory/cli.py`, where its comment about `ROLES` is true. `paths_cmd` moves to `setup.py`, as the request asks.
2026-10-12 T-0047 5. Each module imports what it uses by name, for example `from factory.common import _rel, out`. No function body changes, so a moved function reads exactly as it did. Rejected: importing the module and qualifying each call, such as `common.out(...)`, which edits nearly every body. Underscored names keep their underscore when another module imports them.
2026-10-12 T-0047 6. `factory/setup.py` uses `import shutil` and keeps calling `shutil.copy2` through the module. The test that replaces `shutil.copy2` therefore still reaches the moved code.
2026-10-12 T-0047 7. The rule that a move is not a rewrite is checked by machine. Across this change, every top-level function, class and assignment of `factory/*.py` must keep its exact source text. The comparison covers each of this ticket's merges and the checked-out branch, as T-0045's suite checks do. Other tickets' changes are therefore never counted.
2026-10-12 T-0047 8. The request's "within ±50 total Python lines" becomes "at most 100 lines added". The prototype, with one-line docstrings, added 60 lines: five module headers of imports, less the imports `factory/cli.py` no longer needs. With rule 7 in place, the line bound only limits header growth. Rejected: ±50, which would push the implementer to cut docstrings.
2026-10-12 T-0047 9. Acceptance names modules, functions and constants. The subject of this ticket is where code lives, so those names are the behaviour checked. T-0045 decided the same for the test suite's helpers.
2026-10-12 T-0047 10. The six harness-code checks that count text in `factory/cli.py` now count it across `factory/cli.py` and the five new modules (Evidence). The expected numbers do not change. Rejected: leaving them, which fails three and empties three.
2026-10-12 T-0047 11. Docs: `README.md:1171` and `docs/principles.md:106-107` name `factory/gates.py` for the moved gate commands. The README status date moves to the day of the change, as "Maintaining this page" asks. Every other doc line that names `factory/cli.py` stays true and is left alone.
2026-10-12 T-0047 12. Standing: no harness module imports `factory.cli` except the entry point (`__main__.py`), the driver (`drive.py`) and the stats report (`stats.py`). A command that a new module needs comes from that module's own imports. This states the request's rule with the third importer, which the request left out.
2026-10-13 T-0050 The instance file is the only source of a role's model. `run start` records `models[role]` from the instance, and `--model` serves only as a cross-check. This is a standing decision: a later caller, including whatever replaces the Workflow scripts, gets its model from `run start` and never chooses one.
2026-10-13 T-0050 A `--model` that differs from the instance's model is refused with exit 2, before a run id is reserved, so nothing is written. The error reads exactly `model <given> refused for <role>: the instance names <instance model>`. It contains no backtick, `$` or double quote, because the build script passes a park reason through a shell command. Leaving out `--model` is still accepted.
2026-10-13 T-0050 The requester's part B is cut: the scripts do not switch to launching on the model `run start` returns. That value also reaches the script through the clerk's report, so launching on it would trust a second relay. Today the scripts launch on the same value they sent as `--model`. With part A, `run start` accepts that value only when it is the instance's model. Rejected: launching on the returned model, which adds a relay. Rejected: comparing the returned model with the sent one, which guards a failure the evidence does not show (the clerk changing the command it runs).
2026-10-13 T-0050 When the clerk misrelays a model, the Workflow run parks the ticket at that role's run start, with reason `harness-bug: run start <role>: <the refusal>`. The run does not go ahead on the instance's model. Rejected: having the scripts stop sending `--model`. `run start` would then pick the right model, but the agent would still be launched on the misrelayed one.
2026-10-13 T-0050 The requester's part C (a test) is kept as a new suite test file for `run start`. The two Workflow routes are checked by acceptance scenarios that run the scripts under node, as the standing T-0023 decision does for workflow fixes.
2026-10-13 T-0051 Part A runs the suite with pytest-xdist alone (`-n auto`): 66.80 to 146.81 s per run, and under 170 s for two at once. Rejected: calling the CLI in-process, alone (113 to 117 s) or with pytest-xdist (27 to 31 s). The test package's name shadows the harness package, so it needs a swap of the module table around every call, or a `tests/__init__.py` that writes into the checkout. It would also stop about 5,400 CLI calls per run from crossing a real process boundary. The parallel run alone meets the target with margin.
2026-10-13 T-0051 pytest-xdist is switched on once, in `pyproject.toml` (`[tool.pytest.ini_options] addopts = "-n auto"`). So the gate command, the README's suite command and every current-truth scenario that runs the suite use it with no text change. That is Part B. Rejected: adding `-n auto` to `gate_commands`, which changes an infra path and leaves every scenario command running sequentially.
2026-10-13 T-0051 Standing, for later tickets: the harness suite runs in parallel worker processes. A new test must not depend on test order. It must not share a file, port, environment variable or other process-wide state with another test, outside its own `tmp_path`.
2026-10-13 T-0051 The suite gains a dev dependency, pytest-xdist, which `uv run --frozen` installs from the lock. This is a deliberate exception to the 2026-10-04 T-0023 decision, "the suite does not need node today and adding that would change what the gate needs", and the request asks for it.
2026-10-13 T-0051 The flaky test is fixed at its measured cause: a file lock around both stand-ins' call counter. Its 2-second sleeps stay. Rejected: the triage's reading, that the sleeps should become a condition the test waits on. No failure of that kind was seen, though one stressed failure has no kept output (Evidence).
2026-10-13 T-0051 The time bounds are under 180 s for one run, from the request's target of 3 minutes, and under 300 s for each of two runs at once. Measured: 66.80 to 146.81 s, and 162.35 to 169.66 s.
2026-10-13 T-0051 `run last-message` alone decides whether a run was waiting, from the text it keeps, and prints `"waiting": true` or `false`. The driver and both scripts read that field. Rejected: a pattern in each of the three callers, three definitions of one rule. Also rejected: a separate command, one more store call per empty run.
2026-10-13 T-0051 A kept message counts as waiting when, ignoring case, it contains the word `wait` or `waiting`, or `still running`, `still in progress` or `in the background`. It is a hint, not a route: a wrong match only adds a misleading phrase to a park a human reads anyway.
2026-10-13 T-0051 The park reason is `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command` when either of the two runs was waiting, and `EMPTY-OUTPUT from <role>` otherwise. The prefix is kept so that anything that reads the reason's start reads it as before. A failed `run last-message` call counts as not waiting.
2026-10-13 T-0051 The README's "Empty output" entry stops saying that it has not fired on a real ticket. It fired on T-0047.2.
2026-10-13 T-0048 Part A freezes the three `dev/` build documents in place, with a header at line 3. Rejected: moving them to `dev/archive/`, which breaks the `Parent:` links in the plan and skeleton and every path cited in `decisions.md`, `dev/issues.md` and past answers.
2026-10-13 T-0048 Standing: a frozen document is never edited again. Current truth checks that each one equals its text at `7231670` apart from the header.
2026-10-13 T-0048 Part B keeps the tested-but-unfired features in the Built list and changes README's rule instead. The rule now says an entry appears once a feature is built and tested, and says whether it has run on a real ticket. Rejected: moving the three that are still unfired (tripwire, sibling-tests check, the drift check's sibling-merge exception) under "Where this can go". They are built, and that section is for intended work.
2026-10-13 T-0048 The protected-path refusal is corrected to "has fired", against the request's "still true and kept". The log shows the refusal on T-0044.1 and the operator's `--accept-paths`.
2026-10-13 T-0048 `docs/design.md:3` drops its date and points to the changelog, which dates every change. Rejected: bumping the date, which every later design change would also have to do.
2026-10-13 T-0048 Part C homes: - The live-store fence lives under "Where a human decides". - The driver's own same-ticket guard lives in its how-to. The request asked to cut that paragraph to one line, but no other section describes the guard, so the paragraph keeps the guard and drops only the fence detail. - The final check's skip lives in "The build workflow, step by step". - The store branch lives in "How the factory uses git". - Other agent hosts live only in `docs/design.md`.
2026-10-13 T-0048 "Not built" and "Where this can go": - "Where this can go" keeps the named intended work. - "Not built" becomes one paragraph of today's facts, with no bullet that repeats one there. - The bold name "Current truth for the factory itself" moves to "Where this can go", because current truth checks for that phrase.
2026-10-13 T-0048 History moves to one new changelog entry, 72, for issue #101. "Related work and history" keeps every issue reference, as #23 asks. It also keeps its last sentence of current figures (tickets, sub-tickets, runtime commit), which the change re-derives.
2026-10-13 T-0048 Standing, for the operator to confirm or strike at the gate: README gets a line budget of 1,110. A later change that needs more room raises it in its own spec. The request asked for a drop of at least 150 lines, but honest one-home cuts give about 90 (prototype: 1,101 lines). The budget is set at that result, with 9 lines of slack, rather than padding the cuts to reach 150.
2026-10-13 T-0048 Part F rules, standing for later `harness-docs` scenarios: - A scenario finds a changelog entry by the words it opens with, "`<n>. After issue #<k> `", and checks that exactly one entry matches. It never uses the last line or an entry count. - A scenario does not check what one change left untouched against `main` or a fixed commit. The two requirements made only of such checks are removed. - Whitespace is checked once, over the maintained documents in full. The instance's gate command `git diff --check main...HEAD` (`.factory/instance.yaml:23`) still checks each change. - The `fill=` comparisons with `main` stay. They hold on every change that keeps the placeholders filled in the run copies, and a change to those is a change to the prompts. - Each check of the frozen build spec is dropped, with the clause that required it. - Principle 2's status clause is dropped, because the principle no longer has a status line.
2026-10-13 T-0048 One sub-ticket. The prototype's diff is 331 lines, under the 400-line bound, and every part edits README, so parallel sub-tickets would collide. The spec names no seams, so the harness builds it whole. Rejected: the request's suggested split into A+F, B+E, C and D.

## Approved changes not yet archived

none

## Your prior findings (round 1)

## Critic review, round 1 (spec v1 for issue #108)

What I checked myself, from `~/dev/spec-factory` at `525d73f`:

- Cited paths and lines: `agents/factory-planner.md` line 2 (unquoted `: ` present); `factory/setup.py` 179-184 (copy loop with only the `if not exists` branch), 201-204 (`store.initialised` event, "restart the session" line, `out({...})` with `agents`); `tests/factory/test_instance.py` 57-59, 115-135 (key-based reads of init's JSON, byte comparison with templates); `tests/factory/test_store_branch.py` 269 (named keys); `tests/factory/_cli.py` 16 (`REPO`, imported as `from ._cli import`); `README.md` 463, 575-588, 706, "Maintaining this page" at 1057; `docs/changelog.md` last entry `72. After issue #101 (2026-10-11), …`, 72 numbered entries, contiguous; `docs/design.md` 880; `git log -- agents/` gives `f5d8203`, `9b45041` only; `agents/` holds exactly the six `factory-*.md` files; none of the four descriptions contains `"` or `\`; `pyproject.toml` depends on `pyyaml>=6` and sets `addopts = "-n auto"`; this repo has no `.claude/agents/`; `cmp` of the six templates against `~/dev/nanobot-upstream/.claude/agents/` (read only): all same.
- Acceptance commands run as written, under the fresh-HOME wrapper, on this checkout (none runs the suite): frontmatter scenario printed clerk/stub `keys=ok` and the other four `keys=unparsed`; description scenario printed `text=changed rest=same` four times then `others=same`; init-edited-copy scenario printed `exit=0 stale=absent kept=yes named=0 others=0` (stderr empty, JSON has no `stale_agents`); init-missing-copy scenario printed `exit=0 created=factory-triage.md stale=0 same=6 differs=0`; README scenario printed `row=0 step=0 missing=1`; changelog scenario printed `CONTIGUOUS`, `0`, `0`; budget scenario printed `readme=within`, `check=0`. Every "today" result in verification.md matches.
- Tests pinning old behaviour: searched `tests/factory/` for init JSON equality, stderr-empty assertions and `.claude` writes. All init assertions read named keys; the only `.claude` manipulations are unlinks (test_instance 127, 145; test_live_store_guard 42-46). No test pins the absent `stale_agents` key or an empty stderr on init. "Tests to change: none" holds.
- Decision log: the standing `init` decisions (T-0023, T-0025: refusals, store branch, exclude file) are untouched by this change. Approved changes not yet archived: none.
- Not checked: the suite-fails scenario and the prototype's `590 passed` (both need a suite run); Claude Code's own frontmatter parser (the spec says so itself).

Findings

[BLOCKING] 6 proposal.md, Operator steps, first paragraph
Problem: It uses two terms specific to this system that no human-facing section has glossed, "the Driver" and "the runtime upgrade"; a reader new to the system has to infer who performs the step and what must happen first.
Evidence: "Driver" is glossed only under Out of scope ("the session that runs the Nanobot target"), and the upgrade step is explained only under Risk ("the usual runtime upgrade and `--accept-harness` step"); neither is a section the gate operator reads. Problem, Evidence and Decisions do not gloss either.
Suggested fix: Open the step with the glosses in place, for example "After the merge, and after the factory's runtime checkout has been moved to the merged revision and accepted with `--accept-harness`, the Driver (the session that runs the Nanobot target) refreshes …", and keep the Out of scope sentence as is.

[SHOULD-FIX] 6 proposal.md, Evidence first bullet and Decisions bullet 4
Problem: Two more system-specific terms go unglossed where the operator meets them: "the fresh-HOME wrapper" (Evidence, first bullet) and "the instance's own store" / "a throwaway store (`FACTORY_STATE` naming another store)" (Decisions, bullet 4); "store" and "instance" appear nowhere earlier in the human-facing sections.
Evidence: Problem glosses template, `factory init`, target, `inlineRoles` and `factory drive`, but not store, instance or the wrapper.
Suggested fix: In Evidence say "under the harness's running-code wrapper, which gives the command a throwaway HOME", and in Decisions bullet 4 say "for the target's own store (the directory, under its `.factory/`, that holds the factory's tickets and runs); an init pointed at another store by `FACTORY_STATE` …".

[NIT] 3 design.md, part D
Problem: README's "Maintaining this page" says a change to a command also bumps the date in the status header (line 1069); part D does not mention it, and `init`'s output changes.
Evidence: README line 9 reads "Current state as of 2026-10-13"; if the merge lands on a later day the header is stale and the code reviewer is told to treat that as a finding.
Suggested fix: Add to D.2 "and set the status header's date to the merge date if it differs", inside the four-line net budget (it changes no line count).

No other findings. Grounding, testability, scope and consistency hold: every cited path and line exists; each NEW scenario fails today for the stated reason and would fail a stub (the suite-fails scenario catches a test that asserts nothing; the description scenario catches a rephrased description; the edited-copy scenario catches an overwrite or a missing stderr line); the change fits one PR; protected paths `agents/**` and `factory/**` are declared; the changelog entry format matches the existing `<n>. After issue #<k> (<date>), ` pattern; the README budget (1,110 lines, store-setup current truth) leaves four lines, which part D respects.

Out-of-scope observations
- The new init tests in design part C overlap `test_init_is_idempotent_and_creates_only_what_is_missing` and the deleted-copy test in `tests/factory/test_instance.py` 115-135; the implementer should reuse the `target` fixture and `cli` helper rather than new setup code (harness-suite: shared code lives in helper modules).

Prior findings: none (round 1).

STATUS: REVISE
CONFIDENCE: high; every cited path, line and "today" result was checked on this checkout, and the one BLOCKING finding is a gloss the rubric names explicitly, with a one-clause fix.
ESCALATIONS: none

## Previous spec version (v1), as a unified diff to v2

--- specs/T-0052/v1.md
+++ specs/T-0052/v2.md
@@ -13,7 +13,7 @@
 
 ## Evidence
 
-- Parsing each template's header with PyYAML `safe_load` (lines between the opening `---` and the next `---`), run with `uv run --frozen python` under the fresh-HOME wrapper, gives:
+- Parsing each template's header with PyYAML `safe_load` (lines between the opening `---` and the next `---`), run with `uv run --frozen python` under the harness's running-code wrapper (which gives the command a throwaway HOME, so it cannot write the operator's real home directory), gives:
 
   | Template | Result |
   |---|---|
@@ -60,7 +60,7 @@
 - The suite test checks every `agents/*.md`, one case per template, and each failure names its template. It requires a parseable header that is a mapping with `name`, `description`, `model` and `tools`.
 - `factory init` reports an existing copy that differs from its template in a new JSON field, `stale_agents` (each copy's path, as `agents` gives created copies' paths), and with one stderr line per copy naming the copy and its template. The exit stays 0 and the copy is left byte for byte as it was. Rejected: overwriting it, which would discard an operator's deliberate edit. Rejected: refusing with exit 2, because a stale copy does not stop a run that uses `inlineRoles`.
 - "Differs" means any byte difference. A copy the operator edited on purpose is reported too: that is a report, not a refusal.
-- The comparison runs only where init installs copies: for the instance's own store. An init on a throwaway store (`FACTORY_STATE` naming another store) does not read `.claude/agents/`, and its `stale_agents` is `[]`.
+- The comparison runs only where init installs copies: for the target's own store (the directory under the target's `.factory/` that holds the factory's tickets and run records). An init pointed at another store by the `FACTORY_STATE` environment variable, as the tests do with a throwaway store, does not read `.claude/agents/`, and its `stale_agents` is `[]`.
 - A run of init that only reports differing copies writes no `store.initialised` log event and prints no "restart the session" line, because it wrote nothing.
 - Standing rule for later tickets: `factory init` never overwrites a target's existing agent copy; it reports one that differs from its template.
 
@@ -68,7 +68,7 @@
 
 Small. The template change alters four header lines that no run reads today (every run uses `inlineRoles` or `factory drive`). The init change adds one output field and stderr lines. It changes no exit code, writes no new file, and the existing init tests that read the JSON output still pass on the prototype (590 passed). Callers that read init's JSON by key (the tests, the operator) are unaffected by an added key.
 
-The merge moves the harness revision, because `agents/` and `factory/` are harness paths. Each target then needs the usual runtime upgrade and `--accept-harness` step before it runs the new code.
+The merge moves the harness revision, because `agents/` and `factory/` are harness paths. The factory runs from a separate runtime checkout pinned to an accepted harness revision, so no target runs the new code until the operator moves that checkout to the merged revision and accepts it with `--accept-harness` (the usual upgrade step).
 
 `README.md` is at 1,106 lines against its 1,110-line budget. The README edits below must add at most four lines net.
 
@@ -76,7 +76,7 @@
 
 ## Operator steps
 
-- After the merge and the runtime upgrade, the Driver refreshes Nanobot's four copies in `~/dev/nanobot-upstream/.claude/agents/` (planner, spec-critic, spec-writer, triage) from the fixed templates and commits them there. Check: running `factory init` from Nanobot's repository root then prints `"stale_agents": []`.
+- After the merge, and after the factory's runtime checkout (the separate worktree the factory runs from) has been moved to the merged revision and accepted with `--accept-harness`, the Driver (the session that runs the Nanobot target) copies the four fixed templates (planner, spec-critic, spec-writer, triage) from `~/dev/spec-factory/agents/` over the copies in `~/dev/nanobot-upstream/.claude/agents/` and commits them there. Check, read only: `for f in ~/dev/spec-factory/agents/factory-*.md; do cmp -s "$f" ~/dev/nanobot-upstream/.claude/agents/$(basename "$f") && echo same || echo "differs $(basename "$f")"; done` prints `same` six times.
 
 === design.md
 ## Proposed change
@@ -95,12 +95,12 @@
    2. In the copy loop (lines 180-184), add an `elif` for an existing copy. When `(dest / src.name).read_bytes() != src.read_bytes()`, append `str(dest / src.name)` to `stale` and print one line to stderr: `factory init: <copy path> differs from its template <template path>; left as it is`.
    3. Never write the copy. Add `"stale_agents": stale` to the final `out({...})` beside `"agents"`. Leave the `store.initialised` event condition and the "restart the session" line as they are.
 
-   In the same new test file, add suite tests for this: an edited copy is listed and kept; a deleted copy is created and not listed; matching copies give `stale_agents == []`.
+   In the same new test file, add suite tests for this: an edited copy is listed and kept; a deleted copy is created and not listed; matching copies give `stale_agents == []`. Build each target with the shared helpers in `tests/factory/_cli.py` (`git_repo`, `cli`, `js`), the way `tests/factory/test_instance.py`'s `target` fixture does, and add no new setup code. `_cli.py` says a test file imports helpers from there, never from another test file, so do not import that fixture. Do not add these tests to `test_instance.py`: they overlap `test_init_is_idempotent_and_creates_only_what_is_missing` there, but leave that test as it is.
 
 D. Documents.
    1. `README.md` line 463, the `.claude/agents/factory-*.md` row's "Written by" cell: keep "`factory init`, when they are missing" and add that init reports a copy that differs from its template and leaves it. The row must contain the words `differs from its template`.
    2. Step 1 of "Adopting the factory in a repo" (README lines 579-587): add one sentence saying a copy that differs from its template is listed under `stale_agents` and named on stderr, and is never overwritten.
-   3. Net README growth: at most four lines.
+   3. Net README growth: at most four lines. README's "Maintaining this page" asks a change to a command to bump the date in the status header (line 9, now "Current state as of 2026-10-13"): set it to the merge date if that differs. This changes no line count.
    4. `docs/changelog.md`: append one entry, the next number after the last, starting `<n>. After issue #108 (2026-10-13), `. It says the four headers did not parse and are now quoted, that the suite now parses every template's frontmatter, and that init reports a differing copy in `stale_agents` without overwriting it. It also says Nanobot's copies are refreshed by its Driver. The entry must contain the words `frontmatter`, `stale_agents` and `Nanobot`. If another ticket takes the next number first, take the next free one: the entries must stay numbered without a gap.
 
 Size: about 4 template lines, about 7 lines in `setup.py`, a new test file of about 50 lines, 2 README lines and 1 changelog line.
@@ -165,7 +165,7 @@
 === verification.md
 ## Acceptance
 
-Run every scenario from the repository root after `uv sync --frozen`, inside the fresh-HOME wrapper. I ran each one on this checkout (`525d73f`). I also ran the five store-setup scenarios on a prototype of the change in my scratch directory, where each printed its THEN exactly. The prototype had no README or changelog edits, so the three harness-docs scenarios were run on this checkout only.
+Run every scenario from the repository root after `uv sync --frozen`, inside the harness's running-code wrapper (a throwaway HOME). I ran each one on this checkout (`525d73f`). I also ran the five store-setup scenarios on a prototype of the change in my scratch directory, where each printed its THEN exactly. The prototype had no README or changelog edits, so the three harness-docs scenarios were run on this checkout only.
 
 - Every role agent template's frontmatter parses and carries name, description, model and tools → NEW. Today the planner, spec-critic, spec-writer and triage lines print `keys=unparsed`.
 - The four fixed templates keep their description's words and every other line → NEW. Today each of the four prints `text=changed rest=same`, because its description does not parse. `others=same` already holds.
@@ -175,3 +175,12 @@
 - README describes init's report of a differing agent copy → NEW. Today it prints `row=0 step=0 missing=1`.
 - The changelog records issue 108 in one entry without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `0`, then `0`.
 - README stays within its line budget and both documents pass the whitespace check → REGRESSION. Today it prints `readme=within`, then `check=0`; README is at 1,106 lines.
+
+## Responses
+
+- [BLOCKING] Operator steps leaves "the Driver" and "the runtime upgrade" unglossed → FIXED. The step now opens with both glosses: the runtime checkout is "the separate worktree the factory runs from", moved to the merged revision and accepted with `--accept-harness`, and the Driver is "the session that runs the Nanobot target". I also replaced the step's check. v1 had the operator run `factory init` in Nanobot, which writes to a live target. The new check is a read-only `cmp` loop over the six templates, which prints `same` six times once the copies are refreshed. I ran it on this checkout: it prints `same` six times today, because the templates are not yet fixed. Risk now glosses the upgrade step the same way.
+- [SHOULD-FIX] "fresh-HOME wrapper", "instance's own store" and "throwaway store" go unglossed → FIXED. Evidence's first bullet now says "the harness's running-code wrapper (which gives the command a throwaway HOME, so it cannot write the operator's real home directory)". Decisions bullet 5 now says "the target's own store (the directory under the target's `.factory/` that holds the factory's tickets and run records)" and explains `FACTORY_STATE` as the environment variable that points init at another store. verification.md's opening line uses the same gloss.
+- [NIT] Part D does not bump README's status-header date → FIXED. D.3 now says to set line 9's "Current state as of" date to the merge date if it differs, and notes this changes no line count.
+- Out-of-scope observation (new init tests overlap `test_instance.py`) → FIXED in design part C. The new tests build their target with `git_repo`, `cli` and `js` from `tests/factory/_cli.py`, as the `target` fixture does. They do not import from another test file, because `_cli.py`'s docstring forbids that. They do not edit `test_instance.py`, an existing test this spec does not list under Tests to change.
+
+The base is unchanged since v1: `main` is still `525d73f`, and `git diff --stat 525d73f HEAD` over `agents`, `factory/setup.py`, `README.md`, `docs/changelog.md` and `tests/factory` is empty. So the "today" results in Acceptance, which both the critic and I ran on `525d73f`, still hold.
