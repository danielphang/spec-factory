## Problem

The harness is the program that enforces the factory's rules: which state a ticket may move to,
when a merge is allowed, and who may write the store, the factory's on-disk record of tickets and
runs. Almost all of its commands live in one file, `factory/cli.py`. That file is 2,020 of the
harness's 5,073 lines of Python.

The file mixes five jobs that have little to do with each other:

| Job | What it does |
|---|---|
| Ticket and run bookkeeping | creates tickets, moves them between states, starts and finishes role runs (one agent working one step of a ticket) |
| Spec-drift checks | before a build agent starts, refuse when the code has moved away from what the approved spec assumed |
| Setup | prepare a repository for the factory and create or move its store |
| Gates | record review and verification results, and refuse a merge or a ticket close that they do not support |
| Human decisions | the commands a person uses to approve a spec, send it back, or rule on a stopped ticket |

This costs the agents that build harness changes, and the people who review those changes. An
agent asked to change one gate reads the whole 2,020-line file into its context. A reviewer of a
merge-gate change has to find it among setup and bookkeeping code. Every harness ticket that
touches a refusal, a gate or a human command edits this one file.

This change moves the code into one module per job and leaves `factory/cli.py` with the command
parser, the entry point and the bookkeeping commands. Nothing a command does changes: every
refusal message, exit code, logged event and printed result stays the same. The change saves no
lines. Its gain is that each job can be found, read and changed on its own.

## Evidence

All figures are from `main` at `6203096`.

- `wc -l factory/*.py` gives 2020 for `factory/cli.py` and 5073 in total.
- The largest functions in `factory/cli.py`, from an `ast` walk of the file: `build_parser`
  (lines 1764-1953, 190 lines), `resolve` (1144-1252, 109), `store_migrate` (1519-1610, 92),
  `init_cmd` (1400-1479, 80) and `spec_amend` (592-659, 68).
- What imports the CLI module. `grep -lE '^\s*(from factory\.cli import|import factory\.cli|from
  factory import ([^#]*, )?cli\b)' factory/*.py` lists `factory/__main__.py`, `factory/drive.py`
  and `factory/stats.py`. `drive.py` uses only `cli.main` (`drive.py:60`). `stats.py:23` imports
  `ROLES`. `__main__.py:1` imports `main`.
- What the tests use in-process. `tests/factory/clean_harness_cli.py:25-28` and
  `tests/factory/test_store_migrate.py:155-164` import `factory.cli` and call only `cli.main`. No
  test reads `factory/cli.py` as a file. Two tests replace a function before they call `cli.main`:
  - `clean_harness_cli.py:27` replaces `instance.harness_changes`. Its one caller,
    `instance.guard`, is in `factory/instance.py` and does not move.
  - `test_store_migrate.py:149-163` (`ALTERING_COPY`) replaces the global `shutil.copy2`. Its one
    harness caller is `factory/cli.py:1586`, `shutil.copy2(old / f, new / f,
    follow_symlinks=False)`, inside `store_migrate`.
- Which definitions call which, from an `ast` walk of `factory/cli.py`:
  - The drift checks (lines 249-370) use no other definition of the file.
  - `run_start` (206-246) calls `_check_drift` and `_check_sibling_tests`.
  - `ticket_transition` (157-176) calls `_parent_close_verified` (1711-1725).
  - `resolve` calls `_branch_tip` (946-951) and `undeclared_protected` (925-943).
  - `init_cmd` and `spec_amend` call `fence` (1970-1988). `store_migrate` calls `_in_flight`
    (1964-1967).
  - `out` (30-31) is called by nearly every command. `_rel` (34-35) is called by both the
    bookkeeping commands and the human-decision commands. `_add_spec_version` (557-567) is called
    by `spec_add`, `spec_amend` and `approve_spec`.
- `fence` cannot move into `factory/instance.py` unchanged. Its body calls
  `instance.is_own_store`, `instance.own_state_root` and `instance.caller_cwd`
  (`cli.py:1976-1977`), which inside `instance.py` would have to lose their `instance.` prefix.
- `stats_cmd` (1627-1648) carries the comment `# local: stats imports ROLES from here`. The
  comment is true only while the function sits in `factory/cli.py`.
- Current-truth checks that count text in `factory/cli.py`, in
  `openspec/specs/harness-code/spec.md`, lines 17, 45, 49, 53, 57 and 65. The prototype below
  shows that three of them fail after a split, because the counted text moves:

  | Line | Counts | Base | Prototype, old form | Prototype, all six modules |
  |---|---|---|---|---|
  | 17 | `prompt_name`, in-flight refusal, `store.ensure_gitignore(root)` | `0 2 2` | `0 2 1` | `0 2 2` |
  | 53 | `"ticket.transition"` in the CLI, then in `store.py` | `1 1` | `0 1` | `1 1` |
  | 65 | record copies, `"results.superseded"`, planner-run refusal, `specstore.applies` | `0 1 1 1` | `0 0 1 0` | `0 1 1 1` |

  The other three (lines 45, 49, 57) still print their expected `0`, but no longer read the
  moved code.
- Docs that name `factory/cli.py`:
  - `README.md:1170` (the `ticket transition` guards) stays true.
  - `README.md:1171` names `ticket_join`, `merge_cmd` and `archive_cmd`. These move.
  - `README.md:1173` (`build_parser()`) stays true.
  - `docs/principles.md:106-107` names the guards of `ticket transition`, `run start` and `merge`.
    `merge` moves.
  - `docs/principles.md:164` (`run finish`) stays true.
  - `dev/build-harness.spec.md` and `dev/build-harness.plan.md` name `factory/cli.py` as the
    record of how the harness was first built. They are history, not a map of the current code.
- `pyproject.toml` sets `[tool.uv] package = false`. No build tool reads a module named
  `factory/setup.py`.
- Prototype. I cloned `main` into this run's scratch directory and moved the definitions listed
  under Proposed change with a script. Every definition was copied byte for byte. Each new module
  got a one-line docstring and the imports its definitions need.
  - `wc -l`: `factory/cli.py` 882, `common.py` 66, `drift.py` 134, `gates.py` 325, `human.py`
    324, `setup.py` 349.
  - Without `ticket_head` in `gates.py`, `factory/cli.py` would end at about 906 lines: 882, plus
    the function's 22 lines and two blank lines.
  - `uvx ruff check --select F factory` printed `All checks passed!`, as it does on base.
  - Each new module imported first in a fresh interpreter, then `import factory.cli,
    factory.drive, factory.stats`, all succeeded.
  - The harness suite, run in three groups because one run exceeds ten minutes: 575 passed and 1
    failed. The failure was
    `test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`.
    It asserts the order in which two concurrent checker runs are seen. It passed on two reruns of
    its file, on both the prototype and base.
  - The definition check in the scenario "Every definition keeps its exact text, and the split
    adds at most 100 lines" printed:

    | Where | Output |
    |---|---|
    | base | `pairs=0 added=0 removed=0 lines=0` |
    | after the prototype merged as `Merge factory/T-0047.1` | `pairs=1 added=0 removed=0 lines=60` |
    | the same, plus one changed refusal text | `pairs=2 added=1 removed=1 lines=60`, then the changed function's first line, twice |

## Root cause

`factory/cli.py` was the first module of the harness, and each build part added its commands to
it. Its docstring still reads "P0 subset of the build-harness spec, part B/K".
`dev/build-harness.plan.md` records that every sub-ticket of that build edited it. Nothing has
moved commands out since. The file is organised only by `# -----` section comments.

## Out of scope

- Any change to what a command does: its refusals, exit codes, events, records and printed JSON.
- The difference between `merge_cmd`, under which a closed sibling releases its dependants, and
  `ready_implementers`, under which a sibling must be merged. This is filed separately as a
  question.
- Retiring the no-spec-store (P0) mode, and deleting `store migrate` (#83 part D).
- Renaming any definition, including making an underscored helper public.
- Moving the ticket, run, spec and plan commands, which stay in `factory/cli.py`.
- Any change under `tests/`.
- `dev/build-harness.spec.md` and `dev/build-harness.plan.md`, which are build history.

## Open questions

none

## Decisions

1. The command-line code becomes six modules. `factory/cli.py` keeps the parser, the entry point,
   the role lists and the ticket, run, spec and plan commands. The five new modules are:
   - `factory/drift.py` for the spec-drift checks;
   - `factory/setup.py` for `init`, `store migrate` and `paths`;
   - `factory/gates.py` for results, the merge gate, join, the parent check and archive;
   - `factory/human.py` for `approve-spec`, `request-changes`, `resolve`, `decision add` and
     `spec amend`;
   - `factory/common.py` for the helpers more than one module calls, and the live-store fence.
     The fence refuses a write to the live store from inside a role run.

   The names follow the request. `setup.py` is kept because no build tool reads it (Evidence).
2. `fence` and `_in_flight` go to `factory/common.py`. Rejected: `factory/instance.py`, where the
   body of `fence` would change (Evidence). Also rejected: a sixth module, which would add a
   header for two functions.
3. `ticket_head` goes to `factory/gates.py`. It reports the commit that the checkers review and
   verify, and the gates record their results against that commit. Without it, `factory/cli.py`
   ends at about 906 lines (Evidence).
4. `stats_cmd` stays in `factory/cli.py`, where its comment about `ROLES` is true. `paths_cmd`
   moves to `setup.py`, as the request asks.
5. Each module imports what it uses by name, for example `from factory.common import _rel, out`.
   No function body changes, so a moved function reads exactly as it did. Rejected: importing the
   module and qualifying each call, such as `common.out(...)`, which edits nearly every body.
   Underscored names keep their underscore when another module imports them.
6. `factory/setup.py` uses `import shutil` and keeps calling `shutil.copy2` through the module.
   The test that replaces `shutil.copy2` therefore still reaches the moved code.
7. The rule that a move is not a rewrite is checked by machine. Across this change, every
   top-level function, class and assignment of `factory/*.py` must keep its exact source text.
   The comparison covers each of this ticket's merges and the checked-out branch, as T-0045's
   suite checks do. Other tickets' changes are therefore never counted.
8. The request's "within ±50 total Python lines" becomes "at most 100 lines added". The
   prototype, with one-line docstrings, added 60 lines: five module headers of imports, less the
   imports `factory/cli.py` no longer needs. With rule 7 in place, the line bound only limits
   header growth. Rejected: ±50, which would push the implementer to cut docstrings.
9. Acceptance names modules, functions and constants. The subject of this ticket is where code
   lives, so those names are the behaviour checked. T-0045 decided the same for the test suite's
   helpers.
10. The six harness-code checks that count text in `factory/cli.py` now count it across
    `factory/cli.py` and the five new modules (Evidence). The expected numbers do not change.
    Rejected: leaving them, which fails three and empties three.
11. Docs: `README.md:1171` and `docs/principles.md:106-107` name `factory/gates.py` for the moved
    gate commands. The README status date moves to the day of the change, as "Maintaining this
    page" asks. Every other doc line that names `factory/cli.py` stays true and is left alone.
12. Standing: no harness module imports `factory.cli` except the entry point (`__main__.py`), the
    driver (`drive.py`) and the stats report (`stats.py`). A command that a new module needs comes
    from that module's own imports. This states the request's rule with the third importer, which
    the request left out.

## Risk

Blast radius: every command of the harness.

- A moved function whose module lacks an import fails only when the function runs. `ruff`'s
  undefined-name check (F821) and the suite catch this.
- An import cycle fails as soon as a module loads. Each new module is imported first in a fresh
  interpreter, and none imports `factory.cli`.
- The suite replaces two functions while it runs (Evidence). Neither patch point moves out of
  reach.
- Every part edits `factory/cli.py`, so the parts cannot be built in parallel.
- Any other ticket that edits `factory/cli.py` while this one is in flight will conflict with it.
- The running factory is unaffected until the operator upgrades the runtime.

Protected paths: `factory/cli.py`, `factory/common.py`, `factory/drift.py`, `factory/gates.py`, `factory/human.py`, `factory/setup.py`

## Operator steps

After the last part merges, the running factory picks up the split at the next runtime upgrade,
accepted with `--accept-harness` as usual. No other step is needed.

