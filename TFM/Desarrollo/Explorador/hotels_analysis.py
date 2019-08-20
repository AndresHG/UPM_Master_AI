import os
from pprint import pprint as pp
import pandas as pd
import json
import numpy as np

timestamp_data = "stimestamp"

raw_columns = ["Unnamed: 0", "stimestamp", "hotel_id", "hotel_name", "date_from",
               "date_to", "days_in_advance", "adults", "kids", "room", "room_normalized",
               "rate", "rate_normalized", "board", "min_stay", "price", "currency"]

data = {"stimestamp": {"min": "2019-06-27 01:24:30",
                       "max": "2018-06-27 01:24:30"},
        "date_from": {"min": np.inf,
                      "max": 0},
        "date_to": {"min": np.inf,
                    "max": 0},
        "days_in_advance": {"min": np.inf,
                            "max": 0},
        "adults": {"min": np.inf,
                   "max": 0},
        "kids": {"min": np.inf,
                 "max": 0},
        "room_normalized": [],
        "rate_normalized": [],
        "board": [],
        "min_stay": {"min": np.inf,
                     "max": 0}}

def  check_header(df):
    if not "stimestamp" in df.columns:
        df.columns = raw_columns


hotels_path = "Dataset/Hoteles/"

for fileh in os.listdir(hotels_path):
    df = pd.read_csv(hotels_path + fileh)
    for column in df.columns:
        if column == timestamp_data:
            if min(df[column]) < data["stimestamp"]["min"]:
                data["stimestamp"]["min"] = min(df[column])
                pp(min(df[column]))
            if max(df[column]) > data["stimestamp"]["max"]:
                data["stimestamp"]["max"] = max(df[column])
                pp(max(df[column]))
        elif column in ["room_normalized", "rate_normalized", "board"]:
            data[column] = list(set(data[column] + list(df[column])))
        elif column in data.keys():
            if data[column]["min"] > min(df[column]):
                data[column]["min"] = min(df[column])
            if data[column]["max"] < max(df[column]):
                data[column]["max"] = max(df[column])

pp(data)
with open('result.json', 'w') as fp:
    json.dump(data, fp, indent=4, sort_keys=True)
