# PySide6 and Ursina feasibility prototype

Run `python launcher.py` to open the PySide6 controller. **Launch 3D** starts `ursina_worker.py` as a separate process; the move button sends `{"cmd":"move","cell":[r,c]}` as one JSON line, and close sends `{"cmd":"close"}`.

Run `python cycle_benchmark.py` on the intended Windows graphics machine to measure ten worker startup/close cycles. It writes `cycle_results.csv`. The prototype has not been executed in the current environment because Python and a graphics session are unavailable. No stability or timing result is claimed yet.
