
import pandas as pd
import sqlite3
from . import utils
import progressbar

#TODO: Could refactor this whole thing to use pandas data frames
# - rows are main_file fields, have columns for category, types (ukb, sql, pd)

#
# Create mapping from column name to field name
#
def map_col_field(field_cols):
    col_field_map = dict(zip(
        field_cols,
        [int(x.split('-')[0]) for x in field_cols]
    ))
    field_col_map = {}
    for c, f in col_field_map.items():
        field_col_map.setdefault(f, []).append(c)
    return col_field_map, field_col_map

# Create a table for a given category ('cat')
def create_cat_table(con, cat, cat_field_map, field_col_map, field_sqltype_map):
    x = con.execute(f"DROP TABLE IF EXISTS {cat};")

    # Get all the fields that are in this category, if we have them in our data
    cat_fields = ['eid'] + [y for x in cat_field_map[cat] if x in field_col_map for y in field_col_map[x]]
    if (len(cat_fields) == 1):
        return
    cat_col_types = list(field_sqltype_map.get, cat_fields

    cols = ','.join(map(' '.join, zip(['[{}]'.format(x) for x in cat_fields], cat_col_types)))
    cmd = f"CREATE TABLE {cat} ({cols}) ;"
    # print(cmd)
    x = con.execute(cmd)

def create_type_maps():

    ukbtypes = ['Date', 'Categorical multiple', 'Integer',
                'Categorical single', 'Text',
                'Time', 'Continuous', 'Compound']
    sqltypes = ['VARCHAR', 'VARCHAR', 'INTEGER',
                'VARCHAR', 'VARCHAR',
                'VARCHAR', 'REAL', 'VARCHAR']
    pandastypes = ['object', 'object', 'int',
                   'object', 'object',
                   'object', 'float', 'object']

    ukbtype_sqltype_map = dict(zip(ukbtypes, sqltypes))
    ukbtype_pandastypes_map = dict(zip(ukbtypes, pandastypes))
    sqltype_pandastypes_map = dict(zip(sqltypes, pandastypes))

    return ukbtype_sqltype_map, ukbtype_pandastypes_map, sqltype_pandastypes_map

def get_col_types(data_dict, field_cols, col_field_map, ukbtype_sqltype_map):
    field_ukbtype_map = dict(zip(data_dict['FieldID'], data_dict['ValueType']))

    # The plus text at the start is for patient ID
    col_types = ['INTEGER'] + [ukbtype_sqltype_map[field_ukbtype_map[col_field_map[x]]] for x in field_cols]

    return field_ukbtype_map, col_types


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

    data_dict = pd.read_csv(showcase_file)
    main_df = pd.read_csv(main_filename, nrows=2)

    #take all fields except patient id (eid)
    field_cols = main_df.columns.to_list()[1:]
    col_field_map, field_col_map = map_col_field(field_cols)

    #Get a bunch of type maps
    ukbtype_sqltype_map, ukbtype_pandastypes_map,sqltype_pandastypes_map = create_type_maps()
    field_ukbtype_map, col_types = get_col_types(data_dict, field_cols, col_field_map, ukbtype_sqltype_map)
    field_sqltype_map = dict(zip(main_df.columns.to_list(), col_types))

    #
    # Figure out tables to create
    #
    field_cat_map = dict(zip(data_dict['FieldID'], 'cat' + data_dict['Category'].astype(str)))
    cat_field_map = {}
    for f, c in field_cat_map.items():
        cat_field_map.setdefault(c, []).append(f)

    cats = cat_field_map.keys()

    # Connect to db
    con = sqlite3.connect(database='./tmp/ukb5e4.sqlite')

    # Create a table for every category
    print("create table")
    for cat in progressbar.progressbar(cats):
        create_cat_table(con, cat, cat_field_map, field_col_map, field_sqltype_map)

pd.read_csv(main_filename, chunksize=10000, dtype=dict(zip(main_df.columns.to_list(), list(map(sqltype_pandastypes_map.get, col_types)))), d   )
    try:
        print("")

        print("'")
        #chunker = pd.read_csv(main_filename, chunksize=10000, header=0)
        #dtypes = pd.DataFrame([chunk.dtypes for chunk in chunker])
        #types = dtypes.max().to_dict()
l = 50250/10000
utils.printProgressBar(0, l, prefix='Getting column types in main:', suffix='Complete', length=50)
curr_types=None
for i, chunk in enumerate(pd.read_csv(main_filename, chunksize=10000, header=0,low_memory=False, encoding = "ISO-8859-1")):#, engine='python')):
    if curr_types is None:
        curr_types=chunk.dtypes
    else:
        curr_types=pd.DataFrame([chunk.dtypes,curr_types]).max()
    utils.printProgressBar(i + 1, l, prefix='Getting column types in main:', suffix='Complete', length=50)
types = curr_types.to_dict()

        db = sqlite3.connect(db_filename)
        print("Done")
        print("")

        l=502506/10000
        utils.printProgressBar(0, l, prefix='Converting main:', suffix='Complete', length=50)
        for i,main_df in enumerate(pd.read_csv(main_filename, chunksize=10000, dtype=types)):
            main_df.to_sql('main', db, if_exists="append")
            utils.printProgressBar(i+1, l, prefix='Converting main:', suffix='Complete', length=50)

        utils.printProgressBar(0, l, prefix='Converting gpc:', suffix='Complete', length=50)
        for i,gpc_df in enumerate(pd.read_csv(gpc_filename, chunksize=10000)):
            gpc_df.to_sql('gpc', db, if_exists="append")
            utils.printProgressBar(i+1, l, prefix='Converting gpc:', suffix='Complete', length=50)

        search_df.to_sql(name='search', con=db)
        return(db)
    except Exception:
        print("Failed to create connection to a database:", db_filename)
        raise



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














