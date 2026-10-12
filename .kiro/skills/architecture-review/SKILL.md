---
name: architecture-review
description: Audit Python software architecture, module boundaries, imports, concurrency, resource lifecycle, Flask separation, configuration, and reliability. Use for AIAS architecture review or before a refactor.
---
# Architecture Review

## Procedure
1. Read the current tree, README, dependency declarations, CI workflow, entry point, and relevant source files. Verify repository reality rather than trusting docs alone.
2. Trace startup, normal operation, error paths, and shutdown. Identify owners of camera/serial/file/server resources and shared state.
3. Check import consistency, circular dependencies, global mutable state, thread synchronization, race conditions, thread cancellation/joining, and cleanup on exceptions.
4. Review module boundaries between core processing, configuration, logging, web routes, and hardware I/O.
5. Check configuration validation, safe defaults, authentication for local APIs, secret handling, and whether logs leak sensitive values.
6. Check whether tests prove the critical contracts and failure paths.
7. Return findings sorted by severity: P0 (blocks use/data/security), P1 (likely defect/reliability), P2 (maintainability), P3 (minor improvement).

## Required output
For every finding include: severity, file and function/line when available, evidence, impact, recommended minimal fix, and regression test. Separate confirmed defects from risks needing runtime evidence.

## Rules
- First review only; do not edit files unless explicitly asked.
- Do not guess from a filename or README claim when source can be inspected.
- Avoid generic advice without tying it to specific code.
- Keep the review scoped to general software reliability and maintainability; do not improve game-targeting, aim automation, recoil control, or anti-cheat evasion.
