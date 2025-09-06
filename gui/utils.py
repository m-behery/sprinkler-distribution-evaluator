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

from configparser import ConfigParser
from argparse import Namespace
import os
import numpy as np
import pandas as pd
import logging

class INIParser(ConfigParser):
    """
    Extended ConfigParser that provides additional convenience methods for
    reading/writing config values with inline comments removed and type conversion.
    """
    def clean_inline_get(self, section, option):
        """
        Read a value from the given section/option, removing any inline comments
        (both '#' and ';') and stripping whitespace.
        """
        value = self.get(section, option)
        value = value.split('#')[0].split(';')[0]
        return value.strip()
    
    def getint(self, section, option):
        """
        Read an integer value from the config.
        """
        value = self.clean_inline_get(section, option)
        return int(value)
    
    def gettuple(self, section, option, type_=float):
        """
        Read a comma-separated value and convert it into a tuple of the given type.
        Default type is float.
        """
        value = self.clean_inline_get(section, option)
        return tuple(type_(p) for p in value.split(','))
    
    def read(self):
        """
        Read the configuration file from the standard config filepath.
        """
        with open(self.config_filepath, 'r') as f:
            super().read_file(f)
    
    def write(self):
        """
        Write the configuration back to the file, preserving spacing around delimiters.
        """
        with open(self.config_filepath, 'w') as f:
            super().write(f, space_around_delimiters=True)
    
    @property
    def config_filepath(self):
        """
        Returns the full path to the configuration file (config.ini) located in the
        same directory as this script.
        """
        try:
            current_dirpath = os.path.dirname(
                os.path.abspath(__file__)
            )
            return os.path.join(current_dirpath, 'config.ini')
        except IOError as e:
            logging.error(f"Failed to write config to {self.config_filepath}: {e}")

def are_instances(type_, *objs):
    """
    Check if all provided objects are instances of the given type.
    
    Parameters:
        type_: Type to check against (e.g., int, str, Namespace)
        *objs: Any number of objects to check
    
    Returns:
        bool: True if all objects are of the given type, False otherwise
    """
    return all(map(lambda x: isinstance(x, type_), objs))

def namespace_equal(ns1, ns2):
    """
    Recursively compare two argparse.Namespace objects for equality.

    Allowed value types: Namespace, np.ndarray, int, float, str.

    Parameters:
        ns1, ns2: Namespace objects to compare

    Returns:
        bool: True if both namespaces are equal, False otherwise
    """
    if not are_instances(Namespace, ns1, ns2):
        return False
    ns1_keys, ns2_keys = map(lambda x: set(x.__dict__.keys()), (ns1, ns2))
    if ns1_keys != ns2_keys:
        return False
    for key in ns1.__dict__:
        v1, v2 = ns1.__dict__[key], ns2.__dict__[key]
        assert all([
            type(v) in {
                Namespace, np.ndarray, int, float, str
            } for v in (v1, v2)
        ]), 'The only types of allowed within a Namespace are {Namespace, np.ndarray, int, float, str}'
        if type(v1) is not type(v2):
            return False
        elif are_instances(Namespace, v1, v2):
            if not namespace_equal(v1, v2):
                return False
        elif are_instances(np.ndarray, v1, v2):
            if not np.array_equal(v1, v2):
                return False
        elif v1 != v2:
            return False
    return True

def read_csv(csv_filepath):
    """
    Read a CSV file into a numpy array.

    Parameters:
        csv_filepath: Path to the CSV file

    Returns:
        np.ndarray: CSV data as a 2D array, or None if loading fails
    """
    try:
        table = pd.read_csv(csv_filepath, header=None)
        table = table.values
        return table
    except Exception as e:
        logging.error(f'Failed to load CSV file from "{csv_filepath}.\nError Details: {e}"')
        return None

def write_csv(filepath:str, table:np.array):
    """
    Save a numpy array to a CSV file.

    Parameters:
        filepath: Path to save the CSV file
        table: 2D numpy array to save
    """
    return np.savetxt(filepath, table, delimiter=',')