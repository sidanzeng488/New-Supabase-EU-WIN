import psycopg2

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
conn.autocommit = True
cur = conn.cursor()

print('Creating files table...')
print('Reference: https://supabase.com/dashboard/project/ztckqcokiaktbieplxfx/editor/19181')
print('=' * 60)

# Drop existing files table if exists
cur.execute("DROP TABLE IF EXISTS files CASCADE;")

# Create files table based on reference
cur.execute("""
    CREATE TABLE files (
        file_id SERIAL PRIMARY KEY,
        utility_id INTEGER REFERENCES utilities(utility_id),
        project_id INTEGER REFERENCES projects(project_id),
        cip_start_year INTEGER,
        cip_end_year INTEGER,
        page_link TEXT,
        doc_link TEXT
    );
""")

print('files table created successfully!')
print()
print('Table structure:')
print('-' * 60)

cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'files' AND table_schema = 'public'
    ORDER BY ordinal_position;
""")

for row in cur.fetchall():
    nullable = 'NULL' if row[2] == 'YES' else 'NOT NULL'
    print(f'  - {row[0]}: {row[1]} ({nullable})')

cur.close()
conn.close()

print()
print('Done!')
