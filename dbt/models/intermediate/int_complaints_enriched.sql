WITH stg AS (
    SELECT * FROM {{ ref('stg_complaints') }}
)

SELECT
    *,
    CASE
        WHEN product ILIKE '%mortgage%'
          OR product ILIKE '%loan%'
          OR product ILIKE '%payday%'
          OR product ILIKE '%student%'
          OR product ILIKE '%vehicle%'        THEN 'Lending'
        WHEN product ILIKE '%credit card%'
          OR product ILIKE '%prepaid%'        THEN 'Cards'
        WHEN product ILIKE '%checking%'
          OR product ILIKE '%saving%'
          OR product ILIKE '%money transfer%'
          OR product ILIKE '%bank%'           THEN 'Banking'
        WHEN product ILIKE '%debt%'
          OR product ILIKE '%credit reporting%'
          OR product ILIKE '%credit repair%'  THEN 'Debt'
        ELSE 'Other'
    END AS product_category
FROM stg
