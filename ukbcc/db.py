
import pandas as pd
import sqlite3
from . import utils
import progressbar

#TODO: Could refactor this whole thing to use pandas data frames
# - rows are main_file fields, have columns for category, types (ukb, sql, pd)


# Create a table for a given category ('cat')
def create_field_type_table(con, field_type):
    field_cols = ["eid", "field", "time", "value"]
    field_col_types = ["INTEGER",  "INTEGER", "INTEGER", field_type]
    cols = ','.join(map(' '.join, zip(field_cols, field_col_types)))
    x = con.execute(f"DROP TABLE IF EXISTS tab{field_type};")
    cmd = f"CREATE TABLE tab{field_type} ({cols}) ;"
    print(cmd)
    x = con.execute(cmd)


def create_type_maps():
    ukbtypes = ['Date', 'Categorical multiple', 'Integer',
                'Categorical single', 'Text',
                'Time', 'Continuous', 'Compound']
    sqltypes = ['NUMERIC', 'VARCHAR', 'INTEGER',
                'VARCHAR', 'VARCHAR',
                'NUMERIC', 'REAL', 'VARCHAR']
    pandastypes = ['object', 'object', 'Int64',
                   'object', 'object',
                   'object', 'float', 'object']
    #
    ukbtype_sqltype_map = dict(zip(ukbtypes, sqltypes))
    ukbtype_pandastypes_map = dict(zip(ukbtypes, pandastypes))
    #
    return ukbtype_sqltype_map, ukbtype_pandastypes_map



# TODO: do more checks on whether the files exist
def create_sqlite_db(db_filename: str, main_filename: str, gpc_filename: str, search_df: pd.DataFrame) -> sqlite3.Connection:
    """Returns basic statistics for given columns and a translated dataframe.

    Keyword arguments:
    ------------------
    db_filename: str
        path and filename of db to create
    main_filename: str
        path and filename of main dataset
    gp_clinical_file: list[str]
        list of eids
    search_df: str
        path and filename of showcase file

    Returns:
    --------
    conn: sqlite3.Connection
        Connection to the written database

    """

    #Read in files
if(1):
    db_filename='./tmp/ukb1.sqlite'
    showcase_file = '/media/ntfs_2TB/Research/datasets/ukb/showcase.csv'
    main_filename = '/media/ntfs_2TB/Research/datasets/ukb/ukb41268_20.csv'
    gp_filename = '/media/ntfs_2TB/Research/datasets/ukb/gp_clinical.txt'
    data_dict = pd.read_csv(showcase_file)
    main_df = pd.read_csv(main_filename, nrows=2)
    #
    field_df = pd.DataFrame({'field_col': main_df.columns,
                             'field': ['eid'] + [int(x.split('-')[0]) for x in main_df.columns[1:]]})
    field_df['category'] = [-1]+list(map(dict(zip(data_dict['FieldID'], data_dict['Category'])).get, field_df['field'][1:]))
    field_df['ukb_type']=list(map(dict(zip(['eid']+data_dict['FieldID'].to_list(),
                                           ['Integer']+data_dict['ValueType'].to_list())).get, field_df['field']))
    #
    #Map types that come with UKB to other forms
    ukbtype_sqltype_map, ukbtype_pandastypes_map = create_type_maps()
    field_df['sql_type'] = list(map(ukbtype_sqltype_map.get, field_df['ukb_type']))
    field_df['pd_type'] = list(map(ukbtype_pandastypes_map.get, field_df['ukb_type']))
    #
    #
    # Connect to db
    con = sqlite3.connect(database=db_filename)
    #
    # Create a table for every sqltype
    print("create table")
    tabs=["TEXT", "INTEGER", "REAL", "DATE"]
    type_fields={}
    for t in ["VARCHAR", "INTEGER", "REAL", "NUMERIC"]:
            create_field_type_table(con, t)
    #
    for t in ["VARCHAR", "INTEGER", "REAL", "NUMERIC"]:
        type_fields[t] = field_df[field_df['sql_type'] == t]['field_col']
    #
    tf_eid= field_df[field_df['field_col'] == 'eid']['field_col']
    #
    con.commit()
    #
    nrow= int(525000/1000)+1
    date_cols = field_df['field_col'][(field_df['ukb_type']=='Date') | (field_df['ukb_type']=='Time')].to_list()
    dtypes = dict(zip(field_df['field_col'], field_df['pd_type']))
    #
    #
    with progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Bar(), progressbar.ETA(),], max_value=nrow) as bar:
        for i, chunk in enumerate(pd.read_csv(main_filename, chunksize=5000, dtype=object,low_memory=False, encoding = "ISO-8859-1")):
            for t in tabs:
                #Convert to triples, remove nulls and then explode field
                trips = chunk[type_fields[t].append(tf_eid)].melt(id_vars='eid', value_vars=type_fields[t])
                trips = trips[trips['value'].notnull()]
                trips['field'],trips['time'],trips['array']=trips['variable'].str.split("[-.]", 2, expand=True)
                trips = trips[['eid', 'field', 'time', 'value']]
                #
                if not trips.shape[0]:
                    continue
                #chunk_cat_df.to_sql(f'cat{cat}', con, if_exists="append", index=False, method='multi')
                x=con.executemany(f'INSERT INTO tab{t} values({",".join("?" * len(trips.columns))})',
                                trips.values.tolist())
                bar.update(i)
    #
    con.commit()







#
#
#
def isSQLite3(filename):
    from os.path import isfile, getsize

    if not isfile(filename):
        return False
    if getsize(filename) < 100: # SQLite database file header is 100 bytes
        return False

    with open(filename, 'rb') as fd:
        header = fd.read(100)

    return header[:16] == 'SQLite format 3\x00'














