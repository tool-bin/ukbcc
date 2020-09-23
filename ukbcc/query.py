import pandas as pd
import os
#from selenium import webdriver
#import requests
from . import utils
import io
import time


def create_queries(cohort_criteria: dict, main_filename: str, gpc_path: str) -> dict:
    """Returns query strings for gp_clinical and main dataset.

    Keyword arguments:
    ------------------
    cohort_criteria: dict
        dictionary that was created using select_conditions or update_inclusion_logic function
    main_filename: str
        path to main file
    gpc_path: str
        path to gp_clinical.txt file


    Returns:
    --------
    queries: dict(str)
        dictionary containing one query string per database
    """

    queries = {'gp_clinical': {
        'all_of': '', 'any_of': '', 'none_of': ''
    },
        'main': {
            'all_of': '', 'any_of': '', 'none_of': ''
        }
    }
    data = {'gp_clinical': {
        'all_of': [], 'any_of': [], 'none_of': []
    },
        'main': {
            'all_of': [], 'any_of': [], 'none_of': []
        }
    }
    main_fields = []

    for logicKey in cohort_criteria.keys():
        for entry in cohort_criteria[logicKey]:
            if entry[0] in ['read_2', 'read_3']:
                data['gp_clinical'][logicKey].append(entry)
            else:
                data['main'][logicKey].append(entry)
                main_fields.append(entry[0])

    for database in data.keys():
        if len(data[database]) == 0:
            continue
        for logicKey in data[database]:
            if len(data[database][logicKey]) == 0:
                continue
            if gpc_path and database == 'gp_clinical':
                queries['gp_clinical'][logicKey] = _create_mds_query(gpc_path, entries=data[database][logicKey], delimiter='\t', logic=logicKey)
            elif database == 'main':
                queries['main'][logicKey] = _create_mds_query(main_filename, data[database][logicKey], logicKey)
    return queries


def query_databases(cohort_criteria: dict, queries: dict, main_filename: str, write_dir: str,
                    gpc_path: str, out_filename: str = "", write: bool = False) -> list:
    """Returns eids of candidates matching the cohort criteria.

    Queries UKBB database and Main dataset for the specified cohort_criteria.

    Keyword arguments:
    ------------------
    cohort_criteria: dict
        dictionary that was created using select_conditions or update_inclusion_logic function
    queries: dict
        dictionary containing query strings for each database and logic
    main_filename: str
        path to main file
    write_dir: str
        path and name of directory to write output files to
    gpc_path: str
        path and name of GP clinical file
    out_filename: str
        path and out_filename to which to write results if write == True
    write: bool [False]
        set to True to store results in file `out_filename`.

    Returns:
    --------
    eids: list
        List of eids matching the search criterion of the cohort_criteria
    """

    separate_eids = {'gp_clinical': {
        'all_of': [], 'any_of': [], 'none_of': []
    },
        'main': {
            'all_of': [], 'any_of': [], 'none_of': []
        }
    }

    main_fields = []
    for logicKey in cohort_criteria.keys():
        if len(cohort_criteria[logicKey]) == 0:
            continue
        for entry in cohort_criteria[logicKey]:
            if entry[0] not in ['read_2', 'read_3']:
                main_fields.append(entry[0])


    for database in queries.keys():
        if len(queries[database]) == 0:
            print("No queries found for database: {}".format(database))
            break
        for logicKey in queries[database]:
            if len(queries[database][logicKey]) == 0:
                continue
            if database == 'gp_clinical' and gpc_path:
                query = queries['gp_clinical'][logicKey]
                pgc_eids = _query_main_data(main_filename=gpc_path, delimiter='\t', keys=['read_2', 'read_3'],
                                            query=query)
                separate_eids[database][logicKey] = pgc_eids
            elif database == 'main':
                query = queries['main'][logicKey]
                main_eids = _query_main_data(main_filename, main_fields, query)
                separate_eids[database][logicKey] = main_eids

    try:
        ands = set.intersection(*(set(x) for x in [separate_eids['gp_clinical']['all_of'],
                                                   separate_eids['main']['all_of']] if x))
    except Exception as error:
        #print("No results from mandatory conditions, resulting in exception {}. Creating empty ands set".format(error))
        ands = set()
    ors = set(set(separate_eids['gp_clinical']['any_of']) | set(separate_eids['main']['any_of']))
    nots = set(set(separate_eids['gp_clinical']['none_of']) | set(separate_eids['main']['none_of']))
    try:
        ands_ors = set.intersection(*(set(x) for x in [ands, ors] if x))
    except Exception as error:
        #print("No results from intersection between ands and ors, resulting in exception: {}. Creating empty ands_ors set".format(error))
        ands_ors = set()
    eids = list(ands_ors - nots)

    if write:
        output_file = os.path.join(write_dir, out_filename)
        utils.write_txt_file(output_file, eids)
    return eids

def _create_main_query_updates(main_filename: str, cohort_criteria_sublist: list, delimiter=','):
    """Returns list of tuples for selected column_keys from cohort_criteria.

    Creates an updated list to query the main dataset, where the first entry is the field,
    and the second entry is a pandas query string for all keys corresponding to that field.

    Keyword arguments:
    ------------------
    main_filename: str
        path to main dataset
    cohort_criteria_sublist: list[tuples]
        list of tuples from searchCodeDict
    logic: str
        one of "all_of", "any_of", or "none_of"

    Returns:
    --------
    updates: list
        List of tuples matching the search criterion of the searchCodeDict with pandas query logic
    """
    updates = []
    scroll_replace = lambda x: 't' + x.replace('-', '_')
    period_replace = lambda x: x.replace('.', '_')
    for field, value in cohort_criteria_sublist:
        columns_list = utils.get_columns(main_filename=main_filename, keys=[field], nrows=2, delimiter=delimiter).set_index(
            'eid').columns.tolist()
        columns = [period_replace(scroll_replace(x)) for x in columns_list]
        query = _create_col_query(columns, value)
        updates.append((field, query))
    return updates


def _query_main_data(main_filename: str, keys: list, query: str, delimiter: str=',', return_df: bool=False) -> list:
    """Returns eids for given query.

    Filters main data file, extracting only keys needed, then queries it to return matching eids.

    Keyword arguments:
    ------------------
    main_filename: str
        path to main dataset
    keys: list
        list of all column_keys in the cohort_criteria
    query: str
        string to query data. most likely created using _create_mds_query.
    delimiter: str
        delimiter to use to read the main_filename file
    return_df: bool
        determines whether the full dataframe is returned

    Returns:
    --------
    eids: list
        List of eids
    """
    main_df = utils.get_columns(main_filename, keys, delimiter=delimiter).set_index('eid')
    main_df.columns = "t" + main_df.columns.str.replace('-', '_')
    main_df.columns = main_df.columns.str.replace('.', '_')
    #print("dat: {}".format(main_df))
    #print("cols: {}".format(main_df.columns))
    # print("query: {}".format(query))
    filtered_eids = main_df.query(query)#.reset_index()['eid'].tolist()
    if return_df:
        return filtered_eids.reset_index()
    else:
        return filtered_eids.reset_index()['eid'].tolist()

def get_inverse_cohort(main_filename: str, eids: list) -> list:
    """Returns list of remaining eids.

    Keyword arguments:
    ------------------
    main_filename: str
        path to main dataframe
    eids: list
        list of eids in cohort

    Returns:
    --------
    eids: list
    """

    main_df = pd.read_csv(main_filename)
    main_eids = main_df.eid
    return list(set(main_eids) - set(eids))

def _construct_renaming_dict(columns: list, delimiter: str) -> (dict, list):
    """Returns dictionary to rename columns.

    Creates dictionary for renaming. Used internally to reformat main dataframe.

    Keyword arguments:
    ------------------
    columns: list[str]
        columns to be renamed
    delimiter: str
        delimiter to split column names

    Returns:
    --------
    (out, numbers): (dict, list)
        out: dictionary to be used for renaming of the columns
        numbers: list[str] of appendices
    """
    out = dict()
    numbers = []
    for c in columns:
        if c == 'eid':
            out[c] = 'eid'
        else:
            out[c] = c.split(delimiter)[-1]
            numbers.append(c.split(delimiter)[-1])
    return out, numbers

def _create_mds_query(main_filename: str,  entries: list, logic: str, delimiter: str=',') -> str:
    """Returns query for main dataset.

    Keyword arguments:
    ------------------
    entries: list[tuples]
        each tuple consists of field and code
    logic: str
        one of "all_of", "any_of", "none_of"

    Returns:
    --------
    query: str

    """

    updated_entries = _create_main_query_updates(main_filename, entries, delimiter=delimiter)
    query = ""
    updated2_entries = [str(f"({code})") for field, code in updated_entries if code]
    if logic == "all_of":
        query = " and ".join(updated2_entries)
    elif logic == "any_of" or logic == "none_of":
        query = " or ".join(updated2_entries)
    return query


def _create_col_query(columns: list, value: str) -> str:
    """Returns query string for all column variations corresponding to all column_keys in 'keys' using value 'value'.

    Keyword arguments:
    ------------------
    columns: list[str]
        list of keys from the main dataset
    value: str
        target value for each column
    logic: str
        on of "all_of", "any_of", "none_of"


    Returns:
    --------
    query: str

    """

    query = ""
    columnvals = [f"{col}.notnull()" if value == 'not null' else f"{col} == '{value}'" for col in columns]
    query = " or ".join(columnvals)
    return query
