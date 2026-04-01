"""htmlplot — matplotlib-style API that renders beautiful HTML charts.

Quick-start
-----------
::

    import htmlplot as hp

    fig, ax = hp.subplots(title="Country mortality comparison")
    ax.barh(
        ["Turkmenistan", "Afghanistan", "Pakistan", "Iran"],
        [12.93, 14.61, 26.32, 44.55],
        fmt="{:.1f}%",
    )
    ax.infobox(
        "Turkmenistan shows the <strong>lowest mortality ratio</strong> "
        "among all candidate countries."
    )
    fig.show()          # opens browser
    fig.save("chart.html")
    html = fig.to_html()   # embed anywhere

Available charts
----------------
``barh``   horizontal bar chart
``bar``    vertical bar chart
``hist``   histogram

Themes
------
Pass ``theme="dark"`` (default) or ``theme="light"`` to :func:`subplots`
or :class:`Figure`.
"""

from .figure import Figure, subplots
from .axes import Axes
from .themes import PALETTES

__version__ = "0.1.0"
__all__ = ["Figure", "Axes", "subplots", "PALETTES"]
