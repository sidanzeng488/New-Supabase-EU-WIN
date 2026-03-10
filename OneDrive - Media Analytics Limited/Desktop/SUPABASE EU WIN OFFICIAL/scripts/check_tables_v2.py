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

# Check utilities with select=*
print("=" * 60)
print("Checking utilities table (select=*)")
print("=" * 60)

url = f"{SUPABASE_URL}/rest/v1/utilities?select=*&limit=5"
response = requests.get(url, headers=HEADERS)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:1000]}")

# Check projects with select=*
print("\n" + "=" * 60)
print("Checking projects table (select=*)")
print("=" * 60)

url = f"{SUPABASE_URL}/rest/v1/projects?select=*&limit=5"
response = requests.get(url, headers=HEADERS)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:1000]}")

# Check count using HEAD request
print("\n" + "=" * 60)
print("Checking record counts")
print("=" * 60)

for table in ["utilities", "projects", "spending_plan"]:
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    headers_count = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "count=exact",
        "Range-Unit": "items",
        "Range": "0-0"
    }
    response = requests.get(url, headers=headers_count)
    content_range = response.headers.get('content-range', 'N/A')
    print(f"{table}: {content_range}")
