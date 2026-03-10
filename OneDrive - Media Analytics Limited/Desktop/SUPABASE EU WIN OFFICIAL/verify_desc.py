import psycopg2

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

# Check column exists
cur.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'projects' AND column_name = 'description_english';
""")
if cur.fetchone():
    print('Column description_english exists')
else:
    print('Column description_english NOT found!')

# Count non-null
cur.execute("SELECT COUNT(*) FROM projects WHERE description_english IS NOT NULL AND description_english != '';")
count = cur.fetchone()[0]
print(f'Projects with English description: {count}')

# Sample
cur.execute("""
    SELECT project_id, project_name, description_english 
    FROM projects 
    WHERE description_english IS NOT NULL AND description_english != ''
    LIMIT 5;
""")
print('\nSamples:')
for row in cur.fetchall():
    print(f'  [{row[0]}] {row[1][:40]}...')
    print(f'       EN: {row[2][:50]}...' if row[2] else '       EN: None')

cur.close()
conn.close()
