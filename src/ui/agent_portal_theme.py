"""Premium agent workspace — department triage dashboard."""
from __future__ import annotations


def agent_portal_css() -> str:
    pp = '[data-testid="stAppViewContainer"]:has(.premium-agent-scope)'
    s = f"{pp} .premium-agent-scope"

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
      background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%) !important;
    }}
    {pp} [data-testid="stMainBlockContainer"],
    {pp} .block-container {{
      max-width: 1180px !important;
      padding: 58px 1.5rem 1.5rem !important;
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

    {s} .portal-topnav {{
      position: fixed;
      top: 0; left: 0;
      width: 100%; height: 70px;
      background: rgba(255, 255, 255, 0.72);
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
      background: linear-gradient(135deg, #0F766E 0%, #0D9488 55%, #2563EB 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: -0.02em;
      margin: 0;
    }}
    {s} .portal-nav-hint {{
      font-size: 0.72rem;
      font-weight: 600;
      color: #94A3B8;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-right: 6.5rem;
    }}

    {pp} [data-testid="stElementContainer"][class*="st-key-agent_signout"] {{
      position: fixed !important;
      top: 17px !important;
      right: 2rem !important;
      z-index: 1000 !important;
      width: auto !important;
      margin: 0 !important;
      padding: 0 !important;
    }}
    {pp} [class*="st-key-agent_signout"] button {{
      background: rgba(255, 255, 255, 0.85) !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 8px !important;
      color: #64748B !important;
      font-size: 0.82rem !important;
      font-weight: 600 !important;
      padding: 0.42rem 0.9rem !important;
    }}
    {pp} [class*="st-key-agent_signout"] button:hover {{
      border-color: #0D9488 !important;
      color: #0D9488 !important;
    }}

    {s} .portal-profile-card,
    {s} .agent-queue-card {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 18px;
      padding: 1.75rem 1.5rem;
      box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
      min-height: 220px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      box-sizing: border-box;
      height: 100%;
    }}
    {s} .portal-avatar {{
      border-radius: 50%;
      background: linear-gradient(135deg, #CCFBF1 0%, #DBEAFE 100%);
      width: 64px; height: 64px;
      display: flex; align-items: center; justify-content: center;
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
      margin: 0.75rem 0 0;
    }}
    {s} .agent-dept-badge {{
      display: inline-block;
      margin: 0.65rem auto 0;
      padding: 0.3rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: #0F766E;
      background: #CCFBF1;
      border: 1px solid #99F6E4;
    }}
    {s} .agent-queue-card {{
      text-align: center;
    }}
    {s} .agent-queue-lbl {{
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #94A3B8;
      margin: 0 0 0.35rem;
    }}
    {s} .agent-queue-dept {{
      font-size: 1.15rem;
      font-weight: 800;
      color: #0F766E;
      margin: 0 0 0.75rem;
    }}
    {s} .agent-queue-val {{
      font-size: 3rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0;
      line-height: 1;
      letter-spacing: -0.03em;
    }}
    {s} .agent-queue-sub {{
      font-size: 0.82rem;
      font-weight: 600;
      color: #64748B;
      margin: 0.35rem 0 0;
    }}
    {s} .agent-queue-mine {{
      font-size: 0.78rem;
      font-weight: 600;
      color: #2563EB;
      margin: 1rem 0 0;
      padding-top: 1rem;
      border-top: 1px solid #E2E8F0;
    }}
    {s} .portal-metric-body {{
      min-width: 0;
    }}

    {s} .portal-dash {{ margin-bottom: 0.85rem; }}
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
      grid-template-columns: repeat(4, 1fr);
      gap: 0.85rem;
    }}
    {s} .portal-metric {{
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 14px;
      padding: 1rem 1.05rem;
      box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    {s} .portal-metric::before {{
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
    }}
    {s} .portal-metric-unassigned::before {{ background: linear-gradient(90deg, #EA580C, #FB923C); }}
    {s} .portal-metric-mine::before {{ background: linear-gradient(90deg, #2563EB, #60A5FA); }}
    {s} .portal-metric-risk::before {{ background: linear-gradient(90deg, #DC2626, #F87171); }}
    {s} .portal-metric-escalation::before {{ background: linear-gradient(90deg, #B45309, #FBBF24); }}
    {s} .portal-metric:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08);
    }}
    {s} .portal-metric-icon {{
      flex-shrink: 0;
      width: 38px; height: 38px;
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.1rem;
    }}
    {s} .portal-metric-icon-unassigned {{ color: #EA580C; background: #FFF7ED; }}
    {s} .portal-metric-icon-mine {{ color: #2563EB; background: #EFF6FF; }}
    {s} .portal-metric-icon-risk {{ color: #DC2626; background: #FEF2F2; }}
    {s} .portal-metric-icon-escalation {{ color: #B45309; background: #FFFBEB; }}
    {s} .portal-metric-val {{
      font-size: 1.65rem;
      font-weight: 800;
      color: #0F172A;
      margin: 0;
      line-height: 1;
    }}
    {s} .portal-metric-lbl {{
      font-size: 0.74rem;
      font-weight: 700;
      color: #334155;
      margin: 0.3rem 0 0;
    }}
    {s} .portal-metric-hint {{
      font-size: 0.68rem;
      font-weight: 600;
      color: #94A3B8;
      margin: 0.15rem 0 0;
    }}

    {s} .agent-filter-bar {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0.75rem;
      flex-wrap: wrap;
    }}
    {s} .agent-filter-lbl {{
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #94A3B8;
      margin: 0;
    }}

    {s} .portal-queue-head {{
      display: grid;
      grid-template-columns: 0.72fr 2.05fr 0.48fr 0.62fr 0.78fr 0.62fr 0.82fr 1.15fr;
      gap: 0.4rem;
      padding: 0.5rem 0.65rem;
      margin-bottom: 0.35rem;
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.07em;
      text-transform: uppercase;
      color: #94A3B8;
    }}
    {s} .portal-queue-head-resolved {{
      grid-template-columns: 0.8fr 2.4fr 0.85fr 0.95fr 0.7fr 0.75fr;
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
    {pp} [data-testid="stExpander"] [data-testid="stHorizontalBlock"] {{
      align-items: center !important;
      background: #FFFFFF !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 10px !important;
      padding: 0.5rem 0.6rem !important;
      margin-bottom: 0.4rem !important;
      box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04) !important;
    }}
    {s} .portal-row-id {{
      font-size: 0.7rem;
      font-weight: 700;
      color: #0D9488;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      margin: 0;
    }}
    {s} .portal-row-title {{
      font-size: 0.84rem;
      font-weight: 600;
      color: #0F172A;
      margin: 0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    {s} .portal-row-sub {{
      font-size: 0.68rem;
      color: #94A3B8;
      margin: 0.08rem 0 0;
    }}
    {s} .portal-chip {{
      font-size: 0.68rem;
      font-weight: 600;
      border-radius: 9999px;
      padding: 0.2rem 0.5rem;
      white-space: nowrap;
      display: inline-block;
    }}
    {s} .portal-chip-hand {{ color: #B45309; background: #FEF3C7; }}
    {s} .portal-chip-hand-2 {{ color: #3730A3; background: #EEF2FF; }}
    {s} .portal-chip-status {{ color: #475569; background: #F1F5F9; }}
    {s} .portal-chip-status-info {{ color: #1D4ED8; background: #EFF6FF; }}
    {s} .portal-chip-status-warn {{ color: #B45309; background: #FEF3C7; }}
    {s} .portal-chip-priority {{
      font-size: 0.68rem;
      font-weight: 700;
      border-radius: 6px;
      padding: 0.18rem 0.45rem;
    }}
    {s} .pri-p0 {{ color: #991B1B; background: #FEE2E2; }}
    {s} .pri-p1 {{ color: #9A3412; background: #FFEDD5; }}
    {s} .pri-p2 {{ color: #475569; background: #F1F5F9; }}
    {s} .sla-ok {{ color: #047857; }}
    {s} .sla-risk {{ color: #B45309; font-weight: 700; }}
    {s} .sla-breach {{ color: #DC2626; font-weight: 700; }}
    {s} .portal-row-sla {{
      font-size: 0.72rem;
      font-weight: 600;
      margin: 0;
    }}
    {s} .assignee-you {{ color: #2563EB; font-weight: 700; }}
    {s} .assignee-open {{ color: #94A3B8; font-style: italic; }}

    {pp} [data-testid="stExpander"] [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child {{
      display: flex !important;
      flex-direction: column !important;
      gap: 0.3rem !important;
      justify-content: center !important;
    }}
    {pp} [class*="st-key-agent_view_"] button,
    {pp} [class*="st-key-agent_assign_"] button,
    {pp} [class*="st-key-agent_drop_"] button {{
      width: 100% !important;
      min-height: 1.75rem !important;
      padding: 0.28rem 0.4rem !important;
      font-size: 0.68rem !important;
      margin: 0 !important;
    }}
    {pp} [data-testid="stExpander"] [data-testid="stHorizontalBlock"] {{
      gap: 0.35rem !important;
    }}

    {s} .portal-empty-state {{
      text-align: center;
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 14px;
      padding: 1.75rem 1.25rem;
      margin-bottom: 1rem;
      box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
    }}
    {s} .portal-empty-icon {{ font-size: 1.75rem; margin: 0 0 0.5rem; }}
    {s} .portal-empty-title {{ font-size: 1rem; font-weight: 700; color: #475569; margin: 0 0 0.25rem; }}
    {s} .portal-empty-sub {{ font-size: 0.85rem; color: #94A3B8; margin: 0; }}

    {s} .itsm-record {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
      margin-bottom: 0.65rem;
    }}
    {s} .itsm-record-top {{ padding: 0.9rem 1.15rem; border-bottom: 1px solid #E2E8F0; }}
    {s} .itsm-record-key {{ font-size: 0.75rem; font-weight: 700; color: #0D9488; margin: 0 0 0.2rem; }}
    {s} .itsm-record-title {{ font-size: 1.35rem; font-weight: 800; color: #0F172A; margin: 0 0 0.45rem; }}
    {s} .itsm-state-bar {{ display: flex; flex-wrap: wrap; gap: 0.45rem; }}
    {s} .itsm-chip {{ display: inline-block; font-size: 0.72rem; font-weight: 600; border-radius: 4px; padding: 0.2rem 0.5rem; }}
    {s} .itsm-chip-status {{ color: #475569; background: #F1F5F9; }}
    {s} .itsm-chip-domain {{ color: #0F766E; background: #CCFBF1; }}
    {s} .itsm-chip-hand {{ color: #B45309; background: #FEF3C7; }}
    {s} .itsm-chip-hand-2 {{ color: #3730A3; background: #EEF2FF; }}
    {s} .itsm-meta-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); border-top: 1px solid #E2E8F0; }}
    {s} .itsm-meta-cell {{ padding: 0.85rem 1.25rem; border-bottom: 1px solid #F1F5F9; border-right: 1px solid #F1F5F9; }}
    {s} .itsm-meta-cell:nth-child(2n) {{ border-right: none; }}
    {s} .itsm-meta-lbl {{ font-size: 0.68rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #94A3B8; margin: 0 0 0.25rem; }}
    {s} .itsm-meta-val {{ font-size: 0.92rem; font-weight: 600; color: #0F172A; margin: 0; }}
    {s} .itsm-banner {{ margin: 0.55rem 1rem 0; padding: 0.7rem 0.9rem; border-radius: 8px; font-size: 0.86rem; }}
    {s} .itsm-banner-info {{ background: #EFF6FF; border: 1px solid #BFDBFE; color: #1E40AF; }}
    {s} .itsm-banner-warn {{ background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; }}
    {s} .itsm-banner-ref {{ background: #F5F3FF; border: 1px solid #DDD6FE; color: #5B21B6; margin-bottom: 0.85rem; }}
    {s} .itsm-banner-ok {{ background: #ECFDF5; border: 1px solid #A7F3D0; color: #065F46; }}
    {s} .itsm-cite-plain {{ margin: 0 0 0.35rem; font-size: 0.85rem; color: #64748B; }}
    {s} .itsm-cite-muted {{ color: #94A3B8; font-size: 0.78rem; }}
    {s} .itsm-section-title {{ font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: #64748B; margin: 0 0 0.45rem; }}
    {s} .itsm-section {{
      background: #FAFAFA;
      border: 1px solid #E2E8F0;
      border-radius: 10px;
      padding: 1rem 1.15rem;
      margin-bottom: 0.85rem;
    }}
    {s} .itsm-secops-badge {{
      width: 50%;
      margin: 0.04rem auto 0;
      padding: 0.2rem 0.3rem;
      text-align: center;
      background: linear-gradient(180deg, #DBEAFE 0%, #EFF6FF 100%);
      border: 1px solid #93C5FD;
      border-top: none;
      border-radius: 0 0 6px 6px;
      font-size: 0.54rem;
      font-weight: 900;
      letter-spacing: 0.08em;
      color: #1E3A8A;
      line-height: 1.15;
    }}
    {s} .itsm-detail-actions-title {{
      margin-top: 0.15rem !important;
      margin-bottom: 0.35rem !important;
    }}
    {s} .itsm-dept-route-heading {{
      margin-top: 0.45rem !important;
      margin-bottom: 0.35rem !important;
    }}
    {s} .itsm-secops-badge strong {{
      font-weight: 900;
    }}
    {s} .itsm-route-toolbar {{
      margin: 0.35rem 0 0.65rem;
      padding: 0.75rem 1rem 0.35rem;
      background: linear-gradient(135deg, rgba(255,255,255,0.92) 0%, rgba(239,246,255,0.85) 100%);
      border: 1px solid #DBEAFE;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(37, 99, 235, 0.06);
    }}
    {s} .itsm-route-toolbar-title {{
      margin: 0;
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #1E40AF;
    }}
    {s} .itsm-expander-meta {{
      margin: 0 0 0.75rem;
      font-size: 0.86rem;
      color: #334155;
      line-height: 1.45;
    }}
    {s} .itsm-expander-chip {{
      display: inline-block;
      padding: 0.15rem 0.45rem;
      margin-right: 0.35rem;
      border-radius: 6px;
      background: #EFF6FF;
      color: #1D4ED8;
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    {s} .itsm-description-text {{
      margin: 0;
      color: #475569;
      font-size: 0.9rem;
      line-height: 1.55;
      white-space: pre-wrap;
    }}
    {s} .itsm-resolution-list {{
      margin: 0;
      padding-left: 1.2rem;
      color: #475569;
      font-size: 0.9rem;
      line-height: 1.55;
    }}
    {s} .itsm-premium-select-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      margin: 0.5rem 0 0.35rem;
      padding: 0.55rem 0.75rem;
      background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
      border: 1px solid #E2E8F0;
      border-radius: 10px;
      box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
    }}
    {s} .itsm-premium-select-lbl {{
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #64748B;
    }}
    {s} .itsm-premium-select-chevron {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 1.5rem;
      height: 1.5rem;
      border-radius: 999px;
      background: #EFF6FF;
      color: #1D4ED8;
      flex-shrink: 0;
    }}
    {s} .itsm-premium-dropdown-panel {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      padding: 0.65rem 0.75rem 0.35rem;
      margin-bottom: 0.5rem;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    }}
    {s} .itsm-premium-dropdown-title {{
      margin: 0 0 0.35rem;
      font-size: 0.68rem;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #64748B;
    }}
    {s} .itsm-view-only-panel {{
      background: #F8FAFC !important;
      border-color: #E2E8F0 !important;
    }}

    {pp} [data-testid="stPopover"] button {{
      width: 100% !important;
      background: #FFFFFF !important;
      border: 1.5px solid #E2E8F0 !important;
      border-radius: 10px !important;
      color: #0F172A !important;
      font-weight: 600 !important;
      font-size: 0.88rem !important;
      min-height: 2.5rem !important;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
      justify-content: space-between !important;
    }}
    {pp} [data-testid="stPopover"] button:hover {{
      border-color: #93C5FD !important;
      background: #F8FAFC !important;
    }}
    {pp} [data-testid="stPopoverBody"] {{
      background: #FFFFFF !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 12px !important;
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12) !important;
      padding: 0.5rem !important;
    }}
    {pp} [data-testid="stHorizontalBlock"]:has([class*="st-key-agent_detail_assign"]) {{
      align-items: flex-start !important;
      gap: 0.55rem !important;
      margin-bottom: 0.35rem !important;
    }}
    {pp} [data-testid="stColumn"]:has([class*="st-key-agent_route_btn_"]) {{
      display: flex !important;
      flex-direction: column !important;
      align-items: center !important;
      justify-content: flex-start !important;
    }}
    {pp} [data-testid="stHorizontalBlock"]:has([class*="st-key-dept_route_select_"]) {{
      align-items: flex-end !important;
      gap: 0.6rem !important;
      margin: 0 !important;
    }}
    {pp} [class*="st-key-agent_route_btn_"] {{
      margin: 0 !important;
      padding: 0 !important;
      width: 100% !important;
    }}
    {pp} [class*="st-key-agent_route_btn_"] button {{
      width: 100% !important;
      min-height: 2.45rem !important;
      border-radius: 8px 8px 0 0 !important;
      margin: 0 !important;
      font-weight: 800 !important;
    }}
    {pp} [class*="st-key-agent_detail_assign"] button,
    {pp} [class*="st-key-agent_detail_resolve"] button,
    {pp} [class*="st-key-agent_detail_release"] button {{
      min-height: 2.45rem !important;
    }}
    {pp} [data-testid="stMarkdownContainer"]:has(.itsm-secops-badge) {{
      width: 100% !important;
      margin: 0 !important;
      padding: 0 !important;
    }}
    {pp} [class*="st-key-dept_route_select_"] {{
      margin: 0 !important;
      padding: 0 !important;
    }}
    {pp} [class*="st-key-dept_route_select_"] [data-testid="stWidgetLabel"] p {{
      font-size: 0.65rem !important;
      font-weight: 800 !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
      color: #94A3B8 !important;
      margin-bottom: 0.25rem !important;
    }}
    {pp} [class*="st-key-dept_route_select_"] [data-testid="stSelectbox"] > div {{
      background: #FFFFFF !important;
      border: 1.5px solid #CBD5E1 !important;
      border-radius: 10px !important;
      min-height: 2.45rem !important;
      box-shadow: none !important;
    }}
    {pp} [class*="st-key-dept_route_select_"] [data-testid="stSelectbox"] [data-baseweb="select"] {{
      min-height: 2.45rem !important;
      background: transparent !important;
    }}
    {pp} [class*="st-key-dept_route_select_"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
      font-size: 0.9rem !important;
      font-weight: 600 !important;
      color: #0F172A !important;
      padding: 0.45rem 0.65rem !important;
      line-height: 1.35 !important;
      white-space: nowrap !important;
      overflow: visible !important;
      text-overflow: clip !important;
    }}
    {pp} [class*="st-key-dept_route_select_"] [data-testid="stSelectbox"] [data-baseweb="select"] > div > div {{
      color: #0F172A !important;
      opacity: 1 !important;
      -webkit-text-fill-color: #0F172A !important;
    }}
    {pp} [class*="st-key-dept_route_select_"] [data-testid="stSelectbox"] svg {{
      display: block !important;
      width: 1rem !important;
      height: 1rem !important;
      flex-shrink: 0 !important;
      color: #64748B !important;
      fill: currentColor !important;
    }}
    {pp} [class*="st-key-dept_route_btn_"] {{
      margin: 0 !important;
      padding: 0 !important;
    }}
    {pp} [class*="st-key-dept_route_btn_"] button {{
      min-height: 2.45rem !important;
      font-weight: 800 !important;
      border-radius: 10px !important;
      margin-top: 1.38rem !important;
    }}
    {pp} .ticket-detail-view,
    {pp} [data-testid="stMarkdownContainer"]:has(> div > .ticket-detail-view) {{
      display: none !important;
      height: 0 !important;
      margin: 0 !important;
      padding: 0 !important;
      overflow: hidden !important;
      line-height: 0 !important;
    }}

    {pp} [data-testid="stExpander"] {{
      background: #FFFFFF !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 12px !important;
      margin-bottom: 0.85rem !important;
      box-shadow: 0 2px 14px rgba(15, 23, 42, 0.05) !important;
      overflow: hidden !important;
    }}
    {pp} [data-testid="stExpander"] summary {{
      font-size: 0.78rem !important;
      font-weight: 700 !important;
      letter-spacing: 0.06em !important;
      text-transform: uppercase !important;
      color: #334155 !important;
      padding: 0.85rem 1rem !important;
      background: #FFFFFF !important;
      border-bottom: 1px solid #E2E8F0 !important;
    }}
    {pp} [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
      padding: 0.9rem 1rem 1rem !important;
      background: #FFFFFF !important;
    }}
    {pp}:has(.ticket-detail-view) .itsm-record {{
      border: none !important;
      box-shadow: none !important;
      background: #FFFFFF !important;
    }}
    {pp}:has(.ticket-detail-view) .itsm-record-top {{
      border-bottom: none !important;
    }}
    {pp}:has(.ticket-detail-view) .itsm-meta-grid {{
      border-top: none !important;
    }}
    {pp}:has(.ticket-detail-view) .itsm-meta-cell {{
      border-color: #F8FAFC !important;
    }}
    {pp}:has(.ticket-detail-view) [data-testid="stExpander"] {{
      background: #FFFFFF !important;
      border: none !important;
      box-shadow: none !important;
      border-radius: 8px !important;
      margin-bottom: 0.18rem !important;
      overflow: hidden !important;
    }}
    {pp}:has(.ticket-detail-view) [data-testid="stExpander"] summary {{
      background: #FFFFFF !important;
      border: none !important;
      border-bottom: none !important;
      box-shadow: none !important;
      padding: 0.6rem 0.85rem !important;
      border-radius: 8px !important;
      color: #334155 !important;
    }}
    {pp}:has(.ticket-detail-view) [data-testid="stExpander"][open] summary {{
      border-bottom: none !important;
      border-radius: 8px 8px 0 0 !important;
    }}
    {pp}:has(.ticket-detail-view) [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
      background: #FFFFFF !important;
      border: none !important;
      border-top: none !important;
      padding: 0 0.85rem 0.65rem !important;
      margin: 0 !important;
      box-shadow: none !important;
    }}
    {pp}:has(.ticket-detail-view) details {{
      border: none !important;
    }}
    {pp}:has(.ticket-detail-view) details > summary + div {{
      border-top: none !important;
    }}
    {pp} [class*="st-key-agent_detail_back_ref"],
    {pp} [class*="st-key-agent_detail_back_dashboard"] {{
      margin: 0 0 0.1rem !important;
    }}
    {pp} button[data-testid="stBaseButton-primary"] {{
      background: #0D9488 !important;
      border: none !important;
      border-radius: 10px !important;
      font-weight: 700 !important;
    }}
    {pp} button[data-testid="stBaseButton-secondary"] {{
      background: rgba(255,255,255,0.85) !important;
      border: 1px solid #E2E8F0 !important;
      border-radius: 8px !important;
      font-weight: 600 !important;
      font-size: 0.75rem !important;
    }}
    {pp} button[data-testid="stBaseButton-tertiary"] {{
      background: transparent !important;
      border: none !important;
      color: #64748B !important;
    }}
    {pp} [class*="st-key-agent_cite_"] button,
    {pp} [class*="st-key-agent_ref_"] button {{
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
    {pp} [class*="st-key-agent_cite_"] button:hover,
    {pp} [class*="st-key-agent_ref_"] button:hover {{
      color: #1D4ED8 !important;
      background: #EFF6FF !important;
      border-radius: 6px !important;
    }}

    @media (max-width: 960px) {{
      {s} .portal-metrics {{ grid-template-columns: repeat(2, 1fr) !important; }}
    }}
    @media (max-width: 768px) {{
      {pp} [data-testid="stMainBlockContainer"],
      {pp} .block-container {{ padding: 54px 1rem 1.5rem !important; }}
      {s} .portal-metrics {{ grid-template-columns: 1fr !important; }}
      {s} .portal-queue-head {{ display: none !important; }}
      {pp} [data-testid="stElementContainer"][class*="st-key-agent_signout"] {{
        right: 1rem !important;
        top: 14px !important;
      }}
    }}
    </style>
    """
