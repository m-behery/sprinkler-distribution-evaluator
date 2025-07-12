# Sprinkler Pattern Simulation

This tool simulates the precipitation rate distribution of sprinkler layouts (triangular or rectangular) across a user-defined irrigation zone. It uses a real measured sprinkler profile (in mm/h) from a CSV file and tiles it across the field based on the layout configuration. The simulation visualizes the resulting precipitation map and calculates uniformity metrics such as Distribution Uniformity (DU) and Christiansen Uniformity (CU).

## Features

- Supports both triangular and rectangular sprinkler grids.
- Visualizes the combined precipitation rate across the entire zone.
- Computes DU and CU for the central homogeneous patch.
- Uses real sprinkler measurement data from CSV files.

## Configuration

You can modify the simulation settings at the top of the script:

```python
RESOLUTION      = 5                  # pixels per meter
ZONE_DIM_METERS = np.array([50, 50]) # size of the simulated field in meters
CONFIG_METERS   = np.array([5])      # layout spacing: [spacing] or [y_spacing, x_spacing]
CSV_FILEPATH    = './van 18.csv'     # path to sprinkler profile CSV

