import csv
import os
import sys
import requests
import json
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

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
csv_path = os.path.join(project_dir, 'data', 'spending_plan_import.csv')

def create_table():
    """Create spending_plan table using SQL"""
    sql = """
    -- Drop table if exists (optional, comment out if you want to keep existing data)
    -- DROP TABLE IF EXISTS public.spending_plan;
    
    -- Create spending_plan table
    CREATE TABLE IF NOT EXISTS public.spending_plan (
        spending_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        utility_name TEXT,
        project_name TEXT,
        year TEXT NOT NULL,
        cost_type TEXT NOT NULL DEFAULT 'annual',
        cost NUMERIC NOT NULL DEFAULT 0 CHECK (cost >= 0),
        currency TEXT NOT NULL DEFAULT 'EUR'
    );

    -- Enable RLS
    ALTER TABLE public.spending_plan ENABLE ROW LEVEL SECURITY;

    -- Drop existing policies if any
    DROP POLICY IF EXISTS "Enable all access" ON public.spending_plan;
    
    -- Create access policy
    CREATE POLICY "Enable all access" ON public.spending_plan
        FOR ALL USING (true) WITH CHECK (true);

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_spending_plan_utility_name ON public.spending_plan(utility_name);
    CREATE INDEX IF NOT EXISTS idx_spending_plan_project_name ON public.spending_plan(project_name);
    CREATE INDEX IF NOT EXISTS idx_spending_plan_year ON public.spending_plan(year);
    CREATE INDEX IF NOT EXISTS idx_spending_plan_cost_type ON public.spending_plan(cost_type);
    """
    
    # Execute SQL via REST API
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    # Note: This requires a custom function. Let's use direct table creation check instead
    print("Note: Please create the table manually using SQL Editor if not exists.")
    print("Checking if table exists...")
    
    # Check if table exists by trying to query it
    check_url = f"{SUPABASE_URL}/rest/v1/spending_plan?limit=1"
    response = requests.get(check_url, headers=HEADERS)
    
    if response.status_code == 200:
        print("Table 'spending_plan' exists!")
        return True
    elif response.status_code == 404 or "relation" in response.text.lower():
        print("Table 'spending_plan' does not exist. Please create it first using SQL Editor.")
        print("\nSQL to execute:")
        print(sql)
        return False
    else:
        print(f"Check response: {response.status_code} - {response.text}")
        return False

def upload_data(batch_size=500):
    """Upload data from CSV to Supabase"""
    
    print(f"\nReading CSV from: {csv_path}")
    
    # Read CSV file
    records = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                'utility_name': row['utility_name'],
                'project_name': row['project_name'],
                'year': row['year'],
                'cost_type': row['cost_type'],
                'cost': float(row['cost']),
                'currency': row['currency']
            })
    
    total = len(records)
    print(f"Total records to upload: {total}")
    
    # Upload in batches
    url = f"{SUPABASE_URL}/rest/v1/spending_plan"
    success_count = 0
    error_count = 0
    
    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        try:
            response = requests.post(url, headers=HEADERS, json=batch)
            
            if response.status_code in [200, 201]:
                success_count += len(batch)
                print(f"Batch {batch_num}/{total_batches}: Uploaded {len(batch)} records (Total: {success_count}/{total})")
            else:
                error_count += len(batch)
                print(f"Batch {batch_num}/{total_batches}: ERROR - {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
                # If RLS error, try to continue
                if "row-level security" in response.text.lower():
                    print("  RLS policy may need adjustment. Continuing...")
                    
        except Exception as e:
            error_count += len(batch)
            print(f"Batch {batch_num}/{total_batches}: EXCEPTION - {str(e)}")
        
        # Small delay to avoid rate limiting
        if batch_num % 10 == 0:
            time.sleep(0.5)
    
    print(f"\n=== Upload Complete ===")
    print(f"Success: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Total: {total}")

def main():
    print("=" * 50)
    print("Supabase Spending Plan Upload Script")
    print("=" * 50)
    print(f"Target: {SUPABASE_URL}")
    print()
    
    # Check/create table
    if not create_table():
        print("\nPlease create the table first, then run this script again.")
        return
    
    # Upload data
    upload_data()

if __name__ == "__main__":
    main()
