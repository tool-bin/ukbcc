from io import StringIO
import pandas as pd
import re
#from ukbcc import db

def create_query_tuples(cohort_criteria, field_desc):
    print("create query tuples")
    query_tuples = [(vi[0], vi[1]) for v in cohort_criteria.values() for vi in v]
    # query_tuples = [list(qt) + [field_desc[field_desc['field'] == str(int(float(qt[0])))]['tab'].iloc[0]] for qt in query_tuples]
    query_tuples = [list(qt) + [field_desc[field_desc['field'] == qt[0]]['tab'].iloc[0]] for qt in query_tuples]
    print(query_tuples)
    query_tuples = [dict(zip(('field', 'val', 'tab'), q)) for q in query_tuples]
    return(query_tuples)

def pivot_results(field_desc, query_tuples):
	field_sql_map = {f: field_desc[field_desc['field'] == f]['sql_type'].iloc[0] for f in
					 set([q['field'] for q in query_tuples])}
	#print(field_sql_map)
	#col_names_q = ",".join(
	# 	[f"cast(max(distinct case when field='{f}' then value end) as {field_sql_map[f]}) as 'f{f}'" for f in set([q['field'] for q in query_tuples])])

	uniq_fields=set([q['field'] for q in query_tuples])
	pivot_queries = [",".join(generate_main_column_queries(f,field_desc,field_sql_map)) for f in uniq_fields if f not in ['read_2', 'read_3']]
	if 'read_2' in uniq_fields or  'read_3' in uniq_fields:
		pivot_queries = pivot_queries + [f"cast(max(distinct case when field='{q['field']}' and value='{q['val']}' then 1 end) as VARCHAR) as 'f{q['field']}-{q['val']}'" for
									 q in query_tuples if q['field'] in ['read_2', 'read_3'] ]
	#f"max(distinct case when field='{q['field']}' and value ='{q['val']}' then value end) as 'f{q['field']}_{q['val']}'"
	#for q in query_tuples])
	return(",".join(pivot_queries))

def generate_main_column_queries(field, field_desc,field_sql_map):

	fs = expand_field(field, field_desc)
	distinct_str = lambda f: f"distinct case when field='{f[0]}' and time='{f[1]}' and array='{f[2]}' then value end"

	return([f"cast(max({distinct_str(f)}) as {field_sql_map[f[0]]}) as 'f{f[0]}-{f[1]}.{f[2]}'" for f in fs])

def expand_field(field, field_desc):
	fs = field_desc[field_desc["field"] == field]["field_col"].to_list()
	return [re.split(r'[-.]', f) for f in fs]

def join_field_vals(fs, field_desc):
	if (not fs):
		return []
	quote = lambda x: '"' if field_desc[field_desc['field'] == re.sub('^f', '', x)]['sql_type'].iloc[
								 0] == 'VARCHAR' else ""
	return ['"{}" {}'.format(f'{f}_{v}', 'is not NULL' if v == 'nan' else '={}{}{}'.format(quote(f), v, quote(f)))
			for f, v in fs]


def filter_pivoted_results(main_criteria, field_desc):
	#NB: which fields do we one-hot-encode? Those with array values. Need to do some checks to see if this all types of fields.
	q = {}

	# q['all_of'] =  " AND ".join(join_field_vals(main_criteria['all_of']))#field_desc[field_desc['field']=='read_2']['ukb_type'].iloc[0]=='Categorical multiple'
	q['all_of'] = " AND ".join(join_field_vals(main_criteria['all_of'], field_desc))
	# q['any_of'] =  "({})".format(" OR ".join(join_field_vals(main_criteria['any_of'])))
	q['any_of'] = "({})".format(" OR ".join(join_field_vals(main_criteria['any_of'], field_desc)))
	# q['none_of'] = "NOT ({})".format(" OR ".join(join_field_vals(main_criteria['none_of'])))
	# q['none_of'] = "NOT ({})".format(" OR ".join(join_field_vals([(f'{k}_{v}', v) for k, v in main_criteria['none_of']])))
	q['none_of'] = "NOT ({})".format(' OR '.join([f'{x[0]} AND "{x[1][0]}_{x[1][1]}" is not NULL' for x in
												  zip(join_field_vals(main_criteria['none_of'], field_desc),
													  main_criteria['none_of'])]))
	selection_query = " AND ".join([qv for qk, qv in q.items() if main_criteria[qk]])
	return(selection_query)

field_desc = pd.read_csv(StringIO(re.sub('[ \t][ \t]+', ',',
    "field_col   field  category             ukb_type  sql_type  pd_type    tab\n"
          "eid     eid       -1               Integer  INTEGER   Int64      None\n"
    "21017-0.0   21017   100016                  Text  VARCHAR  object       str\n"
    "41270-0.1   41270     2002  Categorical multiple  VARCHAR  object       str\n"
     "6070-0.0    6070   100016    Categorical single  VARCHAR  object       str\n"
       "53-0.0      53   100024                  Date  NUMERIC  object  datetime\n"
     "4286-0.0    4286   100031                  Time  NUMERIC  object  datetime\n"
    "21003-0.0   21003   100024               Integer  INTEGER   Int64       int\n"
    "22182-0.0   22182   100035              Compound  VARCHAR  object       str\n"
       "50-0.0      50   100010            Continuous     REAL   float      real\n"
       "read_3  read_3   read_3  Categorical multiple  VARCHAR  object       str\n"
    )))

cohort_criteria = {'all_of': [], 'any_of': [['21017', '1263']], 'none_of': []}

main_criteria = {k: [('f' + vi[0], vi[1]) for vi in v if vi[0] in field_desc['field'].values]
				 for k, v in cohort_criteria.items()}
main_criteria

#%%
query_tuples = create_query_tuples(cohort_criteria, field_desc)

#%%
pivot_query = pivot_results(field_desc, query_tuples)


#%%

selection_query = filter_pivoted_results(main_criteria, field_desc)
selection_query
