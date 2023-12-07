import heapq


def build_graph(edges):
    graph = {}
    for edge in edges:
        start, end = edge
        if start not in graph:
            graph[start] = []
        if end not in graph:
            graph[end] = []
        # Assuming equal weight for all edges, you can modify this if weights are different
        weight = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
        graph[start].append((end, weight))
        graph[end].append((start, weight))
    return graph


def dijkstra(start, end, edges):
    graph = build_graph(edges)

    # Initialize distances with infinity for all nodes except the start node
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0

    # Predecessors dictionary to keep track of the path
    predecessors = {node: None for node in graph}

    # Priority queue to store nodes with their current distances
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        # Check if the current path to the current node is shorter than the recorded distance
        if current_distance > distances[current_node]:
            continue

        # Explore neighbors and update distances and predecessors
        for neighbor, weight in graph[current_node]:
            distance = current_distance + weight

            # If a shorter path is found, update the distance and predecessor
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    # Reconstruct the path from end to start
    path = []
    current_node = end
    while current_node is not None:
        path.insert(0, current_node)
        current_node = predecessors[current_node]

    # Return the path and the shortest distance
    return path, distances[end]
