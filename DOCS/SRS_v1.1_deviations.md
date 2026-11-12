# SRS v1.1 deviations — 3D visualization descoping

| Requirement | Original | Revised disposition | Reason | Approval |
|---|---|---|---|---|
| FR-21 | SHOULD: optional 3D environment visualization and synchronized robot route | Descoped; feature removed from product | Integrated 3D render was blank under the production HUD; maintaining a separate graphics stack is outside remaining project capacity. 2D map, route, and cleaned overlay remain. | Pending instructor acknowledgement (ADR-0022) |
| AC-06 | MUST: 3D route visualization acceptance | Descoped; not passed and not claimed compliant | The production 3D scene failed visual acceptance. Scope change requires instructor acknowledgement. | Pending instructor acknowledgement (ADR-0022); release MUST gate remains blocked until acknowledged or requirement is restored |

The original SRS and roadmap DOCX files are retained as immutable source records. This deviation does not alter any other MUST requirement or frozen simulation event/snapshot contract.
