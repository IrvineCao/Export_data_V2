select count(1)
from(select 1
from kw_discovery_storefront_keyword
        join kw_discovery_storefront_keyword_perf
            on kw_discovery_storefront_keyword.storefront_id = kw_discovery_storefront_keyword_perf.storefront_id and
                kw_discovery_storefront_keyword.keyword_id = kw_discovery_storefront_keyword_perf.keyword_id
        join onsite_keyword on kw_discovery_storefront_keyword.keyword_id = onsite_keyword.id
        join onsite_storefront on kw_discovery_storefront_keyword.storefront_id = onsite_storefront.id
        join kw_discovery_storefront_workspace
            on kw_discovery_storefront_keyword.storefront_id = kw_discovery_storefront_workspace.storefront_id
where workspace_id = :workspace_id
and ads_ops_storefront_id in :storefront_ids
and created_datetime between :start_date and :end_date
and est_daily_search_volume > 0
and kw_discovery_storefront_keyword.keyword_type != 'irrelevant'
group by kw_discovery_storefront_keyword.keyword_id, kw_discovery_storefront_keyword.storefront_id,
        month(created_datetime))