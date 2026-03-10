import psycopg2

# .env connection: mrkjnptfrxdemcojpdnr
conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)

cur = conn.cursor()

print('=' * 50)
print('Connected to: mrkjnptfrxdemcojpdnr (from .env)')
print('=' * 50)

# test connection
cur.execute('SELECT version();')
print('PostgreSQL version:', cur.fetchone()[0])
print()

# list all public tables
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name;
""")

tables = cur.fetchall()
print(f'Public tables ({len(tables)}):')
print('-' * 40)
if tables:
    for table in tables:
        print(f'  - {table[0]}')
else:
    print('  (empty - no tables)')

cur.close()
conn.close()
