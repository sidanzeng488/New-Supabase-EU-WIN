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
cur.execute('SELECT plant_id, plant_name FROM plants ORDER BY plant_name LIMIT 20')
plants = cur.fetchall()

print('Sample plants from DB:')
for p in plants:
    print(f'  ID={p[0]}: {p[1]}')

# Check uwwName from Excel
print('\nSample uwwName from Excel:')
for name in df['uwwName'].head(10):
    print(f'  {name}')

# Check if there's a match
print('\nTrying to match...')
excel_names = set(df['uwwName'].dropna())

cur.execute('SELECT plant_id, plant_name FROM plants')
db_plants = cur.fetchall()
db_names = {p[1]: p[0] for p in db_plants}

matched = 0
unmatched = []
for name in list(excel_names)[:20]:
    if name in db_names:
        matched += 1
        print(f'  MATCH: {name} -> plant_id={db_names[name]}')
    else:
        unmatched.append(name)

print(f'\nMatched: {matched}')
print(f'Sample unmatched:')
for u in unmatched[:5]:
    print(f'  {u}')

cur.close()
conn.close()
