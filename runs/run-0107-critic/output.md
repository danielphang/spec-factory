Round 1 review of the T-0013 spec (v1), checked on `~/dev/spec-factory` at HEAD `4d0de52` (clean except the store under `.factory/state/`).

What I checked myself:
- Cited paths and lines: `docs/design.md:217-221` (preamble OUTPUT block, reads as quoted), `docs/design.md:381-393` (rubric 6, "could read the Problem section"), `docs/design.md:530-545` (reviewer CHECK items 1-7, no prose item), `docs/design.md:54` (role-context paragraph), `factory/instance.py:28` (`HARNESS`) and `:160-169` (`fill_preamble`, fills `{repo name}` and the protected-path line only), `factory/cli.py:218-219` (preamble + role prompt into `system-prompt.txt`), `factory/compose.py:153` (PR description added for the reviewer), `factory/context.template.md` (21 lines, no reader bullet), `README.md:392-393` (the "once it exists (#23)" sentence), `README.md:348` (the `docs/prompts/` row), `tests/factory/test_instance.py:274` (the named test and its unchanged-lines assertion), `dev/build-harness.spec.md:158` (placeholder list), `docs/prompts/99-doc-reviewer.md` (exists), `HARNESS_PATHS` at `factory/instance.py:33` (no `docs/`, so the revision decision holds). All exist and say what the spec says.
- Acceptance commands, run verbatim: `prompt-copies-verbatim` prints the three `verbatim` lines, `preamble copies equal`, `critic-diff=2 reviewer-diff=2`. `rubric-6-widened-in-every-copy` prints `:1` x3 then `:0` x3. `reviewer-check-in-every-copy` prints `:0` x3. `records-name-the-standard` prints `changelog=0 design=0 buildspec=0 stale=1 row=0`. `briefing-template-has-reader-line` prints `0`. `standard-is-one-page-with-a-pair-per-rule` prints `missing`. `preamble-names-the-standard` (the live one, in a `mktemp` target) prints `standard=[] unfilled=0 file=absent` and the prompt is 95 lines; the temp dir was removed and `git status` shows nothing new outside the store. `gates-pass`: `121 passed`. Every baseline in verification.md matches.
- The operator's authority: `.factory/state/approvals/T-0013/resolve-1.yaml` is answer 1 to the triage question; run-0105's triage output records it as "option (a). Standard and existing checkers only." and lists the prompt and template paths under ESCALATIONS. The Risk section declares every path triage named, plus `factory/instance.py` and the one test.
- Readability as the gate operator: the Problem's first paragraph says what is wrong (agents write for each other; nothing tells them otherwise or checks it, except one section) and for whom (the operator at the spec gate and other human readers), and glosses harness, operator, spec gate and escalation before using them. The first paragraphs of Evidence, Decisions and Operator steps use only terms the Problem or an earlier section glossed (`ticket new` is glossed inline; `fill_preamble` is introduced in Evidence before Decisions uses it).

Findings:

[NIT] 1 Evidence, "Agents also receive another, older copy"
Problem: The command template `agents/factory-<role>.md` does not resolve for two of the three roles it reports on, because the template names differ from the prompt names.
Evidence: `ls agents/` shows `factory-spec-critic.md` and `factory-spec-writer.md`; `factory/prompts/` has `critic.md` and `spec_writer.md`. Run as written for the critic, `sed` fails on `agents/factory-critic.md` and the count becomes 65 (every line of `critic.md`). With the real pairs the figures are exactly as stated: 18, 53, 8.
Suggested fix: Name the three file pairs instead of `<role>`, or drop the command and keep the figures.

[NIT] 6 Problem, "The change" list, second bullet
Problem: "That block gains one line" disagrees with Risk ("gains five preamble lines") and with Part B, which replaces one line with a five-line block.
Evidence: design.md Part B.1 and Risk, Blast radius, first bullet.
Suggested fix: Say "gains one rule" or "one sentence".

[NIT] 4 Decisions, "The `agents/` templates are not changed"
Problem: "The operator's answer names two copies" attributes to the answer something the request says; the recorded answer is one line choosing option (a).
Evidence: `.factory/state/requests/T-0013.md:53` ("Each prompt change lands in both copies, `docs/prompts/` and `factory/prompts/`"); run-0105 quotes the answer as "option (a). Standard and existing checkers only."
Suggested fix: "The request, as accepted by the operator's answer, names two copies".

No blocking issues. The deterministic items fail today for exactly the reasons stated and would fail against a stub that leaves any copy, the placeholder, or the template untouched; the live run checks a real system prompt and a real file, not a grep of the source. The one item that needs a model run is correctly moved to Operator steps. Scope is one PR: three prompt blocks in three copies each, a one-line fill, a template bullet, a new doc, records, one test change with its reason, and one new test file. The only design choices (path into the running checkout; `docs/` not in the revision paths; which five sections are human-facing; BLOCKING kept narrow; reviewer check SHOULD-FIX; `agents/` left alone) are each written down with the alternative rejected. The spec does not conflict with #21 (README truth) or the open follow-up it defers.

Out-of-scope observations:
- The build spec (`dev/build-harness.spec.md:158`) describes a `factory render` command that regenerates `docs/prompts/` and `agents/` from the design doc. No such subcommand exists in `factory/cli.py`, and the README (line 348) says the copies are made by hand. The spec's hand-copy approach matches the code as it is; the build spec is stale on this point.
- The `agents/` drift the spec reports (critic 18, spec writer 53, planner 8 lines) is real and the critic template has no Problem-section rule at all (`grep -c 'Problem section' agents/factory-spec-critic.md` prints 0). Worth its own issue, as the spec says.

STATUS: APPROVE
CONFIDENCE: high. Every cited path and every acceptance baseline was re-run on this checkout and matched; the three findings are wording.
ESCALATIONS: none
