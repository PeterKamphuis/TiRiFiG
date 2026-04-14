"""Shared helpers for computing graph plot scales."""


def set_plot_scale(values):
    """Return padded [min, max] bounds for plotting a value sequence."""
    min_value = min(values)
    max_value = max(values)
    min_max_diff = max_value - min_value
    percentage_of_min_max_diff = 0.1 * min_max_diff
    lower_bound = min_value - percentage_of_min_max_diff
    upper_bound = max_value + percentage_of_min_max_diff

    if min_max_diff == 0:
        return [lower_bound / 2, upper_bound * 1.5]
    return [lower_bound, upper_bound]
