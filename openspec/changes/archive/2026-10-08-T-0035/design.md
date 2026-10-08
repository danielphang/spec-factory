## Proposed change

**A. Critic PROCESS, in all three copies.** In the "## 3. Spec critic" block of `docs/design.md`, then `docs/prompts/03-spec-critic.md` (re-copied from that block), then `factory/prompts/critic.md`, replace the seven lines from `Spot-check at least 2 cited paths ...` through `what you could not check.` with:

```
Spot-check at least 2 cited paths and 1 acceptance command yourself.
Run no test suite: the implementer and the verifier run it. Pick an
acceptance command that runs no test suite, and run it as the spec
gives it. To confirm a finding you may run a small experiment in your
scratch directory, such as a few git commands in a throwaway
repository. A claim you could settle only by running a test suite or
building the change is a finding for the writer, or a question; say
what you could not check.
```

The `Turn economy:` paragraph that follows stays byte for byte. Nothing else in the critic prompt changes. The run copy's one existing difference from the documented copy (`round 2` against `round {2}`) stays.

**B. `docs/principles.md`, principle 2.** Change "the critic's PROCESS section, which runs no test suite and builds nothing (#73, `factory/prompts/critic.md`)." to "the critic's PROCESS section, which runs no test suite (#73, kept by #74, `factory/prompts/critic.md`)." The status line ("done by #41 for the code reviewer and by #73 for the critic ...") stays.

**C. `docs/principles.md`, Spiking section.** Replace its paragraph with:

```
Grounding a claim the spec makes, for example that a path exists or that an acceptance command fails
on the base, is the critic's job. Its prompt sets a floor, two cited paths and one acceptance command,
and no ceiling. To confirm a finding, the critic may run a small scratch check, such as a few git
commands in a throwaway repository; it runs no test suite (principle 2). Vetting whether a whole
approach works is implementation. A critic that builds the change duplicates work the implementer
redoes, in a disposable checkout, and the result survives only as a sentence in a finding. Principle 1
is the reason: a critic's trial of an approach is self-repair's weak signal, and an implementer's is
execution feedback. So vetting a whole approach belongs to the spec writer during investigation, with
its output in Evidence, or to a spike ticket on #64's spike path, run by an implementer and recorded
as a decision. #73 capped the critic at two paths and one command for any one claim and forbade any
build. The replay that accepted #73, three past intakes (#49, #51, #57) with the same inputs, found
that the critic then used about the same tokens (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M),
checked less, and missed a real finding on two of the three, one of which the earlier prompt had
confirmed with a scratch git test. #74 removed the cap and the no-build rule and kept the no-suite
rule.
```

**D. `docs/changelog.md`.** Insert entry 59 directly after entry 58, so it is the last numbered entry (the `Declined:` line stays after it), one line:

```
59. After issue #74 (2026-10-08), where the operator's replay of three past intakes (#49, #51, #57), with the same inputs and bases, found that #73's spec writer rules cut its tokens by about 37% at the same quality, but that its critic rules saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less: it missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk on #51 and, on #57, the brace-list declaration bug that the earlier prompt had confirmed with a scratch git test. The critic's PROCESS drops the per-claim cap (at most two paths and one command for any one claim) and the no-build rule (no clone, worktree or prototype), and says the critic may run a small experiment in its scratch directory to confirm a finding. It keeps its minimum spot-check, the rule that it runs no test suite, the rule for picking an acceptance command, the rule that a claim needing a suite run or a build of the change is a finding or a question, and the three reading rules. `docs/principles.md` principle 2 keeps the critic's no-suite rule, and its Spiking section drops the two-path bound and says that vetting a whole approach is still the spec writer's or a spike's job. The spec writer prompt is unchanged from #73.
```

Size: 31 added and 20 removed lines across five files (prototype `git diff --stat main...HEAD`).

## Tests to change

none. No test under `tests/factory/` names the removed phrases (`git grep`, Evidence). The two tests that compare design blocks with their `docs/prompts/` copies pass on the prototype (`10 passed`), because the three copies change together.

