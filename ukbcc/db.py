
import pandas as pd
import sqlite3
from . import utils
import progressbar

#TODO: Could refactor this whole thing to use pandas data frames
# - rows are main_file fields, have columns for category, types (ukb, sql, pd)


# Create a table for a given category ('cat')
def create_cat_table(con, cat, field_df):
    field_cols = field_df[field_df['category']==cat]['field_col'].tolist()
    field_col_types = ['INTEGER PRIMARY KEY']+field_df[field_df['category']==cat]['sql_type'].tolist()
    if not field_cols:
        return()
    cols = ','.join(map(' '.join, zip(['eid']+['[f{}]'.format(x) for x in field_cols], field_col_types)))
    x = con.execute(f"DROP TABLE IF EXISTS cat{cat};")
    cmd = f"CREATE TABLE cat{cat} ({cols}) ;"
    #print(cmd)
    x = con.execute(cmd)

def create_type_maps():
    ukbtypes = ['Date', 'Categorical multiple', 'Integer',
                'Categorical single', 'Text',
                'Time', 'Continuous', 'Compound']
    sqltypes = ['VARCHAR', 'VARCHAR', 'INTEGER',
                'VARCHAR', 'VARCHAR',
                'VARCHAR', 'REAL', 'VARCHAR']
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
    db_filename='./tmp/ukb.sqlite'
    showcase_file = '/media/ntfs_2TB/Research/datasets/ukb/showcase.csv'
    main_filename = '/media/ntfs_2TB/Research/datasets/ukb/ukb41268.csv'
    gp_filename = '/media/ntfs_2TB/Research/datasets/ukb/gp_clinical.txt'
    data_dict = pd.read_csv(showcase_file)
    main_df = pd.read_csv(main_filename, nrows=2)

    field_df = pd.DataFrame({'field_col': main_df.columns,
                             'field': ['eid'] + [int(x.split('-')[0]) for x in main_df.columns[1:]]})
    field_df['category'] = [-1]+list(map(dict(zip(data_dict['FieldID'], data_dict['Category'])).get, field_df['field'][1:]))
    field_df['ukb_type']=list(map(dict(zip(['eid']+data_dict['FieldID'].to_list(),
                                           ['Integer']+data_dict['ValueType'].to_list())).get, field_df['field']))

    #Map types that come with UKB to other forms
    ukbtype_sqltype_map, ukbtype_pandastypes_map = create_type_maps()
    field_df['sql_type'] = list(map(ukbtype_sqltype_map.get, field_df['ukb_type']))
    field_df['pd_type'] = list(map(ukbtype_pandastypes_map.get, field_df['ukb_type']))


    # Connect to db
    con = sqlite3.connect(database=db_filename)

    # Create a table for every category
    print("create table")
    cats = list(set(field_df['category'].tolist()[1:]))
    for cat in progressbar.progressbar(cats):
            create_cat_table(con, cat, field_df)

    #
    con.commit()
    #
    nrow= int(525000/1000)+1
    date_cols = field_df['field_col'][(field_df['ukb_type']=='Date') | (field_df['ukb_type']=='Time')].to_list()
    dtypes = dict(zip(field_df['field_col'], field_df['pd_type']))
    #
    with progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Bar(), progressbar.ETA(),], max_value=nrow) as bar:
        for i, chunk in enumerate(pd.read_csv(main_filename, chunksize=5000, dtype=object,low_memory=False, encoding = "ISO-8859-1")):
            for cat in cats[1:]:
                fields=field_df['field_col'][field_df['category'] == cat].tolist()
                chunk_cat_df = chunk[['eid']+fields]
                if chunk_cat_df[fields].isnull().all().all():
                    continue
                chunk_cat_df.columns = ['eid']+['f'+f for f in fields]
                #chunk_cat_df.to_sql(f'cat{cat}', con, if_exists="append", index=False, method='multi')
                x=con.executemany(f'INSERT INTO cat{cat} values({",".join("?" * len(chunk_cat_df.columns))})',
                                chunk_cat_df.values.tolist())
                bar.update(i)
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














