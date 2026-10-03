## T-0012.5 / Design-doc and build-spec text for `.factory/` instances

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: T-0012.2

Parallel-safe: yes, with T-0012.1, .3, .4 and .6. Its only files are `docs/design.md`, `docs/changelog.md` and `dev/build-harness.spec.md`, which no sibling edits after T-0012.2. It touches no harness path, so it may merge after T-0012.6 without changing the harness revision.

Scope: F.1–F.4.
- The changelog entry is numbered one past the last entry at merge time (42 today).
- `## Responses` in `dev/build-harness.spec.md` stays as written.
- Neither replaced line in `docs/design.md` (the "Role-context block" paragraph, piece 8's row) is inside a prompt block, so no `docs/prompts/` file changes. Prompt-copies-moved-unchanged checks this.

Acceptance:
- **design-doc-instance-text** → NEW [specs/repo-layout]. THEN `kept=1 open=0 piece8=1 logged=1`.
- **build-spec-render-paths** → NEW [specs/repo-layout]. THEN `stale=0 new=N d8=1`, N ≥ 3. Today, at `specs/build-harness.md`, the three stale hits before `## Responses` (line 523) are lines 145, 158 and 456, the ones F.4 names.
- **changelog-entry-appended** → NEW (intermediate; F.3).
  - WHEN `grep '^[0-9][0-9]*\. ' docs/changelog.md | tail -1 | grep -c "^$(($(git show main:docs/changelog.md | grep -c '^[0-9][0-9]*\. ')+1))\. After issue #19 (2026-10-02):"`
  - THEN `1`.
- **responses-unchanged** → NEW (intermediate; F.4).
  - WHEN `diff <(git show main:dev/build-harness.spec.md | awk '/^## Responses/{f=1} f') <(awk '/^## Responses/{f=1} f' dev/build-harness.spec.md) >/dev/null; echo "exit=$?"`
  - THEN `exit=0`.
- **changelog-moved-verbatim** → REGRESSION. THEN `SAME`, then `declined=1 numbering=CONTIGUOUS in_design=0`. The appended entry is beyond the compared head and keeps numbering contiguous.
- **design-text-kept** → REGRESSION. THEN `0`. The only two rewritten lines are the ones the scenario excludes.
- **prompt-copies-moved-unchanged** → REGRESSION. THEN `changed=0 of 10 VERBATIM`.
- **no-old-paths, documents only** → REGRESSION (the T-0012.2 intermediate). THEN `exit=1`.
- **whitespace (sub-ticket diff)** → REGRESSION. `exit=0`.

Tests to change: none

Protected paths: none

Out of scope:
- Building `factory render` / `render --check`.
- Reconciling the build spec's third meaning of `factory init` (the parent's out-of-scope observation).
- Editing any changelog entry other than the appended one.
- `README.md` (E).

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
