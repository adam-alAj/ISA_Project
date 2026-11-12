# Coding standards

## Python style

- Target Python 3.12; support 3.11 as fallback. Use four spaces, readable names, and full type hints on public functions and data structures.
- Use `snake_case` for modules/functions/variables, `PascalCase` for classes, and `UPPER_SNAKE_CASE` only for constants.
- Prefer small functions, explicit data flow, `pathlib`, and frozen dataclasses for value objects. Avoid hidden mutable globals and unseeded randomness.
- Add concise Google-style docstrings to public APIs and explain non-obvious algorithm choices.
- Raise specific exceptions with actionable messages. Use `logging`; library modules must not print.
- Keep algorithms, environment, robot, coverage, and simulation free of PySide6 and Matplotlib imports. UI and visualization consume core interfaces/events.
- Keep occupancy and cleaning state separate. Search expansion must not mutate robot state. Fix and document neighbor order and tie-breaking.

## Tests and quality

- Use pytest; test behavior and boundary conditions. Add/adjust tests with each behavior change.
- Use Ruff when installed; do not treat formatter success as evidence of correctness.
- Tests should use deterministic synthetic maps and avoid dependence on display hardware unless marked as UI integration tests.

## Import boundary check

Run `python scripts/check_core_ui_imports.py` to reject direct UI/graphics imports in core packages. The check is intentionally a lightweight text scan; dynamic imports and aliases still require code review.
