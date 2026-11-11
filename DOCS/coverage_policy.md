# Coverage policy and denominator

Point-to-point search answers whether there is a legal route between two cells. Coverage is a separate repeated-target process: select an uncleaned floor cell, ask the configured route planner for a path, execute it through `Robot.step`, and update the cleaning layer.

The raw denominator is every `FREE` or `DOOR` cell connected to the start by four-neighbor transitions on the uninflated occupancy grid. Walls and unknown cells are excluded. The raw percentage is cleaned raw-denominator cells divided by this count.

The robot centre must stay in the footprint-inflated navigable mask. Its cleaning disc is applied to raw traversable cells, so it may clean a cell without occupying it. `structurally_uncoverable` contains raw reachable cells which no reachable legal centre can clean. Achievable coverage excludes those cells; the raw percentage and the structurally-uncoverable set/count remain available for honest reporting. Planner-specific failures are reported separately as `unreachable_cells`.

The baseline target policy uses Manhattan distance from current position and row/column tie breaking. It builds a balanced kd-tree once and deactivates cleaned/excluded cells incrementally, avoiding a full candidate-pair scan per selection. Identical policy identity is part of the experiment run hash. Search wall time is accumulated separately from simulated robot time.
