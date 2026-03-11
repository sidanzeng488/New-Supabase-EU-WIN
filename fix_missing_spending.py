"""
修复脚本：补充被错误删除的 spending_plan 记录
只插入缺失的记录，不删除现有数据
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import csv
import json
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

print("=" * 60)
print("步骤 1: 获取数据库中现有的记录")
print("=" * 60)

# 获取现有记录的唯一键 (utility_name, project_name, year, cost_type)
cur.execute("""
    SELECT utility_name, project_name, year, cost_type 
    FROM spending_plan
""")
existing = set()
for row in cur.fetchall():
    key = (row[0], row[1], row[2], row[3])
    existing.add(key)

print(f"数据库中现有记录: {len(existing)} 条")

print("\n" + "=" * 60)
print("步骤 2: 读取 CSV 文件，找出缺失的记录")
print("=" * 60)

missing_from_csv = []
with open('data/spending_plan_import.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row['utility_name'], row['project_name'], row['year'], row['cost_type'])
        if key not in existing:
            missing_from_csv.append({
                'utility_name': row['utility_name'],
                'project_name': row['project_name'],
                'year': row['year'],
                'cost_type': row['cost_type'],
                'cost': float(row['cost']) if row['cost'] else 0.0,
                'currency': row['currency']
            })

print(f"CSV 中缺失的记录: {len(missing_from_csv)} 条")

print("\n" + "=" * 60)
print("步骤 3: 读取 JSON 文件，找出缺失的 future_year 记录")
print("=" * 60)

with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

missing_future = []
for r in data:
    utility_name = r.get('Column1.utilityName') or r.get('Column1.Utility Name (UN)') or ''
    project_name = r.get('Column1.Project Name (PN)') or ''
    future_cost = r.get('Column1.Future Year Costs (FC)_EUR')
    
    if not utility_name or not project_name:
        continue
    
    key = (utility_name, project_name, 'future_year', 'future')
    if key not in existing:
        if future_cost is not None:
            missing_future.append({
                'utility_name': utility_name,
                'project_name': project_name,
                'year': 'future_year',
                'cost_type': 'future',
                'cost': float(future_cost) if future_cost else 0.0,
                'currency': 'EUR'
            })

print(f"JSON 中缺失的 future_year 记录: {len(missing_future)} 条")

# 合并所有缺失记录
all_missing = missing_from_csv + missing_future
print(f"\n总共需要补充: {len(all_missing)} 条记录")

if len(all_missing) == 0:
    print("\n没有缺失的记录，无需修复！")
    cur.close()
    conn.close()
    exit()

print("\n" + "=" * 60)
print("步骤 4: 插入缺失的记录")
print("=" * 60)

# 批量插入
batch_size = 1000
inserted = 0
errors = 0

for i in range(0, len(all_missing), batch_size):
    batch = all_missing[i:i+batch_size]
    values = [(
        r['utility_name'],
        r['project_name'],
        r['year'],
        r['cost_type'],
        r['cost'],
        r['currency']
    ) for r in batch]
    
    try:
        execute_values(cur, """
            INSERT INTO spending_plan (utility_name, project_name, year, cost_type, cost, currency)
            VALUES %s
        """, values)
        conn.commit()
        inserted += len(batch)
        print(f"  已插入: {inserted}/{len(all_missing)}")
    except Exception as e:
        conn.rollback()
        errors += len(batch)
        print(f"  错误: {e}")

print(f"\n插入完成: {inserted} 条成功, {errors} 条失败")

cur.close()
conn.close()

print("\n✅ 修复完成！")
