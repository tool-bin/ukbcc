import pandas as pd
from ukbcc import query
#import requests
import json
import os
from configparser import ConfigParser


def read_dictionary(file: str):
    """Loads contents of a file into a dictionary

    Keyword arguments:
    ------------------
    file: str
        path and name of file

    Returns:
    --------
    dict
    """
    with open(file, 'r') as f:
        dic = json.loads(f.read())
    return dic


def write_dictionary(out_dic: dict, output_file: str):
    """Write contents of a dictionary to a file

    Keyword arguments:
    ------------------
    out_dic: dict
        dictionary to write to file
    output_file: str
        file to write dictionary to

    Returns:
    --------
    """
    with open(output_file, 'w') as f:
        f.write(json.dumps(out_dic))

def write_config(config_directory: str, main_filename: str,
                 gp_clinical_file: str, out_path: str, out_filename: str):
    """Write configuration file for file paths

    Keyword arguments:
    ------------------
    config_directory: str
        path of directory to write config file to
    main_filename: str
        name of main.csv file
    gp_clinical_file: str
        name of GP Clinical file
    out_path: str
        path of write files to
    out_filename: str
        name to write cohort IDs to

    Returns:
    --------
    check: str
        string that states whether config file exists
    """
    if not os.path.exists(config_directory):
        os.mkdir(config_directory)
    config_out = os.path.join(config_directory, "config.conf")
    with open(config_out, "w+") as file:
        file.write('[PATHS]\n'
                   f'main_filename = "{main_filename}"\n'
                   f'gp_clinical_file = "{gp_clinical_file}"\n'
                   f'out_path = "{out_path}"\n'
                   f'out_filename = "{out_filename}"\n')

    if os.path.exists(config_out):
        check = f"Config saved successfully to {config_out}."
    else:
        check = "Config not saved."
    return check

def download_latest_files(download_path: str) -> bool:
    """Returns acknowledgement.

    Downloads showcase and coding files from ukbb website in case they are out of date.

    Keyword arguments:
    ------------------
    download_path: str
        path to download the latest showcase and coding files to

    Returns:
    --------
    bool
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


def get_columns(main_filename: str, keys: list, delimiter: str=',', nrows: int = None, out_filename: str = "", write: bool = False) -> \
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

    main_df = pd.read_csv(main_filename, nrows=1, dtype='string', delimiter=delimiter)
    keys_query = _get_query(keys)
    col_list = main_df.filter(regex=keys_query).columns.tolist()
    filtered_df = pd.read_csv(main_filename, usecols=col_list, dtype=str, nrows=nrows, delimiter=delimiter)
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

def filter_df_columns(main_filename: str, column_keys: list, eids: list):
    """Filters main dataset using a list of columns and a list of eids.

    Keyword arguments:
    ------------------
    main_filename: str
        file location of the main dataset file
    column_keys: list
        list of columns (datafields) to load from the main dataset
    eids: list[str]
        list of cohort ids

    Returns:
    --------
    filtered_df: pd.DataFrame
        filtered main dataframe

    """
    if 'eid' not in column_keys:
        column_keys.append('eid')
    main_df = pd.read_csv(main_filename, usecols=column_keys)
    main_df_filtered = main_df.set_index('eid').iloc[main_df.set_index('eid').index.isin(eids)]
    return main_df_filtered

def write_txt_file(output_file: str, eids: list):
    with open(output_file, "w") as f:
        for id in eids:
            f.write(str(id) + ",")


def read_txt_file(file: str):
    lines = []
    with open(file, "r") as f:
        for line in f.read().split(','):
            if line != "":
                lines.append(line)
    return lines


def filter_main_df(main_filename: str, column_keys: list, values: list, eids: list=[], write: bool=True, filename: str="filtered_main_df_eids.txt") \
        -> pd.DataFrame:
    """Returns bulk dataframe.

    Filters the main dataset based on a list of columns and their corresponding values.

    Keyword arguments:
    ------------------
    main_filename: str
        path and name of main dataset
    column_keys: list[str]
        keys of the columns that should be included to create the bulk file
    values: list[str]
        list of values with which to filter the columns
    eids: list[str]
        optional list of eids to filter main dataframe with - if empty list, dataframe will not be filtered
    write: bool[True]
        if true, list of filtered eids will be written to text file
    filename: str["filtered_main_df_eids"]
        optional filename for writing out the filtered main dataframe

    Returns:
    --------
    df: pd.DataFrame
        filtered main dataframe with columns based on column_keys parameter and values based on values parameter
        if the write option is enabled, the pandas DataFrame will be written the string specified in the filename argument
    """
    entries = list(zip(column_keys, values))
    collist = get_columns(main_filename, column_keys).columns.tolist()
    query_string = query._create_mds_query(main_filename, entries, 'any_of')
    filtered = query._query_main_data(main_filename=main_filename, keys=collist, query=query_string, return_df=True).set_index('eid')
    if eids:
        filtered_df = filtered.loc[filtered.index.intersection(eids)]
        return filtered_df, filtered_df.index.tolist()
        if write:
            write_txt_file(filename, filtered_eids)
    else:
        return filtered
