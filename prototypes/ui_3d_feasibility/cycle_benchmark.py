"""Measure ten Ursina worker startup/close cycles on the local graphics host."""

from __future__ import annotations

import csv
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

WORKER = Path(__file__).with_name("ursina_worker.py")
RESULTS = Path(__file__).with_name("cycle_results.csv")


def main() -> int:
    """Run ten worker cycles and save startup/exit results as CSV."""
    rows: list[dict[str, str | float | int]] = []
    for cycle in range(1, 11):
        process = subprocess.Popen(
            [sys.executable, str(WORKER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        lines: queue.Queue[str] = queue.Queue()

        def collect() -> None:
            assert process.stdout is not None
            for line in process.stdout:
                lines.put(line.rstrip())

        threading.Thread(target=collect, daemon=True).start()
        started = time.perf_counter()
        ready = False
        errors: list[str] = []
        deadline = started + 45
        while time.perf_counter() < deadline and process.poll() is None:
            try:
                line = lines.get(timeout=0.1)
            except queue.Empty:
                continue
            if line.startswith("READY_JSON "):
                ready = True
                break
            if line.strip():
                errors.append(line.strip())
        startup_seconds = time.perf_counter() - started if ready else -1.0
        if process.poll() is None and process.stdin is not None:
            process.stdin.write('{"cmd":"close"}\n')
            process.stdin.flush()
        try:
            exit_code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                exit_code = process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                exit_code = process.wait()
        rows.append(
            {
                "cycle": cycle,
                "startup_seconds": round(startup_seconds, 3),
                "ready": int(ready),
                "exit_code": exit_code,
                "notes": "; ".join(errors[-3:]),
            }
        )
        print(f"cycle {cycle:02d}: ready={ready} startup={startup_seconds:.3f}s exit={exit_code}")

    with RESULTS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["cycle", "startup_seconds", "ready", "exit_code", "notes"])
        writer.writeheader()
        writer.writerows(rows)
    good = sum(bool(row["ready"]) and row["exit_code"] == 0 for row in rows)
    print(f"RESULT {good}/10 cycles completed; details: {RESULTS}")
    return 0 if good == 10 else 1


if __name__ == "__main__":
    raise SystemExit(main())
