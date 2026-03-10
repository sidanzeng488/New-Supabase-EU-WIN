import psycopg2

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

# Show all tables
cur.execute('''
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    ORDER BY table_name;
''')
print('All public tables:')
for t in cur.fetchall():
    print(f'  - {t[0]}')

# Show plant_utility_link table structure
print('\nplant_utility_link table structure:')
cur.execute('''
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'plant_utility_link'
    ORDER BY ordinal_position;
''')
cols = cur.fetchall()
if cols:
    for col in cols:
        print(f'  {col[0]}: {col[1]} (nullable: {col[2]})')
else:
    print('  Table does not exist!')

# Show plants table columns
print('\nplants table columns:')
cur.execute('''
    SELECT column_name, data_type FROM information_schema.columns
    WHERE table_name = 'plants'
    ORDER BY ordinal_position;
''')
for col in cur.fetchall():
    print(f'  {col[0]}: {col[1]}')

print('\nutilities table columns:')
cur.execute('''
    SELECT column_name, data_type FROM information_schema.columns
    WHERE table_name = 'utilities'
    ORDER BY ordinal_position;
''')
for col in cur.fetchall():
    print(f'  {col[0]}: {col[1]}')

cur.close()
conn.close()
