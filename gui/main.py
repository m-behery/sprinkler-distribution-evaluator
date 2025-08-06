# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QApplication
from viewmodel import ViewModel

import sys
from model import Model
from helper import INIParser
from view import View

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
    view = View(viewmodel)
    
    app = QApplication(sys.argv)
    view.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()