import psycopg2
import json

# Connect to database
conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
conn.autocommit = True
cur = conn.cursor()

print('=' * 60)
print('UTILITY Import Script')
print('Using: Column1.CIP Excel Document Utility Name - Local Language')
print('=' * 60)

# Step 1: Clear existing data
print('\n[1/4] Clearing existing utilities...')
cur.execute("DELETE FROM utilities;")
print('  - Cleared')

# Step 2: Load JSON data
print('\n[2/4] Loading JSON data...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'  - Loaded {len(data)} records')

# Step 3: Extract unique utilities using Local Language name as key
print('\n[3/4] Extracting unique utilities...')
utilities = {}
for record in data:
    # Use Local Language name as the unique key
    utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
    if utility_local and utility_local not in utilities:
        utilities[utility_local] = {
            'utility_name_local': utility_local,
            'utility_name_en': record.get('Column1.CIP Excel Document Utility Name - English Language') or utility_local,
            'country': record.get('Column1.HQ Country'),
            'city': record.get('Column1.City/Subregion')
        }

print(f'  - Found {len(utilities)} unique utilities')

# Step 4: Insert utilities
print('\n[4/4] Inserting utilities into database...')
inserted = 0
for local_name, info in utilities.items():
    try:
        cur.execute("""
            INSERT INTO utilities (utility_name_local, "Utility_Name_EN", country, city)
            VALUES (%s, %s, %s, %s)
            RETURNING utility_id;
        """, (info['utility_name_local'], info['utility_name_en'], info['country'], info['city']))
        utility_id = cur.fetchone()[0]
        inserted += 1
        print(f'  + [{utility_id}] {info["utility_name_local"]} ({info["city"]}, {info["country"]})')
    except Exception as e:
        print(f'  ! Error: {e}')

print('\n' + '=' * 60)
print(f'Import completed: {inserted} utilities inserted')
print('=' * 60)

# Verify
cur.execute("SELECT COUNT(*) FROM utilities;")
count = cur.fetchone()[0]
print(f'\nTotal utilities in database: {count}')

cur.close()
conn.close()
