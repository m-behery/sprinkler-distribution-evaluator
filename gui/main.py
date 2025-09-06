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

from PyQt5.QtWidgets import QApplication
from viewmodel import ViewModel

import sys
from model import Model
from utils import INIParser
from view import View

def main():
    """
    Main function to initialize and run the application.
    
    Steps:
    1. Create the QApplication instance.
    2. Parse the configuration file using INIParser.
    3. Initialize the Model using configuration values.
    4. Wrap the Model in a ViewModel.
    5. Initialize the View, passing the ViewModel and parser.
    6. Show the main window and start the Qt event loop.
    """
    
    app = QApplication(sys.argv)
    
    parser = INIParser()
    parser.read()
    
    model = Model(
        resolution      = parser.getint('Display', 'RESOLUTION'),
        zone_dim_meters = parser.gettuple('Sprinklers', 'ZONE_DIM_METERS'),
        config_meters    = parser.gettuple('Sprinklers', 'CONFIG_METERS'),
        csv_filepath     = parser.clean_inline_get('Sprinklers', 'CSV_FILEPATH'),
    )
    viewmodel = ViewModel(model)
    view = View(viewmodel, parser)
    
    view.show()
    sys.exit(app.exec_())
    
    
if __name__ == '__main__':
    main()