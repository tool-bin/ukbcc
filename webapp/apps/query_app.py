import dash
from app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import pandas as pd
import os
import tableone
from io import StringIO

from ukbcc import query, utils, db
import pprint

from datetime import datetime
print_time = lambda: datetime.now().strftime("%H:%M:%S")

from dash.exceptions import PreventUpdate

all_dropdown = dbc.FormGroup(
    [
        dbc.Label("All of these", html_for="example-email"),
        dcc.Dropdown(id={"index":0, "name":"query_term_dropdown"}, placeholder="Enter defined terms", clearable=True, multi=True, persistence=False),
        dbc.FormText(
            "Add terms that must all be present for an individual to be included in the cohort",
            color="secondary",
        ),
    ]
)

any_dropdown = dbc.FormGroup(
    [
        dbc.Label("Any of these", html_for="example-email"),
        dcc.Dropdown(id={"index":1, "name":"query_term_dropdown"}, placeholder="Enter defined terms", clearable=True, multi=True, persistence=False),
        dbc.FormText(
            "Add terms that are optionally present for an individual to be included in the cohort",
            color="secondary",
        ),
    ]
)


none_dropdown = dbc.FormGroup(
    [
        dbc.Label("None of these", html_for="example-email"),
        dcc.Dropdown(id={"index":2, "name":"query_term_dropdown"}, placeholder="Enter defined terms", clearable=True, multi=True, persistence=False),
        dbc.FormText(
            "Add terms that must be absent for an individual to be included in the cohort",
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
                dbc.FormGroup([all_dropdown, any_dropdown, none_dropdown,
                               dbc.Button("Submit", color="success", id='cohort_search_submit1')])
            ),
            dbc.Row(dbc.Col(id='query_results'), align='center'),
            dbc.Row([
               dbc.Button("Previous", color='primary', id={"name":"prev_button_query","type":"nav_btn"}, style={"margin": "5px"}),
               dbc.Button("Next", color='primary',  id={"name":"next_button_query","type":"nav_btn"}, style={"margin": "5px"})
            ]),

            dbc.Modal(
                [
                    dbc.ModalHeader("Running query..."),
                    dbc.ModalBody(id="run_query"),
                    # dbc.Row(dbc.Col(id="status_message"))),
                    # dbc.Row(dbc.Col(id="query_output"))),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close_run_query_btn", className="ml-auto", style={"margin": "5px"})
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


def _term_iterator(id: str, defined_terms: dict):
    """Creates list of tuples from defined_terms dictionary.

    Iterates through field, value combinations within defined_terms[id]['any']
    and appends them to a list as tuples of (key, value)

    Keyword arguments:
    ------------------
    id: str
        id to use as key for defined_terms dict
    defined_terms: dict
        dictionary returned by alter_defined_term function in "definitions_app.py"

    Returns:
    --------
    rand_terms: list
        list of tuples of field, value combinations

    """
    rand_terms = []
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
     State({"index":2, "name":"query_term_dropdown"}, 'value'),
     State("config_store", "data")]
)
def submit_cohort_query(n, defined_terms, all_terms, any_terms, none_terms, config):
    print('\nsubmit_cohort_query()')
    print(n)
    pp = pprint.PrettyPrinter(indent=4)

    if n is None:
        raise PreventUpdate

    #Put data in the right for for the ukbcc backend
    anys = []
    nones = []
    alls = []

    print("defined terms {}".format(defined_terms))

    if all_terms:
        print("all terms! {}".format(all_terms))
        for id in all_terms:
            print("id {}".format(id))
            alls = _term_iterator(id, defined_terms)

    if any_terms:
        print("any terms! {}".format(any_terms))
        for id in any_terms:
            print("id {}".format(id))
            anys = _term_iterator(id, defined_terms)

    if none_terms:
        print("none terms! {}".format(none_terms))
        for id in none_terms:
            print("id {}".format(id))
            nones = _term_iterator(id, defined_terms)

    print("any terms {}, all terms {}, none terms {}".format(anys, alls, nones))

    # TODO - HACK
    cohort_criteria = {
        "all_of": alls,
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

    #TODO: HACK FOR OUTPUT FILE
    config['out_filename'] = "cohort_ids.txt"


    print('\ncreate_queries query_sqlite_db {}'.format(print_time()))

    db_filename = '/home/bwgoudey/Research2/GWAS/ukbcc/tmp/ukb.sqlite'

    res = db.query_sqlite_db(db_filename, cohort_criteria)
    ret = html.P(f"No matching ids found. Please change your criteria.")
    if(res.shape[0]):
        t1=tableone.TableOne(res)
        ret=dbc.Table.from_dataframe(pd.read_csv(StringIO(t1.to_csv())), striped=True, bordered=True,
                                 hover=True)

    ids=res['eid'].to_list()
    # #print("cohort_criteria: {}".format(cohort_criteria))
    # queries = query.create_queries(cohort_criteria=cohort_criteria, main_filename=config['main_path'],
    #                                gpc_path=config['gp_path'])
    # pp.pprint(queries)
    # print('\nquery_databases {}'.format(print_time()))
    # ids = query.query_databases(cohort_criteria=cohort_criteria, queries=queries, main_filename=config['main_path'],
    #                       write_dir=config['cohort_path'], gpc_path=config['gp_path'], out_filename=config['out_filename'], write=True)
    #print(ids)
    print('\nfinished query_databases {}'.format(print_time()))

    return dbc.Row(
                dbc.Col([
                    ret
                ])
            ),ret

    # return html.P(f"Found {len(ids)} matching ids.")
