"""Embedded CSS for htmlplot – dark and light themes."""

_DARK_CSS = """\
/* === htmlplot – dark theme ============================================= */
.hp-figure {
  font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 820px;
  margin: 0 auto;
  color: #e0e6f0;
}

/* Card ------------------------------------------------------------------ */
.hp-card {
  background: #161b27;
  border: 1px solid #232a38;
  border-radius: 14px;
  padding: 26px 30px 22px;
  box-shadow: 0 6px 32px rgba(0, 0, 0, 0.45);
}

.hp-card-title {
  font-size: 10.5px;
  font-weight: 700;
  color: #5a6a80;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  margin-bottom: 22px;
}

/* Horizontal bar chart -------------------------------------------------- */
.hp-barh-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 9px;
}
.hp-barh-row:last-of-type { margin-bottom: 0; }

.hp-barh-label {
  width: 150px;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 500;
  color: #a0aec0;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hp-barh-track {
  flex: 1;
  background: #1e2535;
  border-radius: 6px;
  height: 30px;
  overflow: hidden;
}

.hp-barh-fill {
  height: 100%;
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding: 0 11px;
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.3px;
  min-width: 46px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

/* Vertical bar chart ---------------------------------------------------- */
.hp-bar-outer {
  width: 100%;
}

.hp-bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 0 4px;
}

.hp-bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}

.hp-bar-value-label {
  font-size: 11px;
  font-weight: 600;
  color: #7a8a9c;
  margin-bottom: 5px;
  text-align: center;
}

.hp-bar-body {
  width: 100%;
  border-radius: 5px 5px 0 0;
  min-height: 4px;
  transition: height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.hp-bar-baseline {
  width: 100%;
  height: 1px;
  background: #232a38;
  margin-top: 0;
}

.hp-bar-xlabel {
  font-size: 11px;
  font-weight: 500;
  color: #5a6a80;
  margin-top: 7px;
  text-align: center;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Histogram ------------------------------------------------------------- */
/* re-uses .hp-bar-* styles — no extra rules needed */

/* Info box -------------------------------------------------------------- */
.hp-info-box {
  margin-top: 20px;
  padding: 12px 16px;
  background: rgba(74, 130, 200, 0.07);
  border-left: 3px solid #4a82c8;
  border-radius: 0 7px 7px 0;
  font-size: 12.5px;
  color: #7a8ea8;
  line-height: 1.65;
}

.hp-info-box strong {
  color: #b8cce0;
  font-weight: 600;
}

/* Divider --------------------------------------------------------------- */
.hp-divider {
  width: 100%;
  height: 1px;
  background: #232a38;
  margin: 14px 0;
}

/* Legend ---------------------------------------------------------------- */
.hp-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
  margin-bottom: 14px;
}

.hp-legend-item {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 500;
  color: #8090a4;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.hp-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* SVG chart wrap -------------------------------------------------------- */
.hp-svg-wrap {
  width: 100%;
  overflow: hidden;
}

/* Tooltip --------------------------------------------------------------- */
.hp-tip {
  position: fixed;
  z-index: 99999;
  pointer-events: none;
  display: none;
  background: #111620;
  border: 1px solid #2a3648;
  border-radius: 8px;
  padding: 8px 13px;
  font-size: 12px;
  line-height: 1.6;
  color: #c8d8e8;
  white-space: nowrap;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.55);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.hp-tip b {
  color: #e8f2fc;
  font-weight: 600;
  display: block;
  margin-bottom: 1px;
}

/* Hover effects --------------------------------------------------------- */
.hp-barh-fill {
  transition: filter 0.12s;
}
.hp-barh-track:hover .hp-barh-fill {
  filter: brightness(1.2);
  cursor: default;
}

.hp-bar-body {
  transition: filter 0.12s;
}
.hp-bar-col:hover .hp-bar-body {
  filter: brightness(1.2);
  cursor: default;
}

.hp-barh-track { cursor: default; }
.hp-bar-col    { cursor: default; }

/* Figure grid layout ---------------------------------------------------- */
.hp-figure-row {
  display: flex;
  gap: 16px;
}

.hp-figure-row .hp-card {
  flex: 1;
  min-width: 0;
}

/* Stacked bar chart ----------------------------------------------------- */
.hp-sbar-body {
  width: 100%;
  display: flex;
  flex-direction: column-reverse;
  overflow: hidden;
  border-radius: 5px 5px 0 0;
}

.hp-sbar-seg {
  min-height: 2px;
  transition: filter 0.12s;
}

.hp-sbar-seg:hover {
  filter: brightness(1.18);
  cursor: default;
}
"""

_LIGHT_CSS = """\
/* === htmlplot – light theme ============================================ */
.hp-figure {
  font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 820px;
  margin: 0 auto;
  color: #1a2030;
}

.hp-card {
  background: #ffffff;
  border: 1px solid #e4e8f0;
  border-radius: 14px;
  padding: 26px 30px 22px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.07);
}

.hp-card-title {
  font-size: 10.5px;
  font-weight: 700;
  color: #9aabbc;
  letter-spacing: 1.2px;
  text-transform: uppercase;
  margin-bottom: 22px;
}

.hp-barh-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 9px;
}
.hp-barh-row:last-of-type { margin-bottom: 0; }

.hp-barh-label {
  width: 150px;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 500;
  color: #4a5568;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hp-barh-track {
  flex: 1;
  background: #f0f4f8;
  border-radius: 6px;
  height: 30px;
  overflow: hidden;
}

.hp-barh-fill {
  height: 100%;
  border-radius: 6px;
  display: flex;
  align-items: center;
  padding: 0 11px;
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.3px;
  min-width: 46px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
}

.hp-bar-outer { width: 100%; }

.hp-bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 0 4px;
}

.hp-bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}

.hp-bar-value-label {
  font-size: 11px;
  font-weight: 600;
  color: #8090a4;
  margin-bottom: 5px;
  text-align: center;
}

.hp-bar-body {
  width: 100%;
  border-radius: 5px 5px 0 0;
  min-height: 4px;
}

.hp-bar-baseline {
  width: 100%;
  height: 1px;
  background: #e0e8f0;
  margin-top: 0;
}

.hp-bar-xlabel {
  font-size: 11px;
  font-weight: 500;
  color: #9aabbc;
  margin-top: 7px;
  text-align: center;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hp-info-box {
  margin-top: 20px;
  padding: 12px 16px;
  background: rgba(74, 130, 200, 0.06);
  border-left: 3px solid #4a82c8;
  border-radius: 0 7px 7px 0;
  font-size: 12.5px;
  color: #6a7a90;
  line-height: 1.65;
}

.hp-info-box strong {
  color: #2a3a50;
  font-weight: 600;
}

.hp-divider {
  width: 100%;
  height: 1px;
  background: #e4e8f0;
  margin: 14px 0;
}

/* Legend ---------------------------------------------------------------- */
.hp-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
  margin-bottom: 14px;
}

.hp-legend-item {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  font-weight: 500;
  color: #6a7a90;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.hp-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* SVG chart wrap -------------------------------------------------------- */
.hp-svg-wrap {
  width: 100%;
  overflow: hidden;
}

/* Tooltip --------------------------------------------------------------- */
.hp-tip {
  position: fixed;
  z-index: 99999;
  pointer-events: none;
  display: none;
  background: #ffffff;
  border: 1px solid #d0d8e8;
  border-radius: 8px;
  padding: 8px 13px;
  font-size: 12px;
  line-height: 1.6;
  color: #2a3a50;
  white-space: nowrap;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
  font-family: 'Segoe UI', system-ui, sans-serif;
}

.hp-tip b {
  color: #1a2a40;
  font-weight: 600;
  display: block;
  margin-bottom: 1px;
}

/* Hover effects --------------------------------------------------------- */
.hp-barh-fill {
  transition: filter 0.12s;
}
.hp-barh-track:hover .hp-barh-fill {
  filter: brightness(0.92);
  cursor: default;
}

.hp-bar-body {
  transition: filter 0.12s;
}
.hp-bar-col:hover .hp-bar-body {
  filter: brightness(0.92);
  cursor: default;
}

.hp-barh-track { cursor: default; }
.hp-bar-col    { cursor: default; }

/* Figure grid layout ---------------------------------------------------- */
.hp-figure-row {
  display: flex;
  gap: 16px;
}

.hp-figure-row .hp-card {
  flex: 1;
  min-width: 0;
}

/* Stacked bar chart ----------------------------------------------------- */
.hp-sbar-body {
  width: 100%;
  display: flex;
  flex-direction: column-reverse;
  overflow: hidden;
  border-radius: 5px 5px 0 0;
}

.hp-sbar-seg {
  min-height: 2px;
  transition: filter 0.12s;
}

.hp-sbar-seg:hover {
  filter: brightness(0.90);
  cursor: default;
}
"""

_PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: {bg};
      padding: 32px 24px;
      min-height: 100vh;
    }}
    {css}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

_BG = {"dark": "#0d1117", "light": "#f4f6fa"}


def get_css(theme: str = "dark") -> str:
    return _DARK_CSS if theme != "light" else _LIGHT_CSS


def render_page(title: str, body: str, theme: str = "dark", script: str = "") -> str:
    return _PAGE_TEMPLATE.format(
        title=title,
        bg=_BG.get(theme, _BG["dark"]),
        css=get_css(theme),
        body=body + ("\n" + script if script else ""),
    )
