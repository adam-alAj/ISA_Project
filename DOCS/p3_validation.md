# P3 acceptance report

Status: implementation and tests are written; Python execution and API freeze are pending.

| Acceptance criterion | Status | Evidence / remaining work |
|---|---|---|
| Battery and lifetime limits work independently and together | Implemented, unverified | Parameterized tests cover battery-only, lifetime-only, both-limit precedence, exact-boundary exhaustion, and zero initial budgets. |
| 10,000 legal/illegal attempts preserve invariants | Implemented, unverified | Seeded property test uses seed `20261111`, checks map/footprint legality, non-negative resources, cleaning-count consistency and state identity on rejected moves. |
| Rejected-step atomicity | Implemented, unverified | Tests compare serialized immutable state bytes and cleaning layer before/after failed movement and resource preflight. |
| Units and coefficients documented | Implemented | See `docs/robot_model.md`; all defaults come from the provisional editable config. |
| Worked numeric example | Test added; execution pending | At 0.10 m/cell and 0.25 m/s: one step takes 0.4 s; nine new cells cost 0.18 units plus 0.05 movement = 0.23 units. |
| Robot API frozen | **Not frozen** | The upstream P2 environment API is still draft, and the required map review/signature has not happened. ADR-0014 records the proposed contract. |

## Environment limitation

No Python or pytest executable is available in this workspace, so no P3 test result is claimed. Run `pytest tests/robot` in the project Python 3.12 environment before freezing the robot API. P3 work proceeds against the documented draft P2 contract under the user's instruction to continue later phases while HUMAN ACTION items remain open.
