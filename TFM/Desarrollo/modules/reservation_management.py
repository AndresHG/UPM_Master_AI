
from pprint import pprint

from modules.global_vars import *

# Generate de room code and type that will be used to code
def get_room_code(room_type):
    for key, value in ROOMS_CODE.items():
        if room_type in value: return key
    # return "double"
    # if "suite" in room_type:
        # return "suite"
    # elif "double" in room_type:
        # return "double"
    return "ERROR"
    # return '-'.join(room_type.split(" "))

# Get the type of day given a datetime
def get_day_code(day):
    if day.weekday() in WEEK_DAYS: return WEEK_CODE
    else: return WEEKEND_CODE

# Generate season code given a datetime
def get_season_code(date):
    if str(date.month) in HIGH_SEASON.keys() and date.day in HIGH_SEASON[str(date.month)]: return HIGH_SEASON_CODE
    else: return LOW_SEASON_CODE

# Generate table id code
def get_reservation_code(reservation):
    code = ""

    # Days in advance (30 posibilities)
    code += str(reservation[DAYS_IN_ADVANCE])
    code += CODE_SEPARATOR

    # Room type (3 posibilities, 2 at the moment)
    if get_room_code(reservation[ROOM]) == "ERROR":
        return "ERROR"
    code += get_room_code(reservation[ROOM])
    code += CODE_SEPARATOR

    # Board of the reservation (2 posibilities)
    code += BOARD_CODE[reservation[BOARD]]
    code += CODE_SEPARATOR

    # Day type (2 posibilities)
    code += get_day_code(reservation[DATE_FROM])
    code += CODE_SEPARATOR

    # Season of the day (2 posibilities)
    code += get_season_code(reservation[DATE_FROM])

    return code
