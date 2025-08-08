#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 01:25:01 2025

@author: mohamed
"""
from argparse import Namespace
import numpy as np
from helper import INIParser, namespace_equal, read_csv
import logging
from functools import wraps
from sprinklers import Pr_table_to_grid, Pr_grid_to_table, Pr_table_to_dist, run_simulation

class Model:
    
    def __init__(self, resolution, zone_dim_meters, config_meters, csv_filepath):
        
        self._resolution = resolution
        self._zone_dim_meters = zone_dim_meters
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
        self.Pr_dist = Pr_table_to_dist(value, self._resolution)
    
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
    
    @property
    def Pr_dist(self):
        return self._Pr_dist
    
    @Pr_dist.setter
    def Pr_dist(self, value:np.ndarray):
        self._Pr_dist = value
        
    def __repr__(self):
        return f'{self.__class__.__name__}(resolution={self._resolution}, zone_dim_meters={self._zone_dim_meters}, config_meters={self._config_meters}, csv_filepath={self._csv_filepath})'
































