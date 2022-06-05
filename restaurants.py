import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional
from fuzzysearch import find_near_matches
from typing_extensions import TypeAlias


"""
Template file for restaurant.py module.
"""


"""
Module that contains the code related to the restaurants list collection
and related searches.
"""


@dataclass
class Restaurant:
    """Representation of a Restaurant. The Restaurant class contains all the
    parameters that could be used to identify a restaurant through a bot
    search. Some of them optional in case there is a Restaurant that does
    not contain some of the parameters (NA - Not Available)."""

    name: str  # Name of the restaurant.
    institution_name: Optional[str]  # Name of the institution.
    addresses_road_name: str  # Address road name.
    addresses_start_street_number: str  # Address number.
    addresses_neighborhood_name: str  # Address neighbourhood name.
    addresses_district_name: str  # Address district name.
    addresses_zip_code: str  # Address zip code.
    addresses_town: str  # Address town.
    values_value: str  # Telephone number.
    longitude: str
    latitude: str


# List of restaurants
Restaurants: TypeAlias = List[Restaurant]


def convert_to_coord(coord: str) -> str:
    """Given a string containing a coordinate following
    the format of restaurants.csv, the function returns
    the same coordinate in the 'correct' format for the
    other functions and methods."""

    i: int
    num: str = coord[0]
    if coord[0] == "2":
        num += "."
        i = 1
    if coord[0] == "4":
        num += coord[1]
        num += "."
        i = 2

    while i < len(coord):
        num += coord[i]
        i += 1

    return num


def read() -> Restaurants:
    """Reads the restaurants.csv file and creates a DataFrame, from which, for
    each row, a new Restaurant is created and then added to the list of
    restaurants."""

    restaurants: Restaurants = []

    csv_file = pd.read_csv('restaurants.csv', encoding='latin1', sep=';')
    raw_data = pd.DataFrame(csv_file)

    # Assignation of None value to the NA values in the raw DataFrame.
    data = raw_data.replace(to_replace=np.nan, value=None)

    for row in data.itertuples():
        # The coordinates are converted to the right format.
        latitude = convert_to_coord(str(row.geo_epgs_4326_x))
        longitude = convert_to_coord(str(row.geo_epgs_4326_y))
        restaurant = Restaurant(row.name,
                                row.institution_name,
                                row.addresses_road_name,
                                row.addresses_start_street_number,
                                row.addresses_neighborhood_name,
                                row.addresses_district_name,
                                row.addresses_zip_code,
                                row.addresses_town,
                                row.values_value,
                                longitude,
                                latitude)

        restaurants.append(restaurant)

    return restaurants


def find(query: str, restaurants: Restaurants) -> Restaurants:
    """Given a query and a list of restaurants, the function returns
    another list of restaurants that contains that query or similar in some
    of its parameters."""

    matching_restaurants: Restaurants = []

    for restaurant in restaurants:
        # A list with all the parameters of "restaurant" is created.
        restaurant_parameters = [str(restaurant.name),
                                 str(restaurant.institution_name),
                                 str(restaurant.addresses_road_name),
                                 str(restaurant.addresses_start_street_number),
                                 str(restaurant.addresses_neighborhood_name),
                                 str(restaurant.addresses_district_name),
                                 str(restaurant.addresses_zip_code),
                                 str(restaurant.addresses_town),
                                 str(restaurant.values_value),
                                 str(restaurant.longitude),
                                 str(restaurant.latitude)]
        # The query string is searched in the elements of the parameter list
        # using the fuzzysearch function 'find_near_matches()'.
        for parameter in restaurant_parameters:
            found: bool = (find_near_matches(query, str(parameter),
                                             max_l_dist=1) != [])

            if (parameter != "None") and found:
                matching_restaurants.append(restaurant)
                # Once a matching parameter is found, this loop stops.
                break

    return matching_restaurants
