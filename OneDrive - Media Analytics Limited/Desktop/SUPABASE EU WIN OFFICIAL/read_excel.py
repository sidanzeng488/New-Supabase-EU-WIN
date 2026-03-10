import pandas as pd

# Read Excel file
df = pd.read_excel('data/Utility_to_treatment_plant_matching_batch_1.xlsx')

print('Excel columns:')
for col in df.columns:
    print(f'  - {col}')

print(f'\nTotal rows: {len(df)}')
print('\nFirst 10 rows:')
print(df.head(10).to_string())

print('\n\nColumn data types:')
print(df.dtypes)
