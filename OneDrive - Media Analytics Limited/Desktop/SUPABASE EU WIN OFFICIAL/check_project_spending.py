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

# Check spending_plan table structure
print('spending_plan table columns:')
cur.execute('''
    SELECT column_name, data_type 
    FROM information_schema.columns
    WHERE table_name = 'spending_plan'
    ORDER BY ordinal_position
''')
for col in cur.fetchall():
    print(f'  {col[0]}: {col[1]}')

# Get project IDs
cur.execute('SELECT project_id FROM projects WHERE project_name = %s', (project_name,))
project_ids = [r[0] for r in cur.fetchall()]
print(f'\nProject IDs: {project_ids}')

# Check spending_plan for these projects
print(f'\n{"="*80}')
print('Spending Plan records for these projects:')
print('=' * 80)

cur.execute('''
    SELECT sp.*, p.project_name
    FROM spending_plan sp
    JOIN projects p ON sp.project_id = p.project_id
    WHERE sp.project_id = ANY(%s)
    ORDER BY sp.project_id, sp.year
''', (project_ids,))

columns = [desc[0] for desc in cur.description]
rows = cur.fetchall()

print(f'\nFound {len(rows)} spending_plan records\n')

# Group by project_id
from collections import defaultdict
by_project = defaultdict(list)
for row in rows:
    row_dict = dict(zip(columns, row))
    by_project[row_dict['project_id']].append(row_dict)

for pid, records in sorted(by_project.items()):
    print(f'\nProject ID: {pid}')
    print(f'  Years: {[r["year"] for r in records]}')
    print(f'  Total CAPEX: {[r.get("total_capex") for r in records]}')
    for r in records:
        print(f'    Year {r["year"]}: CAPEX={r.get("total_capex")}, OPEX={r.get("opex")}')

# Check for differences in spending_plan data
print(f'\n{"="*80}')
print('Summary by Year:')
print('=' * 80)

cur.execute('''
    SELECT sp.year, COUNT(*) as cnt, SUM(sp.total_capex) as total_capex
    FROM spending_plan sp
    WHERE sp.project_id = ANY(%s)
    GROUP BY sp.year
    ORDER BY sp.year
''', (project_ids,))

for row in cur.fetchall():
    print(f'  Year {row[0]}: {row[1]} records, Total CAPEX: {row[2]}')

cur.close()
conn.close()
