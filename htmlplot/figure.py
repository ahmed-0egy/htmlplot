"""Figure — top-level container that owns Axes and renders the final HTML."""

from __future__ import annotations

import math
import os
import tempfile
import webbrowser
from typing import Sequence

import html as _html

from .axes import Axes
from ._styles import get_css, render_page
from ._scripts import get_script

# Vertical overhead inside each card that isn't the chart itself (px).
# card-title font 10.5 px + margin-bottom 22 px ≈ 35 px title block
_CARD_PAD_V = 48     # top-padding(26) + bottom-padding(22)
_TITLE_H    = 35     # card-title block height when a title is present
_ROW_GAP    = 16     # gap between rows / columns in a grid


class Figure:
    """A figure holds one or more :class:`Axes` panels.

    Parameters
    ----------
    title:
        Page / window title (not the chart title).
    theme:
        ``"dark"`` (default) or ``"light"``.
    width:
        Maximum width of the figure container in pixels.
        Defaults to 820 px for single-column and auto-scales for grids.
    height:
        Total height of the figure container in pixels.  When set, charts
        inside each cell are automatically scaled to fit — mirroring
        matplotlib's ``figsize`` height behaviour.
    ncols:
        Number of columns in the subplot grid (set automatically by
        :func:`subplots`; rarely needed directly).
    """

    def __init__(
        self,
        title: str = "Figure",
        theme: str = "dark",
        width: int | None = None,
        height: int | None = None,
        ncols: int = 1,
    ) -> None:
        self.title = title
        self.theme = theme
        self.width = width
        self.height = height
        self._ncols = max(1, ncols)
        self._axes: list[Axes] = []

    # ------------------------------------------------------------------
    # Axes management
    # ------------------------------------------------------------------

    def add_axes(self) -> Axes:
        """Create and return a new :class:`Axes` attached to this figure."""
        ax = Axes(self)
        self._axes.append(ax)
        return ax

    # Convenience: let Figure proxy chart methods directly (single-panel use)
    def barh(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().barh(*args, **kwargs); return self

    def bar(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().bar(*args, **kwargs); return self

    def hist(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().hist(*args, **kwargs); return self

    def lineplot(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().lineplot(*args, **kwargs); return self

    def scatter(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().scatter(*args, **kwargs); return self

    def kmplot(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().kmplot(*args, **kwargs); return self

    def pie(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().pie(*args, **kwargs); return self

    def boxplot(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().boxplot(*args, **kwargs); return self

    def heatmap(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().heatmap(*args, **kwargs); return self

    def stackedbar(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().stackedbar(*args, **kwargs); return self

    def pie(self, *args, **kwargs) -> "Figure":
        ax = self._ensure_single_ax()
        ax.pie(*args, **kwargs)
        return self

    def monthbars(self, *args, **kwargs) -> "Figure":
        ax = self._ensure_single_ax()
        ax.monthbars(*args, **kwargs)
        return self

    def infobox(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().infobox(*args, **kwargs); return self

    def divider(self, *args, **kwargs) -> "Figure":
        self._ensure_single_ax().divider(*args, **kwargs); return self

    def set_title(self, title: str) -> "Figure":
        self._ensure_single_ax().set_title(title); return self

    def _ensure_single_ax(self) -> Axes:
        if not self._axes:
            return self.add_axes()
        return self._axes[-1]

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _cell_height(self) -> int | None:
        """Return per-cell pixel height when the figure has a fixed height."""
        if not self.height or not self._axes:
            return None
        nrows = max(1, math.ceil(len(self._axes) / self._ncols))
        total_gap = (nrows - 1) * _ROW_GAP
        return max(80, (self.height - total_gap) // nrows)

    def to_html(self, full_page: bool = True) -> str:
        """Return complete HTML.

        Parameters
        ----------
        full_page:
            If True (default), wrap in a ``<!DOCTYPE html>`` page.
            If False, return only the ``<div class="hp-figure">…</div>``
            fragment — suitable for Jupyter or embedding.
        """
        cell_h = self._cell_height()

<<<<<<< Updated upstream
        if self._ncols > 1 and self._axes:
            rows_html: list[str] = []
            # When height is constrained, rows share the figure height equally
            row_style = ' style="flex:1 1 0;min-height:0;"' if self.height else ""
            for i in range(0, len(self._axes), self._ncols):
                row_cards = "\n".join(
                    ax.to_html(cell_height=cell_h)
                    for ax in self._axes[i:i + self._ncols]
                )
                rows_html.append(
                    f'<div class="hp-figure-row"{row_style}>\n{row_cards}\n</div>'
                )
            inner = "\n".join(rows_html)
        else:
            inner = "\n".join(
                ax.to_html(cell_height=cell_h) for ax in self._axes
            )

        # ------ figure container style ------------------------------------
        # Width: explicit > auto for grid > CSS default
        if self.width:
            w = self.width
        elif self._ncols > 1:
            w = self._ncols * 440 + (self._ncols - 1) * _ROW_GAP
        else:
            w = 820

        fig_style = f"max-width:{w}px;"
        if self.height:
            # Make the figure a fixed-height flex column so rows can
            # share the space proportionally (like matplotlib's figsize)
            fig_style += f"height:{self.height}px;display:flex;flex-direction:column;"

        body = f'<div class="hp-figure" style="{fig_style}">\n{inner}\n</div>'
=======
        fig_heading = ""
        if (self.title and self.title != "Figure"
                and len(self._axes) > 1):
            fig_heading = (
                f'<div class="hp-card-title" style="margin-bottom:8px;">'
                f'{_html.escape(self.title)}</div>\n'
            )

        width_style = f"max-width:{self.width}px;" if self.width else ""
        body = (
            f'<div class="hp-figure" style="{width_style}">\n'
            f'{fig_heading}{cards}\n</div>'
        )
>>>>>>> Stashed changes

        if full_page:
            return render_page(self.title, body, self.theme, script=get_script())

        css = get_css(self.theme)
        return f"<style>\n{css}\n</style>\n{body}\n{get_script()}"

    def save(self, path: str) -> str:
        """Write a standalone HTML file and return the absolute path."""
        html = self.to_html(full_page=True)
        abs_path = os.path.abspath(path)
        with open(abs_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return abs_path

    def show(self) -> None:
        """Save to a temp file and open it in the default browser."""
        tmp = os.path.join(tempfile.gettempdir(), "_htmlplot_preview.html")
        self.save(tmp)
        webbrowser.open(f"file:///{tmp.replace(os.sep, '/')}")

    def _repr_html_(self) -> str:
        return self.to_html(full_page=False)

    def __repr__(self) -> str:
        n = len(self._axes)
        dims = (
            f"width={self.width}, height={self.height}"
            if self.width or self.height else "auto"
        )
        return f"<htmlplot.Figure title={self.title!r} axes={n} {dims}>"


# ---------------------------------------------------------------------------
# Module-level factory – matches matplotlib.pyplot.subplots()
# ---------------------------------------------------------------------------

def subplots(
    nrows: int = 1,
    ncols: int = 1,
    *,
    title: str = "Figure",
    theme: str = "dark",
    width: int | None = None,
    height: int | None = None,
    figsize: "tuple[int, int] | None" = None,
) -> "tuple[Figure, Axes] | tuple[Figure, list[Axes]] | tuple[Figure, list[list[Axes]]]":
    """Create a :class:`Figure` with a grid of :class:`Axes`.

    Mirrors ``matplotlib.pyplot.subplots`` — returns ``(fig, ax)`` for a
    single panel and ``(fig, axes_grid)`` for multi-panel layouts.

    Parameters
    ----------
    nrows, ncols:
        Grid dimensions.
    title:
        Page title.
    theme:
        ``"dark"`` (default) or ``"light"``.
    width:
        Maximum figure width in pixels.
    height:
        Total figure height in pixels.  Charts inside each cell are scaled
        to fill the allocated row height automatically.
    figsize:
        ``(width_px, height_px)`` shorthand — overrides *width* and *height*.
        Mirrors matplotlib's ``figsize`` (but in pixels instead of inches).

    Examples
    --------
    ::

        # Fixed 900 × 600 px dashboard with a 2 × 2 grid
        fig, axes = hp.subplots(2, 2, figsize=(900, 600), title="Dashboard")
        axes[0][0].bar(...)
        axes[0][1].pie(...)
        axes[1][0].hist(...)
        axes[1][1].barh(...)
        fig.show()
    """
    if figsize is not None:
        width, height = int(figsize[0]), int(figsize[1])

    fig = Figure(title=title, theme=theme, width=width, height=height, ncols=ncols)

    if nrows == 1 and ncols == 1:
<<<<<<< Updated upstream
        return fig, fig.add_axes()
=======
        ax = fig.add_axes()
        if title and title != "Figure":
            ax.set_title(title)
        return fig, ax
>>>>>>> Stashed changes

    grid: list[list[Axes]] = [
        [fig.add_axes() for _ in range(ncols)]
        for _ in range(nrows)
    ]

    if nrows == 1:
        return fig, grid[0]
    return fig, grid
