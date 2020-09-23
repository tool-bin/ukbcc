import pytest
from ukbcc import db
import pandas as pd


def test_field_(main_csv, showcase_csv):
    main_df = pd.read_csv(main_csv, nrows=1)
    field_df = db.create_field_df(main_df, showcase_csv)
    
    exp_output = (
    "field_col,  field,  category,              ukb_type, sql_type, pd_type"
          "eid,    eid,        -1,               Integer,  INTEGER,   Int64"
    "21017-0.0,  21017,    100016,                  Text,  VARCHAR,  object"
    "41270-0.1,  41270,      2002,  Categorical, multiple,  VARCHAR,  object"
     "6070-0.0,   6070,    100016,    Categorical, single,  VARCHAR,  object"
     "6119-0.0,   6119,    100041,    Categorical, single,  VARCHAR,  object"
     "6148-0.1,   6148,    100041,  Categorical, multiple,  VARCHAR,  object"
     "6148-0.2,   6148,    100041,  Categorical, multiple,  VARCHAR,  object"
       "53-0.0,     53,    100024,                  Date,  NUMERIC,  object"
     "4286-0.0,   4286,    100031,                  Time,  NUMERIC,  object"
    "20137-0.0,  20137,       122,                  Time,  NUMERIC,  object"
    "21003-0.0,  21003,    100024,               Integer,  INTEGER,   Int64"
    "22182-0.0,  22182,    100035,              Compound,  VARCHAR,  object")
    

    assert 
