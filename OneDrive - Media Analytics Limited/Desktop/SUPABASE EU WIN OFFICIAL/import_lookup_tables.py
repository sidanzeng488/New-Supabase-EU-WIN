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

print('=' * 60)
print('Importing Lookup Tables from Reference Database')
print('=' * 60)

# === SECTOR ===
print('\n[1/7] Importing sector...')
cur.execute("DELETE FROM sector; ALTER SEQUENCE sector_sector_id_seq RESTART WITH 1;")
sectors = [
    (1, 'Water'),
    (2, 'Wastewater'),
    (3, 'Stormwater'),
    (4, 'Water & Wastewater'),
    (5, 'Other')
]
for s in sectors:
    cur.execute("INSERT INTO sector (sector_id, sector_name) VALUES (%s, %s);", s)
print(f'  - Inserted {len(sectors)} sectors')

# === APPLICATION ===
print('\n[2/7] Importing application...')
cur.execute("DELETE FROM application; ALTER SEQUENCE application_application_id_seq RESTART WITH 1;")
applications = [
    (1, 'Water Resources'),
    (2, 'Drinking Water Treatment'),
    (3, 'Water Networks'),
    (4, 'Desalination'),
    (5, 'Wastewater Networks'),
    (6, 'Wastewater Treatment'),
    (7, 'Sludge Management'),
    (8, 'Stormwater'),
    (9, 'Other')
]
for a in applications:
    cur.execute("INSERT INTO application (application_id, application_name) VALUES (%s, %s);", a)
print(f'  - Inserted {len(applications)} applications')

# === SUB_APPLICATION ===
print('\n[3/7] Importing sub_application...')
cur.execute("DELETE FROM sub_application; ALTER SEQUENCE sub_application_sub_application_id_seq RESTART WITH 1;")
sub_applications = [
    (1, 'Water Transmission'),
    (2, 'Distribution Networks'),
    (3, 'Pump Stations'),
    (4, 'Primary Treatment'),
    (5, 'Secondary Treatment'),
    (6, 'Tertiary Treatment'),
    (7, 'Quaternary Treatment'),
    (8, 'Reuse'),
    (9, 'Planning & Engineering'),
    (10, 'Administrative / Support'),
    (11, 'Construction Budget / Unspecified Construction'),
    (12, 'Collection Systems'),
    (13, 'Lift Stations'),
    (14, 'Green Infrastructure'),
    (15, 'General Stormwater'),
    (16, 'Combined Sewer Overflow'),
    (17, 'Groundwater Extraction'),
    (18, 'Dams and Reservoirs'),
    (19, 'Surface Water Intakes'),
    (20, 'Other')
]
for sa in sub_applications:
    cur.execute("INSERT INTO sub_application (sub_application_id, sub_application_name) VALUES (%s, %s);", sa)
print(f'  - Inserted {len(sub_applications)} sub_applications')

# === STATUS ===
print('\n[4/7] Importing status...')
cur.execute("DELETE FROM status; ALTER SEQUENCE status_status_id_seq RESTART WITH 1;")
statuses = [
    (1, 'planned'),
    (2, 'ongoing'),
    (3, 'inactive')
]
for s in statuses:
    cur.execute("INSERT INTO status (status_id, status_name) VALUES (%s, %s);", s)
print(f'  - Inserted {len(statuses)} statuses')

# === THEME ===
print('\n[5/7] Importing theme...')
cur.execute("DELETE FROM theme; ALTER SEQUENCE theme_theme_id_seq RESTART WITH 1;")
themes = [
    (1, 'Energy Efficiency'),
    (2, 'Emerging Contaminants'),
    (3, 'PFAS'),
    (4, 'UWWTD')
]
for t in themes:
    cur.execute("INSERT INTO theme (theme_id, theme_name) VALUES (%s, %s);", t)
print(f'  - Inserted {len(themes)} themes')

# === PLANT_TYPE ===
print('\n[6/7] Importing plant_type...')
cur.execute("DELETE FROM plant_type; ALTER SEQUENCE plant_type_plant_type_id_seq RESTART WITH 1;")
plant_types = [
    (1, 'new'),
    (2, 'retrofit')
]
for pt in plant_types:
    cur.execute("INSERT INTO plant_type (plant_type_id, description) VALUES (%s, %s);", pt)
print(f'  - Inserted {len(plant_types)} plant_types')

# === TECHNOLOGY ===
print('\n[7/7] Importing technology...')
cur.execute("DELETE FROM technology; ALTER SEQUENCE technology_technology_id_seq RESTART WITH 1;")
technologies = [
    (1, 'Pipes'),
    (2, 'Pumps'),
    (3, 'Valves'),
    (4, 'Settling Clarifiers'),
    (5, 'Non-membrane Filtration'),
    (6, 'MF/UF Systems'),
    (7, 'RO/NF Systems'),
    (8, 'Flotation'),
    (9, 'Screens'),
    (10, 'Activated Carbon Systems'),
    (11, 'Ion Exchange'),
    (12, 'Chlorination'),
    (13, 'Ozonation'),
    (14, 'Advanced Oxidation Processes'),
    (15, 'Ultraviolet Light'),
    (16, 'Aeration Systems'),
    (17, 'Aerobic Biological Systems'),
    (18, 'Anaerobic Biological Systems'),
    (19, 'Anaerobic Digestion'),
    (20, 'Sludge Thickening'),
    (21, 'Sludge Dewatering Equipment'),
    (22, 'Sludge Stabilisation Equipment'),
    (23, 'Sludge Drying Equipment'),
    (24, 'Sludge incineration'),
    (25, 'Customer Meters'),
    (26, 'Lab Equipment & Services'),
    (27, 'Physical Parameter Sensors'),
    (28, 'Water Quality Sensors'),
    (29, 'Control Systems and SCADA'),
    (30, 'Data Management/Analysis'),
    (31, 'No Specific Technology')
]
for tech in technologies:
    cur.execute("INSERT INTO technology (technology_id, technology_name) VALUES (%s, %s);", tech)
print(f'  - Inserted {len(technologies)} technologies')

# === SUMMARY ===
print('\n' + '=' * 60)
print('Import Summary:')
print('=' * 60)

tables = ['sector', 'application', 'sub_application', 'status', 'theme', 'plant_type', 'technology']
for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    count = cur.fetchone()[0]
    print(f'  {table}: {count} rows')

cur.close()
conn.close()

print('\nDone!')
