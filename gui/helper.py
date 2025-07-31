#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 01:26:06 2025

@author: mohamed
"""
from configparser import ConfigParser
from argparse import Namespace
import os
import numpy as np
import logging

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
    
    def write(self):
        with open(self.config_filepath, 'w') as f:
            super().write(f, space_around_delimiters=True)
    
    @property
    def config_filepath(self):
        try:
            current_dirpath = os.path.dirname(
                os.path.abspath(__file__)
            )
            return os.path.join(current_dirpath, 'config.ini')
        except IOError as e:
            logging.error(f"Failed to write config to {self.config_filepath}: {e}")

def are_instances(*objs, type_):
    return all(map(lambda x: isinstance(x, type_), objs))

def namespace_equal(ns1, ns2):
    if not are_instances(ns1, ns2, Namespace):
        raise NotImplementedError('Both args are meant to be of `argparse.Namespace` type.')
    ns1_keys, ns2_keys = map(lambda x: set(x.__dict__.keys()), (ns1, ns2))
    if ns1_keys != ns2_keys:
        return False
    for key in ns1.__dict__:
        v1, v2 = ns1.__dict__[key], ns2.__dict__[key]
        if type(v1) is not type(v2):
            return False
        elif are_instances(v1, v2, Namespace) and not namespace_equal(v1, v2):
            return False
        elif are_instances(v1, v2, np.ndarray) and not np.array_equal(v1, v2):
            return False
        elif v1 != v2:
            return False
    return True
    