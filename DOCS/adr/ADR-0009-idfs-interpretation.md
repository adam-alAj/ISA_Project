# ADR-0009 IDFS interpretation

## Context
The SRS course label is “IDFS/IDDFS” but explicitly requests instructor confirmation.

## Decision
Use canonical algorithm ID `iddfs` for Iterative Deepening Depth-First Search and accept `idfs` as an alias. This is a working assumption until the instructor confirms the course terminology.

## Consequences
The name registry maps `idfs` to `iddfs`; P4 planning uses repeated depth-limited DFS and accounts for repeated expansions. Keep the alias so a later naming correction does not require changing every call site. Confirm terminology with the instructor before freezing the algorithm interface.

## Status
Working assumption accepted by the user on 2026-11-11; instructor confirmation remains HUMAN ACTION and non-blocking.
