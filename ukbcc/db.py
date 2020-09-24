import pandas as pd
import sqlite3
import progressbar
from datetime import datetime
import re
import os

# Create a table for a given category ('cat')
def create_long_value_table_query(tab_name, tab_type):
	field_cols = ["eid", "field", "time", "value"]
	field_col_types = ["INTEGER", "VARCHAR", "INTEGER", tab_type]
	cols = ','.join(map(' '.join, zip(field_cols, field_col_types)))
	cmd = f"CREATE TABLE {tab_name} ({cols}) ;"
	return (cmd)


def create_type_maps():
	ukbtypes = ['Date', 'Categorical multiple', 'Integer',
				'Categorical single', 'Text',
				'Time', 'Continuous', 'Compound']
	sqltypes = ['NUMERIC', 'VARCHAR', 'INTEGER',
				'VARCHAR', 'VARCHAR',
				'NUMERIC', 'REAL', 'VARCHAR']
	# pandastypes can only have strings integers and floats in read_csv
	pandastypes = ['object', 'object', 'Int64',
				   'object', 'object',
				   'object', 'float', 'object']
	#
	ukbtype_sqltype_map = dict(zip(ukbtypes, sqltypes))
	ukbtype_pandastypes_map = dict(zip(ukbtypes, pandastypes))
	#
	return ukbtype_sqltype_map, ukbtype_pandastypes_map


def populate_gp(con, gpc_filename, nrow, step):
	with progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Bar(), progressbar.ETA(), ],
								 max_value=int(nrow / step) + 1) as bar:
		for i, chunk in enumerate(
				pd.read_csv(gpc_filename, chunksize=step, low_memory=False, encoding="ISO-8859-1", delimiter='\t')):
			chunk['read_2'] = chunk.read_2.combine_first(chunk.read_3)

			# To have field as data_provider and value as read2/3
			trips = chunk.rename(columns={'data_provider': 'field', 'event_dt': 'time', 'read_2': 'value'})[
				['eid', 'field', 'time', 'value']]
			trips = trips[trips['value'].notnull()]
			trips['field'] = 'read_' + trips['field'].astype(str)

			x = con.executemany(f'INSERT INTO {"str"} values({",".join("?" * len(trips.columns))})',
								trips.values.tolist())
			bar.update(i)
	#
	print('UKBCC database - finished populating GP clinical')


def create_tab_fields_map(tabs, field_desc):
	tab_fields = {}
	type_lookups = dict(
		zip(['str', 'int', 'real', 'datetime'], [['Text', 'Compound', 'Categorical multiple', 'Categorical single'],
												 ['Integer'],
												 ['Continuous'],
												 ['Date', 'Time']]))
	for tab_name, field_type in tabs.items():
		tab_fields[tab_name] = \
			field_desc[(field_desc['ukb_type'].isin(type_lookups[tab_name])) & (field_desc['field_col'] != 'eid')][
				'field_col']

	return (tab_fields)


def create_field_desc(main_df, showcase_file):
	data_dict = pd.read_csv(showcase_file)
	data_dict['FieldID'] = list(map(str, data_dict['FieldID']))
	ukbtype_sqltype_map, ukbtype_pandastypes_map = create_type_maps()

	field_desc = pd.DataFrame({'field_col': main_df.columns,
							   'field': ['eid'] + [str(x.split('-')[0]) for x in main_df.columns[1:]]})
	field_desc['category'] = [-1] + list(
		map(dict(zip(data_dict['FieldID'], data_dict['Category'])).get, field_desc['field'][1:]))
	field_desc['ukb_type'] = list(map(dict(zip(['eid'] + data_dict['FieldID'].to_list(),
											   ['Integer'] + data_dict['ValueType'].to_list())).get,
									  field_desc['field']))

	field_desc['sql_type'] = list(map(ukbtype_sqltype_map.get, field_desc['ukb_type']))
	field_desc['pd_type'] = list(map(ukbtype_pandastypes_map.get, field_desc['ukb_type']))

	# Append gp_clinical data
	field_desc_new = pd.DataFrame({
		'field_col': ['read_2', 'read_3'],
		'field': ['read_2', 'read_3'],
		'category': ['read_2', 'read_3'],
		'ukb_type': ['Categorical multiple', 'Categorical multiple'],
		'sql_type': ['VARCHAR', 'VARCHAR'],
		'pd_type': ['object', 'object']
	})

	return field_desc.append(field_desc_new)


def create_table_queries(tabs):
	#
	# Create a table for every sqltype
	print("create tables")
	queries=[]
	for tab_name, field_type in tabs.items():
		queries.append(f"DROP TABLE IF EXISTS {tab_name};")
		queries.append(create_long_value_table_query(tab_name=tab_name, tab_type=field_type))
	return queries


def insert_main_chunk(chunk, tabs, tf_eid, tab_fields):
	for tab_name, field_type in tabs.items():
		# Convert to triples, remove nulls and then explode field
		trips = chunk[tab_fields[tab_name].append(tf_eid)].melt(id_vars='eid', value_vars=tab_fields[tab_name])
		trips = trips[trips['value'].notnull()]

		# This is constant if we have it in the row before?
		trips['field'], trips['time'], trips['array'] = trips['variable'].str.split("[-.]", 2).str
		trips = trips[['eid', 'field', 'time', 'value']]
		if (tab_name == 'datetime'):
			trips['value'] = pd.to_numeric(trips['value'])
		#
		# if not trips.shape[0]:
		#    continue
		return (f'INSERT INTO {tab_name} values({",".join("?" * len(trips.columns))})',
							trips.values.tolist())


def insert_gp_clin_chunk(chunk):
	chunk['read_2'] = chunk.read_2.combine_first(chunk.read_3)

	# To have field as data_provider and value as read2/3
	trips = chunk.rename(columns={'data_provider': 'field', 'event_dt': 'time', 'read_2': 'value'})[
		['eid', 'field', 'time', 'value']]
	trips = trips[trips['value'].notnull()]
	trips['field'] = 'read_' + trips['field'].astype(str)

	return (f'INSERT INTO {"str"} values({",".join("?" * len(trips.columns))})',
						trips.values.tolist())


def create_index(con):
	print('Creating string index')
	con.execute('CREATE INDEX str_index ON str (field, value, time, eid)')
	print('Creating integer index')
	con.execute('CREATE INDEX int_index ON int (field, value, time, eid)')
	print('Creating continuous index')
	con.execute('CREATE INDEX real_index ON real (field, value, time, eid)')
	print('Creating date index')
	con.execute('CREATE INDEX dt_index ON datetime (field, value, time, eid)')

# Get estimate of number of lines in a file. If file is <10MB, get exact, otherwise estimate based
# on the number of lines in the first 10MB and add 10%
def estimate_lines(filename):
	filesize = os.path.getsize(filename)
	if filesize < 10*1024**2:
		nlines = sum(1 for line in open(filename))
	else:
		with open(filename, 'rb') as file:
			buf = file.read(10*1024**2)
			nlines_est = len(buf) // buf.count(b'\n')
		nlines = 1.1* os.path.getsize(filename) // nlines_est
	return nlines

# Add columns to field_desc indicate which table each field goes into
def add_tabs_to_field_desc(field_desc, tab_fields):
	field_tab_map = {item: k for k, v in tab_fields.items() for item in v.to_list()}
	field_tab_map['eid'] = None
	field_desc['tab'] = list(map(field_tab_map.get, field_desc['field_col']))


# TODO: do more checks on whether the files exist
def create_sqlite_db(db_filename: str, main_filename: str, gp_clin_filename: str,
					 showcase_file: str, step=5000) -> sqlite3.Connection:
	"""Returns basic statistics for given columns and a translated dataframe.

	Keyword arguments:
	------------------
	db_filename: str
		path and filename of db to create
	main_filename: str
		path and filename of main dataset
	gpc_filename: str
		path and filename of gp_clinical table dataset
	showcase_file: str
		path and filename of showcase file

	Returns:
	--------
	conn: sqlite3.Connection
		Connection to the written database

	"""
	main_df = pd.read_csv(main_filename, nrows=1)
	field_desc = create_field_desc(main_df, showcase_file)

	# Connect to db
	con = sqlite3.connect(database=db_filename)
	tabs = dict(zip(['str', 'int', 'real', 'datetime'], ["VARCHAR", "INTEGER", "REAL", "REAL"]))
	tab_fields = create_tab_fields_map(tabs, field_desc)
	#Create queries to drop and create tables.
	x=map(con.execute, create_table_queries(tabs))

	# Add columns to field_desc indicate which table each field goes into
	# Then write fields to a table in the database
	field_desc = add_tabs_to_field_desc(field_desc, tab_fields)
	field_desc.to_sql("field_desc", con, if_exists='replace', index=False)

	# Create list of dates, dictionary of all column types and a boolean vector of where 'eid' sits
	date_cols = field_desc['field_col'][
		(field_desc['ukb_type'] == 'Date') | (field_desc['ukb_type'] == 'Time')].to_list()
	dtypes_dict = dict(zip(field_desc['field_col'].to_list(), field_desc['pd_type'].to_list()))
	tf_eid = field_desc[field_desc['field_col'] == 'eid']['field_col']

	# GP clinical data
	max_pb = int(estimate_lines(gp_clin_filename) / step) + 1
	pb_widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.ETA(), ]
	reader = pd.read_csv(gp_clin_filename, chunksize=step, low_memory=False, encoding="ISO-8859-1", delimiter='\t',
						 dtype=dtypes_dict, parse_dates=date_cols)
	with progressbar.ProgressBar(widgets=pb_widgets, max_value=max_pb)		 as bar:
		for i, chunk in enumerate(reader):
			x = con.executemany(insert_gp_clin_chunk(chunk))
			bar.update(i)

	# TODO: This is slow. We can parallelise this using Queue
	# TODO: Repeats the specific code above, except insert call and delimiter
	max_pb = int(estimate_lines(main_filename)/ step)+ 1
	reader = pd.read_csv(main_filename, chunksize=step, low_memory=False, encoding="ISO-8859-1",
						 dtype=dtypes_dict, parse_dates=date_cols)
	with progressbar.ProgressBar(widgets=pb_widgets, max_value=max_pb) as bar:
		for i, chunk in enumerate(reader):
			x = con.executemany(insert_main_chunk(chunk, tabs, tf_eid, tab_fields))
			bar.update(i)
	#
	con.commit()
	print('UKBCC database - finished populating')

	create_index(con)
	print('UKBCC database - finished')

	return (con)


#
#
# query_tuples: list of tuples, each with 3 entries: field, condition, value
# a = con.execute('''
#            select eid,
#                   max(distinct case when field=6072 then value end) as f6072,
#          from (select * from str where
#                field = 6072 and value = 1 or
#                field = 21000
#          union
#                select * from real where
#                field = 5262 or
#                field = 5263 or
#                field = 5254 or
#                field = 5255)
#         GROUP BY eid LIMIT 10''').fetchall()
###
def query_sqlite_db(db_filename: str, cohort_criteria: dict):
	# TODO: Fix cohort criteria generation so that its more inline with the db we create.
	print("orig cohort_criteria: {}".format(cohort_criteria))
	cohort_criteria = {k: [(re.sub(r'\.[0-9]+$', '', v0), v1) for (v0, v1) in vs] for k, vs in cohort_criteria.items()}
	print("new cohort_criteria: {}".format(cohort_criteria))

	print(f'Open database {datetime.now()}')
	con = sqlite3.connect(database=db_filename)

	print(f'Read field info {datetime.now()}')
	field_desc = pd.read_sql('SELECT * from field_desc', con)
	print(f'Done {datetime.now()}')

	print("generate main criteria: {}".format(cohort_criteria))
	# main_criteria = {k: [('f'+str(int(float(vi[0]))),vi[1]) for vi in v if str(int(float(vi[0]))) in field_desc['field'].values]
	# 				 for k, v in cohort_criteria.items()}
	main_criteria = {k: [('f' + vi[0], vi[1]) for vi in v if vi[0] in field_desc['field'].values]
					 for k, v in cohort_criteria.items()}

	# Fit each condition to a template and derive a final filter
	# Fit each condition to a template and derive a final filter
	def join_field_vals(fs):
		if (not fs):
			return []
		quote = lambda x: '"' if field_desc[field_desc['field'] == re.sub('^f', '', x)]['sql_type'].iloc[
									 0] == 'VARCHAR' else ""
		return ['"{}" {}'.format(f'{f}_{v}', 'is not NULL' if v == 'nan' else '={}{}{}'.format(quote(f), v, quote(f)))
				for f, v in fs]

	print(f'generate selection criteria')
	q = {}

	# q['all_of'] =  " AND ".join(join_field_vals(main_criteria['all_of']))#field_desc[field_desc['field']=='read_2']['ukb_type'].iloc[0]=='Categorical multiple'
	q['all_of'] = " AND ".join(join_field_vals(main_criteria['all_of']))
	print('1')
	# q['any_of'] =  "({})".format(" OR ".join(join_field_vals(main_criteria['any_of'])))
	q['any_of'] = "({})".format(" OR ".join(join_field_vals(main_criteria['any_of'])))
	print('2')
	# q['none_of'] = "NOT ({})".format(" OR ".join(join_field_vals(main_criteria['none_of'])))
	# q['none_of'] = "NOT ({})".format(" OR ".join(join_field_vals([(f'{k}_{v}', v) for k, v in main_criteria['none_of']])))
	q['none_of'] = "NOT ({})".format(' OR '.join([f'{x[0]} AND "{x[1][0]}_{x[1][1]}" is not NULL' for x in
												  zip(join_field_vals(main_criteria['none_of']),
													  main_criteria['none_of'])]))
	print('3')
	selection_query = " AND ".join([qv for qk, qv in q.items() if main_criteria[qk]])

	print('generate query_tuples {}'.format(cohort_criteria.values()))
	# Add the table for the field inop each query and turn in them into dictionaries to help readability
	# query_tuples = [(int(float(vi[0])), vi[1]) for v in cohort_criteria.values() for vi in v]
	print(1)
	query_tuples = [(vi[0], vi[1]) for v in cohort_criteria.values() for vi in v]
	# query_tuples = [list(qt) + [field_desc[field_desc['field'] == str(int(float(qt[0])))]['tab'].iloc[0]] for qt in query_tuples]
	print(2)
	query_tuples = [list(qt) + [field_desc[field_desc['field'] == qt[0]]['tab'].iloc[0]] for qt in query_tuples]
	print(3)
	query_tuples = [dict(zip(('field', 'val', 'tab'), q)) for q in query_tuples]

	print('generate column naming query')
	# column naming query
	field_sql_map = {f: field_desc[field_desc['field'] == f]['sql_type'].iloc[0] for f in
					 set([q['field'] for q in query_tuples])}
	# col_names_q = ",".join([f"cast(max(distinct case when field='{f}' then value end) as {field_sql_map[f]}) as 'f{f}'" for f in set([q['field'] for q in query_tuples])])
	col_names_q = ",".join([
		f"max(distinct case when field='{q['field']}' and value ='{q['val']}' then value end) as 'f{q['field']}_{q['val']}'"
		for q in query_tuples])

	# Make query: select * from tab where field=f1 and value=v1 or field=f2 and value=v2 ...
	# Make query: select * from tab where field=f1 and value=v1 or field=f2 and value=v2 ...
	def tab_select(tab, qts):
		if not qts:
			return ""
		quote = lambda x: '"' if field_desc[field_desc['field'] == re.sub('^f', '', x)]['sql_type'].iloc[
									 0] == 'VARCHAR' else ""
		return 'select * from {} where {}'.format(tab,
												  " or ".join(['field="{}" and value {}'.format(
													  q['field'],
													  'is not NULL' if q['val'] == 'nan' else '={}{}{}'.format(
														  quote(q['field']), q['val'], quote(q['field']))
												  ) for q in qts]))  # TODO: duplicates join_field_vals

	# print('derive unique tabs')
	tabs = [t for t in field_desc['tab'].iloc[1:].unique()]
	# Look at the fields in each table, form into query, take union
	union_q = "(" + " union ".join(
		filter(len, [tab_select(tab, [qt for qt in query_tuples if qt['tab'] == tab]) for tab in tabs])) + ")"

	q = f'''select * from (
            select eid, {col_names_q}
          from {union_q}
         GROUP BY eid) where {selection_query}'''.strip('\n')

	print(f'Run query {datetime.now()}\n {q}')
	res = pd.read_sql(q, con)
	print(f'Done {datetime.now()}')
	return (res)
