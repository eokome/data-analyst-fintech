#!/usr/bin/env python3
import os
import logging
from datetime import date, timedelta
from typing import Iterator

import requests
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CFPB_URL     = "https://api.consumerfinance.gov/data/complaints"
PAGE_SIZE    = 5000
INITIAL_DATE = date(2020, 1, 1)
FLUSH_AT     = 80_000  # rows to accumulate before writing to Snowflake

COLUMNS = [
    "COMPLAINT_ID", "DATE_RECEIVED", "PRODUCT", "SUB_PRODUCT",
    "ISSUE", "SUB_ISSUE", "CONSUMER_COMPLAINT_NARRATIVE",
    "COMPANY_PUBLIC_RESPONSE", "COMPANY", "STATE", "ZIP_CODE", "TAGS",
    "CONSUMER_CONSENT_PROVIDED", "SUBMITTED_VIA", "DATE_SENT_TO_COMPANY",
    "COMPANY_RESPONSE_TO_CONSUMER", "TIMELY_RESPONSE", "CONSUMER_DISPUTED",
]

_FIELD_MAP = {
    "COMPLAINT_ID":                 "complaint_id",
    "DATE_RECEIVED":                "date_received",
    "PRODUCT":                      "product",
    "SUB_PRODUCT":                  "sub_product",
    "ISSUE":                        "issue",
    "SUB_ISSUE":                    "sub_issue",
    "CONSUMER_COMPLAINT_NARRATIVE": "consumer_complaint_narrative",
    "COMPANY_PUBLIC_RESPONSE":      "company_public_response",
    "COMPANY":                      "company",
    "STATE":                        "state",
    "ZIP_CODE":                     "zip_code",
    "TAGS":                         "tags",
    "CONSUMER_CONSENT_PROVIDED":    "consumer_consent_provided",
    "SUBMITTED_VIA":                "submitted_via",
    "DATE_SENT_TO_COMPANY":         "date_sent_to_company",
    "COMPANY_RESPONSE_TO_CONSUMER": "company_response_to_consumer",
    "TIMELY_RESPONSE":              "timely_response",
    "CONSUMER_DISPUTED":            "consumer_disputed",
}

DATABASE = os.environ["SNOWFLAKE_DATABASE"]
SCHEMA   = os.environ["SNOWFLAKE_SCHEMA"]
TABLE    = "COMPLAINTS"

_CREATE_DB     = f"CREATE DATABASE IF NOT EXISTS {DATABASE}"
_CREATE_SCHEMA = f"CREATE SCHEMA IF NOT EXISTS {DATABASE}.{SCHEMA}"
_CREATE_TABLE  = f"""
CREATE TABLE IF NOT EXISTS {DATABASE}.{SCHEMA}.{TABLE} (
    COMPLAINT_ID                  VARCHAR,
    DATE_RECEIVED                 VARCHAR,
    PRODUCT                       VARCHAR,
    SUB_PRODUCT                   VARCHAR,
    ISSUE                         VARCHAR,
    SUB_ISSUE                     VARCHAR,
    CONSUMER_COMPLAINT_NARRATIVE  VARCHAR,
    COMPANY_PUBLIC_RESPONSE       VARCHAR,
    COMPANY                       VARCHAR,
    STATE                         VARCHAR,
    ZIP_CODE                      VARCHAR,
    TAGS                          VARCHAR,
    CONSUMER_CONSENT_PROVIDED     VARCHAR,
    SUBMITTED_VIA                 VARCHAR,
    DATE_SENT_TO_COMPANY          VARCHAR,
    COMPANY_RESPONSE_TO_CONSUMER  VARCHAR,
    TIMELY_RESPONSE               VARCHAR,
    CONSUMER_DISPUTED             VARCHAR
)
"""


def hits_to_df(hits: list[dict]) -> pd.DataFrame:
    rows = [
        {col: str(h.get(api_key) or "") for col, api_key in _FIELD_MAP.items()}
        for h in hits
    ]
    return pd.DataFrame(rows, columns=COLUMNS)


def _fetch_window(
    session: requests.Session, start: date, end: date
) -> Iterator[list[dict]]:
    frm = 0
    while True:
        params = {
            "date_received_min": str(start),
            "date_received_max": str(end),
            "size":              PAGE_SIZE,
            "frm":               frm,
            "format":            "json",
        }
        resp = session.get(CFPB_URL, params=params, timeout=60)
        resp.raise_for_status()
        hits = resp.json()["hits"]["hits"]
        if not hits:
            break
        yield [h["_source"] for h in hits]
        if len(hits) < PAGE_SIZE:
            break
        frm += PAGE_SIZE


def _get_load_start(conn: snowflake.connector.SnowflakeConnection) -> date:
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT MAX(DATE_RECEIVED) FROM {DATABASE}.{SCHEMA}.{TABLE}")
        row = cur.fetchone()
        if row and row[0]:
            return date.fromisoformat(str(row[0])) - timedelta(days=7)
        return INITIAL_DATE
    except Exception:
        return INITIAL_DATE
    finally:
        cur.close()


def _setup(conn: snowflake.connector.SnowflakeConnection) -> None:
    cur = conn.cursor()
    cur.execute(_CREATE_DB)
    cur.execute(_CREATE_SCHEMA)
    cur.execute(_CREATE_TABLE)
    cur.close()


def main() -> None:
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )
    _setup(conn)

    load_start = _get_load_start(conn)
    load_end   = date.today()
    log.info("Loading %s → %s", load_start, load_end)

    cur = conn.cursor()
    cur.execute(
        f"DELETE FROM {DATABASE}.{SCHEMA}.{TABLE} "
        f"WHERE DATE_RECEIVED >= '{load_start}' AND DATE_RECEIVED <= '{load_end}'"
    )
    cur.close()

    session = requests.Session()
    batch: list[dict] = []
    current = load_start

    while current <= load_end:
        for page in _fetch_window(session, current, current):
            batch.extend(page)
        if len(batch) >= FLUSH_AT or current == load_end:
            if batch:
                df = hits_to_df(batch)
                write_pandas(conn, df, TABLE, database=DATABASE, schema=SCHEMA)
                log.info("Flushed %s rows (through %s)", f"{len(df):,}", current)
                batch = []
        current += timedelta(days=1)

    conn.close()
    log.info("Done.")


if __name__ == "__main__":
    main()
