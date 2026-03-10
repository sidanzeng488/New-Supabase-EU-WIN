import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = 'https://mrkjnptfrxdemcojpdnr.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ya2pucHRmcnhkZW1jb2pwZG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDU2MTEsImV4cCI6MjA4ODM4MTYxMX0.FsIVmoRGlZbL5LcIclHYcusJM0KMnL4OsNyk3-ORNd8'
HEADERS = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Prefer': 'return=representation'}

# 1. Check sector table
print('=== SECTOR TABLE ===')
r = requests.get(f'{SUPABASE_URL}/rest/v1/sector?select=*', headers=HEADERS)
sectors = r.json()
print(f'Count: {len(sectors)}')
for s in sectors:
    print(f"  {s['sector_id']}: {s['sector_name']}")

# 2. Check application table
print('\n=== APPLICATION TABLE ===')
r = requests.get(f'{SUPABASE_URL}/rest/v1/application?select=*', headers=HEADERS)
apps = r.json()
print(f'Count: {len(apps)}')
for a in apps:
    print(f"  {a['application_id']}: {a['application_name']}")

# 3. Check sub_application table
print('\n=== SUB_APPLICATION TABLE ===')
r = requests.get(f'{SUPABASE_URL}/rest/v1/sub_application?select=*', headers=HEADERS)
sub_apps = r.json()
print(f'Count: {len(sub_apps)}')
for s in sub_apps:
    print(f"  {s['sub_application_id']}: {s['sub_application_name']}")

# 4. Check projects coverage - fetch all records
print('\n=== PROJECTS COVERAGE ===')
projects = []
offset = 0
while True:
    r = requests.get(f'{SUPABASE_URL}/rest/v1/projects?select=project_id,sector_id,application_id,sub_application_id&offset={offset}&limit=1000', headers=HEADERS)
    batch = r.json()
    if not batch:
        break
    projects.extend(batch)
    offset += 1000
    print(f'  Fetched {len(projects)} records...')

total = len(projects)
has_sector = sum(1 for p in projects if p.get('sector_id'))
has_app = sum(1 for p in projects if p.get('application_id'))
has_sub = sum(1 for p in projects if p.get('sub_application_id'))

print(f'\nTotal projects: {total}')
print(f'Has sector_id: {has_sector} ({100*has_sector/total:.1f}%)')
print(f'Has application_id: {has_app} ({100*has_app/total:.1f}%)')
print(f'Has sub_application_id: {has_sub} ({100*has_sub/total:.1f}%)')

# 5. Unique values used in projects
print('\n=== UNIQUE VALUES IN PROJECTS ===')
used_sectors = set(p['sector_id'] for p in projects if p.get('sector_id'))
used_apps = set(p['application_id'] for p in projects if p.get('application_id'))
used_subs = set(p['sub_application_id'] for p in projects if p.get('sub_application_id'))

print(f'sector_id used: {sorted(used_sectors)}')
print(f'application_id used: {sorted(used_apps)}')
print(f'sub_application_id used: {sorted(used_subs)}')
