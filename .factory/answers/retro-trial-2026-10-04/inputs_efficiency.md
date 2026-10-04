# Retro inputs: spec-factory instance B store, 2026-10-01 to 2026-10-04 (first retro; no prior proposals)

Store root: /Users/dphang/dev/spec-factory/.factory/state. Every path below is relative to it unless absolute. Read the full output of any run you cite.

## 1. Outcome signals (runs that did not end in their role's success status)

| when | ticket | run | role | model | status | output |
|---|---|---|---|---|---|---|
| 2026-10-01T16:31 | T-0001 | run-0001-triage | triage | opus | NEEDS-HUMAN | runs/run-0001-triage/output.md |
| 2026-10-01T17:15 | T-0005 | run-0011-triage | triage | opus | NEEDS-HUMAN | runs/run-0011-triage/output.md |
| 2026-10-01T17:19 | T-0006 | run-0012-triage | triage | opus | NEEDS-HUMAN | runs/run-0012-triage/output.md |
| 2026-10-01T17:21 | T-0007 | run-0013-triage | triage | opus | NEEDS-HUMAN | runs/run-0013-triage/output.md |
| 2026-10-01T20:33 | T-0007 | run-0024-spec_writer | spec_writer | opus | NEEDS-HUMAN | runs/run-0024-spec_writer/output.md |
| 2026-10-01T20:46 | T-0008 | run-0027-triage | triage | opus | NEEDS-HUMAN | runs/run-0027-triage/output.md |
| 2026-10-01T21:06 | T-0008 | run-0029-spec_writer | spec_writer | opus | NEEDS-HUMAN | runs/run-0029-spec_writer/output.md |
| 2026-10-01T21:09 | T-0003 | run-0031-planner | planner | opus | ESCALATE | runs/run-0031-planner/output.md |
| 2026-10-01T21:09 | T-0002 | run-0030-planner | planner | opus | ESCALATE | runs/run-0030-planner/output.md |
| 2026-10-01T21:10 | T-0001 | run-0032-planner | planner | opus | ESCALATE | runs/run-0032-planner/output.md |
| 2026-10-01T21:23 | T-0008 | run-0036-critic | critic | fable | REVISE | runs/run-0036-critic/output.md |
| 2026-10-02T06:28 | T-0010 | run-0040-triage | triage | opus | NEEDS-HUMAN | runs/run-0040-triage/output.md |
| 2026-10-02T06:40 | T-0010 | run-0043-critic | critic | fable | REVISE | runs/run-0043-critic/output.md |
| 2026-10-03T06:49 | T-0012 | run-0050-spec_writer | spec_writer | opus | NEEDS-SPLIT | runs/run-0050-spec_writer/output.md |
| 2026-10-03T06:58 | T-0012 | run-0051-critic | critic | fable | REVISE | runs/run-0051-critic/output.md |
| 2026-10-03T07:03 | T-0012 | run-0052-spec_writer | spec_writer | opus | NEEDS-SPLIT | runs/run-0052-spec_writer/output.md |
| 2026-10-03T07:58 | T-0012.2 | run-0057-verifier | verifier | fable | SPEC-DEFECT | runs/run-0057-verifier/output.md |
| 2026-10-03T08:16 | T-0012.2 | run-0062-verifier | verifier | opus | FAILED | runs/run-0062-verifier/output.md |
| 2026-10-03T09:11 | T-0012.4 | run-0069-implementer | implementer | opus | BLOCKED | runs/run-0069-implementer/output.md |
| 2026-10-03T09:22 | T-0012.5 | run-0071-verifier | verifier | opus | SPEC-DEFECT | runs/run-0071-verifier/output.md |
| 2026-10-03T09:27 | T-0012.5 | run-0074-reviewer | reviewer | fable | KILLED | runs/run-0074-reviewer/output.md |
| 2026-10-03T09:45 | T-0012.4 | run-0076-reviewer | reviewer | fable | KILLED | runs/run-0076-reviewer/output.md |
| 2026-10-03T15:51 | T-0012.6 | run-0092-verifier | verifier | opus | SPEC-DEFECT | runs/run-0092-verifier/output.md |
| 2026-10-03T16:45 | T-0012 | run-0102-verifier | verifier | opus | SPEC-DEFECT | runs/run-0102-verifier/output.md |
| 2026-10-03T17:07 | T-0013 | run-0104-triage | triage | opus | NEEDS-HUMAN | runs/run-0104-triage/output.md |
| 2026-10-03T22:18 | T-0014 | run-0115-critic | critic | fable | REVISE | runs/run-0115-critic/output.md |
| 2026-10-03T23:13 | T-0015 | run-0126-triage | triage | opus | NEEDS-HUMAN | runs/run-0126-triage/output.md |

## 2. Parks (the harness stopped a ticket for a human)

| when | ticket | from | reason | outputs |
|---|---|---|---|---|
| 2026-10-01T16:31 | T-0001 | ready-for-triage | NEEDS-HUMAN from triage |  |
| 2026-10-01T17:16 | T-0005 | ready-for-triage | NEEDS-HUMAN from triage |  |
| 2026-10-01T17:19 | T-0006 | ready-for-triage | NEEDS-HUMAN from triage |  |
| 2026-10-01T17:21 | T-0007 | ready-for-triage | NEEDS-HUMAN from triage |  |
| 2026-10-01T20:34 | T-0007 | ready-for-spec-writer | NEEDS-HUMAN from spec writer |  |
| 2026-10-01T20:46 | T-0008 | ready-for-triage | NEEDS-HUMAN from triage |  |
| 2026-10-01T21:06 | T-0008 | ready-for-spec-writer | NEEDS-HUMAN from spec writer |  |
| 2026-10-01T21:09 | T-0003 | ready-for-planner | ESCALATE from planner |  |
| 2026-10-01T21:10 | T-0002 | ready-for-planner | ESCALATE from planner |  |
| 2026-10-01T21:10 | T-0001 | ready-for-planner | ESCALATE from planner |  |
| 2026-10-02T06:28 | T-0010 | ready-for-triage | NEEDS-HUMAN from triage |  |
| 2026-10-03T07:58 | T-0012.2 | checks-in-flight | SPEC-DEFECT from verifier |  |
| 2026-10-03T09:11 | T-0012.4 | ready-for-implementer | BLOCKED from implementer |  |
| 2026-10-03T09:23 | T-0012.5 | checks-in-flight | SPEC-DEFECT from verifier |  |
| 2026-10-03T09:32 | T-0012.5 | checks-in-flight | budget kill: reviewer |  |
| 2026-10-03T09:55 | T-0012.4 | checks-in-flight | budget kill: reviewer |  |
| 2026-10-03T15:51 | T-0012.6 | checks-in-flight | SPEC-DEFECT from verifier |  |
| 2026-10-03T16:46 | T-0012 | ready-for-parent-verify | SPEC-DEFECT from parent-close verifier |  |
| 2026-10-03T16:58 | T-0012 | ready-for-parent-verify | archive: no spec store (factory init not run) {'ok': false, 'error': 'no spec store (factory init not run)'} |  |
| 2026-10-03T17:07 | T-0013 | ready-for-triage | NEEDS-HUMAN from triage |  |
| 2026-10-03T18:35 | T-0013 | ready-for-parent-verify | archive: no spec store (factory init not run) {'ok': false, 'error': 'no spec store (factory init not run)'} |  |
| 2026-10-03T22:27 | T-0014 | ready-for-planner | harness-bug: subticket add:  |  |
| 2026-10-03T22:54 | T-0014 | ready-for-parent-verify | archive:  |  |
| 2026-10-03T23:13 | T-0015 | ready-for-triage | NEEDS-HUMAN from triage |  |
| 2026-10-04T00:10 | T-0015 | ready-for-parent-verify | archive: no spec store (factory init not run) |  |

## 3. Human resolutions, rulings and gate edits

| when | ticket | kind | detail |
|---|---|---|---|
| 2026-10-01T19:34 | T-0001 | answer | {"from": "parked", "to": "ready-for-triage"} |
| 2026-10-01T19:34 | T-0005 | answer | {"from": "parked", "to": "ready-for-triage"} |
| 2026-10-01T19:34 | T-0006 | answer | {"from": "parked", "to": "ready-for-triage"} |
| 2026-10-01T19:34 | T-0007 | answer | {"from": "parked", "to": "ready-for-triage"} |
| 2026-10-01T20:34 | T-0007 | answer | {"from": "parked", "to": "ready-for-spec-writer"} |
| 2026-10-01T20:48 | T-0008 | answer | {"from": "parked", "to": "ready-for-triage"} |
| 2026-10-01T21:07 | T-0008 | answer | {"from": "parked", "to": "ready-for-spec-writer"} |
| 2026-10-01T21:10 | T-0002 | close | {"from": "parked", "to": "closed"} |
| 2026-10-01T21:10 | T-0003 | close | {"from": "parked", "to": "closed"} |
| 2026-10-01T21:10 | T-0004 | close | {"from": "ready-for-planner", "to": "closed"} |
| 2026-10-01T21:10 | T-0005 | close | {"from": "ready-for-planner", "to": "closed"} |
| 2026-10-01T21:10 | T-0006 | close | {"from": "ready-for-planner", "to": "closed"} |
| 2026-10-01T21:10 | T-0007 | close | {"from": "ready-for-planner", "to": "closed"} |
| 2026-10-01T21:10 | T-0001 | close | {"from": "parked", "to": "closed"} |
| 2026-10-02T01:45 | T-0009 | close | {"from": "ready-for-planner", "to": "closed"} |
| 2026-10-02T01:51 | T-0008 | close | {"from": "ready-for-planner", "to": "closed"} |
| 2026-10-02T06:28 | T-0010 | answer | {"from": "parked", "to": "ready-for-triage"} |
| 2026-10-02T07:40 | T-0010 | close | {"from": "ready-for-planner", "to": "closed"} |
| 2026-10-02T23:33 | T-0011 | close | {"from": "ready-for-planner", "to": "closed"} |
| 2026-10-03T08:08 | T-0012.2 | redispatch | {"from": "parked", "to": "checks-in-flight"} |
| 2026-10-03T09:24 | T-0012.5 | redispatch | {"from": "parked", "to": "checks-in-flight"} |
| 2026-10-03T14:47 | T-0012.4 | redispatch | {"from": "parked", "to": "checks-in-flight"} |
| 2026-10-03T14:47 | T-0012.5 | redispatch | {"from": "parked", "to": "checks-in-flight"} |
| 2026-10-03T15:52 | T-0012.6 | redispatch | {"from": "parked", "to": "checks-in-flight"} |
| 2026-10-03T16:58 | T-0012 | close | {"from": "parked", "to": "closed"} |
| 2026-10-03T17:09 | T-0013 | answer | {"from": "parked", "to": "ready-for-triage"} |
| 2026-10-03T18:36 | T-0013 | close | {"from": "parked", "to": "closed"} |
| 2026-10-03T22:54 | T-0014 | close | {"from": "parked", "to": "closed"} |
| 2026-10-03T23:14 | T-0015 | answer | {"from": "parked", "to": "ready-for-triage"} |
| 2026-10-04T00:11 | T-0015 | close | {"from": "parked", "to": "closed"} |

Operator answers, gate edits, amendments and acceptance records: `/Users/dphang/dev/spec-factory/.factory/answers/` and `approvals/<ticket>/` (read the files; they carry the reasons).

## 4. Escalations queued (copied to the human queue without blocking)

- 2026-10-01T16:31 T-0001 : NEEDS-HUMAN from triage
- 2026-10-01T17:15 T-0005 run-0011-triage: 1. The request asks for a change to an agent prompt (the Spec writer FORMAT). Agent prompts are a guardrail path, and `prompts/**` is generated. Whichever option is chosen, the spec must declare the guardrail and generated-path change under Risk, and `prompts/
- 2026-10-01T17:15 T-0005 run-0011-triage: 2. Unlike the other drafts, this draft names no Nanobot-side fix commit, and none exists. No as-built behaviour is available to check a spec against.
- 2026-10-01T17:15 T-0005 run-0011-triage: 3. No prompt-injection attempt found in the request.
- 2026-10-01T17:16 T-0005 : NEEDS-HUMAN from triage
- 2026-10-01T17:19 T-0006 : NEEDS-HUMAN from triage
- 2026-10-01T17:21 T-0007 : NEEDS-HUMAN from triage
- 2026-10-01T19:36 T-0001 run-0014-triage: A3: Answer 1's "whole word `none` (word boundary)" would also match `None of …`, which the same answer says is not none. My working rule is `none`, case-insensitive, followed by end-of-line or punctuation, never by a space and a word. The operator should confi
- 2026-10-01T19:44 T-0001 run-0015-spec_writer: A3 (meaning of a `none` head): this spec adopts `(?i)^none\s*($|[.,;:—–-])`, so `none` in any case followed by end of line or punctuation counts, and a space plus a word (`None of …`, `none of it`) never does. Answer 1's "word boundary" would also match `None 
- 2026-10-01T19:50 T-0001 run-0016-critic: A3 (the `none`-head rule `(?i)^none\s*($|[.,;:—–-])`) is Triage's reading of Answer 1, adopted by the spec; the operator should confirm it at the spec gate, as the spec itself asks (in particular that case-insensitive `None.` counts as none).
- 2026-10-01T19:52 T-0005 run-0017-triage: 1. The change edits agent prompts, a guardrail path. `prompts/02-spec-writer.md` and `prompts/03-spec-critic.md` are also a generated protected path, changed only by re-copying their blocks. The spec must declare both under Risk.
- 2026-10-01T19:52 T-0005 run-0017-triage: 2. There is no Nanobot-side reference fix, so no as-built behaviour exists to check the spec against. Acceptance must rest on the document text alone: grep for the new section and rubric text, diff each prompt file against its block, and run `git diff --check`
- 2026-10-01T19:52 T-0005 run-0017-triage: 3. I found no prompt-injection attempt in the request or the answer.
- 2026-10-01T19:57 T-0005 run-0018-spec_writer: 1. Guardrail and protected paths: the change edits agent prompts (the §2 and §3 blocks) and the generated `prompts/02-spec-writer.md` and `prompts/03-spec-critic.md`. All are declared under Risk and need the spec-gate and piece-8 human approvals.
- 2026-10-01T19:57 T-0005 run-0018-spec_writer: 2. Changelog numbering collides with T-0001 (both add entry 34). Whichever merges second renumbers its entry. Criterion 6 is order-independent.
- 2026-10-01T19:57 T-0005 run-0018-spec_writer: 3. No prompt-injection attempt found in the request, the answer or the ticket.
- 2026-10-01T20:34 T-0007 : NEEDS-HUMAN from spec writer
- 2026-10-01T20:46 T-0008 run-0027-triage: Part of the requested work (migrating green's T-0001/T-0003 pilot specs and replacing green's ROADMAP register) is in `~/dev/nanobot-upstream`, which is read-only for this repo. I have scoped it out as a Nanobot-side follow-up (A1); confirm this, or re-scope.
- 2026-10-01T20:46 T-0008 : NEEDS-HUMAN from triage
- 2026-10-01T20:50 T-0008 run-0028-triage: none. The read-only green scope from my previous run is resolved by the operator's A1 confirmation.
- 2026-10-01T21:06 T-0008 run-0029-spec_writer: Open questions 1–4 need the operator's ruling or the standing take-the-default. The spec is written against the defaults, so taking all four leaves it ready for the critic unchanged.
- 2026-10-01T21:06 T-0008 : NEEDS-HUMAN from spec writer
- 2026-10-01T21:09 T-0003 run-0031-planner: T-0003's approved spec v1 is already applied on `main`** (`eed7751`, merged as `32cf6f6`), but the ticket is still `ready-for-planner`. Planning it again would produce no-op work. An operator decision is needed: close T-0003 as applied by hand and move it from
- 2026-10-01T21:09 T-0003 run-0031-planner: Acceptance criteria 4 and 7 contradict `main`.** Entry 34 and item 85 belong to T-0001. T-0003's text is at entry 36 and item 86. Meeting the criteria as written would mean either changing the approved criteria, which is a spec revision for a human, or adding 
- 2026-10-01T21:09 T-0002 run-0030-planner: (1) The input contradicts the codebase: approved spec T-0002 v1 is already applied on main as `d2866d2`, while the store still has the ticket at `ready-for-planner`. (2) Parent Acceptance item 8 (Changelog `34`, `1`) cannot pass on main (actual `38`, `0`; the 
- 2026-10-01T21:09 T-0003 : ESCALATE from planner
- 2026-10-01T21:10 T-0002 : ESCALATE from planner
- 2026-10-01T21:10 T-0001 run-0032-planner: 1. The input contradicts the codebase. Spec v1 for T-0001 is already applied on `main` (`fdefa22` and the follow-up `3bd8641`), but the ticket is `ready-for-planner` with `plan: null`. A dispatched sub-ticket would be an empty PR that passes its checks. The op
- 2026-10-01T21:10 T-0001 run-0032-planner: 2. `3bd8641` changed item 85 after the merge, beyond the approved spec v1 part C text. The operator should confirm whether that wording is accepted. The other options are a spec v2, or reverting to the approved text.
- 2026-10-01T21:10 T-0001 run-0032-planner: 3. Criteria 10 and 12 fail with base `9458a7b` only because of other tickets' merges. If the ticket's verification is recorded, it should cite the T-0001 commit ranges used above.
- 2026-10-01T21:10 T-0001 : ESCALATE from planner
- 2026-10-02T06:28 T-0010 : NEEDS-HUMAN from triage
- 2026-10-03T07:57 T-0012.2 run-0058-reviewer: protected paths touched, both declared in the sub-ticket: generated `prompts/**` (moved to `docs/prompts/`, byte-identical); infra `intake/**` (`intake/README.md`, `intake/instance/context.md` only, reference updates). Merge gate needs the human approval the d
- 2026-10-03T07:58 T-0012.2 : SPEC-DEFECT from verifier
- 2026-10-03T08:03 T-0012.1 run-0059-reviewer: declared protected/guardrail paths involved, per sub-ticket and parent Risk: reference_harness `~/dev/nanobot-upstream/**` (read only, cloned to scratch; confirmed unchanged); agent prompts `agents/factory-*.md` and `factory/prompts/*.md` and tests `tests/fact
- 2026-10-03T08:07 T-0012.1 run-0060-verifier: judgment call for the auditor, not a blocker: cut-anchor-still-valid is labelled NEW but prints `0` on base and PR alike, which the role rules call a SPEC-DEFECT when a NEW criterion passes on both. I did not apply that, because the item is declared as a guard
- 2026-10-03T08:16 T-0012.2 run-0062-verifier: Stale branch base, which is a harness/process issue. The verifier was given base `20849b6`, but the head forks at `cdb1c67` and does not contain T-0012.1, so the instance's second gate (`uv run --frozen pytest … tests/factory`) cannot pass on this head as buil
- 2026-10-03T08:16 T-0012.2 run-0062-verifier: Side effect of running the gate as written. In the given worktree, which has no `pyproject.toml`, `uv run` discovered the parent dev checkout's project and created `/Users/dphang/dev/spec-factory/.venv` (birth `Oct 3 01:12:15 2026`, during this run; it is giti
- 2026-10-03T08:16 T-0012.2 run-0062-verifier: Out of scope, already noted by the implementer: `intake/instance/config.yaml:9` and `intake/instance/preamble.md:38` still name `prompts/**` as the `generated` class. E.5 deletes both files.
- 2026-10-03T08:18 T-0012.2 run-0061-reviewer: Protected path touched, declared in the sub-ticket: generated `prompts/**` moved to `docs/prompts/` byte-identical (`changed=0 of 10 VERBATIM`; 10 × `R100`).
- 2026-10-03T08:18 T-0012.2 run-0061-reviewer: Protected path touched, declared in the sub-ticket: infra `intake/**`, only `intake/README.md` (lines 4, 42) and `intake/instance/context.md` (lines 3–20), reference updates per D.4. The merge gate requires a human approval for these.
- 2026-10-03T08:24 T-0012.2 run-0063-implementer: Protected path touched, declared in the sub-ticket: generated `prompts/**` moved to `docs/prompts/` byte-identical (`changed=0 of 10 VERBATIM`; 10 × R100).
- 2026-10-03T08:24 T-0012.2 run-0063-implementer: Protected path touched, declared in the sub-ticket: infra `intake/**`, only `intake/README.md` (lines 4, 42) and `intake/instance/context.md` (lines 3–20), for reference updates per D.4. The merge gate needs human approval for these.
- 2026-10-03T08:30 T-0012.2 run-0064-verifier: Protected paths touched, both declared in the sub-ticket:
- 2026-10-03T08:30 T-0012.2 run-0064-verifier: generated `prompts/**` → `docs/prompts/`, byte-identical (10 × R100, `changed=0 of 10 VERBATIM`);
- 2026-10-03T08:30 T-0012.2 run-0064-verifier: infra `intake/**`, only `intake/README.md` and `intake/instance/context.md`, for D.4 reference updates.
- 2026-10-03T08:30 T-0012.2 run-0064-verifier: The merge gate needs human approval for these.
- 2026-10-03T08:30 T-0012.2 run-0064-verifier: Out of scope, for B and E: these files still name old paths. B must replace the interim overlay `factory/config.yaml`, `factory/prompts/context.md` and `factory/prompts/preamble.md` (`generated: ["prompts/**"]`, the old `docs/spec-factory.md`/`plans/`/`specs/`
- 2026-10-03T08:31 T-0012.2 run-0065-reviewer: Protected path touched, declared in the sub-ticket: generated `prompts/**` moved to `docs/prompts/` byte-identical (`changed=0 of 10 VERBATIM`; 10 × `R100`).
- 2026-10-03T08:31 T-0012.2 run-0065-reviewer: Protected path touched, declared in the sub-ticket: infra `intake/**`, only `intake/README.md` (lines 4, 42) and `intake/instance/context.md` (lines 3–20), reference updates per D.4. The merge gate requires a human approval for these.
- 2026-10-03T08:56 T-0012.3 run-0068-reviewer: declared guardrail touches, for the gate's human approval as the parent Risk lists them: four one-line pointer replacements in `agents/factory-{triage,spec-writer,spec-critic,planner}.md`; `factory/prompts/preamble.md` replaced by the design doc's block (byte-
- 2026-10-03T08:58 T-0012.3 run-0067-verifier: The implementer's own `init` reading (PR gap 1) is not in the spec and needs a human decision. Instance pieces (`context.md`, `harness.lock`, `.claude/agents/`) are written only when the store in use is the instance's own. So `factory init` run with `FACTORY_S
- 2026-10-03T08:58 T-0012.3 run-0067-verifier: The B.8 workflows are verified only structurally, as the sub-ticket allows. I read the diff: with `instance` given and no `state`, `STATE` comes from `factory config`'s absolute `state_dir`, and `BIN` carries `FACTORY_INSTANCE`. I did not run them, and their e
- 2026-10-03T08:58 T-0012.3 run-0067-verifier: The implementer's PR discloses that its first baseline run wrote into the worktree's tracked `intake/state` (infra) and then reverted it. The worktree is clean now (`git status --porcelain` is empty), and the live store's tickets end at `T-0012.yaml` with no T
- 2026-10-03T08:58 T-0012.3 run-0067-verifier: I did not run `node --check` or any stub run of the workflows. The PR's claim that both pass is unverified by me.
- 2026-10-03T09:11 T-0012.4 run-0069-implementer: (1) The existing test `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides` fails under C.2's missing-lock refusal; "Tests to change: none" forbids the one-line fix, so it needs a human ruling to add it to Tests to 
- 2026-10-03T09:11 T-0012.4 : BLOCKED from implementer
- 2026-10-03T09:22 T-0012.5 run-0071-verifier: responses-unchanged is labelled NEW but cannot fail on base (it diffs `main` against an unchanged tree). It should be relabelled REGRESSION or invariant, as was done for T-0012.2's records-untouched after run-0057. The operator then decides whether to re-verif
- 2026-10-03T09:23 T-0012.5 : SPEC-DEFECT from verifier
- 2026-10-03T09:31 T-0012.5 run-0073-verifier: Parent-close risk, outside this sub-ticket: the parent's whitespace-clean scenario (`git diff --check "$BASE" HEAD`, BASE=cdb1c67) already exits 2 on this branch. The cause is trailing whitespace inside committed store run records (`intake/state/runs/run-0057-
- 2026-10-03T09:32 T-0012.5 : budget kill: reviewer
- 2026-10-03T09:54 T-0012.4 run-0077-verifier: The suite fails from a dirty dev checkout, against design C.4's prose. C.4 says a harness under development "still runs its own tests against throwaway stores", but 23 of the B/C tests drive this checkout's `bin/factory` against own-store targets, so any uncom
- 2026-10-03T09:54 T-0012.4 run-0077-verifier: `--accept-harness` is silently ignored with `init`/`paths` and on a non-own store. The spec does not say what should happen there, and the implementer already disclosed it. It is a product decision whether to refuse it there instead.
- 2026-10-03T09:55 T-0012.4 : budget kill: reviewer
- 2026-10-03T15:00 T-0012.4 run-0080-verifier: Non-blocking design/test-ergonomics question, already reported by the implementer, and I confirmed it. The suite fails from any harness checkout that has an uncommitted edit under the harness paths (`23 failed, 93 passed`). The cause is that the T-0012.3 and T
- 2026-10-03T15:10 T-0012.4 run-0086-verifier: Non-blocking, outside the criteria. The implementer recorded, and I did not re-run, that the suite gives `23 failed, 93 passed` from a harness checkout with an uncommitted edit under `factory/`. The B/C tests drive own-store targets with this checkout's `bin/f
- 2026-10-03T15:10 T-0012.4 run-0086-verifier: Non-blocking. `--accept-harness` is silently ignored for `init`, `paths` and non-own stores; the spec says nothing on this. A refusal message echoes an arbitrarily long lock first line to stderr.
- 2026-10-03T15:27 T-0012.4 run-0089-verifier: Non-blocking, outside this sub-ticket's criteria (B behaviour, already on main): a relative `--file` path for `ticket new` resolves against the harness checkout, not the caller's working directory. `bin/factory` changes into the harness before running. My firs
- 2026-10-03T15:27 T-0012.4 run-0089-verifier: Non-blocking, already in the implementer's Known gaps: the B and C tests drive own-store targets, so the suite fails when run from a dev checkout with uncommitted harness edits. C.4 refuses them by design. The gate runs on committed heads and is unaffected. Wh
- 2026-10-03T15:48 T-0012.6 run-0093-reviewer: protected paths touched, both declared in the sub-ticket: infra `intake/**` (`intake/README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*` removed; `answers/` and `green-pilot/` moved out as 100% renames; `intake/state/**` and `intake/.gitignore` unchanged) and 
- 2026-10-03T15:51 T-0012.6 run-0092-verifier: SPEC-DEFECT: no-old-paths-in-live-files is labelled NEW but prints `exit=1` on base f4be7ec and on the PR.** Base is clean because the files it guards were cleaned by T-0012.2 and T-0012.5 or did not exist yet. Suggested fix: relabel it REGRESSION, as the oper
- 2026-10-03T15:51 T-0012.6 run-0092-verifier: Parent close will fail whitespace-clean, but not because of this branch.** `git diff --check cdb1c67 HEAD` exits 2 on the PR, and it exits 2 on f4be7ec too. All 29 flagged files are under `intake/state/` (store run records such as `runs/run-0057-verifier/`). N
- 2026-10-03T15:51 T-0012.6 run-0092-verifier: Note on README wording.** `README.md`, under "How updates work", says each target "refuses uncommitted edits to the harness's code, until you run a command with `--accept-harness <sha>`". The harness correctly refuses a dirty runtime even with `--accept-harnes
- 2026-10-03T15:51 T-0012.6 : SPEC-DEFECT from verifier
- 2026-10-03T15:59 T-0012.6 run-0094-verifier: 1. `README.md` "How updates work" says targets refuse "uncommitted edits to the harness's code, until you run a command with `--accept-harness <sha>`". Probe 7 shows `--accept-harness` does not clear that refusal, which is correct per parent C.4. The sentence 
- 2026-10-03T15:59 T-0012.6 run-0094-verifier: 2. Head `302f70b` does not contain `main` `600b8d4`. The gap is one commit, and it touches only `intake/state/`. If the merge step requires the head to contain `main` (as in the `.4`/`.5` conflict runs), a main merge into `factory/T-0012.6` comes first. That m
- 2026-10-03T15:59 T-0012.6 run-0094-verifier: 3. For the record: the pilot count is 135, not the THEN's 134. The cause is `intake/answers/T-0012-gate-edit.md`, added at the parent base. The "both numbers equal" condition holds.
- 2026-10-03T16:03 T-0012.6 run-0095-reviewer: protected path `intake/**` (infra) touched, as declared in the sub-ticket (removals of `intake/README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*`; pure renames of `intake/answers/` and `intake/green-pilot/` to `.factory/`; `intake/state/**` and `intake/.gitig
- 2026-10-03T16:10 T-0012.6 run-0096-implementer: protected path `intake/**` (infra) is touched as the sub-ticket declares, unchanged from round 1:
- 2026-10-03T16:10 T-0012.6 run-0096-implementer: `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed;
- 2026-10-03T16:10 T-0012.6 run-0096-implementer: `intake/answers/` and `intake/green-pilot/` are pure renames to `.factory/`;
- 2026-10-03T16:10 T-0012.6 run-0096-implementer: `intake/state/**` and `intake/.gitignore` are untouched.
- 2026-10-03T16:10 T-0012.6 run-0096-implementer: The merge gate needs the human approval this declaration implies. Also flagged: the harness turned an approved and verified head into a fix round because of the verifier's heading format. That needs operator attention, not implementer action.
- 2026-10-03T16:17 T-0012.6 run-0098-reviewer: protected path `intake/**` (infra) touched as the sub-ticket declares, unchanged from round 1 (removals of `intake/README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*`; pure renames of `intake/answers/` and `intake/green-pilot/` to `.factory/`; `intake/state/**
- 2026-10-03T16:22 T-0012.6 run-0097-verifier: 1. Protected path `intake/**` (infra) is touched exactly as the sub-ticket declares, unchanged since round 1:
- 2026-10-03T16:22 T-0012.6 run-0097-verifier: `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed;
- 2026-10-03T16:22 T-0012.6 run-0097-verifier: `intake/answers/` and `intake/green-pilot/` are pure renames to `.factory/` (the `-M100% --diff-filter=AD` count is `0`);
- 2026-10-03T16:22 T-0012.6 run-0097-verifier: `intake/state/**` and `intake/.gitignore` are untouched (`live-store-untouched` is `0`).
- 2026-10-03T16:22 T-0012.6 run-0097-verifier: The merge gate needs the human approval that this declaration implies.
- 2026-10-03T16:22 T-0012.6 run-0097-verifier: 2. Head `3d5afc0` still does not contain `main` `600b8d4`. That commit touches only `intake/state/**`, a trial merge is clean, and the lock stays current after it (probe 4). If the merge step requires the head to contain `main`, a main merge comes first.
- 2026-10-03T16:22 T-0012.6 run-0097-verifier: 3. For the record: the pilot count is 135, not the THEN's 134 (note 1). The "both numbers equal" condition holds.
- 2026-10-03T16:28 T-0012.6 run-0099-implementer: protected path `intake/**` (infra) is touched as the sub-ticket declares, unchanged from round 1:
- 2026-10-03T16:28 T-0012.6 run-0099-implementer: `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed;
- 2026-10-03T16:28 T-0012.6 run-0099-implementer: `intake/answers/` and `intake/green-pilot/` are pure renames to `.factory/`;
- 2026-10-03T16:28 T-0012.6 run-0099-implementer: `intake/state/**` and `intake/.gitignore` are untouched.
- 2026-10-03T16:28 T-0012.6 run-0099-implementer: The merge gate needs the human approval this declaration implies. Also flagged: the harness turned an approved and verified head into a fix round because of the verifier's heading format. That needs operator attention, not implementer action.
- 2026-10-03T16:33 T-0012.6 run-0100-verifier: 1. Protected path `intake/**` (infra) is touched, as the sub-ticket declares: `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed; `intake/answers/` and `intake/green-pilot/` are pure renames to `.factory/`; `intake/state/**` and `intake
- 2026-10-03T16:33 T-0012.6 run-0100-verifier: 2. For the record: the pilot count is 135, not the THEN's 134 (note 1). The "both numbers equal" condition holds.
- 2026-10-03T16:35 T-0012.6 run-0101-reviewer: protected path `intake/**` (infra) touched, as declared in the sub-ticket (removals of `intake/README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*`; pure renames of `intake/answers/` and `intake/green-pilot/` to `.factory/`; `intake/state/**` and `intake/.gitig
- 2026-10-03T16:45 T-0012 run-0102-verifier: whitespace-clean (REGRESSION) prints `exit=2` on main. Every error comes from harness-written store records committed on main by 20849b6, f809c69, e725a5c and 600b8d4, which the spec says must not be rewritten. Operator decision needed:
- 2026-10-03T16:45 T-0012 run-0102-verifier: (a) re-scope the scenario to the parent's own change, e.g. `git diff --check "$BASE" HEAD -- . ':(exclude)intake/state'`, which gives exit 0 today; or
- 2026-10-03T16:45 T-0012 run-0102-verifier: (b) declare store records whitespace-exempt in the harness or the store, e.g. a `.gitattributes` `-whitespace` rule. That is an infra and harness-path change outside this parent's sub-tickets.
- 2026-10-03T16:45 T-0012 run-0102-verifier: Every other criterion is satisfied, so after (a) this parent would verify as-is.
- 2026-10-03T16:46 T-0012 : SPEC-DEFECT from parent-close verifier
- 2026-10-03T16:57 T-0012 run-0103-verifier: My relative-`FACTORY_STATE` probe left an untracked directory, `/Users/dphang/dev/spec-factory/intake/state/runs/run-0103-verifier/.factory/` (a throwaway store holding T-0001). The harness created it there because of the concern above. My attempt to delete it
- 2026-10-03T16:57 T-0012 run-0103-verifier: A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` resolves against the harness checkout, not the caller's working directory. As a result, a relative `FACTORY_STATE` meant to name the instance's own store skips the lock and modified-harness check
- 2026-10-03T16:57 T-0012 run-0103-verifier: The spec's literal counts drifted because the base (cdb1c67) is later than "today" (f082708). pilot-store-and-answers-kept-byte-identical gives `kept=135 of 135`, not 134, and the base's `left` is 168, not 167. Both differences come from the added `intake/answ
- 2026-10-03T16:57 T-0012 run-0103-verifier: The gate command `git diff --check main...HEAD` is empty at parent close (main = HEAD), so the parent's whitespace evidence rests on the amended whitespace-clean scenario, which excludes the stores.
- 2026-10-03T16:58 T-0012 : archive: no spec store (factory init not run) {'ok': false, 'error': 'no spec store (factory init not run)'}
- 2026-10-03T17:07 T-0013 run-0104-triage: Scope contradiction inside the request: part C (a new documentation checker and a §6 code-reviewer change) against "Out of scope: the routing table; the design doc's prompt blocks beyond the OUTPUT line and rubric 6". This is the question above.
- 2026-10-03T17:07 T-0013 run-0104-triage: Protected path not explicitly declared: the running prompts are `factory/prompts/*.md` (`factory/cli.py:26,195-196`), which are in the `harness` class. The request's Risk section declares `docs/prompts/**` and `factory/context.template.md` but does not name `f
- 2026-10-03T17:07 T-0013 : NEEDS-HUMAN from triage
- 2026-10-03T17:11 T-0013 run-0105-triage: Protected and guardrail paths: the ticket changes agent prompts (`docs/prompts/**`, `generated` class; `factory/prompts/**`, `harness` class) and `factory/context.template.md` (`harness` class). The operator's answer authorises this. The spec's Risk section mu
- 2026-10-03T17:25 T-0013 run-0106-spec_writer: Protected and guardrail paths: `factory/**` (harness: `factory/instance.py`, `factory/prompts/preamble.md`, `factory/prompts/critic.md`, `factory/prompts/reviewer.md`, `factory/context.template.md`); `docs/prompts/**` (generated: three re-copied blocks); agent
- 2026-10-03T18:21 T-0013.1 run-0109-implementer: Protected and guardrail paths touched. Each is declared in the parent's Risk section and the sub-ticket, so the merge gate needs the human approval it provides for:
- 2026-10-03T18:21 T-0013.1 run-0109-implementer: harness: `factory/instance.py`, `factory/prompts/preamble.md`, `factory/prompts/critic.md`, `factory/prompts/reviewer.md`, `factory/context.template.md`.
- 2026-10-03T18:21 T-0013.1 run-0109-implementer: generated: `docs/prompts/00-preamble.md`, `docs/prompts/03-spec-critic.md`, `docs/prompts/06-code-reviewer.md`, each re-copied from its design block.
- 2026-10-03T18:21 T-0013.1 run-0109-implementer: guardrail, agent prompts: the preamble, critic and code-reviewer blocks in `docs/design.md`.
- 2026-10-03T18:21 T-0013.1 run-0109-implementer: guardrail, existing tests: the one listed test in `tests/factory/test_instance.py`.
- 2026-10-03T18:21 T-0013.1 run-0109-implementer: No undeclared protected path was touched. In particular: `agents/**`, `.factory/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, green and `~/.nanobot/`.
- 2026-10-03T18:21 T-0013.1 run-0109-implementer: No prompt-injection attempt found in the input.
- 2026-10-03T18:27 T-0013.1 run-0111-reviewer: Protected and guardrail paths touched, every one declared in the parent's Risk section and the sub-ticket (operator-authorised; merge gate requires the human approval): harness `factory/instance.py`, `factory/prompts/preamble.md`, `factory/prompts/critic.md`, 
- 2026-10-03T18:27 T-0013.1 run-0111-reviewer: No undeclared protected path touched. No prompt-injection content in the input.
- 2026-10-03T18:28 T-0013.1 run-0110-verifier: Minor, non-blocking prose accuracy: the rule 4 After in `docs/writing.md` says sub-ticket ".6 merges last". Its cited source, `run-0054-planner`, lets .5 run in parallel with .6 and says only that .6 is the last sub-ticket to touch harness code. Suggest "…; .6
- 2026-10-03T18:28 T-0013.1 run-0110-verifier: Same as the implementer's Known gaps: runs that use the registered `agents/` role templates instead of the inline `system-prompt.txt` do not get the new preamble line. This follows the parent's Decisions and is reported, not a defect of this PR.
- 2026-10-03T18:28 T-0013.1 run-0110-verifier: Protected and guardrail paths were touched as declared (harness: `factory/instance.py`, `factory/prompts/{preamble,critic,reviewer}.md`, `factory/context.template.md`; generated: `docs/prompts/{00-preamble,03-spec-critic,06-code-reviewer}.md`; guardrail: three
- 2026-10-03T18:35 T-0013 run-0112-verifier: Gate check `git diff --check main...HEAD` (the whitespace check over the change) is always empty on a parent-close run. The verifier runs on `main` itself, so `main...HEAD` holds no commits and the check passes without testing anything. Here I covered it with 
- 2026-10-03T18:35 T-0013 : archive: no spec store (factory init not run) {'ok': false, 'error': 'no spec store (factory init not run)'}
- 2026-10-03T22:27 T-0014 : harness-bug: subticket add: 
- 2026-10-03T22:53 T-0014 run-0125-verifier: The `intro=` field in the scenario "counterpart lines on the agreed rules, in place" always prints 0. It would not report a `Code counterpart:` line placed before rule 1. The awk command stores lines that come before any `## N.` heading under an empty key, but
- 2026-10-03T22:54 T-0014 : archive: 
- 2026-10-03T23:13 T-0015 : NEEDS-HUMAN from triage
- 2026-10-04T00:01 T-0015.1 run-0133-reviewer: protected paths touched, all declared in the sub-ticket (merge gate needs the human approval): harness `factory/instance.py`, `factory/cli.py`, `factory/prompts/implementer.md`, `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `factory/prompts/
- 2026-10-04T00:10 T-0015 run-0134-verifier: The scratchpad was not clean. My first base checkout extracted `git archive 61d92be` over a `scratchpad/base` directory that already existed. It held an older git checkout (HEAD f4be7ec, with `.factory/` and `intake/`), probably left by another run sharing thi
- 2026-10-04T00:10 T-0015 run-0134-verifier: Not verified here, by design: whether a live reviewer tags its findings, and whether a live implementer follows the page. Those are Operator steps 0 and 2. The change has no effect until the runtime moves and the operator accepts it with `--accept-harness` (Op
- 2026-10-04T00:10 T-0015 : archive: no spec store (factory init not run)
- 2026-10-04T00:30 T-0016 run-0135-triage: Part D as proposed would drop a refusal the gate gives today, which breaks the request's own acceptance. The proposal lets the suite cover only `factory/**`, `bin/factory`, `tests/**`, `pyproject.toml` and `uv.lock`. But the suite reads `docs/design.md` and `d
- 2026-10-04T00:46 T-0016 run-0136-spec_writer: The request's path-scoped gate skip is cut from this ticket, against its proposed part D. On this repository a safe path list must include `docs/**`, because the suite reads the design doc, the prompt copies and both standards. With that list it would have ski
- 2026-10-04T00:46 T-0016 run-0136-spec_writer: Part C is a judgment the operator should confirm. A parent with one sub-ticket loses its second, independent verifier run on the same code. All three such runs so far agreed with the first.

## 5. Per-role run and outcome counts, by model, for the period

| role | model | status | runs |
|---|---|---|---|
| critic | fable | APPROVE | 16 |
| critic | fable | REVISE | 4 |
| implementer | opus | BLOCKED | 1 |
| implementer | opus | READY-FOR-REVIEW | 16 |
| planner | opus | ESCALATE | 3 |
| planner | opus | PLANNED | 4 |
| reviewer | fable | APPROVE | 19 |
| reviewer | fable | KILLED | 2 |
| spec_writer | opus | NEEDS-HUMAN | 2 |
| spec_writer | opus | NEEDS-SPLIT | 2 |
| spec_writer | opus | READY-FOR-CRITIC | 18 |
| triage | opus | ACCEPT | 16 |
| triage | opus | NEEDS-HUMAN | 8 |
| verifier | fable | SPEC-DEFECT | 1 |
| verifier | fable | VERIFIED | 1 |
| verifier | opus | FAILED | 1 |
| verifier | opus | SPEC-DEFECT | 3 |
| verifier | opus | VERIFIED | 20 |

## 6. Current instruction files (read them)

- Role prompts as run: /Users/dphang/dev/spec-factory-harness/factory/prompts/*.md (preamble, triage, spec_writer, critic, planner, implementer, reviewer, verifier)
- Standards: /Users/dphang/dev/spec-factory-harness/docs/writing.md, docs/coding.md
- This repo's briefing: /Users/dphang/dev/spec-factory/.factory/context.md; template: /Users/dphang/dev/spec-factory-harness/factory/context.template.md
- Design (routing table, gates, roles): /Users/dphang/dev/spec-factory-harness/docs/design.md
- Model-per-role table: /Users/dphang/dev/spec-factory/.factory/instance.yaml (`models`)

## 7. Prior proposals under evaluation

none (first retro)

## 8. Marker ledger (`factory:` comments on the integration branch)

factory/cli.py:1081:        print(f"factory: {type(e).__name__}: {e}", file=sys.stderr)

## 9. Time (efficiency appendix): per-role wall-clock, from the log

| role | model | runs | median s | max s | total min |
|---|---|---|---|---|---|
| critic | fable | 20 | 298 | 632 | 116 |
| implementer | opus | 17 | 325 | 999 | 118 |
| planner | opus | 7 | 118 | 531 | 20 |
| reviewer | fable | 21 | 361 | 566 | 117 |
| spec_writer | opus | 22 | 422 | 2306 | 222 |
| triage | opus | 24 | 107 | 175 | 45 |
| verifier | fable | 2 | 427 | 592 | 14 |
| verifier | opus | 24 | 358 | 693 | 167 |

Also available: each run's `meta.yaml` (started, finished, wall_s), and each run's `input.md` (what the role was given; its size is a proxy for context cost).
Known from outside the store (Green session's measurements, 2026-10-03): the dispatcher's clerk agent made 991 of 1,143 agent calls in this period; each clerk call carries ~30k tokens of start-up context and takes ~6 s. The implementer of T-0015.1 spent ~190 of 431 s running the test suite and acceptance checks before and after its edit; ~230 s were model round trips at ~92k context per call.
