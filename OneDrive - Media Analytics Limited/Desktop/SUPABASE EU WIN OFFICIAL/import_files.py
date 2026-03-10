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
print('Importing Files from merge_final.json')
print('One file per project (using project_id from DB)')
print('=' * 60)

# Step 1: Load utility mapping
print('\n[1/4] Loading utility mapping...')
cur.execute("SELECT utility_name_local, utility_id FROM utilities;")
utility_map = {row[0]: row[1] for row in cur.fetchall()}
print(f'  - utilities: {len(utility_map)} entries')

# Step 2: Get all project_ids from database
print('\n[2/4] Loading project IDs from database...')
cur.execute("SELECT project_id FROM projects ORDER BY project_id;")
project_ids = [row[0] for row in cur.fetchall()]
print(f'  - projects: {len(project_ids)} entries')

# Step 3: Load JSON data
print('\n[3/4] Loading JSON data...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'  - Loaded {len(data)} records')

# Step 4: Clear and insert files
print('\n[4/4] Inserting files...')
cur.execute("DELETE FROM files;")
cur.execute("ALTER SEQUENCE files_file_id_seq RESTART WITH 1;")

# Match JSON records to project_ids in order
# Filter JSON to only records with project_name (same as projects import)
valid_records = [r for r in data if r.get('Column1.Project Name (PN)')]
print(f'  - Valid JSON records: {len(valid_records)}')

inserted = 0
errors = 0

for i, record in enumerate(valid_records):
    if i >= len(project_ids):
        break
    
    project_id = project_ids[i]
    
    utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
    utility_id = utility_map.get(utility_local)
    
    doc_link = record.get('Column1.DocumentLink')
    page_link = record.get('Column1.PageLink')
    cip_start = record.get('Column1.CIPStartYear')
    cip_end = record.get('Column1.CIPEndYear')
    
    # Validate year values
    try:
        cip_start_int = int(cip_start) if cip_start and str(cip_start).isdigit() else None
        cip_end_int = int(cip_end) if cip_end and str(cip_end).isdigit() else None
    except:
        cip_start_int = None
        cip_end_int = None
    
    try:
        cur.execute("""
            INSERT INTO files (utility_id, project_id, cip_start_year, cip_end_year, page_link, doc_link)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING file_id;
        """, (
            utility_id,
            project_id,
            cip_start_int,
            cip_end_int,
            page_link,
            doc_link
        ))
        inserted += 1
        
        if inserted % 2000 == 0:
            print(f'  - Inserted {inserted} files...')
            
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f'  ! Error at project_id {project_id}: {e}')

print(f'\n  - Total inserted: {inserted}')
print(f'  - Errors: {errors}')

# Summary
print('\n' + '=' * 60)
print('Import Summary')
print('=' * 60)

cur.execute("SELECT COUNT(*) FROM files;")
file_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM projects;")
project_count = cur.fetchone()[0]

print(f'Total files in database: {file_count}')
print(f'Total projects in database: {project_count}')
print(f'Match: {"YES" if file_count == project_count else "NO - diff: " + str(project_count - file_count)}')

# Sample
print('\nSample files:')
cur.execute("""
    SELECT f.file_id, f.project_id, u.utility_name_local, p.project_name, f.cip_start_year, f.cip_end_year
    FROM files f
    LEFT JOIN utilities u ON f.utility_id = u.utility_id
    LEFT JOIN projects p ON f.project_id = p.project_id
    ORDER BY f.file_id
    LIMIT 5;
""")
for row in cur.fetchall():
    util_name = row[2][:25] + '...' if row[2] and len(row[2]) > 25 else row[2]
    proj_name = row[3][:30] + '...' if row[3] and len(row[3]) > 30 else row[3]
    print(f'  [file:{row[0]} proj:{row[1]}] {util_name}')
    print(f'       Project: {proj_name} ({row[4]}-{row[5]})')

cur.close()
conn.close()

print('\nDone!')
