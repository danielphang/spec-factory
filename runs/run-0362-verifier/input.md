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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0362-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0362-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0362-verifier/wt` (branch `factory/T-0033.1`, base `2f7f75f3961d2bd20b2fb106bd587ff94dd7621f`, head `ba3fea8154f74ccd5007fd25d18f8215e0b7f000`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0033.1

T-0033.1 / Merge gate merges protected-path changes the approved spec never declared, and the reviewer prompt promises a check the gate does not run
Depends on: none
Parallel-safe: yes

Parent: T-0033, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- An undeclared protected path is refused at merge, by name, and nothing merges
- Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing
- A declared protected path, or an unprotected one, merges with no further approval
- The build parks a merge refused for protected paths with the gate's reason
- Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through
- Accepting paths is refused on any other park and writes nothing
- A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling
- A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6
- The reviewer run prompt says what the merge gate checks
- Every reviewer prompt copy states what the merge gate checks
- Every spec writer prompt copy gives the declaration line
- The design doc and build spec drop the per-PR approval for protected paths
- The changelog records issue 57's change without a numbering gap
- README describes the protected-path check and the new resolve verb
- The protected-path change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0033/v2.md`

=== proposal.md
## Problem

The factory merges changes to its own protected files without checking that a human ever authorized them. The factory is a chain of AI agents that turns a written request into merged code. Each repository it runs on (an instance) lists some protected paths: files where a change alters something sensitive. In this repository they are the factory's own code (the harness), its configuration and its copies of the agent prompts. A human, the operator, approves each spec at the spec gate before any code is written. The spec is then built as one or more sub-tickets, each one change of reviewable size. Before a sub-ticket's change merges, two agents check it: the reviewer reads the diff, and the verifier runs the test suite and the spec's acceptance commands. The merge gate is the last automated check before the change is merged into the integration branch (the branch the factory merges into, `main` here). It confirms that the reviewer approved and the verifier passed, but it never looks at which files the change touches. So a change to a protected file merges whenever the reviewer and verifier pass it, even when the approved spec never said the change would touch that file.

The documents promise more than the code does. The design says a protected-path change needs a human approval before it merges. The reviewer's instructions say "the merge gate will require a human approval". Neither is true. The gap matters most here, because this is the gate that guards the factory's changes to itself.

The operator has ruled how the gate should work, as a standing rule for every instance. Each spec has a Risk section, which lists the protected paths the change will touch. The operator approves that list at the spec gate, and the approved list is the authorization. At merge, the gate must refuse each changed protected path that the approved spec does not declare. It must name each one and park the sub-ticket: stop it until a human gives a ruling, a written answer that the next agent reads. A declared path merges with no further approval. Asking for a human approval on every change would have stopped 18 of the last 20 merges here.

A second, smaller fault blocks the human's ruling. When the reviewer on a sub-ticket escalates a question to a human and the human rules on it, the ruling command sends the sub-ticket to the spec critic. The critic is a step of the spec-writing loop, which never runs for sub-tickets. On 2026-10-05 the operator had to place a ruling file by hand and re-run the reviewer and verifier with a second command.

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

## PR description (the implementer's output)

Sub-ticket: T-0033.1, "Merge gate merges protected-path changes the approved spec never declared, and the reviewer prompt promises a check the gate does not run". Parent T-0033, approved spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0033/v2.md`).
Branch: `factory/T-0033.1`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0033.1`
Commit: `ba3fea8154f74ccd5007fd25d18f8215e0b7f000` (one commit on base `2f7f75f3961d2bd20b2fb106bd587ff94dd7621f`)

## What changed

Before this change, the merge gate merged any change to a protected path once the reviewer and verifier passed it. A protected path is a file the instance (one repository the factory runs on) lists in `instance.yaml` as sensitive; here, that is the harness's own code and the prompt copies. Now the gate refuses each changed protected path that the approved spec does not declare. The human answers the refusal with one of two new or rerouted commands. The reviewer and spec writer prompts and the documents now say what the gate actually does.

**A. Merge gate** (`factory/cli.py`, `factory/gitops.py`)
- `gitops.changed_files(repo, base, head, globs)` lists the paths `base...head` changes that match git glob pathspecs (`:(glob)<p>`, with `--no-renames`). It existed with no caller anywhere in the repo (grep of the whole tree: only its definition). I extended it in place rather than adding a second diff helper.
- `cli.declared_paths(spec_text)` reads the `Protected paths:` lines of the `## Risk` section with the spec's regular expression. It uses `specstore.lines_outside_fences`, so a line in a fenced block declares nothing and does not end the section. Entries starting `~` or `/` are skipped.
- `cli.undeclared_protected(root, cfg, t, head)` returns the sorted undeclared paths and where it read the declarations. The pinned spec is the parent's approved version, or the ticket's own when it has no parent. A path in the ticket's `accepted_paths` counts as declared.
- `merge_cmd` calls it after the three result checks and before the merge lock. A refusal logs `merge.refused` with `paths`, changes no ticket field and raises `BLOCKED from merge gate: protected paths not declared in <id> spec v<n>: <p1>, <p2>`. With no approved spec, the error reads `... not declared (<id> has no approved spec): ...`. The docstring names the new condition.
- `_branch_tip(repo, t)` is the existing "head is the branch tip" check, moved out of `merge_cmd` so that `--accept-paths` refuses with the same wording.

**B. Build workflow** (`factory/workflows/build.js`): when `merge` is refused with an error starting `BLOCKED `, the build parks the sub-ticket with that error, verbatim. Before, it recorded the refusal as a harness bug. That is one `if` line plus a comment.

**C. Human resolution** (`factory/cli.py` `resolve`, `build_parser`)
- New `resolve --accept-paths F`. It is added to the parser with the spec's help text, to the `--decision` guard and to the "resolve needs one of" message. Its refusals run in this order, and nothing is written until all of them pass:
  1. The park reason must start `BLOCKED from merge gate:`.
  2. The head must be the tip of its branch.
  3. At least one undeclared protected path must remain (`nothing to accept: ...`).

  It then writes F as the next `ruling-<n>.md` and sets `accepted_paths` to the sorted union. It moves the ticket to `checks-in-flight` (the state in which the reviewer and verifier judge it), and no result row moves.
- In `--ruling`, a park reason starting `ESCALATE from reviewer` now returns the ticket to `checks-in-flight` at the same round. Before, it went to `ready-for-critic`. Results that did not pass are set aside first. The set-aside block came out of `--redispatch` into `_set_aside_failed_rows(root, t)`, which both branches call; `--redispatch` behaves as before. The move records `head` and `superseded`.
- A `BLOCKED from merge gate:` park already took the BLOCKED branch of `--ruling`, which goes to `ready-for-implementer` at the same round. The code is unchanged there except its comment; a new test covers the route.

**D. Prompts.** In `docs/design.md`, the §6 check 6 block now carries the spec's exact text. The §2 `## Risk` FORMAT line now carries the four lines from the spec. Both blocks were re-copied to `docs/prompts/06-code-reviewer.md` and `docs/prompts/02-spec-writer.md`, and the same text change was made to `factory/prompts/reviewer.md` and `factory/prompts/spec_writer.md`. Scenarios 11 and 12 check that each block and its copy are byte-identical (`copy=SAME`) and that the run copies keep their fills (`fill=unchanged`).

**E. Documents**
- `docs/design.md`: the line-21, line-23, piece 7, piece 8 (both columns), piece 9, resolution-rule, merge-gate-row and Protected-paths gate-row edits, as specified. In this file they sit 2 lines lower than the spec's numbers, because `main` moved; each was matched by its text.
- `dev/build-harness.spec.md`: the piece-8 bullet (line 246) and item 25.
- `docs/changelog.md`: new entry 63, "After issue #57 (2026-10-05), ...". Numbering stays contiguous.
- `README.md`:
  - The merge-gate row of the terms table now says the gate checks declared protected paths, and glosses "protected path".
  - The "Merges, one at a time." bullet gains the new condition and a sentence saying a refusal parks the sub-ticket.
  - A new **Protected paths at merge.** bullet sits under Built.
  - The Unstick row gains `--accept-paths F` and the reviewer-escalation route.

Callers of the existing functions this change touches (coding standard rule 2, found by grep):
- `merge_cmd` is reached only through `bin/factory merge`, from `build.js` and the tests.
- `resolve` is reached only through `bin/factory resolve`.
- `gitops.changed_files` had no caller.
- The redispatch block's only caller was `--redispatch`; `test_redispatch_rows.py` and the human-resolution redispatch scenarios still pass.

## Acceptance results

I ran every scenario as written, from the worktree root, in the HOME wrapper, with `TMPDIR` set to this run's scratch directory. The GIVEN blocks are the spec's `t0033-gate.sh`, the current-truth `t0023-wf.mjs` from human-resolution and `t0029-prompt.sh` from role-escalations. I extracted them, and each WHEN line, from the spec files with a script, so no command was retyped. The "before" run was on base `2f7f75f` with `uv sync --frozen` done; the "after" run was on `ba3fea8`. Full logs: `.../run-0361-implementer/scratch/before.txt` and `after.txt`.

| # | Scenario | Label | Before (base) | After (`ba3fea8`) |
|---|---|---|---|---|
| 1 | An undeclared protected path is refused at merge, by name, and nothing merges | NEW | `exit=0 blocked=0 named=0 declared=0 main=moved merged` | `exit=2 blocked=1 named=2 declared=0 main=unchanged checks-in-flight` |
| 2 | Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing | NEW | `exit=0 named=0 main=moved` ×3 | `exit=2 named=1 main=unchanged` ×3 |
| 3 | A declared protected path, or an unprotected one, merges with no further approval | REGRESSION | `exit=0 merged` ×2 | `exit=0 merged` ×2 |
| 4 | The build parks a merge refused for protected paths with the gate's reason | NEW | `park: harness-bug: merge: BLOCKED from merge gate: ...core/b.py` | `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py` |
| 5 | Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through | NEW | `accept=2 parked rows=3 ruling=missing` / `merge=2 on_main=1` | `accept=0 checks-in-flight rows=3 ruling=kept` / `merge=0 on_main=1` |
| 6 | Accepting paths is refused on any other park and writes nothing | NEW | `accept=2 refused=0 parked rulings=0` | `accept=2 refused=1 parked rulings=0` |
| 7 | A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling | NEW | `ruling=2 parked reason=0` / `in_input=0` | `ruling=0 ready-for-implementer reason=1` / `in_input=1` |
| 8 | A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling | NEW | `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml ` / `in_input=0` | `exit=0 checks-in-flight kept: ci.yaml verifier.yaml ` / `in_input=1` |
| 9 | All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 | REGRESSION | the 4 expected lines | `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` |
| 10 | The reviewer run prompt says what the merge gate checks | NEW | `gate=0 promise=1` | `gate=1 promise=0` |
| 11 | Every reviewer prompt copy states what the merge gate checks | NEW | `gate=0 promise=1` ×3, `copy=SAME fill=unchanged` | `gate=1 promise=0` ×3, `copy=SAME fill=unchanged` |
| 12 | Every spec writer prompt copy gives the declaration line | NEW | `reads=0 form=0 braces=0` ×3, `copy=SAME fill=unchanged` | `reads=1 form=1 braces=1` ×3, `copy=SAME fill=unchanged` |
| 13 | The design doc and build spec drop the per-PR approval for protected paths | NEW | `gates=1 either=1 onpr=1 piece8=0 piece9=1 gaterow=0 stale=1 reviewer_rule=0 old_route=1 build=1 build_new=0` | `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0 build=0 build_new=1` |
| 14 | The changelog records issue 57's change without a numbering gap | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `5` |
| 15 | README describes the protected-path check and the new resolve verb | NEW | `built=0 unstick=0 merges=0` | `built=1 unstick=1 merges=1` |
| 16 | The protected-path change adds no whitespace errors | REGRESSION | `exit=0` | `exit=0` |

What the table shows:
- Every NEW scenario failed on the base exactly as `verification.md` predicted, so the spec matches the code it was written against.
- Every scenario prints its THEN line exactly on `ba3fea8`.
- The REGRESSION scenarios (3, 9 and 16) passed after the change, so no base re-run was needed.

Gates, on commit `ba3fea8`, from the worktree, each exactly as written:
- `(export HOME=...; git diff --check main...HEAD)`: no output, exit 0. The branch adds no whitespace errors.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `408 passed in 317.17s`. The whole harness suite passes, the new file included.

Also, not a gate: `ruff check` on the changed Python files printed `All checks passed!`. I also checked this change against its own Risk line, using the new `declared_paths` on `specs/T-0033/v2.md` and this instance's `protected_paths`. Every changed file under `factory/**` and `docs/prompts/**` is declared, so the new gate would merge this change as is.

## Tests added/changed

- Added `tests/factory/test_merge_protected_paths.py`: 17 cases on a Python port of the `t0033-gate.sh` fixture, all driven through `bin/factory`.
  - The refusal: its exact text, no backtick, `$` or double quote in it, main unchanged, ticket record unchanged, and one `merge.refused` event with sorted `paths`.
  - Five cases that declare nothing: another ticket's declaration, a move out of the protected tree, a Risk line in another form, a fenced line, and a brace-list entry.
  - Three cases that merge: a declared glob, a list marker with a trailing full stop, and unprotected paths only.
  - A ticket with no parent and no approved spec.
  - The build park, through `build.js` with a stub clerk.
  - `--accept-paths`: acceptance and then the merge; refusal on another park; refusal when the head is not the branch tip; refusal when nothing remains.
  - `--ruling` on a merge-gate park.
  - `--ruling` on a reviewer ESCALATE, with set-aside rows and the round unchanged.

  Before the code change, the file gave `14 failed, 3 passed`. The 3 that passed were the merge cases, which are regressions. After the change, all 17 pass.
- No existing test changed. The spec's "Tests to change" is none.

## Known gaps and uncertainties

- `factory:` markers added: none.
- The protected-path patterns are flattened in `undeclared_protected` with the same one-liner `instance.fill_preamble` uses (`[globs] if isinstance(globs, str) else list(globs or [])`). A shared helper would belong in `factory/instance.py`. That file is protected and the approved Risk line does not declare it, so I left it alone. The duplication is one expression.
- An entry that git rejects as a pathspec stops the gate with a git error instead of a `BLOCKED` refusal. I checked this: `` `../x` `` makes git exit 128 with "outside repository". In that case `merge` exits 2 with a `git diff ...` error, and the build parks the sub-ticket as `harness-bug: merge: ...`, not as a merge-gate park. The spec does not cover this. No current spec declares such an entry.
- The README status date stays `2026-10-09`. It already reads that date, which is today in UTC (this machine's local date is 2026-10-08). If the merge lands on a later date, the date needs moving at merge.
- The spec puts `--accept-paths` after `--ruling` in the order a mixed call takes, so `--ruling F --accept-paths G` runs `--ruling` only. The spec does not say what such a call should do, and I added no refusal for it.

## Out-of-scope observations

- The build spec's piece-8 wording (`protected path <p> not declared in the pinned spec v<N>`, one path per message) describes the unbuilt pre-receive design. It differs from the local gate's single `BLOCKED from merge gate: protected paths not declared in <id> spec v<n>: <p1>, <p2>` message. Both texts are as the spec dictates. They describe different gates, but a reader may expect them to match.
- `docs/design.md` line 76 (implementer model choice: "no protected path") and the sub-ticket `Protected paths:` field at line 574 are unchanged, as the spec's Out of scope says.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance scenario prints its THEN exactly on the commit, every NEW one failed on the base as described, and both gates pass (408 tests).
ESCALATIONS: none

## Diff `2f7f75f3961d2bd20b2fb106bd587ff94dd7621f...ba3fea8154f74ccd5007fd25d18f8215e0b7f000`

diff --git a/README.md b/README.md
index f6eddcc..235c207 100644
--- a/README.md
+++ b/README.md
@@ -121,7 +121,7 @@ agent hosts is under "Where this can go".
 | sub-ticket | one independently mergeable piece of a planned ticket; `T-0012.4` |
 | gate | a point where a human must decide before the pipeline continues; the spec gate is the main one |
 | gate commands | the target's own check commands, such as lint and tests (`gate_commands` in `instance.yaml`); the verifier runs them and records the gate result. No human is involved |
-| merge gate | the harness's check before a merge: both verdicts and the gate result on the same commit, which is the branch's tip and contains the integration branch. No human is involved |
+| merge gate | the harness's check before a merge: both verdicts and the gate result on the same commit, which is the branch's tip and contains the integration branch, and every protected path the change touches declared in the approved spec. A protected path is one `instance.yaml` lists under `protected_paths` because a change to it is sensitive, such as the harness's own code. No human is involved, except that a refusal for an undeclared protected path parks the sub-ticket for a human |
 | checker | the code reviewer or the verifier: a role that judges a commit and cannot change it |
 | parent | a ticket that has sub-tickets; its final check verifies the whole spec |
 | PR description | the implementer's final report on what it changed; there is no pull request in local mode |
@@ -480,12 +480,15 @@ The harness changes git in five ways, all local; it never pushes.
   - the commit is the branch's tip;
   - the gate result is PASS, the reviewer's verdict APPROVE and the verifier's VERIFIED, all on
     that commit;
+  - every protected path the change touches is declared on the `Protected paths:` line of the
+    approved spec's Risk section, or a human accepted it for this sub-ticket;
   - the commit contains the integration branch's current tip.
 
   It checks the last condition and merges under a lock, so two merges never interleave. A passing
   sub-ticket is merged with `git merge --no-ff`, and its message names the branch, the title and
   the id. Only the last refusal is recorded on the ticket: the sub-ticket goes back to its
-  implementer to merge the integration branch in, and both checks run again.
+  implementer to merge the integration branch in, and both checks run again. A refusal for an
+  undeclared protected path changes nothing on the ticket; the build parks the sub-ticket with it.
 - **Setting up the store.** `factory init` checks `factory-store` out as a worktree at the store's
   path, creating the branch with no history when none exists, and adds the path to the repo's git
   exclude file. `factory store migrate` creates the branch from an existing store, with one commit.
@@ -791,7 +794,7 @@ FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLE
 |---|---|---|
 | **File** | `factory ticket new --file <abs path>` | that this request is worth a ticket |
 | **Gate** | `factory approve-spec T-n [--edit F]` · `factory request-changes T-n F` · close | the spec's intent, risk declarations, operator steps, "tests to change"; a gate edit becomes a new spec version and is what gets pinned |
-| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, or the harness blocked an implementer whose sub-ticket lists a test no merged sibling added) · `--redispatch` (re-run the checks on the same commit after an outside fix, or after a checker ended without output twice) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, a re-check, a re-plan, a re-scope, or closing |
+| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, or the harness blocked an implementer whose sub-ticket lists a test no merged sibling added; a ruling on the code reviewer's escalation re-runs the checks, with the ruling in their input) · `--accept-paths F` (the merge gate refused a protected path the approved spec does not declare: accept it under the approved design, and the sub-ticket returns to its checks; `--ruling F` sends the sub-ticket back to its implementer instead) · `--redispatch` (re-run the checks on the same commit after an outside fix, or after a checker ended without output twice) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, an accepted protected path, a re-check, a re-plan, a re-scope, or closing |
 | **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included. It appends one dated line to the target's decision log, `decisions.md`, which the spec writer, critic and planner receive with their input | that a decision binds later tickets |
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
@@ -871,6 +874,13 @@ path above is relative to the store.
   diff and leaves the test suite and the gate commands to the verifier. Every role is told to wait
   for the commands it starts before it ends its turn. It is tested, and has not yet fired on a real
   ticket.
+- **Protected paths at merge.** The merge gate refuses a change to a protected path that the
+  approved spec does not declare on the `Protected paths:` line of its Risk section, and names
+  each such path. The human approves that line at the spec gate, so a declared path merges with
+  no further approval. A refused sub-ticket parks as blocked. The human answers with
+  `resolve --accept-paths F`, which accepts the paths for that sub-ticket and returns it to its
+  checks, whose passing results stand, or with `resolve --ruling F`, which sends it back to its
+  implementer. It is tested, and has not yet fired on a real ticket.
 
 **Not built**
 
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 1fd6fa9..e18390b 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -243,7 +243,7 @@ Runtime: `factory/hooks/pre-receive` is a `#!/bin/sh` shim installed into `~/fac
 4. **`refs/heads/main`** (merge gate). Only `harness`; fast-forward only. `H = new`; ticket with `head == H`. Normal conditions, first failure named:
    - `results/H/{ci,reviewer,verifier}.yaml` = `PASS`,`APPROVE`,`VERIFIED` (`missing: ci, reviewer, verifier for H`);
    - `git merge-base --is-ancestor old H` (`head H does not contain main <old>`);
-   - piece 8, per path in `git diff --name-only old H`: protected glob or **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`protected path <p> needs human approval on H` / `guardrail path <p> needs human approval on H`); existing test file (test glob, present in `old`) modified or deleted → in `spec.tests_to_change` of the pinned version, or named by one of the sub-ticket's `(added by <ID>)` lines that `run start` checked (`existing test <p> modified; not in Tests to change of pinned spec v<N>`); new test file → nothing.
+   - piece 8, per path in `git diff --name-only old H`: in-repo protected glob → declared on the `Protected paths:` line of the pinned spec's Risk section, or in the sub-ticket's `accepted_paths` (`protected path <p> not declared in the pinned spec v<N>`); **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`guardrail path <p> needs human approval on H`); existing test file (test glob, present in `old`) modified or deleted → in `spec.tests_to_change` of the pinned version, or named by one of the sub-ticket's `(added by <ID>)` lines that `run start` checked (`existing test <p> modified; not in Tests to change of pinned spec v<N>`); new test file → nothing.
    - **Exception (doc §Harness table piece 7; the only one), two branches:**
      - *retro*: `type: retro`, `parent: null`, every changed path matches a non-test guardrail glob (the doc's list: CI config, AGENTS.md, skills, prompts — `factory/hooks/**`, `paths.yaml`, `identities.yaml`, `factory/workflows/**` are protected, S5) → conditions become `ci PASS` + head contains main + `approvals/<ID>/guardrail-H.yaml` (human-pushed).
      - *revert*: `type: revert`, `parent: null`, `reverted_head: X` the `head` of a `merged` ticket `T` whose record holds `merge: {base_before: B, main_after: A}` (written by `factory merge`, G), the branch human-pushed (rule 1: no role may push `revert/*`), and `git diff old H` equals `git diff A B` — the inverse of that change proposal's diff, main-before-merge against main-after-merge (E5: a clean `git revert` produces exactly this patch and an extra hunk breaks it) → the same three conditions. Piece 8 on a revert: files present in `A` and absent in `B` (files the reverted PR added) and the tests `T`'s pinned spec listed under "Tests to change" are exempt, `approvals/<ID>/guardrail-H.yaml` being the piece-8 row for them; any other existing test modified or deleted → the normal piece-8 refusal.
@@ -374,7 +374,7 @@ Setup: `git clone $O w; cd w; git commit --allow-empty -m c`.
 22. Rows `ci PASS`, `reviewer APPROVE`, `verifier VERIFIED` for `H` (via `results record`), `H` contains `main`, diff = `nanobot/hello.py` + new `tests/factory/test_hello.py` → `factory merge T-0001` exit 0; `git ls-remote $O main | cut -f1` → `H`; `status: merged` [NEW]
 23. As 22 but `main` advanced by `M` after the rows → exit 2, `head H does not contain main M`; `status: ready-for-implementer`, `round: {spec: 0, pr: 1}` [NEW]
 24. As 22 but rows for previous head `H0` → exit 2, `missing: ci, reviewer, verifier for H` [NEW]
-25. As 22 plus `pyproject.toml` changed, no approval → exit 2, `protected path pyproject.toml needs human approval on H`; after `AS daniel factory approve-pr T-0001 --head H` → exit 0 [NEW]
+25. As 22 plus `pyproject.toml` changed, not declared → exit 2, `protected path pyproject.toml not declared in the pinned spec v1`; with `pyproject.toml` on the pinned spec's `Protected paths:` line → exit 0, no approval row [NEW]
 26. **Guardrail gate on a normal PR:** as 22 plus `AGENTS.md` changed → exit 2, `guardrail path AGENTS.md needs human approval on H`; after `approve-pr` → exit 0 [NEW]
 27. As 22 but modifying existing `tests/factory/test_existing.py` not in the pinned list → exit 2, `existing test tests/factory/test_existing.py modified; not in Tests to change of pinned spec v1`; with it listed → exit 0 [NEW]
 28. As 22 but only adding `tests/factory/test_new.py` → exit 0, no approval row [NEW]
diff --git a/docs/changelog.md b/docs/changelog.md
index 8507f64..fd60730 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -64,5 +64,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 60. After issue #75 (2026-10-08), where every spec writer and critic input carried all of current truth and the whole decision log, whatever its ticket touched: one spec writer input on this repo's store was 171.6 kB, of which 123.9 kB was current truth and 32.4 kB the log, and the Nanobot store adds about 480 kB to each writer input. Triage now receives the capability index, one line per current-truth capability with its size, spec path and requirement names, and names the capabilities a request touches on a new `Capabilities:` output line. The spec writer and critic receive those capabilities in full, plus each one their spec cites by path, and the capability index for the rest. They and the planner receive the decision-log lines of the ticket and of those capabilities, and a decision index for the rest: one line per other ticket, with a `grep` command that reads its lines. A ticket whose triage output has no `Capabilities:` line keeps the whole of both. The projection for the Nanobot store's last ten tickets is a mean writer input of 101 kB and a maximum of 167 kB, against 521 kB and 635 kB before; that still misses the request's 40 kB and 100 kB targets, because the rest of a writer input lies outside this change. Rejected: `factory spec show` and `factory decision show` commands, because a command run from inside a role must clear the live-store fence, the guard that refuses store commands while a role runs, and find the instance; a path needs neither.
 61. After issue #78 (2026-10-09), where #75's filter reduced every decision logged against another ticket to a line of the decision index, because no line in either store's decision log names a capability: in the operator's replay of a Nanobot ticket, the spec writer put new code in a module that another ticket's standing decision rules out, and the critic missed it. The spec writer, critic and planner receive the whole decision log again, whatever capabilities their ticket names. The decision index and its `grep` command are gone; the capability index stays. Measured on 2026-10-09, the decision part of each of their inputs grows from under 3 kB to about 36 kB on this repo's store, and from about 5 kB to about 80 kB on the Nanobot store. Rejected: the request's rule of sending in full the lines that name no capability and filtering the rest, because on today's logs it sends every line anyway, and it could still hide a cross-cutting decision that happens to name a capability.
 62. After issue #77 (2026-10-08), where Nanobot ticket T-0024 was sent back to the spec gate after planning and approved at a new version: its new plan's sub-ticket was created, but the old plan's sub-ticket that the operator had closed parked the parent at once, and only moving that sub-ticket's record out of the store's `tickets/` by hand let the build go on. Each sub-ticket now records `planned_from`, the parent's approved version when it was created, which nothing changes afterwards. Once a parent has a sub-ticket planned from a later version, its sub-tickets that have not merged and were planned from an earlier one are superseded: kept with their ids and records, but left out of `ready-implementers` (listed under `superseded`), the final check, the close, archive and `resolve --replan`. Merged ones stay merged and count. `subticket add` reports and logs the sub-tickets it supersedes, and refuses a plan whose `Depends on` names one; the planner's input names them. A record without `planned_from` falls back to its `spec.approved_version`, and a second plan at the same approved version supersedes nothing. Rejected: a superseded mark written at re-plan time, which needs a migration for stores that already hold such sub-tickets; and comparing with the parent's current approved version, which would supersede the live plan after a spec amendment that keeps it.
+63. After issue #57 (2026-10-05), where the merge gate merged changes to protected paths without reading any declaration of them, while the code reviewer's prompt promised that the gate would require a human approval: the approved spec's Risk section is now the authorization. The spec writer declares every protected path the change will touch on one line of Risk, `Protected paths: none` or `Protected paths:` followed by backticked entries, one path or glob per entry, with no brace lists; the human approves that line at the spec gate. At merge, the gate compares the changed paths, from the merge base with the integration branch and with both sides of a move, against the instance's in-repo protected globs and the pinned spec's line. It refuses each undeclared protected path by name, with an error that starts `BLOCKED from merge gate`, and the build parks the sub-ticket with that error. The human answers the park with `resolve --accept-paths F`, which accepts those paths for that sub-ticket and returns it to its checks, whose passing results stand, or with `resolve --ruling F`, which sends it back to its implementer at the same round. A ruling on a reviewer's ESCALATE now returns the sub-ticket to its checks, with the results that did not pass set aside, instead of to the spec critic, a step that never runs for a sub-ticket. Check 6 of the code reviewer prompt says what the gate does, the spec writer's FORMAT gives the declaration line, and the design's gate lines, piece 7, piece 8, piece 9 and the resolution rules drop the per-PR approval for protected paths. Rejected: reading every backticked path in Risk, since Risk sections also name paths they promise not to touch; and a human approval on every change to a protected path, which would have stopped 18 of the last 20 merges in this repository.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 2a98d97..b23a4d8 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -18,9 +18,9 @@ The pipeline, in order:
 8. REQUEST-CHANGES, FAILED, and CI failures go back to the implementer as findings; a merge conflict triggers a conflict run (same round); a verifier SPEC-DEFECT goes to the human queue. Merge only when CI is green, both the reviewer's APPROVE and the verifier's VERIFIED name the PR's current head commit, the head contains current main, and any piece-8 approval is recorded. Any new commit, including a CI fix or rebase, re-runs both (harness piece 6).
 9. **Retro** runs weekly after the audit, or on demand after a major block of work, and proposes instruction changes from failure patterns, as a PR. It is not optional: it is the only path by which the pipeline improves.
 
-The pipeline runs autonomously. A human is interrupted only at the five gates in "Human gates and convergence": spec approval, a PR touching a protected path, the daily escalation queue, a guardrail change, and the weekly audit. Everything else is dispatched by the harness without asking.
+The pipeline runs autonomously. A human is interrupted only at the five gates in "Human gates and convergence": spec approval, a merge refused for a protected path the approved spec does not declare, the daily escalation queue, a guardrail change, and the weekly audit. Everything else is dispatched by the harness without asking.
 
-Two path lists appear throughout. **Guardrail paths** are fixed: existing tests, CI config, AGENTS.md, skills, and these prompts. **Protected paths** are per repo: `{auth, payments, migrations, infra, public API, dependencies}`. A change to either needs a human approval record before it merges.
+Two path lists appear throughout. **Guardrail paths** are fixed: existing tests, CI config, AGENTS.md, skills, and these prompts. **Protected paths** are per repo: `{auth, payments, migrations, infra, public API, dependencies}`. A change to a guardrail path needs a human approval record before it merges. A change to a protected path merges when the approved spec's Risk section declares it: the human approves that declaration at the spec gate, and the merge gate refuses a protected path the spec does not declare.
 
 Three wiring rules matter more than any wording:
 
@@ -46,9 +46,9 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | 4 | Scoped credentials | Each role gets only the access its rules allow. Implementer: push to its own branch. Triage, spec writer, critic, planner, reviewer, verifier, and gate runner: read-only clone plus a shell, with no secrets in the environment, since they run PR code before any security check has passed (model access through a proxy sidecar that holds the key, so the container has none to leak; no git write token; restricted egress). Retro: push a branch and open a PR, nothing else. No role can push to main. Only the harness identity and humans write the ticket store; role outputs enter it through the dispatcher, and the merge gate accepts an approval row only if a human identity pushed it, judged by the server's pusher identity, not the commit author | Job-level `permissions:` on a per-job `GITHUB_TOKEN` | One git user or deploy key per role, with server-side rights set on the git host. Secrets injected per job from a vault or env, never baked into the image |
 | 5 | Change proposal | A unit of review: a branch, its base, its head commit, and a place for the PR description and findings. Approvals attach to the head commit. Fix rounds push to the same branch, which is the ticket's identity | Pull requests | A branch naming convention (`ticket/<id>`) plus a record in the ticket store holding base, head SHA, and the description. GitLab MRs or Gerrit changes are direct equivalents |
 | 6 | Commit-bound results | Reviewer, verifier, and CI results are stored against a specific head SHA. A new push makes prior results stale; a result arriving for a head that is no longer current is discarded | Check runs and commit statuses; required checks re-run on push | A `results` table keyed by `(head_sha, role)`. The merge condition queries the *current* head only, so stale rows never match |
-| 7 | Merge gate | Nothing reaches main without CI green, APPROVE and VERIFIED on the current head, a head that contains current main, and a human approval record where piece 8 requires it. A bug in a prompt cannot bypass this. One exception, stated here and nowhere else, for two kinds of PR with no sub-ticket: a retro PR whose diff touches only non-test guardrail paths, and a human-authored revert whose diff the gate verifies is exactly the inverse of one merged change proposal's diff (main before that merge against main after it, both recorded in the store at merge time). Either merges on CI green, head contains main, and a human approval on that head recorded under the guardrail-changes gate; the human reads the whole diff, which stands in for APPROVE and VERIFIED. A no-sub-ticket PR that fails this test is closed and logged to the human queue | Branch protection with required checks and required reviews. Required checks cannot be waived per PR, so the exception needs a harness-emitted check that reports success for exception PRs | A server-side pre-receive hook on main that checks the results table, or a single merge bot that alone can write to main and checks the conditions before fast-forwarding. Either works; the hook is stricter |
-| 8 | Guardrail and protected paths | If the diff touches a guardrail or protected path, the merge gate requires an approval row signed by a human identity. For existing tests, the spec gate's approval of "Tests to change" is that row for exactly the tests listed. A test file an earlier sibling sub-ticket of the same parent added is also covered when the sub-ticket lists it as added by that sibling and the sibling-tests check has passed (Tests a sibling added, below); any other guardrail or protected path needs a human approval on the PR itself. The harness code (its package, entry point, agent templates and dependency lock) is itself a protected path in the repo that holds it. | CODEOWNERS with required owner review for CI config, AGENTS.md, skills, prompts, and protected paths. Not for tests: CODEOWNERS fires on added files too. Existing tests get a required check that fails when a test file is modified or deleted and not in the pinned spec's "Tests to change" or among the sub-ticket's checked sibling entries (on a revert: files the reverted PR added and the tests its pinned spec listed under "Tests to change" are exempt, and the revert's human approval is the piece-8 row for them) | A path list checked in the merge gate, with the same modified-or-deleted rule for test files. Keep the list in the repo under CI config, so it is itself a guardrail path |
-| 9 | Human surface | Where people approve specs, answer escalations, review protected PRs, reply to requesters, and read the weekly audit sample. Every decision writes back to the store as a record: who, when, which spec version or head SHA | Issue comments, PR reviews, approvals | The tracker's UI plus notifications (Slack, email) with links. The approval must be a stored, attributable record the merge gate can check, not a chat message |
+| 7 | Merge gate | Nothing reaches main without CI green, APPROVE and VERIFIED on the current head, a head that contains current main, every changed protected path declared (piece 8), and a human approval record where piece 8 requires one. A bug in a prompt cannot bypass this. One exception, stated here and nowhere else, for two kinds of PR with no sub-ticket: a retro PR whose diff touches only non-test guardrail paths, and a human-authored revert whose diff the gate verifies is exactly the inverse of one merged change proposal's diff (main before that merge against main after it, both recorded in the store at merge time). Either merges on CI green, head contains main, and a human approval on that head recorded under the guardrail-changes gate; the human reads the whole diff, which stands in for APPROVE and VERIFIED. A no-sub-ticket PR that fails this test is closed and logged to the human queue | Branch protection with required checks and required reviews. Required checks cannot be waived per PR, so the exception needs a harness-emitted check that reports success for exception PRs | A server-side pre-receive hook on main that checks the results table, or a single merge bot that alone can write to main and checks the conditions before fast-forwarding. Either works; the hook is stricter |
+| 8 | Guardrail and protected paths | If the diff touches a protected path, the merge gate requires the pinned spec's Risk section to declare it on its `Protected paths:` line, or a human to have accepted that path for the sub-ticket after the gate refused it (`resolve --accept-paths`); the spec gate's approval is the authorization, and there is no per-PR approval. If the diff touches a guardrail path, the merge gate requires an approval row signed by a human identity. For existing tests, the spec gate's approval of "Tests to change" is that row for exactly the tests listed. A test file an earlier sibling sub-ticket of the same parent added is also covered when the sub-ticket lists it as added by that sibling and the sibling-tests check has passed (Tests a sibling added, below); any other guardrail path needs a human approval on the PR itself. The harness code (its package, entry point, agent templates and dependency lock) is itself a protected path in the repo that holds it. | CODEOWNERS with required owner review for CI config, AGENTS.md, skills and prompts; protected paths get a required check that fails on a changed protected path the pinned spec does not declare. Not for tests: CODEOWNERS fires on added files too. Existing tests get a required check that fails when a test file is modified or deleted and not in the pinned spec's "Tests to change" or among the sub-ticket's checked sibling entries (on a revert: files the reverted PR added and the tests its pinned spec listed under "Tests to change" are exempt, and the revert's human approval is the piece-8 row for them) | A path list checked in the merge gate, with the same modified-or-deleted rule for test files. Keep the list in the repo under CI config, so it is itself a guardrail path |
+| 9 | Human surface | Where people approve specs, answer escalations, answer merges refused for an undeclared protected path, reply to requesters, and read the weekly audit sample. Every decision writes back to the store as a record: who, when, which spec version or head SHA | Issue comments, PR reviews, approvals | The tracker's UI plus notifications (Slack, email) with links. The approval must be a stored, attributable record the merge gate can check, not a chat message |
 | 10 | Audit log | Every transition, every agent output, every human decision, append-only. The weekly audit and the retro read from here | Issue and PR timelines, Actions logs | An append-only table or log stream. Store full agent outputs as artifacts keyed by run id. If it isn't logged, the retro can't see it |
 | 11 | Gate runner | Runs `{gate commands}` (build, lint, typecheck, tests) on a head SHA and records PASS/FAIL against it (piece 6) | Actions CI | Any CI. Without one, the verifier runs the gates as step 4 of its prompt, and its "Gate suite" line is recorded as the CI result. Separate CI is better because it isn't an agent. A gate command may name the paths it covers, as git pathspecs. For a sub-ticket whose diff touches none of them, the harness marks the command SKIPPED for the reviewer and verifier, with the reason, and records it on the `ci` row; the row's PASS or FAIL still comes from the commands that ran. A command without paths always runs |
 | 12 | Secrets | Model API keys and git credentials, available to a run that needs them but never in the repo, the prompt, or the log | Actions secrets | Vault, cloud secret manager, or env injection at container start. Redact from logs |
@@ -105,10 +105,12 @@ Rules the table relies on:
 - When a human resolves a parked ticket:
   - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way. When the answer is a standing decision, the human passes `--decision "<line>"` with the answer, or with the close, so that it lands in `decisions.md`.
   - BLOCKED, a critic ESCALATE, and a planner ESCALATE return to the role that emitted them with the ruling, same round, or the human re-scopes (spec gate or writer round reset) or closes.
+  - A merge the gate refused for an undeclared protected path parks as BLOCKED. A ruling returns the sub-ticket to its implementer, same round. `resolve --accept-paths` instead adds the named paths to what that sub-ticket may change and returns it to its checks, whose passing results stand; every other merge condition still applies.
   - A spec loop at max rounds goes to the spec gate.
   - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (new sub-tickets under the same parent) or closes the parent. A new plan made from a later approved version supersedes the earlier plan's sub-tickets that have not merged: they keep their records and ids, are no longer dispatched, and neither park the parent nor hold back its close. Merged ones stay merged and count toward the close.
   - An archive refused for no change folder or no spec store parks the parent the same way, but its spec never entered the spec store: the human closes the parent as applied. Current truth is not updated, and archive appends nothing to `decisions.md`; the human logs any decision with `factory decision add`. If current truth should carry the spec, it is re-intaken as a new ticket.
-  - A PR loop at max rounds, a SPEC-DEFECT, or a reviewer ESCALATE returns to the implementer with the round reset and the human's ruling as findings, or the ticket closes. The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive. There is no merge-gate override. A budget-killed run, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches the same role on the same inputs, same round (the human may raise that run's budget or amend the sub-ticket first), or the ticket closes. In-flight siblings keep the spec version they received; the human decides whether to re-plan.
+  - A reviewer ESCALATE returns to its checks with the ruling in both checkers' input, same round. Its results that did not pass are set aside, so the reviewer runs again; a ruling that asks for a fix becomes the reviewer's REQUEST-CHANGES.
+  - A PR loop at max rounds or a SPEC-DEFECT returns to the implementer with the round reset and the human's ruling as findings, or the ticket closes. The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive. There is no merge-gate override. A budget-killed run, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches the same role on the same inputs, same round (the human may raise that run's budget or amend the sub-ticket first), or the ticket closes. In-flight siblings keep the spec version they received; the human decides whether to re-plan.
 
 | From | STATUS | Next | Receives |
 |---|---|---|---|
@@ -138,7 +140,7 @@ Rules the table relies on:
 | Any role | EMPTY-OUTPUT, the first in a row | The same role again, same round | The same inputs |
 | Any role | EMPTY-OUTPUT, the second in a row | Human queue | Both runs' last messages |
 | Merge gate | Head does not contain current main | Implementer (same round, conflict run): merge main into the branch, or rebase where {force-push allowed} | Conflict output; the new head re-runs CI and both checkers |
-| Merge gate | CI green + APPROVE + VERIFIED on current head + head contains main + piece-8 approvals | Merge; then dispatch sub-tickets that depended on this one. When all sub-tickets have merged, one verifier run on main against the parent's full Acceptance list (every scenario of its pinned delta, with its `verification.md` label). When the parent has one sub-ticket, `main` has not moved since that sub-ticket merged, the sub-ticket's text names every scenario of the parent's pinned delta, and its VERIFIED run checked the merged head against the parent's recorded base, that run stands for the parent-close run and no new run starts. VERIFIED archives the change (Spec store), then closes the parent; FAILED, SPEC-DEFECT or an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) parks the parent in the human queue | Parent-close run: pinned parent spec; head = current main; base = the main SHA recorded before the parent's first sub-ticket merged; `{gate commands}` |
+| Merge gate | CI green + APPROVE + VERIFIED on current head + head contains main + piece-8 checks | Merge; then dispatch sub-tickets that depended on this one. When all sub-tickets have merged, one verifier run on main against the parent's full Acceptance list (every scenario of its pinned delta, with its `verification.md` label). When the parent has one sub-ticket, `main` has not moved since that sub-ticket merged, the sub-ticket's text names every scenario of the parent's pinned delta, and its VERIFIED run checked the merged head against the parent's recorded base, that run stands for the parent-close run and no new run starts. VERIFIED archives the change (Spec store), then closes the parent; FAILED, SPEC-DEFECT or an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) parks the parent in the human queue | Parent-close run: pinned parent spec; head = current main; base = the main SHA recorded before the parent's first sub-ticket merged; `{gate commands}` |
 | Weekly audit done, or on demand | — | Retro | Full outputs behind every outcome signal since the last retro (piece 10), current instruction files, every proposal still under evaluation with its metric, and per-role run and outcome counts, broken down by model, for the period and for each prior proposal's window, and the marker ledger: one row per `factory:` comment in the code on the integration branch, with file:line, limit and upgrade trigger, flagged `no-trigger` where it names none, composed by the harness when the retro runs |
 | Retro | PROPOSED | Guardrail-changes gate (human); on approval, the no-sub-ticket merge row | PR |
 | Retro | NO-CHANGES | Log only | — |
@@ -153,7 +155,7 @@ Humans own the decisions agents are worst at: what to build, what's risky, and w
 | Gate | When | Human does |
 |---|---|---|
 | Spec approval | Every spec, before planning | Confirms intent and priority; answers open questions; approves the Risk section's protected-path declarations, any Operator steps, and the "Tests to change" list, which is the only authorization to alter a test that existed before the parent's first sub-ticket merged; a test an earlier sibling added needs only the sub-ticket's checked entry (piece 8) |
-| Protected paths | Any PR touching a protected path | Reviews the PR and records the piece-8 approval; the merge gate does not merge without it |
+| Protected paths | A merge the gate refused because a changed protected path is not declared in the pinned spec's Risk section | Accepts the paths under the approved design (`resolve --accept-paths`), which returns the sub-ticket to its checks, or sends it back to its implementer with a ruling (`resolve --ruling`) |
 | Escalations | Daily | Clears the queue; answers or re-scopes |
 | Guardrail changes | Any PR touching a guardrail path beyond the tests its spec lists; any retro or revert PR | Approves or rejects, including retro proposals and reverts |
 | Audit | Weekly | Reads {5} random merged PRs end to end; tracks failure rate and cost per issue |
@@ -397,7 +399,10 @@ openspec/changes/<ticket id>/ (schema spec-factory).
 ## Open questions   none | list
 ## Decisions        none | one line per design call this change makes,
                     including each answered open question
-## Risk             blast radius; every protected path this will touch
+## Risk             blast radius; every protected path this will touch,
+                    declared on one line the merge gate reads:
+                    Protected paths: none | `<path or glob>`, `<path or glob>`
+                    one path or glob per entry, no brace lists
 ## Operator steps   (optional) actions or checks on live or protected state
                     that only the operator can perform, after merge; not
                     acceptance; the human approves them at the spec gate
@@ -664,9 +669,10 @@ CHECK, IN THIS ORDER
    would notice that the spec didn't ask for?
 5. Security and data safety: injection, authz, secrets, destructive ops.
 6. Protected paths touched? If the sub-ticket does not declare them,
-   ESCALATE. If it does, list them under ESCALATIONS, finish the review,
-   and give the STATUS the code earns; the merge gate will require a
-   human approval.
+   ESCALATE. If it does, list them under ESCALATIONS for the record,
+   finish the review, and give the STATUS the code earns. The merge
+   gate merges a path the approved spec's Risk section declares with no
+   further approval, and refuses and parks one it does not declare.
 7. The coding standard at {coding standard}: a finding against it
    carries the tag and severity the standard gives it. Not style.
 8. PR description: could the operator at the gate read its What changed
diff --git a/docs/prompts/02-spec-writer.md b/docs/prompts/02-spec-writer.md
index e2b097d..a2b04de 100644
--- a/docs/prompts/02-spec-writer.md
+++ b/docs/prompts/02-spec-writer.md
@@ -80,7 +80,10 @@ openspec/changes/<ticket id>/ (schema spec-factory).
 ## Open questions   none | list
 ## Decisions        none | one line per design call this change makes,
                     including each answered open question
-## Risk             blast radius; every protected path this will touch
+## Risk             blast radius; every protected path this will touch,
+                    declared on one line the merge gate reads:
+                    Protected paths: none | `<path or glob>`, `<path or glob>`
+                    one path or glob per entry, no brace lists
 ## Operator steps   (optional) actions or checks on live or protected state
                     that only the operator can perform, after merge; not
                     acceptance; the human approves them at the spec gate
diff --git a/docs/prompts/06-code-reviewer.md b/docs/prompts/06-code-reviewer.md
index d391fbb..6fb668f 100644
--- a/docs/prompts/06-code-reviewer.md
+++ b/docs/prompts/06-code-reviewer.md
@@ -22,9 +22,10 @@ CHECK, IN THIS ORDER
    would notice that the spec didn't ask for?
 5. Security and data safety: injection, authz, secrets, destructive ops.
 6. Protected paths touched? If the sub-ticket does not declare them,
-   ESCALATE. If it does, list them under ESCALATIONS, finish the review,
-   and give the STATUS the code earns; the merge gate will require a
-   human approval.
+   ESCALATE. If it does, list them under ESCALATIONS for the record,
+   finish the review, and give the STATUS the code earns. The merge
+   gate merges a path the approved spec's Risk section declares with no
+   further approval, and refuses and parks one it does not declare.
 7. The coding standard at {coding standard}: a finding against it
    carries the tag and severity the standard gives it. Not style.
 8. PR description: could the operator at the gate read its What changed
diff --git a/factory/cli.py b/factory/cli.py
index 2da17fa..759811b 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -655,23 +655,80 @@ def results_show(a, root, cfg):
     out({"ok": True, "id": t["id"], "head": head, "rows": {k: v["status"] for k, v in rows.items()}, "missing": missing})
 
 
+DECLARED_RE = re.compile(r"^\s*(?:[-*]\s+)?Protected paths:\s*(none|`[^`]+`(?:\s*,\s*`[^`]+`)*)\s*\.?\s*$")
+
+
+def _in_repo(globs: list[str]) -> list[str]:
+    """The patterns a repository diff can match: one starting `~` or `/` names a path outside it."""
+    return [g for g in globs if not g.startswith(("~", "/"))]
+
+
+def declared_paths(spec_text: str) -> list[str]:
+    """The entries of each `Protected paths:` line (DECLARED_RE) in the spec's `## Risk` section, in
+    order. The section runs from a line that is exactly `## Risk` to the next line starting `## ` or
+    `=== `; a line inside a fenced code block neither starts nor ends it and declares nothing."""
+    entries, in_risk = [], False
+    for line, in_fence in specstore.lines_outside_fences(spec_text):
+        if in_fence:
+            continue
+        if line.startswith(("## ", "=== ")):
+            in_risk = line.rstrip() == "## Risk"
+        elif in_risk and (m := DECLARED_RE.match(line)) and m.group(1) != "none":
+            entries += re.findall(r"`([^`]+)`", m.group(1))
+    return _in_repo(entries)
+
+
+def undeclared_protected(root: Path, cfg: dict, t: dict, head: str) -> tuple[list[str], str]:
+    """(the changed protected paths of `t` at `head` that the pinned spec does not declare, sorted;
+    where the declarations were read, for the refusal). Changed is `integration...head`. The pinned
+    spec is the parent's approved version, or the ticket's own when it has no parent; a path in the
+    ticket's `accepted_paths` counts as declared (`resolve --accept-paths`)."""
+    sid = t.get("parent") or t["id"]
+    av = (store.load_ticket(root, sid) if sid != t["id"] else t)["spec"]["approved_version"]
+    where = f"in {sid} spec v{av}" if av is not None else f"({sid} has no approved spec)"
+    patterns = [g for globs in (cfg.get("protected_paths") or {}).values()
+                for g in ([globs] if isinstance(globs, str) else list(globs or []))]
+    repo = gitops.repo_root(cfg)
+    integ = gitops.integration_branch(cfg, repo)
+    changed = gitops.changed_files(repo, integ, head, _in_repo(patterns))
+    if not changed:
+        return [], where
+    spec = root / "specs" / sid / f"v{av}.md"
+    declared = declared_paths(spec.read_text(encoding="utf-8")) if av is not None and spec.exists() else []
+    ok = set(gitops.changed_files(repo, integ, head, declared)) | set(t.get("accepted_paths") or [])
+    return sorted(p for p in changed if p not in ok), where
+
+
+def _branch_tip(repo: Path, t: dict) -> str:
+    """The ticket's head, refused unless it is the tip of its branch."""
+    head = t.get("head")
+    if not head or gitops.rev(repo, t["branch"]) != head:
+        raise Refused(f"{t['id']} head {head} is not the branch tip; run ticket head")
+    return head
+
+
 def merge_cmd(a, root, cfg):
     """Rule-4 checks (part G) in the local stand-in: ci PASS + APPROVE + VERIFIED on the current
-    head, head contains the integration branch; then a local --no-ff merge. Exit 2 names the
-    first failing condition; 'head does not contain main' is the conflict-run signal."""
+    head, every changed protected path declared by the pinned spec (piece 8), head contains the
+    integration branch; then a local --no-ff merge. Exit 2 names the first failing condition;
+    'BLOCKED from merge gate' parks for a human; 'head does not contain main' is the conflict-run
+    signal."""
     t = store.load_ticket(root, a.id)
     if t["status"] not in ("ready-for-merge", "checks-in-flight"):
         raise Refused(f"{t['id']} is {t['status']}, not ready-for-merge")
     repo = gitops.repo_root(cfg)
     integ = gitops.integration_branch(cfg, repo)
-    head = t.get("head")
-    if not head or gitops.rev(repo, t["branch"]) != head:
-        raise Refused(f"{t['id']} head {head} is not the branch tip; run ticket head")
+    head = _branch_tip(repo, t)
     rows = store.results_for(root, head)
     for role, want in (("ci", "PASS"), ("reviewer", "APPROVE"), ("verifier", "VERIFIED")):
         got = (rows.get(role) or {}).get("status")
         if got != want:
             raise Refused(f"{role} is {got or 'missing'} for {head[:9]}, need {want}")
+    undeclared, where = undeclared_protected(root, cfg, t, head)
+    if undeclared:
+        store.log_event(root, "merge.refused", ticket=t["id"], head=head, reason="protected paths not declared",
+                        paths=undeclared)
+        raise Refused(f"BLOCKED from merge gate: protected paths not declared {where}: {', '.join(undeclared)}")
     with gitops.MergeLock(repo):
         if not gitops.head_contains(repo, head, integ):
             t["merge_refused"] = "head does not contain main"
@@ -839,7 +896,7 @@ def request_changes(a, root, cfg):
 def resolve(a, root, cfg):
     if a.decision is not None:  # refuse before anything is written, so a decision is never dropped
         # the branch below that will run: --answer wins, and --close runs only with no other mode
-        if not (a.answer or (a.close and not (a.ruling or a.to or a.redispatch or a.replan))):
+        if not (a.answer or (a.close and not (a.ruling or a.accept_paths or a.to or a.redispatch or a.replan))):
             raise Refused("--decision applies only with --answer or --close")
         specstore.decision_text(a.decision)
     t = store.load_ticket(root, a.id)
@@ -882,13 +939,35 @@ def resolve(a, root, cfg):
             if st == "parked" and (reason.startswith("NEEDS-HUMAN") or "CLARIFY" in reason):
                 raise Refused("use --answer")
             raise Refused(f"--ruling applies to an ESCALATE or BLOCKED park; {t['id']} is {st} ({reason or 'no park'})")
-        if reason.startswith("BLOCKED"):  # an implementer's BLOCKED: back to it, same round, ruling in its input
+        if reason.startswith("ESCALATE from reviewer"):
+            # Back to its checks, same round: the reviewer runs again with the ruling in its input.
+            head, moved = t.get("head"), _set_aside_failed_rows(root, t)
+            store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
+            dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
+            shutil.copyfile(a.ruling, dest)
+            move("checks-in-flight", "ruling", {"ruling": _rel(root, dest), "head": head, "superseded": moved})
+            return
+        if reason.startswith("BLOCKED"):  # an implementer's or the gate's BLOCKED: back to the implementer, same round
             to = "ready-for-implementer"
         else:
             to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
         dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
         shutil.copyfile(a.ruling, dest)
         move(to, "ruling", {"ruling": _rel(root, dest)})
+    elif a.accept_paths:
+        # The merge gate refused a protected path the pinned spec does not declare; the human accepts
+        # it under the approved design for this sub-ticket. Its results stand, so the build merges it.
+        if st != "parked" or not reason.startswith("BLOCKED from merge gate:"):
+            raise Refused("--accept-paths applies to a merge gate park (BLOCKED from merge gate); "
+                          f"{t['id']} is {st} ({reason or 'no park'})")
+        head = _branch_tip(gitops.repo_root(cfg), t)
+        paths, _ = undeclared_protected(root, cfg, t, head)
+        if not paths:
+            raise Refused(f"nothing to accept: {t['id']} has no undeclared protected path at {head[:9]}")
+        dest = d / f"ruling-{_next_n(d, 'ruling')}.md"
+        shutil.copyfile(a.accept_paths, dest)
+        t["accepted_paths"] = sorted(set(t.get("accepted_paths") or []) | set(paths))
+        move("checks-in-flight", "accept-paths", {"ruling": _rel(root, dest), "head": head, "accepted": paths})
     elif a.to:
         if a.to != "spec-gate":
             raise Refused("--to accepts only spec-gate")
@@ -897,28 +976,10 @@ def resolve(a, root, cfg):
         move("awaiting-spec-gate", "to-spec-gate", {})
     elif a.redispatch:
         # Re-run the checkers on the same head after the cause of the park is fixed outside the ticket
-        # (a harness or gate defect, a killed checker). Round unchanged. The head's rows that did not
-        # pass are set aside under results/<head>/superseded-<n>/ so the join cannot read them as
-        # current; the build then runs only the checkers with no row. The reviewer row stays when it
-        # is APPROVE; the verifier and ci rows, written by one verifier run, stay together when they
-        # are VERIFIED and PASS.
+        # (a harness or gate defect, a killed checker). Round unchanged.
         if st != "parked" or parked.get("from") not in ("checks-in-flight", "ready-for-merge"):
             raise Refused(f"--redispatch applies to a sub-ticket parked from its checks; {t['id']} is {st} (from {parked.get('from')})")
-        head = t.get("head")
-        moved = []
-        if head:
-            rows = {k: v.get("status") for k, v in store.results_for(root, head).items()}
-            stale = [] if rows.get("reviewer") == "APPROVE" else ["reviewer"]
-            if not (rows.get("verifier") == "VERIFIED" and rows.get("ci") == "PASS"):
-                stale += ["verifier", "ci"]
-            rd = root / "results" / head
-            todo = [store.result_path(root, head, r) for r in stale if r in rows]
-            if todo:
-                dest = rd / f"superseded-{len(list(rd.glob('superseded-*'))) + 1}"
-                dest.mkdir(parents=True, exist_ok=True)
-                for f in todo:
-                    f.rename(dest / f.name)
-                    moved.append(f.stem)
+        head, moved = t.get("head"), _set_aside_failed_rows(root, t)
         store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
         move("checks-in-flight", "redispatch", {"head": head, "superseded": moved})
     elif a.replan:
@@ -940,7 +1001,31 @@ def resolve(a, root, cfg):
             raise Refused(f"{t['id']} is already closed")
         move("closed", "close", decided("resolve --close"))
     else:
-        raise Refused("resolve needs one of --answer F | --ruling F | --to spec-gate | --redispatch | --replan F | --close")
+        raise Refused("resolve needs one of --answer F | --ruling F | --accept-paths F | --to spec-gate | --redispatch | "
+                      "--replan F | --close")
+
+
+def _set_aside_failed_rows(root: Path, t: dict) -> list[str]:
+    """Move the head's rows that did not pass under results/<head>/superseded-<n>/, so the join cannot
+    read them as current and the build runs only the checkers with no row. The reviewer row stays
+    when it is APPROVE; the verifier and ci rows, written by one verifier run, stay together when
+    they are VERIFIED and PASS. Returns the roles moved."""
+    head = t.get("head")
+    moved: list[str] = []
+    if head:
+        rows = {k: v.get("status") for k, v in store.results_for(root, head).items()}
+        stale = [] if rows.get("reviewer") == "APPROVE" else ["reviewer"]
+        if not (rows.get("verifier") == "VERIFIED" and rows.get("ci") == "PASS"):
+            stale += ["verifier", "ci"]
+        rd = root / "results" / head
+        todo = [store.result_path(root, head, r) for r in stale if r in rows]
+        if todo:
+            dest = rd / f"superseded-{len(list(rd.glob('superseded-*'))) + 1}"
+            dest.mkdir(parents=True, exist_ok=True)
+            for f in todo:
+                f.rename(dest / f.name)
+                moved.append(f.stem)
+    return moved
 
 
 def decision_add(a, root, cfg):
@@ -1546,6 +1631,7 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("id")
     p.add_argument("--answer")
     p.add_argument("--ruling")
+    p.add_argument("--accept-paths", metavar="F", help="a sub-ticket the merge gate refused for undeclared protected paths: accept them under the approved design and return it to its reviewer and verifier")
     p.add_argument("--to")
     p.add_argument("--redispatch", action="store_true")
     p.add_argument("--replan", metavar="F", help="a parked parent whose sub-tickets all merged: back to the planner with F as a ruling")
diff --git a/factory/gitops.py b/factory/gitops.py
index 0acc227..b20da26 100644
--- a/factory/gitops.py
+++ b/factory/gitops.py
@@ -93,8 +93,12 @@ def diff(repo: Path, base: str, head: str) -> str:
     return git(repo, "diff", f"{base}...{head}")
 
 
-def changed_files(repo: Path, base: str, head: str) -> list[str]:
-    out = git(repo, "diff", "--name-only", f"{base}...{head}")
+def changed_files(repo: Path, base: str, head: str, globs: list[str]) -> list[str]:
+    """The paths `base...head` changes (from the merge base) that match one of `globs`, git glob
+    pathspecs (`**` crosses directories, `*` does not). A move lists both its sides. No glob: none."""
+    if not globs:
+        return []
+    out = git(repo, "diff", "--name-only", "--no-renames", f"{base}...{head}", "--", *(f":(glob){g}" for g in globs))
     return [ln for ln in out.splitlines() if ln]
 
 
diff --git a/factory/prompts/reviewer.md b/factory/prompts/reviewer.md
index c94b6b9..f7656fb 100644
--- a/factory/prompts/reviewer.md
+++ b/factory/prompts/reviewer.md
@@ -22,9 +22,10 @@ CHECK, IN THIS ORDER
    would notice that the spec didn't ask for?
 5. Security and data safety: injection, authz, secrets, destructive ops.
 6. Protected paths touched? If the sub-ticket does not declare them,
-   ESCALATE. If it does, list them under ESCALATIONS, finish the review,
-   and give the STATUS the code earns; the merge gate will require a
-   human approval.
+   ESCALATE. If it does, list them under ESCALATIONS for the record,
+   finish the review, and give the STATUS the code earns. The merge
+   gate merges a path the approved spec's Risk section declares with no
+   further approval, and refuses and parks one it does not declare.
 7. The coding standard at {coding standard}: a finding against it
    carries the tag and severity the standard gives it. Not style.
 8. PR description: could the operator at the gate read its What changed
diff --git a/factory/prompts/spec_writer.md b/factory/prompts/spec_writer.md
index c60265a..28b4892 100644
--- a/factory/prompts/spec_writer.md
+++ b/factory/prompts/spec_writer.md
@@ -84,7 +84,10 @@ openspec/changes/<ticket id>/ (schema spec-factory).
 ## Open questions   none | list
 ## Decisions        none | one line per design call this change makes,
                     including each answered open question
-## Risk             blast radius; every protected path this will touch
+## Risk             blast radius; every protected path this will touch,
+                    declared on one line the merge gate reads:
+                    Protected paths: none | `<path or glob>`, `<path or glob>`
+                    one path or glob per entry, no brace lists
 ## Operator steps   (optional) actions or checks on live or protected state
                     that only the operator can perform, after merge; not
                     acceptance; the human approves them at the spec gate
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index 48a2dfe..b76619c 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -194,6 +194,9 @@ async function buildOne(st) {
       await transition(st, 'ready-for-merge', null, 'Build')
       const m = await clerk(`${BIN} merge ${st}`, 'Build', `merge ${st}`)
       if (m.ok) { log(`${st} merged: ${m.main_after}`); return }
+      // A refusal that starts `BLOCKED ` is the merge gate blocking the merge (an undeclared protected
+      // path): park with it verbatim, for `resolve --accept-paths` or `resolve --ruling`.
+      if (typeof m.error === 'string' && m.error.startsWith('BLOCKED ')) { await park(st, m.error, outs, 'Build'); return }
       // The gate refused. Ask the join again: a moved integration branch is a conflict run, bounded there.
       const again = await clerk(`${BIN} ticket join ${st}`, 'Build', `join ${st} after refusal`)
       if (again.ok && again.decision === 'conflict') { await transition(st, 'ready-for-implementer', null, 'Build'); continue }
diff --git a/tests/factory/test_merge_protected_paths.py b/tests/factory/test_merge_protected_paths.py
new file mode 100644
index 0000000..0e87552
--- /dev/null
+++ b/tests/factory/test_merge_protected_paths.py
@@ -0,0 +1,296 @@
+"""The merge gate refuses a changed protected path the pinned spec does not declare (spec-factory
+T-0033, issue #57). The pinned spec's Risk section declares protected paths on one line,
+`Protected paths: none | `<path or glob>`, ...`; the operator approves it at the spec gate. At merge,
+`factory merge` refuses each changed protected path that line does not declare, naming it, with an
+error that starts `BLOCKED from merge gate: `, and the build parks the sub-ticket with that error.
+`resolve --accept-paths F` accepts the paths for that sub-ticket and returns it to its checks;
+`resolve --ruling F` sends it back to its implementer. A ruling on a reviewer's ESCALATE returns the
+sub-ticket to its checks.
+
+Black-box through `bin/factory`, each case on the spec's t0033-gate.sh fixture: a scratch instance
+whose protected paths are `core/**`, `bin/tool` and `~/.secret/**`, a throwaway store and a scratch
+target whose main holds core/a.py, core/b.py, bin/tool and docs/d.md.
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+FIXTURE = REPO / "tests" / "factory" / "fixtures" / "instance"
+
+# Drives factory/workflows/build.js with a stub clerk: each command gets the reply of the longest key
+# its `bin/factory` arguments start with (a list is used in turn, the last one repeating). Prints
+# `park: <reason>` per park.
+WF_DRIVER = r"""
+import { readFileSync } from 'node:fs'
+const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
+  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(process.argv[3]) }
+const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
+const lines = []
+const agent = async (prompt) => {
+  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
+  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
+  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
+  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
+  if (p) lines.push(`park: ${p[1]}`)
+  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
+  let r = key ? R[key] : { out: { ok: true } }
+  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
+  return { stdout: JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
+}
+const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
+await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
+console.log(lines.join('\n'))
+"""
+
+
+class Gate:
+    """The t0033-gate.sh fixture. `risk` is the line T-0001's approved spec carries in its Risk
+    section (None: T-0001 is never approved and has no sub-ticket; the commit lands on T-0001's own
+    branch). `changes` as in the fixture: `p` appends to p, `p-` deletes p, `p>q` renames p to q."""
+
+    def __init__(self, tmp_path: Path, risk: str | None, changes: str):
+        self.tmp = tmp_path
+        inst, self.store, self.target = tmp_path / "inst", tmp_path / "store", tmp_path / "t"
+        inst.mkdir()
+        shutil.copy(FIXTURE / "context.md", inst / "context.md")
+        kept = [ln for ln in (FIXTURE / "instance.yaml").read_text().splitlines()
+                if not ln.startswith(("protected_paths:", "  infra:"))]
+        (inst / "instance.yaml").write_text("\n".join(kept + [
+            "protected_paths:", '  harness: ["core/**", "bin/tool"]', '  credentials: ["~/.secret/**"]']) + "\n")
+        self.env = {**os.environ, "FACTORY_INSTANCE": str(inst), "FACTORY_STATE": str(self.store),
+                    "FACTORY_REPO": str(self.target), "FACTORY_INTEGRATION_BRANCH": "main",
+                    "PYTHONDONTWRITEBYTECODE": "1"}
+        subprocess.run(["git", "init", "-q", "-b", "main", str(self.target)], check=True)
+        for f in ("core/a.py", "core/b.py", "bin/tool", "docs/d.md"):
+            (self.target / f).parent.mkdir(parents=True, exist_ok=True)
+            (self.target / f).write_text("x\n")
+        self.git("add", "-A")
+        self.git("commit", "-qm", "init")
+        for tid, line in (("T-0001", risk), ("T-0002", "Protected paths: `core/b.py`")):
+            self.spec(tid, line)
+        self.sub = "T-0001"
+        if risk is not None:
+            plan = tmp_path / "plan.md"
+            plan.write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
+            self.ok("subticket", "add", "T-0001", "--file", str(plan))
+            self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
+            self.sub = "T-0001.1"
+        branch = f"factory/{self.sub}"
+        self.git("checkout", "-qb", branch)
+        for c in changes.split():
+            if ">" in c:
+                src, dst = c.split(">")
+                (self.target / dst).parent.mkdir(parents=True, exist_ok=True)
+                self.git("mv", src, dst)
+            elif c.endswith("-"):
+                self.git("rm", "-q", c[:-1])
+            else:
+                (self.target / c).parent.mkdir(parents=True, exist_ok=True)
+                with (self.target / c).open("a") as fh:
+                    fh.write("y\n")
+                self.git("add", c)
+        self.git("commit", "-qm", "work")
+        self.head = self.git("rev-parse", "HEAD")
+        self.git("checkout", "-q", "main")
+        self.main = self.git("rev-parse", "main")
+        self.ok("ticket", "set", self.sub, "status=checks-in-flight", f"branch={branch}", f"head={self.head}")
+        self.record("verifier", "Gate suite: PASS\nSTATUS: VERIFIED", "run-0001-verifier")
+        self.record("reviewer", "STATUS: APPROVE", "run-0002-reviewer")
+
+    def spec(self, tid: str, line: str | None) -> None:
+        req, spec = self.tmp / "req.md", self.tmp / "spec.md"
+        req.write_text(f"# F {tid}\n\nDo x.\n")
+        spec.write_text(f"=== proposal.md\n## Problem\nx\n## Risk\nBlast radius: small.\n{line or ''}\n"
+                        "=== design.md\n## Proposed change\nA. x\n")
+        self.ok("ticket", "new", "--file", str(req))
+        self.ok("ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t")
+        self.ok("spec", "add", tid, "--file", str(spec))
+        self.ok("ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+        if line is not None:
+            self.ok("ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t")
+            self.ok("approve-spec", tid)
+
+    def record(self, role: str, body: str, run: str) -> None:
+        out = self.tmp / f"{run}.md"
+        out.write_text(f"Commit: {self.head}\n{body}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+        self.ok("results", "record", self.sub, "--head", self.head, "--role", role, "--output", str(out), "--run", run)
+
+    def git(self, *argv: str) -> str:
+        cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=self.target,
+                            capture_output=True, text=True, check=True)
+        return cp.stdout.strip()
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def refused(self, *argv: str) -> str:
+        cp = self.cli(*argv)
+        assert cp.returncode == 2, cp.stdout + cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])["error"]
+
+    def ticket(self, tid: str | None = None) -> dict:
+        return yaml.safe_load((self.store / "tickets" / f"{tid or self.sub}.yaml").read_text())
+
+    def park_with_merge_error(self) -> str:
+        error = self.refused("merge", self.sub)
+        self.ok("ticket", "park", self.sub, "--reason", error)
+        return error
+
+    def rows(self) -> list[str]:
+        return sorted(p.name for p in (self.store / "results" / self.head).glob("*.yaml"))
+
+    def ruling(self, text: str) -> str:
+        f = self.tmp / "ruling.md"
+        f.write_text(text)
+        return str(f)
+
+
+def test_an_undeclared_protected_path_is_refused_by_name_and_nothing_changes(tmp_path):
+    g = Gate(tmp_path, "Protected paths: `core/a.py`", "core/a.py core/b.py bin/tool docs/d.md")
+    before = g.ticket()
+    error = g.refused("merge", g.sub)
+    assert error == "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: bin/tool, core/b.py"
+    assert not any(c in error for c in "`$\"")
+    assert g.git("rev-parse", "main") == g.main
+    assert g.ticket() == before
+    events = [json.loads(ln) for p in sorted((g.store / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]
+    refused = [e for e in events if e["event"] == "merge.refused"]
+    assert len(refused) == 1 and refused[0]["paths"] == ["bin/tool", "core/b.py"]
+    assert refused[0]["reason"] == "protected paths not declared" and refused[0]["head"] == g.head
+
+
+@pytest.mark.parametrize("risk, changes", [
+    ("Protected paths: none", "core/b.py"),                 # T-0002 declares core/b.py, not T-0001
+    ("Protected paths: none", "core/b.py>docs/b.py"),       # moved out of the protected tree
+    ("Not touched: `core/b.py`", "core/b.py"),              # a Risk line in another form
+    ("```\nProtected paths: `core/b.py`\n```", "core/b.py"),  # inside a fenced code block
+    ("Protected paths: `core/{a,b}.py`", "core/b.py"),      # a brace list is one literal entry
+])
+def test_nothing_but_the_pinned_specs_own_declaration_line_declares_a_path(tmp_path, risk, changes):
+    g = Gate(tmp_path, risk, changes)
+    error = g.refused("merge", g.sub)
+    assert error == "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"
+    assert g.git("rev-parse", "main") == g.main
+
+
+@pytest.mark.parametrize("risk, changes", [
+    ("Protected paths: `core/**`, `bin/tool`", "core/a.py core/new/c.py bin/tool"),
+    ("- Protected paths: `core/b.py`.", "core/b.py docs/d.md"),
+    ("Protected paths: none", "docs/d.md docs/e.md"),
+])
+def test_a_declared_protected_path_or_an_unprotected_one_merges(tmp_path, risk, changes):
+    g = Gate(tmp_path, risk, changes)
+    assert g.ok("merge", g.sub)["state"] == "merged"
+    assert g.git("rev-parse", "main") != g.main
+
+
+def test_a_ticket_with_no_parent_and_no_approved_spec_declares_nothing(tmp_path):
+    g = Gate(tmp_path, None, "core/a.py")
+    assert g.refused("merge", g.sub) == (
+        "BLOCKED from merge gate: protected paths not declared (T-0001 has no approved spec): core/a.py")
+
+
+def test_the_build_parks_a_merge_gate_refusal_with_its_reason(tmp_path):
+    node = shutil.which("node")
+    assert node, "node must be on PATH: this case runs factory/workflows/build.js"
+    error = "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"
+    replies = {
+        "ticket show T-0001 ": {"out": {"ok": True, "state": "planned"}},
+        "ticket ready-implementers": [
+            {"out": {"ok": True, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"],
+                     "subtickets": ["T-0001.1"], "closed": []}},
+            {"out": {"ok": True, "ready": [], "resumable": [], "remaining": ["T-0001.1"],
+                     "subtickets": ["T-0001.1"], "closed": []}}],
+        "ticket show T-0001.1": {"out": {"ok": True, "state": "checks-in-flight"}},
+        "ticket head": {"out": {"ok": True, "head": "ab" * 20}},
+        "results show": {"out": {"ok": True, "rows": {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"},
+                                 "missing": []}},
+        "ticket join": {"out": {"ok": True, "decision": "merge", "reason": "ci PASS + APPROVE + VERIFIED"}},
+        "merge": {"out": {"ok": False, "error": error}, "exit": 2},
+    }
+    driver = tmp_path / "wf.mjs"
+    driver.write_text(WF_DRIVER)
+    cp = subprocess.run([node, str(driver), "factory/workflows/build.js", json.dumps(replies)],
+                        capture_output=True, text=True, cwd=REPO)
+    assert cp.stdout.strip() == f"park: {error}", cp.stdout + cp.stderr
+
+
+def test_accepting_the_refused_paths_returns_the_sub_ticket_to_its_checks_and_it_merges(tmp_path):
+    g = Gate(tmp_path, "Protected paths: `core/a.py`", "core/a.py core/b.py bin/tool")
+    g.park_with_merge_error()
+    pr = g.ticket()["round"]["pr"]
+    g.ok("resolve", g.sub, "--accept-paths", g.ruling("Ruling: part of the approved design.\n"))
+    t = g.ticket()
+    assert t["status"] == "checks-in-flight" and t["parked"] is None and t["round"]["pr"] == pr
+    assert t["accepted_paths"] == ["bin/tool", "core/b.py"]
+    assert g.rows() == ["ci.yaml", "reviewer.yaml", "verifier.yaml"]
+    assert (g.store / "approvals" / g.sub / "ruling-1.md").read_text() == "Ruling: part of the approved design.\n"
+    assert g.ok("merge", g.sub)["state"] == "merged"
+
+
+def test_accepting_paths_is_refused_on_any_other_park_and_writes_nothing(tmp_path):
+    g = Gate(tmp_path, "Protected paths: none", "core/b.py")
+    g.ok("ticket", "park", g.sub, "--reason", "ESCALATE from reviewer")
+    before = g.ticket()
+    error = g.refused("resolve", g.sub, "--accept-paths", g.ruling("Ruling: x\n"))
+    assert error.startswith("--accept-paths applies to a merge gate park (BLOCKED from merge gate); T-0001.1 is parked")
+    assert g.ticket() == before and not list((g.store / "approvals" / g.sub).glob("ruling-*"))
+
+
+def test_accepting_paths_is_refused_when_the_head_is_not_the_branch_tip(tmp_path):
+    g = Gate(tmp_path, "Protected paths: none", "core/b.py")
+    g.park_with_merge_error()
+    g.git("checkout", "-q", "factory/T-0001.1")
+    g.git("commit", "-q", "--allow-empty", "-m", "later")
+    g.git("checkout", "-q", "main")
+    before = g.ticket()
+    assert "is not the branch tip" in g.refused("resolve", g.sub, "--accept-paths", g.ruling("Ruling: x\n"))
+    assert g.ticket() == before and not list((g.store / "approvals" / g.sub).glob("ruling-*"))
+
+
+def test_accepting_paths_is_refused_when_no_undeclared_protected_path_remains(tmp_path):
+    g = Gate(tmp_path, "Protected paths: none", "core/b.py")
+    g.park_with_merge_error()
+    g.ok("resolve", g.sub, "--accept-paths", g.ruling("Ruling: x\n"))
+    g.ok("ticket", "park", g.sub, "--reason", "BLOCKED from merge gate: again")
+    before = g.ticket()
+    error = g.refused("resolve", g.sub, "--accept-paths", g.ruling("Ruling: y\n"))
+    assert error == f"nothing to accept: T-0001.1 has no undeclared protected path at {g.head[:9]}"
+    assert g.ticket() == before and len(list((g.store / "approvals" / g.sub).glob("ruling-*"))) == 1
+
+
+def test_a_ruling_on_a_merge_gate_refusal_sends_the_sub_ticket_back_to_its_implementer(tmp_path):
+    g = Gate(tmp_path, "Protected paths: none", "core/b.py")
+    g.park_with_merge_error()
+    pr = g.ticket()["round"]["pr"]
+    g.ok("resolve", g.sub, "--ruling", g.ruling("Ruling: take core/b.py out of this change.\n"))
+    t = g.ticket()
+    assert t["status"] == "ready-for-implementer" and t["round"]["pr"] == pr and not t.get("accepted_paths")
+
+
+def test_a_ruling_on_a_reviewer_escalation_returns_the_sub_ticket_to_its_checks(tmp_path):
+    g = Gate(tmp_path, "Protected paths: none", "docs/d.md")
+    g.record("reviewer", "STATUS: ESCALATE", "run-0003-reviewer")
+    g.ok("ticket", "park", g.sub, "--reason", "ESCALATE from reviewer")
+    pr = g.ticket()["round"]["pr"]
+    g.ok("resolve", g.sub, "--ruling", g.ruling("Ruling: the escalation is settled.\n"))
+    t = g.ticket()
+    assert t["status"] == "checks-in-flight" and t["round"]["pr"] == pr
+    assert g.rows() == ["ci.yaml", "verifier.yaml"]
+    assert [p.name for p in (g.store / "results" / g.head / "superseded-1").iterdir()] == ["reviewer.yaml"]
+    assert t["history"][-1]["superseded"] == ["reviewer"]
+    assert (g.store / "approvals" / g.sub / "ruling-1.md").exists()
