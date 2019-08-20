
import pandas as pd
from datetime import datetime
from pprint import pprint as pp
import json
import os
import shutil
import numpy as np
import random
import operator

from modules.aux_functions import *
from room import Room
from modules.global_vars import *
from modules.reservation_management import get_reservation_code
from modules.table_manager import manage_table, write_table_data, get_table_data

np.random.seed(583)
random.seed(352)

my_hotel_path = HOTEL_TABLES_PATH + HOTEL + '/'
file_name = '21_double-superior_breakfast_weekend_ls.json'
file_to_test = my_hotel_path + file_name
hotel_data = {}
ara_values = {}

# Open the file to read it
with open(file_to_test, 'r') as fp:
    hotel_data = json.load(fp)

room_type, season = operator.itemgetter(*[1, 4])(file_name.split(".")[0].split("_"))
room = Room(room_type, HOTEL, hotel_data, season, file_name)

new_price = room.optimal_price()
print(new_price)
