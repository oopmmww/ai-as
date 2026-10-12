---
name: release-check
description: Perform a pre-merge or pre-release verification of an AIAS change. Use after implementation, before merging, or when asked whether a change is ready.
---
# Release / Merge Check

1. Confirm the task's acceptance criteria and inspect the final diff.
2. Check `git diff --check`, accidental file changes, generated artifacts, secrets, and local configuration/log files.
3. Inspect the repository's actual CI workflow and run the existing relevant test/lint commands.
4. Confirm a regression test exists for each bug fix and tests cover failure paths proportionately.
5. Check docs/config samples are updated if interfaces or configuration changed.
6. Review thread/resource lifecycle and backward compatibility for the changed modules.
7. List unresolved failures, skipped tests, untested physical hardware, and rollback concerns.

Output one of: **Ready**, **Ready with caveats**, or **Not ready**, with evidence. Do not call work ready if a required check failed or was never run; distinguish missing tooling from a test failure. Never claim success on the basis of code inspection alone.
