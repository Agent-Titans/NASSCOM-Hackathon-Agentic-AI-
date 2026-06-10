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

    /* Fixed top bar — IntelliQ brand always visible (Employee / Agent parity) */
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
      grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
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
    {s} .admin-team-members {{
      margin-top: 0.75rem;
      padding-top: 0.65rem;
      border-top: 1px solid #F1F5F9;
    }}
    {s} .admin-team-members-title {{
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #94A3B8;
      margin: 0 0 0.35rem;
    }}
    {s} .admin-member-row {{
      display: flex;
      align-items: center;
      gap: 0.45rem;
      padding: 0.22rem 0;
      font-size: 0.76rem;
    }}
    {s} .admin-presence-dot {{
      width: 9px;
      height: 9px;
      border-radius: 50%;
      flex-shrink: 0;
      border: 2px solid #FFFFFF;
      box-shadow: 0 0 0 1px rgba(15, 23, 42, 0.08);
    }}
    {s} .presence-available {{
      background: #22C55E;
      animation: admin-presence-pulse 2.4s ease-in-out infinite;
    }}
    {s} .presence-away {{
      background: #F59E0B;
    }}
    {s} .presence-offline {{
      background: #94A3B8;
    }}
    @keyframes admin-presence-pulse {{
      0%, 100% {{ box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.2); }}
      50% {{ box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.15); }}
    }}
    {s} .admin-member-name {{
      font-weight: 600;
      color: #334155;
      flex: 1;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    {s} .admin-presence-label {{
      font-size: 0.68rem;
      color: #94A3B8;
      white-space: nowrap;
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
    {s} .admin-table-card-head .admin-filter-count {{
      margin: 0;
      white-space: nowrap;
    }}
    {s} .admin-table-panel {{
      display: none;
    }}
    {pp} [data-testid="stHorizontalBlock"]:has(.admin-table-toolbar) {{
      border: 1px solid #E8ECF1 !important;
      border-bottom: 1px solid #E8ECF1 !important;
      border-radius: 12px 12px 0 0 !important;
      background: #FFFFFF !important;
      padding: 0 1.1rem !important;
      align-items: center !important;
      margin-bottom: 0 !important;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }}
    {s} .admin-table-toolbar {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 0.75rem;
      padding: 0.8rem 0 0.7rem;
      border: none;
      background: transparent;
    }}
    {s} .admin-table-toolbar h3 {{
      margin: 0 !important;
      font-size: 0.95rem;
      font-weight: 700;
      color: #1E293B;
    }}
    {pp} [class*="st-key-admin_col_filter_clear_"] {{
      margin-top: 0 !important;
      padding-top: 0.55rem !important;
    }}
    {s} .admin-table-clear-wrap {{
      display: block;
      min-height: 0;
    }}
    {s} .admin-col-filter-title {{
      font-size: 0.72rem;
      font-weight: 700;
      color: #64748B;
      margin: 0 0 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    {pp} [data-testid="stHorizontalBlock"]:has([class*="st-key-admin_col_hdr_"]) {{
      margin: 0 !important;
      gap: 0 !important;
      background: #F8FAFC !important;
      border-left: 1px solid #E8ECF1 !important;
      border-right: 1px solid #E8ECF1 !important;
      border-bottom: 1px solid #E8ECF1 !important;
      padding: 0 !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      align-items: stretch !important;
      min-height: 2.15rem !important;
      max-height: 2.15rem !important;
    }}
    {pp} [data-testid="stHorizontalBlock"]:has([class*="st-key-admin_col_hdr_"]) > [data-testid="column"] {{
      display: flex !important;
      align-items: center !important;
      min-height: 0 !important;
      padding: 0 0.55rem !important;
      border-right: 1px solid #E8ECF1 !important;
      box-sizing: border-box !important;
    }}
    {pp} [data-testid="stHorizontalBlock"]:has([class*="st-key-admin_col_hdr_"]) > [data-testid="column"]:last-child {{
      border-right: none !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] {{
      border: none !important;
      margin: 0 !important;
      padding: 0 !important;
      width: 100% !important;
      min-width: 0 !important;
      height: 2.15rem !important;
      max-height: 2.15rem !important;
      overflow: hidden !important;
      display: flex !important;
      align-items: center !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stVerticalBlock"] {{
      gap: 0 !important;
      width: 100% !important;
      min-height: 0 !important;
      justify-content: center !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stElementContainer"] {{
      margin: 0 !important;
      padding: 0 !important;
      min-height: 0 !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] {{
      width: 100% !important;
      min-width: 0 !important;
      height: 2rem !important;
      max-height: 2rem !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] button {{
      width: 100% !important;
      max-width: 100% !important;
      height: 1.85rem !important;
      min-height: 1.85rem !important;
      max-height: 1.85rem !important;
      display: inline-flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      align-items: center !important;
      justify-content: space-between !important;
      gap: 0.15rem !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      padding: 0 0.2rem 0 0.3rem !important;
      font-size: 0.68rem !important;
      font-weight: 600 !important;
      letter-spacing: normal !important;
      text-transform: none !important;
      color: #64748B !important;
      border-radius: 0 !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      word-break: keep-all !important;
      line-height: 1 !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] button > div {{
      display: inline-flex !important;
      flex-direction: row !important;
      flex-wrap: nowrap !important;
      align-items: center !important;
      justify-content: space-between !important;
      width: 100% !important;
      min-width: 0 !important;
      gap: 0.1rem !important;
      line-height: 1 !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] button svg {{
      flex-shrink: 0 !important;
      width: 0.75rem !important;
      height: 0.75rem !important;
      margin: 0 !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] button:hover {{
      background: #F8FAFC !important;
      color: #6366F1 !important;
    }}
    {pp} [class*="st-key-admin_col_hdr_"] [data-testid="stPopoverButton"] button p {{
      font-size: 0.68rem !important;
      font-weight: 600 !important;
      letter-spacing: normal !important;
      text-transform: none !important;
      white-space: nowrap !important;
      overflow: hidden !important;
      text-overflow: ellipsis !important;
      margin: 0 !important;
      line-height: 1 !important;
      flex: 1 1 auto !important;
      min-width: 0 !important;
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
    {pp} [class*="st-key-admin_open_"] {{
      margin: 0 !important;
      padding: 0 !important;
    }}
    {pp} [class*="st-key-admin_open_"] button {{
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      color: #6366F1 !important;
      font-weight: 700 !important;
      font-size: 0.78rem !important;
      padding: 0.45rem 0.35rem !important;
      min-height: 0 !important;
      justify-content: flex-start !important;
      text-align: left !important;
    }}
    {pp} [class*="st-key-admin_open_"] button:hover {{
      color: #4338CA !important;
      background: #F8FAFC !important;
      text-decoration: underline !important;
    }}
    {s} .admin-table-data {{
      background: #FFFFFF;
      padding: 0;
      border: 1px solid #E8ECF1;
      border-top: none;
      border-radius: 0 0 12px 12px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }}
    {s} .admin-table-data-html {{
      padding: 0 0.55rem 0.35rem;
      overflow-x: auto;
    }}
    {pp} [data-testid="stHorizontalBlock"]:has([class*="st-key-admin_open_"]) {{
      border-bottom: 1px solid #F1F5F9 !important;
      border-left: 1px solid #E8ECF1 !important;
      border-right: 1px solid #E8ECF1 !important;
      align-items: center !important;
      min-height: 2.35rem !important;
      margin: 0 !important;
      gap: 0 !important;
      padding: 0 !important;
      background: #FFFFFF !important;
    }}
    {s} .admin-table-data-footer {{
      border: 1px solid #E8ECF1;
      border-top: none;
      border-radius: 0 0 12px 12px;
      height: 0;
      margin: 0 0 0.75rem;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }}
    {pp} [data-testid="stHorizontalBlock"]:has([class*="st-key-admin_open_"]) > [data-testid="column"] {{
      display: flex !important;
      align-items: center !important;
      padding: 0 0.55rem !important;
      border-right: 1px solid #F8FAFC !important;
      box-sizing: border-box !important;
    }}
    {pp} [data-testid="stHorizontalBlock"]:has([class*="st-key-admin_open_"]) > [data-testid="column"]:last-child {{
      border-right: none !important;
    }}
    {s} .admin-row-text {{
      font-size: 0.78rem;
      color: #334155;
      line-height: 1.35;
      display: block;
      padding: 0.45rem 0.35rem;
    }}
    {s} .admin-empty-rows {{
      color: #94A3B8;
      font-size: 0.85rem;
      padding: 1rem 0.35rem;
      margin: 0;
    }}
    {s} .admin-ticket-detail h2 {{
      font-size: 1.35rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0.25rem 0 0.75rem;
      letter-spacing: -0.02em;
    }}
    {s} .admin-ticket-detail-id {{
      font-size: 0.82rem;
      font-weight: 700;
      color: #6366F1;
      margin: 0;
    }}
    {s} .admin-ticket-detail-chips {{
      display: flex;
      gap: 0.4rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }}
    {s} .admin-ticket-meta-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.85rem 1rem;
    }}
    {s} .admin-ticket-meta-grid .meta-lbl {{
      font-size: 0.65rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: #94A3B8;
      margin: 0 0 0.2rem;
    }}
    {s} .admin-ticket-meta-grid .meta-val {{
      font-size: 0.85rem;
      font-weight: 600;
      color: #1E293B;
      margin: 0;
    }}
    {s} .admin-ticket-desc {{
      margin: 0;
      color: #475569;
      font-size: 0.9rem;
      line-height: 1.55;
      white-space: pre-wrap;
    }}
    {s} .admin-resolution-steps {{
      margin: 0;
      padding-left: 1.2rem;
      color: #475569;
      font-size: 0.88rem;
      line-height: 1.5;
    }}
    {s} .sla-ok {{ color: #16A34A !important; }}
    {s} .sla-risk {{ color: #D97706 !important; }}
    {s} .sla-breach {{ color: #DC2626 !important; }}

    {s} .admin-table-wrap {{
      overflow-x: auto;
    }}
    {s} .admin-table-wrap-body {{
      margin-top: 0 !important;
      border-top: none;
      background: #FFFFFF;
      padding: 0 0.35rem 0.35rem;
      box-sizing: border-box;
    }}
    {s} .admin-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8rem;
      table-layout: auto;
    }}
    {s} .admin-table-fixed {{
      table-layout: fixed;
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
      padding: 0.5rem 0.4rem;
      border-bottom: 1px solid #F1F5F9;
      color: #334155;
      vertical-align: middle;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 0.78rem;
      line-height: 1.35;
    }}
    {s} .admin-table td:nth-child(2),
    {s} .admin-table td.admin-cell-wrap {{
      white-space: normal;
      word-break: break-word;
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
