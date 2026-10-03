## T-0012.3 / Instances: resolver, `instance.yaml`, briefing, filled preamble, `init`, `paths`, agent pointer, workflows, test conftest

Parent: `intake/state/specs/T-0012/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: T-0012.1, T-0012.2

Parallel-safe: no, with T-0012.4 and T-0012.6, which depend on it and edit the same harness files or need them. It is parallel-safe with T-0012.5, which shares no files.

Scope: B.1–B.9, plus C.1 (the harness-revision function only, used by `init` and `paths`).
- The `<harness>` for C.1 is the running checkout.
- Delete A's interim `factory/config.yaml` and `factory/prompts/context.md`.
- `factory/prompts/preamble.md` becomes byte-identical to `docs/prompts/00-preamble.md`.
- New files: `factory/instance.template.yaml`, `factory/context.template.md`, `tests/factory/conftest.py`, `tests/factory/fixtures/instance/{instance.yaml,context.md}`, and new test files for B's behaviours.

Acceptance (first `uv sync --frozen`; then from the repo root):
- **harness-files-in-repo** → NEW [specs/harness-home]. THEN only `agents=6 green_only=0`.
- **role-prompt-text-unchanged** → NEW [specs/harness-home]. THEN `changed=0 of 14`.
- **init-creates-instance-in-throwaway-target** → NEW [specs/factory-instance]. THEN `init=0`, then `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1`.
- **store-command-from-subdirectory-uses-target-instance** → NEW [specs/factory-instance]. THEN `init=0`, then `new=0 tickets=[T-0001.yaml] harness_changes=0`.
- **command-outside-any-instance-refused** → NEW [specs/factory-instance]. THEN `exit=2 created=0 names_instance=1`.
- **factory-instance-override-from-elsewhere** → NEW [specs/factory-instance]. THEN `init=0`, then `found=1`.
- **composed-input-opens-with-instance-context** → NEW [specs/factory-instance]. THEN `init=0`, then `first=[CTX-MARKER for demo]`.
- **run-system-prompt-names-instance** → NEW [specs/factory-instance]. THEN `init=0`, then `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1`.
- **paths-name-harness-workflows-and-instance** → NEW [specs/factory-instance]. THEN `init=0`, then `True True True True`.
- **init-refusals-and-idempotence** → NEW (intermediate; B.5).
  - WHEN `H=$PWD; D=$(mktemp -d); (cd $D && $H/bin/factory init --repo-name x >/dev/null 2>&1; echo "outside_git=$?"); T=$(mktemp -d); git -C $T init -q -b main && git -C $T -c user.name=t -c user.email=t@t commit -q --allow-empty -m init && cd $T && $H/bin/factory init >/dev/null 2>&1; echo "no_name=$?"; $H/bin/factory init --repo-name demo >/dev/null 2>&1; a=$(find .factory .claude -type f | sort | xargs cksum | cksum); $H/bin/factory init >/dev/null 2>&1; echo "again=$? same=$([ "$a" = "$(find .factory .claude -type f | sort | xargs cksum | cksum)" ] && echo yes || echo no)"`
  - THEN `outside_git=2`, then `no_name=2`, then `again=0 same=yes`.
- **agent-pointer-replaced** → NEW (intermediate; B.7).
  - WHEN ``for f in triage spec-writer spec-critic planner; do echo "$f old=$(grep -c 'factory/prompts/preamble.md' agents/factory-$f.md) new=$(grep -cF 'Read `system-prompt.txt` in the run directory that holds your input file before anything else; its preamble is the top of your system prompt.' agents/factory-$f.md)"; done``
  - THEN four lines, each ending `old=0 new=1`.
  - The rest of each file is covered by role-prompt-text-unchanged.
- **workflows-take-instance** → NEW (intermediate; B.8; structural only).
  - WHEN `for w in intake build; do echo "$w $(grep -c FACTORY_INSTANCE factory/workflows/$w.js)"; done`
  - THEN each count ≥ 1.
  - The workflows' behaviour is exercised end to end only by operator step 3 after close. Say so in the PR rather than claiming more.
- **no-old-paths, documents and harness** → NEW (intermediate for no-old-paths-in-live-files). `.factory/*` arrives in T-0012.6.
  - WHEN the T-0012.2 intermediate grep with pathspec `-- README.md docs dev agents factory`.
  - THEN `exit=1`.
- **harness-history-carried** → REGRESSION. THEN `0`.
- **harness-suite-passes-after-uv-sync** → REGRESSION. THEN `sync=0` and `N passed`, N ≥ 70, no `failed`/`error`. This now includes the new B test files, run through the new conftest and fixture.
- **docs-moved-and-split**, **prompt-copies-moved-unchanged** → REGRESSION. Same THEN as at T-0012.2.
- **green-harness-still-present** → REGRESSION.
- **whitespace (sub-ticket diff)** → REGRESSION. `exit=0`.

Tests to change: none.
- Existing files under `tests/factory/` stay byte-identical. The new `conftest.py` and the fixture instance change which config they run with (parent Risk).
- Check before merge: every imported test still runs against a throwaway store. `FACTORY_STATE` is set in `test_p0_cli.py`, `test_results_commit.py`, `test_shepherd.py`, `test_spec_store.py` and `test_subtickets.py`. `test_killed_checker.py` uses `test_shepherd`'s fixtures.

Protected paths: none of instance B's classes are written. `docs/prompts/00-preamble.md` is read only. Guardrails touched (declared in the parent's Risk):
- agent prompts: four `agents/` pointer lines, and `factory/prompts/preamble.md` becoming the design doc's block;
- tests: new conftest, fixture and test files.

Out of scope:
- Lock enforcement, `--accept-harness`, and the dirty-harness refusal (C.2–C.5).
- Instance B's `.factory/` (E).
- Any change to the seven role prompts.
- Changing the role text of the agent files.
- `factory render`.

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
