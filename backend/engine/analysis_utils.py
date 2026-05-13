import numpy as np

def norm(arr):
    arr = np.array(arr)
    return (arr / (np.max(arr) + 1e-6)).tolist()

def smooth(arr, window_size=5):
    window = np.ones(window_size) / window_size
    return np.convolve(arr, window, mode='same').tolist()
