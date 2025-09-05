#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 01:59:18 2025

@author: mohamed
"""
from model import Model
from PyQt5.QtCore import QObject, pyqtSignal, pyqtProperty
import numpy as np
from argparse import Namespace
from utils import namespace_equal

class ViewModel(QObject):
    
    resolution__changed        = pyqtSignal(int)
    zone_dim_meters__changed   = pyqtSignal(tuple)
    config_meters__changed      = pyqtSignal(tuple)
    csv_filepath__changed       = pyqtSignal(str)
    Pr_table__changed          = pyqtSignal(object)
    Pr_step__changed           = pyqtSignal(float)
    Pr_grid__changed           = pyqtSignal(object)
    evaluation_result__changed = pyqtSignal(object)
    
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
            
    zone_dim_meters = pyqtProperty(tuple, fget=get__zone_dim_meters,
                                   fset=set__zone_dim_meters,
                                   notify=zone_dim_meters__changed)
    
    def get__config_meters(self):
        return self._model.config_meters
    
    def set__config_meters(self, value:tuple):
        if self._model.config_meters != value:
            self._model.config_meters = value
            self.config_meters__changed.emit(value)
            
    config_meters = pyqtProperty(tuple, fget=get__config_meters,
                                fset=set__config_meters,
                                notify=config_meters__changed)
    
    def get__csv_filepath(self):
        return self._model.csv_filepath
    
    def set__csv_filepath(self, value:str):
        if self._model.csv_filepath != value:
            self._model.csv_filepath = value
            self.csv_filepath__changed.emit(value)
            self.Pr_table__changed.emit(self._model.Pr_table)
            self.Pr_step__changed.emit(self._model.Pr_step)
            self.Pr_grid__changed.emit(self._model.Pr_grid)
            
    csv_filepath = pyqtProperty(str, fget=get__csv_filepath,
                               fset=set__csv_filepath,
                               notify=csv_filepath__changed)

    def get__Pr_table(self):
        return self._model.Pr_table
    
    def set__Pr_table(self, value:np.array):
        if not np.array_equal(self._model.Pr_table, value):
            self._model.Pr_table = value
            self.Pr_table__changed.emit(value)
            self.Pr_step__changed.emit(self._model.Pr_step)
            self.Pr_grid__changed.emit(self._model.Pr_grid)
    
    Pr_table = pyqtProperty('QVariant', fget=get__Pr_table,
                            fset=set__Pr_table,
                            notify=Pr_table__changed)
    
    def get__Pr_step(self):
        return self._model.Pr_step
     
    def set__Pr_step(self, value:float):
        if self._model.Pr_step != value:
            self._model.Pr_step = value
            self.Pr_step__changed.emit(value)
            self.Pr_table__changed.emit(self._model.Pr_table)
     
    Pr_step = pyqtProperty(float, fget=get__Pr_step,
                           fset=set__Pr_step,
                           notify=Pr_step__changed)

    def get__Pr_grid(self):
        return self._model.Pr_grid
    
    def set__Pr_grid(self, value:np.array):
        if not np.array_equal(self._model.Pr_grid, value):
            self._model.Pr_grid = value
            self.Pr_grid__changed.emit(value)
            self.Pr_table__changed.emit(self._model.Pr_table)
    
    Pr_grid = pyqtProperty('QVariant', fget=get__Pr_grid,
                            fset=set__Pr_grid,
                            notify=Pr_grid__changed)
    
    def get__evaluation_result(self):
        return self._model.evaluation_result
    
    def set__evaluation_result(self, value:Namespace):
        if not namespace_equal(self._model.evaluation_result, value):
            self._model.evaluation_result = value
            self.evaluation_result__changed.emit(value)
    
    evaluation_result = pyqtProperty('QVariant', fget=get__evaluation_result,
                                     fset=set__evaluation_result,
                                     notify=evaluation_result__changed)
    