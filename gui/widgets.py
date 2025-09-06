#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 18:36:52 2025

@author: mohamed
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QComboBox, QDoubleSpinBox,
    QTableWidgetItem, QPushButton, QSlider, QStyledItemDelegate, QHBoxLayout,
    QGridLayout, QGroupBox, QFormLayout, QHeaderView, QFrame, QTextEdit, 
    QLineEdit, QSizePolicy, QFileDialog, QApplication,
)
from PyQt5.QtGui import QColor, QBrush, QDoubleValidator, QIcon, QPalette
from PyQt5.QtCore import Qt, QTimer
import numpy as np
from viewmodel import ViewModel
from utils import write_csv
from sprinklers import evaluate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils import INIParser
from typing import Final

CELL_SIZE = 40

class Header(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(Qt.AlignCenter)
        self.setSectionResizeMode(QHeaderView.Fixed)
        self.setDefaultSectionSize(CELL_SIZE)

class SimpleHeader(Header):
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        text = self.model().headerData(logicalIndex, self.orientation(), Qt.DisplayRole)
        if text is not None:
            painter.drawText(rect, Qt.AlignCenter, str(text))
        painter.restore()

class RotatedHeader(Header):
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

class Canvas4ImageAs3D(FigureCanvas):
    
    def __init__(self, parent=None, w=5, h=4, dpi=100, minimum_width=500):
        fig = Figure((w, h), dpi)
        super().__init__(fig)
        
        self.ax = fig.add_subplot(111, projection='3d')
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumWidth(minimum_width)
    
    def plot(self, image, resolution, deg_angles):
        h, w = image.shape
        x_range, y_range = np.arange(w) / resolution, np.arange(h) / resolution
        x_map, y_map = np.meshgrid(x_range, y_range)
        self.ax.clear()
        self.ax.plot_surface(x_map, y_map, image, cmap='viridis', edgecolor='none')
        self.ax.view_init(*deg_angles)
        self.ax.set_xlabel('x (m)')
        self.ax.set_ylabel('y (m)')
        self.ax.set_zlabel('Pr (mm/hr)')
        self.draw()
        
    def mousePressEvent(self, event):       pass
    def mouseReleaseEvent(self, event):     pass
    def mouseDoubleClickEvent(self, event): pass
    def mouseMoveEvent(self, event):        pass
    def wheelEvent(self, event):            pass
    
    def keyPressEvent(self, event):
        degrees = 5
        shift_pressed = event.modifiers() & Qt.ShiftModifier
        if shift_pressed:
            degrees = 1
            
        elev, azim = self.ax.elev, self.ax.azim
        
        key_pressed = event.key()
        match key_pressed:
            case Qt.Key_W:
                elev += degrees
            case Qt.Key_S:
                elev -= degrees
            case Qt.Key_A:
                azim -= degrees
            case Qt.Key_D:
                azim += degrees

        self.ax.view_init(elev, azim)
        self.draw()
    
class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, minimum, maximum, decimals=2, single_step=0.1, minimum_width=80):
        super().__init__()
        self.setDecimals(decimals)
        self.setSingleStep(single_step)
        self.setRange(minimum, maximum)
        self.setMinimumWidth(minimum_width)