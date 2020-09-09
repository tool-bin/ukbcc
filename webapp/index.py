import dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import json

from app import app
from apps import config_app, kw_search_app, include_kw_app, definitions_app, query_app, results_app
import webbrowser
from threading import Timer

from dash.exceptions import PreventUpdate

#Define storage for web-based interface
app.layout = dbc.Container(
<<<<<<< HEAD
	[
		dcc.Store(id="config_store", storage_type='local'),
		dcc.Store(id="kw_search", storage_type='session'),
		dcc.Store(id="cohort_id_results", storage_type='memory'),
		dcc.Store(id="include_fields", storage_type='session'),
		dcc.Store(id="defined_terms", storage_type='session'),
		dcc.Store(id='selected_terms_data', storage_type='memory'),
		dcc.Store(id='cohort_id_results_modified', storage_type='memory'),

		html.H1('UKB Cohort Curator'),
		html.Hr(),
		dbc.Tabs(
			[
				dbc.Tab(label="Configure", tab_id="config"),
				dbc.Tab(label="Define Terms", tab_id="definitions"),
				dbc.Tab(label="Cohort search", tab_id="query"),
				#dbc.Tab(label="Exclude fields", tab_id="exclude"),
				dbc.Tab(label="Results History", tab_id="results")
			],
			id="tabs",
			active_tab="config"
		),
		html.Div(id="tab-content", className="p-4"),
		html.Div(id='search_logic_state', style={'display': 'none'}),

	]
=======
    [
        dcc.Store(id="config_store", storage_type='local'),
        dcc.Store(id="kw_search", storage_type='memory'),
        dcc.Store(id="kw_search_terms", storage_type='session'),
        dcc.Store(id="cohort_id_results", storage_type='memory'),
        dcc.Store(id="cohort_id_results_timestamp", storage_type='memory'),
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
>>>>>>> ui
)


@app.callback(
	Output("tab-content", "children"),
	[Input("tabs", "active_tab")]
)
<<<<<<< HEAD
def render_tab_content(active_tab):
	"""
	This callback takes the 'active_tab' property as input, as well as the
	stored graphs, and renders the tab content depending on what the value of
	'active_tab' is.
	"""
	if active_tab:
		print("active tab is {}".format(active_tab))
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

	#return active_tab#html.P("Click config to start")
=======
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
>>>>>>> ui


@app.callback(
<<<<<<< HEAD
	[Output("tabs", "active_tab"),
	 Output("cohort_id_results_modified", "data")],
	[Input({'type': 'nav_btn', 'name': ALL}, "n_clicks"),
	Input("cohort_id_results", "modified_timestamp")],
	[State("cohort_id_results", "data"),
	 State("cohort_id_results_modified", "data")]
)
def tab_button_click_handler(values, results_ts_new, results, results_ts_old):
	ctx = dash.callback_context
	print("ctx in tab click handler {}".format(ctx.triggered))
	print("tab click handlers click value {}".format(values))
	#TODO: Why not make a dictionary of the fields and automate this mapping. But I'm so lazy...
	button_map={"next_button_config":"definitions",
				"prev_button_terms": "config",
				"next_button_terms": "query",
				"prev_button_query": "definitions",
				"next_button_query": "results",
				"prev_button_results": "query"
				}

	print("tab_button_click_handler - results_ts_new: {}".format(results_ts_new))
	print("tab_button_click_handler - results_ts_old: {}".format(results_ts_old))
	print("tab_button_click_handler - results: {}".format(results))
	print("tab_button_click_handler - ctx.trig: {}".format(ctx.triggered))

	print (ctx.triggered is None)
	print(ctx.triggered[0]['value'] =='cohort_id_results.modified_timestamp')
	print(results_ts_new==-1)
	# print("results timestamp {}".format(results_timestamp))
	if ctx.triggered is None or \
			ctx.triggered[0]['value'] =='cohort_id_results.modified_timestamp' or \
			results_ts_new==-1:
		print ('tab_button_click_handler - PreventUpdate')
		raise PreventUpdate

	if results_ts_new!=results_ts_old and results_ts_new!=-1 and results is not None:
		print("Change tabs due to results")
		return "results", results_ts_new
	if ctx.triggered and ctx.triggered[0]['value'] and ctx.triggered[0]['value']!= -1 :
		print("Change tabs due to buttons")
		print("ctx {}".format(ctx.triggered[0]['value']))
		button_id_dict_str = ctx.triggered[0]['prop_id'].split('.')[0]
		print("button id {}".format(button_id_dict_str))
		button_id_dict=json.loads(button_id_dict_str)
		return button_map[button_id_dict["name"]], results_ts_new
	return "config", results_ts_new
=======
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
    print("ctx {}".format(ctx.triggered))
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
>>>>>>> ui

port = 8050 #default port

def open_browser():
	webbrowser.open_new("http://localhost:{}".format(port))

if __name__ == '__main__':
<<<<<<< HEAD
	#Timer(1, open_browser).start();
	app.run_server(debug=True, use_reloader=True, dev_tools_props_check=False, dev_tools_ui=True)
=======
    app.run_server(debug=True, use_reloader=True, dev_tools_props_check=False, dev_tools_ui=True)
>>>>>>> ui
