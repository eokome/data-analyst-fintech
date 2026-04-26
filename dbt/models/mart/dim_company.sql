WITH companies AS (
    SELECT DISTINCT company
    FROM {{ ref('stg_complaints') }}
    WHERE company IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY company) AS company_key,
    company                              AS company_name
FROM companies
