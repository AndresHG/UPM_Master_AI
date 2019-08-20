import numpy as np
from datetime import datetime
import os
import json
import pandas as pd

from modules.global_vars import *

# Parse data
def cleanData(df):
    df[DATE_TO] = df[DATE_TO].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
    df[DATE_FROM] = df[DATE_FROM].apply(lambda x: datetime.strptime(str(x), '%Y%m%d'))
    df[TIMESTAMP] = pd.to_datetime(df[TIMESTAMP])
    df[ROOM] = df[ROOM].apply(lambda x: x.lower())
    return df

# Round rpice
def round_price(price, units):
    price = int(round(price))
    return (price // units) * units if price % units <= units / 2 else (price // units) * units + units

# Create competition function
def create_competition(price, std_desviation):
    return np.random.normal(price, std_desviation, MAX_COMP_PRICES)


def get_outcome_prob(comp_data, our_price, comp_price, our_clients):
    """Calculate the probability that a client comes to our hotel given our price and competence price

    :param our_price: Self price of the room
    :param comp_price: Competence price for the same room
    :param our_clients: Number of clients that have chosen us in the past
    :returns: Probability of choosing our hotel
    :rtype: Double

    """
    total_clients = our_clients
    # Search for competence data to calculate the demand
    for indi, comp_hotel in enumerate(COMPETENCE_HOTELS):
        if comp_data[comp_hotel]:
            try:
                selected_price = comp_price.split(",")[indi]
                total_clients += comp_data[comp_hotel][selected_price]

            except Exception as e:
                print("Precio no encontrado en la competencia")
                total_clients += our_clients
                # If we dont have competence data, we asume they have the same clients than us
        else:
            total_clients += our_clients

    return our_clients / total_clients

def competence_data(file_name):
    """Retrieve the competence data

    :returns: Comptence prices and its correspond clients
    :rtype: Dictionary

    """
    comp_data = {}
    for indi, comp_hotel in enumerate(COMPETENCE_HOTELS):
        comp_table = HOTEL_TABLES_PATH + comp_hotel + '/' + file_name
        if os.path.isfile(comp_table):
            with open(comp_table) as fp:
                comp_data[comp_hotel] = json.load(fp)
        else:
            comp_data[comp_hotel] = {}
    return comp_data
