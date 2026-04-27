import os

import pandas as pd
import plotly.express as px
import snowflake.connector
import streamlit as st

st.set_page_config(page_title="CFPB Complaint Analytics", page_icon="📊", layout="wide")

S = "FINTECH_DB.MART"

JOINS = f"""
FROM {S}.FCT_COMPLAINTS f
LEFT JOIN {S}.DIM_DATE      dd ON dd.DATE_KEY    = f.DATE_KEY
LEFT JOIN {S}.DIM_PRODUCT   dp ON dp.PRODUCT_KEY = f.PRODUCT_KEY
LEFT JOIN {S}.DIM_COMPANY   dc ON dc.COMPANY_KEY = f.COMPANY_KEY
LEFT JOIN {S}.DIM_GEOGRAPHY dg ON dg.STATE_KEY   = f.STATE_KEY
"""


def _conn():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        role=os.environ["SNOWFLAKE_ROLE"],
        schema="MART",
    )


@st.cache_data(ttl=3600)
def run_query(sql: str) -> pd.DataFrame:
    conn = _conn()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetch_pandas_all()
    finally:
        conn.close()


def where_clause(categories: list, years: list, states: list) -> str:
    parts = []
    if categories:
        cats = ", ".join(f"'{c}'" for c in categories)
        parts.append(f"dp.PRODUCT_CATEGORY IN ({cats})")
    if years:
        yrs = ", ".join(str(y) for y in years)
        parts.append(f"dd.YEAR IN ({yrs})")
    if states:
        sts = ", ".join(f"'{s}'" for s in states)
        parts.append(f"dg.STATE_ABBREV IN ({sts})")
    return ("WHERE " + " AND ".join(parts)) if parts else ""


# ── Load filter options (cached, no user filters applied) ───────────────────
cat_opts = run_query(
    f"SELECT DISTINCT product_category FROM {S}.DIM_PRODUCT "
    f"WHERE product_category IS NOT NULL ORDER BY product_category"
)["PRODUCT_CATEGORY"].tolist()

year_opts = run_query(
    f"SELECT DISTINCT dd.year "
    f"FROM {S}.FCT_COMPLAINTS f "
    f"LEFT JOIN {S}.DIM_DATE dd ON dd.DATE_KEY = f.DATE_KEY "
    f"WHERE dd.year IS NOT NULL ORDER BY dd.year"
)["YEAR"].tolist()

state_opts = run_query(
    f"SELECT DISTINCT state_abbrev FROM {S}.DIM_GEOGRAPHY ORDER BY state_abbrev"
)["STATE_ABBREV"].tolist()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")
    sel_cats   = st.multiselect("Product Category", cat_opts,   default=cat_opts)
    sel_years  = st.multiselect("Year",             year_opts,  default=year_opts)
    sel_states = st.multiselect("State",            state_opts, default=state_opts)

# Skip filter clause when all options are selected (avoids bloated IN lists)
cats_filter   = sel_cats   if set(sel_cats)            != set(cat_opts)            else []
years_filter  = [int(y) for y in sel_years] if set(map(str, sel_years)) != set(map(str, year_opts)) else []
states_filter = sel_states if set(sel_states)          != set(state_opts)          else []
W = where_clause(cats_filter, years_filter, states_filter)

# ── KPIs ─────────────────────────────────────────────────────────────────────
kpi_df = run_query(f"""
    SELECT
        COUNT(f.complaint_id)                                                       AS total_complaints,
        ROUND(AVG(CASE WHEN f.consumer_disputed THEN 1.0 ELSE 0.0 END) * 100, 1)  AS pct_disputed,
        ROUND(AVG(CASE WHEN f.timely_response   THEN 1.0 ELSE 0.0 END) * 100, 1)  AS pct_timely
    {JOINS} {W}
""")

top_cat_df = run_query(f"""
    SELECT dp.product_category, COUNT(*) AS cnt
    {JOINS} {W}
    GROUP BY dp.product_category
    ORDER BY cnt DESC
    LIMIT 1
""")

total        = int(kpi_df["TOTAL_COMPLAINTS"].iloc[0])
pct_disputed = float(kpi_df["PCT_DISPUTED"].iloc[0])
pct_timely   = float(kpi_df["PCT_TIMELY"].iloc[0])
top_cat      = top_cat_df["PRODUCT_CATEGORY"].iloc[0] if not top_cat_df.empty else "N/A"

# ── Header ───────────────────────────────────────────────────────────────────
st.title("CFPB Consumer Complaint Analytics")
st.caption("EPCVIP Lead Generation Signal · Eliza Okome — ISBA 4715")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Complaints",       f"{total:,}")
k2.metric("% Consumer Disputed",    f"{pct_disputed}%")
k3.metric("% Timely Response",      f"{pct_timely}%")
k4.metric("Top Complaint Category", top_cat)

st.divider()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📈 Descriptive — What Happened?", "🔍 Diagnostic — Why Did It Happen?"])

# ──────── Descriptive ────────────────────────────────────────────────────────
with tab1:
    # Complaint volume over time (line)
    vol_df = run_query(f"""
        SELECT dd.year, dd.month, COUNT(*) AS complaint_count
        {JOINS} {W}
        GROUP BY dd.year, dd.month
        ORDER BY dd.year, dd.month
    """)
    vol_df["period"] = (
        vol_df["YEAR"].astype(str) + "-" + vol_df["MONTH"].astype(str).str.zfill(2)
    )
    fig_vol = px.line(
        vol_df, x="period", y="COMPLAINT_COUNT",
        title="Complaint Volume Over Time",
        labels={"period": "Month", "COMPLAINT_COUNT": "Complaints"},
        markers=True,
    )
    fig_vol.update_xaxes(tickangle=45)
    st.plotly_chart(fig_vol, use_container_width=True)

    col_a, col_b = st.columns(2)

    # Top 10 products (bar)
    with col_a:
        top10_df = run_query(f"""
            SELECT dp.product, COUNT(*) AS complaint_count
            {JOINS} {W}
            GROUP BY dp.product
            ORDER BY complaint_count DESC
            LIMIT 10
        """)
        fig_top10 = px.bar(
            top10_df, x="COMPLAINT_COUNT", y="PRODUCT", orientation="h",
            title="Top 10 Products by Complaint Count",
            labels={"COMPLAINT_COUNT": "Complaints", "PRODUCT": "Product"},
        )
        fig_top10.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_top10, use_container_width=True)

    # Complaints by state (choropleth)
    with col_b:
        state_df = run_query(f"""
            SELECT dg.state_abbrev, dg.state_name, COUNT(*) AS complaint_count
            {JOINS} {W}
            GROUP BY dg.state_abbrev, dg.state_name
            ORDER BY complaint_count DESC
        """)
        fig_state = px.choropleth(
            state_df,
            locations="STATE_ABBREV",
            locationmode="USA-states",
            color="COMPLAINT_COUNT",
            scope="usa",
            hover_name="STATE_NAME",
            color_continuous_scale="Blues",
            title="Complaints by State",
        )
        st.plotly_chart(fig_state, use_container_width=True)

# ──────── Diagnostic ─────────────────────────────────────────────────────────
with tab2:
    # Timely response rate — worst 20 companies (top offenders)
    timely_df = run_query(f"""
        SELECT
            dc.company_name,
            ROUND(AVG(CASE WHEN f.timely_response THEN 1.0 ELSE 0.0 END) * 100, 1) AS timely_rate,
            COUNT(*) AS complaint_count
        {JOINS} {W}
        GROUP BY dc.company_name
        HAVING COUNT(*) >= 10
        ORDER BY timely_rate ASC
        LIMIT 20
    """)
    fig_timely = px.bar(
        timely_df, x="TIMELY_RATE", y="COMPANY_NAME", orientation="h",
        title="Timely Response: Worst 20 Companies (≥10 complaints)",
        labels={"TIMELY_RATE": "Timely Response Rate (%)", "COMPANY_NAME": "Company"},
    )
    fig_timely.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_timely, use_container_width=True)

    # COVID vs Rate Hike period comparison
    period_df = run_query(f"""
        SELECT
            CASE
                WHEN dd.is_covid_period     THEN 'COVID Period (Mar 2020 – Jun 2021)'
                WHEN dd.is_rate_hike_period THEN 'Rate Hike Period (Mar 2022 – Jul 2023)'
                ELSE 'Other Period'
            END AS period,
            COUNT(*) AS complaint_count
        {JOINS} {W}
        GROUP BY 1
        ORDER BY complaint_count DESC
    """)
    fig_period = px.bar(
        period_df, x="PERIOD", y="COMPLAINT_COUNT",
        title="Complaint Volume by Economic Period",
        labels={"PERIOD": "Period", "COMPLAINT_COUNT": "Complaints"},
        color="PERIOD",
        color_discrete_map={
            "COVID Period (Mar 2020 – Jun 2021)":     "#E74C3C",
            "Rate Hike Period (Mar 2022 – Jul 2023)": "#F39C12",
            "Other Period":                            "#3498DB",
        },
    )
    fig_period.update_layout(showlegend=False)
    st.plotly_chart(fig_period, use_container_width=True)
