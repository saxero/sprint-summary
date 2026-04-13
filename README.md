# Sprint Summary Report Skill

Professional Sprint Performance Report Generator

## Quick Start

```bash
python3 scripts/generate_report.py ./UserStories.csv \
  --sprint-start 2026-04-07 \
  --sprint-end 2026-04-17 \
  --output my-sprint-report.html
```

## Features

✅ **Completion Dashboard**
- Total items counter
- Completed/opened item counter  
- Progress percentage with visual bar
- Donut chart showing completion ratio

✅ **Item Aging Scatter Plot**
- Vertical Y-axis: Age in days (oldest items at top)
- Horizontal X-axis: Scattered for visibility
- Color-coded by status (Closed, Open, In Progress, etc.)
- Risk zones: Amber (14d), Red (28d)
- Hover tooltips with item key and age

✅ **Clean, Professional Design**
- Apple-inspired UI with Inter font
- Responsive layout for desktop/mobile
- Print-optimized (Ctrl+P to PDF)
- Dark text on light background

## Parameters

| Parameter | Required | Format | Example |
|-----------|----------|--------|---------|
| `csv_path` | Yes | Path to CSV file | `UserStories.csv` |
| `--sprint-start` | Yes | YYYY-MM-DD | `2026-04-07` |
| `--sprint-end` | Yes | YYYY-MM-DD | `2026-04-17` |
| `--output` | No | Filename | `sprint-report.html` (default) |

## CSV Requirements

Your CSV must contain these columns:
- **Issue key** — Unique ticket ID
- **Issue Type** — Type of work
- **Status** — Current status
- **Created** — Creation timestamp
- **Resolved** — Resolution timestamp (if closed)
- **Assignee** — Person assigned

Export from Jira: Issues → Export → CSV

## Output

A single **self-contained HTML file** with:
- No external dependencies (Chart.js via CDN)
- Embedded styling and scripts
- Printable to PDF
- Mobile responsive

## Example Usage

```bash
# Generate report for latest sprint
python3 scripts/generate_report.py ./UserStories.csv \
  --sprint-start 2026-04-07 \
  --sprint-end 2026-04-17

# Custom output filename
python3 scripts/generate_report.py ./data/tickets.csv \
  --sprint-start 2026-03-31 \
  --sprint-end 2026-04-13 \
  --output reports/sprint-7-summary.html

# Open in browser
python3 scripts/generate_report.py UserStories.csv \
  --sprint-start 2026-04-07 \
  --sprint-end 2026-04-17 && \
  start sprint-report.html
```

## Interpreting the Report

### Completion Section
Shows a donut chart with:
- **Green** = Completed (Closed, Done)
- **Orange** = Open/In Progress

### Aging Scatter Plot
Vertical scatter where:
- **Y-axis** = Days since creation (top = older)
- **X-axis** = Random spread for visibility
- **Colors**:
  - 🟢 Green: Completed  
  - 🔵 Blue: In Progress
  - 🟠 Orange: Open
  - 🔴 Red: Rejected

### Risk Zones
- 🟠 **Amber line **at 14 days — moderate risk
- 🔴 **Red line** at 28 days — high risk

## Notes

- Dates must match Jira CSV format
- Assignee names are NOT displayed (privacy-safe)
- All calculations are automatic
- HTML is self-contained and shareable
- Compatible with Chart.js 4.4.1
