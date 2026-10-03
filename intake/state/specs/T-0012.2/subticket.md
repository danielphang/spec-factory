## T-0012.2 / Document re-layout: `docs/design.md` + `docs/changelog.md`, `docs/prompts/`, `dev/`

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: none

Parallel-safe: yes, with T-0012.1. Its files are `docs/**`, `prompts/**`, `specs/build-harness.md`, `plans/**`, `issues/README.md`, `dev/**`, `README.md`, `intake/README.md` and `intake/instance/context.md`, and T-0012.1 touches none of them. Every later sub-ticket waits for it.

Scope: D.1–D.4.
- Content is unchanged apart from the path updates D.4 lists, plus the one added line in "How to use this".
- Records are left as written: `intake/answers/`, `intake/green-pilot/`, `intake/state/`, and the changelog entries.

Acceptance:
- **docs-moved-and-split** → NEW [specs/repo-layout]. THEN only `old_tracked=0`.
- **changelog-moved-verbatim** → NEW [specs/repo-layout]. THEN `SAME`, then `declined=1 numbering=CONTIGUOUS in_design=0`.
- **design-text-kept** → NEW [specs/repo-layout]. THEN `0`.
- **prompt-copies-moved-unchanged** → NEW [specs/repo-layout]. THEN `changed=0 of 10 VERBATIM`.
- **no-old-paths, documents only** → NEW (intermediate for no-old-paths-in-live-files). `agents`, `factory` and `.factory/*` are left out here because T-0012.1's overlay may be on `main` until T-0012.3, and `.factory/` arrives in T-0012.6.
  - WHEN `git grep -n -e 'docs/spec-factory\.md' -e 'specs/build-harness\.md' -e 'plans/build-harness\.md' -e 'plans/P0-intake-skeleton\.md' -e 'issues/README\.md' -e 'HARNESS_PIN' -e 'intake/setup\.sh' -e '[^/a-z_]prompts/' -e '^prompts/' -- README.md docs dev >/dev/null; echo "exit=$?"`
  - THEN `exit=1`. Today the matches are in `README.md` (4), `plans/build-harness.md` (9) and `plans/P0-intake-skeleton.md` (1). `docs/`, `specs/`, `issues/` and `prompts/` have none (`git grep -c`, run today).
- **how-to-use-names-new-homes** → NEW (intermediate; D.1's added line).
  - WHEN `awk '/^## How to use this/{f=1;next} /^## /{f=0} f' docs/design.md | grep 'docs/changelog\.md' | grep -c 'docs/prompts/'`
  - THEN `1`.
- **records-untouched** → REGRESSION (intermediate; an invariant, relabelled by the operator after the verifier's SPEC-DEFECT on run-0057).
  - WHEN `git diff --name-only main...HEAD -- intake/state intake/answers intake/green-pilot intake/.gitignore | wc -l | tr -d ' '`
  - THEN `0`.
- **green-harness-still-present** → REGRESSION. THEN `green keeps its harness`.
- **whitespace (sub-ticket diff)** → REGRESSION. WHEN `git diff --check main...HEAD; echo "exit=$?"`. THEN only `exit=0`.

Tests to change: none

Protected paths:
- generated `prompts/**`: moved to `docs/prompts/`, byte-identical.
- infra `intake/**`: only `intake/README.md` and `intake/instance/context.md`, for reference updates (D.4).

Out of scope:
- The design-doc and build-spec text changes (F), including the changelog entry 42.
- README's full rewrite (E.6). Only references are updated here.
- Removing anything under `intake/` (E).
- Any harness file.

---

## Shared plan context (from the plan; applies to every sub-ticket)

Six sub-tickets, one for each lettered part. The spec's seam list is a real dependency chain (A, then B, then C, then E), and each part is reviewed differently: A by mechanical comparison against green, B and C by reading code and tests, D as pure renames, E as an instance cutover, and F as design prose. Merging any two of them would mix those review modes in one diff. D and F are small enough to merge into one, but F's prose edits would then sit inside a rename diff, which makes the renames harder to verify. So they stay separate.

Order and parallelism:

```
T-0012.1 (A) ─┐
              ├─> T-0012.3 (B) ─> T-0012.4 (C) ─┐
T-0012.2 (D) ─┤                                  ├─> T-0012.6 (E)
              └─> T-0012.5 (F)                   │
              (T-0012.2 also feeds E directly) ──┘
```

- T-0012.1 and T-0012.2 can run in parallel. Their file sets do not overlap (see each ticket).
- T-0012.3 waits for both. That way B's preamble can be checked byte for byte against `docs/prompts/00-preamble.md`, and role-prompt-text-unchanged runs verbatim at B.
- T-0012.5 needs only T-0012.2, and it can run in parallel with .1, .3, .4 and .6, because it edits only `docs/design.md`, `docs/changelog.md` and `dev/build-harness.spec.md`.
- T-0012.6 is the **last sub-ticket that may touch harness paths**. Nothing that edits `factory/`, `bin/factory`, `agents/`, `pyproject.toml` or `uv.lock` runs in parallel with it or merges after it unless that change also rewrites `.factory/harness.lock` (parent E.3; Risk, "Lock behaviour after close"). This includes fix-ups to .1, .3 and .4.

Planner choices the spec left open:
- **`intake/green-pilot/` moves to `.factory/green-pilot/`**, byte-identical, and `intake/answers/` moves to `.factory/answers/`, as E.5 says. `dev/` and `docs/` are ruled out. Both are in the pathspec of no-old-paths-in-live-files, and 23 of the 148 tracked pilot files contain matching old-path strings (`git grep -c <the scenario's patterns> -- intake/green-pilot | wc -l` → `23`). Records may not be rewritten. `.factory/**` is `infra` in E's protected paths, which suits closed records.
- **T-0012.6 (E) puts the moved suite into instance B's gate** (`.factory/instance.yaml`, E.1). During the build, every sub-ticket from T-0012.1 onward also runs the suite as a REGRESSION check in its own acceptance. That holds whether or not the operator does the optional step 1.
- **C.1 (the harness-revision function) is built in T-0012.3 (B)**, not T-0012.4. B.5 (`init` writes `.factory/harness.lock`) and B.6 (`paths` prints `harness_revision`) both need it, and B comes before C. C.2–C.5 (enforcement) stay in T-0012.4. This moves where the code lands. It does not change what the spec asks for.

Readings applied to every sub-ticket (from the spec's own text, not new design):
- `<harness>` in C.1 and C.4 is the **running** checkout: the one whose `bin/factory` is executing. The requirements say "running harness revision" and "running harness checkout". The `harness:` key in `instance.yaml` does not change which checkout is checked. At close, `~/dev/spec-factory-harness` does not exist yet (operator step 2 creates it), and instance-b-opens-every-ticket runs the dev checkout's own `bin/factory`.
- `BASE` in the parent scenarios is the parent's recorded base, for every sub-ticket. Sub-ticket gates use `main...HEAD`.
- Scenarios that call `bin/factory` need the checkout's `.venv`. Without it, `bin/factory` falls back to the system `python3` (green's `bin/factory`: `[[ -x "$PY" ]] || PY="python3"`), which may lack `pyyaml`. Each such sub-ticket therefore starts its acceptance with `uv sync --frozen`.
- Parent scenarios are cited by name. Their WHEN command and THEN result are exactly as written in the parent spec file named in brackets; I did not retype the long commands, to avoid transcription drift. Intermediate checks are written out in full.

---
