import pytest
from ukbcc import db
# from ukbcc.tests import conftest as cf
import pandas as pd
from io import StringIO
import re
from pandas._testing import assert_frame_equal
import numpy as np
import sqlite3


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
     'CREATE TABLE str (eid INTEGER,field VARCHAR,time INTEGER,array INTEGER,value VARCHAR) ;',
     'DROP TABLE IF EXISTS int;',
     'CREATE TABLE int (eid INTEGER,field VARCHAR,time INTEGER,array INTEGER,value INTEGER) ;',
     'DROP TABLE IF EXISTS real;',
     'CREATE TABLE real (eid INTEGER,field VARCHAR,time INTEGER,array INTEGER,value REAL) ;',
     'DROP TABLE IF EXISTS datetime;',
     'CREATE TABLE datetime (eid INTEGER,field VARCHAR,time INTEGER,array INTEGER,value REAL) ;'
    ]
    assert tab_create_queries  == exp_output


def test_tab_creation(tmpdir):
    db_filename = str(tmpdir.mkdir("sqlite").join("db.sqlite"))
    con = sqlite3.connect(database=db_filename)
    queries = [
     'DROP TABLE IF EXISTS str;',
     'CREATE TABLE str (eid INTEGER,field VARCHAR,time INTEGER, array INTEGER,value VARCHAR) ;',
     'DROP TABLE IF EXISTS int;',
     'CREATE TABLE int (eid INTEGER,field VARCHAR,time INTEGER, array INTEGER,value INTEGER) ;']
    con.executescript("".join(queries))
    con.commit()
    tabs=con.execute("select name from sqlite_master where type = 'table';").fetchall()
    exp_tabs=set(["int", "str"])
    assert set([x[0] for x in tabs]) == exp_tabs


def test_tab_fields_map():
    field_desc = pd.read_csv(StringIO(re.sub('[ \t][ \t]+', ',', (
    "field_col  field  category             ukb_type  sql_type  pd_type\n"
         "eid     eid       -1               Integer  INTEGER   Int64\n"
   "21017-0.0   21017   100016                  Text  VARCHAR  object\n"
      "53-0.0      53   100024                  Date  NUMERIC  object\n"
    "4286-0.0    4286   100031                  Time  NUMERIC  object\n"
   "21003-0.0   21003   100024               Integer  INTEGER   Int64\n"
   "22182-0.0   22182   100035              Compound  VARCHAR  object\n"
      "50-0.0      50   100010            Continuous     REAL   float\n"
      "read_3  read_3   read_3  Categorical multiple  VARCHAR  object\n"
    ))))
    tabs = {'str': 'VARCHAR', 'int': 'INTEGER', 'real': 'REAL', 'datetime': 'REAL'}
    tab_fields = db.create_tab_fields_map(tabs, field_desc)

    exp_output={'str': ['21017-0.0', '22182-0.0', 'read_3'], 'int': ['21003-0.0'], 'real': ['50-0.0'], 'datetime': ['53-0.0', '4286-0.0']}
    assert tab_fields == exp_output


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
    tab_fields = {'str': ['21017-0.0', '41270-0.1', '6070-0.0', '22182-0.0', 'read_3'], 'int': ['21003-0.0'], 'real': ['50-0.0'], 'datetime': ['53-0.0', '4286-0.0']}

    field_desc=db.add_tabs_to_field_desc(field_desc, tab_fields)

    exp_field_desc = pd.read_csv(StringIO(re.sub('[ \t][ \t]+', ',',
    "field_col   field  category             ukb_type  sql_type  pd_type    tab\n"
          "eid     eid       -1               Integer  INTEGER   Int64      None\n"
    "21017-0.0   21017   100016                  Text  VARCHAR  object       str\n"
    "41270-0.1   41270     2002  Categorical multiple  VARCHAR  object       str\n"
     "6070-0.0    6070   100016    Categorical single  VARCHAR  object       str\n"
       "53-0.0      53   100024                  Date  NUMERIC  object  datetime\n"
     "4286-0.0    4286   100031                  Time  NUMERIC  object  datetime\n"
    "21003-0.0   21003   100024               Integer  INTEGER   Int64       int\n"
    "22182-0.0   22182   100035              Compound  VARCHAR  object       str\n"
       "50-0.0      50   100010            Continuous     REAL   float      real\n"
       "read_3  read_3   read_3  Categorical multiple  VARCHAR  object       str\n"
    )))
    exp_field_desc['tab'].iloc[0]=None

    assert_frame_equal(field_desc, exp_field_desc)

def test_create_query_tuples(field_desc, cohort_criteria):
    # cohort_criteria = {'all_of': [], 'any_of': [['21017', '1263']], 'none_of': []}
    exp_query_tuples = [{'field': '21017', 'val': '1263', 'tab': 'str'}]
    query_tuples = db.create_query_tuples(cohort_criteria, field_desc)
    assert query_tuples == exp_query_tuples

def test_unify_query_tuples(field_desc, query_tuples):
    exp_union_str = "(select * from str where field='21017' and value ='1263')"
    union_str = db.unify_query_tuples(query_tuples, field_desc)
    assert union_str == exp_union_str

def test_pivot_results(field_desc, query_tuples):
    exp_pivot_queries = "cast(max(distinct case when field='21017' and time='0' and array='0' then value end) as VARCHAR) as 'f21017-0.0'"
    pivot_query = db.pivot_results(field_desc, query_tuples)
    assert exp_pivot_queries == pivot_query

def test_filter_pivot_results(field_desc):
    main_criteria = {'all_of': [], 'any_of': [('21017', '1263')], 'none_of': []}
    exp_selection_query = '(("f21017-0.0" ="1263"))'
    selection_query = db.filter_pivoted_results(main_criteria, field_desc)
    assert exp_selection_query == selection_query


#Compute number of lines over a small file
def test_line_estimate(main_csv):
    obs_nlines = db.estimate_line_count(main_csv)
    exp_nlines = 15
    assert exp_nlines == obs_nlines



def test_db_create(sqlite_db):#main_csv, showcase_csv, gp_csv, tmpdir):
    #db_file = str(tmpdir.mkdir("sqlite").join("db.sqlite"))
    #con = db.create_sqlite_db(db_filename=db_file,
    #                 main_filename=main_csv,
    #                 gp_clin_filename = gp_csv,
    #                 showcase_file = showcase_csv,
    #                 step=2)
    con = sqlite_db
    #Check we've created the right tables
    tabs=con.execute("select name from sqlite_master where type = 'table';").fetchall()
    exp_tabs=set(["int", "str", "real", "datetime", "field_desc"])
    assert set([x[0] for x in tabs]) == exp_tabs

    #Check some main dataset fields exist
    vals_6148 = con.execute("select * from str where field='6148'").fetchall()
    assert len(vals_6148)==16

    vals_4286 = con.execute("select * from datetime where field='4286'").fetchall()
    assert len(vals_4286)==8

    #Check some gp_clinical fields exist
    vals_read_3 = con.execute("select * from str where field='read_3'").fetchall()
    assert len(vals_read_3)==3

    #Check some gp_clinical fields exist
    vals_read_2 = con.execute("select * from str where field='read_2'").fetchall()
    assert len(vals_read_2)==3
    


def test_db_main_insert(main_csv):
    dtypes_dict = {
         'eid': 'Int64',
         '21017-0.0': 'object',
         '41270-0.1': 'object',
         '6070-0.0': 'object',
         '53-0.0': 'object',
         '4286-0.0': 'object',
         '21003-0.0': 'Int64',
         '22182-0.0': 'object',
         '50-0.0': 'float',
         'read_3': 'object'
    }
    date_cols = ['53-0.0', '4286-0.0']
    main_df = pd.read_csv(main_csv, low_memory=False, encoding="ISO-8859-1", dtype=dtypes_dict, parse_dates=date_cols)
    query=db.insert_main_chunk(main_df, tab_name="datetime", tab_fields=['53-0.0', '4286-0.0'])
    print(query)
