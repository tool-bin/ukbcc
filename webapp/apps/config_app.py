from app import app

import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc

import os
import json
from ukbcc import query, utils
#
# Configuration Tab
# TODO: Use form group https://dash-bootstrap-components.opensource.faculty.ai/docs/components/form/

# set default aux_path
aux_path = "./data_files"

main_dat_path_input = dbc.FormGroup([
        dbc.Label("Main Dataset (path)", html_for={"type":"config","name":"main_dat_path"}),
        dbc.Input(placeholder="Path", type="text", id={"type":"config","name":"main_dat_path"}, persistence=True),
        #dbc.Input( type="file", id={"type": "file", "name": "main_dat_path"}),
        dbc.FormText("Specify the path to main dataset (server)", color="secondary")
])

gp_dat_path_input = dbc.FormGroup([
        dbc.Label("GP data (path)", html_for={"type":"config", "name":"gp_path"}),
        dbc.Input(placeholder="Path", type="text", id={"type":"config", "name":"gp_path"}, persistence=True),
        #dbc.Input(type="file", id={"type": "file", "name": "gp_path"},),
        dbc.FormText("Specify the path to GP data (server)", color="secondary")
])
cohort_path_input = dbc.FormGroup([
        dbc.Label("Cohort output (path)", html_for={"type": "config", "name": "cohort_path"}),
        dbc.Input(placeholder="Path to Cohort", type="text", id={"type": "config", "name": "cohort_path"},
                  persistence=True),
        #dbc.Input(type="file", id={"type": "file", "name": "cohort_path"}),
        dbc.FormText("Specify the output path", color="secondary")
])
# aux_path_input = dbc.FormGroup([
#         dbc.Label("Auxillary files (path)", html_for={"type": "config", "name": "aux_path"}),
#         dbc.Input(placeholder="Path to Aux files", type="text", id={"type": "config", "name": "aux_path"},
#               persistence=True),
#         #dbc.Input(type="file", id={"type": "file", "name": "aux_path"}),
#         dbc.FormText("Specify the path to download (or with existing) auxillary files", color="secondary")
# ])
out_filename_input = dbc.FormGroup([
        dbc.Label("Output file (name)", html_for={"type": "config", "name": "out_filename"}),
        dbc.Input(placeholder="Name of file to write cohort IDs to", type="text", id={"type": "config", "name": "out_filename"},
              persistence=True),
        #dbc.Input(type="file", id={"type": "file", "name": "aux_path"}),
        dbc.FormText("Please specifiy the name of the file to write the cohort IDs to", color="secondary")
])

tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Settings", className="card-text"),

            dbc.Form([main_dat_path_input,
                        gp_dat_path_input,
                      #dbc.Row([
                      #%      dbc.Col(driver_path_input),
                      #      dbc.Col(driver_type_input)
                      #],form=True),
                      # aux_path_input,
                      cohort_path_input,
                      out_filename_input,
                     # dbc.Row([
                     #     dbc.Col(user_input),
                     #     dbc.Col(pass_input)
                     # ],form = True),
                    #app_id_input
                      ]),

            dbc.Row([
                dbc.Button("Check paths", color="success", id="open_checkpath_modal_btn")#,
                #dbc.Input(placeholder="GP Path", type="text",disabled='true',        id={"type":"config", "name":"gp_path"}, persistence=True)
                ]),
            dbc.Row([
                dbc.Button("Save configuration", color="success", id="save_config_modal_btn")#,
                #dbc.Input(placeholder="GP Path", type="text",disabled='true',        id={"type":"config", "name":"gp_path"}, persistence=True)
                ]),
            #dbc.Button("Download GP", color="success", id="download_gp_btn"),
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

@app.callback(
    Output("saveconfig_modalbody", "children"),
    [Input("save_config_modal_btn", "n_clicks")],
    # Input({'type': 'config', 'name': ALL}, "value")]
    [State({'type': 'config', 'name': "main_dat_path"}, "value"),
     State({'type': 'config', 'name': "gp_path"}, "value"),
     State({'type': 'config', 'name': "cohort_path"}, "value"),
     State({'type': 'config', 'name': "out_filename"}, "value")]
    # [State({"config_store"}, "data")]
)
def write_config_check(n_click, main_dat_path, gp_path, cohort_path, out_filename):
    check = utils.write_config(cohort_path, main_dat_path, gp_path, cohort_path, out_filename)
    return dbc.Row(
                dbc.Col([
                    html.P(check)
                ]))

@app.callback(
    Output("saveconfig_modal", "is_open"),
    [Input("save_config_modal_btn", "n_clicks"),
     Input("close_saveconfig_modal_btn", "n_clicks")],
    [State("saveconfig_modal", "is_open")],
)
def check(n1, n2, is_open):
    check = toggle_modals(n1, n2, is_open)
    return check
#
# When we hit the check paths button, print a modal stating whether the given paths are reasonable
# TODO: Add more sophisticated checks here (check for driver rather than just path)
@app.callback(
    Output("pathcheck_modalbody", "children"),
    [Input("open_checkpath_modal_btn", "n_clicks")],
    [State({'type': 'config', 'name': "main_dat_path"}, "value"),
     State({'type': 'config', 'name': "gp_path"}, "value"),
     # State({'type': 'config', 'name': "aux_path"}, "value"),
     State({'type': 'config', 'name': "cohort_path"}, "value")]
)
def run_checkpath_modal_check(n_click, main_dat_path, gp_path, cohort_path, aux_path=aux_path):
    if(not main_dat_path):
        main_dat_path=''
    if (not gp_path):
        gp_path = ''
    if (not aux_path):
        aux_path = ''
    if (not cohort_path):
        cohort_path = ''
    val_map = {True:'exists', False:'does not exist', None:'does not exist'}
    #BG: This is a bit verbose but I'm not too fussed at the moment.
    return dbc.Row(
                dbc.Col([
                    html.P("Path to main data {} ({})".format(val_map[os.path.exists(main_dat_path)], main_dat_path)),
                    html.P("Path to GP {} ({})".format(val_map[os.path.exists(gp_path)], gp_path)),
                    html.P("Path to auxillary data {} ({})".format(val_map[os.path.exists(aux_path)], aux_path)),
                    html.P("Path to output cohort info {} ({})".format(val_map[os.path.exists(cohort_path)], cohort_path))
                ]), "overflow-wrap: break-word")


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
    config = config or {}

    if ctx.triggered and ctx.inputs_list and ctx.inputs_list[0]:
        #Convert input set of patterns into a dictionary
        #Use the results to write config dict
        print (ctx.inputs_list)
        for field in ctx.inputs_list[0]:
            config_id_dict = field
            print('config_id_dict: {}'.format(field))
            print('config_id_dict type: {}'.format(type(field)))
            #If we have a value for some path, add it
            if('value' in config_id_dict):
                config[config_id_dict['id']['name']]=config_id_dict['value']
        return config
    return(config)
