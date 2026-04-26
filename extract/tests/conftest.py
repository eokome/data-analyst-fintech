import os
import sys
from unittest.mock import MagicMock

# Set dummy Snowflake env vars before extract_cfpb is imported
os.environ.setdefault("SNOWFLAKE_DATABASE", "TEST_DB")
os.environ.setdefault("SNOWFLAKE_SCHEMA", "TEST_SCHEMA")

# Mock snowflake.connector so extract_cfpb can be imported without the package installed
snowflake_mock = MagicMock()
sys.modules.setdefault("snowflake", snowflake_mock)
sys.modules.setdefault("snowflake.connector", snowflake_mock.connector)
sys.modules.setdefault("snowflake.connector.pandas_tools", snowflake_mock.connector.pandas_tools)
