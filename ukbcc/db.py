
import pandas as pd
import sqlite3
from . import utils


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
