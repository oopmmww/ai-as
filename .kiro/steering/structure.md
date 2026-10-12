---
inclusion: always
---
# Repository Structure and Boundaries

The README currently describes this layout; always verify the actual tree before editing:

- `main.py`: application entry point
- `src/core/`: vision/application core and serial bridge
- `src/config/`: configuration and related learning/configuration components
- `src/logging/`: event/performance logging and logger routes
- `src/web/`: Flask routes and dashboard routes
- `templates/`: HTML templates
- `config/`: runtime configuration files
- `firmware/`: microcontroller firmware
- `docs/`: project notes, roadmap, and integration documentation
- `.kiro/specs/`: Kiro requirements/design/tasks

Architecture rules:
- Keep Flask route handlers thin; place reusable logic in appropriate modules.
- Avoid circular imports and importing modules by relying on the current working directory.
- Keep configuration, processing, presentation, logging, and hardware I/O separated.
- Avoid introducing a new abstraction layer unless a concrete problem justifies it.
- Before moving files or renaming public functions, search for all references and update tests/docs.
- Do not overwrite existing `.kiro/specs/` work; create a new spec folder for a distinct task.
