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
            dbc.FormText("Specify the name and path of file to write cohort IDs to e.g /data/cohort_ids.txt", color="secondary")
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

@app.callback(
    [Output("save_cohort_ids_modal", "is_open"),
    Output("save_id_status", "children")],
    [Input("save_cohort_ids_modal_btn", "n_clicks"),
    Input("save_cohort_ids_button", "n_clicks"),
    Input("close_cohort_file_modal_btn", "n_clicks")],
    [State("config_store","data"),
    State("cohort_id_results", "data"),
    State("cohort_ids_outfile", "value"),
    State("save_cohort_ids_modal", "is_open")],
)
def save_cohort_ids(n1: int, n2: int, n3: int, config_init: dict, cohort_ids: list, outfilename: str, is_open: bool):
    """Handler to save cohort IDs to text file.

    Keyword arguments:
    ------------------
    n1: int
        indicates number of clicks of "save_cohort_ids_modal_btn"
    n2: int
        indicates number of clicks of "save_cohort_ids_btn"
    n3: int
        indicates number of clicks of "close_cohort_file_modal_btn"
    config_init: dict
        contains configuration file paths
    cohort_ids: list
        contains cohort IDs found after performing cohort search
    outfilename: str
        name of file to write cohort IDs to
    is_open: bool
        indicates with "save_cohort_ids_modal" is open

    Returns:
    --------
    check: bool
        indicates with "save_cohort_ids_modal" is open
    write_out_status: str
        indicates if cohort IDs file has been created

    """
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']:
        raise PreventUpdate

    write_out_status = ""
    if not cohort_ids:
        write_out_status = "No results have been returned, please run a cohort search by navigating to the Configure tab."
        return False, write_out_status
    if outfilename:
        write_out_status = "Wrote cohort IDs successfully to {}".format(outfilename)
        try:
            outfile_path = config_init['cohort_path']
            os.path.exists(outfile_path)
        except FileNotFoundError as fe:
            write_out_status = "outfile path parent directory does not exists, caused following exception {}".format(fe)
        if n2:
            try:
                outfile = os.path.join(outfile_path, outfilename)
                utils.write_txt_file(outfile, cohort_ids)
            except Exception as e:
                write_out_status = "failed to write cohort ids to file, caused following exception {}".format(e)
    elif not outfilename and n2:
            write_out_status = "No path or filename provided, please provide valid path and filename by clicking the Save cohort IDs button."
    check = toggle_modals(n1, n2, n3, is_open)
    return check, write_out_status


@app.callback(
    [Output("history_results", "children")],
    [Input("cohort_id_results", "modified_timestamp")],
    [State("cohort_id_results", "data"),
     State("config_store", "data")]
)
def return_results(results_returned: int, results: list, config: dict):
    """Check whether results were returned from cohort search.

    Keyword arguments:
    ------------------
    results_returned: int
        timestamp for when "cohort_id_results" store was last updated
    config: dict
        contain configuration file paths

    Returns:
    --------
    output_text: str
        indicates whether results were returned by cohort search

    """
    if results_returned:
        output_text = dbc.Col([html.P(f"Found {len(results)} matching ids.")])
    else:
        output_text = dbc.Col([html.P("No results, please run a cohort search by navigating to the Configure tab.")])
        button = ""
    return [output_text]
