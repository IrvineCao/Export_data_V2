select keyword
    , onsite_storefront.marketplace_code
    , onsite_storefront.country_code
    , storefront_name
    , kw_discovery_storefront_keyword.storefront_id
    , operational_status
    , category_name
    , active_skus
    , shop_ads_status
    , product_ads_status
    , translation
    , brand_name
    , tag_1
    , tag_2
    , tag_3
    , note_1
    , note_2
    , kw_discovery_storefront_keyword.keyword_type
    , month(created_datetime)
    , storefront_division
    , sum(est_daily_search_volume)  as search_volume
    , sum(ads_gmv)                  as ads_gmv
    , sum(cost)                     as cost
    , sum(click)                    as click
    , sum(impression)               as impression
    , sum(ads_item_sold)            as ads_item_sold
    , AVG(current_avg_bidding_price)AS bidding_price
    , AVG(suggested_bidding_price)  AS suggested_bidding_price
    , peak_day_ads_gmv
    , peak_day_bau_ads_gmv
    , AVG((ads_gmv / cost))		    as roas
    , AVG((ads_item_sold / click))  AS cr
    , AVG((click / impression)) 	AS ctr
    , AVG((cost / click)) 			AS cpc
    , MAX(company_competitor) 		AS company_competitor
    , MAX(product_competitor) 		AS product_competitor
    , MAX(storefront_competitor) 	AS storefront_competitor
from kw_discovery_storefront_keyword
        join kw_discovery_storefront_keyword_perf
            on kw_discovery_storefront_keyword.storefront_id = kw_discovery_storefront_keyword_perf.storefront_id and
                kw_discovery_storefront_keyword.keyword_id = kw_discovery_storefront_keyword_perf.keyword_id
        join onsite_keyword on kw_discovery_storefront_keyword.keyword_id = onsite_keyword.id
        join onsite_storefront on kw_discovery_storefront_keyword.storefront_id = onsite_storefront.id
        join kw_discovery_storefront_workspace
            on kw_discovery_storefront_keyword.storefront_id = kw_discovery_storefront_workspace.storefront_id
where workspace_id = :workspace_id
and created_datetime between :start_date and :end_date
and ads_ops_storefront_id in :storefront_ids
and est_daily_search_volume > 0
and kw_discovery_storefront_keyword.keyword_type != 'irrelevant'
group by kw_discovery_storefront_keyword.keyword_id, kw_discovery_storefront_keyword.storefront_id,
    month(created_datetime)