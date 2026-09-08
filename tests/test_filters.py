import numpy as np
import pytest

from electrophys_lab.filters import apply_filter, composite_signal


def test_composite_signal_is_sum_of_components():
    data = composite_signal()
    np.testing.assert_allclose(
        data["composite"], data["sig1"] + data["sig2"] + data["sig3"]
    )


def test_none_filter_is_a_passthrough():
    data = composite_signal()
    out = apply_filter(data["composite"], fs=500, cutoff_hz=14, btype="none")
    assert out is data["composite"]


def test_invalid_btype_raises():
    with pytest.raises(ValueError):
        apply_filter(np.zeros(10), fs=500, cutoff_hz=14, btype="bandpass")


def test_lowpass_removes_the_100hz_component():
    data = composite_signal()
    filtered = apply_filter(data["composite"], fs=500, cutoff_hz=40, btype="low")
    # A signal made only of the two low-frequency components has much lower
    # amplitude variance contributed by fast wiggles than the raw composite.
    residual = data["composite"] - filtered
    assert np.std(residual) > np.std(data["sig3"]) * 0.5  # most of sig3 removed from `filtered`
    assert np.std(filtered - (data["sig1"] + data["sig2"])) < np.std(data["sig3"])


def test_highpass_removes_the_low_frequency_components():
    data = composite_signal()
    filtered = apply_filter(data["composite"], fs=500, cutoff_hz=40, btype="high")
    # What's left should look much more like sig3 alone than like sig1+sig2.
    assert np.std(filtered - data["sig3"]) < np.std(filtered - (data["sig1"] + data["sig2"]))
