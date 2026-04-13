import numpy as np

# Multiplies the waveform amplitude a certain factor
def volume_scale(y, scale_min=0.8, scale_max=1.2):
    scale = np.random.uniform(scale_min, scale_max)
    return y * scale

# Shifts
def time_shift(y, shift_limit=0.05):
    shift = int(np.random.uniform(-shift_limit, shift_limit) * len(y))
    return np.roll(y, shift)

# Adds noise
def add_noise(y, noise_min=0.001, noise_max=0.015):
    noise = np.random.uniform(noise_min, noise_max)
    noise_samples = np.random.randn(len(y))
    return y + noise * noise_samples