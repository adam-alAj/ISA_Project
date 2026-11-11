# ADR-0001 Python version

## Context
The SRS supports Python 3.11 or 3.12; teammates need a common, reproducible baseline.

## Decision
Target Python 3.12, with 3.11 as a fallback. This is provisional until dependencies pass the Windows smoke test.

## Consequences
Setup docs and CI should prefer 3.12 and retain a 3.11 compatibility check where practical. Dependency versions remain unpinned until verified.

## Status
Accepted provisionally by the user on 2026-11-11. Revisit only if a dependency or platform conflict appears.
