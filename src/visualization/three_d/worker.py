"""Ursina JSON-lines worker; all simulation decisions remain in the main app."""

from __future__ import annotations

import json
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any

PROJECT_ROOT=str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:sys.path.insert(0,PROJECT_ROOT)

from src.visualization.three_d.protocol import MESSAGE_SCHEMA_VERSION


def main() -> int:
    """Start a 3D window and consume versioned commands from stdin."""
    protocol_stdout=sys.stdout
    # Ursina/Panda diagnostics go to stderr. stdout stays a clean JSONL channel.
    sys.stdout=sys.stderr
    try:
        from ursina import (AmbientLight, DirectionalLight, EditorCamera, Entity,
                            Mesh, Text, Ursina, Vec3, application, camera, color, window)
    except Exception as exc:
        protocol_stdout.write(json.dumps({"schema_version":MESSAGE_SCHEMA_VERSION,
            "type":"error","message":f"Ursina import failed: {exc}"})+"\n")
        protocol_stdout.flush(); return 2

    from src.visualization.three_d.player import ScenePlayer

    app=Ursina(title="Smart Vacuum 3D", vsync=True, borderless=False)
    window.title="Smart Vacuum 3D · synchronized playback"
    window.size=(1280,800); window.color=color.rgb(224,232,240)
    window.fps_counter.enabled=True
    try:
        camera.lens.setNearFar(.02,500)
    except AttributeError:
        pass
    DirectionalLight(y=4,z=-3,rotation=(45,-35,0),color=color.rgba(255,255,255,230))
    AmbientLight(color=color.rgba(140,140,155,255))
    messages:queue.Queue[dict[str,Any]]=queue.Queue()
    player_box={"player":None}
    stopping={"value":False}
    fps_state={"started":time.perf_counter(),"frames":0}

    def emit(kind: str, **payload):
        protocol_stdout.write(json.dumps({"schema_version":MESSAGE_SCHEMA_VERSION,
            "type":kind,**payload},separators=(",",":"))+"\n")
        protocol_stdout.flush()

    def read_stdin():
        for line in sys.stdin:
            try: message=json.loads(line)
            except json.JSONDecodeError:
                emit("protocol_error",message="invalid JSON line"); continue
            if not isinstance(message,dict) or message.get("schema_version")!=MESSAGE_SCHEMA_VERSION:
                emit("protocol_error",message="unsupported message schema"); continue
            messages.put(message)
        messages.put({"cmd":"close","schema_version":MESSAGE_SCHEMA_VERSION})

    def handle(message):
        command=message.get("cmd")
        if command=="init":
            if player_box["player"] is not None:
                for entity in reversed(player_box["player"].entities):
                    entity.disable(); entity.remove_node()
            player_box["player"]=ScenePlayer(message,{
                "Entity":Entity,"Mesh":Mesh,"EditorCamera":EditorCamera,"Vec3":Vec3,
                "color":color,"camera":camera,"Text":Text,
            })
            emit("initialized",entity_count=player_box["player"].entity_count,
                 static_entity_count=player_box["player"].layout.static_entity_count,
                 floor_rectangles=len(player_box["player"].layout.floors),
                 robot_position=tuple(player_box["player"].robot.position),
                 camera_position=tuple(player_box["player"].camera.position),
                 camera_rotation=tuple(player_box["player"].camera.rotation))
        elif command=="event":
            if player_box["player"] is not None:player_box["player"].enqueue(message.get("event",{}))
        elif command=="close":
            stopping["value"]=True; app.userExit()
        elif command=="capture":
            path=Path(message.get("path","docs/img/three_d_scene.png"))
            path.parent.mkdir(parents=True,exist_ok=True)
            from panda3d.core import Filename
            image=app.win.getScreenshot()
            if image.write(Filename.fromOsSpecific(str(path.resolve()))):emit("captured",path=str(path))
            else:emit("error",message=f"could not write screenshot: {path}")
        elif command=="camera" and player_box["player"] is not None:
            player_box["player"].camera_preset(message.get("preset","reset"))
            emit("camera_applied",position=tuple(player_box["player"].u["camera"].world_position),
                 rotation=tuple(player_box["player"].u["camera"].world_rotation))
        elif player_box["player"] is not None:
            player_box["player"].control(message)
            if command in {"play","pause","step","reset","speed","seek"}:
                emit("control_applied",cmd=command)

    def update():
        for _ in range(256):
            try:message=messages.get_nowait()
            except queue.Empty:break
            handle(message)
            if stopping["value"]:return
        if player_box["player"] is not None:
            import ursina
            player_box["player"].update(ursina.time.dt)
        fps_state["frames"]+=1
        elapsed=time.perf_counter()-fps_state["started"]
        if elapsed>=1.0:
            emit("fps_sample",fps=round(fps_state["frames"]/elapsed,1),interval_s=round(elapsed,3))
            fps_state["frames"]=0; fps_state["started"]=time.perf_counter()

    def input(key):
        player=player_box["player"]
        if player is None:return
        if key=="t":player.camera_preset("top")
        elif key=="f":player.camera_preset("follow")
        elif key=="r":player.camera_preset("reset")

    # Ursina resolves these hooks from __main__ on each frame/key press.
    import __main__
    __main__.update=update
    __main__.input=input
    threading.Thread(target=read_stdin,name="3d-json-reader",daemon=True).start()
    emit("process_ready")
    app.run()
    emit("closed")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
