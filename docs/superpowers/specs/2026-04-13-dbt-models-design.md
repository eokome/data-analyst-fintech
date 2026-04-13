# dbt Models Design

**Date:** 2026-04-13
**Project:** Financial Services Lead Gen Analytics
**Milestone:** 01 — Extract, Load & Transform (due Apr 27)

## Overview

Three-layer dbt project (staging → intermediate → mart) transforming raw CFPB complaint data loaded into Snowflake into a star schema for Streamlit dashboarding.

## Snowflake Setup

- **Database:** `FINTECH_DB` (to be created)
- **Schemas:**
  - `RAW` — Python extraction scripts load here
  - `STAGING` — dbt staging models (views)
  - `MART` — dbt mart models (tables)

## Folder Structure

```
dbt/
├── dbt_project.yml
├── profiles.yml              ← gitignored
├── packages.yml
├── models/
│   ├── staging/
│   │   ├── _sources.yml      ← declares RAW.COMPLAINTS as dbt source
│   │   ├── _staging.yml      ← staging tests
│   │   └── stg_complaints.sql
│   ├── intermediate/
│   │   ├── _intermediate.yml
│   │   └── int_complaints_enriched.sql
│   └── mart/
│       ├── _mart.yml         ← mart tests + relationships
│       ├── fct_complaints.sql
│       ├── dim_date.sql
│       ├── dim_product.sql
│       ├── dim_company.sql
│       ├── dim_geography.sql
│       └── dim_issue.sql
└── seeds/
```

## Materializations

| Layer | Type | Reason |
|---|---|---|
| staging | view | Always fresh, no storage cost |
| intermediate | view | Lightweight join/logic layer |
| mart | table | Streamlit queries these directly — needs to be fast |

## Models

### Staging — `stg_complaints.sql`

Reads from `RAW.COMPLAINTS`. Renames columns to snake_case, casts types, filters nulls on key fields. No business logic.

**Key transformations:**
- `complaint_id::INT`
- `date_received::DATE`
- `timely_response` → BOOLEAN
- `consumer_disputed` → BOOLEAN
- `has_narrative` → BOOLEAN
- Filter: `WHERE complaint_id IS NOT NULL`

### Intermediate — `int_complaints_enriched.sql`

Adds `product_category` — groups CFPB's 20+ product names into 4 clean buckets using a CASE statement:

| product_category | Includes |
|---|---|
| Lending | Mortgage, personal loan, payday loan, student loan, vehicle loan |
| Cards | Credit card, prepaid card |
| Banking | Checking account, savings account, money transfer |
| Debt | Debt collection, credit reporting, credit repair |

### Mart — Star Schema

**`fct_complaints`** — grain: one row per complaint

| Column | Type | Description |
|---|---|---|
| complaint_id | INT (PK) | Natural key from CFPB |
| date_key | INT (FK) | → dim_date |
| product_key | INT (FK) | → dim_product |
| company_key | INT (FK) | → dim_company |
| state_key | INT (FK) | → dim_geography |
| issue_key | INT (FK) | → dim_issue |
| submitted_via | VARCHAR | Web, phone, referral, etc. |
| timely_response | BOOLEAN | Company responded on time |
| consumer_disputed | BOOLEAN | Consumer pushed back |
| has_narrative | BOOLEAN | Consumer wrote description |
| company_response | VARCHAR | Closed w/ relief, explanation, etc. |

**`dim_date`** — grain: one row per calendar day

| Column | Type | Notes |
|---|---|---|
| date_key | INT (PK) | YYYYMMDD |
| full_date | DATE | |
| year | INT | |
| quarter | INT | |
| month | INT | |
| month_name | VARCHAR | |
| week_of_year | INT | |
| is_covid_period | BOOLEAN | 2020-03-01 to 2021-06-30 |
| is_rate_hike_period | BOOLEAN | 2022-03-01 to 2023-07-31 |

**`dim_product`** — grain: one row per product/sub_product combination

| Column | Type | Notes |
|---|---|---|
| product_key | INT (PK) | Surrogate key |
| product | VARCHAR | CFPB product name |
| sub_product | VARCHAR | CFPB sub-product name |
| product_category | VARCHAR | Derived: Lending, Cards, Banking, Debt |

**`dim_company`** — grain: one row per company

| Column | Type | Notes |
|---|---|---|
| company_key | INT (PK) | Surrogate key |
| company_name | VARCHAR | As reported in CFPB |

**`dim_geography`** — grain: one row per state

| Column | Type | Notes |
|---|---|---|
| state_key | INT (PK) | Surrogate key |
| state_abbrev | VARCHAR | CA, TX, FL, etc. |
| state_name | VARCHAR | Full name |
| region | VARCHAR | Northeast, South, Midwest, West |

**`dim_issue`** — grain: one row per issue/sub_issue combination

| Column | Type | Notes |
|---|---|---|
| issue_key | INT (PK) | Surrogate key |
| issue | VARCHAR | CFPB issue name |
| sub_issue | VARCHAR | CFPB sub-issue name |

## Tests

### Staging (`_staging.yml`)

| Column | Tests |
|---|---|
| complaint_id | not_null, unique |
| date_received | not_null |
| product | not_null |
| state | accepted_values (50 states + DC + PR) |
| timely_response | accepted_values (true, false) |

### Mart (`_mart.yml`)

| Model | Column | Tests |
|---|---|---|
| fct_complaints | complaint_id | not_null, unique |
| fct_complaints | date_key | not_null, relationships → dim_date.date_key |
| fct_complaints | product_key | not_null, relationships → dim_product.product_key |
| fct_complaints | company_key | not_null, relationships → dim_company.company_key |
| fct_complaints | state_key | not_null, relationships → dim_geography.state_key |
| fct_complaints | issue_key | not_null, relationships → dim_issue.issue_key |
| dim_date | date_key | not_null, unique |
| dim_product | product_key | not_null, unique |
| dim_company | company_key | not_null, unique |
| dim_geography | state_key | not_null, unique |
| dim_issue | issue_key | not_null, unique |

## Data Scope

- **Source:** CFPB Consumer Complaints API, filtered to `date_received >= 2020-01-01`
- **Estimated rows:** 3–4 million complaints
- **Update frequency:** Daily via GitHub Actions

## Grading Rubric Mapping

| Requirement | How it's met |
|---|---|
| At least one staging model per source | `stg_complaints.sql` |
| At least one fact + dimension table | `fct_complaints` + 5 dim tables |
| Star schema with relationships | FK columns in fct_complaints, `relationships` tests in `_mart.yml` |
| At least one dbt test passing | not_null + unique + relationships tests on all models |
| `dbt run` and `dbt test` execute without errors | All models tested before submission |
| Models materialized in Snowflake | Mart → tables, staging/intermediate → views |
