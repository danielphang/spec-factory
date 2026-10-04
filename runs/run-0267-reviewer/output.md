Commit: fb72f7a7284a3208150c72ea20fe31299c9fdd4e (branch `factory/T-0025.1`, base and merge-base `0b1abad474cb9c583ed8445fc33617f9f0bdc37b`; five commits, `fb72f7a` new since round 1)

## What I checked and how

Round 2. I read the round-1 findings, the verifier's round-1 report, the human ruling and the PR description, then reviewed the worktree at `fb72f7a`, concentrating on the lines changed since `d001090` (`git diff 878c68b...HEAD --stat`: `factory/cli.py` 18 lines, `factory/gitops.py` 14, `tests/factory/test_store_branch.py` +42, `README.md` 2).

1. **Test integrity.** `tests/factory/test_live_store_guard.py` is unchanged since round 1; the only existing-test edit on the branch is still the two `init` iterations the human ruling allows. The three new test cases are in the new file `test_store_branch.py`. Nothing weakened.
2. **Gate commands**, from the worktree through the HOME wrapper: `git diff --check main...HEAD` printed `exit=0`. `uv run --frozen pytest -q -p no:cacheprovider tests/factory` with `TMPDIR` on a fresh `/tmp/t0025-rev2-suite.*` directory printed `283 passed in 287.81s`: the 280 of round 1 plus this round's three cases.
3. **Acceptance.** I re-ran the three WHENs that exercise the changed code, verbatim under `bash` through the wrapper (`scratch/acc.sh`): `branch=factory-store seen_by_main=0`; `exit=0 branch=factory-store restored=1`; `exit=2 instance=none names_path=1`. The documents did not change this round, so the document scenarios stand as round 1 and the verifier recorded them.
4. **Probes** (`scratch/probes.sh`, throwaway repos, throwaway HOME, git 2.54.0):
   - `git for-each-ref 'refs/remotes/*/factory-store'` over refs `origin/factory-store`, `origin/x/factory-store`, `a/b/factory-store`, `nas/factory-store`, `origin/factory-storex` printed only `refs/remotes/nas/factory-store refs/remotes/origin/factory-store`: `*` is one path segment, so the round-1 defect (a namespaced code branch taken for the store) is closed by the pattern alone.
   - `git symbolic-ref -q HEAD` on an unborn `factory-store` printed `refs/heads/factory-store` with exit 0, so A.1.1 still holds for an unborn branch after the move to `gitops.git`.
   - With a tag `factory-store` beside the branch, `symbolic-ref --short HEAD` printed `heads/factory-store` while the full form printed `refs/heads/factory-store`. The implementer's reason for keeping the full-ref comparison in A.1.1, instead of my round-1 suggestion `_head_branch(top) == STORE_BRANCH`, is correct. Accepted.
   - A clone whose only remote is named `a/b` (`git clone -o a/b`) and carries the pushed store: `init` printed `exit=0 upstream=none restored=1`, a new orphan store beside the pushed one. This is the Known gap the description declares; the spec's A.3.2 gives this exact pattern, so it is spec-conformant and not a finding (Out-of-scope observations).
5. **Correctness of the changed lines.** The six former `subprocess.run` git calls now go through `gitops.git(..., check=False)`, whose stripped stdout is empty in exactly the cases the old code tested the return code for (`factory/gitops.py:31-35`). The unborn-branch fallback at `factory/cli.py:959-962` consults `FACTORY_INTEGRATION_BRANCH`, then `cfg["integration_branch"]`, then `_head_branch`, which keeps `gitops.integration_branch`'s precedence (`factory/gitops.py:22-28`) and leaves that function's four other callers untouched, as the sub-ticket requires for `merge_cmd`.
6. **Scope and protected paths.** No new file outside the sub-ticket's list. `factory/cli.py` and `factory/gitops.py` are declared by the sub-ticket and the parent's Risk; listed under ESCALATIONS.
7. **PR description.** What changed names each fix in words, glosses store, instance, integration branch, store branch, git worktree and unborn branch at first use, states "factory: markers added: none" and names `init_cmd`'s one caller. Known gaps declares the slash-remote limit and the repeated precedence check. Meets the standard.

## Findings

[SHOULD-FIX] stdlib: tests/factory/test_store_branch.py:177: `subprocess.run(["rm", "-rf", str(state(t))], check=True)` shells out for what `shutil.rmtree` does; it is the only such call in the suite, and `factory/store.py` already uses `rmtree` → a test that fails here reports a `CalledProcessError` from `rm` rather than the Python error naming the path, and the test depends on a shell tool for nothing. Replace with `shutil.rmtree(state(t))`.

net: 0 lines possible (the replacement is line-neutral once `shutil` is imported).

## Prior findings

- [BLOCKING] reuse (`_refuse_inside_store`, `_head_branch`, `_store_hint`, `_add_store_checkout`, `gitops.common_dir`, `gitops.last_tracked`) → RESOLVED at `fb72f7a`. All six calls go through `gitops.git(check=False)`; the one departure from my literal suggestion (A.1.1 keeps the full ref) is right, as my tag probe shows.
- [SHOULD-FIX] `remote_branches` matched any ref ending in `/factory-store` → RESOLVED. The pattern `refs/remotes/*/factory-store` is passed to `for-each-ref` and the `endswith` filter is gone; the parametrized test covers both the decoy-only and decoy-and-store cases, and my probe confirms the pattern's segment behaviour.
- [SHOULD-FIX] PR description missing the `factory:` marker statement and the callers → RESOLVED, both sentences present.
- [NIT] unborn HEAD on an existing instance with no `integration_branch` → RESOLVED, with a test (`test_an_existing_instance_on_an_unborn_branch_counts_as_never_tracked`) that failed before the fix for the reason the finding gave.

## Out-of-scope observations

- A remote whose name contains a slash (for example `a/b`) is not seen by `refs/remotes/*/factory-store`, so `init` on such a clone starts a new orphan store beside the pushed one (probe 4). The spec's A.3.2 names this pattern and the description declares the gap. An exact match against `git remote`'s names would close it; that is a spec change, for T-0025.2 or a follow-up, not this sub-ticket.
- `gitops.integration_branch` still raises on an unborn HEAD for its other callers, as round 1 noted. Not this sub-ticket's.
- README lines still giving `.factory/state/` as the live store's location are T-0025.2's, per the sub-ticket's Out of scope.

STATUS: APPROVE
CONFIDENCE: high. Both gates pass on `fb72f7a` (`exit=0`; `283 passed`), the three acceptance WHENs on the changed code print their THEN, every round-1 finding is closed by a line I read or a probe I ran, and the one remaining finding is a SHOULD-FIX in a new test file.
ESCALATIONS: protected paths touched, as the sub-ticket and the parent's Risk declare: harness (`factory/cli.py`, `factory/gitops.py`). The harness is the code that runs every ticket, so the merge gate requires a human approval for these two files.
