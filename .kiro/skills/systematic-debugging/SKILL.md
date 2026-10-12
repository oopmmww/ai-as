---
name: systematic-debugging
description: Investigate Python, Flask, OpenCV, threading, and serial-device bugs by finding root cause before changing code. Use for exceptions, hangs, race conditions, incorrect outputs, or regressions.
---
# Systematic Debugging

1. **Reproduce and observe.** Capture the exact command, environment, traceback/logs, inputs, and expected versus actual behavior. Do not edit code yet.
2. **Trace the failure path.** Follow the data and call path backward from the failure. Inspect recent diffs and compare with a working path.
3. **Form one testable hypothesis.** Add temporary, non-sensitive instrumentation or a minimal test if needed. Change one variable at a time.
4. **Prove root cause.** Prefer a small reproducible test or controlled experiment over intuition.
5. **Add a regression test.** Ensure the test fails for the original defect where practical.
6. **Apply the smallest fix.** Avoid unrelated cleanup and multiple speculative fixes at once.
7. **Verify.** Run the regression test and relevant suite, inspect logs and `git diff`, and report remaining uncertainties.

For thread bugs, capture thread names/states and ownership of shared objects; do not insert arbitrary sleeps as a synchronization fix. For serial bugs, use a mock or loopback test before requiring physical hardware.

If two or three fixes fail, stop patching and revisit the hypothesis or architecture.
