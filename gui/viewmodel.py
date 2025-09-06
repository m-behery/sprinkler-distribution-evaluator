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
    