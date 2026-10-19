# splotchlines

My standard matplotlib plotting settings and helper functions.

## Install

```bash
pip install -r requirements.txt
```

Text is rendered with LaTeX (`text.usetex`), so you also need a LaTeX
installation (e.g. TeX Live) with the `cm-super` and `dvipng` packages.

## Usage

Run the examples:

```bash
python example.py
```

The figures are written to `Plots/examples/`, relative to the directory you
run the script from.

- `plot_style.py`: the rcParams (fonts, sizes, LaTeX preamble).
- `plotting.py`: plotting helpers (`line`, `scatter`, `hist`, `heatmap`, `deviation`, ...).
- `example.py`: one example per plot type. Start here.
