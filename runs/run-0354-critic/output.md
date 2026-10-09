Round 2 review of T-0038 spec v2.

Scope of this round: whether the three round-1 findings are resolved, and the text that changed. Per the v1→v2 diff, only proposal.md changed (Problem, Evidence, Out of scope, one Decision, Risk, Operator steps, all wording) plus the verification's preamble and a new Responses section. design.md, the four spec files and the acceptance items are byte-for-byte unchanged, so the round-1 spot-checks of cited code, log lines, test pins and consistency stand.

Spot-checks this round (`main` still at `51e2af7`, `git rev-parse --short HEAD`):
- Re-read `factory/store.py:228-235` (`subtickets_of`: glob of `tickets/<parent>.*.yaml`, sorted by index) and `factory/cli.py:438-484` (`subticket_add`, `_create_subtickets` writing `st["spec"]` at 478 and nothing about the plan). Both as the Root cause says.
- Ran both no-suite acceptance commands as written, under the HOME wrapper, from `~/dev/spec-factory`. Documents scenario printed `design=0 build-spec=0 readme=0 changelog=0 CONTIGUOUS`; whitespace scenario printed `whitespace=ok untouched=0`. Both match the verification's "today" lines.
- Grepped proposal.md for the words the Responses say were removed: no "stand-in", no "the human", no "pinned", and "target"/"instance" no longer appear in Problem or Operator steps. The park reason "sub-ticket closed by a human" is kept verbatim, as the Responses say.
- Read the five human-facing sections as the gate operator. Problem, paragraph one, now says what is wrong (the build stops for good on old-plan work), for whom (the operator, glossed), and the cost (hand-editing ticket state files). "Nanobot" is glossed as one of the repositories the factory builds in. Evidence, Decisions and Open questions use only terms the Problem glossed earlier or gloss them inline (`planned_from` is defined in its first sentence). Operator steps gloss `factory-store` and `--accept-harness`.

Prior findings:
- [BLOCKING] 6, unglossed "target" and "`factory-store`" in Problem and Operator steps: RESOLVED. Problem reads "ticket T-0024 on Nanobot, one of the repositories the factory builds in"; Operator steps read "On `factory-store`, the branch that holds Nanobot's ticket state".
- [SHOULD-FIX] 6, first paragraph does not say who has the problem: RESOLVED. The operator is named and glossed in the first sentence, and the second sentence says what they must do by hand.
- [NIT] 6, "pinned" unglossed: RESOLVED. Now "amends an approved spec after planning", with T-0027 introduced as "approved but not yet built".

Findings

[SHOULD-FIX] 6 proposal.md, Operator steps first paragraph
Problem: "a harness revision that contains this change" uses "harness", this repo's name for its own program (README terms table, `README.md:44` and `:138`), with no gloss anywhere in proposal.md; the word's only earlier use is the Evidence's last paragraph ("the harness suite"), also unglossed.
Evidence: `grep -n harness` over proposal.md finds first use at the Evidence's final paragraph and again in Operator steps; neither says what the harness is. I did not raise this in round 1 on the v1 wording ("accepts a harness with this change"), and I am not blocking on it now: "harness" is a common word for the program that drives an agent pipeline, and a deeply technical reader lands on the right meaning from `--accept-harness` and "revision". It is still a system term a first-time reader has to infer.
Suggested fix: "Once Nanobot runs a revision of the harness, the factory's own program, that contains this change (...)".

[NIT] 6 proposal.md, Risk third paragraph
Problem: "The change reaches a target only after the runtime is moved to a revision that contains it and the instance accepts that harness" uses "target", "runtime" and "instance" where the Problem and Operator steps now say "Nanobot, one of the repositories the factory builds in" and `--accept-harness`; one concept, two vocabularies (writing standard rule 9).
Evidence: Risk is not one of the sections the rubric holds to the first-paragraph rule, so this is not blocking; the Responses say "instance" was removed, which is true of Operator steps but not of Risk.
Suggested fix: "The change reaches a repository the factory builds in only after that repository is moved onto a harness revision that contains it with `--accept-harness`."

Not checked, as in round 1 and unchanged: the prototype outputs of the NEW scenarios and `384 passed` need the change built; the implementer and verifier own them. The verification's new statement that three NEW items were re-run in round 2 is consistent with the "today" lines I reproduced for the two no-suite items, but I did not re-run the three fixture-based items myself.

Substance: unchanged from round 1 and still sound. The split rule (unmerged and `planned_from` below the parent's highest) covers the Nanobot record without a migration, the T-0027 moved record, and the same-version re-plan; the `Depends on` refusal and the planner line close the one route by which a new plan could wait on a superseded sub-ticket; every lettered part is needed; "Tests to change: none" holds against the pins I read in round 1 (`test_shepherd.py:385`, `test_replan.py:108,117,127`, `test_build_startup.py:84-91`, each one approved version per parent); the protected path `factory/**` is declared.

Out-of-scope observations: the dev checkout has an untracked file `.factory/answers/T-0037-answer.md` (`git status --short`). It belongs to another ticket and does not touch this spec.

STATUS: APPROVE
CONFIDENCE: high; the round-1 findings are fixed exactly as described, the only changed text is wording in proposal.md and I read all of it, the two no-suite acceptance commands ran as written and matched, and the design, specs and acceptance are byte-identical to the v1 I spot-checked against the code.
ESCALATIONS: none
