# ============================================================
# Customer Support & Helpdesk Analytics Dashboard  v2
# Single-Cell Google Colab Script — BUG-FREE
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from IPython.display import display, HTML

# ── Seed for reproducibility ────────────────────────────────
np.random.seed(42)

# ============================================================
# STEP 1 — GENERATE REALISTIC HELPDESK DATA
# ============================================================
n = 5000

ticket_ids = [f"TKT-{str(i).zfill(5)}" for i in range(1, n + 1)]

start_date = pd.Timestamp("2024-01-01")
end_date   = pd.Timestamp("2024-06-30 23:59:59")
created_dates = pd.to_datetime(
    np.random.randint(start_date.value, end_date.value, n)
)

categories = np.random.choice(
    ['Technical Issue', 'Billing', 'Account Access', 'Feature Request', 'Bug Report'],
    size=n, p=[0.30, 0.22, 0.18, 0.15, 0.15]
)
priorities = np.random.choice(
    ['Low', 'Medium', 'High', 'Urgent'],
    size=n, p=[0.25, 0.35, 0.25, 0.15]
)

frt_map = {'Urgent': (5, 30), 'High': (15, 60), 'Medium': (30, 120), 'Low': (60, 240)}
frt_mins = np.array([np.random.randint(*frt_map[p]) for p in priorities])

base_res = {'Urgent': (1, 8), 'High': (4, 24), 'Medium': (8, 48), 'Low': (12, 72)}
resolution_hours = np.array([np.random.uniform(*base_res[p]) for p in priorities])
bug_mask = categories == 'Bug Report'
resolution_hours[bug_mask] *= np.random.uniform(1.3, 1.8, bug_mask.sum())
resolution_hours = np.round(resolution_hours, 2)

res_min, res_max = resolution_hours.min(), resolution_hours.max()
res_norm = (resolution_hours - res_min) / (res_max - res_min)
csat_float = 5 - (res_norm * 3.5) + np.random.normal(0, 0.4, n)
csat_scores = np.clip(np.round(csat_float).astype(int), 1, 5)

df = pd.DataFrame({
    'Ticket_ID':                ticket_ids,
    'Created_Date':             created_dates,
    'Category':                 categories,
    'Priority':                 priorities,
    'First_Response_Time_Mins': frt_mins,
    'Resolution_Time_Hours':    resolution_hours,
    'CSAT_Score':               csat_scores,
})

print(f"✅ Generated {len(df):,} tickets  |  Date range: {df.Created_Date.min().date()} → {df.Created_Date.max().date()}")
print(df.head(3).to_string())

# ============================================================
# STEP 2 — CALCULATE KPIs
# ============================================================
total_tickets  = len(df)
avg_frt        = round(df['First_Response_Time_Mins'].mean(), 1)
avg_resolution = round(df['Resolution_Time_Hours'].mean(), 2)
avg_csat       = round(df['CSAT_Score'].mean(), 2)

print(f"\n📊 KPIs")
print(f"   Total Tickets      : {total_tickets:,}")
print(f"   Avg FRT            : {avg_frt} mins")
print(f"   Avg Resolution     : {avg_resolution} hrs")
print(f"   Avg CSAT           : {avg_csat} / 5.0")

# ============================================================
# STEP 3 — PLOTLY FIGURES
# ============================================================
PALETTE = {
    'ocean':   '#2196F3',
    'coral':   '#FF6B6B',
    'amber':   '#FFB347',
    'slate':   '#78909C',
    'teal':    '#26C6DA',
    'violet':  '#AB47BC',
    'bg':      '#0f172a',
    'card':    '#1e293b',
    'text':    '#e2e8f0',
    'subtext': '#94a3b8',
    'grid':    '#334155',
}

# ── FIX: pre-define rgba fill colors as proper rgba() strings ──
# Plotly go.Box fillcolor does NOT support 8-digit hex (#RRGGBBAA).
# Must use rgba(R, G, B, A) format.
BOX_COLORS = {
    'Low':    {'line': '#78909C', 'fill': 'rgba(120,144,156,0.25)'},
    'Medium': {'line': '#2196F3', 'fill': 'rgba(33,150,243,0.25)'},
    'High':   {'line': '#FFB347', 'fill': 'rgba(255,179,71,0.25)'},
    'Urgent': {'line': '#FF6B6B', 'fill': 'rgba(255,107,107,0.25)'},
}

CAT_COLORS = [
    PALETTE['ocean'], PALETTE['coral'], PALETTE['amber'],
    PALETTE['teal'],  PALETTE['violet']
]

LAYOUT_BASE = dict(
    paper_bgcolor=PALETTE['card'],
    plot_bgcolor =PALETTE['card'],
    font=dict(family='Segoe UI, sans-serif', color=PALETTE['text'], size=13),
    margin=dict(t=60, b=40, l=40, r=30),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=PALETTE['text'])),
)

# ── Figure 1: Donut — Ticket Volume by Category ─────────────
cat_counts = df['Category'].value_counts().reset_index()
cat_counts.columns = ['Category', 'Count']

fig_category = go.Figure(go.Pie(
    labels=cat_counts['Category'],
    values=cat_counts['Count'],
    hole=0.5,
    marker=dict(colors=CAT_COLORS, line=dict(color=PALETTE['bg'], width=2)),
    textinfo='label+percent',
    textfont=dict(size=12, color=PALETTE['text']),
    hovertemplate='<b>%{label}</b><br>Tickets: %{value:,}<br>Share: %{percent}<extra></extra>',
))
fig_category.update_layout(
    **LAYOUT_BASE,
    title=dict(
        text='Ticket Volume by Category',
        font=dict(size=16, color=PALETTE['text']),
        x=0.5, xanchor='center'
    ),
    showlegend=True,
)

# ── Figure 2: Bar — Avg CSAT by Category ────────────────────
csat_by_cat = df.groupby('Category')['CSAT_Score'].mean().reset_index()
csat_by_cat.columns = ['Category', 'Avg_CSAT']
csat_by_cat = csat_by_cat.sort_values('Avg_CSAT', ascending=False)

fig_csat = go.Figure()
fig_csat.add_trace(go.Bar(
    x=csat_by_cat['Category'],
    y=csat_by_cat['Avg_CSAT'],
    marker=dict(
        color=csat_by_cat['Avg_CSAT'],
        colorscale=[[0, PALETTE['coral']], [0.5, PALETTE['amber']], [1, PALETTE['teal']]],
        showscale=False,
        line=dict(color=PALETTE['bg'], width=1),
    ),
    text=csat_by_cat['Avg_CSAT'].round(2),
    textposition='outside',
    textfont=dict(color=PALETTE['text'], size=12),
    hovertemplate='<b>%{x}</b><br>Avg CSAT: %{y:.2f}<extra></extra>',
))
fig_csat.add_hline(
    y=4.2,
    line=dict(color=PALETTE['amber'], width=2, dash='dash'),
    annotation_text='Target: 4.2',
    annotation_font=dict(color=PALETTE['amber'], size=12),
    annotation_position='top right',
)
fig_csat.update_layout(
    **LAYOUT_BASE,
    title=dict(
        text='Customer Satisfaction (CSAT) by Category',
        font=dict(size=16, color=PALETTE['text']),
        x=0.5, xanchor='center'
    ),
    xaxis=dict(title='Category',          color=PALETTE['subtext'], showgrid=False, zeroline=False),
    yaxis=dict(title='Avg CSAT Score',    color=PALETTE['subtext'], range=[0, 5.5],
               gridcolor=PALETTE['grid'], zeroline=False),
)

# ── Figure 3: Box — Resolution Time by Priority ─────────────
# FIX: fillcolor must be rgba() string, NOT 8-digit hex
priority_order = ['Low', 'Medium', 'High', 'Urgent']

fig_resolution = go.Figure()
for pri in priority_order:
    subset = df[df['Priority'] == pri]['Resolution_Time_Hours']
    fig_resolution.add_trace(go.Box(
        y=subset,
        name=pri,
        marker_color=BOX_COLORS[pri]['line'],
        line=dict(color=BOX_COLORS[pri]['line'], width=2),
        fillcolor=BOX_COLORS[pri]['fill'],          # ← proper rgba() string
        boxmean='sd',
        hovertemplate=f'<b>{pri}</b><br>Resolution: %{{y:.1f}} hrs<extra></extra>',
    ))

fig_resolution.update_layout(
    **LAYOUT_BASE,
    title=dict(
        text='Resolution Time Distribution by Priority',
        font=dict(size=16, color=PALETTE['text']),
        x=0.5, xanchor='center'
    ),
    xaxis=dict(
        title='Priority',
        color=PALETTE['subtext'],
        showgrid=False,
        categoryorder='array',
        categoryarray=priority_order,           # exact order: Low → Medium → High → Urgent
    ),
    yaxis=dict(
        title='Resolution Time (Hours)',
        color=PALETTE['subtext'],
        gridcolor=PALETTE['grid'],
        zeroline=False,
    ),
    showlegend=False,
)

print("\n✅ All 3 Plotly figures created successfully.")

# ============================================================
# STEP 4 — BUILD PURE HTML/CSS DASHBOARD
# ============================================================
html_category   = fig_category.to_html(full_html=False, include_plotlyjs=False)
html_csat       = fig_csat.to_html(full_html=False, include_plotlyjs=False)
html_resolution = fig_resolution.to_html(full_html=False, include_plotlyjs=False)

csat_color = '#22c55e' if avg_csat >= 4.0 else '#f97316'
csat_badge = '▲ On Target' if avg_csat >= 4.0 else '▼ Below Target'

dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Helpdesk Analytics Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:      #0f172a;
      --card:    #1e293b;
      --border:  #334155;
      --text:    #e2e8f0;
      --subtext: #94a3b8;
      --ocean:   #2196F3;
      --coral:   #FF6B6B;
      --amber:   #FFB347;
      --teal:    #26C6DA;
    }}

    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'IBM Plex Sans', sans-serif;
      min-height: 100vh;
      padding: 32px 28px;
    }}

    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 32px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
    }}
    header h1 {{
      font-size: 1.6rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(135deg, var(--ocean), var(--teal));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    header p {{
      font-size: 0.82rem;
      color: var(--subtext);
      font-family: 'IBM Plex Mono', monospace;
      margin-top: 4px;
    }}
    .badge {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 6px 14px;
      font-size: 0.78rem;
      color: var(--subtext);
      font-family: 'IBM Plex Mono', monospace;
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }}
    @media (max-width: 900px) {{ .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }} }}

    .kpi-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 22px 20px 18px;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s, border-color 0.2s;
    }}
    .kpi-card:hover {{ transform: translateY(-2px); border-color: var(--ocean); }}
    .kpi-card::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
    }}
    .kpi-card.blue::before   {{ background: var(--ocean); }}
    .kpi-card.coral::before  {{ background: var(--coral); }}
    .kpi-card.amber::before  {{ background: var(--amber); }}
    .kpi-card.csat::before   {{ background: {csat_color}; }}

    .kpi-label {{
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--subtext);
      margin-bottom: 10px;
    }}
    .kpi-value {{
      font-size: 2rem;
      font-weight: 700;
      line-height: 1;
      font-family: 'IBM Plex Mono', monospace;
    }}
    .kpi-unit {{ font-size: 0.85rem; color: var(--subtext); margin-left: 4px; }}
    .kpi-sub  {{ margin-top: 8px; font-size: 0.75rem; color: var(--subtext); }}
    .csat-badge {{
      display: inline-block;
      margin-top: 8px;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
      background: {csat_color}22;
      color: {csat_color};
      border: 1px solid {csat_color}44;
    }}

    .chart-grid-top {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }}
    @media (max-width: 820px) {{ .chart-grid-top {{ grid-template-columns: 1fr; }} }}

    .chart-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 8px;
      overflow: hidden;
    }}
    .chart-card .plotly-graph-div {{ width: 100% !important; }}

    footer {{
      margin-top: 28px;
      text-align: center;
      font-size: 0.72rem;
      color: var(--subtext);
      font-family: 'IBM Plex Mono', monospace;
      padding-top: 16px;
      border-top: 1px solid var(--border);
    }}
  </style>
</head>
<body>

<header>
  <div>
    <h1>Helpdesk Support Analytics</h1>
    <p>Jan 2024 – Jun 2024 &nbsp;|&nbsp; 5,000 Tickets &nbsp;|&nbsp; Live Dashboard</p>
  </div>
  <div class="badge">Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</div>
</header>

<section class="kpi-grid">
  <div class="kpi-card blue">
    <div class="kpi-label">Total Tickets</div>
    <div class="kpi-value">{total_tickets:,}</div>
    <div class="kpi-sub">Across all categories</div>
  </div>
  <div class="kpi-card coral">
    <div class="kpi-label">Avg First Response</div>
    <div class="kpi-value">{avg_frt}<span class="kpi-unit">min</span></div>
    <div class="kpi-sub">First Response Time</div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-label">Avg Resolution</div>
    <div class="kpi-value">{avg_resolution}<span class="kpi-unit">hrs</span></div>
    <div class="kpi-sub">Mean Time to Resolve</div>
  </div>
  <div class="kpi-card csat">
    <div class="kpi-label">Avg CSAT Score</div>
    <div class="kpi-value" style="color:{csat_color}">{avg_csat}<span class="kpi-unit">/ 5.0</span></div>
    <div class="csat-badge">{csat_badge}</div>
  </div>
</section>

<section class="chart-grid-top">
  <div class="chart-card">{html_category}</div>
  <div class="chart-card">{html_csat}</div>
</section>

<section>
  <div class="chart-card">{html_resolution}</div>
</section>

<footer>
  Customer Support &amp; Helpdesk Analytics Dashboard &nbsp;·&nbsp; Built with Plotly &amp; Python
</footer>

</body>
</html>
"""

# ============================================================
# STEP 5 — EXPORT & AUTO-DOWNLOAD
# ============================================================
output_file = "Helpdesk_Support_Dashboard.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(dashboard_html)

print(f"\n✅ Dashboard saved → '{output_file}'  ({len(dashboard_html):,} chars)")

try:
    from google.colab import files
    files.download(output_file)
    print("⬇️  Download initiated.")
except ImportError:
    print("ℹ️  Not in Colab — file saved locally.")

display(HTML(f"""
<div style="background:#1e293b;color:#e2e8f0;padding:14px 18px;border-radius:8px;
            font-family:monospace;font-size:13px;border:1px solid #334155;margin-top:12px;">
  ✅ <b>Dashboard ready!</b><br>
  📄 File: <code>{output_file}</code><br>
  🎫 Tickets: {total_tickets:,} &nbsp;|&nbsp;
  ⏱ Avg FRT: {avg_frt} min &nbsp;|&nbsp;
  🕐 Avg Res: {avg_resolution} hrs &nbsp;|&nbsp;
  ⭐ Avg CSAT: <span style="color:{'#22c55e' if avg_csat>=4 else '#f97316'}">{avg_csat}/5.0</span>
</div>
"""))
