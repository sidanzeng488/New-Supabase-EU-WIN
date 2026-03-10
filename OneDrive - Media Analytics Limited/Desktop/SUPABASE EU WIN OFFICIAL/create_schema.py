import psycopg2

# .env connection: mrkjnptfrxdemcojpdnr
conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
conn.autocommit = True
cur = conn.cursor()

print('Creating schema based on ER diagram...')
print('=' * 50)

# === LOOKUP TABLES ===
print('\n[1/4] Creating lookup tables...')

cur.execute("""
-- SECTOR (行业)
CREATE TABLE IF NOT EXISTS sector (
    sector_id SERIAL PRIMARY KEY,
    sector_name VARCHAR(255) NOT NULL UNIQUE
);

-- APPLICATION (应用)
CREATE TABLE IF NOT EXISTS application (
    application_id SERIAL PRIMARY KEY,
    application_name VARCHAR(255) NOT NULL
);

-- SUB_APPLICATION (子应用)
CREATE TABLE IF NOT EXISTS sub_application (
    sub_application_id SERIAL PRIMARY KEY,
    sub_application_name VARCHAR(255) NOT NULL
);

-- STATUS (状态)
CREATE TABLE IF NOT EXISTS status (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(255) NOT NULL UNIQUE
);

-- PLANT_TYPE (工厂类型)
CREATE TABLE IF NOT EXISTS plant_type (
    plant_type_id SERIAL PRIMARY KEY,
    description VARCHAR(255) NOT NULL UNIQUE
);

-- TECHNOLOGY (技术)
CREATE TABLE IF NOT EXISTS technology (
    technology_id SERIAL PRIMARY KEY,
    technology_name VARCHAR(255) NOT NULL
);

-- THEME (主题)
CREATE TABLE IF NOT EXISTS theme (
    theme_id SERIAL PRIMARY KEY,
    theme_name VARCHAR(255) NOT NULL UNIQUE
);
""")
print('  - sector, application, sub_application, status, plant_type, technology, theme')

# === BASE TABLES ===
print('\n[2/4] Creating base tables...')

cur.execute("""
-- UTILITIES (公用事业)
CREATE TABLE IF NOT EXISTS utilities (
    utility_id SERIAL PRIMARY KEY,
    utility_name VARCHAR(255) NOT NULL
);

-- PLANTS (工厂)
CREATE TABLE IF NOT EXISTS plants (
    plant_id SERIAL PRIMARY KEY,
    plant_name VARCHAR(255)
);

-- NOTICE (通知)
CREATE TABLE IF NOT EXISTS notice (
    notice_id SERIAL PRIMARY KEY
);
""")
print('  - utilities, plants, notice')

# === MAIN TABLE ===
print('\n[3/4] Creating main table (projects)...')

cur.execute("""
-- PROJECTS (项目)
CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    project_name VARCHAR(500) NOT NULL,
    project_description TEXT,
    sector_id INTEGER REFERENCES sector(sector_id),
    application_id INTEGER REFERENCES application(application_id),
    sub_application_id INTEGER REFERENCES sub_application(sub_application_id),
    status_id INTEGER REFERENCES status(status_id),
    plant_type_id INTEGER REFERENCES plant_type(plant_type_id),
    utility_id INTEGER REFERENCES utilities(utility_id),
    utility_name VARCHAR(255)
);
""")
print('  - projects')

# === LINK TABLES ===
print('\n[4/4] Creating link tables...')

cur.execute("""
-- PROJECT_PLANT_LINK (项目-工厂关联)
CREATE TABLE IF NOT EXISTS project_plant_link (
    project_id INTEGER REFERENCES projects(project_id),
    plant_id INTEGER REFERENCES plants(plant_id),
    PRIMARY KEY (project_id, plant_id)
);

-- TECHNOLOGY_PROJECT (技术-项目关联)
CREATE TABLE IF NOT EXISTS technology_project (
    tp_id SERIAL PRIMARY KEY,
    technology_id INTEGER REFERENCES technology(technology_id),
    project_id INTEGER REFERENCES projects(project_id)
);

-- PROJECT_NOTICE_LINK (项目-通知关联)
CREATE TABLE IF NOT EXISTS project_notice_link (
    project_id INTEGER REFERENCES projects(project_id),
    notice_id INTEGER REFERENCES notice(notice_id),
    confidence_level NUMERIC(3,2),
    PRIMARY KEY (project_id, notice_id)
);

-- THEME_PROJECT_LINK (主题-项目关联)
CREATE TABLE IF NOT EXISTS theme_project_link (
    theme_project_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id),
    theme_id INTEGER REFERENCES theme(theme_id)
);
""")
print('  - project_plant_link, technology_project, project_notice_link, theme_project_link')

# === VERIFY ===
print('\n' + '=' * 50)
print('Verifying created tables...')

cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
    ORDER BY table_name;
""")

tables = cur.fetchall()
print(f'\nPublic tables ({len(tables)}):')
for table in tables:
    print(f'  ✓ {table[0]}')

cur.close()
conn.close()

print('\n' + '=' * 50)
print('Schema creation completed!')
