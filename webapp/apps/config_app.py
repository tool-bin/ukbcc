from app import app

import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import os
import json
import ukbcc
from ukbcc import query, utils
#
# Configuration Tab
# TODO: Use form group https://dash-bootstrap-components.opensource.faculty.ai/docs/components/form/

db_path_input = dbc.FormGroup([
        dbc.Label("SQLite Database (path)", html_for={"type": "config_input","name":"db_path"}),
        dbc.Input(placeholder="Specify the name and path to sqlite database e.g /data/ukb_sql.sqlite"),
                                      type="text", id={"type": "config_input","name":"db_path"}, persistence=True, style={"margin": "5px"}),
        dbc.FormText("Specify the name and path to SQLite database file", color="secondary"),
        dbc.FormFeedback(
                    "Path exists", valid=True
                ),
        dbc.FormFeedback(
                    "Path does not exist, please check path",
                    valid=False,
                )
])

gp_path_input = dbc.FormGroup([
        dbc.Label("GP Dataset (path)", html_for={"type": "config_input", "name":"gp_path"}),
        dbc.Input(placeholder="Specify the name and path to GP data file e.g /data/gp_clinical.txt", type="text", id={"type": "config_input", "name":"gp_path"}, persistence=True),
        #dbc.Input(type="file", id={"type": "file", "name": "gp_path"},),
        dbc.FormText("Specify the name and path to GP data file", color="secondary"),
        dbc.FormFeedback(
                    "Path exists", valid=True
                ),
        dbc.FormFeedback(
                    "Path does not exist, please check path",
                    valid=False,
                )
])

showcase_path_input = dbc.FormGroup([
        dbc.Label("Showcase Dataset (path)", html_for={"type": "config_input", "name": "showcase_path"}),
        dbc.Input(placeholder="Specify the name and path to the showcase data csv file e.g /data/Data_Dictionary_Showcase.csv.", type="text", id={"type": "config_input", "name": "showcase_path"},
        persistence=True),
        dbc.FormText("Path to data showcase csv file. This file can be downloaded here: https://biobank.ctsu.ox.ac.uk/~bbdatan/Data_Dictionary_Showcase.csv", color="secondary"),
        dbc.FormFeedback(
                    "Path exists", valid=True
                ),
        dbc.FormFeedback(
                    "Path does not exist, please check path",
                    valid=False,
                )
])

codings_path_input = dbc.FormGroup([
        dbc.Label("Codings Dataset (path)", html_for={"type": "config_input", "name":"codings_path"}),
        dbc.Input(placeholder="Specify the name and path to the readcodes csv file e.g /data/Codings_Showcase.csv.", type="text", id={"type": "config_input", "name": "codings_path"},
        persistence=True),
        dbc.FormText("Path to read codes csv file, This file can be downloaded here: https://biobank.ctsu.ox.ac.uk/~bbdatan/Codings_Showcase.csv", color="secondary"),
        dbc.FormFeedback(
                    "Path exists", valid=True
                ),
        dbc.FormFeedback(
                    "Path does not exist, please check path",
                    valid=False,
                )
])

cohort_path_input = dbc.FormGroup([
        dbc.Label("Directory for Output Files (path)", html_for={"type": "config_input", "name":"cohort_path"}),
        dbc.Input(placeholder="Specify the directory to save the output files to e.g /data/ukbcc_output.", type="text", id={"type": "config_input", "name": "cohort_path"},
        persistence=True),
        dbc.FormText("Directory path to save output files to", color="secondary"),
        dbc.FormFeedback(
                    "Path exists", valid=True
                ),
        dbc.FormFeedback(
                    "Path does not exist, please check path",
                    valid=False,
                )
])


tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Settings", className="card-text"),
            dbc.Form([db_path_input,
                      gp_path_input,
                      showcase_path_input,
                      codings_path_input,
                      cohort_path_input
                      ]),

            dbc.Row([dbc.Button("Next", color='primary', id={"name":"next_button_config","type":"nav_btn"}, style={"margin": "5px"})]),
        ]
    ),
    className="mt-3",
)

def toggle_modals(n1: int, n2: int, is_open: bool):
    if n1 or n2:
        return not is_open
    return is_open

def check_path_exists(path: str):
    if path:
        is_path = os.path.exists(path)
        return is_path, not is_path
    return False, False


@app.callback(
    [Output({'type': 'config_input', 'name': 'db_path'}, "valid"), Output({'type': 'config_input', 'name': 'db_path'}, "invalid"),
    Output({'type': 'config_input', 'name': 'gp_path'}, "valid"), Output({'type': 'config_input', 'name': 'gp_path'}, "invalid"),
    Output({'type': 'config_input', 'name': 'codings_path'}, "valid"), Output({'type': 'config_input', 'name': 'codings_path'}, "invalid"),
    Output({'type': 'config_input', 'name': 'showcase_path'}, "valid"), Output({'type': 'config_input', 'name': 'showcase_path'}, "invalid"),
    Output({'type': 'config_input', 'name': 'cohort_path'}, "valid"), Output({'type': 'config_input', 'name': 'cohort_path'}, "invalid")],
    [Input({'type': 'config_input', 'name': "db_path"}, "value"),
    Input({'type': 'config_input', 'name': "gp_path"}, "value"),
    Input({'type': 'config_input', 'name': "codings_path"}, "value"),
    Input({'type': 'config_input', 'name': "showcase_path"}, "value"),
    Input({'type': 'config_input', 'name': "cohort_path"}, "value")]
)
def check_validity(db_path: str, gp_path: str, codings_path: str, showcase_path: str, cohort_path: str):
    """Check path validity.

    Keyword arguments:
    ------------------
    db_path: str
        path to main dataset
    gp_path: str
        path to GP Clinical dataset
    codings_path: str
        path to codings dataset
    showcase_path: str
        path to showcase dataset
    cohort_path: str
        path to directory to write output files to

    Returns:
    --------
    main_valid: bool
        whether main dataset path is valid
    main_invalid: bool
        whether main dataset path is invalid
    gp_valid: bool
        whether GP Clinical dataset path is valid
    gp_invalid: bool
        whether GP Clinical dataset path is invalid
    codings_valid: bool
        whether codings dataset path is valid
    codings_invalid: bool
        whether codings dataset path is invalid
    showcase_valid: bool
        whether showcase dataset path is valid
    showcase_invalid: bool
        whether showcase dataset path is invalid
    cohort_valid: bool
        whether cohort directory path is valid
    cohort_invalid: bool
        whether cohort directory path is invalid
    """
    main_valid, main_invalid = check_path_exists(db_path)
    gp_valid, gp_invalid = check_path_exists(gp_path)
    codings_valid, codings_invalid = check_path_exists(codings_path)
    showcase_valid, showcase_invalid = check_path_exists(showcase_path)
    cohort_valid, cohort_invalid = check_path_exists(cohort_path)
    return main_valid, main_invalid, gp_valid, gp_invalid, codings_valid, codings_invalid, showcase_valid, showcase_invalid, cohort_valid, cohort_invalid


# Save config input
# Changes whenever one of the config fields is altered
@app.callback(Output("config_store", "data"),
              [Input({'type': 'config_input', 'name': ALL}, "value")],
              [State("config_store", "data")])
#Data is a dict containing all stored data
def save_config_handler(values: str, config_init: dict):
    """Handler to save path configuration to config_store store.

    Keyword arguments:
    ------------------
    values: str
        path inputs
    config_init: dict
        config_store store

    Returns:
    --------
    config: dict
        config with updated input paths

    """
    ctx = dash.callback_context

    if not ctx.triggered or not ctx.triggered[0]['value']:
        raise PreventUpdate

    config = config_init or {}

    # TODO: Make this readable from a config or .py file
    config['readcodes_path'] = "../data_files/readcodes.csv"
    #temp name for file until specified later in the cohort search process
    config['out_filename'] = "cohort_ids.txt"

    if ctx.triggered and ctx.inputs_list and ctx.inputs_list[0]:
        for field in ctx.inputs_list[0]:
            config_id_dict = field
            if 'value' in config_id_dict:
                config[config_id_dict['id']['name']]=config_id_dict['value']
        return config
    return config
