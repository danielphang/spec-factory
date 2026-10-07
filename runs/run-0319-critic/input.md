## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
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
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0319-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0319-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v2)

=== proposal.md
## Problem

The factory merges changes to its own protected files without checking that a human ever authorized them. The factory is a chain of AI agents that turns a written request into merged code. Each repository it runs on (an instance) lists some protected paths: files where a change alters something sensitive. In this repository they are the factory's own code (the harness), its configuration and its copies of the agent prompts. A human, the operator, approves each spec at the spec gate before any code is written. The spec is then built as one or more sub-tickets, each one change of reviewable size. Before a sub-ticket's change merges, two agents check it: the reviewer reads the diff, and the verifier runs the test suite and the spec's acceptance commands. The merge gate is the last automated check before the change is merged into the integration branch (the branch the factory merges into, `main` here). It confirms that the reviewer approved and the verifier passed, but it never looks at which files the change touches. So a change to a protected file merges whenever the reviewer and verifier pass it, even when the approved spec never said the change would touch that file.

The documents promise more than the code does. The design says a protected-path change needs a human approval before it merges. The reviewer's instructions say "the merge gate will require a human approval". Neither is true. The gap matters most here, because this is the gate that guards the factory's changes to itself.

The operator has ruled how the gate should work, as a standing rule for every instance. Each spec has a Risk section, which lists the protected paths the change will touch. The operator approves that list at the spec gate, and the approved list is the authorization. At merge, the gate must refuse each changed protected path that the approved spec does not declare. It must name each one and park the sub-ticket: stop it until a human gives a ruling, a written answer that the next agent reads. A declared path merges with no further approval. Asking for a human approval on every change would have stopped 18 of the last 20 merges here.

A second, smaller fault blocks the human's ruling. When the reviewer on a sub-ticket escalates a question to a human and the human rules on it, the ruling command sends the sub-ticket to the spec critic. The critic is a step of the spec-writing loop, which never runs for sub-tickets. On 2026-10-05 the operator had to place a ruling file by hand and re-run the reviewer and verifier with a second command.

## Evidence

The commands below ran on `main` at `d226a4d`, from `~/dev/spec-factory`, with a throwaway `HOME`. They use the fixture script this spec gives under the first merge-gate scenario (`t0033-gate.sh`). The fixture protects `core/**` and `bin/tool`, and builds one sub-ticket that the reviewer approved and the verifier passed. `main` has since moved to `220ebdc`. That change touches only `factory/compose.py` and adds one test file; `git diff --quiet d226a4d 220ebdc -- factory/cli.py factory/workflows/build.js factory/prompts docs dev README.md` exits 0, so every file this evidence reads is unchanged.

- An undeclared protected path merges. T-0001's approved spec declares only `core/a.py`. The sub-ticket also changes `core/b.py` and `bin/tool`. Merge-gate scenario 1 printed `exit=0 blocked=0 named=0 declared=0 main=moved merged`. That means the merge succeeded (`exit=0`) and the integration branch moved with both undeclared protected files in it.
- Three more undeclared cases merge. In the first, only another ticket's spec declares the path (T-0002 declares `core/b.py`). In the second, the change moves `core/b.py` out of the protected tree. In the third, the Risk section's only mention of `core/b.py` is a "Not touched" line. Scenario 2 printed `exit=0 named=0 main=moved` three times: each merged. The second case also shows why the gate must turn off git's rename detection. `git diff --name-only main...$H` lists only `docs/b.py`, so a gate reading it would never see the protected `core/b.py` leave. With `--no-renames` it lists `core/b.py` and `docs/b.py`.
- The gate reads no paths. `factory/cli.py` `merge_cmd` (lines 645-687) checks four things: the ticket state; that the recorded commit is the branch tip; the three recorded results (`ci` PASS, reviewer APPROVE, verifier VERIFIED); and that the commit contains the integration branch. No line reads the changed paths, `protected_paths` or a spec.
- The reviewer prompt promises a check that does not exist. Check 6 ends "the merge gate will require a human approval" (`factory/prompts/reviewer.md` lines 24-27, `docs/prompts/06-code-reviewer.md` lines 24-27, `docs/design.md` lines 640-643). The design doc asks for a per-PR approval in five places. Line 21 names "a PR touching a protected path" as one of five human gates. Line 23 says "A change to either needs a human approval record before it merges". Line 48 (piece 8) says "any other guardrail or protected path needs a human approval on the PR itself". Line 49 (piece 9) has people "review protected PRs". Line 154 says "the merge gate does not merge without it". `dev/build-harness.spec.md` line 246 and item 25 (line 377) specify the same per-PR approval, through an `approve-pr` command that was never built.
- Risk sections today are prose, so the gate needs a fixed form to read. I read the Risk sections of the approved specs T-0013, T-0022, T-0024, T-0028 and T-0029 (`.factory/store/specs/`). Each lists the protected paths it touches. Each also names, in backticks, paths it does not touch, such as T-0013's "Not touched: `.factory/**` …" and T-0022's "It does not touch `.factory/**`, `bin/factory` …". A gate that counted every backticked path in Risk would authorize exactly the paths these specs promise to leave alone. T-0022 also uses brace lists (`factory/prompts/{preamble,planner,…}.md`). Git does not expand braces, so such an entry matches no file.
- The cost of a per-PR approval. I diffed each of the last 20 merge commits on `main`'s first-parent line with `git diff --name-only --no-renames <merge>^1 <merge>` and matched the result against this instance's in-repo protected globs. 18 of the 20 touched a protected path. The operator's answer gives 19 of 20 over its own window.
- The case that exposed the gap. On 2026-10-04 sub-ticket T-0028.1 parked with reason `ESCALATE from reviewer` (`.factory/store/tickets/T-0028.1.yaml`, history). Its reviewer had escalated a 3-line change to `factory/store.py`. The approved spec asks for that change in part A.5, but its Risk list does not name the file. The operator accepted it. The ruling at `.factory/store/approvals/T-0028.1/ruling-1.md` says it was "Placed by hand because `resolve --ruling` routes a sub-ticket's reviewer escalation to the critic". It was followed by `resolve --redispatch`, which re-runs the reviewer and verifier on the same commit.
- The misroute, reproduced. With the fixture, a reviewer ESCALATE result is recorded, the sub-ticket is parked `ESCALATE from reviewer`, and `resolve --ruling` is run. Human-resolution scenario 4 printed `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`, then `in_input=0`. That means the sub-ticket went to the spec critic's state, and the ESCALATE result stayed, so a re-check would park again. No reviewer run could start to read the ruling (`in_input=0`). The code is `factory/cli.py` `resolve`, lines 864-875: any ESCALATE whose reason lacks "planner" goes to `ready-for-critic`.
- What the build does today with a merge refusal it does not recognise. The build workflow is the script that runs the agents for each sub-ticket and calls the merge gate. Build-dispatch scenario 1 feeds it a stubbed merge refusal. It printed `park: harness-bug: merge: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`. That means the workflow filed the refusal as a fault in the factory's own code. The workflow asks again whether to merge (`factory/workflows/build.js` lines 195-200), gets "merge" again, and files any refusal other than a conflict that way.
- No reference fix exists. The request names no commit on the Nanobot side, where the factory's code first ran.

## Root cause

- `factory/cli.py` `merge_cmd` (645-687) has no path condition. It was written as the local stand-in for the rule-4 checks, and the protected-path part of piece 8 was never ported.
- `factory/prompts/reviewer.md` check 6, its design block and `docs/prompts/` copy describe the per-PR approval of the unbuilt pre-receive design (`dev/build-harness.spec.md` part F), not the local gate.
- The spec writer's format asks for "every protected path this will touch" under Risk but gives no form a program can read (`factory/prompts/spec_writer.md` line 80, `docs/prompts/02-spec-writer.md` line 76, `docs/design.md` line 387).
- `factory/cli.py` `resolve`, `--ruling` branch (864-875), knows two ESCALATE routes, planner and critic. It sends every other ESCALATE, the reviewer's included, to the critic.
- `factory/workflows/build.js` lines 195-200 treat every merge refusal other than a conflict as a harness bug.

## Out of scope

- Guardrail paths are unchanged. Existing tests still change only when the pinned spec lists them under "Tests to change" or an earlier sibling added them. The non-test guardrails (agent prompts, AGENTS.md, skills, CI config) keep their documented per-PR approval. The local gate checks neither rule today, and this change does not add them.
- Protected paths outside the repository (`~/dev/nanobot-upstream/**`, `~/.nanobot/**`). A repository diff cannot contain them. The gate skips such patterns.
- A per-head human approval for paths that change the factory's own rules (option 3 of the operator's answer). See Decisions.
- A check at `spec add` or `approve-spec` that the Risk section has a well-formed `Protected paths:` line. That belongs with the spec lint, issue #67.
- The sub-ticket's own `Protected paths:` field, which the planner writes. The gate does not read it, and its format does not change.
- The first two sentences of the reviewer's check 6 (escalate an undeclared path, list a declared one). The implementer and verifier prompts are not changed.
- Rulings on a budget-kill or EMPTY-OUTPUT park. They belong to issue #41's line in `decisions.md`.
- The design's "round reset" route for a max-round cutoff or a SPEC-DEFECT. It stays as written and unbuilt.
- Nothing under `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml` or `uv.lock` changes, and no instance's `protected_paths` changes.

## Open questions

none

## Decisions

- The authorization is the pinned spec's Risk section. The pinned spec is the version the operator approved at the spec gate. For a sub-ticket, that is its parent's approved version (`specs/<parent>/v<approved_version>.md`). A ticket with no parent uses its own approved version. A ticket with no approved spec declares nothing. This is standing for every instance, from the operator's 2026-10-05 answer. It is already the 2026-10-07 T-0033 line in `decisions.md`, the factory's log of standing decisions that later tickets must follow.
- The gate reads declarations from one fixed line in the Risk section: `Protected paths: none`, or `Protected paths: ` followed by one or more backticked paths or globs, separated by commas. An optional list marker (`- ` or `* `) may come before it, and an optional full stop after it. Each entry is one path or one glob. A brace list such as `factory/prompts/{a,b}.md` is one literal entry, which git does not expand, so it matches no file and declares nothing. A Risk line in any other shape declares nothing, and so does a line inside a fenced code block. Several such lines declare their union. Standing: specs declare protected paths only this way. Rejected: reading every backticked path in Risk, because today's Risk sections also put the paths they promise not to touch in backticks (Evidence). Rejected: the planner's per-sub-ticket `Protected paths:` field, which an agent writes and no human approves.
- A changed path is "protected" when it matches one of the instance's in-repo `protected_paths` globs. It is "declared" when it matches a declared entry. Both matches use git's glob pathspecs (`:(glob)<pattern>`, so `**` crosses directories and `*` does not). This follows the 2026-10-05 T-0028 decision that the harness never adds a glob matcher of its own. Patterns that start with `~` or `/` are skipped.
- The changed paths are those of `git diff --name-only --no-renames <integration branch>...<head>`, measured from the merge base; the head is the commit the gate is judging. Once the head contains the integration branch, that is exactly what the merge adds. `--no-renames` lists both sides of a move (Evidence). Rejected: the triage's "parent base". A catch-up run is an implementer run that merges the integration branch into a sub-ticket's branch that has fallen behind. After one, a diff from the parent's base counts other tickets' merged changes against this sub-ticket.
- The gate runs this check after the three recorded results and before the containment check and the merge lock. A change that will be refused costs no catch-up run.
- A refusal exits 2 and changes no ticket field. It logs one `merge.refused` event with the paths. Its error starts `BLOCKED from merge gate: ` and names each undeclared path, sorted and comma-separated. It names no declared path and uses no backtick, `$` or double quote, because the build workflow passes the reason through a shell command.
- The build workflow parks the sub-ticket with that error, verbatim, as the reason. It already does the same for the harness's `BLOCKED from harness:` refusal at run start.
- The human answers that park with one of two commands. `resolve --ruling F` sends the change back. It uses the existing BLOCKED route: the sub-ticket returns to its implementer with F in its input, and its round count (the number of fix cycles it may use) is not reset. The new `resolve --accept-paths F` accepts the paths under the approved design. It records F as the sub-ticket's next ruling. It adds the undeclared paths, recomputed on the current head, to a ticket field `accepted_paths`, which the gate treats as declared. It returns the sub-ticket to `checks-in-flight`, the state in which the reviewer and verifier judge it, with its recorded results kept, so the build merges it on its next pass. Rejected: one acceptance per head, because a catch-up run makes a new head and the same paths would park again. Rejected: amending the pinned spec's Risk section, because no command amends a pinned spec yet (T-0027 asks for one). An acceptance adds paths only for that sub-ticket and leaves every other merge condition in force.
- `--accept-paths` refuses, with exit 2 and nothing written, on a park whose reason does not start `BLOCKED from merge gate:`. Its error starts `--accept-paths applies to`. It also refuses when the head is not the branch tip, or when no undeclared protected path remains.
- A ruling on a park whose reason starts `ESCALATE from reviewer` returns the sub-ticket to `checks-in-flight`, round count unchanged. Its recorded results are set aside as `--redispatch` sets them aside: an APPROVE reviewer result is kept, and a VERIFIED verifier result with a PASS gate result is kept. Every other result moves to `superseded-<n>/`. The reviewer and verifier runs that follow receive the ruling, as they already do (`factory/compose.py` lines 278 and 300). This overturns `docs/design.md` line 109, which sends a reviewer ESCALATE to the implementer with the round count reset. Rejected: that route, because the 2026-10-05 escalation needed no code change. The re-run reviewer can still return REQUEST-CHANGES when a ruling asks for a fix.
- Check 6 of the reviewer prompt keeps its first two sentences and adds "for the record" to the list of declared paths. Its last sentence says what the gate does: it merges a declared path with no further approval, and refuses and parks one the approved spec does not declare.
- No per-head approval is added for paths that change the factory's own rules (option 3 of the operator's answer). The answer leaves it open for this spec gate. Adding it is a gate edit to this spec (a new lettered part) or a later ticket.

## Risk

Protected paths: `factory/cli.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/06-code-reviewer.md`

- The paths on the line above are in class harness (`factory/**`) and class generated (`docs/prompts/**`). `factory/gitops.py` is declared in case the implementer puts the diff helper there; it may stay untouched. The two `docs/prompts/` files change only by re-copying their design-doc blocks.
- Guardrail paths: the agent prompts. That is the §2 (spec writer) and §6 (code reviewer) blocks of `docs/design.md` and the four prompt files above. One new test file goes under `tests/factory/`. No existing test changes.
- Unprotected documents changed: `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md`, `README.md`.
- Blast radius: every merge on every instance that accepts the new harness revision, the Nanobot fork included. A gate that is too strict parks good changes. A gate that is too loose lets undeclared ones through. Scenarios in both directions guard it.
- Transition cost. No approved spec has the new `Protected paths:` line yet. On this instance, each sub-ticket that touches a protected path will park once at merge. That covers T-0026, T-0027, T-0031 (ready for their planner) and T-0030 (planned, sub-tickets in flight). On the Nanobot instance it covers T-0021 (planned). The operator answers each park with `--accept-paths` or `--ruling`. Specs still waiting at their spec gate can be given the line by a gate edit first (Operator steps).
- Shell quoting. The workflow passes the park reason inside double quotes and replaces only `"`. A protected file whose name contains a backtick or `$` would be expanded by the clerk's shell. No such file exists in either repository.
- Overlap. T-0030 (planned) may edit `factory/prompts/reviewer.md` and the §6 block. T-0027 (amend a pinned spec) could later replace `--accept-paths` with a real amendment. Text conflicts are resolved by the usual catch-up run. The changelog scenario finds this entry by its text, not its number.
- This change's own merge runs on the current runtime, which does not check paths. The new check first acts after the runtime upgrade.

## Operator steps

1. After merge, upgrade the runtime and accept the new harness revision on both instances, as for any harness change. The runtime is the pinned checkout of the harness that runs tickets (`~/dev/spec-factory-harness`). Each instance runs only the harness commit it has accepted, recorded in its `harness.lock`. The two instances are this repository and the Nanobot fork at `~/dev/nanobot-upstream`, the other repository the factory runs on. The rule is standing for both.
2. Before that, decide what to do about approved specs without the `Protected paths:` line. A spec still at its spec gate can get the line by a gate edit, your change to a spec as you approve it (`factory approve-spec <T> --edit F`). On the Nanobot instance those are T-0024, T-0027, T-0030, T-0031 and T-0032. For specs already approved, answer each `BLOCKED from merge gate` park with `factory resolve <sub-ticket> --accept-paths F` or `--ruling F`.
3. If you want option 3 (a per-head approval for paths that change the factory's own rules), say so at this gate. It is not part of this spec.

=== design.md
## Proposed change

Run every new command from the repository root. Changes are listed by part. Parts A to C are code; D and E are text. One new test file, for example `tests/factory/test_merge_protected_paths.py`, covers A to C with its own scratch repositories. Besides the cases the Acceptance scenarios show, it covers these five, which no scenario exercises:
- a ticket with no parent and no approved spec, whose refusal reads `… not declared (<id> has no approved spec): …`;
- `--accept-paths` refused when the ticket's head is not its branch tip;
- `--accept-paths` refused when no undeclared protected path remains;
- a `Protected paths:` line inside a fenced code block of the Risk section, which declares nothing;
- a brace-list entry (`` `core/{a,b}.py` ``), which declares nothing, so a change to `core/b.py` is refused.

A. Merge gate: refuse undeclared protected paths (`factory/cli.py` `merge_cmd`, a helper in `factory/cli.py` or `factory/gitops.py`).
  1. A helper that returns the undeclared protected paths of a ticket at a head:
     - Read the in-repo patterns from `cfg["protected_paths"]`, a mapping of class to a glob or a list of globs (as `instance.fill_preamble` reads it). Skip patterns that start with `~` or `/`. With no in-repo pattern, return an empty list.
     - Run `git diff --name-only --no-renames <integration>...<head> -- ':(glob)<p1>' ':(glob)<p2>' …` in the repository. Its lines are the changed protected paths.
     - Find the pinned spec. For a ticket with a `parent`, it is the parent's `spec.approved_version`; for a ticket with none, the ticket's own. Read `specs/<that id>/v<n>.md` from the store. Missing version or file: no declarations.
     - Take the `## Risk` section, reading lines with `specstore.lines_outside_fences` so that a line inside a fenced code block neither starts nor ends the section nor declares anything (the same rule `compose.without_evidence` uses). The section is the lines after a line that is exactly `## Risk` (trailing spaces allowed), up to the next line that starts with `## ` or `=== `. Each line that matches the regular expression below declares the backticked entries it holds (`none` declares nothing). Skip entries that start with `~` or `/`. An entry is passed to git as given; a brace in it stays literal.
       ```
       ^\s*(?:[-*]\s+)?Protected paths:\s*(none|`[^`]+`(?:\s*,\s*`[^`]+`)*)\s*\.?\s*$
       ```
     - A changed protected path is declared when it is listed by `git diff --name-only --no-renames <integration>...<head> -- ':(glob)<d1>' …` over the declared entries, or when it is in the ticket's `accepted_paths` list (exact match). Return the rest, sorted.
  2. In `merge_cmd`, after the three-row loop and before `with gitops.MergeLock(repo):`, call the helper. When it returns paths:
     - log `merge.refused` with `ticket`, `head`, `reason: "protected paths not declared"` and `paths`;
     - raise `Refused("BLOCKED from merge gate: protected paths not declared in <spec id> spec v<n>: <p1>, <p2>")`. With no approved spec, use `… not declared (<id> has no approved spec): …`.
     - Change no ticket field. The `{"ok": false, "error": …}` line on stdout and the exit code 2 come from the existing `Refused` handling.
  3. Update `merge_cmd`'s docstring to name the new condition.

B. Build workflow (`factory/workflows/build.js`, the `join.decision === 'merge'` branch, lines 194-200): after `const m = …merge…`, when `!m.ok` and `typeof m.error === 'string' && m.error.startsWith('BLOCKED ')`, `await park(st, m.error, outs, 'Build'); return`, before asking the join again. Nothing else in the script changes.

C. Human resolution (`factory/cli.py` `resolve` and `build_parser`).
  1. New mode `--accept-paths F`, added to the parser (help: "a sub-ticket the merge gate refused for undeclared protected paths: accept them under the approved design and return it to its reviewer and verifier"), to the `--decision` guard's list of modes that block `--close`, and to the "resolve needs one of" message. Behaviour, in order, nothing written before the last refusal:
     - refuse unless `st == "parked"` and `reason.startswith("BLOCKED from merge gate:")`. The error is `--accept-paths applies to a merge gate park (BLOCKED from merge gate); <id> is <st> (<reason or 'no park'>)`;
     - refuse when the ticket's `head` is not the tip of its `branch`, with merge's wording;
     - compute the helper of A.1 on the head, and refuse with `nothing to accept: <id> has no undeclared protected path at <head[:9]>` when it is empty;
     - copy F to `approvals/<id>/ruling-<n>.md`. Set `t["accepted_paths"]` to the sorted union of the old list and the computed paths. Call `move("checks-in-flight", "accept-paths", {"ruling": <rel>, "head": head, "accepted": paths})`. No result row moves.
  2. In the `--ruling` branch, before the planner/critic choice: a reason that starts with `ESCALATE from reviewer` returns the ticket to `checks-in-flight`. First set aside the head's rows with the same rule `--redispatch` uses. Move that block into a small function both branches call, with no change to `--redispatch`'s behaviour. Log `results.superseded`. Then write the ruling file and `move("checks-in-flight", "ruling", {"ruling": …, "head": head, "superseded": moved})`.
  3. A park reason that starts with `BLOCKED from merge gate:` already takes the BLOCKED branch of `--ruling` (`ready-for-implementer`, same round). No code change is needed; the new test covers it.

D. Prompts. Edit each design block and re-copy it to its `docs/prompts/` file byte for byte. Apply the same text change to the run copy under `factory/prompts/`, keeping that copy's existing fills.
  1. Code reviewer (`docs/design.md` "## 6. Code reviewer" block, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`). Check 6 becomes exactly:
     ```
     6. Protected paths touched? If the sub-ticket does not declare them,
        ESCALATE. If it does, list them under ESCALATIONS for the record,
        finish the review, and give the STATUS the code earns. The merge
        gate merges a path the approved spec's Risk section declares with no
        further approval, and refuses and parks one it does not declare.
     ```
  2. Spec writer (`docs/design.md` "## 2. Spec writer" block, `docs/prompts/02-spec-writer.md`, `factory/prompts/spec_writer.md`). The `## Risk` line of FORMAT becomes these four lines:
     ```
     ## Risk             blast radius; every protected path this will touch,
                         declared on one line the merge gate reads:
                         Protected paths: none | `<path or glob>`, `<path or glob>`
                         one path or glob per entry, no brace lists
     ```

E. Documents.
  1. `docs/design.md`, outside the prompt blocks:
     - line 21: "a PR touching a protected path" becomes "a merge refused for a protected path the approved spec does not declare".
     - line 23: "A change to either needs a human approval record before it merges." becomes "A change to a guardrail path needs a human approval record before it merges. A change to a protected path merges when the approved spec's Risk section declares it: the human approves that declaration at the spec gate, and the merge gate refuses a protected path the spec does not declare."
     - line 47 (piece 7): "and a human approval record where piece 8 requires it" becomes "every changed protected path declared (piece 8), and a human approval record where piece 8 requires one".
     - line 48 (piece 8): the first sentence becomes "If the diff touches a protected path, the merge gate requires the pinned spec's Risk section to declare it on its `Protected paths:` line, or a human to have accepted that path for the sub-ticket after the gate refused it (`resolve --accept-paths`); the spec gate's approval is the authorization, and there is no per-PR approval. If the diff touches a guardrail path, the merge gate requires an approval row signed by a human identity." "any other guardrail or protected path needs a human approval on the PR itself" becomes "any other guardrail path needs a human approval on the PR itself". In the GitHub column, "skills, prompts, and protected paths" becomes "skills and prompts; protected paths get a required check that fails on a changed protected path the pinned spec does not declare".
     - line 49 (piece 9): "review protected PRs" becomes "answer merges refused for an undeclared protected path".
     - resolution rules: after the line-105 bullet, add "  - A merge the gate refused for an undeclared protected path parks as BLOCKED. A ruling returns the sub-ticket to its implementer, same round. `resolve --accept-paths` instead adds the named paths to what that sub-ticket may change and returns it to its checks, whose passing results stand; every other merge condition still applies." In the line-109 bullet, "A PR loop at max rounds, a SPEC-DEFECT, or a reviewer ESCALATE returns" becomes "A PR loop at max rounds or a SPEC-DEFECT returns". Before that bullet, add "  - A reviewer ESCALATE returns to its checks with the ruling in both checkers' input, same round. Its results that did not pass are set aside, so the reviewer runs again; a ruling that asks for a fix becomes the reviewer's REQUEST-CHANGES."
     - line 139 (Merge gate row): "+ piece-8 approvals" becomes "+ piece-8 checks".
     - line 154 becomes:
       ```
       | Protected paths | A merge the gate refused because a changed protected path is not declared in the pinned spec's Risk section | Accepts the paths under the approved design (`resolve --accept-paths`), which returns the sub-ticket to its checks, or sends it back to its implementer with a ruling (`resolve --ruling`) |
       ```
  2. `dev/build-harness.spec.md`:
     - line 246: the piece-8 bullet's "protected glob or **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`protected path <p> needs human approval on H` / `guardrail path <p> needs human approval on H`)" becomes "in-repo protected glob → declared on the `Protected paths:` line of the pinned spec's Risk section, or in the sub-ticket's `accepted_paths` (`protected path <p> not declared in the pinned spec v<N>`); **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`guardrail path <p> needs human approval on H`)".
     - item 25 becomes "25. As 22 plus `pyproject.toml` changed, not declared → exit 2, `protected path pyproject.toml not declared in the pinned spec v1`; with `pyproject.toml` on the pinned spec's `Protected paths:` line → exit 0, no approval row [NEW]".
  3. `docs/changelog.md`: one new numbered entry, after the last one, starting "After issue #57 (2026-10-05), ". It records these points. The merge gate merged protected-path changes without reading any declaration, while the reviewer prompt promised a human approval. The approved spec's Risk section is now the authorization, read from its `Protected paths:` line, one path or glob per entry. The gate refuses an undeclared protected path with `BLOCKED from merge gate`, and the build parks it. `--accept-paths` and `--ruling` resolve that park. A reviewer ESCALATE ruling returns to the checks. The prompt and design lines changed. Numbering stays contiguous.
  4. `README.md`:
     - the "merge gate" row of "Terms used on this page" adds that every protected path the change touches is declared in the approved spec, and that a refusal for an undeclared one parks the sub-ticket for a human;
     - the "Merges, one at a time." bullet adds the condition "every protected path the change touches is declared on the `Protected paths:` line of the approved spec's Risk section, or a human accepted it for this sub-ticket";
     - a new **Built** bullet, `- **Protected paths at merge.**`, says what the gate refuses, that the sub-ticket parks as blocked, the two ways to answer, and that it is tested and has not yet fired on a real ticket;
     - the **Unstick** row adds `--accept-paths F` (the merge gate refused a protected path the approved spec does not declare: accept it under the approved design; `--ruling F` sends the sub-ticket back instead) and says that a ruling on a reviewer's escalation re-runs the checks;
     - the status date moves to the merge date.

Size: about 125 changed lines of code and text in A to E and about 200 lines of new tests. That fits one PR.

## Tests to change

none. No existing test pins the old behaviour. I searched `tests/factory/` for `ESCALATE from reviewer` (no hits) and for `--ruling` (only `test_resolve_rulings.py`, `test_decision_log.py`, `test_sibling_tests.py`; their critic, planner and BLOCKED routes and their refusal text are unchanged). I also checked the five files that call `merge` (`test_shepherd.py`, `test_parent_close_reuse.py`, `test_sibling_tests.py`, `test_store_branch.py`, and the gate fixture of current truth). Their branches change only files outside the fixture instance's protected paths (`.factory/instance.yaml`, `.factory/harness.lock`, `.factory/context.md`). `test_writing_standard.py` and `test_coding_standard.py` compare the §6 and §2 blocks with their `docs/prompts/` copies, and still pass when both are re-copied. The test file added on `main` since v1, `tests/factory/test_role_inputs.py`, tests role inputs and reads no Risk section, merge or ruling route.

=== specs/merge-gate/spec.md
## ADDED Requirements

### Requirement: The merge gate refuses a changed protected path the pinned spec does not declare
`factory merge` MUST refuse with exit 2, merging nothing and changing no ticket field, when a path in `git diff --name-only --no-renames <integration>...<head>` matches an in-repo `protected_paths` glob and is neither declared on a `Protected paths:` line of the Risk section of the pinned spec nor in the ticket's `accepted_paths`. Its error SHALL start `BLOCKED from merge gate: ` and name each such path and no declared one. A declaration in another ticket's spec, or a Risk line in any other form, SHALL declare nothing.

#### Scenario: An undeclared protected path is refused at merge, by name, and nothing merges
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0033-gate.sh <<'EOF'
# Sourced from the repo root, with $1 the line T-0001's approved spec carries in its Risk section
# (each ^ in it stands for a backtick) and $2 the changes the sub-ticket's one commit makes,
# space-separated: `p` appends to file p (creating it), `p-` deletes p, `p>q` renames p to q.
# Builds a scratch instance whose protected paths are `core/**`, `bin/tool` and `~/.secret/**`,
# and a target whose main holds core/a.py, core/b.py, bin/tool and docs/d.md. T-0002's approved
# spec declares `core/b.py`. T-0001 is planned as T-0001.1, whose branch factory/T-0001.1 holds
# that one commit, head $H, with reviewer APPROVE, verifier VERIFIED and gate PASS recorded on $H;
# T-0001.1 is at checks-in-flight. Leaves $B, $T, $H and $M (main's tip).
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
mkdir $T/inst && cp tests/factory/fixtures/instance/context.md $T/inst/
grep -v '^protected_paths:\|^  infra:' tests/factory/fixtures/instance/instance.yaml > $T/inst/instance.yaml
printf '%s\n' 'protected_paths:' '  harness: ["core/**", "bin/tool"]' '  credentials: ["~/.secret/**"]' >> $T/inst/instance.yaml
export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t config user.email f@x && git -C $T/t config user.name f
mkdir -p $T/t/core $T/t/bin $T/t/docs && for f in core/a.py core/b.py bin/tool docs/d.md; do echo x > $T/t/$f; done
git -C $T/t add -A && git -C $T/t commit -q -m init
for id in T-0001 T-0002; do
  [ $id = T-0001 ] && L=$(printf '%s' "$1" | tr '^' '\140') || L='Protected paths: `core/b.py`'
  printf "# F $id\n\nDo x.\n" > $T/req.md
  printf '=== proposal.md\n## Problem\nx\n## Risk\nBlast radius: small.\n%s\n=== design.md\n## Proposed change\nA. x\n' "$L" > $T/spec.md
  $B ticket new --file $T/req.md >/dev/null
  $B ticket transition $id --to ready-for-spec-writer --by t >/dev/null && $B spec add $id --file $T/spec.md >/dev/null
  $B ticket transition $id --to ready-for-critic --by t --round spec:init >/dev/null
  $B ticket transition $id --to awaiting-spec-gate --by t >/dev/null && $B approve-spec $id >/dev/null
done
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && $B subticket add T-0001 --file $T/plan.md >/dev/null
$B ticket transition T-0001 --to planned --by t >/dev/null
git -C $T/t checkout -q -b factory/T-0001.1
for f in $(echo "$2"); do
  case $f in
    *'>'*) mkdir -p $T/t/$(dirname ${f#*>}) && git -C $T/t mv ${f%%>*} ${f#*>} ;;
    *-) git -C $T/t rm -q ${f%-} ;;
    *) mkdir -p $T/t/$(dirname $f) && echo y >> $T/t/$f && git -C $T/t add $f ;;
  esac
done
git -C $T/t commit -q -m work && H=$(git -C $T/t rev-parse HEAD) && git -C $T/t checkout -q main && M=$(git -C $T/t rev-parse main)
$B ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/r.md
$B results record T-0001.1 --head $H --role verifier --output $T/v.md --run run-0001-verifier >/dev/null
$B results record T-0001.1 --head $H --role reviewer --output $T/r.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py bin/tool docs/d.md' && $B merge T-0001.1 >$T/o 2>/dev/null; x=$?; J=$(tail -1 $T/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from merge gate: ') named=$(echo "$J" | grep -o 'core/b\.py\|bin/tool' | sort -u | grep -c .) declared=$(echo "$J" | grep -c 'core/a\.py\|docs/d\.md') main=$([ "$(git -C $T/t rev-parse main)" = "$M" ] && echo unchanged || echo moved) $($B ticket show T-0001.1 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=2 blocked=1 named=2 declared=0 main=unchanged checks-in-flight`. `named=2`: the error names both undeclared protected paths. `declared=0`: it names neither the declared protected path nor the unprotected one.

#### Scenario: Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The three cases: T-0001 declares nothing while T-0002 declares `core/b.py`; the sub-ticket renames `core/b.py` out of the protected tree; T-0001's only mention of `core/b.py` is a line `Not touched: ` followed by it.
- WHEN `(for c in 'Protected paths: none|core/b.py' 'Protected paths: none|core/b.py>docs/b.py' 'Not touched: ^core/b.py^|core/b.py'; do (. ${TMPDIR:-/tmp}/t0033-gate.sh "${c%%|*}" "${c#*|}" && $B merge T-0001.1 >$T/o 2>/dev/null; x=$?; echo "exit=$x named=$(tail -1 $T/o | grep -c 'core/b\.py') main=$([ "$(git -C $T/t rev-parse main)" = "$M" ] && echo unchanged || echo moved)"); done)`
- THEN it prints three lines, each exactly `exit=2 named=1 main=unchanged`

### Requirement: A declared or unprotected path merges with no further approval
`factory merge` SHALL merge, as before, a sub-ticket whose changed protected paths are all declared on its pinned spec's `Protected paths:` line, by exact path or glob, and one that changes no protected path.

#### Scenario: A declared protected path, or an unprotected one, merges with no further approval
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(for c in 'Protected paths: ^core/**^, ^bin/tool^|core/a.py core/new/c.py bin/tool' 'Protected paths: none|docs/d.md docs/e.md'; do (. ${TMPDIR:-/tmp}/t0033-gate.sh "${c%%|*}" "${c#*|}" && $B merge T-0001.1 >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p')"); done)`
- THEN it prints exactly `exit=0 merged`, twice

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: The build parks a merge the gate blocked, with the gate's reason
When `factory merge` is refused with an error that starts `BLOCKED `, `factory/workflows/build.js` MUST park the sub-ticket with that error, verbatim, as the reason, and SHALL NOT record it as a harness bug.

#### Scenario: The build parks a merge refused for protected paths with the gate's reason
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "ticket join": {"out": {"ok": true, "decision": "merge", "reason": "ci PASS + APPROVE + VERIFIED on the current head"}}, "merge": {"out": {"ok": false, "error": "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"}, "exit": 2}}')`
- THEN it prints exactly `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`

=== specs/human-resolution/spec.md
## ADDED Requirements

### Requirement: Accepting the refused paths returns the sub-ticket to its checks, which then merge
`factory resolve <id> --accept-paths F`, on a park whose reason starts `BLOCKED from merge gate:`, MUST write F as the ticket's next ruling, add the head's undeclared protected paths to the ticket's `accepted_paths`, keep every result row, and return the ticket to `checks-in-flight`; `factory merge` SHALL then merge it. On any other park it MUST refuse with exit 2, writing nothing, with an error containing `--accept-paths applies to`.

#### Scenario: Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The scenario parks the sub-ticket with the gate's own error, as the build does.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: core/b.py is part of the approved design.\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>&1; echo "accept=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') rows=$(ls $FACTORY_STATE/results/$H | grep -c yaml) ruling=$(cmp -s $T/ru.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo kept || echo missing)"; $B merge T-0001.1 >/dev/null 2>&1; echo "merge=$? on_main=$(git -C $T/t diff --name-only $M main | grep -c 'core/b\.py')")`
- THEN it prints exactly `accept=0 checks-in-flight rows=3 ruling=kept`, then `merge=0 on_main=1`

#### Scenario: Accepting paths is refused on any other park and writes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: x\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>$T/err; echo "accept=$? refused=$(grep -c 'accept-paths applies to' $T/err) $($B ticket show T-0001.1 | sed -n 's/^status: //p') rulings=$(ls $FACTORY_STATE/approvals/T-0001.1 2>/dev/null | grep -c ruling)")`
- THEN it prints exactly `accept=2 refused=1 parked rulings=0`

### Requirement: A ruling on a merge gate's refusal sends the sub-ticket back to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts `BLOCKED from merge gate:` SHALL return the sub-ticket to `ready-for-implementer` at the same round, and the next implementer input SHALL contain F.

#### Scenario: A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: take core/b.py out of this change.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "ruling=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') reason=$(echo "$E" | grep -c '^BLOCKED from merge gate: ')"; R=$($B run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take core/b.py out of this change.')")`
- THEN it prints exactly `ruling=0 ready-for-implementer reason=1`, then `in_input=1`

### Requirement: A ruling on a reviewer's escalation returns the sub-ticket to its checks
`factory resolve <id> --ruling F` on a park whose reason starts `ESCALATE from reviewer` MUST write F as the ticket's next ruling and return the ticket to `checks-in-flight` at the same round. It MUST set aside the head's rows that did not pass, by the rule `--redispatch` uses, and the next reviewer input SHALL contain F.

#### Scenario: A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'docs/d.md' && printf "Commit: $H\nSTATUS: ESCALATE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/e.md && $B results record T-0001.1 --head $H --role reviewer --output $T/e.md --run run-0003-reviewer >/dev/null && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: the escalation is settled.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')"; R=$($B run start --role reviewer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: the escalation is settled.')")`
- THEN it prints exactly `exit=0 checks-in-flight kept: ci.yaml verifier.yaml ` (the reviewer's ESCALATE row set aside, the passing verifier and gate rows kept), then `in_input=1`

=== specs/role-escalations/spec.md
## MODIFIED Requirements

### Requirement: Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
The system prompts of implementer, code reviewer and verifier runs MUST still carry the preamble's rule to escalate a protected path that the approved spec's Risk section does not declare. The code reviewer's prompt MUST still carry check 6's rule to ESCALATE a path the sub-ticket does not declare and to list a declared one under ESCALATIONS. Check 6 SHALL say that the merge gate merges a path the approved spec's Risk section declares with no further approval, and SHALL NOT promise a human approval at merge.

#### Scenario: All three run prompts keep the undeclared-path rule and the reviewer keeps check 6
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && u="a protected path the approved spec's Risk section does not declare"; for r in implementer reviewer verifier; do echo "$r undeclared=$(prompt $r | grep -cF "$u")"; done; echo "check6=$(prompt reviewer | grep -cF '6. Protected paths touched? If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS')")`
- THEN it prints exactly `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1`, one per line

#### Scenario: The reviewer run prompt says what the merge gate checks
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && P=$(prompt reviewer); echo "gate=$(echo "$P" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval") promise=$(echo "$P" | grep -c 'will require a human approval')")`
- THEN it prints exactly `gate=1 promise=0`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The prompts tell the reviewer what the gate checks and the spec writer how to declare
Every copy of the code reviewer prompt (the `docs/design.md` §6 block, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`) SHALL carry check 6's new last sentence and MUST NOT say `will require a human approval`. Every copy of the spec writer prompt SHALL give the `Protected paths:` line under Risk and the rule of one path or glob per entry with no brace lists. Each design block and its `docs/prompts/` file MUST stay byte-identical, and each `factory/prompts/` copy SHALL differ from its `docs/prompts/` file only where it did on `main`.

#### Scenario: Every reviewer prompt copy states what the merge gate checks
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "gate=$(echo "$J" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval, and refuses and parks one it does not declare") promise=$(echo "$J" | grep -c 'will require a human approval')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `gate=1 promise=0`, then `copy=SAME fill=unchanged`

#### Scenario: Every spec writer prompt copy gives the declaration line
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-sw.txt; T=$(mktemp -d); sed -n '/^## 2\. Spec writer/,/^## 3\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; do echo "reads=$(grep -c 'declared on one line the merge gate reads:$' $f) form=$(grep -c '^ *Protected paths: none | .<path or glob>., .<path or glob>.$' $f) braces=$(grep -c '^ *one path or glob per entry, no brace lists$' $f)"; done; git show main:factory/prompts/spec_writer.md > $T/a; git show main:docs/prompts/02-spec-writer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/02-spec-writer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/spec_writer.md docs/prompts/02-spec-writer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `reads=1 form=1 braces=1`, then `copy=SAME fill=unchanged`

### Requirement: The documents record the protected-path rule at merge
`docs/design.md` SHALL drop the per-PR approval for protected paths, describe the declared-path rule in piece 8 and the Protected paths gate row, and route a reviewer ESCALATE back to its checks; `dev/build-harness.spec.md` SHALL describe the same rule; `docs/changelog.md` SHALL gain an entry for issue #57 and stay numbered without a gap; `README.md` SHALL describe the check and `--accept-paths`; and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec drop the per-PR approval for protected paths
- WHEN `(echo "gates=$(grep -c 'a PR touching a protected path, the daily escalation queue' docs/design.md) either=$(grep -c 'A change to either needs a human approval record before it merges' docs/design.md) onpr=$(grep -c 'any other guardrail or protected path needs a human approval on the PR itself' docs/design.md) piece8=$(grep '^| 8 |' docs/design.md | grep -c 'Protected paths:') piece9=$(grep -c 'review protected PRs' docs/design.md) gaterow=$(grep '^| Protected paths |' docs/design.md | grep -c -- '--accept-paths') stale=$(grep -c 'records the piece-8 approval; the merge gate does not merge without it' docs/design.md) reviewer_rule=$(grep -c '^  - A reviewer ESCALATE returns to its checks' docs/design.md) old_route=$(grep -c 'or a reviewer ESCALATE returns to the implementer' docs/design.md) build=$(grep -c 'protected path pyproject.toml needs human approval on H' dev/build-harness.spec.md) build_new=$(grep '^25\. ' dev/build-harness.spec.md | grep -c 'not declared')")`
- THEN it prints exactly `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0 build=0 build_new=1`

#### Scenario: The changelog records issue 57's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #57 ' docs/changelog.md | grep -oF -e 'Risk' -e '--accept-paths' -e 'BLOCKED from merge gate' -e 'checks' -e 'Protected paths:' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the protected-path check and the new resolve verb
- WHEN `(echo "built=$(grep -c '^- \*\*Protected paths at merge\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--accept-paths') merges=$(sed -n '/^- \*\*Merges, one at a time\.\*\*/,/^- \*\*Setting up the store\.\*\*/p' README.md | grep -c 'Risk section' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `built=1 unstick=1 merges=1`

#### Scenario: The protected-path change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Each NEW item's failure today was observed on `main` at `d226a4d` with a throwaway `HOME`, running the WHEN as written, except where an item says otherwise. `main` is now `220ebdc`. That change touches only `factory/compose.py` and adds `tests/factory/test_role_inputs.py`; `git diff --quiet d226a4d 220ebdc -- factory/cli.py factory/workflows/build.js factory/prompts docs dev README.md` exits 0. Rulings still reach the implementer, reviewer and verifier inputs there (`factory/compose.py` lines 278 and 300). I did not re-run the scenarios on `220ebdc` in this round: running the fixture script was refused by this session's tool permissions.

- An undeclared protected path is refused at merge, by name, and nothing merges → NEW. Today it prints `exit=0 blocked=0 named=0 declared=0 main=moved merged`: the merge goes through with `core/b.py` and `bin/tool` undeclared.
- Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing → NEW. Today it prints `exit=0 named=0 main=moved` three times.
- A declared protected path, or an unprotected one, merges with no further approval → REGRESSION. It prints `exit=0 merged` twice today. It guards against a gate that refuses too much, or that chokes on the out-of-repo `~/.secret/**` pattern.
- The build parks a merge refused for protected paths with the gate's reason → NEW. Today it prints `park: harness-bug: merge: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`.
- Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through → NEW. Today it prints `accept=2 parked rows=3 ruling=missing`, then `merge=2 on_main=1`. The first merge already went through, and `--accept-paths` is an unknown argument.
- Accepting paths is refused on any other park and writes nothing → NEW. Today it prints `accept=2 refused=0 parked rulings=0`. Argparse refuses the unknown flag, with no `--accept-paths applies to` text.
- A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling → NEW. Today it prints `ruling=2 parked reason=0`, then `in_input=0`. The merge went through, so the park reason is empty and `--ruling` refuses it.
- A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling → NEW. Today it prints `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`, then `in_input=0`.
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 → REGRESSION. It prints the expected four lines today.
- The reviewer run prompt says what the merge gate checks → NEW. Today it prints `gate=0 promise=1`.
- Every reviewer prompt copy states what the merge gate checks → NEW. Today it prints `gate=0 promise=1` three times, then `copy=SAME fill=unchanged`.
- Every spec writer prompt copy gives the declaration line → NEW. Today it prints `reads=0 form=0 braces=0` three times, then `copy=SAME fill=unchanged`. The `braces` count is new in v2. I did not run the whole scenario, but `grep -c 'no brace lists' docs/design.md docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md` on `220ebdc` printed `0` for each file, so no copy holds the line today.
- The design doc and build spec drop the per-PR approval for protected paths → NEW. Today it prints `gates=1 either=1 onpr=1 piece8=0 piece9=1 gaterow=0 stale=1 reviewer_rule=0 old_route=1 build=1 build_new=0`. The `piece9` count is new in v2; On `220ebdc`, `grep -c 'review protected PRs' docs/design.md` printed `1`, which is line 49.
- The changelog records issue 57's change without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `0`.
- README describes the protected-path check and the new resolve verb → NEW. Today it prints `built=0 unstick=0 merges=0`.
- The protected-path change adds no whitespace errors → REGRESSION.

## Responses

- [BLOCKING] 6, unglossed terms in Evidence, Decisions and Operator steps. FIXED. The Problem now names the two agents that check a sub-ticket, the reviewer (reads the diff) and the verifier (runs the test suite and acceptance commands), and glosses instance, harness, park and ruling. Evidence paragraph 1 says "the fixture script this spec gives under the first merge-gate scenario" in place of "GIVEN block", and glosses the build workflow where it first appears. Decisions bullet 1 glosses the pinned spec and `decisions.md` (the factory's log of standing decisions that later tickets must follow); later bullets gloss catch-up run, round count and `checks-in-flight`. Operator step 1 glosses the runtime (the pinned checkout of the harness, `~/dev/spec-factory-harness`), the harness commit each instance accepts in its `harness.lock`, and names the Nanobot instance as the fork at `~/dev/nanobot-upstream`. Step 2 glosses a gate edit.
- [SHOULD-FIX] 6, two names per concept. FIXED. The Problem introduces "the integration branch (the branch the factory merges into, `main` here)", and every later human-facing sentence uses that name. "Reviewing agents" and "checkers" are gone from proposal.md: it says "the reviewer and verifier" throughout, and "recorded results" for what v1 called rows. The design.md resolution-rule text that goes into `docs/design.md` keeps "checks" and "checkers", which are that document's own terms.
- [SHOULD-FIX] 4, brace lists. FIXED. Decisions bullet 2 now says each entry is one path or one glob, and that a brace list is one literal entry that git does not expand, so it declares nothing. D.2's FORMAT gains a fourth line, `one path or glob per entry, no brace lists`. The spec-writer scenario checks it (`braces=1`), and A.1 says an entry goes to git as given. The new test file covers a brace-list entry being refused.
- [NIT] 2, three untested branches. FIXED as suggested. The design.md opening now lists the cases the new test file must cover: the no-approved-spec wording, both secondary `--accept-paths` refusals, plus a fenced `Protected paths:` line and a brace-list entry. The acceptance list is unchanged apart from the two added counts.
- [NIT] 5, piece 9 still says "review protected PRs". FIXED. E.1 changes line 49's phrase to "answer merges refused for an undeclared protected path", Evidence lists line 49 among the per-PR places, and the design-doc scenario checks it (`piece9=0`).
- Change not asked for by a finding: A.1 now reads the Risk section with `specstore.lines_outside_fences`, so a `Protected paths:` line quoted inside a fenced code block declares nothing. This follows the section rule `compose.without_evidence` adopted on `main` since v1 (`220ebdc`). Without it, a spec that quotes an example declaration in its Risk section would authorize the example's paths.
- Critic's out-of-scope note on the 2026-10-07 T-0032 line in `decisions.md`. The note says that line attributes T-0028.1's by-hand ruling to the budget-kill and EMPTY-OUTPUT route, while it was a reviewer ESCALATE misroute. This spec leaves the decision log unchanged. The Evidence bullet "The case that exposed the gap" records the correct cause, with the ruling file as the source.

## Current truth: build-dispatch

# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

### Requirement: An implementer starts only when each sibling-added test it may change came from a merged sibling
`factory run start --role implementer` on a sub-ticket MUST refuse with exit 2, writing no run, worktree, branch or in-flight entry, with an error that starts `BLOCKED from harness: ` and names the file, when a line `` `<file>` (added by <ID>) `` inside its "Tests to change" field names a file that existed at the parent's base, or whose first adding commit on the integration branch since that base lies inside no merged sibling's recorded merge. It SHALL accept a file a merged sibling's merge added, and SHALL ignore such a line outside that field.

#### Scenario: A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0022-sib.sh <<'EOF'
# Sourced from the repo root with E set to a test file path. Builds a scratch store whose parent
# T-0001 is planned as ST-1 and ST-2: ST-2 depends on ST-1 and lists `$E` under Tests to change as
# added by ST-1. Builds a scratch target whose main holds tests/test_old.py from before the plan,
# tests/test_interim.py from ST-1's recorded merge, and tests/test_operator.py from a later direct
# commit that is no sibling's merge. ST-2's Scope line mentions tests/test_old.py in the same form.
# T-0001.1 is merged; T-0001.2 is ready for its implementer.
T22=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T22/store FACTORY_REPO=$T22/t FACTORY_INTEGRATION_BRANCH=main
printf '# Fixture\n\nThe bot should do the thing.\n' > $T22/req.md && printf '## Problem\nx\n' > $T22/spec.md
bin/factory ticket new --file $T22/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T22/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T22/t && mkdir $T22/t/tests && echo 'def test_old(): pass' > $T22/t/tests/test_old.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm base && A=$(git -C $T22/t rev-parse HEAD)
git -C $T22/t checkout -qb sib && echo 'def test_interim(): pass' > $T22/t/tests/test_interim.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm interim && git -C $T22/t checkout -q main
git -C $T22/t -c user.email=f@x -c user.name=f merge -q --no-ff -m 'Merge ST-1' sib && B=$(git -C $T22/t rev-parse HEAD)
echo 'def test_operator(): pass' > $T22/t/tests/test_operator.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm operator
printf 'ST-1 / Interim\nDepends on: none\nParallel-safe: yes\nInterim tests: `tests/test_interim.py`, broken by ST-2\n\nST-2 / Final\nDepends on: ST-1\nParallel-safe: yes\nScope: B, which reads `tests/test_old.py` (added by the base commit)\nTests to change:\n- `%s` (added by ST-1): ST-2 replaces the interim behaviour\nProtected paths: none\n' "$E" > $T22/plan.md
bin/factory subticket add T-0001 --file $T22/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket set T-0001.1 status=merged "merge.base_before='$A'" "merge.main_after='$B'" >/dev/null
bin/factory ticket set T-0001 "parent_base='$A'" >/dev/null
bin/factory ticket set T-0001.2 status=ready-for-implementer >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0022-build.mjs <<'EOF'
// node t0022-build.mjs, from the checkout under test after sourcing t0022-sib.sh: runs
// factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE. Each clerk command runs
// for real (sh -c, from this checkout, environment unchanged); each role run returns an empty
// output, which the workflow records as a killed run. Prints each park, as `park <id>: <reason>`.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return ''
  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
}
const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p') runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `exit=0 ready-for-implementer runs=1`

#### Scenario: A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(for E in tests/test_old.py tests/test_operator.py tests/test_never.py; do (. ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >$T22/o 2>/dev/null; x=$?; J=$(tail -1 $T22/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: ') names=$(echo "$J" | grep -cF "$E") runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) branch=$(git -C $FACTORY_REPO branch --list 'factory/T-0001.2' | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"); done)`
- THEN it prints three lines, each exactly `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`

### Requirement: The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it
When an implementer's run start is refused with an error that starts `BLOCKED `, the build workflow SHALL park the sub-ticket with that error, verbatim, as the reason, so that `factory resolve <id> --ruling F` MUST accept the park and return the sub-ticket to `ready-for-implementer`.

#### Scenario: The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(E=tests/test_old.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(BLOCKED from harness:\).*/\1/'; printf 'Ruling: x\n' > $T22/r.md; bin/factory resolve T-0001.2 --ruling $T22/r.md >/dev/null 2>&1; echo "ruling=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')")`
- THEN it prints exactly `park T-0001.2: BLOCKED from harness:`, then `ruling=0 ready-for-implementer`

### Requirement: The build asks the whole-spec step before it runs the planner
At `ready-for-planner`, `factory/workflows/build.js` MUST first run `plan whole-spec`. On `"planner": "skipped"` it SHALL move the parent to `planned` and build the sub-ticket with no planner run. On any other success it SHALL run the planner as before. On a refusal it MUST park the parent with `harness-bug: plan whole-spec: <error>`.

#### Scenario: A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": true, "planner": "skipped", "reason": "fixture", "subtickets": [{"id": "T-0001.1"}]}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": false, "error": "T-0001 has no approved spec"}, "exit": 2}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, `park: harness-bug: plan whole-spec: T-0001 has no approved spec`, one per line

#### Scenario: A spec that needs the planner still gets a planner run
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": true, "planner": "needed", "reason": "the spec writer marked it NEEDS-SPLIT"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "stub stop"}, "exit": 2}}')`
- THEN it prints exactly `start: planner`, then `park: harness-bug: subticket add: stub stop`

### Requirement: A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT
When a role run ends without an output file, or with a blank one, whatever the agent call returned, `run finish` MUST record it as `EMPTY-OUTPUT` and never as `KILLED`. The workflow MUST keep the agent's non-blank last message as that run's `last-message.md` and re-dispatch the same role once. A second `EMPTY-OUTPUT` in a row SHALL park the ticket as `EMPTY-OUTPUT from <role>`, with no result row for that run.

#### Scenario: A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0032-checks.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh: T-0001 is planned as one sub-ticket, T-0001.1,
# whose branch factory/T-0001.1 holds one commit; T-0001.1 is at checks-in-flight on that head $H,
# with no result rows, so the build runs both checkers on it.
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md
bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
git -C $T23/t checkout -qb factory/T-0001.1 && echo x > $T23/t/x.txt && git -C $T23/t add x.txt
git -C $T23/t -c user.email=f@x -c user.name=f commit -qm work && git -C $T23/t checkout -q main
H=$(git -C $T23/t rev-parse factory/T-0001.1)
bin/factory ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0032-build.mjs <<'EOF'
// node t0032-build.mjs '<plays JSON>', from the checkout under test after sourcing t0023-parent.sh
// and t0032-checks.sh: runs factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE.
// Each clerk command runs for real (sh -c, from this checkout, environment unchanged). Each role
// run plays the next entry of its role's list in <plays> (the last one repeats):
//   {"say": "<text>"}     returns <text> (or null) as its final message and writes no output file;
//   {"write": "<STATUS>"} writes an output with the run's head as its Commit: line (and, for the
//                         verifier, "Gate suite: PASS") and that STATUS, and returns the same text.
// Prints each park, as `park <id>: <reason>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const plays = JSON.parse(process.argv[2]), n = {}
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const list = plays[r[2]] || [{ say: '' }]
  n[r[2]] = (n[r[2]] || 0) + 1
  const p = list[Math.min(n[r[2]], list.length) - 1]
  if ('say' in p) return p.say
  const head = (readFileSync(`${r[1]}/meta.yaml`, 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = `Commit: ${head}\n` + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') + `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(M="Both suite runs are still in progress; I'll write the review once the monitor reports their final lines."; . ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs "{\"reviewer\": [{\"say\": \"$M\"}], \"verifier\": [{\"write\": \"VERIFIED\"}]}"; for r in reviewer verifier; do echo "$r: $(for d in $(ls -d $FACTORY_STATE/runs/*-$r); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')"; done; echo "kept=$(find $FACTORY_STATE/runs -path '*-reviewer/last-message.md' -exec grep -lxF "$M" {} + | grep -c .) $(bin/factory results show T-0001.1 | tail -1 | grep -o '"rows": {[^}]*}')")`
- THEN it prints exactly `park T-0001.1: EMPTY-OUTPUT from reviewer`, then `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` (two reviewer runs, both empty), then `verifier: VERIFIED `, then `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` (both last messages kept verbatim, apostrophe included; no reviewer row, so a `--redispatch` re-runs only the reviewer)

#### Scenario: One empty reviewer run followed by a real one routes on the real one
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once. The first reviewer call returns `null`; the verifier's SPEC-DEFECT gives the join a fixed stop.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"say": null}, {"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: EMPTY-OUTPUT APPROVE `

#### Scenario: An implementer that returns nothing twice parks as EMPTY-OUTPUT
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once. In that fixture every role run returns an empty string.
- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs; echo "implementer: $(for d in $(ls -d $FACTORY_STATE/runs/*-implementer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.2: EMPTY-OUTPUT from implementer`, then `implementer: EMPTY-OUTPUT EMPTY-OUTPUT `

#### Scenario: An intake role's second empty output in a row parks as EMPTY-OUTPUT
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once. The stub store answers every `run finish` with `EMPTY-OUTPUT`.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": {"out": {"ok": true, "run_id": "run-0009-x", "status": "EMPTY-OUTPUT", "escalations": []}}}')`
- THEN it prints exactly `start: triage`, then `start: triage`, then `park: EMPTY-OUTPUT from triage`

### Requirement: A role run that writes its output runs once and routes on its STATUS
A role run whose output file holds a STATUS MUST NOT be re-dispatched, and the build SHALL route on that STATUS as before.

#### Scenario: A reviewer that writes its output runs once
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: APPROVE `

## Current truth: gate-commands

# gate-commands

## Requirements

### Requirement: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them
Each `gate_commands` entry SHALL be a command string or a mapping of `command` and an optional `paths` list of git pathspecs. When a reviewer or verifier run starts on a sub-ticket, the harness MUST mark SKIPPED, with its reason, each command whose paths the diff from base to head touches none of. It MUST list that command apart from the commands to run, and record it in the run's `meta.yaml`. A command with no `paths` SHALL always be listed to run.

#### Scenario: A gate command scoped to paths is skipped for a diff that touches none of them
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0028-sub.sh <<'EOF'
# Sourced from the repo root, with $1 the file the sub-ticket's one commit changes (docs/b.md or
# src/a.txt) and $2 `scoped` or `plain`. Builds a scratch instance and target. `scoped` gives the
# gate the unscoped command `git diff --check main...HEAD` and the command `sh -c 'exit 7'` scoped
# to `src/`; `plain` keeps the fixture's one unscoped command. Sub-ticket T-0001.1 reaches
# checks-in-flight with that commit as its head; a verifier run is started and composed on it.
# Leaves $B (the CLI), $T, $I (the implementer run), $R and $V (the verifier run and its
# directory), $H (the head) and $COMPOSE (that compose's exit code).
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
mkdir $T/inst && cp tests/factory/fixtures/instance/context.md $T/inst/
grep -v '^gate_commands:' tests/factory/fixtures/instance/instance.yaml > $T/inst/instance.yaml
if [ "$2" = scoped ]; then
  printf '%s\n' 'gate_commands:' '  - "git diff --check main...HEAD"' "  - {command: \"sh -c 'exit 7'\", paths: [\"src/\"]}" >> $T/inst/instance.yaml
else
  printf '%s\n' 'gate_commands: ["git diff --check main...HEAD"]' >> $T/inst/instance.yaml
fi
export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t config user.email f@x && git -C $T/t config user.name f
mkdir -p $T/t/src $T/t/docs && echo a > $T/t/src/a.txt && echo b > $T/t/docs/b.md
git -C $T/t add -A && git -C $T/t commit -q -m init
printf '# F\n\nDo x.\n' > $T/req.md && printf '## Problem\nx\n' > $T/spec.md
$B ticket new --file $T/req.md >/dev/null
$B ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
$B spec add T-0001 --file $T/spec.md >/dev/null
$B ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
$B ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
$B approve-spec T-0001 >/dev/null
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && $B subticket add T-0001 --file $T/plan.md >/dev/null
I=$($B run start --role implementer --ticket T-0001.1 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
echo more >> $T/store/worktrees/T-0001.1/$1 && git -C $T/store/worktrees/T-0001.1 commit -q -am change
$B run finish $I --status-override READY-FOR-REVIEW >/dev/null && $B ticket head T-0001.1 >/dev/null
$B ticket transition T-0001.1 --to checks-in-flight --by t --round pr:init >/dev/null
R=$($B run start --role verifier --ticket T-0001.1 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); V=$T/store/runs/$R
H=$(git -C $T/t rev-parse factory/T-0001.1)
$B run compose $R >/dev/null 2>&1; COMPOSE=$?
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -vc 'exit 7') skipped=$(grep '^SKIPPED' $V/input.md 2>/dev/null | grep -F 'exit 7' | grep -c 'src/') meta=$(grep -c 'exit 7' $V/meta.yaml | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `compose=0 run=1 skipped=1 meta=1`

#### Scenario: A diff that touches a scoped command's paths runs that command
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh src/a.txt scoped && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -cF 'exit 7') skipped=$(grep -c '^SKIPPED' $V/input.md 2>/dev/null)")`
- THEN it prints exactly `compose=0 run=1 skipped=0`

#### Scenario: A gate command with no paths runs on every diff, as today
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md plain && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md | grep -cF 'git diff --check main...HEAD') skipped=$(grep -c '^SKIPPED' $V/input.md)")`
- THEN it prints exactly `compose=0 run=1 skipped=0`

### Requirement: A skipped command is recorded on the gate result, and the merge still needs that result to pass
When a verifier's result is recorded, the `ci` row MUST list each command that verifier run skipped, with status SKIPPED and its reason. `factory merge` SHALL still refuse unless that row is PASS.

#### Scenario: A skipped gate command is recorded on the gate result, and the merge still needs a passing gate
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && for g in FAIL PASS; do printf 'Commit: %s\nGate suite: %s\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' $H $g > $T/v.md; printf 'Commit: %s\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' $H > $T/r.md; $B results record T-0001.1 --head $H --role verifier --output $T/v.md --run $R >/dev/null; $B results record T-0001.1 --head $H --role reviewer --output $T/r.md --run run-0003-reviewer >/dev/null; $B merge T-0001.1 >/dev/null 2>&1; m=$?; C=$T/store/results/$H/ci.yaml; echo "$g: merge=$m recorded=$(grep -q 'exit 7' $C && grep -q SKIPPED $C && echo yes || echo no)"; done)`
- THEN it prints exactly `FAIL: merge=2 recorded=yes`, then `PASS: merge=0 recorded=yes`

### Requirement: The implementer is given every gate command
The implementer's input SHALL list every gate command to run, scoped or not, and no SKIPPED line.

#### Scenario: The implementer is still given every gate command
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && $B run compose $I >/dev/null 2>&1; echo "compose=$? both=$(grep -F 'Gate commands' $T/store/runs/$I/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -cF 'exit 7') skipped=$(grep -c '^SKIPPED' $T/store/runs/$I/input.md 2>/dev/null)")`
- THEN it prints exactly `compose=0 both=1 skipped=0`

### Requirement: A malformed gate entry refuses every build role's run start
A `gate_commands` entry MUST make `run start` refuse with exit 2 for the implementer, reviewer or verifier, naming `gate_commands` and creating no run, when it is anything other than one of these: a string; or a mapping with a non-empty string `command`, an optional non-empty list of non-empty strings `paths`, and no other key.

#### Scenario: A malformed gate entry refuses a checker's run start and creates no run
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(for bad in '{command: "true", path: ["src/"]}' '{command: "true", paths: "src/"}'; do (. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md plain && grep -v '^gate_commands:' $T/inst/instance.yaml > $T/i.yaml && echo "gate_commands: [$bad]" >> $T/i.yaml && mv $T/i.yaml $T/inst/instance.yaml && n=$(ls $T/store/runs | wc -l) && $B run start --role reviewer --ticket T-0001.1 >/dev/null 2>$T/err; echo "exit=$? new_runs=$(( $(ls $T/store/runs | wc -l) - n )) named=$(grep -c 'gate_commands' $T/err)"); done)`
- THEN it prints exactly `exit=2 new_runs=0 named=1`, twice

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 dirs=1 prompts=0`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule, and the build spec SHALL call the store branch only `factory-store`. `docs/changelog.md` SHALL gain one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch, `factory store migrate`, the `git clean -ffdx` hazard and a checkout from before the move, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location. The change MUST add no whitespace errors.

#### Scenario: The design doc names the store branch and the path rule
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
- THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`

#### Scenario: The build spec calls the store branch factory-store
- WHEN `(Q=$(printf '\140'); echo "old_name=$(grep -c "${Q}tickets${Q}\|refs/heads/tickets\|HEAD:tickets" dev/build-harness.spec.md) new_name=$(grep -c 'factory-store' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints `old_name=0 new_name=1`

#### Scenario: The changelog records the store branch in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The README describes the store branch and the move
`old_cost` joins the page into one line first, because the retired clause is wrapped across two lines. `old_refs` counts only the places that give the live store's location, so a how-to may still name the path a store moves from.
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`

#### Scenario: The store-branch change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

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
`docs/design.md` SHALL describe the check in a paragraph that starts `**Tests a sibling added.**`, in piece 8 and in the spec approval gate row, and SHALL no longer call the gate's list the only authorization to alter an existing test; `dev/build-harness.spec.md` SHALL name the `BLOCKED from harness` refusal; `docs/changelog.md` SHALL gain an entry for issue #40 and stay numbered without a gap; `README.md` SHALL describe the check and the new `--ruling` case; and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec describe the check
- WHEN `(echo "piece8=$(grep '^| 8 |' docs/design.md | grep -c 'added by that sibling') gate=$(grep '^| Spec approval |' docs/design.md | grep -c 'a test an earlier sibling added') stale=$(grep -c 'which is the only authorization to alter an existing test' docs/design.md) check=$(grep -c '^\*\*Tests a sibling added\.\*\*.*BLOCKED from harness:' docs/design.md) build=$(grep -c 'BLOCKED from harness' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `piece8=1 gate=1 stale=0 check=1 build=1`

#### Scenario: The changelog records issue 40's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #40 ' docs/changelog.md | grep -oF -e 'own base' -e 'added by' -e 'BLOCKED from harness' -e 'Decision' -e 'critic rubric 1' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the sibling tests check and its ruling
- WHEN `(echo "built=$(grep -c '^- \*\*Sibling tests check\.\*\*' README.md) ruling=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'a test no merged sibling added')")`
- THEN it prints exactly `built=1 ruling=1`

#### Scenario: The sibling-tests change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the declared-path rule
The "## 5. Implementer" and "## 7. Verifier" blocks of `docs/design.md` SHALL carry the declared-path rule and stay verbatim copies of `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`. The run copies under `factory/prompts/` SHALL differ from those files only by the fills they had on `main`. The code reviewer and preamble copies MUST NOT change. `docs/changelog.md` SHALL gain one entry for issue #49, numbered without a gap, and the change MUST add no whitespace errors.

#### Scenario: The design blocks and their copies carry the rule and stay in step
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); for r in "5. Implementer|05-implementer.md|implementer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) rule=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -c 'A protected path the sub-ticket declares is not an escalation') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `implementer copy=SAME rule=1 fill=unchanged`, then `verifier copy=SAME rule=1 fill=unchanged`. `copy=SAME`: the design block equals its `docs/prompts/` file. `rule=1`: that file carries the rule. `fill=unchanged`: the run copy under `factory/prompts/` differs from the documented copy only where it did on `main`.

#### Scenario: The code reviewer and preamble copies do not change
- WHEN `(echo "changed=$(git diff --name-only main...HEAD -- factory/prompts/reviewer.md factory/prompts/preamble.md docs/prompts/06-code-reviewer.md docs/prompts/00-preamble.md | grep -c .)")`
- THEN it prints exactly `changed=0`

#### Scenario: The changelog records the declared-path rule in a contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#49' | grep -c 'ESCALATIONS')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The declared-path change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the small-change lane
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap. `docs/design.md`, `dev/build-harness.spec.md` and `README.md` SHALL describe the whole-spec sub-ticket and gate-command paths. No prompt copy SHALL change, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the small-change lane as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e 'paths' -e SKIPPED -e 'plan whole-spec' -e NEEDS-SPLIT -e seams | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc, build spec and README describe both skips, and no prompt copy changes
- WHEN `(echo "design=$(grep -c 'whole-spec' docs/design.md | awk '{print ($1 > 0)}') gate=$(grep '^| 11 | Gate runner' docs/design.md | grep -c 'SKIPPED') build=$(grep -c 'plan whole-spec' dev/build-harness.spec.md | awk '{print ($1 > 0)}') readme=$(grep -c 'plan whole-spec' README.md | awk '{print ($1 > 0)}') skipped=$(grep -c 'SKIPPED' README.md | awk '{print ($1 > 0)}') stale=$(grep -c 'The build workflow runs the planner, which' README.md) prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts agents | grep -c .)")`
- THEN it prints exactly `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0`

#### Scenario: The small-change lane adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

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
Every copy of the code reviewer prompt SHALL say `Do not run the test suite or the gate commands: the verifier runs them on the same head`, and SHALL allow a narrow command that confirms a specific finding. No existing line of that prompt MAY be removed, and the verifier prompt MUST NOT change. The reviewer's composed input MUST NOT list the gate commands, while the implementer's and the verifier's inputs still SHALL.

#### Scenario: Every reviewer copy carries the rule, keeps every existing line, and the verifier prompt is unchanged
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "judge=$(echo "$J" | grep -c 'Do not run the test suite or the gate commands: the verifier runs them on the same head') narrow=$(echo "$J" | grep -c 'You may run a narrow command to confirm a specific finding')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed) removed=$(git diff main...HEAD -- docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md | grep -v '^---' | grep -c '^-') verifier_changed=$(git diff --name-only main...HEAD -- docs/prompts/07-verifier.md factory/prompts/verifier.md | grep -c .)")`
- THEN it prints three lines, each exactly `judge=1 narrow=1`, then `copy=SAME fill=unchanged removed=0 verifier_changed=0`

#### Scenario: The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && for r in reviewer verifier implementer; do [ $r = implementer ] && bin/factory ticket set T-0001.1 status=ready-for-implementer 'in_flight=[]' >/dev/null; R=$(bin/factory run start --role $r --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); bin/factory run compose ${R:-none} >/dev/null 2>&1; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "$r gates=$(grep -c 'Gate commands (run each from your worktree' $I 2>/dev/null) told=$(grep -c 'The verifier runs the gate commands on this head; you do not run them' $I 2>/dev/null)"; done)`
- THEN it prints exactly `reviewer gates=0 told=1`, `verifier gates=1 told=0`, `implementer gates=1 told=0`, one per line

### Requirement: The documents record the empty-output route
`docs/design.md` SHALL state the EMPTY-OUTPUT rule and its two routing-table rows, and SHALL list a second EMPTY-OUTPUT among the park reasons. `dev/build-harness.spec.md` SHALL describe EMPTY-OUTPUT and `run last-message`, and SHALL no longer describe a KILLED condition or seam. `README.md` SHALL no longer say that a run is parked for exceeding a budget, and SHALL describe the empty-output retry. `docs/changelog.md` SHALL gain an entry for issue #41, numbered without a gap. The change MUST add no whitespace errors.

#### Scenario: The design doc states the EMPTY-OUTPUT rule, its rows and its park
- WHEN `(echo "rule=$(grep -c '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md) rows=$(grep -c '^| Any role | EMPTY-OUTPUT' docs/design.md) parks=$(grep '^- A non-empty ESCALATIONS line' docs/design.md | grep -c 'a second EMPTY-OUTPUT in a row') kill=$(grep -c 'never recorded as a budget kill' docs/design.md)")`
- THEN it prints exactly `rule=1 rows=2 parks=1 kill=1`

#### Scenario: The build spec describes EMPTY-OUTPUT and no longer a KILLED condition
- WHEN `(echo "stale=$(grep -c 'KILLED condition\|KILLED seam' dev/build-harness.spec.md) empty=$(grep -c 'EMPTY-OUTPUT' dev/build-harness.spec.md | awk '{print ($1 > 0)}') note=$(grep -c 'run last-message' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `stale=0 empty=1 note=1`

#### Scenario: README drops the budget park and describes the empty-output retry
- WHEN `(echo "budget=$(grep -c 'exceeding its budget\|over budget' README.md) built=$(grep -c '^- \*\*Empty output\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'ended without output twice')")`
- THEN it prints exactly `budget=0 built=1 unstick=1`

#### Scenario: The changelog records issue 41 without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #41 ' docs/changelog.md | grep -oF -e EMPTY-OUTPUT -e foreground -e 'last message' -e 're-dispatched once' -e 'gate commands' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The empty-output change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

## Current truth: live-store-guard

# live-store-guard

## Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Writes from inside a store's run directories or code checkouts are refused, marked or not
Every `factory` command on an instance's own store except the read-only list above MUST be refused with exit 2, writing nothing, when the caller's directory lies under that store's `runs/` or `worktrees/`, whether or not its environment has `FACTORY_DISPATCH=1` and whether or not any run is in flight.

#### Scenario: Marked writes from a run's scratch directory or a worktree directory are refused, init included
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && mkdir -p $S/worktrees/T-0001/sub && S0=$(snap); cd $W && FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B init --repo-name x >/dev/null 2>&1; i=$?; cd $S/worktrees/T-0001/sub && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "scratch_decision=$d scratch_init=$i worktree_new=$n store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`

#### Scenario: Writes from a finished run's scratch directory are refused with no run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1) && S0=$(snap); cd $W && $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "idle=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]') new=$n decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `idle=1 new=2 decision=2 store=unchanged`

### Requirement: Reads, marked commands from outside the store, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands SHALL succeed from anywhere, a command with `FACTORY_DISPATCH=1` run from outside the store's `runs/` and `worktrees/` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced from any directory; with no run in flight, unmarked writes from outside those directories SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; cd $W && $B ticket show T-0001 >/dev/null 2>&1; w=$?; echo "show=$s config=$c log=$l results=$r inside=$w")`
- THEN it prints exactly `show=0 config=0 log=0 results=0 inside=0`

#### Scenario: A marked write from the repository root still writes while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && cd $T/tgt && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced, even from a run's scratch directory
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_STATE=$T/s $B init >/dev/null 2>&1); i=$?; cd $W && FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

### Requirement: The marker does not lift the harness lock
A command with `FACTORY_DISPATCH=1` on an instance's own store MUST still be refused by the harness lock's uncommitted-edit check, with exit 2 and nothing written, whether or not a run is in flight.

#### Scenario: A marked write from a harness checkout with an uncommitted edit is still refused
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $T/c/bin/factory ticket new --file $T/req.md >/dev/null && $T/c/bin/factory run start --role triage --ticket T-0001 >/dev/null && echo '# uncommitted edit' >> $T/c/factory/status.py && S0=$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum) && FACTORY_DISPATCH=1 $T/c/bin/factory decision add T-0001 x >/dev/null 2>$T/err; echo "exit=$? lock=$(head -1 $T/err | grep -c 'has uncommitted changes:$') store=$([ "$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 lock=1 store=unchanged`

## Current truth: merge-gate

# merge-gate

## Requirements

### Requirement: A store commit does not hold back a merge
On an instance whose store is the checkout of `factory-store`, a store commit made after a sub-ticket's checks SHALL NOT stop `factory merge` from merging that sub-ticket.

#### Scenario: A sub-ticket merges after a store commit
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: rows recorded"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=0 refused=0`

### Requirement: A commit to the integration branch still holds back a merge
`factory merge` MUST still refuse, with `head does not contain main`, a sub-ticket whose head does not contain a commit made to the integration branch after its checks.

#### Scenario: A sub-ticket is refused after a code commit to main
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && echo y > y.txt && git add y.txt && git commit -q -m "code on main"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=2 refused=1`

## Current truth: role-escalations

# role-escalations

## Requirements

### Requirement: The implementer and verifier leave declared protected paths out of ESCALATIONS
The system prompt of every implementer and verifier run SHALL say that a protected path the sub-ticket declares is not an escalation, that the code reviewer lists declared paths once for each head it reviews, that the role may name them but not under ESCALATIONS, and that a protected path the sub-ticket does not declare still goes under ESCALATIONS.

#### Scenario: Implementer and verifier run prompts carry the declared-path rule
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0029-prompt.sh <<'EOF'
# Sourced from the repo root of the checkout under test. Defines `prompt <role>`: starts one run of
# that role (implementer, reviewer or verifier) on a scratch target with a throwaway store, and
# prints the run's system prompt on one line, runs of spaces squeezed.
T29=$(cd "$(mktemp -d)" && pwd -P); B29=$PWD/bin/factory
git init -q -b main $T29/tgt && git -C $T29/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
(cd $T29/tgt && $B29 init --repo-name demo >/dev/null 2>&1)
printf '# F\n\nDo x.\n' > $T29/req.md
(cd $T29/tgt && FACTORY_STATE=$T29/s $B29 ticket new --file $T29/req.md >/dev/null)
prompt() (
  cd $T29/tgt && export FACTORY_STATE=$T29/s
  case $1 in
    implementer) $B29 ticket set T-0001 status=ready-for-implementer 'in_flight=[]' >/dev/null ;;
    *) $B29 ticket set T-0001 status=checks-in-flight 'in_flight=[]' head=$(git rev-parse HEAD) >/dev/null ;;
  esac
  R=$($B29 run start --role $1 --ticket T-0001 --model opus 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
  tr '\n' ' ' < $T29/s/runs/${R:-none}/system-prompt.txt 2>/dev/null | tr -s ' '
)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer verifier; do P=$(prompt $r); echo "$r declared=$(echo "$P" | grep -c 'A protected path the sub-ticket declares is not an escalation') notunder=$(echo "$P" | grep -c 'but not under ESCALATIONS') undeclared=$(echo "$P" | grep -c 'still goes under ESCALATIONS when the sub-ticket does not declare it')"; done)`
- THEN it prints exactly `implementer declared=1 notunder=1 undeclared=1`, then `verifier declared=1 notunder=1 undeclared=1`

### Requirement: Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
The system prompts of implementer, code reviewer and verifier runs MUST still carry the preamble's rule to escalate a protected path that the approved spec's Risk section does not declare, and the code reviewer's prompt MUST still carry check 6 unchanged.

#### Scenario: All three run prompts keep the undeclared-path rule and the reviewer keeps check 6
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && u="a protected path the approved spec's Risk section does not declare"; for r in implementer reviewer verifier; do echo "$r undeclared=$(prompt $r | grep -cF "$u")"; done; echo "check6=$(prompt reviewer | grep -cF '6. Protected paths touched? If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS')")`
- THEN it prints exactly `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1`, one per line

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

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

### Requirement: A spec that needs one sub-ticket becomes that sub-ticket without a planner run
`factory plan whole-spec <parent>`, on a parent at `ready-for-planner` with an approved spec, MUST act when four conditions hold: the parent has no sub-ticket; it has no earlier planner run; its latest spec-writer run did not end NEEDS-SPLIT; and its approved spec has no `##` or `###` heading, other than a requirement line, naming seams. It MUST then create one sub-ticket `<parent>.1`, ready for its implementer, whose text names every scenario of the approved spec. It MUST log `plan.skipped` with the reason, and report `"planner": "skipped"`. Otherwise it SHALL report `"planner": "needed"` with the reason and write nothing.

#### Scenario: A spec that needs one sub-ticket becomes that sub-ticket without a planner run
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0028-plan.sh <<'EOF'
# Sourced from the repo root, with $1 the STATUS a spec writer run ends with (READY-FOR-CRITIC or
# NEEDS-SPLIT) and $2 one more line for the spec's design part (empty for none). Builds a scratch
# store whose T-0001 has one spec writer run with that status. Its output, a spec with two labelled
# scenarios, becomes spec v1 and is approved, so T-0001 is ready-for-planner. Leaves $B and $T.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
export FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null
$B ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
W=$($B run start --role spec_writer --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
sed 's/^|//' > $T/store/runs/$W/output.md <<EOS
|=== proposal.md
|## Problem
|x
|=== design.md
|## Proposed change
|A. Do x.
|$2
|=== specs/demo/spec.md
|## ADDED Requirements
|### Requirement: X
|It SHALL do x.
|#### Scenario: First check
|- WHEN \`true\`
|- THEN it exits 0
|#### Scenario: Second check
|- WHEN \`true\`
|- THEN it exits 0
|=== verification.md
|## Acceptance
|- First check → NEW; fails today
|- Second check → REGRESSION
|STATUS: $1
|CONFIDENCE: high, fixture
|ESCALATIONS: none
EOS
$B run finish $W >/dev/null && $B spec add T-0001 --from-run $W >/dev/null
$B ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
$B ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
$B approve-spec T-0001 >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B plan whole-spec T-0001 > $T/o 2>&1; echo "exit=$? planner=$(tail -1 $T/o | sed -n 's/.*"planner": "\([a-z]*\)".*/\1/p') subs=$(ls $T/store/tickets | tr '\n' ' ')"; echo "state=$($B ticket show T-0001.1 2>/dev/null | sed -n 's/^status: //p') $($B ticket ready-implementers T-0001 2>/dev/null | tail -1 | grep -o '"ready": \[[^]]*\]') names=$(grep -cxF -e '- First check' -e '- Second check' $T/store/specs/T-0001.1/subticket.md 2>/dev/null) logged=$($B log tail --event plan.skipped --ticket T-0001 | grep -c .)")`
- THEN it prints exactly `exit=0 planner=skipped subs=T-0001.1.yaml T-0001.yaml `, then `state=ready-for-implementer "ready": ["T-0001.1"] names=2 logged=1`

#### Scenario: A spec the writer split, or a parent a planner already ran on, still goes to the planner and nothing is written
Needs the GIVEN block of "A spec that needs one sub-ticket becomes that sub-ticket without a planner run" run once. The three cases are a NEEDS-SPLIT spec, a spec with a `### Size and seams` heading, and a parent with an earlier planner run.
- WHEN `(for c in 'NEEDS-SPLIT|' 'READY-FOR-CRITIC|### Size and seams' 'READY-FOR-CRITIC|planner-ran'; do (s=${c%%|*}; x=${c#*|}; [ "$x" = planner-ran ] && e='' || e=$x; . ${TMPDIR:-/tmp}/t0028-plan.sh $s "$e" && if [ "$x" = planner-ran ]; then P=$($B run start --role planner --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); $B run finish $P --status-override ESCALATE >/dev/null; fi; $B plan whole-spec T-0001 > $T/o 2>&1; echo "exit=$? planner=$(tail -1 $T/o | sed -n 's/.*"planner": "\([a-z]*\)".*/\1/p') subs=$(ls $T/store/tickets | tr '\n' ' ')logged=$($B log tail --event plan.skipped | grep -c .)"); done)`
- THEN it prints exactly `exit=0 planner=needed subs=T-0001.yaml logged=0`, three times

### Requirement: The whole-spec step refuses where a planner run would
`factory plan whole-spec` MUST refuse with exit 2, writing nothing, on a parent that is not at `ready-for-planner`, has a run in flight, or has no approved spec. A refusal for the wrong state SHALL name the state with `not ready-for-planner`.

#### Scenario: The whole-spec step refuses a parent that is not ready for its planner
Needs the GIVEN block of "A spec that needs one sub-ticket becomes that sub-ticket without a planner run" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B ticket transition T-0001 --to planned --by t >/dev/null && $B plan whole-spec T-0001 >/dev/null 2>$T/err; echo "exit=$? named=$(grep -c 'not ready-for-planner' $T/err) subs=$(ls $T/store/tickets | tr '\n' ' ')")`
- THEN it prints exactly `exit=2 named=1 subs=T-0001.yaml `

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

## Your prior findings (round 1)

## Review of T-0033 spec v1 (round 1)

What I checked myself, on `main` at `d226a4d` (`git rev-parse --short HEAD`), with a throwaway `HOME` and `TMPDIR` set to this run's scratch directory:

- Cited paths and lines. `factory/cli.py` `merge_cmd` is lines 645-687 and reads no changed path, no `protected_paths` and no spec. The `--ruling` branch of `resolve` (lines 866-876) sends every ESCALATE whose reason lacks "planner" to `ready-for-critic`. Check 6 of `factory/prompts/reviewer.md`, `docs/prompts/06-code-reviewer.md` and the §6 block of `docs/design.md` ends "the merge gate will require a human approval" at the lines cited. `docs/design.md` lines 21, 23, 47, 48, 105, 109, 139, 154 and 387, `dev/build-harness.spec.md` lines 246 and 377, `factory/prompts/spec_writer.md` line 80 and `factory/workflows/build.js` lines 194-200 hold the text the spec quotes. `factory/workflows/build.js` line 56 exposes a refusal's JSON `error` on the clerk result, so part B's `m.error.startsWith('BLOCKED ')` has something to read, in the same form the run-start check already uses at lines 81-84.
- Acceptance commands. The GIVEN fixture ran as written (41 lines). Merge-gate scenario 1 printed `exit=0 blocked=0 named=0 declared=0 main=moved merged`: today the undeclared `core/b.py` and `bin/tool` merge. Human-resolution scenario 4 printed `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`: the reviewer's escalation ruling goes to the critic with the ESCALATE row still in place. Both match verification.md.
- Git semantics the design relies on. In a scratch repository, `git diff --name-only --no-renames main...H` on a rename lists `core/b.py docs/b.py`; `-- ':(glob)core/**'` lists `core/a.py` and `core/new/c.py`, `':(glob)core/*'` lists only `core/a.py`, and `':(glob)~/.secret/**'` lists nothing and exits 0. A bare directory entry (`core`, `core/`) under glob magic also matches its files, so a declared directory works.
- Rubric 1, tests pinning overturned behaviour. `grep -rn "ESCALATE from reviewer" tests/factory/` finds nothing. `test_resolve_rulings.py` line 98 parametrises only `ESCALATE from critic` and `ESCALATE from planner`. No merge test's branch changes a path the fixture instance (`.factory/instance.yaml`, `.factory/harness.lock`, `.factory/context.md`) or the template protects. "Tests to change: none" holds.
- Evidence figures. The last 20 first-parent merges on `main`, diffed with `--no-renames` against this instance's in-repo globs: `merges=20 protected=18`. The Nanobot tickets named in Operator step 2 are all `awaiting-spec-gate` and T-0021 is `planned` (read from `~/dev/nanobot-upstream/.factory/store/tickets/`, nothing written). This instance's T-0026, T-0027, T-0031 are `ready-for-planner` and T-0030 `planned`, as Risk says. Issue #57 is in `dev/issues.md` line 64. The 2026-10-07 T-0033 line is in `decisions.md`.
- Rulings already reach the checkers: `factory/compose.py` lines 249 and 271 add every `ruling-*.md` to the implementer, reviewer and verifier input, so C.2's "as they already do" is true.

The design is sound and the scenarios discriminate: another ticket's declaration, a rename out of the tree, a "Not touched" line, a `*`-for-`**` matcher and an all-backticks reader each fail a scenario. One finding blocks, on the writing standard.

### Findings

[BLOCKING] 6 proposal.md, first paragraph of Evidence, Decisions and Operator steps
Problem: Each of these sections opens with a term specific to this system that no human-facing section has glossed, so the standard's reader has to infer: Evidence paragraph 1 uses "GIVEN block" and "verifier" (the Problem only ever says "both reviewing agents"); Decisions bullet 1 uses "instance" and "`decisions.md`"; Operator step 1 uses "the runtime", "harness revision" and "the Nanobot instance".
Evidence: Read the Problem, Evidence, Decisions and Operator steps as the operator the rubric describes against `docs/writing.md` rules 2 and 6. "instance" first appears at Decisions bullet 1; "runtime" first appears at Operator step 1; "verifier" first appears at Evidence paragraph 1. None is defined anywhere in those sections. The Problem itself is good: its first paragraph says what is wrong and for whom, and glosses protected paths, the merge gate, the operator, sub-tickets and the Risk section.
Suggested fix: One sentence each, where the term first appears: name the two checking agents in the Problem (the reviewer reads the diff, the verifier runs the tests) and use those names from then on; say an instance is one repository the factory runs on, and `decisions.md` its standing-decision log; say the runtime is the pinned checkout of the harness that each instance has accepted, and that "the Nanobot instance" is the fork at `~/dev/nanobot-upstream`; write "the fixture script this spec gives" instead of "GIVEN block" in Evidence.

[SHOULD-FIX] 6 proposal.md, Problem and Evidence
Problem: Two concepts carry two names each, against rule 9: the Problem says "the main branch", Evidence and Decisions say "the integration branch"; the Problem says "reviewing agents", later text says "reviewer", "verifier", "checkers" and "checks".
Evidence: Problem paragraph 1 ("merged into the main branch") against Evidence bullet 1 ("the integration branch moved") and Decisions bullet 4 ("`<integration>`"). Problem paragraph 1 ("both reviewing agents") against Evidence paragraph 1 ("reviewer and verifier") and Decisions bullet 8 ("The checkers that re-run").
Suggested fix: Pick "integration branch (the branch the factory merges into, `main` here)" at first use and keep it, and name reviewer and verifier once (see the blocking finding) so "checkers" can be dropped or introduced as "the two checkers, reviewer and verifier".

[SHOULD-FIX] 4 proposal.md Decisions bullet 2 and design.md D.2
Problem: A brace list such as `factory/prompts/{preamble,planner}.md` passes the regular expression as one entry, git does not expand it, so the spec writer's habit the Evidence documents would produce a declaration that parks every sub-ticket touching those files, and nothing in the spec-writer FORMAT line or the Decisions says one path or glob per entry.
Evidence: Evidence bullet 5 records T-0022's brace list. The regex in A.1 accepts `` `[^`]+` `` for an entry. The proposed FORMAT line in D.2 shows the shape but gives no rule against brace lists. My scratch check: `:(glob)` matches `*` and `**` only; a brace is literal.
Suggested fix: Add to the FORMAT line's third row, or a fourth, "one path or glob per entry; no brace lists", and one clause in Decisions bullet 2 saying a brace list is one literal entry that matches nothing.

[NIT] 2 specs/merge-gate/spec.md and specs/human-resolution/spec.md
Problem: Three branches in the design have no scenario: the refusal's "(<id> has no approved spec)" wording in A.2 for a ticket with no parent and no approved spec, and the two secondary refusals of `--accept-paths` in C.1 (head not the branch tip; no undeclared path left).
Evidence: The only no-parent merge fixture in current truth (`t0025-gate.sh`) changes `x.txt`, which no instance protects, so the first branch is exercised nowhere; no scenario exercises the other two.
Suggested fix: Leave the acceptance list as it is and let the new test file cover the three in one or two cases, or say in design.md that the new test file covers them.

[NIT] 5 design.md E.1
Problem: After E.1, piece 9 of `docs/design.md` (line 49, "Human surface") still says people "review protected PRs", a per-PR review this change removes.
Evidence: `sed -n 49p docs/design.md`: "Where people approve specs, answer escalations, review protected PRs, reply to requesters, and read the weekly audit sample."
Suggested fix: Add to E.1 a one-line change of that phrase to "answer a merge refused for an undeclared protected path", or leave it and say so.

Out-of-scope observations: `dev/build-harness.spec.md` lines 208 and 314 still list `approve-pr` and `approvals/ID/pr-SHA.yaml`; they stay correct for guardrail paths, which keep their per-PR approval, so nothing to change here. The T-0032 decision line of 2026-10-07 attributes the T-0028.1 by-hand ruling to issue #41's budget-kill and EMPTY-OUTPUT route; this spec, with the ruling file as evidence, shows it was a reviewer ESCALATE misroute. Someone may want to amend that line later.

Prior findings: none (round 1).

STATUS: REVISE
CONFIDENCE: high; every cited line, both reproduced scenarios, the git pathspec behaviour, the 18-of-20 count and the test search were checked on `d226a4d`, and the one blocking finding is a writing-standard gap whose fix is a few sentences.
ESCALATIONS: none

## Previous spec version (v1)

=== proposal.md
## Problem

The factory merges changes to its own protected files without checking that the human ever authorized them. Every repository the factory works on lists some protected paths: files where a change alters something sensitive. In this repository they are the factory's own code, its configuration and its copies of the agent prompts. Before an agent's change is merged into the main branch, a last automated check, the merge gate, confirms that the tests passed and both reviewing agents approved. It never looks at which files the change touches. So a change to a protected file merges whenever the two reviewing agents pass it. This happens even when the spec the operator approved never said the change would touch that file. The operator is the human who approves each spec before any code is written.

The documents promise more than the code does. The design says a protected-path change needs a human approval before it merges. The reviewing agent's instructions say "the merge gate will require a human approval". Neither is true. The gap matters most here, because this is the gate that guards the factory's changes to itself.

The operator has ruled how the gate should work, as a standing rule for every repository the factory runs on. Each spec has a Risk section, which lists the protected paths the change will touch. The operator approves that list at the spec gate, and the approved list is the authorization. At merge, the gate must refuse each changed protected path that the approved spec does not declare. It must name each one and stop the change for a human ruling. A declared path merges with no further approval. Asking for a human approval on every change would have stopped 18 of the last 20 merges here.

A second, smaller fault blocks the human's ruling. An approved spec is built as one or more sub-tickets, each one change of reviewable size. When the reviewing agent on a sub-ticket escalates a question and the human rules on it, the ruling command sends the sub-ticket to the spec critic. That is a step of the spec-writing loop, which never runs for sub-tickets. On 2026-10-05 the operator had to place a ruling file by hand and re-run the checks with a second command.

## Evidence

All commands ran on `main` at `d226a4d`, from `~/dev/spec-factory`, with a throwaway `HOME` and the scratch fixture this spec gives as a GIVEN block (`t0033-gate.sh`). The fixture protects `core/**` and `bin/tool`, and builds one sub-ticket whose reviewer and verifier both passed.

- An undeclared protected path merges. T-0001's approved spec declares only `core/a.py`. The sub-ticket also changes `core/b.py` and `bin/tool`. Merge-gate scenario 1 printed `exit=0 blocked=0 named=0 declared=0 main=moved merged`. The merge succeeded (`exit=0`), and the integration branch moved with both undeclared protected files in it.
- Three more undeclared cases merge. The first is a path that only another ticket's spec declares (T-0002 declares `core/b.py`). The second moves `core/b.py` out of the protected tree. The third has a Risk section whose only mention of `core/b.py` is a "Not touched" line. Scenario 2 printed `exit=0 named=0 main=moved` three times. The second case also shows why the gate must turn off git's rename detection. `git diff --name-only main...$H` lists only `docs/b.py`, so a gate reading it would never see the protected `core/b.py` leave. With `--no-renames` it lists `D core/b.py` and `A docs/b.py`.
- The gate reads no paths. `factory/cli.py` `merge_cmd` (lines 645-687) checks four things: the ticket state, that the recorded head is the branch tip, the three result rows (`ci` PASS, reviewer APPROVE, verifier VERIFIED), and that the head contains the integration branch. No line reads the changed paths, `protected_paths` or a spec.
- The reviewer prompt promises a check that does not exist. Check 6 ends "the merge gate will require a human approval" (`factory/prompts/reviewer.md` lines 24-27, `docs/prompts/06-code-reviewer.md` lines 24-27, `docs/design.md` lines 640-643). The design doc asks for a per-PR approval in four places: line 21 ("a PR touching a protected path" is one of five human gates), line 23 ("A change to either needs a human approval record before it merges"), line 48 (piece 8: "any other guardrail or protected path needs a human approval on the PR itself") and line 154 ("the merge gate does not merge without it"). `dev/build-harness.spec.md` line 246 and item 25 (line 377) specify the same per-PR approval, through an `approve-pr` command that was never built.
- Risk sections today are prose, so the gate needs a fixed form to read. I read the Risk sections of the approved specs T-0013, T-0022, T-0024, T-0028 and T-0029 (`.factory/store/specs/`). Each lists the protected paths it touches. Each also names, in backticks, paths it does not touch. Examples are T-0013's "Not touched: `.factory/**` …" and T-0022's "It does not touch `.factory/**`, `bin/factory` …". A gate that counted every backticked path in Risk would authorize exactly the paths these specs promise to leave alone. T-0022 also uses brace lists (`factory/prompts/{preamble,planner,…}.md`), which git does not expand.
- The cost of a per-PR approval. I checked the last 20 merge commits on `main`'s first-parent line with `git diff --name-only --no-renames <merge>^1 <merge>` against this instance's in-repo protected globs. 18 of the 20 touched a protected path. The operator's answer gives 19 of 20 over its own window.
- The case that exposed the gap. On 2026-10-04 sub-ticket T-0028.1 parked with reason `ESCALATE from reviewer` (`.factory/store/tickets/T-0028.1.yaml`, history). Its reviewer had escalated a 3-line change to `factory/store.py`. The approved spec asks for that change in part A.5, but its Risk list does not name the file. The operator accepted it. The ruling at `.factory/store/approvals/T-0028.1/ruling-1.md` says it was "Placed by hand because `resolve --ruling` routes a sub-ticket's reviewer escalation to the critic". It was followed by `resolve --redispatch`.
- The misroute, reproduced. With the fixture, a reviewer ESCALATE row is recorded, the sub-ticket is parked `ESCALATE from reviewer`, and `resolve --ruling` is run. Human-resolution scenario 4 printed `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`, then `in_input=0`. The sub-ticket went to the spec-critic state. The ESCALATE row stayed, so a re-check would park again. No reviewer run could start to read the ruling. The code is `factory/cli.py` `resolve`, lines 864-875: any ESCALATE whose reason lacks "planner" goes to `ready-for-critic`.
- What the build does today with a merge refusal it does not recognise. Build-dispatch scenario 1 stubs a merge refusal. It printed `park: harness-bug: merge: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`. The workflow asks the join again (`factory/workflows/build.js` lines 195-200). The join answers `merge` again, and the workflow files the refusal as a harness bug.
- No reference fix exists. The request names no Nanobot-side commit.

## Root cause

- `factory/cli.py` `merge_cmd` (645-687) has no path condition. It was written as the local stand-in for the rule-4 checks, and the protected-path part of piece 8 was never ported.
- `factory/prompts/reviewer.md` check 6, its design block and `docs/prompts/` copy describe the per-PR approval of the unbuilt pre-receive design (`dev/build-harness.spec.md` part F), not the local gate.
- The spec writer's format asks for "every protected path this will touch" under Risk but gives no form a program can read (`factory/prompts/spec_writer.md` line 80, `docs/design.md` line 387).
- `factory/cli.py` `resolve`, `--ruling` branch (864-875), knows two ESCALATE routes, planner and critic. It sends every other ESCALATE, the reviewer's included, to the critic.
- `factory/workflows/build.js` lines 195-200 treat every merge refusal other than a conflict as a harness bug.

## Out of scope

- Guardrail paths are unchanged. Existing tests still change only when the pinned spec lists them under "Tests to change" or an earlier sibling added them. The non-test guardrails (agent prompts, AGENTS.md, skills, CI config) keep their documented per-PR approval. The local gate checks neither rule today, and this change does not add them.
- Protected paths outside the repository (`~/dev/nanobot-upstream/**`, `~/.nanobot/**`). A repository diff cannot contain them. The gate skips such patterns.
- A per-head human approval for paths that change the factory's own rules (option 3 of the operator's answer). See Decisions.
- A check at `spec add` or `approve-spec` that the Risk section has a well-formed `Protected paths:` line. That belongs with the spec lint, issue #67.
- The sub-ticket's own `Protected paths:` field, which the planner writes. The gate does not read it, and its format does not change.
- The first two sentences of the reviewer's check 6 (escalate an undeclared path, list a declared one). The implementer and verifier prompts are not changed.
- Rulings on a budget-kill or EMPTY-OUTPUT park. They belong to issue #41's line in `decisions.md`.
- The design's "round reset" route for a max-round cutoff or a SPEC-DEFECT. It stays as written and unbuilt.
- Nothing under `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml` or `uv.lock` changes, and no instance's `protected_paths` changes.

## Open questions

none

## Decisions

- The authorization is the pinned spec's Risk section. For a sub-ticket, that is its parent's approved spec version (`specs/<parent>/v<approved_version>.md`). A ticket with no parent uses its own approved version. A ticket with no approved spec declares nothing. Standing for every instance, from the operator's 2026-10-05 answer, already in `decisions.md` as the 2026-10-07 T-0033 line.
- The gate reads declarations from one fixed line in the Risk section: `Protected paths: none`, or `Protected paths: ` followed by one or more backticked paths or globs, separated by commas. An optional list marker (`- ` or `* `) may come before it, and an optional full stop after it. A Risk line in any other shape declares nothing. Several such lines declare their union. Standing: specs declare protected paths only this way. Rejected: reading every backticked path in Risk. Today's Risk sections put the paths they promise not to touch in backticks too (Evidence), so that reading would authorize them. Rejected: the planner's per-sub-ticket `Protected paths:` field, which an agent writes and no human approves.
- A changed path is "protected" when it matches one of the instance's in-repo `protected_paths` globs. It is "declared" when it matches a declared entry. Both matches use git's glob pathspecs (`:(glob)<pattern>`, so `**` crosses directories and `*` does not). This follows the 2026-10-05 T-0028 decision that the harness never adds a glob matcher of its own. Patterns that start with `~` or `/` are skipped.
- The changed paths are those of `git diff --name-only --no-renames <integration>...<head>`, measured from the merge base. Once the head contains the integration branch, that is exactly what the merge adds. `--no-renames` lists both sides of a move (Evidence). Rejected: the triage's "parent base". After a catch-up run merges the integration branch into the sub-ticket's branch, a diff from the parent's base counts other tickets' merged changes against this one.
- The gate runs this check after the three result rows and before the containment check and the merge lock. A change that will be refused costs no catch-up run.
- A refusal exits 2 and changes no ticket field. It logs one `merge.refused` event with the paths. Its error starts `BLOCKED from merge gate: ` and names each undeclared path, sorted and comma-separated. It names no declared path and uses no backtick, `$` or double quote, because the workflow passes the reason through a shell command.
- The build workflow parks the sub-ticket with that error, verbatim, as the reason. It does the same today for the harness's `BLOCKED from harness:` refusal at run start.
- The human answers that park with one of two commands. `resolve --ruling F` sends the change back. It uses the existing BLOCKED route: the sub-ticket returns to its implementer at the same round, with F in its input. The new `resolve --accept-paths F` accepts the paths under the approved design. It records F as the sub-ticket's next ruling. It adds the undeclared paths, recomputed on the current head, to a ticket field `accepted_paths`, which the gate treats as declared. It returns the sub-ticket to `checks-in-flight` with its result rows kept, so the build merges it on its next pass. Rejected: one acceptance per head. A catch-up run makes a new head, so the same paths would park again. Rejected: amending the pinned spec's Risk section. No command amends a pinned spec yet (T-0027 asks for one). An acceptance adds paths only for that sub-ticket and leaves every other merge condition in force.
- `--accept-paths` refuses, with exit 2 and nothing written, on a park whose reason does not start `BLOCKED from merge gate:`. Its error starts `--accept-paths applies to`. It also refuses when the head is not the branch tip, or when no undeclared protected path remains.
- A ruling on a park whose reason starts `ESCALATE from reviewer` returns the sub-ticket to `checks-in-flight` at the same round. Its rows are set aside as `--redispatch` sets them aside: an APPROVE reviewer row is kept, and a VERIFIED verifier row with a PASS gate row is kept. Every other row moves to `superseded-<n>/`. The checkers that re-run receive the ruling, as they already do. This overturns `docs/design.md` line 109, which sends a reviewer ESCALATE to the implementer with the round reset. Rejected: that route. The 2026-10-05 escalation needed no code change. The re-run reviewer can still REQUEST-CHANGES when a ruling asks for a fix.
- Check 6 of the reviewer prompt keeps its first two sentences and adds "for the record" to the list of declared paths. Its last sentence says what the gate does: it merges a declared path with no further approval, and refuses and parks one the approved spec does not declare.
- No per-head approval is added for paths that change the factory's own rules (option 3 of the operator's answer). The answer leaves it open for this spec gate. Adding it is a gate edit to this spec (a new lettered part) or a later ticket.

## Risk

Protected paths: `factory/cli.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `docs/prompts/02-spec-writer.md`, `docs/prompts/06-code-reviewer.md`

- The paths on the line above are in class harness (`factory/**`) and class generated (`docs/prompts/**`). `factory/gitops.py` is declared in case the implementer puts the diff helper there; it may stay untouched. The two `docs/prompts/` files change only by re-copying their design-doc blocks.
- Guardrail paths: the agent prompts. That is the §2 (spec writer) and §6 (code reviewer) blocks of `docs/design.md` and the four prompt files above. One new test file goes under `tests/factory/`. No existing test changes.
- Unprotected documents changed: `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md`, `README.md`.
- Blast radius: every merge on every instance that accepts the new harness revision, the Nanobot fork included. A gate that is too strict parks good changes. A gate that is too loose lets undeclared ones through. Scenarios in both directions guard it.
- Transition cost. No approved spec has the new `Protected paths:` line yet. On this instance, each sub-ticket that touches a protected path will park once at merge. That covers T-0026, T-0027, T-0030 (planned, sub-tickets in flight) and T-0031. On the Nanobot instance it covers T-0021 (planned). The operator answers each park with `--accept-paths` or `--ruling`. Specs still waiting at their spec gate can be given the line by a gate edit first (Operator steps).
- Shell quoting. The workflow passes the park reason inside double quotes and replaces only `"`. A protected file whose name contains a backtick or `$` would be expanded by the clerk's shell. No such file exists in either repository.
- Overlap. T-0030 (planned) may edit `factory/prompts/reviewer.md` and the §6 block. T-0027 (amend a pinned spec) could later replace `--accept-paths` with a real amendment. Text conflicts are resolved by the usual catch-up run. The changelog scenario finds this entry by its text, not its number.
- This change's own merge runs on the current runtime, which does not check paths. The new check first acts after the runtime upgrade.

## Operator steps

1. After merge, move the runtime and accept the new harness revision on this instance and on the Nanobot instance, as for any harness change. The rule is standing for both.
2. Before that, decide what to do about approved specs without the `Protected paths:` line. Specs still at their spec gate can get the line by a gate edit (`factory approve-spec <T> --edit F`). On the Nanobot instance those are T-0024, T-0027, T-0030, T-0031 and T-0032. For specs already approved, answer each `BLOCKED from merge gate` park with `factory resolve <sub-ticket> --accept-paths F` or `--ruling F`.
3. If you want option 3 (a per-head approval for paths that change the factory's own rules), say so at this gate. It is not part of this spec.

=== design.md
## Proposed change

Run every new command from the repository root. Changes are listed by part. Parts A to C are code; D and E are text. One new test file, for example `tests/factory/test_merge_protected_paths.py`, covers A to C with its own scratch repositories (the Acceptance scenarios show the cases).

A. Merge gate: refuse undeclared protected paths (`factory/cli.py` `merge_cmd`, a helper in `factory/cli.py` or `factory/gitops.py`).
  1. A helper that returns the undeclared protected paths of a ticket at a head:
     - Read the in-repo patterns from `cfg["protected_paths"]`, a mapping of class to a glob or a list of globs (as `instance.fill_preamble` reads it). Skip patterns that start with `~` or `/`. With no in-repo pattern, return an empty list.
     - Run `git diff --name-only --no-renames <integration>...<head> -- ':(glob)<p1>' ':(glob)<p2>' …` in the repository. Its lines are the changed protected paths.
     - Find the pinned spec. For a ticket with a `parent`, it is the parent's `spec.approved_version`; for a ticket with none, the ticket's own. Read `specs/<that id>/v<n>.md` from the store. Missing version or file: no declarations.
     - Take the `## Risk` section: the lines after a line that is exactly `## Risk` (trailing spaces allowed), up to the next line that starts with `## ` or `=== `. Each line that matches the regular expression below declares the backticked entries it holds (`none` declares nothing). Skip entries that start with `~` or `/`.
       ```
       ^\s*(?:[-*]\s+)?Protected paths:\s*(none|`[^`]+`(?:\s*,\s*`[^`]+`)*)\s*\.?\s*$
       ```
     - A changed protected path is declared when it is listed by `git diff --name-only --no-renames <integration>...<head> -- ':(glob)<d1>' …` over the declared entries, or when it is in the ticket's `accepted_paths` list (exact match). Return the rest, sorted.
  2. In `merge_cmd`, after the three-row loop and before `with gitops.MergeLock(repo):`, call the helper. When it returns paths:
     - log `merge.refused` with `ticket`, `head`, `reason: "protected paths not declared"` and `paths`;
     - raise `Refused("BLOCKED from merge gate: protected paths not declared in <spec id> spec v<n>: <p1>, <p2>")`. With no approved spec, use `… not declared (<id> has no approved spec): …`.
     - Change no ticket field. The `{"ok": false, "error": …}` line on stdout and the exit code 2 come from the existing `Refused` handling.
  3. Update `merge_cmd`'s docstring to name the new condition.

B. Build workflow (`factory/workflows/build.js`, the `join.decision === 'merge'` branch, lines 194-200): after `const m = …merge…`, when `!m.ok` and `typeof m.error === 'string' && m.error.startsWith('BLOCKED ')`, `await park(st, m.error, outs, 'Build'); return`, before asking the join again. Nothing else in the script changes.

C. Human resolution (`factory/cli.py` `resolve` and `build_parser`).
  1. New mode `--accept-paths F`, added to the parser (help: "a sub-ticket the merge gate refused for undeclared protected paths: accept them under the approved design and return it to its checks"), to the `--decision` guard's list of modes that block `--close`, and to the "resolve needs one of" message. Behaviour, in order, nothing written before the last refusal:
     - refuse unless `st == "parked"` and `reason.startswith("BLOCKED from merge gate:")`. The error is `--accept-paths applies to a merge gate park (BLOCKED from merge gate); <id> is <st> (<reason or 'no park'>)`;
     - refuse when the ticket's `head` is not the tip of its `branch`, with merge's wording;
     - compute the helper of A.1 on the head, and refuse with `nothing to accept: <id> has no undeclared protected path at <head[:9]>` when it is empty;
     - copy F to `approvals/<id>/ruling-<n>.md`. Set `t["accepted_paths"]` to the sorted union of the old list and the computed paths. Call `move("checks-in-flight", "accept-paths", {"ruling": <rel>, "head": head, "accepted": paths})`. No result row moves.
  2. In the `--ruling` branch, before the planner/critic choice: a reason that starts with `ESCALATE from reviewer` returns the ticket to `checks-in-flight`. First set aside the head's rows with the same rule `--redispatch` uses. Move that block into a small function both branches call, with no change to `--redispatch`'s behaviour. Log `results.superseded`. Then write the ruling file and `move("checks-in-flight", "ruling", {"ruling": …, "head": head, "superseded": moved})`.
  3. A park reason that starts with `BLOCKED from merge gate:` already takes the BLOCKED branch of `--ruling` (`ready-for-implementer`, same round). No code change is needed; the new test covers it.

D. Prompts. Edit each design block and re-copy it to its `docs/prompts/` file byte for byte. Apply the same text change to the run copy under `factory/prompts/`, keeping that copy's existing fills.
  1. Code reviewer (`docs/design.md` "## 6. Code reviewer" block, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`). Check 6 becomes exactly:
     ```
     6. Protected paths touched? If the sub-ticket does not declare them,
        ESCALATE. If it does, list them under ESCALATIONS for the record,
        finish the review, and give the STATUS the code earns. The merge
        gate merges a path the approved spec's Risk section declares with no
        further approval, and refuses and parks one it does not declare.
     ```
  2. Spec writer (`docs/design.md` "## 2. Spec writer" block, `docs/prompts/02-spec-writer.md`, `factory/prompts/spec_writer.md`). The `## Risk` line of FORMAT becomes these three lines:
     ```
     ## Risk             blast radius; every protected path this will touch,
                         declared on one line the merge gate reads:
                         Protected paths: none | `<path or glob>`, `<path or glob>`
     ```

E. Documents.
  1. `docs/design.md`, outside the prompt blocks:
     - line 21: "a PR touching a protected path" becomes "a merge refused for a protected path the approved spec does not declare".
     - line 23: "A change to either needs a human approval record before it merges." becomes "A change to a guardrail path needs a human approval record before it merges. A change to a protected path merges when the approved spec's Risk section declares it: the human approves that declaration at the spec gate, and the merge gate refuses a protected path the spec does not declare."
     - line 47 (piece 7): "and a human approval record where piece 8 requires it" becomes "every changed protected path declared (piece 8), and a human approval record where piece 8 requires one".
     - line 48 (piece 8): the first sentence becomes "If the diff touches a protected path, the merge gate requires the pinned spec's Risk section to declare it on its `Protected paths:` line, or a human to have accepted that path for the sub-ticket after the gate refused it (`resolve --accept-paths`); the spec gate's approval is the authorization, and there is no per-PR approval. If the diff touches a guardrail path, the merge gate requires an approval row signed by a human identity." "any other guardrail or protected path needs a human approval on the PR itself" becomes "any other guardrail path needs a human approval on the PR itself". In the GitHub column, "skills, prompts, and protected paths" becomes "skills and prompts; protected paths get a required check that fails on a changed protected path the pinned spec does not declare".
     - resolution rules: after the line-105 bullet, add "  - A merge the gate refused for an undeclared protected path parks as BLOCKED. A ruling returns the sub-ticket to its implementer, same round. `resolve --accept-paths` instead adds the named paths to what that sub-ticket may change and returns it to its checks, whose passing results stand; every other merge condition still applies." In the line-109 bullet, "A PR loop at max rounds, a SPEC-DEFECT, or a reviewer ESCALATE returns" becomes "A PR loop at max rounds or a SPEC-DEFECT returns". Before that bullet, add "  - A reviewer ESCALATE returns to its checks with the ruling in both checkers' input, same round. Its results that did not pass are set aside, so the reviewer runs again; a ruling that asks for a fix becomes the reviewer's REQUEST-CHANGES."
     - line 139 (Merge gate row): "+ piece-8 approvals" becomes "+ piece-8 checks".
     - line 154 becomes:
       ```
       | Protected paths | A merge the gate refused because a changed protected path is not declared in the pinned spec's Risk section | Accepts the paths under the approved design (`resolve --accept-paths`), which returns the sub-ticket to its checks, or sends it back to its implementer with a ruling (`resolve --ruling`) |
       ```
  2. `dev/build-harness.spec.md`:
     - line 246: the piece-8 bullet's "protected glob or **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`protected path <p> needs human approval on H` / `guardrail path <p> needs human approval on H`)" becomes "in-repo protected glob → declared on the `Protected paths:` line of the pinned spec's Risk section, or in the sub-ticket's `accepted_paths` (`protected path <p> not declared in the pinned spec v<N>`); **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`guardrail path <p> needs human approval on H`)".
     - item 25 becomes "25. As 22 plus `pyproject.toml` changed, not declared → exit 2, `protected path pyproject.toml not declared in the pinned spec v1`; with `pyproject.toml` on the pinned spec's `Protected paths:` line → exit 0, no approval row [NEW]".
  3. `docs/changelog.md`: one new numbered entry, after the last one, starting "After issue #57 (2026-10-05), ". It records these points. The merge gate merged protected-path changes without reading any declaration, while the reviewer prompt promised a human approval. The approved spec's Risk section is now the authorization, read from its `Protected paths:` line. The gate refuses an undeclared protected path with `BLOCKED from merge gate`, and the build parks it. `--accept-paths` and `--ruling` resolve that park. A reviewer ESCALATE ruling returns to the checks. The prompt and design lines changed. Numbering stays contiguous.
  4. `README.md`:
     - the "merge gate" row of "Terms used on this page" adds that every protected path the change touches is declared in the approved spec;
     - the "Merges, one at a time." bullet adds the condition "every protected path the change touches is declared on the `Protected paths:` line of the approved spec's Risk section, or a human accepted it for this sub-ticket";
     - a new **Built** bullet, `- **Protected paths at merge.**`, says what the gate refuses, that the sub-ticket parks as blocked, the two ways to answer, and that it is tested and has not yet fired on a real ticket;
     - the **Unstick** row adds `--accept-paths F` (the merge gate refused a protected path the approved spec does not declare: accept it under the approved design; `--ruling F` sends the sub-ticket back instead) and says that a ruling on a reviewer's escalation re-runs the checks;
     - the status date moves to the merge date.

Size: about 120 changed lines of code and text in A to E and about 180 lines of new tests. That fits one PR.

## Tests to change

none. No existing test pins the old behaviour. I searched `tests/factory/` for `ESCALATE from reviewer` (no hits) and for `--ruling` (only `test_resolve_rulings.py`, `test_decision_log.py`, `test_sibling_tests.py`; their critic, planner and BLOCKED routes and their refusal text are unchanged). I also checked the five files that call `merge` (`test_shepherd.py`, `test_parent_close_reuse.py`, `test_sibling_tests.py`, `test_store_branch.py`, and the gate fixture of current truth). Their branches change only files outside the fixture instance's protected paths (`.factory/instance.yaml`, `.factory/harness.lock`, `.factory/context.md`). `test_writing_standard.py` and `test_coding_standard.py` compare the §6 and §2 blocks with their `docs/prompts/` copies, and still pass when both are re-copied.

=== specs/merge-gate/spec.md
## ADDED Requirements

### Requirement: The merge gate refuses a changed protected path the pinned spec does not declare
`factory merge` MUST refuse with exit 2, merging nothing and changing no ticket field, when a path in `git diff --name-only --no-renames <integration>...<head>` matches an in-repo `protected_paths` glob and is neither declared on a `Protected paths:` line of the Risk section of the pinned spec nor in the ticket's `accepted_paths`. Its error SHALL start `BLOCKED from merge gate: ` and name each such path and no declared one. A declaration in another ticket's spec, or a Risk line in any other form, SHALL declare nothing.

#### Scenario: An undeclared protected path is refused at merge, by name, and nothing merges
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0033-gate.sh <<'EOF'
# Sourced from the repo root, with $1 the line T-0001's approved spec carries in its Risk section
# (each ^ in it stands for a backtick) and $2 the changes the sub-ticket's one commit makes,
# space-separated: `p` appends to file p (creating it), `p-` deletes p, `p>q` renames p to q.
# Builds a scratch instance whose protected paths are `core/**`, `bin/tool` and `~/.secret/**`,
# and a target whose main holds core/a.py, core/b.py, bin/tool and docs/d.md. T-0002's approved
# spec declares `core/b.py`. T-0001 is planned as T-0001.1, whose branch factory/T-0001.1 holds
# that one commit, head $H, with reviewer APPROVE, verifier VERIFIED and gate PASS recorded on $H;
# T-0001.1 is at checks-in-flight. Leaves $B, $T, $H and $M (main's tip).
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
mkdir $T/inst && cp tests/factory/fixtures/instance/context.md $T/inst/
grep -v '^protected_paths:\|^  infra:' tests/factory/fixtures/instance/instance.yaml > $T/inst/instance.yaml
printf '%s\n' 'protected_paths:' '  harness: ["core/**", "bin/tool"]' '  credentials: ["~/.secret/**"]' >> $T/inst/instance.yaml
export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t config user.email f@x && git -C $T/t config user.name f
mkdir -p $T/t/core $T/t/bin $T/t/docs && for f in core/a.py core/b.py bin/tool docs/d.md; do echo x > $T/t/$f; done
git -C $T/t add -A && git -C $T/t commit -q -m init
for id in T-0001 T-0002; do
  [ $id = T-0001 ] && L=$(printf '%s' "$1" | tr '^' '\140') || L='Protected paths: `core/b.py`'
  printf "# F $id\n\nDo x.\n" > $T/req.md
  printf '=== proposal.md\n## Problem\nx\n## Risk\nBlast radius: small.\n%s\n=== design.md\n## Proposed change\nA. x\n' "$L" > $T/spec.md
  $B ticket new --file $T/req.md >/dev/null
  $B ticket transition $id --to ready-for-spec-writer --by t >/dev/null && $B spec add $id --file $T/spec.md >/dev/null
  $B ticket transition $id --to ready-for-critic --by t --round spec:init >/dev/null
  $B ticket transition $id --to awaiting-spec-gate --by t >/dev/null && $B approve-spec $id >/dev/null
done
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && $B subticket add T-0001 --file $T/plan.md >/dev/null
$B ticket transition T-0001 --to planned --by t >/dev/null
git -C $T/t checkout -q -b factory/T-0001.1
for f in $(echo "$2"); do
  case $f in
    *'>'*) mkdir -p $T/t/$(dirname ${f#*>}) && git -C $T/t mv ${f%%>*} ${f#*>} ;;
    *-) git -C $T/t rm -q ${f%-} ;;
    *) mkdir -p $T/t/$(dirname $f) && echo y >> $T/t/$f && git -C $T/t add $f ;;
  esac
done
git -C $T/t commit -q -m work && H=$(git -C $T/t rev-parse HEAD) && git -C $T/t checkout -q main && M=$(git -C $T/t rev-parse main)
$B ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/r.md
$B results record T-0001.1 --head $H --role verifier --output $T/v.md --run run-0001-verifier >/dev/null
$B results record T-0001.1 --head $H --role reviewer --output $T/r.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py bin/tool docs/d.md' && $B merge T-0001.1 >$T/o 2>/dev/null; x=$?; J=$(tail -1 $T/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from merge gate: ') named=$(echo "$J" | grep -o 'core/b\.py\|bin/tool' | sort -u | grep -c .) declared=$(echo "$J" | grep -c 'core/a\.py\|docs/d\.md') main=$([ "$(git -C $T/t rev-parse main)" = "$M" ] && echo unchanged || echo moved) $($B ticket show T-0001.1 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=2 blocked=1 named=2 declared=0 main=unchanged checks-in-flight`. `named=2`: the error names both undeclared protected paths. `declared=0`: it names neither the declared protected path nor the unprotected one.

#### Scenario: Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The three cases: T-0001 declares nothing while T-0002 declares `core/b.py`; the sub-ticket renames `core/b.py` out of the protected tree; T-0001's only mention of `core/b.py` is a line `Not touched: ` followed by it.
- WHEN `(for c in 'Protected paths: none|core/b.py' 'Protected paths: none|core/b.py>docs/b.py' 'Not touched: ^core/b.py^|core/b.py'; do (. ${TMPDIR:-/tmp}/t0033-gate.sh "${c%%|*}" "${c#*|}" && $B merge T-0001.1 >$T/o 2>/dev/null; x=$?; echo "exit=$x named=$(tail -1 $T/o | grep -c 'core/b\.py') main=$([ "$(git -C $T/t rev-parse main)" = "$M" ] && echo unchanged || echo moved)"); done)`
- THEN it prints three lines, each exactly `exit=2 named=1 main=unchanged`

### Requirement: A declared or unprotected path merges with no further approval
`factory merge` SHALL merge, as before, a sub-ticket whose changed protected paths are all declared on its pinned spec's `Protected paths:` line, by exact path or glob, and one that changes no protected path.

#### Scenario: A declared protected path, or an unprotected one, merges with no further approval
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(for c in 'Protected paths: ^core/**^, ^bin/tool^|core/a.py core/new/c.py bin/tool' 'Protected paths: none|docs/d.md docs/e.md'; do (. ${TMPDIR:-/tmp}/t0033-gate.sh "${c%%|*}" "${c#*|}" && $B merge T-0001.1 >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p')"); done)`
- THEN it prints exactly `exit=0 merged`, twice

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: The build parks a merge the gate blocked, with the gate's reason
When `factory merge` is refused with an error that starts `BLOCKED `, `factory/workflows/build.js` MUST park the sub-ticket with that error, verbatim, as the reason, and SHALL NOT record it as a harness bug.

#### Scenario: The build parks a merge refused for protected paths with the gate's reason
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "ticket join": {"out": {"ok": true, "decision": "merge", "reason": "ci PASS + APPROVE + VERIFIED on the current head"}}, "merge": {"out": {"ok": false, "error": "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"}, "exit": 2}}')`
- THEN it prints exactly `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`

=== specs/human-resolution/spec.md
## ADDED Requirements

### Requirement: Accepting the refused paths returns the sub-ticket to its checks, which then merge
`factory resolve <id> --accept-paths F`, on a park whose reason starts `BLOCKED from merge gate:`, MUST write F as the ticket's next ruling, add the head's undeclared protected paths to the ticket's `accepted_paths`, keep every result row, and return the ticket to `checks-in-flight`; `factory merge` SHALL then merge it. On any other park it MUST refuse with exit 2, writing nothing, with an error containing `--accept-paths applies to`.

#### Scenario: Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The scenario parks the sub-ticket with the gate's own error, as the build does.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: core/b.py is part of the approved design.\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>&1; echo "accept=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') rows=$(ls $FACTORY_STATE/results/$H | grep -c yaml) ruling=$(cmp -s $T/ru.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo kept || echo missing)"; $B merge T-0001.1 >/dev/null 2>&1; echo "merge=$? on_main=$(git -C $T/t diff --name-only $M main | grep -c 'core/b\.py')")`
- THEN it prints exactly `accept=0 checks-in-flight rows=3 ruling=kept`, then `merge=0 on_main=1`

#### Scenario: Accepting paths is refused on any other park and writes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: x\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>$T/err; echo "accept=$? refused=$(grep -c 'accept-paths applies to' $T/err) $($B ticket show T-0001.1 | sed -n 's/^status: //p') rulings=$(ls $FACTORY_STATE/approvals/T-0001.1 2>/dev/null | grep -c ruling)")`
- THEN it prints exactly `accept=2 refused=1 parked rulings=0`

### Requirement: A ruling on a merge gate's refusal sends the sub-ticket back to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts `BLOCKED from merge gate:` SHALL return the sub-ticket to `ready-for-implementer` at the same round, and the next implementer input SHALL contain F.

#### Scenario: A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: take core/b.py out of this change.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "ruling=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') reason=$(echo "$E" | grep -c '^BLOCKED from merge gate: ')"; R=$($B run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take core/b.py out of this change.')")`
- THEN it prints exactly `ruling=0 ready-for-implementer reason=1`, then `in_input=1`

### Requirement: A ruling on a reviewer's escalation returns the sub-ticket to its checks
`factory resolve <id> --ruling F` on a park whose reason starts `ESCALATE from reviewer` MUST write F as the ticket's next ruling and return the ticket to `checks-in-flight` at the same round. It MUST set aside the head's rows that did not pass, by the rule `--redispatch` uses, and the next reviewer input SHALL contain F.

#### Scenario: A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'docs/d.md' && printf "Commit: $H\nSTATUS: ESCALATE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/e.md && $B results record T-0001.1 --head $H --role reviewer --output $T/e.md --run run-0003-reviewer >/dev/null && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: the escalation is settled.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')"; R=$($B run start --role reviewer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: the escalation is settled.')")`
- THEN it prints exactly `exit=0 checks-in-flight kept: ci.yaml verifier.yaml ` (the reviewer's ESCALATE row set aside, the passing verifier and gate rows kept), then `in_input=1`

=== specs/role-escalations/spec.md
## MODIFIED Requirements

### Requirement: Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
The system prompts of implementer, code reviewer and verifier runs MUST still carry the preamble's rule to escalate a protected path that the approved spec's Risk section does not declare. The code reviewer's prompt MUST still carry check 6's rule to ESCALATE a path the sub-ticket does not declare and to list a declared one under ESCALATIONS. Check 6 SHALL say that the merge gate merges a path the approved spec's Risk section declares with no further approval, and SHALL NOT promise a human approval at merge.

#### Scenario: All three run prompts keep the undeclared-path rule and the reviewer keeps check 6
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && u="a protected path the approved spec's Risk section does not declare"; for r in implementer reviewer verifier; do echo "$r undeclared=$(prompt $r | grep -cF "$u")"; done; echo "check6=$(prompt reviewer | grep -cF '6. Protected paths touched? If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS')")`
- THEN it prints exactly `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1`, one per line

#### Scenario: The reviewer run prompt says what the merge gate checks
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && P=$(prompt reviewer); echo "gate=$(echo "$P" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval") promise=$(echo "$P" | grep -c 'will require a human approval')")`
- THEN it prints exactly `gate=1 promise=0`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The prompts tell the reviewer what the gate checks and the spec writer how to declare
Every copy of the code reviewer prompt (the `docs/design.md` §6 block, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`) SHALL carry check 6's new last sentence and MUST NOT say `will require a human approval`. Every copy of the spec writer prompt SHALL give the `Protected paths:` line under Risk. Each design block and its `docs/prompts/` file MUST stay byte-identical, and each `factory/prompts/` copy SHALL differ from its `docs/prompts/` file only where it did on `main`.

#### Scenario: Every reviewer prompt copy states what the merge gate checks
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "gate=$(echo "$J" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval, and refuses and parks one it does not declare") promise=$(echo "$J" | grep -c 'will require a human approval')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `gate=1 promise=0`, then `copy=SAME fill=unchanged`

#### Scenario: Every spec writer prompt copy gives the declaration line
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-sw.txt; T=$(mktemp -d); sed -n '/^## 2\. Spec writer/,/^## 3\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; do echo "reads=$(grep -c 'declared on one line the merge gate reads:$' $f) form=$(grep -c '^ *Protected paths: none | .<path or glob>., .<path or glob>.$' $f)"; done; git show main:factory/prompts/spec_writer.md > $T/a; git show main:docs/prompts/02-spec-writer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/02-spec-writer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/spec_writer.md docs/prompts/02-spec-writer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `reads=1 form=1`, then `copy=SAME fill=unchanged`

### Requirement: The documents record the protected-path rule at merge
`docs/design.md` SHALL drop the per-PR approval for protected paths, describe the declared-path rule in piece 8 and the Protected paths gate row, and route a reviewer ESCALATE back to its checks; `dev/build-harness.spec.md` SHALL describe the same rule; `docs/changelog.md` SHALL gain an entry for issue #57 and stay numbered without a gap; `README.md` SHALL describe the check and `--accept-paths`; and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec drop the per-PR approval for protected paths
- WHEN `(echo "gates=$(grep -c 'a PR touching a protected path, the daily escalation queue' docs/design.md) either=$(grep -c 'A change to either needs a human approval record before it merges' docs/design.md) onpr=$(grep -c 'any other guardrail or protected path needs a human approval on the PR itself' docs/design.md) piece8=$(grep '^| 8 |' docs/design.md | grep -c 'Protected paths:') gaterow=$(grep '^| Protected paths |' docs/design.md | grep -c -- '--accept-paths') stale=$(grep -c 'records the piece-8 approval; the merge gate does not merge without it' docs/design.md) reviewer_rule=$(grep -c '^  - A reviewer ESCALATE returns to its checks' docs/design.md) old_route=$(grep -c 'or a reviewer ESCALATE returns to the implementer' docs/design.md) build=$(grep -c 'protected path pyproject.toml needs human approval on H' dev/build-harness.spec.md) build_new=$(grep '^25\. ' dev/build-harness.spec.md | grep -c 'not declared')")`
- THEN it prints exactly `gates=0 either=0 onpr=0 piece8=1 gaterow=1 stale=0 reviewer_rule=1 old_route=0 build=0 build_new=1`

#### Scenario: The changelog records issue 57's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #57 ' docs/changelog.md | grep -oF -e 'Risk' -e '--accept-paths' -e 'BLOCKED from merge gate' -e 'checks' -e 'Protected paths:' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the protected-path check and the new resolve verb
- WHEN `(echo "built=$(grep -c '^- \*\*Protected paths at merge\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--accept-paths') merges=$(sed -n '/^- \*\*Merges, one at a time\.\*\*/,/^- \*\*Setting up the store\.\*\*/p' README.md | grep -c 'Risk section' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `built=1 unstick=1 merges=1`

#### Scenario: The protected-path change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Each NEW item's failure today was observed on `main` at `d226a4d` with a throwaway `HOME`, running the WHEN as written.

- An undeclared protected path is refused at merge, by name, and nothing merges → NEW. Today it prints `exit=0 blocked=0 named=0 declared=0 main=moved merged`: the merge goes through with `core/b.py` and `bin/tool` undeclared.
- Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing → NEW. Today it prints `exit=0 named=0 main=moved` three times.
- A declared protected path, or an unprotected one, merges with no further approval → REGRESSION. It prints `exit=0 merged` twice today. It guards against a gate that refuses too much, or that chokes on the out-of-repo `~/.secret/**` pattern.
- The build parks a merge refused for protected paths with the gate's reason → NEW. Today it prints `park: harness-bug: merge: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`.
- Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through → NEW. Today it prints `accept=2 parked rows=3 ruling=missing`, then `merge=2 on_main=1`. The first merge already went through, and `--accept-paths` is an unknown argument.
- Accepting paths is refused on any other park and writes nothing → NEW. Today it prints `accept=2 refused=0 parked rulings=0`. Argparse refuses the unknown flag, with no `--accept-paths applies to` text.
- A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling → NEW. Today it prints `ruling=2 parked reason=0`, then `in_input=0`. The merge went through, so the park reason is empty and `--ruling` refuses it.
- A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling → NEW. Today it prints `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`, then `in_input=0`.
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 → REGRESSION. It prints the expected four lines today.
- The reviewer run prompt says what the merge gate checks → NEW. Today it prints `gate=0 promise=1`.
- Every reviewer prompt copy states what the merge gate checks → NEW. Today it prints `gate=0 promise=1` three times, then `copy=SAME fill=unchanged`.
- Every spec writer prompt copy gives the declaration line → NEW. Today it prints `reads=0 form=0` three times, then `copy=SAME fill=unchanged`.
- The design doc and build spec drop the per-PR approval for protected paths → NEW. Today it prints `gates=1 either=1 onpr=1 piece8=0 gaterow=0 stale=1 reviewer_rule=0 old_route=1 build=1 build_new=0`.
- The changelog records issue 57's change without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `0`.
- README describes the protected-path check and the new resolve verb → NEW. Today it prints `built=0 unstick=0 merges=0`.
- The protected-path change adds no whitespace errors → REGRESSION.
