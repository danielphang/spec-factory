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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0530-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0530-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0052.1` (branch `factory/T-0052.1`, base `43a289e000c971ecc22d5303d387e3669bf5d987`, head `8d07f458b674f9041c6c2b861e626dc08121f053`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0052.1

T-0052.1 / Fix the YAML frontmatter in four role agent templates, test every template's frontmatter, and have `factory init` report a target copy that differs from its template
Depends on: none
Parallel-safe: yes

Parent: T-0052, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Every role agent template's frontmatter parses and carries name, description, model and tools
- The four fixed templates keep their description's words and every other line
- The suite fails on a template with broken frontmatter and names it
- init reports an edited agent copy and leaves it as it is
- init still creates a missing agent copy and lists no matching copy
- README describes init's report of a differing agent copy
- The changelog records issue 108 in one entry without a numbering gap
- README stays within its line budget and both documents pass the whitespace check
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0052/v2.md`

=== proposal.md
## Problem

Four of the factory's six role agent definitions cannot be loaded by Claude Code, and fixing them in this repository would not fix the copies already installed in a target repository.

A role agent template is a Claude Code agent definition kept in `agents/`: a Markdown file whose YAML header (its frontmatter) gives the agent's name, a one-line description, the model it runs on and the tools it may use. `factory init`, the command that sets a repository up to use the factory (a target), copies each template into that repository's `.claude/agents/`, where Claude Code registers it when a session starts.

In the planner, spec critic, spec writer and triage templates, the description is an unquoted YAML value that contains a colon followed by a space (`Spec factory Planner role: splits …`). YAML reads that as the start of a second key, so the whole header fails to parse. The operator saw Claude Code report this for the spec writer on 2026-10-13. No run has failed yet, because every workflow run passes `inlineRoles: true` (run every role as a general-purpose agent that reads its prompt from a file) and `factory drive` (the shell-driven runner) starts each role as a `claude -p` process with its prompt inline. Any run that uses the registered agents would fail at the first of these four roles.

Nothing in the harness's test suite reads these headers, which is how the break went unnoticed. And `factory init` copies a template only when the target has no file of that name, so a target that already has a broken copy keeps it after the template is fixed, and nothing tells its operator. The Nanobot target, the factory's other live user, holds byte-identical copies of all six templates, broken four included.

This change quotes the four descriptions, adds a suite test that parses every template's header, and makes `factory init` name each installed copy that differs from its template while still leaving that copy as it is.

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

## Reviewer findings on your previous head

Commit: 8d07f458b674f9041c6c2b861e626dc08121f053 (branch `factory/T-0052.1`, one commit on base `525d73fdd4d3a2d70f66961195f9f9e19ac44c7d`)

## Checks, in order

1. Test integrity: no existing test file is in the diff (`git diff --stat 525d73f..HEAD` lists only `README.md`, four `agents/*.md`, `docs/changelog.md`, `factory/setup.py` and the new `tests/factory/test_agent_templates.py`). Nothing weakened, skipped, deleted or hard-coded. The spec's "Tests to change" is `none`, and that holds.

2. Correctness, against the spec's intent:
   - A. Templates: each of the four diffs changes exactly one line, wrapping the description in double quotes with the words unchanged; clerk and stub are untouched. I ran `yaml.safe_load` over the header of every `agents/*.md` in the worktree: all six parse and carry `name`, `description`, `model`, `tools` (clerk and stub also carry `omitClaudeMd`, which the test's subset check allows, as the spec intends).
   - B. Suite test (`tests/factory/test_agent_templates.py:16-25`): parametrized over a glob with the file name as id, no hard-coded list; asserts line 1, parses with `yaml.safe_load`, asserts a dict with the four keys; every message names the template; a YAML error is not caught. The extra closing-`---` assertion (line 21) is a sound guard: without it `lines.index("---", 1)` raises a bare `ValueError` that names no template, which would break the "names it" requirement for that failure shape.
   - C. `factory/setup.py:187-190`: the `elif` compares bytes, appends the copy path (same form as `agents`), prints the one stderr line in the specified wording, never writes. `stale_agents` sits beside `agents` in `out(...)` (line 209). The `store.initialised` condition (line 204) and the restart line (line 206) are unchanged, so a report-only run logs nothing and asks for no restart; `test_init_lists_an_edited_copy_and_leaves_it` checks the restart line. The comparison runs only under `if own:`, so a `FACTORY_STATE` init gives `stale_agents == []`, as the Decisions require. `instance.AGENTS` is `HARNESS / "agents"` with `HARNESS = Path(__file__).resolve().parent.parent` (`factory/instance.py:31,34`), the same directory the test's `REPO / "agents"` names, so the exact stderr assertion at test line 47 is sound. The three init tests use only `git_repo`, `cli` and `js` from `_cli.py`, as asked.
   - D. Documents: the README row's "Written by" cell keeps `when they are missing` and contains `differs from its template`; step 1 gains one sentence naming `stale_agents` and stderr and says "never overwritten"; README is 1,108 lines (`wc -l`), +2 net; the status date stays 2026-10-13, which is today. Changelog entry 73 follows 72, opens `73. After issue #108 (2026-10-13), `, and names `frontmatter`, `stale_agents` and `Nanobot`.

3. Scope: every hunk maps to a lettered part. Nothing outside.

4. Silent behaviour changes: one added JSON key and new stderr lines, both specified. `test_init_is_idempotent_and_creates_only_what_is_missing` (`test_instance.py:116-138`) reads named keys and checks `tree()` of `.factory` and `.claude`, and the new branch writes no file, so it is unaffected.

5. Security and data safety: reads a file the target already holds, writes nothing new, no shell, no secrets.

6. Protected paths: `agents/**` and `factory/**` are touched; the parent's Risk section declares both. Listed under ESCALATIONS for the record.

7. Coding standard: the test-side `initialised` helper is three lines over `git_repo` and `cli`, and the spec forbids importing `test_instance.py`'s fixture, so rung 1 is taken as far as the spec allows. The `elif` is six lines of stdlib. No `factory:` marker needed. Lean already.

8. PR description: What changed opens with the problem and who has it, glosses "role agent template" and `.claude/agents/` at first use, and says in words what each part did. Known gaps are honest and useful (the line-2 vs line-3 note, the extra closing-`---` check, the runtime-checkout path in the stderr line). The operator could read it at the gate.

## Findings

none.

## Prior findings

none (round 1).

STATUS: APPROVE
CONFIDENCE: high. I read every hunk against each lettered part and each Decision, confirmed the six headers parse in the worktree and that the test's template path equals the one `init_cmd` prints; the suite and gate commands are the verifier's to run on this head.
ESCALATIONS: for the record only, no action needed: the diff touches the protected paths `agents/**` (four template files) and `factory/**` (`factory/setup.py`), both declared in the approved spec's Risk section, so the merge gate merges them without further approval.

## Verifier findings on your previous head

Commit: 8d07f458b674f9041c6c2b861e626dc08121f053 (branch `factory/T-0052.1`). Base given: 43a289e000c971ecc22d5303d387e3669bf5d987 (`main`).

The branch was not cut from the base I was given. `git merge-base HEAD main` is `525d73f`. Since then `main` has gained T-0053.1 (merge `af439c4`), which added its own changelog entry `73. After issue #110`. This PR also numbers its entry 73. On its own the branch passes every acceptance command. Merged onto `main`, it breaks the changelog criterion. The spec planned for this case: "If another ticket takes the next number first, take the next free one: the entries must stay numbered without a gap." Details are under the changelog criterion below.

How I ran things: every command went through the running-code wrapper (a fresh temporary HOME each time), after `uv sync --frozen`. For the PR I ran in the worktree at `8d07f45`. For the base I ran in a clone at `43a289e` under my scratch directory. To check the merge, I made a second scratch clone at `43a289e` and ran `git merge --no-ff 8d07f45`. Each scenario command was saved to `scratch/sc/s<n>.sh`. I grep-checked each saved command against the input to confirm it matches the spec text exactly.

Per criterion:
- NEW | Every role agent template's frontmatter parses and carries name, description, model and tools | base: clerk and stub `keys=ok`; planner, spec-critic, spec-writer and triage `keys=unparsed` | PR: all six `keys=ok` | PASS
- NEW | The four fixed templates keep their description's words and every other line | base: each of the four `text=changed rest=same`, then `others=same` | PR: `planner text=same rest=same`, `spec-critic text=same rest=same`, `spec-writer text=same rest=same`, `triage text=same rest=same`, `others=same` | PASS
- NEW | The suite fails on a template with broken frontmatter and names it | base: `suite=passed clerk=0 stub=0` | PR: `suite=failed clerk=1 stub=1` | PASS
- NEW | init reports an edited agent copy and leaves it as it is | base: `exit=0 stale=absent kept=yes named=0 others=0` | PR: `exit=0 stale=factory-planner.md kept=yes named=1 others=0` | PASS
- REGRESSION | init still creates a missing agent copy and lists no matching copy | base: not run (I ran it anyway: `exit=0 created=factory-triage.md stale=0 same=6 differs=0`) | PR: `exit=0 created=factory-triage.md stale=0 same=6 differs=0` | PASS
- NEW | README describes init's report of a differing agent copy | base: `row=0 step=0 missing=1` | PR: `row=1 step=1 missing=1` | PASS. On the trial merge it also gives `row=1 step=1 missing=1`.
- NEW | The changelog records issue 108 in one entry without a numbering gap | base: `CONTIGUOUS`, `0`, `0` | PR head alone: `CONTIGUOUS`, `1`, `3` | FAIL against the given base. On the trial merge of `8d07f45` into `43a289e` (no conflict; git auto-merged `docs/changelog.md`), the same command prints `GAPPED`, `1`, `3`. `grep -n '^7[0-9]\. ' docs/changelog.md` on the merge shows line 78 `73. After issue #108` followed by line 80 `73. After issue #110`. That is two entries numbered 73, with #108's entry placed before #110's. The command passes on the head only because the head does not contain `main`'s entry 73. The fix the spec asks for is to rebase onto `43a289e` and renumber the entry to 74, after #110's entry.
- REGRESSION | README stays within its line budget and both documents pass the whitespace check | base: not run (I ran it anyway: `readme=within`, `check=0`) | PR: `readme=within`, `check=0` | PASS. On the trial merge, README is 1,108 lines and the command prints `readme=within`, `check=0`.

Gate suite: PASS
  `git diff --check main...HEAD`: no output, exit 0. Note that this compares the merge-base `525d73f` to HEAD, so it does not see the entry-73 collision.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `593 passed in 95.18s`.
  Extra, not a gate: the full suite on the trial merge (`bd9583a`) gave `593 passed in 114.76s`. The code side merges cleanly.

Probes:
- Two edited copies (planner, triage) and one deleted copy (clerk) in one init → exit 0, `agents=factory-clerk.md`, `stale=factory-planner.md,factory-triage.md`, one stderr line naming each copy and its template, and the "restart the session" line, because a copy was created → OK. The report is not special-cased to the planner.
- A copy truncated to 0 bytes (`factory-stub.md`) → exit 0, listed under `stale_agents`, and still 0 bytes afterwards → OK.
- `FACTORY_STATE` set to a throwaway store, with an edited planner copy → exit 0, `stale_agents= []`. This matches the spec's decision that init run against another store does not read `.claude/agents/` → OK.
- The frontmatter test on a scratch copy of the tree with three extra templates added and no edit to the test. One template had no closing `---`, one had a list as its frontmatter, and one had a quoted description containing `: `. Result: `2 failed, 7 passed`. The failures were `[factory-extra.md]` "frontmatter has no closing ---" and `[factory-list.md]` "frontmatter is not a mapping"; the quoted-colon template passed. → OK. The glob picks up new templates and each failure names its template.
- `.claude/agents/factory-stub.md` replaced by a directory → init exits 1 with `factory: IsADirectoryError`. Before this change, the `exists()` check would have skipped the directory silently. → CONCERN, outside the criteria. The input is unusual and no criterion covers it, so this does not count toward FAILED.

Protected paths this change touches: `agents/**` and `factory/**`. Both are declared in the spec's Risk section.

STATUS: FAILED
CONFIDENCE: high. All eight commands and both gates ran in full on the head. The failure is reproduced by a real merge onto the given base, where the changelog command prints `GAPPED`.
ESCALATIONS:
- The harness gave me base `43a289e` (current `main`), but the implementer's branch was cut from `525d73f`, and T-0053.1 merged in between. Unless this branch is rebased or the entry renumbered before merge, `docs/changelog.md` on `main` will have two entries numbered 73. Neither the gate (`git diff --check main...HEAD` only checks merge-base to HEAD) nor the head-only acceptance command catches this. A human should decide whether the harness rebases a branch onto the current base before review, or whether the implementer reruns on the new base.
- Outside the criteria: `factory init` now crashes (exit 1, `IsADirectoryError`) when a directory sits where an agent copy belongs. Before this change it skipped the directory without error. This is a minor robustness regression, noted for the operator.

## Gate suite on your previous head
PASS

