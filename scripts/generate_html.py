haz #!/usr/bin/env python3
"""
Generate HTML report from sprint analysis JSON data.
"""

import argparse
import json
import sys
from pathlib import Path

def generate_html(data):
    """Generate HTML report from analysis data."""
    m = data['meta']
    k = data['kpis']
    scatter = data['scatter_items']
    
    # Sort scatter items by age (descending - oldest first)
    scatter_sorted = sorted(scatter, key=lambda x: x['age_days'], reverse=True)
    
    # Prepare scatter plot data
    # Y-axis: age in days (older = higher), X-axis: random scatter for visibility
    scatter_points = []
    for i, item in enumerate(scatter_sorted):
        # Spread items horizontally
        x = (i % 5) - 2  # Range from -2 to 2
        y = item['age_days']
        color = '#ff3b30' if y > 28 else '#ff9500' if y > 14 else '#34c759'
        scatter_points.append({
            'x': x,
            'y': y,
            'key': item['key'],
            'status': item['status'],
            'color': color,
            'type': item['type'],
            'is_closed': item['is_closed']
        })
    
    # Prepare Chart.js data
    import math
    max_age = max((p['y'] for p in scatter_points), default=30)
    
    scatter_datasets = []
    # Group by status for coloring
    status_groups = {}
    for p in scatter_points:
        status = p['status']
        if status not in status_groups:
            status_groups[status] = []
        status_groups[status].append(p)
    
    status_colors = {
        'Closed': '#34c759',
        'Done': '#34c759',
        'Open': '#ff9500',
        'New': '#86868b',
        'In Progress': '#0071e3',
        'Rejected': '#ff3b30'
    }
    
    scatter_data_points = []
    for p in scatter_points:
        scatter_data_points.append({
            'x': p['x'],
            'y': p['y'],
            'key': p['key'],
            'status': p['status'],
            'type': p['type']
        })
    
    # Generate HTML
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
.status-open {{ color: #ff9500; }}
.status-closed {{ color: #34c759; }}
.status-done {{ color: #34c759; }}
.status-rejected {{ color: #ff3b30; }}
</style>
</head>
<body>

<div class="header">
  <h1>{m['sprint_name']}</h1>
  <div class="meta">{m['sprint_start']} → {m['sprint_end']} · Generado {m['generated_at']}</div>
</div>

<div class="kpis">
  <div class="kpi">
    <div class="kpi-label">Total de ítems</div>
    <div class="kpi-value">{k['total_items']}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Leftovers</div>
    <div class="kpi-value">{k['leftovers']}</div>
    <div class="kpi-unit">antes del sprint</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Completados</div>
    <div class="kpi-value">{k['closed_items']}</div>
    <div class="kpi-unit">de {k['total_items']}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Abiertos</div>
    <div class="kpi-value">{k['open_items']}</div>
    <div class="kpi-unit">{round(100-k['pct_done'])}% restante</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Progreso</div>
    <div class="kpi-value" style="font-size:48px">{k['pct_done']}%</div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:{k['pct_done']}%"></div>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Tickets Completados vs Total</h2>
  <div class="card">
    <div class="chart-container">
      <canvas id="chart-completion"></canvas>
    </div>
    <div class="legend">
      <div class="legend-item">
        <span class="legend-dot" style="background:#34c759"></span>
        <span>Completados ({k['closed_items']})</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background:#ff9500"></span>
        <span>Abiertos ({k['open_items']})</span>
      </div>
    </div>
  </div>
</div>

<div class="section">
  <h2 class="section-title">Antigüedad de Items (Scatter Plot)</h2>
  <div class="card">
    <div class="chart-container">
      <canvas id="chart-scatter"></canvas>
    </div>
    <div class="legend">
      <div class="legend-item">
        <span class="legend-dot" style="background:#34c759"></span>
        <span>Reciente (&lt;14 días)</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background:#ff9500"></span>
        <span>Moderado (14-28 días)</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot" style="background:#ff3b30"></span>
        <span>Antiguo (&gt;28 días)</span>
      </div>
    </div>
    <div class="risk-zones">
      <div class="risk-item" style="color:#ff9500">
        <span class="risk-line"></span>
        <span>Riesgo moderado (14d)</span>
      </div>
      <div class="risk-item" style="color:#ff3b30">
        <span class="risk-line"></span>
        <span>Riesgo alto (28d)</span>
      </div>
    </div>
  </div>
</div>

<footer>
  <p>Sprint Summary Report · Data from Jira CSV export</p>
</footer>

<script>
const DATA = {json.dumps(data)};

// Completion chart
const ctxCompletion = document.getElementById('chart-completion').getContext('2d');
new Chart(ctxCompletion, {{
  type: 'doughnut',
  data: {{
    labels: ['Completados', 'Abiertos'],
    datasets: [{{
      data: [{k['closed_items']}, {k['open_items']}],
      backgroundColor: ['#34c759', '#ff9500'],
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
  const status = point.status;
  const color = status === 'Closed' || status === 'Done' ? '#34c759' :
                status === 'Open' ? '#ff9500' :
                status === 'In Progress' ? '#0071e3' :
                status === 'Rejected' ? '#ff3b30' : '#86868b';
  
  if (!datasets[status]) {{
    datasets[status] = {{
      label: status,
      data: [],
      backgroundColor: color + '80',
      borderColor: color,
      borderWidth: 1.5,
      pointRadius: 6,
      pointHoverRadius: 8
    }};
  }}
  datasets[status].data.push({{x: point.x, y: point.y, key: point.key, type: point.type}});
}});

const ctxScatter = document.getElementById('chart-scatter').getContext('2d');
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
        display: true,
        position: 'top'
      }},
      tooltip: {{
        callbacks: {{
          label: function(context) {{
            const point = context.raw;
            return point.key + ' (' + Math.round(point.y) + 'd)';
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
          text: 'Días desde creación (los más antiguos arriba)'
        }},
        min: 0,
        max: maxAge + 5,
        ticks: {{
          stepSize: 7
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
    parser = argparse.ArgumentParser(description='Generate HTML report from sprint analysis JSON')
    parser.add_argument('--data', required=True, help='Path to analysis JSON file')
    parser.add_argument('--output', '-o', default='sprint-report.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    try:
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        html = generate_html(data)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Report generated: {args.output}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
