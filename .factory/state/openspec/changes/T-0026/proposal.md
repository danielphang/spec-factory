## Problem

The operator cannot tell, at a glance, what task a factory run is working on. Every row in the run's live progress display names the work by a bare ticket id, such as `T-0018`, and the operator does not remember which id is which task. Each glance at the display, often on a phone, means looking the id up.

Some background on the parts involved. The factory moves each request through a chain of AI agents. Each request is a ticket with an id (`T-0026`) and a one-line title. A large ticket is split into sub-tickets (`T-0025.1`), each with its own title. Two scripts drive the agents: one takes a ticket from request to an approved spec, and one builds an approved ticket. Both run inside Claude Code's Workflow tool, whose progress display (in the terminal and in the mobile app) shows two kinds of text:

- an agent label: one row per agent the script starts. Besides the role agents (triage, spec writer, implementer and so on), the scripts start a small "clerk" agent for every read or write of the ticket store, the database of ticket records. So most rows are clerk rows.
- a narrator line: a free-text message the script prints above the rows.

Today the role rows read `triage T-0012`, the clerk rows read `clerk: run start triage` with no ticket at all, and the narrator lines name the ticket by bare id or not at all. Nothing on the display says what the task is.

This change adds a short version of the ticket's title beside every ticket id in both scripts. The short title is the title cut to at most 60 characters at a word boundary. It appears in four places: a narrator line when a run starts, giving the ticket, its short title and its state; a narrator line each time the ticket's state changes; every role row; and every clerk row. A sub-ticket's rows and lines carry the sub-ticket's own title. Only display text changes: the store commands the scripts send and the way they route on each agent's result stay exactly as they are.

## Evidence

I ran each workflow script on this checkout under node, with a stand-in for the clerk agent. The stand-in returns canned store replies instead of running commands, and records every agent label, every narrator line and every store command. The acceptance scenarios already in force for the build and intake scripts drive them the same way. The full setup is the first block of the first acceptance scenario below.

An intake run of a ticket titled "Workflow view shows a short task title beside every ticket id, in narrator lines and agent labels" printed these labels and lines (excerpt):

```
label: clerk: run start triage
label: triage T-0001
log: triage run-0009-x: ACCEPT
label: clerk: transition -> ready-for-spec-writer
...
log: critic run-0009-x: APPROVE
label: clerk: transition -> awaiting-spec-gate
log: T-0001: spec approved by critic in round 1; awaiting the human gate (bin/factory approve-spec T-0001)
```

No label or line carries the title. Of 18 labels, none carries it: `roles=0 clerk=0 untitled=18`. Three state changes produced no narrator line of their own: `transitions=0`. The first narrator line appears only after the first agent has finished.

A build run of a parent ticket with one sub-ticket printed 31 labels, none with a title (`untitled=31`). Its narrator lines name the sub-ticket in brackets after a run id, for example `log: implementer run-0009-x (T-0001.1): READY-FOR-REVIEW`. The transitions to `checks-in-flight`, `ready-for-merge` and `closed` produced no narrator line (`changes=0`).

Where the code builds this text:

- `factory/workflows/intake.js:54` and `factory/workflows/build.js:45` build every clerk label as `` `clerk: ${label}` ``.
- Role labels are `` `${role} ${TICKET}` `` and `` `${role} (stub) ${TICKET}` `` (intake.js:97 and :91), and `` `${role} ${ticket}` `` and `` `${role} (stub) ${ticket}` `` (build.js:88 and :82).
- The narrator lines are the `log()` calls at intake.js:72, 112, 113 and 166, and at build.js:63, 111, 112, 172, 176, 232, 240, 243 and 260. None names a title. The request said "the scripts never call `log()`". That is not so; the existing calls name only an id, which is the problem.
- The title is already in hand. Both scripts call `ticket show <id> --json` for the parent (intake.js:126, build.js:198), and build.js:126 makes the same call for each sub-ticket. The JSON carries `"title"` (`factory/cli.py:88`).

The request's GitHub-issue part has no reliable source:

- None of the requests under `.factory/state/requests/` has an `issue:` header (`grep -c '^issue:'` found 0 files).
- `ticket show --json` does not return a request's header.
- Two request titles carry a `#NN`, and only one of them names the ticket's own issue. `T-0015`'s title says "(rescoped #20)", and `dev/issues.md` row 20 is that ticket's issue. `T-0020`'s title says "(split from #36)", but its issue is #38 (`dev/issues.md` row 38).

In the first round I applied a prototype of the proposed change to copies of both scripts and ran every scenario below against the copies and against this checkout. Every NEW scenario printed its THEN on the copies and the "fails today" output on this checkout. The byte-identical-commands checksums matched on both. The scripts' existing acceptance scenarios (park reasons, which checkers run, the dispatcher marker) printed the same output on the copies as on this checkout. The prototype changed 28 lines in intake.js and 77 in build.js. That prototype was not kept. In this round I re-ran the base side on `main` at `0b1abad`, which has not moved: the five checksums printed exactly as the REGRESSION scenario states, and the two count scenarios printed `roles=0 clerk=0 untitled=18` and `changes=0 bare=6`, as verification.md states.

## Root cause

The two scripts were written to route tickets, and their display text was never designed for a reader. The clerk helper (`clerk()` in both scripts) receives only an action name, so its label cannot name a ticket. In build.js the helper is called for both the parent and its sub-tickets, so it cannot even tell which ticket an action is for. The scripts keep only the `state` field from the parent's `ticket show --json` reply. intake.js:128 and build.js:200 keep the state and drop the title, and `buildOne` (build.js:126-128) does the same for each sub-ticket. `transition()` (intake.js:117, build.js:116) returns the store's reply without printing anything, so no state change is narrated unless the caller happens to log.

## Out of scope

- The GitHub issue number on the start line is cut. No request carries one in a header, and a `#NN` in a title is not reliable. A request header surfaced through `ticket show --json` would be a store CLI change and can be filed on its own.
- The workflow card's name and description. They come from the fixed `meta` literal (intake.js:1-8, build.js:1-9), which the Workflow tool reads before the script runs.
- Every store command the scripts send, its order, and the routing on each STATUS, join decision and refusal. The REGRESSION scenario fixes them byte for byte.
- The store CLI (`factory/cli.py`), the prompts, the agent definitions and the test suite.
- `README.md`, `docs/design.md` and `docs/changelog.md`. The design doc does not describe labels or narrator lines. The README describes a behaviour only after it has run on a real ticket ("Maintaining this page"), and it does not quote label text today.

## Open questions

none

## Decisions

- The GitHub issue part is cut. Its sources are missing or wrong: no request has an `issue:` header, and one of the two `#NN` titles names another issue. Rejected: parsing `#NN` from the title, which would show #36 for a ticket whose issue is #38. Also rejected: adding the request header to `ticket show --json`, a store CLI change the operator's ask ("a 1-liner snippet besides just identifiers") does not need.
- The short title is the ticket title with whitespace runs collapsed to one space. A title of 60 characters or fewer is shown whole. A longer one is cut at the last space within its first 61 characters (index 60 or earlier), so at most 60 characters are kept. Trailing spaces and `,` `;` `:` `·` `—` `-` are then dropped, and `…` is added. A title with no such space is cut at 60 characters. Rejected: a fixed cut mid-word, which leaves fragments such as "ticke…".
- A ticket's tag is `<id> · <short title>`, joined by a middle dot (U+00B7). It is the bare id when the title is not known yet or is empty.
- Every clerk row reads `clerk <tag>: <action>`. That includes the two calls made before the title is known (`config` and the parent's `ticket show`) and each sub-ticket's first `ticket show`; their tag is the bare id. Rejected: the triage note's assumption that those calls keep their current labels. A uniform form still tells the operator which ticket the run is for.
- A state-change line is printed by the transition helper, the script function that asks the store to move a ticket to a new state, and only when the store accepted the move. A refused move is followed by the line the script already prints when it parks the ticket, that is, stops it for a human.
- The existing narrator lines keep their wording. Each now begins with the tag of the ticket it is about, followed by `: `. build.js's ` (<sub-ticket>)` after a run id is dropped, because the tag now names it.
- Acceptance runs the scripts under node with the stand-in clerk, as the scripts' existing acceptance scenarios do. The request asked for a stub-mode run instead: a run inside the Workflow tool in which each role agent copies a prepared fixture file as its output instead of calling a model. That needs the Claude Code runtime and cannot be a shell command, so it is Operator step 1.

## Risk

Blast radius: display text only. Labels and narrator lines never reach a shell or the store. A title containing quotes or backticks therefore cannot change a command. A REGRESSION scenario checks that every store command is byte-identical on five paths, including a park.

Protected path touched: `factory/workflows/intake.js` and `factory/workflows/build.js`, under the harness path `factory/**`. The request names both files as the change. No other protected path is touched.

The change reaches running tickets only when the operator moves the runtime, the pinned checkout of the harness that runs tickets, and accepts it with `--accept-harness`. Merging into `main` does not change the running code.

The Workflow tool resumes a run by replaying the longest unchanged prefix of its agent calls. I could not confirm whether a label is part of that match. If it is, a run started on the old scripts and resumed on the new ones replays nothing and starts live from its first call. That is safe, because both scripts start from the state the store holds.

Long labels may be cut off on a phone screen. The tag puts the id first and caps the title at 61 characters, so the id and the start of the title stay visible.

## Operator steps

These run after the runtime, the pinned checkout at `~/dev/spec-factory-harness` that runs tickets, has moved to a revision containing this change and been accepted with `--accept-harness`. Below, `$RUNTIME` is that checkout's absolute path.

1. Run the intake script in stub mode on a throwaway ticket store. Stub mode means each role agent copies a prepared fixture file as its output instead of calling a model. A throwaway store keeps the run out of the live store. In a Claude Code session, create the store and one ticket:

   ```
   T=$(mktemp -d)
   FACTORY_STATE=$T/store $RUNTIME/bin/factory init
   printf '# Demo of the workflow view\n\nDo x.\n' > $T/req.md
   FACTORY_STATE=$T/store $RUNTIME/bin/factory ticket new --file $T/req.md
   ```

   Then call the Workflow tool with `scriptPath` set to `$RUNTIME/factory/workflows/intake.js` and args `{ticket: "T-0001", repo: "$RUNTIME", instance: "$RUNTIME/.factory", state: "$T/store", stubs: "$RUNTIME/tests/factory/fixtures/stubs/accept-approve", inlineRoles: true}`, with each `$` value written out as an absolute path. Confirm that the progress display shows the start line `T-0001 · Demo of the workflow view · ready-for-triage`, at least one `→` state-change line, and role and clerk rows that carry `T-0001 · Demo of the workflow view`.
2. On the next real run, open the run in the Claude Code mobile app. Confirm that narrator lines appear there. If they do not, the rows alone still carry the title, and a follow-up ticket should say so.

