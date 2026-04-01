"""Demo – shows all htmlplot chart types with interactivity.

All charts are interactive:
  - Bar charts  → hover any bar to see label + value tooltip
  - Line charts → hover any data point to see series, x, y
  - Scatter     → hover any point to see series, x, y
  - Step/KM     → hover any event point to see series, time, survival
"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import htmlplot as hp

random.seed(42)

# ---------------------------------------------------------------------------
# Example 1 – Horizontal bar chart  (dark, gyr palette)
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
    "among all candidate countries and acts as a natural migratory gateway."
)

# ---------------------------------------------------------------------------
# Example 2 – Vertical bar chart  (light, blues palette)
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
# Example 3 – Histogram  (dark)
# ---------------------------------------------------------------------------
data = [random.gauss(170, 10) for _ in range(400)]

fig3, ax3 = hp.subplots(title="Height Distribution")
ax3.hist(
    data,
    bins=15,
    title="Height distribution (synthetic, n=400)",
    fmt="{:.0f}",
    palette="teals",
)
ax3.infobox("Heights drawn from N(170, 10).")

# ---------------------------------------------------------------------------
# Example 4 – Line chart  (multi-series, dark)
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
# Example 5 – Scatter plot  (multi-series, dark)
# ---------------------------------------------------------------------------
def make_cluster(cx, cy, n=40, spread=8):
    return (
        [cx + random.gauss(0, spread) for _ in range(n)],
        [cy + random.gauss(0, spread) for _ in range(n)],
    )

xa, ya = make_cluster(30, 60)
xb, xb2 = make_cluster(70, 40)

fig5, ax5 = hp.subplots(title="Scatter")
ax5.scatter(
    [xa, xb],
    [ya, xb2],
    title="Cluster separation",
    labels=["Cluster A", "Cluster B"],
    colors=["#4a82c8", "#f0a030"],
    xlabel="Feature 1",
    ylabel="Feature 2",
)
ax5.infobox("Two clusters separated along both axes.")

# ---------------------------------------------------------------------------
# Example 6 – Step / KM-style line chart  (pre-computed survival data)
# ---------------------------------------------------------------------------
# You compute the curve however you like; htmlplot just renders it.
times_uz  = [0, 10, 20, 30, 60, 90, 180, 365, 540, 730]
surv_uz   = [1.0, 0.88, 0.78, 0.70, 0.62, 0.57, 0.48, 0.35, 0.25, 0.17]

times_tk  = [0, 15, 30, 60, 90, 180, 365, 540, 730]
surv_tk   = [1.0, 0.94, 0.90, 0.84, 0.80, 0.72, 0.60, 0.50, 0.40]

# Optional pre-computed confidence intervals
ci_uz = (
    [max(0, s - 0.07) for s in surv_uz],
    [min(1, s + 0.07) for s in surv_uz],
)
ci_tk = (
    [max(0, s - 0.06) for s in surv_tk],
    [min(1, s + 0.06) for s in surv_tk],
)

fig6, ax6 = hp.subplots(title="Survival Curve")
ax6.kmplot(
    [times_uz, times_tk],
    [surv_uz,  surv_tk],
    title="Kaplan\u2013Meier survival curve",
    labels=["Current sites (Uzbekistan)", "Simulated (Turkmenistan)"],
    colors=["#f0604a", "#2ed090"],
    ci=[ci_uz, ci_tk],
    xlabel="Days",
    ylabel="Survival probability",
)
ax6.infobox(
    "30-day mortality: <strong>~30%</strong> &nbsp;&middot;&nbsp; "
    "90-day: <strong>~43%</strong> &nbsp;&middot;&nbsp; "
    "2-year: <strong>~83%</strong>"
)

# ---------------------------------------------------------------------------
# Save all figures
# ---------------------------------------------------------------------------
out_dir = os.path.dirname(__file__)

for i, fig in enumerate([fig1, fig2, fig3, fig4, fig5, fig6], 1):
    path = fig.save(os.path.join(out_dir, f"demo_{i}.html"))
    print(f"Saved: {path}")

fig6.show()
