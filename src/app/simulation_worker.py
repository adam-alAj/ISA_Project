"""QThread wrapper that keeps planning and simulation off the GUI thread."""
from PySide6.QtCore import QThread, Signal
import sys


class SimulationWorker(QThread):
    finished_result = Signal(object)
    failed = Signal(str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        # Python planners execute bytecode in this worker. Give Qt's GUI thread
        # frequent GIL handoffs so timers and input remain responsive.
        previous_switch_interval = sys.getswitchinterval()
        sys.setswitchinterval(0.0005)
        try:
            self.finished_result.emit(self.controller.run())
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
        finally:
            sys.setswitchinterval(previous_switch_interval)
