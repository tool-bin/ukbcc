import pytest
import pandas as pd
from io import StringIO
#import sqlite
#import textwrap

@pytest.fixture(scope='module')
def main_csv(tmpdir_factory):
    test_main_dat =  {
     '21017-0.0': {   366: '21017_0_0', 893: '21017_0_0', 1600: '21017_0_0',
        2492: '21017_0_0', 2700: float("NaN"), 2737: float("NaN"), 3051: 
     '21017_0_0', 3158: float("NaN"), 3161: '21017_0_0', 3313: '21017_0_0', 3337: float("NaN"),
        3704: float("NaN"), 3790: '21017_0_0', 3887: float("NaN"), 4178: '21017_0_0'},
     '41270-0.1': {   366: 'E119', 893: 'H278', 1600: 'H539', 2492: 'Z138',
            2700: 'H048', 2737: 'E148', 3051: 'D226', 3158: 'H269', 3161: 'B964', 3313:
            'D414', 3337: 'H402', 3704: 'H264', 3790: 'R103', 3887: 'A498', 4178: 'H400'},
     '6070-0.0': {   366: 1.0, 893: 1.0, 1600: float("NaN"), 2492: 1.0, 2700: 1.0,
            2737: 1.0, 3051: float("NaN"), 3158: float("NaN"), 3161: float("NaN"), 3313:
            1.0, 3337: 1.0, 3704: 1.0, 3790: 1.0, 3887: float("NaN"), 4178: float("NaN")},
     '6119-0.0': {   366: float("NaN"), 893: float("NaN"), 1600: 3.0, 2492:
            3.0, 2700: 1.0, 2737: float("NaN"), 3051: 3.0, 3158: 3.0, 3161: float("NaN"),
            3313: 1.0, 3337: float("NaN"), 3704: 3.0, 3790: float("NaN"), 3887:
            float("NaN"), 4178: float("NaN")}, 
     '6148-0.1': {   366: 4.0, 893: float("NaN"), 1600: 2.0, 2492: 5.0, 2700:
            float("NaN"), 2737: 4.0, 3051: 4.0, 3158: 6.0, 3161: 4.0, 3313: 2.0, 3337: 4.0,
            3704: 4.0, 3790: 5.0, 3887: float("NaN"), 4178: float("NaN")},
    '6148-0.2': {   366: 5.0, 893: float("NaN"), 1600: 4.0, 2492: 6.0, 2700:
            float("NaN"), 2737: 6.0, 3051: 6.0, 3158: float("NaN"), 3161: float("NaN"),
            3313: float("NaN"), 3337: float("NaN"), 3704: float("NaN"), 3790: float("NaN"),
            3887: 6.0, 4178: float("NaN")}, 
    'eid': {366: 1037918, 893: 1041796, 1600: 1033149, 2492: 1037058, 2700:
            1024938, 2737: 1016017, 3051: 1033388, 3158: 1031625, 3161: 1027382, 3313:
            1038882, 3337: 1030520, 3704: 1003670, 3790: 1027017, 3887: 1031595, 4178:
            1008947} 
    }
    test_main_df = pd.DataFrame.from_dict(test_main_dat)
    fn = tmpdir_factory.mktemp("data").join("ukb.csv")
    test_main_df.to_csv(str(fn))
    print(fn)
    return str(fn)


@pytest.fixture(scope='module')
def gp_csv(tmpdir_factory):
    test_gp_dat = {   
        'data_provider': {   85711: 3, 85712: 3, 85713: 3, 206676: 3, 206677: 3, 206678: 3}, 
        'eid': {   85711: 1037918, 85712: 1037918, 85713: 1037918, 206676: 1016017, 206677: 1016017, 206678: 1016017}, 
        'event_dt': {   85711: '01/01/1980', 85712: '08/05/1984', 85713: '08/12/1986', 206676: '24/12/1964', 206677: '21/09/1966', 206678: '31/10/1967'}, 
        'read_2': {   85711: float("NaN"), 85712: float("NaN"), 85713: float("NaN"), 206676: float("NaN"), 206677: float("NaN"), 206678: float("NaN")}, 
        'read_3': {   85711: 'XE0Gu', 85712: 'F45..', 85713: '229..', 206676: 'Xa8Pq', 206677: 'L04..', 206678: '7F19.'}, 
        'value1': {   85711: float("NaN"), 85712: float("NaN"), 85713: '0.000', 206676: float("NaN"), 206677: '0.000', 206678: float("NaN")}, 
        'value2': {   85711: float("NaN"), 85712: float("NaN"), 85713: float("NaN"), 206676: float("NaN"), 206677: float("NaN"), 206678: float("NaN")}, 
        'value3': {   85711: float("NaN"), 85712: float("NaN"), 85713: float("NaN"), 206676: float("NaN"), 206677: float("NaN"), 206678: float("NaN")}
        }
    test_gp_df = pd.DataFrame.from_dict(test_gp_dat)
    fn = tmpdir_factory.mktemp("data").join("gp.csv")
    test_gp_df.to_csv(str(fn))
    print(fn)
    return str(fn)




#@pytest.fixture
#def cursor(cnxn):
#    cursor = cnxn.cursor()
#    yield cursor
#    cnxn.rollback()
#
#@pytest.fixture
#def birch_bookshelf_project(cursor):
#    stmt = textwrap.dedent('''
#    INSERT INTO projects(name, description)
#    VALUES ('bookshelf', 'Building a bookshelf from birch plywood')
#    ''')
#    cursor.execute(stmt)
#    stmt = 'SELECT @@IDENTITY'
#    project_id = cursor.execute(stmt).fetchval()
#    stmt = textwrap.dedent('''
#    INSERT INTO project_supplies(project_id, name, quantity, unit_cost)
#    VALUES ({project_id}, 'Birch Plywood', 3, 48.50),
#           ({project_id}, 'Wood Glue', 1, 5.99),
#           ({project_id}, 'Screws', 2, 8.97),
#           ({project_id}, 'Stain', 1, 30.99)
#    ''')
#    cursor.execute(stmt.format(project_id = project_id))
#    yield project_id
#
#@pytest.fixture
#def raised_garden_bed_project(cursor):
#    stmt = textwrap.dedent('''
#    INSERT INTO projects(name, description)
#    VALUES ('bookshelf', 'Assemble a raised garden bed')
#    ''')
#    cursor.execute(stmt)
#    stmt = 'SELECT @@IDENTITY'
#    project_id = cursor.execute(stmt).fetchval()
#    stmt = textwrap.dedent('''
#    INSERT INTO project_supplies(project_id, name, quantity, unit_cost)
#    VALUES ({project_id}, '4x4', 3, 3.75),
#           ({project_id}, '2x8', 8, 4.50),
#           ({project_id}, '2x4', 8, 2.50),
#           ({project_id}, 'Screws', 2, 8.97)
#    ''')
#    cursor.execute(stmt.format(project_id = project_id))
#    yield project_id
