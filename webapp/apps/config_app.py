from app import app

import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import wget
import os
import json
import ukbcc
from ukbcc import query, utils

main_path_input = dbc.FormGroup([
        dbc.Label("Main Dataset File", html_for={"type": "config_input","name":"main_path"}),
        dbc.Input(placeholder="Specify the name and path to main dataset file e.g /data/main.csv",
                                      type="text", id={"type": "config_input","name":"main_path"}, persistence=True, style={"margin": "5px"}),
        dbc.FormText("Specify the name and path to main dataset file", color="secondary"),
        dbc.FormFeedback(
                    "Path exists", valid=True
                ),
        dbc.FormFeedback(
                    "Path does not exist, please check path",
                    valid=False,
                )
])

gp_path_input = dbc.FormGroup([
        dbc.Label("GP Dataset File", html_for={"type": "config_input", "name":"gp_path"}),
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

aux_dir_input = dbc.FormGroup([
        dbc.Label("Directory for Auxillary Files", html_for={"type": "config_input", "name": "aux_dir_path"}),
        dbc.Input(placeholder="Specify the directory where the auxillary files should be stored e.g /data/aux_files", type="text", id={"type": "config_input", "name": "aux_dir_path"},
        persistence=True),
        dbc.FormText("Directory path to save auxillary files to. Please see the README to learn more about the auxillary files", color="secondary"),
        dbc.FormFeedback(
                    "Path exists", valid=True
                ),
        dbc.FormFeedback(
                    "Path does not exist, please check path",
                    valid=False,
                )
])
# showcase_path_input = dbc.formgroup([
#         dbc.label("showcase dataset (path)", html_for={"type": "config_input", "name": "showcase_path"}),
#         dbc.input(placeholder="specify the name and path to the showcase data csv file e.g /data/data_dictionary_showcase.csv.", type="text", id={"type": "config_input", "name": "showcase_path"},
#         persistence=true),
#         dbc.formtext("path to data showcase csv file. this file can be downloaded here: https://biobank.ctsu.ox.ac.uk/~bbdatan/data_dictionary_showcase.csv", color="secondary"),
#         dbc.formfeedback(
#                     "path exists", valid=true
#                 ),
#         dbc.formfeedback(
#                     "path does not exist, please check path",
#                     valid=false,
#                 )
# ])
#
# codings_path_input = dbc.FormGroup([
#         dbc.Label("Codings Dataset (path)", html_for={"type": "config_input", "name":"codings_path"}),
#         dbc.Input(placeholder="Specify the name and path to the readcodes csv file e.g /data/Codings_Showcase.csv.", type="text", id={"type": "config_input", "name": "codings_path"},
#         persistence=True),
#         dbc.FormText("Path to read codes csv file, This file can be downloaded here: https://biobank.ctsu.ox.ac.uk/~bbdatan/Codings_Showcase.csv", color="secondary"),
#         dbc.FormFeedback(
#                     "Path exists", valid=True
#                 ),
#         dbc.FormFeedback(
#                     "Path does not exist, please check path",
#                     valid=False,
#                 )
# ])

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


aux_file_download_modal = dbc.Modal(
                [
                    dbc.ModalHeader("Auxillary files"),
                    dbc.ModalBody(id='aux_file_modalbody'),
                    dbc.ModalFooter(
                        dbc.Button("Close", id='aux_modal_close', className="ml-auto")
                    ),
                ],
                id="aux_file_modal")

tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Settings", className="card-text"),
            html.H4("File Paths", className="card-text"),
            dbc.Form([main_path_input,
                      gp_path_input]),
            html.H4("Directory Paths", className="card-text"),
            dbc.Form([aux_dir_input,
                      cohort_path_input]),
            aux_file_download_modal,
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
    [Output({'type': 'config_input', 'name': 'main_path'}, "valid"), Output({'type': 'config_input', 'name': 'main_path'}, "invalid"),
    Output({'type': 'config_input', 'name': 'gp_path'}, "valid"), Output({'type': 'config_input', 'name': 'gp_path'}, "invalid"),
    Output({'type': 'config_input', 'name': 'aux_dir_path'}, "valid"), Output({'type': 'config_input', 'name': 'aux_dir_path'}, "invalid"),
    Output({'type': 'config_input', 'name': 'cohort_path'}, "valid"), Output({'type': 'config_input', 'name': 'cohort_path'}, "invalid")],
    [Input({'type': 'config_input', 'name': "main_path"}, "value"),
    Input({'type': 'config_input', 'name': "gp_path"}, "value"),
    Input({'type': 'config_input', 'name': "aux_dir_path"}, "value"),
    Input({'type': 'config_input', 'name': "cohort_path"}, "value")]
)
def check_validity(main_path: str, gp_path: str, aux_dir_path: str, cohort_path: str):
    """Check path validity.

    Keyword arguments:
    ------------------
    main_path: str
        path to main dataset
    gp_path: str
        path to GP Clinical dataset
    aux_dir_path: str
        path to directory to write auxillary files to
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
    aux_valid: bool
        whether auxillary directory path is valid
    aux_invalid: bool
        whether auxillary directory path is invalid
        whether showcase dataset path is invalid
    cohort_valid: bool
        whether cohort directory path is valid
    cohort_invalid: bool
        whether cohort directory path is invalid
    """
    main_valid, main_invalid = check_path_exists(main_path)
    gp_valid, gp_invalid = check_path_exists(gp_path)
    aux_valid, aux_invalid = check_path_exists(aux_dir_path)
    cohort_valid, cohort_invalid = check_path_exists(cohort_path)
    return main_valid, main_invalid, gp_valid, gp_invalid, aux_valid, aux_invalid, cohort_valid, cohort_invalid


# Save config input
# Changes whenever one of the config fields is altered
@app.callback([Output("config_store", "data"),
               Output("aux_file_modalbody", "children")],
              [Input({'type': 'config_input', 'name': ALL}, "value"),
              Input({"name": "next_button_config", "type": "nav_btn"}, "n_clicks")],
              [State("config_store", "data")]
)
def save_config_handler(values: str, n_click: int, config_init: dict):
    """Handler to save path configuration to config_store store.

    Keyword arguments:
    ------------------
    values: str
        path inputs
    n_click: int
        indicates number of clicks on "next_button_config"
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
    showcase_file = "Data_Dictionary_Showcase.csv"
    codings_file = "Codings_Showcase.csv"
    readcodes_file = "readcodes.csv"

    showcase_url = "https://biobank.ctsu.ox.ac.uk/~bbdatan/Data_Dictionary_Showcase.csv"
    readcodes_url = "https://raw.githubusercontent.com/tool-bin/ukbcc/master/data_files/readcodes.csv"
    codings_url = "https://biobank.ctsu.ox.ac.uk/~bbdatan/Codings_Showcase.csv"

    aux_files = {"showcase": {"file": showcase_file, "url":showcase_url},
                 "codings": {"file": codings_file, "url": codings_url},
                 "readcodes": {"file": readcodes_file, "url": readcodes_url}}
    # TODO: Make this readable from a config or .py file
    # config['readcodes_path'] = "../data_files/readcodes.csv"
    #temp name for file until specified later in the cohort search process
    config['out_filename'] = "cohort_ids.txt"

    if ctx.triggered and ctx.inputs_list and ctx.inputs_list[0]:
        for field in ctx.inputs_list[0]:
            config_id_dict = field
            if 'value' in config_id_dict:
                config[config_id_dict['id']['name']]=config_id_dict['value']

        required_config = set(['main_path', 'gp_path', 'aux_dir_path', 'cohort_path'])
        existing_config_fields=set(config.keys())
        missing_config_fields = required_config.difference(existing_config_fields)
        if len(missing_config_fields)!=0:
            print("Config has not been set. Missing fields: {}".format(', '.join([str(x) for x in missing_config_fields])))
            raise PreventUpdate
        else:
            aux_dir_path = config['aux_dir_path']
            output_text = "Auxillary files exists"
            for k,v in aux_files.items():
                print(f"checking if {k} exists")
                file_path = os.path.join(aux_dir_path, v["file"])
                aux_files[k]['file_path'] = file_path
                if not os.path.exists(file_path):
                    wget.download(v["url"], file_path)
                    output_text = f"Downloading auxillary files to {aux_dir_path}"
                if os.path.exists(file_path):
                    new_k = k + '_path'
                    config[new_k] = file_path
                else:
                    # raise FileNotFoundError(f'{k} file {file_path} did not download, please check')
                    output_text = f"{k} file did not download to {file_path}, please check."
        return config, output_text
    return config

# @app.callback(
#     Output("aux_file_modal", "is_open"),
#     [Input({"name": "next_button_config", "type": "nav_btn"}, "n_clicks")],
#     [State("aux_file_modal", "is_open")]
# )
# def toggle_aux_file_modal(n1: int, is_open: bool):
#     """Toggle the "aux_file_modal".
#
#     Keyword arguments:
#     ------------------
#     n_click: int
#         int specifying the number of times the "submit_btn" is clicked
#
#     Returns:
#     --------
#     is_open: bool
#          boolean specifying whether or not to show "aux_file_modal"
#
#     """
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         raise PreventUpdate
#
#     if n1 or n2 or is_open:
#         return not is_open
#     return is_open
