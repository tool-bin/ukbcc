import dash
from app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import pandas as pd
import os

from ukbcc import query, utils, stats

from dash.exceptions import PreventUpdate

tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Cohort Search Results", className="card-text"),
            # html.P("Please find the results of your cohort search below", className="card-text"),
            dbc.Row(id='history_results', align='center'),
            html.Div([
               dbc.Button("Previous", color='primary', id={"name":"prev_button_results","type":"nav_btn"}, style={"margin": "5px"}),
            ]),

        ]
    ),
    className="mt-3",
)

@app.callback(
    [Output("history_results", "children")],
    [Input("cohort_id_results", "modified_timestamp")],
    [State("cohort_id_results", "data"),
     State("config_store", "data")]
)
def return_results(results_returned, results, config):
    # ctx = dash.callback_context
    # if not ctx.triggered:
    #     raise PreventUpdate
    if results_returned:
        print("inside return results in results tab")
        print("results are {}".format(results[:10]))
        output_path = config['cohort_path']
        output_file = config['out_filename']
        output_text = dbc.Col([html.P(f"Found {len(results)} matching ids. Please find the IDs for cohort in the following file: {os.path.join(output_path, output_file)}")])
    else:
        output_text = dbc.Col([html.P("No results, please run a cohort search by navigating to the Configure tab.")])
    return [output_text]
