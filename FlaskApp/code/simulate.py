import code.environment as e
import code.Visibilty_Graph as vg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from code.ShortestPath import dijkstra
import json
random.seed(77)


def setup_env(num_obstacles = 3):
    # num_obstacles = 3
    coord_range = (950, 950)
    convex = True
    obstacles = e.create_obstacles(num_obstacles, coord_range, convex)
    # e.plot_output(obstacles)
    start, end, polygons = e.build_polygons(obstacles)
    return start, end, polygons, obstacles


def gen_visibility_graph(start, end, polygons):
    visibility_graph = vg.brute_force(start, end, polygons)
    vg_edges = []
    for segment in visibility_graph.segments:
        vg_edges.append(((segment.p1.x, segment.p1.y),(segment.p2.x, segment.p2.y)))
    return visibility_graph, vg_edges


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
    for segment in visibility_graph.segments:
        plt.plot([segment.p1.x, segment.p2.x], [segment.p1.y, segment.p2.y], 'bo-')

    plt.plot(visibility_graph._s.x, visibility_graph._s.y, 'go', label='Start Point')
    plt.plot(visibility_graph._t.x, visibility_graph._t.y, 'ro', label='End Point')

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
        line["x1"] = path[index].x
        line["y1"] = path[index].y
        line["x2"] = path[index + 1].x
        line["y2"] = path[index + 1].y
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

    x_values = [point.x for point in points]
    y_values = [point.y for point in points]

    plt.plot(x_values, y_values, marker='o', linestyle='-')
    plt.title('Points Connected by Lines')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.grid(True)
    plt.show()


def simulate(start, end, polygons, obstacles):
    # print(start, end)
    # print(obstacles)
    visibility_graph, simplified_edges = gen_visibility_graph(start, end, polygons)
    # print(simplified_edges)
    # plot_visibility_graph(visibility_graph, obstacles)
    path = dijkstra(visibility_graph)
    # print(path)
    # plot_shortest_path(path, obstacles)
    return create_json(obstacles, simplified_edges, path)


def main():
    start, end, polygons, obstacles = setup_env()
    print(start, end)
    print(obstacles)
    visibility_graph, simplified_edges = gen_visibility_graph(start, end, polygons)
    print(simplified_edges)
    # plot_visibility_graph(visibility_graph, obstacles)
    path = dijkstra(visibility_graph)
    print(path)
    # plot_shortest_path(path, obstacles)


if __name__ == "__main__":
    main()
