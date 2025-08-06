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

class Model:
    
    def __init__(self, resolution, zone_dim_meters, config_meters, csv_filepath):
        
        self._resolution = resolution
        self._zone_dim_meters = zone_dim_meters
        self._config_meters = config_meters
        self._csv_filepath = None
        self._Pr_table = None
        self._evaluation_result = None
        
        self.csv_filepath = csv_filepath
    
    @property
    def evaluation_result(self):
        return self._evaluation_result
    
    @evaluation_result.setter
    def evaluation_result(self, value:Namespace):
        if not namespace_equal(self._evaluation_result, value):
            self._evaluation_result = value
        
    @property
    def resolution(self):
        return self._resolution
    
    @resolution.setter
    def resolution(self, value:int):
        if self._resolution != value:
            self._resolution = value
        
    @property
    def zone_dim_meters(self):
        return self._zone_dim_meters
    
    @zone_dim_meters.setter
    def zone_dim_meters(self, value:tuple):
        if self._zone_dim_meters != value:
            self._zone_dim_meters = value
        
    @property
    def config_meters(self):
        return self._config_meters
    
    @config_meters.setter
    def config_meters(self, value:tuple):
        if self._config_meters != value:
            self._config_meters = value
        
    @property
    def csv_filepath(self):
        return self._csv_filepath
    
    @csv_filepath.setter
    def csv_filepath(self, value:str):
        if self._csv_filepath != value:
            self._csv_filepath = value
            self.Pr_table = read_csv(value)
    
    @property
    def Pr_table(self):
        return self._Pr_table
    
    @Pr_table.setter
    def Pr_table(self, value:np.ndarray):
        if not np.array_equal(self._Pr_table, value):
            self._Pr_table = value
    
    def __repr__(self):
        return f'{self.__class__.__name__}(resolution={self._resolution}, zone_dim_meters={self._zone_dim_meters}, config_meters={self._config_meters}, csv_filepath={self._csv_filepath})'
