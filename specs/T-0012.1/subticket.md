## T-0012.1 / Import the harness from green with its history, plus `pyproject.toml` and the interim overlay

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: none

Parallel-safe: yes, with T-0012.2 and T-0012.5. Its files are `factory/**`, `bin/factory`, `tests/factory/**`, `agents/**`, `pyproject.toml`, `uv.lock` and root `.gitignore`. Its siblings touch none of them. It reads `intake/instance/*` for the overlay and writes nothing under `intake/`. Not parallel with .3, .4 or .6, which depend on it.

Scope: A.1–A.6.
- Run `git filter-repo` only in a fresh scratch clone, never in `~/dev/nanobot-upstream`.
- Bring the import in with `git pull --no-rebase --allow-unrelated-histories --no-edit <scratch>/g HEAD`.
- If `main` moves while this is in flight, update the branch by merging `main` in, not by rebasing. A rebase would linearise the imported history.

Acceptance (run from the branch checkout at the repo root):
- **harness-history-carried** → NEW [specs/harness-home]. THEN `0`.
- **harness-suite-passes-after-uv-sync** → NEW [specs/harness-home]. THEN `sync=0`, then `N passed in …`, N ≥ 70, no `failed`/`error`.
- **harness-files-in-repo, interim form** → NEW (intermediate). WHEN the parent's harness-files-in-repo command. THEN it prints only `agents=6 green_only=2`. The 2 are the interim overlay files `factory/config.yaml` and `factory/prompts/context.md`; T-0012.3 deletes them and turns this into the parent's `green_only=0`.
- **role-prompt-text-unchanged, interim form** → NEW (intermediate). WHEN the parent's role-prompt-text-unchanged command. THEN `changed=1 of 14`. The 1 is the overlay preamble, which T-0012.3 replaces.
- **import-byte-identical** → NEW (intermediate). Every imported file except the three overlay paths is byte-identical to green at G.
  - WHEN `G=$(git -C ~/dev/nanobot-upstream log -1 --format=%H --grep='^Merge factory/T-0002.1' feat/lionbot-v3); c=0; n=0; for f in $(git -C ~/dev/nanobot-upstream ls-tree -r --name-only "$G" -- factory bin/factory tests/factory | grep -v -x -e factory/config.yaml -e factory/prompts/context.md -e factory/prompts/preamble.md); do n=$((n+1)); git -C ~/dev/nanobot-upstream show "$G:$f" | cmp -s - "$f" 2>/dev/null || c=$((c+1)); done; for f in $(git -C ~/dev/nanobot-upstream ls-tree --name-only "$G" -- .claude/agents/ | grep '/factory-'); do n=$((n+1)); git -C ~/dev/nanobot-upstream show "$G:$f" | cmp -s - "agents/${f##*/}" 2>/dev/null || c=$((c+1)); done; echo "differ=$c of $n"`
  - THEN `differ=0 of 69`. Today it prints `differ=69 of 69`; I ran it.
- **overlay-is-this-repo's-instance** → NEW (intermediate).
  - WHEN `cmp -s factory/prompts/context.md intake/instance/context.md && cmp -s factory/prompts/preamble.md intake/instance/preamble.md && echo overlay=same; uv run --frozen python -c "import yaml; c=yaml.safe_load(open('factory/config.yaml')); print(c['state_dir'], c['environment_files'])"; test -e scripts/full_suite_gate.py && echo gate_script_present`
  - THEN `overlay=same`, then `intake/state ['uv.lock']`, and no `gate_script_present`.
- **project-files** → NEW (intermediate).
  - WHEN `uv lock --check >/dev/null 2>&1; echo "lock=$?"; for s in .venv/ __pycache__/ .pytest_cache/; do grep -qxF "$s" .gitignore || echo "missing $s"; done`
  - THEN only `lock=0`.
- **cut-anchor-still-valid** → NEW (intermediate; Risk, "Fragile acceptance anchor").
  - WHEN `G=$(git -C ~/dev/nanobot-upstream log -1 --format=%H --grep='^Merge factory/T-0002.1' feat/lionbot-v3); git -C ~/dev/nanobot-upstream log --oneline "$G"..feat/lionbot-v3 -- factory/prompts .claude/agents | wc -l | tr -d ' '`
  - THEN `0`. Anything else means green changed a role prompt after G: escalate instead of merging. Today it prints `0` (G is green's HEAD, `7c0a035`).
- **green-harness-still-present** → REGRESSION [specs/self-instance]. THEN `green keeps its harness`. In addition, `git -C ~/dev/nanobot-upstream status --porcelain -- factory bin/factory tests/factory .claude/agents | wc -l | tr -d ' '` prints `0`.
- **whitespace (sub-ticket diff)** → REGRESSION (intermediate for whitespace-clean). WHEN `git diff --check main...HEAD; echo "exit=$?"`. THEN only `exit=0`. Checked: green's imported paths at G have no whitespace errors against the empty tree (`git diff --check <empty-tree> G -- factory bin/factory tests/factory '.claude/agents/factory-*'` exits 0).

Tests to change: none. `tests/factory/**` arrives as new files, byte-identical to green.

Protected paths:
- reference_harness `~/dev/nanobot-upstream/**`: read only. It is cloned into a scratch directory, and acceptance reads it with `git log`, `show` and `cat-file`.
- Guardrails (declared in the parent's Risk): agent prompts (`agents/factory-*.md` and `factory/prompts/*.md` arrive byte-identical) and tests (new files).

Out of scope:
- Any behaviour change, including instance discovery, `init`, `paths` and the lock (B, C).
- Deleting the overlay (B).
- Moving documents (D).
- Writing `.factory/` (E).
- Editing `intake/**`.
- Changing any imported file beyond the three overlay paths.
- Adding the suite to the live gate config. That is operator step 1, and `intake/harness/` is live infra.

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
