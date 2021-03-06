import pytest
from ukbcc import db 
import pandas as pd
from io import StringIO
import re

def test_create_query_tuples(field_desc):
    cohort_criteria = {'all_of': [('6070', '1')], 'any_of': [], 'none_of': []}
 
    query_tuples = db.create_query_tuples(cohort_criteria, field_desc)   
    exp_tuples=[{'field':'6070', 'val':'1', 'tab':'str'}]
    assert exp_tuples == query_tuples


def test_create_query_tuple_multiple(field_desc):
    cohort_criteria = {'all_of': [('6070', '1')], 'any_of': [("read_3", '229..')], 'none_of': [("21003", "55")]}
 
    query_tuples = db.create_query_tuples(cohort_criteria, field_desc)   

    exp_tuples=[{'field':'6070', 'val':'1', 'tab':'str'},{'field':'read_3', 'val':'229..', 'tab':'str'}, {'field':'21003', 'val':'55', 'tab':'int'}]

    assert all([x in exp_tuples for x in query_tuples])


def test_table_queries(field_desc):
    
    query_tuples = [{'field':'6070', 'val':'1', 'tab':'str'},{'field':'read_3', 'val':'229..', 'tab':'str'}, {'field':'21003', 'val':'55', 'tab':'int'}]
    obs_query = db.tab_select('str', query_tuples, field_desc)
    exp_query = "select * from str where field='6070' and value ='1' or field='read_3' and value ='229..'"
    assert obs_query == exp_query

    obs_query = db.tab_select('int', query_tuples, field_desc)
    exp_query = "select * from int where field='21003' and value =55"
    print(exp_query)
    print(obs_query)
    assert obs_query == exp_query


def test_table_queries_with_null(field_desc):
    
    query_tuples = [{'field':'6070', 'val':'1', 'tab':'str'},{'field':'read_3', 'val':'229..', 'tab':'str'}, {'field':'21003', 'val':'nan', 'tab':'int'}]
    obs_query = db.tab_select('str', query_tuples, field_desc)
    exp_query = "select * from str where field='6070' and value ='1' or field='read_3' and value ='229..'"
    assert obs_query == exp_query

    obs_query = db.tab_select('int', query_tuples, field_desc)
    exp_query = "select * from int where field='21003' and value is not NULL"
    print(exp_query)
    print(obs_query)
    assert obs_query == exp_query


#Functional - actually call to db
def test_table_queries_on_db(field_desc, sqlite_db):
    
    query_tuples = [{'field':'6070', 'val':'1', 'tab':'str'},{'field':'read_3', 'val':'229..', 'tab':'str'}, {'field':'21003', 'val':'55', 'tab':'int'}]
    obs_res = sqlite_db.execute(db.tab_select('str', query_tuples, field_desc)).fetchall()
    assert len(obs_res)==9

    obs_res = sqlite_db.execute(db.tab_select('int', query_tuples, field_desc)).fetchall()
    assert len(obs_res)==4


#Functional - actually call to db
def test_table_queries_with_null_on_db(field_desc, sqlite_db):
    
    query_tuples = [{'field':'6070', 'val':'1', 'tab':'str'},{'field':'read_3', 'val':'229..', 'tab':'str'}, {'field':'21003', 'val':'nan', 'tab':'int'}]
    obs_res = sqlite_db.execute(db.tab_select('str', query_tuples, field_desc)).fetchall()
    assert len(obs_res)==9

    obs_res = sqlite_db.execute(db.tab_select('int', query_tuples, field_desc)).fetchall()
    assert len(obs_res)==13


# Test the tuple queries work when we stick them together
def test_unify_queries(field_desc):
    query_tuples = [{'field':'6070', 'val':'1', 'tab':'str'},{'field':'read_3', 'val':'229..', 'tab':'str'}, {'field':'21003', 'val':'nan', 'tab':'int'}]
    obs_query = db.unify_query_tuples(query_tuples, field_desc)
    exp_query = "(select * from str where field='6070' and value ='1' or field='read_3' and value ='229..' union select * from int where field='21003' and value is not NULL)"
    assert obs_query == exp_query


# 
def test_expand_query(field_desc):
    field="6148"
    obs = db.expand_field(field, field_desc)
    exp = [['6148', '0', '1'], ['6148', '0', '2']]
    assert obs == exp


# 
def test_generate_main_column_queries(field_desc):
    field_sql_map = {'6148': 'VARCHAR', 
                     '21003': 'INTEGER', 
                     'read_3': 'VARCHAR', 
                     '6070': 'VARCHAR'}
    
    field="6148"
    obs = db.generate_main_column_queries(field, field_desc,field_sql_map)
    exp = ["cast(max(distinct case when field='6148' and time='0' and array='1' then value end) as VARCHAR) as 'f6148-0.1'",
           "cast(max(distinct case when field='6148' and time='0' and array='2' then value end) as VARCHAR) as 'f6148-0.2'"]
    assert obs == exp


#
def test_pivot_results(field_desc):
    query_tuples = [{'field':'6148', 'val':'1', 'tab':'str'}]
    obs = db.pivot_results(field_desc, query_tuples)
    exp = "cast(max(distinct case when field='6148' and time='0' and array='1' then value end) as VARCHAR) as 'f6148-0.1',cast(max(distinct case when field='6148' and time='0' and array='2' then value end) as VARCHAR) as 'f6148-0.2'"
    print(obs)
    print(exp)
    assert obs == exp


#
def test_pivot_results_read3(field_desc):
    query_tuples = [{'field':'read_3', 'val':'229..', 'tab':'str'}]
    obs = db.pivot_results(field_desc, query_tuples)
    exp = "cast(max(distinct case when field='read_3' and value='229..' then value end) as VARCHAR) as 'fread_3-229..'"
    print(obs)
    print(exp)
    assert obs == exp


def test_selection_criteria_query( field_desc ):
    cohort_criteria = {'all_of': [('6070', '1')], 'any_of': [('6148', '4')], 'none_of': []}
    obs=db.filter_pivoted_results(cohort_criteria, field_desc)
    exp='("f6070-0.0" ="1") AND (("f6148-0.1" ="4" OR "f6148-0.2" ="4"))'
    assert obs==exp


def test_selection_criteria_query2( field_desc ):
    cohort_criteria = {'all_of': [('6148', '4')], 'any_of': [('6070', '1')], 'none_of': []}
    obs=db.filter_pivoted_results(cohort_criteria, field_desc)
    exp='("f6148-0.1" ="4" OR "f6148-0.2" ="4") AND (("f6070-0.0" ="1"))'
    assert obs==exp

# 
# 
# #23/9/20
# # This doesn't current work as I need to port over all pandas queries to use sqlite
# #
# #
# 

#Check all of with a single field works
def test_db_all_query_basic(sqlite_db):
    cohort_criteria = {'all_of': [('6070', "1")], 'any_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)
    exp_ids = set([1041796, 1037058, 1024938, 1016017, 1038882, 1030520, 1003670, 1027017])

    print("df['eid']:{}".format(obs['eid'].tolist()))
    print("set(obs): {}".format(set(obs['eid'].tolist())))
    print(exp_ids)

    assert exp_ids == set(obs['eid'].tolist())


#Check that "all of" works over fields with multiple columns
def test_db_all_multiple_columns(sqlite_db):
    cohort_criteria = {'all_of': [('6148', "4")], 'any_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)
    
    exp_ids = set([1037918,  1033149,  1016017,  1033388,  1030520,  1003670])
    assert exp_ids == set(obs['eid'].tolist())


#Check any of with a single field works
def test_db_any_singleton_query(sqlite_db):
    cohort_criteria = {'any_of': [('6070', "1")], 'all_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1041796, 1037058, 1024938, 1016017, 1038882, 1030520, 1003670, 1027017])
    assert exp_ids == set(obs['eid'].tolist())
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)#Check that any of works over fields with multiple columns

def test_db_any_multiple_columns(sqlite_db):
    cohort_criteria = {'any_of': [('6148', "4")], 'all_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1037918,  1033149,  1016017,  1033388,  1030520,  1003670])
    assert exp_ids == set(obs['eid'].tolist())


#Check any of with two values for the same field returns their union
def test_db_any_pair_same_field_query(sqlite_db):
    cohort_criteria = {'any_of': [('6070', "1"), ('6070', "2")], 'all_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1037918, 1041796, 1037058, 1024938, 1016017, 1038882, 1030520, 1003670, 1027017])
    assert exp_ids == set(obs['eid'].tolist())


#Check any of with two fields returns their union
def test_db_any_pair_diff_field_query(sqlite_db):
    cohort_criteria = {'any_of': [('6070', "1"), ('6119', "1")], 'all_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1041796, 1037058, 1024938, 1016017, 1038882, 1030520, 1003670, 1027017])
    assert exp_ids == set(obs['eid'].tolist())


# Check if a none only query returns values
def test_db_none_basic(sqlite_db):
    cohort_criteria = {'none_of': [('6070', "1")], 'all_of': [], 'any_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1037918,  1033149,  1033388,  1031625,  1031595,  1008947])
    assert exp_ids == set(obs['eid'].tolist())


#Check that "all of" and "none_of" works over fields with multiple columns
def test_db_all__none_multiple_columns(sqlite_db):
    cohort_criteria = {'all_of': [('6148', "4")], 'any_of': [], 'none_of': [("6070", "2")]}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([ 1033149,  1016017,  1033388,  1030520,  1003670])
    assert exp_ids == set(obs['eid'].tolist())


#Check that "none_of" returns empty fields. 
def test_db_none_returns_empty(sqlite_db):
    cohort_criteria = {'all_of': [('6148', "4")], 'any_of': [], 'none_of': [("6070", "2"), ("6070", "1")]}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1033149,  1033388])
    assert exp_ids == set(obs['eid'].tolist())



#Check fields with spaces
def test_db_fields_with_spaces(sqlite_db):
    cohort_criteria = {'all_of': [('41270', "Block H40-H42")], 'any_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1033149,  1041796])
    assert exp_ids == set(obs['eid'].tolist())


#What do we do with fields that don't exist -raise an ValueError exception
def test_db_missing_fields2(sqlite_db):
    cohort_criteria = {'all_of': [('DoesNotExist', "X")], 'any_of': [], 'none_of': []}
    with pytest.raises(ValueError, match=r"DoesNotExist .*"):
        obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    

#What do we do when we query nan?
def test_db_missing_fields(sqlite_db):
    cohort_criteria = {'all_of': [('6070', "nan")], 'any_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1003670, 1016017, 1024938, 1027017, 1030520, 1037058, 1037918, 1038882 ,1041796])
    assert exp_ids == set(obs['eid'].tolist())


#Can we do a query on read2 at all?
def test_db_all_gp_clinical_read2(sqlite_db): 
    cohort_criteria = {'all_of': [('read_2', "4662.")], 'any_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1041796])
    assert exp_ids == set(obs['eid'].tolist())


#Can we read read2 when multiple entries per person
def test_db_all_gp_clinical_read_2_multiple(sqlite_db): 
    cohort_criteria = {'all_of': [('read_2', "XE0of")], 'any_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1016017])
    assert exp_ids == set(obs['eid'].tolist())


#Can we read read3
def test_db_all_gp_clinical_read_3(sqlite_db): 
    cohort_criteria = {'all_of': [('read_3', "XE0Gu")], 'any_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1037918])
    assert exp_ids == set(obs['eid'].tolist())

#Can we query 2 and 3?
def test_db_all_gp_clinical_read2and3(sqlite_db): 
    cohort_criteria = {'all_of': [], 'any_of': [('read_2', "XE0of"), ('read_3', 'XE0Gu')],  'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1016017, 1037918])
    assert exp_ids == set(obs['eid'].tolist())


#Complex query, use gp_clinical and main, and use all, not and any
def test_db_any_pair_same_field_query(sqlite_db):
    cohort_criteria = {'any_of': [('41270', "Block H40-H42"), ('6119', "3"), ('6148','4')], 'all_of': [(('6070', "1"))], 'none_of': [('read_2', "XE0of")]}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([1041796, 1037058,  1030520,  1003670])
    assert exp_ids == set(obs['eid'].tolist())

#Empty query
def test_db_empty_query(sqlite_db):
    cohort_criteria = {'any_of': [], 'all_of': [], 'none_of': []}
    obs=db.query_sqlite_db(con=sqlite_db, cohort_criteria=cohort_criteria)    
    exp_ids = set([])
    assert exp_ids == set(obs['eid'].tolist())
