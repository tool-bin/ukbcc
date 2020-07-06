import pandas as pd
import requests
import json

def read_dictionary(file: str):
    with open(file, 'r') as f:
        dic = json.loads(f.read())
    return dic

def write_dictionary(out_dic: dict, output_file: str):
    with open(output_file, 'w') as f:
        f.write(json.dumps(out_dic))

def download_latest_files(download_path: str) -> bool:
    """Returns acknowledgement.

    Downloads showcase and coding files from ukbb website in case they are out of date.

    Keyword arguments:
    ------------------
    cohort_criteria: dict
        dictionary that was created using select_conditions or update_inclusion_logic function
    main_filename: str
        path to main file

    Returns:
    --------
    queries: dict(str)
        dictionary containing one query string per database
    """

    encoding = 'utf-8'
    showcase = requests.get("https://biobank.ctsu.ox.ac.uk/~bbdatan/Data_Dictionary_Showcase.csv")
    with open('{}/showcase.csv'.format(download_path), 'w+') as f:
        f.write(str(showcase.content, encoding))
    codings = requests.get("https://biobank.ctsu.ox.ac.uk/~bbdatan/Codings_Showcase.csv")
    with open('{}/codings.csv'.format(download_path), 'w+') as f:
        f.write(str(codings.content, encoding))
    return True


def _get_query(keys: list) -> str:
    """Returns a regex string for a pd.DataFrame filter function.

    Keyword arguments:
    ------------------
    keys: list[str]
        a list of datafield collected from the UKBB Data Showcase website e.g 41270

    Returns:
    --------
    regex_string: str
        regex string to filter columns

    """

    start = r"^eid"
    end = r''.join(r"|^{}$|^{}-".format(i, i) for i in keys)
    regex_string = start + end
    return regex_string


def get_columns(main_filename: str, keys: list, nrows: int = None, out_filename: str = "", write: bool = False) -> \
        pd.DataFrame:
    """Returns a dataframe by selecting all relevant keys based on the given key(s).

    Optionally write the dataframe to a csv file.

    Keyword arguments:
    ------------------
    main_filename: str
        file location of the main dataset file
    keys: list[str]
        list of keys (data column_keys) for which to extract columns
    nrows: int
        number of rows to be read. If None, all rows are read.
    out_filename: str
        location to store the file if write == True
    write: bool
        if True, resulting dataframe is written to file out_filename

    Returns:
    --------
    main_df: pd.DataFrame
        filtered dataframe

    """

    main_df = pd.read_csv(main_filename, nrows=1, dtype='string')
    keys_query = _get_query(keys)
    col_list = main_df.filter(regex=keys_query).columns.tolist()
    filtered_df = pd.read_csv(main_filename, usecols=col_list, dtype=str, nrows=nrows)
    if write:
        print("Writing file")
        filtered_df.to_csv(out_filename, index=False)
    return filtered_df


def quick_filter_df(main_filename: str, eids: list) -> pd.DataFrame:
    """Returns all columns of dataframe using specified eids only.

    Keyword arguments:
    ------------------
    main_filename: str
        file location of the main dataset file
    eids: list[str]
        list of cohort ids

    Returns:
    --------
    filtered_df: pd.DataFrame
        filtered main dataframe

    """
    eids_set = set(eids)

    col_names = pd.read_csv(main_filename, nrows=0).columns
    eid_column_df = pd.read_csv(main_filename, usecols=['eid'])
    wanted = list(eid_column_df[eid_column_df['eid'].isin(eids_set)].index)
    wanted = [x + 1 for x in wanted]
    filtered_df = pd.read_csv(main_filename, skiprows=lambda x: x not in wanted, names=col_names)

    return filtered_df

def write_txt_file(output_file: str, eids: str):
    with open(output_file, "w") as f:
        for id in eids:
            f.write(str(id) + ",")

def read_txt_file(file: str):
    lines = []
    with open(file, "r") as f:
        for line in f.read().split(','):
            lines.append(line)
    return lines

def filter_main_df(main_filename: str, column_keys: list, values: list, eids: list, write: bool = True) \
        -> pd.DataFrame:
    """Returns bulk dataframe.

    Creates a bulk file where the first column corresponds to eid and the second column to datafield_array_index. The list of column_keys and values are expected to match for each entry.

    Keyword arguments:
    ------------------
    main_filename: str
        path and name of main dataset
    column_keys: list[str]
        keys of the columns that should be included to create the bulk file
    values: list[str]
        list of values with which to filter the columns
    eids: list[str]
        list of eids
    write: bool [True]
        if true, bulk file will be written to text file

    Returns:
    --------
    df: pd.DataFrame
        dataframe where the first column corresponds to eid and the second column to datafield_array_index
        if the write option is enabled, the pandas DataFrame will be written the string specified in the filename argument
    """
    entries = list(zip(column_keys, values))
    collist = utils.get_columns(main_filename, columns_keys).columns.tolist()
    query = query._create_mds_query(main_filename, entries, 'any_of')
    filtered = query._query_main_data(main_filename, collist, query)
    filtered_eids = filtered.loc[eids].tolist()
    #col_list = filtered.columns.tolist()
    if write:
        write_txt_file(filename)
        # with open(filename, "w") as f:
        #     for line in filtered_eids:
        #         f.write(line + "\n")
        #bulk.to_csv(bulk_filename, columns=['eid', 'out'], sep=" ", header=False, index=False)
    return filtered_eids
