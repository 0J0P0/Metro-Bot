import os
import metro
import networkx
import osmnx as ox
import pickle as pk
from cmath import inf
import matplotlib.pyplot as plt
from typing import List, Tuple, Union
from typing_extensions import TypeAlias
from staticmap import StaticMap, CircleMarker, Line


"""
Template file for city.py module.
"""


"""
Module that contains the code related to the implementation for the
construction of the city graph and the search for routes between two
coordinates in the city.
"""


NodeID: TypeAlias = Union[int, str]
Path: TypeAlias = List[NodeID]

CityGraph: TypeAlias = networkx.Graph
MetroGraph: TypeAlias = networkx.Graph
OsmnxGraph: TypeAlias = networkx.MultiDiGraph


Coord = Tuple[float, float]  # (latitude, longitude)


def show(g: CityGraph) -> None:
    """Opens a new window showing the graphic representation of the
    given graph g."""

    networkx.draw(g, pos=networkx.get_node_attributes(g, 'pos'),
                  with_labels=False, node_size=5)
    plt.show()


def plot(g: CityGraph, filename: str) -> None:
    """Prints the graph g in a map of Open Street Map,
    saving the result in a png named 'filename'."""

    # The OSM default world map.
    map = StaticMap(1000, 1000,
                    url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

    # The nodes of g.
    for node in list(g.nodes):
        marker = CircleMarker(g.nodes[node]['pos'], g.nodes[node]['color'], 1)
        map.add_marker(marker)

    # The edges of g.
    for edge in list(g.edges):
        coordinates: Tuple = (g.nodes[edge[0]]['pos'], g.nodes[edge[1]]['pos'])
        line = Line(coordinates, g[edge[0]][edge[1]]['color'], 2)
        map.add_line(line)

    image = map.render()
    image.save(filename)


def get_edges_from_path(path: Path) -> List[Tuple[NodeID]]:
    """Given a Path (list of nodes in order of traversal),
    returns a list of pairs of nodes representing the edges of the path."""

    edges_from_path: List[Tuple[NodeID]] = []

    for i in range(len(path)):
        if i != len(path) - 1:
            edge: Tuple[NodeID] = [path[i], path[i + 1]]
            edges_from_path.append(edge)

    return edges_from_path


def plot_path(g: CityGraph, p: Path, filename: str,
              edges_from_path: List[Tuple[NodeID]]) -> None:
    """Given a path p of the graph g, the function shows the path in a map
    and stores it in the file filename."""

    # The OSM default world map.
    map = StaticMap(1000, 1000,
                    url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

    # The starting point is added in red with a white border.
    starting_point_1 = CircleMarker(g.nodes[p[0]]['pos'],
                                    "#FFFFFF", 20)
    starting_point_2 = CircleMarker(g.nodes[p[0]]['pos'],
                                    "#FF0000", 15)
    map.add_marker(starting_point_1)
    map.add_marker(starting_point_2)

    # The destination point is added in purple with a white border.
    destination_1 = CircleMarker(g.nodes[p[-1]]['pos'],
                                 "#FFFFFF", 20)
    destination_2 = CircleMarker(g.nodes[p[-1]]['pos'],
                                 "#800080", 15)
    map.add_marker(destination_1)
    map.add_marker(destination_2)

    # The edges of the path.
    for edge in edges_from_path:
        coordinates: Tuple = (g.nodes[edge[0]]['pos'], g.nodes[edge[1]]['pos'])
        line = Line(coordinates, g[edge[0]][edge[1]]['color'], 6)
        map.add_line(line)

    image = map.render()
    image.save(filename)


def load_osmnx_graph(filename: str) -> OsmnxGraph:
    """Loads the City graph from a given file and returns it.
    Precondition: the file has to exist."""

    City_file = open(filename, 'rb')  # read in binary mode from origin file.
    City: OsmnxGraph = pk.load(City_file)
    City_file.close()

    return City


def save_osmnx_graph(g: OsmnxGraph, filename: str) -> None:
    """Saves the City graph g into a given file."""

    city_file = open(filename, 'ab')  # destination file in binary mode.
    pk.dump(g, city_file)
    city_file.close()


def get_osmnx_graph() -> OsmnxGraph:
    """Downloads a simplified graph of Barcelona and returns it."""

    City: OsmnxGraph
    if os.path.exists("./barcelona.grf"):  # City graph already exists.
        City = load_osmnx_graph("./barcelona.grf")
    else:
        City = ox.graph_from_place("Barcelona", network_type='walk',
                                   simplify=True)

        # Remove the geometry attribute from the nodes of the graph, since it
        # won't be of any use.
        for u, v, key, geom in City.edges(data="geometry", keys=True):
            if geom is not None:
                del(City[u][v][key]["geometry"])

        save_osmnx_graph(City, "./barcelona.grf")

    return City


def connect_access_to_street(g1: OsmnxGraph, g2: MetroGraph) -> None:
    """Connects the Metro accesses to their respective Streets,
    using the two given graphs g1 and g2."""

    lon: List = []
    lat: List = []
    accesses: metro.Accesses = metro.read_accesses()

    for access in accesses:
        lon.append(access.geometry[0])
        lat.append(access.geometry[1])

    # Tuple with a list of the nearest nodes and a list with the
    # distance to them.
    connections: Tuple = ox.distance.nearest_nodes(g1, lon, lat,
                                                   return_dist=True)
    a: int = 0
    while a < 352:
        g2.add_edge(connections[0][a], accesses[a].fid,
                    type="Access entry",
                    distance=connections[1][a],
                    speed=100,
                    travel_time=connections[1][a]/100,
                    color="#808080")
        a += 1


def build_city_graph(g1: OsmnxGraph, g2: MetroGraph) -> CityGraph:
    """Merges g1 into g2, modifying the attributes of the nodes and edges of
    g1. Returns g2 merged with g1."""

    # The reason that all the data from g1 to g2 is read is because in this
    # way the nodes and arrests of g1 are purified and only added with the
    # necessary attributes to the graph g2. (If g2 was merged into g1, the
    # number of nodes to traverse would obviously be less).

    # prev_cross and post_cross are crossings of Streets, i.e. nodes of the
    # OsmnxGraph.
    for prev_cross, nbrsdict in g1.adjacency():
        coordinates: Coord = (g1.nodes[prev_cross]['x'],
                              g1.nodes[prev_cross]['y'])
        g2.add_node(prev_cross,
                    type="Crossing",
                    pos=coordinates,
                    color="#2DBF11")

        for post_cross, edgesdict in nbrsdict.items():
            coordinates = (g1.nodes[post_cross]['x'],
                           g1.nodes[post_cross]['y'])
            g2.add_node(post_cross,
                        type="Crossing",
                        pos=coordinates,
                        color="#2DBF11")

            eattr = edgesdict[0]  # first edge attributes.
            street_name: str = "No name registered"
            if 'name' in eattr:  # some Streets don't have a name.
                street_name = eattr['name']

            if prev_cross != post_cross:
                g2.add_edge(prev_cross, post_cross,
                            type="Street",
                            distance=eattr['length'],
                            speed=100,
                            name=street_name,
                            osm_id=eattr['osmid'],
                            travel_time=eattr['length']/100,
                            color="#000000")

    connect_access_to_street(g1, g2)
    return g2


def travel_time(g: CityGraph) -> float:
    """Returns the smallest amount of time needed to go from
    node 1 (source) to node 2 (destiantion) in te graph g."""

    # Nodes 1 and 2 have to be in the graph
    time: float = networkx.shortest_path_length(g, 1, 2, weight='travel_time',
                                                method='dijkstra')

    return time


def remove_src_and_dst_nodes(g: CityGraph) -> None:
    """Removes the source and destination nodes added to the City Graph,
    since they won't be for any use after the path connecting those two
    points is found."""

    # 1 is the source and 2 is the destination nodes.
    g.remove_nodes_from([1, 2])


def find_path(ox_g: OsmnxGraph, g: CityGraph, src: Coord, dst: Coord) -> Path:
    """Adds the source location and the destination location as a nodes to the
    City Graph. In this way, the shortest path in time is sought. Finally it
    returns the shortest path found in terms of travel time."""

    g.add_node(1, type="Start", pos=src, color="#000000")  # Start node.
    nearest_node: NodeID = ox.distance.nearest_nodes(ox_g, src[0], src[1])
    g.add_edge(1, nearest_node, type="Start edge", distance=0.0,
               travel_time=0.0, color="#000000")

    # Destination node.
    g.add_node(2, type="Destination", pos=dst, color="#000000")
    nearest_node = ox.distance.nearest_nodes(ox_g, dst[0], dst[1])
    g.add_edge(2, nearest_node, type="Destination edge",
               distance=0.0, travel_time=0.0, color="#000000")

    path: Path = ox.distance.shortest_path(g, 1, 2, weight='travel_time')
    return path
