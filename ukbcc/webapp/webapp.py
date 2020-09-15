import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import json

from .app import app
from .apps import config_app, kw_search_app, include_kw_app, definitions_app, query_app, results_app
import webbrowser
from threading import Timer

from dash.exceptions import PreventUpdate

#Define storage for web-based interface
app.layout = dbc.Container(
    [
        dcc.Store(id="config_store", storage_type='local'),
        dcc.Store(id="kw_search", storage_type='memory'),
        dcc.Store(id="kw_search_terms", storage_type='session'),
        dcc.Store(id="cohort_id_results", storage_type='memory'),
        dcc.Store(id="cohort_id_results_timestamp", storage_type='memory'),
        dcc.Store(id="cohort_id_report", storage_type='session'),
        dcc.Store(id="include_fields", storage_type='session'),
        dcc.Store(id="defined_terms", storage_type='session'),
        dcc.Store(id='selected_terms_data', storage_type='memory'),

        html.H1('UKB Cohort Curator'),
        html.Hr(),
        dbc.Tabs(
            [
                dbc.Tab(label="Configure", tab_id="config"),
                dbc.Tab(label="Define Terms", tab_id="definitions"),
                dbc.Tab(label="Cohort Search", tab_id="query"),
                #dbc.Tab(label="Exclude fields", tab_id="exclude"),
                dbc.Tab(label="Results History", tab_id="results")
            ],
            id="tabs",
            active_tab="config"
        ),
        html.Div(id="tab-content", className="p-4"),
        html.Div(id='search_logic_state', style={'display': 'none'}),

    ]
)


@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab: str):
    """Render tabs.

    Keyword arguments:
    ------------------
    active_tab: str
        string indicating which tab is currently selected

    Returns:
    --------
    selected tab content: dbc.Tab object
        selected tab content (defaults to config_tab)

    """
    if active_tab:
        if active_tab == "config":
            return config_app.tab
        elif active_tab == "definitions":
            return definitions_app.tab
        elif active_tab == "query":
            return query_app.tab
        elif active_tab == "results":
            return results_app.tab
        else:
            return html.P("Tab '{}' is not implemented...".format(active_tab))
    else:
        return config_app.tab


@app.callback(
    Output("tabs", "active_tab"),
    [Input({'type': 'nav_btn', 'name': ALL}, "n_clicks"),
    Input("cohort_id_results_timestamp", "modified_timestamp")],
    [State("cohort_id_results", "data")]
)
def tab_button_click_handler(values: str, cohort_id_results_timestamp: int, data: list):
    """Configure tab navigation for each tab page.

    Keyword arguments:
    ------------------
    values: str
        indicates number of clicks on "nav_btn"
    cohort_id_results_timestamp: int
        timestamp indicating when cohort_id_results_timestamp storage was updated
    data: list
        data stored in cohort_id_results storage


    Returns:
    --------
    selected tab: str
        selected tab string

    """
    ctx = dash.callback_context
    button_map={"next_button_config":"definitions",
                "prev_button_terms": "config",
                "next_button_terms": "query",
                "prev_button_query": "definitions",
                "next_button_query": "results",
                "prev_button_results": "query"
                }

    prop_id = ctx.triggered[0]['prop_id']
    modified_timestamp_prop = "cohort_id_results_timestamp.modified_timestamp"
    if cohort_id_results_timestamp:
        if prop_id == modified_timestamp_prop:
            return "results"
        else:
            if ctx.triggered and ctx.triggered[0]['value']:
                button_id_dict_str = ctx.triggered[0]['prop_id'].split('.')[0]
                button_id_dict=json.loads(button_id_dict_str)
                return button_map[button_id_dict["name"]]
    else:
        if ctx.triggered and ctx.triggered[0]['value']:
            button_id_dict_str = ctx.triggered[0]['prop_id'].split('.')[0]
            button_id_dict=json.loads(button_id_dict_str)
            return button_map[button_id_dict["name"]]

port = 8050 #default port

def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))

def main():
    Timer(1, open_browser).start();
    app.run_server(debug=True, use_reloader=False, dev_tools_props_check=False, dev_tools_ui=False, port=port)
    # gunicorn -w 4 webapp:main

if __name__ == '__main__':
    main()
