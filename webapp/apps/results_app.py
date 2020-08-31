import dash
from app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import pandas as pd
import os
from pathlib import Path

from ukbcc import query, utils, stats

from dash.exceptions import PreventUpdate

cohort_ids_out = dbc.Form(
    [
        dbc.FormGroup(
        [
            dbc.Label("Cohort IDs File (path)", html_for={"type": "config_input","name":"cohort_ids_outfile"}),
            dbc.Input(placeholder="Name and path of the file to write cohort IDs to",
                                          type="text", id="cohort_ids_outfile", persistence=False, style={"margin": "5px"}),
            dbc.FormText("Specify the name and path of file to write cohort IDs to e.g /data/cohort_ids.txt", color="secondary"),
            dbc.FormFeedback(
                    children="File saved successfully", id="valid_feedback", valid=True
                ),
            dbc.FormFeedback(
                children="Invalid path or filename provided, please provide valid path and filename", id="invalid_feedback", valid=False
            )
        ],
        className='mr-3',
    ),
    dbc.Button(children="Save", color="success", id="save_cohort_ids_button", className="ml-auto", style={"margin":"5px", "display":"block"}),
    ],
)

tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Cohort Search Results", className="card-text"),
            # html.P("Please find the results of your cohort search below", className="card-text"),
            dbc.Row(id='history_results', align='center'),
            html.Div([
                dbc.Button("Save cohort IDs", color='success', id="save_cohort_ids_modal_btn", style={"margin": "5px"})
            ]),
            dbc.Row(dbc.Col(id='save_id_status'), align='center'),
            html.Div([
               dbc.Button("Previous", color='primary', id={"name":"prev_button_results","type":"nav_btn"}, style={"margin": "5px"}),
            ]),
            dbc.Modal(
                [
                    dbc.ModalHeader("Write cohort IDs to file"),
                    dbc.ModalBody(cohort_ids_out, id="write_cohort_file_modal", style={"overflow-wrap": "break-word"}),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close_cohort_file_modal_btn", className="ml-auto", style={"margin": "5px"})
                        # dbc.Button("Save", id="save_cohort_ids_button", color="success", className="ml-auto", style={"margin": "5px"}),
                    ),
                ],
                id="save_cohort_ids_modal",
                size="lg"),
        ]
    ),
    className="mt-3",
)

def toggle_modals(n1, n2, n3, is_open):
    if n1 or n3:
        return not is_open
    return is_open

# @app.callback(
#     [Output("cohort_ids_outfile", "valid"), Output("cohort_ids_outfile", "invalid")],
#     [Input("email-input", "value")],
# )
# def check_validity(text):
#     if text:
#         is_gmail = text.endswith("@gmail.com")
#         return is_gmail, not is_gmail
#     return False, False

@app.callback(
    [Output("save_cohort_ids_modal", "is_open"),
    Output("save_id_status", "children"),
    Output("cohort_ids_outfile", "valid"),
    Output("cohort_ids_outfile", "invalid")],
    [Input("save_cohort_ids_modal_btn", "n_clicks"),
    Input("save_cohort_ids_button", "n_clicks"),
    Input("close_cohort_file_modal_btn", "n_clicks")],
    # Input("cohort_ids_outfile", "value")],
     # Input("", "n_clicks")],
    [State("config_store","data"),
    State("cohort_id_results", "data"),
    State("cohort_ids_outfile", "value"),
    State("save_cohort_ids_modal", "is_open")],
)
def save_cohort_ids(n1, n2, n3, config_init, cohort_ids, outfile, is_open):
    print("outfile {}".format(outfile))
    ctx = dash.callback_context
    # On initialisation, don't run this. Dictionary may not be populated yet
    if not ctx.triggered or not ctx.triggered[0]['value']:
        raise PreventUpdate

    print("checking button clicks - save cohort ids modal {}, save to file button {}, close cohort ids modal {}".format(n1, n2, n3))
    write_out_status = ""
    if not cohort_ids:
        write_out_status = "No results have been returned, please run a cohort search by navigating to the Configure tab."
        return False, write_out_status, False, False
    if outfile:
        print("outfile has been set to {}".format(outfile))
        write_out_status = "Wrote cohort IDs successfully to {}".format(outfile)
        try:
            outfile_path = Path(outfile)
            print("outfile_path is {}".format(outfile_path))
            os.path.exists(outfile_path.parent)
        except FileNotFoundError as fe:
            write_out_status = "outfile path parent directory does not exists, caused following exception {}".format(fe)
            print(write_out_status)
        print("cohort id results {}".format(cohort_ids))
        if n2:
            print("keeping modal open is close button has not been clicked")
            try:
                utils.write_txt_file(outfile, cohort_ids)
            except Exception as e:
                write_out_status = "failed to write cohort ids to file, caused following exception {}".format(e)
            try:
                os.path.exists(outfile_path)
            except Exception as e:
                write_out_status = "could not find cohort_ids file under path {}".format(outfile_path)
    elif not outfile and n2:
            write_out_status = "No path or filename provided, please input valid path and filename by clicking the Save cohort IDs button."
    #     if n2:
    #         wrjite_out_status = "No outfile name provided - please enter name in text box"
    #         return True, "", False, True #write_out_status

    check = toggle_modals(n1, n2, n3, is_open)
    print("check for toggel modals", check)
    return check, write_out_status, False, False
    # if n1:
    #     return True, ""
    # if n2:
    #     return True, "Please provide the path and name of file to write cohort IDs to"
    # if n3:
    #     return False, ""
        # check = toggle_modals(n1, n3, is_open)
        # return check, ""


# @app.callback(
#     Output("save_cohort_ids_modal", "is_open"),
#     [Input("save_cohort_ids_button", "n_clicks"),
#     Input("cohort_ids_outfile", "value")],
#     [State("config_store", "data")]
# )
# def save_cohort_ids(button, config_input, config_init):
#     ctx = dash.callback_context
#     # On initialisation, don't run this. Dictionary may not be populated yet
#     if not ctx.triggered or not ctx.triggered[0]['value']:
#         raise PreventUpdate
#
#     config = config_init or {}
#
#     if ctx.triggered and ctx.inputs_list and ctx.inputs_list[0]:
#         # Convert input set of patterns into a dictionary
#         # Use the results to write config dict
#         print("saving cohort ids {}".format(ctx.inputs_list))
#
#         for field in ctx.inputs_list[0]:
#             config_id_dict = field
#             # If we have a value for some path, add it
#             if 'value' in config_id_dict:
#                 config[config_id_dict['id']['name']]=config_id_dict['value']
#         print("config in save cohorts ids {}".format(config))
#     #     return config
#     # return config

@app.callback(
    [Output("history_results", "children")],
    [Input("cohort_id_results", "modified_timestamp")],
    [State("cohort_id_results", "data"),
     State("config_store", "data")]
)
def return_results(results_returned, results, config):
    if results_returned:
        output_text = dbc.Col([html.P(f"Found {len(results)} matching ids.")])
    else:
        output_text = dbc.Col([html.P("No results, please run a cohort search by navigating to the Configure tab.")])
        button = ""
    return [output_text]
