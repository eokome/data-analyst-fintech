# extract/tests/test_extract.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from extract_cfpb import hits_to_df, COLUMNS


def test_hits_to_df_maps_api_fields():
    hits = [{"complaint_id": "123", "product": "Mortgage", "state": "CA"}]
    df = hits_to_df(hits)
    assert list(df.columns) == COLUMNS
    assert df["COMPLAINT_ID"].iloc[0] == "123"
    assert df["PRODUCT"].iloc[0] == "Mortgage"
    assert df["STATE"].iloc[0] == "CA"


def test_hits_to_df_coerces_missing_to_empty_string():
    hits = [{"complaint_id": "456"}]
    df = hits_to_df(hits)
    assert df["PRODUCT"].iloc[0] == ""
    assert df["STATE"].iloc[0] == ""


def test_hits_to_df_coerces_none_to_empty_string():
    hits = [{"complaint_id": "789", "product": None, "state": None}]
    df = hits_to_df(hits)
    assert df["PRODUCT"].iloc[0] == ""
    assert df["STATE"].iloc[0] == ""
