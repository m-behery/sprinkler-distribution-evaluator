#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sprinkler Distribution Evaluator - A Python tool to simulate and visualize sprinkler coverage
Copyright (C) 2025 Mohamed Behery

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QComboBox, QTableWidgetItem,
    QPushButton, QSlider, QStyledItemDelegate, QHBoxLayout, QGroupBox,
    QFormLayout, QFrame, QTextEdit, QLineEdit, QFileDialog, QTabWidget, 
)
from PyQt5.QtGui import QColor, QBrush, QDoubleValidator
from PyQt5.QtCore import Qt, QTimer
import numpy as np

from viewmodel import ViewModel
from utils import INIParser
from sprinklers import evaluate
from utils import write_csv
from widgets import DoubleSpinBox, SimpleHeader, RotatedHeader, Canvas4ImageAs3D
import constants

class NumericDelegate(QStyledItemDelegate):
    """
    A custom delegate for QTableView/QTableWidget that enforces numeric input.
    
    This delegate ensures that table cells edited by the user only accept floating-point numbers
    within a specific range and with a fixed number of decimal places.
    """
    def createEditor(self, parent, option, index):
        """
        Create an editor widget for a table cell.

        Parameters:
        - parent: the parent widget
        - option: QStyleOptionViewItem describing the item
        - index: QModelIndex identifying the item being edited

        Returns:
        - A QWidget editor with a numeric validator applied.
        """
        editor = super().createEditor(parent, option, index)
        if editor:
            validator = QDoubleValidator(editor)
            validator.setBottom(0.0)
            validator.setTop(1e2)
            validator.setDecimals(2)
            editor.setValidator(validator)
        return editor
    
class View(QWidget):
    def __init__(self, viewmodel:ViewModel, config_parser:INIParser):
        """
        Initialize the main view.
    
        Parameters:
        - viewmodel: The ViewModel instance providing data and logic binding
        - config_parser: The INIParser instance for reading/writing configuration
    
        Responsibilities:
        1. Store references to the viewmodel and config parser for later use.
        2. Initialize internal flags, e.g., `zero_input_flag`.
        3. Set up the user interface by calling `init_ui()`.
        4. Connect UI elements to the ViewModel via `bind_viewmodel()`.
        """
        super().__init__()
        self.zero_input_flag = False
        
        self.viewmodel    = viewmodel
        self.config_parser = config_parser
        
        self.init_ui()
        self.bind_viewmodel()
        

    def init_ui(self):
        """
        Set up the main user interface for the Sprinkler Distribution Evaluator.
        """
        self.setWindowTitle('💧 Sprinkler Distribution Evaluator')
        
        self.evaluation_timer = QTimer(self)
        self.evaluation_timer.setSingleShot(True)
        self.evaluation_timer.timeout.connect(self.update_evaluation_result)
        
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        
        # ---------------------------
        # LEFT PANEL with tabs
        # ---------------------------
        config_layout = QVBoxLayout()
        self.main_layout.addLayout(config_layout)
        self.config_tab_widget = QTabWidget()
        config_layout.addWidget(self.config_tab_widget)
        config_layout.addStretch()
    
        # === Tab 1: main parameters ===
        self.parameters_tab = QWidget()
        self.parameters_panel = QVBoxLayout(self.parameters_tab)
        self.parameters_panel.setSpacing(12)
        
        self.general_groupbox = self._create_general_groupbox()
        self.parameters_panel.addWidget(self.general_groupbox)
        
        self.zone_groupbox = self._create_zone_groupbox()
        self.parameters_panel.addWidget(self.zone_groupbox)
        
        self.config_groupbox = self._create_sprinklers_groupbox()
        self.parameters_panel.addWidget(self.config_groupbox)
        
        self.Pr_table_groupbox = self._create_Pr_table_groupbox()
        self.parameters_panel.addWidget(self.Pr_table_groupbox)
        
        self.parameters_panel.addStretch()
        
        self.export_config_button = QPushButton('📑 Save Config')
        self.parameters_panel.addWidget(self.export_config_button)
        
        self.parameters_panel.addSpacing(9)
        
        self.config_tab_widget.addTab(self.parameters_tab, "Parameters")
    
        # === Tab 2: Pr Measurements ===
        self.Pr_measurements_tab = QWidget()
        self.Pr_measurements_layout = self._create_Pr_measurements_layout()
        self.Pr_measurements_tab.setLayout(self.Pr_measurements_layout)
        
        self.config_tab_widget.addTab(self.Pr_measurements_tab, "Pr Measurements")
        
        # ---------------------------
        # MIDDLE PLOTS PANEL (with tabs)
        # ---------------------------
        self.main_layout.addSpacing(24)
        self.plot_panel = QVBoxLayout()
        self.main_layout.addLayout(self.plot_panel, stretch=2)
        
        # Tab widget for plots
        self.plot_tab_widget = QTabWidget()
        self.plot_panel.addWidget(self.plot_tab_widget)
        
        # === Tab 1: Zone ===
        self.zone_tab = QWidget()
        zone_layout = QVBoxLayout(self.zone_tab)
        self.zone_groupbox_canvas = self._create_canvas_groupbox('Zone')
        zone_layout.addWidget(self.zone_groupbox_canvas)
        self.plot_tab_widget.addTab(self.zone_tab, "Zone")
        
        # === Tab 2: Homogeneous Plot ===
        self.homogenous_tab = QWidget()
        homogenous_layout = QVBoxLayout(self.homogenous_tab)
        self.homogenous_groupbox_canvas = self._create_canvas_groupbox('Homogeneous Plot')
        homogenous_layout.addWidget(self.homogenous_groupbox_canvas)
        self.plot_tab_widget.addTab(self.homogenous_tab, "Homogeneous Plot")
        
        # ---------------------------
        # RIGHT METRICS PANEL
        # ---------------------------
        self.main_layout.addSpacing(8)
        
        self.metrics_panel = QVBoxLayout()
        self.metrics_label = QLabel('Metrics')
        self.metrics_label.setAlignment(Qt.AlignHCenter)
        self.metrics_panel.addWidget(self.metrics_label)
        
        self.metrics_textbox = QTextEdit()
        self.metrics_textbox.setReadOnly(True)
        self.metrics_textbox.setFixedWidth(220)
        self.metrics_panel.addWidget(self.metrics_textbox)
        
        self.main_layout.addLayout(self.metrics_panel, stretch=0)
        
        # ---------------------------
        # Object names + stylesheet
        # ---------------------------
        self.csv_browse_button.setObjectName('csv_browse_button')
        self.export_csv_button.setObjectName('export_csv_button')
        self.export_config_button.setObjectName('export_config_button')
        self.metrics_label.setObjectName('metrics_label')
        self.setStyleSheet(constants.Themes.LIGHT)


    def _create_general_groupbox(self):
        """
        Create the 'General' groupbox containing the resolution settings.
    
        Components:
        - QLabel showing the current resolution.
        - QSlider allowing the user to adjust the resolution from 5 to 100.
    
        Returns:
            QGroupBox: The assembled 'General' groupbox ready to be added to a layout.
        """
        groupbox = QGroupBox('General')
        layout = QVBoxLayout(groupbox)
    
        self.resolution_label = QLabel('Resolution: 5')
        self.resolution_slider = QSlider(Qt.Horizontal)
        self.resolution_slider.setRange(5, 100)
    
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_slider)
        return groupbox
    
    
    def _create_zone_groupbox(self):
        """
        Create the 'Zone' groupbox for defining the dimensions of the irrigation zone.
    
        Components:
        - Two DoubleSpinBoxes for specifying the width and height in meters.
    
        Returns:
            QGroupBox: The assembled 'Zone' groupbox ready to be added to a layout.
        """
        groupbox = QGroupBox('Zone')
        form = QFormLayout(groupbox)
    
        self.zone_dim_a_spinbox = DoubleSpinBox(1.0, 1000.0)
        self.zone_dim_b_spinbox = DoubleSpinBox(1.0, 1000.0)
    
        form.addRow('Width (m):', self.zone_dim_a_spinbox)
        form.addRow('Height (m):', self.zone_dim_b_spinbox)
        return groupbox
    
    
    def _create_sprinklers_groupbox(self):
        """
        Create the 'Sprinklers' groupbox for configuring sprinkler layout.
    
        Components:
        - Configuration dropdown: 'Triangle' or 'Rectangle'
        - Width spinbox (Side for triangle)
        - Height spinbox (optional, only for rectangle)
    
        Returns:
            QGroupBox: The assembled 'Sprinklers' groupbox ready to be added to a layout.
        """
        groupbox = QGroupBox('Sprinklers')
        layout = QVBoxLayout(groupbox)
        
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel('Configuration:'))
        self.config_dropdown = QComboBox()
        self.config_dropdown.addItems(['Triangle', 'Rectangle'])
        selector_layout.addWidget(self.config_dropdown, stretch=1)
        layout.addLayout(selector_layout)
        
        self.config_dim_a_layout = self._create_label_spinbox_row('Width (m):', 0.5, 20.0)
        layout.addLayout(self.config_dim_a_layout)
        
        self.config_dim_b_layout = self._create_label_spinbox_row('Height (m):', 0.5, 20.0)
        layout.addLayout(self.config_dim_b_layout)
        
        return groupbox
    
    
    def _create_Pr_table_groupbox(self):
        """
        Create the 'Pr Table' groupbox which includes CSV selection.
    
        Components:
        - CSV file selector (disabled QLineEdit + browse button)
    
        Returns:
            QGroupBox: The assembled 'Pr Table' groupbox.
        """
        groupbox = QGroupBox('Pr Table')
        
        csv_layout = QHBoxLayout(groupbox)
        self.csv_path_edit = QLineEdit()
        self.csv_path_edit.setPlaceholderText('Select your Pr-table file...')
        self.csv_path_edit.setEnabled(False)
        self.csv_browse_button = QPushButton('📝')
        self.csv_browse_button.setFixedSize(32, 32)
        self.csv_path_edit.setFixedHeight(32)
        csv_layout.addWidget(self.csv_path_edit, stretch=1)
        csv_layout.addWidget(self.csv_browse_button)
        return groupbox
        
    def _create_Pr_measurements_layout(self):
        layout = QVBoxLayout()
        
        self.Pr_measurements_groupbox = QGroupBox('Pr Measurements')
        sub_layout = QVBoxLayout(self.Pr_measurements_groupbox)
        sub_layout.addSpacing(20)
        
        form = QFormLayout()
        self.Pr_step_spinbox = DoubleSpinBox(0.1, 20.0)
        form.addRow('Step (m):', self.Pr_step_spinbox)
        sub_layout.addLayout(form)
        
        sub_layout.addSpacing(46)
        
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeader(SimpleHeader(self.table))
        self.table.setVerticalHeader(RotatedHeader(self.table))
        sub_layout.addWidget(self.table)
        
        layout.addWidget(self.Pr_measurements_groupbox)
        
        layout.addSpacing(6)
        
        self.export_csv_button = QPushButton('📤 Export Table')
        layout.addWidget(self.export_csv_button)
        
        layout.addStretch()
        
        return layout
    
    def _create_canvas_groupbox(self, title: str) -> QGroupBox:
        """
        Create a groupbox containing a canvas for plotting.
    
        Parameters:
            title (str): The title of the groupbox, e.g., 'Zone' or 'Homogeneous Plot'.
    
        Returns:
            QGroupBox: The assembled groupbox with a canvas widget inside.
        
        Notes:
            - Centers the groupbox title.
            - Instantiates a Canvas4ImageAs3D widget and stores a reference
              to it in the corresponding instance attribute:
              `self.zone_canvas` or `self.homogenous_plot_canvas`.
        """
        groupbox = QGroupBox(title)
        groupbox.setAlignment(Qt.AlignHCenter)
        layout = QVBoxLayout(groupbox)
        canvas = Canvas4ImageAs3D(self)
        layout.addWidget(canvas)
        if title.lower() == 'zone':
            self.zone_canvas = canvas
        else:
            self.homogenous_plot_canvas = canvas
        groupbox.setMinimumHeight(433)
        return groupbox
    
    
    def _create_label_spinbox_row(self, label_text: str, min_val: float, max_val: float) -> QHBoxLayout:
        """
        Create a horizontal layout containing a QLabel and a DoubleSpinBox.
    
        Parameters:
            label_text (str): The text for the label.
            min_val (float): Minimum value for the spinbox.
            max_val (float): Maximum value for the spinbox.
    
        Returns:
            QHBoxLayout: The assembled horizontal layout with label and spinbox.
    
        Notes:
            - Sets a fixed width for the label (70 px) for alignment.
            - Stores references to the label and spinbox in instance attributes
              for later access, distinguishing between width and height based on
              the label text.
        """
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(70)
        spinbox = DoubleSpinBox(min_val, max_val)
        layout.addWidget(label)
        layout.addWidget(spinbox)
    
        if 'width' in label_text.lower():
            self.config_dim_a_label = label
            self.config_dim_a_spinbox = spinbox
        else:
            self.config_dim_b_label = label
            self.config_dim_b_spinbox = spinbox
        return layout


    def bind_viewmodel(self):
        """
        Bind all UI widgets to the corresponding ViewModel signals and slots.
        Each group of related widgets is handled in a separate helper method.
        """
        self._bind_resolution()
        self._bind_zone_dimensions()
        self._bind_config()
        self._bind_csv_path()
        self._bind_Pr_step()
        self._bind_Pr_table()
        self._bind_exports()
        
        
    def _bind_resolution(self):
        """
        Bind resolution slider and label to ViewModel.
        """
        self.resolution_slider.valueChanged.connect(self.viewmodel.set__resolution)
        self.viewmodel.resolution__changed.connect(
            lambda value: (
                self.resolution_slider.setValue(value),
                self.resolution_label.setText(f'Resolution: {value}'),
                self.evaluation_timer.start(constants.Evaluation.DELAY_MS)
            )
        )
        self.viewmodel.resolution__changed.emit(self.viewmodel.resolution)
    
    
    def _bind_zone_dimensions(self):
        """
        Bind zone dimension spinboxes to ViewModel.
        """
        self.zone_dim_a_spinbox.valueChanged.connect(self.on_zone_dims_changed)
        self.zone_dim_b_spinbox.valueChanged.connect(self.on_zone_dims_changed)
        self.viewmodel.zone_dim_meters__changed.connect(
            lambda value: (
                self.zone_dim_a_spinbox.setValue(value[0]),
                self.zone_dim_b_spinbox.setValue(value[1]),
                self.evaluation_timer.start(constants.Evaluation.DELAY_MS)
            )
        )
        self.viewmodel.zone_dim_meters__changed.emit(self.viewmodel.zone_dim_meters)
    
    
    def _bind_config(self):
        """
        Bind sprinkler configuration dropdown and spinboxes.
        """
        self.viewmodel.config_meters__changed.connect(self.on_param_changed__config_meters)
        self.viewmodel.config_meters__changed.emit(self.viewmodel.config_meters)
        
        self.config_dropdown.currentIndexChanged.connect(self.on_config_changed)
        self.config_dim_a_spinbox.valueChanged.connect(self.on_config_dims_changed)
        self.config_dim_b_spinbox.valueChanged.connect(self.on_config_dims_changed)
        
        self.config_dim_a_label.setText('Side (m):' if self.viewmodel.is_triangle else 'Width (m):')
        
        
    def on_param_changed__config_meters(self):
        """
        Update the sprinkler configuration UI based on the ViewModel's config_meters.
        Handles both Triangle (single value) and Rectangle (two values) configurations.
        """
        self.config_dropdown.setCurrentIndex(0 if self.viewmodel.is_triangle else 1)
    
        self.config_dim_b_label.setVisible(not self.viewmodel.is_triangle)
        self.config_dim_b_spinbox.setVisible(not self.viewmodel.is_triangle)
        
        try:
            a, b = self.viewmodel.config_meters
            self.config_dim_b_spinbox.setValue(b)
        except ValueError:
            a = self.viewmodel.config_meters[0]
        finally:
            self.config_dim_a_spinbox.setValue(a)
    
    
    def on_config_changed(self):
        """
        Adjust the UI and ViewModel based on the selected sprinkler configuration.
        If 'Triangle' is selected, hide the second dimension and update the first label.
        Otherwise, show both width and height inputs.
        """
        is_triangle = self.config_dropdown.currentIndex() == 0
        self.config_dim_a_label.setText('Side (m):' if is_triangle else 'Width (m):')
        self.config_dim_b_label.setVisible(not is_triangle)
        self.config_dim_b_spinbox.setVisible(not is_triangle)
        self.on_config_dims_changed()
    
    
    def on_config_dims_changed(self):
        """
        Update the ViewModel with the current sprinkler configuration dimensions.
        - For triangle configuration, only the first dimension (side) is used.
        - For rectangle configuration, both width and height are used.
        """
        a = self.config_dim_a_spinbox.value()
        b = self.config_dim_b_spinbox.value()
        value = (a, b) if self.config_dim_b_spinbox.isVisible() else (a,)
        self.viewmodel.set__config_meters(value)
        self.evaluation_timer.start(constants.Evaluation.DELAY_MS)
    
    
    def _bind_csv_path(self):
        """
        Bind CSV file path input and browse button.
        """
        self.csv_path_edit.textChanged.connect(self.viewmodel.set__csv_filepath)
        self.viewmodel.csv_filepath__changed.connect(
            lambda value: (
                self.csv_path_edit.setText(value),
                self.evaluation_timer.start(constants.Evaluation.DELAY_MS),
            )
        )
        self.viewmodel.csv_filepath__changed.emit(self.viewmodel.csv_filepath)
        self.csv_browse_button.clicked.connect(self.select_csv_file)
    
    
    def _bind_Pr_step(self):
        """
        Bind Pr step spinbox.
        """
        self.Pr_step_spinbox.valueChanged.connect(self.viewmodel.set__Pr_step)
        self.viewmodel.Pr_step__changed.connect(
            lambda value: (
                self.Pr_step_spinbox.setValue(value),
                self.update_header_labels(),
                self.evaluation_timer.start(constants.Evaluation.DELAY_MS)
            )
        )
        self.viewmodel.Pr_step__changed.emit(self.viewmodel.Pr_step)
    
    
    def _bind_Pr_table(self):
        """
        Bind table updates to the ViewModel.
        """
        self.table.itemChanged.connect(self.update_Pr_grid)
        self.viewmodel.Pr_grid__changed.connect(self.update_table)
        self.update_table(self.viewmodel.Pr_grid)
        
        
    def _bind_exports(self):
        """
        Bind export buttons to their functions.
        """
        self.export_csv_button.clicked.connect(self.on_export_csv_button_clicked)
        self.export_config_button.clicked.connect(self.export_config)
        
        
    def on_zone_dims_changed(self):
        """
        Update the ViewModel with the current zone dimensions from the spinboxes
        and trigger a delayed evaluation.
        """
        w = self.zone_dim_a_spinbox.value()
        h = self.zone_dim_b_spinbox.value()
        value = (w, h)
        self.viewmodel.set__zone_dim_meters(value)
        self.evaluation_timer.start(constants.Evaluation.DELAY_MS)
        
    @staticmethod
    def blues_qcolor(normalized_value: float) -> QColor:
        v = max(0.0, min(1.0, normalized_value))
        hue = 220                    # blue
        sat = int(255 * v)           # 0 → white, 255 → blue
        val = int(255 * (1-v))       # keep full brightness
        return QColor.fromHsv(hue, sat, val)

    @staticmethod
    def format_table_item(value:float, max_value:float):
        """
        Create a QTableWidgetItem with a background color based on the value
        relative to max_value. Values are normalized and mapped to a greenish
        hue, with text color adjusted for contrast.
    
        Parameters:
            value (float): The numeric value for the table cell.
            max_value (float): Maximum value in the table for normalization.
    
        Returns:
            QTableWidgetItem: Formatted table cell item.
        """
        item = QTableWidgetItem(str(float(value)))
        normalized_value = value / (max_value + 1e-3)
        color = __class__.blues_qcolor(normalized_value)
        item.setBackground(QBrush(color))
        if normalized_value > 0.5:
            item.setForeground(QBrush(QColor(255, 255, 255)))
        item.setTextAlignment(Qt.AlignCenter)
        return item
        
    
    def update_table(self, arr):
        """
        Update the QTableWidget with new Pr values and refresh cell formatting.
    
        Parameters:
            arr (np.ndarray): 2D array containing the Pr values to display.
        """
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
        
        display_rows, display_cols = map(
            lambda x: max(
                constants.Cells.MIN_DISPLAYED,
                min(x, constants.Cells.MAX_DISPLAYED)
            ), 
            [rows, cols]
        )
        total_height = display_rows * constants.Cells.SIZE + 21
        total_width  = display_cols * constants.Cells.SIZE + 35
        self.table.setFixedSize(total_width, total_height)
        self.Pr_measurements_groupbox.setFixedHeight(total_height + 134)
        self.config_tab_widget.setFixedHeight(total_height + 227)
        
        parameter_panel_width = total_width + 24
        self.general_groupbox.setFixedWidth(parameter_panel_width)
        self.zone_groupbox.setFixedWidth(parameter_panel_width)
        self.config_groupbox.setFixedWidth(parameter_panel_width)
        self.Pr_table_groupbox.setFixedWidth(parameter_panel_width)
        self.Pr_measurements_groupbox.setFixedWidth(parameter_panel_width)
        self.export_config_button.setFixedWidth(parameter_panel_width)
        self.export_csv_button.setFixedWidth(parameter_panel_width)
        self.config_tab_widget.setFixedWidth(parameter_panel_width + 22)
        
        self.table.blockSignals(False)


    def update_header_labels(self):
        """
        Update the vertical and horizontal headers of the Pr table
        based on the current step size (Pr_step) and number of rows.
        """
        n, step = self.table.rowCount(), self.viewmodel.Pr_step
        header_labels = np.arange(0.0, n * step, step).round(1).astype('str')
        self.table.setVerticalHeaderLabels(header_labels)
        self.table.setHorizontalHeaderLabels(header_labels)


    def on_export_csv_button_clicked(self):
        """
        Export the current Pr table to a CSV file using the path
        specified in the ViewModel.
        """
        write_csv(self.viewmodel.csv_filepath, self.viewmodel.Pr_table)
        
        
    def select_csv_file(self):
        """
        Open a file dialog for the user to select a CSV file.
        If a file is selected, update the CSV path QLineEdit.
        """
        old_filepath = self.csv_path_edit.text()
        dialog = QFileDialog(self)
        dialog.setWindowTitle('Select CSV File')
        dialog.setNameFilter('CSV Files (*.csv);;Excel Files (*.xls *.xlsx)')
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Force Qt dialog
        for button in dialog.findChildren(QPushButton):
            if 'Open' in button.text():
                button.setText('Select')
            else:
                button.setText('Cancel')
            button.setStyleSheet('color: black')
        if dialog.exec() == QFileDialog.Accepted:
            filepath = dialog.selectedFiles()[0]
            if filepath == old_filepath:
                self.csv_path_edit.setText('')
            self.csv_path_edit.setText(filepath)
        
        
    def keyPressEvent(self, event):
        """
        Handles key presses to allow setting selected table items to zero
        when the '0' key is pressed.
        """
        text = event.text()
        self.zero_input_flag = text == '0'
        if self.zero_input_flag:
            selected_items = self.table.selectedItems()
            self.table.blockSignals(True)
            for item in selected_items:
                item.setText('0.0')
            self.table.blockSignals(False)
            self.update_Pr_grid()
            self.zero_input_flag = False
        elif text in 'adAD':
            self.zone_canvas.keyPressEvent(event)
            self.homogenous_plot_canvas.keyPressEvent(event)
            
        
    def update_Pr_grid(self):
        """
        Reads values from the QTableWidget, constructs the Pr grid,
        removes fully zero rows and columns, ensures a minimum grid size,
        updates the ViewModel, refreshes the table, and triggers evaluation.
        """
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
        self.evaluation_timer.start(constants.Evaluation.DELAY_MS)
        
        
    def update_evaluation_result(self):
        """
        Evaluates the current sprinkler configuration and updates
        the ViewModel, metrics display, and plots.
        """
        result = evaluate(
            self.viewmodel.resolution, 
            self.viewmodel.zone_dim_meters,
            self.viewmodel.config_meters,
            self.viewmodel.Pr_table
        )
        self.viewmodel.set__evaluation_result(result)
    
        # --- Update metrics display instead of printing ---
        metrics_text = (
            '💧 Uniformaity\n'
            '----------------------\n'
            f'Christiansen Uniformity (CU): {result.metrics.CU:.2f} %\n'
            f'Distribution Uniformity (DU): {result.metrics.DU:.2f} %\n'
        )
        self.metrics_textbox.setPlainText(metrics_text)
    
        # --- Update plots ---
        self.zone_canvas.plot(result.zone, self.viewmodel.resolution, (45, 45))
        self.homogenous_plot_canvas.plot(result.homogenous_plot, self.viewmodel.resolution, (45, 45))


    def export_config(self):
        """
        Exports the current configuration from the ViewModel
        into the INI parser and writes it to disk.
        """
        serialize_floats = lambda floats: ', '.join(map(str, floats))
        self.config_parser.set('Display', 'RESOLUTION', str(self.viewmodel.resolution))
        self.config_parser.set('Sprinklers', 'ZONE_DIM_METERS', serialize_floats(self.viewmodel.zone_dim_meters))
        self.config_parser.set('Sprinklers', 'CONFIG_METERS', serialize_floats(self.viewmodel.config_meters))
        self.config_parser.set('Sprinklers', 'CSV_FILEPATH', self.viewmodel.csv_filepath)
        self.config_parser.write()