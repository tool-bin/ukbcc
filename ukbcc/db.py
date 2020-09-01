
import pandas as pd
import sqlite3
from . import utils
import progressbar
import multiprocessing


#TODO: Could refactor this whole thing to use pandas data frames
# - rows are main_file fields, have columns for category, types (ukb, sql, pd)


# Create a table for a given category ('cat')
def create_field_type_table(con, tab_name, tab_type):
    field_cols = ["eid", "field", "time", "value"]
    field_col_types = ["INTEGER",  "INTEGER", "INTEGER", tab_type]
    cols = ','.join(map(' '.join, zip(field_cols, field_col_types)))
    x = con.execute(f"DROP TABLE IF EXISTS {tab_name};")
    cmd = f"CREATE TABLE {tab_name} ({cols}) ;"
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
def create_sqlite_db(db_filename: str, main_filename: str, gpc_filename: str, showcase_file: str, step=5000, nrow=520000) -> sqlite3.Connection:
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
    #db_filename='./tmp/ukb.sqlite'
    #showcase_file = '/media/ntfs_2TB/Research/datasets/ukb/showcase.csv'
    #main_filename = '/media/ntfs_2TB/Research/datasets/ukb/ukb41268.csv'
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
    tabs=dict(zip(['str', 'int', 'real', 'datetime'], ["VARCHAR", "INTEGER", "REAL", "REAL"]))
    for tab_name,field_type in tabs.items():
            create_field_type_table(con,tab_name=tab_name, tab_type=field_type)
    #
    type_fields={}
    type_lookups=dict(zip(['str', 'int', 'real', 'datetime'], [['Categorical multiple', 'Categorical single', 'Text', 'Compound'],
                                                                ['Integer'],
                                                                ['Continuous'],
                                                                ['Date', 'Time']]))
    for tab_name,field_type in tabs.items():
        type_fields[tab_name] = field_df[(field_df['ukb_type'].isin(type_lookups[tab_name])) & (field_df['field_col'] != 'eid')]['field_col']
    #
    tf_eid= field_df[field_df['field_col'] == 'eid']['field_col']
    #
    con.commit()
    #
    #step=1000
    #nrow= 525000
    date_cols = field_df['field_col'][(field_df['ukb_type']=='Date') | (field_df['ukb_type']=='Time')].to_list()
    dtypes = dict(zip(field_df['field_col'], field_df['pd_type']))
    #
    # TODO: This is slow. I wonder whether we can parallelise this by having pd.read_csv spread across 3 workers
    # and then having a single worker pushing to the DB. The problem is that SQLite is not made for parallelism,
    # so we cannot write in parallel. Dask might be a way to do the reading in parallel but not sure how to hand off
    # to another thread for writing.

    def melt_frame(df):

    with progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Bar(), progressbar.ETA(),], max_value=int(nrow/step)+1) as bar:
        chunks = pd.read_csv(main_filename, chunksize=step, dtype=dtypes, low_memory=False, encoding="ISO-8859-1", parse_dates=date_cols)
        for i, chunk in enumerate(chunks):
            for tab_name,field_type in tabs.items():
                #Convert to triples, remove nulls and then explode field
                #print(i,t)
                trips = chunk[type_fields[tab_name].append(tf_eid)].melt(id_vars='eid', value_vars=type_fields[tab_name])
                trips = trips[trips['value'].notnull()]
                trips['field'],trips['time'],trips['array']=trips['variable'].str.split("[-.]", 2).str
                trips = trips[['eid', 'field', 'time', 'value']]
                if(tab_name=='datetime'):
                    trips['value']=pd.to_numeric(trips['value'])
                #
                #if not trips.shape[0]:
                #    continue
                #chunk_cat_df.to_sql(f'cat{cat}', con, if_exists="append", index=False, method='multi')
                x=con.executemany(f'INSERT INTO {tab_name} values({",".join("?" * len(trips.columns))})',
                                trips.values.tolist())
                bar.update(i)
    #
    con.commit()
    print('UKBCC database - finished populting')

    print('Creating string index')
    con.execute('CREATE INDEX str_index ON str (field, value, time, eid)')
    print('Creating integer index')
    con.execute('CREATE INDEX int_index ON int (field, value, time, eid)')
    print('Creating continuous index')
    con.execute('CREATE INDEX real_index ON real (field, value, time, eid)')
    print('Creating date index')
    con.execute('CREATE INDEX dt_index ON datetime (field, value, time, eid)')
    print('UKBCC database - finished')
    return(con)
    #cProfile.run("db.create_sqlite_db(db_filename='./tmp/ukb_tmp.sqlite', main_filename='/media/ntfs_2TB/Research/datasets/ukb/ukb41268_5e3.csv', gpc_filename=None, showcase_file=showcase_file, nrow=5000, step=500)")





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














