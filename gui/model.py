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
        
        self._Pr_table = None
        
        self.csv_filepath = csv_filepath
        
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
        self._Pr_table = self.read_csv(value)
    
    @property
    def Pr_table(self):
        return self._Pr_table
    
    @Pr_table.setter
    def Pr_table(self, value:np.array):
        self._Pr_table = value
        self.write_csv(self.csv_filepath, value)
        
    @staticmethod
    def read_csv(filepath:str):
        try:
            return np.loadtxt(filepath, delimiter=',')
        except:
            return np.array([[]])
    
    @staticmethod
    def write_csv(filepath:str, table:np.array):
        return np.savetxt(filepath, table, delimiter=',')
    
    def __repr__(self):
        return f'{self.__class__.__name__}(resolution={self.resolution}, zone_dim_meters={self.zone_dim_meters}, config_meters={self.config_meters}, csv_filepath={self.csv_filepath})'
