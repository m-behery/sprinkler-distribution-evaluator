#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 01:25:01 2025

@author: mohamed
"""
import numpy as np

class Model:
    
    def __init__(self, resolution, zone_dim_meters, config_meters, csv_filepath):
        self._resolution = resolution
        self._zone_dim_meters = zone_dim_meters
        self._config_meters = config_meters
        self.csv_filepath = csv_filepath
        
    @property
    def resolution(self):
        return self._resolution
        
    @property
    def zone_dim_meters(self):
        return self._zone_dim_meters
        
    @property
    def config_meters(self):
        return self._config_meters
        
    @property
    def csv_filepath(self):
        return self._csv_filepath
    
    @csv_filepath.setter
    def csv_filepath(self, value:str):
        self._csv_filepath = value
        self.Pr_table = self.read_csv(value)
    
    @staticmethod
    def read_csv(filepath):
        return np.loadtxt(filepath, delimiter=',')
    
    def __repr__(self):
        return f'{self.__class__.__name__}(resolution={self.resolution}, zone_dim_meters={self.zone_dim_meters}, config_meters={self.config_meters}, csv_filepath={self.csv_filepath})'
