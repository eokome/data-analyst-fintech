# CLAUDE.md — Financial Services Lead Gen Analytics

## Project Overview

**Student:** Eliza Okome
**Course:** ISBA 4715 — Analytics Engineering
**Repo:** https://github.com/eokome/data-analyst-fintech

This is a portfolio capstone project targeting a Junior Data Analyst role at EPCVIP, Inc. — a lead generation company serving financial services clients. The project demonstrates end-to-end analytics engineering skills: data extraction, Snowflake loading, dbt transformation, and Streamlit dashboarding.

**Business question:** Which financial products and markets have the highest consumer dissatisfaction (as measured by CFPB complaints), and how can a lead generation company use that signal to guide campaign targeting?

## Target Job Posting

- **Role:** Junior Data Analyst at EPCVIP, Inc.
- **PDF:** `docs/job-posting.pdf`
- **Key skills required:** SQL, data pipelines, dashboards, campaign performance monitoring, data accuracy

## Data Sources

| Source | Type | Purpose |
|---|---|---|
| CFPB Consumer Complaints API | REST API (required) | Structured data → Snowflake → dbt → dashboard |
| Web scrape (TBD in Milestone 01) | Web scrape (required) | Unstructured sources → knowledge base |

## Tech Stack

| Layer | Tool |
|---|---|
| Data Warehouse | Snowflake (AWS US East 1) |
| Transformation | dbt |
| Orchestration | GitHub Actions (scheduled) |
| Dashboard | Streamlit (deployed to Streamlit Community Cloud) |
| AI Development | Claude Code + Superpowers |
| Version Control | Git + GitHub (public repo) |

## Directory Structure

```
data-analyst-fintech/
├── docs/                   # Proposal, job posting, resume
├── extract/                # Python extraction scripts (API + scrape)
├── dbt/                    # dbt project (staging + mart models)
├── dashboard/              # Streamlit app
├── knowledge/
│   ├── raw/                # Scraped sources (15+ files, 3+ sites)
│   ├── wiki/               # Claude Code-generated synthesis pages
│   └── index.md            # Index of all wiki pages with summaries
├── .github/workflows/      # GitHub Actions pipelines
├── .gitignore
├── CLAUDE.md               # This file
└── README.md               # Project overview, ERD, pipeline diagram
```

## Security Rules

- Never commit credentials, passwords, or API keys
- All secrets go in `.env` (gitignored) and GitHub Actions secrets
- `profiles.yml` (dbt Snowflake credentials) is gitignored

## Milestones

| Milestone | Due | Status |
|---|---|---|
| Proposal | Apr 13 | In progress |
| Milestone 01: Extract, Load & Transform | Apr 27 | Not started |
| Milestone 02: Present & Polish | May 4 | Not started |
| Final Submission + Interview | May 11 | Not started |

## Knowledge Base Conventions

When answering questions about the knowledge base, follow these conventions:

1. **Always read `knowledge/index.md` first** to understand what wiki pages exist before answering.
2. **Prefer wiki pages over raw sources** for synthesized answers. Wiki pages are in `knowledge/wiki/` and represent synthesized, cross-source insights.
3. **Cite your sources.** When answering from wiki pages, note which wiki page the insight came from. When answering from raw sources, note the file path.
4. **Be honest about gaps.** If the knowledge base doesn't contain enough information to answer a question, say so and suggest what sources might fill the gap.
5. **Raw sources** are in `knowledge/raw/` and represent unprocessed scraped content. Use them to verify or supplement wiki page answers.
6. **Query pattern:** "What does the knowledge base say about X?" → read `knowledge/index.md`, identify relevant wiki pages, read them, then synthesize an answer.
