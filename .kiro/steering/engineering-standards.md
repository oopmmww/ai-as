---
inclusion: always
---
# Engineering Standards

## Work style
- Inspect the relevant source, callers, tests, configuration, and recent git diff before changing code.
- State the root cause and smallest appropriate fix before editing when fixing a defect.
- Prefer small, focused changes. Avoid unrelated refactors in the same change.
- Preserve existing behavior unless the task explicitly changes it.
- Do not claim a test, build, or hardware validation passed unless it was actually run; include the command and result.

## Python quality
- Use clear names, type annotations for important interfaces, and short functions with one responsibility.
- Catch specific exceptions. Do not silently swallow exceptions or use bare `except:`.
- Validate external input and configuration at module boundaries.
- Do not introduce mutable global state when dependency injection or a small state-owning object is sufficient.
- Avoid hard-coded secrets, device paths, or environment assumptions.

## Concurrency and lifecycle
- Identify which thread owns each resource and shared state.
- Use `threading.Event` or an equivalent explicit cancellation mechanism for stoppable loops.
- Use locks/queues when shared mutable state requires coordination; document ownership instead of adding locks blindly.
- Close camera, serial, file, and server resources reliably, including error paths.
- Use bounded waits and explicit thread joins when shutting down. Do not treat a fixed sleep as proof that a thread finished.
- Make startup and shutdown ordering explicit and testable.

## Security and changes
- Keep local dashboards bound to the intended interface and maintain existing authentication checks.
- Never log tokens or sensitive configuration values.
- Avoid destructive file/config migrations without a backup path and explicit approval.
- Do not add game-control/aim automation or anti-cheat evasion behavior.
