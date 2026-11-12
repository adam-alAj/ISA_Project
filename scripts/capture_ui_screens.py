"""Capture the seven retained desktop screens offscreen for P6 review artifacts."""
from pathlib import Path
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication
from src.app.app_controller import AppController
from src.app.main_window import MainWindow
from src.visualization.two_d.map_canvas import MapCanvas


def main():
    root=ROOT
    app=QApplication([]); scratch=tempfile.TemporaryDirectory(prefix="vacuum-ui-capture-")
    controller=AppController(data_root=Path(scratch.name)/"data")
    window=MainWindow(controller); window.resize(1440,900)
    controller.load_map(root/"data"/"maps"/"department_v1")
    window.show(); app.processEvents()
    out=root/"docs"/"img"; out.mkdir(parents=True,exist_ok=True)
    names=("project_home","map_editor","robot_configuration","algorithm_setup","2d_simulation",
           "results_dashboard","report_export")
    for index,name in enumerate(names):
        window.nav.setCurrentRow(index); app.processEvents(); window.stack.currentWidget().grab().save(str(out/f"{name}.png"))
    window.nav.setCurrentRow(4); app.processEvents()
    window.sim_canvas.grab().save(str(out/"2d_simulation.png"))
    import numpy as np
    grid=np.array([[0,0,3,1,2,0],[0,1,0,0,2,0],[0,0,0,3,0,0],[2,0,1,0,0,0],[0,0,0,0,1,0]],dtype=np.uint8)
    golden=MapCanvas(); golden.setFixedSize(640,480); golden.set_map(grid,(4,0),(0,5))
    clean=np.zeros(grid.shape,dtype=bool); clean[3,1]=True; clean[2,2]=True
    golden.set_overlay(cleaned=clean,explored={(1,0),(1,1),(2,1)},path=((4,0),(3,0),(2,0),(1,0)),robot=(2,0))
    golden.show(); app.processEvents()
    image=golden.render_content(480,400,include_marker_labels=False)
    image.save(str(out/"map_canvas_golden.png")); golden.close()
    window.close(); scratch.cleanup()


if __name__=="__main__": main()

