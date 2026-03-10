import json

project_name = 'Realizzazione vasca di prima pioggia conforme al RR 6/2019'

print('Reading JSON file...')
with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total records in JSON: {len(data)}')

# Search for the project
matches = []
for i, record in enumerate(data):
    # Check all string values for the project name
    for key, val in record.items():
        if isinstance(val, str) and 'Realizzazione vasca di prima pioggia' in val:
            matches.append((i, record))
            break

print(f'\nFound {len(matches)} matching records')

# Show details
for idx, (i, record) in enumerate(matches):
    print(f'\n{"="*80}')
    print(f'Match {idx+1} (JSON index {i}):')
    print('='*80)
    for k, v in record.items():
        if v is not None and v != '':
            print(f'  {k}: {v}')
