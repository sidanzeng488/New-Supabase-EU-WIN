import json

project_name = 'Realizzazione vasca di prima pioggia conforme al RR 6/2019'

with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find all matches
matches = []
for i, record in enumerate(data):
    for key, val in record.items():
        if isinstance(val, str) and 'Realizzazione vasca di prima pioggia' in val:
            matches.append(record)
            break

print('='*80)
print('Analysis: "Realizzazione vasca di prima pioggia conforme al RR 6/2019"')
print('='*80)
print(f'\nTotal records in JSON with this project name: {len(matches)}')

# Extract locations
locations = []
for m in matches:
    loc = m.get('Column1.Location', 'N/A')
    locations.append(loc)

print(f'\nThese are {len(set(locations))} DIFFERENT LOCATIONS (cities/towns):')
print('-'*60)

# Group by location
from collections import Counter
loc_count = Counter(locations)
for loc, cnt in sorted(loc_count.items()):
    print(f'  - {loc}: {cnt} record(s)')

print('\n' + '='*80)
print('CONCLUSION:')
print('='*80)
print('''
These are NOT duplicate records!

"Realizzazione vasca di prima pioggia conforme al RR 6/2019" means:
"Construction of first flush tank compliant with RR 6/2019"

RR 6/2019 is an Italian regional regulation (Regolamento Regionale 6/2019)
that requires building stormwater collection tanks.

Cap Holding Spa is building these tanks in MULTIPLE LOCATIONS
across the Milan metropolitan area. Each location is a SEPARATE PROJECT
with its own budget and timeline.

The projects table currently lacks a "location" field to distinguish
these different projects properly.
''')

# Show sample with different costs
print('\nSample showing different locations have different budgets:')
print('-'*80)
for m in matches[:5]:
    loc = m.get('Column1.Location', 'N/A')
    cost_2024 = m.get('Column1.2024 Project Cost (24)_EUR', 0)
    cost_2025 = m.get('Column1.2025 Project Cost (25)_EUR', 0)
    print(f'  {loc}: 2024={cost_2024} EUR, 2025={cost_2025} EUR')
