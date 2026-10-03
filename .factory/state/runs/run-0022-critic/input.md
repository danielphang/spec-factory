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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0022-critic/output.md`

## Spec under review (v1)

## Problem

P0-5 in `plans/P0-intake-skeleton.md` is meant to catch Acceptance criteria that name a test function or an internal symbol, which go stale and which the verifier can't run. Today it greps the whole spec file. The Spec writer prompt lets a criterion give its check as an inline script (`prompts/02-spec-writer.md:24-26`, `docs/spec-factory.md:270-272`). So any spec that uses that allowance scores a P0-5 hit for a helper the script defines, such as `def sess(...)`. It also scores hits for symbols under Root cause and Proposed change, which is where the writer prompt says symbols belong. The metric row "Code identifiers in acceptance" therefore can't tell a stale symbol in a criterion from allowed fixture code. The people affected are the operator reading P0 measurements and every P0 run that uses the allowance.

The operator's decision (Answer 1, option c, 2026-10-01) asks for two numbers:
1. P0-5 gates on prose only: the Acceptance section with fenced blocks stripped must have 0 hits.
2. The package-internal symbols that inline Acceptance scripts import or call are counted and recorded in the metric table, without gating. Helpers the script defines itself are not counted.

The writer prompt's allowance stays as it is.

## Evidence

All commands below were run this session. Paths under `~/dev/nanobot-upstream` were only read.

- Current text. `plans/P0-intake-skeleton.md:46` runs `grep -cE 'test_[a-z_]+\(|def |::' knowledge_vault/sanitized_specs/T-0001.md` → 0 over the whole file. Row `:56` reads `| Code identifiers in acceptance | "doubled", ten relint commits | 0 (P0-5) |`. A grep for `P0-5\|Code identifiers` over `docs specs plans prompts README.md issues` finds only those two lines and issue 06, so no other document restates the rule.
- Results on the real P0 specs in the reference store `~/dev/nanobot-upstream/knowledge_vault/spec_factory/specs/`. "Whole-file" is today's grep. "Restated" is the fence-aware, Acceptance-only command proposed under A.

  | Spec | Whole-file | Restated | Fence lines in Acceptance |
  |---|---|---|---|
  | T-0001/v1.md | 1 | 0 | 8 |
  | T-0001.md | 1 | 0 | 8 |
  | T-0003.md | 5 | 0 | 4 |

  T-0003's hits are fixture `def skill`, `def summary` and `def need` inside Acceptance fences.
- The triage's suggested pipeline is `awk '/^## /{a=…}' | awk '/^```/{f=!f;next} !f'`. It has two defects, and the fixtures used under Acceptance show both:
  - It recognises only column-0 fences. T-0001/v1's Acceptance has 8 fence lines, and 6 of them are indented under list items: `grep -c '^```'` gives 2, `grep -c '^[[:space:]]*```'` gives 8. A `def helper(` inside an indented fence counts as prose. On the first fixture below, that pipeline prints 1 where 0 is right.
  - Its section toggle doesn't know about fences. A column-0 `## ` line inside a fenced heredoc ends the Acceptance section early, and a later real prose hit is missed. On the second fixture below, that pipeline prints 0 where 1 is right.
- There's a real case for the second number. T-0001/v1's Acceptance item A1 is an indented fence containing `from nanobot.agent.context_governance import ContextGovernanceConfig, ContextGovernor` (Acceptance-relative lines 48-50). The round-1 critic flagged it as "[NIT] #2 — A1/A2 name internal symbols" (`~/dev/nanobot-upstream/knowledge_vault/spec_factory/runs/run-0004-critic/output.md`). Today's grep can't see it: it has no `def `, `::` or `test_x(`. The prototype counter in C prints, for T-0001/v1.md:
  - `nanobot.agent.context_governance.ContextGovernanceConfig`
  - `nanobot.agent.context_governance.ContextGovernor`

  For T-0003.md it prints:
  - `nanobot.agent.plugins`
  - `nanobot.agent.plugins.get_config_path`
  - `nanobot.agent.plugins.set_agent_plugin_enabled`
  - `nanobot.agent.skills.SkillsLoader`
- No harness fix exists. The only as-built handling is a manual note at `~/dev/nanobot-upstream/knowledge_vault/spec_factory/P0_MEASUREMENTS.md:8`: "0 outside code fences (1 inside the inline fixture script, which the writer prompt allows)".
- I applied the proposed change to a scratch copy of the plan (41 diff lines) and ran every Acceptance command below against both the unchanged checkout and the scratch copy. The base and PR results quoted under Acceptance are those actual outputs.
- `awk version 20200816` (macOS BSD awk) handles `\140` in a regex and `a=/re/`.

## Root cause

`plans/P0-intake-skeleton.md:46`, the P0-5 bullet, applies the identifier pattern to the whole file. It has no notion of the Acceptance section or of fenced code. Row `:56` gives the metric only one number, so the allowed inline-script code and the forbidden prose naming end up in the same count. Nothing in the plan defines how to count the package symbols that inline scripts depend on.

## Proposed change

Edit `plans/P0-intake-skeleton.md` only.

**A. Restate the P0-5 bullet (line 46).** Keep the bullet's start, `- P0-5 Real models, one real faux-spec: ticket reaches `awaiting-spec-gate`; `knowledge_vault/sanitized_specs/T-0001.md` exists in the spec FORMAT;`. Replace the trailing whole-file grep with prose saying the Acceptance prose, with fenced code blocks stripped, names no test function or internal symbol. Then give this command in a single-backtick code span, followed by `→ 0`:

`awk '/^[[:space:]]*\140\140\140/{f=!f; next} !f && /^## /{a=/^## Acceptance/} a && !f' knowledge_vault/sanitized_specs/T-0001.md | grep -cE 'test_[a-z_]+\(|def |::'`

Add one parenthetical saying `\140` is a backtick, written as an octal escape so the command fits in one code span. Add one sentence saying code inside fences (the writer prompt's inline-script allowance) is not gated and is counted under What you measure.

The Acceptance checks extract this command, so it must meet three constraints:
- The bullet still starts with `- P0-5 `.
- The command is the only code span on that line containing `grep -c`.
- The span contains no literal backtick and keeps the literal path `knowledge_vault/sanitized_specs/T-0001.md`.

The identifier pattern itself is unchanged.

Design notes:
- The fence state is tracked across the whole file, so a `## ` line inside any fence is never taken as a heading. That fixes the second defect described under Evidence.
- Indented fences (up to any indentation) count as fences. That fixes the first defect.

**B. Metric table.**
- Rename the first column of row `:56` to `Code identifiers in Acceptance prose (fenced blocks stripped)`. Keep its baseline and `0 (P0-5)` cells.
- Add a row directly below it: `| Package symbols that inline Acceptance scripts import or call | n/a | record, not gated: the line count of the symbol block below |`.
- Leave every other row unchanged.

**C. Symbol block.** Directly after the metric table (before "If ≥ 2 of 3 specs…"), add a paragraph and a tilde-fenced block.

The paragraph describes three things:
- How to run the block: from the green checkout, with `S` set to the spec file and `PKG=nanobot`.
- What it prints: the distinct fully-qualified package names, sorted, one per line.
- That the recorded number is the line count, and that the list is kept with it.

The block opens with exactly `~~~sh p05-symbols` and closes with exactly `~~~`, both at column 0. Its body is a `python3 - "$PKG" "$S" <<'PY' … PY` heredoc that implements this counting rule:

1. Only lines inside fences (```` ``` ````, any indentation) inside the `## Acceptance` section count. The section is tracked the same way as in A. Prose and other sections are never counted.
2. `from PKG[.mod] import a, b as c` (including a parenthesised multi-line list) counts `PKG[.mod].a` and `PKG[.mod].b`.
3. Any dotted reference `PKG.x[.y…]` elsewhere in fenced code counts as written. This covers `import PKG.x`, `python -m PKG.x`, `PKG.x.f()` and string targets such as `mock.patch("PKG.x.Y")`.
4. For each name bound by rule 2, or by `import PKG.x as A`, every `name.attr` reference counts `<target>.attr`.
5. Not counted:
   - names the script defines itself (they never resolve to `PKG`);
   - stdlib and third-party imports;
   - attributes reached through an instance, such as `Cls().method`.

A reference implementation (33 lines including fences) was prototyped and run this session; its output is quoted under Evidence and Acceptance. The implementer may write it differently, provided the Acceptance output matches.

**Counting choices made here (the operator did not fix them; the gate can strike either):**
- Distinct names are counted per spec, not per criterion. The aim is to measure the symbol surface a spec depends on, and criteria have no machine-readable boundary.
- Rule 3 counts dotted string references such as `mock.patch` targets. Strictly, these are neither imported nor called, but they are the most common stale-symbol dependency in fixture code.

Both choices are visible in the plan's paragraph, so a reader of the metric sees them.

## Acceptance

All commands run from `~/dev/spec-factory`. Each fixture is built with a placeholder `FENCE` that `awk` turns into a triple backtick, so the scripts can be pasted verbatim.

- **1 [NEW]** P0-5 does not gate fixture code or symbols under Root cause. The fixture's only identifier hits are a column-0 fenced helper `def`, an indented fenced helper `def`, and a double-colon symbol path under Root cause. Its Acceptance prose is clean. The command extracts P0-5's command from the plan and runs it on the fixture. → prints `0`. **Fails today:** prints `3` (the whole-file grep counts both helpers and the Root-cause symbol). The triage's column-0 de-fencing would print `1`.

```
cd ~/dev/spec-factory && D=$(mktemp -d) && awk '{gsub(/FENCE/, sprintf("%c%c%c", 96, 96, 96))} 1' > "$D/f1.md" <<'MD'
## Root cause
`nanobot/agent/loop.py::AgentLoop` drops the event; symbols belong here.
## Acceptance
Fixture, once per run:
FENCE
cat > /tmp/fx.py <<'PY'
def sess(key):
    return key
PY
FENCE
- **A1 [NEW]** a trim records the event:
  FENCE
  python - <<'PY'
  from nanobot.agent.gov import Governor, Config as C
  def helper(x):
      return x
  print(C.load(helper(1)))
  PY
  FENCE
  → `records: 1`.
## Out of scope
none
MD
cmd=$(grep '^- P0-5 ' plans/P0-intake-skeleton.md | sed -E 's/.*`([^`]*grep -c[^`]*)`.*/\1/') && sh -c "$(printf '%s' "$cmd" | sed "s#knowledge_vault/sanitized_specs/T-0001.md#$D/f1.md#")"
```

- **2 [REGRESSION]** P0-5 still catches a criterion whose prose names a test node id, even after a column-0 fenced heredoc that contains a `## ` line. → prints `1`. **Passes today** (`1`, from the whole-file grep) and must keep passing. The triage's fence-unaware section toggle would print `0`.

```
cd ~/dev/spec-factory && D=$(mktemp -d) && awk '{gsub(/FENCE/, sprintf("%c%c%c", 96, 96, 96))} 1' > "$D/f2.md" <<'MD'
## Acceptance
Report fixture, once per run:
FENCE
cat > /tmp/r.md <<'R'
## Not a heading
R
FENCE
- **A2 [REGRESSION]** `pytest tests/test_trim.py::test_records -v` → 1 passed.
## Out of scope
none
MD
cmd=$(grep '^- P0-5 ' plans/P0-intake-skeleton.md | sed -E 's/.*`([^`]*grep -c[^`]*)`.*/\1/') && sh -c "$(printf '%s' "$cmd" | sed "s#knowledge_vault/sanitized_specs/T-0001.md#$D/f2.md#")"
```

- **3 [NEW]** The plan's symbol block counts package symbols that fenced Acceptance code imports, calls or patches. It does not count script-defined helpers, stdlib or third-party imports, instance attributes, or package names in prose or outside Acceptance. → prints exactly these lines, then `count: 6`:
  - `nanobot.agent.gov.Config`
  - `nanobot.agent.gov.Config.load`
  - `nanobot.agent.gov.Governor`
  - `nanobot.agent.loop.AgentLoop.run`
  - `nanobot.agent.plugins`
  - `nanobot.agent.plugins.discover`

  **Fails today:** prints only `count: 0`, because the plan defines no such count and the `p05-symbols` block is absent. Missing that count is the defect itself.

```
cd ~/dev/spec-factory && D=$(mktemp -d) && awk '{gsub(/FENCE/, sprintf("%c%c%c", 96, 96, 96))} 1' > "$D/f3.md" <<'MD'
## Root cause
`nanobot.agent.loop.AgentLoop` drops the event (prose outside Acceptance: not counted).
## Acceptance
FENCE
cat > /tmp/fx.py <<'PY'
import json
from loguru import logger
def sess(key):
    return json.dumps(key)
PY
FENCE
- **A1 [NEW]** the event is recorded (`nanobot.agent.loop` named in prose: not counted):
  FENCE
  python - <<'PY'
  from nanobot.agent.gov import Governor, Config as C
  from nanobot.agent import plugins as P
  def helper(x):
      return x
  print(C.load(helper(1)), Governor().fit(), P.discover())
  PY
  FENCE
- **A2 [REGRESSION]** `python -m nanobot.cli.health --json` exits 0, and:
  FENCE
  python - <<'PY'
  from unittest import mock
  with mock.patch("nanobot.agent.loop.AgentLoop.run"):
      pass
  PY
  FENCE
## Out of scope
none
MD
awk '/^~~~sh p05-symbols$/{f=1;next} f&&/^~~~$/{exit} f' plans/P0-intake-skeleton.md > "$D/sym.sh" && S="$D/f3.md" PKG=nanobot sh "$D/sym.sh"; echo "count: $(S="$D/f3.md" PKG=nanobot sh "$D/sym.sh" | grep -c .)"
```

- **4 [NEW]** The metric table records the second number as non-gating: `grep -cE '^\| Package symbols .*\| record, not gated' plans/P0-intake-skeleton.md` → `1`. **Fails today:** `0`.
- **5 [REGRESSION]** P0-1..4 and P0-6..8 are unchanged: `diff <(git show main:plans/P0-intake-skeleton.md | grep -E '^- P0-[1234678] ') <(grep -E '^- P0-[1234678] ' plans/P0-intake-skeleton.md) && echo same` → `same`. **Passes today.**
- **6 [REGRESSION]** The other four metric rows are unchanged: `diff <(git show main:plans/P0-intake-skeleton.md | grep -E '^\| (Rounds|Your interventions|Cost per spec|Would you)') <(grep -E '^\| (Rounds|Your interventions|Cost per spec|Would you)' plans/P0-intake-skeleton.md) && echo rows-same` → `rows-same`. **Passes today.**
- **7 [REGRESSION]** The design doc, build spec, prompts and README are untouched: `git diff --quiet main -- docs specs prompts README.md && echo unchanged` → `unchanged`. **Passes today.**
- **8 [REGRESSION]** There are no whitespace errors: `git diff --check main -- plans/P0-intake-skeleton.md; echo check=$?` → `check=0` and nothing else. **Passes today.**

## Tests to change

None. The repo holds documents and has no test suite.

## Out of scope

- The writer prompt's inline-script allowance and its "never names a test function or internal symbol" rule (`prompts/02-spec-writer.md`, `docs/spec-factory.md:262-276`), critic rubric item 2, `specs/build-harness.md`, and every file under `prompts/` and `intake/`.
- The identifier pattern `test_[a-z_]+\(|def |::`. Widening it was not requested.
- Tilde (`~~~`) fences in specs. The gate does not recognise them, so their content counts as prose. That can only over-count, never hide a hit. Nothing in the P0 specs uses them.
- The P0-5 spec path `knowledge_vault/sanitized_specs/T-0001.md`. The as-built store on green is `knowledge_vault/spec_factory/specs/`, but reconciling the two is a separate finding and is not touched here.
- Anything on green (`~/dev/nanobot-upstream`), including adding the second number to `P0_MEASUREMENTS.md`.

## Open questions

None. The operator settled the design (option c). The two counting choices in C are stated openly, so the gate can strike them without reopening the design.

## Risk

- Blast radius: one planning document. About 41 changed lines in total: one bullet, one renamed row, one new row, one paragraph and a 33-line block. No code, no gating merge logic, and no role prompt changes.
- Protected paths touched: none. `plans/` is not protected. `prompts/**`, `intake/**`, `~/dev/nanobot-upstream/**` and `~/.nanobot/**` are neither written nor read by the change or its Acceptance. The Evidence reads of `~/dev/nanobot-upstream` were read-only.
- Weakening risk: the gate now ignores code inside fences. A writer could move a stale symbol into a fenced block and pass P0-5. That is exactly what the operator chose to observe rather than gate. The symbol block records it, so the runs show whether a stricter rule is needed.
- Portability: the gate uses `\140` and `a=/re/` in awk. Both are POSIX and were verified on macOS awk 20200816. They were not verified on gawk or mawk this session. The symbol block needs `python3` on the green checkout.
