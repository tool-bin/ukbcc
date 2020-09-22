import dash
from ukbcc.webapp.app import app

import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_core_components as dcc
import pandas as pd
import os

from ukbcc import query, utils, stats
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

#Keyword Search Tab
tab = dbc.FormGroup(
    dbc.CardBody(
        [
            html.H3("Cohort Search", className="card-text"),
            html.P("Define the properties of a cohort, based on the defined terms and show results", className="card-text"),
            dbc.Form(
                dbc.FormGroup([all_dropdown, any_dropdown, none_dropdown,
                               dbc.Button("Submit", color="success", id='cohort_search_submit1', style={"margin": "5px"})])
            ),
            dbc.Row(dbc.Col(id='query_results'), align='center'),
            dbc.Row([
               dbc.Button("Previous", color='primary', id={"name":"prev_button_query","type":"nav_btn"}, style={"margin": "5px"}),
               dbc.Button("Next", color='primary',  id={"name":"next_button_query","type":"nav_btn"}, style={"margin": "5px"})
            ]),

            dbc.Modal(
                [
                    dbc.ModalHeader("Running query..."),
                    dbc.ModalBody(id="run_query", children="Please wait, this could take some time.."),
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

def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output("run_query_modal", "is_open"),
    [Input("cohort_search_submit1", "n_clicks"),
    Input("close_run_query_btn", "n_clicks")],
    [State("run_query_modal", "is_open")]
)
def toggle_run_query_modal(n1, n2, is_open):
    check = toggle_modal(n1, n2, is_open)
    return check

#When we load the derived terms update, so does the list of searchable terms
@app.callback(
    Output({"index":MATCH, "name":"query_term_dropdown"}, 'options'),
    [Input({"index":MATCH, "name":"query_term_dropdown"}, 'value')],
    [State('defined_terms', 'data')]
)
def set_querable_terms(active_tab: str, defined_terms: dict):
    """Returns queried terms.

    Keyword arguments:
    ------------------
    active_tab: str
        string indicating which tab is currently selected
    defined_terms: dict
        selected terms

    Returns:
    --------
    opts: list
        selected phenotype to search

    """
    # If we have no defined terms, sop this callback
    if (defined_terms is None):
        print(defined_terms)
        raise PreventUpdate

    opts=[{'label': val['name'][0], 'value': key} for key,val in defined_terms.items()]
    return(opts)


# def _term_iterator(id: str, defined_terms: dict):
def _term_iterator(selterms: dict):
    """Creates list of tuples from selterms dictionary.

    Iterates through field, value combinations within selterms dictionary
    (created from the definted_terms[id]['any_of'] key)
    and appends them to a list as tuples of (key, value)

    Keyword arguments:
    ------------------
    selterms: dict
        dictionary returned by alter_defined_term function in "definitions_app.py"

    Returns:
    --------
    rand_terms: list
        list of tuples of encoded field, value combinations
    decoded_terms: list
        list of tuples of decoded field, value combinations

    """
    rand_terms = []
    rand_terms_decoded = []
    terms = pd.concat([pd.read_json(x) for x in selterms['any']] + [pd.DataFrame()])
    terms['FieldID'] = terms['FieldID'].astype(str)
    terms['Value'] = terms['Value'].astype(str)
    rand_terms = rand_terms + [tuple(x) for x in terms[['FieldID', 'Value']].values]
    rand_terms_decoded = rand_terms_decoded + [tuple(x) for x in terms[['Field', 'Meaning']].values]
    return rand_terms, rand_terms_decoded

def _create_conditional_logic_list(logic_terms: list, defined_terms: dict):
    """Combines list of tuples created from defined_terms dictionary.

    Iterates through the phenotypes selected from the "all of", "any of", and/or
    "none of" dropdowns and merges the list of field, value tuples to a single list

    Keyword arguments:
    ------------------
    logic_terms: list
        list of ids referencing the phenotypes created in the "definition_app.py"
        ids are keys in a dictionary containing all the definted terms
    defined_terms: dict
        dictionary returned by alter_defined_term function in "definitions_app.py"

    Returns:
    --------
    term_final: list
        list of tuples of encoded field, value combinations
    term_decoded_final: list
        list of tuples of decoded field, value combinations

    """
    temp = []
    decoded_temp = []
    for id in logic_terms:
        term_tuples, term_decoded_tuples = _term_iterator(defined_terms[id])
        temp.append(term_tuples)
        decoded_temp.append(term_decoded_tuples)
    term_final = [y for x in temp for y in x]
    term_decoded_final = [y for x in decoded_temp for y in x]
    return term_final, term_decoded_final


#Submit a query
@app.callback(
    [Output("query_results", "children"),
    Output("cohort_id_results", "data"),
    Output("cohort_id_results_timestamp", "data"),
    Output("cohort_id_report", "data")],
    [Input("cohort_search_submit1", "n_clicks")],
    [State("defined_terms", "data"),
     State({"index":0, "name":"query_term_dropdown"}, 'value'),
     State({"index":1, "name":"query_term_dropdown"}, 'value'),
     State({"index":2, "name":"query_term_dropdown"}, 'value'),
     State("config_store", "data"),
     State("kw_search_terms", "data")]
)
def submit_cohort_query(n: int, defined_terms: dict, all_terms: list,
                        any_terms: list, none_terms: list, config: dict,
                        kw_search_terms: list):
    """Run cohort search.

    Keyword arguments:
    ------------------
    n: int
        indicates number of clicks of cohort search button
    defined_terms: dict
        phenotypes
    all_terms: list
        phenotypes for all participants
    any_terms: list
        phenotypes for any participants
    none_terms: list
        phenotypes for none of the participants
    config: dict
        path configuration
    kw_search_terms: list
        search terms

    Returns:
    --------
    output_text: html object
        specifies length of IDs returned from search
    ids: list
        contains IDs returned from search

    """
    print('\nsubmit_cohort_query()')
    pp = pprint.PrettyPrinter(indent=4)

    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    if n is None:
        raise PreventUpdate

    timestamp = datetime.now().timestamp()

    logic_dictionary = {'all_of': all_terms, 'any_of': any_terms, 'none_of': none_terms}
    cohort_dictionaries = {"encoded": {"all_of": [], "any_of": [], "none_of": []},
                           "decoded": {"all_of": [], "any_of": [], "none_of": []}}

    for logic, selected_terms in logic_dictionary.items():
        if selected_terms:
            terms_encoded, terms_decoded = _create_conditional_logic_list(selected_terms, defined_terms)
            cohort_dictionaries["encoded"][logic] = terms_encoded
            cohort_dictionaries["decoded"][logic] = terms_decoded

    outpath = config['cohort_path']
    if kw_search_terms:
        term_outfile = os.path.join(outpath, 'search_terms.txt')
        utils.write_txt_file(term_outfile, kw_search_terms)
        if os.path.exists(term_outfile):
            print(f"successfully saved search terms to file {term_outfile}")
        else:
            print(f"could not save search terms to file {term_outfile}")

    for k, v in cohort_dictionaries.items():
        name = "cohort_dictionary_" + k + ".txt"
        cohort_out = os.path.join(outpath, name)
        utils.write_dictionary(v, cohort_out)
        if os.path.exists(cohort_out):
            print(f"successfully saved {k} cohort dictionary to {cohort_out}")
        else:
            print(f"could not save {k} cohort dictionary to {cohort_out}")

    print('\ncreate_queries {}'.format(print_time()))
    queries = query.create_queries(cohort_criteria=cohort_dictionaries['encoded'],
                                   main_filename=config['main_path'],
                                   gpc_path=config['gp_path'])
    pp.pprint(queries)
    print('\nquery_databases {}'.format(print_time()))
    ids = query.query_databases(cohort_criteria=cohort_dictionaries['encoded'],
                                queries=queries, main_filename=config['main_path'],
                                write_dir=config['cohort_path'], gpc_path=config['gp_path'],
                                out_filename=config['out_filename'], write=False)
    print('\nfinished query_databases {}'.format(print_time()))
    print('\n generating report {}'.format(print_time()))
    stats_dict, translation_df = stats.compute_stats(main_filename=config['main_path'],
                                               eids=ids,
                                               showcase_filename=config['showcase_path'],
                                               coding_filename=config['codings_path'])
    stats_report_dict = stats.create_report(translation_df)

    footer = dbc.ModalFooter(dbc.Button("Close", id="close_run_query_btn_new", className="ml-auto", style={"margin": "5px"}))
    output_text = html.P(f"Found {len(ids)} matching ids.")
    output_runquery = dbc.Row(dbc.Col([output_text,
                                       dbc.Button("Close", color='primary', id="run_query_close", style={"margin": "5px"})]))
    return output_text, ids, timestamp, stats_report_dict
