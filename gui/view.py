#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 03:17:40 2025

@author: mohamed
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QComboBox, QDoubleSpinBox,
    QTableWidgetItem, QPushButton, QSlider, QStyledItemDelegate,
)
from PyQt5.QtGui import QColor, QBrush, QDoubleValidator
from PyQt5.QtCore import Qt, QTimer
import numpy as np
from viewmodel import ViewModel
from helper import write_csv, evaluate

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
    FIXED_DISPLAY_LIMIT = 10
    
    def __init__(self, viewmodel:ViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self.init_ui()
        self.bind_viewmodel()
    
    def init_ui(self):
        
        self.evaluation_timer = QTimer(self)
        self.evaluation_timer.setSingleShot(True)
        self.evaluation_timer.timeout.connect(self.update_evaluation_result)
        
        self.setWindowTitle('Sprinkler Distribution Evaluator')
        self.layout = QVBoxLayout()
        
        self.resolution_label = QLabel('Resolution: 1')
        self.resolution_slider = QSlider(Qt.Horizontal)
        self.resolution_slider.setRange(1, 100)
        
        self.config_label = QLabel('Sprinkler Configuration:')
        self.config_dropdown = QComboBox()
        self.config_dropdown.addItems(['Triangle', 'Rectangle'])
        
        self.config_dim_a_label = QLabel("Width:")
        self.config_dim_a_spinbox = QDoubleSpinBox()
        self.config_dim_a_spinbox.setDecimals(2)
        self.config_dim_a_spinbox.setSingleStep(0.1)
        self.config_dim_a_spinbox.setRange(0.5, 20.0)
        self.config_dim_a_spinbox.setPrefix('Spacing (m): ')
        
        self.config_dim_b_label = QLabel("Height:")
        self.config_dim_b_spinbox = QDoubleSpinBox()
        self.config_dim_b_spinbox.setDecimals(2)
        self.config_dim_b_spinbox.setSingleStep(0.1)
        self.config_dim_b_spinbox.setRange(0.5, 20.0)
        self.config_dim_b_spinbox.setPrefix('Spacing (m): ')
        
        self.layout.addWidget(self.resolution_label)
        self.layout.addWidget(self.resolution_slider)
        self.layout.addWidget(self.config_label)
        self.layout.addWidget(self.config_dropdown)
        self.layout.addWidget(self.config_dim_a_label)
        self.layout.addWidget(self.config_dim_a_spinbox)
        self.layout.addWidget(self.config_dim_b_label)
        self.layout.addWidget(self.config_dim_b_spinbox)
        
        self.table = QTableWidget()
        self.table.setItemDelegate(NumericDelegate(self.table))
        self.layout.addWidget(self.table)
        
        self.apply_button = QPushButton('Apply Table Changes')
        self.layout.addWidget(self.apply_button)
        
        self.setLayout(self.layout)
        
    def bind_viewmodel(self):
        
        self.resolution_slider.setValue(self.viewmodel.resolution)
        self.resolution_label.setText(f'Resolution: {self.viewmodel.resolution}')
        self.resolution_slider.valueChanged.connect(self.on_resolution_changed)
        self.viewmodel.resolution__changed.connect(
            lambda value: (
                self.resolution_slider.setValue(value),
                self.resolution_label.setText(f'Resolution: {value}')
            )
        )
        
        is_triangle = len(self.viewmodel.config_meters) < 2
        a, b = self.viewmodel.config_meters[0], 0.0
        if not is_triangle:
            b = self.viewmodel.config_meters[1]
        
        self.config_dropdown.currentIndexChanged.connect(self.on_config_changed)
        self.config_dropdown.setCurrentIndex(0 if is_triangle else 1)
        self.on_config_changed()
        
        self.config_dim_a_spinbox.valueChanged.connect(self.on_config_dims_changed)
        self.config_dim_b_spinbox.valueChanged.connect(self.on_config_dims_changed)
        self.config_dim_a_spinbox.setValue(a)
        self.config_dim_b_spinbox.setValue(b)
        
        self.update_table(self.viewmodel.Pr_grid)
        self.viewmodel.Pr_grid__changed.connect(self.update_table)
        self.apply_button.clicked.connect(self.on_apply_button_clicked)
        self.table.itemChanged.connect(self.on_table_changed)
    
    def on_config_changed(self):
        is_triangle = self.config_dropdown.currentIndex() == 0
        self.config_dim_a_label.setText('Side:' if is_triangle else 'Width:')
        self.config_dim_b_label.setVisible(not is_triangle)
        self.config_dim_b_spinbox.setVisible(not is_triangle)
        self.on_config_dims_changed()
    
    def on_config_dims_changed(self):
        a = self.config_dim_a_spinbox.value()
        b = self.config_dim_b_spinbox.value()
        self.viewmodel.config_meters = (a, b) if self.config_dim_b_spinbox.isVisible() else (a,)
        self.evaluation_timer.start(self.EVAL_DELAY)
    
    def on_resolution_changed(self, value):
        self.resolution_label.setText(f'Resolution: {value}')
        self.viewmodel.set__resolution(value)
        self.evaluation_timer.start(self.EVAL_DELAY)
        
    def update_table(self, arr):
        self.table.blockSignals(True)
        
        Pr_max = arr.max()
        rows, cols = np.array(arr.shape) + 1
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.clearContents()
        for i in range(rows):
            for j in range(cols):
                if i == rows - 1 or j == cols - 1:
                    item = QTableWidgetItem('')
                else:
                    value = arr[i, j]
                    item = QTableWidgetItem(str(value))
                    
                    normalized_value = value / (Pr_max + 1e-3)
                    color = QColor.fromHsv(100, 255, int(255 * normalized_value))
                    item.setBackground(QBrush(color))
                    if normalized_value < 0.5:
                        item.setForeground(QBrush(QColor(255, 255, 255)))
                        
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
                
        for row in range(rows):
            self.table.setRowHeight(row, self.CELL_SIZE)
            
        for col in range(cols):
            self.table.setColumnWidth(col, self.CELL_SIZE)
            
        total_height = min(rows, self.FIXED_DISPLAY_LIMIT) * self.CELL_SIZE + 25
        total_width = min(cols, self.FIXED_DISPLAY_LIMIT) * self.CELL_SIZE + 20
        self.table.setFixedSize(total_width, total_height)
    
        self.table.blockSignals(False)

    def on_apply_button_clicked(self):
        write_csv(self.viewmodel.csv_filepath, self.viewmodel.Pr_table)
        
    def on_table_changed(self):
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
                else:
                    arr[i, j] = conj_value
                    
        invalid_rows, invalid_cols = map(lambda x: (arr == 0).all(x), (1, 0))
        arr = arr[~invalid_rows, :]
        arr = arr[:, ~invalid_cols]
        self.viewmodel.set__Pr_grid(arr)
        print(arr)
        self.evaluation_timer.start(self.EVAL_DELAY)
            
    def update_evaluation_result(self):
        print(f'Config Dimensions: {self.viewmodel.config_meters}')
        self.viewmodel.evaluation_result = evaluate(
            self.viewmodel.resolution, 
            self.viewmodel.zone_dim_meters,
            self.viewmodel.config_meters,
            self.viewmodel.Pr_dist
        )
        metrics = self.viewmodel.evaluation_result.metrics
        print(f'Metrics - CU: {metrics.CU}, DU: {metrics.DU}')

# =============================================================================
# def write_config(self):
#     serialize_floats = lambda floats: ', '.join(map(str, floats))
#     self.parser.set('Display', 'RESOLUTION', str(self.resolution))
#     self.parser.set('Sprinklers', 'ZONE_DIM_METERS', serialize_floats(self.zone_dim_meters))
#     self.parser.set('Sprinklers', 'CONFIG_METERS', serialize_floats(self.config_meters))
#     self.parser.set('Sprinklers', 'CSV_FILEPATH', self.csv_filepath)
#     self.parser.write()
# =============================================================================