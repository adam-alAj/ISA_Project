# Search counter and goal-test contract (Freeze point 5 input)

**Status: Frozen**  
**Date: 2026-11-11**  
Executable validation: `tests/algorithms/test_search.py` and full suite in
`reports/qa/p6_gate_result.md` (87 tests passed at freeze preparation).

These definitions apply to BFS, DFS, UCS, Greedy Best-First, A*, and IDDFS.
Public result names are defined by `SearchResult` in
`src/algorithms/result.py`; this document is the single semantic reference.

## Counters

- **expanded**: number of times a state is removed from the active frontier and
  its successors are generated. Goal testing occurs before expansion, so a
  popped goal does not increment this count. IDDFS states at the depth cutoff
  are not expanded; IDDFS still tests their successors for whether a deeper
  iteration could find a route.
- **generated**: every successor produced while expanding a state, including
  duplicate successors, already-discovered states, and successors later
  rejected by duplicate/depth dominance rules. The initial state is not
  generated. A depth-limited IDDFS node at its cutoff generates its successors
  for cutoff detection and those successor events count.
- **repeated_expansions**: each expansion after the first expansion of the
  same state within one planner call. IDDFS repeats across depth iterations
  count. A* reopens after a strictly better path cost count when that causes a
  subsequent expansion. A state that is generated repeatedly but never
  expanded contributes nothing to this count.
- **peak_frontier**: maximum number of pending frontier entries observed
  during the call, including stale priority-queue entries until popped.
  Duplicate entries count if the algorithm retains them. The initial frontier
  has size one for a nontrivial valid search. Invalid endpoint and valid
  `start == goal` early returns have peak zero.

## Goal-test and termination rules

- Invalid start/goal validation precedes search; invalid endpoints produce
  zero expansions and generated nodes.
- A valid `start == goal` returns path `[start]`, zero steps/cost/expansions/
  generated/repeats/frontier, and `GOAL_FOUND`.
- BFS, DFS, UCS, Greedy, and A* test for goal when a state is popped, before
  expansion. IDDFS tests a state when popped in each depth-limited iteration,
  before cutoff/expansion processing.
- Search budget checks may terminate before another expansion. A popped goal
  is accepted before the expansion-budget check because finding the goal
  requires no successor generation.

## Trace

Trace is optional and does not alter result counters. When enabled, JSON-safe
trace records may include `NodeExpanded`, `NodeGenerated`, sampled
`FrontierSnapshot`, `GoalReached`, and IDDFS `DepthIterationStarted`. Without a
trace collection or callback, no trace dictionaries are constructed.
Successor order is Up, Right, Down, Left. Priority ties are FIFO insertion
order; A* orders by `(f, h, insertion_counter)`.

## Freeze record

The counter meanings and goal-test order are frozen for P8 analytics and
reporting. A semantic change requires an ADR and updates to the search-counter,
metrics, comparison, and golden-result tests. Search result field names and
the trace payload remain governed by Freeze point 3 (ADR-0015).
