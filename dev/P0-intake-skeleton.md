# P0: intake walking skeleton

Parent: `dev/build-harness.spec.md` (v4). This is not a sub-ticket of `dev/build-harness.plan.md`; it is a cut through it. It builds BH-1-lite, BH-4, and BH-5 and defers BH-2a, BH-2b, BH-3, BH-6, BH-7. Nothing built here is thrown away: the agent definitions, the `factory` CLI, and `intake.js` are the same files the full plan grows.

## Why first

Plan v2 builds the enforcement layer (bare repo, hook, identities, merge gate) before a faux-spec ever flows through a role. The first end-to-end flow is BH-5, four infrastructure sub-tickets in. The question that stalled the Nanobot port was spec quality, not enforcement. P0 answers that question before paying for enforcement, and it exercises the three things the spec marks not-verified on a Mac that don't need a bare repo: Workflow under `claude -p`, model alias strings in `agent()`, and the clerk-via-CLI pattern.

The design doc names v0 as "exercising the routing table, not producing trusted merges." P0 is v0 as designed.

## What it is

One workflow script driving the intake half of the routing table on real input:

```
knowledge_vault/specs/<file>.md
  → Triage (ACCEPT | NEEDS-HUMAN | CLARIFY | REJECT)
  → Spec writer ⇄ Spec critic, max {2} rounds
  → human gate (you read the spec in knowledge_vault/sanitized_specs/)
  → Planner
```

Parts, by the spec's lettering:

| Part | What | From plan v2 |
|---|---|---|
| A | `.claude/agents/factory-*.md` for Triage, Spec writer, Spec critic, Planner, clerk, stub; preamble file; `config.yaml` with `models:` from the doc's table | BH-4 (subset) |
| B-lite | `factory` CLI with four verbs: `ticket new`, `transition` (with the round guard and routing-edge guard), `record`, `run start/finish` writing `runs/<id>/meta.yaml` with `model` | BH-1 (subset) |
| H-intake | `factory/workflows/intake.js`: Triage → writer ⇄ critic join → gate → planner; clerk agent for every store write; `parallel()` unused here | BH-5 |
| K-lite | `factory approve-spec ID` and `factory resolve ID --answer FILE`, run as you | BH-3 (two verbs) |

Store: `tickets/*.yaml` in the working tree of the green checkout, committed by you. No `tickets` branch, no hook, no identities.

## What it skips, on purpose

Bare repo, pre-receive hook, per-role keys, merge gate, gate-run, implementer, reviewer, verifier, retro, parent-close run. Every skipped piece is enforcement or the PR loop. None is needed to learn whether intake produces specs you would build from.

## Acceptance (run as written, on the green checkout)

Black-box, numbered P0-1.. so they don't collide with the spec's 1–84. Each is NEW; today every one fails with `factory: command not found` or "no such workflow", and P0-9 because no `.claude/agents/factory-*.md` file exists yet (its count is `0`).

- P0-1 `factory ticket new --file knowledge_vault/specs/<any>.md` → `tickets/T-0001.yaml` exists with `status: ready-for-triage`, `round: {spec: 0}`.
- P0-9 (after Part A, before P0-2; numbered last so P0-2..P0-8 keep their numbers) A fresh session in the green checkout registers every Part A agent: `ls .claude/agents/factory-*.md | wc -l` → `6`; `diff <(sed -n 's/^name: //p' .claude/agents/factory-*.md | sort) <(claude -p --model haiku --max-turns 1 --output-format stream-json --verbose ok </dev/null | grep '"subtype":"init"' | grep -o '"agents":\[[^]]*\]' | grep -oE '"factory-[^"]*"' | tr -d '"' | sort)` → no output, exit 0. Run P0-2..P0-8 in a session started after this check.
- P0-2 `/factory run intake T-0001` with the `factory-stub` agents configured to emit `STATUS: ACCEPT` then `STATUS: READY-FOR-CRITIC` then `STATUS: APPROVE` → ticket ends `awaiting-spec-gate`; `runs/` holds three `meta.yaml` files, each with `role`, `model`, `started`, `finished`.
- P0-3 Same, stubs emit `REVISE` twice → ticket ends `parked` with reason `max rounds`, `round.spec: 2`, and no `transition` call set the counter by hand (grep the run log).
- P0-4 Stub emits `CLARIFY` → ticket `waiting-requester`; `factory resolve T-0001 --answer a.md` → `ready-for-triage`; `runs/` shows the answer in Triage's next `input.md`.
- P0-5 Real models, one real faux-spec: ticket reaches `awaiting-spec-gate`; `knowledge_vault/sanitized_specs/T-0001.md` exists in the spec FORMAT; its Acceptance prose, with fenced code blocks stripped, names no test function or internal symbol: `awk '/^[[:space:]]*\140\140\140/{f=!f; next} !f && /^## /{a=/^## Acceptance/} a && !f' knowledge_vault/sanitized_specs/T-0001.md | grep -cE 'test_[a-z_]+\(|def |::'` → 0 (`\140` is a backtick, written as an octal escape so the command fits in one code span). Code inside fences (the writer prompt's inline-script allowance) is not gated; the package symbols it imports or calls are counted under What you measure.
- P0-6 `factory approve-spec T-0001` as you → `ready-for-planner`; `/factory run intake T-0001` continues → `plans/T-0001.md` exists with a coverage map whose item count equals the spec's Acceptance count.
- P0-7 Round-2 input: after a real REVISE, `runs/<critic round 2>/input.md` contains the round-1 findings text and the writer's Responses section.
- P0-8 `transition T-0001 --to ready-for-implementer` from `ready-for-triage` → exit 2, "not a routing edge."

## What you measure (three real faux-specs)

| Metric | Baseline from the port | P0 target |
|---|---|---|
| Rounds to critic APPROVE | n/a | ≤ 2 (the cutoff) |
| Code identifiers in Acceptance prose (fenced blocks stripped) | "doubled", ten relint commits | 0 (P0-5) |
| Package symbols that inline Acceptance scripts import or call | n/a | record, not gated: the line count of the symbol block below |
| Your interventions per spec | "most interrupts were which-function questions" | count them; each one is a retro incident |
| Cost per spec | n/a | record; per-(role, model) from `meta.yaml` |
| Would you approve it at the gate unedited? | n/a | yes for ≥ 2 of 3 |

The second number: from the green checkout, with `S` set to the spec file and `PKG=nanobot`, the block below prints the distinct fully-qualified package symbols that fenced code under `## Acceptance` imports, calls or patches, sorted, one per line. The recorded number is its line count; keep the list with it. Counted: `from PKG[.mod] import a, b as c` (each name), `import PKG.x [as A]`, any dotted `PKG.x[.y…]` reference elsewhere in fenced code (so `python -m PKG.x`, `PKG.x.f()` and `mock.patch("PKG.x.Y")`), and `name.attr` on a name bound by an import. Not counted: helpers the script defines, stdlib and third-party imports, attributes reached through an instance (`Cls().method`), and anything in prose or outside Acceptance. Names are distinct per spec, not per criterion, and string targets count: both are choices, visible here so the metric is read with them.

~~~sh p05-symbols
python3 - "$PKG" "$S" <<'PY'
import re, sys
pkg, path = sys.argv[1], sys.argv[2]
code, fence, acc = [], False, False
for line in open(path, encoding="utf-8"):
    line = line.rstrip("\n")
    if re.match(r"^\s*```", line):
        fence = not fence
        continue
    if not fence and line.startswith("## "):
        acc = line.startswith("## Acceptance")
        continue
    if acc and fence:
        code.append(line)
text, found, bound, P = "\n".join(code), set(), {}, re.escape(pkg)
def take(m):  # from PKG[.mod] import a, b as c; the line is not re-scanned, the module path is not counted
    mod, items = m.group(1), m.group(2).strip("()")
    for parts in (it.split() for it in items.split(",")):
        if parts:
            found.add(mod + "." + parts[0]); bound[parts[2] if len(parts) == 3 else parts[0]] = mod + "." + parts[0]
    return " "
text = re.sub(r"^\s*from\s+(" + P + r"(?:\.\w+)*)\s+import\s+(\([^)]*\)|[^\n;#]+)", take, text, flags=re.M)
def take2(m):  # import PKG.x [as A]
    found.add(m.group(1)); bound[m.group(2) or m.group(1)] = m.group(1); return " "
text = re.sub(r"^\s*import\s+(" + P + r"(?:\.\w+)+)(?:\s+as\s+(\w+))?\s*$", take2, text, flags=re.M)
found.update(re.findall(r"\b" + P + r"(?:\.\w+)+", text))  # any other dotted PKG reference, as written
for alias, target in bound.items():  # name.attr on a bound name, not inside another dotted path; Cls().attr does not match
    found.update(target + "." + a for a in re.findall(r"(?<![\w.])" + re.escape(alias) + r"\.(\w+)", text))
print("\n".join(sorted(found)))
PY
~~~

If ≥ 2 of 3 specs pass the gate unedited, the next walking step is BH-6 (the PR loop) on one of them, still without the hook. If not, the retro runs on the three transcripts before any more harness is built, and the fix is in the prompts, not the plan.

The three pilots are SPEC-21, SPEC-26 and SPEC-27 (green's T-0001, T-0002, T-0003). Their specs were pinned before `factory init` created `openspec/` (2026-10-01), so they have no change folder: each parent-close `factory archive` refuses with `no change folder`, the parent parks, and the human closes it as applied (build spec K).

## Risk

- Protected paths touched: none (no infra, no keys, no dependencies beyond pyyaml).
- Workflow under `claude -p` unverified; fallback is an interactive session (same script).
- Role agents may not register mid-session. Claude Code loads `.claude/agents/` when a session starts and afterwards watches it only if the directory existed then, and it never watches the one inside a directory added with `--add-dir`; a session started before Part A's files were written may not see them (2026-10-01: `Agent(subagent_type: "factory-clerk")` → "Agent type 'factory-clerk' not found"). Start the session that runs P0-2..P0-8 in the green checkout after Part A's agent files exist, or restart it after writing them; P0-9 checks this before P0-2. Running every role as `general-purpose` with its prompt read from a file keeps each role's model but drops the `tools:` fences of R6, so R6 is not in force on such a run.
- `agent()` model alias strings unverified; P0-2's `meta.yaml` check is where you find out.
- The working-tree store has no identity on writes. Fine for P0; it is why P0 cannot be used for merges.

## Tests to change: none.

## Out of scope

Everything in "What it skips." Also: the `/factory intake <dir>` bulk form (one ticket at a time is enough to measure), the audit sample, and any change to the frozen `SPEC_MAINTENANCE_WORKFLOW.md`.

STATUS: PLANNED
CONFIDENCE: medium (the unverified items above are exactly what P0 exists to verify)
ESCALATIONS: Nanobot gate commands still unknown (not needed until BH-6); which three faux-specs to use is your call.
