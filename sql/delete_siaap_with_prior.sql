-- =============================================
-- DELETE SIAAP WITH_PRIOR RECORDS
-- Run in Supabase SQL Editor
-- Date: 2026-03-13
-- =============================================

-- Check records before deletion
SELECT 
    utility_name,
    cost_type,
    COUNT(*) as record_count,
    SUM(cost) as total_cost
FROM spending_plan
WHERE utility_name LIKE '%SIAAP%'
GROUP BY utility_name, cost_type
ORDER BY cost_type;

-- =============================================
-- DELETE redundant total_with_prior records
-- These are redundant because:
-- total_with_prior = total + prior_years
-- =============================================

DELETE FROM spending_plan
WHERE utility_name LIKE '%SIAAP%'
  AND cost_type = 'total_with_prior';

-- Verify deletion
SELECT 
    'Remaining SIAAP records by cost_type:' as info;

SELECT 
    cost_type,
    COUNT(*) as record_count
FROM spending_plan
WHERE utility_name LIKE '%SIAAP%'
GROUP BY cost_type
ORDER BY cost_type;

-- Confirm no more total_with_prior records exist
SELECT 
    COUNT(*) as remaining_with_prior_count
FROM spending_plan
WHERE cost_type = 'total_with_prior';

SELECT 'SIAAP with_prior cleanup completed!' AS result;
