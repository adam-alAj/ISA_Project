# Environment model draft

`GridMap` owns a read-only `uint8` occupancy array. Valid motion uses four-neighbor adjacency in U,R,D,L order and admits only FREE or DOOR cells. Cleaning state is a separate boolean array. Coordinates are documented in `docs/environment_api.md`; components, footprint inflation, graph adaptation and validation use NumPy and the standard library only.

The environment API is a P2 draft until Python tests pass and the user-authorized freeze gate is signed.
