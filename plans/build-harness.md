# Plan: Build the spec factory, local-Mac v0 — sub-tickets

Parent: `specs/build-harness.md` in `danielphang/spec-factory` (https://github.com/danielphang/spec-factory/blob/main/specs/build-harness.md); approved text = `spec-build-v3.md` (STATUS NEEDS-SPLIT), pinned by the human gate with these rulings: every Open question on its proposed default; same-user deploy keys accepted for v0; post-hoc budget kill accepted; standing allowlist for real runs, never `bypassPermissions`; first acceptance run interactive; Nanobot gate commands unknown and carried as BH-1's open question; split along seams S1–S5.
Planner: planner · Plan version: 1 · Design doc: `spec-factory-v3.md`

## How the seams became sub-tickets

The spec's seams S1–S5 are the skeleton. Three adjustments were needed to make every sub-ticket independently mergeable *and* to let its acceptance items run at the time it lands; none changes what the spec asks for, only which PR carries which part.

1. **S2's own acceptance needs two commands the spec files under K (S4).** Items 25, 26, 30, 31 call `factory approve-pr` / `factory approve-guardrail`. Those two commands (they write one approval row each as the human identity) move into BH-2. The rest of K stays together.
2. **S3's acceptance needs most of K.** Items 35 and 38 call `factory queue`; 37, 48, 49 and 50 call `factory resolve`; `build.js` runs "after `factory approve-spec`". So the human surface must land *before* the workflows, not in parallel with them. The spec already says S3 and S4 share `factory/cli.py` and are not parallel; this plan simply orders K (BH-3) ahead of H (BH-5, BH-6). Item 62's "next intake run" clause is checked in BH-3 through `factory run compose` (the spec's one input mechanism) and re-checked by the real workflow in BH-5.
3. **S3 is split into three serial PRs**, because at the spec's own estimate it is the largest seam by far and holds two different kinds of change: guardrail text (`.claude/agents/**`, `factory/prompts/**`, `AGENTS.md`, which a human must read at the PR gate) and dispatcher code. BH-4 = render + agent definitions; BH-5 = `intake.js` + the shared `runRole`/clerk/stub machinery; BH-6 = `build.js` + the join. Each is under the spec's ~400-line guide and `build.js` is reviewed with `runRole` already proven by the intake cases.

Four items that sit under a seam heading in the spec but need nothing of that seam are placed where they can actually run: 59 (wall-clock kill, `run finish` only) → BH-1; 57 (redaction) → BH-2, where the key it greps for is minted (the redactor itself is built in BH-1 with an intermediate check); 33 (`--reverts` guard, store-only) → BH-2 as the spec marks it, with BH-1 checking the guard locally; 50 (`resolve --to spec-gate`, `--close`) → BH-3.

**Parallelism: none.** Every candidate pair shares `factory/cli.py` (and BH-3/BH-4 would also be in flight while each other's merge forces a re-verify, which buys nothing on a one-operator Mac). The chain is strictly serial, so no merge ever invalidates an in-flight sibling, and the `ready-implementers` rule dispatches one sub-ticket at a time by construction.

Store IDs: `<parent>.1` … `<parent>.7` map to BH-1 … BH-7 below.

Conventions every sub-ticket inherits from the parent: all paths relative to `~/dev/nanobot-upstream` on `feat/lionbot-v3`; fixture `pip install -e .`, `AS() { FACTORY_KEY=$1 "${@:2}"; }`, `O` = bare repo URL (BH-2 onward); the gate line (item 67) is `ruff check factory tests/factory && mypy factory && pytest -q tests/factory`; new tests only, under `tests/factory/`; `knowledge_vault/ProjectNotes/SPEC_MAINTENANCE_WORKFLOW.md`, `webui/package-lock.json`, `port_state.json`, `scripts/` are never touched (E9, item 64).

---

## BH-1 — Store, requests, audit log, results table, STATUS parser, composer, CLI guards

Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: none
Parallel-safe: no (first in chain; everything else edits `factory/cli.py` after it)
Scope: parent parts **A (skeleton only: `pyproject.toml`, `factory/cli.py` exit-code convention, `factory/config.yaml`)**, **B** (store, requests, `ticket new/show/set/transition/park`, `run start/compose/finish`, `spec add`, `subticket add`, all guards), **C** (log + run artifacts, `log tail`), **D** (results table; `results show`, `results record` writing the local store — identity enforcement is BH-2's hook), **H's STATUS parser** (`factory/status.py`, `factory status parse`), **I.2/I.5's CLI halves** (`run compose` for the store-only roles triage, spec_writer, critic, planner, including the round ≥ 2 and request-changes-notes sources; wall-clock KILLED in `run finish`), **J's redactor** (applied by every writer of `runs/**` and `log/*.jsonl`).

Design constraints carried from the parent (do not re-decide):
- The store root is the directory `~/factory/state` (override `FACTORY_STATE` for tests). In this sub-ticket it is a plain directory; BH-2 makes it the `factory/state` checkout and adds commit-and-push. Every write must therefore go through one `store.py` entry point so BH-2 adds push in one place. This is the additive staging the planner rules allow; it does not change the spec's layout (`tickets/ specs/ requests/ results/ approvals/ log/ runs/ audits/ retros/ queue.md`).
- `factory/config.yaml` is created here with **every** key the parent names, so later sub-tickets read it and never edit it: `repo_name: nanobot`, protected-path names, `max_rounds: {spec: 2, pr: 2}`, placeholders `{rounds: 2, audit_n: 5, retro_min: 3, spec_lines: 400}`, `gate_commands: ["pytest -q"]` (Open question 1 default), `time_budget_s: 1800`, `export_dir: knowledge_vault/sanitized_specs`, `models: {}`, and `routing:` = every edge of doc §Routing table plus the §Routing rules resolution edges, as `(from_state, to_state)` pairs over the B state list.
- `compose.py` is the only composer. For the four store-only roles the source lists are exactly: triage → `[requests/<ID>.md]`; spec_writer → `[tickets/<ID>.yaml, requests/<ID>.md]` + round ≥ 2 `[runs/<last critic run>/output.md, specs/<ID>/v<N-1>.md]` + after request-changes `[approvals/<ID>/changes-<n>.md or the notes path BH-3 defines]`; critic → `[specs/<ID>/v<N>.md]` + round ≥ 2 `[runs/<prior critic run>/output.md, specs/<ID>/v<N-1>.md]` (the writer's `## Responses` is inside v<N>); planner → `[specs/<ID>/v<approved_version>.md]`. Leave a declared, unimplemented entry (exit 2 `compose: role X not supported yet`) for implementer, reviewer, verifier, retro; BH-6 and BH-7 fill them.
- Redaction (J): replace any private-key body (`-----BEGIN … PRIVATE KEY-----` … `END`) and the value of every env var matching `*KEY*|*TOKEN*|*SECRET*` in the harness's own env with `[REDACTED]` before writing `runs/<id>/*` or a log line.

Acceptance (parent items, run as written): **1, 2, 3, 4, 5, 8, 9, 10, 59, 68, 69, 70, 67**.
Intermediate checks (NEW; same fixture, local store, no bare repo):
- Item 6 without `AS`/push: `factory ticket set T-0001 head=H; factory results record T-0001 --head H --role reviewer --output o.md` → `results/H/reviewer.yaml`, `results show` → `reviewer: APPROVE`, `missing: ci, verifier for H`; after `head=H2` a record for `H` → `result.stale-discarded` logged, `missing: ci, reviewer, verifier for H2`.
- Item 33's guard locally: `factory ticket new --type revert --branch revert/x --reverts deadbeef` → exit 2, stderr `deadbeef is not a merged head`; `factory ticket new --type retro --branch retro/2026-w40` → prints `R-…`, `type: retro`, `parent: null`.
- Item 39's composer half: ticket with `specs/T-0001/v1.md`, `v2.md` (v2 contains `## Responses`), a finished critic run whose `output.md` is `critic-1` text, `round.spec: 2`; `run start --role critic; run compose` → `input.md` contains the `## Responses` text, the `critic-1` text, and v1; `meta.yaml` `input_sources` lists exactly those three paths. With `round.spec: 1` → `input_sources: [specs/T-0001/v1.md]` only (item 42's critic clause).
- Item 57's mechanism: `printf -- '-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n-----END OPENSSH PRIVATE KEY-----\n' > k.md; factory run finish RUN --output-file k.md` → `runs/RUN/output.md` contains `[REDACTED]` and not `abc`; `FAKE_TOKEN=zzz factory run finish …` with `zzz` in the file → no `zzz` in `output.md`.
- `factory subticket add T-0001 --file s.md --depends-on T-0001.1 --parallel-safe no` → `T-0001.2` in `waiting-dependencies`, `parallel_safe: false`; with `--depends-on ''` → `ready-for-implementer` (item 34's store half).
- `factory ticket show` prints every schema key from B with `null`/`[]` when unset.
Tests to change: none
Protected paths: **dependencies** `pyproject.toml` (adds the `factory` console script, `pyyaml`, dev `pytest ruff mypy`); **infra** `factory/config.yaml` (new)
Out of scope: anything git-server side (`factory init`, keys, hook, `gate.py`, `merge`, pushing the state); `factory render`, agent definitions, SKILL.md, AGENTS.md; `queue`, `approve-*`, `resolve`, `reply`, `export`, `request-changes`; the workflow scripts; `ready-implementers`/`ready-checkers`/`ticket head`/`run cleanup`; `audit-sample`, `retro-input`; composer entries for implementer/reviewer/verifier/retro; any file under `scripts/`, `knowledge_vault/ProjectNotes/`, `webui/`, `port_state.json`.
Open question carried (per the gate's ruling): Nanobot's own test and lint commands for `{gate commands}` are unknown; `config.yaml` ships `gate_commands: ["pytest -q"]` and nothing in BH-1 depends on the value.

---

## BH-2 — Bare repo, identities and keys, pre-receive hook, merge gate and client, `factory init`

Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: BH-1
Parallel-safe: no (edits `factory/cli.py`, `store.py`, `results.py` from BH-1)
Scope: parent parts **E** (`identities.yaml`, keys, forced commands, local-transport fallback), **F** (hook shim, `factory/hook.py`, `paths.yaml`, rules 1–5, `hook.log`, `factory log import-hook`), **G** (`gate.py` shared by hook and client, `factory merge`, dependant cascade, parent close, head-does-not-contain-main routing), **A's `factory init` and `factory install-hook`**, the two approval-row writers from **K** (`factory approve-pr ID --head SHA`, `factory approve-guardrail ID --head SHA`, each writing `approvals/<ID>/{pr,guardrail}-<SHA>.yaml` with `by:` and pushing as the human identity), and the **state push**: every store write from BH-1 now commits on `~/factory/state` (branch `factory/state`) and pushes to `$O` as the caller's identity (`FACTORY_KEY` → `GIT_SSH_COMMAND`; `FACTORY_IDENTITY` local-path fallback when sshd is absent, exactly as E states).

Design constraints carried from the parent (do not re-decide): the hook reads only server-side `main:factory/identities.yaml`, `main:factory/paths.yaml` and `factory/state` as stored before the push; `install-hook` copies the installed package to `~/factory-remote/hook-env/` with an absolute `FACTORY_HOOK_PYTHON` in the shim; the piece-7 exception is the two branches of F.4 and nothing else; the revert check is the byte-for-byte `cmp` of E5; `init` seeds `main` from `feat/lionbot-v3`, never touches the four frozen paths in E9. Same-user deploy keys with forced commands are the accepted v0 design (gate ruling on Open question 3); do not add a stronger scheme.

Acceptance (parent items, run as written): **6, 7, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 57, 67**.
Intermediate checks (NEW):
- `factory init` twice → second run exit 2 `already initialised` (or equivalent), bare repo and keys unchanged (`ls -la ~/factory-remote/keys/` same mtimes); `ls ~/factory-remote/keys/` → exactly `daniel harness implementer retro` plus `.pub` files, mode 600.
- `factory install-hook` then `git -C ~/factory-remote/nanobot.git cat-file -e refs/heads/main:factory/hook.py` → exists; edit a local copy of `factory/hook.py` to `sys.exit(1)` without reinstalling → item 22's merge still succeeds (hook-env is a copy).
- `factory log import-hook` after item 29 → one `merge.refused` event whose `detail` is the hook's stderr line.
- `git -C ~/dev/nanobot-upstream status --porcelain` after `factory init` → no line for the four E9 paths (item 64's prefix).
Tests to change: none
Protected paths: **infra** `factory/hooks/**` (new), `factory/paths.yaml` (new); **credentials** `factory/identities.yaml` (new)
Out of scope: `approve-spec`, `request-changes`, `resolve`, `queue`, `queue apply`, `reply`, `export`; agent definitions, render, SKILL.md, AGENTS.md; workflows and their clerk commands; Docker, per-Unix-user isolation, cron; the GitHub remote; `scripts/`, frozen E9 paths.
Not verified by the spec writer and therefore an implementer stop-and-escalate point, not a thing to improvise around: ssh forced commands on macOS Remote Login. If sshd is unavailable on the build machine, implement the captured local-transport fallback (E4) and say so in the PR; items 12 and 56 state both acceptable outputs.

---

## BH-3 — Human surface, resolution commands, spec approval and export

Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: BH-2
Parallel-safe: no (edits `factory/cli.py`, which BH-4 also edits)
Scope: parent part **K** minus the two approval-row writers already in BH-2: `factory queue` (regenerates `queue.md` with the five sections and `Decision:` lines), `factory queue apply`, `factory approve-spec ID [--version N] [--edit FILE]` (pins, copies "Tests to change" and Risk paths into the ticket, writes `approvals/<ID>/spec-v<N>.yaml`, → `ready-for-planner`, exports), `factory export ID` (writes `<config export_dir>/<ID>.md`, event `spec.exported`), `factory request-changes ID --notes FILE`, `factory resolve ID (--answer | --ruling --to implementer [--amend-subticket] [--amend-spec] | --redispatch | --close | --to spec-gate)` with `approvals/<ID>/resolve-<n>.yaml` and `human.resolved`, and piece 9's `factory reply ID --file F` (writes `<source dir>/<file>.reply.md` beside the imported request, appends to `queue.md`, event `reply.sent`). Extend `compose.py` so the spec_writer source list includes request-changes notes and the triage/spec_writer lists include `## Answer <n>` (already inside `requests/<ID>.md` after `--answer`), and so the implementer entry (filled in BH-6) can find a ruling at a fixed path (`approvals/<ID>/resolve-<n>.yaml` + the ruling file copied to `approvals/<ID>/ruling-<n>.md`). Every human command refuses without a human identity via the hook (`approval rows need a human pusher`), which BH-2 already enforces; this sub-ticket only has to push as `FACTORY_KEY`.

Acceptance (parent items, run as written): **50, 60, 61, 62, 63, 67**.
Note on 62: its last clause ("the next `intake` run's writer `input.md` contains the notes") is verified here with the spec's one composer — `factory run start --role spec_writer --ticket T-0001 --head none; factory run compose <run_id>` → `input.md` contains the notes and `input_sources` names the notes path — and re-verified by the real intake workflow in BH-5.
Intermediate checks (NEW):
- Item 37's resolution half: ticket in `waiting-requester` with `request: requests/T-0001.md` imported from `kv/specs/a.md`; `factory reply T-0001 --file m.md` → `kv/specs/a.reply.md` exists, `reply.sent` logged, `queue.md` "Waiting on requester" lists `T-0001`; `AS daniel factory resolve T-0001 --answer ans.md` → `ready-for-triage`, `requests/T-0001.md` ends with `## Answer 1` + the answer; `run start --role triage; run compose` → `input.md` contains the answer.
- Item 48's store half: parked `T-0001.1` (via `factory ticket park`) with `round.pr: 2`; `AS daniel factory resolve T-0001.1 --ruling notes.md --to implementer --amend-subticket sub2.md --amend-spec spec2.md` → `ready-for-implementer`, `round.pr: 0`, `specs/T-0001/subticket.md` = `sub2.md`, `specs/T-0001/v<N+1>.md` = `spec2.md`, `approved_version: N+1`, `approvals/T-0001/spec-v<N+1>.yaml` exists, `knowledge_vault/sanitized_specs/T-0001.md` = `spec2.md`.
- Item 49's resolution half: parked `T-0001.1` with `parked.reason: budget kill: reviewer`; `AS daniel factory resolve T-0001.1 --redispatch` → `ready-for-checks`, `round.pr` unchanged.
- `factory queue apply` with a `Decision:` line whose verb is unknown → exit 2, nothing applied, no `human.resolved`.
- `git -C ~/dev/nanobot-upstream status --porcelain` after `init`, `intake`, `approve-spec` → only `knowledge_vault/sanitized_specs/T-0001.md` added beyond the pre-existing lines; `webui/package-lock.json` listed exactly as before (item 64's prefix).
Tests to change: none
Protected paths: none (reads `factory/config.yaml` `export_dir`; does not edit it)
Out of scope: `approve-pr`/`approve-guardrail` (BH-2); `factory render`, agent definitions, SKILL.md, AGENTS.md; the workflows and `ready-implementers`/`ready-checkers`; mirroring `queue.md` into any tracker (Open question 2 default: none); renaming `knowledge_vault/specs/` to `tickets/`; `audit-sample`, `retro-input`; `scripts/`, frozen E9 paths.

---

## BH-4 — `factory render`, preamble, the ten agent definitions, AGENTS.md section

Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: BH-2 (item 56 needs the bare repo and a `ticket/*` branch); ordered after BH-3 only because both edit `factory/cli.py`
Parallel-safe: no (edits `factory/cli.py`, which BH-3 edits; must not be in flight with BH-3)
Scope: parent part **A's render and definitions**: `factory render` writes `factory/prompts/preamble.md` (doc §Shared preamble, placeholders filled from `config.yaml`) and the eight `.claude/agents/factory-<role>.md` from the doc text copied verbatim, with frontmatter `tools:` per R6 (checkers and read-only authors `Read, Grep, Glob, Bash`; implementer and retro add `Edit, Write`), body first line `Read factory/prompts/preamble.md before anything else`, and the one added handoff rule in the triage and spec-writer definitions (addendum 2, quoted in A). Hand-written: `.claude/agents/factory-clerk.md` (`tools: Bash`, allowed `Bash(factory *)`, `Bash(git *)`) and `.claude/agents/factory-stub.md` (`Read` only, plus `Bash(git *)` solely for the implementer stub's `PUSH:` trailer as the build-workflow section states; returns `args.stubs/<role>-<n>.md` verbatim or an empty string when absent). The implementer definition's `env:` for `GIT_SSH_COMMAND` with the implementer key (I.3); if agent-definition frontmatter does not support `env:`, implement the `factory git-push ticket/<ID>` wrapper instead (Open question 8, default accepted) and say which in the PR. `AGENTS.md` gains the "Factory" section naming the layout, the gates, and the guardrail paths `.claude/agents/factory-*`, `.claude/skills/factory*`, `factory/prompts/**`. The doc text itself is never edited.

Acceptance (parent items, run as written): **54, 55, 56, 67**.
Item 56 needs a real model call and, per the gate ruling, runs in an attended interactive session with the standing allowlist from R6; it is the only item in the whole plan that is not stub-driven.
Intermediate checks (NEW):
- `factory render` is idempotent: run twice → `git status --porcelain .claude factory/prompts` empty after the second run.
- `diff <(sed -n '/^## 4. Planner/,/^```$/p' spec-factory-v3.md | sed -n '/^```text/,/^```/p' | sed '1d;$d') <(body of .claude/agents/factory-planner.md after its first line)` → identical modulo the filled `{…}` placeholders (verbatim copy, item A's rule); the same for the other seven roles.
- `grep -c 'Read factory/prompts/preamble.md before anything else' .claude/agents/factory-*.md` → `1` for each of the eight role files.
- `grep -E '^tools:' .claude/agents/factory-stub.md` → contains `Read`, not `Edit`/`Write`.
Tests to change: none
Protected paths: none. **Guardrail paths created or edited** (merge gate will require a human PR approval, piece 8): `.claude/agents/**` (new), `factory/prompts/**` (new), `AGENTS.md` (edit).
Out of scope: `.claude/skills/factory/SKILL.md` (BH-5, since it documents the workflows); the workflow scripts; any wording change to the eight prompts or the preamble beyond placeholder filling and the one addendum-2 rule; `scripts/spec_lint.py` (kept, Open question 7 default); `scripts/`, frozen E9 paths.

---

## BH-5 — Intake workflow: `runRole`, clerk calls, stub seam, `/factory` entry skill

Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: BH-3, BH-4
Parallel-safe: no (edits `factory/cli.py`; next in chain)
Scope: parent part **H** for `intake.js` only, with the common `runRole(role, ticket, head)` step exactly as H defines it (clerk `run start` → clerk `run compose` → `agent()` on `factory-stub` or `factory-<role>` with the pointer prompt → KILLED condition `out === null || out.trim() === ''` → clerk `run finish`), the stub call-index counter in the script, the `MAX` read from `config.yaml` via the clerk, the unknown-STATUS `harness-bug` park, and the clerk running `factory log import-hook` each phase; **I.1, I.2, I.5, I.6** as they apply to the four intake roles (`system-prompt.txt` recorded by the clerk, `meta.yaml` complete with `wall_s` and `workflow_run_id`); **A's `.claude/skills/factory/SKILL.md`** (how to run `factory intake`, then `Workflow({scriptPath: 'factory/workflows/intake.js', args: {ticket, stubs?}})`, approve at the gate, then `build.js`, plus the human commands; the `build` and `retro` lines may point at scripts BH-6/BH-7 add, flagged "lands in the next sub-ticket"); the stub fixture directories `tests/factory/fixtures/stubs/{accept-approve,reject,needs-human,clarify,revise-twice,banana,escalations}`; and a pytest driver that runs the ⟨wf⟩ line from the Acceptance preamble (`claude -p --restricted --tools default --allowedTools "Bash(factory *)" "Bash(git *)" Read Skill Workflow "/factory run intake T-0001 --stubs …"`) and asserts on the store, skipped with a clear reason when `claude` is absent or the Workflow tool is unavailable under `-p` (the spec's stated interactive fallback is then the acceptance path, and the PR says so).

Design constraints carried from the parent: neither script reads a file or composes input text (item 42's grep); the STATUS a role "has" is what `factory run finish` parsed; the CLI guards from BH-1 are authoritative, and an exit 2 from `transition` or `run start` becomes `park --reason 'harness-bug: <stderr>'`.

Acceptance (parent items, run as written): **35, 36, 37, 38, 39, 40, 41, 42, 67**.
Intermediate checks (NEW):
- Item 62's workflow half: after `request-changes`, running case `accept-approve` again → `runs/<spec_writer run>/input.md` contains the notes.
- Item 58 for intake runs: after case `accept-approve`, every `runs/<run_id>/` has `meta.yaml`, `input.md`, `system-prompt.txt`, `output.md`; `meta.yaml` has `wall_s` and `workflow_run_id`.
- Stub KILLED seam on an intake role: case `accept-approve` with `critic-1.md` deleted → `status: parked`, `parked.reason: budget kill: critic`, `round.spec: 1` unchanged, `run.killed` logged; `AS daniel factory resolve T-0001 --redispatch` → `ready-for-critic`; re-run with the file restored → exactly one new `run.started` (critic).
- Not-verified fallback recorded: the PR states whether the Workflow tool ran under `claude -p` on the build machine or the interactive fallback was used, with the captured command and output.
Tests to change: none
Protected paths: **infra** `factory/workflows/**` (new: `intake.js`). **Guardrail path created**: `.claude/skills/factory/SKILL.md`.
Out of scope: `build.js`, `retro.js`, `ready-implementers`, `ready-checkers`, `ticket head`, `run cleanup`, checker checkouts, composer entries for implementer/reviewer/verifier/retro, `results record --role verifier` ci row (L); any cron/launchd dispatcher; `scripts/`, frozen E9 paths.

---

## BH-6 — Build workflow: planner → implementer → reviewer ‖ verifier → join → merge; checker isolation; verifier as CI

Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: BH-5
Parallel-safe: no (edits `factory/cli.py`, `compose.py`, `results.py`, SKILL.md; next in chain)
Scope: parent part **H** for `build.js` (phases Plan and Build, `buildOne`, the `parallel()` join as barrier, the join rules in H.3 including KILLED → park with round unchanged, ESCALATE/SPEC-DEFECT → park with both outputs, all-green → `factory merge`, head-does-not-contain-main → continue with round unchanged, else `pr:+1` or max-round park; resumption after `--ruling`/`--redispatch` from the state the store holds); the clerk-facing commands **`factory ticket ready-implementers PARENT`**, **`factory ticket ready-checkers ST`**, **`factory ticket head ST`** (from `git ls-remote`), **`factory run cleanup RUN`**, the clerk-made checker checkout `~/factory/runs/<run_id>/wt` of the head (**I.3**, checkers hold no key: `FACTORY_KEY`/`GIT_SSH_COMMAND` absent from their environment); **`compose.py` entries** for implementer (sub-ticket, pinned parent spec, `~/factory/clone` `AGENTS.md`; round ≥ 2 both checker outputs + CI result, or the ruling from BH-3's fixed path; the implementer worktree branches from current `main` at dispatch and `meta.yaml` records `base`) and for reviewer/verifier (`git diff main...head`, the PR description = the implementer run's `output.md`, sub-ticket, parent spec; round ≥ 2 both prior outputs and the implementer's `Responses`); **L** (`results record --role verifier` also writes `results/<head>/ci.yaml` from the `Gate suite:` line, `FAIL` + `detail: missing Gate suite line` when absent); the implementer stub's `PUSH:` trailer; stub fixtures `plan-three`, `review-fix`, `parking-wins`, `gate-fail`, `reviewer-killed`; the `build` entry in SKILL.md made live; the pytest driver extended to the build cases.

Design constraints carried from the parent: never a second implementer run on a branch with one in flight (CLI guard from BH-1 plus `ready-implementers`); `parallel_safe: false` sub-tickets wait while any sibling implementer is in flight; results rows go through `results record` so the stale rule applies and the `Commit:` line must equal the current head; the KILLED condition is post-hoc and the only manual kill is the user skipping the agent (gate ruling on Open question 4; do not build a pre-emptive kill).

Acceptance (parent items, run as written): **43, 44, 45, 46, 47, 48, 49, 51, 52, 58, 64, 67**.
Intermediate checks (NEW):
- Planner ESCALATE: case `plan-escalate` (`planner-1.md` STATUS ESCALATE) → `status: parked`, no sub-tickets created, `queue.md` lists the parent under "Parked".
- Implementer BLOCKED: case `review-fix` with `implementer-1.md` STATUS BLOCKED → `T-0001.1` `parked`, no checker `run.started`.
- `factory ticket ready-checkers T-0001.1` with a `reviewer` row on the current head and none for `verifier` → `["verifier"]`; with both → `[]`.
- Checker environment: in case `review-fix`, `runs/<reviewer run>/system-prompt.txt` is the reviewer definition and `grep -cE 'FACTORY_KEY|GIT_SSH_COMMAND' runs/<reviewer run>/meta.yaml` → `0` (the clerk records the env names it passed, not values).
Tests to change: none
Protected paths: **infra** `factory/workflows/**` (`build.js` new). **Guardrail path edited**: `.claude/skills/factory/SKILL.md`.
Out of scope: `retro.js`, `retro-input`, `audit-sample`; Docker, cron, pre-emptive kills, per-agent token caps; model choice per role; a separate CI service; `scripts/`, frozen E9 paths.

---

## BH-7 — Audit sample, retro input, retro workflow

Parent: `specs/build-harness.md` in `danielphang/spec-factory`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: BH-6
Parallel-safe: no (last in chain; edits `factory/cli.py`, `compose.py`, SKILL.md)
Scope: parent part **M**: `factory audit-sample [--since 7d] [--n 5]` → `audits/<date>.yaml` (and, per Risk R2, prints the two baseline numbers for the period from `merge.done`, `round.pr` and `meta.yaml` diff stats — recorded, not asserted); `factory retro-input [--since <last>]` composing the doc §Routing table Retro row to stdout (`incidents`, `instruction files`, `previous proposals`, `counts per role`); `factory/workflows/retro.js` (one `runRole('retro', …, {isolation: 'worktree'})` with the retro key; `PROPOSED` → clerk `factory ticket new --type retro --branch retro/<date>` with `head` from `git ls-remote`, `queue.md` "Guardrail gate"; `NO-CHANGES` → `run.finished` only); the `compose.py` retro entry (= `retro-input` output); the `retro` entry in SKILL.md made live; stub fixtures `retro-nochanges`, `retro-proposed` (the latter's stub pushes `retro/<date>` with the retro key).

Acceptance (parent items, run as written): **53, 65, 66, 67**.
Intermediate checks (NEW):
- `factory audit-sample --n 5` with 0 merged → prints `note: only 0 merged in period`, `audits/<date>.yaml` written with an empty list, exit 0.
- `factory retro-input --since <date after every event>` → the four section headers present, every count `0`, exit 0.
- After `retro-proposed`, `AS daniel factory approve-guardrail R-<date> --head R; factory merge R-<date>` → exit 0 (the piece-7 retro exception, item 30, now reached end to end through the workflow).
Tests to change: none
Protected paths: **infra** `factory/workflows/**` (`retro.js` new). **Guardrail path edited**: `.claude/skills/factory/SKILL.md`.
Out of scope: scheduling the weekly audit/retro (`launchctl`, cron: deferred); cost reporting; any change to the retro prompt text; `scripts/`, frozen E9 paths.

---

## Order and parallel groups

Serial chain, one group of one at every step:
BH-1 → BH-2 → BH-3 → BH-4 → BH-5 → BH-6 → BH-7.

No two sub-tickets run in parallel. BH-3 and BH-4 are the only pair with no semantic dependency; both edit `factory/cli.py`, so each is marked `parallel_safe: no` and `ready-implementers` will hold BH-4 until BH-3 merges (or vice versa if BH-4 is dispatched first; the plan lists BH-3 first).

## Coverage map (parent criterion → sub-ticket)

| Items | Sub-ticket | Note |
|---|---|---|
| 1, 2, 3, 4, 5, 8, 9, 10 | BH-1 | |
| 68, 69, 70 | BH-1 | CLI guards |
| 59 | BH-1 | wall-clock KILLED is `run finish` only |
| 6, 7 | BH-2 | ⟨bare⟩; BH-1 checks the stale rule locally |
| 11–20 | BH-2 | permissions |
| 21–34 | BH-2 | merge gate; 25, 26, 30, 31 use `approve-pr`/`approve-guardrail`, moved into BH-2; 33 implemented in BH-1, verified ⟨bare⟩ here |
| 57 | BH-2 | redactor built in BH-1; the key it greps for is minted here |
| 50, 60, 61, 62, 63 | BH-3 | 62's "next intake run" clause via `run compose` here, re-verified in BH-5 |
| 54, 55, 56 | BH-4 | 56 is the one real-model, interactive item |
| 35–42 | BH-5 | intake workflow |
| 43–49, 51, 52 | BH-6 | build workflow; 48 and 49 also exercised store-side in BH-3 |
| 58 | BH-6 | all run kinds exist only after BH-6 (checker checkouts cleaned); BH-5 checks the intake subset |
| 64 | BH-6 | needs "one ⟨wf⟩ run"; BH-2 and BH-3 check the prefix after `init`/`intake`/`approve-spec` |
| 53, 65, 66 | BH-7 | |
| 67 | BH-1 … BH-7 | gate line on `main` after every merge |

Count: 10 + 3 + 1 + 2 + 10 + 14 + 1 + 5 + 3 + 8 + 9 + 1 + 1 + 3 = 70 (items 1–66, 68–70, and 67). **Uncovered: none.**

## Risk notes for the implementers (from the parent's Risk section, per sub-ticket)

- R1 (identity advisory in v0) is BH-2's territory and is accepted by the gate; BH-2 must not try to close it.
- The fail-closed hook (a bug blocks every merge) lands in BH-2; from BH-3 on, every sub-ticket's own merge runs through it, which is the intended bootstrap.
- R6 permission mode: the ⟨wf⟩ driver line and the real-run allowlist are fixed by the ruling; BH-5/BH-6 may not widen them, and `bypassPermissions`/`dontAsk` appear nowhere (item 54 is BH-4's, but BH-5–BH-7 must keep it true).
- Guardrail paths (`.claude/**`, `factory/prompts/**`, `AGENTS.md`) land in BH-4, BH-5, BH-6, BH-7 → each of those PRs needs the piece-8 human approval on its head besides APPROVE and VERIFIED.

STATUS: PLANNED
CONFIDENCE: medium — the decomposition follows the spec's own seams with three documented reassignments (two K commands into S2; K ordered before H; S3 split into definitions / intake / build), none of which alters a requirement; every one of the 70 items has a sub-ticket where its fixture exists at landing time. Medium rather than high because the spec's own not-verified list (sshd forced commands on macOS, agent-definition `env:`, Workflow under `claude -p`) lands in BH-2, BH-4 and BH-5 and each may force the stated fallback, and because BH-6 is still the largest PR in the chain.
ESCALATIONS:
- Carried per the gate ruling: Nanobot's own test/lint commands for `{gate commands}` remain unknown (Open question 1); BH-1 ships the default `pytest -q` in `config.yaml` and nothing downstream is blocked on it, but the first real (non-stub) verifier run will use whatever is there.
- Item 56 requires a live model call and an attended session (gate ruling: first acceptance run interactive); it cannot be made stub-driven without changing what it checks, so BH-4's verification is partly manual.
- Seam reorder for the record, not a blocker: the spec's "S4 parallel-safe with S3" does not hold once S3's acceptance items are traced (35, 37, 38, 48, 49 and the `approve-spec` precondition all need K), so K (BH-3) is ordered before H (BH-5/BH-6). If the human prefers the spec's literal seam order, the alternative is to fold K into the workflow sub-ticket, which would make that PR roughly 1,000 lines.
