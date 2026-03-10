import psycopg2

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

# First check table structure
print('Projects table columns:')
cur.execute('''
    SELECT column_name, data_type 
    FROM information_schema.columns
    WHERE table_name = 'projects'
    ORDER BY ordinal_position
''')
for col in cur.fetchall():
    print(f'  {col[0]}: {col[1]}')

project_name = 'Realizzazione vasca di prima pioggia conforme al RR 6/2019'

print(f'\n{"="*80}')
print(f'Searching for project: {project_name}')
print('=' * 80)

# Find all projects with this name
cur.execute('''
    SELECT * FROM projects 
    WHERE project_name = %s
    ORDER BY project_id
''', (project_name,))

columns = [desc[0] for desc in cur.description]
rows = cur.fetchall()

print(f'\nFound {len(rows)} records\n')

# Print each record with all non-null fields
for i, row in enumerate(rows):
    print(f'--- Record {i+1} ---')
    for col, val in zip(columns, row):
        if val is not None and val != '':
            print(f'  {col}: {val}')
    print()

cur.close()
conn.close()
