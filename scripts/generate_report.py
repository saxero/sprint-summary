#!/usr/bin/env python3
"""
Sprint Summary Report - Main orchestrator
Combines analysis and HTML generation in one script.
"""

import argparse
import json
import sys
import math
from datetime import datetime
from pathlib import Path
import pandas as pd

DATE_FORMAT = '%d/%b/%y %I:%M %p'

def parse_date(s):
    """Parse Jira date format."""
    if pd.isna(s) or s == '':
        return None
    try:
        return datetime.strptime(str(s).strip(), DATE_FORMAT)
    except ValueError:
        return None

def analyze(csv_path, sprint_start, sprint_end):
    """Analyze CSV and extract sprint metrics."""
    df = pd.read_csv(csv_path)
    
    # Parse dates
    df['created_dt'] = df['Created'].apply(parse_date)
    df['resolved_dt'] = df['Resolved'].apply(parse_date)
    df['status_changed_dt'] = df['Status Category Changed'].apply(parse_date)
    df['status'] = df['Status'].fillna('Unknown')
    df['issue_key'] = df['Issue key']
    df['issue_type'] = df['Issue Type'].fillna('Unknown')
    
    now = datetime.now()
    
    # Ensure dates are datetime objects
    if isinstance(sprint_start, str):
        sprint_start = datetime.strptime(sprint_start, '%Y-%m-%d')
    if isinstance(sprint_end, str):
        sprint_end = datetime.strptime(sprint_end, '%Y-%m-%d')
    
    sprint_start_dt = datetime.combine(sprint_start.date(), datetime.min.time())
    sprint_end_dt = datetime.combine(sprint_end.date(), datetime.min.time())
    
    # Define closed statuses
    closed_statuses = ['Closed', 'Done', 'Rejected']
    df['is_closed'] = df['status'].isin(closed_statuses)
    
    # Count tickets
    total_items = len(df)
    closed_items = df[df['is_closed']].shape[0]
    open_items = total_items - closed_items
    pct_done = round(closed_items / max(total_items, 1) * 100)
    
    # Count leftovers (items that were open before sprint start)
    leftovers = 0
    for idx, row in df.iterrows():
        created = row['created_dt']
        if created and created < sprint_start_dt and not row['is_closed']:
            leftovers += 1
    
    # Prepare scatter data
    scatter_items = []
    for idx, row in df.iterrows():
        created = row['created_dt']
        status_changed = row['status_changed_dt']
        if not created:
            continue

        # Use status change date as start date if item is Open and has status change date
        # Otherwise fall back to creation date
        if row['status'] == 'Open' and status_changed:
            start_date = status_changed
        else:
            start_date = created

        # Calculate age from the appropriate start date
        age = (now - start_date).days

        # Only include items created before or at sprint end
        if created <= sprint_end_dt:
            scatter_items.append({
                'key': row['issue_key'],
                'type': row['issue_type'],
                'status': row['status'],
                'age_days': age,
                'is_closed': row['is_closed'],
                'summary': row.get('Summary', 'Sin título'),
                'assignee': row.get('Assignee', 'Sin asignar')
            })
    
    # Sort by age (descending) for display
    scatter_items.sort(key=lambda x: x['age_days'], reverse=True)
    
    # Get sprint name
    sprint_name = 'Sprint'
    if 'Sprint' in df.columns:
        sprints = df['Sprint'].dropna().value_counts()
        if len(sprints) > 0:
            sprint_name = sprints.index[0]

    # Status distribution for table (Done, In Progress, Not started)
    # Completados = Done + Closed + Rejected
    # Abiertos = Open + In Progress
    # Not started = resto (New, Aceptado, etc.)
    status_counts = df['status'].value_counts().to_dict()
    done_count = status_counts.get('Done', 0) + status_counts.get('Closed', 0) + status_counts.get('Rejected', 0)
    in_progress_count = status_counts.get('Open', 0) + status_counts.get('In Progress', 0)
    not_started_count = total_items - done_count - in_progress_count
    status_table = {
        'done': done_count,
        'in_progress': in_progress_count,
        'not_started': not_started_count,
    }

    # Calculate sprint progress and days remaining
    sprint_duration = (sprint_end_dt - sprint_start_dt).days
    days_elapsed = (now - sprint_start_dt).days
    days_remaining = max(0, (sprint_end_dt - now).days)
    time_progress = min(100, max(0, (days_elapsed / sprint_duration * 100))) if sprint_duration > 0 else 0
    velocity_needed = (total_items - closed_items) / max(1, days_remaining) if days_remaining > 0 else 0

    # Find oldest open items (at risk)
    open_items_list = [item for item in scatter_items if not item['is_closed']]
    oldest_items = sorted(open_items_list, key=lambda x: x['age_days'], reverse=True)[:3]

    # Count items at risk (>14 days moderate, >28 days high)
    moderate_risk = sum(1 for item in open_items_list if 14 < item['age_days'] <= 28)
    high_risk = sum(1 for item in open_items_list if item['age_days'] > 28)

    # Generate highlights
    highlights = []

    # Highlight 1: Sprint pace vs completion
    if pct_done < time_progress - 15:
        highlights.append({
            'icon': '⚠️',
            'title': 'Ritmo de sprint por debajo del objetivo',
            'description': f'El sprint lleva {days_elapsed} días ({time_progress:.0f}% del tiempo) pero solo {pct_done}% está completado. Se necesita completar {velocity_needed:.1f} tickets/día para terminar a tiempo.'
        })
    elif days_remaining <= 2 and pct_done < 80:
        highlights.append({
            'icon': '⏰',
            'title': 'Sprint próximo a cerrar con bajo completion',
            'description': f'Quedan solo {days_remaining} días y el sprint está al {pct_done}%. Considera reducir alcance o extender el sprint.'
        })
    else:
        highlights.append({
            'icon': '📊',
            'title': 'Ritmo de sprint estable',
            'description': f'Sprint al {pct_done}% completado con {days_remaining} días restantes. Velocidad actual suficiente para completar el objetivo.'
        })

    # Highlight 2: Work in progress bottleneck
    wip_ratio = in_progress_count / max(1, total_items - done_count)
    if in_progress_count > done_count * 2:
        highlights.append({
            'icon': '🚧',
            'title': 'Acumulación de trabajo en progreso',
            'description': f'Hay {in_progress_count} tickets en progreso vs {done_count} completados. El equipo tiene demasiado WIP, lo que retrasa la entrega. Considera limitar WIP y enfocar en terminar lo iniciado.'
        })
    elif not_started_count > (done_count + in_progress_count):
        highlights.append({
            'icon': '🆕',
            'title': 'Muchos tickets sin iniciar',
            'description': f'{not_started_count} tickets aún no iniciados ({not_started_count/total_items*100:.0f}% del total). Prioriza iniciar el trabajo para evitar bloqueos al final del sprint.'
        })
    else:
        highlights.append({
            'icon': '✅',
            'title': 'Distribución de trabajo balanceada',
            'description': f'La distribución entre completados ({done_count}), en progreso ({in_progress_count}) y pendientes ({not_started_count}) es saludable. Mantener el foco en completar lo iniciado.'
        })

    # Highlight 3: Risk items (age)
    if high_risk > 0:
        highlights.append({
            'icon': '🔴',
            'title': f'{high_risk} tickets con alto riesgo por antigüedad',
            'description': f'Hay {high_risk} tickets abiertos hace más de 28 días. El más antiguo es {oldest_items[0]["key"]} ({oldest_items[0]["age_days"]} días). Requiere atención inmediata para evitar carry-over.'
        })
    elif moderate_risk > 0:
        highlights.append({
            'icon': '🟡',
            'title': f'{moderate_risk} tickets en riesgo moderado',
            'description': f'Hay {moderate_risk} tickets entre 14-28 días de antigüedad. Considera priorizar {oldest_items[0]["key"]} ({oldest_items[0]["age_days"]} días) para prevenir bloqueos.'
        })
    else:
        highlights.append({
            'icon': '🟢',
            'title': 'Tickets dentro de tiempos aceptables',
            'description': f'La antigüedad de tickets abiertos está controlada. El más antiguo tiene {oldest_items[0]["age_days"] if oldest_items else 0} días. Buen ritmo de refinamiento y priorización.'
        })

    return {
        'meta': {
            'sprint_name': sprint_name,
            'sprint_start': sprint_start_dt.strftime('%Y-%m-%d'),
            'sprint_end': sprint_end_dt.strftime('%Y-%m-%d'),
            'generated_at': now.strftime('%Y-%m-%d %H:%M'),
        },
        'kpis': {
            'total_items': total_items,
            'closed_items': closed_items,
            'open_items': open_items,
            'pct_done': pct_done,
            'leftovers': leftovers,
        },
        'status_table': status_table,
        'scatter_items': scatter_items,
        'highlights': highlights,
        'sprint_metrics': {
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'time_progress': round(time_progress, 1),
            'velocity_needed': round(velocity_needed, 1),
            'moderate_risk': moderate_risk,
            'high_risk': high_risk,
        }
    }

def generate_html(data):
    """Generate HTML report from analysis data."""
    m = data['meta']
    k = data['kpis']
    scatter = data['scatter_items']
    
    # Prepare scatter plot data
    scatter_data_points = []
    for i, item in enumerate(scatter):
        # Spread items horizontally
        x = (i % 5) - 2
        y = item['age_days']
        scatter_data_points.append({
            'x': x,
            'y': y,
            'key': item['key'],
            'status': item['status'],
            'type': item['type'],
            'summary': item['summary'],
            'assignee': item['assignee']
        })
    
    max_age = max((p['y'] for p in scatter_data_points), default=30)
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sprint Report — {m['sprint_name']}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', system-ui, sans-serif;
  background: #ffffff;
  color: #1d1d1f;
  padding: 2.5rem 3rem;
  max-width: 1200px;
  margin: 0 auto;
}}
.header {{
  margin-bottom: 2.5rem;
  border-bottom: 1px solid #f5f5f7;
  padding-bottom: 1.5rem;
}}
h1 {{
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}}
.meta {{
  font-size: 14px;
  color: #86868b;
}}
.kpis {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 2rem;
}}
.kpi {{
  background: #f5f5f7;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}}
.kpi-label {{
  font-size: 12px;
  color: #86868b;
  font-weight: 500;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.kpi-value {{
  font-size: 42px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}}
.kpi-unit {{
  font-size: 14px;
  color: #86868b;
  font-weight: 400;
}}
.progress-bar {{
  width: 100%;
  height: 12px;
  background: #e8e8ed;
  border-radius: 6px;
  overflow: hidden;
  margin-top: 12px;
}}
.progress-fill {{
  height: 100%;
  background: linear-gradient(90deg, #34c759 0%, #0071e3 100%);
  transition: width 0.3s ease;
}}
.section {{
  margin-bottom: 2.5rem;
}}
.section-title {{
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}}
.card {{
  background: #ffffff;
  border: 1px solid #f5f5f7;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}}
.chart-container {{
  position: relative;
  width: 100%;
  height: 400px;
  margin-bottom: 1rem;
}}
.legend {{
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 12px;
  font-size: 13px;
  color: #86868b;
}}
.legend-item {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.legend-dot {{
  width: 10px;
  height: 10px;
  border-radius: 50%;
}}
.risk-zones {{
  display: flex;
  gap: 20px;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f5f5f7;
  font-size: 13px;
}}
.risk-item {{
  display: flex;
  align-items: center;
  gap: 8px;
}}
.risk-line {{
  width: 20px;
  height: 2px;
  background: currentColor;
}}
footer {{
  margin-top: 2.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #f5f5f7;
  font-size: 12px;
  color: #86868b;
  text-align: center;
}}
.two-columns {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
  margin-bottom: 2.5rem;
  align-items: stretch;
}}
.two-columns .section {{
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
}}
.two-columns .card {{
  flex: 1;
}}
@media (max-width: 900px) {{
  .two-columns {{
    grid-template-columns: 1fr;
  }}
}}
@media print {{
  body {{ padding: 0; }}
  .header, .section {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>

<div class="header">
  <h1>{m['sprint_name']}</h1>
  <div class="meta">{m['sprint_start']} → {m['sprint_end']} · Generado {m['generated_at']}</div>
</div>

<div class="kpis">
  <div class="kpi">
    <div class="kpi-label">Total de tickets</div>
    <div class="kpi-value">{k['total_items']}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Leftovers</div>
    <div class="kpi-value">{k['leftovers']}</div>
    <div class="kpi-unit">antes del sprint</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Abiertos</div>
    <div class="kpi-value">{k['open_items']}</div>
    <div class="kpi-unit">{100 - k['pct_done']}% restante</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Progreso</div>
    <div class="kpi-value" style="font-size:48px">{k['pct_done']}%</div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:{k['pct_done']}%"></div>
    </div>
  </div>
</div>

<div class="two-columns">
  <div class="section">
    <h2 class="section-title">Tickets Completados vs Total</h2>
    <div class="card">
      <div class="chart-container">
        <canvas id="chart-completion" width="800" height="400"></canvas>
      </div>
      <div class="legend">
        <div class="legend-item">
          <span class="legend-dot" style="background:#34c759"></span>
          <span>Completados ({data['status_table']['done']})</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background:#0071e3"></span>
          <span>Abiertos ({data['status_table']['in_progress']})</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot" style="background:#ff9500"></span>
          <span>Not Started ({data['status_table']['not_started']})</span>
        </div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2 class="section-title">Distribución por Estado</h2>
    <div class="card">
      <table style="width:100%; border-collapse: collapse; font-size: 14px;">
        <thead>
          <tr style="border-bottom: 1px solid #e8e8ed;">
            <th style="text-align:left; padding: 12px 16px; color: #86868b; font-weight: 500;">Estado</th>
            <th style="text-align:right; padding: 12px 16px; color: #86868b; font-weight: 500;">Tickets</th>
          </tr>
        </thead>
        <tbody>
          <tr style="border-bottom: 1px solid #f5f5f7;">
            <td style="padding: 12px 16px;"><span style="display:inline-block; width:10px; height:10px; background:#34c759; border-radius:50%; margin-right:8px;"></span>Completados</td>
            <td style="text-align:right; padding: 12px 16px; font-weight: 600;">{data['status_table']['done']}</td>
          </tr>
          <tr style="border-bottom: 1px solid #f5f5f7;">
            <td style="padding: 12px 16px;"><span style="display:inline-block; width:10px; height:10px; background:#0071e3; border-radius:50%; margin-right:8px;"></span>Abiertos</td>
            <td style="text-align:right; padding: 12px 16px; font-weight: 600;">{data['status_table']['in_progress']}</td>
          </tr>
          <tr>
            <td style="padding: 12px 16px;"><span style="display:inline-block; width:10px; height:10px; background:#ff9500; border-radius:50%; margin-right:8px;"></span>Not Started</td>
            <td style="text-align:right; padding: 12px 16px; font-weight: 600;">{data['status_table']['not_started']}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr style="border-top: 2px solid #e8e8ed; font-weight: 600;">
            <td style="padding: 12px 16px;">Total</td>
            <td style="text-align:right; padding: 12px 16px;">{data['status_table']['done'] + data['status_table']['in_progress'] + data['status_table']['not_started']}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Antigüedad de Items (Scatter Plot)</h2>
  <div class="card">
    <p style="margin-bottom:1rem; color:#86868b; font-size:13px">
      Items ordenados verticalmente por antigüedad desde que pasaron a Abierto (los más antiguos arriba).
    </p>
    <div class="chart-container">
      <canvas id="chart-scatter" width="800" height="400"></canvas>
    </div>
    <div class="legend">
      <div class="legend-item">
        <span class="legend-dot" style="background:#34c759"></span>
        <span>Completados</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background:#0071e3"></span>
        <span>Abiertos</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background:#ff9500"></span>
        <span>Not Started</span>
      </div>
    </div>
    <div class="risk-zones">
      <div class="risk-item" style="color:#ff9500">
        <span class="risk-line"></span>
        <span>Riesgo moderado (14 días)</span>
      </div>
      <div class="risk-item" style="color:#ff3b30">
        <span class="risk-line"></span>
        <span>Riesgo alto (28 días)</span>
      </div>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">📌 Highlights del Sprint</h2>
  <div class="card" style="padding: 0; overflow: hidden;">
    {''.join(f"""
    <div class="highlight-item" style="padding: 20px 24px; border-bottom: 1px solid #f5f5f7; display: flex; gap: 16px; align-items: flex-start;">
      <div class="highlight-icon" style="font-size: 28px; flex-shrink: 0;">{h['icon']}</div>
      <div class="highlight-content" style="flex: 1;">
        <div class="highlight-title" style="font-weight: 600; font-size: 16px; margin-bottom: 4px; color: #1d1d1f;">{h['title']}</div>
        <div class="highlight-desc" style="font-size: 14px; color: #86868b; line-height: 1.5;">{h['description']}</div>
      </div>
    </div>
    """ for h in data['highlights'])}
  </div>
</div>

<footer>
  <p>Sprint Summary Report · Generado desde Jira CSV</p>
</footer>

<script>
const DATA = {json.dumps(data)};

// Completion donut chart
const ctxCompletion = document.getElementById('chart-completion');
new Chart(ctxCompletion, {{
  type: 'doughnut',
  data: {{
    labels: ['Completados', 'Abiertos', 'Not Started'],
    datasets: [{{
      data: [{data['status_table']['done']}, {data['status_table']['in_progress']}, {data['status_table']['not_started']}],
      backgroundColor: ['#34c759', '#0071e3', '#ff9500'],
      borderWidth: 0,
      hoverOffset: 4
    }}]
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    cutout: '60%',
    plugins: {{
      legend: {{
        display: false
      }},
      tooltip: {{
        callbacks: {{
          label: function(context) {{
            const label = context.label || '';
            const value = context.parsed || 0;
            const total = {k['total_items']};
            const pct = Math.round(value / total * 100);
            return label + ': ' + value + ' (' + pct + '%)';
          }}
        }}
      }}
    }}
  }}
}});

// Scatter plot
const scatterData = {json.dumps(scatter_data_points)};
const maxAge = Math.max(...scatterData.map(d => d.y), 30);

const datasets = {{}};
scatterData.forEach(point => {{
  // Map individual status to grouped categories
  // Completados = Done + Closed + Rejected
  // Abiertos = Open + In Progress
  // Not started = resto
  const status = point.status;
  let category, color;
  if (status === 'Done' || status === 'Closed' || status === 'Rejected') {{
    category = 'Completados';
    color = '#34c759';
  }} else if (status === 'Open' || status === 'In Progress') {{
    category = 'Abiertos';
    color = '#0071e3';
  }} else {{
    category = 'Not Started';
    color = '#ff9500';
  }}

  if (!datasets[category]) {{
    datasets[category] = {{
      label: category,
      data: [],
      backgroundColor: color + '80',
      borderColor: color,
      borderWidth: 1.5,
      pointRadius: 6,
      pointHoverRadius: 8
    }};
  }}
  datasets[category].data.push({{x: point.x, y: point.y, key: point.key, type: point.type, summary: point.summary, assignee: point.assignee}});
}});

const ctxScatter = document.getElementById('chart-scatter');
new Chart(ctxScatter, {{
  type: 'scatter',
  data: {{
    datasets: Object.values(datasets)
  }},
  options: {{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{
        display: false
      }},
      tooltip: {{
        callbacks: {{
          title: function(context) {{
            return context[0].raw.key;
          }},
          label: function(context) {{
            const point = context.raw;
            return [
              point.type,
              point.summary,
              'Asignado: ' + point.assignee,
              'Antigüedad: ' + Math.round(point.y) + ' días (desde Abierto)'
            ];
          }}
        }}
      }}
    }},
    scales: {{
      x: {{
        display: false,
        min: -3,
        max: 3
      }},
      y: {{
        title: {{
          display: true,
          text: 'Días desde Abierto (los más antiguos arriba)',
          font: {{ size: 12 }},
          color: '#86868b'
        }},
        min: 0,
        max: {max_age} + 5,
        grid: {{ color: 'rgba(0,0,0,0.04)' }},
        ticks: {{
          stepSize: Math.max(1, Math.ceil(({max_age} + 5) / 5)),
          color: '#86868b',
          font: {{ size: 11 }}
        }}
      }}
    }}
  }}
}});
</script>

</body>
</html>"""
    
    return html

def main():
    parser = argparse.ArgumentParser(
        description='Generate Sprint Summary Report from Jira CSV'
    )
    parser.add_argument('csv_path', help='Path to Jira CSV export')
    parser.add_argument('--sprint-start', required=True, help='Sprint start date (YYYY-MM-DD)')
    parser.add_argument('--sprint-end', required=True, help='Sprint end date (YYYY-MM-DD)')
    parser.add_argument('--output', '-o', default='sprint-report.html', 
                        help='Output HTML file')
    
    args = parser.parse_args()
    
    try:
        print(f"Analyzing {args.csv_path}...", file=sys.stderr)
        data = analyze(args.csv_path, args.sprint_start, args.sprint_end)
        
        print(f"Generating HTML report...", file=sys.stderr)
        html = generate_html(data)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Report generated: {args.output}", file=sys.stderr)
        print(args.output)  # Output filename for scripting
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
