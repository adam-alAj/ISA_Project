# Synthetic map fixtures

`synthetic.py` provides deterministic array fixtures for open room, corridor,
wall detour, disconnected regions, narrow passage, heuristic trap and weighted
cost scenarios. The real map fixtures are preserved `data/maps/department_v0_2`
and the P1-corrected `data/maps/department_v0_3`. The active department v1 spec
uses the corrected v0.3 room dimensions; tests document that deliberate geometry
change and require unchanged hall states, door cells and v0.2 source hash.
