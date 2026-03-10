import psycopg2

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'utilities' 
    ORDER BY ordinal_position;
""")

print('Current utilities table structure:')
cols = cur.fetchall()
if cols:
    for r in cols:
        print(f'  - {r[0]}: {r[1]}')
else:
    print('  (no columns found)')

cur.close()
conn.close()
