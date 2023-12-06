import code.environment as e
import code.Visibilty_Graph as vg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from code.ShortestPath import dijkstra
import json
random.seed(77)


def setup_env():
    num_obstacles = 3
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
        result_vg = {
            "x": [],
            "y": [],
            "mode": "lines",
            "line": {
                "color": "blue"
            }
        }
        result_vg["x"].extend([item[0][0], item[1][0]])
        result_vg["y"].extend([item[0][1], item[1][1]])
        json_vg.append(result_vg)
    json_result_vg = json.dumps(json_vg, indent=2)

    json_obstacles = []
    for i, sublist in enumerate(obstacles):
        result_obs = {
            "x": [],
            "y": [],
            "mode": 'lines',
            "fill": 'toself',
            "fillcolor": 'red',
            "line": {
                "color": 'red'
            }
        }
        for item in sublist:
            result_obs["x"].append(item[0])
            result_obs["y"].append(item[1])
        # Add the first point to close the shape
        result_obs["x"].append(sublist[0][0])
        result_obs["y"].append(sublist[0][1])
        json_obstacles.append(result_obs)

    json_result_obs = json.dumps(json_obstacles, indent=2)

    path_simplified = []
    for p in path:
        path_simplified.append((p.x, p.y))

    result = {
        "x": [],
        "y": [],
        "mode": 'lines',
        "line": {
            "color": 'blue'
        }
    }

    for item in path_simplified:
        result["x"].append(item[0])
        result["y"].append(item[1])

    json_result_dj = json.dumps(result, indent=2)

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
    print(start, end)
    print(obstacles)
    visibility_graph, simplified_edges = gen_visibility_graph(start, end, polygons)
    print(simplified_edges)
    # plot_visibility_graph(visibility_graph, obstacles)
    path = dijkstra(visibility_graph)
    print(path)
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
