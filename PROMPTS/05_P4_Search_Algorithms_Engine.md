# Prompt 05 — Phase P4: Search Algorithms Engine

## 1. Role
You are an **AI Search Algorithms Engineer / Researcher** (Russell & Norvig-level rigor). You implement classical algorithms explicitly (no black-box libraries), prove behaviour with reference tests, and document guarantees and limitations honestly.

## 2. Context
Use `00_Shared_Context_and_Rules.md`. P2 gate must be met. Can run in parallel with P3. Search code must be **pure** (no UI, no robot, no I/O) and consume only the frozen environment API.

## 3. Inputs
`GridMap`, `neighbors` (order U,R,D,L), synthetic test maps from P2.19, SRS §10, §16.3–16.4, §19.1.

## 4. Objective
Six algorithms with a common interface and testable behaviour. **Exit gate:** all six pass reference tests; results are comparable; search time excludes UI; `SearchResult` + trace format frozen.

## 5. Tasks (ID → concrete instruction)
- **P4.01** `algorithms/problem.py`: `SearchProblem` (start, goal, `neighbors`, `step_cost(a,b)`, `is_goal`, `heuristic(n)` optional). Build it from `GridMap` + cost model (default uniform cost = 1.0 per step; allow weighted cost layers for TS-04).
- **P4.02** `algorithms/result.py`: `SearchResult(found, path, path_length_steps, path_cost, expanded, generated, peak_frontier, repeated_expansions, execution_time_s, termination_reason, trace | None)`; `TerminationReason` enum: `GOAL_FOUND, NO_PATH, INVALID_START, INVALID_GOAL, NODE_BUDGET_EXCEEDED, TIME_BUDGET_EXCEEDED`.
- **P4.03** Document deterministic neighbor order **U,R,D,L** and tie-breaking: priority queues order by `(priority, insertion_counter)`; equal-priority ties resolved FIFO by counter.
- **P4.04** Counter semantics (write in `docs/search_counters.md`, used everywhere): *expanded* = node popped from frontier and its successors generated (counted per expansion, repeated expansions counted again and also in `repeated_expansions`); *generated* = successor states created, duplicates included; *peak_frontier* = max frontier size.
- **P4.05** `bfs.py`: FIFO queue, parent map, goal test at generation (document) or at expansion — choose one, apply consistently, test both counters.
- **P4.06** `dfs.py`: explicit stack (no recursion limits), visited set, neighbors pushed in reverse so that expansion order follows U,R,D,L.
- **P4.07** `ucs.py`: heap on `g(n)`; lazy-deletion of stale entries.
- **P4.08** `greedy.py`: heap on `h(n)`; visited set; documented non-optimality.
- **P4.09** `astar.py`: heap on `f=g+h`, tie-break lower `h` then counter; re-open nodes only when a strictly better `g` is found.
- **P4.10** `algorithms/heuristics.py`: `manhattan(n, goal) × min_step_cost`; assertion helper to verify admissibility/consistency on a map.
- **P4.11** `iddfs.py`: repeated depth-limited DFS with limits 0,1,2,… . **Critical design note:** a pure path-cycle check explodes exponentially on an open 4-neighbor grid; implement the *standard-compliant but tractable* variant: in each iteration keep `best_depth[node]` and re-expand a node only if reached at a strictly smaller depth. Document that this preserves completeness and (for unit costs) shortest-step optimality, and count repeated expansions across iterations.
- **P4.12** Termination for unreachable goals: stop when an iteration generates no node at the depth limit (frontier exhausted) → `NO_PATH`; also support `max_depth` cap.
- **P4.13** Stale-entry and improved-path handling in UCS/A* (tests with weighted graphs that force improvement of an already-queued node).
- **P4.14** Edge cases: `start == goal` (path=[start], cost 0, 0 expansions policy documented), invalid start/goal, no path, disconnected maps, goal inside a wall.
- **P4.15** Optional **trace events** (`NodeExpanded, NodeGenerated, FrontierSnapshot(sampled), GoalReached`) emitted through a callback/generator protocol; zero overhead when disabled; trace format = frozen schema (JSON-serializable).
- **P4.16** Reference tests per algorithm on tiny hand-verifiable grids with expected expansion order (golden tests).
- **P4.17** BFS shortest-step optimality: compare against an independent oracle (e.g., simple Dijkstra) on 200 random unit-cost maps (seeded).
- **P4.18** UCS least-cost on weighted maps (TS-04) vs oracle.
- **P4.19** A* equals UCS cost with admissible heuristic on random maps; expansions(A*) ≤ expansions(UCS) on average.
- **P4.20** Heuristic-trap map (TS-05): Greedy returns a longer path than A*; test asserts `greedy.cost > astar.cost`.
- **P4.21** DFS behaviour follows documented neighbor order (golden path); long winding path is expected and documented.
- **P4.22** IDDFS: depth progression log, completeness on finite test cases, optimal steps on unit costs, repeated-expansion accounting.
- **P4.23** `benchmarks/bench_search.py`: time each algorithm (median of ≥5 runs, `time.perf_counter`) on the real department map for ≥6 start/goal pairs from P1.14; no rendering involved; output CSV. Include node/time budgets to prevent runaway runs.
- **P4.24** `docs/algorithms.md`: per algorithm — data structure, completeness, optimality conditions, time/space complexity (b, d, m, grid specifics), and observed behaviour on the department map (screenshots optional). No claim of a universal winner.

## 6. Constraints
- Algorithms must not import from `robot`, `simulation`, `visualization`, `app`.
- No hidden state between calls; every call is reproducible.
- Do not weaken a test to make an algorithm pass; fix the algorithm.
- Register the six algorithms in a `REGISTRY: dict[str, SearchFn]` with a uniform signature.

## 7. Deliverables
`src/algorithms/*`, `tests/algorithms/*`, `benchmarks/*`, `docs/algorithms.md`, `docs/search_counters.md`, ADR "SearchResult & trace freeze (Freeze point 3)".

## 8. Acceptance gate (report pass/fail each)
- [ ] TS-01…TS-05 pass for all applicable algorithms; oracle comparisons pass on seeded random maps.
- [ ] All six return the same `SearchResult` schema; registry works.
- [ ] IDDFS terminates on unreachable goals and on the real map within budget.
- [ ] Benchmarks run headless and exclude any visualization time.
- [ ] Counter semantics documented and tested.

## 9. Output
Use the report format from Shared Context §8.5. Include a comparison table (expanded, generated, cost, time) for the benchmark pairs, with the caveat that it is not a verdict on the "best" algorithm.
