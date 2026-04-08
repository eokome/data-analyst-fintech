# Project Proposal Design

**Date:** 2026-04-08
**Course:** ISBA 4715
**Student:** Eliza Okome

## Overview

End-to-end marketing analytics pipeline targeting a Junior Data Analyst role in the financial services lead generation industry.

## Job Posting

- **Role:** Junior Data Analyst
- **Company:** EPCVIP, Inc (lead generation company specializing in financial services digital advertising)
- **SQL mention:** "Google Analytics, SQL, or data visualization certifications are a plus."

## Project Framing

**Financial Services Lead Gen Analytics** — a pipeline that ingests consumer complaint data from the Consumer Financial Protection Bureau's public REST API, transforms it through Snowflake using dbt (a tool that uses SQL to clean and organize raw data into analysis-ready tables), and surfaces campaign targeting insights via a deployed Streamlit dashboard.

### Why This Works

The Consumer Financial Protection Bureau complaint database reveals which financial products and geographies have the highest consumer dissatisfaction — exactly the demand signal a lead gen analyst uses to identify where consumers are actively seeking alternatives and where campaigns should be focused.

## Data Sources

- **API (Source 1):** Consumer Financial Protection Bureau Complaint Database REST API — free, public, no auth required, scheduled via GitHub Actions
- **Web Scrape (Source 2):** Financial services marketing content — company websites, fintech blogs, industry reports, Consumer Financial Protection Bureau consumer education pages

## Star Schema Design

- `fact_complaints` — one row per complaint (volume, resolution status, timely response)
- `dim_product` — financial product type (loan, credit card, mortgage, etc.)
- `dim_company` — financial institution receiving the complaint
- `dim_state` — U.S. state geography
- `dim_date` — date submitted, date resolved

## Dashboard Angles

- **Descriptive:** Which financial products receive the most complaints? Which states?
- **Diagnostic:** Are complaint volumes trending up or down by product category? Which companies are improving or declining?
- **Interactive:** Filter by product type, state, date range

## Knowledge Base

Scraped sources from 3+ sites covering:
- EPCVIP and financial services lead gen industry context
- Consumer Financial Protection Bureau consumer education and regulatory content
- Fintech marketing industry publications

## Transferability

This project speaks directly to:
1. Marketing Data Analyst roles at fintech companies
2. Business Intelligence Analyst roles at banks or financial services firms
3. Reporting Analyst roles focused on campaign performance

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake |
| Transformation | dbt (data build tool) — writes SQL to clean raw data and build analysis-ready tables in Snowflake, organized in the right order and tested for accuracy |
| Orchestration | GitHub Actions |
| Dashboard | Streamlit (deployed) |
| Knowledge Base | Claude Code |

## GitHub Repo

- **New name:** `data-analyst-fintech`
- **URL:** https://github.com/eokome/data-analyst-fintech
