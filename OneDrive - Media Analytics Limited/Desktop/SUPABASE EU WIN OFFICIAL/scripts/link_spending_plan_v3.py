import requests
import json
import sys
import os
import time

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = 'https://mrkjnptfrxdemcojpdnr.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ya2pucHRmcnhkZW1jb2pwZG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDU2MTEsImV4cCI6MjA4ODM4MTYxMX0.FsIVmoRGlZbL5LcIclHYcusJM0KMnL4OsNyk3-ORNd8'

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}
HEADERS_MIN = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

def fetch_all(table, fields='*'):
    records, offset, limit = [], 0, 1000
    while True:
        r = requests.get(f'{SUPABASE_URL}/rest/v1/{table}?select={fields}&offset={offset}&limit={limit}', headers=HEADERS)
        if r.status_code != 200:
            print(f"Error fetching {table}: {r.status_code}")
            break
        batch = r.json()
        if not batch: break
        records.extend(batch)
        if (offset + limit) % 10000 == 0:
            print(f"  Fetched {len(records)} from {table}...")
        offset += limit
        if len(batch) < limit: break
    return records

def main():
    print("=" * 60)
    print("Link Spending Plan using correct utility names")
    print("=" * 60)
    
    # Step 1: Load merge_final.json to build project_name -> utility mapping
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    json_path = os.path.join(project_dir, 'data', 'merge_final.json')
    
    print(f"\nStep 1: Loading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        merge_data = json.load(f)
    print(f"Loaded {len(merge_data)} records from merge_final.json")
    
    # Build project_name -> (utility_name_local, utility_name_en) mapping
    project_to_utility = {}
    for record in merge_data:
        project_name = record.get('Column1.Project Name (PN)', '')
        utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language', '')
        utility_en = record.get('Column1.CIP Excel Document Utility Name - English Language', '')
        
        if project_name:
            project_to_utility[project_name.strip().lower()] = {
                'local': utility_local.strip() if utility_local else '',
                'en': utility_en.strip() if utility_en else ''
            }
    
    print(f"Built project->utility mapping: {len(project_to_utility)} entries")
    
    # Step 2: Fetch utilities and build name->id mapping
    print("\nStep 2: Fetching utilities...")
    utilities = fetch_all('utilities', 'utility_id,utility_name_local,Utility_Name_EN')
    print(f"Total utilities: {len(utilities)}")
    
    utility_map = {}
    for u in utilities:
        uid = u['utility_id']
        if u.get('utility_name_local'):
            utility_map[u['utility_name_local'].strip().lower()] = uid
        if u.get('Utility_Name_EN'):
            utility_map[u['Utility_Name_EN'].strip().lower()] = uid
    print(f"Utility name->id mapping: {len(utility_map)} entries")
    
    # Step 3: Fetch projects and build name->id mapping
    print("\nStep 3: Fetching projects...")
    projects = fetch_all('projects', 'project_id,project_name')
    print(f"Total projects: {len(projects)}")
    
    project_map = {}
    for p in projects:
        if p.get('project_name'):
            project_map[p['project_name'].strip().lower()] = p['project_id']
    print(f"Project name->id mapping: {len(project_map)} entries")
    
    # Step 4: Fetch spending_plan
    print("\nStep 4: Fetching spending_plan...")
    spending = fetch_all('spending_plan', 'spending_id,project_name')
    print(f"Total spending_plan records: {len(spending)}")
    
    # Step 5: Analyze matches
    print("\nStep 5: Analyzing matches...")
    matched_utility = 0
    matched_project = 0
    
    for s in spending[:1000]:  # Sample first 1000 for analysis
        project_name = s.get('project_name', '')
        if not project_name:
            continue
            
        # Get utility names from merge_final mapping
        utility_info = project_to_utility.get(project_name.strip().lower(), {})
        utility_local = utility_info.get('local', '')
        utility_en = utility_info.get('en', '')
        
        # Try to match utility
        uid = None
        if utility_local and utility_local.strip().lower() in utility_map:
            uid = utility_map[utility_local.strip().lower()]
        elif utility_en and utility_en.strip().lower() in utility_map:
            uid = utility_map[utility_en.strip().lower()]
        
        if uid:
            matched_utility += 1
        
        # Try to match project
        if project_name.strip().lower() in project_map:
            matched_project += 1
    
    print(f"Sample analysis (first 1000):")
    print(f"  Utility match rate: {matched_utility}/1000 ({100*matched_utility/1000:.1f}%)")
    print(f"  Project match rate: {matched_project}/1000 ({100*matched_project/1000:.1f}%)")
    
    # Step 6: Update all records
    print("\nStep 6: Updating spending_plan records...")
    success, errors, skipped = 0, 0, 0
    total = len(spending)
    
    for i, s in enumerate(spending):
        project_name = s.get('project_name', '')
        if not project_name:
            skipped += 1
            continue
        
        # Get utility names from merge_final mapping
        utility_info = project_to_utility.get(project_name.strip().lower(), {})
        utility_local = utility_info.get('local', '')
        utility_en = utility_info.get('en', '')
        
        # Try to match utility
        uid = None
        if utility_local and utility_local.strip().lower() in utility_map:
            uid = utility_map[utility_local.strip().lower()]
        elif utility_en and utility_en.strip().lower() in utility_map:
            uid = utility_map[utility_en.strip().lower()]
        
        # Try to match project
        pid = project_map.get(project_name.strip().lower())
        
        if uid is None and pid is None:
            skipped += 1
            continue
        
        # Build update
        data = {}
        if uid is not None:
            data['utility_id'] = uid
        if pid is not None:
            data['project_id'] = pid
        
        # Update record
        try:
            r = requests.patch(
                f'{SUPABASE_URL}/rest/v1/spending_plan?spending_id=eq.{s["spending_id"]}',
                headers=HEADERS_MIN,
                json=data
            )
            if r.status_code in [200, 204]:
                success += 1
            else:
                errors += 1
                if errors <= 3:
                    print(f"Error: {r.status_code} - {r.text[:100]}")
        except Exception as e:
            errors += 1
        
        # Progress
        if (i + 1) % 5000 == 0:
            print(f"Progress: {i+1}/{total} (Success: {success}, Errors: {errors}, Skipped: {skipped})")
    
    print(f"\n{'='*60}")
    print("Update Complete!")
    print(f"{'='*60}")
    print(f"Total: {total}")
    print(f"Success: {success}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")

if __name__ == "__main__":
    main()
