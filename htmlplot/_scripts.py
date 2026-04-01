"""Minimal JS tooltip engine injected into every rendered figure.

Design
------
- A single floating ``<div id="hp-tip">`` is created once per page.
- Any element that carries a ``data-tip`` attribute automatically shows a
  tooltip on hover.  The attribute value is an HTML string (``<b>``, ``<br>``
  etc. are supported) that is rendered inside the tooltip via ``innerHTML``.
- Event listeners are attached via delegation on ``document``, so they work
  regardless of when elements are added to the DOM.
- A guard (``if (!document.getElementById('hp-tip'))`` prevents duplicate
  setup when multiple figures appear on the same page (e.g. Jupyter).
"""

_JS = """\
<script>
(function () {
  if (document.getElementById('hp-tip')) return;
  var tip = document.createElement('div');
  tip.id = 'hp-tip';
  tip.className = 'hp-tip';
  document.body.appendChild(tip);

  function place(e) {
    var x = e.clientX + 14, y = e.clientY - 42;
    var w = tip.offsetWidth, h = tip.offsetHeight;
    if (x + w > window.innerWidth  - 8) x = e.clientX - w - 10;
    if (y - h < 4)                       y = e.clientY + 14;
    tip.style.left = x + 'px';
    tip.style.top  = y + 'px';
  }

  document.addEventListener('mouseover', function (e) {
    var el = e.target.closest('[data-tip]');
    if (el) {
      tip.innerHTML = el.getAttribute('data-tip');
      tip.style.opacity = '1';
      tip.style.display = 'block';
      place(e);
    }
  });

  document.addEventListener('mousemove', function (e) {
    if (tip.style.display === 'block') place(e);
  });

  document.addEventListener('mouseout', function (e) {
    var el = e.target.closest('[data-tip]');
    if (el && !el.contains(e.relatedTarget)) {
      tip.style.display = 'none';
    }
  });
}());
</script>"""


def get_script() -> str:
    return _JS
