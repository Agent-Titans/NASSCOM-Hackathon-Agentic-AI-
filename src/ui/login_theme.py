"""SAARTHI login — welcome, sign-in, and workspace scope styles."""
from __future__ import annotations

def login_css(dark: bool) -> str:
    if dark:
        bg = "linear-gradient(180deg, #0F172A 0%, #020617 100%)"
        eyebrow = "#64748B"
        brand_name = "#93C5FD"
        brand_dot = "#60A5FA"
        tagline = "#94A3B8"
        pill_bg = "#0F172A"
        pill_hover = "#1E293B"
        pill_shadow = "0 4px 12px rgba(0, 0, 0, 0.25)"
        card_bg = "rgba(30, 41, 59, 0.55)"
        card_bg_hover = "rgba(30, 41, 59, 0.72)"
        card_border = "rgba(148, 163, 184, 0.25)"
        card_hover_border = "rgba(96, 165, 250, 0.35)"
        card_title = "#F8FAFC"
        card_text = "#94A3B8"
        footer = "#64748B"
        footer_border = "#334155"
        toggle_label = "#94A3B8"
        picker_heading = "#F8FAFC"
        gate_desc = "#94A3B8"
        tile_sub_color = "#94A3B8"
        glass_bg = "rgba(30, 41, 59, 0.55)"
        glass_border = "rgba(148, 163, 184, 0.25)"
        tile_card_bg = "rgba(30, 41, 59, 0.65)"
        tile_card_border = "#475569"
        tile_card_hover_bg = "rgba(30, 41, 59, 0.85)"
    else:
        bg = "linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%)"
        eyebrow = "#94A3B8"
        brand_name = "#1E40AF"
        brand_dot = "#2563EB"
        tagline = "#475569"
        pill_bg = "#0F172A"
        pill_hover = "#1E293B"
        pill_shadow = "0 4px 12px rgba(15, 23, 42, 0.1)"
        card_bg = "rgba(255, 255, 255, 0.40)"
        card_bg_hover = "rgba(255, 255, 255, 0.60)"
        card_border = "rgba(255, 255, 255, 0.6)"
        card_hover_border = "rgba(37, 99, 235, 0.25)"
        card_title = "#0F172A"
        card_text = "#475569"
        footer = "#94A3B8"
        footer_border = "#E2E8F0"
        toggle_label = "#64748B"
        picker_heading = "#0F172A"
        gate_desc = "#475569"
        tile_sub_color = "#64748B"
        glass_bg = "rgba(255, 255, 255, 0.45)"
        glass_border = "rgba(255, 255, 255, 0.7)"
        tile_card_bg = "rgba(255, 255, 255, 0.55)"
        tile_card_border = "rgba(226, 232, 240, 0.8)"
        tile_card_hover_bg = "#FFFFFF"

    w = '[data-testid="stAppViewContainer"]:has(.welcome-scope)'
    ws = '[data-testid="stAppViewContainer"]:has(.workspace-scope)'
    ss = '[data-testid="stAppViewContainer"]:has(.signin-scope)'

    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* —— Shared auth canvas —— */
    [data-testid="stAppViewContainer"]:has(.welcome-scope),
    [data-testid="stAppViewContainer"]:has(.workspace-scope) {{
      background: #EFF2F6 !important;
      min-height: 100vh;
    }}
    [data-testid="stAppViewContainer"]:has(.signin-scope) {{
      background: #F3F4F6 !important;
      min-height: 100vh;
    }}
    [data-testid="stAppViewContainer"]:has(.welcome-scope) {{
      background: {bg} !important;
    }}
    [data-testid="stAppViewContainer"]:has(.welcome-scope) [data-testid="stSidebar"],
    [data-testid="stAppViewContainer"]:has(.workspace-scope) [data-testid="stSidebar"],
    [data-testid="stAppViewContainer"]:has(.signin-scope) [data-testid="stSidebar"] {{
      display: none !important;
    }}
    [data-testid="stAppViewContainer"]:has(.welcome-scope) [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"]:has(.welcome-scope) .block-container {{
      max-width: 100% !important;
      width: 100% !important;
      padding: 0 1.25rem 2rem !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      display: flex !important;
      flex-direction: column !important;
      align-items: center !important;
    }}
    [data-testid="stAppViewContainer"]:has(.workspace-scope) [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"]:has(.workspace-scope) .block-container {{
      max-width: 100% !important;
      width: 100% !important;
      padding: 0 1.25rem 2rem !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}
    [data-testid="stAppViewContainer"]:has(.welcome-scope) [data-testid="stVerticalBlock"] > div,
    [data-testid="stAppViewContainer"]:has(.workspace-scope) [data-testid="stVerticalBlock"] > div {{
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}

    .login-toggle-wrap {{
      width: 100%;
      max-width: 1100px;
      margin: 0 auto;
      padding: 0.75rem 1.25rem 0;
    }}
    .login-toggle-wrap [data-testid="stHorizontalBlock"] {{
      gap: 1rem !important;
      align-items: center !important;
      justify-content: flex-end !important;
      width: 100% !important;
    }}
    .login-toggle-wrap [data-testid="stColumn"] {{
      padding: 0 !important;
      min-width: 0 !important;
      background: transparent !important;
    }}
    .login-toggle-wrap [data-testid="stColumn"]:last-child {{
      flex: 0 0 auto !important;
      width: auto !important;
      min-width: 9rem !important;
    }}
    .login-toggle-wrap label,
    .login-toggle-wrap p {{
      color: {toggle_label} !important;
      font-size: 0.8rem !important;
      white-space: nowrap !important;
    }}

    /* —— Welcome scope —— */
    {w} .login-page-root,
    {w} .welcome-body {{
      width: 100%;
      max-width: 1100px;
      margin: 0 auto;
      padding: 0 1.25rem 2rem;
      box-sizing: border-box;
      text-align: center;
    }}
    {w} .login-page-root {{
      position: relative;
    }}
    {w} .hero-container {{
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      width: 100%;
      margin: 2.5rem auto 0;
      padding: 0 1rem;
      text-align: center;
    }}
    {w} .brand-lockup {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.35rem;
      margin-bottom: 0.15rem;
      text-align: center;
    }}
    {w} .login-eyebrow {{
      margin: 0 0 0.35rem;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: {eyebrow};
    }}
    .brand-lockup .login-title {{
      margin: 0;
      line-height: 1;
    }}
    .brand-wordmark {{
      display: inline-block;
      font-family: "Inter", system-ui, -apple-system, sans-serif;
      font-weight: 900;
      letter-spacing: -0.03em;
      line-height: 1;
      white-space: nowrap;
    }}
    .brand-wordmark-hero {{
      font-size: clamp(3.25rem, 9vw, 4.75rem);
    }}
    .brand-wordmark-nav {{
      font-size: 1.5rem;
      font-weight: 800;
      letter-spacing: -0.02em;
    }}
    .brand-wordmark .brand-name {{
      color: #1E40AF;
      font-family: inherit;
      font-weight: inherit;
    }}
    .brand-wordmark .brand-dot {{
      color: #2563EB;
      font-family: inherit;
      font-weight: inherit;
    }}
    {w} .login-warm-pill {{
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      margin: 1rem 0 0;
      padding: 0.35rem 0.75rem;
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 600;
      color: {card_text};
      background: {glass_bg};
      border: 1px solid {glass_border};
    }}
    {w} .login-warm-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #3B82F6;
      animation: saarthi-pulse 1.2s ease-in-out infinite;
    }}
    @keyframes saarthi-pulse {{
      0%, 100% {{ opacity: 0.45; transform: scale(0.9); }}
      50% {{ opacity: 1; transform: scale(1.1); }}
    }}
    {w} .login-tagline {{
      margin: 0.75rem 0 0;
      font-size: 1.05rem;
      color: {tagline};
      line-height: 1.5;
      max-width: 32rem;
      font-weight: 500;
      font-family: "Inter", system-ui, -apple-system, sans-serif;
    }}
    {w} .login-caption {{
      margin: 0.55rem 0 0;
      font-size: 0.82rem;
      color: {card_text};
      line-height: 1.5;
      max-width: 36rem;
    }}
    {w} [data-testid="stElementContainer"]:has(.login-page-root),
    {w} [data-testid="stElementContainer"]:has(.welcome-body) {{
      width: 100% !important;
      max-width: 1100px !important;
      margin-left: auto !important;
      margin-right: auto !important;
      padding: 0 !important;
    }}
    {w} [data-testid="stElementContainer"]:has(button[data-testid="stBaseButton-primary"]) {{
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      width: 100% !important;
      max-width: 1100px !important;
      margin: 2rem auto 0 !important;
      padding: 0 !important;
      background: transparent !important;
    }}
    {w} [data-testid="stElementContainer"]:has(button[data-testid="stBaseButton-primary"])
      [data-testid="stButton"],
    {w} [data-testid="stElementContainer"]:has(button[data-testid="stBaseButton-primary"])
      div[data-testid="stBlock"] {{
      width: auto !important;
      margin: 0 auto !important;
      display: flex !important;
      justify-content: center !important;
    }}
    {w} button[data-testid="stBaseButton-primary"] {{
      background-color: {pill_bg} !important;
      color: #FFFFFF !important;
      border-radius: 9999px !important;
      padding: 0.8rem 3.5rem !important;
      font-size: 1rem !important;
      font-weight: 600 !important;
      border: none !important;
      box-shadow: none !important;
      margin: 0 auto !important;
      width: auto !important;
      min-height: auto !important;
      transform: none !important;
      transition: all 0.2s ease !important;
      opacity: 1 !important;
      position: relative !important;
      display: inline-flex !important;
    }}
    {w} button[data-testid="stBaseButton-primary"]:hover {{
      background-color: {pill_hover} !important;
      color: #FFFFFF !important;
      transform: translateY(-2px) !important;
    }}
    {w} .product-grid {{
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      gap: 1.5rem !important;
      justify-content: center !important;
      align-items: stretch !important;
      width: 100% !important;
      max-width: 1100px !important;
      margin: 4rem auto 0 !important;
      padding: 0 !important;
      box-sizing: border-box !important;
    }}
    @media (max-width: 980px) {{
      {w} .product-grid {{ flex-wrap: wrap !important; }}
      {w} .login-title {{ font-size: clamp(2.5rem, 10vw, 4rem); }}
    }}
    {w} .product-card {{
      background: {card_bg};
      backdrop-filter: blur(20px) saturate(160%);
      -webkit-backdrop-filter: blur(20px) saturate(160%);
      border: 1px solid {card_border};
      border-radius: 24px;
      padding: 2.5rem 1.5rem;
      width: 290px;
      min-width: 290px;
      max-width: 290px;
      flex: 0 0 290px !important;
      box-sizing: border-box;
      text-align: left;
      box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    {w} .product-card:hover {{
      background: {card_bg_hover};
      transform: translateY(-4px);
      border-color: {card_hover_border};
      box-shadow: 0 12px 28px -6px rgba(31, 38, 135, 0.08);
    }}
    {w} .product-badge {{
      font-size: 0.65rem;
      font-weight: 700;
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
      display: inline-block;
      margin-bottom: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    {w} .badge-instant {{
      background: rgba(37, 99, 235, 0.06);
      color: #2563EB;
    }}
    {w} .badge-automated {{
      background: rgba(79, 70, 229, 0.06);
      color: #4F46E5;
    }}
    {w} .badge-escalated {{
      background: rgba(14, 165, 233, 0.06);
      color: #0EA5E9;
    }}
    {w} .product-card-title {{
      margin: 0 0 0.5rem;
      font-size: 1.25rem;
      font-weight: 800;
      color: {card_title};
      line-height: 1.25;
    }}
    {w} .product-card-desc {{
      margin: 0;
      font-size: 0.9rem;
      color: {card_text};
      line-height: 1.6;
    }}
    {w} .login-footer {{
      text-align: center;
      margin-top: 8rem;
      padding-top: 2.5rem;
      padding-bottom: 2rem;
      border-top: 1px solid {footer_border};
      color: {footer};
      font-size: 0.8rem;
      letter-spacing: 0.05em;
      width: 100%;
    }}

    /* —— Workspace scope — glass column panel —— */
    {ws} [data-testid="stColumn"]:has(.workspace-scope) {{
      background: {glass_bg} !important;
      backdrop-filter: blur(24px) saturate(160%) !important;
      -webkit-backdrop-filter: blur(24px) saturate(160%) !important;
      border: 1px solid {glass_border} !important;
      border-radius: 28px !important;
      padding: 3.5rem 2.5rem !important;
      margin: 6rem auto 2rem !important;
      box-shadow: 0 10px 30px -10px rgba(30, 41, 59, 0.04) !important;
      text-align: center !important;
      box-sizing: border-box !important;
      max-width: 440px !important;
      width: 100% !important;
    }}
    {ws} [data-testid="stColumn"]:has(.workspace-scope) [data-testid="stElementContainer"] {{
      width: 100% !important;
      max-width: 100% !important;
      padding: 0 !important;
    }}
    {ws} [data-testid="stColumn"]:has(.workspace-scope) [data-testid="stMarkdownContainer"] {{
      width: 100% !important;
    }}
    .workspace-scope .gate-brand-line {{
      margin: 0 0 0.35rem;
      font-size: 1.15rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      line-height: 1.2;
    }}
    .workspace-scope .gate-brand {{ color: {brand_name}; }}
    .workspace-scope .gate-brand-dot {{ color: {brand_dot}; }}
    .workspace-scope .gate-eyebrow {{
      margin: 0 0 1rem;
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
      color: {eyebrow};
    }}
    .workspace-scope .gateway-heading {{
      font-size: 2rem;
      font-weight: 800;
      color: {picker_heading};
      letter-spacing: -0.03em;
      margin: 0 0 0.55rem;
      line-height: 1.15;
    }}
    .workspace-scope .gateway-desc {{
      font-size: 0.92rem;
      color: {gate_desc};
      margin: 0 auto 1.5rem;
      line-height: 1.55;
      max-width: 22rem;
    }}
    .workspace-scope .gateway-error {{
      color: #DC2626;
      font-size: 0.85rem;
      margin: 0 0 1rem;
    }}
    .workspace-scope .gateway-empty {{
      color: {gate_desc};
      font-size: 0.9rem;
      margin: 0 0 1rem;
    }}
    .workspace-scope .gateway-copyright {{
      text-align: center;
      color: {footer};
      font-size: 0.75rem;
      letter-spacing: 0.05em;
      margin: 1.75rem 0 0;
      padding-top: 1.35rem;
      border-top: 1px solid {footer_border};
    }}
    .workspace-scope .gateway-tile-list {{
      display: flex;
      flex-direction: column;
      gap: 0;
      margin-top: 0.25rem;
    }}
    .workspace-scope .gate-tile-row {{
      position: relative;
      width: 100%;
      margin: 0;
    }}
    .workspace-scope .gateway-tile-card {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      grid-template-rows: auto auto;
      column-gap: 0.75rem;
      row-gap: 0.15rem;
      align-items: center;
      width: 100%;
      box-sizing: border-box;
      text-align: left;
      background: {tile_card_bg};
      border: 1px solid {tile_card_border};
      border-radius: 16px;
      padding: 1rem 1.25rem;
      height: 92px;
      min-height: 92px;
      max-height: 92px;
      overflow: hidden;
      pointer-events: none;
      transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1),
                  border-color 0.2s ease, background 0.2s ease,
                  box-shadow 0.2s ease;
    }}
    .workspace-scope .gateway-tile-card .tile-title {{
      grid-column: 1;
      grid-row: 1;
      font-size: 1.05rem;
      font-weight: 700;
      color: #1E40AF;
      line-height: 1.3;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .workspace-scope .gateway-tile-card .tile-desc {{
      grid-column: 1;
      grid-row: 2;
      font-size: 0.86rem;
      font-weight: 400;
      color: #64748B;
      line-height: 1.35;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .workspace-scope .gateway-tile-card .tile-chevron {{
      grid-column: 2;
      grid-row: 1 / span 2;
      align-self: center;
      font-size: 1.35rem;
      font-weight: 300;
      color: #64748B;
      line-height: 1;
      transition: color 0.2s ease, transform 0.2s ease;
    }}

    /* Transparent overlay — HTML tile + keyed blank button sibling */
    {ws} [data-testid="stElementContainer"]:has(.gate-tile-row) {{
      position: relative !important;
      z-index: 1 !important;
      margin: 0.75rem 0 0 !important;
      padding: 0 !important;
      width: 100% !important;
    }}
    {ws} [data-testid="stElementContainer"]:has(.gate-tile-row)
      + [data-testid="stElementContainer"][class*="st-key-track_"],
    {ws} [data-testid="stElementContainer"]:has(.gate-tile-row)
      + [data-testid="stElementContainer"][class*="st-key-profile_"] {{
      position: relative !important;
      margin: -92px 0 0.75rem !important;
      height: 92px !important;
      min-height: 92px !important;
      max-height: 92px !important;
      z-index: 10 !important;
      padding: 0 !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      overflow: visible !important;
    }}
    {ws} [data-testid="stElementContainer"][class*="st-key-track_"] [data-testid="stButton"],
    {ws} [data-testid="stElementContainer"][class*="st-key-profile_"] [data-testid="stButton"],
    {ws} [data-testid="stElementContainer"][class*="st-key-track_"] div[data-testid="stBlock"],
    {ws} [data-testid="stElementContainer"][class*="st-key-profile_"] div[data-testid="stBlock"] {{
      width: 100% !important;
      height: 92px !important;
      min-height: 92px !important;
      margin: 0 !important;
      padding: 0 !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}
    {ws} [data-testid="stElementContainer"][class*="st-key-track_"] button,
    {ws} [data-testid="stElementContainer"][class*="st-key-profile_"] button {{
      opacity: 0 !important;
      width: 100% !important;
      height: 92px !important;
      min-height: 92px !important;
      margin: 0 !important;
      padding: 0 !important;
      border: none !important;
      background: transparent !important;
      box-shadow: none !important;
      cursor: pointer !important;
    }}
    {ws} [data-testid="stElementContainer"]:has(.gate-tile-row):has(
      + [data-testid="stElementContainer"]:hover) .gateway-tile-card {{
      transform: scale(1.015);
      border-color: #2563EB;
      background: {tile_card_hover_bg};
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.08);
    }}
    {ws} [data-testid="stElementContainer"]:has(.gate-tile-row):has(
      + [data-testid="stElementContainer"]:hover) .tile-chevron {{
      color: #2563EB;
      transform: translateX(2px);
    }}

    /* Workspace tertiary nav */
    {ws} button[data-testid="stBaseButton-tertiary"],
    {ws} button[kind="tertiary"] {{
      opacity: 1 !important;
      position: relative !important;
      top: auto !important;
      left: auto !important;
      width: 100% !important;
      height: auto !important;
      min-height: auto !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      color: {tile_sub_color} !important;
      font-size: 0.88rem !important;
      font-weight: 500 !important;
      margin-top: 1rem !important;
      padding: 0.35rem 0 !important;
      transform: none !important;
      cursor: pointer !important;
      z-index: 1 !important;
    }}
    {ws} button[data-testid="stBaseButton-tertiary"]:hover,
    {ws} button[kind="tertiary"]:hover {{
      color: #2563EB !important;
      background: transparent !important;
    }}
    {ws} button[data-testid="stBaseButton-tertiary"] p,
    {ws} button[kind="tertiary"] p {{
      display: block !important;
      white-space: normal !important;
      font-size: 0.88rem !important;
      color: inherit !important;
      font-weight: 500 !important;
    }}

    /* —— Sign-in scope (mockup: logo above card, pill buttons, gray inputs) —— */
    .signin-layout-marker,
    .signin-form-marker,
    .signin-card-shell-marker {{
      display: none !important;
    }}
    {ss} .login-toggle-wrap {{
      display: none !important;
    }}
    {ss} [data-testid="stMainBlockContainer"],
    {ss} .block-container {{
      max-width: 100% !important;
      padding: 2.5rem 1.25rem 3rem !important;
      background: transparent !important;
      display: flex !important;
      flex-direction: column !important;
      align-items: center !important;
      justify-content: center !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-layout-marker),
    {ss} [data-testid="stVerticalBlock"]:has(.signin-scope) {{
      align-items: center !important;
      width: 100% !important;
      max-width: 440px !important;
      margin: 0 auto !important;
      gap: 0 !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-layout-marker)
      > [data-testid="stElementContainer"],
    {ss} [data-testid="stVerticalBlock"]:has(.signin-scope)
      > [data-testid="stElementContainer"] {{
      width: 100% !important;
      max-width: 440px !important;
      margin: 0 auto !important;
      padding: 0 !important;
      box-sizing: border-box !important;
    }}
    /* Logo row — outside the white card */
    {ss} [data-testid="stVerticalBlock"]:has(.signin-layout-marker)
      > [data-testid="stElementContainer"]:has(.signin-topnav-outside),
    {ss} [data-testid="stVerticalBlock"]:has(.signin-scope)
      > [data-testid="stElementContainer"]:has(.signin-topnav-outside) {{
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      padding: 0 0 1.35rem !important;
      margin-bottom: 0 !important;
    }}
    /* One seamless white card — pseudo backdrop, transparent segment rows */
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker) {{
      position: relative !important;
      isolation: isolate !important;
      gap: 0 !important;
      row-gap: 0 !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)::before {{
      content: "" !important;
      position: absolute !important;
      left: 0 !important;
      right: 0 !important;
      top: 3rem !important;
      bottom: 0 !important;
      background: #FFFFFF !important;
      border: 1px solid #E8EAED !important;
      border-radius: 18px !important;
      box-shadow: 0 8px 32px rgba(15, 23, 42, 0.1) !important;
      z-index: 0 !important;
      pointer-events: none !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      > [data-testid="stElementContainer"],
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      > [data-testid="stElementContainer"] > div,
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      [data-testid="stForm"],
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      [data-testid="stForm"] [data-testid="stElementContainer"] {{
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      > [data-testid="stElementContainer"] {{
      position: relative !important;
      z-index: 1 !important;
      margin: 0 !important;
      padding-top: 0 !important;
      padding-bottom: 0 !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      > [data-testid="stElementContainer"]:has(.signin-topnav-outside) {{
      padding: 0 0 1.35rem !important;
      z-index: 2 !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      > [data-testid="stElementContainer"]:not(:has(.signin-topnav-outside)),
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      > [data-testid="stLayoutWrapper"]:has(.signin-form-marker) {{
      padding-left: 2rem !important;
      padding-right: 2rem !important;
      box-sizing: border-box !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      > [data-testid="stLayoutWrapper"]:has(.signin-form-marker) {{
      width: 100% !important;
      max-width: 440px !important;
      margin: 0 auto 2.5rem !important;
      padding-bottom: 2.65rem !important;
      position: relative !important;
      z-index: 1 !important;
    }}
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker) [data-testid="stForm"],
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker)
      [data-testid="stForm"] [data-testid="stVerticalBlock"],
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker)
      [data-testid="stElementContainer"],
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker)
      [data-testid="stTextInput"],
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker)
      [data-testid="stTextInput"] > div,
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker)
      [data-testid="stTextInput"] [data-baseweb="input"],
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker)
      [data-testid="stButton"],
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker)
      [data-testid="stButton"] > div,
    {ss} [data-testid="stLayoutWrapper"]:has(.signin-form-marker)
      button[data-testid="stBaseButton-primaryFormSubmit"] {{
      width: 100% !important;
      max-width: 100% !important;
      box-sizing: border-box !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      > [data-testid="stElementContainer"]:has(.signin-card-top) {{
      padding-top: 2.35rem !important;
    }}
    {ss} [data-testid="stForm"]:has(.signin-form-marker) {{
      border: none !important;
      margin: 0 !important;
      padding: 0 0 0.5rem !important;
      width: 100% !important;
      max-width: 100% !important;
      background: transparent !important;
      box-shadow: none !important;
    }}
    {ss} [data-testid="stVerticalBlock"]:has(.signin-card-shell-marker)
      [data-testid="stVerticalBlock"] {{
      gap: 0 !important;
    }}
    .signin-scope.signin-topnav-outside {{
      width: 100%;
      text-align: center;
      padding: 0;
    }}
    .signin-scope.signin-topnav {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      color: #111827;
    }}
    .signin-scope.signin-card-top {{
      width: 100%;
      text-align: center;
      padding: 0;
      box-sizing: border-box;
    }}
    .signin-scope .signin-lock-icon {{
      width: 52px;
      height: 52px;
      margin: 0 auto 1.35rem;
      border-radius: 999px;
      background: #111827;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }}
    .signin-scope .signin-heading {{
      margin: 0;
      font-size: 1.75rem;
      font-weight: 700;
      font-family: "Inter", system-ui, -apple-system, sans-serif;
      color: #111827;
      letter-spacing: -0.02em;
    }}
    .signin-scope .signin-subtitle {{
      margin: 0.55rem auto 2.25rem;
      font-size: 0.92rem;
      color: #6B7280;
      line-height: 1.5;
      max-width: 22rem;
      font-family: "Inter", system-ui, -apple-system, sans-serif;
    }}
    .signin-scope.signin-error {{
      color: #DC2626;
      font-size: 0.85rem;
      text-align: center !important;
      margin: 0;
      padding: 0.35rem 0 0.5rem;
    }}
    {ss} [data-testid="stForm"]:has(.signin-form-marker) > [data-testid="stVerticalBlock"] {{
      display: flex !important;
      flex-direction: column !important;
      gap: 0 !important;
      row-gap: 0 !important;
      align-items: stretch !important;
      width: 100% !important;
    }}
    {ss} [data-testid="stForm"]:has(.signin-form-marker)
      > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {{
      margin: 0 !important;
      padding: 0 !important;
      flex: 0 0 auto !important;
      min-height: 0 !important;
    }}
    {ss} [data-testid="stForm"]:has(.signin-form-marker)
      [data-testid="stElementContainer"][class*="st-key-signin_email"] {{
      margin-bottom: 0.5rem !important;
    }}
    {ss} [data-testid="stForm"]:has(.signin-form-marker)
      [data-testid="stElementContainer"][class*="st-key-signin_password"] {{
      margin-bottom: 0.45rem !important;
    }}
    {ss} [data-testid="stForm"]:has(.signin-form-marker)
      [data-testid="stElementContainer"]:has(.signin-form-marker) {{
      display: none !important;
      height: 0 !important;
      min-height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
      overflow: hidden !important;
    }}
    {ss} [data-testid="stForm"]:has(.signin-form-marker)
      [data-testid="stElementContainer"][class*="st-key-signin_email"] {{
      padding-bottom: 0.1rem !important;
    }}
    {ss} [data-testid="stForm"]:has(.signin-form-marker)
      [data-testid="stElementContainer"][class*="st-key-signin_password"] {{
      padding-bottom: 0.1rem !important;
    }}
    {ss} [data-testid="stTextInput"] {{
      margin-top: 0 !important;
      margin-bottom: 0 !important;
    }}
    {ss} label[data-testid="stWidgetLabel"] {{
      margin-bottom: 0 !important;
      padding-bottom: 0 !important;
    }}
    {ss} label[data-testid="stWidgetLabel"] p {{
      font-size: 0.875rem !important;
      font-weight: 700 !important;
      color: #111827 !important;
      text-align: left !important;
      margin: 0 0 0.5rem !important;
      line-height: 1.35 !important;
    }}
    {ss} [data-testid="stTextInput"] [data-baseweb="input"],
    {ss} div[data-testid="stTextInput"] input,
    {ss} [data-testid="stTextInput"] input {{
      border-radius: 12px !important;
    }}
    {ss} [data-testid="stTextInput"] [data-baseweb="input"] {{
      border: 1px solid #E5E7EB !important;
      background-color: #F3F4F6 !important;
      min-height: 3.125rem !important;
      height: 3.125rem !important;
      box-shadow: none !important;
    }}
    {ss} [class*="st-key-signin_email"] [data-baseweb="input"] {{
      padding-left: 2.65rem !important;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2'%3E%3Crect x='3' y='5' width='18' height='14' rx='2'/%3E%3Cpath d='M3 7l9 6 9-6'/%3E%3C/svg%3E") !important;
      background-repeat: no-repeat !important;
      background-position: 14px center !important;
      background-size: 18px 18px !important;
    }}
    {ss} [class*="st-key-signin_password"] [data-baseweb="input"] {{
      padding-left: 2.65rem !important;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2'%3E%3Crect x='5' y='11' width='14' height='10' rx='2'/%3E%3Cpath d='M8 11V8a4 4 0 1 1 8 0v3'/%3E%3C/svg%3E") !important;
      background-repeat: no-repeat !important;
      background-position: 14px center !important;
      background-size: 18px 18px !important;
    }}
    {ss} [data-testid="stTextInput"] input {{
      border: none !important;
      background: transparent !important;
      color: #111827 !important;
      box-shadow: none !important;
      font-size: 0.92rem !important;
    }}
    {ss} [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {{
      border-color: #3B82F6 !important;
      background-color: #FFFFFF !important;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12) !important;
      outline: none !important;
    }}
    {ss} [data-testid="stTextInput"] [data-baseweb="input"] button {{
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}
    {ss} [data-testid="stForm"] [data-testid="stButton"],
    {ss} [data-testid="stForm"] [data-testid="stButton"] > div,
    {ss} [data-testid="stForm"] [data-testid="stButton"] button {{
      width: 100% !important;
      max-width: 100% !important;
      display: flex !important;
      box-sizing: border-box !important;
    }}
    {ss} button[data-testid="stBaseButton-primary"],
    {ss} button[data-testid="stBaseButton-primaryFormSubmit"] {{
      background: #3B82F6 !important;
      background-image: none !important;
      color: #FFFFFF !important;
      border-radius: 9999px !important;
      border: none !important;
      font-weight: 600 !important;
      font-family: "Inter", system-ui, sans-serif !important;
      min-height: 3.125rem !important;
      height: 3.125rem !important;
      width: 100% !important;
      max-width: 100% !important;
      box-shadow: none !important;
      margin: 0.5rem 0 0 !important;
      padding: 0 1.25rem !important;
    }}
    {ss} button[data-testid="stBaseButton-primary"]:hover,
    {ss} button[data-testid="stBaseButton-primaryFormSubmit"]:hover {{
      background: #2563EB !important;
      background-image: none !important;
    }}
    .signin-scope .signin-link {{
      color: #3B82F6;
      font-weight: 600;
      cursor: default;
    }}
    </style>
    """
