import pytest
import pandas as pd
from io import StringIO
import re
#import sqlite
#import textwrap

@pytest.fixture(scope='module')
def main_csv(tmpdir_factory):
    test_main_dat = ('"21017-0.0"	"41270-0.1"	"6070-0.0"	"6119-0.0"	"6148-0.1"	"6148-0.2"	"eid"\n'
'"21017_0_0"	"E119"	"2"	""	"4"	"5"	"1037918"\n'
'"21017_0_0"	"Block H40-H42"	"1"	""	""	""	"1041796"\n'
'"21017_0_0"	"Block H40-H42"	""	"3"	"2"	"4"	"1033149"\n'
'"21017_0_0"	"Z138"	"1"	"3"	"5"	"6"	"1037058"\n'
'""	"H048"	"1"	"1"	""	""	"1024938"\n'
'""	"E148"	"1"	""	"4"	"6"	"1016017"\n'
'"21017_0_0"	"D226"	""	"3"	"4"	"6"	"1033388"\n'
'""	"H269"	""	"3"	"6"	""	"1031625"\n'
'"21017_0_0"	"D414"	"1"	"1"	"2"	""	"1038882"\n'
'""	"H402"	"1"	""	"4"	""	"1030520"\n'
'""	"H264"	"1"	"3"	"4"	""	"1003670"\n'
'"21017_0_0"	"R103"	"1"	""	"5"	""	"1027017"\n'
'""	"A498"	""	""	""	"6"	"1031595"\n'
'"21017_0_0"	"H400"	""	""	""	""	"1008947"\n')
    test_main_dat = re.sub("\t+", ",", test_main_dat)
    #test_main_df = pd.read_csv(StringIO(test_main_dat), delimiter="[ ]+", quotechar="'")
    fn = tmpdir_factory.mktemp("data").join("ukb.csv")
    fn.write(test_main_dat)#test_main_df.to_csv(str(fn), sep=",", quotechar='"', index=False)
    print(fn)
    return str(fn)


@pytest.fixture(scope='module')
def gp_csv(tmpdir_factory):
    test_gp_dat = (   
"eid,	data_provider,	event_dt,	read_2,	read_3,	value1,	value2,	value3\n"
"1037918,	3,	01/01/1980,	,XE0Gu,	\n"
"1037918,	3,	08/05/1984,	,F45..,	\n"
"1037918,	3,	08/12/1986,	229..,	0.0,	\n"
"1016017,	3,	24/12/1964,	XE0of,	\n"
"1041796,	3,	21/09/1966,	4662.,	0.0,	\n"
"1016017,	3,	31/10/1967,	XE0of,	1.0,	2.0,	3.0\n"
        )
    fn = tmpdir_factory.mktemp("data").join("gp.csv")
    #Tabs write out strangely so we swap tabs for commas when outputting
    fn.write(re.sub(',','\t', re.sub("\t+", "",test_gp_dat)))
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
