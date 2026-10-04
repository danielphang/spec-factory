## Critic review of T-0019 (v1)

Spot-checks performed on `main` at `17efb50`:
- Paths: `factory/subtickets.py` line 17 is the quoted `FIELD_RE`, line 62 the `"depends_on": [], "parallel_safe": False` default, line 88 the `startswith("yes")` read; `factory/compose.py` lines 128-132 render the gate commands verbatim in "Where you work" for build roles only; `factory/instance.py` lines 168-179 (`fill_preamble`) are the only `protected_paths` reader; `.factory/instance.yaml` line 19 is `credentials: ["~/.nanobot/**"]`; `grep -rn HOME factory bin` prints nothing; `factory/workflows/build.js` line 200 parks with `harness-bug: subticket add:`; `factory/cli.py` lines 395-397 map `ValueError` to `Refused`; `.factory/answers/T-0014-plan-normalised.md` and issue rows #13, #36, #37 in `dev/issues.md` exist. The Nanobot `run-0080-implementer/output.md` lines 92-93 carry the quoted `FileExistsError` and cause (read only).
- Acceptance commands run with the GIVEN fixtures on a scratch store: "Dash-bulleted field lines" printed all three sub-tickets `ready-for-implementer`, `depends_on: []`, `parallel_safe: false`; "A sub-ticket with no Depends on line" printed the success JSON, `exit=0`, three ticket files; "A triage input's wrapper" printed `fresh_home=no real_home_untouched=yes cache=` and the input has three `## ` sections; "run_env cannot set HOME" printed `exit=0 input=written`; both `SAME` checks print `SAME`; the planner-prompt greps print `0`. Every "today" result in verification.md that I ran matches.
- Tests to change: `test_instance.py` lines 265-271 (`startswith` on context then `## Output file`), 274-288 (compares every preamble line except 0, i, w, so added lines are compared), 303 (byte-identical copy); every plan fixture I found (`test_shepherd.py` 295/350/408, `test_parent_close_reuse.py` 15-18, both stub `planner-1.md`) has a `Depends on:` line per sub-ticket. "none" is right.

Findings:

[BLOCKING] 6 Operator steps, first paragraph
Problem: "the runtime" is a term specific to this system and is glossed only in Risk, which is not one of the sections the gate operator is assumed to read, so the operator cannot tell from Problem, Evidence, Decisions or Operator steps what has to "move" before step 1 applies.
Evidence: the gloss "the runtime, the pinned checkout of the harness that runs tickets" appears once, in Risk (line 122 of proposal.md); Operator steps line 136 uses "runtime" bare. The rubric makes an unglossed system term in the first paragraph of a human-facing section BLOCKING even when inferable. The fix is one phrase.
Suggested fix: in Operator steps, write "once the runtime (the pinned checkout of the harness that runs tickets) has moved to a revision with this change", and leave the Risk sentence as is or shorten it.

[SHOULD-FIX] 4 Decisions / Operator steps
Problem: this repository's own instance gets no `run_env`, so every implementer and verifier worktree here resolves `uv`'s cache under the throwaway `HOME` and re-downloads its packages on each fresh worktree, and the spec neither decides that this cost is acceptable nor gives the operator a step to add `run_env` here as it does for Nanobot.
Evidence: Evidence paragraph 6 reports "uv installed 6 packages" in a fresh worktree under a throwaway `HOME`; `.factory/instance.yaml` is out of scope (line 102), so only an Operator step can set it; Operator steps cover Nanobot only.
Suggested fix: either add an Operator step 3 for this repo's `instance.yaml` (`UV_CACHE_DIR`, and `UV_PYTHON_INSTALL_DIR` if a managed Python is in use), or add a Decision that this repo runs without `run_env` because the re-download is six small packages per worktree.

[SHOULD-FIX] 3 Proposed change (whole)
Problem: the ticket bundles two independent faults (role test isolation: A, B, E2, E3, F-isolation; plan parsing: C, D, F-plan-fields) in one PR of about a dozen files without marking NEEDS-SPLIT or naming the seam, so a reviewer of either half reads the other's diff and a defect in one blocks the other.
Evidence: Problem names them as two faults with no shared code; Root cause lists disjoint files for each; only E1's changelog entry joins them.
Suggested fix: mark NEEDS-SPLIT with the seam above, and say which half carries the changelog entry (or that each adds its own clause to one entry number, written by whichever merges first).

[NIT] 6 Problem, paragraph 3
Problem: "every one of them parked" uses the ticket state `parked` without saying what it is.
Evidence: no gloss anywhere in the human-facing sections; Risk later says "parks the parent with the refusal text".
Suggested fix: "were set aside as `parked`, the state for a ticket the build has stopped on".

[NIT] 2 Acceptance: "This repo's gate suite passes under a throwaway HOME" and "The harness suite passes"
Problem: the two scenarios run the same two-minute suite twice, once wrapped and once bare, and after part A the preamble tells the role to run the bare one through the wrapper anyway, so the second adds no evidence.
Evidence: role-run-isolation spec lines 291-293 and harness-docs spec lines 367-369; `factory/prompts/implementer.md` line 15 counts an acceptance command that ran a gate command "exactly as written" as that gate's run, and after B4 the handed form is the wrapped one.
Suggested fix: drop the bare scenario, or keep only it and note that the wrapped form is the gate command as handed.

[NIT] 4 Part A rule text
Problem: "That includes every command your briefing, ticket or spec gives you" invites a role to run `git commit` through the wrapper, where a fresh `HOME` hides `~/.gitconfig` and the commit fails for want of an identity; the failure is loud, not silent, so this is wording, not a defect.
Evidence: the rule's first bullet scopes itself to "test, script or prototype" and then widens to "every command"; nothing in the harness sets `user.name` in a worktree (`grep -rn "user.name" factory` was not run; I did not verify).
Suggested fix: "every test or check command your briefing, ticket or spec gives you".

Out-of-scope observations:
- Neither target runs the `agents/` role definitions today (`README.md` line 272: `inlineRoles: true` on every target), so the stale planner OUTPUT block in `agents/factory-planner.md` is inactive; the spec's observation stands and is correctly out of scope.
- Each wrapper invocation leaves one temporary directory behind; nothing removes it. Harmless on a workstation; worth a line in the design doc paragraph if anyone runs this on a long-lived host.

STATUS: REVISE
CONFIDENCE: high; every cited path and all seven acceptance commands I ran match the spec's claims, and the one BLOCKING finding is a rubric-6 gloss with a one-phrase fix.
ESCALATIONS: none
