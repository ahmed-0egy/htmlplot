"""Axes — the chart surface for htmlplot.

Each Axes instance renders one card block of HTML.  Multiple Axes live
inside a Figure (one per row, or arranged in a grid).
"""

from __future__ import annotations

import html
import math
from typing import TYPE_CHECKING, Callable, Sequence

from .themes import get_text_color, resolve_colors
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
            bar_height_px = int((value / _max * height)) if _max else 0
            bars.append({
                "label": label,
                "value": value,
                "bar_height_px": bar_height_px,
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
    ) -> "Axes":
        """Histogram – mirrors ``matplotlib.Axes.hist``.

        Parameters
        ----------
        data:
            Raw numeric observations.
        bins:
            Number of equal-width bins, **or** an explicit list of bin edges.
        density:
            If True, normalise bars so their areas sum to 1 (like a PDF).
        """
        if title:
            self._title = title

        data = [float(x) for x in data]
        _min_d, _max_d = min(data), max(data)

        # Build bin edges
        if isinstance(bins, int):
            n_bins = bins
            step = (_max_d - _min_d) / n_bins if _max_d != _min_d else 1
            edges = [_min_d + step * i for i in range(n_bins + 1)]
        else:
            edges = list(bins)
            n_bins = len(edges) - 1

        # Count
        counts = [0] * n_bins
        for x in data:
            for i in range(n_bins):
                if edges[i] <= x < edges[i + 1]:
                    counts[i] += 1
                    break
            else:
                if x == edges[-1]:
                    counts[-1] += 1

        if density:
            total = sum(counts)
            bin_widths = [edges[i + 1] - edges[i] for i in range(n_bins)]
            counts = [c / (total * bw) if total else 0
                      for c, bw in zip(counts, bin_widths)]

        # Build x-axis labels: midpoints
        labels = [f"{(edges[i] + edges[i+1]) / 2:.3g}" for i in range(n_bins)]

        # Delegate to bar()
        self.bar(labels, counts, title=None, fmt=fmt,
                 palette=colors if colors else palette,
                 height=height)
        # Override chart type so to_html can customise if needed
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

    def to_html(self) -> str:
        parts: list[str] = []

        if self._title:
            parts.append(
                f'<div class="hp-card-title">{_escape(self._title)}</div>'
            )

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

        for ann_type, ann_data in self._annotations:
            if ann_type == "infobox":
                parts.append(
                    f'<div class="hp-info-box">{ann_data}</div>'
                )
            elif ann_type == "divider":
                parts.append('<div class="hp-divider"></div>')

        inner = "\n".join(parts)
        return f'<div class="hp-card">\n{inner}\n</div>'

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
            cols.append(
                f'<div class="hp-bar-col" data-tip="{tip}">'
                f'<div class="hp-bar-value-label">{_escape(b["value_label"])}</div>'
                f'<div class="hp-bar-body" '
                f'style="height:{b["bar_height_px"]}px;background:{b["color"]};"></div>'
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
        # More left margin when ylabel is present
        ML = 52 if ylabel else 28
        MR, MT = 18, 12
        MB = 40 if xlabel else 24
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
            f'style="display:block;overflow:visible;">'
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
                f'<text x="{ML + CW / 2:.1f}" y="{H - 4}" '
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
