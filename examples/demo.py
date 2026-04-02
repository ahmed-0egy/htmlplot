"""Demo – exercises every htmlplot chart type with interactivity.

Charts covered
--------------
1.  Horizontal bar  (barh)          – palette, sort, infobox
2.  Vertical bar    (bar)           – light theme, sort
3.  Histogram       (hist)          – density, cumulative, weights, horizontal
4.  Line chart      (lineplot)      – multi-series, CI bands
5.  Scatter plot    (scatter)       – multi-series
6.  KM / step curve (kmplot)        – confidence intervals
7.  Pie chart       (pie)           – autopct, explode, shadow
8.  Donut chart     (pie + donut)   – 50 % hole
9.  Box plot        (boxplot)       – notch, means, fliers
10. Heatmap         (heatmap)       – annotations, colorbar, viridis
11. Stacked bar     (stackedbar)    – 100 % normalised
12. Subplots grid   (2 × 2)         – mixed chart types
"""

import sys
import os
import math
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import htmlplot as hp

random.seed(42)
out_dir = os.path.dirname(__file__)


# ---------------------------------------------------------------------------
# 1 – Horizontal bar chart
# ---------------------------------------------------------------------------
fig1, ax1 = hp.subplots(title="Mortality Chart")
ax1.barh(
    ["Turkmenistan", "Afghanistan", "Pakistan", "Iran"],
    [12.93, 14.61, 26.32, 44.55],
    title="Country mortality comparison",
    fmt="{:.1f}%",
    palette="gyr",
)
ax1.infobox(
    "Turkmenistan shows the <strong>lowest mortality ratio</strong> "
    "among all candidate countries."
)


# ---------------------------------------------------------------------------
# 2 – Vertical bar chart  (light theme)
# ---------------------------------------------------------------------------
fig2, ax2 = hp.subplots(title="GDP per Capita", theme="light")
ax2.bar(
    ["Germany", "France", "Spain", "Italy", "Poland"],
    [48_000, 43_000, 32_000, 35_000, 19_000],
    title="GDP per capita (USD, 2024)",
    fmt="${:,.0f}",
    palette="blues",
    sort=True,
)
ax2.infobox("Germany leads with a GDP per capita of <strong>$48,000</strong>.")


# ---------------------------------------------------------------------------
# 3a – Histogram  (density + cumulative)
# ---------------------------------------------------------------------------
heights = [random.gauss(170, 10) for _ in range(500)]

fig3a, ax3a = hp.subplots(title="Height Distribution – Density")
ax3a.hist(
    heights,
    bins=15,
    title="Height distribution – PDF (n=500)",
    density=True,
    palette="teals",
)
ax3a.infobox("Bars represent probability density; bin areas sum to 1.")

fig3b, ax3b = hp.subplots(title="Height Distribution – Cumulative")
ax3b.hist(
    heights,
    bins=15,
    title="Cumulative histogram",
    cumulative=True,
    fmt="{:.0f}",
    palette="blues",
)

# 3c – Horizontal histogram with weights
fig3c, ax3c = hp.subplots(title="Weighted Histogram")
w_data = [random.gauss(0, 1) for _ in range(300)]
w_weights = [abs(v) + 0.1 for v in w_data]   # heavier weight for extreme values
ax3c.hist(
    w_data, bins=12,
    title="Weighted horizontal histogram",
    weights=w_weights,
    orientation="horizontal",
    palette="warm",
)


# ---------------------------------------------------------------------------
# 4 – Line chart  (multi-series with CI)
# ---------------------------------------------------------------------------
days = list(range(0, 91, 5))
trend_a = [100 * math.exp(-0.008 * d) + random.gauss(0, 1.5) for d in days]
trend_b = [100 * math.exp(-0.018 * d) + random.gauss(0, 1.5) for d in days]

fig4, ax4 = hp.subplots(title="Trend Comparison")
ax4.lineplot(
    [days, days],
    [trend_a, trend_b],
    title="Recovery index over time",
    labels=["Low-risk cohort", "High-risk cohort"],
    colors=["#2ed090", "#f0604a"],
    xlabel="Day",
    ylabel="Index",
)
ax4.infobox("High-risk cohort declines <strong>2× faster</strong> than low-risk.")


# ---------------------------------------------------------------------------
# 5 – Scatter plot  (multi-series)
# ---------------------------------------------------------------------------
def cluster(cx, cy, n=50, spread=8):
    return (
        [cx + random.gauss(0, spread) for _ in range(n)],
        [cy + random.gauss(0, spread) for _ in range(n)],
    )

xa, ya = cluster(30, 60)
xb, yb = cluster(70, 40)

fig5, ax5 = hp.subplots(title="Scatter")
ax5.scatter(
    [xa, xb], [ya, yb],
    title="Cluster separation",
    labels=["Cluster A", "Cluster B"],
    colors=["#4a82c8", "#f0a030"],
    xlabel="Feature 1", ylabel="Feature 2",
)


# ---------------------------------------------------------------------------
# 6 – KM / survival curves
# ---------------------------------------------------------------------------
times_uz  = [0, 10, 20, 30, 60, 90, 180, 365, 540, 730]
surv_uz   = [1.0, 0.88, 0.78, 0.70, 0.62, 0.57, 0.48, 0.35, 0.25, 0.17]
times_tk  = [0, 15, 30, 60, 90, 180, 365, 540, 730]
surv_tk   = [1.0, 0.94, 0.90, 0.84, 0.80, 0.72, 0.60, 0.50, 0.40]

ci_uz = ([max(0, s - 0.07) for s in surv_uz], [min(1, s + 0.07) for s in surv_uz])
ci_tk = ([max(0, s - 0.06) for s in surv_tk], [min(1, s + 0.06) for s in surv_tk])

fig6, ax6 = hp.subplots(title="Survival Curve")
ax6.kmplot(
    [times_uz, times_tk], [surv_uz, surv_tk],
    title="Kaplan\u2013Meier survival curve",
    labels=["Current sites (Uzbekistan)", "Simulated (Turkmenistan)"],
    colors=["#f0604a", "#2ed090"],
    ci=[ci_uz, ci_tk],
    xlabel="Days", ylabel="Survival probability",
)
ax6.infobox(
    "30-day mortality: <strong>~30%</strong> &nbsp;&middot;&nbsp; "
    "2-year: <strong>~83%</strong>"
)


# ---------------------------------------------------------------------------
# 7 – Pie chart  (autopct + explode + shadow)
# ---------------------------------------------------------------------------
fig7, ax7 = hp.subplots(title="Market Share")
ax7.pie(
    [35, 28, 18, 12, 7],
    labels=["Product A", "Product B", "Product C", "Product D", "Other"],
    title="Market share by product",
    autopct="%.1f%%",
    explode=[0.06, 0, 0, 0, 0],    # pop out the leading slice
    shadow=True,
    startangle=90,
)


# ---------------------------------------------------------------------------
# 8 – Donut chart
# ---------------------------------------------------------------------------
fig8, ax8 = hp.subplots(title="Budget Allocation")
ax8.pie(
    [40, 25, 20, 15],
    labels=["R&D", "Marketing", "Operations", "HR"],
    title="Annual budget allocation",
    donut=0.55,
    autopct="%.0f%%",
    colors=["#4a82c8", "#2ed090", "#f0a030", "#b060f0"],
)


# ---------------------------------------------------------------------------
# 9 – Box plot  (notch, means, fliers)
# ---------------------------------------------------------------------------
random.seed(7)

def make_group(mu, sigma, n, skew=0):
    base = [random.gauss(mu, sigma) for _ in range(n)]
    # Add a few outliers
    base += [mu + skew + random.uniform(2.5, 4.0) * sigma for _ in range(3)]
    return base

groups_data = [
    make_group(55, 12, 60, skew=10),
    make_group(72, 9,  60),
    make_group(68, 15, 60, skew=-8),
    make_group(80, 7,  60),
]

fig9, ax9 = hp.subplots(title="Score Distribution")
ax9.boxplot(
    groups_data,
    labels=["Control", "Treatment A", "Treatment B", "Treatment C"],
    title="Score distribution by group",
    notch=True,
    showmeans=True,
    meanline=False,
    patch_artist=True,
    ylabel="Score",
)
ax9.infobox(
    "Notches indicate 95 % CI around the median. "
    "Triangles mark the mean; open circles are outliers."
)


# ---------------------------------------------------------------------------
# 10 – Heatmap  (correlation matrix, viridis)
# ---------------------------------------------------------------------------
# Simulated correlation matrix (symmetric, diagonal = 1)
features = ["Age", "BMI", "SBP", "Glucose", "CRP", "HbA1c"]
nf = len(features)
corr = [[1.0] * nf for _ in range(nf)]
for i in range(nf):
    for j in range(nf):
        if i == j:
            corr[i][j] = 1.0
        else:
            v = random.uniform(-0.7, 0.9)
            corr[i][j] = round(v, 2)
            corr[j][i] = round(v, 2)

fig10, ax10 = hp.subplots(title="Correlation Matrix")
ax10.heatmap(
    corr,
    xlabels=features,
    ylabels=features,
    title="Feature correlation matrix",
    fmt=".2f",
    cmap="viridis",
    vmin=-1.0, vmax=1.0,
    linewidths=2,
)


# ---------------------------------------------------------------------------
# 11 – Stacked bar  (absolute + 100 % normalised side-by-side)
# ---------------------------------------------------------------------------
quarters = ["Q1", "Q2", "Q3", "Q4"]
revenue = {
    "Product A": [120, 145, 160, 175],
    "Product B": [80,  95, 110, 130],
    "Product C": [45,  55,  60,  70],
}

fig11a, ax11a = hp.subplots(title="Revenue by Product (Absolute)")
ax11a.stackedbar(
    quarters, revenue,
    title="Quarterly revenue (absolute, $k)",
    fmt="${:.0f}k",
)

fig11b, ax11b = hp.subplots(title="Revenue by Product (Normalised)")
ax11b.stackedbar(
    quarters, revenue,
    title="Quarterly revenue share (100 % stacked)",
    normalized=True,
    fmt="{:.1f}%",
)


# ---------------------------------------------------------------------------
# 12 – Subplots grid  (2 × 2)
# ---------------------------------------------------------------------------
fig12, axes12 = hp.subplots(nrows=2, ncols=2, title="Dashboard Overview")

# Top-left: bar chart
axes12[0][0].bar(
    ["Mon", "Tue", "Wed", "Thu", "Fri"],
    [42, 68, 55, 73, 61],
    title="Daily active users",
    palette="blues",
)

# Top-right: pie chart
axes12[0][1].pie(
    [44, 32, 24],
    labels=["Desktop", "Mobile", "Tablet"],
    title="Device breakdown",
    autopct="%.0f%%",
    donut=0.4,
)

# Bottom-left: histogram
axes12[1][0].hist(
    [random.gauss(0, 1) for _ in range(300)],
    bins=14,
    title="Response-time distribution",
    density=True,
    palette="purples",
)

# Bottom-right: horizontal bar
axes12[1][1].barh(
    ["EMEA", "AMER", "APAC", "LATAM"],
    [38, 29, 24, 9],
    title="Revenue by region",
    fmt="{:.0f}%",
    palette="ryg",
)


# ---------------------------------------------------------------------------
# Save all figures
# ---------------------------------------------------------------------------
figures = [
    (fig1,  "demo_01_barh"),
    (fig2,  "demo_02_bar_light"),
    (fig3a, "demo_03a_hist_density"),
    (fig3b, "demo_03b_hist_cumulative"),
    (fig3c, "demo_03c_hist_weighted_horiz"),
    (fig4,  "demo_04_lineplot"),
    (fig5,  "demo_05_scatter"),
    (fig6,  "demo_06_kmplot"),
    (fig7,  "demo_07_pie"),
    (fig8,  "demo_08_donut"),
    (fig9,  "demo_09_boxplot"),
    (fig10, "demo_10_heatmap"),
    (fig11a,"demo_11a_stackedbar"),
    (fig11b,"demo_11b_stackedbar_normalised"),
    (fig12, "demo_12_subplots_grid"),
]

for fig, name in figures:
    path = fig.save(os.path.join(out_dir, f"{name}.html"))
    print(f"Saved: {path}")

# Open the most feature-rich demo in the browser
fig12.show()
