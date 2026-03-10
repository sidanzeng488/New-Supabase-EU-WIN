import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = "https://mrkjnptfrxdemcojpdnr.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ya2pucHRmcnhkZW1jb2pwZG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDU2MTEsImV4cCI6MjA4ODM4MTYxMX0.FsIVmoRGlZbL5LcIclHYcusJM0KMnL4OsNyk3-ORNd8"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# List of tables to check
tables_to_check = [
    "utilities",
    "projects", 
    "spending_plan",
    "utility",
    "project"
]

print("Checking available tables and their structure...")
print("=" * 60)

for table in tables_to_check:
    url = f"{SUPABASE_URL}/rest/v1/{table}?limit=1"
    response = requests.get(url, headers=HEADERS)
    
    print(f"\n{table}:")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"  Status: EXISTS with data")
            print(f"  Columns: {list(data[0].keys())}")
            print(f"  Sample: {json.dumps(data[0], indent=4, ensure_ascii=False)[:500]}")
        else:
            print(f"  Status: EXISTS but EMPTY")
    elif response.status_code == 404:
        print(f"  Status: NOT FOUND")
    else:
        print(f"  Status: ERROR {response.status_code}")
        print(f"  Message: {response.text[:200]}")

# Also check spending_plan count
print("\n" + "=" * 60)
url = f"{SUPABASE_URL}/rest/v1/spending_plan?select=count"
headers_count = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Prefer": "count=exact"
}
response = requests.head(url, headers=headers_count)
if 'content-range' in response.headers:
    print(f"spending_plan total records: {response.headers['content-range']}")
