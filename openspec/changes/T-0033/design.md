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

