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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0026-critic/output.md`

## Spec under review (v2)

## Problem

Every role's input starts with a role-context block. The block carries per-repo facts: which repository the role works in, how to run commands and tests there, and what kind of request to expect. The design documents never mention it. `docs/spec-factory.md` does not say the block exists, that it is per repo, or that it comes first, and `specs/build-harness.md` says the opposite: it describes composed input as "exactly the declared sources" and expects the critic's input to begin with the spec text.

This matters to two groups. Anyone setting up the pipeline for a repo gets no prompt from the design to write or check this block. A wrong block misdirects every role at once, checkers included, and nothing in the design names it as a thing to get right. Whoever builds or audits a harness from `specs/build-harness.md` will find that its input-isolation item (42) contradicts how the reference harness behaves.

The operator decided on 2026-10-01 (option C, document only): declare the block in the design doc's Harness section as a per-repo input every role receives first. Where the target's identity lives stays open, D8 does not change, and multi-target support is a follow-up.

## Evidence

E1–E5 were captured in the spec v1 run (run-0024) on `main` `28b3a74` and re-checked in this run (run-0025). `main` is now `172a71e`; `git diff --stat 28b3a74 HEAD -- docs specs plans prompts README.md` prints nothing, so the documents are unchanged and every line number below still holds. The reference harness is `~/dev/nanobot-upstream` at `2cb06b783` on `feat/lionbot-v3`, read only.

E1. The documents never name the block:
```
$ cd ~/dev/spec-factory && grep -n -i "context.md\|role context\|role-context\|per-repo\|per repo" docs/spec-factory.md specs/build-harness.md plans/*.md README.md
docs/spec-factory.md:7:Eight role prompts share one preamble. ... Fill in `{braces}` per repo.
docs/spec-factory.md:23:Two path lists appear throughout. ... **Protected paths** are per repo: ...
README.md:11:Fill in `{braces}` per repo. ...
```
No line names a role-context block. The Harness section starts at `docs/spec-factory.md:31`. Line 50 says the harness owns "composing each role's input from *only* its declared sources". Line 68 says "\"Receives\" adds to the INPUT the role prompt already declares." No line declares anything that comes before both.

E2. `specs/build-harness.md` describes input as the declared sources only:
- `:201`: `factory run compose RUN` "writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares ... and records their paths as `input_sources:`".
- `:294` (I.2): "Input composed by `factory run compose RUN` (B) from exactly the declared sources (H)".
- `:393` (item 42): the critic's `input.md` "begins with the text of `specs/T-0001/v1.md`, its `meta.yaml` `input_sources` is exactly `[specs/T-0001/v1.md]`".

E3. The reference harness prepends the block and does not record it as a source. In `factory/compose.py` (the lines are the same at the intake pin `053a7bd5e`):
```
PROMPTS = Path(__file__).resolve().parent / "prompts"
...
    parts = [(PROMPTS / "context.md").read_text(encoding="utf-8").rstrip(),
             f"\n## Output file\n`{out_path}`\n"]
    sources: list[str] = []
    def add(rel: str, heading: str) -> None:
        ...
            sources.append(rel)
```
Only `add()` appends to `sources`, and the context file never passes through `add()`.

E4. The behaviour shows up in live runs of this intake instance, under `intake/state/runs/`:
```
run-0019-critic/input.md line 1:  ## Context for this run (composed by the harness, not part of the request)
                         line 30: ## Output file
                         line 33: ## Spec under review (v1)
run-0019-critic/meta.yaml input_sources: [specs/T-0005/v1.md]
run-0022-critic: same layout, input_sources: [specs/T-0006/v1.md]
run-0023-triage: input.md line 1 is the same heading; input_sources: [requests/T-0007.md, runs/run-0013-triage/output.md]
run-0024-spec_writer (spec v1): input.md line 1 is the same heading; input_sources: [runs/run-0023-triage/output.md, requests/T-0007.md]
run-0025-spec_writer (this run): the same heading and the same input_sources
```
So item 42 as written ("begins with the text of `specs/…`") does not describe the as-built critic input. The `input_sources` half ("exactly the spec") does.

E5. The Changelog ends at item 33 (`docs/spec-factory.md:641`), followed by a blank line and the `Declined:` line. The pending specs T-0001, T-0002, T-0003 and T-0005 each also append an item 34 (`intake/state/specs/T-000{1,2,3,5}/v1.md`).

## Root cause

The design gap is in `docs/spec-factory.md` §Harness: functional pieces. The ownership paragraph (line 50) and the routing-table preamble (line 68) define a role's input as its prompt's INPUT plus "Receives". The block that the as-built composer puts first (`factory/compose.py` `compose()`, E3) was added during the build and never written back into the design, so `specs/build-harness.md` (B `run compose`, I.2, item 42) still describes input without it.

## Proposed change

Two files change: `docs/spec-factory.md` and `specs/build-harness.md`. The diff adds 7 lines and removes 4. I applied it on a scratch clone of `main` `172a71e` in this run, and the outputs under Acceptance come from that clone. The new text sits outside every fenced prompt block, so no `prompts/` file is re-copied.

Part D follows option (b) for the `input_sources` question (v1's Open question 1), which Answer 2 took by default: the block is exempt from `input_sources`, and the build spec says why. The operator can overturn that at the spec gate; if so, part D and criteria 6 and 7 are rewritten.

**A. `docs/spec-factory.md`, §Harness: functional pieces.** Insert a new paragraph directly after the "**What the harness itself owns**" paragraph (line 50) and before "**Model per role, starting point.**", with a blank line on each side:

> **Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, and what kind of request to expect. Its text is the same for every role and every run against that repo. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. Where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here.

The paragraph does three things:
- It names the block's purpose and says it is per repo, without fixing its text, as the ticket assumed.
- It reconciles the block with line 50's "only its declared sources" rule by declaring it, so line 50 does not change.
- It leaves the block's location open, as the operator's answer requires.

**B. `docs/spec-factory.md`, §Routing table preamble (line 68).** Append one sentence after "\"Receives\" adds to the INPUT the role prompt already declares.":

> Both follow the role-context block (above).

No routing row changes.

**C. `docs/spec-factory.md`, §Changelog.** Append after item 33 and before the `Declined:` line. The intro sentence stays as it is.

> 34. After the intake run against this repo (2026-10-01): the role-context block is declared in the Harness section as a per-repo input every role receives first, ahead of its declared INPUT and the routing table's "Receives"; where the block is kept stays open.

If another pending spec takes 34 first, whichever merges second renumbers its entry. Criterion 3 accepts either order.

**D. `specs/build-harness.md`, made consistent with A (option (b)):**
1. Part B, the `factory run compose RUN` bullet (`:201`). After "(a run keeps that version even if the spec is re-pinned while it is in flight, K)." insert:
   > The file opens with the repo's role-context block (doc §Harness), ahead of those sources; the block is the same for every run against the repo, so it is not one of the `input_sources:` (its text is in `input.md`).
2. Part I, item 2 (`:294`). Replace "(B) from exactly the declared sources (H)," with "(B): the role-context block (doc §Harness), then exactly the declared sources (H),". The rest of the line is unchanged.
3. Item 42 (`:393`). Make two replacements and leave the rest of the item, including "`input_sources` is exactly `[specs/T-0001/v1.md]`" and `[NEW]`, unchanged:
   - Replace "begins with the text of `specs/T-0001/v1.md`," with "begins with the role-context block and contains, after it, the text of `specs/T-0001/v1.md`,".
   - Replace "`runs/<spec_writer run>/input.md` contains the request text with" with "`runs/<spec_writer run>/input.md` begins with the role-context block and contains the request text with".

D8 (`:127`), `factory render`, items 9 and 77, and every `input_sources` list stay as they are. No path is named for the block.

## Acceptance

Run every command from `~/dev/spec-factory` with bash on the PR branch, with `main` as the base. "Today" means `main` at `172a71e` (documents identical to `28b3a74`). Criteria 1–6 are NEW and 7–13 are REGRESSION.

1. `awk '/^## Harness: functional pieces/{f=1} /^## Human gates and convergence/{f=0} f' docs/spec-factory.md | tr -s ' \n' '  ' | grep -o -e "Every role's input opens with a role-context block" -e 'The block is per repo' -e 'a declared input of every role' -e 'the checkers receive the same block' -e 'Where the block is kept' | sort -u | wc -l | tr -d ' '` → `5`. The Harness section declares the block as first in every role's input, per repo, and a declared input. It also says checkers share the block, and it leaves the location open. [NEW: prints `0` today]
2. `grep '^\*\*Routing table\.\*\*' docs/spec-factory.md | grep -c 'Both follow the role-context block'` → `1`. The "Receives" column is stated to come after the block. [NEW: prints `0`, exit 1 today]
3. `awk '/^## Changelog/{f=1} /^## Appendix/{f=0} f' docs/spec-factory.md | grep '^[0-9][0-9]*\. ' | awk -F. '$1!=NR{gap=1} {last=$0} END{print (gap?"GAP":"CONTIGUOUS"), (last ~ /role-context block/ ? "LAST-IS-ROLE-CONTEXT" : "LAST-IS-OTHER")}'` → `CONTIGUOUS LAST-IS-ROLE-CONTEXT`. The newest Changelog entry records this change, and the numbering has no gap, whatever number the entry gets. [NEW: prints `CONTIGUOUS LAST-IS-OTHER` today]
4. `` grep -e '^- `factory run compose RUN`' -e '^2\. Input composed by `factory run compose RUN`' specs/build-harness.md | grep -c 'role-context block (doc §Harness)' `` → `2`. Both places in the build spec that define composed input include the block. [NEW: prints `0` today]
5. `` grep '^42\. Input isolation' specs/build-harness.md | grep -o -e 'critic run>/input.md` — the file `factory run compose` wrote — begins with the role-context block' -e 'spec_writer run>/input.md` begins with the role-context block' -e 'begins with the text of' | sort | tr '\n' '|' `` → `` critic run>/input.md` — the file `factory run compose` wrote — begins with the role-context block|spec_writer run>/input.md` begins with the role-context block| ``. Item 42 expects the block first in both runs and no longer says the critic's input begins with the spec text. [NEW: prints `begins with the text of|` today]
6. `` grep -c 'not one of the `input_sources:`' specs/build-harness.md `` → `1`. The build spec states that the block is not recorded as a source, and why. [NEW: prints `0`, exit 1 today]
7. `` diff <(git show main:specs/build-harness.md | grep -e '^| D8 ' -e '^9\. `factory run start' -e '^77\. ') <(grep -e '^| D8 ' -e '^9\. `factory run start' -e '^77\. ' specs/build-harness.md) `` → no output, exit 0. D8 (target name and protected paths) and the `input_sources` expectations of items 9 and 77 are unchanged. [REGRESSION]
8. `` diff <(git show main:docs/spec-factory.md | awk '/^[`][`][`]text$/{f=1} f{print} /^[`][`][`]$/{f=0}') <(awk '/^[`][`][`]text$/{f=1} f{print} /^[`][`][`]$/{f=0}' docs/spec-factory.md) `` → no output, exit 0. No prompt block changes, so `prompts/` needs no re-copy. [REGRESSION]
9. `diff <(git show main:docs/spec-factory.md | awk '/^\| # \| Piece \|/,/^\*\*What the harness itself owns\*\*/') <(awk '/^\| # \| Piece \|/,/^\*\*What the harness itself owns\*\*/' docs/spec-factory.md)` → no output, exit 0. The 12-piece table and the ownership paragraph (line 50) are unchanged. [REGRESSION]
10. `diff <(git show main:docs/spec-factory.md | awk '/^\| From \| STATUS \|/,/^Any STATUS not in this table/') <(awk '/^\| From \| STATUS \|/,/^Any STATUS not in this table/' docs/spec-factory.md)` → no output, exit 0. No routing row changes. [REGRESSION]
11. `grep -c -i 'context\.md' docs/spec-factory.md specs/build-harness.md` → `docs/spec-factory.md:0` and `specs/build-harness.md:0` (grep exits 1). Neither document names a location for the block, so where it lives stays open. [REGRESSION]
12. `git diff --name-only main...HEAD | grep -v -x -e docs/spec-factory.md -e specs/build-harness.md` → no output, exit 1. Nothing else is touched: not `prompts/`, `plans/`, `README.md` or `intake/**`. [REGRESSION]
13. `git diff --check main...HEAD` → no output, exit 0. [REGRESSION]

Results, re-run in this run. I extracted the 13 commands verbatim from the spec v1 file (unchanged in this version) and ran them with bash:
- On `main` (`172a71e`), criteria 1–13 gave `0`; `0`; `CONTIGUOUS LAST-IS-OTHER`; `0`; `begins with the text of|`; `0`; clean; clean; clean; clean; `0`/`0`; empty with exit 1; clean.
- On the scratch clone with A–D committed, they gave `5`; `1`; `CONTIGUOUS LAST-IS-ROLE-CONTEXT`; `2`; the two-match string above; `1`; clean; clean; clean; clean; `0`/`0`; empty with exit 1; clean.

## Tests to change

none. This repo holds documents and has no test files. Item 42 of `specs/build-harness.md` is an acceptance item in another spec, not a test file, and part D.3 amends it. It is declared under Risk for the gate.

## Out of scope

- **What must not change:**
  - D8 and anything else about where the target's identity lives.
  - `factory render`, any `instance.yaml`, and any store or CLI behaviour.
  - Multi-target support. The operator's answer makes it a follow-up.
  - The 12-piece table, the routing rows, the preamble and the eight role prompts, including their INPUT lines. The block is declared once, in the Harness section.
  - `prompts/`, `plans/` and `README.md`.
- **The reference harness** (`~/dev/nanobot-upstream/factory/`) is read only. Under option (b) it already matches the new text (E3, E4), so it needs no fix.
- **Recording which version of the block a run saw** (for example a hash field in `meta.yaml`). Answer 2 makes this a follow-up. Until then the version is visible only in each run's `input.md`.
- **Observations, not fixed here:**
  - The as-built composer also inserts an `## Output file` section and per-source `## <heading>` lines between the block and the sources (E3, E4). Neither document declares them.
  - "How to use this" (`docs/spec-factory.md:7`) tells a new repo to fill in `{braces}`, but not to write a role-context block. The operator limited this change to the Harness section.
  - The design gives the block no change-control status. Guardrail paths cover "these prompts", and the block shapes every role much as a prompt does. The reference keeps it at `factory/prompts/context.md`, and `specs/build-harness.md:158` treats `factory/prompts/**` as guardrail. This repo's workaround copy, `intake/instance/context.md`, falls under the protected `infra` path. Whether the design should name the block as a guardrail or protected path is a separate decision for a follow-up.

## Open questions

none. v1's one open question (should the role-context block be recorded in a run's `input_sources`?) was resolved by Answer 2 as option (b): exempt it, and say why. The block is the same for every run against the repo and its text is already in each run's `input.md`, so the run stays auditable; `input_sources` keeps listing declared store paths only. Items 9, 42 and 77 keep their `input_sources` lists, and `plans/build-harness.md` does not change. Answer 2 was taken under the standing take-the-recommendation rule, so the operator can still overturn it at the spec gate.

## Risk

The blast radius is document text only: 7 lines added and 4 removed across two files. No harness, store or prompt changes. A wording mistake in part A would mislead whoever sets up a repo or builds a harness from the doc. Criteria 1, 2 and 4 pin the meaning, and criteria 8–10 show the prompts, the piece table and the routing rows are untouched.

`specs/build-harness.md` item 42 is an acceptance item of an approved spec, and part D.3 rewrites it. This is not editing a criterion to match work: today item 42 contradicts both the as-built harness (E4) and the new design text, and the change keeps its isolation checks intact ("exactly `[specs/T-0001/v1.md]`", no triage output, no writer `CONFIDENCE:` line). It needs the human's approval at the spec gate.

Protected and guardrail paths:
- None are touched. `prompts/**` (generated) is not touched, because no prompt block changes (criteria 8 and 12).
- `intake/**` (infra) is not touched, apart from this output file, which the harness designates.
- `~/dev/nanobot-upstream/**` was read only, with `sed`, `grep`, `git show`, `git log` and `git diff --stat`.
- `~/.nanobot/**` was not read.

Merge order: T-0001, T-0002, T-0003 and T-0005, all awaiting the gate, also append Changelog item 34. Whichever merges later renumbers its entry, and criterion 3 accepts any order. None of them edits `docs/spec-factory.md` lines 50 or 68, or `specs/build-harness.md` lines 201, 294 or 393. I checked their Proposed change sections. T-0002 also edits `specs/build-harness.md` part B (a new bullet before `factory request new`), part H and Risk, all text-anchored and none on the three lines part D changes. T-0002 edits the piece-2 row, so criterion 9 compares against `main` at merge time, not against `28b3a74`.

## Responses

No critic findings yet; this is v2, written after Answer 2. Changes from v1:
- Open question 1 resolved as (b) per Answer 2. Open questions is now none, and the Proposed change, Acceptance (criterion 6 is now plain NEW) and Out of scope text say so. Parts A–D, the 13 criteria and their commands are unchanged.
- Re-based on `main` `172a71e`; the documents are byte-identical to `28b3a74`. All 13 criteria were re-run on `main` and on a fresh scratch clone with A–D applied, with the same results as v1.
- Corrected a citation: Changelog item 33 is at `docs/spec-factory.md:641`, not `:640`. The triage ticket and v1 both said `:640`.
- Corrected the merge-order note: T-0002 also appends a Changelog item 34, and it edits other parts of `specs/build-harness.md`, without overlapping part D.
