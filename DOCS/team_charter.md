# Team charter

Names and assignments are intentionally not filled in. The team must confirm membership, availability, and the decision owner before treating this charter as agreed.

## Roles and RACI

R = responsible for doing the work; A = accountable decision owner; C = consulted; I = informed. Each work item has one accountable role.

| Work item | Lead | Algorithms | Map/environment | UI | QA/docs |
|---|---|---|---|---|---|---|
| Scope, instructor liaison, phase gates | A/R | I | C | I | C |
| Search interface and six planners | C | A/R | C | I | C |
| Map pipeline and environment API | C | C | A/R | I | C |
| Robot and simulation integration | A | R | C | C | C |
| Desktop workflow and 2D view | C | I | C | A/R | C |
| Visualization scope decision (ADR-0022) | A | C | I | C | R |
| Tests, traceability, reports, release docs | C | C | C | C | A/R |

## Ownership roster

| Role | Name | Availability / contact |
|---|---|---|
| Lead | `<TBD>` | `<TBD>` |
| Algorithms | `<TBD>` | `<TBD>` |
| Map/environment | `<TBD>` | `<TBD>` |
| UI | `<TBD>` | `<TBD>` |
| QA/docs | `<TBD>` | `<TBD>` |

**Decision owner:** `<TBD>` (HUMAN ACTION: the team must name one person). Until assigned, decisions affecting requirements or interface freeze points remain provisional and must be recorded in an ADR.

## Working agreements

- Use `main` for reviewed milestones, `develop` for integration, and short-lived `feature/*` branches for task work.
- Link changes to roadmap IDs; keep requirements, tests, and documentation aligned.
- Escalate scope changes and interface changes to the decision owner; record approved changes in `docs/adr/`.
