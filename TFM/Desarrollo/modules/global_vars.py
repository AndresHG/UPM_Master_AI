
import numpy as np

# Variables for CSV parser
TIMESTAMP = "stimestamp"
DATE_FROM = "date_from"
DATE_TO = "date_to"
DAYS_IN_ADVANCE = "days_in_advance"
ROOM = "room_normalized"
RESERVATIONS = "reservations"
RES_DAYS = "reservation_days"
BOARD = "board"
PRICE = "price"

HOTEL = "Melia Barajas"
# HOTEL = "Gran Melia Fenix"
# "NH Barajas",
COMPETENCE_ORDER_KEY = "Competence_Order"
COMPETENCE_HOTELS = ["Axor Barajas",
                     "Senator Barajas"]
ALL_HOTELS = [HOTEL] + COMPETENCE_HOTELS

# Name of the CSV to be read
HOTEL_PATH = "Dataset/Hoteles/obatch- " + HOTEL
# Path to table files
TABLES_PATH = "Tablas/"
# TABLES_PATH = "Tablas/" + HOTEL + "/"
TEMP_HOTEL_TABLES_PATH = "Temp_tables/"
HOTEL_TABLES_PATH = "Tablas_hotel/"
# HOTEL_TABLES_PATH = "Tablas_hotel/" + HOTEL + "/"
FINAL_TABLES_PATH = "Tablas_finales/"
FINAL_CSV_PATH = "CSV_finales/"
PRICE_DAYS_TABLES_PATH = "Tablas_dias_por_precio/"

# Minumun and max prices that the room can handle
MIN_PRICE = 70
MAX_PRICE = 300

# Min and max comp price for virtual creation
MIN_COMP_VIRTUAL = -1
MAX_COMP_VIRTUAL = 1

# Maximun number of competence prices in table division
MAX_COMP_PRICES = 3
MAX_COMP_OCCUR = 6

# Table files extension
TABLES_EXTENSION = ".json"
# Units for the prices to be round
UNITS = 10
# Separator in the code of the tables' names
CODE_SEPARATOR = "_"
# Defines de margin over competitions prices for the room
MARGIN = 10
# Months with the days that are part of the high season
HIGH_SEASON = {"1": list(np.arange(15)),
            "4": list(np.arange(15, 23)),
            "7": list(np.arange(31)),
            "8": list(np.arange(31)),
            "12": list(np.arange(31))}
WEEK_DAYS = [0, 1, 2, 3, 6]
WEEKEND_DAYS = [4, 5]

# Codes for table generation
HIGH_SEASON_CODE = "hs"
LOW_SEASON_CODE = "ls"
WEEK_CODE = "week"
WEEKEND_CODE = "weekend"
BOARD_CODE = {"Alojamiento y Desayuno": "breakfast",
              "Solo Alojamiento": "lodge"}
# ROOMS_CODE = {"simple": [],
#          "double": ["doble",
#                    "suite junior",
#                    "doble duperior con vistas a la piscina",
#                    "doble superior"],
#          "sup": ["doble con vistas a la piscina premium",
#                  "suite",
#                  "doble premium",
#                  "familiar",
#                  "triple"]}
ROOMS_CODE = {
    "simple": [],
    "double": ["doble"],
    "double-superior": ["doble executive",
                        "doble superior",
                        "doble superior con vistas a la piscina",
                        "doble con vistas a la piscina premium",
                        "doble premium"],
    "tiple": ["triple"]
}
ROOM_BENEFITS = {
    "simple": 10,
    "double": 20,
    "double-superior": 30,
    "tiple": 40
}
ROOM_COSTS = {
    "simple": 30,
    "double": 40,
    "double-superior": 40,
    "tiple": 50
}
SEASON_BENEFITS = {
    HIGH_SEASON_CODE: 30,
    LOW_SEASON_CODE: 20
}
