"""Premium employee portal — iCloud top nav, glass profile & action cards."""
from __future__ import annotations


def employee_portal_css() -> str:
    pp = '[data-testid="stAppViewContainer"]:has(.premium-portal-scope)'
    s = f"{pp} .premium-portal-scope"

    return f"""
    <style>
    /* Hide sidebar entirely for employee portal */
    {pp} [data-testid="stSidebar"],
    {pp} [data-testid="collapsedControl"] {{
      display: none !important;
    }}
    {pp} [data-testid="stMain"] {{
      margin-left: 0 !important;
      width: 100% !important;
    }}

    /* Canvas + strip Streamlit chrome */
    {pp} {{
      background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%) !important;
    }}
    {pp} [data-testid="stMainBlockContainer"],
    {pp} .block-container {{
      max-width: 1140px !important;
      padding: 100px 2rem 2.5rem !important;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}
    {pp} [data-testid="stVerticalBlock"] > div,
    {pp} [data-testid="stVerticalBlockBorderWrapper"],
    {pp} [data-testid="stElementContainer"],
    {pp} [data-testid="stMarkdownContainer"],
    {pp} [data-testid="stColumn"],
    {pp} [data-testid="stHorizontalBlock"],
    {pp} [data-testid="stLayoutWrapper"] {{
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      padding: 0 !important;
      margin: 0 !important;
    }}
    {pp} [data-testid="stHorizontalBlock"] {{
      align-items: stretch !important;
      gap: 1.5rem !important;
    }}

    /* —— Fixed iCloud-style top nav —— */
    {s} .portal-topnav {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 70px;
      background: rgba(255, 255, 255, 0.7);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      z-index: 999;
      border-bottom: 1px solid rgba(226, 232, 240, 0.8);
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
    {s} .portal-nav-actions {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      min-width: 120px;
      justify-content: flex-end;
    }}
    {s} .portal-nav-hint {{
      font-size: 0.72rem;
      font-weight: 600;
      color: #94A3B8;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-right: 6.5rem;
    }}

    /* Sign out — inside top nav (all portal_signout* keys) */
    {pp} [data-testid="stElementContainer"][class*="st-key-portal_signout"] {{
      position: fixed !important;
      top: 17px !important;
      right: 2rem !important;
      z-index: 1000 !important;
      width: auto !important;
      margin: 0 !important;
      padding: 0 !important;
    }}
    {pp} [class*="st-key-portal_signout"] button {{
      background: rgba(255, 255, 255, 0.85) !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 8px !important;
      color: #64748B !important;
      font-size: 0.82rem !important;
      font-weight: 600 !important;
      padding: 0.42rem 0.9rem !important;
      backdrop-filter: blur(8px) !important;
    }}
    {pp} [class*="st-key-portal_signout"] button:hover {{
      border-color: #2563EB !important;
      color: #2563EB !important;
      background: #F8FAFC !important;
    }}

    /* —— Top row glass cards (equal height) —— */
    {s} .portal-profile-card,
    {s} .portal-action-card {{
      background: rgba(255, 255, 255, 0.55);
      backdrop-filter: blur(24px) saturate(160%);
      -webkit-backdrop-filter: blur(24px) saturate(160%);
      border: 1px solid rgba(255, 255, 255, 0.75);
      border-radius: 18px;
      padding: 1.75rem 1.5rem;
      box-shadow: 0 8px 28px -8px rgba(30, 41, 59, 0.06);
      min-height: 220px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      box-sizing: border-box;
      height: 100%;
    }}
    {s} .portal-avatar {{
      border-radius: 50%;
      background: #EFF6FF;
      width: 64px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
      margin: 0 auto 1rem;
    }}
    {s} .portal-welcome {{
      font-size: 1.3rem;
      font-weight: 700;
      color: #0F172A;
      text-align: center;
      margin: 0;
    }}
    {s} .portal-email {{
      font-size: 0.85rem;
      color: #64748B;
      text-align: center;
      margin: 0.15rem 0 0;
    }}
    {s} .portal-org {{
      font-size: 0.7rem;
      font-weight: 600;
      color: #94A3B8;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      text-align: center;
      margin: 1rem 0 0;
    }}

    {s} .portal-action-card {{
      justify-content: center;
      transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    {s} .portal-action-title {{
      font-size: 1.35rem;
      font-weight: 800;
      color: #1E40AF;
      margin: 0 0 0.5rem;
    }}
    {s} .portal-action-desc {{
      font-size: 0.88rem;
      color: #64748B;
      line-height: 1.55;
      margin: 0;
    }}
    {s} .portal-action-bundle {{
      pointer-events: none;
      user-select: none;
    }}

    /* New Request — full card is one click target (column-scoped overlay) */
    {pp} [data-testid="stColumn"]:has(.portal-action-bundle) {{
      position: relative !important;
      min-height: 220px !important;
    }}
    {pp} [data-testid="stColumn"]:has(.portal-action-bundle)
      [class*="st-key-portal_btn_create"] {{
      position: absolute !important;
      top: 0 !important;
      left: 0 !important;
      right: 0 !important;
      bottom: 0 !important;
      width: 100% !important;
      height: 100% !important;
      min-height: 220px !important;
      margin: 0 !important;
      padding: 0 !important;
      z-index: 20 !important;
      background: transparent !important;
      border: none !important;
    }}
    {pp} [data-testid="stColumn"]:has(.portal-action-bundle)
      [class*="st-key-portal_btn_create"] button {{
      width: 100% !important;
      height: 100% !important;
      min-height: 220px !important;
      margin: 0 !important;
      padding: 0 !important;
      opacity: 0 !important;
      border: none !important;
      background: transparent !important;
      box-shadow: none !important;
      cursor: pointer !important;
    }}
    {pp} [data-testid="stColumn"]:has(.portal-action-bundle):hover .portal-action-card {{
      transform: scale(1.015);
      border-color: #2563EB;
      background: rgba(255, 255, 255, 0.78);
      box-shadow: 0 12px 32px rgba(37, 99, 235, 0.14);
    }}

    /* —— Dashboard metrics —— */
    {s} .portal-dash {{
      margin-bottom: 1.5rem;
    }}
    {s} .portal-dash-heading {{
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #64748B;
      margin: 0 0 0.85rem;
    }}
    {s} .portal-metrics {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
    }}
    {s} .portal-metric {{
      display: flex;
      align-items: flex-start;
      gap: 0.85rem;
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 14px;
      padding: 1.15rem 1.2rem;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
      transition: transform 0.2s ease, box-shadow 0.2s ease;
      position: relative;
      overflow: hidden;
    }}
    {s} .portal-metric::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
    }}
    {s} .portal-metric-open::before {{ background: linear-gradient(90deg, #2563EB, #60A5FA); }}
    {s} .portal-metric-resolved::before {{ background: linear-gradient(90deg, #059669, #34D399); }}
    {s} .portal-metric-total::before {{ background: linear-gradient(90deg, #6366F1, #A78BFA); }}
    {s} .portal-metric:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
    }}
    {s} .portal-metric-icon {{
      flex-shrink: 0;
      width: 42px;
      height: 42px;
      border-radius: 11px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    {s} .portal-metric-icon-open {{
      color: #2563EB;
      background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
    }}
    {s} .portal-metric-icon-resolved {{
      color: #059669;
      background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
    }}
    {s} .portal-metric-icon-total {{
      color: #6366F1;
      background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
    }}
    {s} .portal-metric-body {{
      min-width: 0;
    }}
    {s} .portal-metric-val {{
      font-size: 1.85rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0;
      line-height: 1;
      letter-spacing: -0.02em;
    }}
    {s} .portal-metric-lbl {{
      font-size: 0.78rem;
      font-weight: 700;
      color: #334155;
      margin: 0.35rem 0 0;
    }}
    {s} .portal-metric-hint {{
      font-size: 0.72rem;
      font-weight: 600;
      margin: 0.2rem 0 0;
    }}
    {s} .portal-metric-open .portal-metric-hint {{ color: #2563EB; }}
    {s} .portal-metric-resolved .portal-metric-hint {{ color: #059669; }}
    {s} .portal-metric-total .portal-metric-hint {{ color: #6366F1; }}

    /* —— Queue list alignment —— */
    {s} .portal-queue-head {{
      display: grid;
      grid-template-columns: 0.8fr 2.05fr 0.95fr 0.7fr 1.05fr 0.7fr;
      gap: 0.5rem;
      padding: 0.5rem 0.75rem;
      margin-bottom: 0.35rem;
      font-size: 0.65rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #94A3B8;
    }}
    {pp} [data-testid="stExpander"] [data-testid="stHorizontalBlock"] {{
      align-items: center !important;
      background: rgba(255, 255, 255, 0.45) !important;
      border: 1px solid rgba(226, 232, 240, 0.65) !important;
      border-radius: 10px !important;
      padding: 0.55rem 0.65rem !important;
      margin-bottom: 0.45rem !important;
    }}
    {s} .portal-row-id {{
      font-size: 0.72rem;
      font-weight: 700;
      color: #2563EB;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      margin: 0;
      line-height: 1.3;
    }}
    {s} .portal-row-title {{
      font-size: 0.88rem;
      font-weight: 600;
      color: #0F172A;
      margin: 0;
      line-height: 1.3;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    {s} .portal-row-date {{
      font-size: 0.72rem;
      color: #94A3B8;
      margin: 0.1rem 0 0;
    }}
    {s} .portal-row-assignee {{
      font-size: 0.75rem;
      font-weight: 600;
      color: #475569;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    {s} .ticket-comment {{
      border-top: 1px solid #E2E8F0;
      padding: 0.65rem 0;
    }}
    {s} .ticket-comment:first-of-type {{
      border-top: none;
      padding-top: 0;
    }}
    {s} .ticket-comment-meta {{
      font-size: 0.72rem;
      color: #64748B;
      margin: 0 0 0.25rem;
    }}
    {s} .ticket-comment-body {{
      font-size: 0.88rem;
      color: #334155;
      margin: 0;
      line-height: 1.45;
    }}
    {s} .ticket-comment-empty {{
      font-size: 0.85rem;
      color: #94A3B8;
      margin: 0;
    }}
    {pp} [class*="st-key-portal_view_"] button,
    {pp} [class*="st-key-portal_hist_"] button {{
      width: 100% !important;
      min-height: 2rem !important;
      padding: 0.35rem 0.5rem !important;
      font-size: 0.75rem !important;
    }}

    /* Empty state */
    {s} .portal-empty-state {{
      text-align: center;
      background: rgba(255, 255, 255, 0.55);
      border: 1px dashed #E2E8F0;
      border-radius: 14px;
      padding: 1.75rem 1.25rem;
      margin-bottom: 1rem;
    }}
    {s} .portal-empty-icon {{ font-size: 1.75rem; margin: 0 0 0.5rem; }}
    {s} .portal-empty-title {{
      font-size: 1rem;
      font-weight: 700;
      color: #475569;
      margin: 0 0 0.25rem;
    }}
    {s} .portal-empty-sub {{
      font-size: 0.85rem;
      color: #94A3B8;
      margin: 0;
    }}
    {s} .portal-chip {{
      font-size: 0.72rem;
      font-weight: 600;
      border-radius: 9999px;
      padding: 0.22rem 0.6rem;
      white-space: nowrap;
    }}
    {s} .portal-chip-hand {{ color: #B45309; background: #FEF3C7; }}
    {s} .portal-chip-hand-2 {{ color: #3730A3; background: #EEF2FF; }}
    {s} .portal-chip-hand-1 {{ color: #047857; background: #ECFDF5; }}
    {s} .portal-chip-status {{ color: #475569; background: #F1F5F9; }}
    {s} .portal-chip-status-ok {{ color: #047857; background: #ECFDF5; }}
    {s} .portal-chip-status-info {{ color: #1D4ED8; background: #EFF6FF; }}
    {s} .portal-chip-status-warn {{ color: #B45309; background: #FEF3C7; }}

    /* Detail record (unchanged ITSM) */
    {s} .itsm-record {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
      margin-bottom: 1rem;
    }}
    {s} .itsm-record-top {{ padding: 1.25rem 1.5rem; border-bottom: 1px solid #E2E8F0; }}
    {s} .itsm-record-key {{ font-size: 0.75rem; font-weight: 700; color: #2563EB; margin: 0 0 0.35rem; }}
    {s} .itsm-record-title {{ font-size: 1.45rem; font-weight: 800; color: #0F172A; margin: 0 0 0.65rem; }}
    {s} .itsm-state-bar {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
    {s} .itsm-chip {{ display: inline-block; font-size: 0.72rem; font-weight: 600; border-radius: 4px; padding: 0.2rem 0.5rem; }}
    {s} .itsm-chip-status {{ color: #475569; background: #F1F5F9; }}
    {s} .itsm-chip-domain {{ color: #1E40AF; background: #EFF6FF; }}
    {s} .itsm-chip-hand {{ color: #B45309; background: #FEF3C7; }}
    {s} .itsm-chip-hand-2 {{ color: #3730A3; background: #EEF2FF; }}
    {s} .itsm-chip-hand-1 {{ color: #047857; background: #ECFDF5; }}
    {s} .itsm-meta-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); border-top: 1px solid #E2E8F0; }}
    {s} .itsm-meta-cell {{ padding: 0.85rem 1.25rem; border-bottom: 1px solid #F1F5F9; border-right: 1px solid #F1F5F9; }}
    {s} .itsm-meta-cell:nth-child(2n) {{ border-right: none; }}
    {s} .itsm-meta-lbl {{ font-size: 0.68rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #94A3B8; margin: 0 0 0.25rem; }}
    {s} .itsm-meta-val {{ font-size: 0.92rem; font-weight: 600; color: #0F172A; margin: 0; }}
    {s} .itsm-banner {{ margin: 1rem 1.25rem 0; padding: 0.85rem 1rem; border-radius: 8px; font-size: 0.88rem; }}
    {s} .itsm-banner-info {{ background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; }}
    {s} .itsm-banner-warn {{ background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; }}
    {s} .itsm-banner-ok {{ background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; }}
    {s} .itsm-banner-ref {{ background: #F5F3FF; border: 1px solid #DDD6FE; color: #5B21B6; margin: 0 0 1rem; }}
    {s} .itsm-section {{
      background: #FAFAFA;
      border: 1px solid #E2E8F0;
      border-radius: 10px;
      padding: 1rem 1.15rem;
      margin-bottom: 0.85rem;
    }}
    {s} .itsm-cite-plain {{ margin: 0 0 0.35rem; font-size: 0.85rem; color: #64748B; }}
    {s} .itsm-cite-muted {{ color: #94A3B8; font-size: 0.78rem; }}
    {s} .itsm-section-title {{ font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #64748B; margin: 0 0 0.65rem; }}
    {s} .itsm-description-text {{
      margin: 0 0 0.65rem;
      color: #475569;
      font-size: 0.9rem;
      font-weight: 400;
      font-family: inherit;
      line-height: 1.55;
      white-space: pre-wrap;
    }}
    {s} .itsm-description-text:last-child {{ margin-bottom: 0; }}

    {pp} [data-testid="stExpander"] {{
      background: rgba(255,255,255,0.65) !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 12px !important;
      margin-bottom: 0.85rem !important;
    }}
    {pp} [data-testid="stExpander"] summary {{
      font-size: 0.78rem !important;
      font-weight: 700 !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
      color: #475569 !important;
      padding: 0.8rem 1rem !important;
      background: rgba(248,250,252,0.9) !important;
    }}
    {pp} button[data-testid="stBaseButton-primary"] {{
      background: #2563EB !important;
      border: none !important;
      border-radius: 10px !important;
      font-weight: 700 !important;
      font-size: 0.9rem !important;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2) !important;
    }}
    {pp} button[data-testid="stBaseButton-primary"]:hover {{
      background: #1D4ED8 !important;
      box-shadow: 0 6px 16px rgba(37, 99, 235, 0.28) !important;
    }}
    {pp} button[data-testid="stBaseButton-secondary"] {{
      background: rgba(255,255,255,0.8) !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 8px !important;
      font-weight: 600 !important;
      font-size: 0.78rem !important;
      color: #334155 !important;
    }}
    {pp} button[data-testid="stBaseButton-tertiary"] {{
      background: transparent !important;
      border: none !important;
      color: #64748B !important;
    }}
    {pp} [class*="st-key-portal_cite_"] button,
    {pp} [class*="st-key-portal_ref_"] button {{
      justify-content: flex-start !important;
      text-align: left !important;
      width: 100% !important;
      padding: 0.2rem 0 !important;
      min-height: 0 !important;
      color: #2563EB !important;
      font-size: 0.85rem !important;
      font-weight: 600 !important;
      text-decoration: underline !important;
      text-underline-offset: 2px !important;
    }}
    {pp} [class*="st-key-portal_cite_"] button:hover,
    {pp} [class*="st-key-portal_ref_"] button:hover {{
      color: #1D4ED8 !important;
      background: #EFF6FF !important;
      border-radius: 6px !important;
    }}
    {pp} [data-testid="stForm"] {{
      background: #FFFFFF !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 14px !important;
      padding: 1.35rem 1.5rem !important;
      box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
    }}
    {s} .portal-create-hero {{
      margin: 0.5rem 0 1.5rem;
      padding: 1.25rem 1.35rem;
      background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
      border: 1px solid #E2E8F0;
      border-radius: 14px;
      box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04);
    }}
    {s} .portal-create-kicker {{
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #2563EB;
      margin: 0 0 0.4rem;
    }}
    {s} .portal-create-title {{
      font-size: 1.55rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0 0 0.35rem;
      letter-spacing: -0.02em;
    }}
    {s} .portal-create-sub {{
      font-size: 0.92rem;
      color: #64748B;
      margin: 0;
      line-height: 1.5;
    }}
    {s} .portal-form-section {{
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #64748B;
      margin: 1.1rem 0 0.45rem;
    }}
    {s} .portal-optional {{
      font-weight: 600;
      letter-spacing: 0.02em;
      text-transform: none;
      color: #94A3B8;
      font-size: 0.68rem;
    }}
    {pp} [data-testid="stForm"] [data-testid="stRadio"] label,
    {pp} [data-testid="stForm"] [data-testid="stCheckbox"] label {{
      font-size: 0.88rem !important;
      font-weight: 500 !important;
      color: #334155 !important;
    }}
    {pp} [data-testid="stForm"] [data-testid="stRadio"] [data-testid="stHorizontalBlock"] {{
      gap: 0.5rem !important;
      flex-wrap: wrap !important;
    }}
    {pp} [data-testid="stForm"] [data-testid="stCheckbox"] {{
      margin-bottom: 0.25rem !important;
    }}
    {pp} [data-testid="stForm"] [data-testid="stWidgetLabel"] p {{
      font-size: 0.82rem !important;
      font-weight: 700 !important;
      color: #0F172A !important;
      margin-bottom: 0.35rem !important;
    }}
    {pp} [data-testid="stForm"] [data-testid="stTextInput"] input,
    {pp} [data-testid="stForm"] [data-testid="stTextArea"] textarea {{
      border: 1.5px solid #CBD5E1 !important;
      border-radius: 10px !important;
      background: #FFFFFF !important;
      color: #0F172A !important;
      padding: 0.65rem 0.85rem !important;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05) !important;
    }}
    {pp} [data-testid="stForm"] [data-testid="stTextInput"] input:focus,
    {pp} [data-testid="stForm"] [data-testid="stTextArea"] textarea:focus {{
      border-color: #2563EB !important;
      outline: none !important;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }}
    {pp} [data-testid="stForm"] [data-testid="stTextInput"] > div,
    {pp} [data-testid="stForm"] [data-testid="stTextArea"] > div {{
      border: none !important;
      background: transparent !important;
    }}

    /* Compact centered assignment dialog (Hand 2/3 submit) */
    {pp} [data-testid="stDialog"] > div {{
      max-width: 360px !important;
      width: min(360px, calc(100vw - 2rem)) !important;
    }}
    {pp} [data-testid="stDialog"] [data-testid="stModal"] {{
      width: min(360px, calc(100vw - 2rem)) !important;
    }}

    /* Mobile — stack profile + action cards */
    @media (max-width: 768px) {{
      {pp} [data-testid="stMainBlockContainer"],
      {pp} .block-container {{
        padding: 88px 1rem 2rem !important;
      }}
      {s} .portal-topnav {{
        padding: 0 1rem !important;
        height: 64px !important;
      }}
      {pp} [data-testid="stElementContainer"][class*="st-key-portal_signout"] {{
        right: 1rem !important;
        top: 14px !important;
      }}
      {s} .portal-metrics {{
        grid-template-columns: 1fr !important;
      }}
      {s} .portal-profile-card,
      {s} .portal-action-card {{
        min-height: 180px !important;
      }}
      {pp} [data-testid="stColumn"]:has(.portal-action-bundle) {{
        min-height: 180px !important;
      }}
      {pp} [data-testid="stColumn"]:has(.portal-action-bundle)
        [class*="st-key-portal_btn_create"],
      {pp} [data-testid="stColumn"]:has(.portal-action-bundle)
        [class*="st-key-portal_btn_create"] button {{
        min-height: 180px !important;
      }}
      {s} .portal-queue-head {{
        display: none !important;
      }}
    }}
    </style>
    """
