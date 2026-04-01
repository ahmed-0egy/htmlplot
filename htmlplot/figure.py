"""Figure — top-level container that owns Axes and renders the final HTML."""

from __future__ import annotations

import os
import tempfile
import webbrowser
from typing import Sequence

from .axes import Axes
from ._styles import get_css, render_page
from ._scripts import get_script


class Figure:
    """A figure holds one or more :class:`Axes` panels arranged vertically.

    Usage::

        fig, ax = hp.subplots(title="My Chart")
        ax.barh(labels, values)
        fig.show()          # open in browser
        fig.save("out.html")
        html = fig.to_html()        # embed in a larger page
        # In Jupyter: just call  fig  at the end of a cell
    """

    def __init__(
        self,
        title: str = "Figure",
        theme: str = "dark",
        width: int | None = None,
    ) -> None:
        self.title = title
        self.theme = theme          # "dark" | "light"
        self.width = width          # optional max-width override (px)
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
        ax = self._ensure_single_ax()
        ax.barh(*args, **kwargs)
        return self

    def bar(self, *args, **kwargs) -> "Figure":
        ax = self._ensure_single_ax()
        ax.bar(*args, **kwargs)
        return self

    def hist(self, *args, **kwargs) -> "Figure":
        ax = self._ensure_single_ax()
        ax.hist(*args, **kwargs)
        return self

    def lineplot(self, *args, **kwargs) -> "Figure":
        ax = self._ensure_single_ax()
        ax.lineplot(*args, **kwargs)
        return self

    def scatter(self, *args, **kwargs) -> "Figure":
        ax = self._ensure_single_ax()
        ax.scatter(*args, **kwargs)
        return self

    def kmplot(self, *args, **kwargs) -> "Figure":
        ax = self._ensure_single_ax()
        ax.kmplot(*args, **kwargs)
        return self

    def infobox(self, *args, **kwargs) -> "Figure":
        ax = self._ensure_single_ax()
        ax.infobox(*args, **kwargs)
        return self

    def set_title(self, title: str) -> "Figure":
        ax = self._ensure_single_ax()
        ax.set_title(title)
        return self

    def _ensure_single_ax(self) -> Axes:
        if not self._axes:
            return self.add_axes()
        return self._axes[-1]

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def to_html(self, full_page: bool = True) -> str:
        """Return complete HTML.

        Parameters
        ----------
        full_page:
            If True (default), wrap in a ``<!DOCTYPE html>`` page.
            If False, return only the ``<div class="hp-figure">…</div>``
            block — suitable for embedding in a larger HTML document.
            Either way the required CSS is included.
        """
        cards = "\n".join(ax.to_html() for ax in self._axes)

        width_style = f"max-width:{self.width}px;" if self.width else ""
        body = (
            f'<div class="hp-figure" style="{width_style}">\n{cards}\n</div>'
        )

        if full_page:
            return render_page(self.title, body, self.theme, script=get_script())

        # embed mode: inline the CSS + script alongside the figure block
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

    # Jupyter / IPython rich display
    def _repr_html_(self) -> str:
        return self.to_html(full_page=False)

    def __repr__(self) -> str:
        n = len(self._axes)
        return f"<htmlplot.Figure title={self.title!r} axes={n}>"


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
) -> "tuple[Figure, Axes] | tuple[Figure, list[Axes]] | tuple[Figure, list[list[Axes]]]":
    """Create a :class:`Figure` with a grid of :class:`Axes`.

    Mirrors ``matplotlib.pyplot.subplots``:

    - ``nrows=1, ncols=1``  → returns ``(fig, ax)``
    - ``nrows=1, ncols>1``  → returns ``(fig, [ax1, ax2, …])``
    - ``nrows>1``           → returns ``(fig, [[ax00, ax01], [ax10, …], …])``
    """
    fig = Figure(title=title, theme=theme, width=width)

    if nrows == 1 and ncols == 1:
        ax = fig.add_axes()
        return fig, ax

    grid: list[list[Axes]] = [
        [fig.add_axes() for _ in range(ncols)]
        for _ in range(nrows)
    ]

    if nrows == 1:
        return fig, grid[0]
    return fig, grid
