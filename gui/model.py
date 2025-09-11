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
from argparse import Namespace
import numpy as np
from utils import read_csv
from sprinklers import Pr_table_to_grid, Pr_grid_to_table

class Model:
    
    def __init__(self, resolution, zone_dim_meters, config_meters, csv_filepath):
        
        assert 0 < len(config_meters) <= 2, 'config_meters can either have 1 (i.e. triangular) or 2 (i.e. rectangluar) dimensions.'
        
        self._resolution = resolution
        self._zone_dim_meters = zone_dim_meters
        self._is_triangle = len(config_meters) < 2
        self._config_meters = config_meters
        self._csv_filepath = None
        self._Pr_grid = None
        self._Pr_step = None
        self._evaluation_result = None
        
        self.csv_filepath = csv_filepath
    
    @property
    def evaluation_result(self):
        return self._evaluation_result
    
    @evaluation_result.setter
    def evaluation_result(self, value:Namespace):
        self._evaluation_result = value
        
    @property
    def resolution(self):
        return self._resolution
    
    @resolution.setter
    def resolution(self, value:int):
        self._resolution = value
        
    @property
    def zone_dim_meters(self):
        return self._zone_dim_meters
    
    @zone_dim_meters.setter
    def zone_dim_meters(self, value:tuple):
        self._zone_dim_meters = value
        
    @property
    def is_triangle(self):
        return len(self.config_meters) < 2
        
    @property
    def config_meters(self):
        return self._config_meters
    
    @config_meters.setter
    def config_meters(self, value:tuple):
        self._config_meters = value
        
    @property
    def csv_filepath(self):
        return self._csv_filepath
    
    @csv_filepath.setter
    def csv_filepath(self, value:str):
        self._csv_filepath = value
        self.Pr_table = read_csv(value)
    
    @property
    def Pr_table(self):
        return self._Pr_table
    
    @Pr_table.setter
    def Pr_table(self, value:np.ndarray):
        self._Pr_table = value
        self._Pr_grid, self._Pr_step = Pr_table_to_grid(value)
    
    @property
    def Pr_step(self):
        return self._Pr_step
    
    @Pr_step.setter
    def Pr_step(self, value:float):
        self._Pr_step = value
        self.Pr_table = Pr_grid_to_table(self._Pr_grid, value)
    
    @property
    def Pr_grid(self):
        return self._Pr_grid
    
    @Pr_grid.setter
    def Pr_grid(self, value:np.ndarray):
        self._Pr_grid = value
        self.Pr_table = Pr_grid_to_table(value, self._Pr_step)
        
    def __repr__(self):
        return f'{self.__class__.__name__}(resolution={self._resolution}, zone_dim_meters={self._zone_dim_meters}, config_meters={self._config_meters}, csv_filepath={self._csv_filepath})'
































