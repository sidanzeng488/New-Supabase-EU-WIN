-- =============================================
-- UPDATE NOTICE TABLE - Complete Structure
-- Run in Supabase SQL Editor
-- =============================================

-- =============================================
-- 1. 添加所有列到 notice 表
-- =============================================
ALTER TABLE public.notice
ADD COLUMN IF NOT EXISTS notice_type text,
ADD COLUMN IF NOT EXISTS publish_date date,
ADD COLUMN IF NOT EXISTS description text,
ADD COLUMN IF NOT EXISTS buyer_name_raw text,
ADD COLUMN IF NOT EXISTS buyer_utility_id integer,
ADD COLUMN IF NOT EXISTS buyer_email text,
ADD COLUMN IF NOT EXISTS buyer_match_confidence numeric,
ADD COLUMN IF NOT EXISTS application_id integer,
ADD COLUMN IF NOT EXISTS sector_id integer,
ADD COLUMN IF NOT EXISTS sub_application_id integer,
ADD COLUMN IF NOT EXISTS cpv_code text,
ADD COLUMN IF NOT EXISTS tender_start_date date,
ADD COLUMN IF NOT EXISTS tender_end_date date,
ADD COLUMN IF NOT EXISTS performance_start_date date,
ADD COLUMN IF NOT EXISTS performance_end_date date,
ADD COLUMN IF NOT EXISTS total_value numeric,
ADD COLUMN IF NOT EXISTS tender_type text,
ADD COLUMN IF NOT EXISTS tender_type_confidence double precision,
ADD COLUMN IF NOT EXISTS currency text,
ADD COLUMN IF NOT EXISTS notice_title text,
ADD COLUMN IF NOT EXISTS html_english text,
ADD COLUMN IF NOT EXISTS procurement_docs text,
ADD COLUMN IF NOT EXISTS original_description text,
ADD COLUMN IF NOT EXISTS buyer_city text,
ADD COLUMN IF NOT EXISTS buyer_country text,
ADD COLUMN IF NOT EXISTS winner_name text,
ADD COLUMN IF NOT EXISTS winner_email text;

-- =============================================
-- 2. 添加 CHECK 约束 (buyer_match_confidence 0-1)
-- =============================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'notice_buyer_match_confidence_check'
    ) THEN
        ALTER TABLE public.notice
        ADD CONSTRAINT notice_buyer_match_confidence_check
        CHECK (buyer_match_confidence IS NULL OR (buyer_match_confidence >= 0 AND buyer_match_confidence <= 1));
    END IF;
END $$;

-- =============================================
-- 3. 添加外键约束
-- =============================================

-- buyer_utility_id -> utilities(utility_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'notice_buyer_utility_id_fkey'
    ) THEN
        ALTER TABLE public.notice
        ADD CONSTRAINT notice_buyer_utility_id_fkey
        FOREIGN KEY (buyer_utility_id) REFERENCES public.utilities(utility_id);
    END IF;
END $$;

-- application_id -> application(application_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'notice_application_id_fkey'
    ) THEN
        ALTER TABLE public.notice
        ADD CONSTRAINT notice_application_id_fkey
        FOREIGN KEY (application_id) REFERENCES public.application(application_id);
    END IF;
END $$;

-- sector_id -> sector(sector_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'notice_sector_id_fkey'
    ) THEN
        ALTER TABLE public.notice
        ADD CONSTRAINT notice_sector_id_fkey
        FOREIGN KEY (sector_id) REFERENCES public.sector(sector_id);
    END IF;
END $$;

-- sub_application_id -> sub_application(sub_application_id)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'notice_sub_application_id_fkey'
    ) THEN
        ALTER TABLE public.notice
        ADD CONSTRAINT notice_sub_application_id_fkey
        FOREIGN KEY (sub_application_id) REFERENCES public.sub_application(sub_application_id);
    END IF;
END $$;

-- =============================================
-- 4. 创建索引以提升查询性能
-- =============================================
CREATE INDEX IF NOT EXISTS idx_notice_buyer_utility ON public.notice(buyer_utility_id);
CREATE INDEX IF NOT EXISTS idx_notice_application ON public.notice(application_id);
CREATE INDEX IF NOT EXISTS idx_notice_sector ON public.notice(sector_id);
CREATE INDEX IF NOT EXISTS idx_notice_sub_application ON public.notice(sub_application_id);
CREATE INDEX IF NOT EXISTS idx_notice_publish_date ON public.notice(publish_date);
CREATE INDEX IF NOT EXISTS idx_notice_tender_type ON public.notice(tender_type);
CREATE INDEX IF NOT EXISTS idx_notice_buyer_country ON public.notice(buyer_country);

-- =============================================
-- 5. 启用行级安全策略 (RLS)
-- =============================================
ALTER TABLE public.notice ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Enable all access" ON public.notice;
CREATE POLICY "Enable all access" ON public.notice FOR ALL USING (true) WITH CHECK (true);

-- =============================================
-- 6. 添加表注释
-- =============================================
COMMENT ON TABLE public.notice IS 'EU tender/procurement notices';
COMMENT ON COLUMN public.notice.notice_type IS 'Type of notice (e.g., contract award, prior information)';
COMMENT ON COLUMN public.notice.buyer_match_confidence IS 'Confidence level (0-1) for buyer matching';
COMMENT ON COLUMN public.notice.cpv_code IS 'Common Procurement Vocabulary code';
COMMENT ON COLUMN public.notice.tender_type_confidence IS 'Confidence level for tender type classification';

-- =============================================
-- 7. 验证表结构
-- =============================================
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'notice'
ORDER BY ordinal_position;

SELECT 'Notice table update completed successfully!' AS result;
