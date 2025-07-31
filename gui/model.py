#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 01:25:01 2025

@author: mohamed
"""
from sprinklers import run_simulation
from argparse import Namespace
import numpy as np
from helper import INIParser
import logging
from functools import wraps

class Model:
    
# =============================================================================
#     def __init__(self, resolution, zone_dim_meters, config_meters, csv_filepath):
#         
#         self._autosave = False
#         
#         self._resolution = resolution
#         self._zone_dim_meters = zone_dim_meters
#         self._config_meters = config_meters
#         
#         self._Pr_table = None
#         self._evaluation_result = None
#         
#         self.csv_filepath = csv_filepath
# =============================================================================
    
    def __init__(self):
        
        self._parser = INIParser()
        self._parser.read()
        
        self._autowrite_config = False
        self._autoeval = False
        
        self._resolution = self._parser.getint('Display', 'RESOLUTION')
        self._zone_dim_meters = self._parser.gettuple('Sprinklers', 'ZONE_DIM_METERS')
        self._config_meters = self._parser.gettuple('Sprinklers', 'CONFIG_METERS')
        
        self._Pr_table = None
        self._evaluation_result = None
        
        self.csv_filepath = self._parser.clean_inline_get('Sprinklers', 'CSV_FILEPATH')
        
    def autosync(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)
            if getattr(self, 'autoeval', False):
                self.evaluate()
                logging.debug(f"Auto-evaluated after `{method.__name__}`")
            if getattr(self, 'autowrite_config', False):
                self.write_config()
                logging.debug(f"Auto-wrote configuration after `{method.__name__}`")
            return result
        return wrapper
        
    @property
    def parser(self):
        return self._parser
        
    @property
    def autowrite_config(self):
        return self._autowrite_config
        
    @autowrite_config.setter
    def autowrite_config(self, value:bool):
        self._autowrite_config = value
        
    @property
    def autoeval(self):
        return self._autoeval
        
    @autoeval.setter
    def autoeval(self, value:bool):
        self._autoeval = value
    
    def update(self):
        if self.autoeval:
            self.evaluate()
            
        if self.autowrite_config:
            self.write_config()
    
    def evaluate(self):
        self.evaluation_result = run_simulation(self.resolution,
                                                self.zone_dim_meters,
                                                self.config_meters,
                                                self.Pr_table)
        
    def write_config(self):
        serialize_floats = lambda floats: ', '.join(map(str, floats))
        self.parser.set('Display', 'RESOLUTION', str(self.resolution))
        self.parser.set('Sprinklers', 'ZONE_DIM_METERS', serialize_floats(self.zone_dim_meters))
        self.parser.set('Sprinklers', 'CONFIG_METERS', serialize_floats(self.config_meters))
        self.parser.set('Sprinklers', 'CSV_FILEPATH', self.csv_filepath)
        self.parser.write()
    
    @property
    def evaluation_result(self):
        return self._evaluation_result
    
    @evaluation_result.setter
    def evaluation_result(self, value:Namespace):
        self._evaluation_result = value
        
    @property
    def resolution(self):
        return self._resolution
    
    @autosync
    @resolution.setter
    def resolution(self, value:int):
        self._resolution = value
        
    @property
    def zone_dim_meters(self):
        return self._zone_dim_meters
    
    @autosync
    @zone_dim_meters.setter
    def zone_dim_meters(self, value:tuple):
        self._zone_dim_meters = value
        
    @property
    def config_meters(self):
        return self._config_meters
    
    @autosync
    @config_meters.setter
    def config_meters(self, value:tuple):
        self._config_meters = value
        
    @property
    def csv_filepath(self):
        return self._csv_filepath
    
    @autosync
    @csv_filepath.setter
    def csv_filepath(self, value:str):
        self._csv_filepath = value
        self._Pr_table = self.read_csv(value)
    
    @property
    def Pr_table(self):
        return self._Pr_table
    
    @Pr_table.setter
    def Pr_table(self, value:np.array):
        if not np.array_equal(self.Pr_table, value):
            self._Pr_table = value
            self.evaluate()
            self.write_csv(self.csv_filepath, value)
    
    @staticmethod
    def read_csv(filepath:str):
        try:
            return np.loadtxt(filepath, delimiter=',')
        except Exception as e:
            logging.warning(f"Failed to load CSV from {filepath}: {e}")
            return np.empty((0, 0))
    
    @staticmethod
    def write_csv(filepath:str, table:np.array):
        return np.savetxt(filepath, table, delimiter=',')
    
    def __repr__(self):
        return f'{self.__class__.__name__}(resolution={self.resolution}, zone_dim_meters={self.zone_dim_meters}, config_meters={self.config_meters}, csv_filepath={self.csv_filepath})'
