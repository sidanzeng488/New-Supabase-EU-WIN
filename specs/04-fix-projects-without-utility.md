# Fix Projects Without Utility Association

## Date
2026-03-13

## Issue Description

44 projects in the `projects` table had no `utility_id` association. Investigation revealed two categories of issues:

1. **Invalid records**: 19 projects with `project_name = '0'` (data errors)
2. **Missing utility mapping**: 25 projects from Irish Water and Katowickie Wodociągi

### Root Cause

The `import_projects.py` script extracts utility information from:
- `Column1.CIP Excel Document Utility Name - Local Language`
- `Column1.CIP Excel Document Utility Name - English Language`

However, some data sources only populate `Column1.utilityName` field, leaving the CIP fields as `null`.

| Field | Irish Water | Katowickie | Status |
|-------|-------------|------------|--------|
| `Column1.utilityName` | `Uisce Eireann (Irish Water)` | `Katowickie Wodociągi S.A.` | ✅ Has data |
| `Column1.CIP...Local Language` | `null` | `null` | ❌ Empty |
| `Column1.CIP...English Language` | `null` | `null` | ❌ Empty |

## Analysis

### Affected Records

| Category | Project IDs | Count | Action |
|----------|-------------|-------|--------|
| Invalid (project_name='0') | 12731-12742, 15973-15979 | 19 | Delete |
| Irish Water | 7037-7053 | 17 | Update utility |
| Katowickie Wodociągi | 9189-9196 | 8 | Update utility |
| **Total** | - | **44** | - |

### Utility Mapping

| Utility | utility_id | utility_name_local | utility_name_en |
|---------|------------|-------------------|-----------------|
| Irish Water | 48 | Uisce Éireann | Irish Water |
| Katowickie Wodociągi | 63 | Katowickie Wodociągi Spółka Akcyjna | Katowice Waterworks |

## Solution

### Step 1: Delete Invalid Records

```sql
-- Delete from spending_plan first (foreign key constraint)
DELETE FROM spending_plan 
WHERE project_id IN (
    SELECT project_id FROM projects WHERE project_name = '0'
);

-- Then delete from projects
DELETE FROM projects WHERE project_name = '0';
```

**Result**: 19 records deleted

### Step 2: Update Irish Water Projects

```sql
UPDATE projects
SET 
    utility_id = 48,
    utility_name = 'Irish Water'
WHERE project_id BETWEEN 7037 AND 7053
AND utility_id IS NULL;
```

**Result**: 17 records updated

### Step 3: Update Katowickie Wodociągi Projects

```sql
UPDATE projects
SET 
    utility_id = 63,
    utility_name = 'Katowickie Wodociągi S.A.'
WHERE project_id BETWEEN 9189 AND 9196
AND utility_id IS NULL;
```

**Result**: 8 records updated

### Step 4: Update JSON Source Data

Updated `data/merge_final.json` to fill in the missing CIP utility fields:

```python
# For Irish Water records
record['Column1.CIP Excel Document Utility Name - Local Language'] = 'Uisce Éireann'
record['Column1.CIP Excel Document Utility Name - English Language'] = 'Irish Water'

# For Katowickie Wodociągi records
record['Column1.CIP Excel Document Utility Name - Local Language'] = 'Katowickie Wodociągi Spółka Akcyjna'
record['Column1.CIP Excel Document Utility Name - English Language'] = 'Katowice Waterworks'
```

**Result**: 25 JSON records updated

## Verification

```sql
SELECT 
    COUNT(*) as total_projects,
    COUNT(utility_id) as with_utility,
    COUNT(*) - COUNT(utility_id) as without_utility
FROM projects;
```

**Final Result**:
| Metric | Value |
|--------|-------|
| Total projects | 15,993 |
| With utility | 15,993 |
| Without utility | **0** ✅ |

## Impact

- **Deleted**: 19 invalid project records + related spending_plan records
- **Updated**: 25 projects now have correct utility associations
- **JSON synced**: Source data updated to prevent future import issues

## Recommendations

1. **Update `import_projects.py`**: Add fallback logic to use `Column1.utilityName` when CIP fields are empty:

```python
utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
utility_name = record.get('Column1.CIP Excel Document Utility Name - English Language')

# Fallback to utilityName if CIP fields are empty
if not utility_local and not utility_name:
    utility_name = record.get('Column1.utilityName', '')
```

2. **Data validation**: Add checks during import to flag records with missing utility information.
