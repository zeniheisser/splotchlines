"""
Common style for all plots in this repository. Importing this module applies it.

- All text is typeset with LaTeX (Computer Modern serif)
-- All text has the same size, 10pt. The figures are as wide as the text of an A4 page with 2.5 cm
  margins (16 cm), so the text is 12pt when the figure is included at its natural size
  (e.g. \\includegraphics[width=16cm]{...} or \\includegraphics{...})
- Tick marks point into the plot
- No gridlines, no legend frames
"""
import matplotlib as mpl

FONT_SIZE = 10
FIG_WIDTH = 16 / 2.54  # [in] text width of an A4 page with 2.5 cm margins
FIG_HEIGHT = FIG_WIDTH / 1.618  # golden ratio
FIG_SIZE = (FIG_WIDTH, FIG_HEIGHT)

STYLE = {
    # LaTeX text
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Computer Modern Roman"],
    "text.latex.preamble": r"\usepackage[T1]{fontenc}\usepackage{amsmath}",
    # Identical text sizes everywhere
    "font.size": FONT_SIZE,
    "axes.titlesize": FONT_SIZE,
    "axes.labelsize": FONT_SIZE,
    "xtick.labelsize": FONT_SIZE,
    "ytick.labelsize": FONT_SIZE,
    "legend.fontsize": FONT_SIZE,
    "legend.title_fontsize": FONT_SIZE,
    "figure.titlesize": FONT_SIZE,
    # Tick marks inside the plot
    "xtick.direction": "in",
    "ytick.direction": "in",
    # No gridlines, no legend frames
    "axes.grid": False,
    "legend.frameon": False,
    # Figure size matching the A4 text width
    "figure.figsize": FIG_SIZE,
    "savefig.bbox": "tight",
}


def apply():
    mpl.rcParams.update(STYLE)


apply()
