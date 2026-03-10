"""
Update existing project names in database by appending Location
Only updates the specific projects, preserves all other data
"""
import psycopg2
import json

print('='*60)
print('Update Project Names in Database (Preserve Other Data)')
print('='*60)

# Connect to database
conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
conn.autocommit = True
cur = conn.cursor()

# Read JSON to get the location mapping
print('\n[1/3] Reading JSON for location mapping...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build mapping from old name to new names with locations
# The JSON has already been updated, so we need the original name
old_name = 'Realizzazione vasca di prima pioggia conforme al RR 6/2019'

# Get all new names from JSON (they now have location appended)
new_names = []
for record in data:
    pn = record.get('Column1.Project Name (PN)')
    if pn and pn.startswith(old_name + '-'):
        new_names.append(pn)

print(f'  Found {len(new_names)} updated names in JSON')

# Get existing projects with the old name
print('\n[2/3] Finding projects to update in database...')
cur.execute('''
    SELECT project_id, project_name 
    FROM projects 
    WHERE project_name = %s
    ORDER BY project_id
''', (old_name,))
old_projects = cur.fetchall()
print(f'  Found {len(old_projects)} projects with old name')

# Update each project with a unique new name
print('\n[3/3] Updating project names...')
updated = 0
# Remove duplicates from new_names and make a list
unique_new_names = list(dict.fromkeys(new_names))

for i, (project_id, _) in enumerate(old_projects):
    if i < len(unique_new_names):
        new_name = unique_new_names[i]
        cur.execute('''
            UPDATE projects 
            SET project_name = %s 
            WHERE project_id = %s
        ''', (new_name, project_id))
        updated += 1
        print(f'  Updated project {project_id}: {new_name}')
    else:
        print(f'  Warning: No new name available for project {project_id}')

print('\n' + '='*60)
print(f'Updated {updated} projects')
print('='*60)

# Verify
print('\nVerification - projects with updated names:')
cur.execute('''
    SELECT project_id, project_name 
    FROM projects 
    WHERE project_name LIKE %s
    ORDER BY project_id
''', (old_name + '-%',))
for row in cur.fetchall():
    print(f'  [{row[0]}] {row[1]}')

cur.close()
conn.close()
print('\nDone!')
