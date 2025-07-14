WITH main_query AS (
    SELECT
        keyword.id AS keyword____a_id,
        keyword.keyword_type AS keyword____a_keyword_type,
        keyword.keyword AS keyword____a_keyword,
        product_a.device_type AS product____a_device_type,
        keyword.status AS keyword____a_status,
        product_a.display_type AS product____a_display_type,
        keyword.first_interaction_at AS keyword____a_first_interaction_at,
        product.marketplace_name AS product____a_marketplace_name,
        product.id AS product____a_id,
        product.product_url AS product____a_product_url,
        product.historical_sold AS product____a_historical_sold,
        storefront.storefront_type AS storefront____a_storefront_type,
        product.brand_name AS product____a_brand_name,
        product.product_name AS product____a_product_name,
        product.selling_price AS product____a_selling_price,
        product.sold AS product____a_sold,
        product.discount AS product____a_discount,
        global_company_z.name AS storefront____global_company____a_name,
        storefront.id AS storefront____a_id,
        storefront.storefront_url AS storefront____a_storefront_url,
        storefront.storefront_name AS storefront____a_storefront_name,
        storefront.country_name AS storefront____a_country_name,
        storefront.marketplace_name AS storefront____a_marketplace_name,
        product_a.slot AS product____m_slot,
        workspace.id AS workspace____a_id
    FROM passport_workspace AS workspace
        INNER JOIN onsite_storefront AS storefront ON (true)
        LEFT JOIN global_company AS global_company_z ON storefront.global_company_id = global_company_z.id
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
                MAX(product_a.device_type) AS device_type,
                AVG(product_a.slot) AS slot
            FROM
                onsite_keyword_sharded AS keyword
                INNER JOIN metric_share_of_search_product AS product_a ON (product_a.keyword_id = keyword.id)
            WHERE
                true
                AND product_a.timing = 'daily'
                AND (
                    (
                        created_datetime BETWEEN :start_date AND :end_date
                    )
                )
            GROUP BY
                NULL,
                product_a.keyword_id,
                product_a.product_id,
                product_a.device_type,
                product_a.display_type
        ) product_a ON (product_a.keyword_id = keyword.id)
        AND (product_a.product_id = product.id)
        AND product_a.timing = 'daily'
    WHERE
        (true)
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
SELECT
    keyword____a_keyword as keyword,
    product____a_product_name as product_name,
    storefront____global_company____a_name as global_company,
    storefront____a_storefront_name as storefront_name,
    product____a_historical_sold as item_sold_LT,
    product____a_sold as item_sold_l30d,
    product____a_selling_price as selling_price,
    round(AVG(product____m_slot),0) AS product_slot,
    product____a_device_type as device_type,
    product____a_display_type as display_type
FROM
    main_query
GROUP BY
    keyword____a_id,
    product____a_id,
    product____a_device_type,
    product____a_display_type