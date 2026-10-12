## Acceptance

- The four dead definitions are gone and nothing names them → NEW; today it prints `4 0`.
- No harness or test file names the force-push setting → NEW; today it prints `4`.
- Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write → NEW; today it prints `2 3 3`.
- No harness module has three blank lines in a row → NEW; today it prints `1` (`factory/cli.py:1969`, the third of the four blank lines at `:1967-1970`).
- The three stale texts are gone → NEW; today it prints `3`.
- The repo-root helper takes no argument and every caller passes none → NEW; today it prints `13 0 0`.
- The harness has no unused imports or variables → REGRESSION; today it prints `All checks passed!`.
- The harness suite passes, and only the force-push test lines change under tests → REGRESSION; today `577 passed` and no diff under `tests`. The implementer's in-flight refusal and the plan whole-spec refusal keep their coverage through the existing suite. The second half shows that their test files are unchanged.
- A second intake run on a ticket is refused with the same text → REGRESSION; today it prints the three lines shown, run on `0ba4e4f`.

## Responses

- [BLOCKING] 6 Decisions, first bullet → FIXED. The bullet now opens by glossing the spec store (the folder of requirement files that says what the harness does), a capability (a named area of behaviour, with build-dispatch as the example), and triage (the first role, which accepts the request). It quotes the store's refusal text instead of using "delta part" as a term. Evidence's last paragraph now glosses "current truth" (the archived requirement files) at its first use. While there, I also glossed the other factory names in the human sections: role, ticket store, the per-repository configuration file and its template, `factory run start`, `factory init`, the Workflow scripts, `_start_build_run` and compose. I also added a line after each Evidence output saying what it shows (writing standard rule 5).
- [SHOULD-FIX] 1 Evidence, last paragraph → FIXED. Both paths now read `.factory/store/openspec/specs/...`. I re-ran the check from `~/dev/spec-factory` at `0ba4e4f`: `ls .factory/store/openspec/specs/` lists 14 capabilities, including `harness-suite`, and `grep -rln 'already has run' .factory/store/openspec/specs/` lists no file (exit 1).
- [NIT] 1 Root cause item 12 and Design C, last bullet → FIXED. Both now say `:1967-1970`. Confirmed with `awk 'NR>=1966&&NR<=1971'`: line 1966 is `return ap`, lines 1967-1970 are empty and line 1971 is the fence comment. The Evidence paragraph and the Acceptance line for the blank-lines scenario now say the awk hit at `:1969` is the third of those four lines.

No scenario, command or expected result changed from v1. The critic ran each NEW scenario on `0ba4e4f` and got the "today" values listed above.

## Critic rounds

round 1 · spec v1 · run-0448-critic · REVISE

## Round 1 review of T-0044 spec v1 (harness de-bloat)

What I checked on `main` at `0ba4e4f`, from `~/dev/spec-factory`:
- Cited paths and lines: `factory/cli.py:199-240` (run_start), `:377`, `:778`, `:1469`, `:1960-1972`; `factory/gitops.py:18-19`, `:202-211` (last lines of a 211-line file); `factory/store.py:1-4`, `:15`, `:29`; `factory/specstore.py:8-9`, `:20`, `:202`; `factory/compose.py:110`, `:278-350`, `:420`; `factory/instance.py:88-90`; `tests/factory/test_instance.py:109,113,354`; `.factory/instance.yaml:34`; `~/dev/nanobot-upstream/.factory/instance.yaml:65` (read only). All match the spec's text and the `force_push_allowed` hit list.
- Ran the six grep/awk scenarios of `harness-code` as written, under the running-code wrapper: `4 0`, `2 3 3`, `1`, `13 0 0`, `3` (the stale-text count). Each equals the "today" value under Acceptance, so each NEW item fails today for the stated reason.
- Ran the build-dispatch scenario (throwaway target, no suite): printed `T-0001 already has run run-0001-triage in flight`, `exit=2`, `run-0001-triage`, as the spec says.
- Rubric 1 test search: the merged refusal text is pinned by `tests/factory/test_whole_spec_plan.py:200`, `test_p0_cli.py:97`, `test_shepherd.py:533`; the text does not change, so none belongs under Tests to change. No test names `run_gates`, `STATES`, `OPS`, `store.load_config`, `prompt_name`, `ensure_gitignore`, `repo_root(` or the `not supported yet` message. "Tests to change" is exactly the two files the key removal breaks.
- Design E's F841 claim: at every one of the 11 `cli.py` callers and `compose.py:110`, `cfg` is a parameter (or closure variable at `:1219`) with other uses in the same function; no local `cfg =` assignment. The claim holds.
- Rubric 5: "Approved changes not yet archived: none". T-0046/T-0047 are named under Risk with the overlap stated. The T-0023 temp-dir decision the suite scenario cites exists (decision log, 2026-10-04).
- Not run: the suite and `uvx ruff` (REGRESSION items; the verifier runs them).

Findings:

[BLOCKING] 6 Decisions, first bullet
Problem: The first bullet uses five names specific to this system with no gloss: "capability", "spec store", "delta part", "triage output" and "build-dispatch"; the operator new to the system cannot tell what is being added or why it must be added somewhere.
Evidence: Problem and Evidence gloss none of them. Evidence's last paragraph says "Current truth opened" and "current-truth requirement", also unglossed. `docs/writing.md` rule 2 and rubric 6 make an unglossed term in a human section's first paragraph blocking.
Suggested fix: Open the bullet with one sentence such as "The spec store is the folder of requirement files (`.factory/store/openspec/specs/<capability>/spec.md`, one folder per capability, a named area of behaviour) that each ticket must add to; a change with no such addition is refused", then name `harness-code` and `build-dispatch` as two such folders; gloss "current truth" (the archived requirement files) where Evidence first uses it.

[SHOULD-FIX] 1 Evidence, last paragraph
Problem: The paths `openspec/specs/harness-suite/spec.md` and `openspec/specs/*/spec.md` do not exist from `~/dev/spec-factory`, where the paragraph says the checks ran.
Evidence: `ls openspec/specs/` → "No such file or directory"; the store's tree is `.factory/store/openspec/specs/...` (the capability index in my input gives those absolute paths).
Suggested fix: Write both paths as `.factory/store/openspec/specs/...`.

[NIT] 1 Root cause item 12 and Design C, last bullet
Problem: The four blank lines are at `factory/cli.py:1967-1970`, not `:1966-1969`.
Evidence: `awk 'NR>=1966&&NR<=1971'` shows `1966: return ap`, `1967-1970` empty, `1971` the fence comment; the awk scenario reports the third blank at `:1969`, which agrees.
Suggested fix: Change both line ranges to `:1967-1970`.

Prior findings: none (round 1).

round 2 · spec v2 · run-0450-critic · APPROVE

## Round 2 review of T-0044 spec v2 (harness de-bloat)

Scope of this round: whether the three round-1 findings are resolved, and the text the v1-to-v2 diff changed (Problem, Evidence prose, Decisions, Root cause item 12, Design C last bullet, the blank-lines Acceptance line, the new Responses section). The diff shows no scenario, command or expected result changed; the round-1 checks of every cited line and every runnable NEW scenario on `0ba4e4f` still stand.

What I checked on `main` at `0ba4e4f`, from `~/dev/spec-factory` (working tree clean):
- `ls .factory/store/openspec/specs/ | wc -l` → `14`; `.factory/store/openspec/specs/harness-suite/spec.md` exists; `grep -rln 'already has run' .factory/store/openspec/specs/` prints nothing, exit 1. The corrected Evidence paths and the "no current-truth requirement covers the refusal" claim hold.
- `awk 'NR>=1966&&NR<=1971' factory/cli.py`: 1966 `return ap`, 1967-1970 empty, 1971 the fence comment. The corrected range `:1967-1970` is right, and `:1969` is its third line.
- `factory/store.py:1-4` and `factory/cli.py:205-213` match the spec's description (docstring line 3 is the commit-and-push sentence; the two in-flight branches at `:207-208` and `:211-212` raise identical text with the reviewer/verifier branch between them).
- Read the human-facing sections as the gate operator against `docs/writing.md`: the Problem's first paragraph now says what the harness is, what is wrong (dead code, an unread setting, stale comments) and for whom (every reader of the harness, and operators misled by the setting). Each factory name in Problem, Evidence, Decisions and Operator steps is glossed where it first appears: role, ticket store, configuration file and template, `factory run start`, `factory init`, Workflow scripts, current truth, spec store, capability, triage, `_start_build_run`, compose. Each Evidence output is followed by what it shows (rule 5).

Prior findings:
- [BLOCKING] 6 Decisions, first bullet → RESOLVED. The bullet opens with the spec store, capability and build-dispatch glossed, quotes the store's refusal text in place of "delta part", and names triage as the first role. "Current truth" is glossed at its first use in Evidence.
- [SHOULD-FIX] 1 Evidence, last paragraph → RESOLVED. Both paths read `.factory/store/openspec/specs/...` and resolve from `~/dev/spec-factory` (checked above).
- [NIT] 1 Root cause item 12 and Design C, last bullet → RESOLVED. Both say `:1967-1970`; the Acceptance line explains the `:1969` awk hit as the third of those lines (checked above).

New findings on changed text: none. The added glosses are short and factual; none makes the spec vaguer or longer than the gloss needs. The claim in Responses that no scenario changed agrees with the diff.

Not run this round: the suite and `uvx ruff` (REGRESSION items; the verifier runs them). Not re-run: the six grep/awk scenarios and the build-dispatch scenario, whose commands are byte-identical to v1 and were run in round 1 on the same commit.
