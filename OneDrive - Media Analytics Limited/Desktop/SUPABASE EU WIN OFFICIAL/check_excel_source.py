import pandas as pd

project_name = 'Realizzazione vasca di prima pioggia conforme al RR 6/2019'

# Read all sheets from Excel
print('Reading Excel file...')
excel_file = 'data/Europe utility spending plan tracker.xlsx'
xl = pd.ExcelFile(excel_file)

print(f'Sheet names: {xl.sheet_names}')

for sheet_name in xl.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # Search for the project name in any column
    found = False
    for col in df.columns:
        try:
            matches = df[df[col].astype(str).str.contains('Realizzazione vasca di prima pioggia', na=False, case=False)]
            if len(matches) > 0:
                print(f'\n{"="*80}')
                print(f'Sheet: {sheet_name}')
                print(f'Found {len(matches)} matches in column "{col}"')
                print('='*80)
                
                # Show all columns for these matches
                print(f'\nColumns: {list(df.columns)}')
                print(f'\nMatched rows:')
                for idx, row in matches.iterrows():
                    print(f'\n  Row {idx}:')
                    for c in df.columns:
                        val = row[c]
                        if pd.notna(val) and str(val).strip():
                            print(f'    {c}: {val}')
                found = True
                break
        except:
            continue
    
    if not found:
        # Check first few columns
        print(f'Sheet {sheet_name}: No matches found (columns: {list(df.columns)[:5]}...)')
