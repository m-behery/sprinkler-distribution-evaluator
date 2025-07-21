# -*- coding: utf-8 -*-

from model import Model
from helper import INIParser

def main():
    
    parser = INIParser()
    parser.read()
    
    model = Model(
        resolution      = parser.getint('Display', 'RESOLUTION'), 
        zone_dim_meters = parser.gettuple('Sprinklers', 'ZONE_DIM_METERS'), 
        config_meters    = parser.gettuple('Sprinklers', 'CONFIG_METERS'),
        csv_filepath     = parser.clean_inline_get('Sprinklers', 'CSV_FILEPATH'),
    )
    
    print(model)
    
if __name__ == '__main__':
    main()