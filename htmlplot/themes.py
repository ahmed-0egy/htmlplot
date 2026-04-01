"""Color palettes and utilities for htmlplot."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Named palettes – each is a list of hex stops (low → high)
# ---------------------------------------------------------------------------
PALETTES: dict[str, list[str]] = {
    # diverging – most used for "higher = worse"
    "gyr":     ["#2ed090", "#f0d040", "#f0604a"],   # green → yellow → red
    "ryg":     ["#f0604a", "#f0d040", "#2ed090"],   # red → yellow → green
    # sequential
    "blues":   ["#c6e0f5", "#1a6aaa"],
    "greens":  ["#b8f0d4", "#0a7040"],
    "reds":    ["#fce0d8", "#c02010"],
    "purples": ["#e4d4f8", "#5a18b0"],
    "oranges": ["#fde8c0", "#c86000"],
    "teals":   ["#c0f0ec", "#107880"],
    # multi-stop
    "viridis": ["#440154", "#31688e", "#35b779", "#fde725"],
    "plasma":  ["#0d0887", "#cc4778", "#f89441", "#f0f921"],
    "cool":    ["#6ee2f5", "#6454f0"],
    "warm":    ["#f0a070", "#f03060"],
    # monochrome
    "mono":    ["#2a3040", "#c0cce0"],
}

PALETTE_ALIASES = {
    "green_red": "gyr",
    "red_green": "ryg",
}


def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rgb_to_hex(r: float, g: float, b: float) -> str:
    return f"#{int(round(r)):02x}{int(round(g)):02x}{int(round(b)):02x}"


def _lerp_rgb(
    c1: tuple[float, float, float],
    c2: tuple[float, float, float],
    t: float,
) -> tuple[float, float, float]:
    return (
        c1[0] + (c2[0] - c1[0]) * t,
        c1[1] + (c2[1] - c1[1]) * t,
        c1[2] + (c2[2] - c1[2]) * t,
    )


def get_color(value: float, vmin: float, vmax: float, palette: str = "gyr") -> str:
    """Return a hex color for *value* within [vmin, vmax] using *palette*."""
    palette = PALETTE_ALIASES.get(palette, palette)
    stops = PALETTES.get(palette)
    if stops is None:
        # treat as a single solid hex colour
        return palette if palette.startswith("#") else "#4a82c8"

    t = (value - vmin) / (vmax - vmin) if vmax != vmin else 0.5
    t = max(0.0, min(1.0, t))

    rgb_stops = [_hex_to_rgb(c) for c in stops]
    n = len(rgb_stops) - 1
    scaled = t * n
    i = min(int(scaled), n - 1)
    local_t = scaled - i
    rgb = _lerp_rgb(rgb_stops[i], rgb_stops[i + 1], local_t)
    return _rgb_to_hex(*rgb)


def get_text_color(bg_hex: str, threshold: float = 0.45) -> str:
    """Return a dark or light text colour that contrasts with *bg_hex*."""
    r, g, b = _hex_to_rgb(bg_hex)
    # perceptual luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#0a1018" if luminance > threshold else "#f0f4f8"


def resolve_colors(
    values: list[float],
    palette: str | list[str] | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
) -> list[str]:
    """
    Return a list of hex colours for *values*.

    - If *palette* is a list of hex strings, cycle through them.
    - If *palette* is a named palette string, interpolate based on value.
    - If *palette* is None, default to "gyr".
    """
    if palette is None:
        palette = "gyr"

    if isinstance(palette, list):
        return [palette[i % len(palette)] for i in range(len(values))]

    _vmin = vmin if vmin is not None else min(values)
    _vmax = vmax if vmax is not None else max(values)
    return [get_color(v, _vmin, _vmax, palette) for v in values]
