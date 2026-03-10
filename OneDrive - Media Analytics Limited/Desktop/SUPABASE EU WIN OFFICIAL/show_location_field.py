import json

with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find records with this project name
project_name = 'Realizzazione vasca di prima pioggia conforme al RR 6/2019'

print('JSON records with Location field:')
print('='*80)

count = 0
for record in data:
    pn = record.get('Column1.Project Name (PN)', '')
    if project_name in str(pn):
        count += 1
        location = record.get('Column1.Location', 'N/A')
        cost_2024 = record.get('Column1.2024 Project Cost (24)_EUR', 0)
        print(f'{count}. Location: {location}')
        print(f'   Project Name: {pn}')
        print(f'   2024 Cost: {cost_2024} EUR')
        print()

print(f'Total: {count} records')
