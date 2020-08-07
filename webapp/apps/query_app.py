import dash
from app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import pandas as pd
import os

from ukbcc import query, utils
import pprint

from datetime import datetime
print_time = lambda: datetime.now().strftime("%H:%M:%S")

from dash.exceptions import PreventUpdate

all_dropdown = dbc.FormGroup(
    [
        dbc.Label("All of these", html_for="example-email"),
        dcc.Dropdown(id={"index":0, "name":"query_term_dropdown"}, placeholder="Enter defined terms", clearable=True, multi=True, persistence=True),
        dbc.FormText(
            "Add terms that all be present for an individal to be included in the cohort",
            color="secondary",
        ),
    ]
)


none_dropdown = dbc.FormGroup(
    [
        dbc.Label("None of these", html_for="example-email"),
        dcc.Dropdown(id={"index":1, "name":"query_term_dropdown"}, placeholder="Enter defined terms", clearable=True, multi=True, persistence=True),
        dbc.FormText(
            "Add terms that must be absent for an individal to be included in the cohort",
            color="secondary",
        ),
    ]
)


#
#
# Keyword Search Tab
#
tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Cohort Search", className="card-text"),
            html.P("Define the properties of a cohort, based on the defined terms and show results", className="card-text"),
            dbc.Form(
                dbc.FormGroup([all_dropdown, none_dropdown,
                               dbc.Button("Submit", color="success", id='cohort_search_submit1')])
            ),
            dbc.Row(dbc.Col(id='query_results'), align='center'),
            dbc.Row([
               dbc.Button("Previous", color='primary', id={"name":"prev_button_query","type":"nav_btn"}),
               dbc.Button("Next", color='primary',  id={"name":"next_button_query","type":"nav_btn"})
            ]),

            dbc.Modal(
                [
                    dbc.ModalHeader("Running query..."),
                    dbc.ModalBody(id="run_query"),
                    # dbc.Row(dbc.Col(id="status_message"))),
                    # dbc.Row(dbc.Col(id="query_output"))),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close_run_query_btn", className="ml-auto")
                    ),
                ],
                id="run_query_modal")
        ]
    ),
    className="mt-3",
)

@app.callback(
    Output("run_query", "children"),
    [Input("cohort_search_submit1", "n_clicks")]
)
def update_run_query_modal(n_click):
    return dbc.Row(
                dbc.Col([
                    html.P("Please wait, this could take some time...")
                ]))

@app.callback(
    Output("run_query_modal", "is_open"),
    [Input("cohort_search_submit1", "n_clicks"),
    Input("close_run_query_btn", "n_clicks")],
    [State("run_query_modal", "is_open")]
)
def toggle_run_query_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
#
# When we load the derived terms update, so does the list of searchable terms
#
@app.callback(
    Output({"index":MATCH, "name":"query_term_dropdown"}, 'options'),
    [Input({"index":MATCH, "name":"query_term_dropdown"}, 'value')],
    [State('defined_terms', 'data')]
)
def set_querable_terms(active_tab, defined_terms):
    # If we have no defined terms, sop this callback
    if (defined_terms is None):
        print(defined_terms)
        raise PreventUpdate

    opts=[ {'label': val['name'][0], 'value': key} for key,val in defined_terms.items()]
    return(opts)


def _term_iterator(id: str, defined_terms: dict, rand_terms: list):
    """Creates list of tuples from defined_terms dictionary.

    Iterates through field, value combinations within defined_terms[id]['any']
    and appends them to a list as tuples of (key, value)

    Keyword arguments:
    ------------------
    id: str
        id to use as key for defined_terms dict
    defined_terms: dict
        dictionary returned by alter_defined_term function in "definitions_app.py"
    rand_terms: list
        list to append all tuples to

    Returns:
    --------
    rand_terms: list
        list of tuples of field, value combinations

    """
    terms = pd.concat([pd.read_json(x) for x in defined_terms[id]['any']] + [pd.DataFrame()])
    terms['FieldID'] = terms['FieldID'].astype(str)
    terms['Value'] = terms['Value'].astype(str)
    rand_terms = rand_terms + [tuple(x) for x in terms[['FieldID', 'Value']].values]
    return rand_terms

#
# Submit a query
#
@app.callback(
    [Output("run_query_modal", "children"),
    Output("query_results", "children")],
    [Input("cohort_search_submit1", "n_clicks")],
    [State("defined_terms", "data"),
     State({"index":0, "name":"query_term_dropdown"}, 'value'),
     State({"index":1, "name":"query_term_dropdown"}, 'value'),
     State("config_store", "data")]
)
def submit_cohort_query(n, defined_terms, all_terms, none_terms, config):
    print('\nsubmit_cohort_query()')
    print(n)
    pp = pprint.PrettyPrinter(indent=4)

    if n is None:
        raise PreventUpdate


    #Put data in the right for for the ukbcc backend
    # TODO - HACK: Only doing first all term, ignoring none

    print('all terms', all_terms)

    anys = []
    nones = []

    for id in all_terms:
        anys = _term_iterator(id, defined_terms, anys)

    for id in none_terms:
        nones = _term_iterator(id, defined_terms, nones)

    print(anys)
    print(nones)

    # TODO - HACK
    cohort_criteria = {
        "all_of": [],
        "any_of": anys,
        "none_of": nones
    }

    outpath = config['cohort_path']
    cohort_out = os.path.join(outpath, "cohort_dictionary.txt")
    utils.write_dictionary(cohort_criteria, cohort_out)

    if os.path.exists(cohort_out):
        print(f"successfully saved cohort dictionary to {cohort_out}")
    else:
        print(f"could not save cohort dictionary to {cohort_out}")


    print('\ncreate_queries {}'.format(print_time()))
    print(config['gp_path'])
    queries = query.create_queries(cohort_criteria=cohort_criteria, main_filename=config['main_dat_path'],
                                   gpc_path=config['gp_path'])
    pp.pprint(queries)
    print('\nquery_databases {}'.format(print_time()))
    ids = query.query_databases(cohort_criteria=cohort_criteria, queries=queries, main_filename=config['main_dat_path'],
                          write_dir=config['cohort_path'], gpc_path=config['gp_path'], out_filename=config['out_filename'], write=True)
    #print(ids)
    print('\nfinished query_databases {}'.format(print_time()))

    return dbc.Row(
                dbc.Col([
                    html.P(f"Found {len(ids)} matching ids.")
                ])), html.P(f"Found {len(ids)} matching ids.")
    # return html.P(f"Found {len(ids)} matching ids.")
