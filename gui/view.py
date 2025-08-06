#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 03:17:40 2025

@author: mohamed
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QComboBox, QDoubleSpinBox,
    QTableWidgetItem, QPushButton, QSlider,
)
from PyQt5.QtCore import Qt, QTimer
import numpy as np
from viewmodel import ViewModel
from helper import write_csv, evaluate

class View(QWidget):
    
    EVAL_DELAY = 1000
    
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
        
        self.resolution_label = QLabel('Resolution:')
        self.resolution_slider = QSlider(Qt.Horizontal)
        self.resolution_slider.setRange(1, 100)
        self.resolution_value_label = QLabel('1')
        
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
        self.layout.addWidget(self.resolution_value_label)
        self.layout.addWidget(self.config_label)
        self.layout.addWidget(self.config_dropdown)
        self.layout.addWidget(self.config_dim_a_label)
        self.layout.addWidget(self.config_dim_a_spinbox)
        self.layout.addWidget(self.config_dim_b_label)
        self.layout.addWidget(self.config_dim_b_spinbox)
        
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        
        self.apply_button = QPushButton('Apply Table Changes')
        self.layout.addWidget(self.apply_button)
        
        self.setLayout(self.layout)
        
    def bind_viewmodel(self):
        
        self.resolution_slider.setValue(self.viewmodel.resolution)
        self.resolution_value_label.setText(str(self.viewmodel.resolution))
        self.resolution_slider.valueChanged.connect(self.on_resolution_changed)
        self.viewmodel.resolution__changed.connect(
            lambda value: (
                self.resolution_slider.setValue(value),
                self.resolution_value_label.setText(str(value))
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
        
        self.update_table(self.viewmodel.Pr_table)
        self.viewmodel.Pr_table__changed.connect(self.update_table)
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
        self.resolution_value_label.setText(str(value))
        self.viewmodel.set__resolution(value)
        self.evaluation_timer.start(self.EVAL_DELAY)
        
    def update_table(self, arr):
        self.table.blockSignals(True)
        rows, cols = arr.shape
        rows += 1
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.setHorizontalHeaderLabels(['x', 'y', 'Pr (mm/h)'])
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem('' if i == rows - 1 else str(arr[i,j]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
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
                try:
                    arr[i, j] = float(item.text()) if item else 0.0
                except ValueError:
                    arr[i, j] = 0.0
        invalid = (arr == [0,0,0]).all(1)
        arr = arr[~invalid]
        self.viewmodel.set__Pr_table(arr)
        
    def keyPressEvent(self, event):
        is_empty = lambda row: all([self.table.item(row, col).text() == '' for col in range(self.table.columnCount())])
        if event.key() == Qt.Key_Delete:
            selected_ranges = self.table.selectedRanges()
            if selected_ranges:
                self.table.blockSignals(True)
                for selection in selected_ranges:
                    for row in reversed(range(selection.topRow(), selection.bottomRow() + 1)):
                        if is_empty(row):
                            continue
                        self.table.removeRow(row)
                self.table.blockSignals(False)
            self.on_table_changed()
        else:
            super().keyPressEvent(event)
            
    def update_evaluation_result(self):
        print(f'Config Dimensions: {self.viewmodel.config_meters}')
        self.viewmodel.evaluation_result = evaluate(
            self.viewmodel.resolution, 
            self.viewmodel.zone_dim_meters,
            self.viewmodel.config_meters,
            self.viewmodel.Pr_table
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