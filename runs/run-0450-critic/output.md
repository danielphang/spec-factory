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

STATUS: APPROVE
CONFIDENCE: high; every round-1 finding is fixed as described, the fixes were checked against the tree at `0ba4e4f`, and no command or expected result changed between v1 and v2.
ESCALATIONS: none
