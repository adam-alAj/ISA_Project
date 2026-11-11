# Search algorithms (draft)

All algorithms consume `SearchProblem` and return the same `SearchResult`. The grid adapter uses four-neighbor U,R,D,L movement, charges the target cell's cost for weighted transitions, and defaults to unit costs. Search timing excludes visualization and I/O. All priorities are deterministic; equal priorities are FIFO by insertion counter (A* prefers lower h before FIFO).

| Algorithm | Frontier / repeated-state policy | Complete | Optimality | Complexity |
|---|---|---|---|---|
| BFS | FIFO queue; discover once | Yes on finite graphs | Minimum steps for unit edge costs | O(b^d) time and space; on finite grids O(V+E) |
| DFS | Explicit LIFO stack, reverse pushes | Yes on finite graphs with visited set | No | O(V+E) time, O(V) space on finite grids |
| UCS | Heap by g; stale entries discarded; strict improvements | Yes for finite graphs with positive costs | Minimum cost for nonnegative costs (zero-cost cycles need care) | O((V+E) log V) typical |
| Greedy Best-First | Heap by h; visited at generation | Yes on finite graphs | No | O((V+E) log V) typical; O(V) stored states |
| A* | Heap by f, then h, then insertion; strict-g reopen | Yes on finite graphs under nonnegative costs | Optimal with admissible h and appropriate goal handling; consistent h avoids reopens | O((V+E) log V) typical, heuristic dependent |
| IDDFS | Repeated depth-limited DFS; per-iteration best-depth dominance pruning | Yes on finite graphs | Minimum steps for unit costs | Tree bound O(b^d) time, O(bd) space; graph dominance reduces duplicate work |

For a four-neighbor grid, branching factor is at most four and Manhattan distance is admissible for uniform costs; weighted grids scale it by the minimum traversable step cost. Greedy may return longer routes; DFS depends strongly on neighbor order. IDDFS records repeated expansions across iterations. No algorithm is declared a universal winner.

Department-map benchmarks are pending because Python is unavailable in the current execution environment. `benchmarks/bench_search.py` provides the headless harness and writes a CSV when run in the project environment. The current environment map is still draft, so benchmark measurements would not be a freeze result.

## Draft API status

The implementation is not frozen. Upstream GridMap remains draft and automated tests could not be run in this workspace; see ADR-0015.
