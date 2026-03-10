"""
Import projects from merge_final.json
ONLY affects projects table, preserves all other tables
"""
import psycopg2
import json

print('='*60)
print('Import Projects (Only projects table)')
print('='*60)

# Connect
conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
conn.autocommit = True
cur = conn.cursor()

# Load mappings
print('\n[1/5] Loading mappings...')
cur.execute("SELECT sector_name, sector_id FROM sector;")
sector_map = {row[0]: row[1] for row in cur.fetchall()}

cur.execute("SELECT application_name, application_id FROM application;")
application_map = {row[0]: row[1] for row in cur.fetchall()}

cur.execute("SELECT sub_application_name, sub_application_id FROM sub_application;")
sub_application_map = {row[0]: row[1] for row in cur.fetchall()}

cur.execute("SELECT description, project_type_id FROM project_type;")
project_type_map = {row[0].lower(): row[1] for row in cur.fetchall()}

cur.execute("SELECT utility_name_local, utility_id FROM utilities;")
utility_map = {row[0]: row[1] for row in cur.fetchall()}

print(f'  Loaded: sector={len(sector_map)}, app={len(application_map)}, sub_app={len(sub_application_map)}, utility={len(utility_map)}')

# Load JSON
print('\n[2/5] Loading JSON...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'  Loaded {len(data)} records')

# Clear ONLY projects table
print('\n[3/5] Clearing projects table...')
cur.execute("DELETE FROM projects;")
cur.execute("ALTER SEQUENCE projects_project_id_seq RESTART WITH 1;")
print('  Cleared projects table only')

# Insert
print('\n[4/5] Inserting projects...')
CURRENT_YEAR = 2026
inserted = 0
errors = 0

for i, record in enumerate(data):
    try:
        project_name = record.get('Column1.Project Name (PN)')
        project_description = record.get('Column1.Project Description (PD)')
        description_english = record.get('Column1.Project Description (PD)_EN')
        
        sector_id = sector_map.get(record.get('Sector'))
        application_id = application_map.get(record.get('Application'))
        sub_application_id = sub_application_map.get(record.get('Sub-application'))
        
        # Status based on years
        cip_start = record.get('Column1.CIPStartYear')
        cip_end = record.get('Column1.CIPEndYear')
        try:
            start_year = int(cip_start) if cip_start else None
            end_year = int(cip_end) if cip_end else None
        except:
            start_year = None
            end_year = None
        
        if start_year and end_year:
            if start_year > CURRENT_YEAR:
                status_id = 1
            elif start_year <= CURRENT_YEAR <= end_year:
                status_id = 2
            elif end_year < CURRENT_YEAR:
                status_id = 3
            else:
                status_id = 1
        else:
            status_id = 1
        
        status_tag = record.get('Status Tags', '')
        project_type_id = project_type_map.get(status_tag.lower() if status_tag else '')
        
        utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
        utility_id = utility_map.get(utility_local)
        utility_name = record.get('Column1.CIP Excel Document Utility Name - English Language')
        
        cur.execute("""
            INSERT INTO projects (project_name, project_description, description_english, 
                sector_id, application_id, sub_application_id, status_id, project_type_id, 
                utility_id, utility_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (project_name, project_description, description_english, sector_id, 
              application_id, sub_application_id, status_id, project_type_id, 
              utility_id, utility_name))
        
        inserted += 1
        if inserted % 2000 == 0:
            print(f'  Inserted {inserted}...')
            
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f'  Error at {i}: {e}')

print(f'\n[5/5] Done!')
print(f'  Inserted: {inserted}')
print(f'  Errors: {errors}')

# Verify
cur.execute("SELECT COUNT(*) FROM projects")
print(f'\nTotal projects in database: {cur.fetchone()[0]}')

cur.close()
conn.close()
