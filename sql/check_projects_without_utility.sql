-- =============================================
-- CHECK PROJECTS WITHOUT UTILITY LINK
-- =============================================

-- 1. Count projects without utility_id
SELECT 
    COUNT(*) as total_projects,
    COUNT(utility_id) as with_utility,
    COUNT(*) - COUNT(utility_id) as without_utility
FROM projects;

-- 2. List projects without utility_id
SELECT 
    project_id,
    project_name,
    utility_name,
    utility_id
FROM projects
WHERE utility_id IS NULL
ORDER BY project_id;

-- 3. Group by utility_name to see patterns
SELECT 
    utility_name,
    COUNT(*) as project_count
FROM projects
WHERE utility_id IS NULL
GROUP BY utility_name
ORDER BY project_count DESC;

-- 4. Check if utility_name exists in utilities table but not linked
SELECT 
    p.project_id,
    p.project_name,
    p.utility_name as project_utility_name,
    u.utility_id,
    u.utility_name_local,
    u.utility_name_en
FROM projects p
LEFT JOIN utilities u ON p.utility_name = u.utility_name_en 
                      OR p.utility_name = u.utility_name_local
WHERE p.utility_id IS NULL
AND u.utility_id IS NOT NULL
LIMIT 20;
