from app import app

import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import os
import json
from ukbcc import query, utils
#
# Configuration Tab
# TODO: Use form group https://dash-bootstrap-components.opensource.faculty.ai/docs/components/form/

main_path_input = dbc.FormGroup([
        dbc.Label("Main Dataset (path)", html_for={"type":"config","name":"main_path"}),
        dbc.Input(placeholder="Specify the name and path to main dataset file e.g /data/main.csv", type="text", id={"type":"config","name":"main_path"}, persistence=True),
        dbc.FormText("Specify the name and path to main dataset file", color="secondary")
])

gp_path_input = dbc.FormGroup([
        dbc.Label("GP Dataset (path)", html_for={"type":"config", "name":"gp_path"}),
        dbc.Input(placeholder="Specify the name and path to GP data file e.g /data/gp_clinical.txt", type="text", id={"type":"config", "name":"gp_path"}, persistence=True),
        #dbc.Input(type="file", id={"type": "file", "name": "gp_path"},),
        dbc.FormText("Specify the name and path to GP data file", color="secondary")
])

showcase_path_input = dbc.FormGroup([
        dbc.Label("Showcase Dataset (path)", html_for={"type": "config", "name": "showcase_path"}),
        dbc.Input(placeholder="Specify the name and path to the showcase data csv file e.g /data/Data_Dictionary_Showcase.csv.", type="text", id={"type": "config", "name": "showcase_path"},
        persistence=True),
        dbc.FormText("Path to data showcase csv file. This file can be downloaded here: https://biobank.ctsu.ox.ac.uk/~bbdatan/Data_Dictionary_Showcase.csv", color="secondary")
])

codings_path_input = dbc.FormGroup([
        dbc.Label("Codings Dataset (path)", html_for={"type": "config", "name":"codings_path"}),
        dbc.Input(placeholder="Specify the name and path to the readcodes csv file e.g /data/Codings_Showcase.csv.", type="text", id={"type": "config", "name": "codings_path"},
        persistence=True),
        dbc.FormText("Path to read codes csv file, This file can be downloaded here: https://biobank.ctsu.ox.ac.uk/~bbdatan/Codings_Showcase.csv", color="secondary")
])

tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Settings", className="card-text"),
            dbc.Form([main_path_input,
                      gp_path_input,
                      showcase_path_input,
                      codings_path_input
                      ]),

            dbc.Row([
                dbc.Button("Check paths", color="success", id="open_checkpath_modal_btn")#,
                ]),
            # dbc.Row([
            #     dbc.Button("Write configuration to file", color="success", id="save_config_modal_btn")#,
            #     #dbc.Input(placeholder="GP Path", type="text",disabled='true',        id={"type":"config", "name":"gp_path"}, persistence=True)
            #     ]),
            # dbc.Button("Load configuration from file", color="success", id="upload_config_btn"),
            dbc.Row([dbc.Button("Next", color='primary', id={"name":"next_button_config","type":"nav_btn"})]),

            dbc.Modal(
                [
                    dbc.ModalHeader("Check paths"),
                    dbc.ModalBody(id="pathcheck_modalbody", style={"overflow-wrap": "break-word"}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close_checkpath_modal_btn", className="ml-auto")
                    ),
                ],
                id="checkpath_modal"),
            dbc.Modal(
                [
                    dbc.ModalHeader(""),
                    dbc.ModalBody(id="saveconfig_modalbody"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close_saveconfig_modal_btn", className="ml-auto")
                    ),
                ],
                id="saveconfig_modal")
        ]
    ),
    className="mt-3",
)

def toggle_modals(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# @app.callback(
#     Output("saveconfig_modalbody", "children"),
#     [Input("save_config_modal_btn", "n_clicks")],
#     # Input({'type': 'config', 'name': ALL}, "value")]
#     [State({'type': 'config', 'name': "main_path"}, "value"),
#      State({'type': 'config', 'name': "gp_path"}, "value"),
#      State({'type': 'config', 'name': "cohort_path"}, "value"),
#      State({'type': 'config', 'name': "out_filename"}, "value")]
#     # [State({"config_store"}, "data")]
# )
# def write_config_check(n_click, main_path, gp_path, cohort_path, out_filename):
#
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         raise PreventUpdate
#
#     check = utils.write_config(cohort_path, main_path, gp_path, cohort_path, out_filename)
#     return dbc.Row(
#                 dbc.Col([
#                     html.P(check)
#                 ]))

# @app.callback(
#     Output("saveconfig_modal", "is_open"),
#     [Input("save_config_modal_btn", "n_clicks"),
#      Input("close_saveconfig_modal_btn", "n_clicks")],
#     [State("saveconfig_modal", "is_open")],
# )
# def check(n1, n2, is_open):
#     check = toggle_modals(n1, n2, is_open)
#     return check
#
# When we hit the check paths button, print a modal stating whether the given paths are reasonable
@app.callback(
    Output("pathcheck_modalbody", "children"),
    [Input("open_checkpath_modal_btn", "n_clicks")],
    [State({'type': 'config', 'name': "main_path"}, "value"),
     State({'type': 'config', 'name': "gp_path"}, "value"),
     State({'type': 'config', 'name': "codings_path"}, "value"),
     State({'type': 'config', 'name': "showcase_path"}, "value")]
     # State({'type': 'config', 'name': "cohort_path"}, "value")]
)
def run_checkpath_modal_check(n_click, main_path, gp_path, codings_path, showcase_path):
    if(not main_path):
        main_path=''
    if (not gp_path):
        gp_path = ''
    if (not codings_path):
        codings_path = ''
    if (not showcase_path):
         showcase_path= ''
    val_map = {True:'exists', False:'does not exist', None:'does not exist'}
    #BG: This is a bit verbose but I'm not too fussed at the moment.
    return dbc.Row(
                dbc.Col([
                    html.P("Path to main data {} ({})".format(val_map[os.path.exists(main_path)], main_path)),
                    html.P("Path to GP {} ({})".format(val_map[os.path.exists(gp_path)], gp_path)),
                    html.P("Path to showcase data {} ({})".format(val_map[os.path.exists(showcase_path)], showcase_path)),
                    html.P("Path to codings data {} ({})".format(val_map[os.path.exists(codings_path)], codings_path))
                ]))


# Open/close path check modal
# Launch a modal which tells us whether the config paths exist
# Called when we hit the check paths button or the lose button inside the modal itself.
# TODO: Change the colour of the paths
# TODO: Consider making the check happen automatically when the path is entered
@app.callback(
    Output("checkpath_modal", "is_open"),
    [Input("open_checkpath_modal_btn", "n_clicks"),
     Input("close_checkpath_modal_btn", "n_clicks")],
    [State("checkpath_modal", "is_open")],
)
def check(n1, n2, is_open):
    check = toggle_modals(n1, n2, is_open)
    return check

# Save config input
# Changes whenevery one of the config fields is altered
@app.callback(Output("config_store", "data"),
              [Input({'type': 'config', 'name': ALL}, "value")],
              [State("config_store", "data")])
#Data is a dict containing all stored data
def save_config_handler(values, config):
    ctx = dash.callback_context
    print("config_dict:{}".format(config))
    if config:
        print("config store exists")
        configdic = config
    else:
        configdic = {}
    # else:
    #     config = {}
    # config = config or {}
    # specify default path for readcodes.csv
    readcodes_path = "../data_files/readcodes.csv"
    configdic['readcodes_path'] = readcodes_path
    if ctx.triggered and ctx.inputs_list and ctx.inputs_list[0]:
        #Convert input set of patterns into a dictionary
        #Use the results to write config dict
        print(ctx.inputs_list)
        for field in ctx.inputs_list[0]:
            config_id_dict = field
            #If we have a value for some path, add it
            if('value' in config_id_dict):
                configdic[config_id_dict['id']['name']]=config_id_dict['value']
        return configdic
    return(configdic)
