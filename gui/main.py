# -*- coding: utf-8 -*-

from model import Model
from viewmodel import ViewModel
from helper import INIParser
from PyQt5.QtCore import QCoreApplication
import numpy as np
import os

def main():
    
    # Step 1: Instantiate the model
    parser = INIParser()
    parser.read()
    
    model = Model(
        resolution      = parser.getint('Display', 'RESOLUTION'), 
        zone_dim_meters = parser.gettuple('Sprinklers', 'ZONE_DIM_METERS'), 
        config_meters    = parser.gettuple('Sprinklers', 'CONFIG_METERS'),
        csv_filepath     = parser.clean_inline_get('Sprinklers', 'CSV_FILEPATH'),
    )
    
    # Step 2: Instantiate the ViewModel
    vm = ViewModel(model)
    
    # Step 3: Connect signal to test handler
    def signal_report(name):
        def handler(value):
            print(f'{name} changed → {value}')
        return handler
    
    vm.resolution__changed.connect(signal_report('resolution'))
    vm.zone_dim_meters__changed.connect(signal_report('zone_dim_meters'))
    vm.config_meters__changed.connect(signal_report('config_meters'))
    vm.csv_filepath__changed.connect(signal_report('csv_filepath'))
    vm.Pr_table__changed.connect(signal_report('Pr_table'))
    
    # Step 4: Trigger some changes
    print("Initial resolution:", vm.get__resolution())
    vm.set__resolution(20)
    
    print("Initial zone_dim_meters:", vm.get__zone_dim_meters())
    vm.set__zone_dim_meters((100.0, 100.0))
    
    print("Initial config_meters:", vm.get__config_meters())
    vm.set__config_meters((20.0, 20.0))
    
    print("Initial CSV path:", vm.get__csv_filepath())
    vm.set__csv_filepath('test_data.csv') # triggers table reload
    
    # Modify the data array and set
    new_table = np.zeros((2, 3))
    vm.set__Pr_table(new_table)
    
    # Optional: Check if model reflects changes
    print("\nModel now:")
    print(model)
    
    # Clean up test CSV
    os.remove('test_data.csv')
    
if __name__ == '__main__':
    main()