import json
import re
import csv
import os
import sys

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

# Read JSON file
json_path = os.path.join(project_dir, 'data', 'merge_final.json')
print(f"Reading file: {json_path}")

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} raw records")

# 正则模式匹配所有 _EUR 字段
patterns = {
    # 单年成本: Column1.2025 Project Cost (25)_EUR
    'annual': re.compile(r'Column1\.(\d{4}) Project Cost \(\d+\)_EUR'),
    # 往年成本: Column1.Prior Year Project Spending/Costs (PY)_EUR
    'prior': re.compile(r'Column1\.Prior Year Project Spending/Costs \(PY\)_EUR'),
    # 汇总成本（含往年）: Column1.SIAAP cost 2024-2034 + prior years_EUR 或其他类似格式
    'total_with_prior': re.compile(r'Column1\.[^"]*cost[^"]*\+ prior years_EUR', re.IGNORECASE),
    # 汇总成本: Column1.SIAAP cost 2024-2034_EUR 或其他类似格式 (但不包含 prior)
    'total': re.compile(r'Column1\.[^"]*cost[^"]*\d{4}-\d{4}_EUR$', re.IGNORECASE),
}

spending_records = []

for idx, record in enumerate(data):
    utility_name = record.get('Column1.utilityName', '')
    project_name = record.get('Column1.Project Name (PN)', '')
    cip_start = record.get('Column1.CIPStartYear', '')
    cip_end = record.get('Column1.CIPEndYear', '')
    
    for key, value in record.items():
        if not key.endswith('_EUR') or value is None:
            continue
            
        cost = float(value) if value else 0.0
        
        # 匹配单年成本
        match = patterns['annual'].match(key)
        if match:
            year = match.group(1)
            spending_records.append({
                'utility_name': utility_name,
                'project_name': project_name,
                'year': year,
                'cost_type': 'annual',
                'cost': cost,
                'currency': 'EUR'
            })
            continue
        
        # 匹配往年成本
        if patterns['prior'].match(key):
            spending_records.append({
                'utility_name': utility_name,
                'project_name': project_name,
                'year': 'prior_years',
                'cost_type': 'prior',
                'cost': cost,
                'currency': 'EUR'
            })
            continue
        
        # 匹配汇总成本（含往年）- 必须在 total 之前检查
        if patterns['total_with_prior'].search(key):
            year_label = f"total_{cip_start}_{cip_end}_with_prior" if cip_start and cip_end else "total_with_prior"
            spending_records.append({
                'utility_name': utility_name,
                'project_name': project_name,
                'year': year_label,
                'cost_type': 'total_with_prior',
                'cost': cost,
                'currency': 'EUR'
            })
            continue
        
        # 匹配汇总成本（不含 prior）
        if patterns['total'].search(key) and 'prior' not in key.lower():
            year_label = f"total_{cip_start}_{cip_end}" if cip_start and cip_end else "total"
            spending_records.append({
                'utility_name': utility_name,
                'project_name': project_name,
                'year': year_label,
                'cost_type': 'total',
                'cost': cost,
                'currency': 'EUR'
            })

# 输出为 CSV
output_path = os.path.join(project_dir, 'data', 'spending_plan_import.csv')
with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'utility_name', 'project_name', 'year', 'cost_type', 'cost', 'currency'
    ])
    writer.writeheader()
    writer.writerows(spending_records)

print(f"\nGenerated {len(spending_records)} spending_plan records")
print(f"Saved to: {output_path}")

# Count by type
from collections import Counter
type_counts = Counter(r['cost_type'] for r in spending_records)
print("\nRecords by cost_type:")
for cost_type, count in sorted(type_counts.items()):
    print(f"  {cost_type}: {count}")

# Show sample records
print("\nFirst 5 records:")
for i, rec in enumerate(spending_records[:5]):
    proj_name = rec['project_name'][:30] if rec['project_name'] else 'N/A'
    print(f"  {i+1}. {rec['utility_name']} | {proj_name}... | {rec['year']} | {rec['cost_type']} | {rec['cost']}")
