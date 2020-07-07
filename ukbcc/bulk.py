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

    bulk_in = pd.read_csv(bulk_filename, delimiter=" ", names=['eid', 'datafield'], dtype=str).set_index('eid')
    bulk_filt = bulk_in[bulk_in.index.isin(eids)].reset_index()
    if write:
        bulk_name = bulk_filename[:-5]
        print("Writing file to : {}".format(bulk_name))
        out = "{}_filtered_eids.bulk".format(bulk_name)
        bulk_filt.to_csv(out, sep=" ", header=False, index=False)
    return bulk_filt


def create_bulk_df(main_filename: str, column_keys: list, values: list, eids: list, write: bool = True, bulk_filename: str="bulk_filtered_eids.bulk") -> pd.DataFrame:
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
    collist = utils.get_columns(main_filename, column_keys).columns.tolist()
    query_string = query._create_mds_query(main_filename, entries, 'any_of')
    filtered = query._query_main_data(main_filename, collist, query_string, return_df=True)
    # filtered_eids = filtered.loc[eids].index.tolist()
    df_eids = filtered['eid'].tolist()
    filtered_eids = list(set.intersection(*(set(x) for x in [df_eids, eids] if x)))
    col_list = filtered.columns.tolist()
    lines = []
    for eid in filtered_eids:
        for col in col_list:
            original = col.split('t')[1]
            line = f'{eid} {original}'
            lines.append(line)
    if write:
        with open(bulk_filename, "w") as f:
            for line in lines:
                f.write(line + "\n")
        #bulk.to_csv(bulk_filename, columns=['eid', 'out'], sep=" ", header=False, index=False)
    return filtered

def download_bulk_files(bulk_file: str, key_file: str, ukbfetch_file: str="./ukbfetch"):
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

def download_genetic_files(typename: str, key_file: str, chr: str="all", ukbgene_file: str="./ukbgene"):
    """

    Runs the ukbgene utility to download the genotype call files and related genomic data for each chromosome.

    Keyword arguments:
    ------------------
    typename: str
        type of data to be retrieved - valid entries include 'cal', 'con', 'int', 'baf', 'l2r', 'imp', 'hap'
    key_file: str
        path and name of the key file in order to authenticate to ukb data servers
    chr: str
        optional variable specifying chromosome to download the data for - if "all", download for all chromosomes
    ukbgene_file: str
        path and name of ukbgene utility

    Returns:
    --------
    """
    valid_types = ['cal', 'con', 'int', 'baf', 'l2r', 'imp', 'hap']
    valid_chr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X', 'Y', 'XY', 'MT']

    if typename not in valid_types:
        raise Exception("Invalid typename, please provide a typename in: {}".format(valid_types))
    else:
        if chr == 'all':
            for c in valid_chr:
                command = f"{ukbgene_file} {typename} -c{c} -a{key_file}&"
                os.system(command)
        else:
            if chr not in valid_chr:
                raise Exception("Invalid chromosome, please provide a chromosome in {}".format(valid_chr))
            else:
                command = f"{ukbgene_file} {typename} -c{chr} -a{key_file}&"
                os.system(command)
