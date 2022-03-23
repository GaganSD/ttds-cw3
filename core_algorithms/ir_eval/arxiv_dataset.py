# -*- coding: utf-8 -*-
"""Arxiv Dataset.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GI32wRFGV9jXgvT4NQhsgectZqnI2lXR
"""

import json
import pandas as pd
import os
from datetime import datetime
from ../mongoDB_api_live_index import *
from ../live_index_generator import *
import os

def latest_date_create(list_dicts):
  max_date = datetime.min
  for temp_dict in list_dicts:
    t = datetime.strptime(temp_dict['created'], '%a, %d %b %Y %H:%M:%S %Z')
    if t > max_date: max_date = t
  return max_date.strftime("%d/%m/%Y")

def live_index():
  os.system("kaggle datasets download -d Cornell-University/arxiv")
  os.system("unzip arxiv.zip")

  rows = []
  for line in open('arxiv-metadata-oai-snapshot.json', 'r'):
      t = json.loads(line)
      rows.append(t)

  df = pd.DataFrame(rows)
  df.sort_values("update_date", ascending=False, inplace=True)
  df.drop_duplicates(keep="first", subset=['title'], inplace=True)
  df.sort_values("id", ascending=True, inplace=True)

  df = df[["id", "title", "versions", "abstract", "authors"]]
  df.loc[:, 'versions'] = df['versions'].map(latest_date_create)
  df.loc[:, 'authors'] = df['authors'].str.replace(' and ',', ')
  df.rename(columns={"versions": "date"}, inplace=True)
  df.loc[:, 'url'] = 'https://arxiv.org/abs/' + df['id']
  df.loc[:, 'text'] = " "

  client = MongoDBClient("34.142.18.57")

  # Update Index
  indexGen = IndexGenerator(client_ip = "34.142.18.57", activate_stemming = True, activate_stop = False, start_index=0, local_dataset=df, source_name="arxiv", identifier="id")
  indexGen.clean_indexing()
  indexGen.run_indexing()

  # insert_dataset_data
  success_num = client.insert_data(df, "paper", "arxiv", "id")
  print("# data inserted ", success_num)

  #client.update_data("paper", "arxiv", "my-datase", {"subtitle": "new new subtitle"})