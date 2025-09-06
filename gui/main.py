# -*- coding: utf-8 -*-
"""
@author: mohamed
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