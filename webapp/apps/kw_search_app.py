import dash
from app import app

import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import os
import pandas as pd
import dash_table
from ukbcc import filter as ukbcc_filter
import json
from dash.exceptions import PreventUpdate

#
#
# Keyword Search Tab
#
kw_search_group = dbc.FormGroup(
        [
            html.H3("Specify Keywords", className="card-text"),
            dbc.Row([
                dbc.Col([
                    dbc.Input(id="keyword_input", placeholder="Specify keywords to search, separated by semicolon", type="text", persistence=True)
                ]),
                dbc.Col([
                    dbc.Button("Search", color="success", id="submit_btn")
                ]),
            ]),
            dbc.Row(id='kw_search_output_select'),
            html.Div(id='kw_search_output')
            # html.Div([
            #     dash_table.DataTable(
            #         id='table-editing-simple',
            #         columns=(
            #             [{'id': 'Model', 'name': 'Model'}] +
            #             [{'id': p, 'name': p} for p in params]
            #         ),
            #         data=[
            #             dict(Model=i, **{param: 0 for param in params})
            #             for i in range(1, 5)
            #         ],
            #         editable=True
            #     ),
            #     dcc.Graph(id='table-editing-simple-output')
            # ])
        ],
    className="mt-3"
)


#
#
# Handle keyword search input
# TODO: Are all these checks needed? Very unclear to me.
@app.callback(Output('kw_search', 'data'),
              [Input('submit_btn', 'n_clicks')],
              [State("config_store", "data"),
               State("keyword_input", "value"),
               State("kw_search", "data")]
            )
def search_kw_button(_, config, search_terms, kw_search):

    print('search_kw_button')
    #Cancel if we haven't pressed the button
    ctx = dash.callback_context
    if len(ctx.triggered) and ctx.triggered[0]['prop_id']=='.':
        raise PreventUpdate

    # If we haven't clicked submit and we have a previous value, return the previous value
    if len(ctx.triggered) and ctx.triggered[0]['value'] is None and kw_search is not None:
        return kw_search

    #Show error if we haven't set any config
    if config=={}:
        print('no config')
        return "Config has not been set. Missing all fields"

    #Show error if we are missing fields
    required_config = set(['main_dat_path', 'gp_path', 'cohort_path', 'aux_path'])
    existing_config_fields=set(config.keys())
    missing_config_fields = required_config.difference(existing_config_fields)
    if len(missing_config_fields)!=0:
        print("Config has not been set. Missing fields: {}".format(', '.join([str(x) for x in missing_config_fields])))
        raise PreventUpdate

    print('config')
    print(config)

    # Run the search
    #Show error if we haven't set any search terms
    if search_terms is None:
        print ('No search terms')
        raise PreventUpdate

    if len(search_terms)==0:
        print ('No search terms')
        #return "No search terms specified"
        raise PreventUpdate

    search_terms = search_terms.split(';')
    print('Search terms ')
    print(search_terms)

    coding_filename = os.path.join(config['aux_path'], "codings.csv")
    showcase_filename = os.path.join(config['aux_path'], "showcase.csv")
    readcode_filename = os.path.join(config['aux_path'], "readcodes.csv")
    print('Constructing Search')
    search_df = ukbcc_filter.construct_search_df(showcase_filename=showcase_filename,
                                           coding_filename=coding_filename,
                                           readcode_filename=readcode_filename)
    print('Searching keyword')
    candidate_df = ukbcc_filter.construct_candidate_df(searchable_df=search_df, search_terms=search_terms)
    print('Done searching keyword')
    return candidate_df.to_json()


#
#
# Show_candidates as a big queryable table
# Actually the plotly dash table looks pretty average
# #
# #
@app.callback([Output('kw_search_output_select', 'children'),
               Output('kw_search_output', 'children')],
             [Input('kw_search', 'data')]
            )
def show_candidates(candidate_df_json):

    #TODO: This 100 filter is a hack to get around returning nothing or some other component. But seems fragile.
    if candidate_df_json is not None and len(candidate_df_json)>100:
        candidate_df = pd.read_json(candidate_df_json)
        return dbc.Row(
            dbc.Col([
                dbc.Row([
                    html.Div([
                    dbc.Button("Select All", id={'type':'select_btn', 'name':'select'}),
                    dbc.Button("Deselect All", id={'type':'select_btn', 'name':'deselect'}),
                    dbc.Button("Return selected fields", id={'modal_ctrl':'none', 'name':'return_rows'})
                    ])
                ])
                ]
                )
                ), dash_table.DataTable(
                        id='kw_result_table',
                        #css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
                        # style_cell={
                        #     'whiteSpace': 'normal',
                        #     'height': 'auto',
                        # },
                        columns=[{"name": i, "id": i} for i in candidate_df.columns],
                        data=candidate_df.to_dict('records'),
                        row_selectable='multi',
                        filter_action='native',
                        page_size=10,
                        fixed_rows={'headers': True},
                        style_cell_conditional=[
                            {'if': {'column_id': 'Field'},   'width': '1%'},
                            {'if': {'column_id': 'FieldID'}, 'width': '6%'},
                            {'if': {'column_id': 'Coding'},  'width': '6%'},
                            {'if': {'column_id': 'Value'},   'width': '8%'},
                            {'if': {'column_id': 'Meaning'}, 'width': '40%', 'text-align': 'left'}
                            ]
                    )

# @app.callback(Output('kw_search_output', 'children'),
#              [Input('kw_search', 'data')]
#             )
# def show_candidates(candidate_df_json):
#
#     #TODO: This 100 filter is a hack to get around returning nothing or some other component. But seems fragile.
#     if candidate_df_json is not None and len(candidate_df_json)>100:
#         candidate_df = pd.read_json(candidate_df_json)
#         return dbc.Row(
#             dbc.Col([
#                 dbc.Row([
#                     html.Div([
#                     dbc.Button("Select All", id={'type':'select_btn', 'name':'select'}),
#                     dbc.Button("Deselect All", id={'type':'select_btn', 'name':'deselect'}),
#                     dbc.Button("Return selected fields", id={'modal_ctrl':'none', 'name':'return_rows'})
#                     ])
#                 ])
#                 ,
#                 dbc.Row(
#                     dash_table.DataTable(
#                         id='kw_result_table',
#                         #css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
#                         style_cell={
#                             'whiteSpace': 'normal',
#                             'height': 'auto',
#                         },
#                         columns=[{"name": i, "id": i} for i in candidate_df.columns],
#                         data=candidate_df.to_dict('records'),
#                         row_selectable='multi',
#                         filter_action='native',
#                         page_size=10,
#                         fixed_rows={'headers': True},
#                         style_cell_conditional=[
#                             {'if': {'column_id': 'Field'},   'width': '1%'},
#                             {'if': {'column_id': 'FieldID'}, 'width': '6%'},
#                             {'if': {'column_id': 'Coding'},  'width': '6%'},
#                             {'if': {'column_id': 'Value'},   'width': '8%'},
#                             {'if': {'column_id': 'Meaning'}, 'width': '40%'}
#
#                         ]
#
#                     )
#                 )
#             ], width={"size": 20, "offset": 2}), justify='right')

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
def select_all(n_clicks, rows, selected_rows, derived_viewport_indices, derived_virtual_indices):
    print("Select All")

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

    print("After: Selected rows"),
    print(select_rows)
    return select_rows



@app.callback(
    Output('selected_terms_data', 'data'),
    [Input({'modal_ctrl': 'none', 'name': 'return_rows'}, "n_clicks")],
    [State('kw_result_table', 'derived_virtual_data'),
    State('kw_result_table', 'derived_virtual_selected_rows')]
)
def store_selected_terms(nclick, rows, derived_virtual_selected_rows):
    ctx = dash.callback_context
    if (not ctx.triggered):
        print('\tNothing triggered')
        raise PreventUpdate

    print("Updating terms")
    print(type(rows))
    print(type(derived_virtual_selected_rows))
    return [rows, derived_virtual_selected_rows]
