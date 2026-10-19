"""
Minimal plotting wrapper on top of plot_style (imported here, so the style is applied).

Each figure holds a single plot. By default figures are half the text width of an A4 page (minus a
small gap), so two of them fit side by side when included at natural size, e.g.

    \\includegraphics{a.pdf}\\hfill\\includegraphics{b.pdf}

Text is 10pt here (instead of plot_style's 12pt), which reads better at half width while staying
close to the size of the body text.

Every plot function draws into `ax` if given, otherwise creates a new figure of the requested
`size`, and returns (fig, ax). Call several times with the same `ax` to overlay series, then
optionally add a panel below showing each series' deviation from a reference:

    fig, ax = line(x, y_true, label="Truth")
    line(x, y_pred, fmt="--", label="Prediction", ax=ax, ylabel="$y$")
    deviation(ax, ref="Truth", kind="diff", xlabel="$x$", save="Plots/pred.pdf")

`size` is "full", "half" or "third" of the text width, a float fraction of the text width, or an
explicit (width, height) in inches. `aspect` is width / height of the whole figure.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.container import ErrorbarContainer
from matplotlib.patches import StepPatch

import plot_style

FONT_SIZE = 10
mpl.rcParams.update({key: FONT_SIZE for key in plot_style.STYLE if key.endswith("size") and key != "figure.figsize"})

GAP = 0.04  # fraction of the text width left between figures placed side by side
SIZES = {"full": 1.0, "half": (1 - GAP) / 2, "third": (1 - 2 * GAP) / 3}
ASPECT = 4 / 3  # default width / height for line, scatter and histogram figures
HEATMAP_ASPECT = 1.4  # fits a square heat map with its colorbar and labels, without spare height


def fig_size(size="half", aspect=ASPECT):
    """(width, height) in inches for a named size, a fraction of the text width, or a tuple."""
    if isinstance(size, (tuple, list)):
        return tuple(size)
    width = plot_style.FIG_WIDTH * (SIZES[size] if isinstance(size, str) else size)
    return (width, width / aspect)


def figure(size="half", aspect=ASPECT):
    """A single-axes figure sized for the page, with constrained layout."""
    return plt.subplots(figsize=fig_size(size, aspect), layout="constrained")


def _get_ax(ax, size, aspect):
    if ax is None:
        return figure(size, aspect)
    return ax.figure, ax


def _colorbar(fig, mappable, ax, label):
    # Attached to the drawn box of ax (not its layout slot), so it matches the height of a square heat map
    cbar = fig.colorbar(mappable, cax=ax.inset_axes([1.04, 0, 0.05, 1]), label=label)
    cbar.ax.tick_params(which="both", direction="out")
    # Matplotlib rasterizes the color strip in vector output, snapped to a coarse pixel grid, so it sits
    # slightly off the frame. Keep it vector; edges in the face color avoid seams between the steps
    cbar.solids.set_rasterized(False)
    cbar.solids.set_edgecolor("face")
    return cbar


def finish(fig, ax, xlabel=None, ylabel=None, title=None, xscale=None, yscale=None,
           xlim=None, ylim=None, legend=None, save=None):
    """Apply labels, scales, limits and legend to ax; save the figure if `save` is a path."""
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title)
    if xscale is not None:
        ax.set_xscale(xscale)
    if yscale is not None:
        ax.set_yscale(yscale)
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    # legend=None: show it only if some artist has a label
    if legend or (legend is None and ax.get_legend_handles_labels()[1]):
        ax.legend()
    if save is not None:
        fig.savefig(save, pad_inches=0.02)  # constrained layout already pads; keeps the saved size ~figsize
    return fig, ax


def line(x, y, fmt="-", yerr=None, label=None, ax=None, size="half", aspect=ASPECT,
         plot_kw=None, **finish_kw):
    """Line plot of y against x, with error bars if yerr is given."""
    fig, ax = _get_ax(ax, size, aspect)
    plot_kw = plot_kw or {}
    if yerr is None:
        ax.plot(x, y, fmt, label=label, **plot_kw)
    else:
        ax.errorbar(x, y, yerr=yerr, fmt=fmt, label=label, capsize=2, **plot_kw)
    return finish(fig, ax, **finish_kw)


def scatter(x, y, c=None, s=8, label=None, cbar_label=None, ax=None, size="half", aspect=ASPECT,
            plot_kw=None, **finish_kw):
    """Scatter plot; if c is an array the points are colored by it and a colorbar is added."""
    fig, ax = _get_ax(ax, size, aspect)
    sc = ax.scatter(x, y, c=c, s=s, label=label, **(plot_kw or {}))
    if c is not None and np.ndim(c) > 0 and not isinstance(c, str):
        _colorbar(fig, sc, ax, cbar_label)
    return finish(fig, ax, **finish_kw)


def hist(data, bins=50, label=None, density=False, fill=False, ax=None, size="half", aspect=ASPECT,
         plot_kw=None, **finish_kw):
    """
    Step histogram of data: an array, or a list of arrays with a list of labels. With an integer
    `bins`, several datasets share the same bin edges.
    """
    fig, ax = _get_ax(ax, size, aspect)
    datasets = [data] if np.ndim(data[0]) == 0 else data
    labels = [label] if len(datasets) == 1 and not isinstance(label, (list, tuple)) else (label or [None] * len(datasets))
    edges = np.histogram_bin_edges(np.concatenate([np.ravel(d) for d in datasets]), bins)
    for d, lab in zip(datasets, labels):
        counts, _ = np.histogram(d, edges, density=density)
        ax.stairs(counts, edges, label=lab, fill=fill, **(plot_kw or {}))
    return finish(fig, ax, **finish_kw)


def heatmap(z, x=None, y=None, cmap="viridis", cbar_label=None, vmin=None, vmax=None, log=False,
            square=True, ax=None, size="half", aspect=HEATMAP_ASPECT, plot_kw=None, **finish_kw):
    """
    Heat map of the 2D array z (rows along y, columns along x). x and y are the bin centers or
    edges of the columns and rows; if omitted, the cells are indexed by integers. With square=True
    the plotting area is square, whatever the axis ranges.
    """
    fig, ax = _get_ax(ax, size, aspect)
    z = np.asarray(z)
    x = np.arange(z.shape[1]) if x is None else x
    y = np.arange(z.shape[0]) if y is None else y
    norm = mpl.colors.LogNorm(vmin, vmax) if log else mpl.colors.Normalize(vmin, vmax)
    mesh = ax.pcolormesh(x, y, z, cmap=cmap, norm=norm, shading="auto", **(plot_kw or {}))
    _colorbar(fig, mesh, ax, cbar_label)
    if square:
        ax.set_box_aspect(1)
    return finish(fig, ax, **finish_kw)


def _series(ax):
    """(label, x, y, style) of the labeled lines, error-bar series and histograms on ax."""
    series = []
    errorbar_lines = set()
    for c in ax.containers:
        if isinstance(c, ErrorbarContainer):
            ln = c.lines[0]
            errorbar_lines.add(ln)
            series.append((c.get_label(), *ln.get_data(), _line_style(ln)))
    for ln in ax.get_lines():
        if ln not in errorbar_lines and not ln.get_label().startswith("_"):
            series.append((ln.get_label(), *ln.get_data(), _line_style(ln)))
    for patch in ax.patches:
        if isinstance(patch, StepPatch):
            values, edges, _ = patch.get_data()
            style = {"color": patch.get_edgecolor(), "linestyle": patch.get_linestyle()}
            series.append((patch.get_label(), edges, values, ("stairs", style)))
    return series


def _line_style(ln):
    return ("line", {"color": ln.get_color(), "linestyle": ln.get_linestyle(),
                     "marker": ln.get_marker(), "markersize": ln.get_markersize()})


def deviation(ax, ref=0, kind="ratio", height=0.35, gap=0.05, ylabel=None, ylim=None, xlabel=None, save=None):
    """
    Add a panel below ax showing how each series on ax deviates from the reference series `ref`
    (its label, or its index in the order the series were drawn). kind is "ratio" (y / ref),
    "diff" (y - ref) or "rel" ((y - ref) / ref). The panel shares the x axis with ax; the figure
    grows to fit it, so ax keeps its size. `height` and `gap` (the separation between ax and the
    panel) are fractions of the height of ax.

    Works on lines, error-bar series and histograms drawn with this module. Series with different
    x values from the reference are compared on the reference's x by linear interpolation.
    Returns (fig, panel_ax).
    """
    fig = ax.figure
    series = _series(ax)
    labels = [s[0] for s in series]
    ref_label, ref_x, ref_y, (_, ref_style) = series[labels.index(ref) if isinstance(ref, str) else ref]
    ref_y = np.asarray(ref_y, float)

    # The panel is attached under the drawn box of ax; the figure grows to fit it, so ax keeps its size
    w, h = fig.get_size_inches()
    fig.set_size_inches(w, h * (1 + height + gap))
    panel = ax.inset_axes([0, -height - gap, 1, height], sharex=ax)
    ax.tick_params(labelbottom=False)
    panel.set_xlabel(xlabel if xlabel is not None else ax.get_xlabel())
    ax.set_xlabel("")

    with np.errstate(divide="ignore", invalid="ignore"):
        compare = {"ratio": lambda y: y / ref_y, "diff": lambda y: y - ref_y,
                   "rel": lambda y: (y - ref_y) / ref_y}[kind]
        for label, x, y, (series_kind, style) in series:
            y = np.asarray(y, float)
            if label == ref_label:
                continue
            if series_kind == "stairs":
                if len(x) != len(ref_x) or not np.allclose(x, ref_x):
                    raise ValueError(f"Histogram '{label}' does not have the same bins as the reference '{ref_label}'")
                d = compare(y)
                panel.stairs(np.where(np.isfinite(d), d, np.nan), x, baseline=None, **style)  # empty reference bins: gaps
            else:
                if len(x) != len(ref_x) or not np.allclose(x, ref_x):
                    y = np.interp(ref_x, x, y)
                panel.plot(ref_x, compare(y), **style)
    panel.axhline(1 if kind == "ratio" else 0, color=ref_style["color"], linestyle=ref_style["linestyle"], linewidth=0.8)

    default_ylabel = {"ratio": "Ratio", "diff": "Diff.", "rel": "Rel. dev."}[kind]  # short: the panel is low
    panel.set_ylabel(ylabel if ylabel is not None else default_ylabel)
    panel.yaxis.set_major_locator(mpl.ticker.MaxNLocator(nbins=4, prune="upper"))  # top label would clash with ax
    if ylim is not None:
        panel.set_ylim(ylim)
    _align_ylabels(fig, [ax, panel])
    if save is not None:
        fig.savefig(save, pad_inches=0.02)
    return fig, panel


def _align_ylabels(fig, axes):
    """Put the y labels of vertically stacked axes of equal width at the same horizontal position."""
    fig.canvas.draw()
    x = min(a.transAxes.inverted().transform(a.yaxis.label.get_window_extent())[0, 0] for a in axes)
    for a in axes:
        a.yaxis.set_label_coords(x, 0.5)
