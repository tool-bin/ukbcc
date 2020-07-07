import pandas as pd
import numpy as np
from . import utils


def compute_stats(main_filename: str, eids: list, showcase_filename: str, coding_filename: str,
                  column_keys: list = ['34-0.0', '52-0.0', '22001-0.0', '21000-0.0', '22021-0.0']) \
                  -> (dict, pd.DataFrame):
    """Returns basic statistics for given columns and a translated dataframe.

    Keyword arguments:
    ------------------
    main_filename: str
        path and filename of main dataset
    eids: list[str]
        list of eids
    showcase_filename: str
        path and filename of showcase file
    coding_filename: str
        path and filename of coding file
    column_keys: list[str]
        list of column keys to include from the main dataset

    Returns:
    --------
    (stats_dict, translated_df): (dict, pd.DataFrame)
        stats_dict is a dictionary with one entry per column and the fields: type, status, stats_table,
        `stats_table`: pd.Series with statistics
        `status`: str, with success or error message
        `type`: description of the table type
        translation_df is the extraction of the relevant columns and decoded values
    """

    # get relevant columns
    translation_df = utils.quick_filter_df(main_filename=main_filename, eids=eids)
    translation_df = translation_df.filter(items=column_keys)

    # create dictionary that contains all codes
    field_dict = dict()
    showcase = pd.read_csv(showcase_filename, dtype='string')
    coding = pd.read_csv(coding_filename, dtype='string')
    codes = []

    for field in column_keys:
        field = field.split('-')[0]
        field_dict[field] = dict()
        try:
            field_dict[field]['name'] = showcase.query('FieldID == "{}"'.format(field))['Field'].values[0]
        except:
            field_dict[field]['name'] = field
        try:
            field_dict[field]['coding'] = int(showcase.query('FieldID == "{}"'.format(field))['Coding'].values[0])
            codes.append(int(showcase.query('FieldID == "{}"'.format(field))['Coding'].values[0]))
        except:
            field_dict[field]['coding'] = np.nan
        try:
            field_dict[field]['type'] = showcase.query('FieldID == "{}"'.format(field))['ValueType'].values[0]
        except:
            field_dict[field]['type'] = np.nan

    # create coding dictionary for values
    coding_dict = dict()
    for col in set(codes):
        relevant_df = coding.query('Coding == "{}"'.format(col))
        coding_dict['{}'.format(col)] = dict(zip(relevant_df.Value, relevant_df.Meaning))

    # create dictionary to rename columns
    rename_dict = dict()
    for col in translation_df.columns:
        rename_dict[col] = col.split('-')[0]

    # rename columns
    translation_df = translation_df.rename(columns=rename_dict)

    # replace values
    for col in translation_df.columns:
        col_type = field_dict[col]['type']
        coding_scheme = field_dict[col]['coding']

        print(f'{col}, {col_type}, {coding_scheme}')
        if col_type in ['Integer', 'Categorical single']:
            translation_df[col] = translation_df[col].astype(pd.Int32Dtype()).astype(str)
        if not pd.isna(coding_scheme):
            if str(coding_scheme) in coding_dict.keys():
                translation_df[col] = translation_df[col].map(coding_dict[f"{coding_scheme}"])

    name_dict = dict()
    statistics_dict = dict()

    for col in translation_df.columns:
        try:
            name_dict[col] = field_dict[col]['name']
            statistics_dict[field_dict[col]['name']] = {}
        except:
            name_dict[col] = col
            statistics_dict[col] = {}

    # understand column types to extract meaningful statistics
    for col in translation_df.columns:
        col_type = field_dict[col]['type']
        if col_type in ['Integer', 'Continuous']:
            translation_df[col] = pd.to_numeric(translation_df[col], errors='coerce')
            statistics_dict[field_dict[col]['name']]['type'] = 'Pandas describe'
            statistics_dict[field_dict[col]['name']]['status'] = 'success'
            statistics_dict[field_dict[col]['name']]['stats_table'] = translation_df[col].describe()
        elif col_type in ['Date', 'Time']:
            translation_df[col] = pd.to_datetime(translation_df[col], errors='coerce')
            statistics_dict[field_dict[col]['name']]['type'] = 'Pandas describe'
            statistics_dict[field_dict[col]['name']]['status'] = 'success'
            statistics_dict[field_dict[col]['name']]['stats_table'] = translation_df[col].describe()
        elif col_type in ['Categorical multiple', 'Text', 'Compound']:
            statistics_dict[field_dict[col]['name']]['type'] = 'NA'
            statistics_dict[field_dict[col]['name']][
                'status'] = f'ERROR: stats on {col_type} data currently not supported'
            statistics_dict[field_dict[col]['name']]['stats_table'] = pd.DataFrame()
        else:
            statistics_dict[field_dict[col]['name']]['type'] = 'Value count'
            statistics_dict[field_dict[col]['name']]['status'] = 'success'
            statistics_dict[field_dict[col]['name']]['stats_table'] = translation_df[col].value_counts(normalize=False)

    # rename columns to make them more readable
    translation_df = translation_df.rename(columns=name_dict)

    return statistics_dict, translation_df