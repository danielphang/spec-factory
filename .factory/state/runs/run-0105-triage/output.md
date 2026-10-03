Type: feature

Title: A one-page writing standard for human-facing sections, applied by the critic and the code reviewer

Summary: The factory's agents write for each other. The person who actually reads their output is someone else: the operator at the gate, a reviewer reading a PR description, a later session reading a run's output. That reader is technical but new to this system. Issue #11 fixed this for one section, the spec's Problem paragraph, by giving the critic a rubric item (rubric 6) it can check. The requester wants that fix extended to every human-facing section, and the operator's answer (option a) fixes the scope at five parts. First, a one-page standard, `docs/writing.md`, made of checkable rules, each with a before/after pair from the factory's own outputs. Second, one preamble OUTPUT line making every human-read section follow it. Third, critic rubric 6 generalised from the Problem section to every human-facing section of a spec, keeping its BLOCKING rule. Fourth, one code-reviewer SHOULD-FIX check on whether the PR description's What changed and Known gaps are readable. Fifth, a per-instance "reader" line in the briefing template `factory/context.template.md`. Each prompt change lands in both copies, `docs/prompts/` and `factory/prompts/`.

Evidence:
- The operator reviewed the draft overview on 2026-10-03 and left three findings, quoted in the request:
  1. "`--accept-harness` appeared in a diagram with no statement of what requires it."
  2. A list of what is built was a pile of nested parentheticals. The operator called it "incomprehensible" and asked for "at least the plain outline".
  3. "consider audience and what they know and don't know; this doc will be read by a technical audience that will probably see this project for the first time."
- The request says the same failures recur in factory outputs. Evidence sections quote commands without saying what they show. A PR's "What changed" is just a file list. Escalations name a state (`checks-in-flight`) without saying what is stuck.
- Operator answer, 2026-10-03: "option (a). Standard and existing checkers only." The doc-reviewer as a checker role goes to a follow-up issue. The README rewrite is not part of this ticket: "README.md is already the overview (752ce40), and #21 part B keeps it current." The spec's Risk section declares `factory/prompts/**`.
- Checked again on this checkout (`~/dev/spec-factory`, HEAD `c9b7bb1`):
  - `docs/writing.md` does not exist (`ls docs/writing.md`: No such file or directory).
  - Rubric 6 covers only the Problem section today. It reads "the operator at the gate could read the Problem section" at `docs/design.md:382`, `docs/prompts/03-spec-critic.md:19` and `factory/prompts/critic.md:19`.
  - The preamble OUTPUT block (`docs/design.md:217-218`) has no readability rule. `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md` are byte-identical (`diff` prints nothing).
  - The code reviewer's PR DESCRIPTION format starts at `docs/design.md:510`, and its CHECK list at `docs/design.md:530`. The CHECK list has no check on the prose.
  - Agents receive the `factory/prompts/` copies: `factory/cli.py:195-196` reads `PROMPTS / "preamble.md"` and `PROMPTS / f"{prompt_name}.md"`, with `PROMPTS` set to `factory/prompts` at line 26.
  - Protected paths reach agents because `fill_preamble` (`factory/instance.py:160-169`) writes them into the preamble from `instance.yaml`.
  - `factory/context.template.md` is 21 lines long and has no line naming the reader.
- No duplicate. #11 is closed and covered only the Problem section. #21 (README, current truth) consumes this standard but does not duplicate it. Store ticket T-0013 is this request (#23).
- No harness fix exists elsewhere. The request says "Fix as implemented elsewhere: none", and green has no writing-standard file.

Assumptions (inferences, not stated by the requester):
- Rubric 6 keeps its current BLOCKING rule: an unglossed term of art in a first paragraph blocks. It is widened to every human-facing section of a spec, meaning at least Problem and Evidence. The request's Decisions also call readability BLOCKING for specs. The code-reviewer check stays SHOULD-FIX, as the request and the answer both say.
- "Agent prompts" are a guardrail path, and `docs/prompts/**`, `factory/prompts/**` and `factory/context.template.md` are protected (the `generated` and `harness` classes). This ticket is the explicit authority to change them. The spec's Risk section must name all three, plus the `docs/design.md` blocks: the preamble OUTPUT block, §3 rubric 6 and the §6 CHECK list. It must also carry the doc's own conventions: a `docs/changelog.md` entry and `dev/build-harness.spec.md` kept consistent.
- Agents run the prompts in the runtime checkout (`~/dev/spec-factory-harness`), not in `main`. A merged change reaches agents only after the operator's upgrade step and `--accept-harness`. The acceptance items can check `main`; the spec should say that taking effect needs the upgrade.
- Two items are left open for the spec writer, who must list them under Decisions, as the answer directs:
  1. How the standard reaches a target that has no `docs/writing.md` of its own. The options are inlining it into the preamble, a path into the harness checkout, or a per-instance copy.
  2. How the acceptance item that needs an LLM run ("a critic run on a seeded spec … returns a rubric-6 finding") is made deterministic through a harness stub or fixture, or how it is otherwise judged.
- The requester's README acceptance item ("`README.md`'s first paragraph names what the project is and for whom") leaves this ticket with part E. It may already pass after `752ce40`, so it would prove nothing here.
- Suggested priority: P1, as the requester labels it. Priority is a human call.

Reason: Accepted. The operator's answer settles the scope question from the previous triage (run-0104): option (a), standard and existing checkers only. The remaining open points (how the standard reaches a target without its own copy, and the deterministic critic check) are explicitly handed to the spec writer as Decisions. They are not product calls that block a spec.

Out-of-scope observations:
- The follow-up issue the answer calls for, "the Appendix doc-reviewer as a checker role for documentation tickets", does not exist yet. Someone needs to file it in `dev/issues.md` so it is not lost. Triage does not write there.
- The relayed user message asks whether the previous NEEDS-HUMAN stop drifted from the standing instruction to work autonomously. From the triage role's side: run-0104 stopped because the request's part C contradicted its own out-of-scope line. The triage role requires NEEDS-HUMAN for a scope call like that. Whether the driving session should have taken a default instead is for that session to answer, not this one.

STATUS: ACCEPT
CONFIDENCE: high. The operator's answer settles the only blocking question, and every file fact cited was re-checked on HEAD `c9b7bb1`.
ESCALATIONS:
- Protected and guardrail paths: the ticket changes agent prompts (`docs/prompts/**`, `generated` class; `factory/prompts/**`, `harness` class) and `factory/context.template.md` (`harness` class). The operator's answer authorises this. The spec's Risk section must declare all of them.
