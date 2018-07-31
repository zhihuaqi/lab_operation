#!/usr/bin/env python
import sys
import scipy.stats as stats
import pandas as pd
import numpy as np
import sqlite3

def extract_info_from_sql_file(path_to_file):
    ## connect to the sqlite DB
    sqlite_file = path_to_file
    conn = sqlite3.connect(sqlite_file)

    ## join the batch_to_component and component tables
    sql = "SELECT bc.batch_id, c.component_type, c.name as component_name " \
          "FROM batch_to_component bc JOIN component c ON bc.component_id = c.id;"
    component_for_batches = pd.read_sql_query(sql, conn)

    ## transform long table to wide table
    component_info = component_for_batches.pivot('batch_id', 'component_type', 'component_name')
    component_info['batch_id'] = component_info.index

    ## extract metric info for each batch
    metric_for_batches = pd.read_sql_query("SELECT b.id as batch_id, b.metric FROM batch b;", conn)

    ## merge the component and metric info for each batch
    info_batches = pd.merge(component_info, metric_for_batches, on='batch_id', how='outer')
    info_batches = info_batches.set_index('batch_id')

    ##extract the component_info list
    component_list = component_for_batches.groupby(['component_type', 'component_name']).agg(lambda x: 1)
    component_list.reset_index(inplace=True)
    component_list = component_list[['component_type', 'component_name']]

    return info_batches, component_list

def perform_t_test(component_type, component_name, df):
    g1=df[df[component_type] == component_name]['metric']
    g2=df[df[component_type] != component_name]['metric']
    t_stat, p_val = stats.ttest_ind(g1, g2)
    return pd.Series([t_stat, p_val], index=['effect_size', 'p_val'])

def evaluate_significance(pvals, degreeOfFreedom, alpha=0.01):
    return pvals.apply(lambda p: p * degreeOfFreedom < alpha)

if __name__ == "__main__":

    ## read path to sqlite file and alpha
    sqlite_file = sys.argv[1]
    if len(sys.argv) >= 3:
        alpha = float(sys.argv[2])
    else:
        alpha = 0.01

    ## read data
    info, comp = extract_info_from_sql_file(sqlite_file)

    ## perform t-tests
    res = comp.apply(lambda row: perform_t_test(row['component_type'], row['component_name'], info), axis=1)

    ## multi-testing adjustment
    dof = len(comp.index) - comp['component_type'].nunique()
    res['is_significant'] = evaluate_significance(res['p_val'], dof, alpha)

    ## drop the raw p values
    res = res.drop('p_val', 1)

    ## combine the result and write output
    all = pd.concat([comp, res], axis=1)
    all.to_csv('result.csv', index=False)






