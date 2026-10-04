Commit: 5f43cba12a208e095e48872471e4f6f2f9dc47f5 (branch `factory/T-0019.1`, base `1c5f6a7`)

## What I checked, in the role's order

1. **Test integrity.** `git diff --name-only main...HEAD` lists eight files, the exact set the sub-ticket declares; the only test file is the new `tests/factory/test_run_isolation.py`. No existing test, CI config, `AGENTS.md` or skill changed. The two agent prompts that changed (`factory/prompts/preamble.md`, `docs/prompts/00-preamble.md`) are the edit part A asks for.
2. **Correctness.** I re-ran every S1 acceptance scenario on this worktree, from its root after `uv sync --frozen`, with the parent's fixture GIVEN block written first and my shell's `HOME` set to a fresh temporary directory (`/private/var/folders/.../tmp.VrKcMNSIB1`). Results:
   - Triage probe: `fresh_home=yes real_home_untouched=yes cache=`. The probe wrote its file under a HOME other than mine, nothing landed in mine, and no `run_env` variable leaked in.
   - Planner and implementer inputs: `planner 1`, `implementer 1`. Each carries the section exactly once.
   - Gate commands wrapped: both wrapped forms printed, then `end`. Both gate commands reach the implementer wrapped.
   - `run_env` reaches the command: `fresh_home=yes real_home_untouched=yes cache=/tmp/t0019 cache`. A value with a space arrived intact.
   - `run_env` with HOME: stderr `run_env may not set HOME: the running-code wrapper sets it to a fresh temporary directory`, then `exit=2 input=absent`. `cli.py:1158-1161` turns `Refused` into exit 2, and `run_compose` (`cli.py:270-278`) writes `input.md` only after `compose` returns, so a refused `run_env` writes nothing.
   - Preamble rule in every copy and in the run's system prompt: `design.md 1 1 1`, `00-preamble.md 1 1 1`, `preamble.md 1 1 1`, `system-prompt.txt 1 1 1`.
   - Preamble block identity (awk/diff): `SAME`.
   - README: `1`, `1`, `1`. Design doc and template `run_env`: `docs/design.md:1`, `factory/instance.template.yaml:1`.
   - Changelog: `1` then `CONTIGUOUS`; entry 48 carries the S1 clause verbatim from parent E1.
   - `git diff --check main...HEAD`: exit 0.
   - Gate suite under a throwaway HOME, with `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR` pointed at uv's real directories so the venv built on managed CPython 3.12.13: `182 passed in 107.78s`, no failures. 171 on base plus the 11 new cases.
   - `ruff check factory/compose.py tests/factory/test_run_isolation.py`: `All checks passed!`.
   Read against the spec's text: the `RUNNING CODE` block sits after the protected-paths placeholder and before `GUARDRAIL PATHS` with one blank line each side (`docs/design.md:205-216`); B3's section text and B4's "exactly as written; each is already wrapped" match the parent word for word; B6's two edits to the Role-context paragraph match; the template comment (B5) says what the parent asks. `gate_commands` still replaces `{integration}` first and `wrap` is applied to its output (`compose.py:166`), so wrapping happens after replacement as B4 requires. `factory/instance.py` is untouched, as the placement note demands.
3. **Scope.** Nothing outside parts A, B1-B6, E1 (S1 clause), E2, E3, F1. `dev/build-harness.spec.md` untouched (E4).
4. **Silent behavior changes.** Every composed input gains the section and the reviewer's input, not only the implementer's and verifier's, now carries wrapped gate commands (`compose.py:157` covers all three build roles). Both are what the parent asks for ("every role"; "build-role inputs"). `compose` can now raise `Refused` on a bad `run_env`, which is the specified refusal. `gate_commands()` itself is unchanged and has no other caller (`grep -rn gate_commands factory bin` finds only `compose.py` and the template), so nothing else sees bare or wrapped commands differently.
5. **Security and data safety.** Values are quoted with `shlex.quote`, so a `run_env` value cannot break out of the wrapper. Names are checked against `[A-Za-z_][A-Za-z0-9_]*`, so a name cannot inject shell either. No secrets, no destructive operations.
6. **Protected paths.** All four touched protected paths are declared by the sub-ticket; listed under ESCALATIONS.
7. **Coding standard.** `run_env` and `wrap` are new, and no helper in `factory/` already does either (`grep -rn 'A-Za-z_\]\|shlex' factory` finds nothing outside `compose.py`); both use the standard library (`re`, `shlex`), rung 2. No `factory:` marker needed; the PR says "markers added: none". Lean already.
8. **PR description.** See the finding below.

## Findings

- [SHOULD-FIX] PR description: What changed: the first paragraph uses "roles", "the Nanobot instance" and "the harness composes" before glossing any of them; only "gate commands" is glossed → a reader at the gate who has not read the design doc cannot tell from the paragraph who ran the tests or what composes the input. One clause each would do: roles are the AI agents the factory runs a change through; the harness is the code that builds each role's input; an instance is a target repository's copy of the factory's config.

## Coding-standard pass

Lean already.

## Prior findings

None (round 1).

## Out-of-scope observations

- A `run_env` value that is a YAML list or mapping goes through `str()` and is exported as its Python repr (for example `X="['a', 'b']"`). The parent specifies `str(value)` and asks for no refusal, and the PR's Known gaps covers the null and boolean cases, but not this one. A later ticket could refuse non-scalar values.
- `.factory/context.md` on this instance still shows the bare test command; the preamble and the new section now tell roles to wrap it. The PR already notes this; it is an instance-file change.

STATUS: APPROVE
CONFIDENCE: high. Every S1 acceptance scenario and both gate commands ran on this worktree at `5f43cba` under a throwaway HOME with the results quoted above; the diff matches the parent's text part by part, and the one finding is prose.
ESCALATIONS: protected paths touched, all declared by the sub-ticket: harness `factory/compose.py`, `factory/instance.template.yaml`, `factory/prompts/preamble.md`; generated `docs/prompts/00-preamble.md`. The merge gate needs a human approval for these.
