"""Ursina scene renderer and event-only route player.

Importing this module does not import Ursina. Instantiate `ScenePlayer` only in
the dedicated 3D worker process after its graphics context is created.
"""

from __future__ import annotations

from collections import deque
from typing import Any

from src.visualization.three_d.coords import cell_to_world
from src.visualization.three_d.meshing import SceneLayout, build_scene_layout


class ScenePlayer:
    """Build merged static geometry and animate only frozen simulation events."""

    def __init__(self, message: dict[str, Any], ursina_api: dict[str, Any]):
        self.u = ursina_api
        self.grid = message["grid"]
        self.cell_m = float(message["cell_m"])
        self.start_cell = tuple(message["start_cell"])
        self.robot_cell = tuple(message.get("robot_cell", self.start_cell))
        self.speed_m_per_s = float(message["speed_m_per_s"])
        self.playback_speed = float(message.get("playback_speed", 1.0))
        self.layout: SceneLayout = build_scene_layout(
            self.grid, self.cell_m, message.get("metadata"),
            wall_height_m=float(message.get("wall_height_m", 2.7)),
        )
        self.entities = []
        self.pending: deque[dict[str, Any]] = deque()
        self.playing = True
        self.step_once = False
        self.moving = False
        self.elapsed = 0.0
        self.move_duration = 0.0
        self.move_from = cell_to_world(self.robot_cell, self.cell_m)
        self.move_to = self.move_from
        self.path_cells = list(map(tuple, message.get("initial_path", ())))
        if not self.path_cells:
            self.path_cells = [self.robot_cell]
        self.cleaned_cells = {tuple(cell) for cell in message.get("cleaned_cells", ())}
        self._route_mesh_counter = 0
        self._clean_mesh_counter = 0
        self._make_static_geometry()
        self._make_dynamic_meshes()
        self.robot = self._make_robot(float(message["robot_diameter_m"]))
        self._sync_robot(self.move_from)
        self._make_camera()
        self._make_room_labels(message.get("metadata", {}).get("spec"))
        self._make_hud()
        # Include the editor camera and the worker's two lights as scene nodes.
        self.entity_count = len(self.entities) + 3

    def _entity(self, **kwargs):
        entity = self.u["Entity"](**kwargs)
        self.entities.append(entity)
        return entity

    def _rect_entity(self, rect, *, height: float, y: float, color_value):
        cell = self.cell_m
        x0, x1 = rect.col * cell, (rect.col + rect.width) * cell
        z0, z1 = -rect.row * cell, -(rect.row + rect.height) * cell
        return self._entity(model="cube", position=((x0+x1)/2, y, (z0+z1)/2),
            scale=(rect.width*cell, height, rect.height*cell), color=color_value,
            collider=None, texture=None)

    def _make_static_geometry(self):
        u = self.u
        for rect in self.layout.floors:
            self._rect_entity(rect, height=.04, y=-.02, color_value=u["color"].rgb(218, 216, 205))
        for rect in self.layout.walls:
            self._rect_entity(rect, height=self.layout.wall_height_m,
                              y=self.layout.wall_height_m/2,
                              color_value=u["color"].rgb(93, 99, 110))
        for obstacle in self.layout.objects:
            is_column=obstacle.name.upper()=="C1" or "column" in obstacle.name.lower()
            shade = u["color"].rgb(105, 116, 132) if is_column else u["color"].rgb(139, 115, 85)
            for rect in obstacle.rectangles:
                self._rect_entity(rect, height=obstacle.height_m, y=obstacle.height_m/2, color_value=shade)

    @staticmethod
    def _mesh(u, vertices, triangles):
        mesh = u["Mesh"](vertices=vertices, triangles=triangles, mode="triangle", static=False)
        mesh.generate()
        return mesh

    def _make_dynamic_meshes(self):
        u = self.u
        self.route_entity = self._entity(model=None, color=u["color"].rgb(203, 51, 44),
                                         double_sided=True, collider=None)
        self.cleaned_entity = self._entity(model=None,
            color=u["color"].rgba(45, 163, 104, 170), double_sided=True, collider=None)

    def _make_robot(self, diameter: float):
        u = self.u
        x, _, z = cell_to_world(self.robot_cell, self.cell_m)
        body = self._entity(model="cylinder", position=(x, diameter*.12, z),
            scale=(diameter, diameter*.24, diameter), color=u["color"].rgb(38, 117, 219), collider=None)
        self.robot_indicator=self._entity(model="sphere", position=(x, diameter*.30, z-diameter*.26),
            scale=(diameter*.18, diameter*.18, diameter*.18), color=u["color"].rgb(255, 194, 61), collider=None)
        self.robot_diameter = diameter
        return body

    def _make_camera(self):
        u = self.u
        rows, cols = len(self.grid), len(self.grid[0])
        self.center = (cols*self.cell_m/2, 0.0, -rows*self.cell_m/2)
        self.camera = u["EditorCamera"](rotation=(50, 0, 0), position=(self.center[0], max(rows,cols)*self.cell_m*.8, self.center[2]+max(rows,cols)*self.cell_m*.8),
                                         rotation_speed=150, pan_speed=(2,2), zoom_speed=1.15)
        self.camera.look_at(self.u["Vec3"](*self.center))
        u["camera"].fov = 55
        try:
            u["camera"].lens.setNearFar(.02, max(rows,cols)*self.cell_m*8)
        except AttributeError:
            pass
        self.reset_camera_position = self.camera.position

    def _make_room_labels(self, spec):
        if not isinstance(spec, dict):
            return
        u = self.u
        metadata = spec.get("parameters", {})
        domain = spec.get("domain_px", (0,0,0,0))
        origin_x, origin_y = domain[:2]
        ppm = float(metadata.get("ppm", 0))
        if ppm <= 0:
            return
        for name, (x0,y0,x1,y1) in spec.get("rooms", {}).items():
            x=((x0+x1)/2-origin_x)/ppm; z=-((y0+y1)/2-origin_y)/ppm
            label = u["Text"](text=str(name), position=(x,.04,z), scale=.22,
                              billboard=True, color=u["color"].black)
            self.entities.append(label)

    def _make_hud(self):
        u=self.u
        self.hud=u["Text"](text="Ready · drag to orbit · wheel to zoom · T top · F follow · R reset",
                           position=(-.86,.47),scale=.8,background=True)
        self.entities.append(self.hud)

    def enqueue(self, event: dict[str, Any]):
        if event.get("type") in {"RunStarted", "SearchStarted", "SearchFinished", "TargetSelected",
                                  "MoveExecuted", "CellsCleaned", "ResourceUpdated", "TargetUnreachable", "RunStopped"}:
            self.pending.append(event)

    def control(self, message: dict[str, Any]):
        command=message.get("cmd")
        if command=="play":self.playing=True; self.step_once=False
        elif command=="pause":self.playing=False; self.step_once=False
        elif command=="step":self.playing=False; self.step_once=True
        elif command=="speed":self.playback_speed=max(.25,min(16.0,float(message.get("value",1))))
        elif command=="reset":self.reset(tuple(message.get("cell",self.start_cell)))
        elif command=="seek":
            cell=tuple(message.get("cell",self.robot_cell)); self.reset(cell)
            self.cleaned_cells={tuple(c) for c in message.get("cleaned_cells",())}; self._refresh_cleaned_mesh()

    def reset(self, cell):
        self.pending.clear(); self.moving=False; self.playing=False; self.step_once=False
        self.robot_cell=tuple(cell); self.path_cells=[self.robot_cell]; self.cleaned_cells.clear()
        self.move_from=cell_to_world(self.robot_cell,self.cell_m); self.move_to=self.move_from
        self._sync_robot(self.move_from); self._refresh_route_mesh(); self._refresh_cleaned_mesh()

    def _sync_robot(self, position):
        x,y,z=position
        self._sync_robot_xyz(x,y,z)

    def _sync_robot_xyz(self,x,y,z):
        self.robot.x=x; self.robot.y=y+self.robot_diameter*.12; self.robot.z=z
        self.robot_indicator.x=x; self.robot_indicator.y=y+self.robot_diameter*.30
        self.robot_indicator.z=z-self.robot_diameter*.26

    def _strip_geometry(self, points, width):
        vertices=[]; triangles=[]
        for a,b in zip(points,points[1:]):
            dx,dz=b[0]-a[0],b[2]-a[2]; length=(dx*dx+dz*dz)**.5
            if length==0:continue
            px,pz=-dz/length*width/2,dx/length*width/2
            i=len(vertices)
            vertices.extend([(a[0]+px,a[1],a[2]+pz),(a[0]-px,a[1],a[2]-pz),
                             (b[0]-px,b[1],b[2]-pz),(b[0]+px,b[1],b[2]+pz)])
            triangles.extend([(i,i+1,i+2),(i,i+2,i+3)])
        return vertices,triangles

    def _refresh_route_mesh(self):
        points=[(x,.012,z) for x,_,z in (cell_to_world(c,self.cell_m) for c in self.path_cells)]
        vertices,triangles=self._strip_geometry(points,max(.012,self.cell_m*.12))
        self.route_entity.model=self._mesh(self.u,vertices,triangles) if triangles else None

    def _refresh_cleaned_mesh(self):
        cell=self.cell_m; y=.008; vertices=[]; triangles=[]
        for row,col in sorted(self.cleaned_cells):
            x0=col*cell; x1=(col+1)*cell; z0=-row*cell; z1=-(row+1)*cell; i=len(vertices)
            vertices.extend([(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)])
            triangles.extend([(i,i+1,i+2),(i,i+2,i+3)])
        self.cleaned_entity.model=self._mesh(self.u,vertices,triangles) if triangles else None

    def _apply_event(self,event):
        kind=event.get("type"); payload=event.get("payload",{})
        if kind=="CellsCleaned":
            self.cleaned_cells.update(tuple(c) for c in payload.get("cells",()))
            self._clean_mesh_counter+=len(payload.get("cells",()))
            if self._clean_mesh_counter>=64:self._refresh_cleaned_mesh(); self._clean_mesh_counter=0
        elif kind=="MoveExecuted":
            target=tuple(payload["position"])
            self.move_from=(self.robot.position.x-self.robot_diameter*.0,
                            self.robot.position.y-self.robot_diameter*.12,
                            self.robot.position.z)
            self.move_to=cell_to_world(target,self.cell_m)
            self.robot_cell=target; self.elapsed=0.0
            self.move_duration=max(.001,self.cell_m/self.speed_m_per_s/self.playback_speed)
            self.moving=True
        elif kind=="RunStopped":
            self._refresh_route_mesh(); self._refresh_cleaned_mesh(); self.playing=False
            self.hud.text=f"Stopped: {payload.get('reason','unknown')} · {len(self.path_cells)-1} moves"
        elif kind=="TargetSelected":
            self.hud.text=f"Coverage target: {payload.get('target')}"

    def update(self, delta_time: float):
        # Keep the camera above the floor and bound its perspective zoom to a
        # useful range; EditorCamera still handles orbit, pan and mouse zoom.
        self.camera.y=max(.25,self.camera.y)
        dimension=max(len(self.grid),len(self.grid[0]))*self.cell_m
        self.camera.target_z=max(-dimension*3,min(-1.0,self.camera.target_z))
        if self.moving:
            self.elapsed+=max(0.0,float(delta_time))
            alpha=min(1.0,self.elapsed/self.move_duration)
            a=self.move_from; b=self.move_to
            self._sync_robot_xyz(a[0]+(b[0]-a[0])*alpha,
                                 a[1]+(b[1]-a[1])*alpha,
                                 a[2]+(b[2]-a[2])*alpha)
            if alpha>=1:
                self.moving=False; self.path_cells.append(self.robot_cell)
                self._route_mesh_counter+=1
                if self._route_mesh_counter>=24:self._refresh_route_mesh(); self._route_mesh_counter=0
                if self.step_once:self.step_once=False; self.playing=False
            return
        if not (self.playing or self.step_once) or not self.pending:
            return
        event=self.pending.popleft(); self._apply_event(event)
        if self.step_once and event.get("type")!="MoveExecuted" and not self.pending:
            self.step_once=False

    def camera_preset(self, preset: str):
        if preset=="top":
            rows,cols=len(self.grid),len(self.grid[0])
            # EditorCamera normally keeps its camera at local z=-20. That
            # offset is useful for perspective orbiting but makes a top-down
            # map view point past the floor; centre the camera on its pivot.
            self.u["camera"].position=(0,0,0)
            self.camera.position=(self.center[0],max(rows,cols)*self.cell_m*1.2,self.center[2])
            self.camera.rotation=(270,0,0)
        elif preset=="follow":
            x,_,z=self.robot.position
            self.camera.position=(x+self.cell_m*3,self.robot.position.y+self.cell_m*10,z+self.cell_m*5)
            self.camera.look_at(self.robot.position)
        else:
            self.camera.position=self.reset_camera_position
            self.camera.look_at(self.u["Vec3"](*self.center))
