"""Qt-side QProcess client for the isolated Ursina renderer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal

from src.visualization.three_d.protocol import command, encode_message


WORKER_PATH = Path(__file__).with_name("worker.py")


class ThreeDClient(QObject):
    """Send map initialization and frozen events to one Ursina subprocess."""

    status = Signal(str)
    message = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process=QProcess(self)
        self.process.setProgram(sys.executable)
        self.process.setArguments(["-u",str(WORKER_PATH)])
        self.process.started.connect(self._on_started)
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.errorOccurred.connect(lambda error:self.status.emit(f"3D process error: {error}"))
        self.process.finished.connect(self._on_finished)
        self._init_payload=None
        self._buffer=b""
        self._pending_writes:list[bytes]=[]
        self.last_event_seq=-1

    @property
    def is_running(self) -> bool:
        return self.process.state()!=QProcess.ProcessState.NotRunning

    def launch(self, payload: dict) -> None:
        """Launch a 3D process and send its one-time scene payload."""
        if self.is_running:return
        self._init_payload=payload
        self._buffer=b""
        self._pending_writes.clear()
        self.status.emit("Starting 3D renderer…")
        self.process.start()

    def _on_started(self):
        self.status.emit("3D renderer process started; loading map…")
        if self._init_payload is not None:
            self.process.write(encode_message(command("init",**self._init_payload)))
        for data in self._pending_writes:self.process.write(data)
        self._pending_writes.clear()

    def send(self, name: str, **payload) -> None:
        if not self.is_running:return
        try:
            data=encode_message(command(name,**payload))
            if self.process.state()==QProcess.ProcessState.Starting:
                self._pending_writes.append(data)
            else:self.process.write(data)
        except (TypeError,ValueError) as exc:self.status.emit(f"3D message rejected: {exc}")

    def begin_run(self, start_cell) -> None:
        """Reset the 3D event cursor when a new simulation starts."""
        self.last_event_seq=-1
        self.send("reset",cell=tuple(start_cell))
        self.send("play")

    def send_event(self,event) -> None:
        if not self.is_running:return
        data=event if isinstance(event,dict) else {
            "schema_version":event.schema_version,"type":event.type,"t_sim":event.t_sim,
            "seq":event.seq,"payload":event.payload}
        seq=int(data.get("seq",self.last_event_seq+1))
        if seq<=self.last_event_seq:return
        self.last_event_seq=seq
        self.send("event",event=data)

    def send_events(self,events) -> None:
        for event in events:self.send_event(event)

    def set_speed(self,multiplier:float) -> None:
        self.send("speed",value=float(multiplier))

    def _read_stdout(self):
        self._buffer+=bytes(self.process.readAllStandardOutput())
        while b"\n" in self._buffer:
            line,self._buffer=self._buffer.split(b"\n",1)
            if not line:continue
            try:message=json.loads(line.decode("utf-8"))
            except (UnicodeDecodeError,json.JSONDecodeError):
                self.status.emit("3D worker sent an invalid protocol line"); continue
            self.message.emit(message)
            if message.get("type")=="initialized":
                self.status.emit(f"3D ready · {message.get('entity_count',0)} entities")
            elif message.get("type")=="error":self.status.emit(message.get("message","3D worker error"))

    def _read_stderr(self):
        data=bytes(self.process.readAllStandardError()).decode("utf-8",errors="replace").strip()
        if data:self.status.emit(f"3D: {data.splitlines()[-1][:140]}")

    def _on_finished(self,code,status):
        self.status.emit("3D renderer closed" if code==0 else f"3D renderer exited ({code})")
        self.last_event_seq=-1

    def close(self,timeout_ms:int=1800) -> None:
        """Request a graceful close, then terminate/kill at the shutdown boundary."""
        if not self.is_running:return
        self.send("close")
        if not self.process.waitForFinished(timeout_ms):
            self.process.terminate()
            if not self.process.waitForFinished(800):
                self.process.kill(); self.process.waitForFinished(800)
