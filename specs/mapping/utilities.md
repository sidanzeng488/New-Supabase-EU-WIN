# Utilities Table Mapping

> Source: `data/merge_final.json`  
> Import Script: `import_utilities.py`

---

## Field Mapping

| Database Field | JSON Source Field | Description |
|----------------|-------------------|-------------|
| `utility_name_local` | `Column1.CIP Excel Document Utility Name - Local Language` | Utility name in local language |
| `Utility_Name_EN` | `Column1.CIP Excel Document Utility Name - English Language` | Utility name in English |
| `utility_name_original` | `Column1.utilityName` | Original utility name (from spending data) |
| `country` | `Column1.HQ Country` | Country of headquarters |
| `city` | `Column1.City/Subregion` | City or subregion |

---

## Deduplication Logic

Utilities are deduplicated by `utility_name_local`. If a utility with the same local name already exists, it is not inserted again.

```python
utilities = {}
for record in data:
    utility_local = record.get('Column1.CIP Excel Document Utility Name - Local Language')
    if utility_local and utility_local not in utilities:
        utilities[utility_local] = {
            'utility_name_local': utility_local,
            'utility_name_en': record.get('Column1.CIP Excel Document Utility Name - English Language'),
            'country': record.get('Column1.HQ Country'),
            'city': record.get('Column1.City/Subregion')
        }
```

---

## Name Fields Explanation

The utilities table has multiple name fields that serve different purposes:

| Field | Purpose | Used By |
|-------|---------|---------|
| `utility_name_local` | Original name in local language | Primary key for matching projects |
| `Utility_Name_EN` | English translation | Display purposes |
| `utility_name_original` | Name from `Column1.utilityName` | Matching spending_plan records |

### Why Multiple Name Fields?

The JSON data contains utility names in different formats:

1. **CIP Document Names** (for projects):
   - `Column1.CIP Excel Document Utility Name - Local Language`
   - `Column1.CIP Excel Document Utility Name - English Language`

2. **Spending Data Names** (for spending_plan):
   - `Column1.utilityName`

These may not always match exactly, so we store all variants for flexible linking.

---

## Linking Strategy

### Projects → Utilities
```python
# Match by local language name
utility_id = utility_map.get(
    record.get('Column1.CIP Excel Document Utility Name - Local Language')
)
```

### Spending Plan → Utilities
```sql
-- Try matching in priority order:
-- 1. utility_name_original
-- 2. utility_name_en  
-- 3. utility_name_local
```

---

## Example JSON Record

```json
{
  "Column1.CIP Excel Document Utility Name - Local Language": "Berliner Wasserbetriebe",
  "Column1.CIP Excel Document Utility Name - English Language": "Berlin Water Works",
  "Column1.utilityName": "Berlin Water",
  "Column1.HQ Country": "Germany",
  "Column1.City/Subregion": "Berlin"
}
```

This would create a utility record:

| Field | Value |
|-------|-------|
| `utility_name_local` | Berliner Wasserbetriebe |
| `Utility_Name_EN` | Berlin Water Works |
| `utility_name_original` | Berlin Water |
| `country` | Germany |
| `city` | Berlin |

---

## Additional Fields (from UWWTD data)

The utilities table may also contain fields populated from EU Urban Wastewater Treatment Directive (UWWTD) data:

| Database Field | Source | Description |
|----------------|--------|-------------|
| `wastewater_population_served` | UWWTD data | Population served by wastewater services |
| `record_year` | UWWTD data | Year of the record |

---

## Notes

1. **Case Sensitivity**: Utility name matching is case-sensitive in most operations. Some scripts apply `.lower().strip()` for more flexible matching.

2. **Primary Identifier**: `utility_name_local` is the primary identifier used to link with projects during import.

3. **Original Name Update**: The `utility_name_original` field is updated separately using `scripts/update_utility_original_name.py` after the initial import.
