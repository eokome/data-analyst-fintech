WITH source AS (
    SELECT * FROM {{ source('raw', 'complaints') }}
)

SELECT
    TRY_CAST(complaint_id AS INT)                                          AS complaint_id,
    TRY_TO_DATE(LEFT(date_received, 10))                                   AS date_received,
    product,
    sub_product,
    issue,
    sub_issue,
    consumer_complaint_narrative,
    company_public_response,
    company,
    state,
    zip_code,
    submitted_via,
    company_response_to_consumer                                           AS company_response,
    IFF(LOWER(timely_response) = 'yes', TRUE, FALSE)                       AS timely_response,
    IFF(LOWER(consumer_disputed) = 'yes', TRUE, FALSE)                    AS consumer_disputed,
    (
        consumer_complaint_narrative IS NOT NULL
        AND consumer_complaint_narrative != ''
    )::BOOLEAN                                                             AS has_narrative
FROM source
WHERE TRY_CAST(complaint_id AS INT) IS NOT NULL
