WITH products AS (
    SELECT DISTINCT
        product,
        COALESCE(sub_product, 'Unknown') AS sub_product,
        product_category
    FROM {{ ref('int_complaints_enriched') }}
    WHERE product IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY product, sub_product) AS product_key,
    product,
    sub_product,
    product_category
FROM products
