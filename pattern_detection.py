import numpy as np
from scipy.stats import linregress
from param_reader import param_reader

# read the parameters from file
param = param_reader("param.txt")


def is_horizontal(points, tolerance=0.015):  # 1.5% price tolerance
    avg_price = np.mean(points)
    deviation = np.abs(points - avg_price) / avg_price
    return np.all(deviation < tolerance)


def calculate_slope(points):
    slope, intercept, r_value, _, _ = linregress(np.arange(len(points)), points)
    return slope, intercept,r_value**2  # Return slope and R-squared


def pattern_detection(highs, lows):
    # calculate the slops for both
    high_slope, high_C, high_r2 = calculate_slope(highs)
    low_slope, low_C, low_r2 = calculate_slope(lows)

    # Classification conditions PARAM
    angle_threshold = param["angle_threshold"]  # Degrees
    r2_threshold_weak = param["r2_threshold_weak"]
    r2_threshold_strong = param["r2_threshold_strong"]

    # Angles for resistance/support
    high_angle = np.degrees(np.arctan(high_slope))
    low_angle = np.degrees(np.arctan(low_slope))

    # Rectangle conditions
    is_upper_flat = abs(high_angle) < angle_threshold or high_r2 < r2_threshold_weak
    is_lower_flat = abs(low_angle) < angle_threshold or low_r2 < r2_threshold_weak

    if is_upper_flat and is_lower_flat:
        return "rectangle", 0, 0, 0, 0, min(lows), max(highs)

    # Ascending triangle (flat highs, rising lows)
    if (abs(low_angle) >= angle_threshold and low_r2 >= r2_threshold_strong) and is_upper_flat:
        return "ascending_triangle", 0, 0, low_slope, low_C, None, max(highs)

    # Descending triangle (falling highs, flat lows)
    if (abs(high_angle) >= angle_threshold and high_r2 >= r2_threshold_strong) and is_lower_flat:
        return "descending_triangle", high_slope, high_C,0, 0, min(lows), None

    # Symmetrical triangle (converging)
    if (abs(high_angle) >= angle_threshold and high_r2 >= r2_threshold_weak and
          abs(low_angle) >= angle_threshold and low_r2 >= r2_threshold_weak):
        return "symmetrical_triangle", high_slope, high_C, low_slope, low_C, None, None

    return "no_pattern", high_slope,high_C, low_slope,low_C, min(lows), max(highs)