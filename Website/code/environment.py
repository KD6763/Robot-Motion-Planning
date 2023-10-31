"""
file: environment.py
description: This program create random obstacles(polygons) based on given
configuration settings
language: python3
author: Anurag Kallurwar, ak6491@rit.edu
"""


import sys
import math as m
import random
import matplotlib.pyplot as plt


def partition(num_partitions: int):
    factorize = lambda num: {factor for i in range(1, int(m.sqrt(num)) + 1)
                               if num % i == 0 for factor in [i, num // i]}
    factors = sorted(factorize(num_partitions))
    random_index = random.choices(range(0, len(factors)), weights = None,
                                  k = 1)[0]
    partitions = (factors[random_index], factors[-random_index - 1])
    return partitions


def orient(pointP: tuple, pointQ: tuple, pointR):
    """
    Get the orientation between three points
    :param pointP: Point P
    :param pointQ: Point Q
    :param pointR: Point R
    :return: Integer
    """
    result = (pointQ[0] * pointR[1] - pointR[0] * pointQ[1]) - \
             (pointP[0] * pointR[1] - pointR[0] * pointP[1]) + \
             (pointP[0] * pointQ[1] - pointQ[0] * pointP[1])
    if result > 0: # Counter-Clockwise
        return 1
    elif result < 0: # Clockwise
        return -1
    return 0 # Collinear


def half_hull(points: list):
    """
    Creates half a hull from given points
    :param points: input points
    :return: Half hull
    """
    stack = []
    stack.append(points[0])
    stack.append(points[1])
    for index in range(2, len(points)):
        while len(stack) >= 2 and orient(points[index], stack[-1], stack[-2])\
                <= 0:
            stack.pop()
        stack.append(points[index])
    return stack


def graham_scan(num_points: int, points: list):
    """
    Creates convex hull using graham scan algorithm
    :param num_points: number of points
    :param points: input points
    :return: convex hull points
    """
    if num_points < 3:
        return "Convex Hull not possible"
    sorted_by_x = sorted(points, key = lambda point : point[0])
    convex_hull = half_hull(sorted_by_x) + half_hull(sorted_by_x[::-1])[1:-1]
    return convex_hull[::-1]


def create_obstacles(num_obstacles: int, coord_range: tuple):
    partitions = partition(num_obstacles)
    x_splits = [50] + sorted(random.sample(range(101, coord_range[0] - 1),
                                          partitions[0] - 1)) + [coord_range[0]]
    y_splits = [50] + sorted(random.sample(range(101, coord_range[1] - 1),
                                          partitions[1] - 1)) + [coord_range[1]]
    partition_areas = []
    for i in range(len(x_splits) - 1):
        for j in range(len(y_splits) - 1):
            partition_areas += [((x_splits[i], x_splits[i + 1]),
                                 (y_splits[j], y_splits[j + 1]))]
    print(partition_areas)
    obstacles = []
    for area in partition_areas:
        num_points = random.randint(4, 10)
        points = [(random.randint(area[0][0], area[0][1]), random.randint(
            area[1][0], area[1][1])) for i in range(num_points)]
        obstacle = graham_scan(num_points, points)
        obstacles.append(obstacle)
    return obstacles


def plot_output(obstacles: list):
    """
    Plot the points and convex hull
    :param points: input points
    :param convex_hull: convex hull
    :return: None
    """

    fig, ax = plt.subplots()
    ax.set_title("Environment")
    for obstacle in obstacles:
        points_x = [point[0] for point in obstacle] + [obstacle[0][0]]
        points_y = [point[1] for point in obstacle] + [obstacle[0][1]]
        ax.plot(points_x, points_y, c='k')
    ax.scatter([0], [0], c='r', label="Start")
    ax.scatter([1000], [1000], c='g', label="Destination")
    ax.scatter([0], [0], c='b', label="Point Robot", marker='*', s=10)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    # ax.set_aspect('equal')
    ax.set_aspect('equal', adjustable='box')
    ax.legend(bbox_to_anchor=(1.0, 1), loc='upper left', fontsize=7)
    plt.tight_layout()
    plt.show()


def main():
    """
    The main function
    :return: None
    """
    # inputs = sys.argv()
    # if len(inputs) < 2:
    #     print("Sorry not possible")
    # num_obstacles = int(inputs[1])
    num_obstacles = 6
    coord_range = (950, 950)
    obstacles = create_obstacles(num_obstacles, coord_range)
    print(obstacles)
    plot_output(obstacles)


if __name__ == '__main__':
    main()  # Calling Main Function
