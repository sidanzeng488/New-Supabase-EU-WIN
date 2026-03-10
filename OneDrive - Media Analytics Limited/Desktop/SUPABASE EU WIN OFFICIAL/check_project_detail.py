import psycopg2

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

project_name = 'Realizzazione vasca di prima pioggia conforme al RR 6/2019'

# Check spending_plan for this project name
print('Spending Plan records by project_id:')
cur.execute('''
    SELECT project_id, year, cost_type, cost, currency
    FROM spending_plan
    WHERE project_name = %s
    ORDER BY project_id, year, cost_type
''', (project_name,))

rows = cur.fetchall()
print(f'Total spending_plan records: {len(rows)}')

# Group by project_id
from collections import defaultdict
by_project = defaultdict(list)
for row in rows:
    by_project[row[0]].append(row)

print(f'\nNumber of unique project_ids in spending_plan: {len(by_project)}')
for pid, records in sorted(by_project.items()):
    print(f'\n  Project ID {pid}: {len(records)} records')
    # Show first few
    for r in records[:3]:
        print(f'    Year={r[1]}, Type={r[2]}, Cost={r[3]}, Currency={r[4]}')
    if len(records) > 3:
        print(f'    ... and {len(records)-3} more')

# Check if there are projects WITHOUT spending_plan
print('\n' + '='*80)
print('Projects table records:')
cur.execute('''
    SELECT p.project_id, p.project_name, p.utility_id, p.sub_application_id
    FROM projects p
    WHERE p.project_name = %s
    ORDER BY p.project_id
''', (project_name,))

projects = cur.fetchall()
print(f'Total project records: {len(projects)}')

# Check which projects have spending_plan
project_ids_with_sp = set(by_project.keys())
for p in projects:
    has_sp = 'YES' if p[0] in project_ids_with_sp else 'NO'
    print(f'  ID={p[0]}, utility={p[2]}, sub_app={p[3]}, has_spending_plan={has_sp}')

# Check original source - files table maybe
print('\n' + '='*80)
print('Checking source data...')

# Check the Excel file for duplicates
import pandas as pd
try:
    df = pd.read_excel('data/Europe utility spending plan tracker.xlsx', sheet_name=None)
    for sheet_name, sheet_df in df.items():
        if 'project' in sheet_name.lower() or 'cap' in sheet_name.lower():
            print(f'\nSheet: {sheet_name}')
            # Find matching rows
            for col in sheet_df.columns:
                if 'name' in col.lower() or 'project' in col.lower():
                    matches = sheet_df[sheet_df[col].astype(str).str.contains(project_name[:30], na=False, case=False)]
                    if len(matches) > 0:
                        print(f'  Found {len(matches)} matches in column "{col}"')
                        print(matches.head(5).to_string())
                        break
except Exception as e:
    print(f'Could not read Excel: {e}')

cur.close()
conn.close()
