# Financial Services Lead Gen Analytics

**Course:** ISBA 4715 — Analytics Engineering &nbsp;|&nbsp; **Student:** Eliza Okome  
**Target Role:** Junior Data Analyst @ EPCVIP, Inc.

**Business Question:** Which financial products and markets have the highest consumer dissatisfaction (as measured by CFPB complaints), and how can a lead generation company use that signal to guide campaign targeting?

## Pipeline

```mermaid
flowchart LR
    A[CFPB Complaints API] -->|daily fetch| B[GitHub Actions]
    B -->|extract_cfpb.py| C[(Snowflake\nFINTECH_DB.RAW\nCOMPLAINTS)]
    C -->|dbt staging| D[(FINTECH_DB.STAGING\nstg_complaints)]
    D -->|dbt intermediate| E[(FINTECH_DB.STAGING\nint_complaints_enriched)]
    E -->|dbt mart| F[(FINTECH_DB.MART\nfct_complaints + 5 dims)]
    F -->|Streamlit query| G[Streamlit Dashboard]
```

## Star Schema (ERD)

```mermaid
erDiagram
    fct_complaints {
        int complaint_id PK
        int date_key FK
        int product_key FK
        int company_key FK
        int state_key FK
        int issue_key FK
        varchar submitted_via
        boolean timely_response
        boolean consumer_disputed
        boolean has_narrative
        varchar company_response
    }
    dim_date {
        int date_key PK
        date full_date
        int year
        int quarter
        int month
        varchar month_name
        int week_of_year
        boolean is_covid_period
        boolean is_rate_hike_period
    }
    dim_product {
        int product_key PK
        varchar product
        varchar sub_product
        varchar product_category
    }
    dim_company {
        int company_key PK
        varchar company_name
    }
    dim_geography {
        int state_key PK
        varchar state_abbrev
        varchar state_name
        varchar region
    }
    dim_issue {
        int issue_key PK
        varchar issue
        varchar sub_issue
    }
    fct_complaints ||--|| dim_date : "date_key"
    fct_complaints ||--|| dim_product : "product_key"
    fct_complaints ||--|| dim_company : "company_key"
    fct_complaints ||--|| dim_geography : "state_key"
    fct_complaints ||--|| dim_issue : "issue_key"
```

## Setup

### Prerequisites

- Python 3.11+
- Snowflake account
- `pip install dbt-snowflake`

### Local Development

1. Copy env template and fill in credentials:
   ```bash
   cp .env.example .env
   # edit .env with your Snowflake credentials
   ```

2. Install Python dependencies:
   ```bash
   pip install -r extract/requirements.txt
   ```

3. Run the extract:
   ```bash
   python extract/extract_cfpb.py
   ```

4. Run dbt (profiles.yml reads credentials from `.env` via `env_var()`):
   ```bash
   cd dbt
   dbt run --profiles-dir .
   dbt test --profiles-dir .
   ```

### GitHub Actions (CI/CD)

Add the following secrets in **GitHub → Settings → Secrets and variables → Actions**:

| Secret | Value |
|---|---|
| `SNOWFLAKE_ACCOUNT` | `VXBOMAL-QGC80885` |
| `SNOWFLAKE_USER` | your Snowflake username |
| `SNOWFLAKE_PASSWORD` | your Snowflake password |
| `SNOWFLAKE_WAREHOUSE` | `COMPUTE_WH` |
| `SNOWFLAKE_DATABASE` | `FINTECH_DB` |
| `SNOWFLAKE_ROLE` | `ACCOUNTADMIN` |

The workflow runs daily at 6:00 AM UTC and can be triggered manually from the **Actions** tab.

## Data Source

**CFPB Consumer Complaints Database**  
- API: `https://api.consumerfinance.gov/data/complaints`  
- Date range: 2020-01-01 to present  
- Estimated volume: 3–4 million complaints

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake (AWS US East 1) |
| Transformation | dbt-snowflake |
| Orchestration | GitHub Actions |
| Dashboard | Streamlit (Milestone 02) |
| Version Control | Git + GitHub |
