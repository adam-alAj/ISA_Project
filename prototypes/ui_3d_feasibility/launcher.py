"""PySide6 controller for a separate Ursina worker process."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget

WORKER = Path(__file__).with_name("ursina_worker.py")


class FeasibilityWindow(QMainWindow):
    """Small controller window that starts and sends JSON-lines to Ursina."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PySide6 + Ursina feasibility")
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.readyReadStandardError.connect(self._read_error)
        self.status = QLabel("Ursina is stopped")
        self.launch_button = QPushButton("Launch 3D")
        self.launch_button.clicked.connect(self.launch_3d)
        self.move_button = QPushButton("Send move to cell [2, 3]")
        self.move_button.clicked.connect(self.send_move)
        self.close_button = QPushButton("Close 3D")
        self.close_button.clicked.connect(self.close_3d)
        layout = QVBoxLayout()
        for widget in (self.status, self.launch_button, self.move_button, self.close_button):
            layout.addWidget(widget)
        root = QWidget()
        root.setLayout(layout)
        self.setCentralWidget(root)

    def launch_3d(self) -> None:
        """Start Ursina in its own Python process."""
        if self.process.state() != QProcess.ProcessState.NotRunning:
            return
        self.process.start(sys.executable, [str(WORKER)])
        self.status.setText("Starting Ursina process…")
        self.process.started.connect(lambda: self.status.setText("Ursina process started"))

    def send_move(self) -> None:
        """Send a sample grid move using the agreed JSON-lines protocol."""
        if self.process.state() == QProcess.ProcessState.NotRunning:
            self.status.setText("Launch the 3D process first")
            return
        message = json.dumps({"cmd": "move", "cell": [2, 3]}) + "\n"
        self.process.write(message.encode("utf-8"))

    def close_3d(self) -> None:
        """Ask the worker to close, then terminate it if it does not exit."""
        if self.process.state() == QProcess.ProcessState.NotRunning:
            return
        self.process.write(b'{"cmd":"close"}\n')
        if not self.process.waitForFinished(2000):
            self.process.terminate()
            self.process.waitForFinished(1000)
        self.status.setText("Ursina is stopped")

    def _read_output(self) -> None:
        output = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace").strip()
        if output:
            self.status.setText(output.splitlines()[-1][:120])

    def _read_error(self) -> None:
        error = bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace").strip()
        if error:
            self.status.setText(f"Ursina: {error.splitlines()[-1][:100]}")

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt callback spelling
        self.close_3d()
        event.accept()


def main() -> int:
    """Run the PySide6 feasibility controller window."""
    app = QApplication(sys.argv)
    window = FeasibilityWindow()
    window.resize(360, 180)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
