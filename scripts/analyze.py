#!/usr/bin/env python3
"""
Sprint Summary Report Generator
Generates an HTML report from a Jira CSV with completed vs total tickets
and an aging scatter plot (items vertical by age).
"""

import argparse
import json
import sys
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
    df['opened_dt'] = df['Updated'].apply(parse_date)
    df['resolved_dt'] = df['Resolved'].apply(parse_date)
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
    
    # Prepare scatter data
    scatter_items = []
    for idx, row in df.iterrows():
        created = row['created_dt']
        if not created:
            continue

        opened = row['opened_dt']
        if not opened:
            continue
        
        # Calculate absolute age (days since creation)
        age = (now - opened).days
        
        # Only include items in sprint window or created before
        if created <= sprint_end_dt:
            scatter_items.append({
                'key': row['issue_key'],
                'type': row['issue_type'],
                'status': row['status'],
                'age_days': age,
                'is_closed': row['is_closed']
            })
    
    # Sort by age (descending) for display
    scatter_items.sort(key=lambda x: x['age_days'], reverse=True)
    
    # Status distribution
    status_dist = df['status'].value_counts().to_dict()
    
    # Get sprint name
    sprint_name = 'Sprint'
    if 'Sprint' in df.columns:
        sprints = df['Sprint'].dropna().value_counts()
        if len(sprints) > 0:
            sprint_name = sprints.index[0]
    
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
        },
        'scatter_items': scatter_items,
        'status_dist': status_dist,
    }

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
        data = analyze(args.csv_path, args.sprint_start, args.sprint_end)
        
        # Output JSON for debugging
        print(json.dumps(data, indent=2), file=sys.stderr)
        
        # Save data to JSON file
        json_file = Path(args.output).stem + '.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Data saved to {json_file}", file=sys.stderr)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
