import heapq
import math


def euclidean_distance(point1, point2):
    """
    Find the Euclidean distance among the points
    :param point1: The first Point
    :param point2: The Second Point
    :return: The Euclidean distance
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def build_matrix(coordinates):
    """
    Build a matrix from the points
    :param coordinates: All the points
    :return: Graph in a form of matrix
    """
    graph = {point: {} for point in coordinates}
    for i, point1 in enumerate(coordinates):
        for j, point2 in enumerate(coordinates):
            if i != j:
                weight = euclidean_distance(point1, point2)
                graph[point1][point2] = weight
    return graph


def dijkstra(coordinates, start, intermediate_points, end):
    """
    Find the shortest paths to all the points connected in a graph from the starting point
    :param coordinates: All the points in a graph
    :param start: Starting Point
    :param intermediate_points: All the intermediate points
    :param end: The destination
    :return: Shortest Paths to all points from Start Point
    """
    graph = build_matrix(coordinates)

    distances = {point: float('inf') for point in graph}
    end_dist = {end: float('inf')}
    predecessors = {point: None for point in graph}
    distances[start] = 0

    vertices_to_visit = [(0, start)]

    while vertices_to_visit:
        current_distance, current_point = heapq.heappop(vertices_to_visit)

        if current_distance > distances[current_point]:
            continue

        for neighbor, weight in graph[current_point].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                if neighbor == end:
                    end_dist = distance
                predecessors[neighbor] = current_point
                heapq.heappush(vertices_to_visit, (distance, neighbor))

    shortest_paths = {}
    shortest_path_end = {}
    for intermediate_point in intermediate_points:
        path = []
        current_point = intermediate_point
        while current_point is not None:
            path.insert(0, current_point)
            current_point = predecessors[current_point]
        shortest_paths[intermediate_point] = path
        if intermediate_point == end:
            shortest_path_end = path

    return end_dist, shortest_path_end
