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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0529-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0529-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0529-verifier/wt` (branch `factory/T-0052.1`, base `43a289e000c971ecc22d5303d387e3669bf5d987`, head `8d07f458b674f9041c6c2b861e626dc08121f053`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

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

## PR description (the implementer's output)

Sub-ticket: T-0052.1 (parent T-0052, spec v2: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0052/v2.md`)
Branch: `factory/T-0052.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0052.1`, one commit `8d07f45` on base `525d73f`.

## What changed

Claude Code could not load four of the factory's six role agent templates. A role agent template is a Claude Code agent definition in `agents/`, and `factory init` copies it into a target repository's `.claude/agents/`. The four templates now parse. The harness suite now fails if any template's header stops parsing. `factory init` now names an installed copy that differs from its template, so a target holding an old broken copy finds out.

- **A. Templates.** In `agents/factory-planner.md`, `factory-spec-critic.md`, `factory-spec-writer.md` and `factory-triage.md`, the `description:` value is now wrapped in double quotes. The words are unchanged, and no other line changed. `factory-clerk.md` and `factory-stub.md` are untouched.
- **B. Suite test.** New file `tests/factory/test_agent_templates.py`. The test `test_template_frontmatter_parses_and_carries_the_agent_keys` runs once for each `agents/*.md` file found by a glob, with the file name as the case id, so a seventh template is checked with no edit to the test. Each case checks four things: line 1 is `---`, a closing `---` exists, the lines between them parse with `yaml.safe_load` into a dict, and that dict has `name`, `description`, `model` and `tools`. Every assertion message names the template. A YAML error is not caught, so the case fails under its own id.
- **C. `factory init` report** (`factory/setup.py` `init_cmd`). The copy loop gained an `elif` branch for a copy that already exists. If the copy's bytes differ from the template's, init appends the copy's path to `stale` and prints one stderr line: `factory init: <copy> differs from its template <template>; left as it is`. The copy is never written. `"stale_agents": stale` sits beside `"agents"` in the JSON output. The `store.initialised` log condition and the "restart the session" line are unchanged. So a run of init that only reports differing copies logs nothing and asks for no restart, and the new test checks that. The only caller is `factory/cli.py:783` (`p.set_defaults(fn=init_cmd)`), found with `grep -rn init_cmd factory`. The same new test file has three init tests: an edited copy is listed and kept, a deleted copy is created and not listed, and matching copies give `stale_agents == []`. They build each target with `git_repo`, `cli` and `js` from `tests/factory/_cli.py`.
- **D. Documents.**
  - `README.md` line 463: the `.claude/agents/factory-*.md` row's "Written by" cell keeps "`factory init`, when they are missing" and adds "it reports a copy that differs from its template and leaves it as it is".
  - Step 1 of "Adopting the factory in a repo" gained one sentence. It says init never overwrites an agent copy, and that a copy differing from its template is listed under `stale_agents` and named on stderr. README grows from 1,106 to 1,108 lines, inside the four-line allowance. The status-header date stays 2026-10-13, which is today.
  - `docs/changelog.md`: new entry 73, `73. After issue #108 (2026-10-13), …`, placed after entry 72 and before the "Declined:" line.

## Acceptance results

Each command ran from the worktree inside the running-code wrapper, which gives every run a throwaway HOME.

- **Every role agent template's frontmatter parses and carries name, description, model and tools** (NEW). Before: `factory-clerk.md keys=ok`, `factory-planner.md keys=unparsed`, `factory-spec-critic.md keys=unparsed`, `factory-spec-writer.md keys=unparsed`, `factory-stub.md keys=ok`, `factory-triage.md keys=unparsed`. After: all six print `keys=ok`. All six headers now parse and carry the four keys.
- **The four fixed templates keep their description's words and every other line** (NEW). Before: each of the four printed `text=changed rest=same`, then `others=same`. After: `planner text=same rest=same`, `spec-critic text=same rest=same`, `spec-writer text=same rest=same`, `triage text=same rest=same`, `others=same`. The parsed description equals the old raw text, and no other line moved.
- **The suite fails on a template with broken frontmatter and names it** (NEW). Before: `suite=passed clerk=0 stub=0`. After: `suite=failed clerk=1 stub=1`. I re-ran the scenario with its pytest log kept, to check that the failures come from the new test and nothing else: `FAILED …test_template_frontmatter_parses_and_carries_the_agent_keys[factory-clerk.md]`, `FAILED …[factory-stub.md]`, `2 failed, 591 passed`. Both runs also printed `tar: Failed to set default locale`, which is noise from `tar` and does not affect the result.
- **init reports an edited agent copy and leaves it as it is** (NEW). Before: `exit=0 stale=absent kept=yes named=0 others=0`. After: `exit=0 stale=factory-planner.md kept=yes named=1 others=0`. The edited copy is listed, named once on stderr and kept byte for byte, and init exits 0.
- **init still creates a missing agent copy and lists no matching copy** (REGRESSION). After: `exit=0 created=factory-triage.md stale=0 same=6 differs=0`.
- **README describes init's report of a differing agent copy** (NEW). Before: `row=0 step=0 missing=1`. After: `row=1 step=1 missing=1`.
- **The changelog records issue 108 in one entry without a numbering gap** (NEW). Before: `CONTIGUOUS`, `0`, `0`. After: `CONTIGUOUS`, `1`, `3`. There is one #108 entry, it names `frontmatter`, `stale_agents` and `Nanobot`, and the numbering has no gap.
- **README stays within its line budget and both documents pass the whitespace check** (REGRESSION). After: `readme=within`, `check=0`.
- **Gate `git diff --check main...HEAD`**: no output, exit 0.
- **Gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory`**: `593 passed in 88.12s`. The 593 include the 9 new tests: six template cases and three init cases.

Red step: before the fix, the new test file gave `7 failed, 2 passed`. The four broken templates failed, the three init tests failed on the missing `stale_agents` key, and clerk and stub passed. After the fix it gave `9 passed`.

## Tests added/changed

- Added `tests/factory/test_agent_templates.py`, a new file with 6 parametrized template cases and 3 init tests, as part B and part C ask.
- Changed: none. No existing test file was touched. `test_init_is_idempotent_and_creates_only_what_is_missing` in `test_instance.py` is left as it is, as the spec asks.

## Known gaps and uncertainties

- The spec says the description is on "line 2". It is on line 3 of each template: line 1 is `---` and line 2 is `name:`. I edited the `description:` line, which is the spec's intent, and the "keep every other line" scenario confirms nothing else changed.
- The frontmatter test checks one thing the spec does not list: that a closing `---` exists. Without that check, a missing close would fail with a bare `ValueError` that does not name the template.
- The stderr line prints the template's path as `instance.AGENTS / <name>`, which is the harness checkout's `agents/` directory. In a target run from the runtime checkout, that path is under `~/dev/spec-factory-harness/agents/`, not the dev checkout.
- factory: markers added: none.

## Out-of-scope observations

- Nanobot's `.claude/agents/` copies are still the broken ones. The Driver refreshes them after the merge and the runtime upgrade, as the spec's Operator steps say. Nothing outside the worktree was written.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN exactly. The broken-template scenario fails only on the new cases. The full suite passed on the commit (593 passed).
ESCALATIONS: none

## Diff `43a289e000c971ecc22d5303d387e3669bf5d987...8d07f458b674f9041c6c2b861e626dc08121f053`

diff --git a/README.md b/README.md
index e6dc6ba..9e93114 100644
--- a/README.md
+++ b/README.md
@@ -460,7 +460,7 @@ The store's path is `state_dir` in `instance.yaml`. `factory init` creates a new
 |---|---|---|---|---|
 | `instance.yaml`, `context.md` | integration | `factory init`, then edited by the operator | the operator | durable |
 | `harness.lock` | integration | `factory init`; `--accept-harness` rewrites it | the operator | durable |
-| `.claude/agents/factory-*.md` | integration | `factory init`, when they are missing | the operator, if the target keeps them | durable |
+| `.claude/agents/factory-*.md` | integration | `factory init`, when they are missing; it reports a copy that differs from its template and leaves it as it is | the operator, if the target keeps them | durable |
 | Store records: requests, tickets, specs, plans, runs, results, approvals, current truth, changes, decisions, log | `factory-store` | the harness, through the workflows' clerk or `factory drive`, and the operator's commands | the operator, with `git -C <store> commit`; the harness commits the store once, the first commit `store migrate` makes | durable |
 | `runs/*/scratch/`, `runs/*/wt/`, `worktrees/` | none; git ignores them | `run start` | never | scratch until the ticket moves on (kept while parked); checker checkouts until `run cleanup`; implementer checkouts until the merge |
 | `drive/<ticket>.yaml` | none; git ignores it | `factory drive` | never | a live view of one driver process, rewritten at each step; read by the next drive of that ticket, which refuses to start while it shows a live driver; kept until that next drive |
@@ -584,7 +584,9 @@ From inside the target repo, with `R` the runtime (`~/dev/spec-factory-harness`)
    branch out instead, which restores the store. When more than one remote carries the branch it
    refuses and names each; pick one with `git branch factory-store <remote>/factory-store` and run
    `init` again. It also refuses from inside the store, and at a store path the integration branch
-   has ever tracked. Idempotent.
+   has ever tracked. Idempotent. An agent copy already in `.claude/agents/` is never overwritten:
+   one that differs from its template is listed under `stale_agents` in the JSON output and named
+   on stderr.
 2. Restart the Claude Code session so the agents register.
 3. Fill in `.factory/context.md`, the briefing every role reads first: which repo this is, how to
    run its tests, what kind of request to expect. Set `gate_commands` and `protected_paths` in
diff --git a/agents/factory-planner.md b/agents/factory-planner.md
index 1e717ab..5406bf2 100644
--- a/agents/factory-planner.md
+++ b/agents/factory-planner.md
@@ -1,6 +1,6 @@
 ---
 name: factory-planner
-description: Spec factory Planner role: splits one approved spec into ordered, independently mergeable sub-tickets with a coverage map.
+description: "Spec factory Planner role: splits one approved spec into ordered, independently mergeable sub-tickets with a coverage map."
 model: opus
 tools: Read, Grep, Glob, Bash, Write
 ---
diff --git a/agents/factory-spec-critic.md b/agents/factory-spec-critic.md
index 204a99d..7f49cd5 100644
--- a/agents/factory-spec-critic.md
+++ b/agents/factory-spec-critic.md
@@ -1,6 +1,6 @@
 ---
 name: factory-spec-critic
-description: Spec factory Spec critic role: judges a spec against the six-item rubric; APPROVE, REVISE or ESCALATE. Never sees the writer's reasoning.
+description: "Spec factory Spec critic role: judges a spec against the six-item rubric; APPROVE, REVISE or ESCALATE. Never sees the writer's reasoning."
 model: fable
 tools: Read, Grep, Glob, Bash, Write
 ---
diff --git a/agents/factory-spec-writer.md b/agents/factory-spec-writer.md
index b2db1e5..087954c 100644
--- a/agents/factory-spec-writer.md
+++ b/agents/factory-spec-writer.md
@@ -1,6 +1,6 @@
 ---
 name: factory-spec-writer
-description: Spec factory Spec writer role: investigates the repo and writes one spec in the factory format for an accepted ticket.
+description: "Spec factory Spec writer role: investigates the repo and writes one spec in the factory format for an accepted ticket."
 model: opus
 tools: Read, Grep, Glob, Bash, Write
 ---
diff --git a/agents/factory-triage.md b/agents/factory-triage.md
index 86fc614..824db75 100644
--- a/agents/factory-triage.md
+++ b/agents/factory-triage.md
@@ -1,6 +1,6 @@
 ---
 name: factory-triage
-description: Spec factory Triage role: turns one raw request into an accepted ticket, or routes it (NEEDS-HUMAN, CLARIFY, REJECT).
+description: "Spec factory Triage role: turns one raw request into an accepted ticket, or routes it (NEEDS-HUMAN, CLARIFY, REJECT)."
 model: opus
 tools: Read, Grep, Glob, Bash, Write
 ---
diff --git a/docs/changelog.md b/docs/changelog.md
index e686eb2..4c8039d 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -75,5 +75,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 71. After issue #106 (2026-10-12), where both verifier runs of one sub-ticket started the harness suite in the background, ended their turns to wait for it and so wrote no output: one run of the suite took six to ten minutes, against the 10-minute limit of a single agent tool call. The ticket parked as `EMPTY-OUTPUT from verifier`, a reason that did not say why. The harness suite now runs across every CPU core with pytest-xdist, a new dev dependency, switched on once in `pyproject.toml` (`addopts = "-n auto"`), so the gate command and every scenario that runs the suite use it with no change to their text; one run measured 66.80 to 146.81 seconds when the change was specified, against 385.56 seconds one test at a time. A new test must not depend on test order, or share a file, port, environment variable or other process-wide state with another test outside its own `tmp_path`. Adding pytest-xdist is a deliberate exception to the 2026-10-04 decision not to add to what the gate needs. The suite's two stand-in `claude` programs now hold a file lock around their per-role call counter, so a copy of one role started beside another no longer reads the counter while the other rewrites it, which had now and then crashed a checker run under load. `factory run last-message` also prints `waiting`: true when the kept message contains, ignoring case, the word `wait` or `waiting`, or `still running`, `still in progress` or `in the background`. The driver and both workflow scripts park a second EMPTY-OUTPUT in a row as `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command` when either run was waiting, and as `EMPTY-OUTPUT from <role>` otherwise; the route itself is unchanged, and no role prompt changes. Rejected: calling the CLI in-process in the suite, which was faster but needs a module-table swap around every call and stops most CLI calls from crossing a real process boundary; adding `-n auto` to the gate command, which leaves every scenario that runs the suite running one test at a time; and deciding waiting in each caller or in a separate command, rather than once in `run last-message`.
 
 72. After issue #101 (2026-10-11), where the operator read two long maintained documents at every spec gate and parts of README were false: README explained several mechanisms two or three times, said six features had not yet run on a real ticket when the stores' logs showed they had, and kept project history; and the briefing asked every design change to keep `dev/build-harness.spec.md` in step though it describes a design the code never had. The three `dev/` build documents, `dev/build-harness.spec.md`, `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md`, are frozen as history: each gains a header at line 3 and is otherwise as it was at `7231670`, and no change updates them; `.factory/context.md` and README's `dev/` row say so, and the briefing no longer names them in a design change's conventions. `dev/issues.md` stays the live issue index. README's claims now match the logs: the one-sub-ticket path has run on real tickets on both targets (16 tickets from T-0031 to T-0051 here, five on the Nanobot store); the driver took T-0035 and T-0036 through intake and the build on the Nanobot target; a gate command's path skip is recorded for T-0036.1; the re-plan after a re-spec fired for T-0031; the protected-path refusal at merge fired for T-0044.1, which the operator accepted with `--accept-paths`; every run has its scratch directory; and a run with no output is run once more, not recorded as killed. The tripwire, the sibling-tests check and the drift check's sibling-merge exception still say they have not yet fired or run, and the effort entry that neither target sets it. README's rule for its Built list now admits a thing once it is built and tested and asks its entry to say whether it has yet run on a real ticket, and `docs/design.md` line 3 drops its own date and points here. Each mechanism has one home in README: the live-store fence under "Where a human decides", the driver and its same-ticket guard under its how-to, the final check's skip under "The build workflow, step by step", the store branch under "How the factory uses git", and other agent hosts only in `docs/design.md`; the Built entries become short pointers, "Not built" one paragraph that repeats nothing under "Where this can go", and the glossary points to "Where it runs" and defines a protected path in its own row. History moved out of README: the overlap of 41 and 11 runs of different tickets in the two stores on 2026-10-04, the double count `factory/cost.py` once made (entry 70), the two stores' moves onto their store branch with `factory store migrate`, the page's origin story and the regeneration pass's two past catches, a target described as cut over that was not and a bound stated on the wrong case; "Related work and history" keeps every issue reference beside what it names. `docs/design.md`'s model-per-role paragraph points to principle 4 and entry 70 for the first `factory stats` figures, which it no longer repeats; they were, up to 2026-10-07 12:00 UTC over both stores, the code reviewer (Fable) changing an outcome in 4 of 94 runs with 3 BLOCKING findings for 94,860,442 context tokens over 99 runs, the critic (Fable) in 19 of 84 for 66,027,675, the verifier in 8 of 108 on Opus for 232,945,610 and in 1 of 5 on Fable for 5,189,563, and the implementer (Opus) in 18 of 111 for 372,507,821 over 114 runs. README is held to at most 1,110 lines; a later change that needs more raises the bound in its own spec. The `harness-docs` current truth is rewritten so each check keeps passing after later changes: a check finds a changelog entry by its opening words, `<n>. After issue #<k> `, and never by the last line or an entry count; no check measures what one change left untouched against `main` or a fixed commit, and the two requirements made only of such checks are removed; whitespace is checked once over the maintained documents in full, while the instance's gate command still checks each change; the frozen build spec's checks, and principle 2's retired status clause, are dropped. Rejected: moving the build documents to `dev/archive/`, which breaks the `Parent:` links and every path cited to them; moving the built but unfired features under "Where this can go", which is for intended work; bumping `docs/design.md`'s date, which every later change would also have to do; padding the cuts to the requested 150 lines, against about 90 that one home per mechanism gives; and splitting the work into four sub-tickets, which would all edit README.
+73. After issue #108 (2026-10-13), where Claude Code could not load four of the six role agent templates in `agents/` (planner, spec critic, spec writer and triage): each one's frontmatter, the YAML header that names the agent, held an unquoted description containing a colon and a space, which YAML reads as a second key, so the header did not parse. No run failed, because every workflow run passes `inlineRoles: true` and `factory drive` starts each role with its prompt inline. The four descriptions are now quoted, with their words unchanged. The harness suite now parses every template's frontmatter, one case per template, and requires `name`, `description`, `model` and `tools`; no test read these headers before. `factory init` still never overwrites an existing copy in a target's `.claude/agents/`; it now lists each copy that differs from its template under `stale_agents` in its JSON output and names it on stderr, and still exits 0. Nanobot's copies, byte-identical to the old templates, are refreshed by its Driver after the merge and the runtime upgrade. Rejected: rephrasing the descriptions without the colon, which changes their words; overwriting a differing copy, which would discard an operator's deliberate edit; and refusing with exit 2, because a stale copy does not stop a run that uses `inlineRoles`.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/factory/setup.py b/factory/setup.py
index 2f8474f..4731407 100644
--- a/factory/setup.py
+++ b/factory/setup.py
@@ -167,6 +167,7 @@ def init_cmd(a):
         store.write_text(cfg_path, new_text)
         created.append(str(cfg_path))
     agents: list[str] = []
+    stale: list[str] = []
     store_branch = None
     if own:
         ctx = inst / "context.md"
@@ -183,6 +184,10 @@ def init_cmd(a):
                 (dest / src.name).parent.mkdir(parents=True, exist_ok=True)
                 shutil.copyfile(src, dest / src.name)
                 agents.append(str(dest / src.name))
+            elif (dest / src.name).read_bytes() != src.read_bytes():  # reported, never overwritten
+                stale.append(str(dest / src.name))
+                print(f"factory init: {dest / src.name} differs from its template {src}; left as it is",
+                      file=sys.stderr)
         checkout = gitops.checkout_of(repo, gitops.STORE_BRANCH)
         if checkout is not None and checkout.resolve() == root:
             store_branch = gitops.STORE_BRANCH
@@ -201,7 +206,7 @@ def init_cmd(a):
     if agents:
         print("restart the session so the agents register", file=sys.stderr)
     out({"ok": True, "written": written, "active": True, "instance": str(inst), "state": str(root),
-         "created": created, "agents": agents, "store_branch": store_branch})
+         "created": created, "agents": agents, "stale_agents": stale, "store_branch": store_branch})
 
 
 STATE_DIR_LINE = re.compile(r"^(state_dir:[ \t]*)([^#\n]*?)([ \t]*(?:#.*)?)$", re.M)
diff --git a/tests/factory/test_agent_templates.py b/tests/factory/test_agent_templates.py
new file mode 100644
index 0000000..f62b9e1
--- /dev/null
+++ b/tests/factory/test_agent_templates.py
@@ -0,0 +1,68 @@
+"""Role agent templates (`agents/*.md`): every template's frontmatter parses and carries the keys
+Claude Code needs, and `factory init` reports an installed copy that differs from its template
+without overwriting it.
+"""
+from __future__ import annotations
+
+from pathlib import Path
+
+import pytest
+import yaml
+
+from ._cli import REPO, cli, git_repo, js
+
+TEMPLATES = sorted((REPO / "agents").glob("*.md"))
+
+
+@pytest.mark.parametrize("template", TEMPLATES, ids=[p.name for p in TEMPLATES])
+def test_template_frontmatter_parses_and_carries_the_agent_keys(template):
+    lines = template.read_text(encoding="utf-8").splitlines()
+    assert lines[:1] == ["---"], f"{template.name}: line 1 is not ---"
+    assert "---" in lines[1:], f"{template.name}: frontmatter has no closing ---"
+    header = yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))
+    assert isinstance(header, dict), f"{template.name}: frontmatter is not a mapping"
+    missing = {"name", "description", "model", "tools"} - set(header)
+    assert not missing, f"{template.name}: frontmatter lacks {sorted(missing)}"
+
+
+def initialised(tmp_path: Path) -> Path:
+    t = git_repo(tmp_path / "target")
+    cp = cli(t, "init", "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    return t
+
+
+def test_init_lists_an_edited_copy_and_leaves_it(tmp_path):
+    t = initialised(tmp_path)
+    copy = t / ".claude" / "agents" / "factory-planner.md"
+    copy.write_bytes(copy.read_bytes() + b"local edit\n")
+    kept = copy.read_bytes()
+    cp = cli(t, "init")
+    assert cp.returncode == 0, cp.stderr
+    out = js(cp)
+    assert [Path(p).name for p in out["stale_agents"]] == ["factory-planner.md"]
+    assert out["agents"] == []
+    assert copy.read_bytes() == kept
+    template = REPO / "agents" / "factory-planner.md"
+    assert f"factory init: {copy} differs from its template {template}; left as it is" in cp.stderr
+    assert "restart the session" not in cp.stdout + cp.stderr
+
+
+def test_init_creates_a_deleted_copy_and_does_not_list_it(tmp_path):
+    t = initialised(tmp_path)
+    copy = t / ".claude" / "agents" / "factory-triage.md"
+    copy.unlink()
+    cp = cli(t, "init")
+    assert cp.returncode == 0, cp.stderr
+    out = js(cp)
+    assert [Path(p).name for p in out["agents"]] == ["factory-triage.md"]
+    assert out["stale_agents"] == []
+    assert copy.read_bytes() == (REPO / "agents" / "factory-triage.md").read_bytes()
+    assert "differs" not in cp.stderr
+
+
+def test_init_with_matching_copies_lists_none(tmp_path):
+    cp = cli(initialised(tmp_path), "init")
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["stale_agents"] == [] and js(cp)["agents"] == []
+    assert "differs" not in cp.stderr
