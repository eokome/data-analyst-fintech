WITH date_spine AS (
    SELECT
        DATEADD(DAY, SEQ4(), '2020-01-01'::DATE) AS full_date
    FROM TABLE(GENERATOR(ROWCOUNT => 3650))
    WHERE DATEADD(DAY, SEQ4(), '2020-01-01'::DATE) <= CURRENT_DATE()
)

SELECT
    TO_NUMBER(TO_CHAR(full_date, 'YYYYMMDD'))                       AS date_key,
    full_date,
    YEAR(full_date)                                                  AS year,
    QUARTER(full_date)                                               AS quarter,
    MONTH(full_date)                                                 AS month,
    TO_CHAR(full_date, 'MMMM')                                      AS month_name,
    WEEKOFYEAR(full_date)                                            AS week_of_year,
    (full_date BETWEEN '2020-03-01'::DATE AND '2021-06-30'::DATE)   AS is_covid_period,
    (full_date BETWEEN '2022-03-01'::DATE AND '2023-07-31'::DATE)   AS is_rate_hike_period
FROM date_spine
