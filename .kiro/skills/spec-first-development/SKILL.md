---
name: spec-first-development
description: Plan a non-trivial software change for AIAS before implementation. Use for new features, refactors, architecture changes, or multi-file bug fixes that need requirements, design, tasks, and acceptance criteria.
---
# Spec-First Development

## Workflow
1. Inspect the current code, related callers, docs, tests, and existing `.kiro/specs/` folders.
2. Restate the problem, constraints, out-of-scope items, and observable acceptance criteria.
3. For a multi-file or non-trivial task, create a new `.kiro/specs/<short-task-name>/` with `requirements.md`, `design.md`, and `tasks.md`. Do not overwrite an existing spec.
4. The design must identify changed modules, data/control flow, failure modes, concurrency/resource ownership, compatibility, and test strategy.
5. Break implementation into small tasks that can be validated independently. Prefer one root-cause fix at a time.
6. Implement only the approved scope. Do not add unrelated refactors or dependencies without justification.
7. Update task status only after implementing and verifying the corresponding work.
8. Finish with a concise summary of files changed, tests actually run, risks, and unverified hardware/manual steps.

For a one-line low-risk fix, a brief plan and a regression test may be enough; do not create ceremonial specs for every tiny edit.

## Guardrails
- Do not invent APIs, modules, test results, protocol details, or hardware support.
- Do not implement automated aiming, game-input manipulation, recoil control, or anti-cheat evasion.
