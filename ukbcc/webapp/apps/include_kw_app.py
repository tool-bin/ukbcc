import dash
from ukbcc.webapp.app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd
import dash_table
import json

#Keyword search tab
tab_include_content = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Specify fields to include in cohort", className="card-text"),
            dbc.Row(id='include_fields_tab'),
            html.H3("--")
        ]
    ),
    className="mt-3",
)

@app.callback(
    Output('include_fields_tab', 'children'),
    [Input('kw_search', 'data')]
    )
def show_candidates(candidate_df_json: dict):
    """Show selected terms for a phenotype.

    Keyword arguments:
    ------------------
    candidate_df_json: dict
        seleted terms from results returned by keyword search

    Returns:
    --------
    :html objects
        data_table object containing select terms results


    """
    if candidate_df_json and len(candidate_df_json)>100:
        candidate_df = pd.read_json(candidate_df_json)
        return dbc.Row(
            dbc.Col([
                dbc.Row([
                    dbc.Button("Select All", id={'type':'select_btn', 'name':'select'}, style={"margin": "5px"}),
                    dbc.Button("Deselect All", id={'type':'select_btn', 'name':'deselect'}, style={"margin": "5px"})
                ])
                ,
                dbc.Row(
                    dash_table.DataTable(id='include_table',
                                         columns=[{"name": i, "id": i} for i in candidate_df.columns],
                                         data=candidate_df.to_dict('records'),
                                         row_selectable='multi',
                                         filter_action='native')
                )
            ]))

@app.callback(
    [Output(component_id="include_table", component_property="selected_rows")],
    [Input({'type': 'select_btn', 'name': ALL}, "n_clicks")],
    [State(component_id="include_table", component_property="derived_virtual_data"),
     State(component_id="include_table", component_property="selected_rows"),
     State(component_id="include_table", component_property="derived_viewport_selected_rows"),
     State(component_id="include_table", component_property="derived_virtual_selected_rows")]
)
def select_all(n_clicks: int, rows: dict, selected_rows: list, derived_viewport_indices: list, derived_virtual_indices: list):
    """Select all terms from data table.

    Keyword arguments:
    ------------------
    n_clicks: int
        indicates how many times select_btn is clicked
    rows: dict
        data from keyword search
    selected_rows: list
        selected rows
    derived_viewport_indices: list
        currently showing row indices
    derived_virtual_indices: list
        virtual row indices

    Returns:
    --------
    select_rows: list
        selected rows

    """

    ctx = dash.callback_context

    #Figure out which button was pressed
    calling_button="select"
    if ctx.triggered and ctx.triggered[0]['value']:
        calling_button = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['name']

    #Take action
    if selected_rows is None or calling_button == 'deselect':
        select_rows= [[]]
    else:
        select_rows = [[i for i in range(len(rows))]]
    return select_rows
