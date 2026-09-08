"""Virtual Electrophysiology Lab — Panel app.

Modernized, English-language rebuild of a 2019 Google Colab / Bokeh notebook
(current Bokeh/Panel APIs, no deprecated `bokeh.models.widgets` imports, no
Colab `#@param` cells). Run locally with:

    panel serve app.py --show

or open it directly in a Jupyter notebook with `pn.extension()` already called.

For a zero-install version of the same three modules, see the live demo
linked in the README.
"""

import numpy as np
import panel as pn
from bokeh.models import HoverTool
from bokeh.plotting import figure

from electrophys_lab.filters import apply_filter, composite_signal
from electrophys_lab.membrane_rc import rc_trace, time_constant_us
from electrophys_lab.nernst import nernst_potential_mv

pn.extension(sizing_mode="stretch_width")

ACCENT = "#B45309"
IONS = {
    "Na+": {"valence": 1, "out": 150, "in": 15, "color": "#3987e5"},
    "K+": {"valence": 1, "out": 5, "in": 100, "color": "#d95926"},
    "Cl-": {"valence": -1, "out": 150, "in": 13, "color": "#199e70"},
}


# ---------------------------------------------------------------- Module 1 --
def build_nernst_module() -> pn.Column:
    ion_select = pn.widgets.RadioButtonGroup(
        name="Ion species", options=list(IONS), button_type="primary"
    )
    out_slider = pn.widgets.IntSlider(name="External concentration (mM)", start=1, end=200, value=150)
    in_slider = pn.widgets.IntSlider(name="Internal concentration (mM)", start=1, end=200, value=15)

    def _sync_defaults(event):
        d = IONS[event.new]
        out_slider.value, in_slider.value = d["out"], d["in"]

    ion_select.param.watch(_sync_defaults, "value")

    def plot(ion, c_out, c_in):
        names, values, colors = [], [], []
        for name, d in IONS.items():
            live = name == ion
            v = nernst_potential_mv(c_out if live else d["out"], c_in if live else d["in"], d["valence"])
            names.append(name)
            values.append(v)
            colors.append(ACCENT if live else d["color"])
        p = figure(
            height=320, width=520, title="Equilibrium potential (mV)",
            y_range=names, tools="hover,save", tooltips=[("Vm", "@right{0.1f} mV")],
        )
        p.hbar(y=names, right=values, height=0.5, fill_color=colors, line_color=None)
        p.line([0, 0], [-0.5, len(names) - 0.5], line_color="gray", line_dash="dashed")
        p.xaxis.axis_label = "mV"
        return p

    def readout(ion, c_out, c_in):
        vm = nernst_potential_mv(c_out, c_in, IONS[ion]["valence"])
        return f"### Equilibrium potential: **{vm:+.1f} mV**"

    return pn.Column(
        "## Module 1 — Equilibrium potential",
        "Vm = (RT / zF) * ln([ion]out / [ion]in)",
        ion_select, out_slider, in_slider,
        pn.bind(readout, ion_select, out_slider, in_slider),
        pn.bind(plot, ion_select, out_slider, in_slider),
    )


# ---------------------------------------------------------------- Module 2 --
CELL_PRESETS = {
    "Large cell": {"r_mohm": 25, "c_pf": 0.0314},
    "Small cell": {"r_mohm": 6370, "c_pf": 0.000314},
}


def build_rc_module() -> pn.Column:
    preset = pn.widgets.RadioButtonGroup(name="Preset", options=list(CELL_PRESETS) + ["Custom"], button_type="primary")
    r_slider = pn.widgets.FloatSlider(name="Membrane resistance R (MOhm, log scale)", start=0, end=4, step=0.01, value=1.4)
    c_slider = pn.widgets.FloatSlider(name="Membrane capacitance C (pF, log scale)", start=-5, end=0, step=0.01, value=-1.5)

    def _sync_defaults(event):
        if event.new == "Custom":
            return
        d = CELL_PRESETS[event.new]
        r_slider.value = np.log10(d["r_mohm"])
        c_slider.value = np.log10(d["c_pf"])

    preset.param.watch(_sync_defaults, "value")
    preset.value = "Large cell"

    def plot(_preset, r_exp, c_exp):
        r, c = 10**r_exp, 10**c_exp
        p = figure(height=320, width=560, title="Membrane charge / discharge", tools="hover,save",
                   tooltips=[("t", "@x{0.00} us"), ("V", "@y{0.0} mV")])
        for label, d, color in [
            ("Large cell (reference)", CELL_PRESETS["Large cell"], "#3987e5"),
            ("Small cell (reference)", CELL_PRESETS["Small cell"], "#d95926"),
        ]:
            trace = rc_trace(d["r_mohm"], d["c_pf"])
            p.line(trace["t"], trace["v"], legend_label=label, color=color, line_width=2, alpha=0.7)
        trace = rc_trace(r, c)
        p.line(trace["t"], trace["v"], legend_label="Your cell", color=ACCENT, line_width=3)
        p.xaxis.axis_label, p.yaxis.axis_label = "Time (us)", "Potential (mV)"
        p.legend.location, p.legend.click_policy = "top_right", "hide"
        return p

    def readout(_preset, r_exp, c_exp):
        tau = time_constant_us(10**r_exp, 10**c_exp)
        unit = "us" if tau < 1000 else "ms"
        val = tau if tau < 1000 else tau / 1000
        return f"### Time constant tau: **{val:.3g} {unit}**"

    return pn.Column(
        "## Module 2 — Passive membrane properties",
        "tau = R * C",
        preset, r_slider, c_slider,
        pn.bind(readout, preset, r_slider, c_slider),
        pn.bind(plot, preset, r_slider, c_slider),
    )


# ---------------------------------------------------------------- Module 3 --
def build_filter_module() -> pn.Column:
    data = composite_signal()
    filter_type = pn.widgets.RadioButtonGroup(name="Filter type", options=["none", "low", "high"], button_type="primary")
    cutoff = pn.widgets.IntSlider(name="Cutoff frequency (Hz)", start=1, end=200, value=14)

    def plot_signals():
        p = figure(height=260, width=820, title="Signal components", tools="pan,wheel_zoom,box_zoom,reset,save")
        p.line(data["t"], data["sig1"], legend_label="Signal 1 (5 Hz)", color="#3987e5", alpha=0.7)
        p.line(data["t"], data["sig2"], legend_label="Signal 2 (10 Hz)", color="#d95926", alpha=0.7)
        p.line(data["t"], data["sig3"], legend_label="Signal 3 (100 Hz)", color="#199e70", alpha=0.7)
        p.line(data["t"], data["composite"], legend_label="Composite", color="#c98500", line_width=2)
        p.legend.click_policy = "hide"
        p.xaxis.axis_label, p.yaxis.axis_label = "Time (s)", "Amplitude (mV)"
        return p

    def plot_filtered(btype, cutoff_hz):
        filtered = apply_filter(data["composite"], fs=500, cutoff_hz=cutoff_hz, btype=btype)
        p = figure(height=300, width=820, title="Filtered vs. composite", tools="pan,wheel_zoom,box_zoom,reset,save")
        p.line(data["t"], data["composite"], legend_label="Composite", color="#c98500", alpha=0.4)
        p.line(data["t"], filtered, legend_label="Filtered", color="#3987e5", line_width=2)
        p.legend.click_policy = "hide"
        p.xaxis.axis_label, p.yaxis.axis_label = "Time (s)", "Amplitude (mV)"
        return p

    return pn.Column(
        "## Module 3 — Electronic filters",
        "6th-order Butterworth, zero-phase (scipy.signal.butter + filtfilt)",
        plot_signals(),
        filter_type, cutoff,
        pn.bind(plot_filtered, filter_type, cutoff),
    )


def create_app() -> pn.Column:
    return pn.Column(
        "# Virtual Electrophysiology Lab",
        "Interactive study guide for membrane biophysics. Python/Panel rebuild of a 2019 "
        "teaching notebook — see the zero-install web version linked in the README for the "
        "same three modules with no environment to set up.",
        build_nernst_module(),
        build_rc_module(),
        build_filter_module(),
    )


app = create_app()
app.servable(title="Virtual Electrophysiology Lab")

if __name__ == "__main__":
    pn.serve(app, show=True, title="Virtual Electrophysiology Lab")
