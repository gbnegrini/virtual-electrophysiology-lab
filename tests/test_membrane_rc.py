import pytest

from electrophys_lab.membrane_rc import (
    RESTING_POTENTIAL_MV,
    STEP_AMPLITUDE_MV,
    charge_mv,
    discharge_mv,
    rc_trace,
    time_constant_us,
)

# The two reference cells from the original notebook.
LARGE_CELL = {"r_mohm": 25, "c_pf": 3.14e-14 * 1e12, "expected_tau_us": 0.785}
SMALL_CELL = {"r_mohm": 637 * 10, "c_pf": 3.14e-16 * 1e12, "expected_tau_us": 2.0}


@pytest.mark.parametrize("cell", [LARGE_CELL, SMALL_CELL])
def test_time_constant_matches_notebook(cell):
    tau = time_constant_us(cell["r_mohm"], cell["c_pf"])
    assert tau == pytest.approx(cell["expected_tau_us"], rel=0.01)


def test_charge_starts_at_zero_and_approaches_v0():
    tau = time_constant_us(25, 0.0314)
    assert charge_mv(0, 25, 0.0314) == pytest.approx(0.0, abs=1e-9)
    assert charge_mv(5 * tau, 25, 0.0314) == pytest.approx(STEP_AMPLITUDE_MV, rel=0.01)


def test_discharge_decays_toward_zero():
    tau = time_constant_us(25, 0.0314)
    v_start = discharge_mv(0, 25, 0.0314)
    v_later = discharge_mv(5 * tau, 25, 0.0314)
    assert v_later < v_start
    assert v_later == pytest.approx(0.0, abs=v_start * 0.01)


def test_rc_trace_offsets_to_resting_potential():
    trace = rc_trace(25, 0.0314, n=50)
    assert trace["v"][0] == pytest.approx(RESTING_POTENTIAL_MV, abs=1e-6)
    assert len(trace["t"]) == len(trace["v"]) == 100
    assert trace["tau"] == pytest.approx(0.785, rel=0.01)
