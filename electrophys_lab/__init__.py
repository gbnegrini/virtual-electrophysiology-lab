"""Virtual Electrophysiology Lab.

A small package of the physics functions behind the interactive lab: the Nernst
equilibrium potential, passive (RC) membrane properties, and Butterworth
signal filtering.
"""

from .nernst import nernst_potential_mv
from .membrane_rc import charge_mv, discharge_mv, rc_trace, time_constant_us
from .filters import apply_filter, composite_signal

__all__ = [
    "nernst_potential_mv",
    "charge_mv",
    "discharge_mv",
    "rc_trace",
    "time_constant_us",
    "apply_filter",
    "composite_signal",
]
