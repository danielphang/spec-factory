## Problem

The clerk, a small agent that copies the factory's command output back to the workflow scripts, sometimes miscopies it. Each slip stops a build partway through, and the operator, who launches the factory's runs and answers its stops, has to find the cause and restart the build by hand. This store holds four such stops from one kind of slip, all on 2026-10-13, three of them on one piece of work.

How the clerk comes into it. The factory moves a ticket through its roles in one of two ways. The older way is a pair of workflow scripts, `factory/workflows/intake.js` and `build.js`. They are JavaScript programs that Claude Code's Workflow tool runs, and each starts the roles (triage, spec writer, implementer, reviewer, verifier and so on) as separate agents. A workflow script cannot read a file or run a command. Each time it needs the factory's records, which the factory calls its store (tickets, runs and results), it asks the clerk to run one command of the harness, the factory's own command-line program `factory`, and to copy that command's output back word for word. The script parses the copied text as JSON and decides the next step.

Two of the clerk's slips stop a build:

- **It changes a value.** At the start of a run the script asks the harness for the factory's configuration, which names the model each role runs on. The clerk has reported the wrong model for a role, for example the verifier as `fable` where the instance says `opus`. An instance is a repository's `.factory/` directory; among other settings it names each role's model. The harness refuses to start a role on a model the instance does not name, which is the right call. The sub-ticket, one PR-sized piece of a ticket, still stops, or "parks", until a human resumes it.
- **It reformats.** Once, on the other repository this factory runs on, the clerk returned a one-line JSON reply spread over many lines. The script reads JSON only one line at a time, found none, and parked a sub-ticket whose implementer had already finished its work. The operator answers a park with one of the `factory resolve` commands, and none of them covers this one. The operator resumed it with raw state edits.

This change makes three fixes. First, the operator launches a **launch copy** instead of the script itself. A launch copy is the workflow script with the instance's models, round limits and store written into one line by a harness command, so no agent relays them. Second, a reply spread over several lines still parses. Third, the park after a finished implementer gets its own `resolve` command. The harness's refusal of a wrong model stays as a backstop. The clerk keeps relaying every other command. `factory drive`, the newer runner that needs no clerk, does not change.

## Evidence

- The request quotes #109 and #112. In 5 of 8 builds on 2026-10-12 and 2026-10-13 the clerk relayed `"verifier": "fable"` where the command printed `"opus"`. On 2026-10-14 it relayed `factory run finish`'s one-line JSON pretty-printed, and the build parked a sub-ticket whose implementer had finished `READY-FOR-REVIEW`. The operator resumed that park with `ticket head`, then `ticket transition --to checks-in-flight --round pr:init`, then a relaunch.
- This store's log, `grep '"ticket.parked"' .factory/store/log/*.jsonl | grep -c 'model fable refused'`, prints `4`. The parks are T-0048.1 at 2026-10-13T18:26 and T-0052.1 at 19:42, 19:46 and 19:49.
- The scripts take their models from the clerk's relay. `factory/workflows/build.js:225-226` runs `${BIN} config` through `clerk()` and sets `MODELS = cfg.models; MAX_PR = cfg.max_rounds.pr`, and `STATE = cfg.state_dir` when no `state` argument was given. `build.js:84` sends `--model ${MODELS[role]}` to `run start`, and `build.js:110` launches the agent on `MODELS[role]`. `intake.js:146-147` does the same with `max_rounds.spec`.
- `clerk()` parses one line at a time. `build.js:47-51` splits the trimmed stdout into lines and tries `JSON.parse` on each, from the last. `build.js:52` returns `no JSON on stdout` when none parses. `intake.js:56-61` is the same code.
- The harness prints one line. `factory/common.py:12-13` `out()` prints `json.dumps(obj, ensure_ascii=False)` with no indent, so a reply spread over lines is the clerk's doing.
- No resolve route covers #112's park. In `factory/human.py` `resolve`, `--to` accepts only `spec-gate` (`human.py:255-257`). `--redispatch` needs a park from `checks-in-flight` or `ready-for-merge` (`human.py:261-265`). `--ruling` takes a `ready-for-implementer` park only when its reason starts `harness-bug: run start implementer:` (`human.py:223-224`).
- Both runners read the branch tip again when they enter a sub-ticket at `checks-in-flight`: `build.js:178` and `factory/drive.py:469` run `ticket head` before any checker starts.
- Current truth this change touches: `openspec/specs/live-store-guard/spec.md` (its first requirement lists the commands the live-store fence leaves open) and `openspec/specs/harness-code/spec.md` (it pins each command-line module's definitions, `factory/cli.py` under 900 lines, 12 `gitops.repo_root()` call sites and one `"ticket.transition"` literal per place; this change keeps all of them).
- README room, checked this round on `main` at 308d038. `wc -l README.md` prints `1108`, against the 1,110-line budget harness-docs' current truth sets. The text Part F replaces is `README.md:699-711` (13 lines: the `paths` block and the paragraph that launches the scripts), the run-start sentence at `README.md:251-252`, the read-only list at `README.md:831-832` and the **Unstick** row at `README.md:859`, which is one table line.
- Prototype, from round 1. I built parts A to D in a scratch clone and ran every scenario of this change on it and on `main` (308d038). Each NEW scenario except the documents and suite ones printed its THEN on the prototype, and each NEW scenario printed the failure listed in `verification.md` on `main`. The harness suite on the prototype printed `594 passed`, with no existing test file changed. `main` has not moved since, so I did not rebuild it this round.
- In round 1, one run of my scenario runner wrote its output file to the dev checkout's root for a few seconds. I moved it into my scratch directory, and `git -C ~/dev/spec-factory status --porcelain` printed nothing afterwards.
- Reference harness: triage found no as-built fix on the Nanobot fork's `feat/lionbot-v3.5`. I did not search it again.

## Root cause

- #109: `build.js:225-226` and `intake.js:146-147` take each role's model from a model's copy of `factory config`'s output, so the model a role runs on is only as reliable as that copy.
- #112: `clerk()` (`build.js:41-58`, `intake.js:50-66`) parses the relayed stdout only line by line, so one JSON value spread over lines never parses.
- No resume command: `resolve` in `factory/human.py` has no route from a `ready-for-implementer` park to `checks-in-flight`.

## Out of scope

- `run start`'s refusal of a model the instance does not name (T-0050) stays as it is.
- `factory drive` and `factory/drive.py` do not change.
- The clerk keeps relaying every command except `factory config` in a launch copy. Retiring it is #89.
- The scripts launched as they are keep reading the configuration through the clerk (Decision 6).
- No change to `agents/`, `docs/prompts/`, any `instance.yaml` or `dev/issues.md`. The operator updates the issue index after merge, as usual.
- `MAX_PR` in `build.js` is set at line 226 and never read. It stays; it is noted here only.
- README's line budget does not change (Decision 13).
- Cut as speculative: the copy defaulting `repo` to its harness; the copy checking its recorded harness revision at run time; a resume route for tripwire or conflict-limit parks.

## Open questions

none

## Decisions

1. The command is `factory launch-script intake|build`, and what it writes is a launch copy. Each call writes `<name>.js` into a new directory `factory-launch-<random>` under the temporary directory and prints `{"ok": true, "script": <path>, "source", "harness_revision", "instance"}`. Rejected: a fixed path under the instance's `.factory/`. A later launch would rewrite a script a running workflow came from. A run against a throwaway store would also write into the live instance's directory, which here is a protected path: one the instance lists as needing the operator's acceptance before any ticket may change it.
2. A launch copy differs from its script in one line. The scripts gain the line `const LAUNCH = null`. The copy holds `const LAUNCH = {...}` instead: one JSON object with `written_by: "factory launch-script"`, the source path, the harness revision, the instance, and `models`, `max_rounds` and `state_dir` as `factory config` prints them. The file is read-only. This answers the request's Risk. A launch copy is told apart from an edited script because the harness command alone writes it, into a directory the command creates. It is a one-line change to the reviewed script, and that line names the command, the source and the revision.
3. A launch copy asks no clerk for the configuration. It uses `LAUNCH` as the reply `factory config` would give, so the clerk's own model comes from the instance too.
4. `launch-script` refuses exactly where `config` refuses: with no instance, with uncommitted harness edits, or when the instance has not accepted the running harness revision. To get that, it joins the read-only list of the live-store fence, the harness's refusal of store writes that lack the dispatcher's marker while a role run is in flight. It writes no store file. This modifies live-store-guard's first requirement. Rejected: fencing it as a write, which would refuse a launch while another ticket's run is in flight, where `config` stays open.
5. A launch copy sends every store command to the instance it records. Given an `instance` argument that names another instance, it returns an error naming its own before any store command runs. The copy's models and store path belong to its instance. Mixed with another, agents would read one store's runs while the clerk writes another's.
6. The scripts launched as they are keep their clerk path, and README tells the operator to launch the copy. This keeps every scenario and suite test that runs the scripts directly, and T-0050's park as the backstop. Rejected: a script that refuses to run without a copy, which breaks those checks and would need a test-only switch.
7. `clerk()` in both scripts first parses the whole trimmed stdout, then falls back to the last-line scan. Every rule after the parse is unchanged.
8. The resume command is `factory resolve <id> --to checks`. It accepts a sub-ticket that meets four conditions: it is parked; it was parked from `ready-for-implementer`; its reason starts `harness-bug:`; and its newest implementer run started after it last entered `ready-for-implementer` and finished `READY-FOR-REVIEW`. The event log's order decides "after", because the store's timestamps are whole seconds.
9. The route reads the branch tip as `ticket head` does, through one shared definition. It applies the round step the build applies on this move (`pr:init`): a first round's 0 becomes 1, and a later round is unchanged. That is "round unchanged, as the script would have", and it is what the operator ran by hand for #112. It records a `resolve-<n>.yaml` and a `human.resolved` event of kind `to-checks`.
10. Only `harness-bug:` parks qualify, the class #112 belongs to: a store command failed after the implementer finished. A tripwire park and the conflict-limit park keep their documented routes.
11. A head from a conflict run that did not merge the integration branch still moves to checks. The join then sends it back to its implementer as a conflict (`factory/gates.py:203-206`), as it does after the script's own move.
12. The new tests run the scripts under node inside the suite, as `tests/factory/_fixtures.py`'s `BUILD_DRIVER` already does. T-0023's "the suite does not need node" no longer holds.
13. README keeps its 1,110-line budget. Part F names the lines each edit replaces, and its edits together add at most one line, so README ends at 1,109 lines or fewer. Rejected: raising the budget, which nothing here needs.
14. The changelog entry takes the next free number and opens `<n>. After issue #109 `.
15. Each `launch-script` call first removes earlier launch copies: every `factory-launch-*` directory under the temporary directory that is more than one hour old (by its modification time) and holds exactly one file, `intake.js` or `build.js`, containing `"written_by": "factory launch-script"`. It removes nothing else. The Workflow tool keeps its own copy of a script once launched, so an old launch copy is no longer read (operator, at the gate). Rejected: removing every earlier copy, because another session sharing the temporary directory may have written one seconds before its own Workflow call; and leaving them for the system to clear.

## Risk

- Blast radius: every Workflow-tool run (both scripts change), `factory resolve`, the CLI's parser and fence list, and the store helpers that `ticket head` and `ticket transition` use.
- I could not run Claude Code's Workflow tool here. It may not load a script from the temporary directory. Claude Code's auto-mode classifier, its check on what a session running without per-step approval may do, may refuse to launch the copy as it once refused a hand-edited `build.js`. The scripts launched as they are still work, so a refusal costs only the fix (Operator step 1).
- The scripts launched as they are can still receive a wrong model. T-0050's run-start refusal then parks the ticket, as today.
- harness-code's current truth pins the definitions of `common.py`, `drift.py`, `gates.py`, `human.py` and `setup.py`, `factory/cli.py` under 900 lines, 12 `gitops.repo_root()` sites and one `"ticket.transition"` literal in the CLI modules and one in `store.py`. `design.md` places the new code so all of them hold.
- harness-code's current truth also holds "Splitting the command-line code changes no definition". Its scenario (`t0047-moved.py`) compares `git merge-base HEAD main` with HEAD and expects `added=0 removed=0`. That scenario measures T-0047's own split, so on this ticket's branch it reports this change's new and moved definitions, as it has for every `factory/` change since T-0047. A verifier running current truth should not read that count as a regression.
- Protected paths: `factory/**`

## Operator steps

1. After the merge, move the runtime checkout to the new revision and accept it. The runtime checkout, `$RUNTIME` (`~/dev/spec-factory-harness`), is the separate copy of this repository the factory runs from; it moves only when you upgrade it. To accept it, give the first `factory` command you run against this instance `--accept-harness <revision>`, the flag that lets an instance run on a harness revision it has not used before. Then launch the next build from a copy: run `$RUNTIME/bin/factory launch-script build`, and call the Workflow tool with `scriptPath` set to the `script` it prints. Check that the Workflow tool loads the copy and that Claude Code's auto-mode classifier lets it run. If either refuses, report it; launching `build.js` itself still works as before, with its models relayed by the clerk.
2. Tell the runner session of the other target, the Nanobot chat-bot repository this runtime also serves, to launch copies too: the same command, run from that repository.

