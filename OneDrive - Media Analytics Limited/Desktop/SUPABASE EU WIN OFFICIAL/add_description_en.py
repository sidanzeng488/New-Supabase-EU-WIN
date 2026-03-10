import psycopg2
import json

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
conn.autocommit = True
cur = conn.cursor()

print('=' * 60)
print('Adding description_english column to projects')
print('=' * 60)

# Step 1: Add column if not exists
print('\n[1/3] Adding description_english column...')
try:
    cur.execute("""
        ALTER TABLE projects 
        ADD COLUMN IF NOT EXISTS description_english TEXT;
    """)
    print('  - Column added')
except Exception as e:
    print(f'  - Note: {e}')

# Step 2: Load JSON data
print('\n[2/3] Loading JSON data...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'  - Loaded {len(data)} records')

# Step 3: Update projects with English description
print('\n[3/3] Updating projects with English descriptions...')

# Build a mapping: (project_name, utility_local) -> description_en
desc_map = {}
for record in data:
    project_name = record.get('Column1.Project Name (PN)')
    utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
    desc_en = record.get('Column1.Project Description (PD)_EN')
    
    if project_name and desc_en:
        key = (project_name, utility_local)
        desc_map[key] = desc_en

print(f'  - Built mapping for {len(desc_map)} unique project-utility pairs')

# Update in batches
updated = 0
for i, record in enumerate(data):
    project_name = record.get('Column1.Project Name (PN)')
    utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
    desc_en = record.get('Column1.Project Description (PD)_EN')
    
    if project_name and desc_en:
        cur.execute("""
            UPDATE projects 
            SET description_english = %s 
            WHERE project_name = %s 
            AND project_id = %s;
        """, (desc_en, project_name, i + 1))
        
        if cur.rowcount > 0:
            updated += 1
    
    if (i + 1) % 2000 == 0:
        print(f'  - Processed {i + 1} records...')

print(f'\n  - Updated {updated} projects')

# Verify
print('\n' + '=' * 60)
print('Verification')
print('=' * 60)

cur.execute("""
    SELECT project_id, project_name, description_english 
    FROM projects 
    WHERE description_english IS NOT NULL 
    LIMIT 5;
""")

print('\nSample projects with English descriptions:')
for row in cur.fetchall():
    name = row[1][:30] + '...' if len(row[1] or '') > 30 else row[1]
    desc = row[2][:40] + '...' if len(row[2] or '') > 40 else row[2]
    print(f'  [{row[0]}] {name}')
    print(f'       EN: {desc}')

cur.execute("SELECT COUNT(*) FROM projects WHERE description_english IS NOT NULL;")
count = cur.fetchone()[0]
print(f'\nProjects with English description: {count}')

cur.close()
conn.close()

print('\nDone!')
