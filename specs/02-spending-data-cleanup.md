# Spec 02: Spending Data Cleanup

## Problem Description

After the initial deduplication of `spending_plan` records (Spec 01), some records were incorrectly deleted because the deduplication logic only considered `project_name` as the unique key, without accounting for `utility_name`.

### Issue Details

1. **Wrong deduplication key**: The original deduplication used `(project_name, year, cost_type)` as the unique key
2. **Correct deduplication key**: Should be `(utility_name, project_name, year, cost_type)`
3. **Result**: Different utilities with the same project name had their records incorrectly merged/deleted

### Example: Munich (Muenchener Stadtentwaesserung)

| Metric | Expected | After Wrong Dedup |
|--------|----------|-------------------|
| prior_years | 74 records | 58 records |
| future_year | 76 records | 44 records |

## Solution

### Step 1: Identify Missing Records

Compare CSV source data and JSON source data against database to find missing records.

```python
# From CSV (prior_years, annual costs)
missing_from_csv = []
with open('data/spending_plan_import.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = (row['utility_name'], row['project_name'], row['year'], row['cost_type'])
        if key not in existing_db_keys:
            missing_from_csv.append(row)

# From JSON (future_year costs)
missing_future = []
for r in json_data:
    utility_name = r.get('Column1.utilityName') or r.get('Column1.Utility Name (UN)')
    project_name = r.get('Column1.Project Name (PN)')
    key = (utility_name, project_name, 'future_year', 'future')
    if key not in existing_db_keys:
        missing_future.append(...)
```

### Step 2: Insert Missing Records

```python
# Insert missing records
execute_values(cur, """
    INSERT INTO spending_plan (utility_name, project_name, year, cost_type, cost, currency)
    VALUES %s
""", values)
```

### Step 3: Link Foreign Keys

```python
# Link utility_id
UPDATE spending_plan sp
SET utility_id = u.utility_id
FROM utilities u
WHERE sp.utility_name = u.utility_name_original
AND sp.utility_id IS NULL;

# Link project_id
UPDATE spending_plan sp
SET project_id = p.project_id
FROM projects p
WHERE sp.project_name = p.project_name
AND sp.project_id IS NULL;
```

### Step 4: Final Deduplication (Correct Key)

Remove any duplicates using the correct unique key:

```sql
DELETE FROM spending_plan
WHERE spending_id NOT IN (
    SELECT MAX(spending_id)
    FROM spending_plan
    GROUP BY utility_name, project_name, year, cost_type
)
```

## Results

### Records Fixed

| Action | Count |
|--------|-------|
| Missing records from CSV | 765 |
| Missing future_year from JSON | 133 |
| Total inserted | 898 |
| Duplicates removed (final cleanup) | 271 |

### Final State

| Metric | Value |
|--------|-------|
| Total spending_plan records | 115,654 |
| Unique projects | 15,254 |
| Duplicate records | 0 ✅ |

### Munich Verification

| Year | Records |
|------|---------|
| 2020 | 74 |
| 2021 | 74 |
| 2022 | 74 |
| 2023 | 74 |
| 2024 | 74 |
| prior_years | 74 |
| future_year | 74 |

**Note**: JSON has 76 records but only 74 unique project names due to duplicates in source data:
- "Pauschale, Strukturverbesserungen und Erneuerungen" (2 times)
- "Planungspauschale" (2 times)

## Scripts Created

1. `fix_missing_spending.py` - Identifies and inserts missing records
2. `fix_link_spending.py` - Links utility_id and project_id
3. `final_dedup.py` - Final deduplication with correct key

## Lessons Learned

1. **Always use complete unique key**: When deduplicating, ensure all relevant columns are included
2. **Verify source data**: Original data may contain legitimate duplicates that should be preserved
3. **Test with specific examples**: Use known cases (like Munich) to verify deduplication logic

## Date

2026-03-11
