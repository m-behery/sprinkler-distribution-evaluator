#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  6 18:39:37 2025

@author: mohamed
"""

from typing import Final

class Themes:
    
    def __new__(self):
        raise NotImplementedError('ThemeDetector is a static class')
    
    LIGHT: Final = """
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
        
        QLabel#metricsLabel {
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
        
        QPushButton#csvBrowse {
            qproperty-iconSize: 16px;
            border: 1px solid #c8cace;
            border-radius: 4px;
            background-color: #e6e8eb;
            color: #111;
        }
        QPushButton#csvBrowse:hover {
            background-color: #d6d8db;
        }
        QPushButton#csvBrowse:pressed {
            background-color: #c6c8cc;
        }

        QPushButton#applyButton {
            background-color: #4caf50;
        }
        QPushButton#applyButton:hover {
            background-color: #45a049;
        }
        QPushButton#applyButton:pressed {
            background-color: #388e3c;
        }
        
        QPushButton#exportConfig {
            background-color: #607d8b;
        }
        QPushButton#exportConfig:hover {
            background-color: #546e7a;
        }
        QPushButton#exportConfig:pressed {
            background-color: #455a64;
        }

        QComboBox QAbstractItemView {
            selection-color: #111;
        }
        """