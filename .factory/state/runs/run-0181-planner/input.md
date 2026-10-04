## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0181-planner/output.md`

## Approved spec (v1, pinned)

=== proposal.md
## Problem

Nothing in the spec factory notices when an AI agent it runs changes the operator's live files outside the repository. The operator learns about it only if the agent happens to say so. The factory runs each requested change through a chain of agents called roles: triage, spec writer, critic, planner, implementer, reviewer and verifier. Each agent call is a role run. The harness is the code that starts and records each run, and keeps every ticket's state in a store. The harness knows exactly when each run starts and finishes, but it never looks at anything outside the repository.

This has already cost live data. On 2026-10-04, while the factory was building a change for the Nanobot chat bot (the factory's other target repository), an implementer's tests overwrote the live bot's per-chat permission file and its backup in `~/.nanobot/`. The overwrite came to light only because one test happened to fail on an unexpected `FileExistsError`. The day before, intake roles left 13 stray session folders in the live bot's data directory, and nobody noticed for a day. A separate approved change gives roles a throwaway `HOME`, to make such writes less likely. Nothing yet tells the operator when one gets through anyway.

This change adds detection. A target's instance can list live files to watch, in two lists. The instance is its `.factory/` directory, which holds its config and its store. A run that changes a file on the "park" list stops its ticket and puts it in the human queue: the ticket is parked. A run that changes a file on the "escalate" list raises an escalation: it puts a flagged item in the operator's queue and lets the run continue. That list is for files with legitimate outside writers, such as a pairing approval or the operator's own edit. Neither list ever prints a file's contents, because these files hold live secrets. A run that is killed is checked the same way.

The leak also had a code-level cause that a coding rule would have caught. A test file imported a path function by name when the test runner loaded it. The test fixture's later replacement of that function never reached the copy the test file already held. So the coding standard, the rules page the implementer and code reviewer follow, gains a rule against that pattern.

## Evidence

Checked on `main` at `1c5f6a7`.

- **The incident is recorded by the run that caused it.** The Nanobot store's `runs/run-0080-implementer/output.md`, lines 91-93, names `/Users/dphang/.nanobot/policies.json` and `policies.json.bak` as overwritten by the first run of `uv run pytest tests/policy` "with the real `HOME`". It quotes the run's own error, `FileExistsError: [Errno 17] File exists: '/Users/dphang/.nanobot/policies.json'`. It names the cause: "the test module imported `policy_store_path` by name when pytest collected it. The conftest fixture replaces the module attribute later, so the test helpers kept calling the real function." That run's sub-ticket worktree shows the fixed form: `tests/policy/test_store.py` lines 23-30 call `store.policy_store_path()`, with a comment that "a name imported at collection time would still point at" the real function. The module is `nanobot/policy/store.py` in that worktree.
- **The 13 stray session folders** are from the request. I did not verify them, because `~/.nanobot/` is off limits to me.
- **No harness code looks outside the repository during a run.** `run start` (`factory/cli.py` lines 197-228) and `run finish` (lines 281-320) read and write only the store and, for build roles, git worktrees. The only reader of the instance's `protected_paths` is `fill_preamble` (`factory/instance.py` lines 168-179), which prints the list into the role's rules text.
- **Today an instance's `tripwire` key is silently ignored.** I appended `tripwire: {park: [<scratch>/live/policies.json, ...], escalate: [<scratch>/live/pairing.json]}` to an instance made from the template, started a triage run, changed `policies.json`, and finished the run (scenario "A changed park-listed file parks the ticket", below). `run finish` printed `{"ok": true, "run_id": "run-0001-triage", "status": "ACCEPT", "confidence": "high", "escalations": []}`. The ticket then read `state=ready-for-triage reason=None`: the change went unnoticed and the ticket stayed ready to move on. The same happened for a killed run, an escalate-listed change (no `escalation.queued` event in the log), and a run cleared from the in-flight list by hand.
- **Today a directory in that list is accepted.** With `tripwire: {park: [<scratch>/live]}`, a directory, `run start` exited 0 and created one run directory. The output was `exit=0 named=no runs=1`: the run started, nothing named the bad entry, and one run was recorded.
- **A run leaves the in-flight list in exactly three places.** The ticket record's `in_flight` list names its running runs. `grep -n in_flight factory/*.py` shows it changed only in `run_start` (append, line 225), `run_finish` (remove, lines 306-307) and the generic `ticket set` (lines 109-121). Neither store has a run left unfinished today: every `meta.yaml` under both stores' `runs/` has a `finished` time except the run writing this spec. Every killed run in the Nanobot log, for example `run-0047-implementer`, went through `run finish --status-override KILLED`.
- **A park written by `run finish` would be undone by the workflow scripts today.** The two scripts that drive roles, `factory/workflows/intake.js` and `factory/workflows/build.js`, route on the role's STATUS right after `run finish`. For example, intake line 153 moves a ticket to `ready-for-critic`. The instance's routing table allows `parked → ready-for-critic` and most other exits from `parked` (`factory/instance.template.yaml`, the `parked:` row). So a park that `run finish` writes would be silently overwritten unless the scripts check for it. In both scripts, the `runRole` function contains no reference to a parked answer from `run finish`: the count printed below is `0` for each.
- **The coding standard has no rule on patch targets.** `docs/coding.md` has rules 1 to 5 (`## 5.` at line 86). Rule 4 says "A finding against rule 2, 3 or 5 takes no tag" (line 67).
- **No reference fix exists.** `git log --all -i --grep=tripwire` in the Nanobot checkout finds no factory commit, so there is no as-built behaviour to compare against.
- **The gate passes today.** `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `171 passed in 103.25s`, and `git diff --check main...HEAD` exited 0.

## Root cause

- `factory/cli.py` `run_start` and `run_finish`: no snapshot of any file outside the store, so there is nothing to compare.
- `factory/cli.py` `ticket_set`: a run removed from `in_flight` by hand is dropped with no record of what it did.
- `factory/workflows/intake.js` and `build.js`, `runRole`: they route on the role's STATUS and never ask whether `run finish` stopped the ticket.
- `docs/coding.md`: no rule that tests reach a patched function through its module, and none that a new path outside the repository ships with a test guard.

## Out of scope

- Prevention: the throwaway `HOME` for every role (approved separately as T-0019, issue #36) and an operating-system write denial (issue #37).
- Watching directories. The 13 stray session folders were in a directory that the live bot writes all the time, and the request excludes such directories. A directory in either list is refused.
- Naming the changed top-level keys of a JSON, YAML or TOML file in an escalation, as the request proposed. Cut: a pairing file's keys can themselves be user identifiers, and the log is committed with the store (Decisions).
- Naming the other runs that overlapped a changed file in the park reason. Cut: the log's timestamps already show them.
- A new `resolve` mode for a tripwire park. The existing `ticket transition` and `resolve --redispatch` resume one.
- Either instance's own files: `.factory/**` here and everything in `~/dev/nanobot-upstream`. Adding Nanobot's lists is an Operator step.
- The design doc's prompt blocks and `docs/prompts/`: no prompt changes.
- `dev/build-harness.spec.md`. I read its lines 202 (`ticket set`), 203 (`run start`) and 205 (`run finish`). None is contradicted, because the change adds behaviour to those commands and removes none.

## Open questions

none

## Decisions

- Detection compares a SHA-256 of each listed file's bytes at run start with one at the end; a file created, deleted or modified counts as changed. Rejected: modification times, which a restore by copy or a write within the same second defeats.
- A `~/` entry resolves against the account's home from the system user database, never the `HOME` variable. A `run start` or `run finish` under a throwaway `HOME` therefore still watches the real files. Rejected: `HOME`, under which that case would hash the wrong files and never fire.
- The baseline is kept per run in the store, in a file the store's `.gitignore` excludes, so the operator's store commit never carries a digest of a live secret file.
- Each run's baseline is compared once, when the run leaves the in-flight list: at `run finish`, which every killed run in either store went through, or at a `ticket set` that removes it. Rejected: comparing at every command that names the ticket, because a run still in progress looks the same as an abandoned one there and would be compared early.
- The park reason says the files changed "during" the run, not "by" it, because runs on other tickets and the operator's own edits can overlap a run, and the tripwire cannot tell them apart.
- When a park-listed change is found on a ticket that is already parked or closed, the tripwire does not park it again; it queues the same reason as an escalation.
- Escalations and park reasons name changed files only, never contents or keys.
- A directory, or an entry that is neither absolute nor `~/`, refuses `run start`, so a bad list is loud from its first run.
- The workflow scripts stop on a `run finish` that reports a park, instead of routing on the role's STATUS, because the routing table lets a ticket leave `parked` for most states.
- The coding rule is rule 6 of `docs/coding.md`, and rule 4's list of untagged rules gains it.
- One change, not split: about 300 lines, half of them the new test file.

## Risk

Blast radius: nothing changes for an instance with no `tripwire` key, or with both lists empty. No baseline is written there, and no command's output gains a field. Under the key, every `run start` hashes a handful of files, every `run finish` hashes them again, and a bad entry refuses every `run start` on that instance. The workflows then park the ticket as `harness-bug: run start …`. A park-listed file that the live service itself rewrites will park tickets on legitimate changes; which files go on which list is the operator's call. A tripwire park stops the workflow before the role's output is recorded (for example, a spec is not added), so resuming re-runs that role.

Protected paths this change touches:
- harness: `factory/tripwire.py` (new), `factory/cli.py`, `factory/store.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/instance.template.yaml`.

Guardrail paths: `docs/coding.md` is the coding standard that the implementer and reviewer prompts name; part E of this ticket asks for its edit. The prompts themselves do not change. New tests go in a new file. No existing test changes.

Not touched: `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `docs/prompts/**`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Ordering: the approved throwaway-`HOME` change (T-0019) also edits `docs/design.md`, `docs/changelog.md`, `README.md` and `factory/instance.template.yaml`, in different places. Build this after it merges. The changelog scenario checks for the next free number, not a fixed one.

Gate: the request says it is pre-approved under the queue policy. Whether that covers a change to five harness files is the operator's decision at the spec gate.

## Operator steps

These come after the merge, once the runtime has moved to a revision with this change. The runtime is the pinned checkout of the harness that runs tickets. The operator accepts that revision for the Nanobot instance with `--accept-harness <revision>`.

1. In the Nanobot instance's `.factory/instance.yaml`, add the Driver's lists:
   `tripwire: {park: ["~/.nanobot/policies.json", "~/.nanobot/policies.json.bak", "~/.nanobot/config.json"], escalate: ["~/.nanobot/pairing.json", "~/.nanobot/config-localgateway.json"]}`
2. Check it: the next role run's `run finish` JSON on that instance carries a `tripwire` field, `{"park": [], "escalate": []}` when nothing changed. If `run start` is refused instead, its message names the entry to fix.
3. This repository's own instance watches no live files, so it gets no list.

=== design.md
## Proposed change

**A. Baseline at run start, comparison at run finish** (`factory/tripwire.py`, new; `factory/cli.py`; `factory/store.py`)
- A1. Read `cfg.get("tripwire")`. Absent, null, or both lists empty: the feature is off, and A2-A5 and B do nothing for that instance. Otherwise it must be a mapping whose only keys are `park` and `escalate`, each optional and each a list of strings. Expand each entry: a leading `~/` becomes the home directory of `pwd.getpwuid(os.getuid()).pw_dir` plus `/`; an entry that then is not absolute is refused. Refuse also an entry that exists and is not a regular file (a directory, for example), and one that exists and cannot be read. Each refusal is `store.Refused` (exit 2) naming `tripwire` and the entry as written and expanded. A path in both lists counts under both.
- A2. In `run_start`, do A1 and hash every listed file before `store.next_run_id` reserves the run directory, so a refusal writes nothing. A file's state is the hex SHA-256 of its bytes, or the string `absent`.
- A3. After `meta.yaml` is written, write the baseline to `runs/<run id>/tripwire.yaml`: `{park: {<expanded path>: <state>}, escalate: {...}, compared: null}`, keys in config order. Call `store.ensure_gitignore(root)` first. Add the line `runs/*/tripwire.yaml` to `STORE_GITIGNORE` and to the list `ensure_gitignore` checks, so the baseline is never committed with the store. Write no digest anywhere else.
- A4. A comparison of one run (`tripwire.compare`, used by A5 and B): if the run has a baseline whose `compared` is null, re-hash each path in the baseline, not the current config. A file that cannot be read now counts as changed. Set `compared` to the current time. Return the changed paths per list, in baseline order. Then act:
  - Park list changed, ticket not `parked` or `closed`: park it with reason `tripwire: <path>, <path> changed during <run id>`, outputs `[<run id>]`, history `by: tripwire`. Do this through one helper shared with `ticket_park`, which today writes the park record and logs `ticket.parked` and `escalation.queued` (`factory/cli.py` lines 173-185). Move that body into the helper and call it from both.
  - Park list changed, ticket already `parked` or `closed`: log `escalation.queued` (`ticket`, `run`, `items: [<that same reason>]`); do not park again.
  - Escalate list changed: log `escalation.queued` (`ticket`, `run`, `items: ["tripwire (escalate): <path>, <path> changed during <run id>"]`). The ticket is not touched.
  - Anything changed: also log `tripwire.changed` (`ticket`, `run`, `park: [...]`, `escalate: [...]`).
  - No event, reason or output ever includes a file's bytes or any part of them.
- A5. In `run_finish`, after the run is recorded and the ticket saved as today (both normal and `--status-override KILLED`), run A4 for this run. When the run had a baseline, add `"tripwire": {"park": [...], "escalate": [...]}` (changed paths) to the printed JSON. When A4 parked the ticket, also add `"parked": "<reason>"`. Without a baseline the JSON is exactly as today.

**B. A run dropped by hand** (`factory/cli.py` `ticket_set`): note `in_flight` before the assignments. After the ticket is saved, run A4 for each run id that was in `in_flight` before and is not after. When one parked the ticket, add `"parked": "<reason>"` to the printed JSON. No other command compares.

**C. The workflow scripts stop on a tripwire park** (`factory/workflows/intake.js`, `factory/workflows/build.js`): in each `runRole`, right after the existing `if (!fin.ok) …` line, add `if (fin.parked) { log(\`<ticket> parked: ${fin.parked}\`); return null }`, using the script's own ticket variable. Every caller already returns on `null` without routing. In `build.js` the reviewer or verifier cleanup still runs first, as it does today.

**D. Template and documents**
- D1. `factory/instance.template.yaml`, after the `protected_paths` block, add this as comments. A commented example keeps `set(template) == set(instance)` true and lets fixtures append the key.
  ```
  # Live files outside the repo that no role run should change, as absolute or `~/` paths (`~` is the
  # account's home, never $HOME). `run start` hashes each; the comparison runs when the run leaves the
  # in-flight list. A changed `park` file parks the ticket; a changed `escalate` file queues an
  # escalation and the run goes on. Contents are never printed. Files only: a directory is refused.
  # tripwire: {park: [], escalate: []}
  ```
- D2. `docs/design.md`: a new paragraph after the **What the harness itself owns** paragraph (line 52), with one blank line on each side, opening exactly `**Tripwire on live files.**`. It says: an instance may list files outside the repository under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list; `~` is the account's home, never `HOME`; files only. `run start` records a SHA-256 of each, or that it is absent, in a baseline the store's `.gitignore` excludes. The run is compared once, when it leaves the in-flight list: at `run finish`, killed runs included, or at a `ticket set` that drops it. A changed `park` file parks the ticket, `tripwire: <files> changed during <run>`. "During", because overlapping runs and the operator's own edits cannot be told apart. A changed `escalate` file queues an escalation and the run goes on. Nothing prints a file's contents. The workflow scripts stop on a `run finish` that parked. It detects a write after the fact; it does not prevent one.
- D3. `README.md`:
  - In "What is built and what is not", **Built**, after the "Instances and the harness lock" bullet, add: `- **Tripwire on live files.** An instance can list files outside the repo that no role run should change, such as a live bot's credentials, under \`tripwire\` in \`instance.yaml\`: a \`park\` list and an \`escalate\` list. The harness hashes each file when a run starts and compares when the run ends, killed runs included. A changed \`park\` file parks the ticket; a changed \`escalate\` file is queued for the operator and the run goes on. Neither prints a file's contents. It is tested, and has not yet fired on a real ticket.` Wrap it at the page's width.
  - In "Where a human decides", after the "Gap, as of today" paragraph's sentence that ends "returns it.", add: `A ticket the tripwire parked returns the same way, to the state its record names as \`parked.from\`, once the operator has checked the named files; a checker park can use \`resolve --redispatch\` instead.`
  - Bump the status-header date to the merge date.
- D4. `docs/changelog.md`: after the last numbered entry and before `Declined:`, one entry with the next number, opening `<n>. After the 2026-10-04 Nanobot incident, where a role's tests overwrote the live bot's permission file and nothing in the factory noticed:`. It says what D2 says in one paragraph. It also says that the coding standard gains rule 6, as part E. It must contain the word `tripwire`.

**E. `docs/coding.md`, rule 6.** Insert before the closing "The check order (rule 1) …" paragraph, with one blank line on each side, in the page's format:

```
## 6. A test reaches a patched path through its module, and a new outside path ships with a guard.
Check: each function or constant your tests patch to redirect a path outside the repository is
called in test code as an attribute of its module (`store.policy_store_path()`), never through a
name imported when the test file loads. Each path your diff adds outside the repository (a data
directory, a config file) comes with an autouse test fixture that fails any test resolving that
path outside `tmp_path`.
Principle: patch where the name is looked up (the Python `unittest.mock` documentation, "Where to
patch"); and fail-safe defaults (Saltzer and Schroeder): a test that stops is cheaper than one that
writes live data.
Before (a Nanobot implementer run, 2026-10-04): the test module ran
`from nanobot.policy.store import policy_store_path` when pytest collected it. The conftest fixture
then replaced `nanobot.policy.store.policy_store_path`, but the test helpers still held the real
function. The tests overwrote the live bot's `~/.nanobot/policies.json` and its `.bak`, and an
unrelated `FileExistsError` was the only sign.
After: the test module runs `from nanobot.policy import store` and calls `store.policy_store_path()`,
so the fixture's patch reaches every call. An autouse fixture fails any test whose resolved policy
path is not under `tmp_path`, so the next escape stops a test instead of writing live data.
```

In rule 4, change "A finding against rule 2, 3 or 5 takes no tag" to "A finding against rule 2, 3, 5 or 6 takes no tag".

**F. New tests**, in a new file `tests/factory/test_tripwire.py`, driven through `bin/factory` on scratch instances and stores. Cover the scenarios in `specs/live-file-tripwire/spec.md`: park, create and delete, escalate, unchanged, killed, dropped by `ticket set` (and not compared while still in flight), the account home, the directory refusal, the baseline kept out of a commit, and no tripwire key. Every listed file lives under `tmp_path`; no test lists a path under the real home that exists.

## Tests to change

none. I checked each existing test against the change:
- `tests/factory/test_instance.py` line 89 and `tests/factory/test_shepherd.py` lines 200-201 check that `.gitignore` contains its two lines, as a subset, so a third line passes.
- `tests/factory/test_instance.py` lines 94-106 compare an initialised instance with the template key for key. The new template text is a comment, so neither gains a key. The test fixture instance (`tests/factory/fixtures/instance/instance.yaml`) has no `tripwire`, so every existing run is unchanged.
- The tests that read `run finish` output (`test_p0_cli.py` line 251, `test_killed_checker.py` line 27) read named fields. Without a baseline the output is unchanged.
- No test drives the workflow scripts; `test_shepherd.py` replays their routing through the CLI.

=== specs/live-file-tripwire/spec.md
## ADDED Requirements

### Requirement: A changed park-listed file parks the ticket without showing its contents
When a role run's ticket belongs to an instance whose `tripwire` lists files under `park`, and any of those files is changed, created or deleted between `run start` and the end of the run, the harness SHALL park the ticket with the reason `tripwire: <changed paths, comma-separated> changed during <run id>`, and no store file or command output SHALL contain any of the file's contents.

#### Scenario: A changed park-listed file parks the ticket
Run every command in this file from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell and may run under a throwaway `HOME`; none depends on `HOME` except where it sets it.
- GIVEN the two fixture scripts written by the block below, run once at column 0 as shown (every later scenario of this change reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0020-fix.sh <<'EOF'
# Sourced from the repo root. A scratch instance (from the template) whose tripwire lists two park
# files and one escalate file under $T20/live, a scratch store, ticket T-0001, one started triage
# run $R, and a triage output $T20/out.md. `show` prints the ticket's state and park reason with
# the scratch directory written as $T20; `secrets` counts files holding the fixture's file contents.
unset FACTORY_REPO FACTORY_INTEGRATION_BRANCH
T20=$(mktemp -d); mkdir -p $T20/inst $T20/live
sed -e 's/__REPO_NAME__/demo/' -e "s|__HARNESS__|\"$PWD\"|" factory/instance.template.yaml > $T20/inst/instance.yaml
printf 'tripwire:\n  park: [%s/live/policies.json, %s/live/new.json]\n  escalate: [%s/live/pairing.json]\n' $T20 $T20 $T20 >> $T20/inst/instance.yaml
printf '{"token": "T20-SECRET-A"}\n' > $T20/live/policies.json
printf '{"chat": "T20-SECRET-B"}\n' > $T20/live/pairing.json
export FACTORY_INSTANCE=$T20/inst FACTORY_STATE=$T20/store
printf '# Fixture\n\nDo the thing.\n' > $T20/req.md && bin/factory ticket new --file $T20/req.md >/dev/null
R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/')
printf 'Type: bug\nTitle: Fixture\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n' > $T20/out.md
show() { bin/factory ticket show T-0001 --json | tail -1 | python3 -c 'import json,sys; t=json.load(sys.stdin); print("state=%s reason=%s" % (t["state"], (t["parked"] or {}).get("reason")))' | sed "s|$T20|\$T20|g"; }
secrets() { echo "secrets=$(grep -rl T20-SECRET $T20/store $T20/*.out 2>/dev/null | wc -l | tr -d ' ')"; }
EOF
cat > ${TMPDIR:-/tmp}/t0020-bare.sh <<'EOF'
# Sourced from the repo root. A scratch instance from the template with $TRIPWIRE (if set) appended,
# a scratch store and ticket T-0001. Set T20 before sourcing to use a directory you prepared.
unset FACTORY_REPO FACTORY_INTEGRATION_BRANCH
T20=${T20:-$(mktemp -d)}; mkdir -p $T20/inst
sed -e 's/__REPO_NAME__/demo/' -e "s|__HARNESS__|\"$PWD\"|" factory/instance.template.yaml > $T20/inst/instance.yaml
[ -n "$TRIPWIRE" ] && printf '%s\n' "$TRIPWIRE" >> $T20/inst/instance.yaml
export FACTORY_INSTANCE=$T20/inst FACTORY_STATE=$T20/store
printf '# Fixture\n\nDo the thing.\n' > $T20/req.md && bin/factory ticket new --file $T20/req.md >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && printf '{"token": "T20-SECRET-C"}\n' > $T20/live/policies.json && bin/factory run finish $R --output-file $T20/out.md > $T20/finish.out 2>&1; show; secrets)`
- THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`, then `secrets=0`

#### Scenario: A park-listed file deleted or created during a run counts as changed
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && rm $T20/live/policies.json && echo '{}' > $T20/live/new.json && bin/factory run finish $R --output-file $T20/out.md >/dev/null 2>&1; show)`
- THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json, $T20/live/new.json changed during run-0001-triage`

#### Scenario: A killed run is still compared
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && echo x > $T20/live/policies.json && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; show)`
- THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`

### Requirement: A changed escalate-listed file queues an escalation and the ticket goes on
When a file under `escalate` changes during a role run, the harness SHALL log an `escalation.queued` event whose item is `tripwire (escalate): <changed paths> changed during <run id>`, SHALL leave the ticket's state unchanged, and SHALL NOT write any of the file's contents to the store or a command's output.

#### Scenario: A changed escalate-listed file is queued and the ticket still moves
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && printf '{"chat": "T20-SECRET-D"}\n' > $T20/live/pairing.json && bin/factory run finish $R --output-file $T20/out.md > $T20/finish.out 2>&1; show; bin/factory log tail -n 1 --event escalation.queued > $T20/esc.out; python3 -c 'import json,sys; t=sys.stdin.read().strip(); print("items=%s" % (json.loads(t)["items"] if t else None))' < $T20/esc.out | sed "s|$T20|\$T20|g"; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null && echo moved=yes; secrets)`
- THEN it prints exactly `state=ready-for-triage reason=None`, then `items=['tripwire (escalate): $T20/live/pairing.json changed during run-0001-triage']`, then `moved=yes`, then `secrets=0`

#### Scenario: Unchanged listed files neither park nor escalate
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && bin/factory run finish $R --output-file $T20/out.md | tail -1 | python3 -c 'import json,sys; print("status=" + json.load(sys.stdin)["status"])'; show; echo "escalations=$(bin/factory log tail -n 100 --event escalation.queued | wc -l | tr -d ' ')")`
- THEN it prints exactly `status=ACCEPT`, then `state=ready-for-triage reason=None`, then `escalations=0`

### Requirement: A run dropped from the in-flight list without run finish is compared then, and only then
When a `ticket set` removes a run from the ticket's in-flight list without `run finish`, the harness SHALL compare that run's listed files as `run finish` would. A command that leaves the run in flight SHALL NOT compare it.

#### Scenario: Clearing an abandoned run compares it; an unrelated set does not
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && echo x > $T20/live/policies.json && bin/factory ticket set T-0001 title=Renamed >/dev/null 2>&1; show; bin/factory ticket set T-0001 'in_flight=[]' >/dev/null 2>&1; show)`
- THEN it prints exactly `state=ready-for-triage reason=None`, then `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`

### Requirement: Home-relative entries resolve against the account's home
A tripwire entry starting `~/` SHALL resolve against the account's home directory from the system user database, not against the `HOME` variable of the process running the command.

#### Scenario: A file under a substitute HOME is not watched
- WHEN `(T20=$(mktemp -d); mkdir -p $T20/home; echo a > $T20/home/.t0020-probe; echo a > $T20/live.json; TRIPWIRE="tripwire: {park: [\"~/.t0020-probe\", $T20/live.json]}"; export HOME=$T20/home; . ${TMPDIR:-/tmp}/t0020-bare.sh && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && echo b > $T20/home/.t0020-probe && echo b > $T20/live.json && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; bin/factory ticket show T-0001 --json | tail -1 | python3 -c 'import json,sys; t=json.load(sys.stdin); print("state=%s reason=%s" % (t["state"], (t["parked"] or {}).get("reason")))' | sed "s|$T20|\$T20|g")`
- THEN it prints exactly `state=parked reason=tripwire: $T20/live.json changed during run-0001-triage` (the account's real `~/.t0020-probe` does not exist and is unchanged; the substitute-`HOME` file is not named)

### Requirement: A tripwire list holds files only
`run start` SHALL be refused, with exit 2, a message naming the entry, and no run recorded, when a tripwire entry is an existing directory.

#### Scenario: A directory in the list refuses run start
- WHEN `(T20=$(mktemp -d); mkdir -p $T20/live; TRIPWIRE="tripwire: {park: [$T20/live]}"; . ${TMPDIR:-/tmp}/t0020-bare.sh && bin/factory run start --role triage --ticket T-0001 > $T20/start.out 2>&1; echo "exit=$? named=$(grep -q "$T20/live" $T20/start.out && echo yes || echo no) runs=$(ls $T20/store/runs 2>/dev/null | wc -l | tr -d ' ')")`
- THEN it prints exactly `exit=2 named=yes runs=0`

### Requirement: The baseline never travels with a store commit
The harness SHALL keep each file's start-of-run SHA-256 in exactly one file in the store, and the store's `.gitignore` SHALL exclude that file.

#### Scenario: The baseline digest is kept but not committable
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && H=$(printf '{"token": "T20-SECRET-A"}\n' | python3 -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())') && echo "held=$(grep -rl $H $T20/store | wc -l | tr -d ' ')" && git -C $T20/store init -q && git -C $T20/store add -A && echo "committed=$(git -C $T20/store grep --cached -l $H | wc -l | tr -d ' ')")`
- THEN it prints exactly `held=1`, then `committed=0`

### Requirement: An instance without a tripwire behaves as before
For an instance with no `tripwire` key, `run start` and `run finish` SHALL write and print exactly what they do today.

#### Scenario: No tripwire key, no new output or file
- WHEN `(TRIPWIRE=; . ${TMPDIR:-/tmp}/t0020-bare.sh && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && printf 'Type: bug\nTitle: F\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n' > $T20/out.md && bin/factory run finish $R --output-file $T20/out.md | tail -1 | python3 -c 'import json,sys; print(sorted(json.load(sys.stdin)))'; ls $FACTORY_STATE/runs/$R | tr '\n' ' '; echo)`
- THEN it prints exactly `['confidence', 'escalations', 'ok', 'run_id', 'status']`, then `meta.yaml output.md system-prompt.txt ` (with the trailing space)

#### Scenario: The harness suite passes under a throwaway HOME
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`
- THEN it exits 0 with no failures

### Requirement: The workflow scripts stop on a tripwire park
Each workflow script's role-running step SHALL return without routing when `run finish` reports that it parked the ticket.

#### Scenario: Both scripts check run finish for a park
This is a structural check: the workflow scripts need the Claude Code Workflow runtime and cannot run in the verifier.
- WHEN `for f in factory/workflows/intake.js factory/workflows/build.js; do echo "$f $(awk '/^async function runRole/{f=1} f&&/^}/{f=0} f' $f | grep -c '\.parked')"; done`
- THEN each of the two lines ends in a number of 1 or more, and reading those lines shows a `return null` taken when the `run finish` answer carries `parked`

=== specs/coding-standard/spec.md
## ADDED Requirements

### Requirement: The coding standard has a rule on patch targets and outside-path guards
`docs/coding.md` SHALL hold a rule 6, in the page's format (a `Check:` line, a `Principle:` line, a `Before` example from the 2026-10-04 incident and an `After:`), saying that tests reach a patched path through its module's attribute and that a new path outside the repository ships with a test guard against resolving it outside `tmp_path`. Rule 4 SHALL list rule 6 among the rules whose findings take no tag.

#### Scenario: Rule 6 is in the page's format and rule 4 names it
- WHEN `awk '/^## 6\. /{f=1;print "heading=yes";next} /^## |^The check order/{f=0} f&&/^Check: /{c=1} f&&/^Principle: /{p=1} f&&/^Before /{b=1} f&&/^After: /{a=1} f&&/tmp_path/{t=1} f&&/store\.policy_store_path/{m=1} END{print "check="(c?"yes":"no"), "principle="(p?"yes":"no"), "before="(b?"yes":"no"), "after="(a?"yes":"no"), "tmp_path="(t?"yes":"no"), "module_attr="(m?"yes":"no")}' docs/coding.md; grep -c 'rule 2, 3, 5 or 6' docs/coding.md; tail -2 docs/coding.md | head -1 | cut -c1-28`
- THEN it prints exactly `heading=yes`, then `check=yes principle=yes before=yes after=yes tmp_path=yes module_attr=yes`, then `1`, then `The check order (rule 1) and`

=== specs/factory-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the tripwire
The design doc SHALL carry a paragraph opening `**Tripwire on live files.**`; the instance template SHALL show the `tripwire` key; the README's **Built** list SHALL name the tripwire, and "Where a human decides" SHALL say how a tripwire park is resumed; the changelog's last numbered entry SHALL record the change, with numbering unbroken.

#### Scenario: Design doc, template and README name the tripwire
- WHEN `echo "design=$(grep -c '^\*\*Tripwire on live files\.\*\*' docs/design.md) template=$(grep -c 'tripwire' factory/instance.template.yaml) built=$(awk '/^\*\*Built\*\*/{f=1} /^\*\*Not built\*\*/{f=0} f' README.md | grep -ci 'tripwire') resume=$(grep -c 'A ticket the tripwire parked' README.md)"`
- THEN it prints `design=1`, `template=` a number of 1 or more, `built=` a number of 1 or more, and `resume=1`

#### Scenario: The changelog records the change in order
- WHEN `awk '/^[0-9]+\. /{n++; split($0,a,"."); if (a[1]+0!=n) bad=1; last=$0} END{print "contiguous=" (bad?"no":"yes"), "last_names_tripwire=" (last ~ /tripwire/ ? "yes":"no")}' docs/changelog.md`
- THEN it prints exactly `contiguous=yes last_names_tripwire=yes`

#### Scenario: The change adds no whitespace errors
- WHEN `git diff --check main...HEAD`
- THEN it exits 0 with no output

=== verification.md
## Acceptance

- A changed park-listed file parks the ticket → NEW. Today it prints `state=ready-for-triage reason=None` then `secrets=0`: the `tripwire` key is ignored and the ticket stays ready to move.
- A park-listed file deleted or created during a run counts as changed → NEW. Today: `state=ready-for-triage reason=None`.
- A killed run is still compared → NEW. Today: `state=ready-for-triage reason=None`.
- A changed escalate-listed file is queued and the ticket still moves → NEW. Today: `state=ready-for-triage reason=None`, `items=None` (no `escalation.queued` event), `moved=yes`, `secrets=0`.
- Unchanged listed files neither park nor escalate → REGRESSION. Today: `status=ACCEPT`, `state=ready-for-triage reason=None`, `escalations=0`.
- Clearing an abandoned run compares it; an unrelated set does not → NEW. Today both lines are `state=ready-for-triage reason=None`.
- A file under a substitute HOME is not watched → NEW. Today: `state=ready-for-triage reason=None`. An implementation that expanded `~` with `HOME` would print `reason=tripwire: $T20/home/.t0020-probe, $T20/live.json changed during run-0001-triage` and fail.
- A directory in the list refuses run start → NEW. Today: `exit=0 named=no runs=1`.
- The baseline digest is kept but not committable → NEW. Today: `held=0`, `committed=0`: no baseline exists.
- No tripwire key, no new output or file → REGRESSION. Today: `['confidence', 'escalations', 'ok', 'run_id', 'status']` and `meta.yaml output.md system-prompt.txt `.
- The harness suite passes under a throwaway HOME → REGRESSION. Today: `171 passed in 103.25s`.
- Both scripts check run finish for a park → NEW. Today it prints `factory/workflows/intake.js 0` and `factory/workflows/build.js 0`. This check is structural; see its scenario.
- Rule 6 is in the page's format and rule 4 names it → NEW. Today: no `heading=yes` line, then `check=no principle=no before=no after=no tmp_path=no module_attr=no`, then `0`, then `The check order (rule 1) and`.
- Design doc, template and README name the tripwire → NEW. Today: `design=0 template=0 built=0 resume=0`.
- The changelog records the change in order → NEW. Today: `contiguous=yes last_names_tripwire=no`.
- The change adds no whitespace errors → REGRESSION. Today it exits 0.

Every "today" output above was produced on `main` at `1c5f6a7` by running the scenario's WHEN exactly as written, after writing the two fixture scripts.

## Out-of-scope observations

- The routing table lets a `ticket transition --by workflow` move a ticket out of `parked` into most states. So any park written outside the workflow script, while that script still routes the same ticket, can be silently undone. Part C closes this for the tripwire only. A store-level guard on leaving `parked` would close it for every park.
- A run left in the in-flight list with no `run finish` blocks the ticket: `run start` refuses the next run. The only recovery today is `ticket set <id> in_flight=[]` or a manual `run finish --status-override KILLED`, and no page documents either.
