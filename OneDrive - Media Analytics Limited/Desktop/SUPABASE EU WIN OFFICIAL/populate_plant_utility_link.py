"""
Populate plant_utility_link table from Utility_to_treatment_plant_matching_batch_1.xlsx
"""
import psycopg2
import pandas as pd

# Read Excel file
print('=' * 60)
print('Populate plant_utility_link Table')
print('Source: Utility_to_treatment_plant_matching_batch_1.xlsx')
print('=' * 60)

df = pd.read_excel('data/Utility_to_treatment_plant_matching_batch_1.xlsx')
print(f'\n[1/4] Loaded Excel file: {len(df)} rows')

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
print('[2/4] Connected to database')

# Get plant_id lookup from plant_name
cur.execute('SELECT plant_id, plant_name FROM plants')
db_plants = cur.fetchall()
plant_name_to_id = {p[1]: p[0] for p in db_plants}
print(f'       Loaded {len(plant_name_to_id)} plants from DB')

# Prepare data
print('\n[3/4] Preparing data...')
insert_data = []
for idx, row in df.iterrows():
    uww_name = row['uwwName']
    utility_id = int(row['utility_id'])
    
    if pd.isna(uww_name):
        continue
    
    if uww_name in plant_name_to_id:
        plant_id = plant_name_to_id[uww_name]
        insert_data.append((plant_id, utility_id))

print(f'       Prepared {len(insert_data)} records to insert')

# Clear existing data (optional - uncomment if needed)
# cur.execute('DELETE FROM plant_utility_link')
# print('       Cleared existing records')

# Insert data
print('\n[4/4] Inserting records...')
inserted = 0
skipped = 0
errors = 0

for plant_id, utility_id in insert_data:
    try:
        # Check if record already exists
        cur.execute('''
            SELECT 1 FROM plant_utility_link 
            WHERE plant_id = %s AND utility_id = %s
        ''', (plant_id, utility_id))
        
        if cur.fetchone():
            skipped += 1
            continue
        
        cur.execute('''
            INSERT INTO plant_utility_link (plant_id, utility_id)
            VALUES (%s, %s)
        ''', (plant_id, utility_id))
        inserted += 1
        
    except Exception as e:
        errors += 1
        print(f'  Error: plant_id={plant_id}, utility_id={utility_id}: {e}')

print(f'\n' + '=' * 60)
print('Results:')
print(f'  Inserted: {inserted}')
print(f'  Skipped (already exists): {skipped}')
print(f'  Errors: {errors}')
print('=' * 60)

# Verify
cur.execute('SELECT COUNT(*) FROM plant_utility_link')
total = cur.fetchone()[0]
print(f'\nTotal records in plant_utility_link: {total}')

# Show sample records
print('\nSample records:')
cur.execute('''
    SELECT pul.plant_id, p.plant_name, pul.utility_id, u.utility_name_en
    FROM plant_utility_link pul
    JOIN plants p ON pul.plant_id = p.plant_id
    JOIN utilities u ON pul.utility_id = u.utility_id
    LIMIT 10
''')
for row in cur.fetchall():
    print(f'  Plant {row[0]} ({row[1][:30]}...) -> Utility {row[2]} ({row[3]})')

cur.close()
conn.close()
print('\nDone!')
