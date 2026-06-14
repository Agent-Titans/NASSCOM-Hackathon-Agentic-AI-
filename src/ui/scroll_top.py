"""Scroll Streamlit main pane to top on navigation."""
from __future__ import annotations

import streamlit.components.v1 as components


def inject_scroll_to_top() -> None:
    components.html(
        """
        <script>
        (function () {
          const doc = window.parent.document;
          const targets = [
            doc.querySelector('section.main'),
            doc.querySelector('[data-testid="stMain"]'),
            doc.documentElement,
            doc.body,
          ].filter(Boolean);
          for (const el of targets) {
            try { el.scrollTop = 0; } catch (e) {}
          }
          try { window.parent.scrollTo(0, 0); } catch (e) {}
        })();
        </script>
        """,
        height=0,
    )
