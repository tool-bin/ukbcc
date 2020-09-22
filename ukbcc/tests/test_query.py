import pytest
from ukbcc import query 

#def test_1_equals_to_2():
#    assert 1 == 2

def test_basic_query_creation(main_csv, gp_csv):
    cohort_criteria = {'all_of': [('6070', '1')], 'any_of': [], 'none_of': []}
    obs_query = query.create_queries(cohort_criteria,
                                   main_filename=main_csv,
                                   gpc_path=gp_csv)
    exp_query={'gp_clinical': {'all_of': '', 'any_of': '', 'none_of': ''}, 'main': {'all_of': "(t6070_0_0 == '1')", 'any_of': '', 'none_of': ''}}
    assert obs_query == exp_query

def test_query(main_csv, gp_csv):
    cohort_criteria = {'all_of': [('6070', "1")], 'any_of': [], 'none_of': []}
    gen_query = query.create_queries(cohort_criteria,
                                   main_filename=main_csv,
                                   gpc_path=gp_csv)
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set([1037918, 1041796, 1037058, 1024938, 1016017, 1038882, 1030520, 1003670, 1027017])
    assert exp_ids == ids
