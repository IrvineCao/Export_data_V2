WITH main_query AS (
    SELECT
        keyword.id as keyword____a_id,
        product_a.device_type AS product____a_device_type,
        product_a.display_type AS product____a_display_type,
        product.id AS product____a_id,
        workspace.id AS workspace____a_id
    FROM passport_workspace AS workspace
        INNER JOIN onsite_storefront AS storefront ON (true)
        INNER JOIN onsite_product AS product ON (product.storefront_id = storefront.id)
        INNER JOIN onsite_keyword_sharded AS keyword ON (true)
        INNER JOIN onsite_keyword_workspace AS keyword_workspace ON (keyword_workspace.workspace_id = workspace.id)
        AND (keyword_workspace.keyword_id = keyword.id)
        INNER JOIN (
            SELECT
                product_a.timing as timing,
                product_a.keyword_id,
                product_a.product_id,
                MAX(product_a.display_type) AS display_type,
                MAX(product_a.device_type) AS device_type
            FROM onsite_keyword_sharded AS keyword
            INNER JOIN metric_share_of_search_product AS product_a ON (product_a.keyword_id = keyword.id)
            WHERE true
                AND product_a.timing = 'daily'
                AND (
                    (
                        created_datetime BETWEEN :start_date AND :end_date
                    )
                )
            GROUP BY
                product_a.keyword_id,
                product_a.product_id,
                product_a.device_type,
                product_a.display_type
        ) product_a 
        ON (product_a.keyword_id = keyword.id)
        AND (product_a.product_id = product.id)
        AND product_a.timing = 'daily'
    WHERE true
        AND (
            storefront.ads_ops_storefront_id IN :storefront_ids
            and workspace.id = :workspace_id
        )
    GROUP BY
        keyword_workspace.id,
        product.id,
        product_a.device_type,
        product_a.display_type,
        keyword.id
)
select count(1)
from (SELECT 1
FROM main_query
GROUP BY keyword____a_id,product____a_id,product____a_device_type,product____a_display_type)