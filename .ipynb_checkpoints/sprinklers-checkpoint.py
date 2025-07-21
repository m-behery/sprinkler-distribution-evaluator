import numpy as np
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────

# Defines how many pixels represent one meter
RESOLUTION      = 5

# The physical size of the simulated irrigation zone (in meters)
ZONE_DIM_METERS = np.array([50, 50])

# Sprinkler layout configuration:
#   - One value → triangular grid (equilateral spacing)
#   - Two values → rectangular grid (x, y spacing)
CONFIG_METERS   = np.array([5])

# Path to the CSV file containing measured precipitation values
CSV_FILEPATH    = './van 18.csv'

# ──────────────────────────────────────────────────────────────────────
# GEOMETRY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────

def create_sprinkler_window(config_pixels):
    """
    Creates a binary mask ("window") representing sprinkler positions in a single tile
    depending on the sprinkler layout (triangular or rectangular).
    
    Args:
        config_pixels (np.ndarray): Sprinkler spacing in pixels.
    
    Returns:
        window (np.ndarray[bool]): A binary mask with `True` where sprinklers are placed.
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

def generate_zone(zone_shape, window):
    """
    Repeats the sprinkler window across the whole zone to simulate a regular grid of sprinklers.
    For triangular layouts, a bottom row is added to complete the pattern.

    Args:
        zone_shape (tuple[int]): Size of the irrigation zone in pixels.
        window (np.ndarray[bool]): Sprinkler placement template.

    Returns:
        zone (np.ndarray[bool]): Zone map with all sprinkler positions.
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

def load_sprinkler_distribution(filepath, resolution):
    """
    Loads a sprinkler precipitation profile from CSV and maps it to a grid.

    CSV columns:
      0: x-coordinate (meters)
      1: y-coordinate (meters)
      2: precipitation (e.g., mm/h or L/m²)

    Args:
        filepath (str): Path to CSV file.
        resolution (int): Pixels per meter.

    Returns:
        distribution (np.ndarray): 2D precipitation rate grid.
    """
    table = np.loadtxt(filepath, delimiter=',')
    positions = (table[:, :2][:, ::-1] * resolution).astype(int)  # [y, x] in pixels
    values = table[:, -1]
    shape = positions.max(axis=0)
    distribution = np.zeros(shape)
    step = np.diff(np.sort(np.unique(positions[:, 0])))[0]
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

def tile_distribution(dist):
    """
    Tiles the sprinkler distribution into a 2x2 symmetric grid.

    This replicates the measured precipitation into all 4 quadrants
    (simulating omnidirectional sprinkler patterns).

    Args:
        dist (np.ndarray): Base distribution from CSV.

    Returns:
        tiled (np.ndarray): Tiled 2D pattern.
    """
    h, w = dist.shape
    tiled = np.zeros((2 * h, 2 * w))
    tiled[:h, :w] = dist[::-1, ::-1]  # top-left
    tiled[:h, w:] = dist[::-1]       # top-right
    tiled[h:, :w] = dist[:, ::-1]    # bottom-left
    tiled[h:, w:] = dist             # bottom-right
    return tiled

def apply_distribution(zone, sprinklers, pattern, step):
    """
    Applies the sprinkler pattern at every sprinkler location in the zone.

    Args:
        zone (np.ndarray): Base zone (only shape is used here).
        sprinklers (np.ndarray): List of [y, x] sprinkler coordinates.
        pattern (np.ndarray): 2D precipitation pattern.
        step (int): Half-width of the pattern application window.

    Returns:
        zone (np.ndarray): Final cumulative precipitation in the zone.
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
    Distribution Uniformity: Mean of the lowest 25% of values
    divided by the mean of all values.
    """
    LQ = plot < np.quantile(plot, 0.25)
    return round(np.mean(plot[LQ]) / np.mean(plot) * 100, 2)

def calculate_CU(plot):
    """
    Christiansen Uniformity: 100 * (1 - (mean deviation / mean)).
    """
    mean_val = np.mean(plot)
    return round(100 * (1 - np.sum(np.abs(plot - mean_val)) / (plot.size * mean_val)), 2)

# ──────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ──────────────────────────────────────────────────────────────────────

def main():
    # Convert physical dimensions to pixels
    zone_pixels   = (RESOLUTION * ZONE_DIM_METERS).astype(int)
    config_pixels = (RESOLUTION * CONFIG_METERS).astype(int)

    # Create sprinkler layout pattern
    window = create_sprinkler_window(config_pixels)

    # Generate all sprinkler locations across the zone
    sprinklers_mask = generate_zone(zone_pixels, window)
    yx_sprinklers = np.stack(np.where(sprinklers_mask), axis=1)

    # Load the sprinkler's precipitation map and tile it to all directions
    raw_dist = load_sprinkler_distribution(CSV_FILEPATH, RESOLUTION)
    pattern = tile_distribution(raw_dist)
    step = raw_dist.shape[0]  # Assuming square (height = width)

		# Apply all sprinkler patterns to generate the cumulative precipitation rate map
    final_zone = apply_distribution(sprinklers_mask, yx_sprinklers, pattern, step)

    # Visualize the full coverage area
    plt.imshow(final_zone, cmap='viridis')
    for y, x in yx_sprinklers:
        plt.plot(x, y, 'ro', markersize=2)
    plt.title("Sprinkler Coverage")
    plt.colorbar(label="Precipitation Rate (mm/h)")
    plt.show()

    # Crop the homogenous area for analysis (usually centered around sprinklers)
    wh, ww = window.shape
    if CONFIG_METERS.size == 1:  # Triangular layout
        h = wh // 2
        hw = ww // 2
        homogenous = final_zone[:h, hw:ww + hw]
    else:  # Rectangular layout
        homogenous = final_zone[:wh, :ww]

    # Calculate uniformity metrics
    DU = calculate_DU(homogenous)
    CU = calculate_CU(homogenous)

    # Show cropped region and metrics
    plt.imshow(homogenous, cmap='viridis')
    plt.title(f"DU: {DU}%, CU: {CU}%")
    plt.colorbar(label="Precipitation Rate (mm/h)")
    plt.show()

if __name__ == "__main__":
    main()
