import requests
import json
import sys
import time

# Fix encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

# Supabase configuration
SUPABASE_URL = "https://mrkjnptfrxdemcojpdnr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ya2pucHRmcnhkZW1jb2pwZG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDU2MTEsImV4cCI6MjA4ODM4MTYxMX0.FsIVmoRGlZbL5LcIclHYcusJM0KMnL4OsNyk3-ORNd8"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

HEADERS_WITH_RETURN = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def fetch_all_records(table_name, select_fields="*"):
    """Fetch all records from a table with pagination"""
    records = []
    offset = 0
    limit = 1000
    
    while True:
        url = f"{SUPABASE_URL}/rest/v1/{table_name}?select={select_fields}&offset={offset}&limit={limit}"
        response = requests.get(url, headers=HEADERS_WITH_RETURN)
        
        if response.status_code != 200:
            print(f"Error fetching {table_name}: {response.status_code} - {response.text[:200]}")
            break
            
        batch = response.json()
        if not batch:
            break
            
        records.extend(batch)
        print(f"  Fetched {len(records)} records from {table_name}...")
        offset += limit
        
        if len(batch) < limit:
            break
    
    return records

def build_utility_mapping():
    """Build utility name to ID mapping"""
    print("\n" + "=" * 60)
    print("Step 1: Building utility name mapping")
    print("=" * 60)
    
    utilities = fetch_all_records("utilities", "utility_id,utility_name_local,Utility_Name_EN")
    print(f"Total utilities: {len(utilities)}")
    
    # Build mapping (lowercase for case-insensitive matching)
    utility_map = {}
    for u in utilities:
        uid = u['utility_id']
        # Map both local and English names
        if u.get('utility_name_local'):
            utility_map[u['utility_name_local'].strip().lower()] = uid
        if u.get('Utility_Name_EN'):
            utility_map[u['Utility_Name_EN'].strip().lower()] = uid
    
    print(f"Utility mapping entries: {len(utility_map)}")
    return utility_map

def build_project_mapping():
    """Build project name to ID mapping"""
    print("\n" + "=" * 60)
    print("Step 2: Building project name mapping")
    print("=" * 60)
    
    projects = fetch_all_records("projects", "project_id,project_name")
    print(f"Total projects: {len(projects)}")
    
    # Build mapping (lowercase for case-insensitive matching)
    project_map = {}
    for p in projects:
        if p.get('project_name'):
            project_map[p['project_name'].strip().lower()] = p['project_id']
    
    print(f"Project mapping entries: {len(project_map)}")
    return project_map

def analyze_spending_plan(utility_map, project_map):
    """Analyze spending_plan and calculate match rates"""
    print("\n" + "=" * 60)
    print("Step 3: Analyzing spending_plan matches")
    print("=" * 60)
    
    # Get unique names from spending_plan
    spending = fetch_all_records("spending_plan", "spending_id,utility_name,project_name")
    print(f"Total spending_plan records: {len(spending)}")
    
    # Get unique names
    utility_names = set()
    project_names = set()
    for s in spending:
        if s.get('utility_name'):
            utility_names.add(s['utility_name'])
        if s.get('project_name'):
            project_names.add(s['project_name'])
    
    print(f"\nUnique utility names in spending_plan: {len(utility_names)}")
    print(f"Unique project names in spending_plan: {len(project_names)}")
    
    # Check matches
    matched_utilities = 0
    unmatched_utilities = []
    for name in utility_names:
        if name.strip().lower() in utility_map:
            matched_utilities += 1
        else:
            unmatched_utilities.append(name)
    
    matched_projects = 0
    unmatched_projects = []
    for name in project_names:
        if name.strip().lower() in project_map:
            matched_projects += 1
        else:
            unmatched_projects.append(name)
    
    print(f"\nUtility match rate: {matched_utilities}/{len(utility_names)} ({100*matched_utilities/len(utility_names):.1f}%)")
    if unmatched_utilities and len(unmatched_utilities) <= 10:
        print(f"Unmatched utilities: {unmatched_utilities}")
    elif unmatched_utilities:
        print(f"Unmatched utilities (first 10): {unmatched_utilities[:10]}")
    
    print(f"\nProject match rate: {matched_projects}/{len(project_names)} ({100*matched_projects/len(project_names):.1f}%)")
    if unmatched_projects and len(unmatched_projects) <= 5:
        print(f"Unmatched projects: {unmatched_projects}")
    elif unmatched_projects:
        print(f"Unmatched projects (first 5): {unmatched_projects[:5]}")
    
    return spending, matched_utilities, matched_projects

def update_spending_plan(spending_records, utility_map, project_map):
    """Update spending_plan with utility_id and project_id"""
    print("\n" + "=" * 60)
    print("Step 4: Updating spending_plan records")
    print("=" * 60)
    
    total = len(spending_records)
    success_count = 0
    error_count = 0
    skip_count = 0
    
    # Process in batches for progress tracking
    batch_size = 500
    
    for i, s in enumerate(spending_records):
        utility_id = None
        project_id = None
        
        # Match utility
        if s.get('utility_name'):
            utility_id = utility_map.get(s['utility_name'].strip().lower())
        
        # Match project
        if s.get('project_name'):
            project_id = project_map.get(s['project_name'].strip().lower())
        
        # Skip if no matches
        if utility_id is None and project_id is None:
            skip_count += 1
            continue
        
        # Build update payload
        update_data = {}
        if utility_id is not None:
            update_data['utility_id'] = utility_id
        if project_id is not None:
            update_data['project_id'] = project_id
        
        # Update record
        url = f"{SUPABASE_URL}/rest/v1/spending_plan?spending_id=eq.{s['spending_id']}"
        try:
            response = requests.patch(url, headers=HEADERS, json=update_data)
            if response.status_code in [200, 204]:
                success_count += 1
            else:
                error_count += 1
                if error_count <= 3:
                    print(f"Error updating {s['spending_id']}: {response.status_code}")
        except Exception as e:
            error_count += 1
        
        # Progress update
        if (i + 1) % batch_size == 0:
            print(f"Progress: {i+1}/{total} (Success: {success_count}, Errors: {error_count}, Skipped: {skip_count})")
    
    print(f"\n=== Update Complete ===")
    print(f"Total records: {total}")
    print(f"Successfully updated: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Skipped (no match): {skip_count}")

def main():
    print("=" * 60)
    print("Spending Plan - Link to Utilities and Projects")
    print("=" * 60)
    print(f"Target: {SUPABASE_URL}")
    
    # Step 1: Build utility mapping
    utility_map = build_utility_mapping()
    
    # Step 2: Build project mapping
    project_map = build_project_mapping()
    
    # Step 3: Analyze matches
    spending_records, matched_u, matched_p = analyze_spending_plan(utility_map, project_map)
    
    # Step 4: Confirm and update
    print("\n" + "=" * 60)
    print("Ready to update spending_plan")
    print("=" * 60)
    print("\nFirst, run this SQL in Supabase SQL Editor to add columns:")
    print("""
-- Add ID columns to spending_plan
ALTER TABLE public.spending_plan 
ADD COLUMN IF NOT EXISTS utility_id INTEGER,
ADD COLUMN IF NOT EXISTS project_id INTEGER;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_spending_plan_utility_id ON public.spending_plan(utility_id);
CREATE INDEX IF NOT EXISTS idx_spending_plan_project_id ON public.spending_plan(project_id);
""")
    
    response = input("\nHave you run the SQL? Press Enter to continue, or 'q' to quit: ")
    if response.lower() == 'q':
        print("Aborted.")
        return
    
    # Step 5: Update records
    update_spending_plan(spending_records, utility_map, project_map)
    
    print("\n" + "=" * 60)
    print("Done! You can now add foreign key constraints (optional):")
    print("=" * 60)
    print("""
-- Add foreign key constraints (optional)
ALTER TABLE public.spending_plan 
ADD CONSTRAINT spending_plan_utility_id_fkey 
FOREIGN KEY (utility_id) REFERENCES public.utilities(utility_id);

ALTER TABLE public.spending_plan 
ADD CONSTRAINT spending_plan_project_id_fkey 
FOREIGN KEY (project_id) REFERENCES public.projects(project_id);
""")

if __name__ == "__main__":
    main()
