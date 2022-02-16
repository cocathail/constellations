#!/usr/bin/python

import requests
import argparse
import pandas as pd

parser = argparse.ArgumentParser(description='Tool to select oldest sequence of a lineage with strong support')

parser.add_argument('-i',
                    '--input_file',
                    help="pangolin output csv",
                    type=str,
                    required=True)

args = parser.parse_args()

def read_join_filter(infile, query_output):
    df1 = pd.read_csv(infile)
    df2 = pd.read_csv(query_output, sep='\t')
    print(df2.head())
    df2 = df2.rename(columns={'accession': 'taxon', 'collection_date': 'date'})
    print(df2.head())
    df3 = df1.set_index('taxon').join(df2.set_index('taxon'))
    df3 = df3.dropna(subset=['scorpio_support'])
    df3 = df3[df3['scorpio_support'] > 0.95 ]
    df3 =df3[df3['date'] > '2020-09-01']
    df3 = df3.sort_values('lineage')
    df3 = df3[['lineage','scorpio_call','scorpio_support','date', 'note']]
    df3.reset_index(level=0, inplace=True)
    df3 = (df3.sort_values('date').groupby('lineage', as_index=False).first().reset_index(drop=True).assign(a=lambda x: x.index + 1))
    df3.to_csv('representative_lineages_out.txt', sep='\t')

def query_api():
    url = "https://www.ebi.ac.uk/ena/portal/api/search"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'result': 'sequence', 'query':'tax_tree(2697049)', 'fields': 'collection_date', 'limit': '0', 'format': 'tsv'}
    r = requests.post(url, data=payload, headers=headers)
    results = r.text
    return results


if __name__ == '__main__':
    query_out = query_api()
    with open('output.txt', 'w', encoding="utf-8") as out_file:
        out_file.write(query_out)
    read_join_filter(args.input_file, 'output.txt')