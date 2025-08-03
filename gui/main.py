# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QApplication
)
from PyQt5.QtCore import Qt
import numpy as np
from viewmodel import ViewModel

import sys
from PyQt5.QtWidgets import QApplication
from model import Model
from viewmodel import ViewModel
from helper import INIParser

class MainWindow(QWidget):
    
    def __init__(self, viewmodel:ViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self.init_ui()
        self.bind_viewmodel()
    
    def init_ui(self):
        
        self.setWindowTitle('Sprinkler Distribution Evaluator')
        self.layout = QVBoxLayout()
        
        self.resolution_label = QLabel('Resolution:')
        self.resolution_input = QLineEdit()
        self.layout.addWidget(self.resolution_label)
        self.layout.addWidget(self.resolution_input)
        
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        
        self.apply_button = QPushButton('Apply Table Changes')
        self.layout.addWidget(self.apply_button)
        
        self.setLayout(self.layout)
        
    def bind_viewmodel(self):
        
        self.resolution_input.setText(str(self.viewmodel.resolution))
        self.resolution_input.editingFinished.connect(self.on_resolution_edited)
        self.viewmodel.resolution__changed.connect(
            lambda value: self.resolution_input.setText(str(value))
        )
        
        self.update_table(self.viewmodel.Pr_table)
        self.viewmodel.Pr_table__changed.connect(self.update_table)
        self.apply_button.clicked.connect(self.on_apply_button_clicked)
        
    def on_resolution_edited(self):
        try:
            value = int(self.resolution_input.text())
            self.viewmodel.set__resolution(value)
        except:
            raise ValueError('Resolution not okay.')
        
    def update_table(self, arr):
        self.table.blockSignals(True)
        rows, cols = arr.shape
        self.table.setRowCount(rows)
        self.table.setColumnCount(cols)
        self.table.setHorizontalHeaderLabels(['x', 'y', 'Pr (mm/h)'])
        for i in range(rows):
            for j in range(cols):
                item = QTableWidgetItem(str(arr[i,j]))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
        self.table.blockSignals(False)
        
    def on_apply_button_clicked(self):
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
        self.viewmodel.set__Pr_table(arr)

# =============================================================================
# def write_config(self):
#     serialize_floats = lambda floats: ', '.join(map(str, floats))
#     self.parser.set('Display', 'RESOLUTION', str(self.resolution))
#     self.parser.set('Sprinklers', 'ZONE_DIM_METERS', serialize_floats(self.zone_dim_meters))
#     self.parser.set('Sprinklers', 'CONFIG_METERS', serialize_floats(self.config_meters))
#     self.parser.set('Sprinklers', 'CSV_FILEPATH', self.csv_filepath)
#     self.parser.write()
# =============================================================================

def main():
    
    parser = INIParser()
    parser.read()
    
    model = Model(
        resolution      = parser.getint('Display', 'RESOLUTION'),
        zone_dim_meters = parser.gettuple('Sprinklers', 'ZONE_DIM_METERS'),
        config_meters    = parser.gettuple('Sprinklers', 'CONFIG_METERS'),
        csv_filepath     = parser.clean_inline_get('Sprinklers', 'CSV_FILEPATH'),
    )
    viewmodel = ViewModel(model)
    
    app = QApplication(sys.argv)
    window = MainWindow(viewmodel)
    window.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()