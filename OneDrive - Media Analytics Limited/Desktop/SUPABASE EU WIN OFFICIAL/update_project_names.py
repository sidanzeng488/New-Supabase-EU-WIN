"""
Update project names in merge_final.json by appending Location
For projects named "Realizzazione vasca di prima pioggia conforme al RR 6/2019"
"""
import json

print('='*60)
print('Update Project Names with Location')
print('='*60)

# Read JSON file
print('\n[1/3] Reading merge_final.json...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'  Loaded {len(data)} records')

# Find and update matching projects
print('\n[2/3] Updating project names...')
target_name = 'Realizzazione vasca di prima pioggia conforme al RR 6/2019'
updated_count = 0

for record in data:
    project_name = record.get('Column1.Project Name (PN)', '')
    location = record.get('Column1.Location', '')
    
    # Check if this is the target project and has location
    if project_name == target_name and location:
        new_name = f'{project_name}-{location}'
        record['Column1.Project Name (PN)'] = new_name
        updated_count += 1
        print(f'  Updated: {new_name}')

print(f'\n  Total updated: {updated_count} records')

# Save updated JSON
print('\n[3/3] Saving updated merge_final.json...')
with open('data/merge_final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('  Saved!')

print('\n' + '='*60)
print('Done! Now run the import script to refresh the database.')
print('='*60)
