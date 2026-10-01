## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0025-spec_writer/output.md`

## Ticket (Triage output)

Type: feature

Title: Declare the per-repo role-context block in the design doc's Harness section as an input every role receives first (document only; where the target lives stays open)

Summary: The requester ran this repo's issue drafts through intake. They found that every role's input begins with a role-context block: per-repo facts such as the repository, how to run things, and what kind of request to expect. The design documents never mention this block. A wrong block quietly misleads every role, and nothing in the design says it exists, that it is per repo, or that it comes first. The operator chose option C on 2026-10-01: add the role-context block to the design doc's Harness section, declared as a per-repo input that every role receives first. Leave open where the target's identity lives (D8 unchanged). Multi-target support is a follow-up and out of scope. Under this repo's conventions, the design-doc change also adds a Changelog entry and keeps `specs/build-harness.md` consistent with the new text.

Evidence:
- Request: "The role context file (`context.md`) is not in the design doc at all; it carries per-repo facts (how to run things, what kind of request to expect) that every role reads first, so a wrong one silently misdirects every role." Fix on the Nanobot side: "none. The workaround is `intake/` in this repo."
- Operator answer (Answer 1, 2026-10-01): "option **C, document only for now.** Add the role-context block to the design doc's Harness section, declared as a per-repo input every role receives first. Leave where the target's identity lives open (D8 unchanged) until a second real target exists beyond this scratch run. Multi-target support (instance in the store, or a per-repo harness copy) is a follow-up, out of scope here."
- Re-checked in this repo (`~/dev/spec-factory`, `main` at `28b3a74`):
  - `grep -n -i "context.md\|role context\|role-context\|per-repo\|per repo"` over `docs/spec-factory.md`, `specs/build-harness.md`, `plans/*.md` and `README.md` matches only `docs/spec-factory.md:7` and `README.md:11` ("Fill in `{braces}` per repo") and `docs/spec-factory.md:23` ("**Protected paths** are per repo"). Neither the doc nor the spec names a role-context block.
  - `docs/spec-factory.md:31` is `## Harness: functional pieces`. Line 50 says the harness owns "composing each role's input from *only* its declared sources". Line 68 says the routing table's "Receives" column "adds to the INPUT the role prompt already declares". No row or rule declares a block that goes in front of every input.
  - `docs/spec-factory.md:605` is `## Changelog`. Its last numbered item is 33 (line 640).
  - `specs/build-harness.md:201` and `:294`: `run compose` writes `input.md` "from exactly the sources `factory/compose.py` declares" and records them as `input_sources:`. `specs/build-harness.md:393` (item 42) expects the critic's `input.md` to begin "with the text of `specs/T-0001/v1.md`" and its `input_sources` to be "exactly `[specs/T-0001/v1.md]`".
- Observed in the reference harness (read only; `~/dev/nanobot-upstream`, `feat/lionbot-v3`, now at `2cb06b783`. The intake pin `intake/HARNESS_PIN` is `053a7bd5e…`):
  - `factory/compose.py:12,35-36` puts `prompts/context.md` from the package directory first in every composed input, ahead of the `## Output file` line and the declared sources. Only the declared sources are appended to `sources`. The context file is not.
  - This run is a live example. `runs/run-0023-triage/meta.yaml` `input_sources` is `[requests/T-0007.md, runs/run-0013-triage/output.md]`, but `input.md` begins with `## Context for this run (composed by the harness, not part of the request)`. The block is delivered first and is not recorded as a source.
- Duplicate search: the store holds T-0001 to T-0008. Their titles and `issues/01`–`08` cover the status parser, clerk schema, triage re-ask input, the P0 agents dir, protected live state, P0-5 grep, this request (T-0007 = `issues/07_single_target_harness.md`) and the OpenSpec schema. None covers the role-context block or target identity, so there is no duplicate.

Assumptions:
- (inference) Scope is the design doc's Harness section plus whatever this repo's conventions force: a Changelog item, and `specs/build-harness.md` made consistent. D8 (`specs/build-harness.md:127`), `factory render`, `instance.yaml`, and any store or CLI change are out of scope by the operator's answer.
- (inference) "Every role receives first" conflicts with `specs/build-harness.md:393` (item 42) as written. Item 42 has the critic's `input.md` begin with the spec text and its `input_sources` be exactly the spec. The spec writer will have to reconcile that item, and possibly the "exactly the sources" wording at `:201`/`:294`, with the new doc text. The operator's answer does not say how.
- (inference, not stated by the requester) Declaring the block as an input means the declaration covers it. That raises a question the answer did not settle: should the block also be recorded in `input_sources` (the reference harness does not record it), or should the doc state why it is exempt from the line-50 "only its declared sources" rule? The spec writer should raise this as an Open question, not decide it silently.
- (inference) The Harness section is not a prompt block, so this change should require no `prompts/` re-copy. If the wording lands in the preamble or a role prompt instead, the matching `prompts/` file has to be re-copied.
- (inference) The block's content is per repo, for example the repository, how to run commands and tests, and what kind of request to expect, as the request describes. The doc should name what the block is for and that it is per repo, not fix its text.
- Priority (suggestion only, a human call): medium. A workaround exists (`intake/instance/context.md`), but the undocumented block shapes every role's input.

Reason: n/a (ACCEPT). The operator answered the design question (option C), and the remaining scope is clear.

STATUS: ACCEPT
CONFIDENCE: high. The scope comes straight from the operator's answer, and every citation above was re-read on this checkout and in the reference harness this run.
ESCALATIONS: none

## Request (raw)

---
title: Harness instance is single-target: running tickets against this repo needs a hand-built overlay
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` D8 (`{repo name}` and protected paths: `nanobot`, default) and `factory render` (fills `{repo name}`, protected paths and gate commands from one `config.yaml`); `README.md` ("Fill in `{braces}` per repo"). The P0 plan builds one instance, for Nanobot.

**What happened (2026-10-01):** issue drafts 01–06 are requests against this repo's documents, and the operator asked for them to go through intake. The only built harness (`~/dev/nanobot-upstream/factory/`, `feat/lionbot-v3`) hardcodes the target in three places: `factory/prompts/preamble.md` line 1 and its protected-path list, `factory/prompts/context.md` (repository, how to run tests, "the request is a legacy faux spec"), and `factory/config.yaml` (`repo_name`, `protected_paths`, `gate_commands`). `FACTORY_STATE` relocates the store but nothing relocates the target. Running the drafts needed `intake/` here: a pinned copy of the harness with those three files replaced by hand.

**Why it matters:** the design says the doc is filled in per repo, but the harness has one instance and no way to point a second store at a second target. The role context file (`context.md`) is not in the design doc at all; it carries per-repo facts (how to run things, what kind of request to expect) that every role reads first, so a wrong one silently misdirects every role.

**Proposed fix (design doc + spec):** make the target a property of the store, not the harness: the store's root carries `instance.yaml` (repo name, repo path, protected paths, gate commands) and `context.md`, `run start`/`run compose` read them from there, and `factory render` takes the instance as input. Name the role-context block in the design doc's Harness section as a per-repo input the composer prepends.

**Fix as implemented on the Nanobot side:** none. The workaround is `intake/` in this repo (scratch; `intake/README.md`).


## Answer 1

Operator decision (2026-10-01, Triage's question on where the target's identity lives): option **C, document only for now.**

Add the role-context block to the design doc's Harness section, declared as a per-repo input every role receives first. Leave where the target's identity lives open (D8 unchanged) until a second real target exists beyond this scratch run. Multi-target support (instance in the store, or a per-repo harness copy) is a follow-up, out of scope here.


## Answer 2

Answer to the Spec writer's Open question 1 (`input_sources` and the role-context block). Taken by default under the operator's standing take-the-recommendation rule; the operator can overturn it at the spec gate.

**(b) Exempt it, and say why.** The block is the same for every run against the repo and its text is already in each run's `input.md`, so the run stays auditable; `input_sources` keeps listing declared store paths only. Items 9, 42 and 77 and `plans/build-harness.md` stay as they are. Recording which version of the block a run saw (a hash field) is a follow-up, out of scope here.

Finish from your saved draft (spec v1): resolve the open question as (b), leave everything else unchanged, and go to READY-FOR-CRITIC.
