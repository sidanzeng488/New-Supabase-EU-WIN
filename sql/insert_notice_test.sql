-- =============================================
-- INSERT TEST NOTICE RECORD
-- Rhine Culvert Construction Project - Cologne
-- =============================================

-- First, let's get the required IDs from lookup tables
-- You may need to adjust these based on your actual data

-- Check if application exists
SELECT application_id, application_name FROM application WHERE application_name = 'Wastewater Networks';

-- Check if sector exists  
SELECT sector_id, sector_name FROM sector WHERE sector_name = 'Wastewater';

-- Check if sub_application exists
SELECT sub_application_id, sub_application_name FROM sub_application WHERE sub_application_name = 'Collection Systems';

-- Check if utility exists
SELECT utility_id, utility_name_local FROM utilities WHERE utility_name_local LIKE '%Stadtentwässerungsbetriebe Köln%';

-- =============================================
-- INSERT NOTICE
-- =============================================

INSERT INTO notice (
    notice_type,
    publish_date,
    description,
    buyer_name_raw,
    buyer_utility_id,
    buyer_email,
    buyer_match_confidence,
    application_id,
    sector_id,
    sub_application_id,
    cpv_code,
    tender_end_date,
    performance_end_date,
    total_value,
    tender_type,
    tender_type_confidence,
    currency,
    notice_title,
    html_english,
    procurement_docs,
    original_description,
    buyer_city,
    buyer_country,
    winner_name,
    winner_email
) VALUES (
    'can-standard',
    '2025-02-12'::date,
    'This request includes all measures for the construction of a Rhine culvert from Cologne-Niehl to Stammheim, including the Rhine crossing. The scope of services includes the technical equipment relating to the mechanical and piping technology trade. The following main equipment parts are planned: - New construction of stainless steel pipelines DN 2,000 with a total length of approx. 40m, DN 1,4000 with a total length of approx. 45m, DN 1,100 with a total length of 40m, DN 80 to DN 800 with a total length of approx. 460m, as well as shut-off valves in the named nominal widths. -Steel and stage structures made of stainless steel and galvanized steel with a total weight of approx. 50,000kg. - Renewal and construction of ventilation systems for three buildings on the left and right banks of the Rhine. - Dismantling and replacing the exhaust air treatment system for the sewer connection on the left bank of the Rhine with a double slide valve structure. - Construction of air dehumidification systems in the buildings on the left and right banks of the Rhine. - New construction of six channel gates for the sewer connection on the left bank of the Rhine in the double gate structure for the three culvert pipes DN 1,100, DN 1,400 and DN 2,000, as well as three channel gate valves for the channel connection on the right bank of the Rhine in the gate and union structure for the three culvert pipes DN 1,100, DN 1,400 and DN 2,000. Furthermore, a throttle valve (3,000x2,500mm) in the inlet canal on the right bank of the Rhine and a gate valve connected to the existing canal of the GKW on the right bank of the Rhine. - Construction of 5 emptying and drainage pumps in the head of the culvert with drainage in front of the double slide valve structure, as well as in the inspection and MID shaft. - Production of a total of three crane systems in the culvert head, inspection shaft and MID shaft.',
    'StEB Stadtentwässerungsbetriebe Köln, AöR',
    (SELECT utility_id FROM utilities WHERE utility_name_local LIKE '%Stadtentwässerungsbetriebe Köln%' LIMIT 1),
    'vergabestelle@steb-koeln.de',
    1.0,  -- buyer_match_confidence (matched utility)
    (SELECT application_id FROM application WHERE application_name = 'Wastewater Networks' LIMIT 1),
    (SELECT sector_id FROM sector WHERE sector_name = 'Wastewater' LIMIT 1),
    (SELECT sub_application_id FROM sub_application WHERE sub_application_name = 'Collection Systems' LIMIT 1),
    '45231300, 45231000, 45252130, 90000000, 39350000',
    NULL,  -- tender_end_date
    '2027-09-30'::date,  -- performance_end_date
    8754930.22,  -- total_value
    'Results',  -- tender_type
    0.438,  -- tender_type_confidence
    'EUR',
    'Germany – Construction work for water and sewage pipelines – Maschinen- und Rohrtechnik, Neubau Reindüker',
    'https://ted.europa.eu/en/notice/-/detail/94945-2025',
    NULL,  -- procurement_docs
    'Bestandteil dieser Anfrage sind alle Maßnahmen zur Herstellung eines Rheindükers von Köln-Niehl nach Stammheim, inklusive Rheinquerung Der Leistungsumfang umfasst die technische Ausrüstung bezüglich des Gewerkes Maschinen- und Rohrleitungstechnik. Folgende Hauptausrüstungsteile sind hierbei vorgesehen: - Neuaufbau von Edelstahlrohrleitungen DN 2.000 mit einer Gesamtlänge von ca. 40m, DN 1.4000 mit einer Gesamtlänge von ca. 45m, DN 1.100 mit einer Gesamtlänge von 40m, DN 80 bis DN 800 mit einer Gesamtlänge von ca. 460m, sowie Absperrarrmaturen in den genannten Nennweiten. -Stahl- und Bühnenkonstruktionen in Edlstahl und Stahl verzinkt mit einem Gesamtgewicht von ca. 50.000kg. - Erneuerung und Neuaufbau von Be- und Entlüftungsanlagen für drei Bauwerke links- und rechtsrheinisch. - Demontage und Erneuerung der Abluftbehandlungsanlage für den Kanalanschluss linksrheinisch mit Doppelschieberbauwerk. - Aufbau von Luftentfeuchtungsanlagen in den Bauwerken links- und rechtsrheinisch. - Neuaufbau von sechs Kanalschiebern für den Kanalanschluss linksrheinisch im Doppelschieberbauwerk für die drei Dükerleitungen DN 1.100, DN 1.400 und DN 2.000, sowie drei Kanalschiebern für den Kanalanschluss rechtsrheinisch im Schieber- und Vereinigungsbauwerk für die drei Dükerleitungen DN 1.100, DN 1.400 und DN 2.000. Weiterhin ein Drosselschieber (3.000x2.500mm) im Zulaufkanal rechtsrheinisch und ein Absperrschieber im Anschluss an den Bestandskanal des GKW rechts-rheinisch. - Aufbau von 5 Entleerungs- und entwässerungspumpen im Dükeroberhaupt mit Ableitung vor das Doppelschieberbauwerk, sowie im Inspektions- und MID-Schacht. - Herstellung von insgesamt drei Krananlagen im Dükeroberhaupt, Inspektionsschacht, sowie MID Schacht.',
    'Köln',
    'DEU',
    'Schachtbau Nordhausen GmbH',
    'SBN@schachtbau.de'
)
RETURNING notice_id;

-- =============================================
-- VERIFY INSERT
-- =============================================
SELECT 
    notice_id,
    notice_type,
    publish_date,
    notice_title,
    buyer_name_raw,
    buyer_city,
    total_value,
    winner_name
FROM notice 
WHERE notice_title LIKE '%Reindüker%'
ORDER BY notice_id DESC
LIMIT 1;
