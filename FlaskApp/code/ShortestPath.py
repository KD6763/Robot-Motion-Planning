from typing import List
from heapq import heappop, heappush

from code.ClassList import VisibilityGraph, Point

def dijkstra(graph: VisibilityGraph) -> List[Point]:
    if not graph.constructed:
        graph.construct_adj_list()

    vertices, edges = graph.vertices, graph.adjacent_list
    distances, prev = {v: float('inf') for v in vertices}, {v: None for v in vertices}
    distances[graph.start] = 0.

    priority_queue = [(0, graph.start)]  # Priority queue to select the vertex with the smallest distance

    while priority_queue:
        u_dist, start_vertex = heappop(priority_queue)  # Select vertex with smallest distance
        if start_vertex in distances:
            for node in edges[start_vertex]:
                end_vertex, weight = node.coord, node.w  # Extract adjacent vertex end_vertex and distance weight
                total_weight = distances[start_vertex] + weight
                if end_vertex not in priority_queue and total_weight < distances[end_vertex]:
                    distances[end_vertex] = total_weight
                    prev[end_vertex] = start_vertex
                    heappush(priority_queue, (total_weight, end_vertex))

            #del distances[start_vertex]  # Mark the vertex as checked

    # Construct path to graph.end using back-tracing
    path = [graph.end]
    cv = graph.end
    while cv != graph.start:
        cv = prev[cv]
        path.append(cv)

    path.reverse()  # Reverse the list for the actual path

    return path
