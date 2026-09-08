"""Nernst equilibrium potential."""

import math

R_GAS = 8.314        # J / (mol K)
F_FARADAY = 96485.0  # C / mol


def nernst_potential_mv(
    c_out: float, c_in: float, valence: int, t_kelvin: float = 310
) -> float:
    """Equilibrium (Nernst) potential of an ion, in millivolts.

    Vm = (R*T) / (z*F) * ln(c_out / c_in)

    Parameters
    ----------
    c_out, c_in : extracellular / intracellular ion concentration (any consistent
        unit, e.g. mM - only the ratio matters).
    valence : the ion's charge, e.g. +1 for Na+/K+, -1 for Cl-.
    t_kelvin : temperature, default 310 K (37 C), matching the original notebook.
    """
    return (R_GAS * t_kelvin) / (valence * F_FARADAY) * math.log(c_out / c_in) * 1000
