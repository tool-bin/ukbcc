import dash
from app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd
import json
from apps import kw_search_app
from datetime import datetime
from dash.exceptions import PreventUpdate
from collections import OrderedDict

import random
import string


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

#get_curr_time
print_time = lambda: datetime.now().strftime("%H:%M:%S")

#
# Modal for keyword search to find fields of interest
#
add_new_phenotype_modal = dbc.Modal(
                [
                    dbc.ModalHeader("What should the new phenotype be called"),
                    dbc.ModalBody(
                        dbc.Form([dbc.FormGroup([
                                dbc.Label("New phenotype name", html_for='new_phenotype_input'),
                                dbc.Input(placeholder="Enter name", type="text", id={"name":"name_input",'type':'new_term'}),
                                dbc.FormText("Specify the name of the phenotype you wish to create", color="secondary"),
                        ])]),
                        id="find_terms_modalbody"),
                    dbc.ModalFooter(
                        #TODO: Pretty sure this 'id' can be simplified.
                        dbc.Button("Add", id={'modal_ctrl':'new_term', 'name': 'submit'}, className="ml-auto")
                    ),
                ],
                id="new_phenotype_modal",
                style={'maxWidth': '1600px', 'width': '90%'})


#
# Modal for keyword search to find fields of interest
#
add_new_term_modal = dbc.Modal(
                [
                    dbc.ModalHeader("Find fields"),
                    dbc.ModalBody(id="find_terms_modalbody", children=kw_search_app.kw_search_group),
                    dbc.ModalFooter(
                        dbc.Button("Close", id={'type': 'find_terms_modal_btn', 'name': 'close'}, className="ml-auto")
                    ),
                ],
                id="find_terms_modal",
                size="xl",
                style={'maxWidth': '1600px', 'width': '90%'})


#
#
# Keyword Search Tab
#
tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Define terms", className="card-text"),
            html.P("Create phenotypes of interest by selecting their corresponding fields", className="card-text"),
            dbc.Button('Add new term', id={'modal_ctrl':'new_term', 'name': 'add'}),
            add_new_phenotype_modal,
            add_new_term_modal,
            dbc.Row(dbc.Col(id='defined_term_rows')),
            dbc.Row([
               dbc.Button("Previous", color='primary', id={"name":"prev_button_terms","type":"nav_btn"}),
               dbc.Button("Next", color='primary', id={"name":"next_button_terms","type":"nav_btn"})
            ]),

        ]
    ),
    className="mt-3",
)


#
#
# When we make a new term, launch a modal which allows us to enter a name
# Use the name to setup the data 'defined_term's storage
# 'defined_term's storage  then populates the list of pre-defined terms
#
@app.callback(
    Output("defined_terms", "data"),
    [Input({'modal_ctrl':ALL,  'name': ALL}, "n_clicks")],
    [State("defined_terms", "data"),
     State({"name":"name_input",'type':ALL}, "value"),
     State("search_logic_state", "children"),
     #State('selected_terms_data', 'children'),
     State('kw_result_table', 'derived_virtual_data'),
     State('kw_result_table', 'derived_virtual_selected_rows')
     ]
)
def alter_defined_term(n_clicks, defined_terms, name,term_add_state, rows, derived_virtual_selected_rows):
    ctx = dash.callback_context

    if (not ctx.triggered):
        raise PreventUpdate

    if len(ctx.triggered) and (ctx.triggered[0]['prop_id'] == '.' or ctx.triggered[0]['value'] is None):
        raise PreventUpdate

    calling_ctx = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    defined_terms = defined_terms or OrderedDict()

    #If we aren't related to a modal, we're a button of a defined term
    if(calling_ctx["modal_ctrl"] == 'none' and calling_ctx['name']!='return_rows'):
        calling_id, calling_action = calling_ctx["name"].rsplit('_', 1)
        del defined_terms[calling_id]
        return defined_terms

    #If we are returning rows from the new term modal
    elif (calling_ctx["modal_ctrl"] == 'none' and calling_ctx['name'] == 'return_rows'):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        selected_df = pd.DataFrame(rows).iloc[derived_virtual_selected_rows]
        defined_terms[term_add_state[0]][term_add_state[1]].append( selected_df.to_json())

    # If we are adding a new term
    elif (calling_ctx["modal_ctrl"] == 'new_term' and calling_ctx["name"] == 'submit'):
        defined_terms[get_random_string(16)]={'name':name, 'any':[], 'all':[]}

    return defined_terms



@app.callback(
    Output("defined_term_rows", "children"),
    [Input("defined_terms", "modified_timestamp")], #See https://dash.plotly.com/dash-core-components/store
    [State("defined_terms", "data")]
)
def populate_defined_terms(_, defined_terms):
    #If we haven't pressed anything, get out


    defined_fields=[]
    for idx, (id,v) in enumerate(defined_terms.items()):
        n_any_terms = len(defined_terms[id]['any'])
        n_all_terms = len(defined_terms[id]['any'])

        #term_count_str = "# terms: {} Any \t{} All".format(n_any_terms)#, n_all_terms)
        term_count_str = "{} terms".format(n_any_terms)  # , n_all_terms)

        tab_any_terms = pd.concat([pd.read_json(x) for x in defined_terms[id]['any']]+[pd.DataFrame()])
        tab_all_terms = pd.concat([pd.read_json(x) for x in defined_terms[id]['all']]+[pd.DataFrame()])

        #TODO: Move this to its own function
        #TODO: Consider using dbc.Collapse to allow showing lots of terms
        defined_fields.append(dbc.Card(dbc.Row([
            dbc.Col(dbc.Button("❌", id={'modal_ctrl':'none','name': id + '_remove'}), width={"size": 1}),
            #dbc.Col(dbc.Input(id={"name": id + '_name', "type": "name_text"}, type='text', disabled=True,  ), width={"size": 3}, ),
            dbc.Col(html.H3(v['name'], id=id + '_name_title'), width={"size": 3}),
            dbc.Col(dbc.Button("Add terms", id={"name": id + '_any', "type": "find_terms_modal_btn"}),
                    width={"size": 2}),
            #dbc.Col(dbc.Button("Add 'all' term", id={"name": id + '_all', "type": "find_terms_modal_btn"}),
            #        width={"size": 2}),
            dbc.Col(html.H5(term_count_str, id={"name": id + '_terms', "type": "text"}), width={"size": 3}),
            dbc.Col(dbc.Button("▼", id={"index": idx, "type": "expand"}), width={"size": 1}),
            dbc.Collapse(
                dbc.Card(
                    dbc.CardBody([
                        html.H5('At least one of these'),
                        dbc.Table.from_dataframe(tab_any_terms, striped=True, bordered=True, hover=True)
                        #html.H5('All of these terms'),
                        #dbc.Table.from_dataframe(tab_all_terms, striped=True, bordered=True, hover=True)
                    ])),
                id={"index": idx, "type": "collapse"})
        ])))
    return (defined_fields)


#
#
# Open/close collapse terms
# Note the use of inex here rather than name
#
@app.callback(
    Output({"index": MATCH,'type':'collapse'}, "is_open"),
    [Input({"index": MATCH,'type':'expand'}, "n_clicks")],
    [State({"index": MATCH,'type':'collapse'}, "is_open")],
)
def toggle_collapse(value, is_open):
    if value:
        return not is_open
    return is_open


#
#
# Open/close find_terms_modal modal
# Modal is launched whenever a find_terms_modal_btn button (which are dynamically created) is pressed
# TODO: can't close if there isn't a term added to the new term modal. Requires determining what the calling button is
#
@app.callback(
    [Output("find_terms_modal", "is_open"),
     Output("search_logic_state", "children")],
    [Input({'type': 'find_terms_modal_btn', 'name': ALL}, "n_clicks"),
     Input({'modal_ctrl':ALL, 'name':'return_rows'}, "n_clicks")],
    [State("find_terms_modal", "is_open"),
     State("search_logic_state", "children")],
)
def toggle_new_term_modal(x, y, is_open, term_add_state):

    ctx = dash.callback_context

    #If nothing pressed
    if(not ctx.triggered):
        raise PreventUpdate

    if len(ctx.triggered) and (ctx.triggered[0]['prop_id'] == '.' or ctx.triggered[0]['value'] is None):
        raise PreventUpdate

    calling_ctx = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])

    # Set any/all state if opening
    term_add_state_new=term_add_state
    if('type' in calling_ctx and calling_ctx['type']=='find_terms_modal_btn'):
        term_add_state_new = calling_ctx["name"].rsplit('_', 1)

    if ctx.triggered[0]['value']:
        return not is_open,term_add_state_new

    return is_open,term_add_state_new


#
#
# Open/close add_new_phenotype_modal modal
# Modal is launched whenever a add_new_phenotype_modal button (which are dynamicaaly created) is pressed
@app.callback(
    Output("new_phenotype_modal", "is_open"),
    [Input({'modal_ctrl':'new_term', 'name': ALL}, "n_clicks")],
    [State("new_phenotype_modal", "is_open")],
)
def toggle_new_phenotype_modal(values, is_open):
    #If nothing pressed
    ctx = dash.callback_context
    if(not ctx.triggered):
        raise PreventUpdate

    if len(ctx.triggered) and (ctx.triggered[0]['prop_id'] == '.' or ctx.triggered[0]['value'] is None):
        raise PreventUpdate

    if ctx.triggered[0]['value']:
        return not is_open

    return is_open