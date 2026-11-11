# Search counters and trace schema (draft)

These semantics are shared by BFS, DFS, UCS, Greedy Best-First, A*, and IDDFS.

* **expanded**: a node popped from the frontier whose successors are generated. Goal testing happens on pop before expansion; a popped goal is therefore not counted.
* **generated**: each successor state produced from an expanded node, including duplicates and already-seen states. The start node is not generated.
* **peak_frontier**: the largest number of pending entries in the queue, stack, or priority queue. Stale priority-queue entries count until popped.
* **repeated_expansions**: expansions after the first expansion of the same state. IDDFS counts repeats across depth iterations; A* counts reopens after a strictly better g value.

For a valid `start == goal`, all algorithms return `[start]`, cost and step count zero, and zero expansions/generated nodes. Invalid endpoints are rejected before search. BFS, DFS, UCS, Greedy, and A* test goals when popped. IDDFS tests a state when popped within its depth limit.

Trace is optional. When enabled, events are JSON-serializable dictionaries with an `event` field: `NodeExpanded`, `NodeGenerated`, sampled `FrontierSnapshot`, and `GoalReached`. IDDFS also emits `DepthIterationStarted`. Without trace collection or callback, no event dictionaries are built. Neighbor order is Up, Right, Down, Left. Priority ties use insertion order; A* orders by `(f, h, insertion_counter)`.

This is a draft contract pending executable test validation and the environment API freeze.
