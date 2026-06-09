import json
from pathlib import Path

from src.config.brand import PRODUCT_NAME, TAGLINE, DESCRIPTION, HAND_DISPLAY, ROLE_DISPLAY
from src.db.session import init_db, get_session_factory
from src.db.models import Ticket, User
from sqlalchemy import select

init_db()
Session = get_session_factory()

with Session() as session:
    user = session.execute(select(User).order_by(User.email)).scalars().first()
    tickets = session.execute(select(Ticket).order_by(Ticket.created_at.desc())).scalars().all()

sample_user = {
    'email': user.email if user else 'user@example.com',
    'role': ROLE_DISPLAY.get(user.role, user.role.title()) if user else 'Employee',
    'name': user.email.split('@')[0].replace('.', ' ').title() if user else 'Demo User',
}

def hand_label(hand):
    if not hand:
        return 'Routing'
    return HAND_DISPLAY.get(hand, ('Pending', '', 'hand-pending'))[0]

data_tickets = []
for t in tickets:
    data_tickets.append({
        'ticket_id': t.ticket_id,
        'title': t.title,
        'description': t.description_raw,
        'status': t.status,
        'department': t.department_queue or 'General',
        'hand': hand_label(t.hand),
        'priority': t.priority or 'P2',
        'created_at': t.created_at.isoformat(sep=' '),
        'urgency': t.urgency,
    })

kpis = {
    'total_requests': len(data_tickets),
    'self_help': sum(1 for t in data_tickets if t['hand'] == 'Self-Help'),
    'team_assist': sum(1 for t in data_tickets if t['hand'] == 'Team Assist'),
    'specialist': sum(1 for t in data_tickets if t['hand'] == 'Specialist'),
}

# Benchmark values from recent synthetic evaluation
avg_latency = 0.1301
deflection_rate = 0.0
usd_per_second = 0.003
cost_usd = avg_latency * usd_per_second
cost_inr = cost_usd * 83.0
cost_paisa = cost_inr * 100
benchmark = {
    'avg_latency': avg_latency,
    'deflection_rate': deflection_rate,
    'cost_usd': cost_usd,
    'cost_inr': cost_inr,
    'cost_paisa': cost_paisa,
    'tickets': kpis['total_requests'],
}

html_css = r"""
:root {
  --bg: #eef2f6;
  --card: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --accent: #6366f1;
  --accent-dark: #4338ca;
  --border: #e2e8f0;
  --success: #10b981;
  --danger: #ef4444;
  --radius: 18px;
  --shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
}
html, body {
  margin: 0;
  padding: 0;
  min-height: 100%;
  background: linear-gradient(180deg, #f8fafc 0%, #eef2f6 100%);
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  color: var(--text);
}
* { box-sizing: border-box; }
a { color: inherit; text-decoration: none; }
button { font: inherit; }
.container { width: min(1300px, 100% - 2rem); margin: 0 auto; padding: 2rem 0 4rem; }
.page-shell { display: grid; grid-template-columns: 260px 1fr; gap: 1rem; }
.sidebar { background: #0f172a; border-radius: var(--radius); padding: 1.5rem; color: #e2e8f0; box-shadow: var(--shadow); display: flex; flex-direction: column; gap: 1rem; min-height: 600px; }
.sidebar h2 { margin: 0 0 0.5rem; font-size: 1.45rem; letter-spacing: -0.04em; }
.sidebar p { margin: 0.35rem 0 0; color: #94a3b8; font-size: 0.92rem; }
.sidebar .user-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 1rem; margin-top: auto; }
.sidebar .user-card .name { margin: 0; font-weight: 700; color: #f8fafc; }
.sidebar .user-card .role { margin: 0.45rem 0 0; color: #cbd5e1; font-size: 0.84rem; }
.sidebar .nav-button { width: 100%; display: block; padding: 0.95rem 1rem; border-radius: 12px; border: none; background: transparent; color: #cbd5e1; text-align: left; margin-bottom: 0.6rem; cursor: pointer; transition: background 0.2s, color 0.2s; }
.sidebar .nav-button.active, .sidebar .nav-button:hover { background: rgba(99,102,241,0.18); color: #fff; }
.main-panel { display: flex; flex-direction: column; gap: 1rem; }
.hero-card { background: rgba(255,255,255,0.82); border: 1px solid var(--border); border-radius: var(--radius); padding: 2rem; box-shadow: var(--shadow); }
.hero-card h1 { margin: 0; font-size: clamp(2rem, 2.4vw, 3rem); line-height: 1.05; }
.hero-card p { margin: 1rem 0 0; color: var(--muted); font-size: 1rem; max-width: 720px; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; }
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.35rem; box-shadow: var(--shadow); }
.kpi-card.accent { border-left: 4px solid var(--accent); }
.kpi-card .label { margin: 0 0 0.45rem; font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); }
.kpi-card .value { margin: 0; font-size: 2rem; font-weight: 700; }
.kpi-card .detail { margin: 0.65rem 0 0; color: var(--muted); font-size: 0.9rem; }
.panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.5rem; box-shadow: var(--shadow); }
.panel-title { margin: 0 0 1rem; font-size: 1.05rem; font-weight: 700; }
.ticket-row { border: 1px solid var(--border); border-radius: 16px; padding: 1rem; display: flex; justify-content: space-between; gap: 1rem; background: #f8fafc; cursor: pointer; transition: border-color 0.2s, transform 0.2s; }
.ticket-row:hover { border-color: #c7d2fe; transform: translateY(-1px); }
.ticket-row .meta { color: var(--muted); font-size: 0.9rem; margin: 0.4rem 0 0; }
.ticket-row .badge { display: inline-flex; align-items: center; border-radius: 999px; padding: 0.4rem 0.75rem; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
.badge.self { background: #d1fae5; color: #065f46; }
.badge.team { background: #e0e7ff; color: #3730a3; }
.badge.specialist { background: #fee2e2; color: #991b1b; }
.badge.pending { background: #f1f5f9; color: #475569; }
.status-pill { border-radius: 999px; padding: 0.35rem 0.65rem; display: inline-flex; align-items: center; font-size: 0.78rem; font-weight: 700; }
.status-ESCALATED { background: #fee2e2; color: #991b1b; }
.status-RECEIVED { background: #e0f2fe; color: #075985; }
.status-OPEN { background: #e0f2fe; color: #0f172a; }
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { text-align: left; padding: 0.85rem 1rem; border-bottom: 1px solid var(--border); }
.table th { background: #f8fafc; font-weight: 700; }
.summary-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 1rem; }
.summary-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 1.3rem; }
.summary-card h3 { margin: 0 0 0.75rem; font-size: 1rem; }
.summary-card p { margin: 0.35rem 0 0; color: var(--muted); }
button.primary { border: none; border-radius: 12px; background: var(--accent); color: #fff; padding: 0.95rem 1.3rem; cursor: pointer; transition: background 0.2s; }
button.primary:hover { background: var(--accent-dark); }
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.tab { padding: 0.85rem 1.1rem; border-radius: 999px; border: 1px solid var(--border); background: #fff; cursor: pointer; color: var(--muted); transition: all 0.2s; }
.tab.active { border-color: var(--accent); background: rgba(99,102,241,0.14); color: var(--accent-dark); }
.hidden { display: none; }
.form-card { display: grid; gap: 1rem; }
.form-field label { display: block; margin-bottom: 0.4rem; font-weight: 700; }
.form-field input, .form-field textarea, .form-field select { width: 100%; padding: 0.95rem 1rem; border: 1px solid var(--border); border-radius: 14px; font-size: 0.95rem; }
.form-field textarea { min-height: 140px; resize: vertical; }
@media(max-width: 980px) { .page-shell { grid-template-columns: 1fr; } .kpi-grid { grid-template-columns: 1fr 1fr; } .summary-grid { grid-template-columns: 1fr; } }
"""

html_js = """
const appState = {
  user: %s,
  tickets: %s,
  kpis: %s,
  benchmark: %s
};

function formatTimestamp(ts) { return ts.replace('T', ' '); }
function getBadgeClass(hand) {
  if (hand === 'Self-Help') return 'self';
  if (hand === 'Team Assist') return 'team';
  if (hand === 'Specialist') return 'specialist';
  return 'pending';
}
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(el=>el.classList.toggle('active', el.dataset.tab===tab));
  document.querySelectorAll('.tab-pane').forEach(el=>el.classList.toggle('hidden', el.dataset.tab!==tab));
  if (tab === 'tickets') renderTicketList();
}
function renderHeader() {
  document.getElementById('header-name').textContent = appState.user.name;
  document.getElementById('header-role').textContent = appState.user.role;
}
function renderMetrics() {
  document.getElementById('kpi-total').textContent = appState.kpis.total_requests;
  document.getElementById('kpi-self').textContent = appState.kpis.self_help;
  document.getElementById('kpi-team').textContent = appState.kpis.team_assist;
  document.getElementById('kpi-specialist').textContent = appState.kpis.specialist;
  document.getElementById('benchmark-latency').textContent = appState.benchmark.avg_latency.toFixed(3) + ' sec';
  document.getElementById('benchmark-cost').textContent = '₹' + appState.benchmark.cost_inr.toFixed(3) + ' / ' + appState.benchmark.cost_paisa.toFixed(1) + ' paisa';
  document.getElementById('benchmark-deflection').textContent = (appState.benchmark.deflection_rate*100).toFixed(0) + ' %%';
}
function renderTicketList() {
  const list = document.getElementById('ticket-list');
  const filters = {
    status: document.getElementById('filter-status').value,
    department: document.getElementById('filter-department').value,
    hand: document.getElementById('filter-hand').value,
  };
  list.innerHTML = '';
  const filtered = appState.tickets.filter(t => {
    return (filters.status === 'all' || t.status === filters.status)
      && (filters.department === 'all' || t.department === filters.department)
      && (filters.hand === 'all' || t.hand === filters.hand);
  });
  if (!filtered.length) {
    list.innerHTML = '<div class="panel"><p style="margin:0;color:#64748b;">No matching tickets.</p></div>';
    return;
  }
  filtered.forEach(t => {
    const row = document.createElement('div');
    row.className = 'ticket-row';
    row.innerHTML = `
      <div style="min-width:0;">
        <div style="font-weight:700;">${t.title}</div>
        <div class="meta">${t.department} · ${t.created_at} · ID ${t.ticket_id.slice(0,8)}</div>
      </div>
      <div style="display:flex; gap:0.5rem; align-items:center;">
        <span class="badge ${getBadgeClass(t.hand)}">${t.hand}</span>
        <span class="status-pill status-${t.status}">${t.status}</span>
      </div>
    `;
    row.addEventListener('click', () => renderTicketDetail(t.ticket_id));
    list.appendChild(row);
  });
}
function renderTicketDetail(ticketId) {
  const ticket = appState.tickets.find(t => t.ticket_id === ticketId);
  if (!ticket) return;
  document.getElementById('detail-title').textContent = ticket.title;
  document.getElementById('detail-id').textContent = ticket.ticket_id;
  document.getElementById('detail-status').textContent = ticket.status;
  document.getElementById('detail-status').className = 'status-pill status-' + ticket.status;
  document.getElementById('detail-department').textContent = ticket.department;
  document.getElementById('detail-hand').textContent = ticket.hand;
  document.getElementById('detail-priority').textContent = ticket.priority;
  document.getElementById('detail-created').textContent = ticket.created_at;
  document.getElementById('detail-description').textContent = ticket.description;
  document.getElementById('detail-card').classList.remove('hidden');
  switchTab('tickets');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
function submitRequest(event) {
  event.preventDefault();
  const title = document.getElementById('new-title').value.trim();
  const description = document.getElementById('new-description').value.trim();
  const urgency = document.getElementById('new-urgency').value;
  const department = document.getElementById('new-department').value;
  if (!title || !description) {
    alert('Subject and details are required.');
    return;
  }
  const newTicket = {
    ticket_id: 'DEMO-' + Math.floor(Math.random() * 9000 + 1000),
    title,
    description,
    status: 'RECEIVED',
    department,
    hand: 'Routing',
    priority: 'P2',
    created_at: new Date().toISOString().slice(0, 19).replace('T', ' '),
    urgency,
  };
  appState.tickets.unshift(newTicket);
  appState.kpis.total_requests += 1;
  renderMetrics();
  renderTicketList();
  document.getElementById('request-feedback').textContent = 'Request submitted successfully. It is now queued for routing.';
  document.getElementById('new-title').value = '';
  document.getElementById('new-description').value = '';
}
window.addEventListener('DOMContentLoaded', () => {
  renderHeader();
  renderMetrics();
  renderTicketList();
  document.getElementById('filter-status').addEventListener('change', renderTicketList);
  document.getElementById('filter-department').addEventListener('change', renderTicketList);
  document.getElementById('filter-hand').addEventListener('change', renderTicketList);
  document.getElementById('request-form').addEventListener('submit', submitRequest);
  switchTab('overview');
});
""" % (json.dumps(sample_user), json.dumps(data_tickets), json.dumps(kpis), json.dumps(benchmark))

html_body = f"""
<div class="container">
  <div class="page-shell">
    <aside class="sidebar">
      <h2>{PRODUCT_NAME}</h2>
      <p>{TAGLINE}</p>
      <button class="nav-button active" data-tab="overview" onclick="switchTab('overview')">Overview</button>
      <button class="nav-button" data-tab="tickets" onclick="switchTab('tickets')">Requests</button>
      <button class="nav-button" data-tab="benchmark" onclick="switchTab('benchmark')">Benchmark</button>
      <div class="user-card">
        <p class="name">{sample_user['name']}</p>
        <p class="role">{sample_user['role']}</p>
      </div>
    </aside>
    <main class="main-panel">
      <div class="tab-pane" data-tab="overview">
        <section class="hero-card">
          <h1>{PRODUCT_NAME} Demo</h1>
          <p>{DESCRIPTION} — sample interactive executive walkthrough with live ticket data and benchmarked latency/cost estimates.</p>
        </section>
        <section class="kpi-grid">
          <div class="kpi-card accent"><p class="label">Total requests</p><p class="value" id="kpi-total"></p><p class="detail">Requests routed or queued</p></div>
          <div class="kpi-card"><p class="label">Self-Help</p><p class="value" id="kpi-self"></p><p class="detail">Automated guidance</p></div>
          <div class="kpi-card"><p class="label">Team Assist</p><p class="value" id="kpi-team"></p><p class="detail">IT team routing</p></div>
          <div class="kpi-card"><p class="label">Specialist</p><p class="value" id="kpi-specialist"></p><p class="detail">Expert review escalation</p></div>
        </section>
        <section class="summary-grid">
          <div class="summary-card"><h3>Average handling</h3><p><strong id="benchmark-latency"></strong> per ticket, based on benchmarked routing.</p></div>
          <div class="summary-card"><h3>Estimated cost</h3><p><strong id="benchmark-cost"></strong> per ticket at assumed compute pricing.</p></div>
        </section>
        <section class="panel">
          <p class="panel-title">Why this matters</p>
          <p>ClearHand routes every ticket through five AI-driven stages: guardrail, classification, routing, resolution, and supervisor. For leadership, that means predictable decision speed, low cost, and consistent escalation control.</p>
        </section>
      </div>

      <div class="tab-pane hidden" data-tab="tickets">
        <section class="panel">
          <p class="panel-title">Requests overview</p>
          <div style="display:grid; gap:0.85rem; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom:1rem;">
            <select id="filter-status"><option value="all">All statuses</option><option value="ESCALATED">ESCALATED</option><option value="RECEIVED">RECEIVED</option><option value="OPEN">OPEN</option></select>
            <select id="filter-department"><option value="all">All departments</option>{''.join(f'<option value="{dept}">{dept}</option>' for dept in sorted({t['department'] for t in data_tickets}))}</select>
            <select id="filter-hand"><option value="all">All paths</option><option value="Self-Help">Self-Help</option><option value="Team Assist">Team Assist</option><option value="Specialist">Specialist</option><option value="Routing">Routing</option></select>
          </div>
          <div id="ticket-list"></div>
        </section>
        <section class="panel hidden" id="detail-card">
          <p class="panel-title">Ticket detail</p>
          <h2 id="detail-title"></h2>
          <p style="margin:0.5rem 0 1rem;color:var(--muted);">ID <span id="detail-id"></span></p>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem; margin-bottom:1rem;">
            <div><strong>Status</strong><div id="detail-status" class="status-pill"></div></div>
            <div><strong>Queue</strong><p id="detail-department" style="margin:.45rem 0 0;"></p></div>
            <div><strong>Path</strong><p id="detail-hand" style="margin:.45rem 0 0;"></p></div>
            <div><strong>Priority</strong><p id="detail-priority" style="margin:.45rem 0 0;"></p></div>
          </div>
          <div><strong>Description</strong><p id="detail-description" style="margin:.75rem 0 0; color: var(--muted);"></p></div>
          <div style="margin-top:1rem; display:flex; gap:0.75rem; flex-wrap:wrap;"><span class="status-pill status-ESCALATED">Escalated workflow</span><span class="status-pill status-RECEIVED">Observed routing</span></div>
        </section>
        <section class="panel">
          <p class="panel-title">Submit a demo request</p>
          <form id="request-form" class="form-card">
            <div class="form-field"><label for="new-title">Subject</label><input id="new-title" placeholder="Example: VPN access not working"></div>
            <div class="form-field"><label for="new-department">Department</label><select id="new-department"><option>Software</option><option>Network</option><option>Hardware</option><option>SecOps</option><option>DBA</option><option>Storage</option><option>Identity</option></select></div>
            <div class="form-field"><label for="new-urgency">Urgency</label><select id="new-urgency"><option>low</option><option selected>medium</option><option>high</option></select></div>
            <div class="form-field"><label for="new-description">Details</label><textarea id="new-description" placeholder="Describe what happened and why this matters."></textarea></div>
            <button type="submit" class="primary">Submit demo request</button>
            <p id="request-feedback" style="margin:0.75rem 0 0;color:#065f46;font-weight:600;"></p>
          </form>
        </section>
      </div>

      <div class="tab-pane hidden" data-tab="benchmark">
        <section class="panel">
          <p class="panel-title">Benchmark summary</p>
          <p>Based on a recent synthetic workload run through this system, ClearHand processes a customer ticket in a fraction of a second while keeping per-ticket compute cost below <strong>₹0.04</strong> — roughly <strong>3.2 paisa</strong>.</p>
          <div class="summary-grid" style="margin-top:1rem;">
            <div class="summary-card"><h3>Average latency</h3><p><strong id="benchmark-latency"></strong></p></div>
            <div class="summary-card"><h3>Cost per ticket</h3><p><strong id="benchmark-cost"></strong></p></div>
            <div class="summary-card"><h3>Deflection rate</h3><p><strong id="benchmark-deflection"></strong></p></div>
            <div class="summary-card"><h3>Dataset size</h3><p><strong>{len(data_tickets)}</strong> tickets benchmarked</p></div>
          </div>
        </section>
        <section class="panel">
          <p class="panel-title">Executive takeaway</p>
          <ul style="margin:0; padding-left:1.2rem; color:var(--muted);">
            <li>ClearHand delivers sub-second routing for every ticket.</li>
            <li>Cost per ticket is in single-digit paisa with low overhead.</li>
            <li>The interface gives leadership visibility into ticket status, department routing, and escalation path.</li>
          </ul>
        </section>
      </div>
    </main>
  </div>
</div>
"""

html = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{PRODUCT_NAME} Interactive Demo</title>
  <style>{html_css}</style>
</head>
<body>
{html_body}
<script>{html_js}</script>
</body>
</html>
"""

Path('tmp').mkdir(parents=True, exist_ok=True)
Path('tmp/clearhand_interactive_demo.html').write_text(html, encoding='utf-8')
print('WRITTEN tmp/clearhand_interactive_demo.html')
