# -*- coding: utf-8 -*-

from model import Model
from helper import INIParser
from sprinklers import run_simulation
from skimage.io import imsave
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
    print(model)
    
    # Step 2: Run the simulation
    result = run_simulation(model.resolution, model.zone_dim_meters,
                            model.config_meters, model.Pr_table)
    
    os.makedirs('./output_plots', exist_ok=True)
    imsave('./output_plots/zone.png', result.zone)
    imsave('./output_plots/homogenous_plot.png', result.homogenous_plot)
    print(f'DU: {result.metrics.DU}% | CU: {result.metrics.CU}%')
    
if __name__ == '__main__':
    main()