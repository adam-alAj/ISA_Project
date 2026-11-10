# Contributing

## Branch workflow

- `main` contains reviewed, demonstrable work.
- `develop` is the integration branch for the current phase.
- Create short-lived `feature/<topic>` branches from `develop`; use `fix/<topic>` for defects and `docs/<topic>` for documentation-only work.
- Open a pull request to `develop`, link the task ID, describe the change, and include relevant test output. Merge `develop` to `main` at phase or release gates.
- Keep commits focused and avoid committing virtual environments, logs, or generated reports.

## Commit messages

Use Conventional Commits: `type(scope): imperative summary`. Common types are `feat`, `fix`, `docs`, `test`, `refactor`, `build`, and `chore`. Example: `docs(p0): add requirements traceability matrix`.

## Review expectations

Keep search, environment, robot, and simulation modules independent of UI/3D libraries. Record requirement changes and architectural decisions. Add tests with behavior changes and run `pytest` before requesting review.
