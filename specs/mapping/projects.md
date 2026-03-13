# Projects Table Mapping

> Source: `data/merge_final.json`  
> Import Script: `import_projects.py`

---

## Field Mapping

| Database Field | JSON Source Field | Description |
|----------------|-------------------|-------------|
| `project_name` | `Column1.Project Name (PN)` | Project name |
| `project_description` | `Column1.Project Description (PD)` | Project description (original language) |
| `description_english` | `Column1.Project Description (PD)_EN` | Project description (English translation) |
| `sector_id` | `Sector` → lookup `sector` table | Sector ID |
| `application_id` | `Application` → lookup `application` table | Application ID |
| `sub_application_id` | `Sub-application` → lookup `sub_application` table | Sub-application ID |
| `status_id` | Calculated from `CIPStartYear` and `CIPEndYear` | Status ID (see logic below) |
| `project_type_id` | `Status Tags` → lookup `project_type` table | Project type (New/Retrofit) |
| `utility_id` | `Column1.CIP Excel Document Utility Name - Local Language` → lookup `utilities` table | Utility ID |
| `utility_name` | `Column1.CIP Excel Document Utility Name - English Language` | Utility name (English) |

---

## Status Calculation Logic

The `status_id` is dynamically calculated based on CIP (Capital Improvement Plan) years:

```python
cip_start = Column1.CIPStartYear
cip_end = Column1.CIPEndYear
CURRENT_YEAR = 2026

if start_year > CURRENT_YEAR:
    status_id = 1  # planned
elif start_year <= CURRENT_YEAR <= end_year:
    status_id = 2  # ongoing
elif end_year < CURRENT_YEAR:
    status_id = 3  # inactive
else:
    status_id = 1  # default to planned
```

---

## Lookup Tables

### Sector Mapping
- Matches `Sector` field value to `sector.sector_name`
- Returns `sector.sector_id`

### Application Mapping
- Matches `Application` field value to `application.application_name`
- Returns `application.application_id`

### Sub-Application Mapping
- Matches `Sub-application` field value to `sub_application.sub_application_name`
- Returns `sub_application.sub_application_id`

### Project Type Mapping
- Matches `Status Tags` field value (lowercase) to `project_type.description`
- Common values: `new`, `retrofit`
- Returns `project_type.project_type_id`

### Utility Mapping
- Matches `Column1.CIP Excel Document Utility Name - Local Language` to `utilities.utility_name_local`
- Returns `utilities.utility_id`

---

## Example JSON Record

```json
{
  "Column1.Project Name (PN)": "Wastewater Treatment Plant Upgrade",
  "Column1.Project Description (PD)": "Upgrade der Kläranlage",
  "Column1.Project Description (PD)_EN": "Wastewater treatment plant upgrade",
  "Sector": "Wastewater",
  "Application": "Treatment",
  "Sub-application": "Secondary Treatment",
  "Column1.CIPStartYear": 2024,
  "Column1.CIPEndYear": 2028,
  "Status Tags": "New",
  "Column1.CIP Excel Document Utility Name - Local Language": "Berliner Wasserbetriebe",
  "Column1.CIP Excel Document Utility Name - English Language": "Berlin Water Works"
}
```

---

## Notes

1. **Utility Name Storage**: The `utility_name` field stores the English name, while `utility_id` is linked via the local language name.

2. **Missing Lookups**: If a lookup value is not found in the reference table, the corresponding `_id` field will be `NULL`.

3. **Year Fields**: `CIPStartYear` and `CIPEndYear` may be empty or invalid; in such cases, `status_id` defaults to `1` (planned).
