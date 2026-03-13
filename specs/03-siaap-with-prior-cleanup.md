# SIAAP Spending Plan Data Cleanup

## Date
2026-03-13

## Issue Description

SIAAP (Greater Paris Sanitation Authority) data contains redundant `total_with_prior` records in the `spending_plan` table. These records duplicate information that can be derived from existing `total` and `prior` records.

### Data Source
- JSON Field: `Column1.SIAAP cost 2024-2034 + prior years_EUR`
- Records Affected: ~71 SIAAP project records
- Only SIAAP has this field format; no other utilities are affected

## Analysis

### SIAAP Cost Field Structure
| Field | Description | Example Value |
|-------|-------------|---------------|
| `Column1.SIAAP cost 2024-2034_EUR` | CIP period total cost | 9,000,000 |
| `Column1.Prior Year Project Spending/Costs (PY)_EUR` | Prior years cost | 0 |
| `Column1.SIAAP cost 2024-2034 + prior years_EUR` | Total with prior (redundant) | 9,000,000 |

### Why It's Redundant
```
total_with_prior = total + prior_years
```

The `total_with_prior` value can always be calculated from `total` and `prior` values, making it unnecessary to store separately.

## Solution

Delete all `total_with_prior` records for SIAAP from the `spending_plan` table.

## SQL Script

```sql
DELETE FROM spending_plan
WHERE utility_name LIKE '%SIAAP%'
  AND cost_type = 'total_with_prior';
```

## Script Location
`sql/delete_siaap_with_prior.sql`

## Impact

- **Removed**: ~71 redundant `total_with_prior` records
- **Retained**: All `total`, `prior`, and `annual` type records for SIAAP
- **No data loss**: The removed data can be recalculated if needed

## Verification

After running the script, verify:
1. No `total_with_prior` records remain for SIAAP
2. Other cost_type records (total, prior, annual) are intact

```sql
SELECT cost_type, COUNT(*) 
FROM spending_plan 
WHERE utility_name LIKE '%SIAAP%' 
GROUP BY cost_type;
```

## Related Documentation
- `specs/mapping/spending_plan.md` - Spending plan field mapping documentation
