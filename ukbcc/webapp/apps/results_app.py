import dash
from ukbcc.webapp.app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import dash_table
import pandas as pd
import os
import json
from pathlib import Path
import plotly

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
            html.H3("Cohort Search Results Report", className="card-text"),
            html.Div(id='history_results_report'),
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

def _create_table(table_dictionary: dict, c: int):
    """Create data_table object from json-encoded table.

    Keyword Arguments:
    ------------------
    table_dictionary: dict
        dictionary containing table contents
    c: int
        counter to assign ID to table object

    Returns:
    --------
    table: html.Div
        html.Div object containing data_table object
    """
    df = pd.DataFrame.from_dict(table_dictionary)
    table = html.Div([dash_table.DataTable(
        id=f'table_{c}',
        columns=[{"name": i, "id": i} for i in df.columns],
        css=[{'selector': '.dash-filter input', 'rule': 'text-align: left'}, {'selector': '.row', 'rule': 'margin: 0'}],
        style_cell={
                'whiteSpace': 'normal',
                'height': 'auto',
                'text-align': 'left'
        },
        data=df.to_dict('records'))])
    return table

def _create_graph(graph_dictionary: dict, c: int):
    """Create Graph object from json-encoded plotly object.

    Keyword Arguments:
    ------------------
    graph_dictionary: dict
        dictionary containing json-encoded plotly object
    c: int
        counter to assign id to graph object

    Returns:
    --------
    table: html.Div
        html.Div object containing Graph object
    """
    fig = plotly.io.from_json(graph_dictionary)
    fig_report = html.Div([dcc.Graph(id=f'graph_{c}', figure=fig)])
    return fig_report


@app.callback(
    [Output("history_results", "children"),
     Output("history_results_report", "children")],
    [Input("cohort_id_results", "modified_timestamp")],
    [State("cohort_id_results", "data"),
     State("cohort_id_report", "data"),
     State("config_store", "data")]
)
def return_results(results_returned: int, results: list, cohort_id_report: dict, config: dict):
    """Check whether results were returned from cohort search.

    Keyword arguments:
    ------------------
    results_returned: int
        timestamp for when "cohort_id_results" store was last updated
    results: list
        list of cohort IDs
    cohort_id_report: dict
        dict of figures generated by "compute_stats" function in stats module
    config: dict
        contain configuration file paths

    Returns:
    --------
    output_text: dbc object
        indicates whether results were returned by cohort search
    stats_report: dbc object
        dbc object containing list of figures describing cohort

    """
    if results_returned:
        output_text = dbc.Col([html.P(f"Found {len(results)} matching ids.")])
        stats_report = []
        if cohort_id_report:
            c = 0
            overview = cohort_id_report['tables'].pop(0)
            table = _create_table(overview, c)
            stats_report.append(table)
            for t, g in zip(cohort_id_report['tables'], cohort_id_report['graphs']):
                table = _create_table(t, c)
                fig_report = _create_graph(g, c)
                stats_report.append(fig_report)
                stats_report.append(table)
                c += 1
        final = html.Div(stats_report)
    else:
        output_text = dbc.Col([html.P("No results, please run a cohort search by navigating to the Configure tab.")])
        final = []
    return [output_text], [final]
