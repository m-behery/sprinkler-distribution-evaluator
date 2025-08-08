#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 02:51:13 2025

@author: mohamed
"""

import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
from argparse import Namespace
from mpl_toolkits.axes_grid1 import make_axes_locatable

import matplotlib
matplotlib.use('Agg')

import warnings
warnings.filterwarnings("ignore", message="FigureCanvasAgg is non-interactive.*")

# ──────────────────────────────────────────────────────────────────────
# GEOMETRY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def create_sprinkler_window(config_pixels:np.ndarray):
    """
    Creates a binary mask representing sprinkler positions within a tile
    based on the specified layout (triangular if one value is given, else rectangular).
    
    Args:
        config_pixels (np.ndarray): Sprinkler spacing in pixels (1 value = triangular layout, 2 values = rectangular).
    
    Returns:
        window (np.ndarray[bool]): A binary mask with `True` at sprinkler positions.
    """
    if config_pixels.size == 1:
        # Triangular layout
        s = config_pixels[0]
        h = int(0.866 * s)  # Height of equilateral triangle (≈ √3/2 * side)
        window_shape = [2 * h, s]
        window = np.zeros(window_shape, dtype=bool)
        step_y, step_x = np.array(window.shape) // 2

        # Place sprinklers at triangle corners
        window[0, step_x]  = True
        window[step_y, 0]  = True
        window[step_y, -1] = True
        window[-1, step_x] = True
    else:
        # Rectangular layout
        window_shape = config_pixels
        window = np.zeros(window_shape, dtype=bool)

        # Place sprinklers at the four corners of the rectangle
        window[0, 0]   = True
        window[0, -1]  = True
        window[-1, 0]  = True
        window[-1, -1] = True

    return window

def generate_zone(zone_shape:tuple[int], window:np.ndarray[bool]):
    """
    Tiles the sprinkler window across the zone to simulate the full sprinkler grid.
    Adds a bottom row in triangular layout to complete staggered coverage.
    
    Args:
        zone_shape (tuple[int]): Zone dimensions in pixels.
        window (np.ndarray[bool]): Sprinkler tile template.

    Returns:
        zone (np.ndarray[bool]): Boolean array marking sprinkler locations.
    """
    step_y, step_x = window.shape
    zone = np.zeros(zone_shape, dtype=bool)
    n_row_passes = 0

    for y in range(0, zone.shape[0] - step_y, step_y - 1):
        for x in range(0, zone.shape[1] - step_x, step_x - 1):
            zp = zone[y:y+step_y, x:x+step_x]
            zone[y:y+step_y, x:x+step_x] = zp | window[:zp.shape[0], :zp.shape[1]]
        n_row_passes += 1

    # Additional row for triangle layout to simulate staggered coverage
    if window.shape[0] != window.shape[1]:  
        y = n_row_passes * (step_y - 1)
        halfstep_y = step_y // 2 + 1
        half_window = window[:halfstep_y]
        for x in range(0, zone.shape[1] - step_x, step_x - 1):
            zp = zone[y:y+halfstep_y, x:x+step_x]
            zone[y:y+halfstep_y, x:x+step_x] = zp | half_window[:zp.shape[0], :zp.shape[1]]

    return zone

# ──────────────────────────────────────────────────────────────────────
# DISTRIBUTION MODEL
# ──────────────────────────────────────────────────────────────────────

def Pr_table_to_step(Pr_table:np.ndarray):
    try:
        return np.diff(np.sort(np.unique(Pr_table[:, 0])))[0]
    except IndexError:
        return 1

def Pr_table_to_grid(Pr_table:np.ndarray):
    Pr_grid = Pr_table_to_dist(Pr_table, 1)
    Pr_step = Pr_table_to_step(Pr_table)
    return Pr_grid, Pr_step

def Pr_grid_to_table(Pr_grid:np.ndarray, Pr_step:float):
    n = min(Pr_grid.shape)
    distances = np.cumsum(np.ones(n) * Pr_step)
    Pr_table = np.empty((0, 3))
    for i in range(n):
        for j in range(n):
            Pr_table = np.concat([
                [[distances[j], distances[i], Pr_grid[i, j]]],
                Pr_table
            ], axis=0)
    return Pr_table

def Pr_table_to_dist(Pr_table:np.ndarray, resolution:int):
    """
    Maps precipitation measurements from the CSV-like input table to a pixel grid.
    
    Args:
        Pr_table (np.ndarray): Columns = [x, y, precipitation in mm/h] (in meters).
        resolution (int): Pixels per meter.

    Returns:
        distribution (np.ndarray): 2D array representing precipitation rate per pixel.
    """
    if Pr_table.size == 3:
        return None
    positions = (Pr_table[:, :2][:, ::-1] * resolution).astype(int)  # [y, x] in pixels
    values = Pr_table[:, -1]
    shape = positions.max(axis=0)
    distribution = np.zeros(shape)
    step = Pr_table_to_step(positions)
    halfstep = step // 2 + 1

    for y in range(0, shape[0]+1, step):
        for x in range(0, shape[1]+1, step):
            mask = (positions == [y, x]).all(axis=1)
            if not np.any(mask): continue
            Pr = values[mask][0]
            y_min, y_max = max(0, y - halfstep), y + halfstep
            x_min, x_max = max(0, x - halfstep), x + halfstep
            distribution[y_min:y_max, x_min:x_max] = Pr
            
    return distribution

def tile_distribution(dist:np.ndarray):
    """
    Mirrors the measured precipitation pattern into all 4 quadrants
    to simulate omnidirectional sprinkler behavior.
    
    Args:
        dist (np.ndarray): Original precipitation map.

    Returns:
        tiled (np.ndarray): Symmetrically tiled 2D pattern.
    """
    h, w = dist.shape
    tiled = np.zeros((2 * h, 2 * w))
    tiled[:h, :w] = dist[::-1, ::-1]  # top-left
    tiled[:h, w:] = dist[::-1]       # top-right
    tiled[h:, :w] = dist[:, ::-1]    # bottom-left
    tiled[h:, w:] = dist             # bottom-right
    return tiled

def apply_distribution(zone:np.ndarray, sprinklers:np.ndarray, pattern:np.ndarray, step:int):
    """
    Adds the precipitation pattern to each sprinkler location across the zone.

    Args:
        zone (np.ndarray): Zone shape used to define output dimensions.
        sprinklers (np.ndarray): [y, x] sprinkler coordinates.
        pattern (np.ndarray): Precipitation pattern for a single sprinkler.
        step (int): Half-width of the pattern (pattern assumed square).

    Returns:
        zone (np.ndarray): Cumulative precipitation map.
    """
    zone = np.zeros_like(zone, dtype=float)

    for y, x in sprinklers:
        y_min, y_max = y - step, y + step
        x_min, x_max = x - step, x + step
        plot_slice = pattern.copy()

        # Handle boundary clipping
        if y_min < 0: plot_slice = plot_slice[-y_min:]
        if x_min < 0: plot_slice = plot_slice[:, -x_min:]
        y_min = max(y_min, 0)
        x_min = max(x_min, 0)

        # Overlay the pattern
        zp = zone[y_min:y_max, x_min:x_max]
        ps = plot_slice[:zp.shape[0], :zp.shape[1]]
        zone[y_min:y_max, x_min:x_max] = zp + ps

    return zone

# ──────────────────────────────────────────────────────────────────────
# UNIFORMITY CALCULATIONS
# ──────────────────────────────────────────────────────────────────────

def calculate_DU(plot):
    """
    Distribution Uniformity: Ratio of mean of lowest 25% values
    to the mean of all values, expressed as a percentage.
    """
    LQ = plot < np.quantile(plot, 0.25)
    if LQ.any():
        return round(np.mean(plot[LQ]) / (np.mean(plot) + 1e-6) * 100, 2).item()
    return 0.0

def calculate_CU(plot):
    """
    Christiansen Uniformity: Measures uniformity using mean absolute deviation,
    expressed as a percentage (higher is better).
    """
    mean_val = np.mean(plot)
    return round(100 * (1 - np.sum(np.abs(plot - mean_val)) / (plot.size * mean_val + 1e-6)), 2).item()

# ──────────────────────────────────────────────────────────────────────
# VISUALIZE PLOTS
# ──────────────────────────────────────────────────────────────────────

def fig2image(fig):
    """
    Converts a Matplotlib figure to a NumPy image array.
    """
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image = Image.open(buf)
    return np.array(image)

def display_zone(zone, yx_sprinklers):
    """
    Plots the full irrigation zone with all sprinkler locations and intensity map.
    """
    heatmap = plt.imshow(zone, cmap='viridis', origin='lower')
    for y, x in yx_sprinklers:
        plt.plot(x, y, 'ro', markersize=2)
    plt.title("Sprinkler Coverage", fontweight='bold', pad=25, fontsize=15)
    return heatmap
    
def display_homogenous_plot(homogenous_plot):
    """
    Displays a zoomed-in homogeneous plot centered on a tile.
    """
    heatmap = plt.imshow(homogenous_plot, cmap='viridis', origin='lower')
    plt.title("Homogenous Plot", fontweight='bold', pad=25, fontsize=15)
    return heatmap
    
def scaled_ticks(N:int, resolution:int, n_ticks:int=6):
    """
    Generates scaled tick positions and labels based on resolution.
    
    Args:
        N (int): Number of pixels.
        resolution (int): Pixels per meter.
        n_ticks (int): Desired number of ticks.
    
    Returns:
        tuple: (tick positions, tick labels in meters)
    """
    ticks = np.linspace(0, N, n_ticks)
    labels = np.round(np.array(ticks)/resolution, 1)
    return ticks, labels
    
def prepare_image(display_fn, resolution, max_ticks=8, display=True, **fn_args):
    """
    Prepares and optionally displays a Matplotlib image from a display function.

    Args:
        display_fn (callable): Function to call for plotting (e.g. display_zone).
        resolution (int): Pixels per meter.
        max_ticks (int): Max ticks on the dominant axis.
        display (bool): Whether to show the figure (useful for interactive/debug mode).
        **fn_args: Arguments passed to the display function.

    Returns:
        np.ndarray: Image representation of the figure.
    """
    fig = plt.figure()
    heatmap = display_fn(**fn_args)
    
    ax = plt.gca()
    ax.set_aspect('equal')
    
    image = sorted(fn_args.values(), key=lambda arg: arg.size, reverse=True)[0]
    height, width = image.shape
    min_ticks = int(max_ticks * min(height, width) / max(height, width))
    if height > width:
        w_ticks = min_ticks
        h_ticks = max_ticks
    else:
        w_ticks = max_ticks
        h_ticks = min_ticks
        
    xticks, xlabels = scaled_ticks(width, resolution, w_ticks)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels, fontsize=8)
    
    yticks, ylabels = scaled_ticks(height, resolution, h_ticks)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=8)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    ax.set_xlabel("Width (m)", labelpad=10, fontsize=8)
    ax.set_ylabel("Height (m)", labelpad=10, fontsize=8)
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.4)  # size = width, pad = gap
    cbar = fig.colorbar(heatmap, cax=cax)
    cbar.set_label("Precipitation Rate (mm/h)", labelpad=5, fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    
    plt.tight_layout()
    plt.show()
    
    image = fig2image(fig)
    if not display:
        plt.close(fig)
    return image

# ──────────────────────────────────────────────────────────────────────
# SIMULATION EXECUTION
# ──────────────────────────────────────────────────────────────────────

def run_simulation(resolution:int, zone_dim_meters:tuple, config_meters:tuple, Pr_dist:np.ndarray, display=False):
    """
    Runs the entire sprinkler simulation pipeline:
    1. Converts physical dimensions to pixels
    2. Places sprinklers across the zone
    3. Loads and tiles a single-sprinkler precipitation pattern
    4. Applies all patterns to generate the cumulative map
    5. Generates zone and homogenous plot images
    6. Calculates uniformity metrics

    Args:
        resolution (int): Pixels per meter.
        zone_dim_meters (tuple): Zone dimensions in meters (width, height).
        config_meters (tuple): Sprinkler spacing in meters (1 or 2 values).
        Pr_table (np.ndarray): Precipitation data [x, y, value].
        display (bool): Whether to display the plots using plt.show().

    Returns:
        Namespace: Contains zone image, homogenous plot image, and evaluation metrics.
    """
    # Convert physical dimensions to pixels
    zone_pixels  = (resolution * np.array(zone_dim_meters[::-1])).astype(int)
    config_pixels = (resolution * np.array(config_meters[::-1])).astype(int)

    # Create sprinkler layout pattern
    window = create_sprinkler_window(config_pixels)

    # Generate all sprinkler locations across the zone
    sprinklers_mask = generate_zone(zone_pixels, window)
    yx_sprinklers = np.stack(np.where(sprinklers_mask), axis=1)

    # Load the sprinkler's precipitation map and tile it to all directions
    pattern = tile_distribution(Pr_dist)
    step = Pr_dist.shape[0]  # Assuming square (height = width)

	# Apply all sprinkler patterns to generate the cumulative precipitation rate map
    final_zone = apply_distribution(sprinklers_mask, yx_sprinklers, pattern, step)

    # Prepare and visualize the image of the full coverage area
    zone_image = prepare_image(display_zone,
                               resolution, 8, display,
                               zone=final_zone,
                               yx_sprinklers=yx_sprinklers)

    # Crop the homogenous plot for analysis (usually centered around sprinklers)
    wh, ww = window.shape
    if len(config_meters) == 1:  # Triangular layout
        h = wh // 2
        hw = ww // 2
        homogenous_plot = final_zone[:h, hw:ww + hw]
    else:  # Rectangular layout
        homogenous_plot = final_zone[:wh, :ww]

    # Prepare and visualize the homogenous plot image
    homogenous_plot_image = prepare_image(display_homogenous_plot,
                                          resolution, 8, display,
                                          homogenous_plot=homogenous_plot)
        
    # Calculate evaluation metrics
    evaluation_metrics = Namespace(
        DU=calculate_DU(homogenous_plot),
        CU=calculate_CU(homogenous_plot)
    )
    
    result = Namespace(
        zone=zone_image,
        homogenous_plot=homogenous_plot_image,
        metrics=evaluation_metrics,
    )

    return result