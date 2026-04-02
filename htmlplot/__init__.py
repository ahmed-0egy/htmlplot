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
``barh``        horizontal bar chart
``bar``         vertical bar chart
``hist``        histogram  (density, cumulative, weights, orientation)
``lineplot``    multi-series line chart with optional CI bands
``scatter``     multi-series scatter plot
``kmplot``      Kaplan-Meier step-function survival curves
``pie``         pie / donut chart
``boxplot``     box-and-whisker plot (notch, fliers, means)
``heatmap``     2-D colour-mapped grid with optional annotations & colorbar
``stackedbar``  stacked vertical bar chart (supports 100 % normalisation)

Subplots / grid layout
----------------------
::

    fig, axes = hp.subplots(nrows=2, ncols=2, title="Dashboard")
    axes[0][0].bar(...)
    axes[0][1].pie(...)
    axes[1][0].boxplot(...)
    axes[1][1].heatmap(...)
    fig.show()

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
