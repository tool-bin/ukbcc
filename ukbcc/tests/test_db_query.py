import pytest
from ukbcc import query 

#23/9/20
# This doesn't current work as I need to port over all pandas queries to use sqlite
#
#

def test_db_basic_query_creation(sqlite_db):
    cohort_criteria = {'all_of': [('6070', '1')], 'any_of': [], 'none_of': []}
    obs_query = query.create_queries(cohort_criteria,
                                   main_filename=main_csv,
                                   gpc_path=gp_csv)
    exp_query={'gp_clinical': {'all_of': '', 'any_of': '', 'none_of': ''}, 'main': {'all_of': "(t6070_0_0 == '1')", 'any_of': '', 'none_of': ''}}
    assert obs_query == exp_query

#Check all of with a single field works
def test_db_all_query_basic(sqlite_db):
    cohort_criteria = {'all_of': [('6070', "1")], 'any_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1041796", "1037058", "1024938", "1016017", "1038882", "1030520", "1003670", "1027017"])
    assert exp_ids == set(ids)


#Check that "all of" works over fields with multiple columns
def test_db_all_multiple_columns(sqlite_db):
    cohort_criteria = {'all_of': [('6148', "4")], 'any_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1037918",  "1033149",  "1016017",  "1033388",  "1030520",  "1003670"])
    assert exp_ids == set(ids)


#Check any of with a single field works
def test_db_any_singleton_query(sqlite_db):
    cohort_criteria = {'any_of': [('6070', "1")], 'all_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1041796", "1037058", "1024938", "1016017", "1038882", "1030520", "1003670", "1027017"])
    assert exp_ids == set(ids)




#Check that any of works over fields with multiple columns
def test_db_any_multiple_columns(sqlite_db):
    cohort_criteria = {'any_of': [('6148', "4")], 'all_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1037918",  "1033149",  "1016017",  "1033388",  "1030520",  "1003670"])
    assert exp_ids == set(ids)


#Check any of with two values for the same field returns their union
def test_db_any_pair_same_field_query(sqlite_db):
    cohort_criteria = {'any_of': [('6070', "1"), ('6070', "2")], 'all_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1037918", "1041796", "1037058", "1024938", "1016017", "1038882", "1030520", "1003670", "1027017"])
    assert exp_ids == set(ids)


#Check any of with two fields returns their union
def test_db_any_pair_diff_field_query(sqlite_db):
    cohort_criteria = {'any_of': [('6070', "1"), ('6119', "1")], 'all_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1041796", "1037058", "1024938", "1016017", "1038882", "1030520", "1003670", "1027017"])
    assert exp_ids == set(ids)


# Check if a none only query returns values
def test_db_none_basic(sqlite_db):
    cohort_criteria = {'none_of': [('6070', "1")], 'all_of': [], 'any_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    print(ids)
    exp_ids = set(["1037918",  "1033149",  "1033388",  "1031625",  "1031595",  "1008947"])
    assert exp_ids == set(ids)


#Check that "all of" and "none_of" works over fields with multiple columns
def test_db_all__none_multiple_columns(sqlite_db):
    cohort_criteria = {'all_of': [('6148', "4")], 'any_of': [], 'none_of': [("6070", "2")]}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set([ "1033149",  "1016017",  "1033388",  "1030520",  "1003670"])
    assert exp_ids == set(ids)


#Check that "none_of" returns empty fields. 
def test_db_none_returns_empty(sqlite_db):
    cohort_criteria = {'all_of': [('6148', "4")], 'any_of': [], 'none_of': [("6070", "2"), ("6070", "1")]}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1033149",  "1033388"])
    assert exp_ids == set(ids)



#Check fields with spaces
def test_db_fields_with_spaces(sqlite_db):
    cohort_criteria = {'all_of': [('41270', "Block H40-H42")], 'any_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1033149",  "1041796"])
    assert exp_ids == set(ids)


#What do we do with fields that don't exist
def test_db_missing_fields(sqlite_db):
    cohort_criteria = {'all_of': [('DoesNotExist', "X")], 'any_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set([])
    assert exp_ids == set(ids)

#What do we do when we query nan?
def test_db_missing_fields(sqlite_db):
    cohort_criteria = {'all_of': [('6070', "nan")], 'any_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set([])
    assert exp_ids == set(ids)


#Can we do a query on read2 at all?
def test_db_all_gp_clinical_read2(sqlite_db): 
    cohort_criteria = {'all_of': [('read_2', "229..")], 'any_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1037918"])
    assert exp_ids == set(ids)


#Can we read read2 when multiple entries per person
def test_db_all_gp_clinical_read_2_multiple(sqlite_db): 
    cohort_criteria = {'all_of': [('read_2', "XE0of")], 'any_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1016017"])
    assert exp_ids == set(ids)


#Can we read read3
def test_db_all_gp_clinical_read_3(sqlite_db): 
    cohort_criteria = {'all_of': [('read_3', "XE0Gu")], 'any_of': [], 'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1037918"])
    assert exp_ids == set(ids)

#Can we query 2 and 3?
def test_db_all_gp_clinical_read2and3(sqlite_db): 
    cohort_criteria = {'all_of': [], 'any_of': [('read_2', "XE0of"), ('read_3', 'XE0Gu')],  'none_of': []}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1016017", "1037918"])
    assert exp_ids == set(ids)


#Complex query, use gp_clinical and main, and use all, not and any
def test_db_any_pair_same_field_query(sqlite_db):
    cohort_criteria = {'any_of': [('41270', "Block H40-H42"), ('6119', "3"), ('6148','4')], 'all_of': [(('6070', "1"))], 'none_of': [('read_2', "XE0of")]}
    ids = query.query_databases(cohort_criteria=cohort_criteria,
                                queries=gen_query, main_filename=main_csv,
                                write_dir=None, gpc_path=gp_csv,
                                out_filename=None, write=False)
    
    exp_ids = set(["1041796", "1037058",  "1030520",  "1003670"])
    assert exp_ids == set(ids)

