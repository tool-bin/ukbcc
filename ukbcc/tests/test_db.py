import pytest
from ukbcc import db
import pandas as pd
from io import StringIO
import re
from pandas._testing import assert_frame_equal
import numpy as np


# Confirm that we create a data structure for fields containing all relevant info
def test_field_desc(main_csv, showcase_csv):
    main_df = pd.read_csv(main_csv, nrows=1)
    field_desc = db.create_field_desc(main_df, showcase_csv)
    
    exp_output = pd.read_csv(StringIO(re.sub('[ \t][ \t]+', ',', (
    "field_col  field  category             ukb_type  sql_type  pd_type\n"
         "eid     eid       -1               Integer  INTEGER   Int64\n"
   "21017-0.0   21017   100016                  Text  VARCHAR  object\n"
   "41270-0.1   41270     2002  Categorical multiple  VARCHAR  object\n"
    "6070-0.0    6070   100016    Categorical single  VARCHAR  object\n"
    "6119-0.0    6119   100041    Categorical single  VARCHAR  object\n"
    "6148-0.1    6148   100041  Categorical multiple  VARCHAR  object\n"
    "6148-0.2    6148   100041  Categorical multiple  VARCHAR  object\n"
      "53-0.0      53   100024                  Date  NUMERIC  object\n"
    "4286-0.0    4286   100031                  Time  NUMERIC  object\n"
      "50-0.0      50   100010            Continuous     REAL   float\n"
   "21003-0.0   21003   100024               Integer  INTEGER   Int64\n"
   "22182-0.0   22182   100035              Compound  VARCHAR  object\n"
      "read_2  read_2   read_2  Categorical multiple  VARCHAR  object\n"
      "read_3  read_3   read_3  Categorical multiple  VARCHAR  object\n"
    ))))
    
    np.array_equal(exp_output, field_desc)


def test_tab_creation_queries(main_csv, showcase_csv):
    tabs = dict(zip(['str', 'int', 'real', 'datetime'], ["VARCHAR", "INTEGER", "REAL", "REAL"]))
    tab_create_queries = db.create_table_queries(tabs)

    exp_output = [
     'DROP TABLE IF EXISTS str;', 
     'CREATE TABLE str (eid INTEGER,field VARCHAR,time INTEGER,value VARCHAR) ;', 
     'DROP TABLE IF EXISTS int;',
     'CREATE TABLE int (eid INTEGER,field VARCHAR,time INTEGER,value INTEGER) ;', 
     'DROP TABLE IF EXISTS real;', 
     'CREATE TABLE real (eid INTEGER,field VARCHAR,time INTEGER,value REAL) ;', 
     'DROP TABLE IF EXISTS datetime;', 
     'CREATE TABLE datetime (eid INTEGER,field VARCHAR,time INTEGER,value REAL) ;'
    ]
    assert tab_create_queries  == exp_output


def test_tab_fields_map():
    field_desc = pd.read_csv(StringIO(re.sub('[ \t][ \t]+', ',', (
    "field_col  field  category             ukb_type  sql_type  pd_type\n"
         "eid     eid       -1               Integer  INTEGER   Int64\n"
   "21017-0.0   21017   100016                  Text  VARCHAR  object\n"
   "41270-0.1   41270     2002  Categorical multiple  VARCHAR  object\n"
    "6070-0.0    6070   100016    Categorical single  VARCHAR  object\n"
      "53-0.0      53   100024                  Date  NUMERIC  object\n"
    "4286-0.0    4286   100031                  Time  NUMERIC  object\n"
   "21003-0.0   21003   100024               Integer  INTEGER   Int64\n"
   "22182-0.0   22182   100035              Compound  VARCHAR  object\n"
      "50-0.0      50   100010            Continuous     REAL   float\n"
      "read_3  read_3   read_3  Categorical multiple  VARCHAR  object\n"
    ))))
    tabs = {'str': 'VARCHAR', 'int': 'INTEGER', 'real': 'REAL', 'datetime': 'REAL'}
    tab_fields = db.create_tab_fields_map(tabs, field_desc)

    exp_output={'str': ['21017-0.0', '41270-0.1', '6070-0.0', '22182-0.0', 'read_3'], 'int': ['21003-0.0'], 'real': ['50-0.0'], 'datetime': ['53-0.0', '4286-0.0']}
    assert {k:v.tolist() for k,v in tab_fields.items()} == exp_output
    
    
def test_add_tab_to_field_desc():
    field_desc = pd.read_csv(StringIO(re.sub('[ \t][ \t]+', ',', (
    "field_col  field  category             ukb_type  sql_type  pd_type\n"
         "eid     eid       -1               Integer  INTEGER   Int64\n"
   "21017-0.0   21017   100016                  Text  VARCHAR  object\n"
   "41270-0.1   41270     2002  Categorical multiple  VARCHAR  object\n"
    "6070-0.0    6070   100016    Categorical single  VARCHAR  object\n"
      "53-0.0      53   100024                  Date  NUMERIC  object\n"
    "4286-0.0    4286   100031                  Time  NUMERIC  object\n"
   "21003-0.0   21003   100024               Integer  INTEGER   Int64\n"
   "22182-0.0   22182   100035              Compound  VARCHAR  object\n"
      "50-0.0      50   100010            Continuous     REAL   float\n"
      "read_3  read_3   read_3  Categorical multiple  VARCHAR  object\n"
    ))))
    

    
    output=db.add_tabs_to_field_desc(field_desc, tab_fields)
    
    exp_output = pd.read_csv(StringIO(re.sub('[ \t][ \t]+', ',', (
    "field_col  field  category             ukb_type  sql_type  pd_type\n"
         "eid     eid       -1               Integer  INTEGER   Int64\n"
   "21017-0.0   21017   100016                  Text  VARCHAR  object\n"
   "41270-0.1   41270     2002  Categorical multiple  VARCHAR  object\n"
    "6070-0.0    6070   100016    Categorical single  VARCHAR  object\n"
    "6119-0.0    6119   100041    Categorical single  VARCHAR  object\n"
    "6148-0.1    6148   100041  Categorical multiple  VARCHAR  object\n"
    "6148-0.2    6148   100041  Categorical multiple  VARCHAR  object\n"
      "53-0.0      53   100024                  Date  NUMERIC  object\n"
    "4286-0.0    4286   100031                  Time  NUMERIC  object\n"
   "20137-0.0   20137      122                  Time  NUMERIC  object\n"
   "21003-0.0   21003   100024               Integer  INTEGER   Int64\n"
   "22182-0.0   22182   100035              Compound  VARCHAR  object\n"
      "read_2  read_2   read_2  Categorical multiple  VARCHAR  object\n"
      "read_3  read_3   read_3  Categorical multiple  VARCHAR  object\n"
    ))))
    
    np.array_equal(exp_output, field_desc)



#Compute number of lines over a small file
def test_line_estimate(main_csv):
    obs_nlines = db.estimate_line_count(main_csv)
    exp_nlines = 15
    assert exp_nlines == obs_nlines



def test_db_create(main_csv, showcase_csv, gp_csv, tmpdir):
    db_file = str(tmpdir.mkdir("sqlite").join("db.sqlite"))
    db.create_sqlite_db(db_filename=db_file, 
                     main_filename=main_csv, 
                     gp_clin_filename = gp_csv,
                     showcase_file = showcase_csv,
                     step=1)
    
        
        
