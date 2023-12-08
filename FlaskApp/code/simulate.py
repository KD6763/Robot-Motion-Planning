import code.environment as e
import code.visibility_graph as vg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from code.shortestpath import dijkstra
import json
import math
import numpy as np
# random.seed(334)


def enhancePolygon(vertices, radius):
    """
    Scales a convex polygon by a given thickness for each side.

    :param vertices: List of tuples representing the vertices of the polygon [(x1, y1), (x2, y2), ..., (xn, yn)]
    :param thicknesses: List of thicknesses for each side.
    :return: List of tuples representing the scaled vertices of the polygon.
    """
    radius = (radius) * -1
    def unit_vector(vector):
        """ Returns the unit vector of the vector. """
        return vector / np.linalg.norm(vector)

    def scale_vertex(p1, p2, p3, thickness):
        """
        Scales a single vertex defined by points p1, p2, and p3 with the given thickness.
        """
        # Vector from p1 to p2 and p2 to p3
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p3) - np.array(p2)

        # Unit vectors
        u_v1 = unit_vector(v1)
        u_v2 = unit_vector(v2)

        # Normal vectors pointing "outwards" from the edges
        n1 = np.array([-u_v1[1], u_v1[0]])
        n2 = np.array([-u_v2[1], u_v2[0]])

        # Offset points along the normal vectors by the thickness
        p1_offset = np.array(p1) + n1 * thickness
        p2_offset = np.array(p2) + n1 * thickness
        p3_offset = np.array(p2) + n2 * thickness
        p4_offset = np.array(p3) + n2 * thickness

        # Calculate intersection of the two offset lines (p1_offset -> p2_offset) and (p3_offset -> p4_offset)
        A1 = p2_offset[1] - p1_offset[1]
        B1 = p1_offset[0] - p2_offset[0]
        C1 = A1 * p1_offset[0] + B1 * p1_offset[1]

        A2 = p4_offset[1] - p3_offset[1]
        B2 = p3_offset[0] - p4_offset[0]
        C2 = A2 * p3_offset[0] + B2 * p3_offset[1]

        det = A1 * B2 - A2 * B1
        if det == 0:
            raise ValueError("Lines do not intersect")
        else:
            x = (B2 * C1 - B1 * C2) / det
            y = (A1 * C2 - A2 * C1) / det
            return (math.ceil(x), math.ceil(y))

    scaled_vertices = []

    # Loop through all vertices to calculate the new scaled vertices
    for obstacle in vertices:
        temp = []
        num_vertices = len(obstacle)
        for i in range(len(obstacle)):
            p1 = obstacle[i - 1]  # Previous vertex
            p2 = obstacle[i]      # Current vertex
            p3 = obstacle[(i + 1) % num_vertices]  # Next vertex

            # Scale current vertex and add to list
            scaled_vertex = scale_vertex(p1, p2, p3, radius)
            temp.append(scaled_vertex)
            scaled_vertices.append(temp)
    return scaled_vertices


def setup_env(num_obstacles = 3, radius = 50, convex = True):
    # num_obstacles = 8
    coord_range = (950, 950)
    # convex = False
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
            simply_edge = ((edge.p1.x, edge.p1.y), (edge.p2.x, edge.p2.y))
            if simply_edge not in simplified_edges:
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
            "strokewidth": '1'
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
            "strokewidth": '5'
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
    visibility_graph, simplified_edges = gen_visibility_graph(start, end, thick_polygons)
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
    print(path)


if __name__ == "__main__":
    main()
