"""Helpdesk admin dashboard — sidebar + KPI layout."""
from __future__ import annotations


def admin_portal_css() -> str:
    pp = '[data-testid="stAppViewContainer"]:has(.premium-admin-scope)'
    s = f"{pp} .premium-admin-scope"

    return f"""
    <style>
    {pp} [data-testid="stSidebar"],
    {pp} [data-testid="collapsedControl"] {{
      display: none !important;
    }}
    {pp} [data-testid="stMain"] {{
      margin-left: 0 !important;
      width: 100% !important;
    }}
    {pp} {{
      background: #F4F6F9 !important;
    }}
    {pp} [data-testid="stMainBlockContainer"],
    {pp} .block-container {{
      max-width: 1280px !important;
      padding: 7.5rem 2rem 2.5rem !important;
      margin: 0 auto !important;
    }}
    {pp} [data-testid="stVerticalBlock"] > div,
    {pp} [data-testid="stElementContainer"],
    {pp} [data-testid="stMarkdownContainer"] {{
      background: transparent !important;
    }}

    /* Fixed top bar — ClearHand brand always visible (Employee / Agent parity) */
    {s} .admin-topnav {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 70px;
      background: rgba(255, 255, 255, 0.85);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      z-index: 999;
      border-bottom: 1px solid rgba(226, 232, 240, 0.9);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 2rem;
      box-sizing: border-box;
    }}
    {s} .portal-brand {{
      font-size: 1.4rem;
      font-weight: 800;
      background: linear-gradient(135deg, #1E40AF 0%, #2563EB 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: -0.02em;
      margin: 0;
    }}
    {s} .admin-topnav-meta {{
      font-size: 0.72rem;
      font-weight: 600;
      color: #94A3B8;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-right: 6.5rem;
    }}
    {pp} [data-testid="stElementContainer"][class*="st-key-admin_signout"] {{
      position: fixed !important;
      top: 17px !important;
      right: 2rem !important;
      z-index: 1000 !important;
      width: auto !important;
      margin: 0 !important;
      padding: 0 !important;
    }}
    {pp} [class*="st-key-admin_signout"] button {{
      background: rgba(255, 255, 255, 0.9) !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 8px !important;
      color: #64748B !important;
      font-size: 0.82rem !important;
      font-weight: 600 !important;
      padding: 0.42rem 0.9rem !important;
    }}
    {pp} [class*="st-key-admin_signout"] button:hover {{
      border-color: #2563EB !important;
      color: #2563EB !important;
      background: #F8FAFC !important;
    }}
    /* Horizontal nav row below brand bar */
    {pp} [class*="st-key-admin_nav_"] {{
      margin-bottom: 0.15rem !important;
    }}

    {s} .admin-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1.35rem;
    }}
    {s} .admin-header h1 {{
      font-size: 1.65rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0 0 0.2rem;
      letter-spacing: -0.03em;
    }}
    {s} .admin-header p {{
      font-size: 0.88rem;
      color: #64748B;
      margin: 0;
    }}
    {s} .admin-header-actions {{
      display: flex;
      gap: 0.5rem;
    }}

    {s} .admin-kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin-bottom: 1.25rem;
    }}
    {s} .admin-kpi {{
      background: #FFFFFF;
      border: 1px solid #E8ECF1;
      border-radius: 12px;
      padding: 1.1rem 1.15rem;
      box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }}
    {s} .admin-kpi .label {{
      font-size: 0.72rem;
      font-weight: 600;
      color: #64748B;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin: 0 0 0.35rem;
    }}
    {s} .admin-kpi .value {{
      font-size: 1.85rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0;
      line-height: 1.1;
      letter-spacing: -0.03em;
    }}
    {s} .admin-kpi .sub {{
      font-size: 0.78rem;
      color: #64748B;
      margin: 0.35rem 0 0;
    }}
    {s} .admin-trend-up {{
      color: #16A34A;
      font-weight: 600;
      font-size: 0.78rem;
    }}
    {s} .admin-trend-down {{
      color: #DC2626;
      font-weight: 600;
      font-size: 0.78rem;
    }}
    {s} .admin-trend-good {{
      color: #16A34A;
    }}

    {s} .admin-mid-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
      margin-bottom: 1.25rem;
    }}
    {s} .admin-card {{
      background: #FFFFFF;
      border: 1px solid #E8ECF1;
      border-radius: 12px;
      padding: 1.15rem 1.25rem;
      box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }}
    {s} .admin-card h3 {{
      font-size: 0.92rem;
      font-weight: 700;
      color: #1E293B;
      margin: 0 0 1rem;
    }}
    {s} .admin-bar-row {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.65rem;
    }}
    {s} .admin-bar-label {{
      width: 58px;
      font-size: 0.78rem;
      font-weight: 600;
      color: #475569;
      flex-shrink: 0;
    }}
    {s} .admin-bar-track {{
      flex: 1;
      height: 22px;
      background: #F1F5F9;
      border-radius: 6px;
      overflow: hidden;
    }}
    {s} .admin-bar-fill {{
      height: 100%;
      border-radius: 6px;
      min-width: 4px;
    }}
    {s} .admin-bar-val {{
      width: 36px;
      text-align: right;
      font-size: 0.82rem;
      font-weight: 700;
      color: #1E293B;
    }}
    {s} .fill-h1 {{ background: linear-gradient(90deg, #22C55E, #16A34A); }}
    {s} .fill-h2 {{ background: linear-gradient(90deg, #FBBF24, #F59E0B); }}
    {s} .fill-h3 {{ background: linear-gradient(90deg, #F87171, #EF4444); }}
    {s} .fill-open {{ background: linear-gradient(90deg, #60A5FA, #3B82F6); }}
    {s} .fill-resolved {{ background: linear-gradient(90deg, #34D399, #10B981); }}
    {s} .fill-closed {{ background: linear-gradient(90deg, #94A3B8, #64748B); }}
    {s} .fill-triage {{ background: linear-gradient(90deg, #FB923C, #F97316); }}

    {s} .admin-conf-footer {{
      display: flex;
      gap: 0.75rem;
      margin-top: 1rem;
      padding-top: 0.85rem;
      border-top: 1px solid #F1F5F9;
      flex-wrap: wrap;
    }}
    {s} .admin-conf-pill {{
      font-size: 0.72rem;
      font-weight: 600;
      padding: 0.25rem 0.55rem;
      border-radius: 6px;
    }}
    {s} .conf-high {{ background: #DCFCE7; color: #166534; }}
    {s} .conf-med {{ background: #FEF3C7; color: #92400E; }}
    {s} .conf-low {{ background: #FEE2E2; color: #991B1B; }}

    {s} .admin-team-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      margin-bottom: 1.25rem;
    }}
    {s} .admin-team-card h4 {{
      font-size: 0.88rem;
      font-weight: 700;
      color: #1E293B;
      margin: 0 0 0.25rem;
    }}
    {s} .admin-team-card .open-count {{
      font-size: 1.5rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0.15rem 0;
    }}
    {s} .admin-team-card .meta {{
      font-size: 0.76rem;
      color: #64748B;
      margin: 0 0 0.65rem;
    }}
    {s} .admin-cap-track {{
      height: 8px;
      background: #E2E8F0;
      border-radius: 99px;
      overflow: hidden;
      margin-bottom: 0.35rem;
    }}
    {s} .admin-cap-fill {{
      height: 100%;
      border-radius: 99px;
    }}
    {s} .cap-ok {{ background: #3B82F6; }}
    {s} .cap-warn {{ background: #F59E0B; }}
    {s} .cap-danger {{ background: #EF4444; }}
    {s} .admin-cap-label {{
      font-size: 0.72rem;
      color: #64748B;
    }}

    {s} .admin-filter-bar {{
      background: #F8FAFC;
      border: 1px solid #E8ECF1;
      border-radius: 10px;
      padding: 0.85rem 1rem;
      margin-bottom: 0.85rem;
    }}
    {s} .admin-filter-label {{
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #94A3B8;
      margin: 0 0 0.35rem;
    }}
    {s} .admin-filter-count {{
      font-size: 0.78rem;
      color: #64748B;
      margin: 0.35rem 0 0.5rem;
    }}
    {s} .admin-table-card {{
      padding-bottom: 0.25rem !important;
    }}
    {s} .admin-col-filter-title {{
      font-size: 0.72rem;
      font-weight: 700;
      color: #64748B;
      margin: 0 0 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] {{
      border-bottom: 1px solid #E8ECF1;
      margin-bottom: 0 !important;
      padding-bottom: 0.15rem;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] button {{
      width: 100% !important;
      justify-content: flex-start !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      padding: 0.55rem 0.5rem !important;
      min-height: 0 !important;
      font-size: 0.65rem !important;
      font-weight: 700 !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
      color: #94A3B8 !important;
      border-radius: 0 !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] button:hover {{
      background: #F8FAFC !important;
      color: #6366F1 !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] button p {{
      font-size: 0.65rem !important;
      font-weight: 700 !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
    }}
    {pp} [class*="st-key-admin_col_filter_"] input {{
      border-radius: 8px !important;
      border: 1px solid #E2E8F0 !important;
      font-size: 0.82rem !important;
    }}
    {pp} [class*="st-key-admin_col_filter_"] [data-baseweb="select"] {{
      font-size: 0.8rem !important;
    }}
    {pp} [class*="st-key-admin_col_filter_clear_"] button {{
      border-radius: 8px !important;
      font-size: 0.78rem !important;
      color: #64748B !important;
      border: 1px solid #E2E8F0 !important;
      background: #FFFFFF !important;
    }}

    {s} .admin-table-wrap {{
      overflow-x: auto;
    }}
    {s} .admin-table-wrap-body {{
      margin-top: -0.35rem;
    }}
    {s} .admin-table-body-only td:first-child {{
      padding-left: 0.5rem;
    }}
    {s} .admin-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8rem;
    }}
    {s} .admin-table th {{
      text-align: left;
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #94A3B8;
      padding: 0.65rem 0.75rem;
      border-bottom: 1px solid #E8ECF1;
    }}
    {s} .admin-table td {{
      padding: 0.7rem 0.75rem;
      border-bottom: 1px solid #F1F5F9;
      color: #334155;
      vertical-align: middle;
    }}
    {s} .admin-table tr:hover td {{
      background: #F8FAFC;
    }}
    {s} .admin-id {{
      font-weight: 700;
      color: #6366F1;
      font-size: 0.78rem;
    }}
    {s} .admin-pill {{
      display: inline-block;
      font-size: 0.68rem;
      font-weight: 700;
      padding: 0.2rem 0.45rem;
      border-radius: 5px;
    }}
    {s} .pill-open {{ background: #DBEAFE; color: #1D4ED8; }}
    {s} .pill-resolved {{ background: #D1FAE5; color: #047857; }}
    {s} .pill-triage {{ background: #FFEDD5; color: #C2410C; }}
    {s} .pill-closed {{ background: #F1F5F9; color: #475569; }}
    {s} .pill-h1 {{ background: #DCFCE7; color: #166534; }}
    {s} .pill-h2 {{ background: #FEF3C7; color: #92400E; }}
    {s} .pill-h3 {{ background: #FEE2E2; color: #991B1B; }}

    {pp} [class*="st-key-admin_nav_"] button {{
      width: 100% !important;
      justify-content: center !important;
      background: #FFFFFF !important;
      border: 1px solid #E2E8F0 !important;
      color: #475569 !important;
      font-size: 0.78rem !important;
      font-weight: 600 !important;
      padding: 0.45rem 0.5rem !important;
      border-radius: 8px !important;
      margin-bottom: 1.25rem !important;
      white-space: nowrap !important;
    }}
    {pp} [class*="st-key-admin_nav_"] button:hover {{
      border-color: #93C5FD !important;
      color: #1D4ED8 !important;
      background: #F8FAFC !important;
    }}
    {pp} [class*="st-key-admin_nav_"] button[kind="primary"] {{
      background: #EEF2FF !important;
      border-color: #6366F1 !important;
      color: #4338CA !important;
      font-weight: 700 !important;
    }}
    {pp} [class*="st-key-admin_hdr_export"] button,
    {pp} [class*="st-key-admin_hdr_refresh"] button {{
      border-radius: 8px !important;
      font-size: 0.82rem !important;
      font-weight: 600 !important;
      padding: 0.45rem 0.9rem !important;
    }}
    {pp} [class*="st-key-admin_hdr_export"] button {{
      background: #FFFFFF !important;
      border: 1px solid #E2E8F0 !important;
      color: #475569 !important;
    }}
    {pp} [class*="st-key-admin_hdr_refresh"] button {{
      background: #4F46E5 !important;
      border: none !important;
      color: #FFFFFF !important;
    }}
    @media (max-width: 1100px) {{
      {pp} [data-testid="stMainBlockContainer"],
      {pp} .block-container {{
        padding: 7rem 1rem 2rem !important;
      }}
      {s} .admin-topnav {{
        padding: 0 1rem !important;
      }}
      {pp} [data-testid="stElementContainer"][class*="st-key-admin_signout"] {{
        right: 1rem !important;
      }}
      {s} .admin-kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
      {s} .admin-mid-grid {{ grid-template-columns: 1fr; }}
      {s} .admin-team-grid {{ grid-template-columns: 1fr; }}
    }}
    </style>
    """
