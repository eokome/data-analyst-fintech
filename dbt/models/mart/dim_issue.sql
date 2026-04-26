WITH issues AS (
    SELECT DISTINCT
        issue,
        COALESCE(sub_issue, 'Unknown') AS sub_issue
    FROM {{ ref('stg_complaints') }}
    WHERE issue IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY issue, sub_issue) AS issue_key,
    issue,
    sub_issue
FROM issues
