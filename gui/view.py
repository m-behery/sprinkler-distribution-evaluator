#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 03:17:40 2025

@author: mohamed
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QComboBox, QDoubleSpinBox,
    QTableWidgetItem, QPushButton, QSlider, QStyledItemDelegate, QHBoxLayout,
    QGridLayout, QGroupBox, QFormLayout, QHeaderView, QFrame
)
from PyQt5.QtGui import QColor, QBrush, QDoubleValidator
from PyQt5.QtCore import Qt, QTimer
import numpy as np
from viewmodel import ViewModel
from utils import write_csv
from sprinklers import evaluate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Canvas4ImageAs3D(FigureCanvas):
    
    def __init__(self, parent=None, w=5, h=4, dpi=100):
        self.fig = Figure((w, h), dpi)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.setEnabled(True)
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
    def mousePressEvent(self, event): pass
    def mouseReleaseEvent(self, event): pass
    def mouseDoubleClickEvent(self, event): pass
    def mouseMoveEvent(self, event): pass
    def wheelEvent(self, event): pass
    
    def plot(self, image, resolution, deg_angles):
        h, w = image.shape
        x_range, y_range = np.arange(w) / resolution, np.arange(h) / resolution
        x_map, y_map = np.meshgrid(x_range, y_range)
        self.ax.clear()
        self.ax.plot_surface(x_map, y_map, image, cmap='viridis', edgecolor='none')
        self.ax.view_init(*deg_angles)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.set_zlabel('Pr (mm/hr)')
        self.draw()
        
    def keyPressEvent(self, event):
        step = 1 if event.modifiers() & Qt.ShiftModifier else 5
        
        elev, azim = self.ax.elev, self.ax.azim

        if event.key() == Qt.Key_W:      # Tilt up
            elev += step
        elif event.key() == Qt.Key_S:    # Tilt down
            elev -= step
        elif event.key() == Qt.Key_A:    # Rotate left
            azim -= step
        elif event.key() == Qt.Key_D:    # Rotate right
            azim += step

        self.ax.view_init(elev=elev, azim=azim)
        self.draw()

class NumericDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if editor:
            validator = QDoubleValidator(editor)
            validator.setBottom(0.0)
            validator.setTop(1e2)
            validator.setDecimals(2)
            editor.setValidator(validator)
        return editor

class View(QWidget):
    
    EVAL_DELAY = 1000
    CELL_SIZE = 40
    MAX_DISPLAY_LIMIT = 10
    MIN_DISPLAY_LIMIT = 3
    
    def __init__(self, viewmodel:ViewModel):
        super().__init__()
        self.zero_input_flag = False
        self.viewmodel = viewmodel
        self.init_ui()
        self.bind_viewmodel()
    
    def init_ui(self):
        
# =============================================================================
#         self.evaluation_timer = QTimer(self)
#         self.evaluation_timer.setSingleShot(True)
#         self.evaluation_timer.timeout.connect(self.update_evaluation_result)
#         
#         self.setWindowTitle('Sprinkler Distribution Evaluator')
#         
#         self.main_layout = QHBoxLayout()
#         self.setLayout(self.main_layout)
#         
#         self.parameters_wrapper_layout = QVBoxLayout()
#         self.main_layout.addLayout(self.parameters_wrapper_layout)
#         
#         self.parameters_groupbox = QGroupBox('Parameters')
#         self.parameters_wrapper_layout.addWidget(self.parameters_groupbox)
#         self.parameters_wrapper_layout.addStretch()
#         
#         self.parameters_layout = QVBoxLayout()
#         self.parameters_groupbox.setLayout(self.parameters_layout)
#         
#         self.resolution_label = QLabel('Resolution: 5')
#         self.parameters_layout.addWidget(self.resolution_label)
#         
#         self.resolution_slider = QSlider(Qt.Horizontal)
#         self.resolution_slider.setRange(5, 100)
#         self.parameters_layout.addWidget(self.resolution_slider)
#         
#         self.zone_groupbox = QGroupBox('Zone')
#         self.zone_layout   = QVBoxLayout()
#         self.zone_groupbox.setLayout(self.zone_layout)
#         self.parameters_layout.addWidget(self.zone_groupbox)
#         
#         self.zone_dim_a_layout = QHBoxLayout()
#         self.zone_layout.addLayout(self.zone_dim_a_layout)
#         
#         self.zone_dim_a_label = QLabel("Width (m):")
#         self.zone_dim_a_label.setFixedWidth(70)
#         self.zone_dim_a_layout.addWidget(self.zone_dim_a_label)
#         
#         self.zone_dim_a_spinbox = QDoubleSpinBox()
#         self.zone_dim_a_spinbox.setDecimals(2)
#         self.zone_dim_a_spinbox.setSingleStep(0.1)
#         self.zone_dim_a_spinbox.setRange(1.0, 1e3)
#         self.zone_dim_a_layout.addWidget(self.zone_dim_a_spinbox)
#         
#         self.zone_dim_b_layout = QHBoxLayout()
#         self.zone_layout.addLayout(self.zone_dim_b_layout)
#         
#         self.zone_dim_b_label = QLabel("Height (m):")
#         self.zone_dim_b_label.setFixedWidth(70)
#         self.zone_dim_b_layout.addWidget(self.zone_dim_b_label)
#         
#         self.zone_dim_b_spinbox = QDoubleSpinBox()
#         self.zone_dim_b_spinbox.setDecimals(2)
#         self.zone_dim_b_spinbox.setSingleStep(0.1)
#         self.zone_dim_b_spinbox.setRange(1.0, 1e3)
#         self.zone_dim_b_layout.addWidget(self.zone_dim_b_spinbox)
#         
#         self.config_groupbox = QGroupBox('Sprinklers')
#         self.config_layout   = QVBoxLayout()
#         self.config_groupbox.setLayout(self.config_layout)
#         self.parameters_layout.addWidget(self.config_groupbox)
#         
#         self.config_selector_layout = QHBoxLayout()
#         self.config_layout.addLayout(self.config_selector_layout)
#         
#         self.config_selector_label = QLabel("Configuration:")
#         self.config_selector_label.setFixedWidth(70)
#         self.config_selector_layout.addWidget(self.config_selector_label)
#         
#         self.config_dropdown = QComboBox()
#         self.config_dropdown.addItems(['Triangle', 'Rectangle'])
#         self.config_selector_layout.addWidget(self.config_dropdown)
#         
#         self.config_dim_a_layout = QHBoxLayout()
#         self.config_layout.addLayout(self.config_dim_a_layout)
#         
#         self.config_dim_a_label = QLabel("Width (m):")
#         self.config_dim_a_label.setFixedWidth(70)
#         self.config_dim_a_layout.addWidget(self.config_dim_a_label)
#         
#         self.config_dim_a_spinbox = QDoubleSpinBox()
#         self.config_dim_a_spinbox.setDecimals(2)
#         self.config_dim_a_spinbox.setSingleStep(0.1)
#         self.config_dim_a_spinbox.setRange(0.5, 20.0)
#         self.config_dim_a_layout.addWidget(self.config_dim_a_spinbox)
#         
#         self.config_dim_b_layout = QHBoxLayout()
#         self.config_layout.addLayout(self.config_dim_b_layout)
#         
#         self.config_dim_b_label = QLabel("Height (m):")
#         self.config_dim_b_label.setFixedWidth(70)
#         self.config_dim_b_layout.addWidget(self.config_dim_b_label)
#         
#         self.config_dim_b_spinbox = QDoubleSpinBox()
#         self.config_dim_b_spinbox.setDecimals(2)
#         self.config_dim_b_spinbox.setSingleStep(0.1)
#         self.config_dim_b_spinbox.setRange(0.5, 20.0)
#         self.config_dim_b_layout.addWidget(self.config_dim_b_spinbox, stretch=50)
#         
#         self.measurement_groupbox = QGroupBox('Sprinkler Measurements')
#         self.measurement_layout   = QVBoxLayout()
#         self.measurement_groupbox.setLayout(self.measurement_layout)
#         self.parameters_layout.addWidget(self.measurement_groupbox)
#         
#         self.Pr_step_layout = QHBoxLayout()
#         self.measurement_layout.addLayout(self.Pr_step_layout)
#         
#         self.Pr_step_label = QLabel("Step (m):")
#         self.Pr_step_label.setFixedWidth(70)
#         self.Pr_step_layout.addWidget(self.Pr_step_label)
#         
#         self.Pr_step_spinbox = QDoubleSpinBox()
#         self.Pr_step_spinbox.setDecimals(2)
#         self.Pr_step_spinbox.setSingleStep(0.1)
#         self.Pr_step_spinbox.setRange(0.1, 20.0)
#         self.Pr_step_layout.addWidget(self.Pr_step_spinbox)
#         
#         self.table = QTableWidget()
#         self.table.setItemDelegate(NumericDelegate(self.table))
#         self.measurement_layout.addWidget(self.table)
#         
#         self.apply_button = QPushButton('Export Table')
#         self.measurement_layout.addWidget(self.apply_button)
#         
#         self.zone_canvas = Canvas4ImageAs3D(self)
#         self.homogenous_plot_canvas = Canvas4ImageAs3D(self)
# =============================================================================
        
# =============================================================================
#         self.layout.addWidget(self.zone_canvas)
#         self.layout.addWidget(self.homogenous_plot_canvas)
# =============================================================================

        # --- Window setup ---
        self.setWindowTitle("💧 Sprinkler Distribution Evaluator")
        self.resize(900, 600)

        # --- Timer ---
        self.evaluation_timer = QTimer(self)
        self.evaluation_timer.setSingleShot(True)
        self.evaluation_timer.timeout.connect(self.update_evaluation_result)

        # --- Main layout ---
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        # --- Left Panel (Parameters) ---
        self.parameters_panel = QVBoxLayout()
        self.parameters_panel.setSpacing(12)
        self.main_layout.addLayout(self.parameters_panel, stretch=1)

        # ================= PARAMETERS =================
        self.parameters_groupbox = QGroupBox("General")
        self.parameters_layout = QVBoxLayout(self.parameters_groupbox)

        # Resolution
        self.resolution_label = QLabel("Resolution: 5")
        self.resolution_slider = QSlider(Qt.Horizontal)
        self.resolution_slider.setRange(5, 100)

        self.parameters_layout.addWidget(self.resolution_label)
        self.parameters_layout.addWidget(self.resolution_slider)
        self.parameters_panel.addWidget(self.parameters_groupbox)

        # ================= ZONE =================
        self.zone_groupbox = QGroupBox("Zone")
        zone_form = QFormLayout(self.zone_groupbox)

        self.zone_dim_a_spinbox = self._make_spinbox(1.0, 1000.0)
        zone_form.addRow("Width (m):", self.zone_dim_a_spinbox)

        self.zone_dim_b_spinbox = self._make_spinbox(1.0, 1000.0)
        zone_form.addRow("Height (m):", self.zone_dim_b_spinbox)

        self.parameters_panel.addWidget(self.zone_groupbox)

        # ================= SPRINKLERS =================
        self.config_groupbox = QGroupBox("Sprinklers")
        config_layout = QVBoxLayout(self.config_groupbox)

        # Config selector
        config_selector_layout = QHBoxLayout()
        config_selector_label = QLabel("Configuration:")
        self.config_dropdown = QComboBox()
        self.config_dropdown.addItems(["Triangle", "Rectangle"])
        config_selector_layout.addWidget(config_selector_label)
        config_selector_layout.addWidget(self.config_dropdown, stretch=1)
        config_layout.addLayout(config_selector_layout)

        # Width row (preserve explicit label)
        self.config_dim_a_layout = QHBoxLayout()
        self.config_dim_a_label = QLabel("Width (m):")
        self.config_dim_a_label.setFixedWidth(70)
        self.config_dim_a_spinbox = self._make_spinbox(0.5, 20.0)
        self.config_dim_a_layout.addWidget(self.config_dim_a_label)
        self.config_dim_a_layout.addWidget(self.config_dim_a_spinbox)
        config_layout.addLayout(self.config_dim_a_layout)

        # Height row (preserve explicit label)
        self.config_dim_b_layout = QHBoxLayout()
        self.config_dim_b_label = QLabel("Height (m):")
        self.config_dim_b_label.setFixedWidth(70)
        self.config_dim_b_spinbox = self._make_spinbox(0.5, 20.0)
        self.config_dim_b_layout.addWidget(self.config_dim_b_label)
        self.config_dim_b_layout.addWidget(self.config_dim_b_spinbox)
        config_layout.addLayout(self.config_dim_b_layout)

        self.parameters_panel.addWidget(self.config_groupbox)

        # ================= MEASUREMENTS =================
        self.measurement_groupbox = QGroupBox("Pr Measurements")
        measurement_layout = QVBoxLayout(self.measurement_groupbox)

        form = QFormLayout()
        self.Pr_step_spinbox = self._make_spinbox(0.1, 20.0)
        form.addRow("Step (m):", self.Pr_step_spinbox)
        measurement_layout.addLayout(form)

        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("QTableWidget { gridline-color: #aaa; }")
        measurement_layout.addWidget(self.table)

        # Export button
        self.apply_button = QPushButton("📤 Export Table")
        measurement_layout.addWidget(self.apply_button)

        self.parameters_panel.addWidget(self.measurement_groupbox)

        # Stretch at bottom
        self.parameters_panel.addStretch()
        
        # --- Spacing between panels (invisible gap) ---
        self.main_layout.addSpacing(24)  # Adjust value for desired gap

        # --- Right Panel (Plots) ---
        self.plot_panel = QVBoxLayout()
        self.main_layout.addLayout(self.plot_panel, stretch=2)
        
        # Zone canvas group
        self.zone_groupbox_canvas = QGroupBox("Zone")
        self.zone_groupbox_canvas.setAlignment(Qt.AlignHCenter)  # Center title
        zone_canvas_layout = QVBoxLayout(self.zone_groupbox_canvas)
        self.zone_canvas = Canvas4ImageAs3D(self)
        zone_canvas_layout.addWidget(self.zone_canvas)
        self.plot_panel.addWidget(self.zone_groupbox_canvas)
        
        # Homogeneous Plot canvas group
        self.homogenous_groupbox_canvas = QGroupBox("Homogeneous Plot")
        self.homogenous_groupbox_canvas.setAlignment(Qt.AlignHCenter)  # Center title
        homogenous_canvas_layout = QVBoxLayout(self.homogenous_groupbox_canvas)
        self.homogenous_plot_canvas = Canvas4ImageAs3D(self)
        homogenous_canvas_layout.addWidget(self.homogenous_plot_canvas)
        self.plot_panel.addWidget(self.homogenous_groupbox_canvas)

        # --- Apply global stylesheet for polish ---
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #aaa;
                border-radius: 6px;
                margin-top: 8px;
                padding: 6px;
            }
            QLabel {
                font-size: 13px;
            }
            QPushButton {
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 6px;
                background-color: #4caf50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def _make_spinbox(self, minimum, maximum):
        sb = QDoubleSpinBox()
        sb.setDecimals(2)
        sb.setSingleStep(0.1)
        sb.setRange(minimum, maximum)
        sb.setMinimumWidth(80)
        return sb

    def bind_viewmodel(self):
        
        self.resolution_slider.valueChanged.connect(self.viewmodel.set__resolution)
        self.viewmodel.resolution__changed.connect(
            lambda value: (
                self.resolution_slider.setValue(value),
                self.resolution_label.setText(f'Resolution: {value}'),
                self.evaluation_timer.start(self.EVAL_DELAY)
            )
        )
        self.viewmodel.resolution__changed.emit(self.viewmodel.resolution)
        
        self.zone_dim_a_spinbox.valueChanged.connect(self.on_zone_dims_changed)
        self.zone_dim_b_spinbox.valueChanged.connect(self.on_zone_dims_changed)
        self.viewmodel.zone_dim_meters__changed.connect(
            lambda value: (
                self.zone_dim_a_spinbox.setValue(value[0]),
                self.zone_dim_b_spinbox.setValue(value[1]),
                self.evaluation_timer.start(self.EVAL_DELAY)
            )
        )
        self.viewmodel.zone_dim_meters__changed.emit(self.viewmodel.zone_dim_meters)
        
        self.config_dropdown.currentIndexChanged.connect(self.on_config_changed)
        self.config_dim_a_spinbox.valueChanged.connect(self.on_config_dims_changed)
        self.config_dim_b_spinbox.valueChanged.connect(self.on_config_dims_changed)
        self.viewmodel.config_meters__changed.connect(self.on_param_changed__config_meters)
        self.viewmodel.config_meters__changed.emit(self.viewmodel.config_meters)
        self.on_config_changed()
        
        self.Pr_step_spinbox.valueChanged.connect(self.viewmodel.set__Pr_step)
        self.viewmodel.Pr_step__changed.connect(
            lambda value: (
                self.Pr_step_spinbox.setValue(value),
                self.update_header_labels(),
                self.evaluation_timer.start(self.EVAL_DELAY)
            )
        )
        self.viewmodel.Pr_step__changed.emit(self.viewmodel.Pr_step)
        
        self.table.itemChanged.connect(self.update_Pr_grid)
        self.viewmodel.Pr_grid__changed.connect(self.update_table)
        self.update_table(self.viewmodel.Pr_grid)
        
        self.apply_button.clicked.connect(self.on_apply_button_clicked)
        
    def on_Pr_step_changed(self):
        self.viewmodel.set__Pr_step(self.Pr_step_spinbox.value())
        
    def on_param_changed__config_meters(self):
        is_triangle = len(self.viewmodel.config_meters) < 2
        a, b = self.viewmodel.config_meters[0], 0.0
        if not is_triangle:
            b = self.viewmodel.config_meters[1]
            
        self.config_dropdown.setCurrentIndex(0 if is_triangle else 1)
        self.config_dim_a_spinbox.setValue(a)
        self.config_dim_b_spinbox.setValue(b)
        
    def on_zone_dims_changed(self):
        w = self.zone_dim_a_spinbox.value()
        h = self.zone_dim_b_spinbox.value()
        value = (w, h)
        self.viewmodel.set__zone_dim_meters(value)
        self.evaluation_timer.start(self.EVAL_DELAY)
    
    def on_config_changed(self):
        is_triangle = self.config_dropdown.currentIndex() == 0
        self.config_dim_a_label.setText('Side (m):' if is_triangle else 'Width (m):')
        self.config_dim_b_label.setVisible(not is_triangle)
        self.config_dim_b_spinbox.setVisible(not is_triangle)
        self.on_config_dims_changed()
    
    def on_config_dims_changed(self):
        a = self.config_dim_a_spinbox.value()
        b = self.config_dim_b_spinbox.value()
        value = (a, b) if self.config_dim_b_spinbox.isVisible() else (a,)
        self.viewmodel.set__config_meters(value)
        self.evaluation_timer.start(self.EVAL_DELAY)
    
    @staticmethod
    def format_table_item(value:float, max_value:float):
        item = QTableWidgetItem(str(float(value)))
        normalized_value = value / (max_value + 1e-3)
        color = QColor.fromHsv(100, 255, int(255 * normalized_value))
        item.setBackground(QBrush(color))
        if normalized_value < 0.5:
            item.setForeground(QBrush(QColor(255, 255, 255)))
        item.setTextAlignment(Qt.AlignCenter)
        return item
        
    def update_table(self, arr):
        if arr is None:
            return
        self.table.blockSignals(True)
        
        Pr_max = arr.max()
        rows, cols = np.array(arr.shape) + 1
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.update_header_labels()
        for i in range(rows):
            for j in range(cols):
                if i == rows - 1 or j == cols - 1:
                    item = QTableWidgetItem('')
                else:
                    item = self.format_table_item(arr[i, j], Pr_max)                        
                self.table.setItem(i, j, item)
                
        for row in range(rows):
            self.table.setRowHeight(row, self.CELL_SIZE)
        for col in range(cols):
            self.table.setColumnWidth(col, self.CELL_SIZE)
        display_rows, display_cols = map(lambda x: max(self.MIN_DISPLAY_LIMIT, min(x, self.MAX_DISPLAY_LIMIT)), [rows, cols])
        total_height = display_rows * self.CELL_SIZE + 21
        total_width = display_cols * self.CELL_SIZE + 35
        self.table.setFixedSize(total_width, total_height)
        self.parameters_groupbox.setFixedWidth(total_width + 24)
        self.zone_groupbox.setFixedWidth(total_width + 24)
        self.config_groupbox.setFixedWidth(total_width + 24)
        self.measurement_groupbox.setFixedWidth(total_width + 24)
    
        self.table.blockSignals(False)

    def update_header_labels(self):
        header_labels = np.cumsum([self.viewmodel.Pr_step] * self.table.rowCount()).round(1).astype('str')
        self.table.setVerticalHeaderLabels(header_labels)
        self.table.setHorizontalHeaderLabels(header_labels)

    def on_apply_button_clicked(self):
        write_csv(self.viewmodel.csv_filepath, self.viewmodel.Pr_table)
        
    def update_Pr_grid(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        arr = np.empty((rows, cols))
        for i in range(rows):
            for j in range(cols):
                item = self.table.item(i, j)
                conj_item = self.table.item(j, i)
                
                try:
                    value = float(item.text()) if item else 0.0
                except ValueError:
                    value = 0.0
                    
                try:
                    conj_value = float(conj_item.text()) if conj_item else 0.0
                except ValueError:
                    conj_value = 0.0
                
                if value:
                    arr[i, j] = value
                elif not self.zero_input_flag:
                    arr[i, j] = conj_value
                else:
                    arr[i, j] = 0.0
                    
        invalid_rows, invalid_cols = map(lambda x: (arr == 0).all(x), (1, 0))
        arr = arr[~invalid_rows, :]
        arr = arr[:, ~invalid_cols]
        if arr.size < 4:
            arr = np.zeros((2,2))
        self.viewmodel.set__Pr_grid(arr)
        self.update_table(arr)
        self.evaluation_timer.start(self.EVAL_DELAY)
        
    def keyPressEvent(self, event):
        self.zero_input_flag = event.text() == '0'
        if self.zero_input_flag:
            selected_items = self.table.selectedItems()
            self.table.blockSignals(True)
            for item in selected_items:
                item.setText('0.0')
            self.table.blockSignals(False)
            self.update_Pr_grid()
            self.zero_input_flag = False
            
    def update_evaluation_result(self):
        result = evaluate(
            self.viewmodel.resolution, 
            self.viewmodel.zone_dim_meters,
            self.viewmodel.config_meters,
            self.viewmodel.Pr_table
        )
        self.viewmodel.set__evaluation_result(result)
        print(f'Metrics - CU: {result.metrics.CU}, DU: {result.metrics.DU}')
        self.zone_canvas.plot(result.zone, self.viewmodel.resolution, (45,45))
        self.homogenous_plot_canvas.plot(result.homogenous_plot, self.viewmodel.resolution, (45,45))

# =============================================================================
# def write_config(self):
#     serialize_floats = lambda floats: ', '.join(map(str, floats))
#     self.parser.set('Display', 'RESOLUTION', str(self.resolution))
#     self.parser.set('Sprinklers', 'ZONE_DIM_METERS', serialize_floats(self.zone_dim_meters))
#     self.parser.set('Sprinklers', 'CONFIG_METERS', serialize_floats(self.config_meters))
#     self.parser.set('Sprinklers', 'CSV_FILEPATH', self.csv_filepath)
#     self.parser.write()
# =============================================================================