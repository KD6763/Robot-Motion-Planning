import code.environment as e
import code.Visibilty_Graph as vg
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random
from code.ShortestPath import dijkstra
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
    visibility_graph = vg.rotational_plane_sweep(start, end, polygons)
    print(visibility_graph)
    return visibility_graph


def plot_visibility_graph(visibility_graph, obstacles):
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
    # Plot visibility graph edges
    for segment in visibility_graph.segments:
        plt.plot([segment.p1.x, segment.p2.x], [segment.p1.y, segment.p2.y], 'bo-')

    # Mark start and end points
    plt.plot(visibility_graph._s.x, visibility_graph._s.y, 'go', label='Start Point')
    plt.plot(visibility_graph._t.x, visibility_graph._t.y, 'ro', label='End Point')

    plt.title('Visibility Graph')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.show()


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


def simulate():
    start, end, polygons, obstacles = setup_env()
    print(start, end)
    visibility_graph = gen_visibility_graph(start, end, polygons)
    # plot_visibility_graph(visibility_graph, obstacles)
    path = dijkstra(visibility_graph)
    print(path)
    # plot_shortest_path(path, obstacles)
    return path


def main():
    simulate()


if __name__ == "__main__":
    main()
