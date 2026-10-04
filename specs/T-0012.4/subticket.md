## T-0012.4 / Harness lock: refuse an unaccepted or modified harness on the instance's own store, `--accept-harness`

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: T-0012.3

Parallel-safe: no, with T-0012.6. E's lock must be written after this sub-ticket's harness commits have merged. It is parallel-safe with T-0012.5.

Scope: C.2–C.5.
- C.1 already exists from T-0012.3.
- The check runs only when the store in use is the instance's own store.
- `init` and `paths` are exempt.
- The dirty check uses `git -C <running harness> status --porcelain -- factory bin/factory agents pyproject.toml uv.lock`.

Acceptance (first `uv sync --frozen`):
- **lock-mismatch-refused** → NEW [specs/harness-lock]. THEN `init=0`, then `exit=2 tickets=0 hint=1`.
- **accept-current-revision-rewrites-lock** → NEW [specs/harness-lock]. THEN `init=0`, then `exit=0 lock_is_rev=yes logged=N`, N ≥ 1.
- **accept-other-revision-refused** → REGRESSION (relabelled by the operator, 2026-10-03: passes at base vacuously, per implementer run-0069; the discriminating evidence is the new C tests) [specs/harness-lock]. THEN `init=0`, then `exit=2 lock=0000000000000000000000000000000000000000 tickets=0`.
- **throwaway-store-ignores-lock** → REGRESSION (relabelled by the operator, 2026-10-03: passes at base vacuously, per implementer run-0069; the discriminating evidence is the new C tests) [specs/harness-lock]. THEN `init=0`, then `exit=0 ticket=[T-0001.yaml]`.
- **dirty-harness-refused** → NEW [specs/harness-lock]. THEN `init=0`, then `exit=2 tickets=0 names=1`.
- **missing-lock-refused** → NEW (intermediate; C.2 "or the lock is missing").
  - WHEN the parent's lock-mismatch-refused command, with `printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock` replaced by `rm -f $T/.factory/harness.lock`.
  - THEN `init=0`, then `exit=2 tickets=0 hint=1`.
- **init-and-paths-exempt** → REGRESSION (relabelled by the operator, 2026-10-03: passes at base vacuously, per implementer run-0069; the discriminating evidence is the new C tests) (intermediate; C.2).
  - WHEN `H=$PWD; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && cd $T && $H/bin/factory init --repo-name demo >/dev/null 2>&1; printf '%040d\n' 0 > .factory/harness.lock; $H/bin/factory paths >/dev/null 2>&1; p=$?; $H/bin/factory init >/dev/null 2>&1; echo "paths=$p init=$? lock=$(cat .factory/harness.lock)"`
  - THEN `paths=0 init=0 lock=0000000000000000000000000000000000000000`.
- **accept-does-not-override-dirty** → REGRESSION (relabelled by the operator, 2026-10-03: passes at base vacuously, per implementer run-0069; the discriminating evidence is the new C tests) (intermediate; C.4).
  - WHEN `H=$PWD; C=$(mktemp -d)/h; git clone -q "$H" "$C" && uv sync -q --frozen --project "$C"; T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && cd $T && "$C"/bin/factory init --repo-name demo >/dev/null 2>&1; L=$(cat .factory/harness.lock); REV=$("$C"/bin/factory paths | python3 -c 'import json,sys; print(json.load(sys.stdin)["harness_revision"])'); echo '# local edit' >> "$C"/factory/__init__.py; printf '# demo\n\nDo the thing.\n' > r.md; "$C"/bin/factory --accept-harness "$REV" ticket new --file r.md >/dev/null 2>&1; echo "exit=$? lock_same=$([ "$(cat .factory/harness.lock)" = "$L" ] && echo yes || echo no) tickets=$(ls .factory/state/tickets 2>/dev/null | wc -l | tr -d ' ')"`
  - THEN `exit=2 lock_same=yes tickets=0`.
- **All nine T-0012.3 factory-instance and harness-home scenarios** → REGRESSION, with the same THEN as at T-0012.3. Each makes a fresh `init`, whose lock matches, so the new checks must not refuse them. Run from a clean checkout: an uncommitted harness edit in the checkout under test would now refuse them, by design.
- **harness-suite-passes-after-uv-sync** → REGRESSION. N ≥ 70, plus the new C tests, no `failed`/`error`.
- **green-harness-still-present** → REGRESSION.
- **whitespace (sub-ticket diff)** → REGRESSION. `exit=0`.

Tests to change: `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides` (operator ruling, 2026-10-03, on implementer run-0069's escalation). It was written in T-0012.3, before the lock, and builds an instance `alt` with no `harness.lock`, which C.2 now refuses. Add one line after `(alt / "context.md").write_text("x\n")`: `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`. C.2 stands as written; `config` is not exempted. Otherwise new C test files only.

Protected paths: none of instance B's classes.

Out of scope:
- Writing instance B's `.factory/harness.lock` (E).
- Any refusal of a mismatch between `instance.yaml`'s `harness:` value and the running checkout. The spec has none.
- Changes to `init` or `paths` beyond keeping them exempt.

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
