Task (one sub-ticket, in this repository: the spec-factory harness, a Python CLI `bin/factory` with package `factory/`):

`factory ticket new --file F` imports a request file into the store. Request files may start with an optional YAML frontmatter header between a first line `---` and the next line `---` (keys such as `title:` and `labels:`). Today the header is never read: the ticket title comes from the first `# ` heading, else the file name. An unquoted title containing `: ` makes the header invalid YAML, and such files are imported silently.

Change `ticket new` so that:
- a valid frontmatter `title:` becomes the ticket title (otherwise the first `# ` heading, else the file name, as today);
- a header that is never closed, does not parse as YAML, or is not a key/value mapping is refused (exit 2, the word "frontmatter" in the error) before anything is written to the store.

Acceptance: `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_request_frontmatter.py` passes (5 tests; it is already in the checkout and must not be changed), and the existing `tests/factory/test_p0_cli.py` still passes.
