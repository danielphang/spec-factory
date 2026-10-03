## T-0012.6 / Instance B cutover: `.factory/`, README rewrite, `intake/` reduced to the live store

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: T-0012.3, T-0012.4, T-0012.2. T-0012.1 is included through .3.

Parallel-safe: no, with any sub-ticket that touches harness paths. Its lock is computed at its base (E.3). It is parallel-safe with T-0012.5 (disjoint files; .5 touches no harness path).

Scope: E.1–E.6.
- **`.factory/instance.yaml`**: as E.1 says, without `request_dir`. Its header comment must be rewritten: the copied lines 1–3 name `intake/setup.sh` and `HARNESS_PIN`, which no-old-paths-in-live-files greps for. Comments are not keys.
- **`.factory/context.md`**: as E.2 says. Write the prompt copies' path only as `docs/prompts/`. A bare `prompts/` after a space or backtick matches the scenario's `[^/a-z_]prompts/`. The same holds for `README.md`.
- **`.factory/harness.lock`**: `git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock` at this branch's base.
- **`.factory/README.md`** (E.4).
- **Removals and moves**: remove `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*`.
  - `git mv intake/answers .factory/answers` and `git mv intake/green-pilot .factory/green-pilot`, both pure renames with no content change.
  - Keep `intake/state/` and `intake/.gitignore`.
- **`README.md`** rewritten (E.6).

Acceptance (first `uv sync --frozen`; from the repo root, no `FACTORY_STATE` or `FACTORY_INSTANCE` in the environment):
- **intake-holds-only-live-store** → NEW [specs/self-instance]. THEN `left=0`.
- **pilot-store-and-answers-kept-byte-identical** → NEW [specs/self-instance]. THEN `kept=134 of 134`, both numbers equal.
- **instance-b-opens-every-ticket** → NEW [specs/self-instance]. THEN `tickets=N failed=0`, N ≥ 12.
- **instance-b-config** → NEW [specs/self-instance]. THEN `True True True`, then `context=N`, N ≥ 2.
- **readme-has-install-and-layout** → NEW [specs/repo-layout]. THEN only `checked`.
- **no-old-paths-in-live-files** → NEW [specs/repo-layout], full pathspec. THEN `exit=1`.
- **lock-is-base-revision** → NEW (intermediate; E.3).
  - WHEN `[ "$(head -1 .factory/harness.lock)" = "$(git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock)" ] && echo lock=current || echo lock=stale; echo "harness_paths_changed=$(git diff --name-only main...HEAD -- factory bin/factory agents pyproject.toml uv.lock tests/factory | wc -l | tr -d ' ')"`
  - THEN `lock=current`, then `harness_paths_changed=0`.
- **instance-b-keys** → NEW (intermediate; E.1).
  - WHEN `uv run --frozen python -c "import yaml,os; c=yaml.safe_load(open('.factory/instance.yaml')); print('request_dir' in c, c['environment_files'], c['state_dir'], c['harness']==os.path.expanduser('~/dev/spec-factory-harness'))"; bin/factory paths | python3 -c 'import json,os,sys; p=json.load(sys.stdin); print(os.path.realpath(p["instance"])==os.path.realpath(".factory"), p["state"].endswith("/intake/state"))'`
  - THEN `False [] intake/state True`, then `True True`.
- **records-moved-as-pure-renames** → NEW (intermediate). This keeps whitespace-clean true. Seven pilot files carry trailing whitespace: `intake/green-pilot/openspec/changes/archive/2026-10-03-T-000{1,2}/…` and `runs/run-0015-implementer/input.md`. `git diff --check` passes over the move only because rename detection pairs them unchanged.
  - WHEN `git diff -M100% --diff-filter=AD --name-only main...HEAD -- intake/green-pilot intake/answers .factory/green-pilot .factory/answers | wc -l | tr -d ' '; BASE=$(git merge-base main HEAD); echo "pilot=$(git ls-files .factory/green-pilot | wc -l | tr -d ' ') of $(git ls-tree -r --name-only "$BASE" -- intake/green-pilot | wc -l | tr -d ' ') answers=$(git ls-files .factory/answers | wc -l | tr -d ' ') of $(git ls-tree -r --name-only "$BASE" -- intake/answers | wc -l | tr -d ' ')"`
  - THEN `0`, then `pilot=X of X answers=Y of Y`, with each pair equal (148 and 14 today).
  - Checked in a scratch clone: after `git mv` of both directories, `git diff --check` exits 0 with default settings, the `-M100% --diff-filter=AD` count is `0`, and with `-c diff.renames=false` seven files are flagged.
- **live-store-untouched** → REGRESSION (relabelled by the operator, 2026-10-03, before dispatch: an invariant, as in T-0012.2 and T-0012.5) (intermediate).
  - WHEN `git diff --name-only main...HEAD -- intake/state intake/.gitignore | wc -l | tr -d ' '`
  - THEN `0`.
- **role-prompt-text-unchanged**, **harness-files-in-repo**, **harness-history-carried** → REGRESSION. Same THEN as at T-0012.3 and T-0012.1.
- **docs-moved-and-split**, **changelog-moved-verbatim**, **design-text-kept**, **prompt-copies-moved-unchanged** → REGRESSION.
- **harness-suite-passes-after-uv-sync** → REGRESSION. The conftest's fixed `FACTORY_INSTANCE` must keep the suite off this repo's new `.factory/`.
- **green-harness-still-present** → REGRESSION.
- **whitespace (sub-ticket diff)** → REGRESSION. `git diff --check main...HEAD; echo "exit=$?"` gives `exit=0` with default rename detection.

Tests to change: none

Protected paths:
- infra `intake/**`: `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed. `intake/answers/` and `intake/green-pilot/` move out byte-identical. `intake/state/**` and `intake/.gitignore` are not changed.
- No `generated` or `reference_harness` writes. `credentials` is not read or written.

Out of scope:
- Moving `intake/state/` to `.factory/state/` and deleting `intake/harness/`. That is operator step 2, after close.
- Creating `~/dev/spec-factory-harness` (operator step 2).
- The end-to-end run (operator step 3).
- Any harness code.
- Design-doc text (F).
- Rewriting any record's content.
- Adding `.claude/agents/` to this repo.
- `intake/requests/` (untracked; operator step 2).

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
