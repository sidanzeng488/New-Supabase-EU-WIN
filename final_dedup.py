"""
最终去重：按 (utility_name, project_name, year, cost_type) 去重
保留 spending_id 最大的记录
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import psycopg2

conn = psycopg2.connect(
    host='db.mrkjnptfrxdemcojpdnr.supabase.co',
    port=5432,
    database='postgres',
    user='postgres',
    password='t56rEaP7AC9UQ5jb'
)
cur = conn.cursor()

print("=" * 60)
print("查找重复记录")
print("=" * 60)

# 查找重复的 (utility_name, project_name, year, cost_type) 组合
cur.execute("""
    SELECT utility_name, project_name, year, cost_type, COUNT(*) as cnt
    FROM spending_plan
    GROUP BY utility_name, project_name, year, cost_type
    HAVING COUNT(*) > 1
""")
duplicates = cur.fetchall()
print(f"发现 {len(duplicates)} 组重复")

if len(duplicates) == 0:
    print("没有重复，无需去重！")
    cur.close()
    conn.close()
    exit()

print("\n" + "=" * 60)
print("删除重复记录（保留 spending_id 最大的）")
print("=" * 60)

# 删除重复记录，保留每组中 spending_id 最大的
cur.execute("""
    DELETE FROM spending_plan
    WHERE spending_id NOT IN (
        SELECT MAX(spending_id)
        FROM spending_plan
        GROUP BY utility_name, project_name, year, cost_type
    )
""")
deleted = cur.rowcount
conn.commit()
print(f"删除了 {deleted} 条重复记录")

print("\n" + "=" * 60)
print("验证结果")
print("=" * 60)

cur.execute("SELECT COUNT(*) FROM spending_plan")
total = cur.fetchone()[0]
print(f"spending_plan 总记录数: {total}")

cur.execute("""
    SELECT utility_name, project_name, year, cost_type, COUNT(*) as cnt
    FROM spending_plan
    GROUP BY utility_name, project_name, year, cost_type
    HAVING COUNT(*) > 1
""")
remaining_dups = cur.fetchall()
if remaining_dups:
    print(f"⚠️ 仍有 {len(remaining_dups)} 组重复")
else:
    print("✅ 没有重复！")

cur.close()
conn.close()

print("\n✅ 去重完成！")
