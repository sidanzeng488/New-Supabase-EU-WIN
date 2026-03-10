"""
Add Future Year Costs (FC) to spending_plan table
year = 'future_year'
"""
import psycopg2
import json

print('='*60)
print('Add Future Year Costs to spending_plan')
print('='*60)

# Load JSON
print('\n[1/3] Loading JSON...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'  Loaded {len(data)} records')

# Extract future year costs
print('\n[2/3] Extracting Future Year Costs...')
records = []
for record in data:
    utility_name = record.get('Column1.utilityName', '')
    project_name = record.get('Column1.Project Name (PN)', '')
    future_cost = record.get('Column1.Future Year Costs (FC)_EUR')
    
    if future_cost is not None and project_name:
        records.append({
            'utility_name': utility_name,
            'project_name': project_name,
            'year': 'future_year',
            'cost_type': 'future',
            'cost': float(future_cost) if future_cost else 0.0,
            'currency': 'EUR'
        })

print(f'  Found {len(records)} records with Future Year Costs')

# Insert into database
print('\n[3/3] Inserting into spending_plan...')
conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
conn.autocommit = True
cur = conn.cursor()

inserted = 0
for i, r in enumerate(records):
    cur.execute('''
        INSERT INTO spending_plan (utility_name, project_name, year, cost_type, cost, currency)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (r['utility_name'], r['project_name'], r['year'], r['cost_type'], r['cost'], r['currency']))
    inserted += 1
    
    if inserted % 2000 == 0:
        print(f'  Inserted {inserted}...')

print(f'  Total inserted: {inserted}')

# Link to project_id and utility_id
print('\n[4/4] Linking to project_id and utility_id...')
cur.execute('''
    UPDATE spending_plan sp
    SET project_id = p.project_id
    FROM projects p
    WHERE LOWER(TRIM(sp.project_name)) = LOWER(TRIM(p.project_name))
    AND sp.year = 'future_year'
    AND sp.project_id IS NULL
''')
print(f'  Updated {cur.rowcount} with project_id')

cur.execute('''
    UPDATE spending_plan sp
    SET utility_id = p.utility_id
    FROM projects p
    WHERE sp.project_id = p.project_id
    AND sp.year = 'future_year'
    AND sp.utility_id IS NULL
    AND p.utility_id IS NOT NULL
''')
print(f'  Updated {cur.rowcount} with utility_id')

# Verify
cur.execute("SELECT COUNT(*) FROM spending_plan WHERE year = 'future_year'")
print(f'\nTotal future_year records: {cur.fetchone()[0]}')

cur.close()
conn.close()
print('\nDone!')
