
import pandas as pd
from datetime import datetime
from pprint import pprint as pp
import json
import os
import shutil
import numpy as np

from modules.aux_functions import *
from modules.global_vars import *
from modules.reservation_management import get_reservation_code
from modules.table_manager import manage_table, write_table_data, get_table_data

np.random.seed(583)

def manage_hotel_table(reservation, hotel_table_path):
    """FIXME! briefly describe function

    :param reservation: 
    :param hotel_table_path: 
    :returns: 
    :rtype: 

    """
    table_code = get_reservation_code(reservation)
    file_path = hotel_table_path + table_code + TABLES_EXTENSION

    table_data = get_table_data(file_path)

    # Generate competititon price code
    our_price = str(round_price(reservation[PRICE], UNITS))

    # Case of our_price as key
    # Retrieve value of the table and set it to 0 if not exists

    if our_price in table_data.keys():
        table_data[our_price] += 1
    else:
        table_data[our_price] = 1

    write_table_data(table_data, file_path)

for hotel in ALL_HOTELS:

    hotel_table_path = HOTEL_TABLES_PATH + hotel + "/"

    hotel_path = "Dataset/Hoteles/obatch- " + hotel
    # Load data
    df = pd.read_csv(hotel_path)
    df = cleanData(df)

    # pp(df[ROOM].unique())

    if os.path.exists(hotel_table_path):
        shutil.rmtree(hotel_table_path)
    os.mkdir(hotel_table_path)
    print(hotel_table_path)

    for index, reservation in df.iterrows():
        if get_reservation_code(reservation) == "ERROR":
            continue
        if reservation[DAYS_IN_ADVANCE] <= 31:
            manage_hotel_table(reservation, hotel_table_path)



