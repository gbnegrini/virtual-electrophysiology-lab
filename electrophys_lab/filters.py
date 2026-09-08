"""Composite test signal and Butterworth filtering."""

import numpy as np
from scipy.signal import butter, filtfilt

FILTER_ORDER = 6


def composite_signal(fs: int = 500, duration_s: float = 1.0) -> dict:
    """Three sine components (5 Hz, 10 Hz, 100 Hz) summed into one recording.

    Matches the original notebook's exercise: signal 3 (100 Hz) stands in for
    high-frequency noise riding on top of the 5-10 Hz signal of interest.
    """
    n = int(duration_s * fs)
    t = np.linspace(0, duration_s, n, endpoint=False)
    sig1 = 50 * np.sin(2 * np.pi * 5 * t)
    sig2 = 50 * np.sin(2 * np.pi * 10 * t)
    sig3 = 25 * np.sin(2 * np.pi * 100 * t)
    return {"t": t, "sig1": sig1, "sig2": sig2, "sig3": sig3, "composite": sig1 + sig2 + sig3}


def apply_filter(signal: np.ndarray, fs: int, cutoff_hz: float, btype: str) -> np.ndarray:
    """Zero-phase Butterworth filter (order 6), matching the original notebook.

    btype: "none", "low", or "high".
    """
    if btype == "none":
        return signal
    if btype not in ("low", "high"):
        raise ValueError(f"btype must be 'none', 'low', or 'high', got {btype!r}")
    wn = cutoff_hz / (0.5 * fs)
    b, a = butter(FILTER_ORDER, wn, btype=btype)
    return filtfilt(b, a, signal)
