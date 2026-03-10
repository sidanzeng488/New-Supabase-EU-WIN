"""
Fast batch update spending_plan with utility_id and project_id using SQL
"""
import psycopg2
import json

print('='*60)
print('Fast Link Spending Plan (SQL batch update)')
print('='*60)

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
conn.autocommit = True
cur = conn.cursor()

# Step 1: Update project_id by matching project_name
print('\n[1/2] Updating project_id...')
cur.execute('''
    UPDATE spending_plan sp
    SET project_id = p.project_id
    FROM projects p
    WHERE LOWER(TRIM(sp.project_name)) = LOWER(TRIM(p.project_name))
    AND sp.project_id IS NULL
''')
print(f'  Updated {cur.rowcount} records with project_id')

# Step 2: Update utility_id by matching through projects table
print('\n[2/2] Updating utility_id...')
cur.execute('''
    UPDATE spending_plan sp
    SET utility_id = p.utility_id
    FROM projects p
    WHERE sp.project_id = p.project_id
    AND sp.utility_id IS NULL
    AND p.utility_id IS NOT NULL
''')
print(f'  Updated {cur.rowcount} records with utility_id')

# Verify
print('\n' + '='*60)
print('Verification:')
cur.execute('SELECT COUNT(*) FROM spending_plan')
total = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM spending_plan WHERE project_id IS NOT NULL')
with_project = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM spending_plan WHERE utility_id IS NOT NULL')
with_utility = cur.fetchone()[0]

print(f'  Total records: {total}')
print(f'  With project_id: {with_project} ({100*with_project/total:.1f}%)')
print(f'  With utility_id: {with_utility} ({100*with_utility/total:.1f}%)')
print('='*60)

cur.close()
conn.close()
print('Done!')
