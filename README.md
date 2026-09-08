# Virtual Electrophysiology Lab

> An interactive study guide for membrane biophysics — equilibrium potentials, passive membrane
> properties, and signal filtering.

**[Live demo (zero install, runs in the browser)](https://biomedicaldata.science/demos/electrophysiology-lab/)**

This is a modernized, English-language rebuild of a 2019 Google Colab notebook built for an
Electrophysiology of the Central Nervous System course. The original used Colab `#@param` form
fields and a since-deprecated Bokeh widget API; this version is a tested Python package plus a
[Panel](https://panel.holoviz.org/) app, with a companion zero-install web version (linked above)
for anyone who just wants to try it without setting up a Python environment.

## Modules

1. **Equilibrium potential** — the Nernst potential of an ion species as a function of its
   valence and the concentration ratio across the membrane.
2. **Passive membrane properties** — the RC time constant of the neuronal membrane, comparing
   charge/discharge curves for cells of different size.
3. **Electronic filters** — separating a signal of interest from high-frequency noise using a
   6th-order zero-phase Butterworth filter.

## Project structure

```
electrophys_lab/    # the physics: pure, tested functions (no plotting, no widgets)
  nernst.py          Nernst equilibrium potential
  membrane_rc.py      RC charge/discharge curves and time constant
  filters.py          composite test signal + Butterworth filtering (scipy)
app.py               Panel app: binds the functions above to interactive widgets/plots
web/index.html       zero-install browser version (vanilla JS + SVG, no build step) —
                     the source of the live demo linked above
tests/               pytest suite for electrophys_lab/, validated against the
                     original notebook's textbook reference values
original/            the unmodified 2019 Colab export, kept for provenance
```

The physics is factored out from the UI on purpose — `electrophys_lab/` has no Bokeh or Panel
import at all, so it's trivially testable and reusable (it's also what the browser demo's
JavaScript port was validated against: the Butterworth filter there matches
`scipy.signal.butter` + `filtfilt` to <1e-8 absolute error).

## Running it

```bash
git clone https://github.com/gbnegrini/virtual-electrophysiology-lab.git
cd virtual-electrophysiology-lab
pip install -r requirements.txt

panel serve app.py --show
```

Or open `app.py`'s functions directly in a Jupyter notebook (`import panel as pn; pn.extension()`
first).

The browser version needs no install at all — `web/index.html` is fully self-contained (only an
external Google Fonts stylesheet, everything else inline), so opening it directly in a browser
works.

## Testing

```bash
pip install -r requirements.txt
pip install -e .
pytest tests/ -v
```

CI runs the test suite on Python 3.10 and 3.12 on every push (see
`.github/workflows/tests.yml`).

## Credits

Original notebook and course materials by Guilherme Bauer-Negrini, 2019 (Electrophysiology of
the Central Nervous System). Code is MIT licensed; the instructional text/content is
CC BY-NC 4.0.
