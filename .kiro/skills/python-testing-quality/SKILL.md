---
name: python-testing-quality
description: Improve Python code quality with targeted tests, type hints, lint checks, clear exception handling, and regression coverage. Use for bug fixes, refactors, code cleanup, or preparing a change for review.
---
# Python Testing and Quality

## Before coding
- Inspect `requirements.txt`, existing tests, `.github/workflows/`, and any `pyproject.toml`, `pytest.ini`, or lint config.
- Use current project tools and invocation patterns first. Do not install or configure a new tool without explaining why.

## Test strategy
- Add the smallest regression test that reproduces the defect.
- Use deterministic fixtures and dependency injection/mocks for camera capture, filesystem paths, clocks, and serial devices.
- Test error paths: missing/invalid configuration, empty frames, wrong dtype/channel count, device unavailable, timeout, malformed response, and shutdown after an exception where relevant.
- Avoid tests that require a live multiplayer game, real input automation, or undisclosed physical devices.

## Code review checklist
- Are types, return values, state transitions, and error cases clear?
- Are exceptions specific and actionable?
- Are resources closed on both success and failure?
- Are global state and hidden side effects avoided?
- Are constants/configuration validated and documented?
- Are tests deterministic, isolated, and meaningful?

## Completion report
State exact test/lint commands and their real outcomes. Distinguish automated tests from manual checks and physical-device checks. Do not claim coverage increased unless measured.
