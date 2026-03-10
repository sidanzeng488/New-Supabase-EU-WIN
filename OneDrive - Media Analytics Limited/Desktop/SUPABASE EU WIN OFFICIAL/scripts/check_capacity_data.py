import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('data/Europe utility spending plan tracker.xlsx', sheet_name=0)

# P列和Q列
p_col = df.iloc[:, 15]  # Wastewater: Population served
q_col = df.iloc[:, 16]  # YEAR

# 统计
valid_rows = df[p_col.notna() & q_col.notna()]
print(f'Total rows: {len(df)}')
print(f'Rows with both P and Q values: {len(valid_rows)}')

# 显示前20行有效数据，包括 utility 名称列
print('\nFirst 20 valid rows:')
print(f'{"Idx":<4} | {"Utility Local Name":<45} | {"Capacity":<15} | {"Year"}')
print('-' * 85)

for idx, row in valid_rows.head(20).iterrows():
    local_name = str(row.iloc[3])[:42] if pd.notna(row.iloc[3]) else 'N/A'
    capacity = row.iloc[15]
    year = row.iloc[16]
    print(f'{idx:<4} | {local_name:<45} | {capacity:<15} | {year}')

# 检查数据质量
print('\n=== Data Quality Check ===')
print(f'Unique capacity values with ? : {p_col.astype(str).str.contains("\\?", na=False).sum()}')
print(f'Unique capacity values with > : {p_col.astype(str).str.contains(">", na=False).sum()}')
