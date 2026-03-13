-- =============================================
-- FIX PROJECTS WITHOUT UTILITY
-- =============================================

-- =============================================
-- 1. DELETE INVALID RECORDS (project_name = '0')
-- =============================================

-- Check first
SELECT project_id, project_name FROM projects WHERE project_name = '0';

-- Delete invalid records
DELETE FROM projects WHERE project_name = '0';

-- =============================================
-- 2. CHECK IF UTILITIES EXIST
-- =============================================

-- Check for Irish Water
SELECT utility_id, utility_name_local, utility_name_en 
FROM utilities 
WHERE utility_name_local LIKE '%Uisce%' 
   OR utility_name_local LIKE '%Irish Water%'
   OR utility_name_en LIKE '%Irish Water%';

-- Check for Katowickie Wodociągi
SELECT utility_id, utility_name_local, utility_name_en 
FROM utilities 
WHERE utility_name_local LIKE '%Katowic%' 
   OR utility_name_en LIKE '%Katowic%';

-- =============================================
-- 3. UPDATE IRISH WATER PROJECTS (7037-7053)
-- If utility exists, update these projects
-- =============================================

-- First, find the utility_id for Irish Water
-- Then update:
/*
UPDATE projects
SET 
    utility_id = (SELECT utility_id FROM utilities WHERE utility_name_local LIKE '%Uisce%' OR utility_name_en LIKE '%Irish Water%' LIMIT 1),
    utility_name = 'Irish Water'
WHERE project_id BETWEEN 7037 AND 7053;
*/

-- =============================================
-- 4. UPDATE POLISH PROJECTS (9189-9196)
-- If utility exists, update these projects
-- =============================================

/*
UPDATE projects
SET 
    utility_id = (SELECT utility_id FROM utilities WHERE utility_name_local LIKE '%Katowic%' LIMIT 1),
    utility_name = 'Katowickie Wodociągi S.A.'
WHERE project_id BETWEEN 9189 AND 9196;
*/

-- =============================================
-- 5. VERIFY RESULTS
-- =============================================

-- Check remaining projects without utility
SELECT 
    COUNT(*) as total_projects,
    COUNT(utility_id) as with_utility,
    COUNT(*) - COUNT(utility_id) as without_utility
FROM projects;

-- List any remaining without utility
SELECT project_id, project_name, utility_name, utility_id
FROM projects
WHERE utility_id IS NULL;
