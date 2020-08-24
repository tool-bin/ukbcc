import dash
from app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd
import dash_table
import json

#
#
# Keyword Search Tab
#
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


#
#
# Show_candidates as a big queryable table
# Actually the plotly dash table looksk pretty average
#
@app.callback(Output('include_fields_tab', 'children'),
             [Input('kw_search', 'data')]
            )
def show_candidates(candidate_df_json):
    print('show_candidates')
    #print(candidate_df_json)
    print(type(candidate_df_json))
    print(len(candidate_df_json))
    if candidate_df_json is not None and len(candidate_df_json)>100:
        candidate_df = pd.read_json(candidate_df_json)
        print(candidate_df)
        return dbc.Row(
            dbc.Col([
                dbc.Row([
                    dbc.Button("Select All", id={'type':'select_btn', 'name':'select'}),
                    dbc.Button("Deselect All", id={'type':'select_btn', 'name':'deselect'})
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
def select_all(n_clicks, rows, selected_rows, derived_viewport_indices, derived_virtual_indices):
    print("Select All")

    if rows is not None:
        print("rows")
        print(rows[min(1,len(rows)):min(10, len(rows))])
    print("Before: Selected rows"),
    print(selected_rows)
    print("Before: derived_viewport_selected_rows")
    print(derived_viewport_indices)
    print("Before: derived_virtual_selected_rows")
    print(derived_virtual_indices)

    ctx = dash.callback_context
    print("\nIn select_all()")
    print(ctx.triggered)

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
