import psycopg2
import pandas as pd

# Read Excel file
df = pd.read_excel('data/Utility_to_treatment_plant_matching_batch_1.xlsx')

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

# Get all plants
cur.execute('SELECT plant_id, plant_name FROM plants')
db_plants = cur.fetchall()
db_names = {p[1]: p[0] for p in db_plants}

print(f'Total plants in DB: {len(db_plants)}')
print(f'Total rows in Excel: {len(df)}')

# Match all
matched = 0
unmatched = []
match_results = []

for idx, row in df.iterrows():
    uww_name = row['uwwName']
    utility_id = row['utility_id']
    
    if pd.isna(uww_name):
        continue
        
    if uww_name in db_names:
        matched += 1
        match_results.append({
            'plant_id': db_names[uww_name],
            'plant_name': uww_name,
            'utility_id': utility_id
        })
    else:
        unmatched.append(uww_name)

print(f'\nMatched: {matched}')
print(f'Unmatched: {len(unmatched)}')

print('\n=== First 20 Unmatched Names ===')
for name in unmatched[:20]:
    print(f'  - {name}')

print('\n=== First 10 Match Results ===')
for r in match_results[:10]:
    print(f'  plant_id={r["plant_id"]}, utility_id={r["utility_id"]}, name={r["plant_name"]}')

# Check current plant_utility_link table
cur.execute('SELECT COUNT(*) FROM plant_utility_link')
current_count = cur.fetchone()[0]
print(f'\nCurrent records in plant_utility_link: {current_count}')

cur.close()
conn.close()
