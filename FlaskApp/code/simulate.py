import code.environment as e
import code.visibility_graph as vg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from code.shortestpath import dijkstra
import json
import numpy as np
# random.seed(334)


def enhancePolygon(obstacles, radius = 50*2):
    # radius = 50
 
    # Calculate new vertices
    polygons = []
    for vertex in obstacles:
        # Vector from centroid to vertex
        # print(np.array(vertex))
        centroids = np.mean(np.array(vertex), axis=0)
        # print(centroids)
        vectors = np.array(vertex) - centroids
 
        # Calculate distance from centroid to vertex
        distances = np.linalg.norm(vectors)
 
        # Calculate new distance after adding thickness
        new_distance = distances + radius*2
 
        # Scaling factor
        scaling_factor = new_distance / distances if distances != 0 else 1
 
        # Calculate scaled vertex
        scaled_vertex = centroids + vectors * scaling_factor
 
        # Append scaled vertex to the list
        polygons.append(list(scaled_vertex))
    return polygons


def setup_env(num_obstacles = 3, radius = 50):
    # num_obstacles = 8
    coord_range = (950, 950)
    convex = True
    obstacles = e.create_obstacles(num_obstacles, coord_range, convex)
    # print(obstacles)
    #obstacles = [[(200, 400), (400, 400), (400, 500), (200, 500)], [(450, 350), (550, 350), (550, 450), (450, 450)], [(600, 100), (700, 100), (700, 400), (600, 400)]]
    # e.plot_output(obstacles)
    start, end, polygons = e.build_polygons(obstacles)
    start, end, thick_polygons = e.build_polygons(enhancePolygon(obstacles, radius))
    return start, end, polygons, obstacles, thick_polygons


def gen_visibility_graph(start, end, polygons):
    graph = vg.VisGraph()
    graph.build(start, end, polygons)
    simplified_edges = list()
    for point in graph.visgraph.get_points():
        for edge in graph.visgraph[point]:
            if ((edge.p1.x, edge.p1.y), (edge.p2.x, edge.p2.y)) not in simplified_edges:
                simplified_edges.append(((edge.p1.x, edge.p1.y), (edge.p2.x, edge.p2.y)))
    return graph, simplified_edges

def plot_visibility_graph(visibility_graph, obstacles):
    fig, ax = plt.subplots()
    ax.set_title("Environment")
    for obs in obstacles:
        random_color = "#{:02X}{:02X}{:02X}".format(random.randint(1, 255),
                                                    random.randint(1, 255),
                                                    255)
        polygon = patches.Polygon(obs, closed=True, edgecolor='black',
                                  facecolor=random_color)
        ax.add_patch(polygon)
    for edge in visibility_graph:
        plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], color='blue')

    plt.plot(0, 0, 'go', label='Start Point')
    plt.plot(1000, 1000, 'ro', label='End Point')

    plt.title('Visibility Graph')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.show()


def create_json(obstacles, simplified_edges, path):
    json_vg = []
    for item in simplified_edges:
        line = {
            "type": 'line',
            "stroke-width": 1
        }
        line["fill"] = "#{:02X}{:02X}{:02X}".format(255, 0, 0)
        line["x1"] = item[0][0]
        line["y1"] = item[0][1]
        line["x2"] = item[1][0]
        line["y2"] = item[1][1]
        json_vg.append(line)
    json_result_vg = json.dumps(json_vg, indent=2)

    json_obstacles = []
    for i, sublist in enumerate(obstacles):
        polygon = {
            "type": 'polygon',
            "points": [],
        }
        random_color = "#{:02X}{:02X}{:02X}".format(random.randint(1, 255),
                                                    random.randint(1, 255),
                                                    255)
        polygon["fill"] = random_color
        for item in sublist:
            point = dict()
            point["x"] = item[0]
            point["y"] = item[1]
            polygon["points"].append(point)
        # Add the first point to close the shape
        point = dict()
        point["x"] = sublist[0][0]
        point["y"] = sublist[0][1]
        polygon["points"].append(point)
        json_obstacles.append(polygon)

    json_result_obs = json.dumps(json_obstacles, indent=2)

    json_path = []
    for index in range(len(path) - 1):
        line = {
            "type": 'line',
            "stroke-width": 3
        }
        line["fill"] = "#{:02X}{:02X}{:02X}".format(0, 255, 0)
        line["x1"] = path[index][0]
        line["y1"] = path[index][1]
        line["x2"] = path[index + 1][0]
        line["y2"] = path[index + 1][1]
        json_path.append(line)

    json_result_dj = json.dumps(json_path, indent=2)

    return json_result_dj, json_result_obs, json_result_vg


def plot_shortest_path(points, obstacles):
    # Plot obstacles
    fig, ax = plt.subplots()
    ax.set_title("Environment")
    for obs in obstacles:
        random_color = "#{:02X}{:02X}{:02X}".format(random.randint(1, 255),
                                                    random.randint(1, 255),
                                                    255)
        polygon = patches.Polygon(obs, closed=True, edgecolor='black',
                                  facecolor=random_color)
        ax.add_patch(polygon)

    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]

    plt.plot(x_values, y_values, marker='o', linestyle='-')
    plt.title('Points Connected by Lines')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.show()


def simulate(start, end, polygons, obstacles, thick_polygons):
    # print(start, end)
    # print(obstacles)
    visibility_graph, simplified_edges = gen_visibility_graph(start, end, polygons)
    # print(simplified_edges)
    # plot_visibility_graph(visibility_graph, obstacles)
    start_point = (start.x, start.y)
    end_point = (end.x, end.y)
    path, shortest_distance = dijkstra(start_point, end_point, simplified_edges)
    # print(path)
    # plot_shortest_path(path, obstacles)
    return create_json(obstacles, simplified_edges, path)


def main():
    start, end, polygons, obstacles, thick_polygons = setup_env()
    visibility_graph, simplified_edges = gen_visibility_graph(start, end, thick_polygons)
    plot_visibility_graph(simplified_edges, obstacles)
    start_point = (start.x, start.y)
    end_point = (end.x, end.y)
    path, shortest_distance = dijkstra(start_point, end_point, simplified_edges)
    plot_shortest_path(path, obstacles)
    print("Shortest Path: " + str(path))
    print("The Distance: " + str(shortest_distance))


if __name__ == "__main__":
    main()
