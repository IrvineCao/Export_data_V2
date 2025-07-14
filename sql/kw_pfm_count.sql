WITH dim_data AS (
	SELECT
	  sf.storefront_type,
	  kw.keyword,
	  ws_tag.name,
	  kw.id AS dim_keyword_id,
	  kw.country_name AS keyword_country,
	  kw_ws.id AS keyword_ws_id,
	  sf.storefront_name,
	  sf.id AS storefront_id,
	  sf.marketplace_code as marketplace_code,
	  sf.storefront_sid,
	  aos.id AS aos_id,
	  sf_ws.workspace_id
	FROM onsite_storefront sf
	  JOIN onsite_storefront_workspace sf_ws ON sf_ws.storefront_id = sf.id
	  JOIN ads_ops_storefront aos ON sf_ws.ads_ops_storefront_id = aos.id
	  JOIN passport_workspace ws ON sf_ws.workspace_id = ws.id
	  JOIN onsite_keyword_workspace kw_ws ON kw_ws.workspace_id = ws.id
	  JOIN onsite_keyword_sharded kw ON kw_ws.keyword_id = kw.id
	  JOIN onsite_keyword_workspace_tag kw_ws_tag ON kw_ws_tag.keyword_workspace_id = kw_ws.id
	  LEFT JOIN onsite_workspace_tag ws_tag ON ws_tag.id = kw_ws_tag.workspace_tag_id
	WHERE true
	  AND sf.ads_ops_storefront_id IN :storefront_ids
	  AND ws.id = :workspace_id
)

,sos_metrics AS (
  SELECT
    s.timing,
    s.keyword_id AS sos_keyword_id,
    s.storefront_id,
    date(created_datetime) as sos_date,
    s.display_type AS display_type,
    AVG(s.share_of_search) AS share_of_search,
    s.product_position AS product_position,
    AVG(s.suggested_bidding_price) AS suggested_cpc,
    s.device_type AS device_type,
    AVG(s.search_volume) AS search_volume
  FROM global_company gc
    JOIN onsite_storefront sf ON sf.global_company_id = gc.id
    JOIN metric_share_of_search_storefront s ON s.storefront_id = sf.id
    JOIN (SELECT DISTINCT dim_keyword_id, storefront_id FROM dim_data) dim 
      ON s.keyword_id = dim.dim_keyword_id 
      AND s.storefront_id = dim.storefront_id
  WHERE TRUE
    AND (:device_type is null or s.device_type = :device_type)
  	AND (:display_type is null or s.display_type = :display_type)
  	AND (:product_position is null or s.product_position = :product_position)
    AND s.timing = 'daily'
    AND created_datetime between :start_date and :end_date
  GROUP BY s.keyword_id, s.storefront_id,month(created_datetime)
  ,s.display_type,s.device_type,s.product_position
)
,ads_metrics AS (
  SELECT
    p.timing,
    p.ads_ops_storefront_id,
    p.keyword_id AS ads_keyword_id,
    p.tool_id,
    date(created_datetime) as ads_date,
    SUM(p.ads_order) AS ads_order,
    SUM(p.cost) AS cost,
    SUM(p.direct_order) AS direct_order,
    SUM(p.ads_gmv) AS ads_gmv,
    SUM(p.direct_atc) AS direct_atc,
    SUM(p.direct_gmv) AS direct_gmv,
    SUM(p.direct_item_sold) AS direct_item_sold,
    SUM(p.click) AS click,
    SUM(p.atc) AS atc,
    SUM(p.ads_item_sold) AS ads_item_sold,
    SUM(p.impression) AS impression,
    AVG(p.active_skus) AS active_skus,
    SUM(p.direct_conversion) AS direct_conversion,
    SUM(p.conversion) AS conversion,
    AVG(p.active_shops) AS active_shops
  FROM ads_ops_storefront aos
    JOIN onsite_storefront_keyword_ads_performance p ON p.ads_ops_storefront_id = aos.id
    JOIN (SELECT DISTINCT dim_keyword_id, aos_id FROM dim_data) dim 
      ON p.keyword_id = dim.dim_keyword_id 
      AND p.ads_ops_storefront_id = dim.aos_id
  WHERE p.timing = 'daily'
    AND created_datetime between :start_date and :end_date
  GROUP BY p.ads_ops_storefront_id, p.keyword_id,month(created_datetime)
)

,main_data AS (
  SELECT
    d.*,
    s.search_volume,s.share_of_search,s.suggested_cpc,s.sos_date,s.display_type,s.device_type,s.product_position,
    a.ads_order,a.cost,a.direct_order,
    a.ads_gmv,a.direct_atc,a.direct_gmv,
    a.direct_item_sold,a.click,a.atc,
    a.ads_item_sold,a.impression,
    a.active_skus,a.direct_conversion,
    a.conversion,a.active_shops,
    (a.cost / NULLIF(a.click, 0)) AS cpc
  FROM dim_data d
    JOIN sos_metrics s ON s.sos_keyword_id = d.dim_keyword_id 
      AND s.storefront_id = d.storefront_id
    LEFT JOIN ads_metrics a ON a.ads_keyword_id = d.dim_keyword_id 
      AND a.ads_ops_storefront_id = d.aos_id
)

-- Final result
select count(1)
from(select 1
FROM main_data
GROUP BY
  workspace_id,
  storefront_id,
  keyword_ws_id,
  month(sos_date)
  ,display_type,device_type,product_position)