

import pandas as pd
from datetime import datetime
from pprint import pprint as pp
import json
import os
import shutil
import numpy as np
import random

from modules.aux_functions import *
from modules.global_vars import *
from modules.reservation_management import get_reservation_code
from modules.table_manager import manage_table, write_table_data, get_table_data

np.random.seed(583)
random.seed(352)

my_hotel_path = HOTEL_TABLES_PATH + HOTEL + '/'

for table_name in os.listdir(my_hotel_path):
    competence_prices = {}
    table_file = my_hotel_path + table_name
    with open(table_file) as fp:
        hotel_data = json.load(fp)

    mean_price = np.mean([int(x) for x in hotel_data.keys()])

    for comp_hotel in COMPETENCE_HOTELS:
        comp_file = HOTEL_TABLES_PATH + comp_hotel + '/' + table_name

        # If table exists in the competence folder, use that data
        if os.path.isfile(comp_file):
            comp_data = {}
            with open(comp_file) as fp:
                comp_data = json.load(fp)

            # Prices to use
            ptu = MAX_COMP_PRICES if MAX_COMP_PRICES <= len(comp_data) else len(comp_data)

            ################
            # Posibilidad de seleccionar aquellos valores con más clientes
            competition = random.sample(comp_data.keys(), ptu)
            competence_prices[comp_hotel] = competition
        else:
            competition = [round_price(x, UNITS) for x in create_competition(mean_price, MARGIN)]
            competence_prices[comp_hotel] = competition

    hotel_data_out = {}
    for price, clients in hotel_data.items():
        comp_price = {}
        for w in range(MAX_COMP_OCCUR):

            comp_price_key = ''
            # Se compara para ver que esos valores de la comptencia no hayan salido ya
            while comp_price_key == '' or comp_price_key in comp_price.keys():
                comp_price_ts = []
                # Por cada hotel de la competencia se coge uno de los precios
                for comp_hotel_key in competence_prices:
                    comp_price_ts += random.sample(competence_prices[comp_hotel_key], 1)
                comp_price_key = ','.join(comp_price_ts)
            comp_price[comp_price_key] = (sum([int(x) for x in comp_price_ts])) / int(price)

        hotel_data_out[price] = {}
        mean_prop= sum(comp_price.values())
        for comp_key, comp_prop in comp_price.items():
            hotel_data_out[price][comp_key] = int(round(clients * (comp_prop / mean_prop)))

    comp_data_glob = competence_data(table_name)
    # for price in hotel_data_out:
        # for comp_key in hotel_data_out[price]:
            # our_clients = hotel_data_out[price][comp_key]
            # hotel_data_out[price][comp_key] = get_outcome_prob(comp_data_glob, price, comp_key, our_clients)

    write_table_data(hotel_data_out, table_file)
