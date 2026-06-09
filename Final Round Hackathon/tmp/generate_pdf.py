"""Generate a professional PDF user manual for ClearHand."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(str(ROOT))

from fpdf import FPDF
from PIL import Image

SCREENSHOTS = ROOT / "tmp" / "screenshots"
OUTPUT = ROOT / "tmp" / "ClearHand_User_Manual.pdf"

PRIMARY = (99, 102, 241)
DARK = (15, 23, 42)
GRAY = (100, 116, 139)
WHITE = (255, 255, 255)

def T(txt):
    """Clean text of unicode chars not in latin-1."""
    return txt.replace("\u2014", "--").replace("\u2013", "-").replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"').replace("\u2022", "*").replace("\u2026", "...").replace("\u00a0", " ").replace("\u2190", "<-").replace("\u2713", "OK").replace("\u2605", "*").replace("\u00b7", "*").replace("\u2022", "*").replace("\u2010", "-").replace("\u2011", "-").replace("\u2012", "-")

class ManualPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GRAY)
            self.cell(0, 8, T("ClearHand User Manual v1.0"), align="L")
            self.cell(0, 8, T(f"Page {self.page_no()}"), align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(200, 200, 210)
            self.line(10, 16, 200, 16)

    def footer(self):
        pass

    def cover_page(self):
        self.add_page()
        self.ln(60)
        self.set_fill_color(*PRIMARY)
        self.rect(0, 50, 210, 6, "F")
        self.set_font("Helvetica", "B", 40)
        self.set_text_color(*DARK)
        self.cell(0, 15, T("ClearHand"), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 18)
        self.set_text_color(*GRAY)
        self.cell(0, 12, T("Multi-Agent IT Ticket Routing & Resolution"), new_x="LMARGIN", new_y="NEXT")
        self.ln(8)
        self.set_font("Helvetica", "", 14)
        self.cell(0, 10, T("User Manual v1.0"), new_x="LMARGIN", new_y="NEXT")
        self.ln(6)
        self.set_font("Helvetica", "I", 11)
        self.set_text_color(*GRAY)
        self.cell(0, 8, T("NASSCOM Hackathon 2026  |  Final Round Submission"), new_x="LMARGIN", new_y="NEXT")
        self.set_fill_color(*PRIMARY)
        self.rect(0, 245, 210, 6, "F")

    def ch_title(self, title):
        self.add_page()
        self.set_x(10)
        self.set_draw_color(*PRIMARY)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(*DARK)
        self.cell(0, 12, T(title), new_x="LMARGIN", new_y="NEXT")
        self.set_x(10)
        self.ln(4)

    def sec_title(self, title):
        self.set_x(10)
        self.ln(3)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*PRIMARY)
        self.cell(0, 10, T(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*PRIMARY)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(3)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.set_x(10)
        self.multi_cell(190, 5.5, T(text))
        self.ln(2)

    def screenshot(self, name, caption=""):
        fp = SCREENSHOTS / f"{name}.png"
        if not fp.exists():
            self.body(f"[Screenshot {name} not found]")
            return
        max_w = 170
        max_h = 110
        with Image.open(fp) as img:
            w, h = img.size
            aspect = w / h
            if w > max_w or h > max_h:
                if aspect > max_w / max_h:
                    w_display = max_w
                    h_display = max_w / aspect
                else:
                    h_display = max_h
                    w_display = max_h * aspect
            else:
                w_display = w * 0.2646
                h_display = h * 0.2646

        x = (210 - w_display) / 2
        self.image(str(fp), x=x, w=w_display, h=h_display)
        if caption:
            self.ln(2)
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(*GRAY)
            self.cell(0, 6, T(caption), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def tip_box(self, text):
        self.ln(2)
        self.set_fill_color(238, 242, 255)
        self.set_draw_color(*PRIMARY)
        y0 = self.get_y()
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        x0 = self.get_x()
        self.set_x(14)
        self.multi_cell(182, 5.5, T(text))
        y1 = self.get_y()
        self.set_fill_color(238, 242, 255)
        self.rect(14, y0, 182, y1 - y0, "F")
        self.set_xy(14, y0)
        self.multi_cell(182, 5.5, T("i  " + text))
        self.set_x(10)
        self.ln(4)


def build():
    pdf = ManualPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Cover ──
    pdf.cover_page()

    # ── TOC ──
    pdf.add_page()
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 14, T("Table of Contents"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(10)
    pdf.ln(6)
    toc = [
        ("1", "Introduction"),
        ("2", "Getting Started"),
        ("  2.1", "Welcome Screen"),
        ("  2.2", "Workspace Gateway"),
        ("  2.3", "Demo Sandbox & Login"),
        ("3", "Employee Portal"),
        ("  3.1", "Home Dashboard"),
        ("  3.2", "New Request Form"),
        ("  3.3", "Self-Help Result (Hand 1)"),
        ("  3.4", "Team Assist Result (Hand 2)"),
        ("  3.5", "Specialist Result (Hand 3)"),
        ("  3.6", "Ticket Detail View"),
        ("4", "Agent Workspace"),
        ("  4.1", "Agent Dashboard"),
        ("  4.2", "Team Queue"),
        ("5", "Admin Console"),
        ("  5.1", "Admin Dashboard"),
        ("  5.2", "Audit Log"),
        ("6", "Dark Mode"),
        ("7", "Frequently Asked Questions"),
    ]
    for num, title in toc:
        is_ch = not num.startswith("  ")
        pdf.set_font("Helvetica", "B" if is_ch else "", 12 if is_ch else 11)
        pdf.set_text_color(*DARK if is_ch else GRAY)
        pdf.cell(0, 8, T(f"{num}  {title}"), new_x="LMARGIN", new_y="NEXT")

    # ════════════════════════════════════════════════
    # CHAPTER 1
    # ════════════════════════════════════════════════
    pdf.ch_title("Chapter 1: Introduction")
    pdf.body(
        "ClearHand is an AI-powered multi-agent system for IT service desk ticket routing and resolution. "
        "It ingests user-submitted support tickets and runs them through a pipeline of five AI agents -- "
        "Guardrail, Classifier, Router, Resolver, and Supervisor -- to produce a decision (Hand 1/2/3) "
        "with a confidence score."
    )
    pdf.body("The three routing outcomes are:")
    pdf.body(
        "  Hand 1 -- Self-Help: The system generates step-by-step resolution instructions for the employee "
        "to follow independently.\n\n"
        "  Hand 2 -- Team Assist: The ticket is routed to the appropriate IT department queue (Hardware, "
        "Software, Network, etc.) for an agent to resolve.\n\n"
        "  Hand 3 -- Specialist: The ticket is escalated for human specialist review (e.g., security incidents)."
    )
    pdf.body(
        "ClearHand provides three role-based portals:\n"
        "  * Employee Portal -- Submit tickets, view resolution steps, provide feedback\n"
        "  * Agent Workspace -- Manage department queue, resolve tickets, track SLA\n"
        "  * Admin Console -- Dashboard with KPIs, audit log, and system monitoring"
    )

    # ════════════════════════════════════════════════
    # CHAPTER 2
    # ════════════════════════════════════════════════
    pdf.ch_title("Chapter 2: Getting Started")
    pdf.body(
        "This chapter walks you through launching the application, signing in, and selecting your workspace. "
        "ClearHand uses a demo sandbox with pre-seeded user profiles so you can explore all features without "
        "setting up a production environment."
    )

    pdf.sec_title("2.1  Welcome Screen")
    pdf.body(
        "When you first launch ClearHand (http://localhost:8501), you are greeted by the welcome screen. "
        "The page showcases the product branding, a dark mode toggle in the top-right corner, and three "
        "feature cards describing the core capabilities: Instant Resolution, Intelligent Routing, and "
        "Governed Escalation."
    )
    pdf.screenshot("01_welcome_screen", "Figure 2.1: Welcome screen with product branding and feature overview")
    pdf.body("To proceed, click the 'Sign In' button centered on the screen. This takes you to the Workspace Gateway.")

    pdf.sec_title("2.2  Workspace Gateway")
    pdf.body(
        "The Workspace Gateway presents two operational tracks to choose from:\n\n"
        "  * Employee Portal -- For submitting support requests and tracking resolutions.\n"
        "  * Agent Workspace -- For IT agents to manage queues and service tickets."
    )
    pdf.screenshot("02_workspace_gateway", "Figure 2.2: Workspace Gateway -- choose your operational track")
    pdf.tip_box("Tip: Hover over each tile to see a brief description. Click the tile to select that workspace.")

    pdf.sec_title("2.3  Demo Sandbox & Login")
    pdf.body(
        "After selecting a workspace, you enter the Demo Sandbox. This page lists pre-seeded user profiles "
        "for demonstration purposes. Each profile represents a different role and department.\n\n"
        "Employee profiles include: Karan Joshi, Emily Reed, James Wu, Sarah Kim, Michael Brown.\n\n"
        "Agent profiles include: Alex Chen (Hardware), Marcus Lee (Software), Priya Nair (Network), "
        "Sam Ortiz (SecOps), Jordan Kim (Identity), Riley Park (DBA), Casey Morgan (Storage), "
        "and the Global System Admin."
    )
    pdf.screenshot("03_demo_sandbox_employee", "Figure 2.3: Demo Sandbox showing available employee profiles")
    pdf.body(
        "Click on any profile to log in as that user. For this manual, we will use Karan Joshi for the "
        "Employee Portal walkthrough."
    )

    # ════════════════════════════════════════════════
    # CHAPTER 3
    # ════════════════════════════════════════════════
    pdf.ch_title("Chapter 3: Employee Portal")
    pdf.body(
        "The Employee Portal is designed for end-users to submit IT support tickets, view resolution "
        "steps, and provide feedback. It features a Jira/ServiceNow-inspired layout with a clean, "
        "modern interface."
    )

    pdf.sec_title("3.1  Home Dashboard")
    pdf.body(
        "Upon logging in as Karan Joshi, you see the Employee Home Dashboard. The page is divided into "
        "several sections:\n\n"
        "  * Profile Card -- Displays your name, email, and organization.\n"
        "  * New Request Card -- Quick access to create a new support ticket.\n"
        "  * Workspace Overview -- KPI metrics showing Open, Resolved, and Total request counts.\n"
        "  * Open Requests -- A collapsible list of pending tickets.\n"
        "  * Closed Requests -- A collapsible list of resolved tickets."
    )
    pdf.screenshot("04_employee_home", "Figure 3.1: Employee Home Dashboard after login")
    pdf.body(
        "From this dashboard, you can click '+ New Request' to begin submitting a ticket, or click 'View' "
        "on any existing ticket to see its details."
    )

    pdf.sec_title("3.2  New Request Form")
    pdf.body(
        "The New Request form collects the following information:\n\n"
        "  * Contact Email -- Pre-filled with your email address.\n"
        "  * Issue Title -- A short summary of the problem.\n"
        "  * Category (optional) -- Choose from Hardware, Software, Network, Security, Access, Other, "
        "or let AI decide.\n"
        "  * Urgency -- Low (P2 / 48h), Medium (P1 / 24h), or High (P0 / 4h).\n"
        "  * Description -- Detailed explanation of the issue.\n"
        "  * Device or Location (optional) -- Where the issue occurred."
    )
    pdf.screenshot("05_new_request_form", "Figure 3.2: New Request form with all fields visible")
    pdf.tip_box(
        "Tip: For best routing accuracy, provide a clear description including error messages, "
        "when the issue started, and any troubleshooting steps you have already tried."
    )

    pdf.sec_title("3.3  Self-Help Result (Hand 1)")
    pdf.body(
        "When a ticket is classified as Self-Help (Hand 1), the system generates step-by-step resolution "
        "instructions. In this example, a password reset request is resolved with guided steps."
    )
    pdf.screenshot("06_ticket_result_self_help", "Figure 3.3: Password reset ticket resolved with Self-Help steps")
    pdf.body(
        "After submission, the ticket detail page shows:\n\n"
        "  * A green routing banner indicating Self-Help guidance is available.\n"
        "  * The ticket metadata grid (Match Strength, Department, Routing, Priority, SLA, etc.).\n"
        "  * Recommended resolution steps listed in order.\n"
        "  * Two feedback buttons: 'Worked' (if the steps resolved it) or 'Did not work' (to escalate)."
    )

    pdf.sec_title("3.4  Team Assist Result (Hand 2)")
    pdf.body(
        "When the system determines that human intervention is needed, the ticket is routed to the "
        "appropriate department queue. In this example, a printer hardware issue is routed to the "
        "Hardware department."
    )
    pdf.screenshot("08_ticket_result_team_assist", "Figure 3.4: Printer issue routed to Hardware team queue")
    pdf.body(
        "Hand 2 tickets display:\n\n"
        "  * A blue routing banner showing the assigned department.\n"
        "  * Priority and SLA information.\n"
        "  * A message indicating the ticket is in the team queue awaiting an agent.\n"
        "  * No automated resolution steps (the agent will handle it)."
    )

    pdf.sec_title("3.5  Specialist Result (Hand 3)")
    pdf.body(
        "Security-related tickets and low-confidence classifications are automatically escalated to "
        "Hand 3 (Specialist). In this example, suspicious login activity triggers an escalation."
    )
    pdf.screenshot("09_ticket_result_specialist", "Figure 3.5: Security incident escalated to Specialist review")
    pdf.body(
        "Hand 3 tickets show:\n\n"
        "  * An amber warning banner: 'Human verification required'.\n"
        "  * A notice that no automated self-help steps are provided.\n"
        "  * Routing to the SecOps (or relevant specialist) team.\n"
        "  * The ticket enters HUMAN_REVIEW status for a specialist to investigate."
    )

    pdf.sec_title("3.6  Ticket Detail View")
    pdf.body(
        "You can view any ticket's full detail by clicking 'View' from the dashboard ticket list. "
        "The detail page provides:\n\n"
        "  * Ticket ID (INC-XXXXXXXX) and title at the top.\n"
        "  * Status, routing badge, and hand classification chips.\n"
        "  * A routing banner explaining the current state.\n"
        "  * Metadata grid with: Match Strength (confidence), Department, Routing, Assignee, "
        "Priority, SLA Target, Urgency, and Opened date.\n"
        "  * Classification category and source.\n"
        "  * Resolution steps (for Hand 1 tickets).\n"
        "  * Feedback buttons (for Hand 1).\n"
        "  * Audit trail showing the agent pipeline trace.\n"
        "  * Comment thread for communication."
    )
    pdf.screenshot("10_ticket_detail", "Figure 3.6: Full ticket detail view with metadata and audit trail")

    # ════════════════════════════════════════════════
    # CHAPTER 4
    # ════════════════════════════════════════════════
    pdf.ch_title("Chapter 4: Agent Workspace")
    pdf.body(
        "The Agent Workspace is designed for IT support agents to manage their department queue, "
        "view ticket details, and resolve tickets. It provides a streamlined interface for triage "
        "and SLA management."
    )

    pdf.sec_title("4.1  Agent Dashboard")
    pdf.body(
        "Logging in as an agent (e.g., Alex Chen from Hardware) takes you to the Agent Dashboard. "
        "This page includes:\n\n"
        "  * Profile card with agent name and department.\n"
        "  * KPI metrics: In Queue count, Department name, Active agents, SLA status.\n"
        "  * Team Queue section showing tickets assigned to the department."
    )
    pdf.screenshot("13_agent_dashboard", "Figure 4.1: Agent Dashboard for Hardware department")
    pdf.tip_box("Note: Agents only see tickets routed to their specific department. A Hardware agent cannot see Software or Network queue tickets.")

    pdf.sec_title("4.2  Team Queue")
    pdf.body(
        "The Team Queue displays all open tickets for the department with the following columns:\n\n"
        "  * Ticket ID (INC-XXXXXXXX) -- Link to view the full detail.\n"
        "  * Summary -- Brief title of the issue.\n"
        "  * Department -- The assigned department.\n"
        "  * Routing -- Hand classification (Self-Help, Team Assist, Specialist).\n"
        "  * Assignee -- Who is working on the ticket.\n\n"
        "Agents can click 'Open' on any ticket to view its full detail and take action."
    )
    pdf.screenshot("14_agent_queue", "Figure 4.2: Team Queue showing open tickets for the Hardware department")
    pdf.body(
        "From the ticket detail view, agents can:\n"
        "  * View the full incident description.\n"
        "  * See AI-suggested resolutions (for Hand 2 tickets).\n"
        "  * Review the audit trail of agent actions.\n"
        "  * Assign, release, or resolve tickets.\n"
        "  * Add comments to the ticket."
    )

    # ════════════════════════════════════════════════
    # CHAPTER 5
    # ════════════════════════════════════════════════
    pdf.ch_title("Chapter 5: Admin Console")
    pdf.body(
        "The Admin Console provides system-wide oversight with KPIs, audit logging, and compliance "
        "monitoring. Administrators can view all tickets across departments and track agent activity."
    )

    pdf.sec_title("5.1  Admin Dashboard")
    pdf.body(
        "Logging in as the Global System Admin reveals the Admin Dashboard with:\n\n"
        "  * KPI metrics: Total Tickets processed, Audit Events count, Active Agents, Policy status.\n"
        "  * Recent audit log events showing the append-only agent trace.\n"
        "  * Overview of the entire system's operation."
    )
    pdf.screenshot("17_admin_dashboard", "Figure 5.1: Admin Dashboard with system-wide metrics and audit events")

    pdf.sec_title("5.2  Audit Log")
    pdf.body(
        "The Audit Log provides a privacy-safe, append-only trace of all agent pipeline activity. "
        "Each entry includes:\n\n"
        "  * Timestamp -- When the event occurred.\n"
        "  * Ticket ID -- The affected ticket (truncated for privacy).\n"
        "  * Agent -- Which agent in the pipeline (Guardrail, Classifier, Router, Resolver, Supervisor).\n"
        "  * Event Type -- What action was performed.\n\n"
        "This log is essential for compliance, troubleshooting, and auditing AI decision-making."
    )
    pdf.screenshot("18_admin_audit_log", "Figure 5.2: Append-only audit log showing agent pipeline trace")

    # ════════════════════════════════════════════════
    # CHAPTER 6
    # ════════════════════════════════════════════════
    pdf.ch_title("Chapter 6: Dark Mode")
    pdf.body(
        "ClearHand includes a full dark mode theme for comfortable use in low-light environments. "
        "The dark mode toggle is available on the welcome screen (before login) in the top-right corner."
    )
    pdf.screenshot("19_dark_mode_welcome", "Figure 6.1: Welcome screen with Dark Mode enabled")
    pdf.body(
        "Dark mode applies to all pages and portals, providing a consistent visual experience. "
        "The setting persists across page navigation but resets on full page refresh."
    )

    # ════════════════════════════════════════════════
    # CHAPTER 7
    # ════════════════════════════════════════════════
    pdf.ch_title("Chapter 7: Frequently Asked Questions")

    faqs = [
        (
            "Q: How does ClearHand decide between Self-Help, Team Assist, and Specialist?",
            "A: The Supervisor agent calculates a confidence score (c_total) based on RAG similarity (60%), "
            "sentiment analysis (20%), and historical success rate (20%). Security issues are always "
            "forced to Specialist (Hand 3). Tickets with low RAG grounding (<0.55 similarity) are "
            "escalated to Team Assist or Specialist."
        ),
        (
            "Q: What happens when I click 'Did not work' on a Self-Help ticket?",
            "A: The ticket is escalated from Hand 1 to Hand 3 (Specialist). The status changes to "
            "HUMAN_REVIEW, and a specialist will investigate the issue manually."
        ),
        (
            "Q: How are tickets routed to the correct department?",
            "A: The Classifier agent categorizes the ticket using Gemini LLM, RAG matching, or keyword "
            "fallback. The Router agent uses a deterministic hash-map lookup to map categories to "
            "department queues (e.g., Hardware -> Hardware, Security -> SecOps)."
        ),
        (
            "Q: Can I add comments to a ticket?",
            "A: Yes. The ticket detail page includes a comment thread where employees, agents, and "
            "admins can communicate. Comments provide context for faster resolution."
        ),
        (
            "Q: How does the system handle prompt injection attacks?",
            "A: The Guardrail agent performs dual-layer defense: (1) Regex pre-check blocks override "
            "phrases before any API call, and (2) Gemini scans the ticket body for injection attempts. "
            "Failed checks force the ticket to Hand 3 / SecOps / P0."
        ),
        (
            "Q: How can I reset demo data?",
            "A: Run 'python scripts/init_db.py && python scripts/seed_users.py' to reinitialize "
            "the database with fresh demo data. Optionally run 'python scripts/seed_rag_demo_tickets.py' "
            "to seed the RAG knowledge base."
        ),
    ]
    for q, a in faqs:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*DARK)
        pdf.set_x(10)
        pdf.multi_cell(190, 6, T(q))
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GRAY)
        pdf.set_x(10)
        pdf.multi_cell(190, 6, T(a))
        pdf.ln(4)

    pdf.output(str(OUTPUT))
    print(f"\nDone: {OUTPUT}")


if __name__ == "__main__":
    build()
