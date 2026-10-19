"""
Usage illustration for plotting.py, on toy data. Run from this directory:

    python plotting_example.py

Figures are written to Plots/examples/.
"""
import os

import numpy as np

import plotting as p

OUT = os.path.join("Plots", "examples")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(0)

# Line plot: overlay two series by passing the axes back in. Labels, scales and saving go on the last call
epochs = np.arange(1, 51)
fig, ax = p.line(epochs, np.exp(-epochs / 15) + 0.01, label="Lipschitz")
p.line(epochs, np.exp(-epochs / 8) + 0.002, fmt="--", label="Unconstrained", ax=ax,
       xlabel="Epoch", ylabel=r"$\mathcal{L}_\mathrm{MSE}$", yscale="log",
       save=os.path.join(OUT, "line.pdf"))

# Line plot with error bars, e.g. mean and std over seeds
widths = 2 ** np.arange(2, 9)
mse = rng.normal(1 / widths, 0.2 / widths, size=(5, len(widths)))  # (seeds, widths)
p.line(widths, mse.mean(axis=0), yerr=mse.std(axis=0), fmt="o-",
       xlabel="Width", ylabel="MSE", xscale="log", yscale="log",
       save=os.path.join(OUT, "errorbar.pdf"))

# Deviation panel: draw the lines as usual (without saving), then add a panel comparing them to a
# reference series. The figure grows to fit the panel, so the main plot keeps its size
x = np.linspace(-3, 3, 200)
fig, ax = p.line(x, np.tanh(x), label="Target")
p.line(x, np.tanh(x) + 0.05 * np.sin(4 * x), fmt="--", label="Lipschitz", ax=ax)
p.line(x, np.tanh(1.1 * x), fmt=":", label="Unconstrained", ax=ax, xlabel=r"$x$", ylabel=r"$f(x)$")
p.deviation(ax, ref="Target", kind="diff", save=os.path.join(OUT, "deviation_line.pdf"))

# Histogram: several datasets at once, with one label each (they share bin edges)
errors = [rng.normal(0, 1, 5000), rng.standard_t(3, 5000)]
p.hist(errors, bins=np.linspace(-6, 6, 61), label=["Lipschitz", "Unconstrained"], density=True,
       xlabel=r"$\Delta$", ylabel="Density", ylim=(0, 0.6),  # headroom for the legend
       save=os.path.join(OUT, "hist.pdf"))

# Deviation panel under histograms: ratio of each histogram to the reference, bin by bin
fig, ax = p.hist(errors, bins=np.linspace(-3, 3, 31), label=["Lipschitz", "Unconstrained"],
                 xlabel=r"$\Delta$", ylabel="Counts", ylim=(0, 650))
p.deviation(ax, ref="Lipschitz", kind="ratio", ylim=(0, 2), save=os.path.join(OUT, "deviation_hist.pdf"))

# Scatter plot colored by a third quantity (adds a colorbar)
y_true = rng.uniform(-1, 1, 400)
y_pred = y_true + rng.normal(0, 0.1, 400)
p.scatter(y_true, y_pred, c=np.abs(y_pred - y_true), cbar_label=r"$|\Delta|$",
          xlabel=r"$y_\mathrm{true}$", ylabel=r"$y_\mathrm{pred}$",
          save=os.path.join(OUT, "scatter.pdf"))

# Heat map over a (depth, width) grid with a log color scale. The plotting area is square by default
depths = np.arange(1, 7)
scan = (1 / widths[None, :] + 0.05 * depths[:, None]) * rng.uniform(0.8, 1.2, (len(depths), len(widths)))
p.heatmap(scan, x=widths, y=depths, log=True, cbar_label="MSE",
          xlabel="Width", ylabel="Depth", xscale="log",
          save=os.path.join(OUT, "heatmap.pdf"))

# Other sizes: full text width with a wider aspect ratio, or an explicit (width, height) in inches
p.line(x, np.tanh(x), size="full", aspect=3, xlabel=r"$x$", ylabel=r"$\tanh(x)$",
       save=os.path.join(OUT, "full_width.pdf"))

print(f"Saved example figures to {OUT}/")
