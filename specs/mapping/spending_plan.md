# Spending Plan Table Mapping

> Source: `data/merge_final.json`  
> Extract Script: `scripts/extract_spending_plan.py`

---

## Field Mapping

| Database Field | JSON Source Field | Description |
|----------------|-------------------|-------------|
| `utility_name` | `Column1.utilityName` | Utility name |
| `project_name` | `Column1.Project Name (PN)` | Project name |
| `year` | Extracted from field name | Year identifier or label |
| `cost_type` | Inferred from field name | Type of cost |
| `cost` | Value from cost field | Amount in EUR |
| `currency` | Fixed value `EUR` | Currency unit |

---

## Cost Field Extraction Rules

The spending plan data is extracted from multiple JSON fields that end with `_EUR`. Each field type has a specific pattern:

### Annual Costs
| JSON Field Pattern | year | cost_type |
|-------------------|------|-----------|
| `Column1.2024 Project Cost (24)_EUR` | `2024` | `annual` |
| `Column1.2025 Project Cost (25)_EUR` | `2025` | `annual` |
| `Column1.2026 Project Cost (26)_EUR` | `2026` | `annual` |
| `Column1.2027 Project Cost (27)_EUR` | `2027` | `annual` |
| ... | ... | ... |

### Prior Year Costs
| JSON Field Pattern | year | cost_type |
|-------------------|------|-----------|
| `Column1.Prior Year Project Spending/Costs (PY)_EUR` | `prior_years` | `prior` |

### Future Year Costs
| JSON Field Pattern | year | cost_type |
|-------------------|------|-----------|
| `Column1.Future Year Costs (FC)_EUR` | `future_year` | `future` |

### Total Costs (with prior years) - DEPRECATED
| JSON Field Pattern | year | cost_type |
|-------------------|------|-----------|
| `Column1.*cost*YYYY-YYYY + prior years_EUR` | `total_{start}_{end}_with_prior` | `total_with_prior` |

> ⚠️ **DEPRECATED**: `total_with_prior` records have been removed from the database.
> Only SIAAP had this field, and it was redundant (can be calculated from `total` + `prior`).
> See: `specs/03-siaap-with-prior-cleanup.md`

### Total Costs (without prior years)
| JSON Field Pattern | year | cost_type |
|-------------------|------|-----------|
| `Column1.*cost*YYYY-YYYY_EUR` | `total_{start}_{end}` | `total` |

---

## Regex Patterns Used

```python
patterns = {
    # Annual costs: Column1.2025 Project Cost (25)_EUR
    'annual': re.compile(r'Column1\.(\d{4}) Project Cost \(\d+\)_EUR'),
    
    # Prior year costs: Column1.Prior Year Project Spending/Costs (PY)_EUR
    'prior': re.compile(r'Column1\.Prior Year Project Spending/Costs \(PY\)_EUR'),
    
    # Total with prior: Column1.SIAAP cost 2024-2034 + prior years_EUR
    'total_with_prior': re.compile(r'Column1\.[^"]*cost[^"]*\+ prior years_EUR', re.IGNORECASE),
    
    # Total without prior: Column1.SIAAP cost 2024-2034_EUR
    'total': re.compile(r'Column1\.[^"]*cost[^"]*\d{4}-\d{4}_EUR$', re.IGNORECASE),
}
```

---

## Linking to Other Tables

### Linking utility_id
The `utility_id` is linked by matching `spending_plan.utility_name` against utilities table in this priority order:

```sql
-- Priority 1: Match utility_name_original
UPDATE spending_plan sp
SET utility_id = u.utility_id
FROM utilities u
WHERE sp.utility_name = u.utility_name_original;

-- Priority 2: Match utility_name_en
UPDATE spending_plan sp
SET utility_id = u.utility_id
FROM utilities u
WHERE sp.utility_name = u.utility_name_en
AND sp.utility_id IS NULL;

-- Priority 3: Match utility_name_local
UPDATE spending_plan sp
SET utility_id = u.utility_id
FROM utilities u
WHERE sp.utility_name = u.utility_name_local
AND sp.utility_id IS NULL;
```

### Linking project_id
The `project_id` is linked by matching `spending_plan.project_name` to `projects.project_name`.

---

## Unique Key

The unique key for deduplication is:

```
(utility_name, project_name, year, cost_type)
```

When duplicates exist, keep the record with the highest `spending_id`.

---

## Example JSON Record

```json
{
  "Column1.utilityName": "Muenchener Stadtentwaesserung",
  "Column1.Project Name (PN)": "Sewer Network Renovation",
  "Column1.CIPStartYear": 2024,
  "Column1.CIPEndYear": 2030,
  "Column1.Prior Year Project Spending/Costs (PY)_EUR": 500000.0,
  "Column1.2024 Project Cost (24)_EUR": 1000000.0,
  "Column1.2025 Project Cost (25)_EUR": 1500000.0,
  "Column1.2026 Project Cost (26)_EUR": 2000000.0,
  "Column1.Future Year Costs (FC)_EUR": 3000000.0
}
```

This would generate 5 spending_plan records:

| utility_name | project_name | year | cost_type | cost |
|--------------|--------------|------|-----------|------|
| Muenchener Stadtentwaesserung | Sewer Network Renovation | prior_years | prior | 500000 |
| Muenchener Stadtentwaesserung | Sewer Network Renovation | 2024 | annual | 1000000 |
| Muenchener Stadtentwaesserung | Sewer Network Renovation | 2025 | annual | 1500000 |
| Muenchener Stadtentwaesserung | Sewer Network Renovation | 2026 | annual | 2000000 |
| Muenchener Stadtentwaesserung | Sewer Network Renovation | future_year | future | 3000000 |

---

## Important Notes

1. **Different Utility Field**: `spending_plan` uses `Column1.utilityName` which is different from `projects` table that uses `Column1.CIP Excel Document Utility Name - English Language`.

2. **NULL Costs**: Fields with `NULL` or missing values are skipped during extraction.

3. **Currency**: All costs are converted to EUR before import.

4. **SIAAP Special Case**: SIAAP (Greater Paris Sanitation Authority) has a unique data structure:
   - Annual cost fields contain "X" markers instead of amounts (converted to 0 in `_EUR` fields)
   - Only total summary fields have actual values
   - `total_with_prior` records have been removed as redundant (see `specs/03-siaap-with-prior-cleanup.md`)
