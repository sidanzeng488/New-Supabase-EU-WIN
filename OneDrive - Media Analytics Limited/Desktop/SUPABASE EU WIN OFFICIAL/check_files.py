import json
from collections import defaultdict

print('Analyzing files data from JSON...')
print('=' * 60)

with open('data/merge_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Group by utility
utility_files = defaultdict(set)
utility_docs = defaultdict(set)

for record in data:
    utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
    doc_link = record.get('Column1.DocumentLink')
    page_link = record.get('Column1.PageLink')
    cip_start = record.get('Column1.CIPStartYear')
    cip_end = record.get('Column1.CIPEndYear')
    file_name = record.get('Column1.FileName')
    
    if utility_local:
        # Track unique doc_links per utility
        if doc_link:
            utility_docs[utility_local].add(doc_link)
        
        # Track unique files (by all fields)
        file_key = (doc_link, page_link, cip_start, cip_end, file_name)
        utility_files[utility_local].add(file_key)

print(f'Total unique utilities in JSON: {len(utility_files)}')
print()

# Count files per utility
print('Files per utility:')
print('-' * 60)

total_files = 0
for utility, files in sorted(utility_files.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
    doc_count = len(utility_docs[utility])
    file_count = len(files)
    total_files += file_count
    name = utility[:45] + '...' if len(utility) > 45 else utility
    print(f'  {name}: {file_count} files, {doc_count} docs')

print(f'\n... and {len(utility_files) - 20} more utilities')
print(f'\nTotal unique files (all utilities): {total_files}')

# Check if each utility should have exactly 1 file
print('\n' + '=' * 60)
print('Analysis:')
print(f'  - Unique utilities: {len(utility_files)}')
print(f'  - Utilities with 1 file: {sum(1 for f in utility_files.values() if len(f) == 1)}')
print(f'  - Utilities with multiple files: {sum(1 for f in utility_files.values() if len(f) > 1)}')
