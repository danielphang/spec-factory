## Proposed change

Line numbers are on `main` at `7231670`. Where a check in the delta depends on exact words, the words are given here; elsewhere the wording is the implementer's, within the line targets. The prototype that met every check came to 1,101 README lines; the budget is 1,110.

**A. Freeze the three `dev/` build documents.**
1. In `dev/build-harness.spec.md`, `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md`, insert after line 2 (the blank line under the title) this line, then one blank line, and change nothing else in the files:
   `> **Frozen as history.** This document records how the harness was first specified and built, and parts of it describe a design the code never had. It is no longer kept in step with `docs/design.md` or the code, and no change updates it; `README.md` and `docs/design.md` describe the system.`
2. `.factory/context.md:9-11`: replace the `dev/` bullet with
   `` - `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the ``
   `  P0 walking skeleton, frozen as history from building the harness, which no change updates;`
   `.factory/context.md:34-36`: drop "`dev/build-harness.spec.md` consistent with the new text," so the sentence reads "A change to the design doc keeps its own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose block changed re-copied from it." After the edit the file names no `build-harness` path.
3. README:1111, the `dev/` row of "Where things live": `` | `dev/` | The issue index (`dev/issues.md`), kept live; and the build spec, its plan and the P0 walking skeleton, frozen as history from building the factory | ``

**B. Correct the stale claims.** Body text names no ticket ids ("Maintaining this page"); ids go in the changelog entry.
1. README:94-95: "A run that returns no output is run once more, then parks its ticket ("Empty output", under "What is built and what is not")." The retro sentence stays.
2. README:157-158: the one-sub-ticket path "has run on real tickets on both targets."
3. README:728-729: replace "The driver is tested, ... the tested route." with the file-tool limits sentence moved from the Built entry (C.2) and "It has taken real tickets through intake and the build on the chat-bot target."
4. README:821-823: drop "; this is tested but has not yet run on a real ticket" (the overlap figure goes in D).
5. README:948, 1000, 1016, 1025-1026: in the rewritten Built entries (C.5), the path skip "is recorded on a real sub-ticket", and the re-plan "has fired on a real ticket". The protected-path refusal "has fired on a real ticket, which the operator accepted with `--accept-paths`", and the driver "has taken real tickets through both on the chat-bot target". Keep "It is tested, and has not yet fired on a real ticket" in the tripwire and sibling-tests entries, the drift entry's "the sibling-merge exception is tested but has not yet run on a real ticket", and "Neither target sets it yet" in the effort entry.
6. README:1147-1150, the "Ground truth only above" rule: "A thing appears in the sections above only once it is built and tested, and its entry says whether it has yet run on a real ticket." The rest of the bullet stays.
7. `docs/design.md:3`: replace `2026-09-30 · Daniel` with `Daniel · first written 2026-09-30; every change since is in `docs/changelog.md``.
8. README:9: the status date becomes the day of the change.

**C. One home per mechanism in README.**
1. Live-store fence (home: "Where a human decides", 834-860, unchanged).
   - README:755-764, in the driver how-to, becomes at most 6 lines. It says the fence exempts the driver because it is the dispatcher, and that the driver marks its own store calls and never its role processes'. It keeps the same-ticket guard: it refuses with exit 2 and nothing written while the ticket or a sub-ticket has a run in flight, or while `drive/<ticket>.yaml` shows another live driver; delete that file if the pid is not a driver; after a SIGKILL, clear runs as "Where a human decides" says. It drops the location rule ("refused like any write") and "even while runs of other tickets are in flight".
   - The Built entry (963-972) becomes at most 3 lines and names "Where a human decides".
2. Driver (home: "Driving a ticket from a shell with `factory drive`").
   - The Built entry (1017-1026) becomes at most 4 lines and names that section. Its file-tool limits sentence moves to the how-to (B.3).
   - "Running on another agent host" (1072-1095) becomes at most 6 non-blank lines, with no table. Keep the heading. Say what a host must offer, that only the pieces in "What depends on Claude Code" need a counterpart, that `factory drive` is that counterpart on Claude Code, and that the comparison with OpenAI Codex and Google Antigravity, untried, is in `docs/design.md`, "Running on another agent host".
3. Final check's skip (home: "The build workflow, step by step").
   - README:329-331 takes the full condition and its reason from 166-169: one sub-ticket, its text names every acceptance scenario, the integration branch has not moved since it merged, so its verifier already checked the same code.
   - 165-170 keeps one sentence pointing there. The phrase "has not moved since" appears once in README.
4. Store branch (home: "How the factory uses git", 505-507).
   - 375-379 becomes "The store is the target's record of every ticket, a git worktree of its own branch, the store branch `factory-store` ("How the factory uses git"). Two targets run on the runtime today: this repo and a chat-bot repo."
   - Drop the first sentence of 619-620 and the sentence at 828.
   - The Built entry (954-956) becomes 2 lines with that pointer. Joined into one line, README says "never moves the integration branch" once.
5. Built entries. Each keeps its bold name exactly, and ends with its status from B:
   - Build, local-only (939-948): at most 6 lines; keep the word `SKIPPED`; point to "How the factory uses git" and "Adopting the factory in a repo".
   - Spec store (949-951): 2 lines.
   - Tripwire on live files (957-962): at most 4 lines, citing `docs/design.md`, "Tripwire on live files".
   - Sibling tests check (973-978): at most 4 lines, citing `docs/design.md`, "Tests a sibling added".
   - Spec amendment and drift (979-993): at most 6 lines, citing `docs/design.md`, "Spec drift"; keep "factory spec amend", "Where a human decides" and "is not drift".
   - Re-plan after a re-spec (994-1000): at most 4 lines.
   - Empty output (1001-1009): at most 6 lines, citing `docs/design.md`; keep `ended its turn waiting on a background command`.
   - Protected paths at merge (1010-1016): at most 4 lines, naming "How the factory uses git" and "Where a human decides".
   - Per-role effort (1027-1030): unchanged.
   - Counting catch and cost, `factory stats` (1031-1037): at most 3 lines, naming "Counting what each role catches and costs"; drop the `factory/cost.py` history (D).
6. "Not built" (1039-1052) becomes one paragraph with no bullets. It says the items under "Where this can go" are named work, not built, and gives today's facts:
   - one machine and one identity do everything, which suits one operator and not a team;
   - "the role prompts in `docs/prompts/` are copied from the design doc by hand", in those words (out of scope: #83 part C);
   - no retro has run;
   - this page stands in for the capabilities no ticket has changed since the spec store was created;
   - the status page `factory report TICKET` is not built, and today you read the store's YAML.
   In "Where this can go", the bullet "**The factory described by itself.**" is renamed "**Current truth for the factory itself.**".
7. README:711-714: drop the sentence repeating what `inlineRoles` does, and point to "What depends on Claude Code".

**D. History to the changelog.**
1. Drop README:819-821 "On 2026-10-04 ... planners)." and README:1035-1036 "`factory/cost.py` now counts the same way; it used to count most calls about twice." The second is already changelog entry 70.
2. Drop "Both stores were made before ... `factory store migrate`." (377-379, under C.4), and "Both targets' stores were moved there with `factory store migrate`." (956). Keep 461-462, which says where each store is.
3. "Related work and history" (1120-1139): replace the narrative with the issue references it carries, every one of #16-#24, #28, #35, #42, #46, #47, #53, #55, #61, #65 and #70, each beside what it names. Then name the two targets (instances A and B), point to `docs/changelog.md` for how this page and the design came to be and to `dev/issues.md`, and keep the final sentence of figures, re-derived. Drop "First written 2026-10-03" and the 2026-10-04 notes.
4. README:1185-1186: drop "(today this caught two: ... on the wrong case)".
5. `docs/design.md:70`: replace everything after "`factory stats` prints the evidence a change to this table needs" up to "counted apart." with "; its first figures, from 2026-10-11, are in `docs/principles.md`, principle 4, and changelog entry 70."
6. `docs/changelog.md`: add entry 72 after entry 71 and before the closing "Declined:" line.
   - It opens with `72. After issue #101 (2026-10-11), `.
   - It records parts A to E, and the `harness-docs` rewrite (F) with its rules.
   - Its words include `frozen`, `build-harness.spec.md`, `context.md`, the moved figure `41 and 11`, `harness-docs` and `not yet`.
   - It names the corrected claims and the tickets that showed them: T-0032 to T-0051 for the one-sub-ticket path, T-0035 and T-0036 for the driver, T-0036.1 for the path skip, T-0031 for the re-plan and T-0044.1 for the protected-path refusal.

**E. Glossary.**
1. Terms rows 138-141 (target, instance, store branch, runtime) become one row: `| target, instance, runtime, store branch | defined under "Where it runs" |`.
2. The merge gate row (127) drops "A protected path is one `instance.yaml` lists under `protected_paths` because a change to it is sensitive, such as the harness's own code." A new row follows it: `| protected path | a path `instance.yaml` lists under `protected_paths` because a change to it is sensitive, such as the harness's own code |`.
3. The **Record** row (868) drops its restatement of who reads the decision log: "`factory decision add T-n "<line>"`, at any ticket state, closed included: one dated line in the decision log".

**F. `harness-docs` current truth.** The delta below is the whole of this part; archive writes it, and no repository file changes for it. It restates 23 requirements and removes 2. Its rules are in Decisions: find a changelog entry by its opening words, drop per-change limits, check whitespace once in full, drop the frozen build spec's checks. It adds 7 requirements for parts A to E.

## Tests to change

none. No test reads `README.md`, `dev/`, `docs/changelog.md` or `.factory/context.md`. The tests that read `docs/design.md` read its prompt blocks and the SCRATCH FILES rule (`tests/factory/test_decision_log.py:235`, `test_coding_standard.py:69`, `test_run_scratch.py:85`), which this change does not touch.

