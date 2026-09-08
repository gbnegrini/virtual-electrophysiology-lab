"""Passive (RC) membrane properties: charge/discharge curves and time constant."""

import math

import numpy as np

RESTING_POTENTIAL_MV = -60.0
STEP_AMPLITUDE_MV = 80.0


def time_constant_us(r_mohm: float, c_pf: float) -> float:
    """Membrane time constant tau = R*C, in microseconds.

    MOhm * pF = 1e6 ohm * 1e-12 F = 1e-6 s, i.e. R[MOhm] * C[pF] gives tau
    directly in microseconds.
    """
    return r_mohm * c_pf


def charge_mv(t_us: float, r_mohm: float, c_pf: float, v0_mv: float = STEP_AMPLITUDE_MV) -> float:
    """Membrane potential (mV, above resting) while charging toward v0_mv."""
    tau = time_constant_us(r_mohm, c_pf)
    return v0_mv * (1 - math.exp(-t_us / tau))


def discharge_mv(t_us: float, r_mohm: float, c_pf: float, v0_mv: float = STEP_AMPLITUDE_MV) -> float:
    """Membrane potential (mV, above resting) while discharging from near-steady-state."""
    tau = time_constant_us(r_mohm, c_pf)
    v_start = charge_mv(5 * tau, r_mohm, c_pf, v0_mv)
    return v_start * math.exp(-t_us / tau)


def rc_trace(r_mohm: float, c_pf: float, n: int = 220) -> dict:
    """Charge (0..5*tau) then discharge (5*tau..10*tau) trace, offset to resting potential.

    Returns a dict with numpy arrays 't' (microseconds) and 'v' (millivolts), and
    the scalar 'tau' (microseconds), matching the shape plotted in the original notebook.
    """
    tau = time_constant_us(r_mohm, c_pf)
    t_up = np.linspace(0, 5 * tau, n)
    t_down = 5 * tau + np.linspace(0, 5 * tau, n)
    v_up = np.array([charge_mv(t, r_mohm, c_pf) for t in t_up]) + RESTING_POTENTIAL_MV
    v_down = np.array([discharge_mv(t - 5 * tau, r_mohm, c_pf) for t in t_down]) + RESTING_POTENTIAL_MV
    return {
        "t": np.concatenate([t_up, t_down]),
        "v": np.concatenate([v_up, v_down]),
        "tau": tau,
    }
