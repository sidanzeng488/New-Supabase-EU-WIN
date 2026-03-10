import json
import requests
import sys
import os

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

def main():
    print("=" * 60)
    print("Update utilities with original utility name")
    print("=" * 60)
    
    # Load merge_final.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    json_path = os.path.join(project_dir, 'data', 'merge_final.json')
    
    print(f"\nLoading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} records")
    
    # Build mapping: (utility_name_local OR utility_name_en) -> utility_name_original
    # We need to map from the CIP document names to Column1.utilityName
    utility_mapping = {}
    
    for record in data:
        utility_original = record.get('Column1.utilityName', '')
        utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language', '')
        utility_en = record.get('Column1.CIP Excel Document Utility Name - English Language', '')
        
        if utility_original:
            if utility_local:
                key = utility_local.strip().lower()
                if key not in utility_mapping:
                    utility_mapping[key] = utility_original.strip()
            if utility_en:
                key = utility_en.strip().lower()
                if key not in utility_mapping:
                    utility_mapping[key] = utility_original.strip()
    
    print(f"Built mapping with {len(utility_mapping)} entries")
    
    # Show some examples
    print("\nSample mappings:")
    for i, (key, value) in enumerate(list(utility_mapping.items())[:5]):
        print(f"  '{key[:50]}...' -> '{value}'")
    
    # Fetch utilities
    print("\nFetching utilities...")
    url = f"{SUPABASE_URL}/rest/v1/utilities?select=utility_id,utility_name_local,Utility_Name_EN"
    response = requests.get(url, headers=HEADERS)
    utilities = response.json()
    print(f"Found {len(utilities)} utilities")
    
    # Update each utility
    print("\nUpdating utilities...")
    success = 0
    not_found = 0
    
    for u in utilities:
        utility_id = u['utility_id']
        utility_local = u.get('utility_name_local', '')
        utility_en = u.get('Utility_Name_EN', '')
        
        # Try to find original name
        original_name = None
        if utility_local:
            original_name = utility_mapping.get(utility_local.strip().lower())
        if not original_name and utility_en:
            original_name = utility_mapping.get(utility_en.strip().lower())
        
        if original_name:
            # Update record
            update_url = f"{SUPABASE_URL}/rest/v1/utilities?utility_id=eq.{utility_id}"
            response = requests.patch(update_url, headers=HEADERS_MIN, json={
                'utility_name_original': original_name
            })
            if response.status_code in [200, 204]:
                success += 1
            else:
                print(f"Error updating {utility_id}: {response.status_code}")
        else:
            not_found += 1
            print(f"No mapping found for: {utility_local or utility_en}")
    
    print(f"\n{'='*60}")
    print("Update Complete!")
    print(f"{'='*60}")
    print(f"Success: {success}")
    print(f"Not found: {not_found}")

if __name__ == "__main__":
    main()
