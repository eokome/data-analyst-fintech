WITH enriched      AS (SELECT * FROM {{ ref('int_complaints_enriched') }}),
     dim_date      AS (SELECT * FROM {{ ref('dim_date') }}),
     dim_product   AS (SELECT * FROM {{ ref('dim_product') }}),
     dim_company   AS (SELECT * FROM {{ ref('dim_company') }}),
     dim_geography AS (SELECT * FROM {{ ref('dim_geography') }}),
     dim_issue     AS (SELECT * FROM {{ ref('dim_issue') }})

SELECT
    e.complaint_id,
    dd.date_key,
    dp.product_key,
    dc.company_key,
    dg.state_key,
    di.issue_key,
    e.submitted_via,
    e.timely_response,
    e.consumer_disputed,
    e.has_narrative,
    e.company_response
FROM enriched e
LEFT JOIN dim_date      dd ON dd.full_date     = e.date_received
LEFT JOIN dim_product   dp ON dp.product       = e.product
                          AND dp.sub_product   = COALESCE(e.sub_product, 'Unknown')
LEFT JOIN dim_company   dc ON dc.company_name  = e.company
LEFT JOIN dim_geography dg ON dg.state_abbrev  = e.state
LEFT JOIN dim_issue     di ON di.issue         = e.issue
                          AND di.sub_issue     = COALESCE(e.sub_issue, 'Unknown')
