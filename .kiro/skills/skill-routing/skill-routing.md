---
inclusion: always
---

# AIAS — Persistent Skill Routing Rules

## Purpose
Apply these rules to every coding, debugging, review, testing, refactoring, and documentation task in this repository. Treat this file as persistent project guidance; do not require the user to repeat these instructions in chat.

## Before working
1. Inspect the repository state and relevant files before proposing or editing code. Preserve all existing user changes.
2. Discover the available skills in `.kiro/skills/`. Check each relevant `SKILL.md` frontmatter (`name` and `description`) and follow the full instructions of the selected skill before performing the task.
3. Select skills based on task intent; use more than one only when their responsibilities are complementary. Prefer existing skills over creating new ones.
4. At the start of the response, briefly name the selected skill(s) and why they apply. If no relevant skill exists, say so briefly and continue using repository standards.
5. For a small, isolated change, avoid unnecessary specifications or large refactors. For multi-file, architectural, or behavior-changing work, use the spec-first workflow before implementation.

## Skill routing
- Architecture, boundaries, dependencies, concurrency, startup/shutdown, or thread safety: `architecture-review`.
- Reproducing a bug, tracing root cause, or investigating regression: `systematic-debugging`.
- Python code changes, unit tests, test quality, or test failures: `python-testing-quality`.
- General computer-vision correctness and repeatable offline image tests: `opencv-offline-validation`.
- UART, USB serial, timeouts, reconnects, device states, or hardware diagnostics: `serial-diagnostics`.
- Multi-file changes, new features, or architecture changes: `spec-first-development`.
- Final verification before reporting completion: `release-check`.

Use the actual discovered skill directory/name if it differs from the list above. Never claim to have read or used a skill unless its instructions were actually inspected and followed.

## Implementation workflow
1. Restate the intended outcome and acceptance criteria briefly when useful.
2. Inspect relevant code, tests, configuration, dependencies, and Git changes.
3. Choose and read relevant skills; identify risks and a minimal implementation plan.
4. Make small, focused changes consistent with existing conventions. Avoid unrelated refactors and new dependencies unless justified.
5. Add or update tests for behavior changes. Prefer deterministic, offline tests and mocks when real hardware is unavailable.
6. Run applicable tests, syntax checks, and diff checks. Use the repository's documented environment and commands when available.
7. Inspect the final diff for accidental changes, security issues, and compatibility risks.
8. Report files changed, skills used, commands actually run, test results, and unresolved limitations.

## Truthfulness and safety
- Never claim a command or test passed unless it was actually executed and succeeded.
- If a check cannot run, state why and provide the exact unchecked item.
- Do not overwrite, reset, or discard user changes without permission.
- Do not assume files, dependencies, hardware, or commands exist; verify first.
- Keep Computer Vision work focused on general image analysis and reproducible offline validation. Do not implement gameplay aiming automation or anti-cheat evasion.

## Completion checklist
Before declaring a coding task complete, verify:
- [ ] The requested behavior is addressed.
- [ ] Relevant skills were selected and followed, or their absence was disclosed.
- [ ] Tests/checks were run when feasible and results are reported accurately.
- [ ] The final diff contains no unrelated changes.
- [ ] Remaining risks or unverified behavior are stated clearly.
