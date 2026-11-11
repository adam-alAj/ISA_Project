"""Accessible, HiDPI-aware QGraphicsView map with simulation overlays."""
from __future__ import annotations

import numpy as np
from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

PALETTE = {0: QColor("#F4F1E8"), 1: QColor("#30343B"), 2: QColor("#E5B94D"), 3: QColor("#168A8A")}


class MapCanvas(QGraphicsView):
    """Paint occupancy and overlays in scene coordinates on a graphics view."""
    cell_clicked = Signal(tuple)

    def __init__(self, parent=None):
        self._scene = QGraphicsScene()
        super().__init__(self._scene, parent)
        self.setMinimumSize(480, 360)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        self.setBackgroundBrush(QColor("#F8FAFC"))
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.grid = None
        self.start = self.goal = self.robot = None
        self.cleaned = np.zeros((0, 0), dtype=bool)
        self.explored: set[tuple[int, int]] = set()
        self.frontier: set[tuple[int, int]] = set()
        self._base_image = QImage()
        self._cleaned_image = QImage()
        self._explored_image = QImage()
        self.path: tuple[tuple[int, int], ...] = ()
        self.pick_mode = "none"
        self.show_grid = True
        self._zoom = 1.0
        self._pan_origin: QPoint | None = None

    def set_map(self, grid, start=None, goal=None):
        incoming = None if grid is None else np.array(grid, dtype=np.uint8, copy=True)
        if (incoming is not None and self.grid is not None and incoming.shape==self.grid.shape
                and np.array_equal(incoming,self.grid)):
            self.start,self.goal=start,goal
            self.robot=start; self.cleaned=np.zeros(incoming.shape,dtype=bool)
            self.explored.clear(); self.frontier.clear(); self.path=()
            if not self._cleaned_image.isNull():self._cleaned_image.fill(Qt.GlobalColor.transparent)
            if not self._explored_image.isNull():self._explored_image.fill(Qt.GlobalColor.transparent)
            self.viewport().update()
            return
        self.grid = incoming
        self.start, self.goal = start, goal
        if self.grid is None:
            self.cleaned = np.zeros((0, 0), dtype=bool); self.scene().setSceneRect(QRectF(0,0,1,1))
            self._base_image=QImage(); self._cleaned_image=QImage(); self._explored_image=QImage()
        else:
            if self.cleaned.shape != self.grid.shape: self.cleaned = np.zeros(self.grid.shape, dtype=bool)
            rows, cols = self.grid.shape; self.scene().setSceneRect(QRectF(0,0,cols,rows))
            self._build_base_image()
            self._cleaned_image=QImage(cols*8,rows*8,QImage.Format.Format_ARGB32); self._cleaned_image.fill(Qt.GlobalColor.transparent)
            self._explored_image=QImage(cols*4,rows*4,QImage.Format.Format_ARGB32); self._explored_image.fill(Qt.GlobalColor.transparent)
            if self._zoom == 1.0: self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.explored.clear(); self.frontier.clear(); self.path = (); self.robot = start
        self.viewport().update()

    def set_overlay(self, *, cleaned=None, explored=None, frontier=None, path=None, robot=None):
        if cleaned is not None and self.grid is not None:
            new_cleaned=np.asarray(cleaned,dtype=bool)
            if new_cleaned.shape==self.grid.shape and not np.array_equal(new_cleaned,self.cleaned):
                changed=np.argwhere(new_cleaned != self.cleaned)
                painter=QPainter(self._cleaned_image)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                for r,c in changed:painter.fillRect(QRectF(int(c)*8,int(r)*8,8,8),Qt.GlobalColor.transparent)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                painter.setPen(QPen(Qt.PenStyle.NoPen)); painter.setBrush(QColor(30,150,90,150))
                for r,c in changed:
                    if new_cleaned[r,c]:painter.drawEllipse(QRectF(int(c)*8+2,int(r)*8+2,4,4))
                painter.end(); self.cleaned=np.array(new_cleaned,copy=True)
        if explored is not None:
            new_explored=set(tuple(cell) for cell in list(explored)[-3000:])
            if new_explored != self.explored and not self._explored_image.isNull():
                removed=self.explored-new_explored; added=new_explored-self.explored
                painter=QPainter(self._explored_image)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                for r,c in removed:painter.fillRect(QRectF(c*4,r*4,4,4),Qt.GlobalColor.transparent)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                painter.setPen(QPen(Qt.PenStyle.NoPen)); painter.setBrush(QColor("#E67E22"))
                for r,c in added:painter.drawEllipse(QRectF(c*4+1,r*4+1,2,2))
                painter.end(); self.explored=new_explored
        if frontier is not None:
            self.frontier=set(tuple(cell) for cell in list(frontier)[-2000:])
        if path is not None: self.path = tuple(tuple(cell) for cell in path)
        if robot is not None: self.robot = tuple(robot)
        self.viewport().update()

    def _build_base_image(self):
        rows,cols=self.grid.shape; scale=8
        image=QImage(cols*scale,rows*scale,QImage.Format.Format_RGB32)
        painter=QPainter(image)
        for r in range(rows):
            for c in range(cols):
                state=int(self.grid[r,c]); cell=QRectF(c*scale,r*scale,scale,scale)
                painter.fillRect(cell,PALETTE.get(state,PALETTE[2]))
                if state==1:
                    painter.setPen(QPen(QColor("#62676F"),1)); painter.drawLine(c*scale,r*scale,(c+1)*scale,(r+1)*scale); painter.drawLine((c+1)*scale,r*scale,c*scale,(r+1)*scale)
                elif state==2:
                    painter.setPen(QPen(QColor("#8A6814"),1)); painter.drawLine(c*scale,(r+1)*scale,(c+1)*scale,r*scale)
                elif state==3:
                    painter.setPen(QPen(QColor("#063F46"),1.5)); painter.drawLine(c*scale+2,r*scale+4,(c+1)*scale-2,r*scale+4)
        painter.end(); self._base_image=image

    def render_content(self, width: int, height: int, *, include_marker_labels: bool = True) -> QImage:
        """Render map content at an exact pixel size without widget chrome.

        This is also used for DPI-independent golden images; it invokes the
        same cached occupancy and overlay painting used by the live view.
        """
        image = QImage(width, height, QImage.Format.Format_RGBA8888)
        image.fill(QColor("#F8FAFC"))
        if self.grid is None:
            return image
        rows, cols = self.grid.shape
        scene_rect = QRectF(0, 0, cols, rows)
        painter = QPainter(image)
        painter.scale(width / cols, height / rows)
        show_grid = self.show_grid
        show_labels = getattr(self, "show_marker_labels", True)
        self.show_grid = False  # Fixed scale makes optional grid spacing ambiguous.
        self.show_marker_labels = include_marker_labels
        try:
            self.drawBackground(painter, scene_rect)
            self.drawForeground(painter, scene_rect)
        finally:
            self.show_grid = show_grid
            self.show_marker_labels = show_labels
            painter.end()
        return image

    def set_pick_mode(self, mode: str):
        self.pick_mode = mode
        self.setCursor(Qt.CursorShape.CrossCursor if mode != "none" else Qt.CursorShape.ArrowCursor)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.fillRect(rect, QColor("#F8FAFC"))
        if self.grid is None:
            painter.setPen(QColor("#475569")); painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Load a map to begin")
            return
        rows,cols=self.grid.shape; scene=QRectF(0,0,cols,rows)
        painter.drawImage(scene,self._base_image)
        if self.show_grid and self.transform().m11() >= 5:
            painter.setPen(QPen(QColor(80,90,100,35),.015))
            for r in range(rows+1):painter.drawLine(QPointF(0,r),QPointF(cols,r))
            for c in range(cols+1):painter.drawLine(QPointF(c,0),QPointF(c,rows))

    def drawForeground(self,painter:QPainter,rect:QRectF):
        if self.grid is None:return
        painter.save(); scene=QRectF(0,0,self.grid.shape[1],self.grid.shape[0])
        if not self._cleaned_image.isNull():painter.drawImage(scene,self._cleaned_image)
        if not self._explored_image.isNull():painter.drawImage(scene,self._explored_image)
        if self.path:
            painter.setPen(QPen(QColor("#B42318"),.45,Qt.PenStyle.SolidLine,Qt.PenCapStyle.RoundCap))
            points=QPolygonF([QPointF(c+.5,r+.5) for r,c in self.path])
            if len(points) > 1:
                painter.drawPolyline(points)
        if self.frontier:
            painter.setPen(QPen(QColor("#7A3E9D"),.06)); painter.setBrush(Qt.BrushStyle.NoBrush)
            for r,c in self.frontier:
                painter.drawPolygon(QPolygonF((QPointF(c+.5,r+.12),QPointF(c+.88,r+.5),QPointF(c+.5,r+.88),QPointF(c+.12,r+.5))))
        self._marker(painter,self.start,"S",QColor("#155EEF"),False)
        self._marker(painter,self.goal,"G",QColor("#7A3E9D"),False)
        self._marker(painter,self.robot,"R",QColor("#D92D20"),True)
        painter.restore()

    def _marker(self,painter,cell,label,color,circle):
        if cell is None:return
        r,c=cell; rect=QRectF(c+.12,r+.12,.76,.76)
        painter.setPen(QPen(QColor("white"),.06)); painter.setBrush(color)
        if circle:painter.drawEllipse(rect)
        else:painter.drawRect(rect)
        if getattr(self, "show_marker_labels", True):
            font=QFont("Segoe UI"); font.setWeight(QFont.Weight.Bold); font.setPointSizeF(.38); painter.setFont(font); painter.setPen(Qt.GlobalColor.white)
            painter.drawText(rect,Qt.AlignmentFlag.AlignCenter,label)

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.MiddleButton:
            self._pan_origin=event.position().toPoint(); self.setCursor(Qt.CursorShape.ClosedHandCursor); return
        if event.button()==Qt.MouseButton.LeftButton and self.pick_mode!="none" and self.grid is not None:
            p=self.mapToScene(event.position().toPoint()); c=int(np.floor(p.x())); r=int(np.floor(p.y()))
            rows,cols=self.grid.shape
            if 0<=r<rows and 0<=c<cols:self.cell_clicked.emit((r,c))
        super().mousePressEvent(event)

    def mouseMoveEvent(self,event):
        if self._pan_origin is not None and event.buttons() & Qt.MouseButton.MiddleButton:
            point=event.position().toPoint(); delta=point-self._pan_origin
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value()-delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value()-delta.y()); self._pan_origin=point; return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.MiddleButton:self._pan_origin=None; self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def wheelEvent(self,event):
        factor=1.15 if event.angleDelta().y()>0 else 1/1.15
        if .25 <= self._zoom*factor <= 8:
            self._zoom*=factor; self.scale(factor,factor)
