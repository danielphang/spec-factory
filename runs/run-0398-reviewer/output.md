Commit: da50576fd4215aa31d4d8091e089c8f50cb791e5 (branch `factory/T-0031.2`, base `2bd9969`), round 1.

## How I checked
I read the whole diff against the sub-ticket and the parent spec v3, then confirmed in the worktree the names the new code relies on: `Refused` is imported in `factory/cli.py:23`, `subprocess` at line 16, `store.write_text` creates the parent directory (`factory/store.py:87-89`), `gitops.remove_worktree(repo, path)` exists (`factory/gitops.py:59`), `requires-python = ">=3.11"` so `str | None` is valid, and `run_start` writes `meta.yaml`, creates `scratch/` and appends to `in_flight` only after `_start_build_run` returns (`factory/cli.py:225-239`), so a refusal inside it records nothing. I ran the spec's prefix once under `sh` with `VIRTUAL_ENV=/v PATH=/v/bin:/usr/bin:/bin`: it printed `PATH=/usr/bin:/bin ve=unset`. I did not run the suite or the gates; the verifier does.

## 1. Test integrity
- `tests/factory/test_run_isolation.py:22-23`: only the `WRAP` constant changed, and it is byte-for-byte the replacement the spec's Tests to change gives. `SECTION` and every assertion unchanged.
- `tests/factory/test_gate_paths.py:217-218`: only the `want` line changed, byte-for-byte the spec's replacement. The `if UNSCOPED in gate else ""` tail, the other two cases and the assertions are unchanged.
- No other existing test file is in the diff (`git diff --stat` lists only those two plus the new `tests/factory/test_environment_sync.py`).
- The new file's assertions are specific: exact wrapper output, the exact input line, exit 2, one stderr line, the forbidden-character set, log contents, directory contents. Nothing is skipped, swallowed or hard-coded to output.

## 2. Correctness against the spec
- A: `factory/compose.py:177-178` holds the spec's prefix verbatim (the Python escape `\'\\n\'` is `'\n'` in the string, so `tr` receives backslash-n), as a module constant with a comment; `wrap()` at 181-187 emits `(<prefix>export HOME=...{exports}; {command})`. No backtick. Both callers (`compose.py:201` Running code, `compose.py:368` gate commands) and the new `cli.py:405` pick it up through `wrap()`.
- B: `compose.environment_sync` (164-172): None for absent/null, the string for a non-empty string, `store.Refused` naming `environment_sync` otherwise. Template key at `instance.template.yaml:38-41` with the comment the spec asks for.
- C: the key is read at `cli.py:367` before any checkout, and also in `run_start` at 218 before the run id is reserved. The sync runs after `copy_environment_files` in both branches (382, 393), so the parent-close verifier is covered. Failure path at 408-412: log with command, exit code, full stdout and stderr; checker checkout removed; one-line `Refused` with no command text or output. The run directory is left holding only the log, which the spec's Risk accepts.
- D: `compose.py:372-375` appends the spec's line word for word, after the SKIPPED lines and before `parts.append(where)`, only when `meta["environment_sync"]` is set.
- E/F: tests and documents as the spec lists them; changelog entry 66 is contiguous and names all four terms.
- Declared deviations in Known gaps (refusal also in `run_start`; a sub-item under I.3 instead of renumbering I.4-I.6) are sound and smaller than the alternatives. Neither changes a scenario's outcome.

## 3. Scope
Every changed file is one the sub-ticket names. Nothing under `docs/prompts/`, `factory/prompts/`, `factory/workflows/`, `.factory/`, `bin/`, `agents/`, `pyproject.toml` or `uv.lock`.

## 4. Silent behavior changes
Only the one the spec asks for: every wrapped command on every instance now carries the prefix, and an instance whose commands relied on an activated environment loses it inside the wrapper. The spec's Risk names both.

## 5. Security and data safety
The sync command is operator-written config, run through `sh -c` by design; its output is captured, never relayed into the refusal, so the build workflow's `"$reason"` expansion gets no `$` or backtick from it. `remove_worktree` is called only on the checkout `_start_build_run` just made under `runs/<id>/wt`.

## 6. Protected paths
`factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml`: all three declared by the sub-ticket and by the spec's Risk line. Listed under ESCALATIONS for the record.

## 7. Coding standard
`_sync_environment` is one new function for one new behaviour with two callers; `environment_sync()` sits beside `run_env()` and follows its shape. No helper this repo already has covers either. Lean already.

## 8. PR description
What changed says in words what each part does and glosses the wrapper, the build roles and the key at first use. Known gaps lists each deviation with its reason and the `factory:` marker count. Readable at the gate as it stands.

Findings:
- [NIT] factory/cli.py:410: the log is `f"...--- stdout\n{cp.stdout}--- stderr\n{cp.stderr}"`, so when the sync's stdout does not end in a newline its last line and the `--- stderr` marker share a line (`'--- stdout\nabc--- stderr\n'` from a probe). The content is all there, which is what the spec requires; the operator reading the log just sees one run-together line. A `{cp.stdout.rstrip('\n')}\n` or a leading `\n` on the marker fixes it.
- [NIT] factory/cli.py:405: `text=True` with the default strict decoding. A sync whose output holds a byte that is not UTF-8 makes `subprocess.run` raise `UnicodeDecodeError`, so run start dies with a traceback instead of the one-line refusal, and no log is written. uv's output is UTF-8, so this is unlikely in practice; `errors="replace"` would close it.

net: Lean already.

Prior findings: none (round 1).

Out-of-scope observations:
- The spec's prefix leaves `PATH` empty when `$VIRTUAL_ENV/bin` was its only entry (grep then prints nothing). The prefix is the spec's verbatim text and no real setup has a one-entry `PATH`; noted only so the Risk line's "exact entry" claim has its edge case on record.
- The build spec addition is a sub-item of I.3 rather than a numbered item after it; the implementer's reason (four cross-references to I.4-I.6) holds, and the acceptance grep passes either way.

STATUS: APPROVE
CONFIDENCE: high. Every spec part maps to a cited line in the diff; the two test edits are the spec's own text; the names the new code depends on were confirmed in the worktree; the two findings are cosmetic and do not change what the scenarios check.
ESCALATIONS: protected paths touched, all declared by the sub-ticket and the spec's Risk line: `factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml`.
