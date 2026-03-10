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
print('Fixing Files Table')
print('Removing project_id, keeping one file per utility')
print('=' * 60)

# Step 1: Drop and recreate files table without project_id
print('\n[1/4] Recreating files table without project_id...')
cur.execute("DROP TABLE IF EXISTS files CASCADE;")
cur.execute("""
    CREATE TABLE files (
        file_id SERIAL PRIMARY KEY,
        utility_id INTEGER REFERENCES utilities(utility_id),
        cip_start_year INTEGER,
        cip_end_year INTEGER,
        page_link TEXT,
        doc_link TEXT
    );
""")
print('  - Table recreated')

# Step 2: Load utility mapping
print('\n[2/4] Loading utility mapping...')
cur.execute("SELECT utility_name_local, utility_id FROM utilities;")
utility_map = {row[0]: row[1] for row in cur.fetchall()}
print(f'  - utilities: {len(utility_map)} entries')

# Step 3: Load JSON data
print('\n[3/4] Loading JSON data...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'  - Loaded {len(data)} records')

# Step 4: Extract ONE file per utility (first occurrence)
print('\n[4/4] Inserting one file per utility...')
files = {}
for record in data:
    utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
    
    if not utility_local or utility_local in files:
        continue
    
    utility_id = utility_map.get(utility_local)
    if not utility_id:
        continue
    
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
    
    files[utility_local] = {
        'utility_id': utility_id,
        'cip_start_year': cip_start_int,
        'cip_end_year': cip_end_int,
        'page_link': page_link,
        'doc_link': doc_link
    }

print(f'  - Found {len(files)} unique utilities with files')

# Insert files
inserted = 0
for utility_local, file_data in files.items():
    cur.execute("""
        INSERT INTO files (utility_id, cip_start_year, cip_end_year, page_link, doc_link)
        VALUES (%s, %s, %s, %s, %s);
    """, (
        file_data['utility_id'],
        file_data['cip_start_year'],
        file_data['cip_end_year'],
        file_data['page_link'],
        file_data['doc_link']
    ))
    inserted += 1

print(f'  - Inserted {inserted} files')

# Summary
print('\n' + '=' * 60)
print('Summary')
print('=' * 60)

cur.execute("SELECT COUNT(*) FROM files;")
file_count = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM utilities;")
utility_count = cur.fetchone()[0]

print(f'Files: {file_count}')
print(f'Utilities: {utility_count}')
print(f'Match: {"YES" if file_count == utility_count else "NO"}')

# Show table structure
print('\nNew files table structure:')
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'files' 
    ORDER BY ordinal_position;
""")
for row in cur.fetchall():
    print(f'  - {row[0]}: {row[1]}')

# Sample
print('\nSample files:')
cur.execute("""
    SELECT f.file_id, u.utility_name_local, f.cip_start_year, f.cip_end_year
    FROM files f
    LEFT JOIN utilities u ON f.utility_id = u.utility_id
    ORDER BY f.file_id
    LIMIT 5;
""")
for row in cur.fetchall():
    name = row[1][:40] + '...' if row[1] and len(row[1]) > 40 else row[1]
    print(f'  [{row[0]}] {name} ({row[2]}-{row[3]})')

cur.close()
conn.close()

print('\nDone!')
