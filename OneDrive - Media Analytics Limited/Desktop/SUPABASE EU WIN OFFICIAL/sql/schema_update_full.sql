-- =============================================
-- SCHEMA UPDATE - Full ER Diagram Implementation
-- Run in Supabase SQL Editor
-- =============================================

-- =============================================
-- 1. 创建 country 表 (基础表，被多个表引用)
-- =============================================
CREATE TABLE IF NOT EXISTS public.country (
    country_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    country_code VARCHAR UNIQUE NOT NULL,
    country_name VARCHAR
);

ALTER TABLE public.country ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all access" ON public.country;
CREATE POLICY "Enable all access" ON public.country FOR ALL USING (true) WITH CHECK (true);

COMMENT ON TABLE public.country IS 'Country lookup table with ISO codes';

-- =============================================
-- 2. 创建 report_code 表
-- =============================================
CREATE TABLE IF NOT EXISTS public.report_code (
    rep_code_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rep_code VARCHAR UNIQUE NOT NULL,
    country_code VARCHAR REFERENCES public.country(country_code),
    year INTEGER,
    version VARCHAR
);

ALTER TABLE public.report_code ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all access" ON public.report_code;
CREATE POLICY "Enable all access" ON public.report_code FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_report_code_country ON public.report_code(country_code);

COMMENT ON TABLE public.report_code IS 'UWWTD report code reference table';

-- =============================================
-- 3. 创建 sensitivity 表
-- =============================================
CREATE TABLE IF NOT EXISTS public.sensitivity (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code VARCHAR UNIQUE NOT NULL,
    definition TEXT,
    nutrient_sensitivity BOOLEAN
);

ALTER TABLE public.sensitivity ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all access" ON public.sensitivity;
CREATE POLICY "Enable all access" ON public.sensitivity FOR ALL USING (true) WITH CHECK (true);

COMMENT ON TABLE public.sensitivity IS 'Water body sensitivity classifications';

-- =============================================
-- 4. 创建 plant_capacity 表
-- =============================================
CREATE TABLE IF NOT EXISTS public.plant_capacity (
    plant_capacity_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    plant_capacity INTEGER,
    rep_code VARCHAR REFERENCES public.report_code(rep_code)
);

ALTER TABLE public.plant_capacity ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all access" ON public.plant_capacity;
CREATE POLICY "Enable all access" ON public.plant_capacity FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_plant_capacity_rep_code ON public.plant_capacity(rep_code);

COMMENT ON TABLE public.plant_capacity IS 'Plant capacity by report period';

-- =============================================
-- 5. 创建 water_bodies 表
-- =============================================
CREATE TABLE IF NOT EXISTS public.water_bodies (
    water_body_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    eu_water_body_code VARCHAR UNIQUE,
    water_type VARCHAR,
    water_body_name VARCHAR,
    country_code VARCHAR REFERENCES public.country(country_code),
    eu_rbd_code VARCHAR,
    rbd_name VARCHAR,
    c_year INTEGER,
    surface_water_category VARCHAR,
    c_area NUMERIC,
    c_length NUMERIC,
    sw_ecological_status VARCHAR,
    sw_chemical_status VARCHAR,
    gw_quantitative_status VARCHAR,
    gw_chemical_status VARCHAR,
    file_url TEXT
);

ALTER TABLE public.water_bodies ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all access" ON public.water_bodies;
CREATE POLICY "Enable all access" ON public.water_bodies FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_water_bodies_country ON public.water_bodies(country_code);
CREATE INDEX IF NOT EXISTS idx_water_bodies_eu_code ON public.water_bodies(eu_water_body_code);

COMMENT ON TABLE public.water_bodies IS 'EU Water Framework Directive water bodies';

-- =============================================
-- 6. 创建 water_body_protected_areas 表
-- =============================================
CREATE TABLE IF NOT EXISTS public.water_body_protected_areas (
    protected_area_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    water_body_code VARCHAR REFERENCES public.water_bodies(eu_water_body_code),
    eu_protected_area_code VARCHAR,
    protected_area_type VARCHAR,
    objectives_set BOOLEAN,
    objectives_met BOOLEAN
);

ALTER TABLE public.water_body_protected_areas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all access" ON public.water_body_protected_areas;
CREATE POLICY "Enable all access" ON public.water_body_protected_areas FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_protected_areas_water_body ON public.water_body_protected_areas(water_body_code);

COMMENT ON TABLE public.water_body_protected_areas IS 'Protected areas associated with water bodies';

-- =============================================
-- 7. 创建 uwwtp_rep 表
-- =============================================
CREATE TABLE IF NOT EXISTS public.uwwtp_rep (
    rep_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rep_code VARCHAR REFERENCES public.report_code(rep_code),
    date_published DATE,
    date_situation_at DATE
);

ALTER TABLE public.uwwtp_rep ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all access" ON public.uwwtp_rep;
CREATE POLICY "Enable all access" ON public.uwwtp_rep FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_uwwtp_rep_code ON public.uwwtp_rep(rep_code);

COMMENT ON TABLE public.uwwtp_rep IS 'UWWTD reporting periods';

-- =============================================
-- 8. 更新 agglomeration 表 - 添加新列
-- =============================================
ALTER TABLE public.agglomeration 
ADD COLUMN IF NOT EXISTS agg_code VARCHAR UNIQUE,
ADD COLUMN IF NOT EXISTS country_code VARCHAR REFERENCES public.country(country_code),
ADD COLUMN IF NOT EXISTS agg_capacity INTEGER,
ADD COLUMN IF NOT EXISTS agg_generated NUMERIC,
ADD COLUMN IF NOT EXISTS latitude FLOAT,
ADD COLUMN IF NOT EXISTS longitude FLOAT;

CREATE INDEX IF NOT EXISTS idx_agglomeration_country ON public.agglomeration(country_code);
CREATE INDEX IF NOT EXISTS idx_agglomeration_agg_code ON public.agglomeration(agg_code);

-- =============================================
-- 9. 更新 plants 表 - 添加所有新列
-- =============================================
-- 基础信息列
ALTER TABLE public.plants 
ADD COLUMN IF NOT EXISTS uwwtp_code VARCHAR UNIQUE,
ADD COLUMN IF NOT EXISTS longitude FLOAT,
ADD COLUMN IF NOT EXISTS plant_capacity_id INTEGER REFERENCES public.plant_capacity(plant_capacity_id),
ADD COLUMN IF NOT EXISTS country_code VARCHAR REFERENCES public.country(country_code),
ADD COLUMN IF NOT EXISTS rep_code VARCHAR REFERENCES public.report_code(rep_code);

-- 处理类型布尔列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS provides_primary_treatment BOOLEAN,
ADD COLUMN IF NOT EXISTS provides_secondary_treatment BOOLEAN,
ADD COLUMN IF NOT EXISTS other_treatment_provided BOOLEAN,
ADD COLUMN IF NOT EXISTS provides_nitrogen_removal BOOLEAN,
ADD COLUMN IF NOT EXISTS provides_phosphorus_removal BOOLEAN,
ADD COLUMN IF NOT EXISTS includes_uv_treatment BOOLEAN,
ADD COLUMN IF NOT EXISTS includes_chlorination BOOLEAN,
ADD COLUMN IF NOT EXISTS includes_ozonation BOOLEAN,
ADD COLUMN IF NOT EXISTS includes_sand_filtration BOOLEAN,
ADD COLUMN IF NOT EXISTS includes_microfiltration BOOLEAN;

-- 其他信息列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS failure_notes TEXT,
ADD COLUMN IF NOT EXISTS commissioning_date DATE,
ADD COLUMN IF NOT EXISTS plant_notes TEXT,
ADD COLUMN IF NOT EXISTS pct_wastewater_reused NUMERIC,
ADD COLUMN IF NOT EXISTS volume_wastewater_reused_m3_per_year NUMERIC;

-- BOD 列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS bod_incoming_measured NUMERIC,
ADD COLUMN IF NOT EXISTS bod_incoming_calculated NUMERIC,
ADD COLUMN IF NOT EXISTS bod_incoming_estimated NUMERIC,
ADD COLUMN IF NOT EXISTS bod_outgoing_measured NUMERIC,
ADD COLUMN IF NOT EXISTS bod_outgoing_calculated NUMERIC,
ADD COLUMN IF NOT EXISTS bod_outgoing_estimated NUMERIC,
ADD COLUMN IF NOT EXISTS bod_removal_pct NUMERIC;

-- COD 列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS cod_incoming_measured NUMERIC,
ADD COLUMN IF NOT EXISTS cod_incoming_calculated NUMERIC,
ADD COLUMN IF NOT EXISTS cod_incoming_estimated NUMERIC,
ADD COLUMN IF NOT EXISTS cod_outgoing_measured NUMERIC,
ADD COLUMN IF NOT EXISTS cod_outgoing_calculated NUMERIC,
ADD COLUMN IF NOT EXISTS cod_outgoing_estimated NUMERIC,
ADD COLUMN IF NOT EXISTS cod_removal_pct NUMERIC;

-- Nitrogen 列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS nitrogen_incoming_measured NUMERIC,
ADD COLUMN IF NOT EXISTS nitrogen_incoming_calculated NUMERIC,
ADD COLUMN IF NOT EXISTS nitrogen_incoming_estimated NUMERIC,
ADD COLUMN IF NOT EXISTS nitrogen_outgoing_measured NUMERIC,
ADD COLUMN IF NOT EXISTS nitrogen_outgoing_calculated NUMERIC,
ADD COLUMN IF NOT EXISTS nitrogen_outgoing_estimated NUMERIC,
ADD COLUMN IF NOT EXISTS nitrogen_removal_pct NUMERIC;

-- Phosphorus 列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS phosphorus_incoming_measured NUMERIC,
ADD COLUMN IF NOT EXISTS phosphorus_incoming_calculated NUMERIC,
ADD COLUMN IF NOT EXISTS phosphorus_incoming_estimated NUMERIC,
ADD COLUMN IF NOT EXISTS phosphorus_outgoing_measured NUMERIC,
ADD COLUMN IF NOT EXISTS phosphorus_outgoing_calculated NUMERIC,
ADD COLUMN IF NOT EXISTS phosphorus_outgoing_estimated NUMERIC,
ADD COLUMN IF NOT EXISTS phosphorus_removal_pct NUMERIC;

-- Article 17 列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS article17_report_date DATE,
ADD COLUMN IF NOT EXISTS article17_compliance_status TEXT,
ADD COLUMN IF NOT EXISTS article17_investment_planned BOOLEAN,
ADD COLUMN IF NOT EXISTS article17_investment_type TEXT,
ADD COLUMN IF NOT EXISTS article17_investment_need NUMERIC,
ADD COLUMN IF NOT EXISTS article17_investment_cost NUMERIC;

-- Funding 列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS eu_funding_scheme TEXT,
ADD COLUMN IF NOT EXISTS eu_funding_amount NUMERIC,
ADD COLUMN IF NOT EXISTS other_funding_scheme TEXT,
ADD COLUMN IF NOT EXISTS other_funding_amount NUMERIC;

-- Planning/Construction 列
ALTER TABLE public.plants
ADD COLUMN IF NOT EXISTS planning_start_date DATE,
ADD COLUMN IF NOT EXISTS construction_start_date DATE,
ADD COLUMN IF NOT EXISTS construction_completion_date DATE,
ADD COLUMN IF NOT EXISTS expected_commissioning_date DATE,
ADD COLUMN IF NOT EXISTS capacity_expansion NUMERIC;

-- Plants 表索引
CREATE INDEX IF NOT EXISTS idx_plants_uwwtp_code ON public.plants(uwwtp_code);
CREATE INDEX IF NOT EXISTS idx_plants_country ON public.plants(country_code);
CREATE INDEX IF NOT EXISTS idx_plants_rep_code ON public.plants(rep_code);
CREATE INDEX IF NOT EXISTS idx_plants_capacity ON public.plants(plant_capacity_id);

-- =============================================
-- 10. 创建 discharge_points 表
-- =============================================
CREATE TABLE IF NOT EXISTS public.discharge_points (
    dcp_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dcp_code VARCHAR UNIQUE,
    plant_code VARCHAR REFERENCES public.plants(uwwtp_code),
    country_code VARCHAR REFERENCES public.country(country_code),
    latitude FLOAT,
    longitude FLOAT,
    is_surface_water BOOLEAN,
    water_body_type VARCHAR,
    water_body_code VARCHAR REFERENCES public.water_bodies(eu_water_body_code),
    sensitivity_code VARCHAR REFERENCES public.sensitivity(code),
    rca_code VARCHAR,
    receiving_water VARCHAR,
    wfd_rbd VARCHAR,
    wfd_sub_unit VARCHAR,
    rep_code VARCHAR REFERENCES public.report_code(rep_code)
);

ALTER TABLE public.discharge_points ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Enable all access" ON public.discharge_points;
CREATE POLICY "Enable all access" ON public.discharge_points FOR ALL USING (true) WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_discharge_points_plant ON public.discharge_points(plant_code);
CREATE INDEX IF NOT EXISTS idx_discharge_points_country ON public.discharge_points(country_code);
CREATE INDEX IF NOT EXISTS idx_discharge_points_water_body ON public.discharge_points(water_body_code);
CREATE INDEX IF NOT EXISTS idx_discharge_points_sensitivity ON public.discharge_points(sensitivity_code);
CREATE INDEX IF NOT EXISTS idx_discharge_points_rep_code ON public.discharge_points(rep_code);

COMMENT ON TABLE public.discharge_points IS 'Wastewater discharge points';

-- =============================================
-- 11. 重命名 utilities 表的列 (如果需要)
-- =============================================
-- 将 Utility_Name_EN 重命名为 utility_name_en (小写)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'utilities' AND column_name = 'Utility_Name_EN') THEN
        ALTER TABLE public.utilities RENAME COLUMN "Utility_Name_EN" TO utility_name_en;
    END IF;
END $$;

-- =============================================
-- 12. 添加表注释
-- =============================================
COMMENT ON TABLE public.plants IS 'Wastewater treatment plants with UWWTD data';
COMMENT ON TABLE public.agglomeration IS 'Urban agglomerations as defined by UWWTD';
COMMENT ON TABLE public.country IS 'Country reference table';
COMMENT ON TABLE public.report_code IS 'UWWTD reporting period codes';

-- =============================================
-- 完成
-- =============================================
SELECT 'Schema update completed successfully!' AS result;
