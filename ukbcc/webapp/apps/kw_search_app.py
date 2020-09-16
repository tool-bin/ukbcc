import dash
from ukbcc.webapp.app import app

import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import os
import pandas as pd
import dash_table
from ukbcc import filter as ukbcc_filter
import json
import configparser
from dash.exceptions import PreventUpdate

#Define form inputs
kw_search_group = dbc.FormGroup(
        [
            html.H3("Specify Keywords", className="card-text"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id="keyword_input", placeholder="Specify keywords to search, separated by semicolon", type="text", persistence=False)
                ]),
                dbc.Col([
                    dbc.Button("Search", color="success", id="submit_btn")
                ]),
            ]),
            dbc.Row(id='kw_search_output_select'),
            html.Div(id='kw_search_output'),
            dbc.Modal(
                [
                    dbc.ModalHeader("Running search.."),
                    dbc.ModalBody(id="running_search_modalbody"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close_running_search_modal_btn", className="ml-auto")
                    ),
                ],
                id="running_search_modal"),
            dbc.Row(id="kw_fields_output")
        ],
    className="mt-3"
)

@app.callback(
    Output("running_search_modalbody", "children"),
    [Input("submit_btn", "n_clicks")]
)
def progress_search(n_click: int):
    """Activate "running_search_modal" modal.

    Keyword arguments:
    ------------------
    n_click: int
        int specifying the number of times the "submit_btn" is clicked

    Returns:
    --------
    modal content: dbc.Row object
         html objects to populate running_search_modalbody

    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    return dbc.Row(
                dbc.Col([
                    html.P("Search is running. Please wait..")
                ]))


@app.callback(
    Output("running_search_modal", "is_open"),
    # Output("running_search_row", "is_open"),
    [Input("submit_btn", "n_clicks"),
    # Input("close_running_search_modal_btn", "n_clicks"),
    Input("kw_search", "modified_timestamp")],
    [State("running_search_modal", "is_open")]
)
def toggle_run_query_modal(n1: int, n2: int, is_open: bool):
    """Toggle the "running_search_modal".

    Keyword arguments:
    ------------------
    n_click: int
        int specifying the number of times the "submit_btn" is clicked

    Returns:
    --------
    is_open: bool
         boolean specifying whether or not to show "running_search_modal"

    """
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if n1 or n2 or is_open:
        return not is_open
    return is_open

# Handle keyword search input
@app.callback(
    [Output('kw_search', 'data'),
    Output('kw_search_terms', 'data')],
    [Input('submit_btn', 'n_clicks')],
    [State("config_store", "data"),
    State("keyword_input", "value"),
    State("kw_search", "data")]
    )
def search_kw_button(_: int, config: dict, search_terms: list, kw_search: dict):
    """Run keyword search.

    Keyword arguments:
    ------------------
    _: int
        int specifying the number of times the "submit_btn" is clicked
    config: dict
        dictionary containing paths specified in "Configure" tab
    search_terms: list
        list of search terms to search dataframe with
    kw_search: dict
        dictionary containing returned results from keywards

    Returns:
    --------
    candidate_df: dict
         dictionary containg returned results from keyword search
    kw_search_terms: list
        list containing search terms

    """
    #Cancel if we haven't pressed the button
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    if len(ctx.triggered) and ctx.triggered[0]['prop_id']=='.':
        raise PreventUpdate

    #If we haven't clicked submit and we have a previous value, return the previous value
    if len(ctx.triggered) and ctx.triggered[0]['value'] is None and kw_search is not None:
        return (kw_search), ()

    #Show error if we haven't set any config
    if not config:
        return ("Config has not been set. Missing all fields"), ()

    #Show error if we are missing fields
    required_config = set(['main_path', 'gp_path', 'readcodes_path', 'codings_path', 'showcase_path'])
    existing_config_fields=set(config.keys())
    missing_config_fields = required_config.difference(existing_config_fields)
    if len(missing_config_fields)!=0:
        print("Config has not been set. Missing fields: {}".format(', '.join([str(x) for x in missing_config_fields])))
        raise PreventUpdate

    # Run the search
    # Show error if we haven't set any search terms
    if not search_terms or len(search_terms)==0:
        raise PreventUpdate

    #TODO: Why is delimiter semicolon, we use comma in command-line version
    search_terms = search_terms.split(';')

    coding_filename = config['codings_path']
    showcase_filename = config['showcase_path']
    readcode_filename = config['readcodes_path']

    search_df = ukbcc_filter.construct_search_df(showcase_filename=showcase_filename,
                                           coding_filename=coding_filename,
                                           readcode_filename=readcode_filename)
    candidate_df = ukbcc_filter.construct_candidate_df(searchable_df=search_df, search_terms=search_terms)
    if not search_terms:
        search_terms = []
    return (candidate_df.to_json()), (search_terms)

# Show candidate search terms
@app.callback(
    [Output('kw_search_output_select', 'children'),
    Output('kw_search_output', 'children'),
    Output('find_terms_modalfooter', 'children')],
   [Input('kw_search', 'modified_timestamp')],
   [State('kw_search', 'data')]
)
def show_candidates(ts, candidate_df_json):
    if not ts:
        raise PreventUpdate

    #TODO: This 100 filter is a hack to get around returning nothing or some other component. But seems fragile.
    if candidate_df_json and len(candidate_df_json)>100:
        candidate_df = pd.read_json(candidate_df_json)
        return dbc.Row(
            dbc.Col([
                dbc.Col([
                    html.Div([
                    dbc.Button("Select All", id={'type':'select_btn', 'name':'select'}, style={"margin": "5px"}),
                    dbc.Button("Deselect All", id={'type':'select_btn', 'name':'deselect'}, style={"margin": "5px"})
                    # dbc.Button("Return selected fields", id={'modal_ctrl':'none', 'name':'return_rows'})
                    ])
                ])
            ])
    ), dash_table.DataTable(
                        id='kw_result_table',
                        css=[{'selector': '.dash-filter input', 'rule': 'text-align: left'}, {'selector': '.row', 'rule': 'margin: 0'}],
                        style_cell={
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                'text-align': 'left'
                        },
                        style_cell_conditional = [
                                {'if': {'column_id':'Value'}, 'width': '50px'}
                        ],
                            columns=[{"name": i, "id": i} for i in candidate_df.columns],
                        data=candidate_df.to_dict('records'),
                        row_selectable='multi',
                        filter_action='native',
                        page_size=25,
                        fixed_rows={'headers': True},
                    ), dbc.Button("Return selected fields", id={'modal_ctrl':'none', 'name':'return_rows'}, className="ml-auto", color='success')
    raise PreventUpdate

# dbc.ModalFooter(
#     dbc.Button("Close", id={'type': 'find_terms_modal_btn', 'name': 'close'}, className="ml-auto")
# ),
#
# Select / Deselect all buttons
#
@app.callback(
    [Output(component_id="kw_result_table", component_property="selected_rows")],
    [Input({'type': 'select_btn', 'name': ALL}, "n_clicks")],
    [State(component_id="kw_result_table", component_property="derived_virtual_data"),
     State(component_id="kw_result_table", component_property="selected_rows"),
     State(component_id="kw_result_table", component_property="derived_viewport_selected_rows"),
     State(component_id="kw_result_table", component_property="derived_virtual_selected_rows")]
)
def select_all(n_clicks: int, rows: list, selected_rows: list, derived_viewport_indices: list, derived_virtual_indices: list):
    """Get selected rows in "kw_results_table".

    Keyword arguments:
    ------------------
    n_clicks: int
        int indicating the number of clicks on "select_btn"
    rows: list
        all rows returned in "kw_result_table"
    selected_rows: list
        all selected rows from "kw_result_table"
    derived_viewport_indices: list
        indices of currently visible rows in "kw_result_table"
    derived_virtual_indices: list
        indices of all rows in "kw_result_table"

    Returns:
    --------
    selected_rows: list
        list of selected rows

    """
    ctx = dash.callback_context
    #Figure out which button was pressed
    calling_button="select"
    if ctx.triggered and ctx.triggered[0]['value']:
        calling_button = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])['name']

    if selected_rows is None or calling_button == 'deselect':
        select_rows= [[]]
    else:
        select_rows = [[i for i in range(len(rows))]]

    return select_rows

@app.callback(
    Output('selected_terms_data', 'data'),
    [Input({'modal_ctrl': 'none', 'name': 'return_rows'}, "n_clicks")],
    [State('kw_result_table', 'derived_virtual_data'),
    State('kw_result_table', 'derived_virtual_selected_rows')]
)
def store_selected_terms(nclick: int, rows: list, derived_virtual_selected_rows: list):
    """Store selected search terms in "selected_terms_data" store.

    Keyword arguments:
    ------------------
    nclick: int
        int indicating the number of clicks on "return_rows" button
    rows: list
        list containing all the selected terms
    derived_virtual_selected_rows: list
        list containing all the selected rows

    Returns:
    --------
    rows: list
        list containing all selected terms
    derived_virtual_selected_rows: list
        list containing all selected rows

    """
    ctx = dash.callback_context
    if (not ctx.triggered):
        raise PreventUpdate

    return [rows, derived_virtual_selected_rows]
