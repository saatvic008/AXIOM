import numpy as np

def calculate_gini(wealths):
    """
    Calculates the Gini coefficient of a list of wealth values.
    0 = perfect equality, 1 = perfect inequality.
    """
    if not wealths or len(wealths) == 0:
        return 0.0
    
    wealths = np.array(wealths)
    if wealths.sum() == 0:
        return 0.0
    
    # Sort wealths
    sorted_wealths = np.sort(wealths)
    n = len(wealths)
    index = np.arange(1, n + 1)
    
    # Gini formula
    return (np.sum((2 * index - n - 1) * sorted_wealths)) / (n * np.sum(sorted_wealths))

def calculate_moving_average(history, window=10):
    """Simple moving average helper."""
    if len(history) < window:
        return np.mean(history)
    return np.mean(history[-window:])
