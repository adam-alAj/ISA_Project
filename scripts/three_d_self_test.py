"""Launch the real 3D worker, load the department map, replay a route and close."""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from src.algorithms.registry import REGISTRY
from src.environment.grid_map import GridMap
from src.map_processing.map_io import load_map
from src.map_processing.spec_loader import load_spec
from src.robot.config import RobotConfig
from src.robot.vacuum_robot import Robot
from src.simulation.modes import PointToPointMission
from src.simulation.simulation_engine import SimulationEngine
from src.visualization.three_d.protocol import command,encode_message


def main() -> int:
    """Run a short live Ursina/software-renderer check and emit a JSON report."""
    map_dir=ROOT/"data"/"maps"/"department_v1"
    grid,metadata=load_map(map_dir)
    metadata["spec"]=load_spec(map_dir/"map_spec.yaml")
    robot_config=RobotConfig()
    start=(118,54); goal=(118,68)
    robot=Robot(GridMap(grid,float(metadata["cell_m"]),metadata=metadata),start,robot_config)
    result,event_log=SimulationEngine(robot).run_point_to_point(
        PointToPointMission(start,goal),REGISTRY["bfs"])
    if not result.found:raise RuntimeError("self-test route is not reachable")

    worker=ROOT/"src"/"visualization"/"three_d"/"worker.py"
    process=subprocess.Popen([sys.executable,"-u",str(worker)],cwd=ROOT,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output:queue.Queue[str]=queue.Queue()
    diagnostics:queue.Queue[str]=queue.Queue()
    def read_output():
        assert process.stdout is not None
        for line in process.stdout:output.put(line.decode("utf-8",errors="replace").strip())
    threading.Thread(target=read_output,name="three-d-self-test-reader",daemon=True).start()
    def read_stderr():
        assert process.stderr is not None
        for line in process.stderr:diagnostics.put(line.decode("utf-8",errors="replace").rstrip())
    threading.Thread(target=read_stderr,name="three-d-self-test-diagnostics",daemon=True).start()

    def send(name,**fields):
        assert process.stdin is not None
        process.stdin.write(encode_message(command(name,**fields))); process.stdin.flush()

    def wait_for(message_type,timeout):
        deadline=time.perf_counter()+timeout
        seen=[]
        while time.perf_counter()<deadline:
            try:line=output.get(timeout=min(.25,max(0.01,deadline-time.perf_counter())))
            except queue.Empty:continue
            try:message=json.loads(line)
            except json.JSONDecodeError:continue
            seen.append(message)
            if message.get("type")==message_type:return message,seen
            if message.get("type")=="error":raise RuntimeError(message.get("message"))
        errors=[]
        while True:
            try:errors.append(diagnostics.get_nowait())
            except queue.Empty:break
        raise TimeoutError(f"worker did not emit {message_type!r} within {timeout}s; received {seen[-4:]}; stderr={errors[-12:]}")

    started=time.perf_counter()
    try:
        wait_for("process_ready",30)
        send("init",grid=grid.tolist(),cell_m=float(metadata["cell_m"]),metadata=metadata,
            start_cell=start,robot_cell=start,robot_diameter_m=robot_config.diameter_m,
            speed_m_per_s=robot_config.speed_m_per_s,playback_speed=16.0)
        initialized,_=wait_for("initialized",30)
        image=ROOT/"docs"/"img"/"three_d_scene.png"
        # Let Ursina render the initialized scene before requesting the back buffer.
        send("camera",preset="top")
        camera_state,_=wait_for("camera_applied",10)
        time.sleep(1.0)
        send("capture",path=str(image))
        captured,_=wait_for("captured",15)
        for event in event_log.events:
            send("event",event={"schema_version":event.schema_version,"type":event.type,
                "t_sim":event.t_sim,"seq":event.seq,"payload":event.payload})
        send("play")
        time.sleep(2.2)
        send("close")
        exit_code=process.wait(timeout=8)
    except Exception:
        if process.poll() is None:process.terminate()
        try:process.wait(timeout=3)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        raise
    remaining=[]
    while True:
        try:remaining.append(json.loads(output.get_nowait()))
        except queue.Empty:break
        except json.JSONDecodeError:continue
    fps=[message["fps"] for message in remaining if message.get("type")=="fps_sample"]
    report={"worker_exit_code":exit_code,"ready_to_initialized_s":round(time.perf_counter()-started,3),
        "entity_count":initialized.get("entity_count"),
        "static_entity_count":initialized.get("static_entity_count"),
        "floor_rectangles":initialized.get("floor_rectangles"),
        "robot_position":initialized.get("robot_position"),
        "camera_position":initialized.get("camera_position"),
        "camera_rotation":initialized.get("camera_rotation"),
        "capture_camera_position":camera_state.get("position"),
        "capture_camera_rotation":camera_state.get("rotation"),
        "route_steps":result.path_length_steps,"event_movement_steps":sum(e.type=="MoveExecuted" for e in event_log.events),
        "fps_samples":fps,"screenshot":captured.get("path")}
    print(json.dumps(report,indent=2))
    return 0 if exit_code==0 and report["entity_count"]<2000 else 1


if __name__=="__main__":
    raise SystemExit(main())
