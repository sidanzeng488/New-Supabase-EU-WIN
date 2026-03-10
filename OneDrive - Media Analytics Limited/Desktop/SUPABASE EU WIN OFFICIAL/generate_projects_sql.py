"""
Generate SQL INSERT statements for projects from merge_final.json
"""
import json
import psycopg2

print('Generating SQL for projects import...')

# Connect to get lookup mappings
conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

# Load mappings
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

cur.close()
conn.close()

print(f'Loaded mappings: sector={len(sector_map)}, app={len(application_map)}, sub_app={len(sub_application_map)}, utility={len(utility_map)}')

# Load JSON
print('Loading JSON...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'Loaded {len(data)} records')

# Current year for status
CURRENT_YEAR = 2026

def escape_sql(val):
    """Escape single quotes for SQL"""
    if val is None:
        return 'NULL'
    val = str(val).replace("'", "''")
    return f"'{val}'"

# Generate SQL
print('Generating SQL...')
sql_lines = []
sql_lines.append('-- Projects Import SQL')
sql_lines.append('-- Generated from merge_final.json')
sql_lines.append('')
sql_lines.append('-- Clear existing data')
sql_lines.append('DELETE FROM technology_project;')
sql_lines.append('DELETE FROM theme_project_link;')
sql_lines.append('DELETE FROM project_plant_link;')
sql_lines.append('DELETE FROM project_notice_link;')
sql_lines.append('DELETE FROM spending_plan;')
sql_lines.append('DELETE FROM projects;')
sql_lines.append('ALTER SEQUENCE projects_project_id_seq RESTART WITH 1;')
sql_lines.append('')
sql_lines.append('-- Insert projects')

for i, record in enumerate(data):
    project_name = record.get('Column1.Project Name (PN)')
    project_description = record.get('Column1.Project Description (PD)')
    description_english = record.get('Column1.Project Description (PD)_EN')
    
    sector_name = record.get('Sector')
    sector_id = sector_map.get(sector_name)
    
    application_name = record.get('Application')
    application_id = application_map.get(application_name)
    
    sub_application_name = record.get('Sub-application')
    sub_application_id = sub_application_map.get(sub_application_name)
    
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
    
    status_tag = record.get('Status Tags', '').lower() if record.get('Status Tags') else ''
    project_type_id = project_type_map.get(status_tag)
    
    utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
    utility_id = utility_map.get(utility_local)
    utility_name = record.get('Column1.CIP Excel Document Utility Name - English Language')
    
    # Build INSERT
    sql = f"""INSERT INTO projects (project_name, project_description, description_english, sector_id, application_id, sub_application_id, status_id, project_type_id, utility_id, utility_name) VALUES ({escape_sql(project_name)}, {escape_sql(project_description)}, {escape_sql(description_english)}, {sector_id or 'NULL'}, {application_id or 'NULL'}, {sub_application_id or 'NULL'}, {status_id}, {project_type_id or 'NULL'}, {utility_id or 'NULL'}, {escape_sql(utility_name)});"""
    
    sql_lines.append(sql)

sql_lines.append('')
sql_lines.append("SELECT 'Projects import completed! Total: ' || COUNT(*) FROM projects;")

# Write SQL file
output_file = 'sql/import_projects.sql'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print(f'\nSQL file generated: {output_file}')
print(f'Total INSERT statements: {len(data)}')
print('\nYou can now run this SQL in Supabase SQL Editor')
