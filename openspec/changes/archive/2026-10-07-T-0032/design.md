## Proposed change

**A. Preamble: wait for your own commands.** Insert this bullet in the RUNNING CODE section, right after the bullet that ends "check command your briefing, ticket or spec gives you.". Make the same edit in all three copies: the `docs/design.md` §Shared preamble block (line 218), `docs/prompts/00-preamble.md` (line 44) and `factory/prompts/preamble.md` (line 44). All three stay byte-identical.
```
- Run every command in the foreground and wait for it to finish.
  Never end your turn while a command you started is still running:
  your final message ends your run, and an output you have not yet
  written is lost.
```

**B. Code reviewer: judge the diff.**
1. Insert this section between "beyond the PR description." and "CHECK, IN THIS ORDER", with one blank line before and after. Make the edit in the `docs/design.md` §6 block (line 611), `docs/prompts/06-code-reviewer.md` (line 4) and `factory/prompts/reviewer.md` (line 4). Change no existing line. The run copy keeps its one fill, "After round 2".
```
WHAT YOU RUN
- Judge the diff by reading it. Do not run the test suite or the gate
  commands: the verifier runs them on the same head.
- You may run a narrow command to confirm a specific finding, such as
  one test or a grep, and cite its output with that finding.
```
2. In `factory/compose.py` (`compose`, the "Where you work" paragraph, lines 175-179), the reviewer's paragraph keeps the worktree, branch, base and head sentence and the no-remote sentence. Its gate-commands sentence is replaced with `The verifier runs the gate commands on this head; you do not run them.` The implementer's and the verifier's paragraphs stay unchanged.

**C. Harness: empty output.**
1. `factory/cli.py` `run_finish`: a run with no `output.md`, or a blank one, and no `--status-override` gets status `EMPTY-OUTPUT` (today `KILLED`), with the error "empty output". It is logged as `run.finished`. An override is unchanged: `--status-override KILLED` still records `KILLED` and logs `run.killed`.
2. New command `factory run last-message RUN --text=TEXT`. When the run's `meta.yaml` status is `EMPTY-OUTPUT`, it writes `runs/<RUN>/last-message.md` (TEXT plus one newline) and prints `{"ok": true, "run_id": …, "last_message": "runs/<RUN>/last-message.md"}`. Otherwise it refuses with exit 2 and writes nothing. It is not on the read-only list, so the live-store guard treats it as a write.
3. Make the same change to `runRole` in `factory/workflows/build.js` and in `factory/workflows/intake.js`:
   - Rename today's body to `runOnce`, with the same arguments and the same returns.
   - In `runOnce`, delete the `killed` condition and always call `run finish <run>` with no override. Keep `run cleanup` for a reviewer or verifier.
   - When `run finish` succeeds with status `EMPTY-OUTPUT` and the agent returned non-blank text, the clerk runs `run last-message <run> '--text=<text>'`. The text is the last 4000 characters of the trimmed returned text. It is shell single-quoted, with each `'` written as `'\''`. A failure of this call is ignored: it never parks and never changes the route.
   - The new `runRole` calls `runOnce`. If the result is `EMPTY-OUTPUT`, it logs the fact and calls `runOnce` once more, on the same role and ticket. If that result is also `EMPTY-OUTPUT`, it parks the ticket with the reason `EMPTY-OUTPUT from <role>` and both run ids as outputs, and returns `null`. Every other result is returned as today.
   - The thrown-call path (`catch`) stays as it is.
   - In `build.js`, delete line 137, the `budget kill: implementer` park.
4. New suite test file `tests/factory/test_empty_output.py`. It checks the CLI half on a throwaway store:
   - `run finish` with no output gives `EMPTY-OUTPUT` in its JSON and in `meta.yaml`;
   - `--status-override KILLED` still gives `KILLED`;
   - `run last-message` writes the file for an `EMPTY-OUTPUT` run;
   - `run last-message` refuses with exit 2, and writes nothing, for a run that finished with an output.

   The workflow halves are checked by the node scenarios, as decided for T-0023: the suite does not need node.

**D. Documents.**
1. `docs/design.md`, §Routing table, "Rules the table relies on":
   - In the bullet that starts "A non-empty ESCALATIONS line" (line 99), add "a second EMPTY-OUTPUT in a row" after "a budget kill (piece 3)" in the list of park reasons.
   - Add a new bullet right after that one: `- A role run that ends without writing its output is EMPTY-OUTPUT, whatever stopped it. The agent call reports no reason, so an empty output is never recorded as a budget kill; the harness keeps the agent's last message with the run. The same role is re-dispatched once, on the same inputs and in the same round. A second EMPTY-OUTPUT in a row parks the ticket with both runs.`
   - In the resolution bullet at line 106, change "A budget-killed run re-dispatches" to "A budget-killed run, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches".
   - Add two table rows after the `| Verifier | SPEC-DEFECT |` row (line 132): `| Any role | EMPTY-OUTPUT, the first in a row | The same role again, same round | The same inputs |` and `| Any role | EMPTY-OUTPUT, the second in a row | Human queue | Both runs' last messages |`.

   The preamble (A) and reviewer (B.1) blocks change as given above.
2. `dev/build-harness.spec.md`:
   - In "Common step `runRole`" (line 275), replace the KILLED condition with: one `run finish RUN`; `EMPTY-OUTPUT` → `run last-message` with the returned text, then one re-dispatch; a second `EMPTY-OUTPUT` → park `EMPTY-OUTPUT from <role>`. Change "the KILLED seam" to "the EMPTY-OUTPUT seam".
   - Rewrite I.5 (line 300) to say the same, and to say that no budget is enforced or reported, so no empty output is a budget kill.
   - Rewrite item 49 (line 410) as the case where the reviewer is empty twice → `EMPTY-OUTPUT from reviewer`, followed by `--redispatch`.
   - Add `factory run last-message RUN --text=T` beside `run finish` (line 205), and say that an empty or missing output is `EMPTY-OUTPUT` there.
   - After this, no line may contain "KILLED condition" or "KILLED seam".
3. `README.md`:
   - Line 107: replace "or a run exceeding its budget" with "or a role that ended without output twice in a row (the first time, the harness runs it once more on the same inputs and keeps its last message)".
   - Line 149, the diagram edge label: change "over budget" to "no output twice".
   - Unstick row (line 437): extend the `--redispatch` gloss to "re-run the checks on the same commit after an outside fix, or after a checker ended without output twice".
   - Add a Built bullet after "Sibling tests check" (line 477). It starts `- **Empty output.**` and says three things in plain words: a run that ends without its output file is re-run once and then parks; the reviewer leaves the suite to the verifier; every role is told to wait for its commands. It ends "It is tested, and has not yet fired on a real ticket."
   - Bump the status date.
4. `docs/changelog.md`: one new last entry, numbered without a gap, starting `After issue #41 (2026-10-04),`. It names `EMPTY-OUTPUT`, the foreground rule, the kept last message, "re-dispatched once", and the reviewer leaving the gate commands to the verifier.

Size: the prototype's code and prompt edits are 104 changed lines. With D and the new test file, the total is about 200.

## Tests to change

none. The full suite passed on the prototype (`310 passed`). The existing tests that pin `KILLED` either use `--status-override KILLED` or record a `KILLED` row by hand, and both stay unchanged.

