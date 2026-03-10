import psycopg2
import json
from datetime import datetime

# Current year for status determination
CURRENT_YEAR = datetime.now().year  # 2026

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
print('Importing Projects from merge_final.json')
print('=' * 60)

# Step 1: Load lookup mappings
print('\n[1/4] Loading lookup mappings...')

# Sector mapping
cur.execute("SELECT sector_name, sector_id FROM sector;")
sector_map = {row[0]: row[1] for row in cur.fetchall()}
print(f'  - sector: {len(sector_map)} entries')

# Application mapping
cur.execute("SELECT application_name, application_id FROM application;")
application_map = {row[0]: row[1] for row in cur.fetchall()}
print(f'  - application: {len(application_map)} entries')

# Sub-application mapping
cur.execute("SELECT sub_application_name, sub_application_id FROM sub_application;")
sub_application_map = {row[0]: row[1] for row in cur.fetchall()}
print(f'  - sub_application: {len(sub_application_map)} entries')

# Status mapping (normalize to lowercase)
cur.execute("SELECT status_name, status_id FROM status;")
status_map = {row[0].lower(): row[1] for row in cur.fetchall()}
# Add common aliases
status_map['new'] = status_map.get('planned', 1)
status_map['retrofit'] = status_map.get('ongoing', 2)
print(f'  - status: {len(status_map)} entries')

# Project type mapping
cur.execute("SELECT description, project_type_id FROM project_type;")
project_type_map = {row[0].lower(): row[1] for row in cur.fetchall()}
print(f'  - project_type: {len(project_type_map)} entries')

# Utility mapping (by local name)
cur.execute("SELECT utility_name_local, utility_id FROM utilities;")
utility_map = {row[0]: row[1] for row in cur.fetchall()}
print(f'  - utilities: {len(utility_map)} entries')

# Step 2: Load JSON data
print('\n[2/4] Loading JSON data...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'  - Loaded {len(data)} records')

# Step 3: Clear existing projects and related tables, reset sequence
print('\n[3/4] Clearing existing projects and related tables...')
# Clear related tables first (foreign key constraints)
cur.execute("DELETE FROM technology_project;")
print('  - Cleared technology_project')
cur.execute("DELETE FROM theme_project_link;")
print('  - Cleared theme_project_link')
cur.execute("DELETE FROM project_plant_link;")
print('  - Cleared project_plant_link')
cur.execute("DELETE FROM project_notice_link;")
print('  - Cleared project_notice_link')
cur.execute("DELETE FROM spending_plan;")
print('  - Cleared spending_plan')
# Now clear projects
cur.execute("DELETE FROM projects;")
cur.execute("ALTER SEQUENCE projects_project_id_seq RESTART WITH 1;")
print('  - Cleared projects')

# Step 4: Insert projects
print('\n[4/4] Inserting projects...')
inserted = 0
errors = 0

for i, record in enumerate(data):
    try:
        # Extract fields
        project_name = record.get('Column1.Project Name (PN)')
        project_description = record.get('Column1.Project Description (PD)')
        description_english = record.get('Column1.Project Description (PD)_EN')
        
        # Get sector_id
        sector_name = record.get('Sector')
        sector_id = sector_map.get(sector_name)
        
        # Get application_id
        application_name = record.get('Application')
        application_id = application_map.get(application_name)
        
        # Get sub_application_id
        sub_application_name = record.get('Sub-application')
        sub_application_id = sub_application_map.get(sub_application_name)
        
        # Get status_id based on CIP years
        cip_start = record.get('Column1.CIPStartYear')
        cip_end = record.get('Column1.CIPEndYear')
        
        try:
            start_year = int(cip_start) if cip_start else None
            end_year = int(cip_end) if cip_end else None
        except:
            start_year = None
            end_year = None
        
        # Determine status based on years
        if start_year and end_year:
            if start_year > CURRENT_YEAR:
                status_id = 1  # planned
            elif start_year <= CURRENT_YEAR <= end_year:
                status_id = 2  # ongoing
            elif end_year < CURRENT_YEAR:
                status_id = 3  # inactive
            else:
                status_id = 1  # default to planned
        else:
            status_id = 1  # default to planned if years not available
        
        # Get project_type_id from Status Tags (New -> new, Retrofit -> retrofit)
        status_tag = record.get('Status Tags', '').lower()
        project_type_id = project_type_map.get(status_tag)
        
        # Get utility_id
        utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
        utility_id = utility_map.get(utility_local)
        utility_name = record.get('Column1.CIP Excel Document Utility Name - English Language')
        
        # Insert
        cur.execute("""
            INSERT INTO projects (
                project_name, project_description, description_english, sector_id, application_id,
                sub_application_id, status_id, project_type_id, utility_id, utility_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING project_id;
        """, (
            project_name, project_description, description_english, sector_id, application_id,
            sub_application_id, status_id, project_type_id, utility_id, utility_name
        ))
        
        inserted += 1
        
        # Progress update every 1000 records
        if inserted % 1000 == 0:
            print(f'  - Inserted {inserted} projects...')
            
    except Exception as e:
        errors += 1
        if errors <= 5:
            print(f'  ! Error at record {i}: {e}')

print(f'\n  - Total inserted: {inserted}')
print(f'  - Errors: {errors}')

# Summary
print('\n' + '=' * 60)
print('Import Summary')
print('=' * 60)
cur.execute("SELECT COUNT(*) FROM projects;")
count = cur.fetchone()[0]
print(f'Total projects in database: {count}')

# Show sample
print('\nSample projects:')
cur.execute("""
    SELECT project_id, project_name, utility_name 
    FROM projects 
    ORDER BY project_id 
    LIMIT 5;
""")
for row in cur.fetchall():
    name = row[1][:50] + '...' if len(row[1] or '') > 50 else row[1]
    print(f'  [{row[0]}] {name}')

cur.close()
conn.close()

print('\nDone!')
