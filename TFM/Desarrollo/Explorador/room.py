
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
from modules.global_vars import ROOM_BENEFITS, ROOM_COSTS, SEASON_BENEFITS, COMPETENCE_HOTELS
from modules.reservation_management import get_reservation_code
from modules.table_manager import manage_table, write_table_data, get_table_data

np.random.seed(583)
random.seed(352)

my_hotel_path = HOTEL_TABLES_PATH + HOTEL + '/'

class Room:


    def __init__(self, room_type, hotel, prices, season, file_name):
        """Create the room propierties

        :param room_type: The normalized type of the room (in global vars)
        :param hotel: The name of the hotel (string)
        :param prices: Dictionary with self prices, competence prices and our occupation
        :param season: The season (low or high)
        :param file_name: The name of the file in our code
        :returns: The object Room
        :rtype: Room Object

        """
        self.room_type = room_type
        self.hotel_name = hotel
        self.prices = prices
        self.season = season
        self.file_name = file_name
        self.comp_data = self.__competence_data()

    def __get_utility(self, room_price, outcome):
        """Calculate the utility of a room given a specific the room price

        :param room_price: The specific price of the room
        :returns: Value of the utility
        :rtype: Integer

        """
        total_benefits = int(room_price) + ROOM_BENEFITS[self.room_type] - \
            ROOM_COSTS[self.room_type] + SEASON_BENEFITS[self.season]
        total_benefits *= (0.5 + outcome)
        return total_benefits

    def __competence_data(self):
        """Retrieve the competence data

        :returns: Comptence prices and its correspond clients
        :rtype: Dictionary

        """
        comp_data = {}
        for indi, comp_hotel in enumerate(COMPETENCE_HOTELS):
            comp_table = HOTEL_TABLES_PATH + comp_hotel + '/' + self.file_name
            if os.path.isfile(comp_table):
                with open(comp_table) as fp:
                    comp_data[comp_hotel] = json.load(fp)
            else:
                comp_data[comp_hotel] = {}
        return comp_data

    def __get_outcome_prob(self, our_price, comp_price, our_clients):
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
            if self.comp_data[comp_hotel]:
                try:
                    selected_price = comp_price.split(",")[indi]
                    total_clients += self.comp_data[comp_hotel][selected_price]
                # If the price is not in the competences prices list
                except Exception as e:
                    print("Precio no encontrado en la competencia")
                    total_clients += our_clients
            # If we dont have competence data, we asume they have the same clients than us
            else:
                total_clients += our_clients

        return our_clients / total_clients

    def __get_price_probability(self, dict_prices, selected_price):
        """Calculate the probability that the competence chose selected_price

        :param dict_prices: Dict with the prices used by the competence
        :param selected_price: Tuple string with the selected prices for the competence
        :returns: Probability that the competence choose the selected_price
        :rtype: Double

        """

        comp_hotel_data = {}
        result = 1

        chosen_prices = selected_price.split(",")
        # We stract the price clients that we have used want from competence data
        for indi, hotel_name in enumerate(COMPETENCE_HOTELS):
            comp_hotel_data[hotel_name] = {}
            comp_hotel_data[hotel_name]['total'] = 0

            for tuple_price in dict_prices.keys():
                price = tuple_price.split(",")[indi]
                if chosen_prices[indi] == price:
                    comp_hotel_data[hotel_name]['chosen'] = self.comp_data[hotel_name][price]
                comp_hotel_data[hotel_name]['total'] += self.comp_data[hotel_name][price]


        # print(comp_hotel_data)
        for hotel_name in comp_hotel_data:
            result *= comp_hotel_data[hotel_name]['chosen'] / comp_hotel_data[hotel_name]['total']

        return result


    def __generate_ara_values(self):
        """Generate ARA values from the formulas

        :returns: Array with all of the ARA values
        :rtype: List

        """
        self.ara_values = {}
        for room_price, comp_prices in self.prices.items():
            temp_ara_val = 0
            for outcome in [0, 1]:
                for comp_price, our_clients in comp_prices.items():
                    if outcome == 1:
                        temp_ara_val += self.__get_utility(room_price, outcome) * \
                            self.__get_outcome_prob(room_price, comp_price, our_clients) * \
                            self.__get_price_probability(comp_prices, comp_price)
                    else:
                        temp_ara_val -= self.__get_utility(room_price, outcome) * \
                            (1 - self.__get_outcome_prob(room_price, comp_price, our_clients)) * \
                            self.__get_price_probability(comp_prices, comp_price)
            self.ara_values[room_price] = temp_ara_val

        return self.ara_values


    def optimal_price(self):
        ara_values = self.__generate_ara_values()
        return max(ara_values.items(), key=operator.itemgetter(1))[0]
