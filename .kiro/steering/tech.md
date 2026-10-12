---
inclusion: always
---
# Technology and Constraints

The repository README describes Python 3.10+, Windows 10/11, OpenCV, Flask, a `requirements.txt`, and firmware under `firmware/`. It documents a serial-connected microcontroller. Treat these as repository claims, not proof that every supported board or dependency has been verified.

Rules:
- Read `requirements.txt`, CI workflows, and the actual source before choosing commands or libraries.
- Preserve the Python versions and dependency constraints currently declared by the project.
- Do not add a library if the standard library or an existing dependency is sufficient. If a new dependency is necessary, explain the benefit, footprint, compatibility, and alternatives before adding it.
- Do not guess serial protocol details or claim hardware compatibility without tests or documentation.
- Prefer deterministic tests that do not require a live device; mock serial I/O where appropriate.
- Do not change build/firmware targets unless the task explicitly asks for it and the change is documented.
