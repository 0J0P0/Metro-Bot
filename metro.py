import networkx
import numpy as np
import pandas as pd
from typing import List, Tuple
import matplotlib.pyplot as plt
from dataclasses import dataclass
from haversine import haversine, Unit
from typing_extensions import TypeAlias
from staticmap import StaticMap, CircleMarker, Line


"""
Template file for metro.py module.
"""


"""
Module that contains the code related to the implementation for the
construction of the metro graph.
"""


@dataclass
class Point:
    """Representation of a Point with a x coordinate and a y coordinate."""
    x_coord: float
    y_coord: float


@dataclass
class Station:
    """Representation of a Metro Station. The Station class contains all
    the useful parameters that a Station from the csv file  'estacions.csv' can
    contain."""

    fid: str
    codi_grup_estacio: int
    nom_estacio: str
    codi_linia: int
    nom_linia: str
    color_linia: str
    geometry: Tuple


@dataclass
class Access:
    """Representation of a Metro Access. The Access class contains all
    the useful parameters that an Access from the csv accessos.csv file can
    contain."""

    fid: str
    nom_acces: str
    codi_grup_estacio: int
    nom_estacio: str
    geometry: Tuple


Stations: TypeAlias = List[Station]
Accesses: TypeAlias = List[Access]
MetroGraph: TypeAlias = networkx.Graph


def transform_to_float(coordinate: str) -> float:
    """Transforms a given string (a real number with a parenthesis in one of
    its sides) into a float by removing the parenthesis. Finally, it returns
    the float number."""

    new_coordinate: str = ""
    i: int = 0

    while i < len(coordinate):
        if coordinate[i] != '(' and coordinate[i] != ')':
            new_coordinate += coordinate[i]
        i += 1

    return float(new_coordinate)


def transform_to_point(geometry: str) -> Point:
    """Transforms a given string (with two coordinates) into a
    Point by spliting it into its x and y components. Finally, it
    returns the Point created."""

    # 'data' is a 2 positions list where 'geometry' is splitted into
    #  two different strings (x and y coordinates), one for each index.
    data = geometry.split()

    point = Point(0, 0)

    point.x_coord = transform_to_float(data[1])
    point.y_coord = transform_to_float(data[2])

    return point


def read_stations() -> Stations:
    """Reads the estacions.csv file and creates a DataFrame, from which, for
    each row, a new Station is created and then added to the list of
    stations. Finally it returns the list of stations."""

    stations: Stations = []

    csv_file = pd.read_csv('estacions.csv',  encoding='latin1', sep=';')
    data = pd.DataFrame(csv_file)

    for row in data.itertuples():
        location = transform_to_point(row.GEOMETRY)
        station = Station(row.FID,
                          row.CODI_GRUP_ESTACIO,
                          row.NOM_ESTACIO,
                          row.CODI_LINIA,
                          row.NOM_LINIA,
                          row.COLOR_LINIA,
                          [location.x_coord, location.y_coord])
        stations.append(station)

    return stations


def read_accesses() -> Accesses:
    """Reads the accessos.csv file and creates a DataFrame, from which, for
    each row, a new Access is created and then added to the list of
    accesses. Finally it returns the list of accesses."""

    accesses: Accesses = []

    csv_file = pd.read_csv('accessos.csv',  encoding='latin1', sep=';')
    data = pd.DataFrame(csv_file)

    for row in data.itertuples():
        location = transform_to_point(row.GEOMETRY)
        access = Access(row.FID,
                        row.NOM_ACCES,
                        row.CODI_GRUP_ESTACIO,
                        row.NOM_ESTACIO,
                        [location.x_coord, location.y_coord])
        accesses.append(access)

    return accesses


def add_access_edge_to_station(Metro: MetroGraph, station: Station,
                               access: Access) -> None:
    """Adds an edge to the Metro graph from a given Access to its
    assigned Station."""

    dist: float = haversine(station.geometry, access.geometry,
                            unit=Unit.METERS)
    Metro.add_edge(station.fid, access.fid,
                   type="Access route",
                   distance=dist,
                   speed=100,
                   travel_time=(dist/100) + 2,
                   color="#808080")


def add_access_to_metro(Metro: MetroGraph, access: Access) -> None:
    """Adds an Access node to the Metro graph."""

    Metro.add_node(access.fid,
                   type="Access",
                   name=access.nom_acces,
                   station_name=access.nom_estacio,
                   group=access.codi_grup_estacio,
                   pos=access.geometry,
                   color="#000000")


def find_station_for_access(stations: Stations, access: Access) -> Station:
    """Finds and returns the corresponding Station for a given Access."""

    for station in stations:
        if station.nom_estacio == access.nom_estacio:
            break
    return station


def add_accesses(Metro: MetroGraph, stations: Stations,
                 accesses: Accesses) -> MetroGraph:
    """Adds each Access to its assigned Station. We know that an Access
    corresponds to a Station if they both have the same 'codi_grup_estacio'
    attribute, therefor, for each Access from a different 'codi_grup_esatcio'
    a search for its Station is done and then a new 'Access route' edge is
    created. Finally it returns the updated Metro graph."""

    access: Access = accesses[0]
    station: Station = find_station_for_access(stations, access)

    add_access_to_metro(Metro, access)
    add_access_edge_to_station(Metro, station, access)

    a: int = 1
    while a < len(accesses):
        if accesses[a].codi_grup_estacio != accesses[a-1].codi_grup_estacio:
            station = find_station_for_access(stations, accesses[a])

        add_access_to_metro(Metro, accesses[a])
        add_access_edge_to_station(Metro, station, accesses[a])
        a += 1

    return Metro


def add_line_to_metro(Metro: MetroGraph, prev_station: Station,
                      post_station: Station, edge_type: str, sp: float,
                      edge_color: str) -> None:
    """Adds an edge to the Metro between two Stations, representing the
    track of the line. Notice that prev_station and post_station are both
    from the same line."""

    dist: float = haversine(prev_station.geometry, post_station.geometry,
                            unit=Unit.METERS)

    Metro.add_edge(prev_station.fid, post_station.fid,
                   type=edge_type,
                   distance=dist,
                   speed=sp,
                   travel_time=dist/sp,
                   color=edge_color)


def add_station_to_metro(Metro: MetroGraph, station: Station) -> None:
    """Adds a Station with its attributes to the Metro graph."""

    Metro.add_node(station.fid,
                   type="Station",
                   name=station.nom_estacio,
                   line=station.nom_linia,
                   group=station.codi_grup_estacio,
                   pos=station.geometry,
                   color='#' + station.color_linia)


def check_for_transbords(Metro: MetroGraph, added_stations: Stations,
                         new_station: Station) -> None:
    """Checks if the new_station has a connection with another line of
    the added_stations. If so, an edge is created connecting
    the two lines in the Metro graph."""

    # Notice the difference between this type of edge (connection between two
    # lines) and the one for the creation of a line.
    add_station_to_metro(Metro, new_station)

    for station in added_stations:
        if station.codi_grup_estacio == new_station.codi_grup_estacio:
            add_line_to_metro(Metro, station, new_station,
                              "Connection between two different lines",
                              100,
                              "#808080")


def add_stations(Metro: MetroGraph, stations: Stations) -> MetroGraph:
    """Adds all the stations, and the connections between each other, to the
    Metro graph. For each line, the stations of that line are added to
    the graph, while it is checked if they can have a connection with any
    other station in the graph. Right after that, the edges that connect all
    the line are created, through the list of line_stations.
    Finally it returns the updated Metro graph."""

    s: int = 0
    added_stations: Stations = []  # Stations already in the Metro graph.
    for line in [1, 2, 3, 4, 5, 94, 91, 104, 101, 11, 99]:  # Metro line num.
        edges: List[Tuple] = []  # Edges of the metro line
        line_stations: Stations = []  # The "path" of the line.

        # Fisrt case to initialize a metro line in the Metro graph.
        add_station_to_metro(Metro, stations[s])
        line_stations.append(stations[s])
        added_stations.append(stations[s])
        s += 1

        while s in range(1, len(stations)) and stations[s].codi_linia == line:
            # Being the first line (1) to be added to the graph there is no
            # need to check for connections with other lines.
            if stations[s].codi_linia == 1:
                add_station_to_metro(Metro, stations[s])
            else:
                check_for_transbords(Metro, added_stations, stations[s])
            added_stations.append(stations[s])
            line_stations.append(stations[s])
            s += 1

        ss: int = 0
        while ss < len(line_stations) - 1:  # Addition of the line edges.
            add_line_to_metro(Metro, line_stations[ss], line_stations[ss+1],
                              "Metro line nº "+line_stations[ss].nom_linia,
                              433.33, "#"+line_stations[ss].color_linia)
            ss += 1

    return Metro


def get_metro_graph() -> MetroGraph:
    """Creates and returns a graph with Stations and Accesses as nodes
    connected by different types of edges depending on the conections."""

    Metro = MetroGraph()

    stations: Stations = read_stations()
    add_stations(Metro, stations)

    accesses: Accesses = read_accesses()
    add_accesses(Metro, stations, accesses)

    return Metro


def show(g: MetroGraph) -> None:
    """Opens a new window showing the graphic representation of the
    given graph g."""

    networkx.draw(g, pos=networkx.get_node_attributes(g, 'pos'),
                  with_labels=False, node_size=5)
    plt.show()


def plot(g: MetroGraph, filename: str) -> None:
    """Prints a given graph g in a map of Open Street Map,
    saving the result in a png named 'filename'."""

    # The OSM default world map.
    map = StaticMap(680, 600,
                    url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

    # The nodes of g.
    for node in list(g.nodes):
        marker = CircleMarker(g.nodes[node]['pos'], '#ff0000', 3)
        map.add_marker(marker)

    # The edges of g.
    for edge in list(g.edges):
        coordinates: Tuple = (g.nodes[edge[0]]['pos'], g.nodes[edge[1]]['pos'])
        line = Line(coordinates, '#0000ff', 2)
        map.add_line(line)

    image = map.render()
    image.save(filename)
