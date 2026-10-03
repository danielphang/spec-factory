## Critic review, round 1 (spec v1, ticket T-0004)

What I checked, from `~/dev/spec-factory` on `main` at `b2674dd` (working tree has only `intake/state/**` changes, none under `plans/`):

- Cited paths and lines. `sed -n 27p plans/P0-intake-skeleton.md` is the Part A row as quoted. Line 40 begins `Black-box, numbered P0-1..` and names only `factory: command not found` / "no such workflow". Line 42 is the P0-1 line (one physical line). Risk is lines 63–68, four bullets, the `claude -p` bullet at line 66, "P0-2's `meta.yaml` check" at line 67. `## Tests to change: none.` is line 70, so the item-1 awk range closes. `specs/build-harness.md:118` is R6 ("Role agent definitions carry `tools:` allowlists"), `:296` is I.4 ("Tool restriction is the agent definition's `tools:` (R6)"), `:136-139` is the agent-file layout, `:413` (item 54) greps `factory-critic.md`. Reference harness `~/dev/nanobot-upstream` on `feat/lionbot-v3` at `053a7bd5e`: `factory/workflows/intake.js:24-26` is the `inlineRoles` comment as quoted; `grep -n agentType` → lines 49, 83, 89 with `INLINE ? 'general-purpose' : …`; `ls .claude/agents/` lists the six files named, and `factory-spec-critic.md` is the critic's name there.
- The two "today" grep claims in Evidence reproduce: the Risk-range grep for `existed when the session started` → `0`; the P0 list → `- P0-1 - P0-2 … - P0-8`. `grep -rnoE "P0-[0-9]+"` outside the plan hits `issues/04_p0_agents_dir.md` (P0-2, P0-5) and `issues/06_p05_grep_vs_inline_scripts.md` (5× P0-5), as stated, so not renumbering is right.
- Claude Code docs (`https://code.claude.com/docs/en/sub-agents`, fetched this run) contain all three quoted sentences verbatim, including "When you add a directory with `--add-dir` or `/add-dir`, Claude Code also loads its `.claude/agents/` folder". The spec's reading (loaded at start, never watched) is correct, and it is why the spec's rule is stronger than the issue draft's "create the directory first". That deviation from `issues/04_p0_agents_dir.md` is explained in the spec, not silent.
- Acceptance, "today" side on `main`: items 1, 2, 4 give `0`, `- P0-1 - P0-2 … - P0-8 `, `0`; items 6, 7, 8 give no output with exit 1, 1, 0. Item 5 trivially `FAIL`s today (no P0-9 line).
- Acceptance, patched side: I applied sections A, B and C exactly as written in a scratch clone (outside the repo; `git diff --stat main...HEAD` → `1 file changed, 3 insertions(+), 1 deletion(-)`). Items 1–4 → `1`, `- P0-1 - P0-9 - P0-2 … - P0-8 `, `1`, `1`. Items 6–8 → no output, exit 1 / 1 / 0. Item 5 → `PASS` on Claude Code `2.1.286` (one Haiku call; the `awk -F'\140' … $6` extraction yields exactly the `diff <(…) <(…)` command). Negative probe: with `factory-stub.md` rewritten without `description:`, the same command prints `5d4` / `< factory-stub` and exits 1, so P0-9 fails for an unregistered agent rather than passing on empty output.
- Scope and paths: one file under `plans/`, which is neither a protected nor a guardrail path. The design doc, `specs/`, `prompts/` and `issues/` are untouched (item 7 enforces it). "Tests to change: none" is correct; the repo has no suite.

Findings:

[NIT] 2 Proposed change B, P0-9 text
Problem: On macOS, `ls … | wc -l` prints `       6` with leading spaces, so the written expectation `` → `6` `` is not byte-exact for the operator reading the plan.
Evidence: BSD `wc -l` pads its count; item 3 of this spec deliberately greps the plan for `` → `6` ``, so the wording is pinned.
Suggested fix: None required; a human reads this value and the registration diff is the part item 5 executes. Leave as is.

No blocking or should-fix findings. The spec deviates from the requester's proposed fix with a stated, verified reason; it makes no product decision (the `factory-critic` vs `factory-spec-critic` naming and whether a fallback run counts are explicitly left to a human); the NEW items fail today for the stated reasons and item 5 executes the plan's own command against fixtures, so a stub P0-9 line would not pass. An implementer can apply A, B and C verbatim without a question.

Out-of-scope observations: I agree with the spec's own list. One addition: the reference harness gives Triage, Spec writer, Spec critic and Planner `tools: Read, Grep, Glob, Bash, Write` (`grep -n '^tools:' ~/dev/nanobot-upstream/.claude/agents/factory-*.md`), which conflicts with R6's "no Edit/Write" for checkers and read-only authors independently of this ticket; the spec notes this already.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high — every cited line and symbol checked; all eight acceptance items run on both `main` and a patched scratch clone with the stated results; the one claim I did not reproduce is the original in-session "Agent type not found", which the spec itself marks as unreproduced and which the reference harness comment and the docs corroborate.
ESCALATIONS: none
