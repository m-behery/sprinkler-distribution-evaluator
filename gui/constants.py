#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 18:39:37 2025

@author: mohamed
"""

from typing import Final

class StaticClass:
    """
    Base class for static-like containers that should not be instantiated.
    """
    def __new__(self):
        raise NotImplementedError('This is a static class that cannot be instantiated.')

class Evaluation(StaticClass):
    """
    Evaluation-related constants.
    """
    DELAY_MS: Final = 1000
    
class Cells(StaticClass):
    """
    Cell/table display constants.
    """
    SIZE: Final          = 40
    MAX_DISPLAYED: Final = 10
    MIN_DISPLAYED: Final = 3

class Themes(StaticClass):
    """
    Application-wide stylesheet definitions.
    """
    LIGHT: Final = '''
        QWidget {
            background-color: #f0f2f5;   /* window bg: light neutral gray */
            font-size: 13px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ccc;
            border-radius: 6px;
            margin-top: 8px;
            padding: 6px;
            background-color: #fafafa;   /* softer off-white card bg */
        }
        
        QSlider {
            background: transparent;
        }
        
        QSlider::groove:horizontal {
            height: 4px;
            background: #ccc;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background: #555;
            border-radius: 6px;
            width: 12px;
            height: 12px;
            margin: -4px 0; /* keeps handle centered */
        }
        
        QLabel {
            font-size: 13px;
            color: #111;
            background-color: transparent;
            padding: 2px;
            border-radius: 2px;
        }
        
        QLabel#metrics_label {
            font-weight: bold;
            font-size: 13px;           
            background-color: transparent;
            padding: 4px 6px;
            qproperty-alignment: 'AlignHCenter | AlignVCenter';
        }
        
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #bbb;
            border-radius: 4px;
            padding: 4px;
        }
        
        QTableWidget {
            gridline-color: #aaa;
            background-color: #ffffff;
            alternate-background-color: #f7f7f7;
            border-radius: 6px;
        }
        
        QTextEdit {
            background-color: #111;
            color: #f1f1f1;
            font-family: Consolas, monospace;
            font-size: 13px;
            border-radius: 6px;
            padding: 6px;
        }
        
        QPushButton {
            font-weight: bold;
            border-radius: 6px;
            padding: 6px 10px;
            color: white;
        }
        
        QPushButton#csv_browse_button {
            qproperty-iconSize: 16px;
            border: 1px solid #c8cace;
            border-radius: 4px;
            background-color: #e6e8eb;
            color: #111;
        }
        QPushButton#csv_browse_button:hover {
            background-color: #d6d8db;
        }
        QPushButton#csv_browse_button:pressed {
            background-color: #c6c8cc;
        }

        QPushButton#export_csv_button {
            background-color: #4caf50;
        }
        QPushButton#export_csv_button:hover {
            background-color: #45a049;
        }
        QPushButton#export_csv_button:pressed {
            background-color: #388e3c;
        }
        
        QPushButton#export_config_button {
            background-color: #607d8b;
        }
        QPushButton#export_config_button:hover {
            background-color: #546e7a;
        }
        QPushButton#export_config_button:pressed {
            background-color: #455a64;
        }

        QComboBox QAbstractItemView {
            selection-color: #111;
        }
        '''