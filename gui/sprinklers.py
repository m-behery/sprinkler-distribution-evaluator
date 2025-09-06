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

import numpy as np
import pandas as pd
from argparse import Namespace

def Pr_table_to_grid(Pr_table):
    """
    Convert a Pr measurement table into a 2D grid and extract the step size.

    Parameters:
        Pr_table: 2D array-like, expected shape (N, 3), where columns are:
                  [x_position, y_position, Pr_value]

    Returns:
        Pr_grid (np.ndarray): 2D array of Pr values arranged as a grid
        Pr_step (float): Step size between adjacent positions along one axis
    """
    if Pr_table is None:
        return np.zeros((2,2)), 1
    Pr_table = pd.DataFrame(Pr_table)
    Pr_grid  = Pr_table.pivot(columns=0, index=1, values=2)
    Pr_step  = Pr_grid.index[:2].diff()[-1]
    Pr_grid  = Pr_grid.values
    return Pr_grid, Pr_step

def Pr_grid_to_table(Pr_grid, Pr_step):
    """
    Convert a 2D Pr grid into a flat table suitable for CSV export or other uses.

    Parameters:
        Pr_grid (np.ndarray): 2D array of Pr values
        Pr_step (float): Spacing between grid points along each axis

    Returns:
        Pr_table (np.ndarray): Flattened table with columns [x, y, Pr_value]
    """
    index, columns = map(
        lambda axis: Pr_step * np.arange(Pr_grid.shape[axis]),
        (0,1)
    )
    Pr_grid = pd.DataFrame(Pr_grid, index, columns)
    Pr_grid.reset_index(inplace=True, names=['1'])
    Pr_table = Pr_grid.melt(id_vars=['1'], var_name='0', value_name='2')
    Pr_table.sort_index(axis=1, inplace=True)
    Pr_table = Pr_table.values
    return Pr_table

def Pr_table_to_quadrant(Pr_table, resolution):
    """
    Convert a Pr table into a full quadrant 2D array, mapping Pr values
    to pixel positions scaled by the resolution.

    Parameters:
        Pr_table (np.ndarray): Array with shape (N, 3), columns [x, y, Pr]
        resolution (float): Scaling factor to convert coordinates to pixel indices

    Returns:
        Pr_quadrant (np.ndarray): 2D array representing the quadrant with Pr values
    """
    if Pr_table is None:
        return np.zeros((2,2))
    
    yx_positions = (Pr_table[:,:2][:,::-1] * resolution).astype('int')
    Pr_values = Pr_table[:,-1]
    
    quadrant_pixels = yx_positions.max(axis=0)
    Pr_quadrant = np.zeros(quadrant_pixels)
    
    step = np.diff(np.sort(np.unique(yx_positions[:,0])))[0].item()
    halfstep = step // 2 + 1
    quadrant_h, quadrant_w = Pr_quadrant.shape
    for y in range(0, quadrant_h + 1, step):
        for x in range(0, quadrant_w + 1, step):
            mask = (yx_positions == [y,x]).all(axis=1)
            if not mask.any():
                return Pr_quadrant
            Pr = Pr_values[mask][0]
            y_min = 0 if y == 0 else y - halfstep
            y_max = y + halfstep
            x_min = 0 if x == 0 else x - halfstep
            x_max = x + halfstep
            Pr_quadrant[y_min : y_max, x_min : x_max] = Pr
    return Pr_quadrant

def generate_sliding_window(configuration_pixels, is_triangle):
    """
    Generate a boolean sliding window array representing sprinkler positions
    based on the configuration shape (triangle or rectangle).

    Parameters:
        configuration_pixels (np.ndarray): Array of pixel dimensions [height, width] or [side_length] for triangle.
        is_triangle (bool): Flag indicating if the configuration is triangular.

    Returns:
        window (np.ndarray): Boolean array where True indicates a sprinkler position.
    """
    if is_triangle:
        triangle_s = configuration_pixels[0]
        triangle_h = int(0.866 * triangle_s)
        window_pixels = np.array([2 * triangle_h, triangle_s])
        window = np.zeros(window_pixels, dtype=bool)
        step_y, step_x = np.array(window.shape) // 2
        window[0, step_x]  = True
        window[step_y, 0]  = True
        window[step_y, -1] = True
        window[-1, step_x] = True
    else:
        window_pixels = np.array(configuration_pixels)
        window = np.zeros(window_pixels, dtype=bool)
        window[0, 0]   = True
        window[0, -1]  = True
        window[-1, 0]  = True
        window[-1, -1] = True
    return window

def generate_sprinklers_mask(zone_pixels, sliding_window, is_triangle):
    """
    Generate a boolean mask for sprinkler positions across a zone.

    Parameters:
        zone_pixels (tuple[int, int]): Size of the zone in pixels (height, width).
        sliding_window (np.ndarray): Boolean array representing a single sprinkler configuration.
        is_triangle (bool): Flag indicating if the configuration is triangular.

    Returns:
        sprinklers_mask (np.ndarray): Boolean mask of the same size as the zone, 
                                      where True indicates sprinkler positions.
    """
    sprinklers_mask = np.zeros(zone_pixels, dtype=bool)
    zone_h, zone_w = sprinklers_mask.shape
    step_y, step_x = sliding_window.shape
    
    n_row_passes = 0
    for y in range(0, zone_h - step_y, step_y - 1):
        for x in range(0, zone_w - step_x, step_x - 1):
            zone_portion = sprinklers_mask[y : y + step_y, x : x + step_x]
            zone_portion_h, zone_portion_w = zone_portion.shape
            sprinklers_mask[y : y + step_y, x : x + step_x] = zone_portion | sliding_window[:zone_portion_h, :zone_portion_w]
        n_row_passes += 1
        
    if is_triangle:
        y = n_row_passes * (step_y - 1)
        halfstep_y = step_y // 2 + 1
        half_window = sliding_window[:halfstep_y]
        for x in range(0, zone_w - step_x, step_x - 1):
            zone_portion = sprinklers_mask[y : y + halfstep_y, x : x + step_x]
            zone_portion_h, zone_portion_w = zone_portion.shape
            sprinklers_mask[y : y + halfstep_y, x : x + step_x] = zone_portion | half_window[:zone_portion_h, :zone_portion_w]
    
    return sprinklers_mask

def Pr_quadrant_to_plot(Pr_quadrant):
    """
    Mirror a quadrant of Pr values to create a full symmetric plot.

    Parameters:
        Pr_quadrant (np.ndarray): 2D array representing a single quadrant (top-left).

    Returns:
        Pr_plot (np.ndarray): 2D array of doubled size, mirrored across both axes.
    """
    Pr_plot = np.zeros(np.array(Pr_quadrant.shape) * 2)
    step_y, step_x = Pr_quadrant.shape
    Pr_plot[:step_y, :step_x] = Pr_quadrant[::-1, ::-1]
    Pr_plot[:step_y, step_x:] = Pr_quadrant[::-1]
    Pr_plot[step_y:, :step_x] = Pr_quadrant[:, ::-1]
    Pr_plot[step_y:, step_x:] = Pr_quadrant
    return Pr_plot

def Pr_plot_to_zone(Pr_plot, sprinklers_mask):
    """
    Map a full Pr plot to the sprinkler zone by adding contributions
    from each sprinkler location.

    Parameters:
        Pr_plot (np.ndarray): 2D array of precipitation distribution around a sprinkler.
        sprinklers_mask (np.ndarray): Boolean 2D array indicating sprinkler positions.

    Returns:
        Pr_zone (np.ndarray): 2D array representing the total Pr over the zone.
    """
    step_y, step_x = np.array(Pr_plot.shape) // 2
    yx_sprinklers = np.stack(np.where(sprinklers_mask), axis=1)
    Pr_zone       = np.zeros(sprinklers_mask.shape)
    for y, x in yx_sprinklers:
        y_min, y_max = y - step_y, y + step_y
        x_min, x_max = x - step_x, x + step_x
        if y_min < 0 and x_min < 0:
            plot_portion = Pr_plot[-y_min:, -x_min:]
        elif y_min < 0:
            plot_portion = Pr_plot[-y_min:]
        elif x_min < 0:
            plot_portion = Pr_plot[:, -x_min:]
        else:
            plot_portion = Pr_plot.copy()
        if y_min < 0:
            y_min = 0
        if x_min < 0:
            x_min = 0
        zone_portion = Pr_zone[y_min : y_max, x_min : x_max]
        zone_portion_h, zone_portion_w = zone_portion.shape
        Pr_zone[y_min : y_max, x_min : x_max] = zone_portion + plot_portion[:zone_portion_h, :zone_portion_w]
    return Pr_zone

def Pr_zone_to_homogenous_plot(Pr_zone, sliding_window, is_triangle):
    """
    Extract a representative "homogeneous plot" from the irrigation zone.

    This function selects a portion of the full precipitation zone (Pr_zone)
    that corresponds to a single repeatable unit of the sprinkler configuration.

    Parameters:
        Pr_zone (np.ndarray): 2D array representing total precipitation over the zone.
        sliding_window (np.ndarray): 2D boolean array representing sprinkler placement pattern.
        is_triangle (bool): Whether the sprinkler configuration is triangular or rectangular.

    Returns:
        homogenous_plot (np.ndarray): Subsection of Pr_zone representing one repeatable unit.
    """
    window_h, window_w = sliding_window.shape
    if is_triangle:
        halfwindow_h = window_h // 2
        window_halfw = window_w // 2
        homogenous_plot = Pr_zone[:halfwindow_h, window_halfw : window_w + window_halfw]
    else:
        homogenous_plot = Pr_zone[:window_h, :window_w]
    return homogenous_plot
    
def compute_DU(Pr_homogenous_plot):
    """
    Compute the Distribution Uniformity (DU) of a precipitation plot.

    DU is the ratio of the average of the lowest-quartile (LQ) precipitation
    values to the overall mean, expressed as a percentage.

    Parameters:
        Pr_homogenous_plot (np.ndarray): 2D array representing precipitation
                                         over a homogeneous plot of the sprinkler layout.

    Returns:
        DU (float): Distribution uniformity in percentage. Returns np.nan
                    if no lowest-quartile values exist.
    """
    LQ_mask = Pr_homogenous_plot < np.quantile(Pr_homogenous_plot, 0.25)
    if not LQ_mask.any():
        return np.nan
    LQ_height = np.mean(Pr_homogenous_plot[LQ_mask])
    mean_height = np.mean(Pr_homogenous_plot)
    eps = np.finfo(mean_height.dtype).eps
    DU = round(LQ_height / (mean_height + eps) * 100, 2)
    DU = DU.item()
    return DU
    
def compute_CU(Pr_homogenous_plot):
    """
    Compute the Christiansen Uniformity (CU) of a precipitation plot.

    CU measures the uniformity of water distribution across the plot. 
    It ranges from 0% (completely non-uniform) to 100% (perfectly uniform).

    Parameters:
        Pr_homogenous_plot (np.ndarray): 2D array representing precipitation
                                         over a homogeneous plot of the sprinkler layout.

    Returns:
        CU (float): Christiansen Uniformity percentage. Returns np.nan if
                    CU is negative due to numerical errors.
    """
    mean_height = np.mean(Pr_homogenous_plot)
    eps = np.finfo(mean_height.dtype).eps
    CU = round(100 * (1 - np.sum(np.abs(Pr_homogenous_plot - mean_height)) / (Pr_homogenous_plot.size * mean_height + eps)), 2)
    CU = CU.item()
    if CU < 0.0:
        return np.nan
    return CU

def evaluate(resolution:int, zone_meters:tuple, configuration_meters:tuple, Pr_table:np.ndarray):
    """
    Evaluate sprinkler distribution uniformity given the layout and measurements.

    Parameters:
        resolution (int): Scaling factor, pixels per meter.
        zone_meters (tuple[float, float]): Physical dimensions of the irrigation zone (width, height) in meters.
        configuration_meters (tuple[float] or tuple[float, float]): Sprinkler configuration dimensions.
            - Single value → triangular layout (equilateral triangle)
            - Two values → rectangular layout
        Pr_table (np.ndarray): CSV table of precipitation measurements with positions and values.

    Returns:
        Namespace: Contains
            - zone (np.ndarray): Precipitation map over the zone.
            - homogenous_plot (np.ndarray): A quadrant slice representing a homogeneous plot.
            - metrics (Namespace): Contains Christiansen Uniformity (CU) and Distribution Uniformity (DU)
    """
    assert type(resolution) is int, \
           '`resolution` should be an integer.'
    
    assert type(zone_meters) is tuple and \
           len(zone_meters) == 2 and \
           all(type(x) in (int, float) for x in zone_meters), \
           '`zone_meters` should be a tuple of 2 numerical values.'
    
    assert type(configuration_meters) is tuple and \
           len(configuration_meters) in {1,2} and \
           all(type(x) in (int, float) for x in configuration_meters), \
           '`configuration_meters` should be a tuple of 1 or 2 numerical values.'
    
    zone_meters, configuration_meters = map(
        lambda x: np.array(x[::-1]), (zone_meters, configuration_meters)
    )
    is_triangle         = configuration_meters.size == 1
    zone_pixels         = (resolution * zone_meters).astype('int')
    configuration_pixels = (resolution * configuration_meters).astype('int')

    sliding_window  = generate_sliding_window(configuration_pixels, is_triangle)
    sprinklers_mask = generate_sprinklers_mask(zone_pixels, sliding_window, is_triangle)
    
    Pr_quadrant = Pr_table_to_quadrant(Pr_table, resolution)
    Pr_plot     = Pr_quadrant_to_plot(Pr_quadrant)
    
    Pr_zone            = Pr_plot_to_zone(Pr_plot, sprinklers_mask)
    Pr_homogenous_plot = Pr_zone_to_homogenous_plot(Pr_zone, sliding_window, is_triangle)

    CU = compute_CU(Pr_homogenous_plot)
    DU = compute_DU(Pr_homogenous_plot)
    
    return Namespace(
        zone            = Pr_zone,
        homogenous_plot = Pr_homogenous_plot,
        metrics         = Namespace(DU=DU, CU=CU)
    )
