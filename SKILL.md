---
name: sprint-summary
description: >
  Generates an executive HTML report for Sprint performance from a Jira CSV export.
  Creates a clean, single-page report showing completed vs total tickets and an aging
  scatter plot with items ordered vertically by age (oldest items at top).
  
  TRIGGER this skill when: the user uploads a CSV file and asks to generate a sprint
  report, summary, or quick visual analysis. Key phrases: "generate sprint report",
  "summary report", "scatter plot", "ticket status", "sprint overview", or when they
  provide a CSV with sprint data and ask for visualization.
---

# Sprint Summary Report Generator

Creates a professional HTML report from a Jira CSV export with two main visualizations:
1. **Tickets Completed vs Total** — Shows progress and remaining work
2. **Item Age Scatter Plot** — Vertical scatter with oldest items at the top

## Usage

```bash
cd /path/to/project && python3 scripts/generate_report.py <csv_file> \
  --sprint-start YYYY-MM-DD \
  --sprint-end YYYY-MM-DD \
  --output report.html
```

## Parameters

- `csv_file` — Path to the Jira CSV export (e.g., `UserStories.csv`)
- `--sprint-start` — Sprint start date (required, format: YYYY-MM-DD)
- `--sprint-end` — Sprint end date (required, format: YYYY-MM-DD)
- `--output` — Output HTML file (default: `sprint-report.html`)

## Example

```bash
cd /path/to/project && python3 scripts/generate_report.py UserStories.csv \
  --sprint-start 2026-04-07 \
  --sprint-end 2026-04-17 \
  --output my-sprint-report.html
```

## CSV Requirements

Must contain these columns:
- `Issue key` — Unique ticket identifier (e.g., MM-37815)
- `Issue Type` — Type of work (Change Request, Story, Bug, etc.)
- `Status` — Current status (Open, Closed, Done, etc.)
- `Created` — Creation date (format: dd/Mon/yy h:mm AM/PM)
- `Resolved` — Resolved date (if completed, same format)
- `Assignee` — Person assigned to the ticket

## Output

Generates a single HTML file with:
- **KPI Section** — Summary metrics (total items, completed, percentage)
- **Progress Bar** — Visual representation of completion ratio
- **Scatter Plot** — Item age distribution (Y-axis: age in days, X-axis: scattered for visibility)
- **Status Legend** — Color-coded by status (Closed, Done, Open, etc.)
- **Responsive Design** — Works on desktop and mobile

## Notes

- Items older than 14 days are marked in amber
- Items older than 28 days are marked in red
- The scatter plot automatically filters by sprint date range
- No assignee names are displayed (privacy-safe)