#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 18:36:52 2025

@author: mohamed
"""

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QHeaderView, QDoubleSpinBox
from PyQt5.QtCore import Qt
import numpy as np
import constants

class Canvas4ImageAs3D(FigureCanvasQTAgg):
    """
    3D Matplotlib canvas to display images as surface plots,
    with optional keyboard rotation and disabled mouse interaction.
    """
    def __init__(self, parent=None, w=5, h=4, dpi=100, minimum_width=500):
        fig = Figure((w, h), dpi)
        super().__init__(fig)
        self.ax = fig.add_subplot(111, projection='3d')
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumWidth(minimum_width)
        
    def plot(self, image, resolution, deg_angles):
        """
        Render a 3D surface plot from a 2D image array with proper axis scaling.
    
        Parameters:
            image: 2D numpy array representing Pr values
            resolution: spatial resolution in meters per pixel
            deg_angles: tuple (elev, azim) for initial viewing angles in degrees
        """
        h, w = image.shape
        x_range = np.arange(w) / resolution
        y_range = np.arange(h) / resolution
        x_map, y_map = np.meshgrid(x_range, y_range)
    
        self.ax.clear()
        self.ax.plot_surface(x_map, y_map, image, cmap='viridis', edgecolor='none')
        self.ax.view_init(*deg_angles)
        self.ax.set_xlabel('x (m)', labelpad=10)
        self.ax.set_ylabel('y (m)', labelpad=10)
        self.ax.set_zlabel('Pr (mm/hr)', labelpad=10)
        
        dx = x_range.max() - x_range.min()
        dy = y_range.max() - y_range.min()
        dz = 0.5 * (dx + dy)
        self.ax.set_box_aspect([dx, dy, dz])
    
        self.draw()

    def mousePressEvent(self, event):       pass
    def mouseReleaseEvent(self, event):     pass
    def mouseDoubleClickEvent(self, event): pass
    def mouseMoveEvent(self, event):        pass
    def wheelEvent(self, event):            pass
    
    def keyPressEvent(self, event):
        """
        Rotate the 3D plot using WASD keys:
            W/S: Elevation up/down
            A/D: Azimuth left/right
        Shift modifier reduces rotation step to 1 degree.
        """
        degrees = 1 if event.modifiers() & Qt.ShiftModifier else 5
        match event.key():
            case Qt.Key_W:
                self.ax.elev += degrees
            case Qt.Key_S:
                self.ax.elev -= degrees
            case Qt.Key_A:
                self.ax.azim -= degrees
            case Qt.Key_D:
                self.ax.azim += degrees
        self.draw()
        
class DoubleSpinBox(QDoubleSpinBox):
    """
    QDoubleSpinBox with preset defaults for decimals, step, and minimum width.
    """
    def __init__(self, minimum, maximum, decimals=2, single_step=0.1, minimum_width=80):
        super().__init__()
        self.setDecimals(decimals)
        self.setSingleStep(single_step)
        self.setRange(minimum, maximum)
        self.setMinimumWidth(minimum_width)

class Header(QHeaderView):
    """
    Base QHeaderView class with fixed size sections and centered alignment.
    """
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter)
        self.setSectionResizeMode(QHeaderView.Fixed)
        self.setDefaultSectionSize(constants.Cells.SIZE)

class SimpleHeader(Header):
    """
    Horizontal header with centered text.
    """
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
        if text is not None:
            painter.drawText(rect, Qt.AlignCenter, str(text))
        painter.restore()

class RotatedHeader(Header):
    """
    Vertical header with rotated text (-90 degrees) for compact display.
    """
    def __init__(self, parent=None):
        super().__init__(Qt.Vertical, parent)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
        if text is not None:
            painter.translate(rect.x(), rect.y() + rect.height())
            painter.rotate(-90)
            painter.drawText(0, 0, rect.height(), rect.width(),
                             Qt.AlignCenter, str(text))
        painter.restore()