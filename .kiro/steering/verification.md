---
inclusion: auto
name: verification
description: Use when verifying a change, running tests or linters, preparing a release, or reporting whether work is complete.
---
# Verification Rules

Before running commands, inspect the repository's declared Python version, dependencies, and CI workflow. Prefer the same checks used by CI.

For each change:
1. Add or update a regression test for the behavior changed.
2. Run the narrowest relevant test first, then the wider suite available in this repository.
3. Run lint/type checks only if configured or clearly document a proposed new tool.
4. Review `git diff --check` and inspect the complete diff for accidental edits, secrets, generated files, and unrelated changes.
5. Report exact commands, pass/fail status, and anything not tested (for example, physical hardware).

If tests cannot run, explain why and provide the next reproducible command. Never label unexecuted checks as passed.
