import pandas as pd
import sqlite3
import numpy as np
import os
# from ukbcc import stats

#%%







sqlfile = "/Users/nathaliewillems/dev/genomics/repos/test/data/ukb_small.sqlite"

con = sqlite3.connect(sqlfile)

field_desc = pd.read_sql('SELECT * from field_desc', con)

field_desc.head(10)


#%%

select = field_desc.loc[field_desc['field_col'].isin(['34-0.0', '52-0.0', '22001-0.0', '21000-0.0', '22021-0.0'])]

select


#%%

field_tabs = select[['field', 'tab']].to_dict(orient='list')
field_tabs

eids = ['1000303', '1000770']

tab_types = field_desc['tab'].unique().tolist()

#%%

query_dict = {}

for tab in tab_types:
    fields = select.loc[select['tab'] == tab]['field'].unique().tolist()
    if fields:
        query_dict[tab] = fields
query_dict


#%%

results_df = []

for key in query_dict.keys():
    fields = query_dict[key]
    field_strings = [f"field={f}" for f in fields]
    cols_str = ",".join(fields)
    # print(cols_str)
    # print(field_strings)
    query_field = " or ".join(field_strings)
    # print(query_field)
    query_str = f"select eid, field, value from {key} where {query_field}"
    results = pd.read_sql(query_str, con)
    results_df.append(results)


#%%

results_df

#%%


stats_fields = ['34-0.0', '52-0.0', '22001-0.0', '21000-0.0', '22021-0.0']


criteria_dict = {'any_of': [(col, 'nan') for col in stats_fields]}

criteria_dict
query_tuples = [(vi[0], vi[1]) for v in criteria_dict.values() for vi in v]
query_tuples
