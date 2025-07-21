#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 01:26:06 2025

@author: mohamed
"""
from configparser import ConfigParser
import os

class INIParser(ConfigParser):
    
    def clean_inline_get(self, section, option):
        value = self.get(section, option)
        value = value.split('#')[0].split(';')[0]
        return value.strip()
    
    def getint(self, section, option):
        value = self.clean_inline_get(section, option)
        return int(value)
    
    def gettuple(self, section, option, type_=float):
        value = self.clean_inline_get(section, option)
        return tuple(type_(p) for p in value.split(','))
    
    def read(self):
        with open(self.config_filepath, 'r') as f:
            super().read_file(f)
    
    @property
    def config_filepath(self):
        current_dirpath = os.path.dirname(
            os.path.abspath(__file__)
        )
        return os.path.join(current_dirpath, 'config.ini')
    