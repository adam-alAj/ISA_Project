"""Measure fixed-size Qt map rendering latency on the 127x120 grid."""
from pathlib import Path
import os, sys, time, statistics
os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
import numpy as np
from PySide6.QtWidgets import QApplication
from src.visualization.two_d.map_canvas import MapCanvas

def main():
    app=QApplication([])
    canvas=MapCanvas(); canvas.resize(1100,760)
    with np.load(ROOT/"data/maps/department_v1/grid.npz") as archive: grid=np.array(archive["grid"],copy=True)
    canvas.set_map(grid,(118,54),(12,36)); canvas.show(); app.processEvents()
    samples=[]
    for _ in range(12):
        start=time.perf_counter(); canvas.grab(); app.processEvents(); samples.append((time.perf_counter()-start)*1000)
    print(f"grid={grid.shape}; size=1100x760; renders={len(samples)}; median_ms={statistics.median(samples):.2f}; max_ms={max(samples):.2f}")
    canvas.close()
if __name__=="__main__":main()
