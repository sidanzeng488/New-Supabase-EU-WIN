import pandas as pd
import requests
import re
import sys
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')

SUPABASE_URL = 'https://mrkjnptfrxdemcojpdnr.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ya2pucHRmcnhkZW1jb2pwZG5yIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI4MDU2MTEsImV4cCI6MjA4ODM4MTYxMX0.FsIVmoRGlZbL5LcIclHYcusJM0KMnL4OsNyk3-ORNd8'
HEADERS = {
    'apikey': SUPABASE_KEY, 
    'Authorization': f'Bearer {SUPABASE_KEY}', 
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# 1. 读取 Excel
print('=== Step 1: Reading Excel ===')
df = pd.read_excel('data/Europe utility spending plan tracker.xlsx', sheet_name=0)

# 提取相关列
utility_local_name = df.iloc[:, 3]   # Column D: Local name
utility_en_name = df.iloc[:, 4]      # Column E: EN name  
capacity_col = df.iloc[:, 15]        # Column P: Wastewater capacity
year_col = df.iloc[:, 16]            # Column Q: Year

# 2. 获取 utilities 表数据
print('\n=== Step 2: Fetching utilities from database ===')
utilities = []
offset = 0
while True:
    r = requests.get(f'{SUPABASE_URL}/rest/v1/utilities?select=utility_id,utility_name_local,Utility_Name_EN&offset={offset}&limit=1000', headers=HEADERS)
    batch = r.json()
    if not batch:
        break
    utilities.extend(batch)
    offset += 1000

print(f'Fetched {len(utilities)} utilities')

# 构建名称到 utility_id 的映射
utility_map = {}
for u in utilities:
    if u.get('utility_name_local'):
        utility_map[u['utility_name_local'].lower().strip()] = u['utility_id']
    if u.get('Utility_Name_EN'):
        utility_map[u['Utility_Name_EN'].lower().strip()] = u['utility_id']

print(f'Built mapping with {len(utility_map)} name entries')

# 3. 处理数据
print('\n=== Step 3: Processing capacity data ===')

def clean_capacity(val):
    """清理容量值，移除 ?, >, 等特殊字符"""
    if pd.isna(val):
        return None
    val_str = str(val).strip()
    # 移除 ?, >, <, 等
    val_str = re.sub(r'[?><!,\s]', '', val_str)
    try:
        return int(float(val_str))
    except:
        return None

records_to_upload = []
matched_utilities = set()

for idx, row in df.iterrows():
    capacity = clean_capacity(row.iloc[15])
    year = row.iloc[16]
    
    if capacity is None or pd.isna(year):
        continue
    
    year_int = int(year)
    
    # 尝试匹配 utility
    local_name = str(row.iloc[3]).lower().strip() if pd.notna(row.iloc[3]) else ''
    en_name = str(row.iloc[4]).lower().strip() if pd.notna(row.iloc[4]) else ''
    
    utility_id = utility_map.get(local_name) or utility_map.get(en_name)
    
    records_to_upload.append({
        'capacity': capacity,
        'year': year_int,
        'creation_date': str(date.today()),
        '_utility_local_name': row.iloc[3] if pd.notna(row.iloc[3]) else None,
        '_utility_id': utility_id
    })
    
    if utility_id:
        matched_utilities.add(utility_id)

print(f'Prepared {len(records_to_upload)} capacity records')
print(f'Matched {len(matched_utilities)} unique utilities')

# 4. 上传到 utilities_capacity 表
print('\n=== Step 4: Uploading to utilities_capacity ===')

# 只上传 capacity, year, creation_date（移除临时字段）
upload_data = [{k: v for k, v in r.items() if not k.startswith('_')} for r in records_to_upload]

batch_size = 500
uploaded = 0
capacity_ids = []

for i in range(0, len(upload_data), batch_size):
    batch = upload_data[i:i+batch_size]
    r = requests.post(
        f'{SUPABASE_URL}/rest/v1/utilities_capacity',
        headers=HEADERS,
        json=batch
    )
    if r.status_code in [200, 201]:
        result = r.json()
        capacity_ids.extend([rec['utility_capacity_id'] for rec in result])
        uploaded += len(batch)
        print(f'  Uploaded {uploaded}/{len(upload_data)} records...')
    else:
        print(f'  Error: {r.status_code} - {r.text}')
        break

print(f'\nTotal uploaded: {uploaded} records')

# 5. 更新 utilities 表的 utility_capacity_id
print('\n=== Step 5: Linking utilities to capacity records ===')

# 根据返回的 capacity_ids 和原始记录的 _utility_id 进行关联
linked = 0
for i, rec in enumerate(records_to_upload):
    if i < len(capacity_ids) and rec['_utility_id']:
        utility_id = rec['_utility_id']
        capacity_id = capacity_ids[i]
        
        r = requests.patch(
            f'{SUPABASE_URL}/rest/v1/utilities?utility_id=eq.{utility_id}',
            headers=HEADERS,
            json={'utility_capacity_id': capacity_id}
        )
        if r.status_code in [200, 204]:
            linked += 1
        
        if linked % 50 == 0:
            print(f'  Linked {linked} utilities...')

print(f'\nTotal linked: {linked} utilities')
print('\n=== Done! ===')
