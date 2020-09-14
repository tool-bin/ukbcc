import pandas as pd
import numpy as np
from . import utils
import os
import plotly.express as px
import plotly
import json


def compute_stats(main_filename: str, eids: list, showcase_filename: str, coding_filename: str,
                  column_keys: list = ['34-0.0', '52-0.0', '22001-0.0', '21000-0.0', '22021-0.0'], out_path: str="") \
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
    out_path: str
        path to store output files. If empty string, files will not be stored.

    Returns:
    --------
    (stats_dict, translated_df): (dict, pd.DataFrame)
        stats_dict is a dictionary with one entry per column and the fields: type, status, stats_table,
        `stats_table`: pd.Series with statistics
        `status`: str, with success or error message
        `type`: description of the table type
        translation_df is the extraction of the relevant columns and decoded values
    """

    if out_path == "":
        write_out = False
    else:
        write_out = True

    translation_df = utils.filter_df_columns(main_filename=main_filename, column_keys=column_keys, eids=eids)

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

        # print(f'{col}, {col_type}, {coding_scheme}')
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
            statistics_dict[field_dict[col]['name']]['stats_table'] = translation_df[col].describe().to_dict()
        elif col_type in ['Date', 'Time']:
            translation_df[col] = pd.to_datetime(translation_df[col], errors='coerce')
            statistics_dict[field_dict[col]['name']]['type'] = 'Pandas describe'
            statistics_dict[field_dict[col]['name']]['status'] = 'success'
            statistics_dict[field_dict[col]['name']]['stats_table'] = translation_df[col].describe().to_dict()
        elif col_type in ['Categorical multiple', 'Text', 'Compound']:
            statistics_dict[field_dict[col]['name']]['type'] = 'NA'
            statistics_dict[field_dict[col]['name']]['data_type'] = col_type
            statistics_dict[field_dict[col]['name']][
                'status'] = f'ERROR: stats on {col_type} data currently not supported'
            statistics_dict[field_dict[col]['name']]['stats_table'] = pd.DataFrame().to_dict()
        else:
            statistics_dict[field_dict[col]['name']]['data_type'] = col_type
            statistics_dict[field_dict[col]['name']]['type'] = 'Value count'
            statistics_dict[field_dict[col]['name']]['status'] = 'success'
            statistics_dict[field_dict[col]['name']]['stats_table'] = translation_df[col].value_counts(normalize=False).to_dict()

    # rename columns to make them more readable
    translation_df = translation_df.rename(columns=name_dict)
    if write_out:
        utils.write_dictionary(statistics_dict, os.path.join(out_path, 'stats_dict.json'))
        translation_df.to_csv(os.path.join(out_path, 'stats_fields.csv'))

    return statistics_dict, translation_df


def create_report(translation_df: pd.DataFrame, create_html: bool=False, out_path: str="."):
    """Creates html report in out_path.

    Keyword arguments:
    ------------------
    translation_df: pd.DataFrame
        dataframe containing only the columns that need should be displayed in the stats report. Likely the output of
        compute_stats.
    create_html: bool
        determines whether to convert report to html page
    out_path: str
        path where report.html gets stored.
    """

    if "Unnamed: 0" in translation_df.columns:
        translation_df = translation_df.drop("Unnamed: 0", axis=1)

    divs = translation_df.describe(include='all')
    tables = []
    graphs = []

    tables.append(divs)

    for col in translation_df.columns:
        div_title = f"""<h2 style="font-family: sans-serif">{col}</h2>"""
        if np.issubdtype(translation_df[col].dtype, np.number):
            div_table = pd.DataFrame(pd.to_numeric(translation_df[col], errors='coerce').describe())
        elif np.issubdtype(translation_df[col].dtype, np.datetime64):
            div_table = pd.DataFrame(pd.to_datetime(translation_df[col], errors='coerce').describe())
        else:
            div_table = pd.DataFrame(translation_df[col].describe())
        div_plot = px.bar(translation_df[col].value_counts(normalize=False).reset_index(), x="index", y=col,
                          title=col)
        tables.append(div_table)
        graphs.append(div_plot)

        if create_html:
            divs_html = divs.to_html(classes='mystyle')
            div_table_html = div_table.to_html(classes='mystyle')
            div_plot_html = div_plot.to_html(classes='mystyle')

            divs_html = divs_html + div_title + div_plot_html + div_table_html

    if create_html:
        html = """\
        <html>
            <style>
                table {{
                    border: 0
                }}

                .mystyle {{
                    font-size: 11pt;
                    font-family: Arial;
                    border-collapse: collapse;
                    border: white;
                }}

                .mystyle td, th {{
                    padding: 5px;
                }}

                .mystyle tr:nth-child(even) {{
                    background: #E3E3E3;
                }}
                .mystyle tr:hover {{
                    background: silver;
                }}
            </style>
            <head>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1 style="font-family: sans-serif">Summary Statistics</h1>
            <div style="padding: 1em">
            {}
            </div>
        </body>
    </html>
    """.format(divs_html)

        with open(os.path.join(out_path, 'report.html'), 'w') as f:
            f.write(html)

    # figures = [divs.to_dict(), div_plot.to_dict(), div_table.to_dict()]
    figures_dict = {"tables": [table.to_dict() for table in tables],
                    "graphs": [plotly.io.to_json(fig) for fig in graphs]}
                    # "graphs": [json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) for fig in graphs]}

    return figures_dict
