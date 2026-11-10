"""Minimal Ursina process that accepts newline-delimited JSON commands."""

from __future__ import annotations

import json
import queue
import sys
import threading
from typing import Any

from ursina import Entity, Ursina, application, color, window

commands: queue.Queue[dict[str, Any]] = queue.Queue()


def read_commands() -> None:
    """Read stdin without blocking Ursina's render loop."""
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            print("ERROR invalid JSON command", flush=True)
            continue
        if isinstance(message, dict):
            commands.put(message)


app = Ursina()
window.title = "Smart Vacuum 3D feasibility"
Entity(model="plane", scale=20, color=color.light_gray, collider="box")
robot = Entity(model="sphere", color=color.azure, scale=(0.5, 0.25, 0.5), y=0.15)
threading.Thread(target=read_commands, daemon=True).start()


def update() -> None:
    """Apply queued commands on Ursina's main thread."""
    while not commands.empty():
        message = commands.get_nowait()
        if message.get("cmd") == "close":
            application.quit()
        elif message.get("cmd") == "move":
            cell = message.get("cell")
            if isinstance(cell, list) and len(cell) == 2 and all(isinstance(v, int) for v in cell):
                row, column = cell
                robot.x = column * 0.1
                robot.z = -row * 0.1


print("READY_JSON {\"event\":\"ready\"}", flush=True)
app.run()
