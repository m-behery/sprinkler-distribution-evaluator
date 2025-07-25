#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 01:59:18 2025

@author: mohamed
"""
from model import Model
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty
import numpy as np

class ViewModel(QObject):
    
    resolution__changed      = pyqtSignal(int)
    zone_dim_meters__changed = pyqtSignal(tuple)
    config_meters__changed    = pyqtSignal(tuple)
    csv_filepath__changed     = pyqtSignal(str)
    Pr_table__changed        = pyqtSignal(object)
    
    def __init__(self, model:Model):
        super().__init__()
        self._model = model
        
    def get__resolution(self):
        return self._model.resolution
    
    def set__resolution(self, value:int):
        if self._model.resolution != value:
            self._model.resolution = value
            self.resolution__changed.emit(value)
    
    resolution = pyqtProperty(int, fget=get__resolution,
                              fset=set__resolution,
                              notify=resolution__changed)
    
    def get__zone_dim_meters(self):
        return self._model.zone_dim_meters
    
    def set__zone_dim_meters(self, value:tuple):
        if self._model.zone_dim_meters != value:
            self._model.zone_dim_meters = value
            self.zone_dim_meters__changed.emit(value)
            
    zone_dim_meters = pyqtProperty('QVariant', fget=get__zone_dim_meters,
                                   fset=set__zone_dim_meters,
                                   notify=zone_dim_meters__changed)
    
    def get__config_meters(self):
        return self._model.config_meters
    
    def set__config_meters(self, value:tuple):
        if self._model.config_meters != value:
            self._model.config_meters = value
            self.config_meters__changed.emit(value)
            
    config_meters = pyqtProperty('QVariant', fget=get__config_meters,
                                 fset=set__config_meters,
                                 notify=config_meters__changed)
    
    def get__csv_filepath(self):
        return self._model.csv_filepath
    
    def set__csv_filepath(self, value:str):
        if self._model.csv_filepath != value:
            self._model.csv_filepath = value
            self.csv_filepath__changed.emit(value)
            self.Pr_table__changed.emit(self._model.Pr_table)
            
    csv_filepath = pyqtProperty(str, fget=get__csv_filepath,
                               fset=set__csv_filepath,
                               notify=csv_filepath__changed)

    def get__Pr_table(self):
        return self._model.Pr_table
    
    def set__Pr_table(self, value:np.array):
        if not np.array_equal(self._model.Pr_table, value):
            self._model.Pr_table = value
            self.Pr_table__changed.emit(value)
    
    Pr_table = pyqtProperty('QVariant', fget=get__Pr_table,
                            fset=set__Pr_table,
                            notify=Pr_table__changed)