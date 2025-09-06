#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 03:17:40 2025

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

from widgets import DoubleSpinBox, SimpleHeader, RotatedHeader, Canvas4ImageAs3D
from constants import Themes

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
    
    EVAL_DELAY        = 1000
    CELL_SIZE         = 40
    MAX_DISPLAY_LIMIT = 10
    MIN_DISPLAY_LIMIT = 3
    
    def __init__(self, viewmodel:ViewModel, config_parser:INIParser):
        super().__init__()
        self.zero_input_flag = False
        self.viewmodel = viewmodel
        self.config_parser = config_parser
        self.init_ui()
        self.bind_viewmodel()
    
# =============================================================================
#     def init_ui(self):
#         # --- Window setup ---
#         self.setWindowTitle("💧 Sprinkler Distribution Evaluator")
#         self.resize(900, 600)
# 
#         # --- Timer ---
#         self.evaluation_timer = QTimer(self)
#         self.evaluation_timer.setSingleShot(True)
#         self.evaluation_timer.timeout.connect(self.update_evaluation_result)
# 
#         # --- Main layout ---
#         self.main_layout = QHBoxLayout(self)
#         self.setLayout(self.main_layout)
# 
#         # --- Left Panel (Parameters) ---
#         self.parameters_panel = QVBoxLayout()
#         self.parameters_panel.setSpacing(12)
#         self.main_layout.addLayout(self.parameters_panel, stretch=1)
# 
#         # ================= GENERAL ==============
#         self.general_groupbox = QGroupBox("General")
#         self.parameters_layout = QVBoxLayout(self.general_groupbox)
# 
#         # Resolution
#         self.resolution_label = QLabel("Resolution: 5")
#         self.resolution_slider = QSlider(Qt.Horizontal)
#         self.resolution_slider.setRange(5, 100)
# 
#         self.parameters_layout.addWidget(self.resolution_label)
#         self.parameters_layout.addWidget(self.resolution_slider)
#         self.parameters_panel.addWidget(self.general_groupbox)
# 
#         # ================= ZONE =================
#         self.zone_groupbox = QGroupBox("Zone")
#         zone_form = QFormLayout(self.zone_groupbox)
# 
#         self.zone_dim_a_spinbox = DoubleSpinBox(1.0, 1000.0)
#         zone_form.addRow("Width (m):", self.zone_dim_a_spinbox)
# 
#         self.zone_dim_b_spinbox = DoubleSpinBox(1.0, 1000.0)
#         zone_form.addRow("Height (m):", self.zone_dim_b_spinbox)
# 
#         self.parameters_panel.addWidget(self.zone_groupbox)
# 
#         # ================= SPRINKLERS =================
#         self.config_groupbox = QGroupBox("Sprinklers")
#         config_layout = QVBoxLayout(self.config_groupbox)
# 
#         # Config selector
#         config_selector_layout = QHBoxLayout()
#         config_selector_label = QLabel("Configuration:")
#         self.config_dropdown = QComboBox()
#         self.config_dropdown.addItems(["Triangle", "Rectangle"])
#         config_selector_layout.addWidget(config_selector_label)
#         config_selector_layout.addWidget(self.config_dropdown, stretch=1)
#         config_layout.addLayout(config_selector_layout)
# 
#         # Width row (preserve explicit label)
#         self.config_dim_a_layout = QHBoxLayout()
#         self.config_dim_a_label = QLabel("Width (m):")
#         self.config_dim_a_label.setFixedWidth(70)
#         self.config_dim_a_spinbox = DoubleSpinBox(0.5, 20.0)
#         self.config_dim_a_layout.addWidget(self.config_dim_a_label)
#         self.config_dim_a_layout.addWidget(self.config_dim_a_spinbox)
#         config_layout.addLayout(self.config_dim_a_layout)
# 
#         # Height row (preserve explicit label)
#         self.config_dim_b_layout = QHBoxLayout()
#         self.config_dim_b_label = QLabel("Height (m):")
#         self.config_dim_b_label.setFixedWidth(70)
#         self.config_dim_b_spinbox = DoubleSpinBox(0.5, 20.0)
#         self.config_dim_b_layout.addWidget(self.config_dim_b_label)
#         self.config_dim_b_layout.addWidget(self.config_dim_b_spinbox)
#         config_layout.addLayout(self.config_dim_b_layout)
# 
#         self.parameters_panel.addWidget(self.config_groupbox)
# 
#         # ================= MEASUREMENTS =================
#         self.measurement_groupbox = QGroupBox("Pr Measurements")
#         measurement_layout = QVBoxLayout(self.measurement_groupbox)
#         
#         csv_layout = QHBoxLayout()
#         self.csv_path_edit = QLineEdit()
#         self.csv_path_edit.setPlaceholderText("Select your CSV file...")
#         self.csv_path_edit.setEnabled(False)
#         self.csv_browse_button = QPushButton('📝')
#         self.csv_browse_button.setFixedSize(32, 32)
#         self.csv_path_edit.setFixedHeight(32)
#         csv_layout.addWidget(self.csv_path_edit, stretch=1)
#         csv_layout.addWidget(self.csv_browse_button)
#         measurement_layout.addLayout(csv_layout)
#         
#         measurement_layout.addSpacing(10)
#         
#         separator = QFrame()
#         separator.setFrameShape(QFrame.HLine)
#         separator.setFrameShadow(QFrame.Sunken)
#         measurement_layout.addWidget(separator)
#         
#         measurement_layout.addSpacing(10)
# 
#         form = QFormLayout()
#         self.Pr_step_spinbox = DoubleSpinBox(0.1, 20.0)
#         form.addRow("Step (m):", self.Pr_step_spinbox)
#         measurement_layout.addLayout(form)
#         
#         measurement_layout.addSpacing(15)
# 
#         # Table
#         self.table = QTableWidget()
#         self.table.setAlternatingRowColors(True)
#         self.table.setHorizontalHeader(
#             SimpleHeader(self.table)
#         )
#         self.table.setVerticalHeader(
#             RotatedHeader(self.table)
#         )
#         measurement_layout.addWidget(self.table)
# 
#         # Export button
#         self.export_csv_button = QPushButton("📤 Export Table")
#         measurement_layout.addWidget(self.export_csv_button)
# 
#         self.parameters_panel.addWidget(self.measurement_groupbox)
#         
#         # ================= EXPORT CONFIG =================
#         self.export_config_button = QPushButton("📑 Export Config")
#         self.parameters_panel.addWidget(self.export_config_button)
# 
#         # Stretch at bottom
#         self.parameters_panel.addStretch()
#         
#         # --- Spacing between panels (invisible gap) ---
#         self.main_layout.addSpacing(24)  # Adjust value for desired gap
# 
#         # --- Right Panel (Plots) ---
#         self.plot_panel = QVBoxLayout()
#         self.main_layout.addLayout(self.plot_panel, stretch=2)
#         
#         # Zone canvas group
#         self.zone_groupbox_canvas = QGroupBox("Zone")
#         self.zone_groupbox_canvas.setAlignment(Qt.AlignHCenter)  # Center title
#         zone_canvas_layout = QVBoxLayout(self.zone_groupbox_canvas)
#         self.zone_canvas = Canvas4ImageAs3D(self)
#         zone_canvas_layout.addWidget(self.zone_canvas)
#         self.plot_panel.addWidget(self.zone_groupbox_canvas)
#         
#         # Homogeneous Plot canvas group
#         self.homogenous_groupbox_canvas = QGroupBox("Homogeneous Plot")
#         self.homogenous_groupbox_canvas.setAlignment(Qt.AlignHCenter)  # Center title
#         homogenous_canvas_layout = QVBoxLayout(self.homogenous_groupbox_canvas)
#         self.homogenous_plot_canvas = Canvas4ImageAs3D(self)
#         homogenous_canvas_layout.addWidget(self.homogenous_plot_canvas)
#         self.plot_panel.addWidget(self.homogenous_groupbox_canvas)
#         
#         # --- Spacing between panels (invisible gap) ---
#         self.main_layout.addSpacing(8)  # Adjust value for desired gap
#         
#         # --- Metrics Panel (Rightmost side) ---
#         self.metrics_panel = QVBoxLayout()
#         
#         # Title label
#         self.metrics_label = QLabel("Metrics")
#         self.metrics_label.setAlignment(Qt.AlignHCenter)
#         self.metrics_panel.addWidget(self.metrics_label)
#         
#         # Textbox
#         self.metrics_textbox = QTextEdit()
#         self.metrics_textbox.setReadOnly(True)
#         self.metrics_textbox.setFixedWidth(220)
#         self.metrics_panel.addWidget(self.metrics_textbox)
#         
#         # Add to main layout (far right)
#         self.main_layout.addLayout(self.metrics_panel, stretch=0)
#         
#         self.csv_browse_button.setObjectName("csvBrowse")
#         self.export_csv_button.setObjectName("applyButton")
#         self.export_config_button.setObjectName("exportConfig")
#         self.metrics_label.setObjectName("metricsLabel")
#         
#         self.setStyleSheet(Themes.LIGHT)
# =============================================================================

    def init_ui(self):
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
        
        # --- General GroupBox ---
        self.general_groupbox = self._create_general_groupbox()
        self.parameters_panel.addWidget(self.general_groupbox)
        
        # --- Zone GroupBox ---
        self.zone_groupbox = self._create_zone_groupbox()
        self.parameters_panel.addWidget(self.zone_groupbox)
        
        # --- Sprinklers GroupBox ---
        self.config_groupbox = self._create_sprinklers_groupbox()
        self.parameters_panel.addWidget(self.config_groupbox)
        
        # --- Measurements GroupBox ---
        self.measurement_groupbox = self._create_measurements_groupbox()
        self.parameters_panel.addWidget(self.measurement_groupbox)
        
        # --- Export Config Button ---
        self.export_config_button = QPushButton("📑 Export Config")
        self.parameters_panel.addWidget(self.export_config_button)
        
        # Stretch at bottom
        self.parameters_panel.addStretch()
        
        # --- Right Panel (Plots) ---
        self.main_layout.addSpacing(24)
        self.plot_panel = QVBoxLayout()
        self.main_layout.addLayout(self.plot_panel, stretch=2)
        
        self.zone_groupbox_canvas = self._create_canvas_groupbox("Zone")
        self.plot_panel.addWidget(self.zone_groupbox_canvas)
        
        self.homogenous_groupbox_canvas = self._create_canvas_groupbox("Homogeneous Plot")
        self.plot_panel.addWidget(self.homogenous_groupbox_canvas)
        
        self.main_layout.addSpacing(8)
        
        # --- Metrics Panel ---
        self.metrics_panel = QVBoxLayout()
        self.metrics_label = QLabel("Metrics")
        self.metrics_label.setAlignment(Qt.AlignHCenter)
        self.metrics_panel.addWidget(self.metrics_label)
        
        self.metrics_textbox = QTextEdit()
        self.metrics_textbox.setReadOnly(True)
        self.metrics_textbox.setFixedWidth(220)
        self.metrics_panel.addWidget(self.metrics_textbox)
        
        self.main_layout.addLayout(self.metrics_panel, stretch=0)
        
        # --- Object Names for Stylesheet ---
        self.csv_browse_button.setObjectName("csvBrowse")
        self.export_csv_button.setObjectName("applyButton")
        self.export_config_button.setObjectName("exportConfig")
        self.metrics_label.setObjectName("metricsLabel")
        
        self.setStyleSheet(Themes.LIGHT)


    def _create_general_groupbox(self):
        groupbox = QGroupBox("General")
        layout = QVBoxLayout(groupbox)
    
        self.resolution_label = QLabel("Resolution: 5")
        self.resolution_slider = QSlider(Qt.Horizontal)
        self.resolution_slider.setRange(5, 100)
    
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_slider)
        return groupbox
    
    
    def _create_zone_groupbox(self):
        groupbox = QGroupBox("Zone")
        form = QFormLayout(groupbox)
    
        self.zone_dim_a_spinbox = DoubleSpinBox(1.0, 1000.0)
        self.zone_dim_b_spinbox = DoubleSpinBox(1.0, 1000.0)
    
        form.addRow("Width (m):", self.zone_dim_a_spinbox)
        form.addRow("Height (m):", self.zone_dim_b_spinbox)
        return groupbox
    
    
    def _create_sprinklers_groupbox(self):
        groupbox = QGroupBox("Sprinklers")
        layout = QVBoxLayout(groupbox)
    
        # Config selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Configuration:"))
        self.config_dropdown = QComboBox()
        self.config_dropdown.addItems(["Triangle", "Rectangle"])
        selector_layout.addWidget(self.config_dropdown, stretch=1)
        layout.addLayout(selector_layout)
    
        # Width row
        self.config_dim_a_layout = self._create_label_spinbox_row("Width (m):", 0.5, 20.0)
        layout.addLayout(self.config_dim_a_layout)
    
        # Height row
        self.config_dim_b_layout = self._create_label_spinbox_row("Height (m):", 0.5, 20.0)
        layout.addLayout(self.config_dim_b_layout)
    
        return groupbox
    
    
    def _create_measurements_groupbox(self):
        groupbox = QGroupBox("Pr Measurements")
        layout = QVBoxLayout(groupbox)
    
        # CSV file selection
        csv_layout = QHBoxLayout()
        self.csv_path_edit = QLineEdit()
        self.csv_path_edit.setPlaceholderText("Select your CSV file...")
        self.csv_path_edit.setEnabled(False)
        self.csv_browse_button = QPushButton("📝")
        self.csv_browse_button.setFixedSize(32, 32)
        self.csv_path_edit.setFixedHeight(32)
        csv_layout.addWidget(self.csv_path_edit, stretch=1)
        csv_layout.addWidget(self.csv_browse_button)
        layout.addLayout(csv_layout)
        layout.addSpacing(10)
    
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        layout.addSpacing(10)
    
        # Step form
        form = QFormLayout()
        self.Pr_step_spinbox = DoubleSpinBox(0.1, 20.0)
        form.addRow("Step (m):", self.Pr_step_spinbox)
        layout.addLayout(form)
        layout.addSpacing(15)
    
        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeader(SimpleHeader(self.table))
        self.table.setVerticalHeader(RotatedHeader(self.table))
        layout.addWidget(self.table)
    
        # Export button
        self.export_csv_button = QPushButton("📤 Export Table")
        layout.addWidget(self.export_csv_button)
    
        return groupbox
    
    def _create_canvas_groupbox(self, title: str) -> QGroupBox:
        groupbox = QGroupBox(title)
        groupbox.setAlignment(Qt.AlignHCenter)
        layout = QVBoxLayout(groupbox)
        canvas = Canvas4ImageAs3D(self)
        layout.addWidget(canvas)
        if title.lower() == "zone":
            self.zone_canvas = canvas
        else:
            self.homogenous_plot_canvas = canvas
        return groupbox
    
    
    def _create_label_spinbox_row(self, label_text: str, min_val: float, max_val: float) -> QHBoxLayout:
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(70)
        spinbox = DoubleSpinBox(min_val, max_val)
        layout.addWidget(label)
        layout.addWidget(spinbox)
    
        if "Width" in label_text:
            self.config_dim_a_label = label
            self.config_dim_a_spinbox = spinbox
        else:
            self.config_dim_b_label = label
            self.config_dim_b_spinbox = spinbox
        return layout

    def bind_viewmodel(self):    
        self._bind_resolution()
        self._bind_zone_dimensions()
        self._bind_config()
        self._bind_csv_path()
        self._bind_Pr_step()
        self._bind_Pr_table()
        self._bind_exports()
        
    def _bind_resolution(self):
        self.resolution_slider.valueChanged.connect(self.viewmodel.set__resolution)
        self.viewmodel.resolution__changed.connect(
            lambda value: (
                self.resolution_slider.setValue(value),
                self.resolution_label.setText(f'Resolution: {value}'),
                self.evaluation_timer.start(self.EVAL_DELAY)
            )
        )
        self.viewmodel.resolution__changed.emit(self.viewmodel.resolution)
    
    def _bind_zone_dimensions(self):
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
    
    def _bind_config(self):
        self.config_dropdown.currentIndexChanged.connect(self.on_config_changed)
        self.config_dim_a_spinbox.valueChanged.connect(self.on_config_dims_changed)
        self.config_dim_b_spinbox.valueChanged.connect(self.on_config_dims_changed)
        self.viewmodel.config_meters__changed.connect(self.on_param_changed__config_meters)
        self.viewmodel.config_meters__changed.emit(self.viewmodel.config_meters)
        self.on_config_changed()
    
    def _bind_csv_path(self):
        self.csv_path_edit.textChanged.connect(self.viewmodel.set__csv_filepath)
        self.viewmodel.csv_filepath__changed.connect(
            lambda value: (
                self.csv_path_edit.setText(value),
                self.evaluation_timer.start(self.EVAL_DELAY),
            )
        )
        self.viewmodel.csv_filepath__changed.emit(self.viewmodel.csv_filepath)
        self.csv_browse_button.clicked.connect(self.select_csv_file)
    
    def _bind_Pr_step(self):
        self.Pr_step_spinbox.valueChanged.connect(self.viewmodel.set__Pr_step)
        self.viewmodel.Pr_step__changed.connect(
            lambda value: (
                self.Pr_step_spinbox.setValue(value),
                self.update_header_labels(),
                self.evaluation_timer.start(self.EVAL_DELAY)
            )
        )
        self.viewmodel.Pr_step__changed.emit(self.viewmodel.Pr_step)
    
    def _bind_Pr_table(self):
        self.table.itemChanged.connect(self.update_Pr_grid)
        self.viewmodel.Pr_grid__changed.connect(self.update_table)
        self.update_table(self.viewmodel.Pr_grid)
        
    def _bind_exports(self):
        self.export_csv_button.clicked.connect(self.on_export_csv_button_clicked)
        self.export_config_button.clicked.connect(self.export_config)
        
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
        
        display_rows, display_cols = map(lambda x: max(self.MIN_DISPLAY_LIMIT, min(x, self.MAX_DISPLAY_LIMIT)), [rows, cols])
        total_height = display_rows * self.CELL_SIZE + 21
        total_width  = display_cols * self.CELL_SIZE + 35
        self.table.setFixedSize(total_width, total_height)
        
        parameter_panel_width = total_width + 24
        self.general_groupbox.setFixedWidth(parameter_panel_width)
        self.zone_groupbox.setFixedWidth(parameter_panel_width)
        self.config_groupbox.setFixedWidth(parameter_panel_width)
        self.measurement_groupbox.setFixedWidth(parameter_panel_width)
        
        self.table.blockSignals(False)

    def update_header_labels(self):
        n, step = self.table.rowCount(), self.viewmodel.Pr_step
        header_labels = np.arange(0.0, n * step, step).round(1).astype('str')
        self.table.setVerticalHeaderLabels(header_labels)
        self.table.setHorizontalHeaderLabels(header_labels)

    def on_export_csv_button_clicked(self):
        write_csv(self.viewmodel.csv_filepath, self.viewmodel.Pr_table)
        
    def select_csv_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if filepath:
            self.csv_path_edit.setText(filepath)
        
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
    
        # --- Update metrics display instead of printing ---
        metrics_text = (
            "💧 Uniformaity\n"
            "----------------------\n"
            f"Christiansen Uniformity (CU): {result.metrics.CU:.2f} %\n"
            f"Distribution Uniformity (DU): {result.metrics.DU:.2f} %\n"
        )
        self.metrics_textbox.setPlainText(metrics_text)
    
        # --- Update plots ---
        self.zone_canvas.plot(result.zone, self.viewmodel.resolution, (45, 45))
        self.homogenous_plot_canvas.plot(result.homogenous_plot, self.viewmodel.resolution, (45, 45))

    def export_config(self):
        serialize_floats = lambda floats: ', '.join(map(str, floats))
        self.config_parser.set('Display', 'RESOLUTION', str(self.viewmodel.resolution))
        self.config_parser.set('Sprinklers', 'ZONE_DIM_METERS', serialize_floats(self.viewmodel.zone_dim_meters))
        self.config_parser.set('Sprinklers', 'CONFIG_METERS', serialize_floats(self.viewmodel.config_meters))
        self.config_parser.set('Sprinklers', 'CSV_FILEPATH', self.viewmodel.csv_filepath)
        self.config_parser.write()