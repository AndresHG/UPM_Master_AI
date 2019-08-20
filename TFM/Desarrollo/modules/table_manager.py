
from datetime import datetime
from pprint import pprint as pp
import json
import os

from modules.global_vars import *
from modules.reservation_management import get_reservation_code
from modules.aux_functions import round_price

# Get the data from the table json file if exists. Else, returns and empty dictionary
def get_table_data(file_path):
    table_data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as fp: table_data = json.load(fp)
    return table_data

# Write the table data into the json file
def write_table_data(table_data, file_path):
    with open(file_path, 'w+') as fp: json.dump(table_data, fp, indent=4, sort_keys=True)

# Create or update tables if needed
def manage_table(reservation, competition, hotel_table_path):
    table_code = get_reservation_code(reservation)
    file_path = hotel_table_path + table_code + TABLES_EXTENSION

    table_data = get_table_data(file_path)

    # Generate competititon price code
    competition_price = ','.join([str(x) for x in competition])
    our_price = str(round_price(reservation[PRICE], UNITS))

    # Case of our_price as key
    # Retrieve value of the table and set it to 0 if not exists

    if our_price in table_data.keys():
        if competition_price in table_data[our_price]:
            table_data[our_price][competition_price] += 1
        else:
            table_data[our_price][competition_price] = 1
    else:
        table_data[our_price] = {}
        table_data[our_price][competition_price] = 1

    # Case of competititon_price as key

    # if competition_price in table_data.keys():
        # if our_price in table_data[competition_price]:
            # table_data[competition_price][our_price] += 1
        # else:
            # table_data[competition_price][our_price] = 1
    # else:
        # table_data[competition_price] = {}
        # table_data[competition_price][our_price] = 1


    # dict(sorted(table_data.items()))
    write_table_data(table_data, file_path)
