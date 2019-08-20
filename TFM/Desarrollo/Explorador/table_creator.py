

import pandas as pd
from datetime import datetime
from pprint import pprint as pp
import json
import os
import shutil
import numpy as np

from modules.aux_functions import *
from modules.reservation_management import get_reservation_code
from modules.global_vars import *
from modules.table_manager import manage_table, write_table_data, get_table_data

np.random.seed(583)

# Load data
df = pd.read_csv(HOTEL_PATH)

df = cleanData(df)

pp(df[ROOM].unique())

hotel_table_path = TABLES_PATH + HOTEL + "/"

if os.path.exists(hotel_table_path):
    shutil.rmtree(hotel_table_path)
os.mkdir(hotel_table_path)

for index, reservation in df.iterrows():
    if get_reservation_code(reservation) == "ERROR":
        continue
    if reservation[DAYS_IN_ADVANCE] <= 31:

        # Create competition
        competition = [round_price(x, UNITS) for x in create_competition(reservation[PRICE], MARGIN)]
        manage_table(reservation, competition, hotel_table_path)


# for filep in os.listdir(TABLES_PATH):
#     table_data = get_table_data(TABLES_PATH + filep)

#     for key1 in table_data:
#         for key2 in table_data[key1]:
#             if len(key1.split(",")) > len(key2.split(",")):
#                 numerator = sum(int(x) for x in key2.split(","))
#                 denominator = numerator + sum(int(x) for x in key1.split(","))
#             else:
#                 numerator = sum(int(x) for x in key1.split(","))
#                 denominator = numerator + sum(int(x) for x in key2.split(","))

#             expe = 1
#             new_val = table_data[key1][key2] / (table_data[key1][key2] / ((numerator / denominator) ** expe))

#             table_data[key1][key2] = new_val

#     write_table_data(table_data, TABLES_PATH + filep)
