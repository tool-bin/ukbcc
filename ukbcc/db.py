
import pandas as pd
import sqlite3



# TODO: do more checks on whether the files exist
def create_sqlite_db(db_filename: str, main_filename: str, gpc_file: str, search_df: pd.DataFrame) -> sqlite3.Connection:
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
    main_df = pd.read_csv(main_filename)
    gpc_df = pd.read_csv(gpc_file)

    try:
        sql_db = sqlite3.connect(db_filename)
        main_df.to_sql(name='main', con=sql_db)
        gpc_df.to_sql(name='gpc', con=sql_db)
        search_df.to_sql(name='search', con=sql_db)
        return(sql_db)
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
