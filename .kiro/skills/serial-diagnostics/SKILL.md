---
name: serial-diagnostics
description: Diagnose general serial-port reliability, protocol framing, timeouts, reconnect behavior, and resource cleanup for AIAS hardware integration. Use when a device disconnects, initialization fails, or serial errors occur.
---
# Serial Hardware Diagnostics

## Workflow
1. Read the existing firmware, Python bridge, configuration, and documentation before inferring the protocol.
2. Record the expected baud rate, framing, message format, acknowledgement behavior, timeout, and device lifecycle only when supported by source/docs.
3. Separate port discovery/opening, transport I/O, protocol parsing, and application decisions.
4. Validate malformed, partial, empty, and delayed input. Ensure timeouts are finite and errors are surfaced with actionable logs.
5. Use bounded retry/backoff for transient reconnects. Avoid infinite tight retry loops.
6. Ensure one clear owner controls the serial handle, writes are serialized, and shutdown closes the handle reliably.
7. Build tests with a fake serial adapter or loopback where possible; mark physical hardware checks as not run if unavailable.

## Rules
- Preserve the documented existing protocol unless a spec approves a compatible change.
- Never log credentials or sensitive payloads.
- Do not add commands to manipulate mouse/keyboard input or gameplay. This skill is for transport reliability and device diagnostics only.
