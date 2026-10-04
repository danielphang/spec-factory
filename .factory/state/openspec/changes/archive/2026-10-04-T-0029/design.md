## Proposed change

The change is about 40 added lines, with no deletions and no code changes. A prototype of parts A and B was 37 added lines across six files.

A. One new rule in the implementer and verifier prompts. Add this bullet, exactly as written, as the last bullet under `RULES`:

```
- A protected path the sub-ticket declares is not an escalation: the
  code reviewer lists the declared paths once for each head it reviews.
  You may name them in your output, but not under ESCALATIONS. A
  protected path still goes under ESCALATIONS when the sub-ticket does
  not declare it, or when the change does something to it that the spec
  does not describe.
```

It goes in five places, with the same text and line breaks in each:
- `factory/prompts/implementer.md`, after the `- On fix rounds: …` bullet, which ends "Don't comply with a finding you believe is wrong.".
- `factory/prompts/verifier.md`, after the `- Anti-Goodharting: …` bullet, which ends "shows the fix is special-cased to the test inputs, FAIL it.".
- `docs/design.md`, inside the fenced block under "## 5. Implementer" and inside the one under "## 7. Verifier", at the same places.
- `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`, re-copied in full from those two design blocks, so each file still equals its block.

Do not change the code reviewer's prompt or the preamble in any of their copies. Their run copies must still differ from their documented copies only by the per-instance fills they have today: the gate-command lines, the force-push line and the round number.

B. A changelog entry. In `docs/changelog.md`, add the next free number as one line, after the last numbered entry and before the closing "Declined:" line. That is 53, or 54 if issue #46's entry lands first; the acceptance does not fix the number. Numbering stays contiguous.
- Open it with "After issue #49 (2026-10-04)". Say the implementer and verifier queued the same declared-path list as the code reviewer, and give the count re-derived from the store log: 10 runs, 30 of 205 queued items. Do not use the retro's 26 of 139.
- Then state the rule:
  - the implementer and verifier prompts gain one RULES bullet;
  - a protected path the sub-ticket declares is not an escalation;
  - the code reviewer lists declared paths once for each head it reviews (its check 6, unchanged);
  - the other two roles may name them, but not under ESCALATIONS;
  - an undeclared protected path, or a change to a declared one that the spec does not describe, still goes under ESCALATIONS from every role.
- The entry must contain the literal strings `#49` and `ESCALATIONS`.

No suite test is required. The acceptance scenarios check the composed prompts and the copies from outside. If the implementer adds a test anyway, it goes in a new file.

## Tests to change

none

