"""
修复关联 utility_id 和 project_id
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
print("关联 utility_id")
print("=" * 60)

# 尝试用 utility_name_original 关联
cur.execute("""
    UPDATE spending_plan sp
    SET utility_id = u.utility_id
    FROM utilities u
    WHERE sp.utility_name = u.utility_name_original
    AND sp.utility_id IS NULL
""")
cnt1 = cur.rowcount
conn.commit()
print(f"通过 utility_name_original 关联: {cnt1} 条")

# 尝试用 utility_name_en 关联
cur.execute("""
    UPDATE spending_plan sp
    SET utility_id = u.utility_id
    FROM utilities u
    WHERE sp.utility_name = u.utility_name_en
    AND sp.utility_id IS NULL
""")
cnt2 = cur.rowcount
conn.commit()
print(f"通过 utility_name_en 关联: {cnt2} 条")

# 尝试用 utility_name_local 关联
cur.execute("""
    UPDATE spending_plan sp
    SET utility_id = u.utility_id
    FROM utilities u
    WHERE sp.utility_name = u.utility_name_local
    AND sp.utility_id IS NULL
""")
cnt3 = cur.rowcount
conn.commit()
print(f"通过 utility_name_local 关联: {cnt3} 条")

print(f"utility_id 总关联: {cnt1 + cnt2 + cnt3} 条")

print("\n" + "=" * 60)
print("关联 project_id")
print("=" * 60)

cur.execute("""
    UPDATE spending_plan sp
    SET project_id = p.project_id
    FROM projects p
    WHERE sp.project_name = p.project_name
    AND sp.project_id IS NULL
""")
project_updated = cur.rowcount
conn.commit()
print(f"关联 project_id: {project_updated} 条")

print("\n" + "=" * 60)
print("验证结果")
print("=" * 60)

# 检查总数
cur.execute("SELECT COUNT(*) FROM spending_plan")
total = cur.fetchone()[0]
print(f"spending_plan 总记录数: {total}")

cur.close()
conn.close()

print("\n✅ 关联完成！")
