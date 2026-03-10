import psycopg2
import json

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

print('Analyzing difference between files and projects...')
print('=' * 60)

# Get counts
cur.execute("SELECT COUNT(*) FROM projects;")
project_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM files;")
file_count = cur.fetchone()[0]

print(f'Projects: {project_count}')
print(f'Files: {file_count}')
print(f'Difference: {project_count - file_count}')

# Find projects without files
print('\n' + '=' * 60)
print('Projects WITHOUT files:')
cur.execute("""
    SELECT p.project_id, p.project_name, p.utility_id, u.utility_name_local
    FROM projects p
    LEFT JOIN utilities u ON p.utility_id = u.utility_id
    WHERE p.project_id NOT IN (SELECT project_id FROM files WHERE project_id IS NOT NULL)
    ORDER BY p.project_id
    LIMIT 20;
""")

rows = cur.fetchall()
print(f'\nFound {project_count - file_count} projects without files. First 20:')
for row in rows:
    name = row[1][:40] + '...' if row[1] and len(row[1]) > 40 else row[1]
    util = row[3][:30] + '...' if row[3] and len(row[3]) > 30 else row[3]
    print(f'  [{row[0]}] {name}')
    print(f'       utility_id: {row[2]}, utility: {util}')

# Check unique project names in projects table
cur.execute("SELECT COUNT(DISTINCT project_name) FROM projects;")
unique_project_names = cur.fetchone()[0]
print(f'\nUnique project names in DB: {unique_project_names}')

# Load JSON to compare
print('\n' + '=' * 60)
print('Checking JSON data...')

with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count unique project names in JSON
json_project_names = set()
for record in data:
    pn = record.get('Column1.Project Name (PN)')
    if pn:
        json_project_names.add(pn)

print(f'Unique project names in JSON: {len(json_project_names)}')
print(f'Total records in JSON: {len(data)}')

# Check for duplicates in projects table
cur.execute("""
    SELECT project_name, utility_id, COUNT(*) as cnt
    FROM projects
    GROUP BY project_name, utility_id
    HAVING COUNT(*) > 1
    LIMIT 10;
""")
dups = cur.fetchall()
if dups:
    print(f'\nDuplicate (project_name, utility_id) in DB: {len(dups)} groups')
    for d in dups[:5]:
        print(f'  "{d[0][:30]}..." utility={d[1]} count={d[2]}')

cur.close()
conn.close()

print('\nDone!')
