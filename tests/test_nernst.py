import pytest

from electrophys_lab.nernst import nernst_potential_mv

# Textbook concentrations for a human neuron and the resulting equilibrium
# potentials, as given in the original 2019 notebook.
PHYSIOLOGICAL_CASES = [
    ("Na+", 150, 15, 1, 61.5),
    ("K+", 5, 100, 1, -80.0),
    ("Cl-", 150, 13, -1, -65.3),
]


@pytest.mark.parametrize("name,c_out,c_in,valence,expected_mv", PHYSIOLOGICAL_CASES)
def test_matches_textbook_values(name, c_out, c_in, valence, expected_mv):
    assert nernst_potential_mv(c_out, c_in, valence) == pytest.approx(expected_mv, abs=0.1)


def test_equal_concentrations_give_zero_potential():
    assert nernst_potential_mv(50, 50, 1) == pytest.approx(0.0, abs=1e-9)


def test_flipping_valence_flips_sign():
    v_cation = nernst_potential_mv(100, 10, 1)
    v_anion = nernst_potential_mv(100, 10, -1)
    assert v_cation == pytest.approx(-v_anion)
