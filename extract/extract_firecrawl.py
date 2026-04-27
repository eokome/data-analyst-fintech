#!/usr/bin/env python3
import os
import logging
from datetime import datetime, timezone

import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from firecrawl.v1 import V1FirecrawlApp as FirecrawlApp
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

URLS = [
    "https://www.epcvip.com",
    "https://www.consumerfinance.gov/about-us/newsroom/",
    "https://www.consumerfinance.gov/data-research/",
]

DATABASE = os.environ["SNOWFLAKE_DATABASE"]
SCHEMA   = os.environ["SNOWFLAKE_SCHEMA"]
TABLE    = "SCRAPED_CONTENT"

_CREATE_TABLE = f"""
CREATE TABLE IF NOT EXISTS {DATABASE}.{SCHEMA}.{TABLE} (
    URL        VARCHAR,
    TITLE      VARCHAR,
    MARKDOWN   VARCHAR,
    SCRAPED_AT TIMESTAMP_NTZ
)
"""


def main() -> None:
    firecrawl = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
    scraped_at = datetime.now(timezone.utc).replace(tzinfo=None)

    rows = []
    for url in URLS:
        log.info("Scraping %s", url)
        result = firecrawl.scrape_url(url, formats=["markdown"])
        title    = (result.metadata or {}).get("title") or ""
        markdown = result.markdown or ""
        rows.append({"URL": url, "TITLE": title, "MARKDOWN": markdown, "SCRAPED_AT": scraped_at})
        log.info("  %d chars, title: %s", len(markdown), title[:60])

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        role=os.environ.get("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )

    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {DATABASE}.{SCHEMA}")
    cur.execute(_CREATE_TABLE)
    cur.execute(f"DELETE FROM {DATABASE}.{SCHEMA}.{TABLE}")
    cur.close()

    df = pd.DataFrame(rows)
    write_pandas(conn, df, TABLE, database=DATABASE, schema=SCHEMA)
    log.info("Loaded %d rows into %s.%s.%s", len(df), DATABASE, SCHEMA, TABLE)

    conn.close()
    log.info("Done.")


if __name__ == "__main__":
    main()
