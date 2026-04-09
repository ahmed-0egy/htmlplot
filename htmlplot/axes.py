"""Axes — the chart surface for htmlplot.

Each Axes instance renders one card block of HTML.  Multiple Axes live
inside a Figure (one per row, or arranged in a grid).
"""

from __future__ import annotations

import html
import math
from typing import TYPE_CHECKING, Callable, Sequence

from .themes import get_color, get_text_color, resolve_colors, PALETTES, PALETTE_ALIASES
from ._utils import nice_ticks

if TYPE_CHECKING:
    from .figure import Figure

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_value(value: float, fmt: str | Callable | None, default: str = "{:g}") -> str:
    if fmt is None:
        return default.format(value)
    if callable(fmt):
        return fmt(value)
    return fmt.format(value)


def _escape(text: str) -> str:
    """HTML-escape but preserve <strong>…</strong> markers in infobox text."""
    safe = html.escape(str(text))
    safe = safe.replace("&lt;strong&gt;", "<strong>").replace("&lt;/strong&gt;", "</strong>")
    return safe


def _tip(label: str, *lines: str) -> str:
    """Build a ``data-tip`` attribute value.

    The returned string is already HTML-attribute-escaped so it can be
    dropped directly into  ``data-tip="..."``  in generated HTML.
    The JS engine reads it back via ``getAttribute`` and sets ``innerHTML``,
    so ``<b>`` / ``<br>`` inside are rendered as HTML in the tooltip.
    """
    parts = [f"<b>{html.escape(label)}</b>"]
    parts += [html.escape(str(l)) for l in lines if l != ""]
    inner = "<br>".join(parts)
    # Escape the whole thing for safe embedding in an HTML attribute
    return html.escape(inner, quote=True)


# ---------------------------------------------------------------------------
# Axes
# ---------------------------------------------------------------------------

class Axes:
    """A single card/chart panel inside a Figure.

    Methods mirror matplotlib's Axes API closely so that muscle memory
    transfers:  ``ax.barh()``, ``ax.bar()``, ``ax.hist()``, ``ax.set_title()``
    etc.  Instead of drawing pixels, each method stores data; ``.to_html()``
    converts everything to a self-contained HTML snippet.
    """

    def __init__(self, figure: "Figure") -> None:
        self._figure = figure
        self._title: str | None = None
        self._chart: dict | None = None        # one primary chart per Axes
        self._annotations: list[tuple[str, str]] = []   # (type, html_content)

    # ------------------------------------------------------------------
    # Title
    # ------------------------------------------------------------------

    def set_title(self, title: str) -> "Axes":
        self._title = title
        return self

    # ------------------------------------------------------------------
    # Primary charts
    # ------------------------------------------------------------------

    def barh(
        self,
        labels: Sequence[str],
        values: Sequence[float],
        *,
        title: str | None = None,
        fmt: str | Callable | None = None,
        palette: str | list[str] | None = "gyr",
        colors: list[str] | None = None,
        max_val: float | None = None,
        sort: bool = False,
        label_width: int = 150,
    ) -> "Axes":
        """Horizontal bar chart – mirrors ``matplotlib.Axes.barh``.

        Parameters
        ----------
        labels:
            Category labels (y-axis).
        values:
            Numeric values for each bar.
        title:
            Chart title (overrides ``set_title``).
        fmt:
            Value label format.  Either a format string (e.g. ``"{:.1f}%"``)
            or a callable ``(float) -> str``.
        palette:
            Named colour palette (``"gyr"``, ``"blues"``, …) **or** a list of
            explicit hex colours that will be cycled.
        colors:
            Explicit list of hex colours; overrides *palette*.
        max_val:
            Treat this as the 100 % reference for bar widths.
        sort:
            Sort bars ascending by value.
        label_width:
            CSS pixel width of the label column.
        """
        if title:
            self._title = title

        labels = list(labels)
        values = list(values)

        if sort:
            pairs = sorted(zip(values, labels))
            values, labels = zip(*pairs)
            values, labels = list(values), list(labels)

        _max = max_val if max_val is not None else max(values)
        _min = min(values)

        bar_colors = resolve_colors(values, palette=colors if colors else palette,
                                    vmin=_min, vmax=_max)

        bars = []
        for label, value, color in zip(labels, values, bar_colors):
            width_pct = (value / _max * 100) if _max else 0
            text_color = get_text_color(color)
            bars.append({
                "label": label,
                "value": value,
                "width_pct": width_pct,
                "color": color,
                "text_color": text_color,
                "value_label": _fmt_value(value, fmt),
            })

        self._chart = {"type": "barh", "bars": bars, "label_width": label_width}
        return self

    # ------------------------------------------------------------------

    def bar(
        self,
        labels: Sequence[str],
        values: Sequence[float],
        *,
        title: str | None = None,
        fmt: str | Callable | None = None,
        palette: str | list[str] | None = "blues",
        colors: list[str] | None = None,
        max_val: float | None = None,
        sort: bool = False,
        height: int = 200,
    ) -> "Axes":
        """Vertical bar chart – mirrors ``matplotlib.Axes.bar``.

        Parameters
        ----------
        height:
            Pixel height of the chart area (excluding x-axis labels).
        """
        if title:
            self._title = title

        labels = list(labels)
        values = list(values)

        if sort:
            pairs = sorted(zip(values, labels))
            values, labels = zip(*pairs)
            values, labels = list(values), list(labels)

        _max = max_val if max_val is not None else max(values)
        _min = min(values)

        bar_colors = resolve_colors(values, palette=colors if colors else palette,
                                    vmin=_min, vmax=_max)

        bars = []
        for label, value, color in zip(labels, values, bar_colors):
            bars.append({
                "label": label,
                "value": value,
                # Store the normalized fraction (0–1); pixel height is
                # computed at render-time from the current chart_height so
                # it rescales correctly when cell_height constrains the layout.
                "bar_height_frac": (value / _max) if _max else 0.0,
                "color": color,
                "value_label": _fmt_value(value, fmt),
            })

        self._chart = {"type": "bar", "bars": bars, "chart_height": height}
        return self

    # ------------------------------------------------------------------

    def hist(
        self,
        data: Sequence[float],
        bins: int | Sequence[float] = 10,
        *,
        title: str | None = None,
        fmt: str | Callable | None = None,
        palette: str | list[str] | None = "blues",
        colors: list[str] | None = None,
        height: int = 200,
        density: bool = False,
        cumulative: bool | int = False,
        data_range: tuple[float, float] | None = None,
        weights: Sequence[float] | None = None,
        orientation: str = "vertical",
    ) -> "Axes":
        """Histogram – mirrors ``matplotlib.Axes.hist``.

        Parameters
        ----------
        data:
            Raw numeric observations.
        bins:
            Number of equal-width bins, **or** an explicit list of bin edges.
        density:
            If True, normalise bars so their areas sum to 1 (probability
            density function — each bar's area represents the probability of
            falling in that bin).
        cumulative:
            If True, each bar shows the running total up to and including
            that bin.  Pass ``-1`` for the reverse (complementary CDF /
            survival-function) histogram.  When combined with *density*,
            the last bar reaches 1.0.
        data_range:
            ``(min, max)`` pair to restrict observations before binning.
            Mirrors matplotlib's ``range`` keyword.
        weights:
            Per-observation weights.  Bin heights become sums of weights
            instead of raw counts.
        orientation:
            ``"vertical"`` (default) – bars grow upward;
            ``"horizontal"`` – bins on the y-axis (delegates to
            :meth:`barh`).
        """
        if title:
            self._title = title

        data = [float(x) for x in data]
        _weights: list[float] = list(weights) if weights is not None else [1.0] * len(data)

        # Apply data_range filter
        if data_range is not None:
            lo_r, hi_r = data_range
            pairs = [(x, w) for x, w in zip(data, _weights) if lo_r <= x <= hi_r]
            if pairs:
                data, _weights = map(list, zip(*pairs))  # type: ignore[assignment]
            else:
                data, _weights = [], []

        if not data:
            return self

        _min_d, _max_d = min(data), max(data)

        # Build bin edges
        if isinstance(bins, int):
            n_bins = bins
            step = (_max_d - _min_d) / n_bins if _max_d != _min_d else 1.0
            edges = [_min_d + step * i for i in range(n_bins + 1)]
        else:
            edges = list(bins)
            n_bins = len(edges) - 1

        # Accumulate weighted counts
        counts: list[float] = [0.0] * n_bins
        for x, w in zip(data, _weights):
            placed = False
            for i in range(n_bins):
                if edges[i] <= x < edges[i + 1]:
                    counts[i] += w
                    placed = True
                    break
            if not placed and x == edges[-1]:
                counts[-1] += w

        # Density normalisation (area = 1)
        if density:
            total_w = sum(counts)
            bin_widths = [edges[i + 1] - edges[i] for i in range(n_bins)]
            counts = [c / (total_w * bw) if total_w and bw else 0.0
                      for c, bw in zip(counts, bin_widths)]

        # Cumulative transform
        if cumulative:
            running = 0.0
            cum_counts: list[float] = []
            for c in counts:
                running += c
                cum_counts.append(running)
            counts = cum_counts
            if cumulative == -1:          # complementary / survival
                peak = counts[-1] if counts else 1.0
                counts = [peak - c for c in counts]

        # Bin-midpoint labels
        labels = [f"{(edges[i] + edges[i + 1]) / 2:.3g}" for i in range(n_bins)]

        if orientation == "horizontal":
            self.barh(labels, counts, title=None, fmt=fmt,
                      palette=colors if colors else palette)
        else:
            self.bar(labels, counts, title=None, fmt=fmt,
                     palette=colors if colors else palette,
                     height=height)

        if self._chart:
            self._chart["subtype"] = "hist"
            self._chart["edges"] = edges
        return self

    # ------------------------------------------------------------------

    def lineplot(
        self,
        x_list: Sequence[Sequence[float]],
        y_list: Sequence[Sequence[float]],
        *,
        labels: Sequence[str] | None = None,
        colors: Sequence[str] | None = None,
        ci: Sequence[tuple[Sequence[float], Sequence[float]]] | None = None,
        title: str | None = None,
        xlabel: str = "",
        ylabel: str = "",
        step: bool = False,
        markers: bool = False,
        marker_size: int = 4,
        svg_height: int = 210,
    ) -> "Axes":
        """Multi-series line chart.

        Parameters
        ----------
        x_list:
            List of x arrays, one per series.
        y_list:
            Corresponding y arrays, one per series.
        labels:
            Legend labels (shown when more than one series, or always if supplied).
        colors:
            Hex colours per series.  Defaults cycle through a built-in palette.
        ci:
            Optional shaded confidence bands.  Each entry is ``(lower, upper)``
            — arrays of the same length as the corresponding *y_list* entry.
        step:
            If ``True``, draw a staircase / step line instead of straight
            segments (useful for survival curves, ECDFs, etc.).
        markers:
            If ``True``, overlay a circle at every data point.
        marker_size:
            Radius of the data-point circles in pixels.
        svg_height:
            Pixel height of the SVG chart area.

        Examples
        --------
        ::

            fig, ax = hp.subplots(title="Trend")
            ax.lineplot(
                [days, days],
                [series_a, series_b],
                labels=["Group A", "Group B"],
                colors=["#4a82c8", "#2ed090"],
                xlabel="Day",
                ylabel="Value",
            )
        """
        if title:
            self._title = title
        self._chart = self._build_svg_chart(
            "lineplot", x_list, y_list,
            labels=labels, colors=colors, ci=ci,
            xlabel=xlabel, ylabel=ylabel,
            step=step, markers=markers, marker_size=marker_size,
            svg_height=svg_height,
        )
        return self

    # ------------------------------------------------------------------

    def scatter(
        self,
        x_list: Sequence[Sequence[float]],
        y_list: Sequence[Sequence[float]],
        *,
        labels: Sequence[str] | None = None,
        colors: Sequence[str] | None = None,
        title: str | None = None,
        xlabel: str = "",
        ylabel: str = "",
        marker_size: int = 5,
        svg_height: int = 210,
    ) -> "Axes":
        """Multi-series scatter plot.

        Parameters
        ----------
        x_list:
            List of x arrays, one per series.
        y_list:
            Corresponding y arrays, one per series.
        labels:
            Legend labels per series.
        colors:
            Hex colours per series.
        marker_size:
            Radius of scatter circles in pixels.
        svg_height:
            Pixel height of the SVG chart area.

        Examples
        --------
        ::

            fig, ax = hp.subplots(title="Scatter")
            ax.scatter(
                [x_a, x_b],
                [y_a, y_b],
                labels=["Control", "Treatment"],
                colors=["#4a82c8", "#f0604a"],
            )
        """
        if title:
            self._title = title
        self._chart = self._build_svg_chart(
            "scatter", x_list, y_list,
            labels=labels, colors=colors, ci=None,
            xlabel=xlabel, ylabel=ylabel,
            step=False, markers=True, marker_size=marker_size,
            svg_height=svg_height,
        )
        return self

    # ------------------------------------------------------------------

    def kmplot(
        self,
        times_list: Sequence[Sequence[float]],
        survival_list: Sequence[Sequence[float]],
        *,
        labels: Sequence[str] | None = None,
        colors: Sequence[str] | None = None,
        ci: Sequence[tuple[Sequence[float], Sequence[float]]] | None = None,
        title: str | None = None,
        xlabel: str = "Time",
        ylabel: str = "Survival probability",
        svg_height: int = 210,
    ) -> "Axes":
        """Step-function line chart for pre-computed survival curves.

        This is a thin convenience wrapper around :meth:`lineplot` with
        ``step=True``.  Pass your already-computed ``(times, survival)``
        arrays — the analytics are entirely up to you.

        Examples
        --------
        ::

            # compute however you like, then hand off to htmlplot
            fig, ax = hp.subplots(title="Kaplan-Meier survival curve")
            ax.kmplot(
                [t1, t2],
                [s1, s2],
                labels=["Uzbekistan", "Turkmenistan"],
                colors=["#f0604a", "#2ed090"],
                ci=[(lo1, hi1), (lo2, hi2)],
            )
        """
        return self.lineplot(
            times_list, survival_list,
            labels=labels, colors=colors, ci=ci,
            title=title, xlabel=xlabel, ylabel=ylabel,
            step=True, markers=False,
            svg_height=svg_height,
        )

    # ------------------------------------------------------------------

    def pie(
        self,
        x: Sequence[float],
        labels: Sequence[str] | None = None,
        *,
        colors: Sequence[str] | None = None,
        explode: Sequence[float] | None = None,
        autopct: str | Callable | None = None,
        pctdistance: float = 0.6,
        shadow: bool = False,
        labeldistance: float = 1.15,
        startangle: float = 90,
        radius: float = 1.0,
        counterclock: bool = True,
        normalize: bool = True,
        title: str | None = None,
        svg_height: int = 260,
        donut: float = 0.0,
    ) -> "Axes":
        """Pie / donut chart – mirrors ``matplotlib.Axes.pie``.

        Parameters
        ----------
        x:
            Wedge sizes.  Normalised to sum-to-1 unless *normalize=False*.
        labels:
            Text label for each wedge.  Shown in a right-side legend.
        colors:
            Explicit hex colours, cycled if fewer than the number of wedges.
        explode:
            Per-wedge radial offset as a fraction of the outer radius
            (0 = no offset, 0.1 = 10 % explode).
        autopct:
            Annotate each wedge with its percentage.  Pass a %-style format
            string like ``"%.1f%%"`` or a callable ``(pct: float) -> str``.
        pctdistance:
            Radial fraction at which the *autopct* label is drawn (default 0.6).
        shadow:
            Draw a subtle elliptical shadow beneath the pie.
        labeldistance:
            Kept for API parity; labels are rendered in the legend.
        startangle:
            Degrees counter-clockwise from 3 o'clock at which the first wedge
            starts.  Default 90 places the first edge at 12 o'clock.
        radius:
            Outer radius scaling factor (default 1.0).
        counterclock:
            If True (default), wedges are drawn counter-clockwise.
        normalize:
            Rescale *x* so values sum to 1.  Default True.
        donut:
            Fraction (0–0.9) for a centred hole: 0 = solid pie, 0.5 = donut.
        svg_height:
            Pixel height of the SVG element.
        """
        if title:
            self._title = title

        x = [float(v) for v in x]
        n = len(x)
        if n == 0:
            return self

        total = sum(x)
        fractions = [v / total for v in x] if total > 0 else [1.0 / n] * n

        _dc = ["#f0604a", "#2ed090", "#4a82c8", "#f0a030",
               "#b060f0", "#40d0d0", "#e0c030", "#c04060"]
        wedge_colors = (
            [colors[i % len(colors)] for i in range(n)]
            if colors
            else [_dc[i % len(_dc)] for i in range(n)]
        )
        wedge_labels = list(labels) if labels else [f"Slice {i + 1}" for i in range(n)]

        self._chart = {
            "type": "pie",
            "fractions": fractions,
            "labels": wedge_labels,
            "colors": wedge_colors,
            "explode": list(explode) if explode else [0.0] * n,
            "autopct": autopct,
            "pctdistance": pctdistance,
            "shadow": shadow,
            "startangle": startangle,
            "counterclock": counterclock,
            "radius": radius,
            "svg_height": svg_height,
            "donut": max(0.0, min(0.9, float(donut))),
            "x_raw": x,
        }
        return self

    # ------------------------------------------------------------------

    def boxplot(
        self,
        data: Sequence[Sequence[float]],
        labels: Sequence[str] | None = None,
        *,
        title: str | None = None,
        vert: bool = True,
        notch: bool = False,
        whis: float | tuple[float, float] = 1.5,
        showfliers: bool = True,
        showmeans: bool = False,
        meanline: bool = False,
        widths: float = 0.5,
        patch_artist: bool = True,
        showcaps: bool = True,
        colors: Sequence[str] | None = None,
        palette: str = "blues",
        svg_height: int = 240,
        xlabel: str = "",
        ylabel: str = "",
    ) -> "Axes":
        """Box-and-whisker plot – mirrors ``matplotlib.Axes.boxplot``.

        Parameters
        ----------
        data:
            List of 1-D arrays, one per group.
        labels:
            Tick label for each group.
        vert:
            If True (default), boxes are vertical (values on y-axis).
        notch:
            If True, draw a notch representing a 95 % CI around the median.
        whis:
            Whisker reach as a multiple of IQR (default 1.5 → Tukey fences),
            **or** an explicit ``(lower_pct, upper_pct)`` percentile pair.
        showfliers:
            If True (default), overlay individual outlier points.
        showmeans:
            If True, mark the mean.
        meanline:
            If True (with *showmeans*), draw the mean as a dashed line across
            the box; otherwise a triangle marker is used.
        widths:
            Box width as a fraction of the per-group slot width (default 0.5).
        patch_artist:
            If True (default), fill boxes with colour.
        showcaps:
            If True (default), draw horizontal caps at whisker tips.
        colors:
            Explicit hex colours per box; overrides *palette*.
        palette:
            Named palette for automatic colouring.
        svg_height:
            Pixel height of the SVG element.
        xlabel, ylabel:
            Axis labels.
        """
        if title:
            self._title = title

        groups = [[float(v) for v in grp] for grp in data]
        n = len(groups)
        group_labels = list(labels) if labels else [f"Group {i + 1}" for i in range(n)]

        _dc = ["#4a82c8", "#2ed090", "#f0604a", "#f0a030",
               "#b060f0", "#40d0d0", "#e0c030", "#c04060"]
        box_colors = (
            [colors[i % len(colors)] for i in range(n)]
            if colors
            else [_dc[i % len(_dc)] for i in range(n)]
        )

        self._chart = {
            "type": "boxplot",
            "groups": groups,
            "labels": group_labels,
            "stats": [self._box_stats(g, whis) for g in groups],
            "colors": box_colors,
            "vert": vert,
            "notch": notch,
            "showfliers": showfliers,
            "showmeans": showmeans,
            "meanline": meanline,
            "widths": widths,
            "patch_artist": patch_artist,
            "showcaps": showcaps,
            "svg_height": svg_height,
            "xlabel": xlabel,
            "ylabel": ylabel,
        }
        return self

    # ------------------------------------------------------------------

    def heatmap(
        self,
        data: Sequence[Sequence[float]],
        *,
        xlabels: Sequence[str] | None = None,
        ylabels: Sequence[str] | None = None,
        fmt: str | Callable | None = ".2g",
        cmap: str = "blues",
        annot: bool = True,
        linewidths: float = 2.0,
        vmin: float | None = None,
        vmax: float | None = None,
        cbar: bool = True,
        title: str | None = None,
        svg_height: int | None = None,
    ) -> "Axes":
        """Heatmap – mirrors ``seaborn.heatmap`` / ``matplotlib.imshow``.

        Parameters
        ----------
        data:
            2-D array of shape (n_rows × n_cols).
        xlabels:
            Column header labels (x-axis, left → right).
        ylabels:
            Row header labels (y-axis, top → bottom).
        fmt:
            Cell annotation format spec (e.g. ``".2g"``, ``".0%"``) or a
            callable ``(value) -> str``.  Set to ``None`` to disable
            annotations even when *annot=True*.
        cmap:
            Named colour palette from :data:`~htmlplot.PALETTES` (default
            ``"blues"``).
        annot:
            If True (default), overlay each cell with its formatted value.
        linewidths:
            Width in pixels of the grid lines between cells (default 2).
        vmin, vmax:
            Clip the colour scale.  Defaults to the data's min / max.
        cbar:
            If True (default), draw a colour-scale bar on the right.
        svg_height:
            Total SVG height in pixels.  Auto-sized from the data shape
            when omitted.
        """
        if title:
            self._title = title

        rows = [[float(v) for v in row] for row in data]
        n_rows = len(rows)
        n_cols = max((len(r) for r in rows), default=0)
        for r in rows:
            while len(r) < n_cols:
                r.append(0.0)

        flat = [v for row in rows for v in row]
        _vmin = vmin if vmin is not None else (min(flat) if flat else 0.0)
        _vmax = vmax if vmax is not None else (max(flat) if flat else 1.0)
        if _vmax == _vmin:
            _vmax = _vmin + 1.0

        _xl = list(xlabels) if xlabels else [str(j) for j in range(n_cols)]
        _yl = list(ylabels) if ylabels else [str(i) for i in range(n_rows)]

        if svg_height is None:
            cell_h_est = max(22, min(52, 300 // max(n_rows, 1)))
            svg_height = n_rows * cell_h_est + 80

        self._chart = {
            "type": "heatmap",
            "data": rows,
            "n_rows": n_rows,
            "n_cols": n_cols,
            "xlabels": _xl,
            "ylabels": _yl,
            "fmt": fmt,
            "cmap": cmap,
            "annot": annot,
            "linewidths": linewidths,
            "vmin": _vmin,
            "vmax": _vmax,
            "cbar": cbar,
            "svg_height": svg_height,
        }
        return self

    # ------------------------------------------------------------------

    def stackedbar(
        self,
        labels: Sequence[str],
        data: "dict[str, Sequence[float]] | Sequence[Sequence[float]]",
        *,
        series_labels: Sequence[str] | None = None,
        colors: Sequence[str] | None = None,
        palette: str | list[str] | None = None,
        height: int = 200,
        fmt: str | Callable | None = None,
        normalized: bool = False,
        title: str | None = None,
        xlabel: str = "",
        ylabel: str = "",
    ) -> "Axes":
        """Stacked vertical bar chart.

        Parameters
        ----------
        labels:
            Category labels along the x-axis.
        data:
            Either a :class:`dict` mapping series names to value arrays, or a
            plain list of arrays (name via *series_labels*).
        series_labels:
            Series names when *data* is a list.
        colors:
            Explicit hex colours per series.
        palette:
            Named palette (used only when *colors* is not provided).
        height:
            Pixel height of the chart area.
        fmt:
            Format for value labels shown in tooltips.
        normalized:
            If True, render as a 100 % stacked bar chart.
        xlabel, ylabel:
            Axis labels.
        """
        if title:
            self._title = title

        labels = list(labels)
        n_cats = len(labels)

        if isinstance(data, dict):
            series_pairs: list[tuple[str, list[float]]] = [
                (k, [float(v) for v in vs]) for k, vs in data.items()
            ]
        else:
            _sl = (list(series_labels) if series_labels
                   else [f"Series {i + 1}" for i in range(len(data))])
            series_pairs = [(_sl[i], [float(v) for v in vs])
                            for i, vs in enumerate(data)]

        # Pad / truncate each series to n_cats
        series_pairs = [(name, (vs + [0.0] * n_cats)[:n_cats])
                        for name, vs in series_pairs]

        _dc = ["#4a82c8", "#2ed090", "#f0604a", "#f0a030",
               "#b060f0", "#40d0d0", "#e0c030", "#c04060"]
        s_colors = (
            [colors[i % len(colors)] for i in range(len(series_pairs))]
            if colors
            else [_dc[i % len(_dc)] for i in range(len(series_pairs))]
        )

        if normalized:
            col_totals = [
                sum(vs[j] for _, vs in series_pairs) for j in range(n_cats)
            ]
            series_pairs = [
                (name, [v / col_totals[j] * 100 if col_totals[j] else 0.0
                        for j, v in enumerate(vs)])
                for name, vs in series_pairs
            ]

        # Compute per-column running bottoms
        bottoms = [0.0] * n_cats
        series_out: list[dict] = []
        for name, vs in series_pairs:
            segs = [{"bottom": bottoms[j], "value": vs[j], "label": labels[j]}
                    for j in range(n_cats)]
            for j in range(n_cats):
                bottoms[j] += vs[j]
            series_out.append({"name": name, "segments": segs})

        self._chart = {
            "type": "stackedbar",
            "labels": labels,
            "series": series_out,
            "series_colors": s_colors,
            "max_total": max(bottoms) if bottoms else 1.0,
            "chart_height": height,
            "fmt": fmt,
            "normalized": normalized,
            "xlabel": xlabel,
            "ylabel": ylabel,
        }
        return self

    # ------------------------------------------------------------------
    # Annotations / extras
    # ------------------------------------------------------------------

    def infobox(self, text: str) -> "Axes":
        """Append an info/callout box below the chart."""
        self._annotations.append(("infobox", text))
        return self

    def divider(self) -> "Axes":
        """Append a thin horizontal rule."""
        self._annotations.append(("divider", ""))
        return self

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    # Card overhead in pixels (top-padding + bottom-padding + title block)
    _CARD_PAD_V = 48   # 26 top + 22 bottom
    _TITLE_H    = 35   # card-title height + its margin-bottom

    def to_html(self, cell_height: int | None = None) -> str:
        """Render this Axes as an HTML card.

        Parameters
        ----------
        cell_height:
            When provided (set by the parent :class:`~htmlplot.Figure` when
            a fixed *height* / *figsize* is used), every chart inside the
            card is scaled so that it fills the available vertical space —
            matching matplotlib's behaviour when ``figsize`` constrains the
            canvas height.
        """
        parts: list[str] = []

        if self._title:
            parts.append(
                f'<div class="hp-card-title">{_escape(self._title)}</div>'
            )

        # ── Compute effective chart height from cell constraint ──────────
        # Subtract card padding and optional title block to get the area
        # available for the actual chart content.
        chart_h: int | None = None
        if cell_height is not None:
            overhead = self._CARD_PAD_V
            if self._title:
                overhead += self._TITLE_H
            chart_h = max(60, cell_height - overhead)

        # ── Temporarily override chart dimensions ────────────────────────
        # SVG charts use "svg_height"; CSS bar charts use "chart_height".
        # We patch the dict, render, then restore — keeping the user's
        # original intent intact for subsequent renders.
        _SVG_CHARTS = ("lineplot", "scatter", "boxplot", "heatmap", "pie")
        _CSS_CHARTS = ("bar", "stackedbar")

        height_key: str | None = None
        orig_h: int | None = None

        if chart_h is not None and self._chart:
            ct0 = self._chart["type"]
            if ct0 in _SVG_CHARTS:
                height_key = "svg_height"
            elif ct0 in _CSS_CHARTS:
                height_key = "chart_height"
            if height_key:
                orig_h = self._chart.get(height_key)
                self._chart[height_key] = chart_h

        try:
            if self._chart:
                ct = self._chart["type"]
                if ct == "barh":
                    parts.append(self._render_barh())
                elif ct == "bar":
                    parts.append(self._render_bar())
                elif ct in ("lineplot", "scatter"):
                    if self._chart.get("series"):
                        parts.append(self._render_legend())
                    parts.append(self._render_svg_chart())
                elif ct == "pie":
                    parts.append(self._render_pie())
                elif ct == "boxplot":
                    parts.append(self._render_boxplot())
                elif ct == "heatmap":
                    parts.append(self._render_heatmap())
                elif ct == "stackedbar":
                    parts.append(self._render_stackedbar())
        finally:
            # Always restore the original height so re-renders are correct
            if height_key and orig_h is not None and self._chart:
                self._chart[height_key] = orig_h

        for ann_type, ann_data in self._annotations:
            if ann_type == "infobox":
                parts.append(f'<div class="hp-info-box">{ann_data}</div>')
            elif ann_type == "divider":
                parts.append('<div class="hp-divider"></div>')

        inner = "\n".join(parts)

        # When cell_height is constrained, fix the card height so rows in a
        # grid all have the same height and the figure fills its allotted space.
        card_style = (
            f' style="height:{cell_height}px;box-sizing:border-box;"'
            if cell_height is not None else ""
        )
        return f'<div class="hp-card"{card_style}>\n{inner}\n</div>'

    # ------------------------------------------------------------------
    # Private renderers
    # ------------------------------------------------------------------

    def _render_barh(self) -> str:
        bars = self._chart["bars"]
        lw = self._chart.get("label_width", 150)
        rows = []
        for b in bars:
            tip = _tip(b["label"], b["value_label"])
            rows.append(
                f'<div class="hp-barh-row">'
                f'<div class="hp-barh-label" style="width:{lw}px">'
                f'{_escape(str(b["label"]))}'
                f'</div>'
                f'<div class="hp-barh-track" data-tip="{tip}">'
                f'<div class="hp-barh-fill" '
                f'style="width:{b["width_pct"]:.2f}%;'
                f'background:{b["color"]};color:{b["text_color"]};">'
                f'{_escape(b["value_label"])}'
                f'</div>'
                f'</div>'
                f'</div>'
            )
        return "\n".join(rows)

    def _render_bar(self) -> str:
        bars = self._chart["bars"]
        ch = self._chart.get("chart_height", 200)
        cols = []
        for b in bars:
            tip = _tip(b["label"], b["value_label"])
            # Recompute pixel height from fraction × current chart_height so
            # the bars scale correctly whenever chart_height is overridden.
            bar_px = int(b.get("bar_height_frac", 0.0) * ch)
            cols.append(
                f'<div class="hp-bar-col" data-tip="{tip}">'
                f'<div class="hp-bar-value-label">{_escape(b["value_label"])}</div>'
                f'<div class="hp-bar-body" '
                f'style="height:{bar_px}px;background:{b["color"]};"></div>'
                f'<div class="hp-bar-baseline"></div>'
                f'<div class="hp-bar-xlabel">{_escape(str(b["label"]))}</div>'
                f'</div>'
            )
        inner = "\n".join(cols)
        return (
            f'<div class="hp-bar-outer">'
            f'<div class="hp-bar-chart" style="height:{ch}px;">'
            f'{inner}'
            f'</div>'
            f'</div>'
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _build_svg_chart(
        chart_type: str,
        x_list, y_list, *,
        labels, colors, ci,
        xlabel, ylabel,
        step, markers, marker_size,
        svg_height,
    ) -> dict:
        """Pack all series data into the chart dict stored on self._chart."""
        _default_colors = ["#f0604a", "#2ed090", "#4a82c8", "#f0a030",
                           "#b060f0", "#40d0d0", "#e0c030", "#c04060"]
        series: list[dict] = []
        for i, (xs, ys) in enumerate(zip(x_list, y_list)):
            color = (colors[i] if colors and i < len(colors)
                     else _default_colors[i % len(_default_colors)])
            label = (labels[i] if labels and i < len(labels)
                     else f"Series {i + 1}")
            entry: dict = {
                "x": list(xs),
                "y": list(ys),
                "color": color,
                "label": label,
            }
            if ci and i < len(ci):
                lo, hi = ci[i]
                entry["ci_lower"] = list(lo)
                entry["ci_upper"] = list(hi)
            series.append(entry)

        return {
            "type": chart_type,
            "series": series,
            "xlabel": xlabel,
            "ylabel": ylabel,
            "step": step,
            "markers": markers,
            "marker_size": marker_size,
            "scatter": chart_type == "scatter",
            "svg_height": svg_height,
        }

    def _render_legend(self) -> str:
        """Colour-dot legend for line/scatter charts."""
        series = self._chart.get("series", [])
        # Only render if there's more than one series, or labels were supplied
        show = len(series) > 1 or any(
            s["label"] != f"Series {i + 1}"
            for i, s in enumerate(series)
        )
        if not show:
            return ""
        items = []
        for s in series:
            items.append(
                f'<div class="hp-legend-item">'
                f'<div class="hp-legend-dot" style="background:{s["color"]};"></div>'
                f'{_escape(s["label"])}'
                f'</div>'
            )
        return f'<div class="hp-legend">{"".join(items)}</div>'

    def _render_svg_chart(self) -> str:
        """Generic SVG renderer shared by lineplot, scatter, and kmplot."""
        chart = self._chart
        series_list: list[dict] = chart["series"]
        xlabel: str = chart.get("xlabel", "")
        ylabel: str = chart.get("ylabel", "")
        svg_height: int = chart.get("svg_height", 210)
        is_step: bool = chart.get("step", False)
        show_markers: bool = chart.get("markers", False)
        is_scatter: bool = chart.get("scatter", False)
        marker_size: int = chart.get("marker_size", 4)

        # --- Layout ----------------------------------------------------------
        W = 520
        H = svg_height
        # Left margin: enough room for y-tick labels (≤7 chars at font-size 10)
        ML = 58 if ylabel else 46
        MR, MT = 20, 14
        # Bottom margin: space for x-tick labels + xlabel; extra 4 px for descenders
        MB = 46 if xlabel else 28
        CW = W - ML - MR
        CH = H - MT - MB

        # --- Data bounds -----------------------------------------------------
        all_x = [v for s in series_list for v in s["x"]]
        all_y = [v for s in series_list for v in s["y"]]
        if not all_x:
            return ""

        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)

        # Add a small y-padding so points don't sit on the axis spine
        y_pad = (y_max - y_min) * 0.08 if y_max != y_min else 0.5
        y_lo = y_min - y_pad
        y_hi = y_max + y_pad

        def tx(v: float) -> float:
            return ML + (v - x_min) / (x_max - x_min) * CW if x_max != x_min else ML + CW / 2

        def ty(v: float) -> float:
            return MT + (y_hi - v) / (y_hi - y_lo) * CH if y_hi != y_lo else MT + CH / 2

        # --- Tick generation -------------------------------------------------
        x_ticks = nice_ticks(x_min, x_max, n=5)
        y_ticks = nice_ticks(y_lo, y_hi, n=5)

        # Unique clip-path id
        clip_id = f"hpsvg{id(self) & 0xFFFFFF}"

        _font = "font-family=\"'Segoe UI',system-ui,sans-serif\""
        _grid_stroke = 'stroke="#1e2535" stroke-width="1"'
        _tick_stroke = 'stroke="#2a3040" stroke-width="1"'
        _label_fill = 'fill="#5a6a80"'

        parts: list[str] = []

        # SVG open + defs
        parts.append(
            f'<div class="hp-svg-wrap">'
            f'<svg viewBox="0 0 {W} {H}" width="100%" '
            f'style="display:block;overflow:hidden;">'
            f'<defs><clipPath id="{clip_id}">'
            f'<rect x="{ML}" y="{MT}" width="{CW}" height="{CH}"/>'
            f'</clipPath></defs>'
        )

        # Y-axis grid lines + labels
        for g in y_ticks:
            if g < y_lo or g > y_hi:
                continue
            y = ty(g)
            parts.append(
                f'<line x1="{ML}" y1="{y:.1f}" x2="{ML + CW}" y2="{y:.1f}" {_grid_stroke}/>'
            )
            parts.append(
                f'<text x="{ML - 7}" y="{y + 3.5:.1f}" '
                f'text-anchor="end" font-size="10" {_label_fill} {_font}>'
                f'{g:g}</text>'
            )

        # X-axis ticks + labels
        for tick in x_ticks:
            x = tx(tick)
            parts.append(
                f'<line x1="{x:.1f}" y1="{MT + CH}" '
                f'x2="{x:.1f}" y2="{MT + CH + 4}" {_tick_stroke}/>'
            )
            parts.append(
                f'<text x="{x:.1f}" y="{MT + CH + 16}" '
                f'text-anchor="middle" font-size="10" {_label_fill} {_font}>'
                f'{tick:g}</text>'
            )

        # Axis spines
        parts.append(
            f'<line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT + CH}" {_tick_stroke}/>'
        )
        parts.append(
            f'<line x1="{ML}" y1="{MT + CH}" x2="{ML + CW}" y2="{MT + CH}" {_tick_stroke}/>'
        )

        # Axis labels
        if xlabel:
            parts.append(
                f'<text x="{ML + CW / 2:.1f}" y="{H - 8}" '
                f'text-anchor="middle" font-size="10" {_label_fill} {_font}>'
                f'{_escape(xlabel)}</text>'
            )
        if ylabel:
            parts.append(
                f'<text transform="rotate(-90)" '
                f'x="{-(MT + CH / 2):.1f}" y="13" '
                f'text-anchor="middle" font-size="10" {_label_fill} {_font}>'
                f'{_escape(ylabel)}</text>'
            )

        # --- Series ----------------------------------------------------------
        for series in series_list:
            xs = series["x"]
            ys = series["y"]
            color = series["color"]
            ci_lower = series.get("ci_lower")
            ci_upper = series.get("ci_upper")

            if not xs:
                continue

            # CI band (behind everything else)
            if ci_lower and ci_upper:
                if is_step:
                    fwd = f'M {tx(xs[0]):.2f} {ty(ci_upper[0]):.2f}'
                    for i in range(1, len(xs)):
                        fwd += f' H {tx(xs[i]):.2f} V {ty(ci_upper[i]):.2f}'
                    fwd += f' H {tx(xs[-1]):.2f}'
                    bwd = [f' V {ty(ci_lower[-1]):.2f}']
                    for i in range(len(xs) - 1, 0, -1):
                        bwd.append(f' H {tx(xs[i]):.2f} V {ty(ci_lower[i - 1]):.2f}')
                    bwd.append(f' H {tx(xs[0]):.2f} Z')
                    band = fwd + "".join(bwd)
                else:
                    # Smooth band: upper fwd then lower bwd
                    fwd = f'M {tx(xs[0]):.2f} {ty(ci_upper[0]):.2f}'
                    fwd += "".join(
                        f' L {tx(xs[i]):.2f} {ty(ci_upper[i]):.2f}'
                        for i in range(1, len(xs))
                    )
                    bwd = "".join(
                        f' L {tx(xs[i]):.2f} {ty(ci_lower[i]):.2f}'
                        for i in range(len(xs) - 1, -1, -1)
                    )
                    band = fwd + bwd + " Z"

                parts.append(
                    f'<path d="{band}" fill="{color}" fill-opacity="0.13" '
                    f'stroke="none" clip-path="url(#{clip_id})"/>'
                )

            # Line path (skip for pure scatter)
            if not is_scatter:
                if is_step:
                    path = f'M {tx(xs[0]):.2f} {ty(ys[0]):.2f}'
                    for i in range(1, len(xs)):
                        path += f' H {tx(xs[i]):.2f} V {ty(ys[i]):.2f}'
                    # Extend last segment to right edge
                    path += f' H {tx(xs[-1]):.2f}'
                else:
                    path = f'M {tx(xs[0]):.2f} {ty(ys[0]):.2f}'
                    path += "".join(
                        f' L {tx(xs[i]):.2f} {ty(ys[i]):.2f}'
                        for i in range(1, len(xs))
                    )

                parts.append(
                    f'<path d="{path}" fill="none" stroke="{color}" '
                    f'stroke-width="2.2" stroke-linejoin="round" '
                    f'stroke-linecap="round" clip-path="url(#{clip_id})"/>'
                )

            # Visible circles (scatter or line markers)
            if show_markers or is_scatter:
                r = marker_size
                for xi, yi in zip(xs, ys):
                    parts.append(
                        f'<circle cx="{tx(xi):.2f}" cy="{ty(yi):.2f}" r="{r}" '
                        f'fill="{color}" fill-opacity="0.85" '
                        f'clip-path="url(#{clip_id})"/>'
                    )

            # Invisible hit-area circles at every data point (tooltip triggers)
            xl = chart.get("xlabel", "")
            yl = chart.get("ylabel", "")
            label = series["label"]
            hr = max(marker_size + 4, 8)   # hit radius always at least 8 px
            for xi, yi in zip(xs, ys):
                x_part = f"{xl}: {xi:g}" if xl else f"{xi:g}"
                y_part = f"{yl}: {yi:g}" if yl else f"{yi:g}"
                tip = _tip(label, x_part, y_part)
                parts.append(
                    f'<circle cx="{tx(xi):.2f}" cy="{ty(yi):.2f}" r="{hr}" '
                    f'fill="transparent" stroke="none" style="cursor:default;" '
                    f'data-tip="{tip}" clip-path="url(#{clip_id})"/>'
                )

        parts.append('</svg></div>')
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Pie chart renderer
    # ------------------------------------------------------------------

    def _render_pie(self) -> str:
        chart = self._chart
        fractions: list[float] = chart["fractions"]
        labels: list[str] = chart["labels"]
        colors: list[str] = chart["colors"]
        explode: list[float] = chart["explode"]
        autopct = chart["autopct"]
        pctdistance: float = chart["pctdistance"]
        shadow: bool = chart["shadow"]
        startangle: float = chart["startangle"]
        counterclock: bool = chart["counterclock"]
        radius: float = chart["radius"]
        H: int = chart["svg_height"]
        donut: float = chart["donut"]
        x_raw: list[float] = chart["x_raw"]
        n = len(fractions)

        _font = "font-family=\"'Segoe UI',system-ui,sans-serif\""

        # Layout: pie occupies a left square; legend on the right
        pie_size = min(H - 16, 256)
        cx = pie_size / 2 + 10
        cy = H / 2
        R = pie_size / 2 * 0.78 * radius
        leg_x = cx + R + 32
        W = max(int(leg_x + 140), 340)

        parts: list[str] = []
        parts.append(
            f'<div class="hp-svg-wrap">'
            f'<svg viewBox="0 0 {W} {H}" width="100%" '
            f'style="display:block;overflow:hidden;">'
        )

        if shadow:
            parts.append(
                f'<ellipse cx="{cx + 5:.1f}" cy="{cy + R * 0.15 + 5:.1f}" '
                f'rx="{R:.1f}" ry="{R * 0.12:.1f}" '
                f'fill="rgba(0,0,0,0.22)"/>'
            )

        # sweep=0 → CCW on screen (standard for counterclock=True)
        sweep = 0 if counterclock else 1
        delta_sign = 1 if counterclock else -1
        θ = math.radians(startangle)

        for i in range(n):
            frac = fractions[i]
            if frac <= 0:
                continue
            color = colors[i]
            ex = explode[i]

            delta = 2 * math.pi * frac * delta_sign
            end_θ = θ + delta
            mid_θ = θ + delta / 2

            ecx = cx + ex * R * math.cos(mid_θ)
            ecy = cy - ex * R * math.sin(mid_θ)

            # For a full-circle slice use two half-arcs to avoid degenerate SVG
            if abs(frac - 1.0) < 1e-9:
                # Split into two 180° arcs
                half_θ = θ + math.pi * delta_sign
                mx = ecx + R * math.cos(half_θ)
                my = ecy - R * math.sin(half_θ)
                x1 = ecx + R * math.cos(θ)
                y1 = ecy - R * math.sin(θ)
                if donut > 0:
                    inner_R = R * donut
                    imx = ecx + inner_R * math.cos(half_θ)
                    imy = ecy - inner_R * math.sin(half_θ)
                    ix1 = ecx + inner_R * math.cos(θ)
                    iy1 = ecy - inner_R * math.sin(θ)
                    path_d = (
                        f"M {x1:.2f},{y1:.2f} A {R:.2f},{R:.2f} 0 0,{sweep} {mx:.2f},{my:.2f} "
                        f"A {R:.2f},{R:.2f} 0 0,{sweep} {x1:.2f},{y1:.2f} "
                        f"L {ix1:.2f},{iy1:.2f} "
                        f"A {inner_R:.2f},{inner_R:.2f} 0 0,{1-sweep} {imx:.2f},{imy:.2f} "
                        f"A {inner_R:.2f},{inner_R:.2f} 0 0,{1-sweep} {ix1:.2f},{iy1:.2f} Z"
                    )
                else:
                    path_d = (
                        f"M {ecx:.2f},{ecy:.2f} L {x1:.2f},{y1:.2f} "
                        f"A {R:.2f},{R:.2f} 0 0,{sweep} {mx:.2f},{my:.2f} "
                        f"A {R:.2f},{R:.2f} 0 0,{sweep} {x1:.2f},{y1:.2f} Z"
                    )
            else:
                x1 = ecx + R * math.cos(θ)
                y1 = ecy - R * math.sin(θ)
                x2 = ecx + R * math.cos(end_θ)
                y2 = ecy - R * math.sin(end_θ)
                large_arc = 1 if abs(delta) > math.pi else 0
                if donut > 0:
                    inner_R = R * donut
                    ix1 = ecx + inner_R * math.cos(θ)
                    iy1 = ecy - inner_R * math.sin(θ)
                    ix2 = ecx + inner_R * math.cos(end_θ)
                    iy2 = ecy - inner_R * math.sin(end_θ)
                    path_d = (
                        f"M {x1:.2f},{y1:.2f} "
                        f"A {R:.2f},{R:.2f} 0 {large_arc},{sweep} {x2:.2f},{y2:.2f} "
                        f"L {ix2:.2f},{iy2:.2f} "
                        f"A {inner_R:.2f},{inner_R:.2f} 0 {large_arc},{1-sweep} "
                        f"{ix1:.2f},{iy1:.2f} Z"
                    )
                else:
                    path_d = (
                        f"M {ecx:.2f},{ecy:.2f} L {x1:.2f},{y1:.2f} "
                        f"A {R:.2f},{R:.2f} 0 {large_arc},{sweep} {x2:.2f},{y2:.2f} Z"
                    )

            pct = frac * 100
            tip = _tip(labels[i], f"{x_raw[i]:g}", f"{pct:.1f}%")
            parts.append(
                f'<path d="{path_d}" fill="{color}" '
                f'stroke="rgba(0,0,0,0.12)" stroke-width="1.5" '
                f'data-tip="{tip}" style="cursor:default;"/>'
            )

            # Autopct text inside wedge
            if autopct is not None:
                px = ecx + pctdistance * R * math.cos(mid_θ)
                py = ecy - pctdistance * R * math.sin(mid_θ)
                if callable(autopct):
                    pct_text = autopct(pct)
                elif isinstance(autopct, str):
                    try:
                        pct_text = autopct % pct
                    except (TypeError, ValueError):
                        pct_text = autopct.format(pct)
                else:
                    pct_text = f"{pct:.1f}%"
                tc = get_text_color(color)
                parts.append(
                    f'<text x="{px:.2f}" y="{py + 4:.2f}" '
                    f'text-anchor="middle" font-size="10" '
                    f'fill="{tc}" font-weight="600" {_font}>'
                    f'{_escape(pct_text)}</text>'
                )

            θ = end_θ

        # Right-side legend
        _lf = "#8090a4"
        item_h = 20
        leg_y0 = max(cy - n * item_h / 2, 8)
        for j in range(n):
            ly = leg_y0 + j * item_h
            c = colors[j]
            pct_str = f"{fractions[j] * 100:.1f}%"
            tip = _tip(labels[j], f"{x_raw[j]:g}", pct_str)
            parts.append(
                f'<rect x="{leg_x:.1f}" y="{ly - 7:.1f}" width="11" height="11" '
                f'rx="3" fill="{c}" data-tip="{tip}" style="cursor:default;"/>'
            )
            parts.append(
                f'<text x="{leg_x + 16:.1f}" y="{ly + 2:.1f}" '
                f'font-size="11" fill="{_lf}" {_font}>'
                f'{_escape(labels[j])}</text>'
            )

        parts.append('</svg></div>')
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Box-plot renderer
    # ------------------------------------------------------------------

    @staticmethod
    def _box_stats(data: list[float], whis) -> dict:
        """Compute Tukey box-plot statistics for one group."""
        if not data:
            return {"q1": 0.0, "q3": 0.0, "median": 0.0, "mean": 0.0,
                    "whisker_lo": 0.0, "whisker_hi": 0.0, "outliers": []}
        sd = sorted(data)
        n = len(sd)

        def _pct(p: float) -> float:
            idx = (n - 1) * p / 100.0
            lo = int(idx)
            hi = lo + 1
            if hi >= n:
                return sd[lo]
            return sd[lo] * (1.0 - (idx - lo)) + sd[hi] * (idx - lo)

        q1, median, q3 = _pct(25), _pct(50), _pct(75)
        iqr = q3 - q1
        mean = sum(data) / n

        if isinstance(whis, (int, float)):
            lo_fence, hi_fence = q1 - whis * iqr, q3 + whis * iqr
        else:
            lo_fence, hi_fence = _pct(whis[0]), _pct(whis[1])

        within = [x for x in sd if lo_fence <= x <= hi_fence]
        return {
            "q1": q1, "q3": q3, "median": median, "mean": mean,
            "whisker_lo": min(within) if within else q1,
            "whisker_hi": max(within) if within else q3,
            "outliers": [x for x in sd if x < lo_fence or x > hi_fence],
        }

    def _render_boxplot(self) -> str:
        chart = self._chart
        stats_list: list[dict] = chart["stats"]
        groups: list[list[float]] = chart["groups"]
        labels: list[str] = chart["labels"]
        colors: list[str] = chart["colors"]
        showfliers: bool = chart["showfliers"]
        showmeans: bool = chart["showmeans"]
        meanline: bool = chart["meanline"]
        widths_frac: float = chart["widths"]
        patch_artist: bool = chart["patch_artist"]
        showcaps: bool = chart["showcaps"]
        use_notch: bool = chart["notch"]
        H: int = chart["svg_height"]
        xlabel: str = chart["xlabel"]
        ylabel: str = chart["ylabel"]
        n = len(stats_list)

        _font = "font-family=\"'Segoe UI',system-ui,sans-serif\""
        _grid = 'stroke="#1e2535" stroke-width="1"'
        _spine = 'stroke="#2a3040" stroke-width="1"'
        _lf = 'fill="#5a6a80"'

        W = 520
        ML = 58 if ylabel else 46
        MR, MT = 20, 14
        MB = 46 if xlabel else 28
        CW = W - ML - MR
        CH = H - MT - MB

        # Data range
        all_v: list[float] = []
        for st in stats_list:
            all_v += [st["whisker_lo"], st["whisker_hi"]]
            if showfliers:
                all_v += st["outliers"]
            if showmeans:
                all_v.append(st["mean"])
        if not all_v:
            return ""

        y_min, y_max = min(all_v), max(all_v)
        y_pad = (y_max - y_min) * 0.10 if y_max != y_min else 0.5
        y_lo, y_hi = y_min - y_pad, y_max + y_pad
        y_ticks = nice_ticks(y_lo, y_hi, n=5)

        def ty(v: float) -> float:
            return MT + (y_hi - v) / (y_hi - y_lo) * CH if y_hi != y_lo else MT + CH / 2

        slot_w = CW / n

        def gx(i: int) -> float:
            return ML + (i + 0.5) * slot_w

        bhw = slot_w * widths_frac * 0.5  # box half-width

        parts: list[str] = []
        parts.append(
            f'<div class="hp-svg-wrap">'
            f'<svg viewBox="0 0 {W} {H}" width="100%" '
            f'style="display:block;overflow:hidden;">'
        )

        # Y grid + labels
        for g in y_ticks:
            if g < y_lo or g > y_hi:
                continue
            gy = ty(g)
            parts.append(f'<line x1="{ML}" y1="{gy:.1f}" x2="{ML+CW}" y2="{gy:.1f}" {_grid}/>')
            parts.append(
                f'<text x="{ML-7}" y="{gy+3.5:.1f}" text-anchor="end" '
                f'font-size="10" {_lf} {_font}>{g:g}</text>'
            )

        # Spines
        parts.append(f'<line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT+CH}" {_spine}/>')
        parts.append(f'<line x1="{ML}" y1="{MT+CH}" x2="{ML+CW}" y2="{MT+CH}" {_spine}/>')

        # X labels
        for i, lbl in enumerate(labels):
            parts.append(
                f'<text x="{gx(i):.1f}" y="{MT+CH+16}" text-anchor="middle" '
                f'font-size="10" {_lf} {_font}>{_escape(str(lbl))}</text>'
            )

        if xlabel:
            parts.append(
                f'<text x="{ML+CW/2:.1f}" y="{H-8}" text-anchor="middle" '
                f'font-size="10" {_lf} {_font}>{_escape(xlabel)}</text>'
            )
        if ylabel:
            parts.append(
                f'<text transform="rotate(-90)" x="{-(MT+CH/2):.1f}" y="13" '
                f'text-anchor="middle" font-size="10" {_lf} {_font}>'
                f'{_escape(ylabel)}</text>'
            )

        # Draw each box
        for i, (st, color) in enumerate(zip(stats_list, colors)):
            x = gx(i)
            xl, xr = x - bhw, x + bhw
            q1y, q3y = ty(st["q1"]), ty(st["q3"])
            medy = ty(st["median"])
            wloy, whiy = ty(st["whisker_lo"]), ty(st["whisker_hi"])

            tip = _tip(
                labels[i],
                f"Median: {st['median']:g}",
                f"Q1–Q3: {st['q1']:g} – {st['q3']:g}",
                f"IQR: {st['q3']-st['q1']:g}",
                f"Whiskers: [{st['whisker_lo']:g}, {st['whisker_hi']:g}]",
            )

            # Dashed whisker stems
            parts.append(
                f'<line x1="{x:.2f}" y1="{whiy:.2f}" x2="{x:.2f}" y2="{q3y:.2f}" '
                f'stroke="{color}" stroke-width="1.5" stroke-dasharray="4,2"/>'
            )
            parts.append(
                f'<line x1="{x:.2f}" y1="{q1y:.2f}" x2="{x:.2f}" y2="{wloy:.2f}" '
                f'stroke="{color}" stroke-width="1.5" stroke-dasharray="4,2"/>'
            )

            # Caps
            if showcaps:
                caphw = bhw * 0.45
                for cap_y in (whiy, wloy):
                    parts.append(
                        f'<line x1="{x-caphw:.2f}" y1="{cap_y:.2f}" '
                        f'x2="{x+caphw:.2f}" y2="{cap_y:.2f}" '
                        f'stroke="{color}" stroke-width="2"/>'
                    )

            # Box body
            fill_a = f'fill="{color}" fill-opacity="0.30"' if patch_artist else 'fill="none"'
            if use_notch and (st["q3"] - st["q1"]) > 0 and len(groups[i]) > 1:
                iqr = st["q3"] - st["q1"]
                notch_ext = 1.57 * iqr / math.sqrt(len(groups[i]))
                nlo_y = ty(st["median"] - notch_ext)
                nhi_y = ty(st["median"] + notch_ext)
                nw = bhw * 0.45
                notch_d = (
                    f"M {xl:.2f},{q3y:.2f} L {xl:.2f},{nhi_y:.2f} "
                    f"L {x-nw:.2f},{medy:.2f} L {xl:.2f},{nlo_y:.2f} "
                    f"L {xl:.2f},{q1y:.2f} L {xr:.2f},{q1y:.2f} "
                    f"L {xr:.2f},{nlo_y:.2f} L {x+nw:.2f},{medy:.2f} "
                    f"L {xr:.2f},{nhi_y:.2f} L {xr:.2f},{q3y:.2f} Z"
                )
                parts.append(
                    f'<path d="{notch_d}" {fill_a} stroke="{color}" stroke-width="1.5" '
                    f'data-tip="{tip}" style="cursor:default;"/>'
                )
            else:
                parts.append(
                    f'<rect x="{xl:.2f}" y="{q3y:.2f}" '
                    f'width="{2*bhw:.2f}" height="{max(q1y-q3y, 1):.2f}" '
                    f'{fill_a} stroke="{color}" stroke-width="1.5" '
                    f'data-tip="{tip}" style="cursor:default;"/>'
                )

            # Median line
            parts.append(
                f'<line x1="{xl:.2f}" y1="{medy:.2f}" x2="{xr:.2f}" y2="{medy:.2f}" '
                f'stroke="{color}" stroke-width="2.5"/>'
            )

            # Mean
            if showmeans:
                meany = ty(st["mean"])
                if meanline:
                    parts.append(
                        f'<line x1="{xl:.2f}" y1="{meany:.2f}" x2="{xr:.2f}" y2="{meany:.2f}" '
                        f'stroke="{color}" stroke-width="1.5" stroke-dasharray="5,3" opacity="0.85"/>'
                    )
                else:
                    ts = 5
                    parts.append(
                        f'<path d="M {x:.2f},{meany-ts:.2f} '
                        f'L {x+ts:.2f},{meany+ts:.2f} L {x-ts:.2f},{meany+ts:.2f} Z" '
                        f'fill="{color}" opacity="0.9"/>'
                    )

            # Outlier circles
            if showfliers:
                for ov in st["outliers"]:
                    oty = ty(ov)
                    otip = _tip(labels[i], f"Outlier: {ov:g}")
                    parts.append(
                        f'<circle cx="{x:.2f}" cy="{oty:.2f}" r="3.5" '
                        f'fill="none" stroke="{color}" stroke-width="1.5" '
                        f'data-tip="{otip}" style="cursor:default;"/>'
                    )

        parts.append('</svg></div>')
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Heatmap renderer
    # ------------------------------------------------------------------

    def _render_heatmap(self) -> str:
        chart = self._chart
        data: list[list[float]] = chart["data"]
        n_rows: int = chart["n_rows"]
        n_cols: int = chart["n_cols"]
        xlabels: list[str] = chart["xlabels"]
        ylabels: list[str] = chart["ylabels"]
        fmt = chart["fmt"]
        cmap: str = chart["cmap"]
        annot: bool = chart["annot"]
        lw: float = chart["linewidths"]
        vmin: float = chart["vmin"]
        vmax: float = chart["vmax"]
        cbar: bool = chart["cbar"]
        H: int = chart["svg_height"]

        if n_rows == 0 or n_cols == 0:
            return ""

        _font = "font-family=\"'Segoe UI',system-ui,sans-serif\""
        _lf = 'fill="#5a6a80"'

        W = 520
        ML = 72   # y-label space
        MR = 55 if cbar else 18
        MT = 32   # x-label space at top
        MB = 14
        CW = W - ML - MR
        CH = H - MT - MB

        cw = CW / n_cols
        ch_cell = CH / n_rows

        parts: list[str] = []
        clip_id = f"hphmc{id(self) & 0xFFFFFF}"
        grad_id = f"hphmg{id(self) & 0xFFFFFF}"

        parts.append(
            f'<div class="hp-svg-wrap">'
            f'<svg viewBox="0 0 {W} {H}" width="100%" '
            f'style="display:block;overflow:hidden;">'
        )
        parts.append(
            f'<defs><clipPath id="{clip_id}">'
            f'<rect x="{ML}" y="{MT}" width="{CW}" height="{CH}"/>'
            f'</clipPath></defs>'
        )

        # Cells
        for ri in range(n_rows):
            for ci in range(n_cols):
                v = data[ri][ci]
                color = get_color(v, vmin, vmax, cmap)
                rx = ML + ci * cw
                ry = MT + ri * ch_cell
                tip = _tip(f"({ylabels[ri]}, {xlabels[ci]})", f"Value: {v:g}")
                sw = lw if lw > 0 else 0
                parts.append(
                    f'<rect x="{rx:.2f}" y="{ry:.2f}" '
                    f'width="{cw:.2f}" height="{ch_cell:.2f}" '
                    f'fill="{color}" stroke="#0d1117" stroke-width="{sw}" '
                    f'data-tip="{tip}" style="cursor:default;"/>'
                )

                if annot and fmt is not None:
                    # Accept ".2g" or "{:.2g}" style format specs
                    if callable(fmt):
                        cell_txt = fmt(v)
                    elif isinstance(fmt, str):
                        spec = fmt if fmt.startswith("{") else f"{{:{fmt}}}"
                        try:
                            cell_txt = spec.format(v)
                        except (ValueError, KeyError):
                            cell_txt = f"{v:g}"
                    else:
                        cell_txt = f"{v:g}"

                    tc = get_text_color(color)
                    fs = max(8, min(13, int(min(cw, ch_cell) * 0.38)))
                    tx_p = rx + cw / 2
                    ty_p = ry + ch_cell / 2 + 4
                    parts.append(
                        f'<text x="{tx_p:.2f}" y="{ty_p:.2f}" '
                        f'text-anchor="middle" font-size="{fs}" '
                        f'fill="{tc}" font-weight="500" {_font}>'
                        f'{_escape(cell_txt)}</text>'
                    )

        # X-axis labels (above the grid)
        for ci, lbl in enumerate(xlabels):
            lx = ML + (ci + 0.5) * cw
            parts.append(
                f'<text x="{lx:.2f}" y="{MT-8}" text-anchor="middle" '
                f'font-size="10" {_lf} {_font}>{_escape(str(lbl))}</text>'
            )

        # Y-axis labels (left)
        for ri, lbl in enumerate(ylabels):
            ly = MT + (ri + 0.5) * ch_cell + 4
            parts.append(
                f'<text x="{ML-8}" y="{ly:.2f}" text-anchor="end" '
                f'font-size="10" {_lf} {_font}>{_escape(str(lbl))}</text>'
            )

        # Colour-scale bar
        if cbar:
            cb_x = W - MR + 10
            cb_y, cb_h, cb_w = MT, CH, 14

            pal_name = PALETTE_ALIASES.get(cmap, cmap)
            stops = PALETTES.get(pal_name, ["#c6e0f5", "#1a6aaa"])
            # Gradient: top = vmax (last stop), bottom = vmin (first stop)
            rev = list(reversed(stops))
            stop_strs = []
            for si, sc in enumerate(rev):
                off = int(100 * si / (len(rev) - 1)) if len(rev) > 1 else 0
                stop_strs.append(f'<stop offset="{off}%" stop-color="{sc}"/>')

            parts.append(
                f'<defs><linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">'
                + "".join(stop_strs)
                + f'</linearGradient></defs>'
            )
            parts.append(
                f'<rect x="{cb_x}" y="{cb_y}" width="{cb_w}" height="{cb_h}" '
                f'fill="url(#{grad_id})" rx="3"/>'
            )

            cb_ticks = nice_ticks(vmin, vmax, n=4)
            for ct in cb_ticks:
                if ct < vmin or ct > vmax:
                    continue
                frac = (ct - vmin) / (vmax - vmin)
                tick_y = cb_y + cb_h * (1 - frac)  # vmax at top
                parts.append(
                    f'<text x="{cb_x + cb_w + 4}" y="{tick_y + 3:.1f}" '
                    f'font-size="9" {_lf} {_font}>{ct:g}</text>'
                )

        parts.append('</svg></div>')
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Stacked bar renderer
    # ------------------------------------------------------------------

    def _render_stackedbar(self) -> str:
        chart = self._chart
        labels: list[str] = chart["labels"]
        series: list[dict] = chart["series"]
        colors: list[str] = chart["series_colors"]
        max_total: float = chart["max_total"]
        ch: int = chart["chart_height"]
        fmt = chart["fmt"]

        # Legend
        leg_items = []
        for s, c in zip(series, colors):
            leg_items.append(
                f'<div class="hp-legend-item">'
                f'<div class="hp-legend-dot" style="background:{c};border-radius:3px;"></div>'
                f'{_escape(s["name"])}'
                f'</div>'
            )
        legend_html = f'<div class="hp-legend">{"".join(leg_items)}</div>'

        cols: list[str] = []
        for j, lbl in enumerate(labels):
            total_val = sum(s["segments"][j]["value"] for s in series)
            # Recompute pixel height from fraction × current chart_height so
            # the columns rescale correctly when chart_height is overridden.
            total_px = int((total_val / max_total * ch)) if max_total else 0
            total_label = _fmt_value(total_val, fmt)

            # Segments: first series → bottom (flex-direction: column-reverse)
            seg_divs: list[str] = []
            for s, c in zip(series, colors):
                v = s["segments"][j]["value"]
                if v <= 0:
                    continue
                tip = _tip(s["name"], f"{lbl}: {_fmt_value(v, fmt)}")
                seg_divs.append(
                    f'<div class="hp-sbar-seg" style="flex:{v:.6g};background:{c};" '
                    f'data-tip="{tip}"></div>'
                )

            inner = "\n".join(seg_divs)
            cols.append(
                f'<div class="hp-bar-col">'
                f'<div class="hp-bar-value-label">{_escape(total_label)}</div>'
                f'<div class="hp-sbar-body" style="height:{total_px}px;">'
                f'{inner}'
                f'</div>'
                f'<div class="hp-bar-baseline"></div>'
                f'<div class="hp-bar-xlabel">{_escape(str(lbl))}</div>'
                f'</div>'
            )

        return (
            legend_html
            + f'<div class="hp-bar-outer">'
            f'<div class="hp-bar-chart" style="height:{ch}px;">'
            + "\n".join(cols)
            + f'</div></div>'
        )
