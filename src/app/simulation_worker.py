"""QThread wrapper that keeps planning and simulation off the GUI thread."""
from PySide6.QtCore import QThread, Signal
import sys


class SimulationWorker(QThread):
    finished_result = Signal(object)
    failed = Signal(str)
    record_saved = Signal(str)
    record_failed = Signal(str)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def run(self):
        # Python planners execute bytecode in this worker. Give Qt's GUI thread
        # frequent GIL handoffs so timers and input remain responsive.
        previous_switch_interval = sys.getswitchinterval()
        sys.setswitchinterval(0.0005)
        try:
            result = self.controller.run()
            try:
                path = self.controller.record_completed_run(result)
                self.record_saved.emit(str(path))
            except Exception as exc:
                self.record_failed.emit(f"{type(exc).__name__}: {exc}")
            self.finished_result.emit(result)
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")
        finally:
            sys.setswitchinterval(previous_switch_interval)
