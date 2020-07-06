import pandas as pd
from . import utils, query
import os

def filter_bulk_file(eids: list, bulk_filename: str, write: bool = True) -> pd.DataFrame:
    """Returns filtered dataframe.

    Filter an existing bulk file for a list of specific EIDs, where the first column is a list of participant IDs and
    the second column is the datafield_array_instance.

    Keyword arguments:
    ------------------
    eids: list[str]
        list of eids
    bulk_filename: str
        path and out_filename of bulk file
    write: bool [True]
        if true, bulk file will be written to text file

    Returns:
    --------
    bulk_df: pd.DataFrame
        returns a pandas DataFrame of the bulk file filtered for the eids list given
        if the write option is enabled, the pandas DataFrame will be written to "{bulk_filename}_filtered_eids.bulk"
    """

    bulk_in = pd.read_csv(bulk_filename, delimiter=" ", names=['eid', 'datafield'], chunksize=10000, dtype=str).set_index('eid')
    final = pd.DataFrame(columns=['eid', 'datafield'])
    for ch in bulk_in:
        filtered_df = ch.loc[eids].reset_index()
        if filtered_df:
            final = final.append(filtered_df, ignore_index=True)
    if write:
        bulk_name = bulk_filename[:-5]
        print("Writing file to : {}".format(bulk_name))
        out = "{}_filtered_eids.bulk".format(bulk_name)
        final.to_csv(out, sep=" ", header=False, index=False)
    return final


def create_bulk_df(main_filename: str, column_keys: list, values: list, eids: list, write: bool = True, bulk_filename: str="bulk_filtered_eids.bulk") \
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
    bulk_filename: str
        path and name of the file to write the bulk dataframe to - a default name is provided

    Returns:
    --------
    bulk_df: pd.DataFrame
        bulk dataframe where the first column corresponds to eid and the second column to datafield_array_index
        if the write option is enabled, the pandas DataFrame will be written the string specified in the bulk_filename argument
    """
    entries = list(zip(column_keys, values))
    collist = utils.get_columns(main_filename, columns_keys).columns.tolist()
    query = query._create_mds_query(main_filename, entries, 'any_of')
    filtered = query._query_main_data(main_filename, collist, query)
    filtered_eids = filtered.loc[eids].index.tolist()
    col_list = filtered.columns.tolist()
    lines = []
    for eid in filtered_eids:
        for col in col_list:
            original = col.split('t')[1]
            line = f'{eid} {original}'
            lines.append(line)
    # main_cols = utils.get_columns(main_filename=main_filename, keys=column_keys).set_index('eid')
    # main_eids = main_cols.loc[eids].reset_index()
    # cols = main_eids.columns.tolist()
    # rename_dict, rename_numbers = query._construct_renaming_dict(cols, '-')
    # formatted = main_eids.rename(columns=rename_dict).melt(id_vars='eid', value_vars=rename_numbers,
    #                                                        value_name="bulk_datafield", var_name="visits")
    # filtered = formatted.loc[formatted['bulk_datafield'] == values[0]].reset_index(drop=True)
    # bulk = filtered[['eid', 'visits']]
    # for df in column_keys:
    #     line = f'{df}_'
    #     bulk['out'] = line + bulk['visits'].str.replace('.', '_')
    if write:
        with open(bulk_filename, "w") as f:
            for line in lines:
                f.write(line + "\n")
        #bulk.to_csv(bulk_filename, columns=['eid', 'out'], sep=" ", header=False, index=False)
    return filtered

def download_bulk_files(ukbfetch_file: str="./ukbfetch", bulk_file: str, key_file: str):
    """

    Runs the ukbfetch utility for a given bulk file to download the associated files (datafields). Expects the bulk file has list `eid` in the first column and `datafield_array_index` in the second column.

    Keyword arguments:
    ------------------
    ukbfetch_file: str
        path and name of ukbfetch utility
    bulk_file: str
        path and name of the bulk_file
    key_file: str
        path and name of the key file in order to authenticate to ukb data servers

    Returns:
    --------
    """
    with open(bulk_file) as f:
        for i, l in enumerate(f):
            pass
        i+=1
    if i <= 1000:
        command = f"{ukbfetch_file} -b{bulk_file} -a{key_file}&"
        os.system(command)
    else:
        command = f"{ukbfetch_file} -b{bulk_file} -a{key_file} -s1 -m1000&"
