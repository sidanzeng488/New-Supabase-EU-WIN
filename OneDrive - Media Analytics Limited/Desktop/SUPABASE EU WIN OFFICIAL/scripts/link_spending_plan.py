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
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code != 200:
            print(f"Error fetching {table_name}: {response.status_code} - {response.text}")
            break
            
        batch = response.json()
        if not batch:
            break
            
        records.extend(batch)
        offset += limit
        
        if len(batch) < limit:
            break
    
    return records

def check_table_structure():
    """Check the structure of utilities and projects tables"""
    print("=" * 60)
    print("Step 1: Checking table structures")
    print("=" * 60)
    
    # Check utilities table
    print("\nChecking 'utilities' table...")
    url = f"{SUPABASE_URL}/rest/v1/utilities?limit=1"
    response = requests.get(url, headers=HEADERS_WITH_RETURN)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"  Columns: {list(data[0].keys())}")
        else:
            print("  Table exists but is empty")
    else:
        print(f"  Error: {response.status_code} - {response.text}")
        return False
    
    # Check projects table
    print("\nChecking 'projects' table...")
    url = f"{SUPABASE_URL}/rest/v1/projects?limit=1"
    response = requests.get(url, headers=HEADERS_WITH_RETURN)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"  Columns: {list(data[0].keys())}")
        else:
            print("  Table exists but is empty")
    else:
        print(f"  Error: {response.status_code} - {response.text}")
        return False
    
    return True

def build_mappings():
    """Build name to ID mappings for utilities and projects"""
    print("\n" + "=" * 60)
    print("Step 2: Building name-to-ID mappings")
    print("=" * 60)
    
    # Fetch utilities
    print("\nFetching utilities...")
    utilities = fetch_all_records("utilities", "utility_id,utility_name")
    print(f"  Found {len(utilities)} utilities")
    
    # Build utility name -> id mapping
    utility_map = {}
    for u in utilities:
        name = u.get('utility_name', '')
        if name:
            utility_map[name.strip().lower()] = u['utility_id']
    
    # Fetch projects
    print("\nFetching projects...")
    projects = fetch_all_records("projects", "project_id,project_name")
    print(f"  Found {len(projects)} projects")
    
    # Build project name -> id mapping
    project_map = {}
    for p in projects:
        name = p.get('project_name', '')
        if name:
            project_map[name.strip().lower()] = p['project_id']
    
    return utility_map, project_map

def get_unique_spending_names():
    """Get unique utility and project names from spending_plan"""
    print("\n" + "=" * 60)
    print("Step 3: Getting unique names from spending_plan")
    print("=" * 60)
    
    # Get distinct utility names
    print("\nFetching distinct utility names...")
    url = f"{SUPABASE_URL}/rest/v1/rpc/get_distinct_utility_names"
    
    # Since we can't use RPC, let's fetch spending_plan and get unique names
    spending = fetch_all_records("spending_plan", "utility_name,project_name")
    
    utility_names = set()
    project_names = set()
    
    for s in spending:
        if s.get('utility_name'):
            utility_names.add(s['utility_name'])
        if s.get('project_name'):
            project_names.add(s['project_name'])
    
    print(f"  Unique utility names in spending_plan: {len(utility_names)}")
    print(f"  Unique project names in spending_plan: {len(project_names)}")
    
    return utility_names, project_names

def analyze_matches(utility_map, project_map, spending_utility_names, spending_project_names):
    """Analyze how many names can be matched"""
    print("\n" + "=" * 60)
    print("Step 4: Analyzing matches")
    print("=" * 60)
    
    # Match utilities
    matched_utilities = 0
    unmatched_utilities = []
    for name in spending_utility_names:
        if name.strip().lower() in utility_map:
            matched_utilities += 1
        else:
            unmatched_utilities.append(name)
    
    print(f"\nUtilities:")
    print(f"  Matched: {matched_utilities}/{len(spending_utility_names)}")
    if unmatched_utilities and len(unmatched_utilities) <= 20:
        print(f"  Unmatched: {unmatched_utilities}")
    elif unmatched_utilities:
        print(f"  Unmatched (first 20): {unmatched_utilities[:20]}")
    
    # Match projects
    matched_projects = 0
    unmatched_projects = []
    for name in spending_project_names:
        if name.strip().lower() in project_map:
            matched_projects += 1
        else:
            unmatched_projects.append(name)
    
    print(f"\nProjects:")
    print(f"  Matched: {matched_projects}/{len(spending_project_names)}")
    if unmatched_projects and len(unmatched_projects) <= 10:
        print(f"  Unmatched: {unmatched_projects}")
    elif unmatched_projects:
        print(f"  Unmatched (first 10): {unmatched_projects[:10]}")
    
    return matched_utilities, matched_projects, unmatched_utilities, unmatched_projects

def update_spending_plan_ids(utility_map, project_map, batch_size=100):
    """Update spending_plan records with utility_id and project_id"""
    print("\n" + "=" * 60)
    print("Step 5: Updating spending_plan with IDs")
    print("=" * 60)
    
    # Fetch all spending records
    print("\nFetching spending_plan records...")
    spending = fetch_all_records("spending_plan", "spending_id,utility_name,project_name")
    print(f"  Total records: {len(spending)}")
    
    # Prepare updates
    updates = []
    matched_utility_count = 0
    matched_project_count = 0
    
    for s in spending:
        utility_id = None
        project_id = None
        
        utility_name = s.get('utility_name', '')
        project_name = s.get('project_name', '')
        
        if utility_name and utility_name.strip().lower() in utility_map:
            utility_id = utility_map[utility_name.strip().lower()]
            matched_utility_count += 1
        
        if project_name and project_name.strip().lower() in project_map:
            project_id = project_map[project_name.strip().lower()]
            matched_project_count += 1
        
        if utility_id is not None or project_id is not None:
            update = {'spending_id': s['spending_id']}
            if utility_id is not None:
                update['utility_id'] = utility_id
            if project_id is not None:
                update['project_id'] = project_id
            updates.append(update)
    
    print(f"\nRecords with matched utility_id: {matched_utility_count}")
    print(f"Records with matched project_id: {matched_project_count}")
    print(f"Total updates to apply: {len(updates)}")
    
    if not updates:
        print("No updates to apply.")
        return
    
    # Apply updates in batches
    print(f"\nApplying updates in batches of {batch_size}...")
    success_count = 0
    error_count = 0
    
    for i in range(0, len(updates), batch_size):
        batch = updates[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(updates) + batch_size - 1) // batch_size
        
        # Update each record individually (Supabase REST API doesn't support bulk update)
        for update in batch:
            spending_id = update.pop('spending_id')
            url = f"{SUPABASE_URL}/rest/v1/spending_plan?spending_id=eq.{spending_id}"
            
            try:
                response = requests.patch(url, headers=HEADERS, json=update)
                if response.status_code in [200, 204]:
                    success_count += 1
                else:
                    error_count += 1
                    if error_count <= 5:
                        print(f"  Error updating {spending_id}: {response.status_code} - {response.text[:100]}")
            except Exception as e:
                error_count += 1
                if error_count <= 5:
                    print(f"  Exception updating {spending_id}: {str(e)}")
        
        print(f"Batch {batch_num}/{total_batches}: Processed {len(batch)} records (Success: {success_count}, Errors: {error_count})")
        
        # Small delay
        if batch_num % 10 == 0:
            time.sleep(0.5)
    
    print(f"\n=== Update Complete ===")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")

def main():
    print("=" * 60)
    print("Spending Plan - Link to Projects and Utilities")
    print("=" * 60)
    print(f"Target: {SUPABASE_URL}")
    
    # Step 1: Check table structures
    if not check_table_structure():
        print("\nError: Required tables not found. Exiting.")
        return
    
    # Step 2: Build mappings
    utility_map, project_map = build_mappings()
    
    if not utility_map and not project_map:
        print("\nNo utilities or projects found. Cannot create links.")
        return
    
    # Step 3: Get unique names from spending_plan
    spending_utility_names, spending_project_names = get_unique_spending_names()
    
    # Step 4: Analyze matches
    analyze_matches(utility_map, project_map, spending_utility_names, spending_project_names)
    
    # Step 5: Ask user to continue
    print("\n" + "=" * 60)
    print("Ready to update spending_plan table")
    print("=" * 60)
    print("\nThis will add utility_id and project_id columns and update records.")
    print("Note: First, please run the following SQL in Supabase SQL Editor to add columns:")
    print("""
-- Add ID columns to spending_plan
ALTER TABLE public.spending_plan 
ADD COLUMN IF NOT EXISTS utility_id INTEGER,
ADD COLUMN IF NOT EXISTS project_id INTEGER;

-- Create indexes for the new columns  
CREATE INDEX IF NOT EXISTS idx_spending_plan_utility_id ON public.spending_plan(utility_id);
CREATE INDEX IF NOT EXISTS idx_spending_plan_project_id ON public.spending_plan(project_id);
""")
    
    input("\nPress Enter after running the SQL, or Ctrl+C to cancel...")
    
    # Step 6: Update records
    update_spending_plan_ids(utility_map, project_map)
    
    print("\n" + "=" * 60)
    print("Optional: Add foreign key constraints")
    print("=" * 60)
    print("""
After verifying the data, you can add foreign key constraints:

-- Add foreign key to utilities (optional)
ALTER TABLE public.spending_plan 
ADD CONSTRAINT spending_plan_utility_id_fkey 
FOREIGN KEY (utility_id) REFERENCES public.utilities(utility_id);

-- Add foreign key to projects (optional)
ALTER TABLE public.spending_plan 
ADD CONSTRAINT spending_plan_project_id_fkey 
FOREIGN KEY (project_id) REFERENCES public.projects(project_id);
""")

if __name__ == "__main__":
    main()
