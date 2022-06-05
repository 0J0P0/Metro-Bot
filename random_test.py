import city
import metro
import restaurants as rs


def city_test() -> None:
    """Offers a random test and some basic information about the City
    graph."""

    Metro: city.MetroGraph = metro.get_metro_graph()
    Streets: city.OsmnxGraph = city.get_osmnx_graph()
    Barcelona: city.CityGraph = city.build_city_graph(Streets, Metro)

    print("Metro graph:", Metro)
    print("Streets graph:", Streets)
    print("Barcelona graph:", Barcelona)

    # Random coordinates for a path
    src: city.Coord = [2.179112, 41.392372]
    dst: city.Coord = [2.156996, 41.40329]

    path: city.Path = city.find_path(Streets, Barcelona, src, dst)
    print("List of nodes that represent the path", path)
    edges = city.get_edges_from_path(path)

    # Image of the path.
    city.plot_path(Barcelona, path, 'path.png', edges)

    # Graphic representation of the City graph.
    city.show(Barcelona)

    # Image of the Metro graph.
    city.plot(Barcelona, 'city.png')


def metro_test() -> None:
    """Offers a random test and some basic information about the Metro
    graph."""

    Metro: metro.MetroGraph = metro.get_metro_graph()
    print(Metro)

    print("Number of nodes in Metro Graph:", len(list(Metro.nodes)), "\n")

    # Random Stations from the Metro graph.
    badal = "ESTACIONS_LINIA.fid--64d2c1cd_17fdec435f4_444b"  # L5
    collblanc_5 = "ESTACIONS_LINIA.fid--64d2c1cd_17fdec435f4_444a"  # L5
    collblanc_9 = "ESTACIONS_LINIA.fid--64d2c1cd_17fdec435f4_4474"  # L9
    collblanc_10 = "ESTACIONS_LINIA.fid--64d2c1cd_17fdec435f4_4486"  # L10

    print("Description of 'collblanc_5' node:", Metro.nodes[collblanc_5], "\n")

    print("Adjacency list between 'badal' and 'collblanc_5':",
          Metro.edges[badal, collblanc_5], "\n")
    print("Adjacency list between 'collblanc_5' and 'collblanc_10':",
          Metro.edges[collblanc_5, collblanc_10], "\n")
    print("Adjacency list between 'collblanc_9' and 'collblanc_10':",
          Metro.edges[collblanc_9, collblanc_10], "\n")

    sant_ramon = "ACCESSOS.2578"  # Random Access
    print("'sant_ramon' Access to 'collblanc_5' Station:",
          Metro.nodes[sant_ramon], "\n")
    print("Adjacency list between 'collblanc_5' and 'sant_ramon':",
          Metro.edges[collblanc_5, sant_ramon], "\n")

    # Number of neighbours random Station.
    vecinos_collblanc_5 = Metro.degree(collblanc_5)  # = 7
    print("Number of Stations and Accesses from 'collblanc_5':",
          vecinos_collblanc_5)

    # Graphic representation of the Metro graph.
    city.show(Metro)

    # Image of the Metro graph.
    city.plot(Metro, "metro_map.png")


def restaurants_test() -> None:
    """Offers a random test and some basic information about the Restaurant
    module."""

    restaurants: rs.Restaurants = rs.read()
    print("Number of restaurants available:", len(restaurants))  # 2540

    query: str = "La Ceba"  # fisrt restaurnat available from the csv file.

    matching_restaurants: rs.Restaurant = rs.find(query, restaurants)

    for restaurant in matching_restaurants:
        print(restaurant)  # prints all the attributes for matched restaurant.


def main():
    city_test()
    metro_test()
    restaurants_test()


main()