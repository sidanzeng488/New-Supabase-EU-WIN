import json
import requests
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
    'Prefer': 'return=minimal'
}

def fetch_all(table, fields='*'):
    records = []
    offset = 0
    limit = 1000
    while True:
        r = requests.get(f'{SUPABASE_URL}/rest/v1/{table}?select={fields}&offset={offset}&limit={limit}', 
                        headers={**HEADERS, 'Prefer': 'return=representation'})
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break
        records.extend(batch)
        offset += limit
        if len(batch) < limit:
            break
    return records

def main():
    print("=" * 60)
    print("Populate Technology and Theme Project Links")
    print("=" * 60)
    
    # Step 1: Load merge_final.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    json_path = os.path.join(project_dir, 'data', 'merge_final.json')
    
    print(f"\nStep 1: Loading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} records")
    
    # Step 2: Fetch lookup tables
    print("\nStep 2: Fetching lookup tables...")
    
    technologies = fetch_all('technology', 'technology_id,technology_name')
    tech_map = {t['technology_name'].strip().lower(): t['technology_id'] for t in technologies}
    print(f"  Technologies: {len(tech_map)}")
    
    themes = fetch_all('theme', 'theme_id,theme_name')
    theme_map = {t['theme_name'].strip().lower(): t['theme_id'] for t in themes}
    print(f"  Themes: {len(theme_map)}")
    
    projects = fetch_all('projects', 'project_id,project_name')
    project_map = {p['project_name'].strip().lower(): p['project_id'] for p in projects if p.get('project_name')}
    print(f"  Projects: {len(project_map)}")
    
    # Step 3: Extract links from merge_final.json
    print("\nStep 3: Extracting links...")
    
    tech_links = []  # (project_id, technology_id)
    theme_links = []  # (project_id, theme_id)
    
    for record in data:
        project_name = record.get('Column1.Project Name (PN)', '')
        if not project_name:
            continue
            
        project_id = project_map.get(project_name.strip().lower())
        if not project_id:
            continue
        
        # Technology Tags (can be comma-separated)
        tech_tags = record.get('Technology Tags', '')
        if tech_tags:
            for tag in tech_tags.split(','):
                tag = tag.strip()
                tech_id = tech_map.get(tag.lower())
                if tech_id:
                    tech_links.append((project_id, tech_id))
        
        # Theme Tags (can be comma-separated)
        theme_tags = record.get('Theme Tags', '')
        if theme_tags:
            for tag in theme_tags.split(','):
                tag = tag.strip()
                theme_id = theme_map.get(tag.lower())
                if theme_id:
                    theme_links.append((project_id, theme_id))
    
    # Remove duplicates
    tech_links = list(set(tech_links))
    theme_links = list(set(theme_links))
    
    print(f"  Technology links: {len(tech_links)}")
    print(f"  Theme links: {len(theme_links)}")
    
    # Step 4: Upload technology_project links
    print("\nStep 4: Uploading technology_project links...")
    
    batch_size = 500
    success = 0
    errors = 0
    
    for i in range(0, len(tech_links), batch_size):
        batch = tech_links[i:i+batch_size]
        batch_data = [{'project_id': pid, 'technology_id': tid} for pid, tid in batch]
        
        r = requests.post(f'{SUPABASE_URL}/rest/v1/technology_project', 
                         headers={**HEADERS, 'Prefer': 'return=minimal,resolution=ignore-duplicates'},
                         json=batch_data)
        
        if r.status_code in [200, 201]:
            success += len(batch)
        else:
            # Try one by one for this batch
            for item in batch_data:
                r2 = requests.post(f'{SUPABASE_URL}/rest/v1/technology_project',
                                  headers={**HEADERS, 'Prefer': 'return=minimal'},
                                  json=item)
                if r2.status_code in [200, 201]:
                    success += 1
                else:
                    errors += 1
        
        if (i + batch_size) % 2000 == 0:
            print(f"  Progress: {min(i+batch_size, len(tech_links))}/{len(tech_links)}")
    
    print(f"  Technology links - Success: {success}, Errors: {errors}")
    
    # Step 5: Upload theme_project_link links
    print("\nStep 5: Uploading theme_project_link links...")
    
    success = 0
    errors = 0
    
    for i in range(0, len(theme_links), batch_size):
        batch = theme_links[i:i+batch_size]
        batch_data = [{'project_id': pid, 'theme_id': tid} for pid, tid in batch]
        
        r = requests.post(f'{SUPABASE_URL}/rest/v1/theme_project_link',
                         headers={**HEADERS, 'Prefer': 'return=minimal,resolution=ignore-duplicates'},
                         json=batch_data)
        
        if r.status_code in [200, 201]:
            success += len(batch)
        else:
            # Try one by one
            for item in batch_data:
                r2 = requests.post(f'{SUPABASE_URL}/rest/v1/theme_project_link',
                                  headers={**HEADERS, 'Prefer': 'return=minimal'},
                                  json=item)
                if r2.status_code in [200, 201]:
                    success += 1
                else:
                    errors += 1
        
        if (i + batch_size) % 2000 == 0:
            print(f"  Progress: {min(i+batch_size, len(theme_links))}/{len(theme_links)}")
    
    print(f"  Theme links - Success: {success}, Errors: {errors}")
    
    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)

if __name__ == "__main__":
    main()
